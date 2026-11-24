from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from app.procedures import split_frontmatter

SKILLS_EXTENSION = "io.modelcontextprotocol/skills"
SKILLS_CACHE: dict[str, Any] = {"ttlMs": 3_600_000, "cacheScope": "public"}


class Reach(Enum):
    EVERY_ENDPOINT = "every_endpoint"
    FULL_ENDPOINT_ONLY = "full_endpoint_only"
    NOT_SERVED = "not_served"


REACH: dict[str, Reach] = {
    "omnidim-audit-calls": Reach.EVERY_ENDPOINT,
    "omnidim-build-agent": Reach.FULL_ENDPOINT_ONLY,
    "omnidim-build-workflow": Reach.FULL_ENDPOINT_ONLY,
    "omnidim-onboard-client": Reach.FULL_ENDPOINT_ONLY,
    "omnidim-run-campaign": Reach.FULL_ENDPOINT_ONLY,
    "omnidim-connect": Reach.NOT_SERVED,
}


@dataclass(frozen=True)
class SkillFile:
    uri: str
    text: str
    digest: str
    size: int


@dataclass(frozen=True)
class Skill:
    uri: str
    frontmatter: dict[str, Any]
    files: tuple[SkillFile, ...]
    reach: Reach

    def entry(self) -> dict[str, Any]:
        return {
            "uri": self.uri,
            "frontmatter": self.frontmatter,
            "resources": [{"uri": f.uri, "digest": f.digest, "size": f.size} for f in self.files],
        }

    def served_on(self, *, read_only: bool) -> bool:
        return self.reach is Reach.EVERY_ENDPOINT or not read_only


def _skill_file(name: str, folder: Path, path: Path) -> SkillFile:
    if path.suffix != ".md":
        raise ValueError(f"{path}: skills serve markdown files only")
    raw = path.read_bytes()
    return SkillFile(
        uri=f"skill://{name}/{path.relative_to(folder).as_posix()}",
        text=raw.decode("utf-8"),
        digest="sha256:" + hashlib.sha256(raw).hexdigest(),
        size=len(raw),
    )


def load_skills(root: Path, reach: dict[str, Reach]) -> dict[str, Skill]:
    folders = sorted(p for p in root.iterdir() if p.is_dir())
    unknown = {p.name for p in folders} ^ set(reach)
    if unknown:
        raise ValueError(f"give every skill folder a REACH entry, and no other: {sorted(unknown)}")
    skills: dict[str, Skill] = {}
    for folder in folders:
        name = folder.name
        if reach[name] is Reach.NOT_SERVED:
            continue
        frontmatter, _ = split_frontmatter(folder / "SKILL.md")
        if frontmatter.get("name") != name:
            raise ValueError(f"{folder}: SKILL.md must be named {name}, like its folder")
        paths = sorted(
            (p for p in folder.rglob("*") if p.is_file()),
            key=lambda p: (p.name != "SKILL.md", p.as_posix()),
        )
        uri = f"skill://{name}/SKILL.md"
        files = tuple(_skill_file(name, folder, p) for p in paths)
        skills[uri] = Skill(uri, frontmatter, files, reach[name])
    return skills


_SKILLS = load_skills(Path(__file__).parent / "vendor" / "omnidim-skills" / "skills", REACH)
_FILES = {f.uri: (skill, f) for skill in _SKILLS.values() for f in skill.files}


def skill_entries(*, read_only: bool) -> list[dict[str, Any]]:
    return [s.entry() for s in _SKILLS.values() if s.served_on(read_only=read_only)]


def skill_entry(uri: str, *, read_only: bool) -> dict[str, Any] | None:
    skill = _SKILLS.get(uri)
    return skill.entry() if skill and skill.served_on(read_only=read_only) else None


def read_skill_file(uri: str, *, read_only: bool) -> dict[str, Any] | None:
    found = _FILES.get(uri)
    if found is None or not found[0].served_on(read_only=read_only):
        return None
    return {"contents": [{"uri": uri, "mimeType": "text/markdown", "text": found[1].text}]}
