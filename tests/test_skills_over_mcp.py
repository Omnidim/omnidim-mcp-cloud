import hashlib
from pathlib import Path
from typing import Any

import pytest
import yaml
from httpx import AsyncClient

from app.skills import REACH, Reach, load_skills
from tests.test_mcp_modern_protocol import _modern
from tests.test_mcp_transport import _mint_access_token

VENDOR = Path(__file__).resolve().parents[1] / "app" / "vendor" / "omnidim-skills" / "skills"
FULL_SKILLS = {
    "omnidim-audit-calls",
    "omnidim-build-agent",
    "omnidim-build-workflow",
    "omnidim-run-campaign",
    "omnidim-troubleshoot",
}


async def _rpc(client: AsyncClient, token: str, path: str, method: str, params: Any = None) -> Any:
    return (await _modern(client, token, method, params, path=path)).json()


def _file_frontmatter(skill: str) -> dict[str, Any]:
    text = (VENDOR / skill / "SKILL.md").read_text()
    meta = yaml.safe_load(text.split("---\n", 2)[1])
    assert isinstance(meta, dict)
    return meta


async def test_list_serves_every_skill_but_connect(client: AsyncClient) -> None:
    token = await _mint_access_token(client)

    result = (await _rpc(client, token, "/mcp", "skills/list"))["result"]

    names = {s["frontmatter"]["name"] for s in result["skills"]}
    assert names == FULL_SKILLS
    assert result["ttlMs"] > 0
    assert result["cacheScope"] == "public"
    assert "nextCursor" not in result


async def test_entry_frontmatter_and_uri_match_the_skill_file(client: AsyncClient) -> None:
    token = await _mint_access_token(client)

    skills = (await _rpc(client, token, "/mcp", "skills/list"))["result"]["skills"]

    for skill in skills:
        name = skill["frontmatter"]["name"]
        assert skill["uri"] == f"skill://{name}/SKILL.md"
        assert skill["frontmatter"] == _file_frontmatter(name)


async def test_manifest_lists_every_file_with_the_digest_and_size_of_what_reads_return(
    client: AsyncClient,
) -> None:
    token = await _mint_access_token(client)
    skills = (await _rpc(client, token, "/mcp", "skills/list"))["result"]["skills"]
    build_agent = next(s for s in skills if s["frontmatter"]["name"] == "omnidim-build-agent")

    listed = {r["uri"] for r in build_agent["resources"]}
    folder = VENDOR / "omnidim-build-agent"
    on_disk = {f"skill://omnidim-build-agent/{p.name}" for p in folder.iterdir()}
    assert listed == on_disk

    for skill in skills:
        for resource in skill["resources"]:
            read = await _rpc(client, token, "/mcp", "resources/read", {"uri": resource["uri"]})
            content = read["result"]["contents"][0]
            raw = content["text"].encode("utf-8")
            assert content["uri"] == resource["uri"]
            assert content["mimeType"] == "text/markdown"
            on_disk = (VENDOR / resource["uri"].removeprefix("skill://")).read_bytes()
            assert raw == on_disk
            assert resource["size"] == len(on_disk)
            assert resource["digest"] == "sha256:" + hashlib.sha256(on_disk).hexdigest()


async def test_get_returns_the_same_entry_as_the_listing(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    listed = (await _rpc(client, token, "/mcp", "skills/list"))["result"]["skills"]
    uri = "skill://omnidim-run-campaign/SKILL.md"

    result = (await _rpc(client, token, "/mcp", "skills/get", {"uri": uri}))["result"]

    assert result["skill"] == next(s for s in listed if s["uri"] == uri)
    assert result["ttlMs"] > 0
    assert result["cacheScope"] == "public"


@pytest.mark.parametrize(
    "params",
    [
        {"uri": "skill://omnidim-connect/SKILL.md"},
        {"uri": "skill://omnidim-build-agent/design-agent.md"},
        {"uri": "skill://nope/SKILL.md"},
        {"uri": 7},
        {},
    ],
)
async def test_get_refuses_what_is_not_a_served_skill(client: AsyncClient, params: Any) -> None:
    token = await _mint_access_token(client)

    body = await _rpc(client, token, "/mcp", "skills/get", params)

    assert body["error"]["code"] == -32602


async def test_unserved_skill_files_cannot_be_read(client: AsyncClient) -> None:
    token = await _mint_access_token(client)

    body = await _rpc(
        client, token, "/mcp", "resources/read", {"uri": "skill://omnidim-connect/SKILL.md"}
    )

    assert body["error"]["code"] == -32602


async def test_readonly_serves_only_the_read_only_skills(client: AsyncClient) -> None:
    token = await _mint_access_token(client)

    skills = (await _rpc(client, token, "/mcp/readonly", "skills/list"))["result"]["skills"]
    get = await _rpc(
        client, token, "/mcp/readonly", "skills/get",
        {"uri": "skill://omnidim-build-agent/SKILL.md"},
    )
    read = await _rpc(
        client, token, "/mcp/readonly", "resources/read",
        {"uri": "skill://omnidim-build-agent/design-agent.md"},
    )

    names = [s["frontmatter"]["name"] for s in skills]
    assert names == ["omnidim-audit-calls", "omnidim-troubleshoot"]
    assert get["error"]["code"] == -32602
    assert read["error"]["code"] == -32602


async def test_skills_need_a_token(client: AsyncClient) -> None:
    res = await client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "skills/list"})

    assert res.status_code == 401


def test_every_vendored_skill_has_a_reach() -> None:
    assert set(REACH) == {p.name for p in VENDOR.iterdir() if p.is_dir()}


def test_a_skill_without_a_reach_stops_the_server_from_starting(tmp_path: Path) -> None:
    (tmp_path / "omnidim-new").mkdir()
    (tmp_path / "omnidim-new" / "SKILL.md").write_text("---\nname: omnidim-new\n---\n")

    with pytest.raises(ValueError, match="omnidim-new"):
        load_skills(tmp_path, {})


def test_a_skill_named_unlike_its_folder_stops_the_server_from_starting(tmp_path: Path) -> None:
    (tmp_path / "omnidim-new").mkdir()
    (tmp_path / "omnidim-new" / "SKILL.md").write_text("---\nname: other\ndescription: d\n---\n")

    with pytest.raises(ValueError, match="omnidim-new"):
        load_skills(tmp_path, {"omnidim-new": Reach.EVERY_ENDPOINT})
