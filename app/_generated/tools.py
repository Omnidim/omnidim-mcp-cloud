"""Auto-generated MCP tool registry. Do not edit by hand.

Run `./.venv/bin/python scripts/regen.py` after editing the upstream
OpenAPI spec or the shared mcp-config.yaml.

Source spec:   omnidim.yaml   sha256=9a177b03630f
Shared config: mcp-config.yaml  sha256=0e541ad6a7d7
"""
from __future__ import annotations

import json
from typing import Any, Final


Tool = dict[str, Any]


_TOOLS_JSON = r"""[
    {
        "name": "addUser",
        "description": "Add user. Create a new child user and organization under the reseller.\nThe new organization is linked to your reseller account\nautomatically.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Full name of the new user."
                },
                "email": {
                    "type": "string",
                    "format": "email",
                    "description": "Email address. Also used as the login."
                },
                "phone": {
                    "type": "string",
                    "description": "Phone number including country code (e.g. `+15551234567`).",
                    "example": "+15551234567"
                },
                "password": {
                    "type": "string",
                    "format": "password",
                    "description": "Account password for the new user."
                },
                "welcome_minutes_to_credit": {
                    "type": "integer",
                    "description": "Minutes to credit to the new account on signup."
                },
                "cost_per_min": {
                    "type": "number",
                    "description": "Cost per minute charged to this user (e.g. `0.20`). Must be at least the reseller's premium model rate.",
                    "example": 0.2
                },
                "concurrent_call_limit": {
                    "type": "integer",
                    "description": "Maximum number of concurrent calls allowed for this account."
                },
                "expiry_date": {
                    "type": "string",
                    "format": "date",
                    "description": "Account expiry date in `YYYY-MM-DD` format (e.g. `2026-12-31`)."
                },
                "user_currency": {
                    "type": "string",
                    "description": "ISO 4217 currency code for the account (e.g. `USD`, `INR`). Defaults to the reseller's currency.",
                    "example": "USD"
                }
            },
            "required": [
                "email",
                "name",
                "password",
                "phone"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/reseller/users/add",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "attachKnowledgeBaseFiles",
        "description": "Attach files to agent. Attach multiple knowledge-base files to an agent.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_ids": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "integer"
                    },
                    "description": "List of knowledge-base file IDs to attach.",
                    "example": [
                        17686
                    ]
                },
                "agent_id": {
                    "type": "integer",
                    "description": "ID of the agent to attach files to.",
                    "example": 158910
                },
                "when_to_use": {
                    "type": "string",
                    "description": "Instruction to the agent on when to consult these files.",
                    "example": "Use these documents to answer billing-related questions."
                }
            },
            "required": [
                "agent_id",
                "file_ids"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/knowledge_base/attach",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "attachPhoneNumber",
        "description": "Attach phone number to agent. Attach an account-owned phone number to an existing agent.",
        "input_schema": {
            "type": "object",
            "properties": {
                "phone_number_id": {
                    "type": "integer",
                    "description": "ID of the phone number to attach.",
                    "example": 23
                },
                "agent_id": {
                    "type": "integer",
                    "description": "ID of the agent to attach the phone number to.",
                    "example": 158910
                }
            },
            "required": [
                "agent_id",
                "phone_number_id"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/phone_number/attach",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "bulkCallActions",
        "description": "Bulk call actions. Pause, resume, or reschedule a running campaign.",
        "input_schema": {
            "type": "object",
            "properties": {
                "bulk_call_id": {
                    "type": "integer"
                },
                "action": {
                    "type": "string",
                    "enum": [
                        "pause",
                        "resume",
                        "reschedule"
                    ],
                    "description": "What to do with the campaign."
                },
                "new_scheduled_datetime": {
                    "type": "string",
                    "description": "New start time for `reschedule`. Format `YYYY-MM-DD HH:MM:SS`.",
                    "example": "2026-12-25 10:00:00"
                },
                "new_timezone": {
                    "type": "string",
                    "description": "IANA timezone for `reschedule`.",
                    "example": "America/New_York"
                }
            },
            "required": [
                "action",
                "bulk_call_id"
            ],
            "additionalProperties": true
        },
        "method": "PUT",
        "path": "/calls/bulk_call/{bulk_call_id}",
        "path_params": [
            "bulk_call_id"
        ],
        "query_params": []
    },
    {
        "name": "calculateCreditOperation",
        "description": "Calculate credit operation. Preview the cost of a transfer or revert without moving any\ncredits. Use this to confirm amounts before calling the\ntransfer or revert endpoints. The response shape differs\nbetween forward transfers and reverts. See the examples.",
        "input_schema": {
            "type": "object",
            "properties": {
                "minutes": {
                    "type": "integer",
                    "description": "Number of minutes to calculate for."
                },
                "cost_per_min": {
                    "type": "number",
                    "description": "Rate per minute for a forward transfer (e.g. `0.20`). Not required when `is_revert` is `true`.",
                    "example": 0.2
                },
                "is_revert": {
                    "type": "boolean",
                    "description": "Set to `true` to calculate a revert instead of a forward transfer.",
                    "default": false
                },
                "child_organization_id": {
                    "type": "integer",
                    "description": "ID of the child organization to revert credits from. Required when `is_revert` is `true`."
                }
            },
            "required": [
                "minutes"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/reseller/credits/calculate",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "canUploadFile",
        "description": "Check file upload capability. Check whether a file can be uploaded based on size and type.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_size": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Size in bytes.",
                    "example": 524288
                },
                "file_type": {
                    "type": "string",
                    "description": "File extension. Only `pdf` is accepted.",
                    "example": "pdf"
                }
            },
            "required": [
                "file_size",
                "file_type"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/knowledge_base/can_upload",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "cancelBulkCall",
        "description": "Cancel bulk call. Cancel a bulk-call campaign.",
        "input_schema": {
            "type": "object",
            "properties": {
                "bulk_call_id": {
                    "type": "integer"
                }
            },
            "required": [
                "bulk_call_id"
            ],
            "additionalProperties": true
        },
        "method": "DELETE",
        "path": "/calls/bulk_call/{bulk_call_id}",
        "path_params": [
            "bulk_call_id"
        ],
        "query_params": []
    },
    {
        "name": "createAgent",
        "description": "Create agent. Create a new agent with the provided configuration. The full\nconfig supports transcriber, model, voice, web search, transfer,\nend-call conditions, post-call actions (email + webhook),\nambient background track, initial ringing sound, and multilingual support.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/agents/create",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "createBulkCall",
        "description": "Create bulk call. Create a new bulk-call campaign. Supports immediate, scheduled, and auto-retry modes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the bulk call campaign.",
                    "example": "Customer Follow-up Campaign"
                },
                "phone_number_id": {
                    "type": "string",
                    "description": "Your phone number id to use for making calls."
                },
                "contact_list": {
                    "type": "array",
                    "minItems": 1,
                    "description": "Array of contact objects. Each row needs `phone_number`.\nAny other key you add on the row (e.g. `customer_name`,\n`account_id`, `priority`) is passed to the agent as a\ncontext variable for that specific call, so the agent\ncan reference it during the conversation.\n",
                    "items": {
                        "type": "object",
                        "required": [
                            "phone_number"
                        ],
                        "properties": {
                            "phone_number": {
                                "type": "string",
                                "description": "Phone number in international format (e.g., +15551234567).",
                                "example": "+15551234567"
                            }
                        },
                        "additionalProperties": true
                    },
                    "example": [
                        {
                            "phone_number": "+15551234567",
                            "customer_name": "John Doe",
                            "account_id": "ACC-12345"
                        },
                        {
                            "phone_number": "+15559876543",
                            "customer_name": "Jane Smith",
                            "account_id": "ACC-67890",
                            "priority": "high"
                        }
                    ]
                },
                "is_scheduled": {
                    "type": "boolean",
                    "default": false,
                    "description": "Whether the campaign should be scheduled for future execution."
                },
                "scheduled_datetime": {
                    "type": "string",
                    "description": "Scheduled execution time in format `YYYY-MM-DD HH:MM:SS` (required if `is_scheduled` is true).",
                    "example": "2026-12-25 10:00:00"
                },
                "timezone": {
                    "type": "string",
                    "default": "UTC",
                    "description": "Timezone for scheduled execution.",
                    "example": "America/New_York"
                },
                "concurrent_call_limit": {
                    "type": "integer",
                    "default": 1,
                    "minimum": 1,
                    "description": "Maximum number of concurrent calls allowed."
                },
                "enabled_reschedule_call": {
                    "type": "boolean",
                    "default": false,
                    "description": "Enable automatic call rescheduling. When enabled the system can reschedule unreachable calls."
                },
                "retry_config": {
                    "type": "object",
                    "description": "Auto-retry configuration object containing retry settings.",
                    "properties": {
                        "auto_retry": {
                            "type": "boolean",
                            "default": false
                        },
                        "auto_retry_schedule": {
                            "type": "string",
                            "enum": [
                                "immediately",
                                "next_day",
                                "scheduled_time"
                            ],
                            "description": "When to retry failed calls."
                        },
                        "retry_schedule_days": {
                            "type": "integer",
                            "default": 0,
                            "minimum": 0,
                            "description": "Days to wait before a scheduled retry."
                        },
                        "retry_schedule_hours": {
                            "type": "integer",
                            "default": 0,
                            "minimum": 0,
                            "description": "Hours to wait before a scheduled retry."
                        },
                        "retry_limit": {
                            "type": "integer",
                            "default": 0,
                            "minimum": 0,
                            "maximum": 5,
                            "description": "Maximum number of retry attempts (0–5)."
                        }
                    }
                }
            },
            "required": [
                "contact_list",
                "name",
                "phone_number_id"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/calls/bulk_call/create",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "createSimulation",
        "description": "Create simulation. Create a new test simulation with scenarios.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the simulation.",
                    "example": "My Simulation"
                },
                "agent_id": {
                    "type": "integer",
                    "description": "ID of the agent to test.",
                    "example": 158910
                },
                "number_of_call_to_make": {
                    "type": "integer",
                    "default": 1,
                    "minimum": 1,
                    "maximum": 3,
                    "description": "Number of calls to make per scenario (default 1, max 3)."
                },
                "concurrent_call_count": {
                    "type": "integer",
                    "default": 3,
                    "minimum": 1,
                    "maximum": 3,
                    "description": "Number of concurrent calls to run (default 3, max 3)."
                },
                "max_call_duration_in_minutes": {
                    "type": "integer",
                    "default": 3,
                    "minimum": 1,
                    "maximum": 10,
                    "description": "Maximum duration for each call in minutes (default 3, max 10)."
                },
                "scenarios": {
                    "type": "array",
                    "description": "List of test scenarios to execute.",
                    "items": {
                        "type": "object",
                        "required": [
                            "name",
                            "description",
                            "expected_result"
                        ],
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the test scenario.",
                                "example": "Polite cancellation"
                            },
                            "description": {
                                "type": "string",
                                "description": "Detailed instructions for the test scenario.",
                                "example": "Ask to cancel a subscription, but be friendly."
                            },
                            "expected_result": {
                                "type": "string",
                                "description": "Expected outcome or behavior from the agent.",
                                "example": "Agent acknowledges the request and routes to retention."
                            },
                            "selected_voices": {
                                "type": "array",
                                "description": "Voice configurations for the test calls. If multiple voices are selected, the agent randomly picks one per call per scenario.",
                                "items": {
                                    "type": "object",
                                    "required": [
                                        "id",
                                        "provider"
                                    ],
                                    "properties": {
                                        "id": {
                                            "type": "string",
                                            "description": "Voice ID from the provider."
                                        },
                                        "provider": {
                                            "type": "string",
                                            "enum": [
                                                "eleven_labs",
                                                "play_ht",
                                                "deepgram",
                                                "cartesia",
                                                "rime"
                                            ],
                                            "example": "eleven_labs"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "required": [
                "agent_id",
                "name"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/simulations",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "deleteAgent",
        "description": "Delete agent. Permanently delete an agent.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": true
        },
        "method": "DELETE",
        "path": "/agents/{agent_id}",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "deleteKnowledgeBaseFile",
        "description": "Delete file from knowledge base. Permanently delete a file. Removes it from any attached agents. Cannot be undone.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_id": {
                    "type": "integer",
                    "description": "ID of the file to delete.",
                    "example": 17686
                }
            },
            "required": [
                "file_id"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/knowledge_base/delete",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "deleteSimulation",
        "description": "Delete simulation. Permanently delete a simulation.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": true
        },
        "method": "DELETE",
        "path": "/simulations/{simulation_id}",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "detachKnowledgeBaseFiles",
        "description": "Detach files from agent. Detach multiple knowledge-base files from an agent.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_ids": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "integer"
                    },
                    "description": "List of knowledge-base file IDs to detach.",
                    "example": [
                        17686
                    ]
                },
                "agent_id": {
                    "type": "integer",
                    "description": "ID of the agent to detach files from.",
                    "example": 158910
                }
            },
            "required": [
                "agent_id",
                "file_ids"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/knowledge_base/detach",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "detachPhoneNumber",
        "description": "Detach phone number. Detach a phone number from its associated agent.",
        "input_schema": {
            "type": "object",
            "properties": {
                "phone_number_id": {
                    "type": "integer",
                    "description": "ID of the phone number to detach.",
                    "example": 23
                }
            },
            "required": [
                "phone_number_id"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/phone_number/detach",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "dispatchCall",
        "description": "Dispatch call. Initiate a call to a phone number using a specified agent. The\nphone number must include a country code with a leading plus.",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "integer",
                    "description": "The ID of the agent that will handle the call.",
                    "example": 158910
                },
                "to_number": {
                    "type": "string",
                    "description": "The phone number to call. Must include country code (e.g., +15551234567).",
                    "example": "+15551234567"
                },
                "from_number_id": {
                    "type": "integer",
                    "description": "The imported phone number id to call.",
                    "example": 23
                },
                "call_context": {
                    "type": "object",
                    "description": "Optional context information as key-value pairs to be passed to the agent during the call. Can contain any custom fields relevant to your use case.",
                    "additionalProperties": true,
                    "example": {
                        "user_name": "Jane Doe",
                        "account_id": "A-2031",
                        "last_order": "2026-04-15"
                    }
                }
            },
            "required": [
                "agent_id",
                "to_number"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/calls/dispatch",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "enhancePrompt",
        "description": "Enhance prompt. Generate prompt-improvement suggestions for a completed simulation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "simulation_id": {
                    "type": "integer"
                }
            },
            "required": [
                "simulation_id"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/simulations/{simulation_id}/enhance-prompt",
        "path_params": [
            "simulation_id"
        ],
        "query_params": []
    },
    {
        "name": "fetchBulkCalls",
        "description": "Fetch bulk calls. List bulk-call campaigns with pagination and optional status filter.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pageno": {
                    "type": "integer",
                    "default": 1
                },
                "pagesize": {
                    "type": "integer",
                    "default": 10,
                    "maximum": 150,
                    "description": "Items per page (max 150 — sending more returns 500)."
                },
                "status": {
                    "type": "string",
                    "description": "Filter by status (e.g. completed)."
                }
            },
            "required": [],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/calls/bulk_call",
        "path_params": [],
        "query_params": [
            "pageno",
            "pagesize",
            "status"
        ]
    },
    {
        "name": "getAgent",
        "description": "Get agent. Get details of a specific agent by ID.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/agents/{agent_id}",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "getBulkCall",
        "description": "Bulk call details. Get detailed information about a bulk-call campaign.",
        "input_schema": {
            "type": "object",
            "properties": {
                "bulk_call_id": {
                    "type": "integer"
                }
            },
            "required": [
                "bulk_call_id"
            ],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/calls/bulk_call/{bulk_call_id}",
        "path_params": [
            "bulk_call_id"
        ],
        "query_params": []
    },
    {
        "name": "getBulkCallLiveStatus",
        "description": "Bulk call live status. Real-time status of a running bulk-call campaign.",
        "input_schema": {
            "type": "object",
            "properties": {
                "bulk_call_id": {
                    "type": "integer"
                }
            },
            "required": [
                "bulk_call_id"
            ],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/bulk-call/{bulk_call_id}/live-status",
        "path_params": [
            "bulk_call_id"
        ],
        "query_params": []
    },
    {
        "name": "getCallLog",
        "description": "Get call log. Detailed information about a specific call (duration, status, transcript, sentiment, extracted variables).",
        "input_schema": {
            "type": "object",
            "properties": {
                "call_log_id": {
                    "type": "integer"
                }
            },
            "required": [
                "call_log_id"
            ],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/calls/logs/{call_log_id}",
        "path_params": [
            "call_log_id"
        ],
        "query_params": []
    },
    {
        "name": "getResellerCreditLogs",
        "description": "Credit transfer logs. Paginated history of all credit transfers and reverts for the\nreseller account. Returns reverse-chronological order by\ndefault. Date filters are inclusive.",
        "input_schema": {
            "type": "object",
            "properties": {
                "page": {
                    "type": "integer",
                    "default": 1,
                    "description": "Page number for pagination."
                },
                "page_size": {
                    "type": "integer",
                    "default": 20,
                    "description": "Number of records per page (max 100)."
                },
                "date_from": {
                    "type": "string",
                    "format": "date",
                    "description": "Filter logs from this date in `YYYY-MM-DD` format (e.g. `2026-01-01`)."
                },
                "date_to": {
                    "type": "string",
                    "format": "date",
                    "description": "Filter logs up to and including this date in `YYYY-MM-DD` format (e.g. `2026-03-31`)."
                }
            },
            "required": [],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/reseller/credits/logs",
        "path_params": [],
        "query_params": [
            "page",
            "page_size",
            "date_from",
            "date_to"
        ]
    },
    {
        "name": "getSimulation",
        "description": "Get simulation. Detailed simulation information.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/simulations/{simulation_id}",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "getVoice",
        "description": "Get voice details. Detailed metadata for a specific voice.",
        "input_schema": {
            "type": "object",
            "properties": {
                "voice_id": {
                    "type": "integer"
                }
            },
            "required": [
                "voice_id"
            ],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/providers/voice/{voice_id}",
        "path_params": [
            "voice_id"
        ],
        "query_params": []
    },
    {
        "name": "importExotelNumber",
        "description": "Import Exotel number. Import an Exotel number by providing your Exotel credentials.",
        "input_schema": {
            "type": "object",
            "properties": {
                "exotel_phone_number": {
                    "type": "string",
                    "description": "Exotel phone number in E.164 format.",
                    "example": "+919876543210"
                },
                "exotel_api_key": {
                    "type": "string",
                    "description": "Your Exotel API key."
                },
                "exotel_api_token": {
                    "type": "string",
                    "description": "Your Exotel API token."
                },
                "exotel_subdomain": {
                    "type": "string",
                    "description": "Your Exotel subdomain (e.g. `your-account.in.exotel.com`)."
                },
                "exotel_account_sid": {
                    "type": "string",
                    "description": "Your Exotel account SID."
                },
                "exotel_app_id": {
                    "type": "string",
                    "description": "The Exotel App ID configured for the bot."
                },
                "name": {
                    "type": "string",
                    "description": "Optional friendly name for the imported number."
                }
            },
            "required": [
                "exotel_account_sid",
                "exotel_api_key",
                "exotel_api_token",
                "exotel_app_id",
                "exotel_phone_number",
                "exotel_subdomain"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/phone_number/import/exotel",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "importSipTrunk",
        "description": "Import SIP trunk. Import a phone number associated with a SIP trunk.",
        "input_schema": {
            "type": "object",
            "properties": {
                "phone_number": {
                    "type": "string",
                    "description": "Phone number in E.164 format (starting with `+`).",
                    "example": "+12025550123"
                },
                "sip_host": {
                    "type": "string",
                    "description": "SIP server hostname or IP.",
                    "example": "sip.yourprovider.com"
                },
                "sip_trunk_name": {
                    "type": "string",
                    "description": "Name for this SIP trunk (must be unique within your account)."
                },
                "name": {
                    "type": "string",
                    "description": "Optional friendly name for the imported number."
                },
                "sip_port": {
                    "type": "integer",
                    "default": 5060,
                    "description": "SIP server port."
                },
                "sip_username": {
                    "type": "string",
                    "description": "SIP authentication username."
                },
                "sip_password": {
                    "type": "string",
                    "format": "password",
                    "description": "SIP authentication password."
                },
                "sip_dial_prefix": {
                    "type": "string",
                    "description": "Optional prefix to prepend before the destination number when dialing (e.g. to strip the country code)."
                },
                "sip_strip_plus": {
                    "type": "boolean",
                    "description": "When true, strips the leading `+` from the dialed number."
                }
            },
            "required": [
                "phone_number",
                "sip_host",
                "sip_trunk_name"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/phone_number/import/sip",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "importTwilioNumber",
        "description": "Import Twilio number. Import an existing Twilio number by providing your Twilio credentials.",
        "input_schema": {
            "type": "object",
            "properties": {
                "phone_number": {
                    "type": "string",
                    "description": "Phone number in E.164 format (starting with `+`).",
                    "example": "+12025550123"
                },
                "account_sid": {
                    "type": "string",
                    "description": "Your Twilio account SID."
                },
                "account_token": {
                    "type": "string",
                    "description": "Your Twilio auth token."
                },
                "name": {
                    "type": "string",
                    "description": "Optional friendly name for the imported number."
                }
            },
            "required": [
                "account_sid",
                "account_token",
                "phone_number"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/phone_number/import/twilio",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "listAgents",
        "description": "List agents. Retrieve all agents for the authenticated user with pagination support.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pageno": {
                    "type": "integer",
                    "default": 1,
                    "description": "Page number for pagination."
                },
                "pagesize": {
                    "type": "integer",
                    "default": 30,
                    "maximum": 150,
                    "description": "Number of items per page (max 150)."
                },
                "name": {
                    "type": "string",
                    "description": "Filter agents whose name matches this substring (case-insensitive)."
                }
            },
            "required": [],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/agents",
        "path_params": [],
        "query_params": [
            "pageno",
            "pagesize",
            "name"
        ]
    },
    {
        "name": "listAllProviders",
        "description": "List all providers. Comprehensive response with services and voices in one payload.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/providers/all",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "listCallLogs",
        "description": "List call logs. Retrieve call logs with pagination and optional filtering.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pageno": {
                    "type": "integer",
                    "default": 1,
                    "description": "Page number for pagination."
                },
                "pagesize": {
                    "type": "integer",
                    "default": 30,
                    "maximum": 150,
                    "description": "Number of items per page."
                },
                "agentid": {
                    "type": "integer",
                    "description": "Filter by agent ID."
                },
                "call_status": {
                    "type": "string",
                    "enum": [
                        "completed",
                        "busy",
                        "failed",
                        "no-answer"
                    ]
                },
                "bulk_call_id": {
                    "type": "integer",
                    "description": "Filter by bulk-call campaign ID."
                }
            },
            "required": [],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/calls/logs",
        "path_params": [],
        "query_params": [
            "pageno",
            "pagesize",
            "agentid",
            "call_status",
            "bulk_call_id"
        ]
    },
    {
        "name": "listChildOrganizations",
        "description": "List child organizations. List all child organizations and their users under the reseller\naccount. Returns each organization's balance, cost-per-minute\nrate, and concurrency limit, plus the dashboard menu access\nflags scoped to your reseller's permissions for every user.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/reseller/organizations",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "listKnowledgeBaseFiles",
        "description": "List knowledge base files. List all knowledge-base files for the authenticated user.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/knowledge_base/list",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "listLLMProviders",
        "description": "List LLM providers. Retrieve all available Large Language Model providers.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/providers/llms",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "listPhoneNumbers",
        "description": "List phone numbers. Retrieve all phone numbers associated with your account.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pageno": {
                    "type": "integer",
                    "default": 1
                },
                "pagesize": {
                    "type": "integer",
                    "default": 30,
                    "maximum": 150
                }
            },
            "required": [],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/phone_number/list",
        "path_params": [],
        "query_params": [
            "pageno",
            "pagesize"
        ]
    },
    {
        "name": "listSTTProviders",
        "description": "List STT providers. Retrieve all Speech-to-Text providers.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/providers/stt",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "listSimulations",
        "description": "List simulations. Retrieve simulations with pagination.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pageno": {
                    "type": "integer",
                    "default": 1
                },
                "pagesize": {
                    "type": "integer",
                    "default": 10,
                    "maximum": 150
                }
            },
            "required": [],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/simulations",
        "path_params": [],
        "query_params": [
            "pageno",
            "pagesize"
        ]
    },
    {
        "name": "listTTSProviders",
        "description": "List TTS providers. Retrieve all Text-to-Speech providers.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/providers/tts",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "listVoices",
        "description": "List voices. Retrieve voices with filtering and pagination support. ElevenLabs\nsupports advanced filtering by name, language, accent, and gender.\nOther providers support basic pagination only.",
        "input_schema": {
            "type": "object",
            "properties": {
                "provider": {
                    "type": "string",
                    "enum": [
                        "eleven_labs",
                        "google",
                        "deepgram",
                        "cartesia",
                        "sarvam"
                    ],
                    "description": "TTS provider to list voices from. Omit to list across all providers."
                },
                "search": {
                    "type": "string",
                    "description": "Substring match against voice name or description. ElevenLabs only."
                },
                "language": {
                    "type": "string",
                    "description": "ISO language code (e.g. `en`, `hi`, `es`). ElevenLabs only."
                },
                "accent": {
                    "type": "string",
                    "description": "Accent label (e.g. `american`, `british`). ElevenLabs only."
                },
                "gender": {
                    "type": "string",
                    "enum": [
                        "male",
                        "female"
                    ],
                    "description": "Filter voices by gender. ElevenLabs only."
                },
                "page": {
                    "type": "integer",
                    "default": 1,
                    "description": "1-indexed page number."
                },
                "page_size": {
                    "type": "integer",
                    "default": 30,
                    "maximum": 100,
                    "description": "Voices per page. Capped at 100."
                }
            },
            "required": [],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/providers/voices",
        "path_params": [],
        "query_params": [
            "provider",
            "search",
            "language",
            "accent",
            "gender",
            "page",
            "page_size"
        ]
    },
    {
        "name": "revertCreditsFromChild",
        "description": "Revert credits. Take back unused minutes from a child organization to the\nreseller balance. The refund is calculated at the child's\ncurrent rate, so you don't pass one. This matches exactly\nwhat was originally charged. Use the calculate endpoint\nfirst to preview the refund.",
        "input_schema": {
            "type": "object",
            "properties": {
                "from_organization_id": {
                    "type": "integer",
                    "description": "ID of the child organization to revert credits from."
                },
                "minutes": {
                    "type": "integer",
                    "description": "Number of minutes to revert."
                }
            },
            "required": [
                "from_organization_id",
                "minutes"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/reseller/credits/revert",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "setChildConcurrency",
        "description": "Set child concurrency limit. Set the maximum number of simultaneous calls a child\norganization can run. Slots come from the reseller's shared\npool. Increasing the limit deducts the delta from your pool\nand fails if you don't have enough slots. Decreasing the\nlimit returns the delta to your pool immediately.",
        "input_schema": {
            "type": "object",
            "properties": {
                "child_organization_id": {
                    "type": "integer",
                    "description": "ID of the child organization to update."
                },
                "new_limit": {
                    "type": "integer",
                    "description": "The desired absolute concurrent call limit (must be `>= 0`)."
                }
            },
            "required": [
                "child_organization_id",
                "new_limit"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/reseller/concurrency",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "setUserAccessControl",
        "description": "Update user access control. Enable or disable dashboard menu access flags for a child user.\nOnly the flags you pass are changed. Flags outside your\nreseller's permissions are silently ignored.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "ID of the child user to update."
                },
                "dashboard_menu_access": {
                    "allOf": [
                        {
                            "$ref": "#/components/schemas/ResellerDashboardMenuAccess"
                        }
                    ],
                    "description": "Flags to update. Only pass the flags you want to\nchange. Others are left untouched. Flags outside\nyour reseller's permissions are silently dropped.\n"
                }
            },
            "required": [
                "dashboard_menu_access",
                "user_id"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/reseller/users/access-control",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "setUserExpiry",
        "description": "Update user expiry. Set or remove the expiry date on a child user. The user must\nbelong to a child organization of your reseller.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "ID of the child user to update."
                },
                "expiry_date": {
                    "type": "string",
                    "format": "date",
                    "nullable": true,
                    "description": "Expiry date in `YYYY-MM-DD` format. Omit or pass `null` to remove the expiry."
                }
            },
            "required": [
                "user_id"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/reseller/users/expiry",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "startSimulation",
        "description": "Start simulation. Begin running a simulation. Optionally update scenarios at start time (same shape as Update simulation).",
        "input_schema": {
            "type": "object",
            "properties": {
                "simulation_id": {
                    "type": "integer"
                },
                "scenarios": {
                    "type": "array",
                    "description": "Optional array of scenarios to update before starting.",
                    "items": {
                        "type": "object",
                        "required": [
                            "name",
                            "description",
                            "expected_result"
                        ],
                        "properties": {
                            "id": {
                                "type": "integer",
                                "description": "Include this to update an existing scenario; omit it to add a new one."
                            },
                            "name": {
                                "type": "string"
                            },
                            "description": {
                                "type": "string",
                                "description": "Updated instructions for the test scenario."
                            },
                            "expected_result": {
                                "type": "string",
                                "description": "Updated expected outcome from the agent."
                            },
                            "selected_voices": {
                                "type": "array",
                                "description": "Updated voice configurations for the test calls.",
                                "items": {
                                    "type": "object",
                                    "required": [
                                        "id",
                                        "provider"
                                    ],
                                    "properties": {
                                        "id": {
                                            "type": "string",
                                            "description": "Voice ID from the provider."
                                        },
                                        "provider": {
                                            "type": "string",
                                            "enum": [
                                                "eleven_labs",
                                                "play_ht",
                                                "deepgram",
                                                "cartesia",
                                                "rime"
                                            ]
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "required": [
                "simulation_id"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/simulations/{simulation_id}/start",
        "path_params": [
            "simulation_id"
        ],
        "query_params": []
    },
    {
        "name": "stopSimulation",
        "description": "Stop simulation. Stop a running simulation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "simulation_id": {
                    "type": "integer"
                }
            },
            "required": [
                "simulation_id"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/simulations/{simulation_id}/stop",
        "path_params": [
            "simulation_id"
        ],
        "query_params": []
    },
    {
        "name": "transferCreditsToChild",
        "description": "Transfer credits to a child. Transfer minutes from the reseller balance to a child\norganization. Credits are deducted from your balance\nimmediately on success. The target organization must be a\ndirect child of your reseller. Use the calculate endpoint\nfirst to preview the cost.",
        "input_schema": {
            "type": "object",
            "properties": {
                "to_organization_id": {
                    "type": "integer",
                    "description": "ID of the child organization to transfer credits to."
                },
                "minutes": {
                    "type": "integer",
                    "description": "Number of minutes to transfer."
                },
                "cost_per_min": {
                    "type": "number",
                    "description": "Rate per minute to charge the child organization (e.g. `0.20`).",
                    "example": 0.2
                }
            },
            "required": [
                "cost_per_min",
                "minutes",
                "to_organization_id"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/reseller/credits/transfer",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "updateAgent",
        "description": "Update agent. Update an existing agent. Send only the fields you want to change.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": true
        },
        "method": "PUT",
        "path": "/agents/{agent_id}",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "updateSimulation",
        "description": "Update simulation. Update an existing simulation. Pass the full `scenarios` array (existing entries you want to keep plus any changes).",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the simulation for identification."
                },
                "agent_id": {
                    "type": "integer",
                    "description": "ID of the agent to test."
                },
                "number_of_call_to_make": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 3,
                    "description": "Number of calls to make per scenario (default 1, max 3)."
                },
                "concurrent_call_count": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 3,
                    "description": "Number of concurrent calls to run (default 3, max 3)."
                },
                "max_call_duration_in_minutes": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10,
                    "description": "Maximum duration for each call in minutes (default 3, max 10)."
                },
                "scenarios": {
                    "type": "array",
                    "description": "Full scenario list. Include existing scenarios you want to keep, plus any new or updated ones.",
                    "items": {
                        "type": "object",
                        "required": [
                            "name",
                            "description",
                            "expected_result"
                        ],
                        "properties": {
                            "id": {
                                "type": "integer",
                                "description": "Include this to update an existing scenario; omit it to add a new one."
                            },
                            "name": {
                                "type": "string",
                                "description": "Name of the test scenario."
                            },
                            "description": {
                                "type": "string",
                                "description": "Updated instructions for the test scenario."
                            },
                            "expected_result": {
                                "type": "string",
                                "description": "Updated expected outcome from the agent."
                            },
                            "selected_voices": {
                                "type": "array",
                                "description": "Updated voice configurations for the test calls.",
                                "items": {
                                    "type": "object",
                                    "required": [
                                        "id",
                                        "provider"
                                    ],
                                    "properties": {
                                        "id": {
                                            "type": "string",
                                            "description": "Voice ID from the provider."
                                        },
                                        "provider": {
                                            "type": "string",
                                            "enum": [
                                                "eleven_labs",
                                                "play_ht",
                                                "deepgram",
                                                "cartesia",
                                                "rime"
                                            ]
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "required": [],
            "additionalProperties": true
        },
        "method": "PUT",
        "path": "/simulations/{simulation_id}",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "uploadKnowledgeBaseFile",
        "description": "Upload file to knowledge base. Upload a PDF file. The file content must be Base64 encoded.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "description": "Base64-encoded file content."
                },
                "filename": {
                    "type": "string",
                    "description": "Filename including the `.pdf` extension.",
                    "example": "sample.pdf"
                }
            },
            "required": [
                "file",
                "filename"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/knowledge_base/create",
        "path_params": [],
        "query_params": []
    }
]"""

TOOLS: Final[list[Tool]] = json.loads(_TOOLS_JSON)
