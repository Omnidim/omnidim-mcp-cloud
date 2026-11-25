"""MCP procedure layer: prompts/list, prompts/get, resources/list, resources/read."""
from httpx import AsyncClient

from .test_mcp_transport import _mint_access_token


async def test_initialize_advertises_prompts_and_resources(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 1, "method": "initialize"},
    )
    caps = res.json()["result"]["capabilities"]
    assert "prompts" in caps
    assert "resources" in caps


async def test_prompts_list(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 2, "method": "prompts/list"},
    )
    prompts = res.json()["result"]["prompts"]
    names = {p["name"] for p in prompts}
    assert {"provision_agent", "audit_calls"} <= names
    prov = next(p for p in prompts if p["name"] == "provision_agent")
    assert any(a["name"] == "purpose" and a["required"] for a in prov["arguments"])


async def test_prompts_get_provision(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "jsonrpc": "2.0",
            "id": 3,
            "method": "prompts/get",
            "params": {
                "name": "provision_agent",
                "arguments": {"purpose": "book dental appointments", "test_number": "+15551234567"},
            },
        },
    )
    text = res.json()["result"]["messages"][0]["content"]["text"]
    assert "book dental appointments" in text
    assert "createAgent" in text
    assert "+15551234567" in text
    assert "call_conversation" in text


async def test_prompts_get_unknown(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 4, "method": "prompts/get", "params": {"name": "nope"}},
    )
    assert res.json()["error"]["code"] == -32602


async def test_resources_list_and_read(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 5, "method": "resources/list"},
    )
    uris = {r["uri"] for r in res.json()["result"]["resources"]}
    assert "omnidim://guide/routing" in uris

    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "jsonrpc": "2.0",
            "id": 6,
            "method": "resources/read",
            "params": {"uri": "omnidim://guide/routing"},
        },
    )
    text = res.json()["result"]["contents"][0]["text"]
    # The cloud server uses flat args; the guide must say so (not requestBody wrapping).
    assert "flat top-level arguments" in text


async def test_resources_read_unknown(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 7, "method": "resources/read", "params": {"uri": "omnidim://nope"}},
    )
    assert res.json()["error"]["code"] == -32602


async def test_versioning_prompt_and_resource(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    # The restore prompt is advertised.
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 20, "method": "prompts/list"},
    )
    names = {p["name"] for p in res.json()["result"]["prompts"]}
    assert "restore_agent_version" in names
    # It weaves in the agent id and steers to preview-before-restore.
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "jsonrpc": "2.0",
            "id": 21,
            "method": "prompts/get",
            "params": {"name": "restore_agent_version", "arguments": {"agent_id": "6391"}},
        },
    )
    text = res.json()["result"]["messages"][0]["content"]["text"]
    assert "6391" in text
    assert "agentVersionActions" in text
    assert 'against: "current"' in text
    # The versioning guide resource explains the diff modes and the gotchas.
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "jsonrpc": "2.0",
            "id": 22,
            "method": "resources/read",
            "params": {"uri": "omnidim://guide/agent-versioning"},
        },
    )
    guide = res.json()["result"]["contents"][0]["text"]
    assert "against=current" in guide
    assert "feature_disabled" in guide


async def _read_resource(client: AsyncClient, token: str, uri: str) -> str:
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 8, "method": "resources/read", "params": {"uri": uri}},
    )
    return str(res.json()["result"]["contents"][0]["text"])


async def test_reference_resources_listed(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 8, "method": "resources/list"},
    )
    uris = {r["uri"] for r in res.json()["result"]["resources"]}
    assert {
        "omnidim://reference/recommended-stack",
        "omnidim://reference/voices",
        "omnidim://reference/agent-config",
    } <= uris


