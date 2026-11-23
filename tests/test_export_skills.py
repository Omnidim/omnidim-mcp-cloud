"""scripts/export_skills.py writes Agent Skills from the server's own prompts and guides."""

import re
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from export_skills import export

from app._generated.tools import TOOLS
from app.procedures import EXTRA_TOOLS

SERVED = {t["name"] for t in (*TOOLS, *EXTRA_TOOLS)}
NOT_TOOLS = {"requestBody"}
SKILLS = [
    "omnidim-audit-calls",
    "omnidim-build-agent",
    "omnidim-build-workflow",
    "omnidim-connect",
    "omnidim-onboard-client",
    "omnidim-run-campaign",
]


@pytest.fixture
def out(tmp_path: Path) -> Path:
    export(tmp_path)
    return tmp_path


def _frontmatter(text: str) -> dict[str, str]:
    m = re.match(r"^---\n(.*?)\n---\n", text, flags=re.S)
    assert m, "SKILL.md must start with YAML frontmatter"
    meta = yaml.safe_load(m.group(1))
    assert isinstance(meta, dict)
    return meta


def test_writes_every_skill(out: Path) -> None:
    assert sorted(p.name for p in out.iterdir() if p.is_dir()) == SKILLS


@pytest.mark.parametrize("skill", SKILLS)
def test_frontmatter_follows_the_spec(out: Path, skill: str) -> None:
    meta = _frontmatter((out / skill / "SKILL.md").read_text())
    assert meta["name"] == skill
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", meta["name"])
    assert 0 < len(meta["description"]) <= 1024
    assert "Use when" in meta["description"]


@pytest.mark.parametrize("skill", SKILLS)
def test_every_tool_named_is_one_the_server_serves(out: Path, skill: str) -> None:
    text = "\n".join(p.read_text() for p in (out / skill).rglob("*.md"))
    # camelCase in backticks is a tool name, except fields the guides spell out.
    named = {n for n in re.findall(r"`([a-z]+[A-Z][A-Za-z]*)`", text)} - NOT_TOOLS
    assert named, "a skill should name the tools it uses"
    assert named <= SERVED, f"unknown tools: {sorted(named - SERVED)}"


@pytest.mark.parametrize("skill", SKILLS)
def test_links_point_at_files_that_exist(out: Path, skill: str) -> None:
    text = (out / skill / "SKILL.md").read_text()
    for link in re.findall(r"\]\((references/[^)]+)\)", text):
        assert (out / skill / link).is_file(), link
    assert "omnidim://" not in "\n".join(p.read_text() for p in (out / skill).rglob("*.md"))


def test_client_onboarding_keeps_every_rule_that_protects_money(out: Path) -> None:
    text = (out / "omnidim-onboard-client" / "SKILL.md").read_text()
    for guard in [
        "Idempotency-Key",
        "/reseller/credits/logs",
        "monthly_rental_usd",
        "Check its balance and numbers before any retry",
        "Never retry an Aadhaar or `redirect` step in a loop",
    ]:
        assert guard in text, guard


def test_export_is_deterministic(tmp_path: Path) -> None:
    a, b = tmp_path / "a", tmp_path / "b"
    export(a)
    export(b)
    files = sorted(p.relative_to(a) for p in a.rglob("*") if p.is_file())
    assert files == sorted(p.relative_to(b) for p in b.rglob("*") if p.is_file())
    for f in files:
        assert (a / f).read_text() == (b / f).read_text()


@pytest.mark.parametrize("skill", SKILLS)
def test_skills_read_as_skills_not_mcp_prompts(out: Path, skill: str) -> None:
    from app.procedures import DEMO_OFFER_RULE

    text = "\n".join(p.read_text() for p in (out / skill).rglob("*.md"))
    assert not re.search(r"`[a-z_]+` prompt", text), "names an MCP prompt skill users lack"
    assert DEMO_OFFER_RULE not in text
    assert "(describe" not in text, "unfilled prompt default"
