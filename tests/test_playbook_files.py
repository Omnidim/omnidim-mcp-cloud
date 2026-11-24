import re
from pathlib import Path

import pytest
import yaml

from app._generated.tools import TOOLS
from app.procedures import (
    DEMO_OFFER_RULE,
    EXTRA_TOOLS,
    GUIDE_NAMES,
    PLAYBOOK_NAMES,
    build_prompt,
    guide_text,
    prompts_for_listing,
    read_resource,
    resources_for_listing,
)

SKILLS = Path(__file__).resolve().parents[1] / "app" / "vendor" / "omnidim-skills"
SERVED_TOOLS = {t["name"] for t in (*TOOLS, *EXTRA_TOOLS)}
NOT_TOOLS = {"requestBody"}


def _frontmatter(text: str) -> tuple[dict[str, str], str]:
    m = re.match(r"^---\n(.*?)\n---\n+", text, flags=re.S)
    assert m, "the file must start with YAML frontmatter"
    meta = yaml.safe_load(m.group(1))
    assert isinstance(meta, dict)
    return meta, text[m.end() :]


def _playbook_files() -> list[Path]:
    return sorted(p for p in (SKILLS / "skills").glob("*/*.md") if p.name != "SKILL.md")


def test_every_playbook_file_is_served_by_name() -> None:
    names = {p.stem.replace("-", "_") for p in _playbook_files()}
    assert names <= set(PLAYBOOK_NAMES), f"not served: {sorted(names - set(PLAYBOOK_NAMES))}"
    for path in _playbook_files():
        _, text = _frontmatter(path.read_text())
        body = text.split("\n", 1)[1].strip()
        assert body in (guide_text(path.stem.replace("-", "_")) or "")


def test_every_guide_file_is_a_resource() -> None:
    listed = {r["uri"]: r for r in resources_for_listing()}
    for path in sorted((SKILLS / "guides").glob("*/*.md")):
        uri = f"omnidim://{path.parent.name}/{path.stem}"
        meta, body = _frontmatter(path.read_text())
        assert listed[uri]["name"] == meta["name"]
        assert listed[uri]["description"] == meta["description"]
        resource = read_resource(uri)
        assert resource is not None
        assert resource["contents"][0]["text"].startswith(body.strip())
        assert uri in GUIDE_NAMES


def test_prompt_inputs_follow_the_playbook_text() -> None:
    built = build_prompt(
        "provision_agent", {"purpose": "book dental appointments", "test_number": "+15551234567"}
    )
    assert built is not None
    text = built["messages"][0]["content"]["text"]
    _, steps = _frontmatter(
        (SKILLS / "skills" / "omnidim-build-agent" / "provision-agent.md").read_text()
    )
    assert steps.split("\n", 1)[1].strip() in text
    tail = text[text.index("The user gave") :]
    assert "purpose: book dental appointments" in tail
    assert "test_number: +15551234567" in tail


def test_prompt_inputs_are_one_line_and_only_the_declared_ones() -> None:
    built = build_prompt(
        "audit_calls", {"focus": "  why\n\nfailed  ", "agent_id": " ", "evil": "x"}
    )
    assert built is not None
    tail = built["messages"][0]["content"]["text"].split("The user gave:\n", 1)[1]
    assert tail == "- focus: why failed"


def test_the_routing_guide_is_listed_first() -> None:
    assert resources_for_listing()[0]["uri"] == "omnidim://guide/routing"
    assert GUIDE_NAMES[len(PLAYBOOK_NAMES)] == "omnidim://guide/routing"


def test_a_prompt_without_inputs_is_the_playbook_alone() -> None:
    built = build_prompt("audit_calls", {})
    assert built is not None
    assert "The user gave" not in built["messages"][0]["content"]["text"]


def test_the_demo_offer_stays_out_of_the_public_files() -> None:
    public = "".join(p.read_text() for p in SKILLS.rglob("*.md"))
    assert DEMO_OFFER_RULE not in public
    assert DEMO_OFFER_RULE in (guide_text("omnidim://guide/routing") or "")
    assert build_prompt("book_demo", {}) is not None


@pytest.mark.parametrize("skill", sorted(p.parent.name for p in SKILLS.glob("skills/*/SKILL.md")))
def test_skill_frontmatter_follows_the_agent_skills_spec(skill: str) -> None:
    meta, _ = _frontmatter((SKILLS / "skills" / skill / "SKILL.md").read_text())
    assert meta["name"] == skill
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", meta["name"])
    assert 0 < len(meta["description"]) <= 1024
    assert "Use when" in meta["description"]


def test_every_tool_a_skill_names_is_served() -> None:
    text = "".join(p.read_text() for p in SKILLS.rglob("*.md"))
    named = set(re.findall(r"`([a-z]+[A-Z][A-Za-z]*)`", text)) - NOT_TOOLS
    assert named
    assert named <= SERVED_TOOLS, f"unknown tools: {sorted(named - SERVED_TOOLS)}"


def test_every_link_in_a_skill_folder_points_at_a_file() -> None:
    for skill in (SKILLS / "skills").iterdir():
        for page in skill.glob("*.md"):
            for link in re.findall(r"\]\(([^)#:]+\.md)\)", page.read_text()):
                assert (skill / link).is_file(), f"{page}: {link}"


def test_every_omnidim_link_is_served() -> None:
    text = "".join(p.read_text() for p in SKILLS.rglob("*.md"))
    for uri in set(re.findall(r"omnidim://[a-z]+/[a-z0-9-]+", text)):
        assert uri in GUIDE_NAMES, uri


def test_each_playbook_declares_its_own_prompt_inputs() -> None:
    listed = {p["name"]: p for p in prompts_for_listing()}
    for path in _playbook_files():
        meta, body = _frontmatter(path.read_text())
        assert meta["name"] == path.stem.replace("-", "_")
        assert listed[meta["name"]]["arguments"] == meta.get("arguments", [])
        assert listed[meta["name"]]["description"] == body.split("\n", 1)[0].removeprefix("# ")
