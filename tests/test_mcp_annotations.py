"""MCP tool annotations: unit logic + tools/list wiring."""
from typing import Any

from httpx import AsyncClient

from app._generated.tools import TOOLS
from app.procedures import EXTRA_TOOLS

from .test_mcp_transport import _mint_access_token

_BY_NAME = {t["name"]: t for t in (*TOOLS, *EXTRA_TOOLS)}


def tool_annotations(name: str, method: str) -> dict[str, Any]:
    """The marks a tool ships with. Regen writes them from the spec's x-mcp."""
    tool = _BY_NAME[name]
    # The old callers passed "POST" for any non-GET; only GET versus not matters.
    methods = {r["method"] for r in tool.get("actions", {"": tool}).values()}
    assert (methods == {"GET"}) == (method.upper() == "GET"), f"{name} is {methods}"
    return dict(tool["annotations"])


def test_every_generated_tool_has_a_title() -> None:
    """Regen adds tools; titles are hand-authored. Without this guard a new
    tool ships with no display name (the version-history tools did).
    """
    missing = [t["name"] for t in TOOLS if "title" not in t["annotations"]]
    assert missing == []


def test_version_overwrite_and_removal_are_destructive() -> None:
    for name in ("agentVersionActions",):
        a = tool_annotations(name, "POST")
        assert a["destructiveHint"] is True, name
        assert a["openWorldHint"] is False, name


def test_get_tools_are_read_only() -> None:
    a = tool_annotations("listAgents", "GET")
    assert a["readOnlyHint"] is True
    assert a["openWorldHint"] is False
    assert a["destructiveHint"] is False
    assert a["title"] == "List agents"


def test_plain_writes_are_not_destructive() -> None:
    a = tool_annotations("createAgent", "POST")
    assert a["readOnlyHint"] is False
    assert a["destructiveHint"] is False
    assert a["openWorldHint"] is False


def test_removals_are_destructive_not_open_world() -> None:
    for name in ("deleteAgent", "phoneNumberAgentActions"):
        a = tool_annotations(name, "POST")
        assert a["destructiveHint"] is True, name
        assert a["openWorldHint"] is False, name


def test_call_placing_tools_are_destructive_and_open_world() -> None:
    for name in (
        "dispatchCall",
        "createBulkCall",
        "addBulkCallContact",
        "addBulkCallContacts",
        "retryBulkCall",
        "bulkCallActions",
    ):
        a = tool_annotations(name, "POST")
        assert a["destructiveHint"] is True, name
        assert a["openWorldHint"] is True, name


def test_adding_to_a_campaign_is_not_destructive() -> None:
    a = tool_annotations("addBulkCallNumber", "POST")
    assert a["readOnlyHint"] is False
    assert a["destructiveHint"] is False
    assert a["openWorldHint"] is False


def test_changing_existing_settings_is_destructive() -> None:
    for name, method in (
        ("setBulkCallConcurrency", "PUT"),
        ("setBulkCallDailyTimeControl", "PUT"),
        ("setBulkCallNumberActive", "PUT"),
        ("updateAgent", "PUT"),
        ("workflowActions", "PATCH"),
        ("whatsappCampaignActions", "POST"),
    ):
        a = tool_annotations(name, method)
        assert a["readOnlyHint"] is False, name
        assert a["destructiveHint"] is True, name


def test_campaign_reads_are_read_only() -> None:
    for name in ("listBulkCallLines", "listBulkCallNumbers"):
        a = tool_annotations(name, "GET")
        assert a["readOnlyHint"] is True, name
        assert a["openWorldHint"] is False, name


def test_phone_number_purchase_and_release_are_destructive_and_open_world() -> None:
    for name in ("purchasePhoneNumber", "releasePhoneNumber"):
        a = tool_annotations(name, "POST")
        assert a["destructiveHint"] is True, name
        assert a["openWorldHint"] is True, name


def test_messaging_and_outside_url_tools_are_destructive_and_open_world() -> None:
    for name in (
        "sendWhatsappMessage",
        "whatsappCampaignActions",
        "addWhatsappCampaignContacts",
        "importWhatsappNumbers",
        "agentIntegrationActions",
    ):
        a = tool_annotations(name, "POST")
        assert a["destructiveHint"] is True, name
        assert a["openWorldHint"] is True, name


def test_opt_out_lift_cancel_and_auto_renew_are_destructive() -> None:
    for name in (
        "liftWhatsappOptOut",
        "setPhoneNumberAutoRenew",
    ):
        a = tool_annotations(name, "POST")
        assert a["destructiveHint"] is True, name
        assert a["openWorldHint"] is False, name


def test_whatsapp_import_preview_is_read_only() -> None:
    assert tool_annotations("previewWhatsappNumbers", "POST")["readOnlyHint"] is True


def test_phone_number_search_is_read_only() -> None:
    a = tool_annotations("searchPhoneNumbers", "GET")
    assert a["readOnlyHint"] is True
    assert a["openWorldHint"] is False
    assert a["title"] == "Search available phone numbers"


async def test_tools_list_includes_annotations(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
    )
    tools = res.json()["result"]["tools"]
    assert tools
    by_name = {t["name"]: t for t in tools}
    assert all("annotations" in t for t in tools)
    assert by_name["dispatchCall"]["annotations"]["destructiveHint"] is True
    assert by_name["dispatchCall"]["annotations"]["openWorldHint"] is True
    assert by_name["listAgents"]["annotations"]["readOnlyHint"] is True


def test_a_merged_tool_asks_before_its_strongest_action() -> None:
    files = tool_annotations("agentKnowledgeBaseActions", "POST")
    assert files["destructiveHint"] is True
    assert files["openWorldHint"] is False
    campaign = tool_annotations("whatsappCampaignActions", "POST")
    assert campaign["destructiveHint"] is True
    assert campaign["openWorldHint"] is True
    providers = tool_annotations("listProviders", "GET")
    assert providers["readOnlyHint"] is True


def test_workflow_reads_stay_read_only_after_the_merge() -> None:
    # One read tool, so read-only tokens (the support agent) keep every workflow read.
    a = _BY_NAME["workflow"]["annotations"]
    assert a["readOnlyHint"] is True
    assert a["destructiveHint"] is False
    assert _BY_NAME["deleteWorkflow"]["annotations"]["destructiveHint"] is True
