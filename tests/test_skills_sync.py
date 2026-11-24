import importlib.util
import io
import tarfile
from pathlib import Path

import pytest

_spec = importlib.util.spec_from_file_location(
    "skills_sync", Path(__file__).resolve().parents[1] / "scripts" / "skills_sync.py"
)
assert _spec and _spec.loader
skills_sync = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(skills_sync)


def _archive(files: dict[str, str]) -> tarfile.TarFile:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for name, text in files.items():
            data = text.encode()
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    buf.seek(0)
    return tarfile.open(fileobj=buf, mode="r:gz")


def test_only_skills_and_guides_are_copied(tmp_path: Path) -> None:
    archive = _archive(
        {
            "skills-abc/skills/x/SKILL.md": "s",
            "skills-abc/guides/guide/y.md": "g",
            "skills-abc/README.md": "r",
            "skills-abc/.github/workflows/ci.yml": "c",
        }
    )
    skills_sync._unpack(archive, tmp_path)
    copied = sorted(str(p.relative_to(tmp_path)) for p in tmp_path.rglob("*") if p.is_file())
    assert copied == ["guides/guide/y.md", "skills/x/SKILL.md"]


def test_a_path_that_climbs_out_is_refused(tmp_path: Path) -> None:
    archive = _archive({"skills-abc/skills/../../evil.md": "x"})
    with pytest.raises(ValueError, match="unsafe"):
        skills_sync._unpack(archive, tmp_path / "in")
    assert not (tmp_path / "evil.md").exists()


def test_a_failed_swap_keeps_the_old_copy(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vendor = tmp_path / "omnidim-skills"
    (vendor / "skills").mkdir(parents=True)
    (vendor / "SOURCE").write_text("old\n")
    staging = tmp_path / "staging"
    staging.mkdir()
    real_rename = Path.rename

    def rename(self: Path, target: Path) -> Path:
        if self == staging:
            raise OSError("disk full")
        return real_rename(self, target)

    monkeypatch.setattr(Path, "rename", rename)
    with pytest.raises(OSError):
        skills_sync._swap(staging, vendor)
    assert (vendor / "SOURCE").read_text() == "old\n"
