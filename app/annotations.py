"""MCP tool annotations: a display title plus read-only / destructive /
open-world hints, so clients can parallelize reads and confirm before
destructive or real-world actions. Hand-authored (regen-safe); the tools/list
handler in routes/mcp.py applies tool_annotations() per tool.
"""
from __future__ import annotations

from typing import Any

# Human-readable display names, separate from the machine name the model sees.
_TITLES: dict[str, str] = {
    "listAgents": "List agents",
    "createAgent": "Create agent",
    "getAgent": "Get agent",
    "updateAgent": "Update agent",
    "deleteAgent": "Delete agent",
    "listAgentVersions": "List agent versions",
    "createAgentVersion": "Save agent version",
    "diffAgentVersion": "Diff agent version",
    "restoreAgentVersion": "Restore agent version",
    "renameAgentVersion": "Rename agent version",
    "deleteAgentVersion": "Delete agent version",
    "createSession": "Create voice session",
    "dispatchCall": "Dispatch call",
    "listCallLogs": "List call logs",
    "getCallLog": "Get call log",
    "fetchBulkCalls": "List bulk campaigns",
    "createBulkCall": "Create bulk campaign",
    "addBulkCallContact": "Add contact to campaign",
    "getBulkCall": "Get bulk campaign",
    "bulkCallActions": "Control bulk campaign",
    "cancelBulkCall": "Cancel bulk campaign",
    "getBulkCallLiveStatus": "Get campaign live status",
    "startBulkCall": "Start draft campaign",
    "addBulkCallContacts": "Add contacts to campaign in bulk",
    "retryBulkCall": "Retry unconnected contacts",
    "setBulkCallConcurrency": "Set campaign concurrency",
    "setBulkCallDailyTimeControl": "Set campaign calling hours",
    "listBulkCallLines": "List campaign call results",
    "listBulkCallNumbers": "List campaign rotation pool",
    "addBulkCallNumber": "Add number to rotation pool",
    "setBulkCallNumberActive": "Pause or resume pool number",
    "listKnowledgeBaseFiles": "List knowledge base files",
    "canUploadFile": "Check file upload eligibility",
    "uploadKnowledgeBaseFile": "Upload knowledge base file",
    "attachKnowledgeBaseFiles": "Attach knowledge base files",
    "detachKnowledgeBaseFiles": "Detach knowledge base files",
    "deleteKnowledgeBaseFile": "Delete knowledge base file",
    "listPhoneNumbers": "List phone numbers",
    "attachPhoneNumber": "Attach phone number",
    "detachPhoneNumber": "Detach phone number",
    "importTwilioNumber": "Import Twilio number",
    "importExotelNumber": "Import Exotel number",
    "importSipTrunk": "Import SIP trunk",
    "listLLMProviders": "List LLM providers",
    "listVoices": "List voices",
    "listSTTProviders": "List speech-to-text providers",
    "listTTSProviders": "List text-to-speech providers",
    "listAllProviders": "List all providers",
    "getVoice": "Get voice",
    "searchPhoneNumbers": "Search available phone numbers",
    "purchasePhoneNumber": "Buy phone number",
    "releasePhoneNumber": "Release phone number",
}

# POST tools that only validate or preview, with no state change.
_READ_ONLY: frozenset[str] = frozenset({"canUploadFile"})

# Irreversible removals, overwrites of live config, plus tools that place
# real outbound calls.
_DESTRUCTIVE: frozenset[str] = frozenset(
    {
        "deleteAgent",
        "deleteAgentVersion",
        "restoreAgentVersion",
        "deleteKnowledgeBaseFile",
        "detachKnowledgeBaseFiles",
        "detachPhoneNumber",
        "cancelBulkCall",
        "dispatchCall",
        "createBulkCall",
        "addBulkCallContact",
        "addBulkCallContacts",
        "startBulkCall",
        "retryBulkCall",
        "purchasePhoneNumber",
        "releasePhoneNumber",
    }
)

# Tools that reach the external phone network (a carrier, not just our API).
_OPEN_WORLD: frozenset[str] = frozenset(
    {
        "dispatchCall",
        "createBulkCall",
        "addBulkCallContact",
        "addBulkCallContacts",
        "startBulkCall",
        "retryBulkCall",
        "purchasePhoneNumber",
        "releasePhoneNumber",
    }
)


def tool_annotations(name: str, method: str) -> dict[str, Any]:
    """MCP annotations for a tool. Hints are set explicitly because the spec
    defaults (destructiveHint, openWorldHint) are conservative."""
    annotations: dict[str, Any] = {}
    title = _TITLES.get(name)
    if title:
        annotations["title"] = title
    read_only = method.upper() == "GET" or name in _READ_ONLY
    annotations["readOnlyHint"] = read_only
    if read_only:
        annotations["openWorldHint"] = False
    else:
        annotations["destructiveHint"] = name in _DESTRUCTIVE
        annotations["openWorldHint"] = name in _OPEN_WORLD
    return annotations
