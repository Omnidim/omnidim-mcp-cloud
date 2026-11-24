from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.procedures import (
    _PLAYBOOK_NOTE,
    PLAYBOOK_NAMES,
    build_prompt,
    guide_text,
    prompts_for_listing,
    resources_for_listing,
)
from app.skills import REACH, SKILLS_DIR, load_skills


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
                **r,
                "text": guide_text(r["uri"]),
            }
            for r in resources_for_listing()
            if r["mimeType"] == "text/markdown"
        ],
        "skills": [
            {
                "name": skill.frontmatter["name"],
                "readOnly": skill.served_on(read_only=True),
                "files": [{"path": f.uri.split("/", 3)[3], "text": f.text} for f in skill.files],
            }
            for skill in load_skills(SKILLS_DIR, REACH).values()
        ],
    }


if __name__ == "__main__":
    body = json.dumps(playbooks(), indent=2, ensure_ascii=False)
    Path(sys.argv[1]).write_text(f"export default {body};\n")
