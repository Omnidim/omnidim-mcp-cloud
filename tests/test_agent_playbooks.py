import json
import re
from typing import Any

from app._generated.tools import TOOLS
from app.procedures import (
    AGENT_CONFIG_GUIDE,
    CALL_TIPS_GUIDE,
    build_prompt,
    prompts_for_listing,
    read_resource,
)
from app.routes.mcp import INSTRUCTIONS


def _playbook(name: str, arguments: dict[str, str] | None = None) -> str:
    built = build_prompt(name, arguments or {})
    assert built is not None, name
    return str(built["messages"][0]["content"]["text"])


def _guide(uri: str) -> str:
    resource = read_resource(uri)
    assert resource is not None, uri
    return str(resource["contents"][0]["text"])


def test_the_agent_lifecycle_has_design_build_and_update_playbooks() -> None:
    names = {p["name"] for p in prompts_for_listing()}
    assert {"design_agent", "provision_agent", "update_agent", "restore_agent_version"} <= names
    for name in ("design_agent", "update_agent"):
        assert name in INSTRUCTIONS


def test_design_asks_every_question_in_one_message_and_builds_nothing() -> None:
    text = _playbook("design_agent", {"purpose": "remind dental patients"})
    assert "remind dental patients" in text
    assert "in one message" in text
    assert '"default"' in text
    assert "Confirm, or tell me what to change." in text
    assert "createAgent" not in text
    assert "updateAgent" not in text
    assert "`provision_agent` prompt" in text


def test_outbound_welcome_is_a_short_name_check_unless_the_user_gave_one() -> None:
    for name in ("design_agent", "provision_agent"):
        text = _playbook(name)
        assert "8 words or fewer" in text
        assert "word for word" in text


def test_build_follows_the_approved_design() -> None:
    text = _playbook("provision_agent", {"purpose": "remind dental patients"})
    assert "`design_agent` prompt" in text
    assert "No conflicts found" in text
    assert "[MISSING: what]" in text
    assert "omnidim://guide/agent-prompt" in text


def test_build_sets_the_whole_agent_not_just_the_prompt() -> None:
    text = _playbook("provision_agent")
    for field in (
        '"temperature": 0.3',
        "end_call",
        "voicemail",
        "first_ideal_message",
        "interruption_min_words",
        "addPostCallAction",
        "extracted_variables",
        "getAgent",
        "createAgentVersion",
    ):
        assert field in text, field


def test_build_never_sets_what_the_platform_does_not_have() -> None:
    text = _playbook("provision_agent")
    assert "streaming" not in text.lower()
    assert "tts language" not in text.lower()


def test_update_backs_up_before_it_applies_and_can_undo() -> None:
    text = _playbook("update_agent", {"change": "agent 42 says the clinic name wrong"})
    assert "agent 42 says the clinic name wrong" in text
    assert text.index("getAgent") < text.index("createAgentVersion") < text.index("updateAgent")
    assert '"Apply"' in text
    assert "restoreAgentVersion" in text
    assert "SMALL FIX" in text


def test_the_prompt_guide_has_eight_sections() -> None:
    text = _guide("omnidim://guide/agent-prompt")
    headings = re.findall(r"^## (\d)\. ", text, flags=re.M)
    assert headings == [str(n) for n in range(1, 9)]
    assert "Never deny being AI" in text


def test_examples_use_the_measured_temperature() -> None:
    blocks = re.findall(r"^\{\n.*?\n\}$", AGENT_CONFIG_GUIDE, re.M | re.S)
    examples = [json.loads(m) for m in blocks]
    assert examples
    for example in examples:
        assert example["model"]["temperature"] == 0.3


def test_call_tips_no_longer_teach_filler_acknowledgements() -> None:
    assert "Got it" not in CALL_TIPS_GUIDE


def _schema(tool: str) -> dict[str, Any]:
    return next(t for t in TOOLS if t["name"] == tool)["input_schema"]


