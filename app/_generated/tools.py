"""Auto-generated MCP tool registry. Do not edit by hand.

Run `./.venv/bin/python scripts/regen.py` after the upstream OpenAPI spec
or mcp-config.yaml changes.

Source spec:   omnidim.yaml   sha256=0fe03d109b80
Config:        mcp-config.yaml  sha256=0d075000b968
"""
from __future__ import annotations

import json
from typing import Any, Final


Tool = dict[str, Any]


_TOOLS_JSON = r"""[
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
        "description": "Add contacts in bulk. Add up to 1000 contacts to a campaign in one request.\n\nThis is the batch form of Add contact to dynamic campaign. Prefer it\nwhenever you have more than a handful: one request of 500 contacts is\nfar cheaper than 500 requests, on your side and ours.\n\nRepeated numbers are kept, not merged. If the same number appears twice\nwith different variables, it is called twice, because two rows for one\nnumber usually means two real reasons to call.\n\nRows that fail validation are reported in `rejected` and the rest are\nstill added, so a single bad number does not lose the batch. If the\ncampaign has `call_conditions`, rows that do not match are added with\nstatus `Skipped`.",
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {
                    "type": "integer",
                    "description": "Id of the bulk call campaign."
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
                    "type": "integer",
                    "description": "Id of the bulk call campaign."
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
        "query_params": []
    },
    {
        "name": "createAgent",
        "description": "Create agent. Create a new agent with the provided configuration. The full\nconfig supports transcriber, model, voice, web search, transfer,\nend-call conditions, post-call actions (email + webhook),\nambient background track, initial ringing sound, and multilingual support.\n\n> **Voicemail detection is an access-gated feature** that we turn on per\naccount. If it isn't enabled for yours yet,\n[request access](https://omnidim.io/contact-us?reason=product&lock=1)\nbefore configuring the `voicemail` object.",
        "input_schema": {
            "type": "object",
            "properties": {
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
                            "enum": [
                                "nova-3",
                                "nova-2"
                            ],
                            "description": "The model to use for transcription (required when provider is `deepgram_stream`).",
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
                        "model": {
                            "type": "string",
                            "description": "TTS model identifier. Only consumed when `provider` is\n`cartesia` (e.g. `sonic-3.5`). For ElevenLabs and other\nproviders the model is implied by `voice_id` and this\nfield is ignored.\n",
                            "example": "sonic-3.5"
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
                                "DuckDuckGo"
                            ],
                            "description": "The search provider to use.",
                            "example": "DuckDuckGo"
                        }
                    }
                },
                "post_call_actions": {
                    "type": "object",
                    "description": "Side effects that fire once the call ends. Configure email, webhook, or both.",
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
                                            "no_answer",
                                            "busy",
                                            "cancelled"
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
                                            "no_answer",
                                            "busy",
                                            "cancelled"
                                        ]
                                    },
                                    "example": [
                                        "completed",
                                        "failed"
                                    ]
                                }
                            }
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
                "name",
                "welcome_message"
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
        "description": "Create bulk call. Create a new bulk-call campaign. Only name, phone_number_id and a\ncontact_list are needed to dial a list now; every other field adds\none behaviour on top (drafts, rotation, filtering, scheduling,\nretries, dynamic feeding).\n\nThe guide below the field reference walks the whole journey: the\nfirst campaign and its response, each behaviour with a working\nrequest, every refusal message with its fix, and the endpoints that\noperate a campaign once it runs.",
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
        "name": "createSession",
        "description": "Create session. Create a voice Session: a short-lived, single-conversation\nreservation that lets a client hold a live voice chat with your\nagent. This is step 1 of 2. Creating the Session does not start any\naudio on its own; it returns a `ws_url` that a client then connects\nto over WebSocket to actually talk.\n\nCall this endpoint from your server with your API key, and return\nonly the `ws_url` to your client. The API key must never reach the\nbrowser. The `ws_url` is the only thing the client needs, and it is\nsafe to hand out because it is single-use and expires. For how to\nconnect and talk, see \"Connect the client and talk\" below the\nrequest details.",
        "input_schema": {
            "type": "object",
            "properties": {
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
                    "description": "Per-session variables that personalize the conversation.\nSet server-side, so visitors cannot tamper with them.\n",
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
        "name": "deleteAgent",
        "description": "Delete agent. Permanently delete an agent.",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "integer",
                    "description": "The ID of the agent."
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
        "query_params": []
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
            "against"
        ]
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
        "name": "fetchBulkCalls",
        "description": "Fetch bulk calls. List bulk-call campaigns with pagination and optional status filter.",
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
            "pageno",
            "pagesize",
            "status"
        ]
    },
    {
        "name": "getAgent",
        "description": "Get agent. Get details of a specific agent by ID. The response also includes a `version_history_enabled` boolean showing whether [version history](/docs/api-reference/agents/listAgentVersions) is turned on for the agent's organization.",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "integer",
                    "description": "The ID of the agent."
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
        "query_params": []
    },
    {
        "name": "getBulkCall",
        "description": "Bulk call details. Get detailed information about a bulk-call campaign.",
        "input_schema": {
            "type": "object",
            "properties": {
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
        "query_params": []
    },
    {
        "name": "getBulkCallLiveStatus",
        "description": "Bulk call live status. Real-time status of a running bulk-call campaign.",
        "input_schema": {
            "type": "object",
            "properties": {
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
        "query_params": []
    },
    {
        "name": "getCallLog",
        "description": "Get call log. Detailed information about a specific call (duration, status, transcript, sentiment, extracted variables).",
        "input_schema": {
            "type": "object",
            "properties": {
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
        "name": "listAgentVersions",
        "description": "List agent versions. List an agent's saved versions, newest first. Includes manual (named) versions, automatic versions, and system backups taken before a restore.",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "integer",
                    "description": "The ID of the agent."
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
                        "auto",
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
        "name": "listBulkCallLines",
        "description": "Bulk call results. Per-contact results for a campaign: what happened on each call, the\nvariables you sent with that contact, and a pointer to the recording.\n\n## Paging\n\nThere is one rule. Call it with no `cursor`, then keep passing back the\n`next_cursor` you were handed until it comes back `null`.\n\n```\ncursor = None\nwhile True:\n    page = GET /lines?pagesize=150&cursor={cursor}\n    handle(page[\"records\"])\n    cursor = page[\"next_cursor\"]\n    if not cursor: break\n```\n\nEach call returns a page of rows, oldest first: `pagesize` goes up to\n150 and defaults to 30. Cursors are opaque, so pass back the string you\nwere given and never build one. No contact is skipped or returned\ntwice, even while the campaign is still dialing.\n\n## Transcripts are not in the row\n\nEach row carries `call.recording_id`, not the conversation. Transcripts\nreach 212 KB, so carrying them here would make one page tens of\nmegabytes. Fetch the one you want from\n`GET /calls/logs/{recording_id}`.",
        "input_schema": {
            "type": "object",
            "properties": {
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
            "pageno",
            "pagesize",
            "agentid",
            "call_status",
            "bulk_call_id"
        ]
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
                }
            },
            "required": [
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
                "retry_strategy": {
                    "type": "string",
                    "default": "all",
                    "description": "Which contacts to re-queue. `all` takes everything that did\nnot connect.\n"
                },
                "max_retries": {
                    "type": "integer",
                    "description": "Skip contacts already retried this many times."
                },
                "failure_reasons": {
                    "type": "array",
                    "description": "Re-queue only contacts that failed for these reasons, for\nexample `no-answer` and `busy`.\n",
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
        "description": "Search available phone numbers. Search the OmniDimension number shop for phone numbers available to buy\nin a region. Price and validity are flat per region, so every result\nshows the same `monthly_rental_usd` and `validity_days`, and that is the\nexact amount a purchase will charge.",
        "input_schema": {
            "type": "object",
            "properties": {
                "region": {
                    "type": "string",
                    "enum": [
                        "IN",
                        "US"
                    ],
                    "description": "Region to search in."
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
        "name": "updateAgent",
        "description": "Update agent. Update an existing agent. Send only the fields you want to change.\n\n> **Voicemail detection is an access-gated feature** that we turn on per account. If it isn't enabled for yours yet, [request access](https://omnidim.io/contact-us?reason=product&lock=1) before configuring the `voicemail` object below.",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "integer",
                    "description": "The ID of the agent."
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
                            "enum": [
                                "nova-3",
                                "nova-2"
                            ],
                            "description": "The model to use for transcription (required when provider is `deepgram_stream`).",
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
                        "model": {
                            "type": "string",
                            "description": "TTS model identifier. Only consumed when `provider` is\n`cartesia` (e.g. `sonic-3.5`). For ElevenLabs and other\nproviders the model is implied by `voice_id` and this\nfield is ignored.\n",
                            "example": "sonic-3.5"
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
                                "DuckDuckGo"
                            ],
                            "description": "The search provider to use.",
                            "example": "DuckDuckGo"
                        }
                    }
                },
                "post_call_actions": {
                    "type": "object",
                    "description": "Side effects that fire once the call ends. Configure email, webhook, or both.",
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
                                            "no_answer",
                                            "busy",
                                            "cancelled"
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
                                            "no_answer",
                                            "busy",
                                            "cancelled"
                                        ]
                                    },
                                    "example": [
                                        "completed",
                                        "failed"
                                    ]
                                }
                            }
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
