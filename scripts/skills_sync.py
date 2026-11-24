from __future__ import annotations

import io
import json
import shutil
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

REPO = "Omnidim/skills"
VENDOR = Path(__file__).resolve().parents[1] / "app" / "vendor" / "omnidim-skills"
FOLDERS = ("skills", "guides")
USAGE = "uv run python scripts/skills_sync.py <branch, tag or commit of Omnidim/skills>"


def _commit(ref: str) -> str:
    url = f"https://api.github.com/repos/{REPO}/commits/{ref}"
    with urllib.request.urlopen(url, timeout=30) as res:
        sha: str = json.load(res)["sha"]
    return sha


def _unpack(archive: tarfile.TarFile, into: Path) -> None:
    for member in archive.getmembers():
        parts = Path(member.name).parts[1:]
        if not parts or parts[0] not in FOLDERS or not member.isfile():
            continue
        if ".." in parts:
            raise ValueError(f"unsafe path in the archive: {member.name}")
        target = into.joinpath(*parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        extracted = archive.extractfile(member)
        assert extracted is not None
        target.write_bytes(extracted.read())


def sync(ref: str) -> str:
    sha = _commit(ref)
    url = f"https://codeload.github.com/{REPO}/tar.gz/{sha}"
    with urllib.request.urlopen(url, timeout=60) as res:
        archive = tarfile.open(fileobj=io.BytesIO(res.read()), mode="r:gz")
    VENDOR.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(dir=VENDOR.parent))
    try:
        _unpack(archive, staging)
        for folder in FOLDERS:
            if not any((staging / folder).rglob("*.md")):
                raise ValueError(f"{REPO}@{sha} has no markdown under {folder}/")
        (staging / "SOURCE").write_text(f"https://github.com/{REPO}/tree/{sha}\n")
    except Exception:
        shutil.rmtree(staging)
        raise
    shutil.rmtree(VENDOR, ignore_errors=True)
    staging.rename(VENDOR)
    return sha


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(USAGE)
    print(sync(sys.argv[1]))
