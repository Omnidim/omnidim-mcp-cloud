import importlib.util
from pathlib import Path

from app.procedures import GUIDE_NAMES, guide_text

_spec = importlib.util.spec_from_file_location(
    "export_npm_playbooks",
    Path(__file__).resolve().parents[1] / "scripts" / "export_npm_playbooks.py",
)
assert _spec is not None and _spec.loader is not None
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)


def test_the_npm_export_carries_every_playbook_and_guide_as_readguide_serves_it() -> None:
    exported = _module.playbooks()
    entries = exported["playbooks"] + exported["guides"]
    names = [e.get("uri", e.get("name")) for e in entries]
    assert sorted(names) == sorted(GUIDE_NAMES)
    for guide in exported["guides"]:
        assert guide["text"] == guide_text(guide["uri"])
    for playbook in exported["playbooks"]:
        unfilled = next(v for v in playbook["variants"] if v["given"] == [])
        assert unfilled["text"] == guide_text(playbook["name"])
        assert len(playbook["variants"]) == 2 ** len(playbook["arguments"])


def test_each_variant_carries_a_marker_for_every_given_value() -> None:
    exported = _module.playbooks()["playbooks"]
    campaign = next(p for p in exported if p["name"] == "build_outbound_campaign")
    pinned = next(v for v in campaign["variants"] if v["given"] == ["agent_id", "goal"])
    assert _module.marker("agent_id") in pinned["text"]
    assert "bot_id" in pinned["text"]


def test_the_npm_export_carries_each_served_skill_byte_for_byte() -> None:
    vendor = Path(__file__).resolve().parents[1] / "app" / "vendor" / "omnidim-skills" / "skills"

    skills = {s["name"]: s for s in _module.playbooks()["skills"]}

    assert set(skills) == {
        "omnidim-audit-calls",
        "omnidim-build-agent",
        "omnidim-build-workflow",
        "omnidim-onboard-client",
        "omnidim-run-campaign",
    }
    assert [n for n, s in skills.items() if s["readOnly"]] == ["omnidim-audit-calls"]
    for name, skill in skills.items():
        on_disk = {p.name: p.read_text() for p in (vendor / name).iterdir()}
        assert {f["path"]: f["text"] for f in skill["files"]} == on_disk
