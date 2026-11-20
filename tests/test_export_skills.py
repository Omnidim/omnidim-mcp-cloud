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
    "audit-calls",
    "build-agent",
    "build-workflow",
    "connect-omnidim",
    "run-outbound-campaign",
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


def test_writes_the_five_skills(out: Path) -> None:
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


def test_export_is_deterministic(tmp_path: Path) -> None:
    a, b = tmp_path / "a", tmp_path / "b"
    export(a)
    export(b)
    files = sorted(p.relative_to(a) for p in a.rglob("*") if p.is_file())
    assert files == sorted(p.relative_to(b) for p in b.rglob("*") if p.is_file())
    for f in files:
        assert (a / f).read_text() == (b / f).read_text()
