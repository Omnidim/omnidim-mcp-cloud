from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.procedures import (
    _PLAYBOOK_NOTE,
    _RESOURCES,
    PLAYBOOK_NAMES,
    build_prompt,
    guide_text,
    prompts_for_listing,
)


def marker(arg: str) -> str:
    return f"\u27e6{arg}\u27e7"


def variants(prompt: dict[str, Any]) -> list[dict[str, Any]]:
    names = [a["name"] for a in prompt["arguments"]]
    out = []
    for given in itertools.chain.from_iterable(
        itertools.combinations(names, n) for n in range(len(names) + 1)
    ):
        built = build_prompt(prompt["name"], {a: marker(a) for a in given})
        assert built is not None
        steps = built["messages"][0]["content"]["text"]
        text = f"# {prompt['description']}\n\n{_PLAYBOOK_NOTE}\n\n{steps}"
        out.append({"given": sorted(given), "text": text})
    return out


def playbooks() -> dict[str, Any]:
    prompts = {p["name"]: p for p in prompts_for_listing()}
    return {
        "playbooks": [
            {**prompts[name], "variants": variants(prompts[name])} for name in PLAYBOOK_NAMES
        ],
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
