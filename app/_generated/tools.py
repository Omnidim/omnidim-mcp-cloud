"""Auto-generated MCP tool registry. Do not edit by hand.

Run `./.venv/bin/python scripts/regen.py` after the upstream OpenAPI spec
or mcp-config.yaml changes.

Source spec:   pub.yaml   sha256=2a35849a45ef
Config:        mcp-config.yaml  sha256=eaf21f879f19
"""
from __future__ import annotations

import json
from typing import Any, Final


Tool = dict[str, Any]


_TOOLS_JSON = r"""[
    {
        "name": "activateWorkflow",
        "description": "Activate a workflow. Turn the published workflow on, so real events run it. Use it to resume a workflow you paused with `deactivateWorkflow`.",
        "input_schema": {
            "type": "object",
            "properties": {
                "workflow_id": {
                    "type": "integer",
                    "description": "Id of the workflow."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                }
            },
            "required": [
                "workflow_id"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/workflows/{workflow_id}/activate",
        "path_params": [
            "workflow_id"
        ],
        "query_params": [
            "user_id"
        ]
    },
    {
        "name": "addBulkCallContact",
        "description": "Add contact to dynamic campaign. Push a single contact into a dynamic bulk-call campaign in real\ntime. Dynamic campaigns are created from the dashboard (Bulk Call\n> Create New Campaign > Dynamic Campaign) and stay alive waiting\nfor contacts, so this webhook is how you feed them from a CRM,\nform, or automation platform. The contact is queued immediately,\nand the campaign starts calling it as soon as it is within\noperating hours.",
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {
                    "type": "integer",
                    "description": "ID of the dynamic campaign to add the contact to."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "to_number": {
                    "type": "string",
                    "description": "Contact phone number in international format (e.g., +15551234567).",
                    "example": "+15551234567"
                },
                "custom_variables": {
                    "type": "object",
                    "description": "Key-value pairs passed to the agent as context for this\ncall, so the agent can reference them during the\nconversation (e.g. the contact's name or reason for the\ncall). Match these keys to the variables used in your\nagent's welcome message or prompt.\n",
                    "additionalProperties": true,
                    "example": {
                        "name": "Demo User",
                        "interest": "Home Insurance"
                    }
                },
                "metadata": {
                    "type": "object",
                    "description": "Key-value pairs stored on the contact for your own\ntracking (e.g. CRM or lead IDs). Not shared with the\nagent.\n",
                    "additionalProperties": true,
                    "example": {
                        "crm_lead_id": "lead_9876",
                        "source": "website_form"
                    }
                }
            },
            "required": [
                "campaign_id",
                "to_number"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/calls/bulk_call/{campaign_id}/add_contact",
        "path_params": [
            "campaign_id"
        ],
        "query_params": []
    },
    {
        "name": "addBulkCallContacts",
        "description": "Add contacts in bulk. Add up to 1000 contacts to a campaign in one request.\n\nThis is the batch form of Add contact to dynamic campaign. Prefer it\nwhenever you have more than a handful: one request of 500 contacts is\nfar cheaper than 500 requests, on your side and ours.\n\nRepeated numbers are kept, not merged. If the same number appears twice\nwith different variables, it is called twice, because two rows for one\nnumber usually means two real reasons to call.\n\nRows that fail validation are reported in `rejected` and the rest are\nstill added, so a single bad number does not lose the batch. A row that\nis missing a column the campaign's `call_conditions` need is reported in\n`rejected`; the condition values themselves are not evaluated on this\nroute.",
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {
                    "type": "integer",
                    "description": "Id of the bulk call campaign."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "contacts": {
                    "type": "array",
                    "maxItems": 1000,
                    "description": "Each row needs `to_number`. Note this differs from the\n`contact_list` on Create bulk call, which uses\n`phone_number` and takes loose keys: here the variables go\nin an explicit `custom_variables` object.\n",
                    "items": {
                        "type": "object",
                        "required": [
                            "to_number"
                        ],
                        "properties": {
                            "to_number": {
                                "type": "string",
                                "description": "Number to call, in international format.",
                                "example": "+15551234567"
                            },
                            "custom_variables": {
                                "type": "object",
                                "description": "Passed to the agent as context for this call, so it\ncan use them in the conversation.\n",
                                "additionalProperties": true,
                                "example": {
                                    "contact_name": "Ravi"
                                }
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Stored with the contact and returned on its row in\nBulk call results. Not shown to the agent.\n",
                                "additionalProperties": true
                            }
                        }
                    }
                }
            },
            "required": [
                "campaign_id",
                "contacts"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/calls/bulk_call/{campaign_id}/add_contacts",
        "path_params": [
            "campaign_id"
        ],
        "query_params": []
    },
    {
        "name": "addBulkCallNumber",
        "description": "Add number to rotation pool. Add one of your numbers to the campaign's rotation pool. Works while the\ncampaign is running, which is how you bring in a fresh number when the\npool is running out of healthy ones.\n\nThe number must belong to you and must not already be in the pool. A\nnumber with no agent attached gets this campaign's agent attached\nautomatically; a number attached to a **different** agent is refused.",
        "input_schema": {
            "type": "object",
            "properties": {
                "bulk_call_id": {
                    "type": "integer",
                    "description": "Id of the bulk call campaign."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "phone_number_id": {
                    "type": "integer",
                    "example": 178,
                    "description": "One of your numbers, from List phone numbers."
                }
            },
            "required": [
                "bulk_call_id",
                "phone_number_id"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/calls/bulk_call/{bulk_call_id}/numbers",
        "path_params": [
            "bulk_call_id"
        ],
        "query_params": []
    },
    {
        "name": "addPostCallAction",
        "description": "Add a post-call action. Add one post-call action to the agent. The agent's other actions are not changed. Send an `Idempotency-Key` header to make a retry safe: the same key and body return the action the first request added.",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "integer",
                    "description": "The ID of the agent."
                },
                "Idempotency-Key": {
                    "type": "string",
                    "description": "Any unique string. A retry with the same key and body adds nothing new."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "type": {
                    "type": "string",
                    "enum": [
                        "email",
                        "webhook",
                        "omni_crm",
                        "cloud_whatsapp",
                        "workflow",
                        "google_sheets",
                        "slack",
                        "salesforce",
                        "hubspot",
                        "zoho_bigin"
                    ],
                    "description": "The channel. It cannot change after the action is created:\ndelete it and add a new one. `google_sheets`, `slack`,\n`salesforce`, `hubspot` and `zoho_bigin` deliver through an\naccount connected in the dashboard: pass its id as\n`integration_id` (see List integrations).\n"
                },
                "integration_id": {
                    "type": "integer",
                    "description": "`google_sheets`, `slack`, `salesforce`, `hubspot`, `zoho_bigin`\nonly, required: the id of your integration of that type.\n"
                },
                "spreadsheet_id": {
                    "type": "string",
                    "description": "`google_sheets` only, required: the id in the sheet's URL, the\npart after `/d/`.\n",
                    "example": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
                },
                "spreadsheet_name": {
                    "type": "string",
                    "description": "`google_sheets` only: the sheet's name, for display."
                },
                "worksheet_name": {
                    "type": "string",
                    "description": "`google_sheets` only: the tab to append to. Defaults to `Sheet1`.",
                    "example": "Calls"
                },
                "channel_id": {
                    "type": "string",
                    "description": "`slack` only: the channel id. Send this or `channel_name`.",
                    "example": "C08RTQ1NY81"
                },
                "channel_name": {
                    "type": "string",
                    "description": "`slack` only: the channel name. Send this or `channel_id`.",
                    "example": "sales"
                },
                "object_name": {
                    "type": "string",
                    "description": "`salesforce`: `Lead` (default), `Contact`, `Account`,\n`Opportunity`, `Case`, `Task` or `Product`. `hubspot`, required:\n`contact`, `company`, `deal` or `ticket`. Both send a fixed set of\nfields for the chosen object, so they take no `extracted_variables`.\n"
                },
                "create_call_log": {
                    "type": "boolean",
                    "description": "`zoho_bigin` only: log the call in Zoho Bigin. Defaults to true."
                },
                "update_contact": {
                    "type": "boolean",
                    "description": "`zoho_bigin` only: update a matching contact with what the call captured. Defaults to true."
                },
                "create_contact": {
                    "type": "boolean",
                    "description": "`zoho_bigin` only: create a contact when no contact matches. Defaults to true."
                },
                "recipients": {
                    "type": "array",
                    "description": "`email` only, required: the addresses to notify.",
                    "items": {
                        "type": "string",
                        "format": "email"
                    },
                    "example": [
                        "support@acme-corp.io"
                    ]
                },
                "url": {
                    "type": "string",
                    "format": "uri",
                    "description": "`webhook` only, required: the endpoint that receives a POST with the call payload.",
                    "example": "https://crm.acme-corp.io/omnidim-callback"
                },
                "phone_number_id": {
                    "type": "integer",
                    "description": "`cloud_whatsapp` only, required: your Cloud WhatsApp number the message is sent from. Also send `template_id` or `templates`, or nothing is sent."
                },
                "template_id": {
                    "type": "integer",
                    "description": "`cloud_whatsapp` only: an approved template on that number."
                },
                "template_variables": {
                    "type": "array",
                    "description": "`cloud_whatsapp` only: which extracted variable fills each template placeholder.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "index": {
                                "type": "string",
                                "description": "The placeholder number, as a string.",
                                "example": "1"
                            },
                            "extracted_var": {
                                "type": "string",
                                "description": "The key of the extracted variable whose value fills this placeholder.",
                                "example": "customer_name"
                            }
                        }
                    }
                },
                "templates": {
                    "type": "array",
                    "description": "`cloud_whatsapp` only: one or more templates to send.",
                    "items": {
                        "type": "object",
                        "description": "One Cloud WhatsApp template to send after the call.",
                        "properties": {
                            "template_id": {
                                "type": "integer",
                                "description": "An approved template on the chosen number."
                            },
                            "usage_description": {
                                "type": "string",
                                "description": "When this template should be sent. After the call, the model reads\nthese descriptions to choose which templates fit the conversation.\n",
                                "example": "Send when the caller books an appointment."
                            },
                            "always_send": {
                                "type": "boolean",
                                "description": "Send this template after every call, whichever templates the model chooses."
                            },
                            "variable_mappings": {
                                "type": "array",
                                "description": "How to fill each template placeholder.",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "index": {
                                            "type": "string",
                                            "description": "The placeholder number, as a string.",
                                            "example": "1"
                                        },
                                        "extracted_var": {
                                            "type": "string",
                                            "description": "The extracted variable whose value fills this placeholder."
                                        },
                                        "static_value": {
                                            "type": "string",
                                            "description": "A fixed value for this placeholder. When set, it is used\ninstead of the extracted variable.\n"
                                        },
                                        "mode": {
                                            "type": "string",
                                            "enum": [
                                                "variable",
                                                "static"
                                            ],
                                            "description": "Which input the dashboard shows for this placeholder. It\ndoes not change the value sent: a `static_value` is used\nfirst, then the extracted variable, then `fallback_value`.\n"
                                        },
                                        "fallback_value": {
                                            "type": "string",
                                            "description": "The value to use when the variable is not extracted."
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "workflow_id": {
                    "type": "integer",
                    "description": "`workflow` only, required: the workflow to run. It must have a published version, or the action is skipped."
                },
                "include": {
                    "type": "array",
                    "description": "Which sections to include.",
                    "items": {
                        "type": "string",
                        "enum": [
                            "summary",
                            "extracted_variables",
                            "fullConversation",
                            "sentiment"
                        ]
                    }
                },
                "extracted_variables": {
                    "type": "array",
                    "description": "Variables the model should pull out of the conversation. A key\nalready used by another action on this agent must have the same\nprompt, or the request is refused with `400`. Other actions are\nnever changed to match.\n",
                    "items": {
                        "type": "object",
                        "required": [
                            "key",
                            "prompt"
                        ],
                        "properties": {
                            "key": {
                                "type": "string",
                                "description": "Unique identifier for the variable in the post-call payload.",
                                "example": "customer_issue"
                            },
                            "prompt": {
                                "type": "string",
                                "description": "Instruction for the model on what to pull out of the conversation.",
                                "example": "Identify the main issue the customer is experiencing."
                            }
                        }
                    }
                },
                "trigger_call_statuses": {
                    "type": "array",
                    "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                    "items": {
                        "type": "string",
                        "enum": [
                            "completed",
                            "voicemail_detected",
                            "failed",
                            "no-answer",
                            "busy",
                            "canceled"
                        ]
                    }
                }
            },
            "required": [
                "agent_id",
                "type"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/agents/{agent_id}/post-call-actions",
        "path_params": [
            "agent_id"
        ],
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
        "description": "Attach phone number to agent. Attach a phone number to an existing agent. Without `user_id`, use any\nnumber and agent your key can manage. With `user_id`, the number and the\nagent must both belong to that client.",
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
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller accounts only: the client to act on. Omit it to act on your own account.",
                    "example": 1234
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
                    "type": "integer",
                    "description": "Id of the bulk call campaign."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "action": {
                    "type": "string",
                    "example": "pause",
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
        "name": "canUploadFile",
        "description": "Check file upload capability. Check whether a file can be uploaded based on size and type.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
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
        "description": "Cancel bulk call. Cancel a scheduled bulk-call campaign. A campaign that is already running, or is still a draft, is refused.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "bulk_call_id": {
                    "type": "integer",
                    "description": "Id of the bulk call campaign."
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
        "query_params": [
            "user_id"
        ]
    },
    {
        "name": "createAgent",
        "description": "Create agent. Create a new agent with the provided configuration. The full\nconfig supports transcriber, model, voice, web search, transfer,\nend-call conditions, post-call actions (email, webhook, Omni CRM,\nCloud WhatsApp, or a workflow),\nambient background track, initial ringing sound, and multilingual support.\n\n> **Voicemail detection is an access-gated feature** that we turn on per\naccount. If it isn't enabled for yours yet,\n[request access](https://omnidim.io/contact-us?reason=product&lock=1)\nbefore configuring the `voicemail` object.",
        "input_schema": {
            "type": "object",
            "properties": {
                "Idempotency-Key": {
                    "type": "string",
                    "maxLength": 255,
                    "description": "Your own unique key for this agent, for example a fresh UUID.\nSend the same key when you retry. If the first request already\ncreated the agent, you get that agent back instead of a second\none, so a request that timed out is safe to repeat. The same key\nwith a different request body is refused. Keys are kept for 24\nhours.\n"
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "name": {
                    "type": "string",
                    "description": "Name for the agent.",
                    "example": "Customer Support Agent"
                },
                "welcome_message": {
                    "type": "string",
                    "description": "Initial message the agent will say when answering a call.",
                    "example": "Hello! How can I help you today?"
                },
                "is_welcome_message_dynamic": {
                    "type": "boolean",
                    "description": "When true, the welcome message is treated as a directive the agent uses to generate a tailored greeting for each call, rather than being spoken word for word. When false, the welcome message is spoken exactly as written."
                },
                "is_welcome_message_interruption": {
                    "type": "boolean",
                    "description": "Allow the caller to interrupt the welcome message. When false, the agent finishes speaking the welcome before listening."
                },
                "is_interruption_allowed": {
                    "type": "boolean",
                    "description": "Global toggle for whether the caller can interrupt the agent mid-sentence at any point in the call."
                },
                "dynamic_variables": {
                    "type": "object",
                    "description": "Key/value map used to substitute placeholders in the agent's\nprompt and welcome message at call time. Reference a variable\nin your prompt with `{{variable_name}}`. Useful for\npersonalising the same agent across many calls.\n",
                    "additionalProperties": {
                        "type": "string"
                    },
                    "example": {
                        "customer_name": "Jane Doe",
                        "order_id": "ORD-12345"
                    }
                },
                "context_breakdown": {
                    "type": "array",
                    "description": "List of context breakdowns, each containing `title`, `body`, and optional `is_enabled`.",
                    "items": {
                        "type": "object",
                        "required": [
                            "title",
                            "body"
                        ],
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Title of the breakdown.",
                                "example": "Purpose"
                            },
                            "body": {
                                "type": "string",
                                "description": "Body of the breakdown, the detailed prompt content.",
                                "example": "This agent helps customers with product inquiries and support issues."
                            },
                            "is_enabled": {
                                "type": "boolean",
                                "default": true,
                                "description": "Whether this section is included in the prompt."
                            }
                        }
                    }
                },
                "call_type": {
                    "type": "string",
                    "enum": [
                        "Incoming",
                        "Outgoing"
                    ],
                    "description": "Call type of the assistant."
                },
                "timezone": {
                    "type": "string",
                    "description": "IANA timezone for this agent, for example `Asia/Kolkata`. Sets the local date and time the agent works with during calls. If not set, the account timezone is used as fallback. Pass an empty string to clear it.",
                    "example": "America/New_York"
                },
                "transcriber": {
                    "type": "object",
                    "description": "Configuration for the speech-to-text transcriber.",
                    "properties": {
                        "provider": {
                            "type": "string",
                            "enum": [
                                "deepgram_stream",
                                "cartesia",
                                "sarvam",
                                "azure_stream",
                                "soniox"
                            ],
                            "description": "The speech-to-text provider to use.",
                            "example": "deepgram_stream"
                        },
                        "model": {
                            "type": "string",
                            "description": "Transcription model for the selected provider. For\n`deepgram_stream` this is `nova-3` or `nova-2`; other\nproviders take their own model identifiers.\n",
                            "example": "nova-3"
                        },
                        "language": {
                            "type": "string",
                            "description": "Language code for the transcriber. Format and supported\nvalues depend on the provider (e.g. `en-US` for Deepgram,\n`hi-IN` for Sarvam). Applies regardless of which\n`provider` is selected.\n",
                            "example": "en-US"
                        },
                        "silence_timeout_ms": {
                            "type": "integer",
                            "description": "Silence timeout in milliseconds.",
                            "example": 400
                        },
                        "should_apply_noise_reduction": {
                            "type": "boolean",
                            "description": "Reduce background noise on the inbound audio stream before transcription."
                        },
                        "interruption_min_words": {
                            "type": "integer",
                            "minimum": 1,
                            "description": "Minimum number of words the caller must say before their speech is treated as an interruption.",
                            "example": 2
                        },
                        "max_call_duration_in_sec": {
                            "type": "integer",
                            "minimum": 1,
                            "description": "Hard upper bound on call length in seconds. The agent will end the call once this is reached.",
                            "example": 600
                        },
                        "first_ideal_message": {
                            "type": "string",
                            "description": "First nudge spoken when the caller goes silent past the\nidle threshold. Set `is_first_ideal_message_dynamic` to\n`true` to have the LLM regenerate this each time.\n"
                        },
                        "is_first_ideal_message_dynamic": {
                            "type": "boolean",
                            "description": "When true, `first_ideal_message` is treated as a prompt and the LLM generates a fresh nudge each call."
                        },
                        "second_ideal_message": {
                            "type": "string",
                            "description": "Second nudge spoken if silence continues after the first."
                        },
                        "is_second_ideal_message_dynamic": {
                            "type": "boolean",
                            "description": "When true, `second_ideal_message` is treated as a prompt and the LLM generates a fresh nudge each call."
                        },
                        "numerals": {
                            "type": "boolean",
                            "description": "Convert numbers from words to digits."
                        },
                        "punctuate": {
                            "type": "boolean",
                            "description": "Add punctuation to the transcript."
                        },
                        "smart_format": {
                            "type": "boolean",
                            "description": "Apply smart formatting to the transcript."
                        },
                        "diarize": {
                            "type": "boolean",
                            "description": "Identify different speakers in the transcript."
                        }
                    }
                },
                "model": {
                    "type": "object",
                    "description": "Configuration for the language model.",
                    "properties": {
                        "model": {
                            "type": "string",
                            "enum": [
                                "azure-gpt-4.1-mini",
                                "azure-gpt-4.1-nano",
                                "azure-gpt-4o",
                                "azure-gpt-4o-mini",
                                "gemini-2.5-flash",
                                "gemini-2.5-flash-lite",
                                "gpt-3.5-turbo",
                                "gpt-4.1-mini",
                                "gpt-4.1-nano",
                                "gpt-4o",
                                "gpt-4o-mini",
                                "gpt-5.1",
                                "llama-3.3-70b-versatile"
                            ],
                            "description": "The language model to use. The current catalog is returned by the LLM providers list.",
                            "example": "gpt-4.1-mini"
                        },
                        "temperature": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                            "description": "Controls randomness in the model's output (0.0 to 1.0).",
                            "example": 0.7
                        }
                    }
                },
                "voice": {
                    "type": "object",
                    "description": "Configuration for the text-to-speech voice. `provider` and `voice_id` identify the voice together, so send both to change it. `provider` on its own is not accepted, and a `voice_id` on its own leaves the voice as it was. The other fields here apply independently.",
                    "dependentRequired": {
                        "provider": [
                            "voice_id"
                        ]
                    },
                    "properties": {
                        "provider": {
                            "type": "string",
                            "enum": [
                                "eleven_labs",
                                "google",
                                "cartesia",
                                "sarvam"
                            ],
                            "description": "The voice provider to use. The current catalog is returned by the TTS providers list. Send `voice_id` alongside it.",
                            "example": "eleven_labs"
                        },
                        "voice_id": {
                            "type": "string",
                            "description": "The provider's voice identifier, returned in the `name` field of the voices list (not the numeric `id`). Takes effect when `provider` is sent alongside it.",
                            "example": "JBFqnCBsd6RMkjVDRZzb"
                        },
                        "speech_speed": {
                            "type": "number",
                            "minimum": 0.5,
                            "maximum": 2.0,
                            "default": 1.0,
                            "description": "Playback speed multiplier for the agent's voice. 1.0 is normal speed."
                        }
                    }
                },
                "web_search": {
                    "type": "object",
                    "description": "Configuration for web search capabilities.",
                    "properties": {
                        "enabled": {
                            "type": "boolean",
                            "description": "Enable or disable web search functionality."
                        },
                        "provider": {
                            "type": "string",
                            "enum": [
                                "DuckDuckGo",
                                "openAI"
                            ],
                            "description": "The search provider to use.",
                            "example": "DuckDuckGo"
                        }
                    }
                },
                "post_call_actions": {
                    "type": "object",
                    "description": "Side effects that fire once the call ends: email, webhook, Omni CRM,\nCloud WhatsApp, a workflow, Google Sheets, Slack, Salesforce, HubSpot\nor Zoho Bigin.\n",
                    "properties": {
                        "email": {
                            "type": "object",
                            "properties": {
                                "enabled": {
                                    "type": "boolean"
                                },
                                "recipients": {
                                    "type": "array",
                                    "description": "Email addresses that should receive the notification.",
                                    "items": {
                                        "type": "string",
                                        "format": "email"
                                    },
                                    "example": [
                                        "support@example.com"
                                    ]
                                },
                                "include": {
                                    "type": "array",
                                    "description": "Which sections to include in the email body.",
                                    "items": {
                                        "type": "string",
                                        "enum": [
                                            "summary",
                                            "extracted_variables",
                                            "fullConversation",
                                            "sentiment"
                                        ]
                                    }
                                },
                                "extracted_variables": {
                                    "type": "array",
                                    "description": "Variables the model should pull out of the conversation for the email.",
                                    "items": {
                                        "type": "object",
                                        "required": [
                                            "key",
                                            "prompt"
                                        ],
                                        "properties": {
                                            "key": {
                                                "type": "string",
                                                "description": "Unique identifier for the variable in the post-call payload.",
                                                "example": "customer_issue"
                                            },
                                            "prompt": {
                                                "type": "string",
                                                "description": "Instruction for the model on what to pull out of the conversation.",
                                                "example": "Identify the main issue the customer is experiencing."
                                            }
                                        }
                                    }
                                },
                                "trigger_call_statuses": {
                                    "type": "array",
                                    "description": "Call outcomes that should fire this action. Omit to\nuse the default (`completed`, `voicemail_detected`).\nPass an explicit list to also include failed calls,\nno-answers, busy signals, etc.\n",
                                    "items": {
                                        "type": "string",
                                        "enum": [
                                            "completed",
                                            "voicemail_detected",
                                            "failed",
                                            "no-answer",
                                            "busy",
                                            "canceled"
                                        ]
                                    },
                                    "example": [
                                        "completed",
                                        "voicemail_detected"
                                    ]
                                }
                            }
                        },
                        "webhook": {
                            "type": "object",
                            "properties": {
                                "enabled": {
                                    "type": "boolean"
                                },
                                "url": {
                                    "type": "string",
                                    "format": "uri",
                                    "description": "Endpoint that receives a POST with the call payload.",
                                    "example": "https://your-webhook-endpoint.com/omnidim-callback"
                                },
                                "include": {
                                    "type": "array",
                                    "description": "Which sections to include in the webhook body.",
                                    "items": {
                                        "type": "string",
                                        "enum": [
                                            "summary",
                                            "extracted_variables",
                                            "fullConversation",
                                            "sentiment"
                                        ]
                                    }
                                },
                                "extracted_variables": {
                                    "type": "array",
                                    "description": "Variables the model should pull out of the conversation for the webhook.",
                                    "items": {
                                        "type": "object",
                                        "required": [
                                            "key",
                                            "prompt"
                                        ],
                                        "properties": {
                                            "key": {
                                                "type": "string",
                                                "description": "Unique identifier for the variable in the post-call payload.",
                                                "example": "customer_issue"
                                            },
                                            "prompt": {
                                                "type": "string",
                                                "description": "Instruction for the model on what to pull out of the conversation.",
                                                "example": "Identify the main issue the customer is experiencing."
                                            }
                                        }
                                    }
                                },
                                "trigger_call_statuses": {
                                    "type": "array",
                                    "description": "Call outcomes that should fire this webhook. Omit to\nuse the default (`completed`, `voicemail_detected`).\n",
                                    "items": {
                                        "type": "string",
                                        "enum": [
                                            "completed",
                                            "voicemail_detected",
                                            "failed",
                                            "no-answer",
                                            "busy",
                                            "canceled"
                                        ]
                                    },
                                    "example": [
                                        "completed",
                                        "failed"
                                    ]
                                }
                            }
                        },
                        "omni_crm": {
                            "allOf": [
                                {
                                    "type": "object",
                                    "description": "Settings every post-call channel shares.",
                                    "properties": {
                                        "enabled": {
                                            "type": "boolean"
                                        },
                                        "include": {
                                            "type": "array",
                                            "description": "Which sections to include in this action.",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "summary",
                                                    "extracted_variables",
                                                    "fullConversation",
                                                    "sentiment"
                                                ]
                                            }
                                        },
                                        "extracted_variables": {
                                            "type": "array",
                                            "description": "Variables the model should pull out of the conversation for this action.",
                                            "items": {
                                                "type": "object",
                                                "required": [
                                                    "key",
                                                    "prompt"
                                                ],
                                                "properties": {
                                                    "key": {
                                                        "type": "string",
                                                        "description": "Unique identifier for the variable in the post-call payload.",
                                                        "example": "customer_issue"
                                                    },
                                                    "prompt": {
                                                        "type": "string",
                                                        "description": "Instruction for the model on what to pull out of the conversation.",
                                                        "example": "Identify the main issue the customer is experiencing."
                                                    }
                                                }
                                            }
                                        },
                                        "trigger_call_statuses": {
                                            "type": "array",
                                            "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "completed",
                                                    "voicemail_detected",
                                                    "failed",
                                                    "no-answer",
                                                    "busy",
                                                    "canceled"
                                                ]
                                            }
                                        }
                                    }
                                },
                                {
                                    "type": "object",
                                    "description": "Save the call to Omni CRM."
                                }
                            ]
                        },
                        "cloud_whatsapp": {
                            "allOf": [
                                {
                                    "type": "object",
                                    "description": "Settings every post-call channel shares.",
                                    "properties": {
                                        "enabled": {
                                            "type": "boolean"
                                        },
                                        "include": {
                                            "type": "array",
                                            "description": "Which sections to include in this action.",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "summary",
                                                    "extracted_variables",
                                                    "fullConversation",
                                                    "sentiment"
                                                ]
                                            }
                                        },
                                        "extracted_variables": {
                                            "type": "array",
                                            "description": "Variables the model should pull out of the conversation for this action.",
                                            "items": {
                                                "type": "object",
                                                "required": [
                                                    "key",
                                                    "prompt"
                                                ],
                                                "properties": {
                                                    "key": {
                                                        "type": "string",
                                                        "description": "Unique identifier for the variable in the post-call payload.",
                                                        "example": "customer_issue"
                                                    },
                                                    "prompt": {
                                                        "type": "string",
                                                        "description": "Instruction for the model on what to pull out of the conversation.",
                                                        "example": "Identify the main issue the customer is experiencing."
                                                    }
                                                }
                                            }
                                        },
                                        "trigger_call_statuses": {
                                            "type": "array",
                                            "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "completed",
                                                    "voicemail_detected",
                                                    "failed",
                                                    "no-answer",
                                                    "busy",
                                                    "canceled"
                                                ]
                                            }
                                        }
                                    }
                                },
                                {
                                    "type": "object",
                                    "description": "Send a Cloud WhatsApp template message after the call.",
                                    "properties": {
                                        "phone_number_id": {
                                            "type": "integer",
                                            "description": "The id of your organization's Cloud WhatsApp number the\nmessage is sent from.\n"
                                        },
                                        "template_id": {
                                            "type": "integer",
                                            "description": "An approved template on that number. A template that is not\napproved, or that belongs to another number, is refused.\n"
                                        },
                                        "template_variables": {
                                            "type": "array",
                                            "description": "Which extracted variable fills each template placeholder.",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "index": {
                                                        "type": "string",
                                                        "description": "The placeholder number, as a string.",
                                                        "example": "1"
                                                    },
                                                    "extracted_var": {
                                                        "type": "string",
                                                        "description": "The key of the extracted variable whose value fills this placeholder.",
                                                        "example": "customer_name"
                                                    }
                                                }
                                            }
                                        },
                                        "templates": {
                                            "type": "array",
                                            "description": "One or more templates to send, each with its variable mapping.",
                                            "items": {
                                                "type": "object",
                                                "description": "One Cloud WhatsApp template to send after the call.",
                                                "properties": {
                                                    "template_id": {
                                                        "type": "integer",
                                                        "description": "An approved template on the chosen number."
                                                    },
                                                    "usage_description": {
                                                        "type": "string",
                                                        "description": "When this template should be sent. After the call, the model reads\nthese descriptions to choose which templates fit the conversation.\n",
                                                        "example": "Send when the caller books an appointment."
                                                    },
                                                    "always_send": {
                                                        "type": "boolean",
                                                        "description": "Send this template after every call, whichever templates the model chooses."
                                                    },
                                                    "variable_mappings": {
                                                        "type": "array",
                                                        "description": "How to fill each template placeholder.",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "index": {
                                                                    "type": "string",
                                                                    "description": "The placeholder number, as a string.",
                                                                    "example": "1"
                                                                },
                                                                "extracted_var": {
                                                                    "type": "string",
                                                                    "description": "The extracted variable whose value fills this placeholder."
                                                                },
                                                                "static_value": {
                                                                    "type": "string",
                                                                    "description": "A fixed value for this placeholder. When set, it is used\ninstead of the extracted variable.\n"
                                                                },
                                                                "mode": {
                                                                    "type": "string",
                                                                    "enum": [
                                                                        "variable",
                                                                        "static"
                                                                    ],
                                                                    "description": "Which input the dashboard shows for this placeholder. It\ndoes not change the value sent: a `static_value` is used\nfirst, then the extracted variable, then `fallback_value`.\n"
                                                                },
                                                                "fallback_value": {
                                                                    "type": "string",
                                                                    "description": "The value to use when the variable is not extracted."
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            ]
                        },
                        "workflow": {
                            "allOf": [
                                {
                                    "type": "object",
                                    "description": "Settings every post-call channel shares.",
                                    "properties": {
                                        "enabled": {
                                            "type": "boolean"
                                        },
                                        "include": {
                                            "type": "array",
                                            "description": "Which sections to include in this action.",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "summary",
                                                    "extracted_variables",
                                                    "fullConversation",
                                                    "sentiment"
                                                ]
                                            }
                                        },
                                        "extracted_variables": {
                                            "type": "array",
                                            "description": "Variables the model should pull out of the conversation for this action.",
                                            "items": {
                                                "type": "object",
                                                "required": [
                                                    "key",
                                                    "prompt"
                                                ],
                                                "properties": {
                                                    "key": {
                                                        "type": "string",
                                                        "description": "Unique identifier for the variable in the post-call payload.",
                                                        "example": "customer_issue"
                                                    },
                                                    "prompt": {
                                                        "type": "string",
                                                        "description": "Instruction for the model on what to pull out of the conversation.",
                                                        "example": "Identify the main issue the customer is experiencing."
                                                    }
                                                }
                                            }
                                        },
                                        "trigger_call_statuses": {
                                            "type": "array",
                                            "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "completed",
                                                    "voicemail_detected",
                                                    "failed",
                                                    "no-answer",
                                                    "busy",
                                                    "canceled"
                                                ]
                                            }
                                        }
                                    }
                                },
                                {
                                    "type": "object",
                                    "description": "Trigger a workflow after the call.",
                                    "properties": {
                                        "workflow_id": {
                                            "type": "integer",
                                            "description": "The id of the workflow to run."
                                        }
                                    }
                                }
                            ]
                        },
                        "google_sheets": {
                            "allOf": [
                                {
                                    "type": "object",
                                    "description": "Settings every post-call channel shares.",
                                    "properties": {
                                        "enabled": {
                                            "type": "boolean"
                                        },
                                        "include": {
                                            "type": "array",
                                            "description": "Which sections to include in this action.",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "summary",
                                                    "extracted_variables",
                                                    "fullConversation",
                                                    "sentiment"
                                                ]
                                            }
                                        },
                                        "extracted_variables": {
                                            "type": "array",
                                            "description": "Variables the model should pull out of the conversation for this action.",
                                            "items": {
                                                "type": "object",
                                                "required": [
                                                    "key",
                                                    "prompt"
                                                ],
                                                "properties": {
                                                    "key": {
                                                        "type": "string",
                                                        "description": "Unique identifier for the variable in the post-call payload.",
                                                        "example": "customer_issue"
                                                    },
                                                    "prompt": {
                                                        "type": "string",
                                                        "description": "Instruction for the model on what to pull out of the conversation.",
                                                        "example": "Identify the main issue the customer is experiencing."
                                                    }
                                                }
                                            }
                                        },
                                        "trigger_call_statuses": {
                                            "type": "array",
                                            "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "completed",
                                                    "voicemail_detected",
                                                    "failed",
                                                    "no-answer",
                                                    "busy",
                                                    "canceled"
                                                ]
                                            }
                                        }
                                    }
                                },
                                {
                                    "type": "object",
                                    "description": "Append the call to a Google Sheet. Sending this key replaces the\nagent's Google Sheets actions; leaving it out keeps them.\n",
                                    "properties": {
                                        "integration_id": {
                                            "type": "integer",
                                            "description": "Required. The id of your Google Sheets integration."
                                        },
                                        "spreadsheet_id": {
                                            "type": "string",
                                            "description": "Required. The id in the sheet's URL, the part after `/d/`."
                                        },
                                        "spreadsheet_name": {
                                            "type": "string"
                                        },
                                        "worksheet_name": {
                                            "type": "string",
                                            "description": "The tab to append to. Defaults to `Sheet1`."
                                        }
                                    }
                                }
                            ]
                        },
                        "slack": {
                            "allOf": [
                                {
                                    "type": "object",
                                    "description": "Settings every post-call channel shares.",
                                    "properties": {
                                        "enabled": {
                                            "type": "boolean"
                                        },
                                        "include": {
                                            "type": "array",
                                            "description": "Which sections to include in this action.",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "summary",
                                                    "extracted_variables",
                                                    "fullConversation",
                                                    "sentiment"
                                                ]
                                            }
                                        },
                                        "extracted_variables": {
                                            "type": "array",
                                            "description": "Variables the model should pull out of the conversation for this action.",
                                            "items": {
                                                "type": "object",
                                                "required": [
                                                    "key",
                                                    "prompt"
                                                ],
                                                "properties": {
                                                    "key": {
                                                        "type": "string",
                                                        "description": "Unique identifier for the variable in the post-call payload.",
                                                        "example": "customer_issue"
                                                    },
                                                    "prompt": {
                                                        "type": "string",
                                                        "description": "Instruction for the model on what to pull out of the conversation.",
                                                        "example": "Identify the main issue the customer is experiencing."
                                                    }
                                                }
                                            }
                                        },
                                        "trigger_call_statuses": {
                                            "type": "array",
                                            "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "completed",
                                                    "voicemail_detected",
                                                    "failed",
                                                    "no-answer",
                                                    "busy",
                                                    "canceled"
                                                ]
                                            }
                                        }
                                    }
                                },
                                {
                                    "type": "object",
                                    "description": "Post the call to a Slack channel. Sending this key replaces the\nagent's Slack actions; leaving it out keeps them.\n",
                                    "properties": {
                                        "integration_id": {
                                            "type": "integer",
                                            "description": "Required. The id of your Slack integration."
                                        },
                                        "channel_id": {
                                            "type": "string",
                                            "description": "The channel id. Send this or `channel_name`."
                                        },
                                        "channel_name": {
                                            "type": "string",
                                            "description": "The channel name. Send this or `channel_id`."
                                        }
                                    }
                                }
                            ]
                        },
                        "salesforce": {
                            "allOf": [
                                {
                                    "type": "object",
                                    "description": "Settings every post-call channel shares.",
                                    "properties": {
                                        "enabled": {
                                            "type": "boolean"
                                        },
                                        "include": {
                                            "type": "array",
                                            "description": "Which sections to include in this action.",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "summary",
                                                    "extracted_variables",
                                                    "fullConversation",
                                                    "sentiment"
                                                ]
                                            }
                                        },
                                        "extracted_variables": {
                                            "type": "array",
                                            "description": "Variables the model should pull out of the conversation for this action.",
                                            "items": {
                                                "type": "object",
                                                "required": [
                                                    "key",
                                                    "prompt"
                                                ],
                                                "properties": {
                                                    "key": {
                                                        "type": "string",
                                                        "description": "Unique identifier for the variable in the post-call payload.",
                                                        "example": "customer_issue"
                                                    },
                                                    "prompt": {
                                                        "type": "string",
                                                        "description": "Instruction for the model on what to pull out of the conversation.",
                                                        "example": "Identify the main issue the customer is experiencing."
                                                    }
                                                }
                                            }
                                        },
                                        "trigger_call_statuses": {
                                            "type": "array",
                                            "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "completed",
                                                    "voicemail_detected",
                                                    "failed",
                                                    "no-answer",
                                                    "busy",
                                                    "canceled"
                                                ]
                                            }
                                        }
                                    }
                                },
                                {
                                    "type": "object",
                                    "description": "Create a Salesforce record from the call. Sends a fixed set of\nfields for the object, so it takes no `extracted_variables`.\nSending this key replaces the agent's Salesforce actions;\nleaving it out keeps them.\n",
                                    "properties": {
                                        "integration_id": {
                                            "type": "integer",
                                            "description": "Required. The id of your Salesforce integration."
                                        },
                                        "object_name": {
                                            "type": "string",
                                            "enum": [
                                                "Lead",
                                                "Contact",
                                                "Account",
                                                "Opportunity",
                                                "Case",
                                                "Task",
                                                "Product"
                                            ],
                                            "description": "Defaults to `Lead`."
                                        }
                                    }
                                }
                            ]
                        },
                        "hubspot": {
                            "allOf": [
                                {
                                    "type": "object",
                                    "description": "Settings every post-call channel shares.",
                                    "properties": {
                                        "enabled": {
                                            "type": "boolean"
                                        },
                                        "include": {
                                            "type": "array",
                                            "description": "Which sections to include in this action.",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "summary",
                                                    "extracted_variables",
                                                    "fullConversation",
                                                    "sentiment"
                                                ]
                                            }
                                        },
                                        "extracted_variables": {
                                            "type": "array",
                                            "description": "Variables the model should pull out of the conversation for this action.",
                                            "items": {
                                                "type": "object",
                                                "required": [
                                                    "key",
                                                    "prompt"
                                                ],
                                                "properties": {
                                                    "key": {
                                                        "type": "string",
                                                        "description": "Unique identifier for the variable in the post-call payload.",
                                                        "example": "customer_issue"
                                                    },
                                                    "prompt": {
                                                        "type": "string",
                                                        "description": "Instruction for the model on what to pull out of the conversation.",
                                                        "example": "Identify the main issue the customer is experiencing."
                                                    }
                                                }
                                            }
                                        },
                                        "trigger_call_statuses": {
                                            "type": "array",
                                            "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "completed",
                                                    "voicemail_detected",
                                                    "failed",
                                                    "no-answer",
                                                    "busy",
                                                    "canceled"
                                                ]
                                            }
                                        }
                                    }
                                },
                                {
                                    "type": "object",
                                    "description": "Create a HubSpot record from the call. Sends a fixed set of\nfields for the object, so it takes no `extracted_variables`.\nSending this key replaces the agent's HubSpot actions; leaving\nit out keeps them.\n",
                                    "properties": {
                                        "integration_id": {
                                            "type": "integer",
                                            "description": "Required. The id of your HubSpot integration."
                                        },
                                        "object_name": {
                                            "type": "string",
                                            "enum": [
                                                "contact",
                                                "company",
                                                "deal",
                                                "ticket"
                                            ],
                                            "description": "Required."
                                        }
                                    }
                                }
                            ]
                        },
                        "zoho_bigin": {
                            "allOf": [
                                {
                                    "type": "object",
                                    "description": "Settings every post-call channel shares.",
                                    "properties": {
                                        "enabled": {
                                            "type": "boolean"
                                        },
                                        "include": {
                                            "type": "array",
                                            "description": "Which sections to include in this action.",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "summary",
                                                    "extracted_variables",
                                                    "fullConversation",
                                                    "sentiment"
                                                ]
                                            }
                                        },
                                        "extracted_variables": {
                                            "type": "array",
                                            "description": "Variables the model should pull out of the conversation for this action.",
                                            "items": {
                                                "type": "object",
                                                "required": [
                                                    "key",
                                                    "prompt"
                                                ],
                                                "properties": {
                                                    "key": {
                                                        "type": "string",
                                                        "description": "Unique identifier for the variable in the post-call payload.",
                                                        "example": "customer_issue"
                                                    },
                                                    "prompt": {
                                                        "type": "string",
                                                        "description": "Instruction for the model on what to pull out of the conversation.",
                                                        "example": "Identify the main issue the customer is experiencing."
                                                    }
                                                }
                                            }
                                        },
                                        "trigger_call_statuses": {
                                            "type": "array",
                                            "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "completed",
                                                    "voicemail_detected",
                                                    "failed",
                                                    "no-answer",
                                                    "busy",
                                                    "canceled"
                                                ]
                                            }
                                        }
                                    }
                                },
                                {
                                    "type": "object",
                                    "description": "Log the call in Zoho Bigin. Sending this key replaces the\nagent's Zoho Bigin actions; leaving it out keeps them.\n",
                                    "properties": {
                                        "integration_id": {
                                            "type": "integer",
                                            "description": "Required. The id of your Zoho Bigin integration."
                                        },
                                        "create_call_log": {
                                            "type": "boolean",
                                            "description": "Log the call. Defaults to true."
                                        },
                                        "update_contact": {
                                            "type": "boolean",
                                            "description": "Update a matching contact with what the call captured. Defaults to true."
                                        },
                                        "create_contact": {
                                            "type": "boolean",
                                            "description": "Create a contact when no contact matches. Defaults to true."
                                        }
                                    }
                                }
                            ]
                        }
                    }
                },
                "transfer": {
                    "type": "object",
                    "description": "Conditional call transfer to a human agent or another number.",
                    "properties": {
                        "enabled": {
                            "type": "boolean"
                        },
                        "transfer_options": {
                            "type": "array",
                            "description": "Where to transfer the call and under what condition. The first matching condition wins. In an agent update, sending this list replaces all saved options. Omit it to keep them unchanged, or send an empty array to clear them.",
                            "items": {
                                "type": "object",
                                "required": [
                                    "number",
                                    "transfer_condition",
                                    "transfer_message"
                                ],
                                "properties": {
                                    "number": {
                                        "type": "string",
                                        "description": "Primary phone number to transfer to. Include country code with leading `+`.",
                                        "example": "+15551234567"
                                    },
                                    "type": {
                                        "type": "string",
                                        "enum": [
                                            "static",
                                            "dynamic"
                                        ],
                                        "default": "static",
                                        "description": "`static` transfers to `number`. `dynamic` lets the agent\npick a number at runtime based on the conversation.\n"
                                    },
                                    "backup_numbers": {
                                        "type": "array",
                                        "description": "Fallback numbers tried if the primary is unreachable.",
                                        "items": {
                                            "type": "string"
                                        }
                                    },
                                    "transfer_condition": {
                                        "type": "string",
                                        "description": "Natural-language condition that triggers this transfer option.",
                                        "example": "Transfer if the customer asks to speak with a human."
                                    },
                                    "transfer_message": {
                                        "type": "string",
                                        "description": "Message the agent says to the caller before executing the transfer.",
                                        "example": "Please hold while I connect you to one of our agents."
                                    }
                                }
                            }
                        }
                    }
                },
                "end_call": {
                    "type": "object",
                    "description": "Hang up automatically when a condition is met.",
                    "properties": {
                        "enabled": {
                            "type": "boolean"
                        },
                        "condition": {
                            "type": "string",
                            "description": "Natural-language condition that triggers ending the call. Only evaluated when `enabled` is true.",
                            "example": "End the call once the customer's issue is resolved."
                        },
                        "message": {
                            "type": "string",
                            "description": "What the agent says before hanging up.",
                            "example": "Thank you for contacting us. Have a great day!"
                        },
                        "message_type": {
                            "type": "string",
                            "enum": [
                                "static",
                                "prompt"
                            ],
                            "description": "`static` speaks `message` verbatim. `prompt` treats\n`message_prompt` as an LLM instruction and generates a\nfresh closing line each call (useful for matching the\ncaller's language and tone).\n"
                        },
                        "message_prompt": {
                            "type": "string",
                            "description": "LLM prompt used to generate the closing line when `message_type` is `prompt`.",
                            "example": "End the call politely in the same language the user is speaking."
                        }
                    }
                },
                "background_track": {
                    "type": "object",
                    "description": "Ambient background noise that plays under the agent's voice.",
                    "properties": {
                        "enabled": {
                            "type": "boolean",
                            "description": "Whether to mix the ambient track under the agent's audio."
                        },
                        "name": {
                            "type": "string",
                            "enum": [
                                "call_center",
                                "filler",
                                "office",
                                "office_1",
                                "restaurant"
                            ],
                            "description": "Ambient track to mix under the agent."
                        },
                        "volume": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                            "default": 0.2,
                            "description": "Volume level on a 0–1 scale. Default 0.2."
                        },
                        "tts_volume_reduction": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                            "description": "Amount to drop the agent's TTS volume while the ambient track plays, on a 0–1 scale. Helps the voice cut through without raising the overall mix."
                        }
                    }
                },
                "initial_ringing_sound_enabled": {
                    "type": "boolean",
                    "description": "Plays a ringing tone after the call is picked up, until the agent starts speaking."
                },
                "voicemail": {
                    "type": "object",
                    "description": "Voicemail / answering-machine handling for outbound calls. Set this with the nested object shown here; the agent object returns these values as the flat fields `voicemail_enabled` and `voicemail_message`. Voicemail detection is an access-gated feature. If it isn't enabled for your account, [request access](https://omnidim.io/contact-us?reason=product&lock=1).",
                    "properties": {
                        "enabled": {
                            "type": "boolean",
                            "description": "Detect voicemail and leave your message instead of speaking to a machine."
                        },
                        "message": {
                            "type": "string",
                            "description": "Message to leave when voicemail is detected."
                        }
                    }
                },
                "languages": {
                    "type": "array",
                    "description": "Languages the agent should support. Pass each language as a display-name string exactly as it appears in the dashboard's language picker. Unrecognized names are skipped.",
                    "items": {
                        "type": "string"
                    },
                    "example": [
                        "English (India)",
                        "Hindi"
                    ]
                }
            },
            "required": [
                "context_breakdown",
                "name"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/agents/create",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "createAgentVersion",
        "description": "Save an agent version. Save the agent's current configuration as a named version.",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "integer",
                    "description": "The ID of the agent."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "name": {
                    "type": "string",
                    "example": "v2 pricing script",
                    "description": "Display name for the version."
                },
                "note": {
                    "type": "string",
                    "example": "Shorter opener, new objection handling.",
                    "description": "Optional note describing the version."
                }
            },
            "required": [
                "agent_id",
                "name"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/agents/{agent_id}/versions",
        "path_params": [
            "agent_id"
        ],
        "query_params": []
    },
    {
        "name": "createBulkCall",
        "description": "Create bulk call. Create a new bulk-call campaign. Only name, phone_number_id and a\ncontact_list are needed to dial a list now; every other field adds\none behavior on top (drafts, rotation, filtering, scheduling,\nretries, dynamic feeding).\n\nThe guide below the field reference walks the whole journey: the\nfirst campaign and its response, each behavior with a working\nrequest, every refusal message with its fix, and the endpoints that\noperate a campaign once it runs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "name": {
                    "type": "string",
                    "description": "Name of the bulk call campaign.",
                    "example": "Customer Follow-up Campaign"
                },
                "phone_number_id": {
                    "type": "string",
                    "example": "177",
                    "description": "The number this campaign calls from. With a `rotation`, the\nrotation numbers dial instead and this one is the standby.\n"
                },
                "bot_id": {
                    "type": "integer",
                    "description": "Agent to run the campaign. Defaults to the agent attached\nto `phone_number_id`; required when the number has none.\n"
                },
                "save_as_draft": {
                    "type": "boolean",
                    "default": false,
                    "description": "Store the campaign without dialing; start it later with the\nstart endpoint. See Drafts in the guide below.\n"
                },
                "call_conditions": {
                    "type": "array",
                    "description": "Dial only the contacts that match every condition; the rest\nare kept as `Skipped`. See Filtering in the guide below.\n",
                    "items": {
                        "type": "object",
                        "required": [
                            "column",
                            "operator",
                            "value"
                        ],
                        "properties": {
                            "column": {
                                "type": "string",
                                "description": "Key on the contact row to test.",
                                "example": "plan"
                            },
                            "operator": {
                                "type": "string",
                                "default": "equals",
                                "example": "equals",
                                "enum": [
                                    "equals",
                                    "not_equals",
                                    "contains",
                                    "greater_than",
                                    "less_than"
                                ],
                                "description": "`contains` is case-insensitive. `greater_than` and\n`less_than` compare numerically, and a row whose value\nis not a number fails the condition rather than\nerroring.\n"
                            },
                            "value": {
                                "type": "string",
                                "example": "pro"
                            }
                        }
                    }
                },
                "rotation": {
                    "type": "object",
                    "description": "Rotate the campaign across several of your numbers, so no\nsingle number burns out. See Rotation in the guide below.\n",
                    "required": [
                        "numbers"
                    ],
                    "properties": {
                        "numbers": {
                            "type": "array",
                            "minItems": 1,
                            "description": "The numbers to rotate across; each must be yours and\nlisted once.\n",
                            "items": {
                                "type": "object",
                                "required": [
                                    "phone_number_id"
                                ],
                                "properties": {
                                    "phone_number_id": {
                                        "type": "integer",
                                        "example": 177,
                                        "description": "One of your numbers, from List phone numbers."
                                    },
                                    "sequence": {
                                        "type": "integer",
                                        "default": 10,
                                        "description": "Rotation order. Lowest dials first."
                                    }
                                }
                            }
                        },
                        "strategy": {
                            "type": "string",
                            "default": "fixed_count",
                            "example": "fixed_count",
                            "enum": [
                                "fixed_count",
                                "cpr_threshold",
                                "both",
                                "none"
                            ],
                            "description": "When to move to the next number: every\n`calls_per_number` calls, on low health score, both, or\nnever.\n"
                        },
                        "calls_per_number": {
                            "type": "integer",
                            "default": 50,
                            "example": 50,
                            "description": "Calls before moving on. Used by `fixed_count` and `both`."
                        },
                        "health_threshold": {
                            "type": "number",
                            "default": 30.0,
                            "description": "Health score below which a number is rotated away from.\nUsed by `cpr_threshold` and `both`.\n"
                        },
                        "fallback": {
                            "type": "string",
                            "default": "pause",
                            "enum": [
                                "pause",
                                "continue_best"
                            ],
                            "description": "When every number is unhealthy: `pause` the campaign,\nor `continue_best` with the healthiest one.\n"
                        }
                    }
                },
                "is_dynamic": {
                    "type": "boolean",
                    "default": false,
                    "description": "A dynamic campaign stays alive accepting contacts via the\nadd-contact webhooks, and `contact_list` becomes optional.\n"
                },
                "contact_list": {
                    "type": "array",
                    "description": "Who to call. Each row needs `phone_number`; any other key\nreaches the agent as context for that one call.\n",
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
                            "default": 1,
                            "minimum": 1,
                            "maximum": 10,
                            "description": "Retry attempts, 1 to 10. To disable retries omit it and\nleave `auto_retry` false; never send `0`.\n"
                        }
                    }
                }
            },
            "required": [
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
        "name": "createClonedVoice",
        "description": "Create a cloned voice. Clone a voice from an audio sample. The sample must be Base64 encoded and\n1 KB to 25 MB. MP3, WAV and WebM are accepted; a non-audio body is\nrefused.\n\nCreation is asynchronous. This call returns `202` at once with\n`status: processing`. Poll `GET /voices/{voice_id}` until `status` is\n`ready` or `failed`, then use the `voice_id` in an agent's `voice` config with\n`voice.provider: cartesia`.\n\nYou must send `consent: true`: you confirm you have the right to clone\nthis voice. The attestation is recorded against the clone.\n\nLimits apply per user: 5 clones an hour, 20 a day, and 200 stored\n(processing plus ready). A request over a limit is refused with `429`.",
        "input_schema": {
            "type": "object",
            "properties": {
                "Idempotency-Key": {
                    "type": "string",
                    "description": "Optional. Send a unique value per clone; a retry with the same key\nand body returns the first clone instead of creating a second. Every\nclone costs money at the provider, so this makes a retry safe. Up to\n255 printable characters.\n"
                },
                "name": {
                    "type": "string",
                    "description": "A name for the cloned voice, 1 to 100 characters.",
                    "example": "Front desk"
                },
                "clip": {
                    "type": "string",
                    "description": "Base64-encoded audio, 1 KB to 25 MB (MP3, WAV or WebM)."
                },
                "filename": {
                    "type": "string",
                    "description": "Optional original filename, for your reference.",
                    "example": "sample.mp3"
                },
                "description": {
                    "type": "string",
                    "description": "Optional description."
                },
                "language": {
                    "type": "string",
                    "description": "A short language code for the voice. Defaults to `en`.",
                    "example": "en"
                },
                "gender": {
                    "type": "string",
                    "enum": [
                        "male",
                        "female"
                    ],
                    "default": "female",
                    "description": "The voice's gender. Defaults to `female`."
                },
                "consent": {
                    "type": "boolean",
                    "description": "Required and must be `true`: you confirm you have the right\nto clone this voice.\n",
                    "example": true
                }
            },
            "required": [
                "clip",
                "consent",
                "name"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/voices",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "createSession",
        "description": "Create session. Create a voice Session: a short-lived, single-conversation\nreservation that lets a client hold a live voice chat with your\nagent. This is step 1 of 2. Creating the Session does not start any\naudio on its own; it returns a `ws_url` that a client then connects\nto over WebSocket to actually talk.\n\nCall this endpoint from your server with your API key, and return\nonly the `ws_url` to your client. The API key must never reach the\nbrowser. The `ws_url` is the only thing the client needs, and it is\nsafe to hand out because it is single-use and expires. For how to\nconnect and talk, see \"Connect the client and talk\" below the\nrequest details.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "agent_id": {
                    "type": "integer",
                    "description": "ID of the agent the session talks to.",
                    "example": 158910
                },
                "type": {
                    "type": "string",
                    "default": "voice",
                    "example": "voice",
                    "enum": [
                        "voice"
                    ],
                    "description": "The session type. Only `voice` is supported."
                },
                "custom_variables": {
                    "type": "object",
                    "additionalProperties": true,
                    "description": "Per-session variables that personalize the conversation.\nSet server-side, so visitors cannot tamper with them.\nTwo reserved keys are read as instructions for this session\nand never reach the agent: `__languages` and\n`__post_call_actions`.\n",
                    "properties": {
                        "__languages": {
                            "oneOf": [
                                {
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    }
                                },
                                {
                                    "type": "string"
                                }
                            ],
                            "description": "Languages this session runs in, replacing the agent's\nconfigured list. The first entry is the language the\nvisitor is greeted in. Send an array, or a pipe-separated\nstring such as `Hindi|English`.\n",
                            "example": "Hindi|Gujarati|English"
                        },
                        "__post_call_actions": {
                            "allOf": [
                                {
                                    "type": "object",
                                    "description": "Side effects that fire once the call ends: email, webhook, Omni CRM,\nCloud WhatsApp, a workflow, Google Sheets, Slack, Salesforce, HubSpot\nor Zoho Bigin.\n",
                                    "properties": {
                                        "email": {
                                            "type": "object",
                                            "properties": {
                                                "enabled": {
                                                    "type": "boolean"
                                                },
                                                "recipients": {
                                                    "type": "array",
                                                    "description": "Email addresses that should receive the notification.",
                                                    "items": {
                                                        "type": "string",
                                                        "format": "email"
                                                    },
                                                    "example": [
                                                        "support@example.com"
                                                    ]
                                                },
                                                "include": {
                                                    "type": "array",
                                                    "description": "Which sections to include in the email body.",
                                                    "items": {
                                                        "type": "string",
                                                        "enum": [
                                                            "summary",
                                                            "extracted_variables",
                                                            "fullConversation",
                                                            "sentiment"
                                                        ]
                                                    }
                                                },
                                                "extracted_variables": {
                                                    "type": "array",
                                                    "description": "Variables the model should pull out of the conversation for the email.",
                                                    "items": {
                                                        "type": "object",
                                                        "required": [
                                                            "key",
                                                            "prompt"
                                                        ],
                                                        "properties": {
                                                            "key": {
                                                                "type": "string",
                                                                "description": "Unique identifier for the variable in the post-call payload.",
                                                                "example": "customer_issue"
                                                            },
                                                            "prompt": {
                                                                "type": "string",
                                                                "description": "Instruction for the model on what to pull out of the conversation.",
                                                                "example": "Identify the main issue the customer is experiencing."
                                                            }
                                                        }
                                                    }
                                                },
                                                "trigger_call_statuses": {
                                                    "type": "array",
                                                    "description": "Call outcomes that should fire this action. Omit to\nuse the default (`completed`, `voicemail_detected`).\nPass an explicit list to also include failed calls,\nno-answers, busy signals, etc.\n",
                                                    "items": {
                                                        "type": "string",
                                                        "enum": [
                                                            "completed",
                                                            "voicemail_detected",
                                                            "failed",
                                                            "no-answer",
                                                            "busy",
                                                            "canceled"
                                                        ]
                                                    },
                                                    "example": [
                                                        "completed",
                                                        "voicemail_detected"
                                                    ]
                                                }
                                            }
                                        },
                                        "webhook": {
                                            "type": "object",
                                            "properties": {
                                                "enabled": {
                                                    "type": "boolean"
                                                },
                                                "url": {
                                                    "type": "string",
                                                    "format": "uri",
                                                    "description": "Endpoint that receives a POST with the call payload.",
                                                    "example": "https://your-webhook-endpoint.com/omnidim-callback"
                                                },
                                                "include": {
                                                    "type": "array",
                                                    "description": "Which sections to include in the webhook body.",
                                                    "items": {
                                                        "type": "string",
                                                        "enum": [
                                                            "summary",
                                                            "extracted_variables",
                                                            "fullConversation",
                                                            "sentiment"
                                                        ]
                                                    }
                                                },
                                                "extracted_variables": {
                                                    "type": "array",
                                                    "description": "Variables the model should pull out of the conversation for the webhook.",
                                                    "items": {
                                                        "type": "object",
                                                        "required": [
                                                            "key",
                                                            "prompt"
                                                        ],
                                                        "properties": {
                                                            "key": {
                                                                "type": "string",
                                                                "description": "Unique identifier for the variable in the post-call payload.",
                                                                "example": "customer_issue"
                                                            },
                                                            "prompt": {
                                                                "type": "string",
                                                                "description": "Instruction for the model on what to pull out of the conversation.",
                                                                "example": "Identify the main issue the customer is experiencing."
                                                            }
                                                        }
                                                    }
                                                },
                                                "trigger_call_statuses": {
                                                    "type": "array",
                                                    "description": "Call outcomes that should fire this webhook. Omit to\nuse the default (`completed`, `voicemail_detected`).\n",
                                                    "items": {
                                                        "type": "string",
                                                        "enum": [
                                                            "completed",
                                                            "voicemail_detected",
                                                            "failed",
                                                            "no-answer",
                                                            "busy",
                                                            "canceled"
                                                        ]
                                                    },
                                                    "example": [
                                                        "completed",
                                                        "failed"
                                                    ]
                                                }
                                            }
                                        },
                                        "omni_crm": {
                                            "allOf": [
                                                {
                                                    "type": "object",
                                                    "description": "Settings every post-call channel shares.",
                                                    "properties": {
                                                        "enabled": {
                                                            "type": "boolean"
                                                        },
                                                        "include": {
                                                            "type": "array",
                                                            "description": "Which sections to include in this action.",
                                                            "items": {
                                                                "type": "string",
                                                                "enum": [
                                                                    "summary",
                                                                    "extracted_variables",
                                                                    "fullConversation",
                                                                    "sentiment"
                                                                ]
                                                            }
                                                        },
                                                        "extracted_variables": {
                                                            "type": "array",
                                                            "description": "Variables the model should pull out of the conversation for this action.",
                                                            "items": {
                                                                "type": "object",
                                                                "required": [
                                                                    "key",
                                                                    "prompt"
                                                                ],
                                                                "properties": {
                                                                    "key": {
                                                                        "type": "string",
                                                                        "description": "Unique identifier for the variable in the post-call payload.",
                                                                        "example": "customer_issue"
                                                                    },
                                                                    "prompt": {
                                                                        "type": "string",
                                                                        "description": "Instruction for the model on what to pull out of the conversation.",
                                                                        "example": "Identify the main issue the customer is experiencing."
                                                                    }
                                                                }
                                                            }
                                                        },
                                                        "trigger_call_statuses": {
                                                            "type": "array",
                                                            "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                                            "items": {
                                                                "type": "string",
                                                                "enum": [
                                                                    "completed",
                                                                    "voicemail_detected",
                                                                    "failed",
                                                                    "no-answer",
                                                                    "busy",
                                                                    "canceled"
                                                                ]
                                                            }
                                                        }
                                                    }
                                                },
                                                {
                                                    "type": "object",
                                                    "description": "Save the call to Omni CRM."
                                                }
                                            ]
                                        },
                                        "cloud_whatsapp": {
                                            "allOf": [
                                                {
                                                    "type": "object",
                                                    "description": "Settings every post-call channel shares.",
                                                    "properties": {
                                                        "enabled": {
                                                            "type": "boolean"
                                                        },
                                                        "include": {
                                                            "type": "array",
                                                            "description": "Which sections to include in this action.",
                                                            "items": {
                                                                "type": "string",
                                                                "enum": [
                                                                    "summary",
                                                                    "extracted_variables",
                                                                    "fullConversation",
                                                                    "sentiment"
                                                                ]
                                                            }
                                                        },
                                                        "extracted_variables": {
                                                            "type": "array",
                                                            "description": "Variables the model should pull out of the conversation for this action.",
                                                            "items": {
                                                                "type": "object",
                                                                "required": [
                                                                    "key",
                                                                    "prompt"
                                                                ],
                                                                "properties": {
                                                                    "key": {
                                                                        "type": "string",
                                                                        "description": "Unique identifier for the variable in the post-call payload.",
                                                                        "example": "customer_issue"
                                                                    },
                                                                    "prompt": {
                                                                        "type": "string",
                                                                        "description": "Instruction for the model on what to pull out of the conversation.",
                                                                        "example": "Identify the main issue the customer is experiencing."
                                                                    }
                                                                }
                                                            }
                                                        },
                                                        "trigger_call_statuses": {
                                                            "type": "array",
                                                            "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                                            "items": {
                                                                "type": "string",
                                                                "enum": [
                                                                    "completed",
                                                                    "voicemail_detected",
                                                                    "failed",
                                                                    "no-answer",
                                                                    "busy",
                                                                    "canceled"
                                                                ]
                                                            }
                                                        }
                                                    }
                                                },
                                                {
                                                    "type": "object",
                                                    "description": "Send a Cloud WhatsApp template message after the call.",
                                                    "properties": {
                                                        "phone_number_id": {
                                                            "type": "integer",
                                                            "description": "The id of your organization's Cloud WhatsApp number the\nmessage is sent from.\n"
                                                        },
                                                        "template_id": {
                                                            "type": "integer",
                                                            "description": "An approved template on that number. A template that is not\napproved, or that belongs to another number, is refused.\n"
                                                        },
                                                        "template_variables": {
                                                            "type": "array",
                                                            "description": "Which extracted variable fills each template placeholder.",
                                                            "items": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "index": {
                                                                        "type": "string",
                                                                        "description": "The placeholder number, as a string.",
                                                                        "example": "1"
                                                                    },
                                                                    "extracted_var": {
                                                                        "type": "string",
                                                                        "description": "The key of the extracted variable whose value fills this placeholder.",
                                                                        "example": "customer_name"
                                                                    }
                                                                }
                                                            }
                                                        },
                                                        "templates": {
                                                            "type": "array",
                                                            "description": "One or more templates to send, each with its variable mapping.",
                                                            "items": {
                                                                "type": "object",
                                                                "description": "One Cloud WhatsApp template to send after the call.",
                                                                "properties": {
                                                                    "template_id": {
                                                                        "type": "integer",
                                                                        "description": "An approved template on the chosen number."
                                                                    },
                                                                    "usage_description": {
                                                                        "type": "string",
                                                                        "description": "When this template should be sent. After the call, the model reads\nthese descriptions to choose which templates fit the conversation.\n",
                                                                        "example": "Send when the caller books an appointment."
                                                                    },
                                                                    "always_send": {
                                                                        "type": "boolean",
                                                                        "description": "Send this template after every call, whichever templates the model chooses."
                                                                    },
                                                                    "variable_mappings": {
                                                                        "type": "array",
                                                                        "description": "How to fill each template placeholder.",
                                                                        "items": {
                                                                            "type": "object",
                                                                            "properties": {
                                                                                "index": {
                                                                                    "type": "string",
                                                                                    "description": "The placeholder number, as a string.",
                                                                                    "example": "1"
                                                                                },
                                                                                "extracted_var": {
                                                                                    "type": "string",
                                                                                    "description": "The extracted variable whose value fills this placeholder."
                                                                                },
                                                                                "static_value": {
                                                                                    "type": "string",
                                                                                    "description": "A fixed value for this placeholder. When set, it is used\ninstead of the extracted variable.\n"
                                                                                },
                                                                                "mode": {
                                                                                    "type": "string",
                                                                                    "enum": [
                                                                                        "variable",
                                                                                        "static"
                                                                                    ],
                                                                                    "description": "Which input the dashboard shows for this placeholder. It\ndoes not change the value sent: a `static_value` is used\nfirst, then the extracted variable, then `fallback_value`.\n"
                                                                                },
                                                                                "fallback_value": {
                                                                                    "type": "string",
                                                                                    "description": "The value to use when the variable is not extracted."
                                                                                }
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            ]
                                        },
                                        "workflow": {
                                            "allOf": [
                                                {
                                                    "type": "object",
                                                    "description": "Settings every post-call channel shares.",
                                                    "properties": {
                                                        "enabled": {
                                                            "type": "boolean"
                                                        },
                                                        "include": {
                                                            "type": "array",
                                                            "description": "Which sections to include in this action.",
                                                            "items": {
                                                                "type": "string",
                                                                "enum": [
                                                                    "summary",
                                                                    "extracted_variables",
                                                                    "fullConversation",
                                                                    "sentiment"
                                                                ]
                                                            }
                                                        },
                                                        "extracted_variables": {
                                                            "type": "array",
                                                            "description": "Variables the model should pull out of the conversation for this action.",
                                                            "items": {
                                                                "type": "object",
                                                                "required": [
                                                                    "key",
                                                                    "prompt"
                                                                ],
                                                                "properties": {
                                                                    "key": {
                                                                        "type": "string",
                                                                        "description": "Unique identifier for the variable in the post-call payload.",
                                                                        "example": "customer_issue"
                                                                    },
                                                                    "prompt": {
                                                                        "type": "string",
                                                                        "description": "Instruction for the model on what to pull out of the conversation.",
                                                                        "example": "Identify the main issue the customer is experiencing."
                                                                    }
                                                                }
                                                            }
                                                        },
                                                        "trigger_call_statuses": {
                                                            "type": "array",
                                                            "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                                            "items": {
                                                                "type": "string",
                                                                "enum": [
                                                                    "completed",
                                                                    "voicemail_detected",
                                                                    "failed",
                                                                    "no-answer",
                                                                    "busy",
                                                                    "canceled"
                                                                ]
                                                            }
                                                        }
                                                    }
                                                },
                                                {
                                                    "type": "object",
                                                    "description": "Trigger a workflow after the call.",
                                                    "properties": {
                                                        "workflow_id": {
                                                            "type": "integer",
                                                            "description": "The id of the workflow to run."
                                                        }
                                                    }
                                                }
                                            ]
                                        },
                                        "google_sheets": {
                                            "allOf": [
                                                {
                                                    "type": "object",
                                                    "description": "Settings every post-call channel shares.",
                                                    "properties": {
                                                        "enabled": {
                                                            "type": "boolean"
                                                        },
                                                        "include": {
                                                            "type": "array",
                                                            "description": "Which sections to include in this action.",
                                                            "items": {
                                                                "type": "string",
                                                                "enum": [
                                                                    "summary",
                                                                    "extracted_variables",
                                                                    "fullConversation",
                                                                    "sentiment"
                                                                ]
                                                            }
                                                        },
                                                        "extracted_variables": {
                                                            "type": "array",
                                                            "description": "Variables the model should pull out of the conversation for this action.",
                                                            "items": {
                                                                "type": "object",
                                                                "required": [
                                                                    "key",
                                                                    "prompt"
                                                                ],
                                                                "properties": {
                                                                    "key": {
                                                                        "type": "string",
                                                                        "description": "Unique identifier for the variable in the post-call payload.",
                                                                        "example": "customer_issue"
                                                                    },
                                                                    "prompt": {
                                                                        "type": "string",
                                                                        "description": "Instruction for the model on what to pull out of the conversation.",
                                                                        "example": "Identify the main issue the customer is experiencing."
                                                                    }
                                                                }
                                                            }
                                                        },
                                                        "trigger_call_statuses": {
                                                            "type": "array",
                                                            "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                                            "items": {
                                                                "type": "string",
                                                                "enum": [
                                                                    "completed",
                                                                    "voicemail_detected",
                                                                    "failed",
                                                                    "no-answer",
                                                                    "busy",
                                                                    "canceled"
                                                                ]
                                                            }
                                                        }
                                                    }
                                                },
                                                {
                                                    "type": "object",
                                                    "description": "Append the call to a Google Sheet. Sending this key replaces the\nagent's Google Sheets actions; leaving it out keeps them.\n",
                                                    "properties": {
                                                        "integration_id": {
                                                            "type": "integer",
                                                            "description": "Required. The id of your Google Sheets integration."
                                                        },
                                                        "spreadsheet_id": {
                                                            "type": "string",
                                                            "description": "Required. The id in the sheet's URL, the part after `/d/`."
                                                        },
                                                        "spreadsheet_name": {
                                                            "type": "string"
                                                        },
                                                        "worksheet_name": {
                                                            "type": "string",
                                                            "description": "The tab to append to. Defaults to `Sheet1`."
                                                        }
                                                    }
                                                }
                                            ]
                                        },
                                        "slack": {
                                            "allOf": [
                                                {
                                                    "type": "object",
                                                    "description": "Settings every post-call channel shares.",
                                                    "properties": {
                                                        "enabled": {
                                                            "type": "boolean"
                                                        },
                                                        "include": {
                                                            "type": "array",
                                                            "description": "Which sections to include in this action.",
                                                            "items": {
                                                                "type": "string",
                                                                "enum": [
                                                                    "summary",
                                                                    "extracted_variables",
                                                                    "fullConversation",
                                                                    "sentiment"
                                                                ]
                                                            }
                                                        },
                                                        "extracted_variables": {
                                                            "type": "array",
                                                            "description": "Variables the model should pull out of the conversation for this action.",
                                                            "items": {
                                                                "type": "object",
                                                                "required": [
                                                                    "key",
                                                                    "prompt"
                                                                ],
                                                                "properties": {
                                                                    "key": {
                                                                        "type": "string",
                                                                        "description": "Unique identifier for the variable in the post-call payload.",
                                                                        "example": "customer_issue"
                                                                    },
                                                                    "prompt": {
                                                                        "type": "string",
                                                                        "description": "Instruction for the model on what to pull out of the conversation.",
                                                                        "example": "Identify the main issue the customer is experiencing."
                                                                    }
                                                                }
                                                            }
                                                        },
                                                        "trigger_call_statuses": {
                                                            "type": "array",
                                                            "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                                            "items": {
                                                                "type": "string",
                                                                "enum": [
                                                                    "completed",
                                                                    "voicemail_detected",
                                                                    "failed",
                                                                    "no-answer",
                                                                    "busy",
                                                                    "canceled"
                                                                ]
                                                            }
                                                        }
                                                    }
                                                },
                                                {
                                                    "type": "object",
                                                    "description": "Post the call to a Slack channel. Sending this key replaces the\nagent's Slack actions; leaving it out keeps them.\n",
                                                    "properties": {
                                                        "integration_id": {
                                                            "type": "integer",
                                                            "description": "Required. The id of your Slack integration."
                                                        },
                                                        "channel_id": {
                                                            "type": "string",
                                                            "description": "The channel id. Send this or `channel_name`."
                                                        },
                                                        "channel_name": {
                                                            "type": "string",
                                                            "description": "The channel name. Send this or `channel_id`."
                                                        }
                                                    }
                                                }
                                            ]
                                        },
                                        "salesforce": {
                                            "allOf": [
                                                {
                                                    "type": "object",
                                                    "description": "Settings every post-call channel shares.",
                                                    "properties": {
                                                        "enabled": {
                                                            "type": "boolean"
                                                        },
                                                        "include": {
                                                            "type": "array",
                                                            "description": "Which sections to include in this action.",
                                                            "items": {
                                                                "type": "string",
                                                                "enum": [
                                                                    "summary",
                                                                    "extracted_variables",
                                                                    "fullConversation",
                                                                    "sentiment"
                                                                ]
                                                            }
                                                        },
                                                        "extracted_variables": {
                                                            "type": "array",
                                                            "description": "Variables the model should pull out of the conversation for this action.",
                                                            "items": {
                                                                "type": "object",
                                                                "required": [
                                                                    "key",
                                                                    "prompt"
                                                                ],
                                                                "properties": {
                                                                    "key": {
                                                                        "type": "string",
                                                                        "description": "Unique identifier for the variable in the post-call payload.",
                                                                        "example": "customer_issue"
                                                                    },
                                                                    "prompt": {
                                                                        "type": "string",
                                                                        "description": "Instruction for the model on what to pull out of the conversation.",
                                                                        "example": "Identify the main issue the customer is experiencing."
                                                                    }
                                                                }
                                                            }
                                                        },
                                                        "trigger_call_statuses": {
                                                            "type": "array",
                                                            "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                                            "items": {
                                                                "type": "string",
                                                                "enum": [
                                                                    "completed",
                                                                    "voicemail_detected",
                                                                    "failed",
                                                                    "no-answer",
                                                                    "busy",
                                                                    "canceled"
                                                                ]
                                                            }
                                                        }
                                                    }
                                                },
                                                {
                                                    "type": "object",
                                                    "description": "Create a Salesforce record from the call. Sends a fixed set of\nfields for the object, so it takes no `extracted_variables`.\nSending this key replaces the agent's Salesforce actions;\nleaving it out keeps them.\n",
                                                    "properties": {
                                                        "integration_id": {
                                                            "type": "integer",
                                                            "description": "Required. The id of your Salesforce integration."
                                                        },
                                                        "object_name": {
                                                            "type": "string",
                                                            "enum": [
                                                                "Lead",
                                                                "Contact",
                                                                "Account",
                                                                "Opportunity",
                                                                "Case",
                                                                "Task",
                                                                "Product"
                                                            ],
                                                            "description": "Defaults to `Lead`."
                                                        }
                                                    }
                                                }
                                            ]
                                        },
                                        "hubspot": {
                                            "allOf": [
                                                {
                                                    "type": "object",
                                                    "description": "Settings every post-call channel shares.",
                                                    "properties": {
                                                        "enabled": {
                                                            "type": "boolean"
                                                        },
                                                        "include": {
                                                            "type": "array",
                                                            "description": "Which sections to include in this action.",
                                                            "items": {
                                                                "type": "string",
                                                                "enum": [
                                                                    "summary",
                                                                    "extracted_variables",
                                                                    "fullConversation",
                                                                    "sentiment"
                                                                ]
                                                            }
                                                        },
                                                        "extracted_variables": {
                                                            "type": "array",
                                                            "description": "Variables the model should pull out of the conversation for this action.",
                                                            "items": {
                                                                "type": "object",
                                                                "required": [
                                                                    "key",
                                                                    "prompt"
                                                                ],
                                                                "properties": {
                                                                    "key": {
                                                                        "type": "string",
                                                                        "description": "Unique identifier for the variable in the post-call payload.",
                                                                        "example": "customer_issue"
                                                                    },
                                                                    "prompt": {
                                                                        "type": "string",
                                                                        "description": "Instruction for the model on what to pull out of the conversation.",
                                                                        "example": "Identify the main issue the customer is experiencing."
                                                                    }
                                                                }
                                                            }
                                                        },
                                                        "trigger_call_statuses": {
                                                            "type": "array",
                                                            "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                                            "items": {
                                                                "type": "string",
                                                                "enum": [
                                                                    "completed",
                                                                    "voicemail_detected",
                                                                    "failed",
                                                                    "no-answer",
                                                                    "busy",
                                                                    "canceled"
                                                                ]
                                                            }
                                                        }
                                                    }
                                                },
                                                {
                                                    "type": "object",
                                                    "description": "Create a HubSpot record from the call. Sends a fixed set of\nfields for the object, so it takes no `extracted_variables`.\nSending this key replaces the agent's HubSpot actions; leaving\nit out keeps them.\n",
                                                    "properties": {
                                                        "integration_id": {
                                                            "type": "integer",
                                                            "description": "Required. The id of your HubSpot integration."
                                                        },
                                                        "object_name": {
                                                            "type": "string",
                                                            "enum": [
                                                                "contact",
                                                                "company",
                                                                "deal",
                                                                "ticket"
                                                            ],
                                                            "description": "Required."
                                                        }
                                                    }
                                                }
                                            ]
                                        },
                                        "zoho_bigin": {
                                            "allOf": [
                                                {
                                                    "type": "object",
                                                    "description": "Settings every post-call channel shares.",
                                                    "properties": {
                                                        "enabled": {
                                                            "type": "boolean"
                                                        },
                                                        "include": {
                                                            "type": "array",
                                                            "description": "Which sections to include in this action.",
                                                            "items": {
                                                                "type": "string",
                                                                "enum": [
                                                                    "summary",
                                                                    "extracted_variables",
                                                                    "fullConversation",
                                                                    "sentiment"
                                                                ]
                                                            }
                                                        },
                                                        "extracted_variables": {
                                                            "type": "array",
                                                            "description": "Variables the model should pull out of the conversation for this action.",
                                                            "items": {
                                                                "type": "object",
                                                                "required": [
                                                                    "key",
                                                                    "prompt"
                                                                ],
                                                                "properties": {
                                                                    "key": {
                                                                        "type": "string",
                                                                        "description": "Unique identifier for the variable in the post-call payload.",
                                                                        "example": "customer_issue"
                                                                    },
                                                                    "prompt": {
                                                                        "type": "string",
                                                                        "description": "Instruction for the model on what to pull out of the conversation.",
                                                                        "example": "Identify the main issue the customer is experiencing."
                                                                    }
                                                                }
                                                            }
                                                        },
                                                        "trigger_call_statuses": {
                                                            "type": "array",
                                                            "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                                            "items": {
                                                                "type": "string",
                                                                "enum": [
                                                                    "completed",
                                                                    "voicemail_detected",
                                                                    "failed",
                                                                    "no-answer",
                                                                    "busy",
                                                                    "canceled"
                                                                ]
                                                            }
                                                        }
                                                    }
                                                },
                                                {
                                                    "type": "object",
                                                    "description": "Log the call in Zoho Bigin. Sending this key replaces the\nagent's Zoho Bigin actions; leaving it out keeps them.\n",
                                                    "properties": {
                                                        "integration_id": {
                                                            "type": "integer",
                                                            "description": "Required. The id of your Zoho Bigin integration."
                                                        },
                                                        "create_call_log": {
                                                            "type": "boolean",
                                                            "description": "Log the call. Defaults to true."
                                                        },
                                                        "update_contact": {
                                                            "type": "boolean",
                                                            "description": "Update a matching contact with what the call captured. Defaults to true."
                                                        },
                                                        "create_contact": {
                                                            "type": "boolean",
                                                            "description": "Create a contact when no contact matches. Defaults to true."
                                                        }
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                }
                            ],
                            "description": "Post-call actions for this session only, in the same shape\nas `post_call_actions` on agent create. Email and webhook\nonly. They replace the agent's own post-call actions for\nthis session. Items that cannot be used are skipped and\nlisted in `post_call_actions_ignored`.\n"
                        }
                    },
                    "example": {
                        "name": "Demo User"
                    }
                },
                "metadata": {
                    "type": "object",
                    "additionalProperties": true,
                    "description": "Key-value pairs stored on the session for your own\ntracking (e.g. CRM or lead IDs). Not shared with the\nagent; echoed back as `metadata` in the post-call\nwebhook so you can correlate results with your records.\n",
                    "example": {
                        "crm_lead_id": "lead_9876",
                        "source": "website_form"
                    }
                }
            },
            "required": [
                "agent_id",
                "type"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/sessions/create",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "createWorkflow",
        "description": "Create a workflow. Create a workflow with a draft. Without `graph`, the draft holds one `trigger` node, ready for `editWorkflow` ops. Pass `graph` only to start from a complete graph. The response carries the `revision` you need to edit.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "name": {
                    "type": "string",
                    "description": "A non-empty name."
                },
                "graph": {
                    "type": "object",
                    "description": "A complete graph to start a workflow from, in the same shape `getWorkflow`\nreturns under `draft`. A workflow you read can be sent back as a new one.\nIt is built with the same checks as `editWorkflow` ops. Most callers skip it\nand build with `editWorkflow` instead.\n",
                    "required": [
                        "nodes",
                        "edges"
                    ],
                    "properties": {
                        "nodes": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": [
                                    "id",
                                    "type"
                                ],
                                "properties": {
                                    "id": {
                                        "type": "string",
                                        "description": "Lowercase letters, digits and underscores, starting with a letter. Later nodes read this node's output as `{{ context.<id>.<field> }}`."
                                    },
                                    "type": {
                                        "type": "string",
                                        "description": "A node type from `listWorkflowNodeTypes`."
                                    },
                                    "label": {
                                        "type": "string"
                                    },
                                    "position": {
                                        "type": "object",
                                        "properties": {
                                            "x": {
                                                "type": "number"
                                            },
                                            "y": {
                                                "type": "number"
                                            }
                                        }
                                    },
                                    "config": {
                                        "type": "object",
                                        "additionalProperties": true,
                                        "description": "The node's settings. The fields come from `getWorkflowNodeType`."
                                    }
                                }
                            }
                        },
                        "edges": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": [
                                    "from",
                                    "to"
                                ],
                                "properties": {
                                    "from": {
                                        "type": "string",
                                        "description": "Id of the node the edge starts at."
                                    },
                                    "to": {
                                        "type": "string",
                                        "description": "Id of the node the edge ends at."
                                    },
                                    "handle": {
                                        "type": "string",
                                        "description": "The output of the `from` node. Omit it, or send `default`, for a plain node's only output."
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "required": [
                "name"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/workflows",
        "path_params": [],
        "query_params": [
            "user_id"
        ]
    },
    {
        "name": "deactivateWorkflow",
        "description": "Deactivate a workflow. Turn the published workflow off, so real events stop running it. The workflow and its draft stay. Use `activateWorkflow` to turn it back on.",
        "input_schema": {
            "type": "object",
            "properties": {
                "workflow_id": {
                    "type": "integer",
                    "description": "Id of the workflow."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                }
            },
            "required": [
                "workflow_id"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/workflows/{workflow_id}/deactivate",
        "path_params": [
            "workflow_id"
        ],
        "query_params": [
            "user_id"
        ]
    },
    {
        "name": "deleteAgent",
        "description": "Delete agent. Permanently delete an agent.",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "integer",
                    "description": "The ID of the agent."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                }
            },
            "required": [
                "agent_id"
            ],
            "additionalProperties": true
        },
        "method": "DELETE",
        "path": "/agents/{agent_id}",
        "path_params": [
            "agent_id"
        ],
        "query_params": [
            "user_id"
        ]
    },
    {
        "name": "deleteAgentVersion",
        "description": "Delete an agent version. Delete a saved version.",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "integer",
                    "description": "The ID of the agent."
                },
                "version_number": {
                    "type": "integer",
                    "description": "The version number, as returned in `version_number` from the list or save endpoints."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                }
            },
            "required": [
                "agent_id",
                "version_number"
            ],
            "additionalProperties": true
        },
        "method": "DELETE",
        "path": "/agents/{agent_id}/versions/{version_number}",
        "path_params": [
            "agent_id",
            "version_number"
        ],
        "query_params": [
            "user_id"
        ]
    },
    {
        "name": "deleteClonedVoice",
        "description": "Delete a cloned voice. Delete a cloned voice and remove it from the provider. A voice that is\nstill `processing` cannot be deleted.",
        "input_schema": {
            "type": "object",
            "properties": {
                "voice_id": {
                    "type": "integer",
                    "description": "Id of the cloned voice."
                }
            },
            "required": [
                "voice_id"
            ],
            "additionalProperties": true
        },
        "method": "DELETE",
        "path": "/voices/{voice_id}",
        "path_params": [
            "voice_id"
        ],
        "query_params": []
    },
    {
        "name": "deleteKnowledgeBaseFile",
        "description": "Delete file from knowledge base. Permanently delete a file. Removes it from any attached agents. Cannot be undone.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
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
        "name": "deletePostCallAction",
        "description": "Delete a post-call action. Remove one post-call action from the agent. The agent's other actions are not changed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "integer",
                    "description": "The ID of the agent."
                },
                "action_id": {
                    "type": "integer",
                    "description": "The ID of the post-call action."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                }
            },
            "required": [
                "action_id",
                "agent_id"
            ],
            "additionalProperties": true
        },
        "method": "DELETE",
        "path": "/agents/{agent_id}/post-call-actions/{action_id}",
        "path_params": [
            "agent_id",
            "action_id"
        ],
        "query_params": [
            "user_id"
        ]
    },
    {
        "name": "deleteWorkflow",
        "description": "Delete a workflow. Delete a workflow. Its published version stops running. This cannot be undone, so confirm with the user first. To stop it without deleting, use `deactivateWorkflow`.",
        "input_schema": {
            "type": "object",
            "properties": {
                "workflow_id": {
                    "type": "integer",
                    "description": "Id of the workflow."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                }
            },
            "required": [
                "workflow_id"
            ],
            "additionalProperties": true
        },
        "method": "DELETE",
        "path": "/workflows/{workflow_id}",
        "path_params": [
            "workflow_id"
        ],
        "query_params": [
            "user_id"
        ]
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
        "description": "Detach phone number. Detach a phone number from its agent. Without `user_id`, use any number\nyour key can manage. With `user_id`, the number must belong to that\nclient.",
        "input_schema": {
            "type": "object",
            "properties": {
                "phone_number_id": {
                    "type": "integer",
                    "description": "ID of the phone number to detach.",
                    "example": 23
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller accounts only: the client to act on. Omit it to act on your own account.",
                    "example": 1234
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
        "name": "diffAgentVersion",
        "description": "Diff an agent version. Get a record-level diff for this version. By default it shows what changed in this version compared with the version before it. Use `against=current` to compare with the agent's live config (what restoring this version would change), or `against=<number>` to compare with another version.",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "integer",
                    "description": "The ID of the agent."
                },
                "version_number": {
                    "type": "integer",
                    "description": "The version number, as returned in `version_number` from the list or save endpoints."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "against": {
                    "type": "string",
                    "description": "What to compare against. Omit or `previous` for the version before this one (the default). `current` for the agent's live config. A version number to compare with that version."
                }
            },
            "required": [
                "agent_id",
                "version_number"
            ],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/agents/{agent_id}/versions/{version_number}/diff",
        "path_params": [
            "agent_id",
            "version_number"
        ],
        "query_params": [
            "user_id",
            "against"
        ]
    },
    {
        "name": "dispatchCall",
        "description": "Dispatch call. Initiate a call to a phone number using a specified agent. The\nphone number must include a country code with a leading plus.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
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
                    "description": "Id of a phone number on your account to place the call from (see the phone number list endpoint). Omit to use the platform's default number.",
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
                },
                "metadata": {
                    "type": "object",
                    "additionalProperties": true,
                    "description": "Key-value pairs stored on the call for your own tracking\n(e.g. CRM or lead IDs). Not shared with the agent; echoed\nback as `metadata` in the post-call webhook so you can\ncorrelate results with your records.\n",
                    "example": {
                        "crm_lead_id": "lead_9876",
                        "source": "website_form"
                    }
                },
                "__languages": {
                    "oneOf": [
                        {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        {
                            "type": "string"
                        }
                    ],
                    "description": "Languages this call runs in, replacing the agent's configured\nlist for this call only. The first entry is the language the\ncall opens in. Send an array, or a pipe-separated string such\nas `Hindi|English`. Names the platform does not recognize are\nskipped and listed in `languages_ignored`.\n",
                    "example": [
                        "Tamil",
                        "English"
                    ]
                },
                "__post_call_actions": {
                    "allOf": [
                        {
                            "type": "object",
                            "description": "Side effects that fire once the call ends: email, webhook, Omni CRM,\nCloud WhatsApp, a workflow, Google Sheets, Slack, Salesforce, HubSpot\nor Zoho Bigin.\n",
                            "properties": {
                                "email": {
                                    "type": "object",
                                    "properties": {
                                        "enabled": {
                                            "type": "boolean"
                                        },
                                        "recipients": {
                                            "type": "array",
                                            "description": "Email addresses that should receive the notification.",
                                            "items": {
                                                "type": "string",
                                                "format": "email"
                                            },
                                            "example": [
                                                "support@example.com"
                                            ]
                                        },
                                        "include": {
                                            "type": "array",
                                            "description": "Which sections to include in the email body.",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "summary",
                                                    "extracted_variables",
                                                    "fullConversation",
                                                    "sentiment"
                                                ]
                                            }
                                        },
                                        "extracted_variables": {
                                            "type": "array",
                                            "description": "Variables the model should pull out of the conversation for the email.",
                                            "items": {
                                                "type": "object",
                                                "required": [
                                                    "key",
                                                    "prompt"
                                                ],
                                                "properties": {
                                                    "key": {
                                                        "type": "string",
                                                        "description": "Unique identifier for the variable in the post-call payload.",
                                                        "example": "customer_issue"
                                                    },
                                                    "prompt": {
                                                        "type": "string",
                                                        "description": "Instruction for the model on what to pull out of the conversation.",
                                                        "example": "Identify the main issue the customer is experiencing."
                                                    }
                                                }
                                            }
                                        },
                                        "trigger_call_statuses": {
                                            "type": "array",
                                            "description": "Call outcomes that should fire this action. Omit to\nuse the default (`completed`, `voicemail_detected`).\nPass an explicit list to also include failed calls,\nno-answers, busy signals, etc.\n",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "completed",
                                                    "voicemail_detected",
                                                    "failed",
                                                    "no-answer",
                                                    "busy",
                                                    "canceled"
                                                ]
                                            },
                                            "example": [
                                                "completed",
                                                "voicemail_detected"
                                            ]
                                        }
                                    }
                                },
                                "webhook": {
                                    "type": "object",
                                    "properties": {
                                        "enabled": {
                                            "type": "boolean"
                                        },
                                        "url": {
                                            "type": "string",
                                            "format": "uri",
                                            "description": "Endpoint that receives a POST with the call payload.",
                                            "example": "https://your-webhook-endpoint.com/omnidim-callback"
                                        },
                                        "include": {
                                            "type": "array",
                                            "description": "Which sections to include in the webhook body.",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "summary",
                                                    "extracted_variables",
                                                    "fullConversation",
                                                    "sentiment"
                                                ]
                                            }
                                        },
                                        "extracted_variables": {
                                            "type": "array",
                                            "description": "Variables the model should pull out of the conversation for the webhook.",
                                            "items": {
                                                "type": "object",
                                                "required": [
                                                    "key",
                                                    "prompt"
                                                ],
                                                "properties": {
                                                    "key": {
                                                        "type": "string",
                                                        "description": "Unique identifier for the variable in the post-call payload.",
                                                        "example": "customer_issue"
                                                    },
                                                    "prompt": {
                                                        "type": "string",
                                                        "description": "Instruction for the model on what to pull out of the conversation.",
                                                        "example": "Identify the main issue the customer is experiencing."
                                                    }
                                                }
                                            }
                                        },
                                        "trigger_call_statuses": {
                                            "type": "array",
                                            "description": "Call outcomes that should fire this webhook. Omit to\nuse the default (`completed`, `voicemail_detected`).\n",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "completed",
                                                    "voicemail_detected",
                                                    "failed",
                                                    "no-answer",
                                                    "busy",
                                                    "canceled"
                                                ]
                                            },
                                            "example": [
                                                "completed",
                                                "failed"
                                            ]
                                        }
                                    }
                                },
                                "omni_crm": {
                                    "allOf": [
                                        {
                                            "type": "object",
                                            "description": "Settings every post-call channel shares.",
                                            "properties": {
                                                "enabled": {
                                                    "type": "boolean"
                                                },
                                                "include": {
                                                    "type": "array",
                                                    "description": "Which sections to include in this action.",
                                                    "items": {
                                                        "type": "string",
                                                        "enum": [
                                                            "summary",
                                                            "extracted_variables",
                                                            "fullConversation",
                                                            "sentiment"
                                                        ]
                                                    }
                                                },
                                                "extracted_variables": {
                                                    "type": "array",
                                                    "description": "Variables the model should pull out of the conversation for this action.",
                                                    "items": {
                                                        "type": "object",
                                                        "required": [
                                                            "key",
                                                            "prompt"
                                                        ],
                                                        "properties": {
                                                            "key": {
                                                                "type": "string",
                                                                "description": "Unique identifier for the variable in the post-call payload.",
                                                                "example": "customer_issue"
                                                            },
                                                            "prompt": {
                                                                "type": "string",
                                                                "description": "Instruction for the model on what to pull out of the conversation.",
                                                                "example": "Identify the main issue the customer is experiencing."
                                                            }
                                                        }
                                                    }
                                                },
                                                "trigger_call_statuses": {
                                                    "type": "array",
                                                    "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                                    "items": {
                                                        "type": "string",
                                                        "enum": [
                                                            "completed",
                                                            "voicemail_detected",
                                                            "failed",
                                                            "no-answer",
                                                            "busy",
                                                            "canceled"
                                                        ]
                                                    }
                                                }
                                            }
                                        },
                                        {
                                            "type": "object",
                                            "description": "Save the call to Omni CRM."
                                        }
                                    ]
                                },
                                "cloud_whatsapp": {
                                    "allOf": [
                                        {
                                            "type": "object",
                                            "description": "Settings every post-call channel shares.",
                                            "properties": {
                                                "enabled": {
                                                    "type": "boolean"
                                                },
                                                "include": {
                                                    "type": "array",
                                                    "description": "Which sections to include in this action.",
                                                    "items": {
                                                        "type": "string",
                                                        "enum": [
                                                            "summary",
                                                            "extracted_variables",
                                                            "fullConversation",
                                                            "sentiment"
                                                        ]
                                                    }
                                                },
                                                "extracted_variables": {
                                                    "type": "array",
                                                    "description": "Variables the model should pull out of the conversation for this action.",
                                                    "items": {
                                                        "type": "object",
                                                        "required": [
                                                            "key",
                                                            "prompt"
                                                        ],
                                                        "properties": {
                                                            "key": {
                                                                "type": "string",
                                                                "description": "Unique identifier for the variable in the post-call payload.",
                                                                "example": "customer_issue"
                                                            },
                                                            "prompt": {
                                                                "type": "string",
                                                                "description": "Instruction for the model on what to pull out of the conversation.",
                                                                "example": "Identify the main issue the customer is experiencing."
                                                            }
                                                        }
                                                    }
                                                },
                                                "trigger_call_statuses": {
                                                    "type": "array",
                                                    "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                                    "items": {
                                                        "type": "string",
                                                        "enum": [
                                                            "completed",
                                                            "voicemail_detected",
                                                            "failed",
                                                            "no-answer",
                                                            "busy",
                                                            "canceled"
                                                        ]
                                                    }
                                                }
                                            }
                                        },
                                        {
                                            "type": "object",
                                            "description": "Send a Cloud WhatsApp template message after the call.",
                                            "properties": {
                                                "phone_number_id": {
                                                    "type": "integer",
                                                    "description": "The id of your organization's Cloud WhatsApp number the\nmessage is sent from.\n"
                                                },
                                                "template_id": {
                                                    "type": "integer",
                                                    "description": "An approved template on that number. A template that is not\napproved, or that belongs to another number, is refused.\n"
                                                },
                                                "template_variables": {
                                                    "type": "array",
                                                    "description": "Which extracted variable fills each template placeholder.",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "index": {
                                                                "type": "string",
                                                                "description": "The placeholder number, as a string.",
                                                                "example": "1"
                                                            },
                                                            "extracted_var": {
                                                                "type": "string",
                                                                "description": "The key of the extracted variable whose value fills this placeholder.",
                                                                "example": "customer_name"
                                                            }
                                                        }
                                                    }
                                                },
                                                "templates": {
                                                    "type": "array",
                                                    "description": "One or more templates to send, each with its variable mapping.",
                                                    "items": {
                                                        "type": "object",
                                                        "description": "One Cloud WhatsApp template to send after the call.",
                                                        "properties": {
                                                            "template_id": {
                                                                "type": "integer",
                                                                "description": "An approved template on the chosen number."
                                                            },
                                                            "usage_description": {
                                                                "type": "string",
                                                                "description": "When this template should be sent. After the call, the model reads\nthese descriptions to choose which templates fit the conversation.\n",
                                                                "example": "Send when the caller books an appointment."
                                                            },
                                                            "always_send": {
                                                                "type": "boolean",
                                                                "description": "Send this template after every call, whichever templates the model chooses."
                                                            },
                                                            "variable_mappings": {
                                                                "type": "array",
                                                                "description": "How to fill each template placeholder.",
                                                                "items": {
                                                                    "type": "object",
                                                                    "properties": {
                                                                        "index": {
                                                                            "type": "string",
                                                                            "description": "The placeholder number, as a string.",
                                                                            "example": "1"
                                                                        },
                                                                        "extracted_var": {
                                                                            "type": "string",
                                                                            "description": "The extracted variable whose value fills this placeholder."
                                                                        },
                                                                        "static_value": {
                                                                            "type": "string",
                                                                            "description": "A fixed value for this placeholder. When set, it is used\ninstead of the extracted variable.\n"
                                                                        },
                                                                        "mode": {
                                                                            "type": "string",
                                                                            "enum": [
                                                                                "variable",
                                                                                "static"
                                                                            ],
                                                                            "description": "Which input the dashboard shows for this placeholder. It\ndoes not change the value sent: a `static_value` is used\nfirst, then the extracted variable, then `fallback_value`.\n"
                                                                        },
                                                                        "fallback_value": {
                                                                            "type": "string",
                                                                            "description": "The value to use when the variable is not extracted."
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    ]
                                },
                                "workflow": {
                                    "allOf": [
                                        {
                                            "type": "object",
                                            "description": "Settings every post-call channel shares.",
                                            "properties": {
                                                "enabled": {
                                                    "type": "boolean"
                                                },
                                                "include": {
                                                    "type": "array",
                                                    "description": "Which sections to include in this action.",
                                                    "items": {
                                                        "type": "string",
                                                        "enum": [
                                                            "summary",
                                                            "extracted_variables",
                                                            "fullConversation",
                                                            "sentiment"
                                                        ]
                                                    }
                                                },
                                                "extracted_variables": {
                                                    "type": "array",
                                                    "description": "Variables the model should pull out of the conversation for this action.",
                                                    "items": {
                                                        "type": "object",
                                                        "required": [
                                                            "key",
                                                            "prompt"
                                                        ],
                                                        "properties": {
                                                            "key": {
                                                                "type": "string",
                                                                "description": "Unique identifier for the variable in the post-call payload.",
                                                                "example": "customer_issue"
                                                            },
                                                            "prompt": {
                                                                "type": "string",
                                                                "description": "Instruction for the model on what to pull out of the conversation.",
                                                                "example": "Identify the main issue the customer is experiencing."
                                                            }
                                                        }
                                                    }
                                                },
                                                "trigger_call_statuses": {
                                                    "type": "array",
                                                    "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                                    "items": {
                                                        "type": "string",
                                                        "enum": [
                                                            "completed",
                                                            "voicemail_detected",
                                                            "failed",
                                                            "no-answer",
                                                            "busy",
                                                            "canceled"
                                                        ]
                                                    }
                                                }
                                            }
                                        },
                                        {
                                            "type": "object",
                                            "description": "Trigger a workflow after the call.",
                                            "properties": {
                                                "workflow_id": {
                                                    "type": "integer",
                                                    "description": "The id of the workflow to run."
                                                }
                                            }
                                        }
                                    ]
                                },
                                "google_sheets": {
                                    "allOf": [
                                        {
                                            "type": "object",
                                            "description": "Settings every post-call channel shares.",
                                            "properties": {
                                                "enabled": {
                                                    "type": "boolean"
                                                },
                                                "include": {
                                                    "type": "array",
                                                    "description": "Which sections to include in this action.",
                                                    "items": {
                                                        "type": "string",
                                                        "enum": [
                                                            "summary",
                                                            "extracted_variables",
                                                            "fullConversation",
                                                            "sentiment"
                                                        ]
                                                    }
                                                },
                                                "extracted_variables": {
                                                    "type": "array",
                                                    "description": "Variables the model should pull out of the conversation for this action.",
                                                    "items": {
                                                        "type": "object",
                                                        "required": [
                                                            "key",
                                                            "prompt"
                                                        ],
                                                        "properties": {
                                                            "key": {
                                                                "type": "string",
                                                                "description": "Unique identifier for the variable in the post-call payload.",
                                                                "example": "customer_issue"
                                                            },
                                                            "prompt": {
                                                                "type": "string",
                                                                "description": "Instruction for the model on what to pull out of the conversation.",
                                                                "example": "Identify the main issue the customer is experiencing."
                                                            }
                                                        }
                                                    }
                                                },
                                                "trigger_call_statuses": {
                                                    "type": "array",
                                                    "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                                    "items": {
                                                        "type": "string",
                                                        "enum": [
                                                            "completed",
                                                            "voicemail_detected",
                                                            "failed",
                                                            "no-answer",
                                                            "busy",
                                                            "canceled"
                                                        ]
                                                    }
                                                }
                                            }
                                        },
                                        {
                                            "type": "object",
                                            "description": "Append the call to a Google Sheet. Sending this key replaces the\nagent's Google Sheets actions; leaving it out keeps them.\n",
                                            "properties": {
                                                "integration_id": {
                                                    "type": "integer",
                                                    "description": "Required. The id of your Google Sheets integration."
                                                },
                                                "spreadsheet_id": {
                                                    "type": "string",
                                                    "description": "Required. The id in the sheet's URL, the part after `/d/`."
                                                },
                                                "spreadsheet_name": {
                                                    "type": "string"
                                                },
                                                "worksheet_name": {
                                                    "type": "string",
                                                    "description": "The tab to append to. Defaults to `Sheet1`."
                                                }
                                            }
                                        }
                                    ]
                                },
                                "slack": {
                                    "allOf": [
                                        {
                                            "type": "object",
                                            "description": "Settings every post-call channel shares.",
                                            "properties": {
                                                "enabled": {
                                                    "type": "boolean"
                                                },
                                                "include": {
                                                    "type": "array",
                                                    "description": "Which sections to include in this action.",
                                                    "items": {
                                                        "type": "string",
                                                        "enum": [
                                                            "summary",
                                                            "extracted_variables",
                                                            "fullConversation",
                                                            "sentiment"
                                                        ]
                                                    }
                                                },
                                                "extracted_variables": {
                                                    "type": "array",
                                                    "description": "Variables the model should pull out of the conversation for this action.",
                                                    "items": {
                                                        "type": "object",
                                                        "required": [
                                                            "key",
                                                            "prompt"
                                                        ],
                                                        "properties": {
                                                            "key": {
                                                                "type": "string",
                                                                "description": "Unique identifier for the variable in the post-call payload.",
                                                                "example": "customer_issue"
                                                            },
                                                            "prompt": {
                                                                "type": "string",
                                                                "description": "Instruction for the model on what to pull out of the conversation.",
                                                                "example": "Identify the main issue the customer is experiencing."
                                                            }
                                                        }
                                                    }
                                                },
                                                "trigger_call_statuses": {
                                                    "type": "array",
                                                    "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                                    "items": {
                                                        "type": "string",
                                                        "enum": [
                                                            "completed",
                                                            "voicemail_detected",
                                                            "failed",
                                                            "no-answer",
                                                            "busy",
                                                            "canceled"
                                                        ]
                                                    }
                                                }
                                            }
                                        },
                                        {
                                            "type": "object",
                                            "description": "Post the call to a Slack channel. Sending this key replaces the\nagent's Slack actions; leaving it out keeps them.\n",
                                            "properties": {
                                                "integration_id": {
                                                    "type": "integer",
                                                    "description": "Required. The id of your Slack integration."
                                                },
                                                "channel_id": {
                                                    "type": "string",
                                                    "description": "The channel id. Send this or `channel_name`."
                                                },
                                                "channel_name": {
                                                    "type": "string",
                                                    "description": "The channel name. Send this or `channel_id`."
                                                }
                                            }
                                        }
                                    ]
                                },
                                "salesforce": {
                                    "allOf": [
                                        {
                                            "type": "object",
                                            "description": "Settings every post-call channel shares.",
                                            "properties": {
                                                "enabled": {
                                                    "type": "boolean"
                                                },
                                                "include": {
                                                    "type": "array",
                                                    "description": "Which sections to include in this action.",
                                                    "items": {
                                                        "type": "string",
                                                        "enum": [
                                                            "summary",
                                                            "extracted_variables",
                                                            "fullConversation",
                                                            "sentiment"
                                                        ]
                                                    }
                                                },
                                                "extracted_variables": {
                                                    "type": "array",
                                                    "description": "Variables the model should pull out of the conversation for this action.",
                                                    "items": {
                                                        "type": "object",
                                                        "required": [
                                                            "key",
                                                            "prompt"
                                                        ],
                                                        "properties": {
                                                            "key": {
                                                                "type": "string",
                                                                "description": "Unique identifier for the variable in the post-call payload.",
                                                                "example": "customer_issue"
                                                            },
                                                            "prompt": {
                                                                "type": "string",
                                                                "description": "Instruction for the model on what to pull out of the conversation.",
                                                                "example": "Identify the main issue the customer is experiencing."
                                                            }
                                                        }
                                                    }
                                                },
                                                "trigger_call_statuses": {
                                                    "type": "array",
                                                    "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                                    "items": {
                                                        "type": "string",
                                                        "enum": [
                                                            "completed",
                                                            "voicemail_detected",
                                                            "failed",
                                                            "no-answer",
                                                            "busy",
                                                            "canceled"
                                                        ]
                                                    }
                                                }
                                            }
                                        },
                                        {
                                            "type": "object",
                                            "description": "Create a Salesforce record from the call. Sends a fixed set of\nfields for the object, so it takes no `extracted_variables`.\nSending this key replaces the agent's Salesforce actions;\nleaving it out keeps them.\n",
                                            "properties": {
                                                "integration_id": {
                                                    "type": "integer",
                                                    "description": "Required. The id of your Salesforce integration."
                                                },
                                                "object_name": {
                                                    "type": "string",
                                                    "enum": [
                                                        "Lead",
                                                        "Contact",
                                                        "Account",
                                                        "Opportunity",
                                                        "Case",
                                                        "Task",
                                                        "Product"
                                                    ],
                                                    "description": "Defaults to `Lead`."
                                                }
                                            }
                                        }
                                    ]
                                },
                                "hubspot": {
                                    "allOf": [
                                        {
                                            "type": "object",
                                            "description": "Settings every post-call channel shares.",
                                            "properties": {
                                                "enabled": {
                                                    "type": "boolean"
                                                },
                                                "include": {
                                                    "type": "array",
                                                    "description": "Which sections to include in this action.",
                                                    "items": {
                                                        "type": "string",
                                                        "enum": [
                                                            "summary",
                                                            "extracted_variables",
                                                            "fullConversation",
                                                            "sentiment"
                                                        ]
                                                    }
                                                },
                                                "extracted_variables": {
                                                    "type": "array",
                                                    "description": "Variables the model should pull out of the conversation for this action.",
                                                    "items": {
                                                        "type": "object",
                                                        "required": [
                                                            "key",
                                                            "prompt"
                                                        ],
                                                        "properties": {
                                                            "key": {
                                                                "type": "string",
                                                                "description": "Unique identifier for the variable in the post-call payload.",
                                                                "example": "customer_issue"
                                                            },
                                                            "prompt": {
                                                                "type": "string",
                                                                "description": "Instruction for the model on what to pull out of the conversation.",
                                                                "example": "Identify the main issue the customer is experiencing."
                                                            }
                                                        }
                                                    }
                                                },
                                                "trigger_call_statuses": {
                                                    "type": "array",
                                                    "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                                    "items": {
                                                        "type": "string",
                                                        "enum": [
                                                            "completed",
                                                            "voicemail_detected",
                                                            "failed",
                                                            "no-answer",
                                                            "busy",
                                                            "canceled"
                                                        ]
                                                    }
                                                }
                                            }
                                        },
                                        {
                                            "type": "object",
                                            "description": "Create a HubSpot record from the call. Sends a fixed set of\nfields for the object, so it takes no `extracted_variables`.\nSending this key replaces the agent's HubSpot actions; leaving\nit out keeps them.\n",
                                            "properties": {
                                                "integration_id": {
                                                    "type": "integer",
                                                    "description": "Required. The id of your HubSpot integration."
                                                },
                                                "object_name": {
                                                    "type": "string",
                                                    "enum": [
                                                        "contact",
                                                        "company",
                                                        "deal",
                                                        "ticket"
                                                    ],
                                                    "description": "Required."
                                                }
                                            }
                                        }
                                    ]
                                },
                                "zoho_bigin": {
                                    "allOf": [
                                        {
                                            "type": "object",
                                            "description": "Settings every post-call channel shares.",
                                            "properties": {
                                                "enabled": {
                                                    "type": "boolean"
                                                },
                                                "include": {
                                                    "type": "array",
                                                    "description": "Which sections to include in this action.",
                                                    "items": {
                                                        "type": "string",
                                                        "enum": [
                                                            "summary",
                                                            "extracted_variables",
                                                            "fullConversation",
                                                            "sentiment"
                                                        ]
                                                    }
                                                },
                                                "extracted_variables": {
                                                    "type": "array",
                                                    "description": "Variables the model should pull out of the conversation for this action.",
                                                    "items": {
                                                        "type": "object",
                                                        "required": [
                                                            "key",
                                                            "prompt"
                                                        ],
                                                        "properties": {
                                                            "key": {
                                                                "type": "string",
                                                                "description": "Unique identifier for the variable in the post-call payload.",
                                                                "example": "customer_issue"
                                                            },
                                                            "prompt": {
                                                                "type": "string",
                                                                "description": "Instruction for the model on what to pull out of the conversation.",
                                                                "example": "Identify the main issue the customer is experiencing."
                                                            }
                                                        }
                                                    }
                                                },
                                                "trigger_call_statuses": {
                                                    "type": "array",
                                                    "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                                    "items": {
                                                        "type": "string",
                                                        "enum": [
                                                            "completed",
                                                            "voicemail_detected",
                                                            "failed",
                                                            "no-answer",
                                                            "busy",
                                                            "canceled"
                                                        ]
                                                    }
                                                }
                                            }
                                        },
                                        {
                                            "type": "object",
                                            "description": "Log the call in Zoho Bigin. Sending this key replaces the\nagent's Zoho Bigin actions; leaving it out keeps them.\n",
                                            "properties": {
                                                "integration_id": {
                                                    "type": "integer",
                                                    "description": "Required. The id of your Zoho Bigin integration."
                                                },
                                                "create_call_log": {
                                                    "type": "boolean",
                                                    "description": "Log the call. Defaults to true."
                                                },
                                                "update_contact": {
                                                    "type": "boolean",
                                                    "description": "Update a matching contact with what the call captured. Defaults to true."
                                                },
                                                "create_contact": {
                                                    "type": "boolean",
                                                    "description": "Create a contact when no contact matches. Defaults to true."
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    ],
                    "description": "Post-call actions for this call only, in the same shape as\n`post_call_actions` on agent create. Email and webhook only.\nThey replace the agent's own post-call actions for this call;\nthe agent is not changed. Items that cannot be used are\nskipped and listed in `post_call_actions_ignored`, and the\ncall still goes out. Can also be sent inside `call_context`.\n"
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
        "name": "editWorkflow",
        "description": "Edit a workflow draft. Change the draft with a list of `ops`: add, update, move or delete nodes, and connect or disconnect them. The ops apply all together or not at all. You must send the `revision` from your last read. If you get `409 revision_conflict`, read the workflow again and retry. Secrets read back as `********`. Send them back unchanged to keep the stored value. This edits the draft only. Use `publishWorkflow` to make it live.",
        "input_schema": {
            "type": "object",
            "properties": {
                "workflow_id": {
                    "type": "integer",
                    "description": "Id of the workflow."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "revision": {
                    "type": "string",
                    "description": "The `draft.revision` from your last `getWorkflow` or edit."
                },
                "ops": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "description": "One edit to the draft. Set `op` and the fields that op uses.\n\n| `op` | Fields | Effect |\n|---|---|---|\n| `add_node` | `id`, `type`, `label?`, `config?`, `after?`, `handle?`, `position?` | Adds a node. With `after`, it also connects it to that node (on output `handle`). |\n| `update_node` | `id`, `config?`, `label?` | Merges `config` keys into the node. A `null` value removes a key. |\n| `move_node` | `id`, `position` | Moves a node on the canvas. |\n| `delete_node` | `id` | Deletes a node and its edges. |\n| `connect` | `from`, `to`, `handle?` | Adds an edge. |\n| `disconnect` | `from`, `to`, `handle?` | Removes an edge. |\n",
                        "required": [
                            "op"
                        ],
                        "properties": {
                            "op": {
                                "type": "string",
                                "enum": [
                                    "add_node",
                                    "update_node",
                                    "move_node",
                                    "delete_node",
                                    "connect",
                                    "disconnect"
                                ]
                            },
                            "id": {
                                "type": "string",
                                "description": "Node id. For `add_node`, lowercase letters, digits and underscores, starting with a letter. It must be new."
                            },
                            "type": {
                                "type": "string",
                                "description": "`add_node`: a node type from `listWorkflowNodeTypes`."
                            },
                            "label": {
                                "type": "string",
                                "description": "`add_node`, `update_node`: the name shown on the canvas."
                            },
                            "config": {
                                "type": "object",
                                "additionalProperties": true,
                                "description": "`add_node`, `update_node`: the node's settings. The fields come from\n`getWorkflowNodeType`. Send a secret back as `********` to keep the\nstored value.\n"
                            },
                            "after": {
                                "type": "string",
                                "description": "`add_node`: id of the node to connect the new node to."
                            },
                            "handle": {
                                "type": "string",
                                "description": "`add_node`, `connect`, `disconnect`: the output of the source node. Omit for the default output."
                            },
                            "position": {
                                "type": "object",
                                "description": "`add_node`, `move_node`: canvas position. `add_node` places the node for you if you omit it.",
                                "properties": {
                                    "x": {
                                        "type": "number"
                                    },
                                    "y": {
                                        "type": "number"
                                    }
                                }
                            },
                            "from": {
                                "type": "string",
                                "description": "`connect`, `disconnect`: id of the node the edge starts at."
                            },
                            "to": {
                                "type": "string",
                                "description": "`connect`, `disconnect`: id of the node the edge ends at."
                            }
                        }
                    }
                },
                "name": {
                    "type": "string",
                    "description": "Rename the workflow."
                }
            },
            "required": [
                "ops",
                "revision",
                "workflow_id"
            ],
            "additionalProperties": true
        },
        "method": "PATCH",
        "path": "/workflows/{workflow_id}",
        "path_params": [
            "workflow_id"
        ],
        "query_params": [
            "user_id"
        ]
    },
    {
        "name": "fetchBulkCalls",
        "description": "Fetch bulk calls. List bulk-call campaigns with pagination and optional status filter.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "pageno": {
                    "type": "integer",
                    "default": 1,
                    "description": "Page number for pagination."
                },
                "pagesize": {
                    "type": "integer",
                    "default": 10,
                    "maximum": 150,
                    "description": "Items per page (max 150)."
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
            "user_id",
            "pageno",
            "pagesize",
            "status"
        ]
    },
    {
        "name": "getAccountBalance",
        "description": "Get account balance. Read your organization's wallet: the remaining balance, the minutes\nit buys at your rates, your plan, your concurrency headroom, and\nwhether auto-recharge will refill it.\n\nUse it before a campaign, or on a schedule, so you find out you are\nlow on credit from this endpoint rather than from a call failing\nwith `402 payment_required`.\n\nThe response always describes the organization the API key belongs\nto. There is no parameter for reading another account; resellers\nread a client's figures through the Reseller endpoints.\n\nA balance at or below zero does not always mean calls will stop. An\norganization on usage-based billing (`plan.is_usage_based`) keeps\nplacing calls and is metered to its payment method instead, so check\nthat flag before treating a zero balance as a stop condition.\n\nThe API key's user needs Billing access in your organization. If\nyou get a `403`, an administrator can grant it when Billing is\nenabled for your organization; when it is not, contact support.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/account/balance",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "getAgent",
        "description": "Get agent. Get details of a specific agent by ID. The response also includes a `can_publish` boolean showing whether [version history](/docs/api-reference/agents/listAgentVersions) is turned on for the agent's organization.",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "integer",
                    "description": "The ID of the agent."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                }
            },
            "required": [
                "agent_id"
            ],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/agents/{agent_id}",
        "path_params": [
            "agent_id"
        ],
        "query_params": [
            "user_id"
        ]
    },
    {
        "name": "getBulkCall",
        "description": "Bulk call details. Get detailed information about a bulk-call campaign.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "bulk_call_id": {
                    "type": "integer",
                    "description": "Id of the bulk call campaign."
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
        "query_params": [
            "user_id"
        ]
    },
    {
        "name": "getBulkCallLiveStatus",
        "description": "Bulk call live status. Real-time status of a running bulk-call campaign.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "bulk_call_id": {
                    "type": "integer",
                    "description": "Id of the bulk call campaign."
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
        "query_params": [
            "user_id"
        ]
    },
    {
        "name": "getCallLog",
        "description": "Get call log. Detailed information about a specific call (duration, status, transcript, sentiment, extracted variables).",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "call_log_id": {
                    "type": "integer",
                    "description": "Id of the call log, as returned by the call log list."
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
        "query_params": [
            "user_id"
        ]
    },
    {
        "name": "getClonedVoice",
        "description": "Get a cloned voice. One cloned voice, including its creation `status`.",
        "input_schema": {
            "type": "object",
            "properties": {
                "voice_id": {
                    "type": "integer",
                    "description": "Id of the cloned voice."
                }
            },
            "required": [
                "voice_id"
            ],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/voices/{voice_id}",
        "path_params": [
            "voice_id"
        ],
        "query_params": []
    },
    {
        "name": "getClonedVoiceSample",
        "description": "Play a cloned voice sample. Stream the generated mp3 sample of a cloned voice. Only the owner can\nfetch it. `404` (`sample_not_ready`) when no sample exists yet. The\nrequest needs your API key in the `Authorization` header.",
        "input_schema": {
            "type": "object",
            "properties": {
                "voice_id": {
                    "type": "integer",
                    "description": "Id of the cloned voice."
                }
            },
            "required": [
                "voice_id"
            ],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/voices/{voice_id}/sample",
        "path_params": [
            "voice_id"
        ],
        "query_params": []
    },
    {
        "name": "getVoice",
        "description": "Get voice details. Detailed metadata for a specific voice.",
        "input_schema": {
            "type": "object",
            "properties": {
                "voice_id": {
                    "type": "integer",
                    "description": "Numeric id of the voice, as returned in the `id` field of the voices list."
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
        "name": "getWorkflow",
        "description": "Get a workflow. One workflow with its draft, status and `revision`. Call it before every edit to get the current `revision`. Use `view=structure` to see nodes and edges without config on a large workflow. Secrets read back as `********`.",
        "input_schema": {
            "type": "object",
            "properties": {
                "workflow_id": {
                    "type": "integer",
                    "description": "Id of the workflow."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "view": {
                    "type": "string",
                    "enum": [
                        "structure",
                        "full"
                    ],
                    "default": "full",
                    "description": "`structure` leaves node `config` out."
                }
            },
            "required": [
                "workflow_id"
            ],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/workflows/{workflow_id}",
        "path_params": [
            "workflow_id"
        ],
        "query_params": [
            "user_id",
            "view"
        ]
    },
    {
        "name": "getWorkflowExecution",
        "description": "Get a workflow run. One run of a workflow, with the result of each step. Use it to read the outcome of `testWorkflow`. A run is finished when `state` is `completed`, `failed` or `cancelled`.",
        "input_schema": {
            "type": "object",
            "properties": {
                "workflow_id": {
                    "type": "integer",
                    "description": "Id of the workflow."
                },
                "execution_id": {
                    "type": "integer",
                    "description": "The `execution_id` from `testWorkflow`."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                }
            },
            "required": [
                "execution_id",
                "workflow_id"
            ],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/workflows/{workflow_id}/executions/{execution_id}",
        "path_params": [
            "workflow_id",
            "execution_id"
        ],
        "query_params": [
            "user_id"
        ]
    },
    {
        "name": "getWorkflowNodeType",
        "description": "Get a workflow node type. The settings one node type reads, with their types, required flags and outputs. Call it before you add or edit a node, because its `fields` are the keys of the node's `config`. Use `detail=full` only when you need help text and examples.",
        "input_schema": {
            "type": "object",
            "properties": {
                "node_type": {
                    "type": "string",
                    "description": "A node type from `listWorkflowNodeTypes`, such as `whatsapp`."
                },
                "detail": {
                    "type": "string",
                    "enum": [
                        "minimal",
                        "full"
                    ],
                    "default": "minimal",
                    "description": "`full` adds descriptions, examples and `output_example`."
                }
            },
            "required": [
                "node_type"
            ],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/workflow-node-types/{node_type}",
        "path_params": [
            "node_type"
        ],
        "query_params": [
            "detail"
        ]
    },
    {
        "name": "importExotelNumber",
        "description": "Import Exotel number. Import an Exotel number by providing your Exotel credentials.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
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
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
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
                    "description": "Digits added in front of every number dialed through this trunk. See `sip_strip_country_code` for how it combines with the country code."
                },
                "sip_strip_country_code": {
                    "type": "boolean",
                    "description": "When true, the country code is removed from every number dialed through this trunk. When omitted and `sip_dial_prefix` is set, the country code is removed, so send `false` to keep it."
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
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
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
        "name": "listAgentVersions",
        "description": "List agent versions. List an agent's saved versions, newest first. Includes manual (named) versions, automatic versions, and system backups taken before a restore.",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "integer",
                    "description": "The ID of the agent."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
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
                "search": {
                    "type": "string",
                    "description": "Filter versions whose name matches this substring (case-insensitive)."
                },
                "kind": {
                    "type": "string",
                    "enum": [
                        "manual",
                        "system"
                    ],
                    "description": "Filter versions by kind."
                }
            },
            "required": [
                "agent_id"
            ],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/agents/{agent_id}/versions",
        "path_params": [
            "agent_id"
        ],
        "query_params": [
            "user_id",
            "pageno",
            "pagesize",
            "search",
            "kind"
        ]
    },
    {
        "name": "listAgents",
        "description": "List agents. Retrieve all agents for the authenticated user with pagination support.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
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
            "user_id",
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
        "name": "listBulkCallLines",
        "description": "Bulk call results. Per-contact results for a campaign: what happened on each call, the\nvariables you sent with that contact, and a pointer to the recording.\n\n## Paging\n\nThere is one rule. Call it with no `cursor`, then keep passing back the\n`next_cursor` you were handed until it comes back `null`.\n\n```\ncursor = None\nwhile True:\n    page = GET /lines?pagesize=150&cursor={cursor}\n    handle(page[\"records\"])\n    cursor = page[\"next_cursor\"]\n    if not cursor: break\n```\n\nEach call returns a page of rows, oldest first: `pagesize` goes up to\n150 and defaults to 30. Cursors are opaque, so pass back the string you\nwere given and never build one. No contact is skipped or returned\ntwice, even while the campaign is still dialing.\n\n## Transcripts are not in the row\n\nEach row carries `call.recording_id`, not the conversation. Transcripts\nreach 212 KB, so carrying them here would make one page tens of\nmegabytes. Fetch the one you want from\n`GET /calls/logs/{recording_id}`.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "bulk_call_id": {
                    "type": "integer",
                    "description": "Id of the bulk call campaign."
                },
                "cursor": {
                    "type": "string",
                    "description": "The `next_cursor` from your previous response. Omit it on the first\nrequest. Opaque: pass it back unchanged.\n"
                },
                "pagesize": {
                    "type": "integer",
                    "default": 30,
                    "maximum": 150,
                    "description": "Rows per page. Above 150 the request is refused."
                },
                "call_status": {
                    "type": "string",
                    "enum": [
                        "Pending",
                        "In Progress",
                        "completed",
                        "voicemail_detected",
                        "no-answer",
                        "busy",
                        "Failed",
                        "Skipped",
                        "retry_scheduled",
                        "cancelled"
                    ],
                    "description": "Return only contacts in this state."
                },
                "interaction_status": {
                    "type": "string",
                    "description": "Return only contacts with this interaction outcome."
                },
                "search": {
                    "type": "string",
                    "description": "An exact phone number, matched against the contact's number and the\nnumber that called it. Not a substring search.\n"
                },
                "include_total": {
                    "type": "boolean",
                    "default": false,
                    "description": "Add `total_records` to the response. It costs a count over the whole\nfiltered campaign, so it is off unless you ask. Ask for it once to\nfill a header, not on every page of a walk.\n"
                }
            },
            "required": [
                "bulk_call_id"
            ],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/calls/bulk_call/{bulk_call_id}/lines",
        "path_params": [
            "bulk_call_id"
        ],
        "query_params": [
            "user_id",
            "cursor",
            "pagesize",
            "call_status",
            "interaction_status",
            "search",
            "include_total"
        ]
    },
    {
        "name": "listBulkCallNumbers",
        "description": "List rotation pool. The campaign's number pool, and which number is dialing right now.\n\n`calls_this_cycle` is what `fixed_count` rotation compares against, so\nit is the field to watch for the next rotation. `calls_dispatched` is\nthe number's lifetime total across every cycle.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "bulk_call_id": {
                    "type": "integer",
                    "description": "Id of the bulk call campaign."
                }
            },
            "required": [
                "bulk_call_id"
            ],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/calls/bulk_call/{bulk_call_id}/numbers",
        "path_params": [
            "bulk_call_id"
        ],
        "query_params": [
            "user_id"
        ]
    },
    {
        "name": "listCallLogs",
        "description": "List call logs. Retrieve call logs with pagination and optional filtering.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
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
                    ],
                    "description": "Filter by call outcome."
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
            "user_id",
            "pageno",
            "pagesize",
            "agentid",
            "call_status",
            "bulk_call_id"
        ]
    },
    {
        "name": "listClonedVoices",
        "description": "List cloned voices. Your cloned voices, oldest first, one cursor page at a time. Call it with\nno `cursor`, then pass back the `next_cursor` you were handed until it is\n`null`.\n\nOnce a voice is `ready`, its `voice_id` is the provider voice id to put\nin an agent's `voice.voice_id` with `voice.provider: cartesia`.",
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "default": 20,
                    "maximum": 100,
                    "description": "Rows per page. Above 100 the request is refused."
                },
                "cursor": {
                    "type": "string",
                    "description": "The `next_cursor` from your previous response. Omit it on the first\nrequest. Opaque: pass it back unchanged.\n"
                }
            },
            "required": [],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/voices",
        "path_params": [],
        "query_params": [
            "limit",
            "cursor"
        ]
    },
    {
        "name": "listIntegrations",
        "description": "List integrations. List the integrations connected to your workspace, with each one's `id` and `integration_type`. Stored credentials (tokens, secrets, passwords, API keys, and the values of a custom API's headers and parameters) are never returned: they read `********`. When you create an integration, send the real values: `********` is refused. Accounts that sign in with OAuth (Google Sheets, Slack, HubSpot, Salesforce, Zoho Bigin) are connected in the dashboard.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                }
            },
            "required": [],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/integrations",
        "path_params": [],
        "query_params": [
            "user_id"
        ]
    },
    {
        "name": "listKnowledgeBaseFiles",
        "description": "List knowledge base files. List all knowledge-base files for the authenticated user.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                }
            },
            "required": [],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/knowledge_base/list",
        "path_params": [],
        "query_params": [
            "user_id"
        ]
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
        "description": "List phone numbers. Retrieve the phone numbers on your account, whether you bought them\nfrom the OmniDimension number shop or imported your own.",
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
                    "description": "Items per page (max 150)."
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
        "name": "listPostCallActions",
        "description": "List post-call actions. List every post-call action on the agent, each with its own `id`.",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "integer",
                    "description": "The ID of the agent."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                }
            },
            "required": [
                "agent_id"
            ],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/agents/{agent_id}/post-call-actions",
        "path_params": [
            "agent_id"
        ],
        "query_params": [
            "user_id"
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
        "description": "List voices. Retrieve voices with filtering and pagination support. ElevenLabs\nand Cartesia support advanced filtering by name, language, accent,\nand gender.\nOther providers support basic pagination only.",
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
                        "sarvam",
                        "rime",
                        "playht",
                        "hume",
                        "inworld",
                        "smallest"
                    ],
                    "description": "TTS provider to list voices from. Omit to list across all providers."
                },
                "search": {
                    "type": "string",
                    "description": "Substring match against voice name or description. ElevenLabs and Cartesia."
                },
                "language": {
                    "type": "string",
                    "description": "ISO language code (e.g. `en`, `hi`, `es`). ElevenLabs and Cartesia."
                },
                "accent": {
                    "type": "string",
                    "description": "Accent label (e.g. `american`, `british`). ElevenLabs and Cartesia."
                },
                "gender": {
                    "type": "string",
                    "enum": [
                        "male",
                        "female"
                    ],
                    "description": "Filter voices by gender. ElevenLabs and Cartesia."
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
        "name": "listWorkflowFieldOptions",
        "description": "List choices for a node field. The choices for one `ref` field of a node type, such as the phone numbers, agents or integrations in your account. Call it for every `ref` field and never guess an id. If it returns `400 no_options`, the field is not chosen from a list, so ask the user for the value.",
        "input_schema": {
            "type": "object",
            "properties": {
                "node_type": {
                    "type": "string",
                    "description": "A node type from `listWorkflowNodeTypes`, such as `whatsapp`."
                },
                "field": {
                    "type": "string",
                    "description": "A field name from `getWorkflowNodeType`."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "depends": {
                    "type": "integer",
                    "description": "The value of the field this one depends on (`depends_on` in the node type), such as the chosen phone number id."
                }
            },
            "required": [
                "field",
                "node_type"
            ],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/workflow-node-types/{node_type}/options/{field}",
        "path_params": [
            "node_type",
            "field"
        ],
        "query_params": [
            "user_id",
            "depends"
        ]
    },
    {
        "name": "listWorkflowNodeTypes",
        "description": "List workflow node types. Search the node types a workflow can use, such as `whatsapp`, `voice_ai` or `conditional`. Call it first when you do not know which node to add. Then call `getWorkflowNodeType` for the settings of one type.",
        "input_schema": {
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": "Words to match against the type, label and description, such as `whatsapp`."
                },
                "category": {
                    "type": "string",
                    "enum": [
                        "triggers",
                        "messaging",
                        "calls",
                        "flow",
                        "ai",
                        "crm",
                        "integrations"
                    ],
                    "description": "Only types in this category."
                }
            },
            "required": [],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/workflow-node-types",
        "path_params": [],
        "query_params": [
            "q",
            "category"
        ]
    },
    {
        "name": "listWorkflows",
        "description": "List workflows. Your workflows, oldest first, one cursor page at a time. Use it to find a workflow id. Pass back `next_cursor` until it is `null`.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "limit": {
                    "type": "integer",
                    "default": 20,
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Rows per page."
                },
                "cursor": {
                    "type": "string",
                    "description": "The `next_cursor` from the previous page. Omit it on the first request. Pass it back unchanged."
                }
            },
            "required": [],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/workflows",
        "path_params": [],
        "query_params": [
            "user_id",
            "limit",
            "cursor"
        ]
    },
    {
        "name": "publishWorkflow",
        "description": "Publish a workflow. Make the draft the live version. Real events then run it, unless the workflow is paused. Run `validateWorkflow` first: publish is refused while the draft has errors. Ask the user before you publish.",
        "input_schema": {
            "type": "object",
            "properties": {
                "workflow_id": {
                    "type": "integer",
                    "description": "Id of the workflow."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                }
            },
            "required": [
                "workflow_id"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/workflows/{workflow_id}/publish",
        "path_params": [
            "workflow_id"
        ],
        "query_params": [
            "user_id"
        ]
    },
    {
        "name": "purchasePhoneNumber",
        "description": "Purchase a phone number. Buy a phone number from the OmniDimension number shop. The monthly\nrental comes out of your wallet and the number is added to your\naccount, ready to attach to an agent.",
        "input_schema": {
            "type": "object",
            "properties": {
                "Idempotency-Key": {
                    "type": "string",
                    "description": "Your own unique key for this purchase, for example a\nfresh UUID. Strongly recommended: it is what makes a\nretry safe.\n"
                },
                "region": {
                    "type": "string",
                    "enum": [
                        "IN",
                        "US"
                    ],
                    "description": "Region the number belongs to."
                },
                "phone_number": {
                    "type": "string",
                    "description": "The number to buy, as returned by the search operation.",
                    "example": "+15551234567"
                },
                "carrier": {
                    "type": "string",
                    "description": "The carrier to buy from: pass the `carrier` the search\nresponse named, so you buy from the inventory you searched.\nRequired where the region has more than one carrier;\nomitting it there returns `409 carrier_required`.\n",
                    "example": "carrier-1"
                }
            },
            "required": [
                "carrier",
                "phone_number",
                "region"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/phone_number/purchase",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "regenerateClonedVoiceSample",
        "description": "Regenerate a cloned voice sample. Regenerate the sample audio for a `ready` voice.",
        "input_schema": {
            "type": "object",
            "properties": {
                "voice_id": {
                    "type": "integer",
                    "description": "Id of the cloned voice."
                }
            },
            "required": [
                "voice_id"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/voices/{voice_id}/sample",
        "path_params": [
            "voice_id"
        ],
        "query_params": []
    },
    {
        "name": "releasePhoneNumber",
        "description": "Release a phone number. Give up a phone number and stop its rental, so it is not charged at the\nnext renewal. Only a number currently allocated to the account can be\nreleased.",
        "input_schema": {
            "type": "object",
            "properties": {
                "phone_number": {
                    "type": "string",
                    "description": "The number to release.",
                    "example": "+15551234567"
                }
            },
            "required": [
                "phone_number"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/phone_number/release",
        "path_params": [],
        "query_params": []
    },
    {
        "name": "renameAgentVersion",
        "description": "Rename an agent version. Rename a saved version or edit its note. Version history is immutable otherwise; only the name and note can change.",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "integer",
                    "description": "The ID of the agent."
                },
                "version_number": {
                    "type": "integer",
                    "description": "The version number, as returned in `version_number` from the list or save endpoints."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "name": {
                    "type": "string",
                    "example": "v2 pricing script",
                    "description": "New display name for the version."
                },
                "note": {
                    "type": "string",
                    "example": "Shorter opener, new objection handling.",
                    "description": "New note for the version."
                }
            },
            "required": [
                "agent_id",
                "version_number"
            ],
            "additionalProperties": true
        },
        "method": "PATCH",
        "path": "/agents/{agent_id}/versions/{version_number}",
        "path_params": [
            "agent_id",
            "version_number"
        ],
        "query_params": []
    },
    {
        "name": "restoreAgentVersion",
        "description": "Restore an agent version. Restore a version onto the live agent. Your current setup is saved first as a backup version, so restoring is undoable. Configuration is brought back; any knowledge files or integrations that were deleted since this version was saved can't be re-linked, and are reported in `skipped`.",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "integer",
                    "description": "The ID of the agent."
                },
                "version_number": {
                    "type": "integer",
                    "description": "The version number, as returned in `version_number` from the list or save endpoints."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                }
            },
            "required": [
                "agent_id",
                "version_number"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/agents/{agent_id}/versions/{version_number}/restore",
        "path_params": [
            "agent_id",
            "version_number"
        ],
        "query_params": []
    },
    {
        "name": "retryBulkCall",
        "description": "Retry contacts that did not connect. Re-queue contacts that did not connect, without creating a new campaign.\n\nUse it after a campaign finishes with more no-answers than you expected,\nor when the reason was on your side (a bad window, a number that was\nhaving a bad day). Retried contacts keep their original variables.",
        "input_schema": {
            "type": "object",
            "properties": {
                "bulk_call_id": {
                    "type": "integer",
                    "description": "Id of the bulk call campaign."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "retry_strategy": {
                    "type": "string",
                    "default": "all",
                    "description": "Which contacts to re-queue. `all` takes everything that did\nnot connect. `specific` re-queues only the statuses listed\nin `failure_reasons`.\n"
                },
                "failure_reasons": {
                    "type": "array",
                    "description": "Statuses to re-queue. Read only when `retry_strategy` is\n`specific`; for example `no-answer` and `busy`. Ignored when\n`retry_strategy` is `all`.\n",
                    "items": {
                        "type": "string"
                    }
                }
            },
            "required": [
                "bulk_call_id"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/calls/bulk_call/{bulk_call_id}/manual_retry",
        "path_params": [
            "bulk_call_id"
        ],
        "query_params": []
    },
    {
        "name": "searchPhoneNumbers",
        "description": "Search available phone numbers. Search the OmniDimension number shop for phone numbers available to buy\nin a region. Price and validity are flat per region, so every result\nshows the same `monthly_rental_usd` and `validity_days`, and that is the\nexact amount a purchase will charge.\n\nA region can have more than one carrier, each stocking different\nnumber series. Pass the `carrier` you want; the response names the\ncarrier its results came from, and that is the carrier a purchase has\nto pass.",
        "input_schema": {
            "type": "object",
            "properties": {
                "region": {
                    "type": "string",
                    "enum": [
                        "IN",
                        "US"
                    ],
                    "description": "Region to search in. `IN` and `US` both serve numbers. Which\nregions answer is configuration, so a region with no carrier\nenabled returns `404 not_available` rather than an empty list.\n"
                },
                "carrier": {
                    "type": "string",
                    "description": "Which carrier's stock to search: carriers in a region do not sell\nthe same numbers. Required where a region has more than one\ncarrier; omitting it there returns `409 carrier_required` naming\nthe region's carriers and what each one stocks.\n"
                },
                "pattern": {
                    "type": "string",
                    "description": "Digits or prefix to match within the number."
                },
                "page": {
                    "type": "integer",
                    "minimum": 1,
                    "default": 1,
                    "description": "Page of results to return."
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 150,
                    "default": 20,
                    "description": "Results per page."
                }
            },
            "required": [
                "region"
            ],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/phone_number/search",
        "path_params": [],
        "query_params": [
            "region",
            "carrier",
            "pattern",
            "page",
            "limit"
        ]
    },
    {
        "name": "setBulkCallConcurrency",
        "description": "Change concurrency. Change how many calls the campaign places at once, including while it is\nrunning. Raise it to finish sooner, lower it if your team cannot keep up\nwith transfers or your numbers are being answered less.\n\nThe ceiling is your account's concurrency limit.",
        "input_schema": {
            "type": "object",
            "properties": {
                "bulk_call_id": {
                    "type": "integer",
                    "description": "Id of the bulk call campaign."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "concurrent_call_limit": {
                    "type": "integer",
                    "minimum": 1,
                    "example": 5,
                    "description": "Calls to place at once."
                }
            },
            "required": [
                "bulk_call_id",
                "concurrent_call_limit"
            ],
            "additionalProperties": true
        },
        "method": "PUT",
        "path": "/calls/bulk_call/{bulk_call_id}/concurrency",
        "path_params": [
            "bulk_call_id"
        ],
        "query_params": []
    },
    {
        "name": "setBulkCallDailyTimeControl",
        "description": "Set calling hours. Restrict a campaign to a daily calling window, in the campaign's\ntimezone. Outside the window the campaign holds rather than finishing,\nand resumes the next day.",
        "input_schema": {
            "type": "object",
            "properties": {
                "bulk_call_id": {
                    "type": "integer",
                    "description": "Id of the bulk call campaign."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "enable_daily_hard_stop": {
                    "type": "boolean",
                    "example": true,
                    "description": "Stop dialing at `daily_stop_time` each day."
                },
                "daily_stop_time": {
                    "type": "number",
                    "example": 18,
                    "description": "Hour of day to stop, 0 to 23. Fractions are allowed, so\n`17.5` is 17:30. Required when the hard stop is on.\n"
                },
                "daily_stop_timezone": {
                    "type": "string",
                    "example": "Asia/Kolkata",
                    "description": "Timezone for the stop time."
                },
                "enable_daily_auto_start": {
                    "type": "boolean",
                    "example": true,
                    "description": "Resume dialing at `daily_start_time` each day."
                },
                "daily_start_time": {
                    "type": "number",
                    "example": 9,
                    "description": "Hour of day to resume, 0 to 23. Required when auto start\nis on.\n"
                },
                "daily_start_timezone": {
                    "type": "string",
                    "example": "Asia/Kolkata",
                    "description": "Timezone for the start time."
                }
            },
            "required": [
                "bulk_call_id",
                "enable_daily_auto_start",
                "enable_daily_hard_stop"
            ],
            "additionalProperties": true
        },
        "method": "PUT",
        "path": "/calls/bulk_call/{bulk_call_id}/daily-time-control",
        "path_params": [
            "bulk_call_id"
        ],
        "query_params": []
    },
    {
        "name": "setBulkCallNumberActive",
        "description": "Pause or resume a pool number. Stop or resume dialing from one number in the pool.\n\nPausing is what you want when a number starts going bad mid-campaign:\ndialing moves to the next number in sequence and the paused number keeps\nits history and counters. The last active number of a running campaign\ncannot be paused, since the campaign would have nothing to dial from.\n\nSend the state you want rather than a toggle, so retrying the same\nrequest is harmless.\n\n`assignment_id` is the number's id **within this campaign's pool**, from\nList rotation pool. It is not the `phone_number_id`.",
        "input_schema": {
            "type": "object",
            "properties": {
                "bulk_call_id": {
                    "type": "integer",
                    "description": "Id of the bulk call campaign."
                },
                "assignment_id": {
                    "type": "integer",
                    "description": "The `assignment_id` from List rotation pool."
                },
                "is_active": {
                    "type": "boolean",
                    "example": false,
                    "description": "`false` pauses the number, `true` resumes it."
                }
            },
            "required": [
                "assignment_id",
                "bulk_call_id",
                "is_active"
            ],
            "additionalProperties": true
        },
        "method": "PUT",
        "path": "/calls/bulk_call/{bulk_call_id}/numbers/{assignment_id}",
        "path_params": [
            "bulk_call_id",
            "assignment_id"
        ],
        "query_params": []
    },
    {
        "name": "startBulkCall",
        "description": "Start a draft campaign. Start a campaign that was created with `save_as_draft: true`.\n\nDrafts let you build a campaign over several requests: create it, add\ncontacts in batches, set the number pool, set concurrency, then start\nwhen everything is in place. A campaign that is already running,\nscheduled, or finished cannot be started.",
        "input_schema": {
            "type": "object",
            "properties": {
                "bulk_call_id": {
                    "type": "integer",
                    "description": "Id of the bulk call campaign."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                }
            },
            "required": [
                "bulk_call_id"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/calls/bulk_call/{bulk_call_id}/start",
        "path_params": [
            "bulk_call_id"
        ],
        "query_params": []
    },
    {
        "name": "testWorkflow",
        "description": "Test a workflow. Runs the draft once with payload as the trigger data. Every node runs for real: WhatsApp messages, SMS, emails and calls go out and CRM records change. Ask the user before calling it, and use their own phone number or email in the payload.\n\nIt returns an `execution_id` at once. Poll `getWorkflowExecution` for the result.",
        "input_schema": {
            "type": "object",
            "properties": {
                "workflow_id": {
                    "type": "integer",
                    "description": "Id of the workflow."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "payload": {
                    "type": "object",
                    "additionalProperties": true,
                    "description": "The trigger data. Nodes read it as `{{ context.<trigger id>.<field> }}`. See `output_example` of the trigger node type for its shape."
                }
            },
            "required": [
                "workflow_id"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/workflows/{workflow_id}/test",
        "path_params": [
            "workflow_id"
        ],
        "query_params": [
            "user_id"
        ]
    },
    {
        "name": "updateAgent",
        "description": "Update agent. Update an existing agent. Send only the fields you want to change.\n\n`post_call_actions` replaces the agent's email, webhook, Omni CRM, Cloud WhatsApp and workflow actions as one set, but only when you send at least one of those types. Google Sheets, Slack, Salesforce, HubSpot and Zoho Bigin actions are replaced only when their key is sent, and kept otherwise. If a sent action gives a variable key a new prompt, kept actions that use the same key take the new prompt too. To add, change or remove one action without touching the others, use `/agents/{agent_id}/post-call-actions`.\n\n> **Voicemail detection is an access-gated feature** that we turn on per account. If it isn't enabled for yours yet, [request access](https://omnidim.io/contact-us?reason=product&lock=1) before configuring the `voicemail` object below.",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "integer",
                    "description": "The ID of the agent."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "name": {
                    "type": "string",
                    "description": "Name for the agent.",
                    "example": "Customer Support Agent"
                },
                "welcome_message": {
                    "type": "string",
                    "description": "Initial message the agent will say when answering a call.",
                    "example": "Hello! How can I help you today?"
                },
                "is_welcome_message_dynamic": {
                    "type": "boolean",
                    "description": "When true, the welcome message is treated as a directive the agent uses to generate a tailored greeting for each call, rather than being spoken word for word. When false, the welcome message is spoken exactly as written."
                },
                "is_welcome_message_interruption": {
                    "type": "boolean",
                    "description": "Allow the caller to interrupt the welcome message. When false, the agent finishes speaking the welcome before listening."
                },
                "is_interruption_allowed": {
                    "type": "boolean",
                    "description": "Global toggle for whether the caller can interrupt the agent mid-sentence at any point in the call."
                },
                "dynamic_variables": {
                    "type": "object",
                    "description": "Key/value map used to substitute placeholders in the agent's\nprompt and welcome message at call time. Reference a variable\nin your prompt with `{{variable_name}}`. Useful for\npersonalising the same agent across many calls.\n",
                    "additionalProperties": {
                        "type": "string"
                    },
                    "example": {
                        "customer_name": "Jane Doe",
                        "order_id": "ORD-12345"
                    }
                },
                "context_breakdown": {
                    "type": "array",
                    "description": "List of context breakdowns, each containing `title`, `body`, and optional `is_enabled`.",
                    "items": {
                        "type": "object",
                        "required": [
                            "title",
                            "body"
                        ],
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Title of the breakdown.",
                                "example": "Purpose"
                            },
                            "body": {
                                "type": "string",
                                "description": "Body of the breakdown, the detailed prompt content.",
                                "example": "This agent helps customers with product inquiries and support issues."
                            },
                            "is_enabled": {
                                "type": "boolean",
                                "default": true,
                                "description": "Whether this section is included in the prompt."
                            }
                        }
                    }
                },
                "call_type": {
                    "type": "string",
                    "enum": [
                        "Incoming",
                        "Outgoing"
                    ],
                    "description": "Call type of the assistant."
                },
                "timezone": {
                    "type": "string",
                    "description": "IANA timezone for this agent, for example `Asia/Kolkata`. Sets the local date and time the agent works with during calls. If not set, the account timezone is used as fallback. Pass an empty string to clear it.",
                    "example": "America/New_York"
                },
                "transcriber": {
                    "type": "object",
                    "description": "Configuration for the speech-to-text transcriber.",
                    "properties": {
                        "provider": {
                            "type": "string",
                            "enum": [
                                "deepgram_stream",
                                "cartesia",
                                "sarvam",
                                "azure_stream",
                                "soniox"
                            ],
                            "description": "The speech-to-text provider to use.",
                            "example": "deepgram_stream"
                        },
                        "model": {
                            "type": "string",
                            "description": "Transcription model for the selected provider. For\n`deepgram_stream` this is `nova-3` or `nova-2`; other\nproviders take their own model identifiers.\n",
                            "example": "nova-3"
                        },
                        "language": {
                            "type": "string",
                            "description": "Language code for the transcriber. Format and supported\nvalues depend on the provider (e.g. `en-US` for Deepgram,\n`hi-IN` for Sarvam). Applies regardless of which\n`provider` is selected.\n",
                            "example": "en-US"
                        },
                        "silence_timeout_ms": {
                            "type": "integer",
                            "description": "Silence timeout in milliseconds.",
                            "example": 400
                        },
                        "should_apply_noise_reduction": {
                            "type": "boolean",
                            "description": "Reduce background noise on the inbound audio stream before transcription."
                        },
                        "interruption_min_words": {
                            "type": "integer",
                            "minimum": 1,
                            "description": "Minimum number of words the caller must say before their speech is treated as an interruption.",
                            "example": 2
                        },
                        "max_call_duration_in_sec": {
                            "type": "integer",
                            "minimum": 1,
                            "description": "Hard upper bound on call length in seconds. The agent will end the call once this is reached.",
                            "example": 600
                        },
                        "first_ideal_message": {
                            "type": "string",
                            "description": "First nudge spoken when the caller goes silent past the\nidle threshold. Set `is_first_ideal_message_dynamic` to\n`true` to have the LLM regenerate this each time.\n"
                        },
                        "is_first_ideal_message_dynamic": {
                            "type": "boolean",
                            "description": "When true, `first_ideal_message` is treated as a prompt and the LLM generates a fresh nudge each call."
                        },
                        "second_ideal_message": {
                            "type": "string",
                            "description": "Second nudge spoken if silence continues after the first."
                        },
                        "is_second_ideal_message_dynamic": {
                            "type": "boolean",
                            "description": "When true, `second_ideal_message` is treated as a prompt and the LLM generates a fresh nudge each call."
                        },
                        "numerals": {
                            "type": "boolean",
                            "description": "Convert numbers from words to digits."
                        },
                        "punctuate": {
                            "type": "boolean",
                            "description": "Add punctuation to the transcript."
                        },
                        "smart_format": {
                            "type": "boolean",
                            "description": "Apply smart formatting to the transcript."
                        },
                        "diarize": {
                            "type": "boolean",
                            "description": "Identify different speakers in the transcript."
                        }
                    }
                },
                "model": {
                    "type": "object",
                    "description": "Configuration for the language model.",
                    "properties": {
                        "model": {
                            "type": "string",
                            "enum": [
                                "azure-gpt-4.1-mini",
                                "azure-gpt-4.1-nano",
                                "azure-gpt-4o",
                                "azure-gpt-4o-mini",
                                "gemini-2.5-flash",
                                "gemini-2.5-flash-lite",
                                "gpt-3.5-turbo",
                                "gpt-4.1-mini",
                                "gpt-4.1-nano",
                                "gpt-4o",
                                "gpt-4o-mini",
                                "gpt-5.1",
                                "llama-3.3-70b-versatile"
                            ],
                            "description": "The language model to use. The current catalog is returned by the LLM providers list.",
                            "example": "gpt-4.1-mini"
                        },
                        "temperature": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                            "description": "Controls randomness in the model's output (0.0 to 1.0).",
                            "example": 0.7
                        }
                    }
                },
                "voice": {
                    "type": "object",
                    "description": "Configuration for the text-to-speech voice. `provider` and `voice_id` identify the voice together, so send both to change it. `provider` on its own is not accepted, and a `voice_id` on its own leaves the voice as it was. The other fields here apply independently.",
                    "dependentRequired": {
                        "provider": [
                            "voice_id"
                        ]
                    },
                    "properties": {
                        "provider": {
                            "type": "string",
                            "enum": [
                                "eleven_labs",
                                "google",
                                "cartesia",
                                "sarvam"
                            ],
                            "description": "The voice provider to use. The current catalog is returned by the TTS providers list. Send `voice_id` alongside it.",
                            "example": "eleven_labs"
                        },
                        "voice_id": {
                            "type": "string",
                            "description": "The provider's voice identifier, returned in the `name` field of the voices list (not the numeric `id`). Takes effect when `provider` is sent alongside it.",
                            "example": "JBFqnCBsd6RMkjVDRZzb"
                        },
                        "speech_speed": {
                            "type": "number",
                            "minimum": 0.5,
                            "maximum": 2.0,
                            "default": 1.0,
                            "description": "Playback speed multiplier for the agent's voice. 1.0 is normal speed."
                        }
                    }
                },
                "web_search": {
                    "type": "object",
                    "description": "Configuration for web search capabilities.",
                    "properties": {
                        "enabled": {
                            "type": "boolean",
                            "description": "Enable or disable web search functionality."
                        },
                        "provider": {
                            "type": "string",
                            "enum": [
                                "DuckDuckGo",
                                "openAI"
                            ],
                            "description": "The search provider to use.",
                            "example": "DuckDuckGo"
                        }
                    }
                },
                "post_call_actions": {
                    "type": "object",
                    "description": "Side effects that fire once the call ends: email, webhook, Omni CRM,\nCloud WhatsApp, a workflow, Google Sheets, Slack, Salesforce, HubSpot\nor Zoho Bigin.\n",
                    "properties": {
                        "email": {
                            "type": "object",
                            "properties": {
                                "enabled": {
                                    "type": "boolean"
                                },
                                "recipients": {
                                    "type": "array",
                                    "description": "Email addresses that should receive the notification.",
                                    "items": {
                                        "type": "string",
                                        "format": "email"
                                    },
                                    "example": [
                                        "support@example.com"
                                    ]
                                },
                                "include": {
                                    "type": "array",
                                    "description": "Which sections to include in the email body.",
                                    "items": {
                                        "type": "string",
                                        "enum": [
                                            "summary",
                                            "extracted_variables",
                                            "fullConversation",
                                            "sentiment"
                                        ]
                                    }
                                },
                                "extracted_variables": {
                                    "type": "array",
                                    "description": "Variables the model should pull out of the conversation for the email.",
                                    "items": {
                                        "type": "object",
                                        "required": [
                                            "key",
                                            "prompt"
                                        ],
                                        "properties": {
                                            "key": {
                                                "type": "string",
                                                "description": "Unique identifier for the variable in the post-call payload.",
                                                "example": "customer_issue"
                                            },
                                            "prompt": {
                                                "type": "string",
                                                "description": "Instruction for the model on what to pull out of the conversation.",
                                                "example": "Identify the main issue the customer is experiencing."
                                            }
                                        }
                                    }
                                },
                                "trigger_call_statuses": {
                                    "type": "array",
                                    "description": "Call outcomes that should fire this action. Omit to\nuse the default (`completed`, `voicemail_detected`).\nPass an explicit list to also include failed calls,\nno-answers, busy signals, etc.\n",
                                    "items": {
                                        "type": "string",
                                        "enum": [
                                            "completed",
                                            "voicemail_detected",
                                            "failed",
                                            "no-answer",
                                            "busy",
                                            "canceled"
                                        ]
                                    },
                                    "example": [
                                        "completed",
                                        "voicemail_detected"
                                    ]
                                }
                            }
                        },
                        "webhook": {
                            "type": "object",
                            "properties": {
                                "enabled": {
                                    "type": "boolean"
                                },
                                "url": {
                                    "type": "string",
                                    "format": "uri",
                                    "description": "Endpoint that receives a POST with the call payload.",
                                    "example": "https://your-webhook-endpoint.com/omnidim-callback"
                                },
                                "include": {
                                    "type": "array",
                                    "description": "Which sections to include in the webhook body.",
                                    "items": {
                                        "type": "string",
                                        "enum": [
                                            "summary",
                                            "extracted_variables",
                                            "fullConversation",
                                            "sentiment"
                                        ]
                                    }
                                },
                                "extracted_variables": {
                                    "type": "array",
                                    "description": "Variables the model should pull out of the conversation for the webhook.",
                                    "items": {
                                        "type": "object",
                                        "required": [
                                            "key",
                                            "prompt"
                                        ],
                                        "properties": {
                                            "key": {
                                                "type": "string",
                                                "description": "Unique identifier for the variable in the post-call payload.",
                                                "example": "customer_issue"
                                            },
                                            "prompt": {
                                                "type": "string",
                                                "description": "Instruction for the model on what to pull out of the conversation.",
                                                "example": "Identify the main issue the customer is experiencing."
                                            }
                                        }
                                    }
                                },
                                "trigger_call_statuses": {
                                    "type": "array",
                                    "description": "Call outcomes that should fire this webhook. Omit to\nuse the default (`completed`, `voicemail_detected`).\n",
                                    "items": {
                                        "type": "string",
                                        "enum": [
                                            "completed",
                                            "voicemail_detected",
                                            "failed",
                                            "no-answer",
                                            "busy",
                                            "canceled"
                                        ]
                                    },
                                    "example": [
                                        "completed",
                                        "failed"
                                    ]
                                }
                            }
                        },
                        "omni_crm": {
                            "allOf": [
                                {
                                    "type": "object",
                                    "description": "Settings every post-call channel shares.",
                                    "properties": {
                                        "enabled": {
                                            "type": "boolean"
                                        },
                                        "include": {
                                            "type": "array",
                                            "description": "Which sections to include in this action.",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "summary",
                                                    "extracted_variables",
                                                    "fullConversation",
                                                    "sentiment"
                                                ]
                                            }
                                        },
                                        "extracted_variables": {
                                            "type": "array",
                                            "description": "Variables the model should pull out of the conversation for this action.",
                                            "items": {
                                                "type": "object",
                                                "required": [
                                                    "key",
                                                    "prompt"
                                                ],
                                                "properties": {
                                                    "key": {
                                                        "type": "string",
                                                        "description": "Unique identifier for the variable in the post-call payload.",
                                                        "example": "customer_issue"
                                                    },
                                                    "prompt": {
                                                        "type": "string",
                                                        "description": "Instruction for the model on what to pull out of the conversation.",
                                                        "example": "Identify the main issue the customer is experiencing."
                                                    }
                                                }
                                            }
                                        },
                                        "trigger_call_statuses": {
                                            "type": "array",
                                            "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "completed",
                                                    "voicemail_detected",
                                                    "failed",
                                                    "no-answer",
                                                    "busy",
                                                    "canceled"
                                                ]
                                            }
                                        }
                                    }
                                },
                                {
                                    "type": "object",
                                    "description": "Save the call to Omni CRM."
                                }
                            ]
                        },
                        "cloud_whatsapp": {
                            "allOf": [
                                {
                                    "type": "object",
                                    "description": "Settings every post-call channel shares.",
                                    "properties": {
                                        "enabled": {
                                            "type": "boolean"
                                        },
                                        "include": {
                                            "type": "array",
                                            "description": "Which sections to include in this action.",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "summary",
                                                    "extracted_variables",
                                                    "fullConversation",
                                                    "sentiment"
                                                ]
                                            }
                                        },
                                        "extracted_variables": {
                                            "type": "array",
                                            "description": "Variables the model should pull out of the conversation for this action.",
                                            "items": {
                                                "type": "object",
                                                "required": [
                                                    "key",
                                                    "prompt"
                                                ],
                                                "properties": {
                                                    "key": {
                                                        "type": "string",
                                                        "description": "Unique identifier for the variable in the post-call payload.",
                                                        "example": "customer_issue"
                                                    },
                                                    "prompt": {
                                                        "type": "string",
                                                        "description": "Instruction for the model on what to pull out of the conversation.",
                                                        "example": "Identify the main issue the customer is experiencing."
                                                    }
                                                }
                                            }
                                        },
                                        "trigger_call_statuses": {
                                            "type": "array",
                                            "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "completed",
                                                    "voicemail_detected",
                                                    "failed",
                                                    "no-answer",
                                                    "busy",
                                                    "canceled"
                                                ]
                                            }
                                        }
                                    }
                                },
                                {
                                    "type": "object",
                                    "description": "Send a Cloud WhatsApp template message after the call.",
                                    "properties": {
                                        "phone_number_id": {
                                            "type": "integer",
                                            "description": "The id of your organization's Cloud WhatsApp number the\nmessage is sent from.\n"
                                        },
                                        "template_id": {
                                            "type": "integer",
                                            "description": "An approved template on that number. A template that is not\napproved, or that belongs to another number, is refused.\n"
                                        },
                                        "template_variables": {
                                            "type": "array",
                                            "description": "Which extracted variable fills each template placeholder.",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "index": {
                                                        "type": "string",
                                                        "description": "The placeholder number, as a string.",
                                                        "example": "1"
                                                    },
                                                    "extracted_var": {
                                                        "type": "string",
                                                        "description": "The key of the extracted variable whose value fills this placeholder.",
                                                        "example": "customer_name"
                                                    }
                                                }
                                            }
                                        },
                                        "templates": {
                                            "type": "array",
                                            "description": "One or more templates to send, each with its variable mapping.",
                                            "items": {
                                                "type": "object",
                                                "description": "One Cloud WhatsApp template to send after the call.",
                                                "properties": {
                                                    "template_id": {
                                                        "type": "integer",
                                                        "description": "An approved template on the chosen number."
                                                    },
                                                    "usage_description": {
                                                        "type": "string",
                                                        "description": "When this template should be sent. After the call, the model reads\nthese descriptions to choose which templates fit the conversation.\n",
                                                        "example": "Send when the caller books an appointment."
                                                    },
                                                    "always_send": {
                                                        "type": "boolean",
                                                        "description": "Send this template after every call, whichever templates the model chooses."
                                                    },
                                                    "variable_mappings": {
                                                        "type": "array",
                                                        "description": "How to fill each template placeholder.",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "index": {
                                                                    "type": "string",
                                                                    "description": "The placeholder number, as a string.",
                                                                    "example": "1"
                                                                },
                                                                "extracted_var": {
                                                                    "type": "string",
                                                                    "description": "The extracted variable whose value fills this placeholder."
                                                                },
                                                                "static_value": {
                                                                    "type": "string",
                                                                    "description": "A fixed value for this placeholder. When set, it is used\ninstead of the extracted variable.\n"
                                                                },
                                                                "mode": {
                                                                    "type": "string",
                                                                    "enum": [
                                                                        "variable",
                                                                        "static"
                                                                    ],
                                                                    "description": "Which input the dashboard shows for this placeholder. It\ndoes not change the value sent: a `static_value` is used\nfirst, then the extracted variable, then `fallback_value`.\n"
                                                                },
                                                                "fallback_value": {
                                                                    "type": "string",
                                                                    "description": "The value to use when the variable is not extracted."
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            ]
                        },
                        "workflow": {
                            "allOf": [
                                {
                                    "type": "object",
                                    "description": "Settings every post-call channel shares.",
                                    "properties": {
                                        "enabled": {
                                            "type": "boolean"
                                        },
                                        "include": {
                                            "type": "array",
                                            "description": "Which sections to include in this action.",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "summary",
                                                    "extracted_variables",
                                                    "fullConversation",
                                                    "sentiment"
                                                ]
                                            }
                                        },
                                        "extracted_variables": {
                                            "type": "array",
                                            "description": "Variables the model should pull out of the conversation for this action.",
                                            "items": {
                                                "type": "object",
                                                "required": [
                                                    "key",
                                                    "prompt"
                                                ],
                                                "properties": {
                                                    "key": {
                                                        "type": "string",
                                                        "description": "Unique identifier for the variable in the post-call payload.",
                                                        "example": "customer_issue"
                                                    },
                                                    "prompt": {
                                                        "type": "string",
                                                        "description": "Instruction for the model on what to pull out of the conversation.",
                                                        "example": "Identify the main issue the customer is experiencing."
                                                    }
                                                }
                                            }
                                        },
                                        "trigger_call_statuses": {
                                            "type": "array",
                                            "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "completed",
                                                    "voicemail_detected",
                                                    "failed",
                                                    "no-answer",
                                                    "busy",
                                                    "canceled"
                                                ]
                                            }
                                        }
                                    }
                                },
                                {
                                    "type": "object",
                                    "description": "Trigger a workflow after the call.",
                                    "properties": {
                                        "workflow_id": {
                                            "type": "integer",
                                            "description": "The id of the workflow to run."
                                        }
                                    }
                                }
                            ]
                        },
                        "google_sheets": {
                            "allOf": [
                                {
                                    "type": "object",
                                    "description": "Settings every post-call channel shares.",
                                    "properties": {
                                        "enabled": {
                                            "type": "boolean"
                                        },
                                        "include": {
                                            "type": "array",
                                            "description": "Which sections to include in this action.",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "summary",
                                                    "extracted_variables",
                                                    "fullConversation",
                                                    "sentiment"
                                                ]
                                            }
                                        },
                                        "extracted_variables": {
                                            "type": "array",
                                            "description": "Variables the model should pull out of the conversation for this action.",
                                            "items": {
                                                "type": "object",
                                                "required": [
                                                    "key",
                                                    "prompt"
                                                ],
                                                "properties": {
                                                    "key": {
                                                        "type": "string",
                                                        "description": "Unique identifier for the variable in the post-call payload.",
                                                        "example": "customer_issue"
                                                    },
                                                    "prompt": {
                                                        "type": "string",
                                                        "description": "Instruction for the model on what to pull out of the conversation.",
                                                        "example": "Identify the main issue the customer is experiencing."
                                                    }
                                                }
                                            }
                                        },
                                        "trigger_call_statuses": {
                                            "type": "array",
                                            "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "completed",
                                                    "voicemail_detected",
                                                    "failed",
                                                    "no-answer",
                                                    "busy",
                                                    "canceled"
                                                ]
                                            }
                                        }
                                    }
                                },
                                {
                                    "type": "object",
                                    "description": "Append the call to a Google Sheet. Sending this key replaces the\nagent's Google Sheets actions; leaving it out keeps them.\n",
                                    "properties": {
                                        "integration_id": {
                                            "type": "integer",
                                            "description": "Required. The id of your Google Sheets integration."
                                        },
                                        "spreadsheet_id": {
                                            "type": "string",
                                            "description": "Required. The id in the sheet's URL, the part after `/d/`."
                                        },
                                        "spreadsheet_name": {
                                            "type": "string"
                                        },
                                        "worksheet_name": {
                                            "type": "string",
                                            "description": "The tab to append to. Defaults to `Sheet1`."
                                        }
                                    }
                                }
                            ]
                        },
                        "slack": {
                            "allOf": [
                                {
                                    "type": "object",
                                    "description": "Settings every post-call channel shares.",
                                    "properties": {
                                        "enabled": {
                                            "type": "boolean"
                                        },
                                        "include": {
                                            "type": "array",
                                            "description": "Which sections to include in this action.",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "summary",
                                                    "extracted_variables",
                                                    "fullConversation",
                                                    "sentiment"
                                                ]
                                            }
                                        },
                                        "extracted_variables": {
                                            "type": "array",
                                            "description": "Variables the model should pull out of the conversation for this action.",
                                            "items": {
                                                "type": "object",
                                                "required": [
                                                    "key",
                                                    "prompt"
                                                ],
                                                "properties": {
                                                    "key": {
                                                        "type": "string",
                                                        "description": "Unique identifier for the variable in the post-call payload.",
                                                        "example": "customer_issue"
                                                    },
                                                    "prompt": {
                                                        "type": "string",
                                                        "description": "Instruction for the model on what to pull out of the conversation.",
                                                        "example": "Identify the main issue the customer is experiencing."
                                                    }
                                                }
                                            }
                                        },
                                        "trigger_call_statuses": {
                                            "type": "array",
                                            "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "completed",
                                                    "voicemail_detected",
                                                    "failed",
                                                    "no-answer",
                                                    "busy",
                                                    "canceled"
                                                ]
                                            }
                                        }
                                    }
                                },
                                {
                                    "type": "object",
                                    "description": "Post the call to a Slack channel. Sending this key replaces the\nagent's Slack actions; leaving it out keeps them.\n",
                                    "properties": {
                                        "integration_id": {
                                            "type": "integer",
                                            "description": "Required. The id of your Slack integration."
                                        },
                                        "channel_id": {
                                            "type": "string",
                                            "description": "The channel id. Send this or `channel_name`."
                                        },
                                        "channel_name": {
                                            "type": "string",
                                            "description": "The channel name. Send this or `channel_id`."
                                        }
                                    }
                                }
                            ]
                        },
                        "salesforce": {
                            "allOf": [
                                {
                                    "type": "object",
                                    "description": "Settings every post-call channel shares.",
                                    "properties": {
                                        "enabled": {
                                            "type": "boolean"
                                        },
                                        "include": {
                                            "type": "array",
                                            "description": "Which sections to include in this action.",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "summary",
                                                    "extracted_variables",
                                                    "fullConversation",
                                                    "sentiment"
                                                ]
                                            }
                                        },
                                        "extracted_variables": {
                                            "type": "array",
                                            "description": "Variables the model should pull out of the conversation for this action.",
                                            "items": {
                                                "type": "object",
                                                "required": [
                                                    "key",
                                                    "prompt"
                                                ],
                                                "properties": {
                                                    "key": {
                                                        "type": "string",
                                                        "description": "Unique identifier for the variable in the post-call payload.",
                                                        "example": "customer_issue"
                                                    },
                                                    "prompt": {
                                                        "type": "string",
                                                        "description": "Instruction for the model on what to pull out of the conversation.",
                                                        "example": "Identify the main issue the customer is experiencing."
                                                    }
                                                }
                                            }
                                        },
                                        "trigger_call_statuses": {
                                            "type": "array",
                                            "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "completed",
                                                    "voicemail_detected",
                                                    "failed",
                                                    "no-answer",
                                                    "busy",
                                                    "canceled"
                                                ]
                                            }
                                        }
                                    }
                                },
                                {
                                    "type": "object",
                                    "description": "Create a Salesforce record from the call. Sends a fixed set of\nfields for the object, so it takes no `extracted_variables`.\nSending this key replaces the agent's Salesforce actions;\nleaving it out keeps them.\n",
                                    "properties": {
                                        "integration_id": {
                                            "type": "integer",
                                            "description": "Required. The id of your Salesforce integration."
                                        },
                                        "object_name": {
                                            "type": "string",
                                            "enum": [
                                                "Lead",
                                                "Contact",
                                                "Account",
                                                "Opportunity",
                                                "Case",
                                                "Task",
                                                "Product"
                                            ],
                                            "description": "Defaults to `Lead`."
                                        }
                                    }
                                }
                            ]
                        },
                        "hubspot": {
                            "allOf": [
                                {
                                    "type": "object",
                                    "description": "Settings every post-call channel shares.",
                                    "properties": {
                                        "enabled": {
                                            "type": "boolean"
                                        },
                                        "include": {
                                            "type": "array",
                                            "description": "Which sections to include in this action.",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "summary",
                                                    "extracted_variables",
                                                    "fullConversation",
                                                    "sentiment"
                                                ]
                                            }
                                        },
                                        "extracted_variables": {
                                            "type": "array",
                                            "description": "Variables the model should pull out of the conversation for this action.",
                                            "items": {
                                                "type": "object",
                                                "required": [
                                                    "key",
                                                    "prompt"
                                                ],
                                                "properties": {
                                                    "key": {
                                                        "type": "string",
                                                        "description": "Unique identifier for the variable in the post-call payload.",
                                                        "example": "customer_issue"
                                                    },
                                                    "prompt": {
                                                        "type": "string",
                                                        "description": "Instruction for the model on what to pull out of the conversation.",
                                                        "example": "Identify the main issue the customer is experiencing."
                                                    }
                                                }
                                            }
                                        },
                                        "trigger_call_statuses": {
                                            "type": "array",
                                            "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "completed",
                                                    "voicemail_detected",
                                                    "failed",
                                                    "no-answer",
                                                    "busy",
                                                    "canceled"
                                                ]
                                            }
                                        }
                                    }
                                },
                                {
                                    "type": "object",
                                    "description": "Create a HubSpot record from the call. Sends a fixed set of\nfields for the object, so it takes no `extracted_variables`.\nSending this key replaces the agent's HubSpot actions; leaving\nit out keeps them.\n",
                                    "properties": {
                                        "integration_id": {
                                            "type": "integer",
                                            "description": "Required. The id of your HubSpot integration."
                                        },
                                        "object_name": {
                                            "type": "string",
                                            "enum": [
                                                "contact",
                                                "company",
                                                "deal",
                                                "ticket"
                                            ],
                                            "description": "Required."
                                        }
                                    }
                                }
                            ]
                        },
                        "zoho_bigin": {
                            "allOf": [
                                {
                                    "type": "object",
                                    "description": "Settings every post-call channel shares.",
                                    "properties": {
                                        "enabled": {
                                            "type": "boolean"
                                        },
                                        "include": {
                                            "type": "array",
                                            "description": "Which sections to include in this action.",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "summary",
                                                    "extracted_variables",
                                                    "fullConversation",
                                                    "sentiment"
                                                ]
                                            }
                                        },
                                        "extracted_variables": {
                                            "type": "array",
                                            "description": "Variables the model should pull out of the conversation for this action.",
                                            "items": {
                                                "type": "object",
                                                "required": [
                                                    "key",
                                                    "prompt"
                                                ],
                                                "properties": {
                                                    "key": {
                                                        "type": "string",
                                                        "description": "Unique identifier for the variable in the post-call payload.",
                                                        "example": "customer_issue"
                                                    },
                                                    "prompt": {
                                                        "type": "string",
                                                        "description": "Instruction for the model on what to pull out of the conversation.",
                                                        "example": "Identify the main issue the customer is experiencing."
                                                    }
                                                }
                                            }
                                        },
                                        "trigger_call_statuses": {
                                            "type": "array",
                                            "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                                            "items": {
                                                "type": "string",
                                                "enum": [
                                                    "completed",
                                                    "voicemail_detected",
                                                    "failed",
                                                    "no-answer",
                                                    "busy",
                                                    "canceled"
                                                ]
                                            }
                                        }
                                    }
                                },
                                {
                                    "type": "object",
                                    "description": "Log the call in Zoho Bigin. Sending this key replaces the\nagent's Zoho Bigin actions; leaving it out keeps them.\n",
                                    "properties": {
                                        "integration_id": {
                                            "type": "integer",
                                            "description": "Required. The id of your Zoho Bigin integration."
                                        },
                                        "create_call_log": {
                                            "type": "boolean",
                                            "description": "Log the call. Defaults to true."
                                        },
                                        "update_contact": {
                                            "type": "boolean",
                                            "description": "Update a matching contact with what the call captured. Defaults to true."
                                        },
                                        "create_contact": {
                                            "type": "boolean",
                                            "description": "Create a contact when no contact matches. Defaults to true."
                                        }
                                    }
                                }
                            ]
                        }
                    }
                },
                "transfer": {
                    "type": "object",
                    "description": "Conditional call transfer to a human agent or another number.",
                    "properties": {
                        "enabled": {
                            "type": "boolean"
                        },
                        "transfer_options": {
                            "type": "array",
                            "description": "Where to transfer the call and under what condition. The first matching condition wins. In an agent update, sending this list replaces all saved options. Omit it to keep them unchanged, or send an empty array to clear them.",
                            "items": {
                                "type": "object",
                                "required": [
                                    "number",
                                    "transfer_condition",
                                    "transfer_message"
                                ],
                                "properties": {
                                    "number": {
                                        "type": "string",
                                        "description": "Primary phone number to transfer to. Include country code with leading `+`.",
                                        "example": "+15551234567"
                                    },
                                    "type": {
                                        "type": "string",
                                        "enum": [
                                            "static",
                                            "dynamic"
                                        ],
                                        "default": "static",
                                        "description": "`static` transfers to `number`. `dynamic` lets the agent\npick a number at runtime based on the conversation.\n"
                                    },
                                    "backup_numbers": {
                                        "type": "array",
                                        "description": "Fallback numbers tried if the primary is unreachable.",
                                        "items": {
                                            "type": "string"
                                        }
                                    },
                                    "transfer_condition": {
                                        "type": "string",
                                        "description": "Natural-language condition that triggers this transfer option.",
                                        "example": "Transfer if the customer asks to speak with a human."
                                    },
                                    "transfer_message": {
                                        "type": "string",
                                        "description": "Message the agent says to the caller before executing the transfer.",
                                        "example": "Please hold while I connect you to one of our agents."
                                    }
                                }
                            }
                        }
                    }
                },
                "end_call": {
                    "type": "object",
                    "description": "Hang up automatically when a condition is met.",
                    "properties": {
                        "enabled": {
                            "type": "boolean"
                        },
                        "condition": {
                            "type": "string",
                            "description": "Natural-language condition that triggers ending the call. Only evaluated when `enabled` is true.",
                            "example": "End the call once the customer's issue is resolved."
                        },
                        "message": {
                            "type": "string",
                            "description": "What the agent says before hanging up.",
                            "example": "Thank you for contacting us. Have a great day!"
                        },
                        "message_type": {
                            "type": "string",
                            "enum": [
                                "static",
                                "prompt"
                            ],
                            "description": "`static` speaks `message` verbatim. `prompt` treats\n`message_prompt` as an LLM instruction and generates a\nfresh closing line each call (useful for matching the\ncaller's language and tone).\n"
                        },
                        "message_prompt": {
                            "type": "string",
                            "description": "LLM prompt used to generate the closing line when `message_type` is `prompt`.",
                            "example": "End the call politely in the same language the user is speaking."
                        }
                    }
                },
                "background_track": {
                    "type": "object",
                    "description": "Ambient background noise that plays under the agent's voice.",
                    "properties": {
                        "enabled": {
                            "type": "boolean",
                            "description": "Whether to mix the ambient track under the agent's audio."
                        },
                        "name": {
                            "type": "string",
                            "enum": [
                                "call_center",
                                "filler",
                                "office",
                                "office_1",
                                "restaurant"
                            ],
                            "description": "Ambient track to mix under the agent."
                        },
                        "volume": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                            "default": 0.2,
                            "description": "Volume level on a 0–1 scale. Default 0.2."
                        },
                        "tts_volume_reduction": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                            "description": "Amount to drop the agent's TTS volume while the ambient track plays, on a 0–1 scale. Helps the voice cut through without raising the overall mix."
                        }
                    }
                },
                "initial_ringing_sound_enabled": {
                    "type": "boolean",
                    "description": "Plays a ringing tone after the call is picked up, until the agent starts speaking."
                },
                "voicemail": {
                    "type": "object",
                    "description": "Voicemail / answering-machine handling for outbound calls. Set this with the nested object shown here; the agent object returns these values as the flat fields `voicemail_enabled` and `voicemail_message`. Voicemail detection is an access-gated feature. If it isn't enabled for your account, [request access](https://omnidim.io/contact-us?reason=product&lock=1).",
                    "properties": {
                        "enabled": {
                            "type": "boolean",
                            "description": "Detect voicemail and leave your message instead of speaking to a machine."
                        },
                        "message": {
                            "type": "string",
                            "description": "Message to leave when voicemail is detected."
                        }
                    }
                },
                "languages": {
                    "type": "array",
                    "description": "Languages the agent should support. Pass each language as a display-name string exactly as it appears in the dashboard's language picker. Unrecognized names are skipped.",
                    "items": {
                        "type": "string"
                    },
                    "example": [
                        "English (India)",
                        "Hindi"
                    ]
                }
            },
            "required": [
                "agent_id"
            ],
            "additionalProperties": true
        },
        "method": "PUT",
        "path": "/agents/{agent_id}",
        "path_params": [
            "agent_id"
        ],
        "query_params": []
    },
    {
        "name": "updateClonedVoice",
        "description": "Update a cloned voice. Change the name, description or gender of a cloned voice.",
        "input_schema": {
            "type": "object",
            "properties": {
                "voice_id": {
                    "type": "integer",
                    "description": "Id of the cloned voice."
                },
                "name": {
                    "type": "string",
                    "description": "1 to 100 characters."
                },
                "description": {
                    "type": "string"
                },
                "gender": {
                    "type": "string",
                    "enum": [
                        "male",
                        "female"
                    ]
                }
            },
            "required": [
                "voice_id"
            ],
            "additionalProperties": true
        },
        "method": "PATCH",
        "path": "/voices/{voice_id}",
        "path_params": [
            "voice_id"
        ],
        "query_params": []
    },
    {
        "name": "updatePostCallAction",
        "description": "Update a post-call action. Change fields of one post-call action. Fields you don't send keep their value. The `type` cannot change.",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "integer",
                    "description": "The ID of the agent."
                },
                "action_id": {
                    "type": "integer",
                    "description": "The ID of the post-call action."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
                "type": {
                    "type": "string",
                    "enum": [
                        "email",
                        "webhook",
                        "omni_crm",
                        "cloud_whatsapp",
                        "workflow",
                        "google_sheets",
                        "slack",
                        "salesforce",
                        "hubspot",
                        "zoho_bigin"
                    ],
                    "description": "The channel. It cannot change after the action is created:\ndelete it and add a new one. `google_sheets`, `slack`,\n`salesforce`, `hubspot` and `zoho_bigin` deliver through an\naccount connected in the dashboard: pass its id as\n`integration_id` (see List integrations).\n"
                },
                "integration_id": {
                    "type": "integer",
                    "description": "`google_sheets`, `slack`, `salesforce`, `hubspot`, `zoho_bigin`\nonly, required: the id of your integration of that type.\n"
                },
                "spreadsheet_id": {
                    "type": "string",
                    "description": "`google_sheets` only, required: the id in the sheet's URL, the\npart after `/d/`.\n",
                    "example": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
                },
                "spreadsheet_name": {
                    "type": "string",
                    "description": "`google_sheets` only: the sheet's name, for display."
                },
                "worksheet_name": {
                    "type": "string",
                    "description": "`google_sheets` only: the tab to append to. Defaults to `Sheet1`.",
                    "example": "Calls"
                },
                "channel_id": {
                    "type": "string",
                    "description": "`slack` only: the channel id. Send this or `channel_name`.",
                    "example": "C08RTQ1NY81"
                },
                "channel_name": {
                    "type": "string",
                    "description": "`slack` only: the channel name. Send this or `channel_id`.",
                    "example": "sales"
                },
                "object_name": {
                    "type": "string",
                    "description": "`salesforce`: `Lead` (default), `Contact`, `Account`,\n`Opportunity`, `Case`, `Task` or `Product`. `hubspot`, required:\n`contact`, `company`, `deal` or `ticket`. Both send a fixed set of\nfields for the chosen object, so they take no `extracted_variables`.\n"
                },
                "create_call_log": {
                    "type": "boolean",
                    "description": "`zoho_bigin` only: log the call in Zoho Bigin. Defaults to true."
                },
                "update_contact": {
                    "type": "boolean",
                    "description": "`zoho_bigin` only: update a matching contact with what the call captured. Defaults to true."
                },
                "create_contact": {
                    "type": "boolean",
                    "description": "`zoho_bigin` only: create a contact when no contact matches. Defaults to true."
                },
                "recipients": {
                    "type": "array",
                    "description": "`email` only, required: the addresses to notify.",
                    "items": {
                        "type": "string",
                        "format": "email"
                    },
                    "example": [
                        "support@acme-corp.io"
                    ]
                },
                "url": {
                    "type": "string",
                    "format": "uri",
                    "description": "`webhook` only, required: the endpoint that receives a POST with the call payload.",
                    "example": "https://crm.acme-corp.io/omnidim-callback"
                },
                "phone_number_id": {
                    "type": "integer",
                    "description": "`cloud_whatsapp` only, required: your Cloud WhatsApp number the message is sent from. Also send `template_id` or `templates`, or nothing is sent."
                },
                "template_id": {
                    "type": "integer",
                    "description": "`cloud_whatsapp` only: an approved template on that number."
                },
                "template_variables": {
                    "type": "array",
                    "description": "`cloud_whatsapp` only: which extracted variable fills each template placeholder.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "index": {
                                "type": "string",
                                "description": "The placeholder number, as a string.",
                                "example": "1"
                            },
                            "extracted_var": {
                                "type": "string",
                                "description": "The key of the extracted variable whose value fills this placeholder.",
                                "example": "customer_name"
                            }
                        }
                    }
                },
                "templates": {
                    "type": "array",
                    "description": "`cloud_whatsapp` only: one or more templates to send.",
                    "items": {
                        "type": "object",
                        "description": "One Cloud WhatsApp template to send after the call.",
                        "properties": {
                            "template_id": {
                                "type": "integer",
                                "description": "An approved template on the chosen number."
                            },
                            "usage_description": {
                                "type": "string",
                                "description": "When this template should be sent. After the call, the model reads\nthese descriptions to choose which templates fit the conversation.\n",
                                "example": "Send when the caller books an appointment."
                            },
                            "always_send": {
                                "type": "boolean",
                                "description": "Send this template after every call, whichever templates the model chooses."
                            },
                            "variable_mappings": {
                                "type": "array",
                                "description": "How to fill each template placeholder.",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "index": {
                                            "type": "string",
                                            "description": "The placeholder number, as a string.",
                                            "example": "1"
                                        },
                                        "extracted_var": {
                                            "type": "string",
                                            "description": "The extracted variable whose value fills this placeholder."
                                        },
                                        "static_value": {
                                            "type": "string",
                                            "description": "A fixed value for this placeholder. When set, it is used\ninstead of the extracted variable.\n"
                                        },
                                        "mode": {
                                            "type": "string",
                                            "enum": [
                                                "variable",
                                                "static"
                                            ],
                                            "description": "Which input the dashboard shows for this placeholder. It\ndoes not change the value sent: a `static_value` is used\nfirst, then the extracted variable, then `fallback_value`.\n"
                                        },
                                        "fallback_value": {
                                            "type": "string",
                                            "description": "The value to use when the variable is not extracted."
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "workflow_id": {
                    "type": "integer",
                    "description": "`workflow` only, required: the workflow to run. It must have a published version, or the action is skipped."
                },
                "include": {
                    "type": "array",
                    "description": "Which sections to include.",
                    "items": {
                        "type": "string",
                        "enum": [
                            "summary",
                            "extracted_variables",
                            "fullConversation",
                            "sentiment"
                        ]
                    }
                },
                "extracted_variables": {
                    "type": "array",
                    "description": "Variables the model should pull out of the conversation. A key\nalready used by another action on this agent must have the same\nprompt, or the request is refused with `400`. Other actions are\nnever changed to match.\n",
                    "items": {
                        "type": "object",
                        "required": [
                            "key",
                            "prompt"
                        ],
                        "properties": {
                            "key": {
                                "type": "string",
                                "description": "Unique identifier for the variable in the post-call payload.",
                                "example": "customer_issue"
                            },
                            "prompt": {
                                "type": "string",
                                "description": "Instruction for the model on what to pull out of the conversation.",
                                "example": "Identify the main issue the customer is experiencing."
                            }
                        }
                    }
                },
                "trigger_call_statuses": {
                    "type": "array",
                    "description": "Call outcomes that fire this action. Omit to use the default\n(`completed`, `voicemail_detected`).\n",
                    "items": {
                        "type": "string",
                        "enum": [
                            "completed",
                            "voicemail_detected",
                            "failed",
                            "no-answer",
                            "busy",
                            "canceled"
                        ]
                    }
                }
            },
            "required": [
                "action_id",
                "agent_id"
            ],
            "additionalProperties": true
        },
        "method": "PATCH",
        "path": "/agents/{agent_id}/post-call-actions/{action_id}",
        "path_params": [
            "agent_id",
            "action_id"
        ],
        "query_params": []
    },
    {
        "name": "uploadKnowledgeBaseFile",
        "description": "Upload file to knowledge base. Upload a PDF file. The file content must be Base64 encoded.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                },
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
    },
    {
        "name": "validateWorkflow",
        "description": "Validate a workflow draft. Check the draft and list what blocks publish. It changes nothing. Call it after your edits and fix every error before `publishWorkflow`.",
        "input_schema": {
            "type": "object",
            "properties": {
                "workflow_id": {
                    "type": "integer",
                    "description": "Id of the workflow."
                },
                "user_id": {
                    "type": "integer",
                    "description": "Reseller keys only: act as one of your clients by its user id. Omit\nit to act on your own account.\n[How acting for a client works](/docs/reseller/your-clients/acting-as-clients).\n",
                    "example": 1234
                }
            },
            "required": [
                "workflow_id"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/workflows/{workflow_id}/validate",
        "path_params": [
            "workflow_id"
        ],
        "query_params": [
            "user_id"
        ]
    }
]"""

TOOLS: Final[list[Tool]] = json.loads(_TOOLS_JSON)
