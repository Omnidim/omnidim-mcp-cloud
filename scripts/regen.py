#!/usr/bin/env python3
"""Regenerate app/_generated/tools.py from the OmniDimension OpenAPI spec.

By default the spec is fetched from the published docs site, so this runs
from a clean checkout. Set $SPEC to a local file path (or another https URL
on an allowed host) to override.

Reads:
  https://docs.omnidim.io/openapi.yaml          (spec; or $SPEC override)
  internal-openapi.yaml                         (operator-only operations kept
                                                 out of the public docs; or
                                                 $INTERNAL_SPEC)

Each operation's x-mcp block decides its tool: title, effect (read, write or
destructive), open-world, hide-params, or hidden. An operation without one
fails the regen, so nothing reaches agents before someone decides how.

Writes:
  app/_generated/tools.py                       (Python tool registry)
  app/_generated/.spec.yml                      (sha256 of both specs)

Run after the upstream spec changes:
  ./.venv/bin/python scripts/regen.py

Pass --check to compare against the committed output instead of writing it.
Exits non-zero when the upstream spec has moved on, which is how CI notices
that the exposed tool surface no longer matches the API.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import urllib.request
from collections.abc import Iterable
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parent.parent

DEFAULT_SPEC_URL = "https://docs.omnidim.io/openapi.yaml"
ALLOWED_SPEC_HOSTS = {"docs.omnidim.io"}
MAX_SPEC_BYTES = 8 * 1024 * 1024

SPEC_SOURCE = os.environ.get("SPEC", DEFAULT_SPEC_URL)
INTERNAL_SPEC_PATH = Path(os.environ.get("INTERNAL_SPEC", ROOT / "internal-openapi.yaml"))

OUT_TOOLS = ROOT / "app" / "_generated" / "tools.py"
OUT_HASH = ROOT / "app" / "_generated" / ".spec.yml"


def _checked_url(raw: str) -> str:
    """Pin the spec fetch to https on an allowed host.

    A value read from the environment must not become an arbitrary
    outbound request, so the scheme and host are constrained here.
    """
    parsed = urlparse(raw)
    if parsed.scheme != "https":
        sys.stderr.write(f"spec URL must use https: {raw}\n")
        sys.exit(1)
    if parsed.hostname not in ALLOWED_SPEC_HOSTS:
        allowed = ", ".join(sorted(ALLOWED_SPEC_HOSTS))
        sys.stderr.write(f"spec host {parsed.hostname} not allowed (expected: {allowed})\n")
        sys.exit(1)
    return raw


def load_spec_bytes(source: str) -> tuple[bytes, str]:
    """Return the raw spec bytes and a label (URL or path) for provenance."""
    if re.match(r"^https?://", source):
        url = _checked_url(source)
        with urllib.request.urlopen(url, timeout=30) as resp:  # noqa: S310 - host pinned by _checked_url
            data: bytes = resp.read(MAX_SPEC_BYTES + 1)
        if len(data) > MAX_SPEC_BYTES:
            sys.stderr.write("spec is unexpectedly large\n")
            sys.exit(1)
        return data, url
    path = Path(source)
    if not path.exists():
        sys.stderr.write(f"missing spec file: {path}\n")
        sys.exit(1)
    return path.read_bytes(), str(path)


def _operations(spec: dict[str, Any]) -> Iterable[tuple[str, dict[str, Any], dict[str, Any]]]:
    for item in (spec.get("paths") or {}).values():
        for method, op in item.items():
            if method in {"get", "post", "put", "patch", "delete"} and isinstance(op, dict):
                yield method, op, item


def merge_internal(spec: dict[str, Any], internal: dict[str, Any]) -> set[str]:
    """Merge the internal fragment into the spec; return its operation ids (operator-only).

    Overlaps stop the regen: upstream now documents the operation, so the
    fragment copy is stale and must be deleted rather than silently shadow it.
    """
    sections = (
        (spec.setdefault("paths", {}), internal.get("paths") or {}),
        (
            spec.setdefault("components", {}).setdefault("schemas", {}),
            (internal.get("components") or {}).get("schemas") or {},
        ),
    )
    for target, extra in sections:
        if clash := sorted(set(target) & set(extra)):
            raise SystemExit(f"internal spec overlaps the public spec: {', '.join(clash)}")
    operator_only = {
        str(op.get("operationId")) for _, op, _ in _operations({"paths": sections[0][1]})
    }
    for target, extra in sections:
        target.update(extra)

    by_id = {op.get("operationId"): (op, item) for _, op, item in _operations(spec)}
    for op_id, params in (internal.get("x-extra-parameters") or {}).items():
        if op_id not in by_id:
            raise SystemExit(f"x-extra-parameters: no operation {op_id} in the spec")
        op, item = by_id[op_id]
        existing = {
            resolve_refs(p, spec).get("name")
            for p in (*(item.get("parameters") or []), *(op.get("parameters") or []))
        }
        if clash := sorted({p["name"] for p in params} & existing):
            raise SystemExit(f"x-extra-parameters: {op_id} already has {', '.join(clash)}")
        op["parameters"] = [*(op.get("parameters") or []), *params]
    return operator_only


def slug(s: str) -> str:
    """Stable tool name from an operationId or path."""
    return re.sub(r"[^a-zA-Z0-9_]", "_", s)


def resolve_refs(node: Any, spec: dict[str, Any], _seen: frozenset[str] = frozenset()) -> Any:
    """Recursively inline local `$ref` pointers against the spec.

    Without this, a requestBody whose schema is a bare `$ref`
    collapses to an empty property set, leaving the tool with no
    documented input fields. Cyclic refs are broken by returning
    an empty object on re-entry.
    """
    if isinstance(node, list):
        return [resolve_refs(v, spec, _seen) for v in node]
    if not isinstance(node, dict):
        return node
    ref = node.get("$ref")
    if isinstance(ref, str) and ref.startswith("#/"):
        if ref in _seen:
            return {"type": "object"}
        target: Any = spec
        for part in ref[2:].split("/"):
            target = target.get(part, {}) if isinstance(target, dict) else {}
        resolved = resolve_refs(target, spec, _seen | {ref})
        # Merge any sibling keys alongside the $ref (description, etc.).
        siblings = {k: resolve_refs(v, spec, _seen) for k, v in node.items() if k != "$ref"}
        if isinstance(resolved, dict):
            return {**resolved, **siblings}
        return resolved
    return {k: resolve_refs(v, spec, _seen) for k, v in node.items()}


def flatten_all_of(schema: dict[str, Any]) -> dict[str, Any]:
    """Collapse a top-level `allOf` into a single object schema.

    The spec composes some request bodies as
    `allOf: [$ref Schema, {required: [...]}]`. After ref resolution the
    properties live inside the allOf members, so reading `properties`
    off the wrapper yields nothing and the tool publishes an empty
    input schema with no documented fields.
    """
    if "allOf" not in schema:
        return schema
    properties: dict[str, Any] = {}
    required: list[str] = []
    for member in schema["allOf"]:
        if not isinstance(member, dict):
            continue
        flat = flatten_all_of(member)
        properties.update(flat.get("properties", {}))
        required.extend(flat.get("required", []))
    merged = {k: v for k, v in schema.items() if k != "allOf"}
    merged["properties"] = {**properties, **merged.get("properties", {})}
    merged["required"] = [*required, *schema.get("required", [])]
    return merged


def _with_type(prop: dict[str, Any]) -> dict[str, Any]:
    """One property with a top-level `type`, read off its allOf or oneOf members."""
    wrapped = prop.get("allOf")
    if isinstance(wrapped, list) and len(wrapped) == 1 and "type" in wrapped[0]:
        inner = wrapped[0]
        merged = {**inner, **{k: v for k, v in prop.items() if k != "allOf"}}
        if inner.get("description") and prop.get("description"):
            merged["description"] = f"{prop['description'].rstrip()}\n{inner['description']}"
        return merged
    choices = prop.get("oneOf") or prop.get("anyOf")
    if isinstance(choices, list) and all(isinstance(c.get("type"), str) for c in choices):
        return {**prop, "type": sorted({c["type"] for c in choices})}
    return prop


def type_properties(node: Any) -> None:
    """Give every property a top-level `type`: Claude's directory portal refuses one without."""
    if not isinstance(node, dict):
        return
    props = node.get("properties")
    if isinstance(props, dict):
        for key, prop in props.items():
            if isinstance(prop, dict) and "type" not in prop:
                props[key] = prop = _with_type(prop)
            type_properties(prop)
    type_properties(node.get("items"))