async def test_recommended_stack_uses_createagent_enums(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    text = await _read_resource(client, token, "omnidim://reference/recommended-stack")
    for token_str in ("soniox", "cartesia", "gpt-4.1-mini"):
        assert token_str in text
    for other in ("sarvam", "deepgram", "smallest", "eleven_labs", "azure"):
        assert other not in text.lower()


async def test_guides_steer_to_models_every_account_has(client: AsyncClient) -> None:
    # New accounts lack Azure STT and ElevenLabs TTS; the guide steering Claude to them
    # caused 43 of 55 failed MCP agent saves (2026-11-08..11). The guides recommend the
    # platform defaults, which every account has.
    token = await _mint_access_token(client)
    stack = await _read_resource(client, token, "omnidim://reference/recommended-stack")
    cfg = await _read_resource(client, token, "omnidim://reference/agent-config")
    routing = await _read_resource(client, token, "omnidim://guide/routing")
    assert "Use the platform defaults" in routing
    assert "transcriber `azure_stream`;" not in stack
    # The backend ignores voice.model; the call handler pins the Cartesia model.
    voices = await _read_resource(client, token, "omnidim://reference/voices")
    for text in (stack, cfg, routing, voices):
        assert "sonic-" not in text
    assert '"provider": "azure_stream"' not in cfg
    assert '"provider": "eleven_labs"' not in cfg
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "jsonrpc": "2.0",
            "id": 9,
            "method": "prompts/get",
            "params": {"name": "provision_agent", "arguments": {"purpose": "support"}},
        },
    )
    provision = res.json()["result"]["messages"][0]["content"]["text"]
    assert '"provider": "eleven_labs"' not in provision
    assert '"provider": "soniox"' in provision


async def test_guides_lead_with_omnidimension_voices(client: AsyncClient) -> None:
    # OmniDimension voices are our top picks per language. A Cartesia `search` never
    # finds them, so the only way in is listVoices provider=featured.
    token = await _mint_access_token(client)
    routing = await _read_resource(client, token, "omnidim://guide/routing")
    stack = await _read_resource(client, token, "omnidim://reference/recommended-stack")
    voices = await _read_resource(client, token, "omnidim://reference/voices")
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "jsonrpc": "2.0",
            "id": 10,
            "method": "prompts/get",
            "params": {"name": "provision_agent", "arguments": {"purpose": "support"}},
        },
    )
    provision = res.json()["result"]["messages"][0]["content"]["text"]
    for text in (routing, stack, voices, provision):
        assert "OmniDimension voices" in text
        assert "`provider=featured`" in text
    assert "eleven_labs" not in voices


async def test_agent_config_example_is_flat(client: AsyncClient) -> None:
    # The cloud server takes flat args, so the example must NOT wrap in a
    # requestBody object (the prose may still mention the word to say "no wrapper").
    token = await _mint_access_token(client)
    text = await _read_resource(client, token, "omnidim://reference/agent-config")
    assert '"requestBody": {' not in text
    assert '"transcriber": { "provider": "soniox" }' in text


async def test_speech_speed_range_is_documented(client: AsyncClient) -> None:
    # A speech_speed outside the provider's playable range silently mutes the
    # call (ElevenLabs: no audio outside 0.7-1.2), so the guidance must state it.
    token = await _mint_access_token(client)
    cfg = await _read_resource(client, token, "omnidim://reference/agent-config")
    assert "speech_speed" in cfg
    assert "0.7-1.2" in cfg
    routing = await _read_resource(client, token, "omnidim://guide/routing")
    assert "speech_speed" in routing
    assert "0.7-1.2" in routing


async def test_resources_never_expose_internal_infra(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 8, "method": "resources/list"},
    )
    uris = [r["uri"] for r in res.json()["result"]["resources"]]
    for uri in uris:
        text = (await _read_resource(client, token, uri)).lower()
        assert "failover" not in text, uri
        assert "gpt-5.4" not in text, uri


async def test_campaign_prompt_and_resource(client: AsyncClient) -> None:
    token = await _mint_access_token(client)
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "jsonrpc": "2.0",
            "id": 20,
            "method": "prompts/get",
            "params": {
                "name": "build_outbound_campaign",
                "arguments": {"goal": "call 8,000 renewal leads today", "phone_number_id": "177"},
            },
        },
    )
    text = res.json()["result"]["messages"][0]["content"]["text"]
    assert "call 8,000 renewal leads today" in text
    assert "- phone_number_id: 177" in text
    assert "If the user named a dialing number, use its phone_number_id" in text
    assert "save_as_draft: true" in text
    assert "never start one they have not approved" in text
    assert "3600 / average call seconds" in text
    assert "no `requestBody` wrapper" in text

    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "jsonrpc": "2.0",
            "id": 21,
            "method": "resources/read",
            "params": {"uri": "omnidim://guide/bulk-campaigns"},
        },
    )
    guide = res.json()["result"]["contents"][0]["text"]
    assert "to_number" in guide
    assert "next_cursor" in guide
    assert "daily_stop_timezone" in guide
    assert "agent has its own `timezone` field" in guide


