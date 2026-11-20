#!/usr/bin/env python3
"""Regenerate app/_generated/tools.py from the OmniDimension OpenAPI spec.

By default the spec is fetched from the published docs site, so this runs
from a clean checkout. Set $SPEC to a local file path (or another https URL
on an allowed host) to override.

Reads:
  https://docs.omnidim.io/openapi.yaml          (spec; or $SPEC override)

Each operation's x-mcp block decides its tool: title, effect (read, write or
destructive), open-world, hide-params, or hidden. An operation without one
fails the regen, so nothing reaches agents before someone decides how.

Writes:
  app/_generated/tools.py                       (Python tool registry)
  app/_generated/.spec.yml                      (sha256 of the spec)

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
    # Mark which inputs go in the path so the dispatcher can substitute them.
    path_param_names = [p["name"] for p in params if p.get("in") == "path"]
    query_param_names = [p["name"] for p in params if p.get("in") == "query"]
    header_param_names = [p["name"] for p in params if p.get("in") == "header"]
    return {
        "name": op_id,
        "description": full_desc,
        "input_schema": schema,
        "method": method.upper(),
        "path": path,
        "path_params": path_param_names,
        "query_params": query_param_names,
        "header_params": header_param_names,
    }


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


_MCP_KEYS = {"title", "effect", "open-world", "hide-params", "hidden"}
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
        if set(marks) != {"hidden"} or not str(marks["hidden"]).strip():
            raise bad("hidden takes a reason and no other keys")
        return marks
    if not str(marks.get("title", "")).strip():
        raise bad("title is required")
    if marks.get("effect") not in _EFFECTS:
        raise bad(f"effect must be one of {sorted(_EFFECTS)}")
    if method == "get" and marks["effect"] != "read":
        raise bad("a GET is a read")
    if marks.get("open-world") not in (None, True) or (
        marks.get("open-world") and marks["effect"] == "read"
    ):
        raise bad("open-world is true on a write, or absent")
    return marks


def annotations_for(marks: dict[str, Any]) -> dict[str, Any]:
    """MCP annotations, set explicitly because the spec defaults are conservative."""
    if marks["effect"] == "read":
        return {"title": marks["title"], "readOnlyHint": True, "openWorldHint": False}
    return {
        "title": marks["title"],
        "readOnlyHint": False,
        "destructiveHint": marks["effect"] == "destructive",
        "openWorldHint": bool(marks.get("open-world")),
    }


def build_tools(spec: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    """Every exposed tool, sorted by name, and the operations left off."""
    tools: list[dict[str, Any]] = []
    skipped: list[str] = []
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
            tools.append(tool)
    tools.sort(key=lambda t: t["name"])
    return tools, skipped


def check(spec_hash: str, tools: list[dict[str, Any]]) -> int:
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
    tools, skipped = build_tools(spec)

    # Drift sentinel: hash the spec so a checkout can verify tools.py is in
    # sync with the source of truth.
    spec_hash = hashlib.sha256(spec_bytes).hexdigest()

    if "--check" in sys.argv[1:]:
        return check(spec_hash, tools)

    # Embed the registry as a JSON string and load it at import time so the
    # generated module stays valid Python regardless of whether descriptions
    # contain Python-incompatible literals (true / null / lambda / etc.).
    tools_json = json.dumps(tools, indent=4, ensure_ascii=False)
    body = f'''"""Auto-generated MCP tool registry. Do not edit by hand.

Run `./.venv/bin/python scripts/regen.py` after the upstream OpenAPI spec
changes.

Source spec:   {spec_name}   sha256={spec_hash[:12]}
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
