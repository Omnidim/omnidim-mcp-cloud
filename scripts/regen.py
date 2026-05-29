#!/usr/bin/env python3
"""Regenerate app/_generated/tools.py from the OmniDimension OpenAPI spec.

Reads:
  ../omnidim-docs/openapi/omnidim.yaml         (or $SPEC override)
  ../omnidim-docs/openapi/mcp-config.yaml      (shared exclude list)

Writes:
  app/_generated/tools.py                       (Python tool registry)
  app/_generated/.spec.yml                      (sha256 of spec + config)

Run after pulling new spec changes:
  ./.venv/bin/python scripts/regen.py
CI fails if the artifact is out of date.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SPEC = ROOT.parent / "omnidim-docs" / "openapi" / "omnidim.yaml"
DEFAULT_CONFIG = ROOT.parent / "omnidim-docs" / "openapi" / "mcp-config.yaml"

SPEC_PATH = Path(os.environ.get("SPEC", DEFAULT_SPEC))
CONFIG_PATH = Path(os.environ.get("MCP_CONFIG", DEFAULT_CONFIG))

OUT_TOOLS = ROOT / "app" / "_generated" / "tools.py"
OUT_HASH = ROOT / "app" / "_generated" / ".spec.yml"


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        sys.stderr.write(f"missing file: {path}\n")
        sys.exit(1)
    return yaml.safe_load(path.read_text())


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

    params = effective_parameters(path_item_params, op.get("parameters", []))
    request_body = op.get("requestBody")
    if request_body is not None and spec is not None:
        request_body = resolve_refs(request_body, spec)
    schema = merge_schema(params, request_body)
    # Mark which inputs go in the path so the dispatcher can substitute them.
    path_param_names = [p["name"] for p in params if p.get("in") == "path"]
    query_param_names = [p["name"] for p in params if p.get("in") == "query"]
    return {
        "name": op_id,
        "description": full_desc,
        "input_schema": schema,
        "method": method.upper(),
        "path": path,
        "path_params": path_param_names,
        "query_params": query_param_names,
    }


def is_excluded(path: str, op_id: str, exclude: dict[str, Any]) -> bool:
    if path in (exclude.get("paths") or []):
        return True
    if op_id in (exclude.get("operation_ids") or []):
        return True
    return False


def main() -> int:
    spec = load_yaml(SPEC_PATH)
    config = load_yaml(CONFIG_PATH)
    exclude = config.get("exclude", {}) or {}

    tools: list[dict[str, Any]] = []
    skipped: list[str] = []

    for path, methods in spec.get("paths", {}).items():
        path_item_params = methods.get("parameters", []) or []
        for method, op in methods.items():
            if method not in {"get", "post", "put", "patch", "delete"}:
                continue
            op_id = op.get("operationId") or slug(f"{method}_{path}")
            if is_excluded(path, op_id, exclude):
                skipped.append(f"{method.upper()} {path}")
                continue
            tools.append(build_tool(path, method, op, path_item_params, spec))

    tools.sort(key=lambda t: t["name"])

    # Drift sentinel: hash the spec + config so CI can verify tools.py is
    # in sync with the source of truth.
    spec_hash = hashlib.sha256(SPEC_PATH.read_bytes()).hexdigest()
    config_hash = hashlib.sha256(CONFIG_PATH.read_bytes()).hexdigest()

    # Embed the registry as a JSON string and load it at import time so the
    # generated module stays valid Python regardless of whether descriptions
    # contain Python-incompatible literals (true / null / lambda / etc.).
    tools_json = json.dumps(tools, indent=4, ensure_ascii=False)
    body = f'''"""Auto-generated MCP tool registry. Do not edit by hand.

Run `./.venv/bin/python scripts/regen.py` after editing the upstream
OpenAPI spec or the shared mcp-config.yaml.

Source spec:   {SPEC_PATH.name}   sha256={spec_hash[:12]}
Shared config: {CONFIG_PATH.name}  sha256={config_hash[:12]}
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

    OUT_HASH.write_text(
        f"openapi_spec: {SPEC_PATH.name}\n"
        f"openapi_spec_sha256: {spec_hash}\n"
        f"mcp_config: {CONFIG_PATH.name}\n"
        f"mcp_config_sha256: {config_hash}\n"
        f"tool_count: {len(tools)}\n"
    )

    print(f"done. {len(tools)} tools, {len(skipped)} skipped.")
    if skipped:
        for s in skipped:
            print(f"  skipped: {s}")
    print(f"  spec hash: {spec_hash[:12]}")
    print(f"  config hash: {config_hash[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