def test_workflow_prompt_asks_before_a_real_test_run():
    from app.procedures import build_prompt

    prompt = build_prompt("build_workflow", {"goal": "Follow up interested leads on WhatsApp"})
    assert prompt is not None
    text = prompt["messages"][0]["content"]["text"]
    assert "Follow up interested leads on WhatsApp" in text
    assert "omnidim://guide/workflows" in text
    assert "for real" in text  # test runs send real messages; the model must ask first
    assert "Only call `testWorkflow` after the" in text
    assert "user says yes" in text


def test_workflow_guide_covers_building_end_to_end():
    from app.procedures import read_resource

    resource = read_resource("omnidim://guide/workflows")
    assert resource is not None
    guide = resource["contents"][0]["text"]
    for topic in ("## Lifecycle", "## Entry", "## Connecting", "## Exit", "## Moving", "## Notes",
                  "## Credentials", "## Test runs are real"):
        assert topic in guide, topic


def test_workflow_guide_names_only_tools_that_exist():
    """The guide steers the model by tool name. A renamed operation must fail here,
    not leave the model calling a tool the server does not have."""
    import re

    from app._generated.tools import TOOLS
    from app.procedures import read_resource

    resource = read_resource("omnidim://guide/workflows")
    assert resource is not None
    guide = resource["contents"][0]["text"]
    named = set(re.findall(r"`([a-z]+Workflow[A-Za-z]*)`", guide))
    assert named, "the guide should name the workflow tools"
    missing = named - {t["name"] for t in TOOLS}
    assert not missing, f"guide names tools the server does not have: {sorted(missing)}"


def test_every_resource_a_prompt_points_at_actually_exists():
    """A guide that names a resource URI has to be able to hand it over.

    The prompts tell the agent to go read `omnidim://...` for the detail. A
    rename on one side and not the other leaves the agent chasing a URI the
    server will not serve, and nothing else catches that.
    """
    import re

    from app.procedures import GUIDE_NAMES, guide_text, read_resource, resources_for_listing

    served = {r["uri"] for r in resources_for_listing()}
    text = "".join(guide_text(name) or "" for name in GUIDE_NAMES)

    for uri in set(re.findall(r"omnidim://[a-z0-9/\-]+", text)):
        assert uri in served, f"{uri} is referenced but not served"
        assert read_resource(uri) is not None


def test_the_carriers_resource_answers_which_carrier_to_buy_from():
    """carrier is required on search and purchase, and an MCP client will not
    let the agent omit it to discover the names from the 409. This resource is
    the only place it can learn them."""
    from app.procedures import read_resource

    guide = read_resource("omnidim://reference/carriers")["contents"][0]["text"]
    for carrier in ("carrier-1", "carrier-2-new", "carrier-us"):
        assert carrier in guide
    assert "Ask, do not pick" in guide
    assert "Buy from the carrier you searched" in guide
    assert "per carrier" in guide


def test_no_tool_exposes_the_reseller_user_id():
    """`user_id` lets a reseller key act as a client. It must never be a tool input."""
    from app._generated.tools import TOOLS

    leaked = [
        t["name"]
        for t in TOOLS
        if "user_id" in t["input_schema"].get("properties", {})
        or any("user_id" in r["query_params"] for r in t.get("actions", {"": t}).values())
    ]
    assert not leaked, f"reseller user_id exposed on: {leaked}"


def test_workflow_guide_warns_against_breaking_a_live_workflow():
    from app.procedures import read_resource

    resource = read_resource("omnidim://guide/workflows")
    assert resource is not None
    guide = resource["contents"][0]["text"]
    assert "## Do not break a workflow that is already running" in guide
    assert "overwrites" in guide


async def test_cloning_sends_users_to_the_dashboard_upload(client: AsyncClient) -> None:
    # A model cannot type a real clip as Base64 (a 30 s clip is ~840k characters), so the
    # create tool is off the MCP and the guide sends the user to the dashboard upload.
    token = await _mint_access_token(client)
    res = await client.post(
        "/mcp",
        headers={"Authorization": f"Bearer {token}"},
        json={"jsonrpc": "2.0", "id": 10, "method": "tools/list"},
    )
    tools = {t["name"]: t for t in res.json()["result"]["tools"]}
    assert "createClonedVoice" not in tools
    assert "listClonedVoices" in tools
    routing = await _read_resource(client, token, "omnidim://guide/routing")
    assert "https://omnidim.io/clone-voice" in routing
    assert "feature_not_enabled" in routing
    # Knowledge-base upload stays (small PDFs work), with the dashboard for larger files.
    assert "https://omnidim.io/files" in routing


