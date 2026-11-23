from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.procedures import _RESOURCES, PLAYBOOK_NAMES, guide_text, prompts_for_listing


def playbooks() -> dict[str, Any]:
    prompts = {p["name"]: p for p in prompts_for_listing()}
    return {
        "playbooks": [{**prompts[name], "text": guide_text(name)} for name in PLAYBOOK_NAMES],
        "guides": [
            {
                **{k: r[k] for k in ("uri", "name", "description", "mimeType")},
                "text": guide_text(r["uri"]),
            }
            for r in _RESOURCES
            if r["mimeType"] == "text/markdown"
        ],
    }


if __name__ == "__main__":
    body = json.dumps(playbooks(), indent=2, ensure_ascii=False)
    Path(sys.argv[1]).write_text(f"export default {body};\n")