BODY_LIST_ARG = "items"


def body_list_schema(request_body: dict[str, Any] | None) -> dict[str, Any] | None:
    schema = ((request_body or {}).get("content", {}).get("application/json", {})).get("schema")
    if not isinstance(schema, dict):
        return None
    lists = [b for b in schema.get("oneOf", []) if isinstance(b, dict) and b.get("type") == "array"]
    if not lists:
        return None
    note = "Send a list, even for one item. It becomes the request body."
    return {**lists[0], "description": note}


def merge_schema(
    parameters: Iterable[dict[str, Any]],
    request_body: dict[str, Any] | None,
) -> dict[str, Any]:
    """Collapse OpenAPI parameters + requestBody into a single JSON Schema.

    Path/query/header params become top-level properties.
    requestBody (application/json) is merged onto the same object.
    """
    properties: dict[str, Any] = {}
    required: list[str] = []

    for p in parameters:
        name = p["name"]
        schema = dict(p.get("schema", {"type": "string"}))
        if p.get("description"):
            schema.setdefault("description", p["description"])
        properties[name] = schema
        if p.get("required") or p.get("in") == "path":
            required.append(name)

    if request_body:
        content = request_body.get("content", {})
        json_body = content.get("application/json", {})
        body_schema = json_body.get("schema")
        if body_schema:
            body_schema = flatten_all_of(body_schema)
            body_props = body_schema.get("properties", {})
            properties.update(body_props)
            required.extend(body_schema.get("required", []))
        if (as_list := body_list_schema(request_body)) is not None:
            properties[BODY_LIST_ARG] = as_list
            if request_body.get("required"):
                required.append(BODY_LIST_ARG)

    return {
        "type": "object",
        "properties": properties,
        "required": sorted(set(required)),
        "additionalProperties": True,
    }