async def test_call_tips_guide_is_served_and_linked(client: AsyncClient) -> None:
    from app.procedures import build_prompt, read_resource

    guide = read_resource("omnidim://guide/call-tips")
    assert guide is not None
    text = guide["contents"][0]["text"]
    assert "welcome_message" in text
    for prompt in ("provision_agent", "build_outbound_campaign"):
        built = build_prompt(prompt, {"purpose": "x", "goal": "x"})
        assert built is not None
        assert "omnidim://guide/call-tips" in built["messages"][0]["content"]["text"]


def test_outbound_greeting_examples_are_short_name_checks() -> None:
    import json
    import re

    from app.procedures import read_resource

    resource = read_resource("omnidim://reference/agent-config")
    assert resource is not None
    blocks = re.findall(r"^\{\n.*?\n\}$", resource["contents"][0]["text"], re.M | re.S)
    examples = [json.loads(m) for m in blocks]
    outbound = [e for e in examples if e["call_type"] == "Outgoing"]
    assert outbound
    for e in outbound:
        assert len(e["welcome_message"].split()) <= 8
        assert "[name]" in e["welcome_message"]


def _text(name: str) -> str:
    from app.procedures import build_prompt, guide_text

    if name.startswith("omnidim://"):
        text = guide_text(name)
    else:
        built = build_prompt(name, {})
        text = built["messages"][0]["content"]["text"] if built else None
    assert text is not None
    return " ".join(text.split())


def test_no_playbook_acts_without_the_users_yes() -> None:
    assert "attach only after the user's yes" in _text("provision_agent")
    assert "Attach only the number the user names" in _text("provision_agent")
    campaign = _text("build_outbound_campaign")
    assert "Change it with `updateAgent` only after the user's yes" in campaign
    assert "use it only after step 8's go-ahead" in campaign
    assert "restore only on their yes" in _text("restore_agent_version")
    assert "restore only on their yes" in _text("omnidim://guide/agent-versioning")
    assert "get a yes, then `publishWorkflow`" in _text("omnidim://guide/workflows")
    assert "release only after the user confirms" in _text("omnidim://guide/routing")
    assert "`build_outbound_campaign` playbook" in _text("omnidim://guide/routing")


def test_campaign_steps_match_the_api() -> None:
    text = _text("build_outbound_campaign")
    assert "{ campaign_id, contacts:" in text
    assert "bulk_call_id, contacts" not in text
    assert "needs its first rows in `contact_list`" in text
    assert "needs `contact_list` at create" in _text("omnidim://guide/bulk-campaigns")


def test_published_agents_are_flagged_before_an_edit() -> None:
    assert "published_state.is_published" in _text("update_agent")
    assert "writes the draft only" in _text("restore_agent_version")
    assert "published_state.is_published" in _text("omnidim://guide/routing")


def test_every_wait_has_a_cap() -> None:
    assert "at most 5 times" in _text("provision_agent")
    assert "up to 10 times" in _text("build_workflow")
    assert "up to 10 times" in _text("omnidim://guide/workflows")
    assert "three empty replies in a row" in _text("book_demo")
    assert "do not poll it in a loop" in _text("build_outbound_campaign")
    assert "at most 10 pages" in _text("build_outbound_campaign")
    assert "After 10 pages, ask the user" in _text("omnidim://guide/bulk-campaigns")


def test_update_keeps_disabled_sections_disabled() -> None:
    assert "Copy `is_enabled` for every section" in _text("update_agent")


def test_restore_preview_states_the_diff_direction() -> None:
    assert "`old` is this version's value" in _text("restore_agent_version")
    assert "`old` is this version's value" in _text("omnidim://guide/agent-versioning")


def test_workflow_example_keeps_secrets_out_of_config() -> None:
    assert "slack_webhook_url: \"<from the user>\"" not in _text("omnidim://guide/workflows")
    assert "integration_id: <from listWorkflowFieldOptions>" in _text("omnidim://guide/workflows")


def test_call_log_scans_use_a_page_that_fits_the_size_cap() -> None:
    assert '"pagesize": 5, "include_details": false' in _text("audit_calls")
    assert "a page of 50 short rows comes back as 6" in _text("audit_calls")


def test_campaign_results_use_a_page_that_fits_the_size_cap() -> None:
    assert "`pagesize` 10" in _text("build_outbound_campaign")
    assert "`pagesize` 10" in _text("omnidim://guide/bulk-campaigns")
