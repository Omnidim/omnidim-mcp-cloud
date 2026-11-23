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
    for entry, name in zip(entries, names, strict=True):
        assert entry["text"] == guide_text(name)
    assert all(p["arguments"] is not None for p in exported["playbooks"])
