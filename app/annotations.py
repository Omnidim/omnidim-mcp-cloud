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
    "listChildOrganizations": "List child organizations",
    "addUser": "Add child user",
    "setUserAccessControl": "Set user access control",
    "setUserExpiry": "Set user expiry",
    "setChildConcurrency": "Set child concurrency limit",
    "calculateCreditOperation": "Preview credit operation",
    "transferCreditsToChild": "Transfer credits to child",
    "revertCreditsFromChild": "Revert credits from child",
    "getResellerCreditLogs": "Get reseller credit logs",
}

# POST tools that only validate or preview, with no state change.
_READ_ONLY: frozenset[str] = frozenset({"canUploadFile", "calculateCreditOperation"})

# Irreversible removals plus tools that place real outbound calls.
_DESTRUCTIVE: frozenset[str] = frozenset(
    {
        "deleteAgent",
        "deleteKnowledgeBaseFile",
        "detachKnowledgeBaseFiles",
        "detachPhoneNumber",
        "cancelBulkCall",
        "revertCreditsFromChild",
        "dispatchCall",
        "createBulkCall",
        "addBulkCallContact",
    }
)

# Tools that reach the external phone network.
_OPEN_WORLD: frozenset[str] = frozenset({"dispatchCall", "createBulkCall", "addBulkCallContact"})


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
