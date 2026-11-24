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


def test_plugin_meets_the_claude_directory_rules(tmp_path: Path) -> None:
    import json
    import tomllib

    from export_skills import export_plugin

    export_plugin(tmp_path)
    server_version = tomllib.loads((Path(__file__).parents[1] / "pyproject.toml").read_text())[
        "project"
    ]["version"]
    manifest = json.loads((tmp_path / ".claude-plugin" / "plugin.json").read_text())
    assert manifest["name"] == "omnidim"
    assert manifest["displayName"] == "OmniDimension"
    assert manifest["version"] == server_version
    assert manifest["description"].startswith("Build, test and update voice AI phone agents")
    assert manifest["author"]["name"] == "OmniDimension"
    assert manifest["license"] == "Apache-2.0"
    assert manifest["privacyPolicyUrl"] == "https://omnidim.io/privacy-policy"
    icon = (tmp_path / ".claude-plugin" / "icon.png").read_bytes()
    assert icon[:8] == b"\x89PNG\r\n\x1a\n"
    width, height = int.from_bytes(icon[16:20]), int.from_bytes(icon[20:24])
    assert width == height and 512 <= width <= 2048, "the directory takes a square 512-2048 px icon"
    servers = json.loads((tmp_path / ".mcp.json").read_text())["mcpServers"]
    assert servers == {"omnidim": {"type": "http", "url": "https://mcp.omnidim.io/mcp"}}
    assert sorted(p.name for p in (tmp_path / "skills").iterdir()) == SKILLS
    (entry,) = json.loads((tmp_path / ".claude-plugin" / "marketplace.json").read_text())["plugins"]
    assert entry["source"] == "./"
    assert not {"strict", "skills", "mcpServers"} & entry.keys(), "plugin.json owns the contents"


def test_export_drops_skills_that_no_longer_exist(tmp_path: Path) -> None:
    (tmp_path / "omnidim-retired-skill").mkdir()
    (tmp_path / "omnidim-retired-skill" / "SKILL.md").write_text("old")
    export(tmp_path)
    assert sorted(p.name for p in tmp_path.iterdir()) == SKILLS