def effective_parameters(
    path_item_params: Iterable[dict[str, Any]],
    op_params: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Merge path-item-level and operation-level parameters.

    OpenAPI applies path-item parameters to every operation under that path.
    An operation-level parameter overrides a path-item one with the same
    (name, in). Without this, path params declared at the path-item level
    (e.g. agent_id on /agents/{agent_id}) are dropped and never substituted.
    """
    merged: dict[tuple[str, str], dict[str, Any]] = {}
    for p in path_item_params:
        merged[(p["name"], p.get("in", "query"))] = p
    for p in op_params:
        merged[(p["name"], p.get("in", "query"))] = p
    return list(merged.values())


def build_tool(
    path: str,
    method: str,
    op: dict[str, Any],
    path_item_params: Iterable[dict[str, Any]] = (),
    spec: dict[str, Any] | None = None,
) -> dict[str, Any]:
    op_id = op.get("operationId") or slug(f"{method}_{path}")
    summary = op.get("summary", "").strip()
    description = op.get("description", "").strip()
    if summary and description:
        full_desc = f"{summary}. {description}"
    else:
        full_desc = summary or description

    op_params = op.get("parameters", [])
    if spec is not None:
        # Parameters may be `$ref`s into components/parameters; resolve before merging by name.
        # Reseller `user_id` (act as a client) must never reach an LLM-driven tool.
        def keep(p: dict[str, Any]) -> bool:
            return not str(p.get("$ref", "")).endswith("/parameters/ClientUserId")

        path_item_params = [resolve_refs(p, spec) for p in path_item_params if keep(p)]
        op_params = [resolve_refs(p, spec) for p in op_params if keep(p)]
    params = effective_parameters(path_item_params, op_params)
    request_body = op.get("requestBody")
    if request_body is not None and spec is not None:
        request_body = resolve_refs(request_body, spec)
    schema = merge_schema(params, request_body)
    # Same field can arrive in the body (via `$ref`): drop it there too.
    schema.get("properties", {}).pop("user_id", None)
    if "required" in schema:
        schema["required"] = [r for r in schema["required"] if r != "user_id"]
        if not schema["required"]:
            del schema["required"]
    type_properties(schema)
    # Mark which inputs go in the path so the dispatcher can substitute them.
    path_param_names = [p["name"] for p in params if p.get("in") == "path"]
    query_param_names = [p["name"] for p in params if p.get("in") == "query"]
    header_param_names = [p["name"] for p in params if p.get("in") == "header"]
    tool = {
        "name": op_id,
        "description": full_desc,
        "input_schema": schema,
        "method": method.upper(),
        "path": path,
        "path_params": path_param_names,
        "query_params": query_param_names,
        "header_params": header_param_names,
    }
    if body_list_schema(request_body) is not None:
        tool["body_list_arg"] = BODY_LIST_ARG
    return tool


def strip_params(op: dict[str, Any], names: list[str]) -> int:
    """Drop named parameters from an operation that is otherwise exposed.

    Done on the spec object before build_tool sees it, so the field leaves the
    input schema and the execution parameters together.
    """
    if not names:
        return 0
    dropped = 0
    params = op.get("parameters")
    if isinstance(params, list):
        before = len(params)
        op["parameters"] = [p for p in params if p.get("name") not in names]
        dropped += before - len(op["parameters"])
    schema = (
        (op.get("requestBody") or {})
        .get("content", {})
        .get("application/json", {})
        .get("schema")
    )
    if isinstance(schema, dict) and isinstance(schema.get("properties"), dict):
        for name in names:
            if name in schema["properties"]:
                del schema["properties"][name]
                dropped += 1
            if isinstance(schema.get("required"), list):
                schema["required"] = [r for r in schema["required"] if r != name]
    return dropped


_MCP_KEYS = {"title", "effect", "open-world", "hide-params", "hidden", "merge"}
_EFFECTS = {"read", "write", "destructive"}


def mcp_marks(op_id: str, method: str, op: dict[str, Any]) -> dict[str, Any]:
    """The operation's x-mcp block, checked. Exits on a missing or bad one."""
    marks = op.get("x-mcp")
    if marks is None:
        raise SystemExit(f"{op_id} has no x-mcp block: add one to the spec")

    def bad(why: str) -> SystemExit:
        return SystemExit(f"bad x-mcp on {op_id}: {why}")

    if not isinstance(marks, dict):
        raise bad("not a mapping")
    if unknown := set(marks) - _MCP_KEYS:
        raise bad(f"unknown keys {sorted(unknown)}")
    if "hidden" in marks:
        reason = marks["hidden"]
        if set(marks) != {"hidden"} or not isinstance(reason, str) or not reason.strip():
            raise bad("hidden takes a reason, as text, and no other keys")
        return marks
    title = marks.get("title")
    if not isinstance(title, str) or not title.strip():
        raise bad("title is required, as text")
    effect = marks.get("effect")
    if not isinstance(effect, str) or effect not in _EFFECTS:
        raise bad(f"effect must be one of {sorted(_EFFECTS)}")
    if method == "get" and effect != "read":
        raise bad("a GET is a read")
    open_world = marks.get("open-world")
    if not (open_world is None or open_world is True) or (open_world and effect == "read"):
        raise bad("open-world is true on a write, or absent")
    hide = marks.get("hide-params", [])
    if not isinstance(hide, list) or not all(isinstance(n, str) for n in hide):
        raise bad("hide-params is a list of input names")
    if "merge" in marks and not _valid_merge(marks["merge"]):
        raise bad("merge takes tool, as text, and action, a snake_case word or a list of them")
    return marks


_ACTION_RE = re.compile(r"[a-z][a-z_]*")
_EFFECT_RANK = {"read": 0, "write": 1, "destructive": 2}
_MERGE_GROUP_KEYS = {"title", "description", "field"}


def _valid_merge(merge: Any) -> bool:
    if not isinstance(merge, dict) or set(merge) != {"tool", "action"}:
        return False
    if not isinstance(merge["tool"], str) or not merge["tool"]:
        return False
    actions = merge_actions(merge)
    return bool(actions) and all(isinstance(a, str) and _ACTION_RE.fullmatch(a) for a in actions)


def merge_actions(merge: dict[str, Any]) -> list[Any]:
    action = merge["action"]
    return list(action) if isinstance(action, list) else [action]


def _without_description(prop: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in prop.items() if k != "description"}


def _merge_group(name: str, groups: dict[str, Any]) -> dict[str, Any]:
    group = groups.get(name)
    if not isinstance(group, dict):
        raise SystemExit(f"{name} is not declared under x-mcp-tools")
    if unknown := set(group) - _MERGE_GROUP_KEYS:
        raise SystemExit(f"bad x-mcp-tools entry {name}: unknown keys {sorted(unknown)}")
    for key in ("title", "description"):
        if not isinstance(group.get(key), str) or not group[key].strip():
            raise SystemExit(f"bad x-mcp-tools entry {name}: {key} is required, as text")
    if not isinstance(group.get("field", "action"), str):
        raise SystemExit(f"bad x-mcp-tools entry {name}: field is text")
    return group


def _action_route(tool: dict[str, Any], inputs: list[str], passes: bool) -> dict[str, Any]:
    route = {
        "operation": tool["name"],
        "method": tool["method"],
        "path": tool["path"],
        "path_params": tool["path_params"],
        "query_params": tool["query_params"],
        "header_params": tool["header_params"],
        "inputs": inputs,
        "required": sorted(r for r in tool["input_schema"].get("required", []) if r in inputs),
        "sends_field": passes,
    }
    if "body_list_arg" in tool:
        route["body_list_arg"] = tool["body_list_arg"]
    return route


def _label_partial_inputs(
    props: dict[str, Any], takers: dict[str, list[str]], every_action: list[str]
) -> None:
    for key, acts in takers.items():
        if len(set(acts)) < len(every_action):
            only = ", ".join(f"`{a}`" for a in acts)
            said = props[key].get("description", "")
            props[key] = {**props[key], "description": f"Only for {only}. {said}".strip()}


def _merged_annotations(
    group: dict[str, Any], members: list[tuple[dict[str, Any], dict[str, Any]]]
) -> dict[str, Any]:
    effect = max((m["effect"] for _, m in members), key=_EFFECT_RANK.__getitem__)
    marks: dict[str, Any] = {"title": group["title"], "effect": effect}
    if any(m.get("open-world") for _, m in members):
        marks["open-world"] = True
    return annotations_for(marks)


def merged_tool(
    name: str, group: dict[str, Any], members: list[tuple[dict[str, Any], dict[str, Any]]]
) -> dict[str, Any]:
    if len(members) < 2:
        raise SystemExit(f"{name} folds one operation: merge two or more, or drop the mark")
    field: str = group.get("field", "action")
    routes: dict[str, dict[str, Any]] = {}
    props: dict[str, Any] = {}
    takers: dict[str, list[str]] = {}
    sections: list[str] = []
    for tool, marks in members:
        actions = merge_actions(marks["merge"])
        passes = isinstance(marks["merge"]["action"], list)
        own = tool["input_schema"].get("properties", {})
        inputs = [k for k in own if not (passes and k == field)]
        for key in inputs:
            if key in props and _without_description(props[key]) != _without_description(own[key]):
                raise SystemExit(f"{name}: input {key} differs between its actions")
            props.setdefault(key, own[key])
            takers.setdefault(key, []).extend(actions)
        route = _action_route(tool, inputs, passes)
        for action in actions:
            if action in routes:
                raise SystemExit(f"{name}: action {action} names two operations")
            routes[action] = route
        sections.append(f"`{'`, `'.join(actions)}`: {tool['description']}")
    every_action = list(routes)
    _label_partial_inputs(props, takers, every_action)
    required = sorted(k for k in props if all(k in r["required"] for r in routes.values()))
    picker = {
        "type": "string",
        "enum": every_action,
        "description": f"What to do: {', '.join(every_action)}.",
    }
    return {
        "name": name,
        "description": (
            f"{group['description'].strip()}\n\nSet `{field}` to pick what to do.\n\n"
            + "\n\n".join(sections)
        ),
        "input_schema": {
            "type": "object",
            "properties": {field: picker, **props},
            "required": [field, *required],
            "additionalProperties": True,
        },
        "annotations": _merged_annotations(group, members),
        "field": field,
        "actions": routes,
    }


def annotations_for(marks: dict[str, Any]) -> dict[str, Any]:
    """MCP annotations, set explicitly because the spec defaults are conservative."""
    if marks["effect"] == "read":
        return {
            "title": marks["title"],
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": False,
        }
    return {
        "title": marks["title"],
        "readOnlyHint": False,
        "destructiveHint": marks["effect"] == "destructive",
        "openWorldHint": bool(marks.get("open-world")),
    }


def apply_briefs(spec: dict[str, Any]) -> None:
    """Swap each schema marked x-mcp-brief for a free-form object described by that line.

    A large shape repeated across tools (post-call actions) then costs one line in each.
    """
    for name, schema in (spec.get("components", {}).get("schemas") or {}).items():
        if not isinstance(schema, dict) or "x-mcp-brief" not in schema:
            continue
        brief = schema["x-mcp-brief"]
        if not isinstance(brief, str) or not brief.strip() or "\n" in brief or len(brief) > 400:
            raise SystemExit(f"bad x-mcp-brief on {name}: one line of text, 400 chars at most")
        spec["components"]["schemas"][name] = {
            "type": "object",
            "additionalProperties": True,
            "description": brief,
        }


def build_tools(
    spec: dict[str, Any], operator_only: Iterable[str] = ()
) -> tuple[list[dict[str, Any]], list[str]]:
    """Every exposed tool, sorted by name, and the operations left off."""
    operator_only = set(operator_only)
    apply_briefs(spec)
    tools: list[dict[str, Any]] = []
    skipped: list[str] = []
    to_merge: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = {}
    for path, methods in spec.get("paths", {}).items():
        path_item_params = methods.get("parameters", []) or []
        for method, op in methods.items():
            if method not in {"get", "post", "put", "patch", "delete"}:
                continue
            op_id = op.get("operationId") or slug(f"{method}_{path}")
            marks = mcp_marks(op_id, method, op)
            if "hidden" in marks:
                skipped.append(f"{method.upper()} {path}")
                continue
            strip_params(op, list(marks.get("hide-params") or []))
            tool = build_tool(path, method, op, path_item_params, spec)
            tool["annotations"] = annotations_for(marks)
            if op_id in operator_only:
                tool["operator_only"] = True
            if "merge" in marks:
                to_merge.setdefault(marks["merge"]["tool"], []).append((tool, marks))
            else:
                tools.append(tool)
    groups = spec.get("x-mcp-tools") or {}
    single_names = {t["name"] for t in tools}
    for name, members in to_merge.items():
        if name in single_names:
            raise SystemExit(f"{name} is both a merged tool and another tool")
        tools.append(merged_tool(name, _merge_group(name, groups), members))
    tools.sort(key=lambda t: t["name"])
    return tools, skipped


def check(spec_hash: str, internal_hash: str, tools: list[dict[str, Any]]) -> int:
    """Compare a fresh generation against the committed sentinel + registry."""
    # Imported here so a plain regen never depends on the committed output.
    from app._generated.tools import TOOLS as committed

    problems: list[str] = []
    sentinel = dict(
        line.split(": ", 1)  # type: ignore[misc]
        for line in OUT_HASH.read_text().splitlines()
        if ": " in line
    )
    if sentinel.get("openapi_spec_sha256") != spec_hash:
        problems.append(
            f"spec moved: committed {sentinel.get('openapi_spec_sha256', '?')[:12]}, "
            f"upstream {spec_hash[:12]}"
        )
    if sentinel.get("internal_spec_sha256") != internal_hash:
        problems.append(f"{INTERNAL_SPEC_PATH.name} changed since the last regen")

    fresh_names = {t["name"] for t in tools}
    committed_names = {t["name"] for t in committed}
    if added := sorted(fresh_names - committed_names):
        problems.append(f"upstream added tools not exposed: {', '.join(added)}")
    if gone := sorted(committed_names - fresh_names):
        problems.append(f"exposed tools no longer in the spec: {', '.join(gone)}")

    if problems:
        for p in problems:
            sys.stderr.write(f"drift: {p}\n")
        sys.stderr.write("run scripts/regen.py and commit the result\n")
        return 1
    print(f"in sync. {len(tools)} tools, spec {spec_hash[:12]}.")
    return 0


def main() -> int:
    spec_bytes, spec_source = load_spec_bytes(SPEC_SOURCE)
    spec = yaml.safe_load(spec_bytes)
    spec_name = spec_source.rsplit("/", 1)[-1]
    spec_is_url = spec_source.startswith("http")
    internal_bytes = INTERNAL_SPEC_PATH.read_bytes()
    operator_only = merge_internal(spec, yaml.safe_load(internal_bytes) or {})
    tools, skipped = build_tools(spec, operator_only)

    # Drift sentinel: hash the spec so a checkout can verify tools.py is in
    # sync with the source of truth.
    spec_hash = hashlib.sha256(spec_bytes).hexdigest()
    internal_hash = hashlib.sha256(internal_bytes).hexdigest()

    if "--check" in sys.argv[1:]:
        return check(spec_hash, internal_hash, tools)

    # Embed the registry as a JSON string and load it at import time so the
    # generated module stays valid Python regardless of whether descriptions
    # contain Python-incompatible literals (true / null / lambda / etc.).
    tools_json = json.dumps(tools, indent=4, ensure_ascii=False)
    body = f'''"""Auto-generated MCP tool registry. Do not edit by hand.

Run `./.venv/bin/python scripts/regen.py` after the upstream OpenAPI spec
changes.

Source spec:   {spec_name}   sha256={spec_hash[:12]}
Internal spec: {INTERNAL_SPEC_PATH.name}   sha256={internal_hash[:12]}
"""
from __future__ import annotations

import json
from typing import Any, Final


Tool = dict[str, Any]


_TOOLS_JSON = r"""{tools_json}"""

TOOLS: Final[list[Tool]] = json.loads(_TOOLS_JSON)
'''
    OUT_TOOLS.parent.mkdir(parents=True, exist_ok=True)
    OUT_TOOLS.write_text(body)

    meta_lines = [f"openapi_spec: {spec_name}"]
    if spec_is_url:
        meta_lines.append(f"openapi_spec_url: {spec_source}")
    meta_lines += [
        f"openapi_spec_sha256: {spec_hash}",
        f"internal_spec: {INTERNAL_SPEC_PATH.name}",
        f"internal_spec_sha256: {internal_hash}",
        f"tool_count: {len(tools)}",
    ]
    OUT_HASH.write_text("\n".join(meta_lines) + "\n")

    print(f"done. {len(tools)} tools, {len(skipped)} skipped.")
    if skipped:
        for s in skipped:
            print(f"  skipped: {s}")
    print(f"  spec hash: {spec_hash[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