def _unknown_keys(value: Any, schema: dict[str, Any], path: str) -> list[str]:
    if not isinstance(value, dict):
        return []
    props = schema.get("properties") or {}
    found: list[str] = []
    for key, inner in value.items():
        if key not in props:
            found.append(f"{path}.{key}")
            continue
        enum = props[key].get("enum")
        if enum and isinstance(inner, str) and not inner.startswith("<") and inner not in enum:
            found.append(f"{path}.{key}={inner}")
        found += _unknown_keys(inner, props[key], f"{path}.{key}")
    return found


def test_the_create_example_sends_only_fields_createagent_accepts() -> None:
    text = _playbook("provision_agent")
    block = re.search(r"^   \{\n(.*?)\n   \}$", text, flags=re.M | re.S)
    assert block is not None
    lines = [ln for ln in block.group(1).splitlines() if '"context_breakdown"' not in ln]
    example = json.loads("{" + "\n".join(lines).rstrip(",") + "}")
    assert _unknown_keys(example, _schema("createAgent"), "createAgent") == []
    assert example["transcriber"]["is_first_ideal_message_dynamic"] is False
    assert example["transcriber"]["is_second_ideal_message_dynamic"] is False


def test_the_post_call_step_sends_only_fields_addpostcallaction_accepts() -> None:
    text = _playbook("provision_agent")
    props = _schema("addPostCallAction")["properties"]
    assert '"omni_crm"' in text and "omni_crm" in props["type"]["enum"]
    for section in re.findall(r'"(summary|sentiment|fullConversation|extracted_variables)"', text):
        assert section in props["include"]["items"]["enum"]
    for key in ("goal_confirmed", "hot_lead", "objection_raised", "not_interested_reason"):
        assert key in text


def test_update_maps_the_getagent_section_keys_back_to_updateagent() -> None:
    text = _playbook("update_agent")
    assert "`context_title`" in text and "`context_body`" in text
    assert "returned `config`" in text
    section = _schema("updateAgent")["properties"]["context_breakdown"]["items"]
    assert {"title", "body"} <= set(section["properties"])


def test_update_never_applies_without_a_known_backup() -> None:
    text = _playbook("update_agent")
    for case in ("can_publish", "no_changes", "version_limit_reached", "feature_not_entitled"):
        assert case in text, case
    assert "version_number" in text


def test_the_design_hands_the_build_every_basic() -> None:
    text = _playbook("design_agent")
    basics = text[text.index("Phase 3") :]
    for item in ("Basics", "AI disclosure", "never-say", "voice gender", "languages"):
        assert item in basics, item


def test_one_rule_for_asking_permission() -> None:
    guide = _guide("omnidim://guide/agent-prompt")
    assert "after the welcome" not in guide
    assert "omnidim://guide/call-tips" in guide


def test_the_read_back_table_names_only_fields_the_write_tools_accept() -> None:
    guide = AGENT_CONFIG_GUIDE[AGENT_CONFIG_GUIDE.index("## Reading an agent back") :]
    rows = re.findall(r"^\| `[^\n]*\| ([^\n]*) \|$", guide, flags=re.M)
    props = _schema("updateAgent")["properties"]
    named = re.findall(r"`([a-z_]+)(?:\[\])?((?:\.[a-z_]+)?)`", "\n".join(rows))
    assert ("context_breakdown", ".title") in named
    told_not_to_send = {"voice", "id", "is_auto_generated"}
    for head, tail in named:
        if not tail and head in told_not_to_send:
            continue
        assert head in props, head
        if tail:
            prop = props[head]
            inner = prop.get("properties") or prop.get("items", {}).get("properties", {})
            assert tail[1:] in inner, head + tail


def test_guides_never_promise_versions_the_platform_does_not_make() -> None:
    text = _guide("omnidim://guide/agent-versioning")
    assert "`auto`" not in text
    assert "auto-saves" not in text
    assert "feature_not_entitled" in text


def test_the_build_picks_a_voice_by_language_and_gender() -> None:
    text = _playbook("provision_agent")
    assert "`featured_languages`" in text and "`gender`" in text
