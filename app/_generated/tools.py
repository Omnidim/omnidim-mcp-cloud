"""Auto-generated MCP tool registry. Do not edit by hand.

Run `./.venv/bin/python scripts/regen.py` after the upstream OpenAPI spec
changes.

Source spec:   omnidim.yaml   sha256=d9438991cab0
Internal spec: internal-openapi.yaml   sha256=aea39ad671f3
"""
from __future__ import annotations

import json
from typing import Any, Final


Tool = dict[str, Any]


_TOOLS_JSON = r"""[
    {
        "name": "addBulkCallContact",
        "description": "Add contact to dynamic campaign. Push one contact into a dynamic bulk-call campaign.\n\nDynamic campaigns are created from the dashboard (Bulk Call > Create New\nCampaign > Dynamic Campaign) and wait for contacts. Use this webhook to feed\nthem from a CRM, form or automation platform. The contact is queued at once.\nThe campaign calls it as soon as it is within operating hours.",
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
                },
                "previous_from_number": {
                    "type": "string",
                    "description": "The number that called this person last. With\n`call_back_from_different_number` on, the call goes out\nfrom another number in the pool.\n",
                    "example": "+15557654321"
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Add contact to campaign",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": true
        }
    },
    {
        "name": "addBulkCallContacts",
        "description": "Add contacts in bulk. Add up to 1000 contacts to a campaign in one request.\n\nThis is the batch form of Add contact to dynamic campaign. Prefer it\nwhenever you have more than a handful of contacts.\n\nRepeated numbers are kept, not merged. The same number with different\nvariables is called twice.\n\nRows that fail validation are reported in `rejected`, and the rest are still\nadded. A row missing a column that the campaign's `call_conditions` need is\nalso rejected. The condition values are not evaluated on this route.",
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
                            },
                            "previous_from_number": {
                                "type": "string",
                                "description": "The number that called this person last. With\n`call_back_from_different_number` on, the call goes\nout from another number in the pool.\n",
                                "example": "+15557654321"
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Add contacts to campaign in bulk",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": true
        }
    },
    {
        "name": "addBulkCallNumber",
        "description": "Add number to rotation pool. Add one of your numbers to the campaign's rotation pool.\n\nIt works while the campaign runs, so use it to bring in a fresh number when\nhealthy ones run low.\n\nThe number must be yours and not already in the pool. A number with no agent\ngets this campaign's agent attached. A number attached to a **different**\nagent is refused.",
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Add number to rotation pool",
            "readOnlyHint": false,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "addCaseMessage",
        "description": "Add case message. Post a message on the customer's support case, as the customer. Reopens a resolved case.",
        "input_schema": {
            "type": "object",
            "properties": {
                "case_number": {
                    "type": "string",
                    "description": "The case number."
                },
                "body": {
                    "type": "string",
                    "maxLength": 10000
                }
            },
            "required": [
                "body",
                "case_number"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/support/cases/{case_number}/messages",
        "path_params": [
            "case_number"
        ],
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Add case message",
            "readOnlyHint": false,
            "destructiveHint": false,
            "openWorldHint": false
        },
        "operator_only": true
    },
    {
        "name": "addPostCallAction",
        "description": "Add a post-call action. Add one post-call action to an agent.\n\nThe agent's other actions stay as they are. Send an `Idempotency-Key` header\nto retry safely: the same key and body return the action the first request\nadded.",
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
                "action": {
                    "type": "string",
                    "enum": [
                        "create",
                        "upsert"
                    ],
                    "description": "`salesforce` only: `upsert` finds the record by the caller's number\nand updates it or creates it. `create` creates a new record every\ncall. Defaults to `create`.\n"
                },
                "match_field": {
                    "type": "string",
                    "description": "`salesforce` only, with `upsert`: the phone field the caller's number is looked up in. Defaults to `Phone`.",
                    "example": "Phone"
                },
                "log_call": {
                    "type": "boolean",
                    "description": "`salesforce` only: log the call on the record, with the summary and recording link. Defaults to false."
                },
                "add_note": {
                    "type": "boolean",
                    "description": "`salesforce` only: add the call summary as a note on the record. Defaults to false."
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
        "query_params": [],
        "header_params": [
            "Idempotency-Key"
        ],
        "annotations": {
            "title": "Add a post-call action",
            "readOnlyHint": false,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "addWhatsappCampaignContacts",
        "description": "Add campaign contacts. Add one contact, or up to 500 at once, to a campaign.\n\nOn a draft they are stored for launch. On a running campaign they are sent\nnow. A contact already in the campaign is skipped, so a retry is safe.\n\nEach contact needs a `phone_number`. Every other key is kept and can fill a\ntemplate parameter through `variable_mapping`.",
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {
                    "type": "integer",
                    "description": "Id of a WhatsApp campaign, from `listWhatsappCampaigns`."
                },
                "items": {
                    "type": "array",
                    "maxItems": 500,
                    "items": {
                        "type": "object",
                        "description": "One contact. `phone_number` is required. Any other key is kept on the\ncontact and can fill a template parameter through `variable_mapping`.\n",
                        "required": [
                            "phone_number"
                        ],
                        "properties": {
                            "phone_number": {
                                "type": "string",
                                "description": "The customer's number in international format, such as `+15551234567`."
                            },
                            "contact_name": {
                                "type": "string",
                                "description": "A name for your team. `name` works too."
                            }
                        },
                        "additionalProperties": true
                    },
                    "description": "Send a list, even for one item. It becomes the request body."
                }
            },
            "required": [
                "campaign_id",
                "items"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/whatsapp/campaigns/{campaign_id}/contacts",
        "path_params": [
            "campaign_id"
        ],
        "query_params": [],
        "header_params": [],
        "body_list_arg": "items",
        "annotations": {
            "title": "Add contacts to WhatsApp campaign",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": true
        }
    },
    {
        "name": "addWhatsappOptOut",
        "description": "Block a customer. Block a customer from receiving messages you start from this number.\n\nThe block lasts until you lift it. The response is `201` for a new block. It\nis `200` with the entry unchanged if the customer was already blocked.",
        "input_schema": {
            "type": "object",
            "properties": {
                "number_id": {
                    "type": "integer",
                    "description": "Id of a WhatsApp number in your workspace, from\n[listWhatsappNumbers](/docs/api-reference/whatsapp/listWhatsappNumbers).\nA number in another workspace answers `404`.\n"
                },
                "customer": {
                    "type": "string",
                    "description": "The customer's number in international format, such as `+15551234567`."
                },
                "note": {
                    "type": "string",
                    "maxLength": 500,
                    "description": "A note for your team."
                }
            },
            "required": [
                "customer",
                "number_id"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/whatsapp/numbers/{number_id}/opt_outs",
        "path_params": [
            "number_id"
        ],
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Add WhatsApp opt-out",
            "readOnlyHint": false,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "agentIntegrationActions",
        "description": "Attach an integration to an agent, or detach it.\n\nSet `action` to pick what to do.\n\n`attach`: Attach an integration to an agent. Attach an integration to an agent.\n\nThe agent can use it on its next call. Integrations already attached stay as\nthey are.\n\n`detach`: Detach an integration from an agent. Remove the integration from the agent. The integration itself is kept and stays available to attach again.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "attach",
                        "detach"
                    ],
                    "description": "What to do: attach, detach."
                },
                "agent_id": {
                    "type": "integer",
                    "description": "The ID of the agent."
                },
                "integration_id": {
                    "type": "integer",
                    "description": "The integration's id, from `listIntegrations` or a create response."
                }
            },
            "required": [
                "action",
                "agent_id",
                "integration_id"
            ],
            "additionalProperties": true
        },
        "annotations": {
            "title": "Attach or detach integration",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": true
        },
        "field": "action",
        "actions": {
            "attach": {
                "operation": "attachAgentIntegration",
                "method": "POST",
                "path": "/agents/{agent_id}/integrations",
                "path_params": [
                    "agent_id"
                ],
                "query_params": [],
                "header_params": [],
                "inputs": [
                    "agent_id",
                    "integration_id"
                ],
                "required": [
                    "agent_id",
                    "integration_id"
                ],
                "sends_field": false
            },
            "detach": {
                "operation": "detachAgentIntegration",
                "method": "DELETE",
                "path": "/agents/{agent_id}/integrations/{integration_id}",
                "path_params": [
                    "agent_id",
                    "integration_id"
                ],
                "query_params": [],
                "header_params": [],
                "inputs": [
                    "agent_id",
                    "integration_id"
                ],
                "required": [
                    "agent_id",
                    "integration_id"
                ],
                "sends_field": false
            }
        }
    },
    {
        "name": "agentKnowledgeBaseActions",
        "description": "Attach knowledge-base files to an agent, or detach them.\n\nSet `action` to pick what to do.\n\n`attach`: Attach files to agent. Attach multiple knowledge-base files to an agent.\n\n`detach`: Detach files from agent. Detach multiple knowledge-base files from an agent.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "attach",
                        "detach"
                    ],
                    "description": "What to do: attach, detach."
                },
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
                    "description": "Only for `attach`. Instruction to the agent on when to consult these files.",
                    "example": "Use these documents to answer billing-related questions."
                }
            },
            "required": [
                "action",
                "agent_id",
                "file_ids"
            ],
            "additionalProperties": true
        },
        "annotations": {
            "title": "Attach or detach knowledge base files",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": false
        },
        "field": "action",
        "actions": {
            "attach": {
                "operation": "attachKnowledgeBaseFiles",
                "method": "POST",
                "path": "/knowledge_base/attach",
                "path_params": [],
                "query_params": [],
                "header_params": [],
                "inputs": [
                    "file_ids",
                    "agent_id",
                    "when_to_use"
                ],
                "required": [
                    "agent_id",
                    "file_ids"
                ],
                "sends_field": false
            },
            "detach": {
                "operation": "detachKnowledgeBaseFiles",
                "method": "POST",
                "path": "/knowledge_base/detach",
                "path_params": [],
                "query_params": [],
                "header_params": [],
                "inputs": [
                    "file_ids",
                    "agent_id"
                ],
                "required": [
                    "agent_id",
                    "file_ids"
                ],
                "sends_field": false
            }
        }
    },
    {
        "name": "agentVersionActions",
        "description": "Rename, delete or restore one saved version of an agent.\n\nSet `action` to pick what to do.\n\n`rename`: Rename an agent version. Rename a saved version or edit its note. Version history is immutable otherwise; only the name and note can change.\n\n`delete`: Delete an agent version. Delete a saved version.\n\n`restore`: Restore an agent version. Restore a version onto the live agent.\n\nYour current setup is saved first as a backup version, so restoring is\nundoable. Configuration comes back. Knowledge files or integrations deleted\nsince this version was saved can't be re-linked. They are reported in\n`skipped`.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "rename",
                        "delete",
                        "restore"
                    ],
                    "description": "What to do: rename, delete, restore."
                },
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
                    "description": "Only for `rename`. New display name for the version."
                },
                "note": {
                    "type": "string",
                    "example": "Shorter opener, new objection handling.",
                    "description": "Only for `rename`. New note for the version."
                }
            },
            "required": [
                "action",
                "agent_id",
                "version_number"
            ],
            "additionalProperties": true
        },
        "annotations": {
            "title": "Rename, delete or restore agent version",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": false
        },
        "field": "action",
        "actions": {
            "rename": {
                "operation": "renameAgentVersion",
                "method": "PATCH",
                "path": "/agents/{agent_id}/versions/{version_number}",
                "path_params": [
                    "agent_id",
                    "version_number"
                ],
                "query_params": [],
                "header_params": [],
                "inputs": [
                    "agent_id",
                    "version_number",
                    "name",
                    "note"
                ],
                "required": [
                    "agent_id",
                    "version_number"
                ],
                "sends_field": false
            },
            "delete": {
                "operation": "deleteAgentVersion",
                "method": "DELETE",
                "path": "/agents/{agent_id}/versions/{version_number}",
                "path_params": [
                    "agent_id",
                    "version_number"
                ],
                "query_params": [],
                "header_params": [],
                "inputs": [
                    "agent_id",
                    "version_number"
                ],
                "required": [
                    "agent_id",
                    "version_number"
                ],
                "sends_field": false
            },
            "restore": {
                "operation": "restoreAgentVersion",
                "method": "POST",
                "path": "/agents/{agent_id}/versions/{version_number}/restore",
                "path_params": [
                    "agent_id",
                    "version_number"
                ],
                "query_params": [],
                "header_params": [],
                "inputs": [
                    "agent_id",
                    "version_number"
                ],
                "required": [
                    "agent_id",
                    "version_number"
                ],
                "sends_field": false
            }
        }
    },
    {
        "name": "bulkCallActions",
        "description": "Start, cancel, pause, resume or reschedule a bulk-call campaign.\n\nSet `action` to pick what to do.\n\n`pause`, `resume`, `reschedule`: Bulk call actions. Pause, resume, or reschedule a running campaign.\n\n`cancel`: Cancel bulk call. Cancel a scheduled bulk-call campaign. A campaign that is already running, or is still a draft, is refused.\n\n`start`: Start a draft campaign. Start a campaign that was created with `save_as_draft: true`.\n\nDrafts let you build a campaign over several requests: create it, add\ncontacts in batches, set the number pool, set concurrency, then start\nwhen everything is in place. A campaign that is already running,\nscheduled, or finished cannot be started.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "pause",
                        "resume",
                        "reschedule",
                        "cancel",
                        "start"
                    ],
                    "description": "What to do: pause, resume, reschedule, cancel, start."
                },
                "bulk_call_id": {
                    "type": "integer",
                    "description": "Id of the bulk call campaign."
                },
                "new_scheduled_datetime": {
                    "type": "string",
                    "description": "Only for `pause`, `resume`, `reschedule`. New start time for `reschedule`. Format `YYYY-MM-DD HH:MM:SS`.",
                    "example": "2026-12-25 10:00:00"
                },
                "new_timezone": {
                    "type": "string",
                    "description": "Only for `pause`, `resume`, `reschedule`. IANA timezone for `reschedule`.",
                    "example": "America/New_York"
                }
            },
            "required": [
                "action",
                "bulk_call_id"
            ],
            "additionalProperties": true
        },
        "annotations": {
            "title": "Control bulk campaign",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": true
        },
        "field": "action",
        "actions": {
            "pause": {
                "operation": "bulkCallActions",
                "method": "PUT",
                "path": "/calls/bulk_call/{bulk_call_id}",
                "path_params": [
                    "bulk_call_id"
                ],
                "query_params": [],
                "header_params": [],
                "inputs": [
                    "bulk_call_id",
                    "new_scheduled_datetime",
                    "new_timezone"
                ],
                "required": [
                    "bulk_call_id"
                ],
                "sends_field": true
            },
            "resume": {
                "operation": "bulkCallActions",
                "method": "PUT",
                "path": "/calls/bulk_call/{bulk_call_id}",
                "path_params": [
                    "bulk_call_id"
                ],
                "query_params": [],
                "header_params": [],
                "inputs": [
                    "bulk_call_id",
                    "new_scheduled_datetime",
                    "new_timezone"
                ],
                "required": [
                    "bulk_call_id"
                ],
                "sends_field": true
            },
            "reschedule": {
                "operation": "bulkCallActions",
                "method": "PUT",
                "path": "/calls/bulk_call/{bulk_call_id}",
                "path_params": [
                    "bulk_call_id"
                ],
                "query_params": [],
                "header_params": [],
                "inputs": [
                    "bulk_call_id",
                    "new_scheduled_datetime",
                    "new_timezone"
                ],
                "required": [
                    "bulk_call_id"
                ],
                "sends_field": true
            },
            "cancel": {
                "operation": "cancelBulkCall",
                "method": "DELETE",
                "path": "/calls/bulk_call/{bulk_call_id}",
                "path_params": [
                    "bulk_call_id"
                ],
                "query_params": [],
                "header_params": [],
                "inputs": [
                    "bulk_call_id"
                ],
                "required": [
                    "bulk_call_id"
                ],
                "sends_field": false
            },
            "start": {
                "operation": "startBulkCall",
                "method": "POST",
                "path": "/calls/bulk_call/{bulk_call_id}/start",
                "path_params": [
                    "bulk_call_id"
                ],
                "query_params": [],
                "header_params": [],
                "inputs": [
                    "bulk_call_id"
                ],
                "required": [
                    "bulk_call_id"
                ],
                "sends_field": false
            }
        }
    },
    {
        "name": "createAgent",
        "description": "Create agent. Create an agent from a name and a context. Every other setting is optional.\n\nOptional settings: transcriber, model, voice, web search, transfer,\nend-call conditions, post-call actions (email, webhook, Omni CRM, Cloud\nWhatsApp, or a workflow), ambient background track, initial ringing\nsound and multilingual support.\n\nLeave out `model`, `transcriber` and `voice` to get your organization's\ndefaults, which always work. To pick one, use the LLM, STT or TTS provider\nlist: it shows only the models your organization can use. Any other model is\nrefused, and the error names the default to use.\n\n> **Voicemail detection is access-gated** and turned on per account. If it is off for yours, [request access](https://omnidim.io/contact-us?reason=product&lock=1) before you configure the `voicemail` object.",
        "input_schema": {
            "type": "object",
            "properties": {
                "Idempotency-Key": {
                    "type": "string",
                    "maxLength": 255,
                    "description": "Your own unique key for this agent, for example a fresh UUID.\nSend the same key when you retry. If the first request already\ncreated the agent, you get that agent back instead of a second\none, so a request that timed out is safe to repeat. The same key\nwith a different request body is refused. Keys are kept for 24\nhours.\n"
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
                    "description": "The agent's prompt sections, each with `title`, `body` and optional `is_enabled`. Sending them replaces the whole list and rebuilds the prompt from the enabled sections in order: each `title` becomes a `# title` heading on its own line, with its `body` below it, the same layout the dashboard uses. A save without `context_breakdown` leaves the prompt unchanged.",
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
                    "description": "`Incoming` for an agent that answers calls, `Outgoing` for one that places them, spelled exactly so. Any other value, `incoming` included, saves as `Outgoing` and the response lists it in `warnings`."
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
                            "description": "The speech-to-text provider to use: a `name` from the STT providers list, which returns the ones your organization can use. Leave it out to use your organization's default transcriber.",
                            "example": "deepgram_stream"
                        },
                        "model": {
                            "type": "string",
                            "description": "Transcription model for the selected provider. For\n`deepgram_stream` this is `nova-3` or `nova-2`. Saved only\nfor `deepgram_stream`, `cartesia` and `sarvam`, and only\nwhen `provider` is in the same request.\n",
                            "example": "nova-3"
                        },
                        "language": {
                            "type": [
                                "string",
                                "array"
                            ],
                            "items": {
                                "type": "string"
                            },
                            "description": "Language code for the transcriber. Format and supported\nvalues depend on the provider (e.g. `en-US` for Deepgram,\n`hi-IN` for Sarvam). `soniox` takes a list of codes, such as\n`[\"en\", \"hi\"]`, and an empty list detects the language. Saved only when `provider` is in the\nsame request and is `deepgram_stream`, `cartesia`, `sarvam`,\n`azure` or `soniox`.\n",
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
                            "description": "The language model to use: a `name` from the LLM providers list, which returns exactly the models your organization can use. Leave it out to use your organization's default model.",
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
                    "description": "Configuration for the text-to-speech voice. `provider` and `voice_id` identify the voice together, so send both to change it. `provider` on its own is not accepted, and a `voice_id` on its own leaves the voice as it was. The other fields here apply independently. Leave out `provider` and `voice_id` to use your organization's default voice.",
                    "dependentRequired": {
                        "provider": [
                            "voice_id"
                        ]
                    },
                    "properties": {
                        "provider": {
                            "type": "string",
                            "description": "The voice provider to use: the `service` of a voice from the voices list, which returns only voices your organization can use. Send `voice_id` alongside it. We recommend OmniDimension voices (list them with `provider=featured`) and Cartesia voices. An agent created without `voice` gets the platform default, a Cartesia voice, which every account can use.",
                            "example": "cartesia"
                        },
                        "voice_id": {
                            "type": "string",
                            "description": "The provider's voice identifier, returned in the `name` field of the voices list (not the numeric `id`). Takes effect when `provider` is sent alongside it.",
                            "example": "faf0731e-dfb9-4cfc-8119-259a79b27e12"
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
                    "additionalProperties": true,
                    "description": "Post-call actions: email, webhook, Omni CRM, WhatsApp, workflow, Google Sheets, Slack, Salesforce, HubSpot or Zoho Bigin. On an agent, add them one at a time with addPostCallAction instead. Full shape: https://docs.omnidim.io/docs/per-call-post-call-actions"
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
                            "type": "boolean",
                            "description": "Turn ending the call on or off. Leave it out to keep the current setting. `false` also clears `condition` and `message`."
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
                    "description": "Languages the agent should support. Pass each language as a display-name string exactly as it appears in the dashboard's language picker. Unrecognized names are skipped, and the request is refused when none is recognized. The order is not kept.",
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
        "query_params": [],
        "header_params": [
            "Idempotency-Key"
        ],
        "annotations": {
            "title": "Create agent",
            "readOnlyHint": false,
            "destructiveHint": false,
            "openWorldHint": false
        }
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Save agent version",
            "readOnlyHint": false,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "createBulkCall",
        "description": "Create bulk call. Create a bulk-call campaign.\n\nOnly `name`, `phone_number_id` and a `contact_list` are needed to dial a\nlist now. Every other field adds one behavior: drafts, rotation, filtering,\nscheduling, retries or dynamic feeding.\n\nThe guide below the field reference shows each behavior with a working\nrequest, every refusal message with its fix, and the endpoints that operate\na running campaign.",
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
                        },
                        "call_back_from_different_number": {
                            "type": "boolean",
                            "default": false,
                            "description": "When on, a repeat call to the same person goes out from\na different number than the one that called them last.\nNeeds two or more numbers in the pool.\n"
                        }
                    }
                },
                "skip_known_invalid_numbers": {
                    "type": "boolean",
                    "default": false,
                    "description": "When on, a contact is not dialed if the carrier said its\nnumber does not exist, in any campaign of your organization\nin the last 14 days. That contact shows as a failed call\nwith the reason `Invalid number` and is never retried.\n"
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
                            "description": "Retry attempts, 1 to 10. To disable retries omit it and\nleave `auto_retry` false; never send `0`. Ignored when\n`retry_steps` is set.\n"
                        },
                        "retry_steps": {
                            "type": "array",
                            "minItems": 1,
                            "maxItems": 10,
                            "description": "A different delay for each retry, in order: retry 1\nwaits for the first step, retry 2 for the second, and\nso on. When set, it replaces `auto_retry_schedule`,\n`retry_schedule_days`, `retry_schedule_hours` and\n`retry_limit`: a contact gets one retry per step. Each\ndelay is at most 30 days. A retry that falls outside\nthe campaign's daily calling hours waits until they\nopen again.\n\nA `days` step can also name a time of day with `at`:\n`{\"delay\": 1, \"unit\": \"days\", \"at\": \"10:00\"}` is 10:00\nthe next day, and `{\"delay\": 0, \"unit\": \"days\", \"at\":\n\"16:00\"}` the same day at 16:00. The date and time are\nread in the calling window's timezone,\n`daily_stop_timezone`; a campaign without a window\n(`enable_daily_hard_stop` off) uses its `timezone`.\nEach retry counts from the try before it; a time that\nhas already passed moves to the next day.\n",
                            "items": {
                                "type": "object",
                                "required": [
                                    "delay",
                                    "unit"
                                ],
                                "properties": {
                                    "delay": {
                                        "type": "integer",
                                        "minimum": 0,
                                        "description": "How long to wait, in `unit`. `0` retries right away."
                                    },
                                    "unit": {
                                        "type": "string",
                                        "enum": [
                                            "minutes",
                                            "hours",
                                            "days"
                                        ]
                                    },
                                    "at": {
                                        "type": "string",
                                        "pattern": "^([01][0-9]|2[0-3]):[0-5][0-9]$",
                                        "description": "Time of day, `HH:MM` (24-hour) in\n`daily_stop_timezone`, or in `timezone` when\n`enable_daily_hard_stop` is off. Only on a\n`days` step; `delay: 0` means the same day.\n"
                                    }
                                }
                            },
                            "example": [
                                {
                                    "delay": 1,
                                    "unit": "hours"
                                },
                                {
                                    "delay": 3,
                                    "unit": "hours"
                                },
                                {
                                    "delay": 1,
                                    "unit": "days",
                                    "at": "10:00"
                                },
                                {
                                    "delay": 0,
                                    "unit": "days",
                                    "at": "16:00"
                                }
                            ]
                        },
                        "retry_unanswered": {
                            "type": "string",
                            "enum": [
                                "off",
                                "no_reply",
                                "no_reply_or_short",
                                "model"
                            ],
                            "default": "off",
                            "description": "Also retry calls that connected but got no conversation.\n`no_reply`: the contact never spoke. `no_reply_or_short`:\nthe contact never spoke, or the call lasted at most\n`retry_unanswered_max_seconds`. `model`: the contact\nnever spoke, or post-call analysis read the transcript\nand found no real conversation. Retries follow the same\nschedule or steps as failed calls.\n"
                        },
                        "retry_unanswered_max_seconds": {
                            "type": "integer",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 120,
                            "description": "Under `no_reply_or_short`, a call this long or shorter\n(in seconds) counts as unanswered.\n"
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Create bulk campaign",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": true
        }
    },
    {
        "name": "createCustomApiIntegration",
        "description": "Create a custom API integration. Save a call to your own HTTP endpoint as an integration.\n\nAttach it to an agent with `agentIntegrationActions` with `action` `attach`. The agent calls the\nendpoint during a call when the conversation needs it, then uses the\nresponse in its reply. The agent fills parameters marked `isLLMGenerated`\nfrom the conversation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "A name for the integration."
                },
                "description": {
                    "type": "string",
                    "description": "What the endpoint does. The agent reads this to decide\nwhen to call it, so say what it returns and when it is useful.\n"
                },
                "url": {
                    "type": "string",
                    "format": "uri"
                },
                "method": {
                    "type": "string",
                    "enum": [
                        "GET",
                        "POST",
                        "PUT",
                        "PATCH",
                        "DELETE"
                    ]
                },
                "headers": {
                    "type": "array",
                    "description": "Fixed headers sent on every request.",
                    "items": {
                        "type": "object",
                        "required": [
                            "key",
                            "value"
                        ],
                        "properties": {
                            "key": {
                                "type": "string"
                            },
                            "value": {
                                "type": "string"
                            }
                        }
                    }
                },
                "query_params": {
                    "type": "array",
                    "description": "Query string parameters.",
                    "items": {
                        "type": "object",
                        "description": "One query or body parameter of a custom API. With `isLLMGenerated`\ntrue the agent fills the value from the conversation, guided by\n`description`. With it false, the text in `description` is sent as a\nfixed value.\n",
                        "required": [
                            "key"
                        ],
                        "properties": {
                            "key": {
                                "type": "string",
                                "description": "The parameter name your endpoint expects."
                            },
                            "description": {
                                "type": "string",
                                "description": "What the agent should put here, or the fixed value when `isLLMGenerated` is false."
                            },
                            "type": {
                                "type": "string",
                                "enum": [
                                    "string",
                                    "number",
                                    "boolean",
                                    "object",
                                    "array"
                                ],
                                "default": "string"
                            },
                            "required": {
                                "type": "boolean",
                                "description": "Whether the agent must supply this parameter."
                            },
                            "isLLMGenerated": {
                                "type": "boolean",
                                "default": true,
                                "description": "Let the agent fill this value from the conversation."
                            },
                            "children": {
                                "type": "array",
                                "description": "Nested fields of an `object` or `array` body parameter. Query parameters have no children.",
                                "items": {
                                    "type": "object"
                                }
                            }
                        }
                    }
                },
                "body_params": {
                    "type": "array",
                    "description": "Request body fields, sent as JSON. A GET request sends no\nbody. Every request with a body also carries the call's\n`from_number`, `to_number` and `call_sid`.\n",
                    "items": {
                        "type": "object",
                        "description": "One query or body parameter of a custom API. With `isLLMGenerated`\ntrue the agent fills the value from the conversation, guided by\n`description`. With it false, the text in `description` is sent as a\nfixed value.\n",
                        "required": [
                            "key"
                        ],
                        "properties": {
                            "key": {
                                "type": "string",
                                "description": "The parameter name your endpoint expects."
                            },
                            "description": {
                                "type": "string",
                                "description": "What the agent should put here, or the fixed value when `isLLMGenerated` is false."
                            },
                            "type": {
                                "type": "string",
                                "enum": [
                                    "string",
                                    "number",
                                    "boolean",
                                    "object",
                                    "array"
                                ],
                                "default": "string"
                            },
                            "required": {
                                "type": "boolean",
                                "description": "Whether the agent must supply this parameter."
                            },
                            "isLLMGenerated": {
                                "type": "boolean",
                                "default": true,
                                "description": "Let the agent fill this value from the conversation."
                            },
                            "children": {
                                "type": "array",
                                "description": "Nested fields of an `object` or `array` body parameter. Query parameters have no children.",
                                "items": {
                                    "type": "object"
                                }
                            }
                        }
                    }
                },
                "request_timeout": {
                    "type": "integer",
                    "default": 10,
                    "description": "Seconds to wait for your endpoint before the agent moves on."
                }
            },
            "required": [
                "method",
                "name",
                "url"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/integrations/custom-api",
        "path_params": [],
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Create custom API integration",
            "readOnlyHint": false,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "createSession",
        "description": "Create session. Create a short-lived voice session and get a `ws_url` for one conversation.\n\nThis is step 1 of 2. Creating the session starts no audio. The client then\nconnects to `ws_url` over WebSocket to talk.\n\nCall this endpoint from your server with your API key. Return only `ws_url`\nto your client, and never the API key. The `ws_url` is single-use and\nexpires, so it is safe to hand to your client. For how to connect and talk,\nsee \"Connect the client and talk\" below the request details.",
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
                            "example": "Hindi|Gujarati|English",
                            "type": [
                                "array",
                                "string"
                            ]
                        },
                        "__post_call_actions": {
                            "type": "object",
                            "additionalProperties": true,
                            "description": "Post-call actions for this session only, in the same shape\nas `post_call_actions` on agent create. Email and webhook\nonly. They replace the agent's own post-call actions for\nthis session. Items that cannot be used are skipped and\nlisted in `post_call_actions_ignored`.\nPost-call actions: email, webhook, Omni CRM, WhatsApp, workflow, Google Sheets, Slack, Salesforce, HubSpot or Zoho Bigin. On an agent, add them one at a time with addPostCallAction instead. Full shape: https://docs.omnidim.io/docs/per-call-post-call-actions"
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Create voice session",
            "readOnlyHint": false,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "createSupportCase",
        "description": "Create support case. File a support case for the signed-in customer. Only after the customer\nhas seen and confirmed the pre-filled form. The customer gets the usual\nacknowledgement email. Limited to a few cases per hour.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "maxLength": 200
                },
                "description": {
                    "type": "string",
                    "maxLength": 10000,
                    "description": "What happened, in the customer's words plus the findings in plain words."
                },
                "type": {
                    "type": "string",
                    "enum": [
                        "bug",
                        "feature_request"
                    ]
                },
                "priority": {
                    "type": "string",
                    "enum": [
                        "critical",
                        "high",
                        "medium"
                    ],
                    "default": "medium"
                },
                "call_log_ids": {
                    "type": "array",
                    "maxItems": 20,
                    "items": {
                        "type": "integer"
                    },
                    "description": "The customer's call logs this case is about."
                },
                "agent_ids": {
                    "type": "array",
                    "maxItems": 20,
                    "items": {
                        "type": "integer"
                    },
                    "description": "The customer's agents this case is about."
                }
            },
            "required": [
                "description",
                "title",
                "type"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/support/cases",
        "path_params": [],
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Create support case",
            "readOnlyHint": false,
            "destructiveHint": false,
            "openWorldHint": false
        },
        "operator_only": true
    },
    {
        "name": "createWhatsappCampaign",
        "description": "Create a campaign. Create a draft campaign from an approved template. It sends nothing until\nyou launch it.\n\nAdd contacts and launch it with the next calls. Scheduling is not offered.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "maxLength": 255
                },
                "phone_number_id": {
                    "type": "integer"
                },
                "template_id": {
                    "type": "integer",
                    "description": "An approved template on that number."
                },
                "campaign_mode": {
                    "type": "string",
                    "enum": [
                        "broadcast",
                        "broadcast_reply"
                    ],
                    "default": "broadcast",
                    "description": "`broadcast_reply` lets the agent answer replies. It needs an agent."
                },
                "agent_id": {
                    "type": "integer",
                    "description": "The agent that answers replies."
                },
                "data_source": {
                    "type": "string",
                    "enum": [
                        "csv",
                        "webhook"
                    ],
                    "default": "csv"
                },
                "is_dynamic": {
                    "type": "boolean",
                    "default": false
                },
                "variable_mapping": {
                    "type": "object",
                    "description": "Template field to contact field or static text.",
                    "additionalProperties": true
                }
            },
            "required": [
                "name",
                "phone_number_id",
                "template_id"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/whatsapp/campaigns",
        "path_params": [],
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Create WhatsApp campaign",
            "readOnlyHint": false,
            "destructiveHint": false,
            "openWorldHint": false
        }
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Delete agent",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": false
        }
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Delete cloned voice",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": false
        }
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Delete knowledge base file",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": false
        }
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Delete a post-call action",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": false
        }
    },
    {
        "name": "deleteWorkflow",
        "description": "Delete a workflow. Delete a workflow and stop its published version.\n\nThis cannot be undone, so confirm with the user first. To stop it without\ndeleting, use `workflowActions` with `action` `deactivate`.",
        "input_schema": {
            "type": "object",
            "properties": {
                "workflow_id": {
                    "type": "integer",
                    "description": "Id of the workflow."
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Delete workflow",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": false
        }
    },
    {
        "name": "diffAgentVersion",
        "description": "Diff an agent version. Get a record-level diff for one agent version.\n\nBy default it compares this version with the one before it. Use\n`against=current` to compare with the live config, which shows what\nrestoring this version would change. Use `against=<number>` to compare with\nanother version.",
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
        ],
        "header_params": [],
        "annotations": {
            "title": "Diff agent version",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "dispatchCall",
        "description": "Dispatch call. Start a call to a phone number with an agent.\n\nThe phone number must include a country code with a leading plus.",
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
                    ],
                    "type": [
                        "array",
                        "string"
                    ]
                },
                "__post_call_actions": {
                    "type": "object",
                    "additionalProperties": true,
                    "description": "Post-call actions for this call only, in the same shape as\n`post_call_actions` on agent create. Email and webhook only.\nThey replace the agent's own post-call actions for this call;\nthe agent is not changed. Items that cannot be used are\nskipped and listed in `post_call_actions_ignored`, and the\ncall still goes out. Can also be sent inside `call_context`.\nPost-call actions: email, webhook, Omni CRM, WhatsApp, workflow, Google Sheets, Slack, Salesforce, HubSpot or Zoho Bigin. On an agent, add them one at a time with addPostCallAction instead. Full shape: https://docs.omnidim.io/docs/per-call-post-call-actions"
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Dispatch call",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": true
        }
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
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/calls/bulk_call",
        "path_params": [],
        "query_params": [
            "pageno",
            "pagesize",
            "status"
        ],
        "header_params": [],
        "annotations": {
            "title": "List bulk campaigns",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "getAccountBalance",
        "description": "Get account balance. Read your organization's wallet balance, plan and auto-recharge state.\n\nThe response also has the minutes the balance buys at your rates and your\nconcurrency headroom.\n\nCall it before a campaign, or on a schedule, so you learn about low credit\nhere and not from a call failing with `402 payment_required`.\n\nThe response always describes the organization the API key belongs to. There\nis no parameter for another account. Resellers read a client's figures\nthrough the Reseller endpoints.\n\nA balance at or below zero does not always stop calls. An organization on\nusage-based billing (`plan.is_usage_based`) keeps placing calls and is\nmetered to its payment method. Check that flag before treating zero as a\nstop condition.\n\nThe API key's user needs Billing access in your organization. If you get a\n`403`, an administrator can grant it when Billing is enabled for your\norganization. When it is not, contact support.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/account/balance",
        "path_params": [],
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Get account balance",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "getAgent",
        "description": "Get agent. Get one agent by ID.\n\nThe response includes `can_publish`: whether [version\nhistory](/docs/api-reference/agents/listAgentVersions) is on for the agent's\norganization.\n\nThe response uses stored field names, such as `context_title` and\n`voice_external_id`. `updateAgent` takes the names in its own request\nbody instead, such as `context_breakdown[].title` and `voice.voice_id`.",
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Get agent",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Get bulk campaign",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Get campaign live status",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "getCallEvents",
        "description": "Get call events. What happened on one call, step by step: what the caller and the agent\nsaid, how long the agent took to reply, the tools it ran, transfers,\nvoicemail, language switches, interruptions, errors, and how the call\nended.\n\nUse it to find out why a call went the way it did: why it hung up, why\na transfer failed, or where the agent was slow.\n\nCalls older than 30 days have no timeline. For those,\n`timeline_available` is `false` and `turns` holds the transcript only.",
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
        "path": "/calls/logs/{call_log_id}/events",
        "path_params": [
            "call_log_id"
        ],
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Get call events",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        },
        "operator_only": true
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Get call log",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Get cloned voice",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "getPlanAndAddons",
        "description": "Get plan and add-ons. Read your organization's plan: its status and renewal or expiry date,\nyour concurrency add-ons, your concurrency limit, which plan features\nyou have, and the phone numbers that renew in the next 14 days with\nwhether your balance covers each renewal.\n\nYour balance and rates are on Get account balance.\n\nThe API key's user needs Billing access in your organization. If\nyou get a `403`, an administrator can grant it when Billing is\nenabled for your organization; when it is not, contact support.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/account/plan",
        "path_params": [],
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Get plan and add-ons",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        },
        "operator_only": true
    },
    {
        "name": "getSupportCase",
        "description": "Get support case. A support case of this customer, with its public thread. Internal notes are never included.",
        "input_schema": {
            "type": "object",
            "properties": {
                "case_number": {
                    "type": "string",
                    "description": "The case number, as returned when the case was created."
                }
            },
            "required": [
                "case_number"
            ],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/support/cases/{case_number}",
        "path_params": [
            "case_number"
        ],
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Get support case",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        },
        "operator_only": true
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Get voice",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "getWhatsappCalling",
        "description": "Get calling settings. Get whether calling is on for this number and whether it can be turned on.\n\nThe response lists the checks. A failing check does not fail the request: it\nstays `200` and names the check that blocks. Meta Cloud numbers only. Your\nplan must include calling.",
        "input_schema": {
            "type": "object",
            "properties": {
                "number_id": {
                    "type": "integer",
                    "description": "Id of a WhatsApp number in your workspace, from\n[listWhatsappNumbers](/docs/api-reference/whatsapp/listWhatsappNumbers).\nA number in another workspace answers `404`.\n"
                }
            },
            "required": [
                "number_id"
            ],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/whatsapp/numbers/{number_id}/calling",
        "path_params": [
            "number_id"
        ],
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Get WhatsApp calling setting",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "getWhatsappCampaign",
        "description": "Get a campaign. Get one campaign with its counts and analytics.\n\nAnalytics include per-source figures and failed contacts grouped by reason.\n`delivery_rate` and `read_rate` are null on a number that does not report\nreceipts.",
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {
                    "type": "integer",
                    "description": "Id of a WhatsApp campaign, from `listWhatsappCampaigns`."
                }
            },
            "required": [
                "campaign_id"
            ],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/whatsapp/campaigns/{campaign_id}",
        "path_params": [
            "campaign_id"
        ],
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Get WhatsApp campaign",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "getWhatsappConversation",
        "description": "Get a conversation. Get one conversation: owner, 24-hour window, opt-out state and unread count.\n\nPoll it while a person is answering.",
        "input_schema": {
            "type": "object",
            "properties": {
                "conversation_id": {
                    "type": "string",
                    "description": "A conversation id: the number id, a dash, then the customer's phone\ndigits, such as `412-919876543210`. From\n[listWhatsappConversations](/docs/api-reference/whatsapp/listWhatsappConversations).\n"
                }
            },
            "required": [
                "conversation_id"
            ],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/whatsapp/conversations/{conversation_id}",
        "path_params": [
            "conversation_id"
        ],
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Get WhatsApp conversation",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "getWhatsappMessage",
        "description": "Get a message. Get one message with its `timeline` of delivery and read steps, oldest\nfirst.\n\nPoll it after a send to learn whether the message was delivered and read. It\nalso shows what the send cost once charged.",
        "input_schema": {
            "type": "object",
            "properties": {
                "message_id": {
                    "type": "integer",
                    "description": "Id of a message, from `listWhatsappMessages` or a send response."
                }
            },
            "required": [
                "message_id"
            ],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/whatsapp/messages/{message_id}",
        "path_params": [
            "message_id"
        ],
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Get WhatsApp message",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "getWhatsappNumber",
        "description": "Get a WhatsApp number. Get one number with its status, quality, messaging limit and what it can\nsend.\n\nA number in another workspace answers `404`.",
        "input_schema": {
            "type": "object",
            "properties": {
                "number_id": {
                    "type": "integer",
                    "description": "Id of a WhatsApp number in your workspace, from\n[listWhatsappNumbers](/docs/api-reference/whatsapp/listWhatsappNumbers).\nA number in another workspace answers `404`.\n"
                }
            },
            "required": [
                "number_id"
            ],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/whatsapp/numbers/{number_id}",
        "path_params": [
            "number_id"
        ],
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Get WhatsApp number",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Import Exotel number",
            "readOnlyHint": false,
            "destructiveHint": false,
            "openWorldHint": false
        }
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Import SIP trunk",
            "readOnlyHint": false,
            "destructiveHint": false,
            "openWorldHint": false
        }
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Import Twilio number",
            "readOnlyHint": false,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "importWhatsappNumbers",
        "description": "Connect WhatsApp numbers. Connect numbers from your WhatsApp Business Account with your Meta access\ntoken.\n\nList the numbers first with [Preview\nnumbers](/docs/api-reference/whatsapp/previewWhatsappNumbers), then pass the\nids you want.\n\nThe token must never expire and must carry both\n`whatsapp_business_management` and `whatsapp_business_messaging`. A system\nuser token does. Add `app_secret` to receive replies. Without it the number\ncan send but not receive.\n\nConnecting a number again updates it. Send a new `access_token` or\n`app_secret` to change either. One number failing does not stop the others.\nIt is listed in `failed` with the reason.",
        "input_schema": {
            "type": "object",
            "properties": {
                "waba_id": {
                    "type": "string",
                    "description": "Your WhatsApp Business Account id, from WhatsApp Manager."
                },
                "access_token": {
                    "type": "string",
                    "description": "A Meta access token that never expires, with both WhatsApp permissions. Stored, never returned."
                },
                "phone_number_ids": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "string"
                    },
                    "description": "Meta's ids for the numbers to connect, as Preview numbers lists them."
                },
                "app_secret": {
                    "type": "string",
                    "description": "Your Meta app's secret. Turns on replies. Stored, never returned."
                }
            },
            "required": [
                "access_token",
                "phone_number_ids",
                "waba_id"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/whatsapp/numbers",
        "path_params": [],
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Import WhatsApp numbers",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": true
        }
    },
    {
        "name": "liftWhatsappOptOut",
        "description": "Lift a block. Lift a block you added, or a marketing block made in WhatsApp.\n\nThe entry stays in the list with `active: false`. You cannot lift a\ncustomer's own STOP over the API. The customer must lift it in WhatsApp or\nmessage you again.",
        "input_schema": {
            "type": "object",
            "properties": {
                "number_id": {
                    "type": "integer",
                    "description": "Id of a WhatsApp number in your workspace, from\n[listWhatsappNumbers](/docs/api-reference/whatsapp/listWhatsappNumbers).\nA number in another workspace answers `404`.\n"
                },
                "opt_out_id": {
                    "type": "integer",
                    "description": "Id of an active opt-out entry, from `listWhatsappOptOuts`."
                }
            },
            "required": [
                "number_id",
                "opt_out_id"
            ],
            "additionalProperties": true
        },
        "method": "DELETE",
        "path": "/whatsapp/numbers/{number_id}/opt_outs/{opt_out_id}",
        "path_params": [
            "number_id",
            "opt_out_id"
        ],
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Lift WhatsApp opt-out",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": false
        }
    },
    {
        "name": "listAgentIntegrations",
        "description": "List an agent's integrations. List the integrations attached to the agent. Stored credentials read `********`.",
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
        "path": "/agents/{agent_id}/integrations",
        "path_params": [
            "agent_id"
        ],
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "List agent integrations",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "listAgentVersions",
        "description": "List agent versions. List an agent's saved versions, newest first. Includes manual (named) versions and system backups taken before a restore. Nothing is saved automatically.",
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
        ],
        "header_params": [],
        "annotations": {
            "title": "List agent versions",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
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
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/agents",
        "path_params": [],
        "query_params": [
            "pageno",
            "pagesize",
            "name"
        ],
        "header_params": [],
        "annotations": {
            "title": "List agents",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "listBulkCallLines",
        "description": "Bulk call results. List per-contact results for a campaign.\n\nEach row has what happened on the call, the variables you sent, and\n`call.recording_id`.\n\n## Paging\n\nCall with no `cursor`. Then pass back the `next_cursor` you were given until\nit is `null`. Rows come oldest first. `pagesize` defaults to 30 and goes up\nto 150. Cursors are opaque, so never build one. No contact is skipped or\nreturned twice, even while the campaign dials.\n\n```\ncursor = None\nwhile True:\n    page = GET /lines?pagesize=150&cursor={cursor}\n    handle(page[\"records\"])\n    cursor = page[\"next_cursor\"]\n    if not cursor: break\n```\n\n## Transcripts are not in the row\n\nTranscripts reach 212 KB, so rows carry only `call.recording_id`. Fetch the\ntranscript from `GET /calls/logs/{recording_id}`.",
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
        ],
        "header_params": [],
        "annotations": {
            "title": "List campaign call results",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "List campaign rotation pool",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
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
                    "description": "Filter by bulk-call campaign ID. Takes one ID."
                },
                "include_details": {
                    "type": "boolean",
                    "default": true,
                    "description": "Set to `false` for a lighter list. Each row then leaves out\n`call_conversation`, `sentiment_analysis_details`, `llm_prompt`,\n`voice_insides`, `custom_variables` and `metadata`. Fetch those for\none call with Get call log.\n"
                },
                "date_from": {
                    "type": "string",
                    "format": "date",
                    "description": "Only calls on or after this day (YYYY-MM-DD, inclusive), in the time zone set on your account. UTC when none is set."
                },
                "date_to": {
                    "type": "string",
                    "format": "date",
                    "description": "Only calls on or before this day (YYYY-MM-DD, inclusive), in the time zone set on your account. Must not be earlier than `date_from`."
                }
            },
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
            "bulk_call_id",
            "include_details",
            "date_from",
            "date_to"
        ],
        "header_params": [],
        "annotations": {
            "title": "List call logs",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "listClonedVoices",
        "description": "List cloned voices. List your cloned voices, oldest first, one cursor page at a time.\n\nCall it with no `cursor`. Then pass back each `next_cursor` until it is\n`null`.\n\nWhen a voice is `ready`, put its `voice_id` in an agent's `voice.voice_id`\nwith `voice.provider: cartesia`.",
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
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/voices",
        "path_params": [],
        "query_params": [
            "limit",
            "cursor"
        ],
        "header_params": [],
        "annotations": {
            "title": "List cloned voices",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "listIntegrations",
        "description": "List integrations. List your workspace integrations, with each one's `id` and\n`integration_type`.\n\nStored credentials (tokens, secrets, passwords, API keys, and the values of\na custom API's headers and parameters) are never returned. They read\n`********`. When you create an integration, send the real values: `********`\nis refused. Accounts that sign in with OAuth (Google Sheets, Slack, HubSpot,\nSalesforce, Zoho Bigin) are connected in the dashboard.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/integrations",
        "path_params": [],
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "List integrations",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "listKnowledgeBaseFiles",
        "description": "List knowledge base files. List all knowledge-base files for the authenticated user.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/knowledge_base/list",
        "path_params": [],
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "List knowledge base files",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
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
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/phone_number/list",
        "path_params": [],
        "query_params": [
            "pageno",
            "pagesize"
        ],
        "header_params": [],
        "annotations": {
            "title": "List phone numbers",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "List post-call actions",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "listProviders",
        "description": "List the LLM, speech-to-text or text-to-speech providers your organization can use, or all of them with their voices.\n\nSet `type` to pick what to do.\n\n`llm`: List LLM providers. Retrieve all available Large Language Model providers.\n\n`stt`: List STT providers. Retrieve all Speech-to-Text providers.\n\n`tts`: List TTS providers. Retrieve all Text-to-Speech providers.\n\n`all`: List all providers. Comprehensive response with services and voices in one payload.",
        "input_schema": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": [
                        "llm",
                        "stt",
                        "tts",
                        "all"
                    ],
                    "description": "What to do: llm, stt, tts, all."
                }
            },
            "required": [
                "type"
            ],
            "additionalProperties": true
        },
        "annotations": {
            "title": "List providers",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        },
        "field": "type",
        "actions": {
            "llm": {
                "operation": "listLLMProviders",
                "method": "GET",
                "path": "/providers/llms",
                "path_params": [],
                "query_params": [],
                "header_params": [],
                "inputs": [],
                "required": [],
                "sends_field": false
            },
            "stt": {
                "operation": "listSTTProviders",
                "method": "GET",
                "path": "/providers/stt",
                "path_params": [],
                "query_params": [],
                "header_params": [],
                "inputs": [],
                "required": [],
                "sends_field": false
            },
            "tts": {
                "operation": "listTTSProviders",
                "method": "GET",
                "path": "/providers/tts",
                "path_params": [],
                "query_params": [],
                "header_params": [],
                "inputs": [],
                "required": [],
                "sends_field": false
            },
            "all": {
                "operation": "listAllProviders",
                "method": "GET",
                "path": "/providers/all",
                "path_params": [],
                "query_params": [],
                "header_params": [],
                "inputs": [],
                "required": [],
                "sends_field": false
            }
        }
    },
    {
        "name": "listVoices",
        "description": "List voices. List the voices your organization can use, with filters and pagination.\n\nUse `provider=featured` for OmniDimension voices in the order the dashboard\nshows them. They are the recommended start. Cartesia voices are next.\n\nEach voice keeps its own `service`: save it as the agent's voice provider. A\nprovider your organization cannot use returns a 400. Cartesia and ElevenLabs\nsupport filtering by name, language, accent and gender. Other providers\nsupport pagination only.",
        "input_schema": {
            "type": "object",
            "properties": {
                "provider": {
                    "type": "string",
                    "example": "featured",
                    "description": "Provider to list voices from. Omit to list every voice your organization can use.\n`featured` lists OmniDimension voices and is the recommended choice, followed by\n`cartesia`. A provider your organization cannot use returns a 400.\n"
                },
                "search": {
                    "type": "string",
                    "description": "Substring match against voice name or description. Cartesia and ElevenLabs."
                },
                "language": {
                    "type": "string",
                    "description": "ISO language code (e.g. `en`, `hi`, `es`). Cartesia and ElevenLabs."
                },
                "accent": {
                    "type": "string",
                    "description": "Accent label (e.g. `american`, `british`). Cartesia and ElevenLabs."
                },
                "gender": {
                    "type": "string",
                    "enum": [
                        "male",
                        "female"
                    ],
                    "description": "Filter voices by gender. Cartesia and ElevenLabs."
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
        ],
        "header_params": [],
        "annotations": {
            "title": "List voices",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "listWhatsappCampaignContacts",
        "description": "List campaign contacts. List per-contact status for a campaign, oldest first.\n\nA contact that read the message and then replied STOP counts as read and\nopted out.",
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {
                    "type": "integer",
                    "description": "Id of a WhatsApp campaign, from `listWhatsappCampaigns`."
                },
                "status": {
                    "type": "string",
                    "enum": [
                        "pending",
                        "sent",
                        "delivered",
                        "read",
                        "replied",
                        "failed",
                        "skipped",
                        "opted_out"
                    ],
                    "description": "Show only contacts in this state."
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
                    "description": "The `next_cursor` from the previous page."
                }
            },
            "required": [
                "campaign_id"
            ],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/whatsapp/campaigns/{campaign_id}/contacts",
        "path_params": [
            "campaign_id"
        ],
        "query_params": [
            "status",
            "limit",
            "cursor"
        ],
        "header_params": [],
        "annotations": {
            "title": "List WhatsApp campaign contacts",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "listWhatsappCampaigns",
        "description": "List campaigns. Your WhatsApp campaigns, oldest first. Filter by status or by number.",
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": [
                        "draft",
                        "scheduled",
                        "in_progress",
                        "paused",
                        "completed",
                        "failed",
                        "cancelled"
                    ],
                    "description": "Show only campaigns in this state."
                },
                "phone_number_id": {
                    "type": "integer",
                    "description": "Show only campaigns on this number."
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
                    "description": "The `next_cursor` from the previous page."
                }
            },
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/whatsapp/campaigns",
        "path_params": [],
        "query_params": [
            "status",
            "phone_number_id",
            "limit",
            "cursor"
        ],
        "header_params": [],
        "annotations": {
            "title": "List WhatsApp campaigns",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "listWhatsappConversations",
        "description": "List conversations. List a number's inbox, newest activity first.\n\nThere are no event webhooks, so poll with `updated_since` to learn about new\nmessages. Page with `cursor`.",
        "input_schema": {
            "type": "object",
            "properties": {
                "number_id": {
                    "type": "integer",
                    "description": "Id of a WhatsApp number in your workspace, from\n[listWhatsappNumbers](/docs/api-reference/whatsapp/listWhatsappNumbers).\nA number in another workspace answers `404`.\n"
                },
                "filter": {
                    "type": "string",
                    "enum": [
                        "all",
                        "unread",
                        "needs_person",
                        "agent",
                        "failed",
                        "window_closed",
                        "campaign_replies"
                    ],
                    "default": "all",
                    "description": "`needs_person` is a person-owned or paused conversation. `window_closed` is one you can only reach with a template."
                },
                "q": {
                    "type": "string",
                    "maxLength": 200,
                    "description": "Search the customer's name, phone number and message text."
                },
                "updated_since": {
                    "type": "string",
                    "description": "An ISO 8601 date and time, such as `2026-10-01T09:00:00+00:00`. Returns\nconversations with a change at or after it. No offset means UTC.\n"
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
                    "description": "The `next_cursor` from the previous page."
                }
            },
            "required": [
                "number_id"
            ],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/whatsapp/numbers/{number_id}/conversations",
        "path_params": [
            "number_id"
        ],
        "query_params": [
            "filter",
            "q",
            "updated_since",
            "limit",
            "cursor"
        ],
        "header_params": [],
        "annotations": {
            "title": "List WhatsApp conversations",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "listWhatsappMessages",
        "description": "List messages. List one conversation's messages, newest first.\n\nPoll forward with `after`, the id of the newest message you have, to get\nonly new ones. Page back through history with `cursor`. Do not pass both.",
        "input_schema": {
            "type": "object",
            "properties": {
                "conversation_id": {
                    "type": "string",
                    "description": "The conversation to read."
                },
                "after": {
                    "type": "integer",
                    "description": "Return messages newer than this message id. `next_cursor` is null in this mode."
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
                    "description": "The `next_cursor` from the previous page. Do not combine it with `after`."
                }
            },
            "required": [
                "conversation_id"
            ],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/whatsapp/messages",
        "path_params": [],
        "query_params": [
            "conversation_id",
            "after",
            "limit",
            "cursor"
        ],
        "header_params": [],
        "annotations": {
            "title": "List WhatsApp messages",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "listWhatsappNumbers",
        "description": "List WhatsApp numbers. List the WhatsApp numbers your API key can see.\n\nNumbers come oldest first, and archived ones are left out. Use it to find a\nnumber id for the other routes. Each number carries `capabilities`, which\nsays what it can send.",
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "default": 20,
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Rows per page."
                },
                "cursor": {
                    "type": "string",
                    "description": "The `next_cursor` from the previous page. Omit it on the first request and pass it back unchanged."
                }
            },
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/whatsapp/numbers",
        "path_params": [],
        "query_params": [
            "limit",
            "cursor"
        ],
        "header_params": [],
        "annotations": {
            "title": "List WhatsApp numbers",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "listWhatsappOptOuts",
        "description": "List opt-outs. Who opted out of messages from this number, oldest first. By default it\nlists active opt-outs only.",
        "input_schema": {
            "type": "object",
            "properties": {
                "number_id": {
                    "type": "integer",
                    "description": "Id of a WhatsApp number in your workspace, from\n[listWhatsappNumbers](/docs/api-reference/whatsapp/listWhatsappNumbers).\nA number in another workspace answers `404`.\n"
                },
                "active": {
                    "type": "string",
                    "enum": [
                        true,
                        false,
                        "all"
                    ],
                    "default": "true",
                    "description": "`true` for active only, `false` for lifted only, `all` for both."
                },
                "customer": {
                    "type": "string",
                    "description": "Find one customer by any spelling of their number."
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
                    "description": "The `next_cursor` from the previous page."
                }
            },
            "required": [
                "number_id"
            ],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/whatsapp/numbers/{number_id}/opt_outs",
        "path_params": [
            "number_id"
        ],
        "query_params": [
            "active",
            "customer",
            "limit",
            "cursor"
        ],
        "header_params": [],
        "annotations": {
            "title": "List WhatsApp opt-outs",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "listWhatsappTemplates",
        "description": "List templates. List the number's message templates, as last synced, oldest first.\n\nPass `status=approved` to see exactly the templates a send accepts. If a\ntemplate you expect is missing, run `syncWhatsappTemplates` first.",
        "input_schema": {
            "type": "object",
            "properties": {
                "number_id": {
                    "type": "integer",
                    "description": "Id of a WhatsApp number in your workspace, from\n[listWhatsappNumbers](/docs/api-reference/whatsapp/listWhatsappNumbers).\nA number in another workspace answers `404`.\n"
                },
                "status": {
                    "type": "string",
                    "description": "Show only templates with this review status, such as `approved`,\n`pending` or `rejected`. Lower-case; omit it for all.\n"
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
                    "description": "The `next_cursor` from the previous page."
                }
            },
            "required": [
                "number_id"
            ],
            "additionalProperties": true
        },
        "method": "GET",
        "path": "/whatsapp/numbers/{number_id}/templates",
        "path_params": [
            "number_id"
        ],
        "query_params": [
            "status",
            "limit",
            "cursor"
        ],
        "header_params": [],
        "annotations": {
            "title": "List WhatsApp templates",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "phoneNumberAgentActions",
        "description": "Attach a phone number to an agent, or detach it from its agent.\n\nSet `action` to pick what to do.\n\n`attach`: Attach phone number to agent. Attach a phone number to an existing agent.\n\nWithout `user_id`, use any number and agent your key can manage. With\n`user_id`, both must belong to that client.\n\n`detach`: Detach phone number. Detach a phone number from its agent.\n\nWithout `user_id`, use any number your key can manage. With `user_id`, the\nnumber must belong to that client.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "attach",
                        "detach"
                    ],
                    "description": "What to do: attach, detach."
                },
                "phone_number_id": {
                    "type": "integer",
                    "description": "ID of the phone number to attach.",
                    "example": 23
                },
                "agent_id": {
                    "type": "integer",
                    "description": "Only for `attach`. ID of the agent to attach the phone number to.",
                    "example": 158910
                }
            },
            "required": [
                "action",
                "phone_number_id"
            ],
            "additionalProperties": true
        },
        "annotations": {
            "title": "Attach or detach phone number",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": false
        },
        "field": "action",
        "actions": {
            "attach": {
                "operation": "attachPhoneNumber",
                "method": "POST",
                "path": "/phone_number/attach",
                "path_params": [],
                "query_params": [],
                "header_params": [],
                "inputs": [
                    "phone_number_id",
                    "agent_id"
                ],
                "required": [
                    "agent_id",
                    "phone_number_id"
                ],
                "sends_field": false
            },
            "detach": {
                "operation": "detachPhoneNumber",
                "method": "POST",
                "path": "/phone_number/detach",
                "path_params": [],
                "query_params": [],
                "header_params": [],
                "inputs": [
                    "phone_number_id"
                ],
                "required": [
                    "phone_number_id"
                ],
                "sends_field": false
            }
        }
    },
    {
        "name": "previewWhatsappNumbers",
        "description": "Preview numbers to connect. List the numbers on your WhatsApp Business Account with their health.\nConnects nothing.\n\nThe access token is checked first, against the same rules as connecting, so\na preview that passes can connect.\n\nFix a number with `needs_migration` or `needs_registration` in WhatsApp\nManager before you connect it, or its sends fail.",
        "input_schema": {
            "type": "object",
            "properties": {
                "waba_id": {
                    "type": "string",
                    "description": "Your WhatsApp Business Account id, from WhatsApp Manager."
                },
                "access_token": {
                    "type": "string",
                    "description": "A Meta access token that never expires, with both WhatsApp permissions."
                }
            },
            "required": [
                "access_token",
                "waba_id"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/whatsapp/numbers/preview",
        "path_params": [],
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Preview WhatsApp numbers to import",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "purchasePhoneNumber",
        "description": "Purchase a phone number. Buy a phone number from the OmniDimension number shop.\n\nThe monthly rental comes out of your wallet. The number is added to your\naccount, ready to attach to an agent.",
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
        "query_params": [],
        "header_params": [
            "Idempotency-Key"
        ],
        "annotations": {
            "title": "Buy phone number",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": true
        }
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Regenerate cloned voice sample",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": false
        }
    },
    {
        "name": "releasePhoneNumber",
        "description": "Release a phone number. Release a phone number and stop its rental.\n\nIt is not charged at the next renewal. Only a number currently allocated to\nthe account can be released.",
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Release phone number",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": true
        }
    },
    {
        "name": "retryBulkCall",
        "description": "Retry contacts that did not connect. Re-queue contacts that did not connect, without a new campaign.\n\nUse it after a campaign finishes with more no-answers than expected, or when\nthe cause was on your side. Retried contacts keep their original variables.\n\nThe retry is refused in these cases:\n\n- The status is not `completed`. The error is `Cannot retry calls. Current status: <status>`.\n- Auto retry is on and some contacts are still `Pending` or `In Progress`. The error is `Cannot retry while calls are still in progress and auto retry is enabled`.\n- A value in `failure_reasons` is not an allowed status. The error is `Invalid failure reason(s)` and lists the allowed values.\n- No contact matches. The error is `No failed calls found to retry matching criteria`.\n\nEach contact is retried from its latest call only. With\n`skip_known_invalid_numbers` on, contacts whose last call ended with the\ncarrier saying the number does not exist are skipped. Connected calls with\nno conversation are not retried.",
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
                    "description": "Which contacts to re-queue. `all` takes everything that did\nnot connect. `specific` re-queues only the statuses listed\nin `failure_reasons`.\n"
                },
                "failure_reasons": {
                    "type": "array",
                    "description": "Statuses to re-queue. Read only when `retry_strategy` is\n`specific`; for example `no-answer` and `busy`. Ignored when\n`retry_strategy` is `all`.\n",
                    "items": {
                        "type": "string",
                        "enum": [
                            "failed",
                            "Failed",
                            "no-answer",
                            "No Answer",
                            "busy",
                            "Busy",
                            "cancelled",
                            "canceled",
                            "voicemail_detected"
                        ]
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Retry unconnected contacts",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": true
        }
    },
    {
        "name": "searchPhoneNumbers",
        "description": "Search available phone numbers. Search the OmniDimension number shop for numbers you can buy in a region.\n\nPrice and validity are flat per region. Every result shows the same\n`monthly_rental_usd` and `validity_days`, and a purchase charges exactly\nthat.\n\nA region can have several carriers, each with different number series. Pass\nthe `carrier` you want. The response names the carrier its results came\nfrom, and a purchase must pass that carrier.",
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
        ],
        "header_params": [],
        "annotations": {
            "title": "Search available phone numbers",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "sendWhatsappMessage",
        "description": "Send a message. Send a text, template, image or document message to a customer.\n\nIt goes out from `phone_number_id`. Set `type` and the field that matches\nit.\n\nOutside the 24-hour window, only a template goes through. Text, image and\ndocument sends are refused with `409 window_closed`. A template send works\nany time and can start a new conversation.\n\nA send does not take the conversation over, so the agent keeps answering.\nSet `take_over: true` to stop the agent and answer yourself.\n\n`Idempotency-Key` is required. The same key with the same body replays the first answer instead of sending again.",
        "input_schema": {
            "type": "object",
            "properties": {
                "Idempotency-Key": {
                    "type": "string",
                    "maxLength": 255,
                    "description": "A unique string you choose, up to 255 characters. Required on this\nroute. The same key with the same body replays the first answer for\n24 hours instead of acting twice. A different body with the same key\nanswers `409`.\n"
                },
                "phone_number_id": {
                    "type": "integer",
                    "description": "The number to send from."
                },
                "to": {
                    "type": "string",
                    "description": "The customer's number in international format, such as `+15551234567`."
                },
                "type": {
                    "type": "string",
                    "enum": [
                        "text",
                        "template",
                        "image",
                        "document"
                    ]
                },
                "text": {
                    "type": "string",
                    "maxLength": 4096,
                    "description": "Required when `type` is `text`."
                },
                "template": {
                    "type": "object",
                    "description": "Required when `type` is `template`.",
                    "required": [
                        "id"
                    ],
                    "properties": {
                        "id": {
                            "type": "integer",
                            "description": "An approved template on this number, from `listWhatsappTemplates`."
                        },
                        "params": {
                            "type": "object",
                            "description": "One value per field in the template's `fields`. Keys are\nthose field keys. String, number or null values.\n",
                            "additionalProperties": true
                        }
                    }
                },
                "media": {
                    "type": "object",
                    "description": "Required when `type` is `image` or `document`.",
                    "required": [
                        "media_id"
                    ],
                    "properties": {
                        "media_id": {
                            "type": "string",
                            "description": "The `media_id` from `uploadWhatsappMedia`, uploaded within the last 24 hours."
                        },
                        "caption": {
                            "type": "string",
                            "maxLength": 1024
                        }
                    }
                },
                "reply_to": {
                    "type": "integer",
                    "description": "A message id in the same conversation to quote. Not allowed with a template."
                },
                "take_over": {
                    "type": "boolean",
                    "default": false,
                    "description": "Stop the agent answering this conversation and let a person run it."
                }
            },
            "required": [
                "Idempotency-Key",
                "phone_number_id",
                "to",
                "type"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/whatsapp/messages",
        "path_params": [],
        "query_params": [],
        "header_params": [
            "Idempotency-Key"
        ],
        "annotations": {
            "title": "Send WhatsApp message",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": true
        }
    },
    {
        "name": "setBulkCallConcurrency",
        "description": "Change concurrency. Change how many calls the campaign places at once, even while it runs.\n\nRaise it to finish sooner. Lower it if your team cannot keep up with\ntransfers or fewer calls are answered. The ceiling is your account's\nconcurrency limit.",
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Set campaign concurrency",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": false
        }
    },
    {
        "name": "setBulkCallDailyTimeControl",
        "description": "Set calling hours. Limit a campaign to a daily calling window in its timezone.\n\nOutside the window the campaign holds, then resumes the next day.",
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Set campaign calling hours",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": false
        }
    },
    {
        "name": "setBulkCallNumberActive",
        "description": "Pause or resume a pool number. Stop or resume dialing from one number in the pool.\n\nPause a number that goes bad mid-campaign. Dialing moves to the next number,\nand the paused number keeps its history and counters. You cannot pause the\nlast active number of a running campaign.\n\nSend the state you want, not a toggle, so a retry is harmless.\n\n`assignment_id` is the number's id **within this campaign's pool**, from List rotation pool. It is not the `phone_number_id`.",
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Pause or resume pool number",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": false
        }
    },
    {
        "name": "setBulkCallRotation",
        "description": "Change rotation settings. Change how a campaign uses its number pool.\n\nSend only the fields you want to change. At least one field is required.\n\nIt works while the status is `draft`, `scheduled`, `in_progress`, `waiting`,\n`paused`, `auto_paused` or `retry_scheduled`. Any other status is refused\nwith `Cannot edit rotation for status: <status>`. To change which numbers\nare in the pool, use the numbers endpoints.",
        "input_schema": {
            "type": "object",
            "properties": {
                "bulk_call_id": {
                    "type": "integer",
                    "description": "Id of the bulk call campaign."
                },
                "strategy": {
                    "type": "string",
                    "enum": [
                        "fixed_count",
                        "cpr_threshold",
                        "both",
                        "none"
                    ],
                    "description": "When to move to the next number: every `calls_per_number`\ncalls, on low health score, both, or never.\n"
                },
                "calls_per_number": {
                    "type": "integer",
                    "description": "Calls before moving on. Used by `fixed_count` and `both`."
                },
                "health_threshold": {
                    "type": "number",
                    "description": "Health score below which a number is rotated away from.\nUsed by `cpr_threshold` and `both`.\n"
                },
                "fallback": {
                    "type": "string",
                    "enum": [
                        "pause",
                        "continue_best"
                    ],
                    "description": "When every number is unhealthy: `pause` the campaign, or\n`continue_best` with the healthiest one.\n"
                },
                "call_back_from_different_number": {
                    "type": "boolean",
                    "description": "When on, a repeat call to the same person goes out from a\ndifferent number than the one that called them last. Needs\ntwo or more numbers in the pool. Must be `true` or `false`.\n"
                },
                "skip_known_invalid_numbers": {
                    "type": "boolean",
                    "description": "When on, a contact is not dialed if the carrier said its\nnumber does not exist, in any campaign of your organization\nin the last 14 days. Must be `true` or `false`.\n"
                }
            },
            "required": [
                "bulk_call_id"
            ],
            "additionalProperties": true
        },
        "method": "PUT",
        "path": "/calls/bulk_call/{bulk_call_id}/rotation",
        "path_params": [
            "bulk_call_id"
        ],
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Set campaign number rotation",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": false
        }
    },
    {
        "name": "setPhoneNumberAutoRenew",
        "description": "Switch auto-renew on a phone number. Turn auto-renew on or off for a number bought from the number shop.\n\nWith auto-renew off, the number is not charged again. It works until the end\nof the period already paid for, then it is released. Turn auto-renew on\nbefore that date and the number renews as normal. Sending the value the\nnumber already has changes nothing and still succeeds.",
        "input_schema": {
            "type": "object",
            "properties": {
                "phone_number": {
                    "type": "string",
                    "description": "The number to switch.",
                    "example": "+15551234567"
                },
                "auto_renew": {
                    "type": "boolean",
                    "description": "`false` stops renewal, `true` turns it back on. Must be a JSON boolean: a string such as `\"false\"`, a number, or a missing value is refused.",
                    "example": false
                }
            },
            "required": [
                "auto_renew",
                "phone_number"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/phone_number/auto_renew",
        "path_params": [],
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Set phone number auto-renew",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": false
        }
    },
    {
        "name": "setWhatsappCalling",
        "description": "Turn calling on or off. Turn calling on or off for a Meta Cloud number.\n\nA customer calls this number. It does not place calls. Turning calling on\nneeds every blocking check to pass, or the request answers `409`. Turning it\noff is always allowed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "number_id": {
                    "type": "integer",
                    "description": "Id of a WhatsApp number in your workspace, from\n[listWhatsappNumbers](/docs/api-reference/whatsapp/listWhatsappNumbers).\nA number in another workspace answers `404`.\n"
                },
                "enabled": {
                    "type": "boolean",
                    "description": "`true` to turn calling on, `false` to turn it off."
                }
            },
            "required": [
                "enabled",
                "number_id"
            ],
            "additionalProperties": true
        },
        "method": "PATCH",
        "path": "/whatsapp/numbers/{number_id}/calling",
        "path_params": [
            "number_id"
        ],
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Turn WhatsApp calling on or off",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": true
        }
    },
    {
        "name": "syncWhatsappTemplates",
        "description": "Sync templates. Pull the number's templates and review statuses from WhatsApp into your\nlist.\n\nRun it after you create or edit a template in Meta. It runs at most once a\nminute per number. A second call inside that minute answers `429`.",
        "input_schema": {
            "type": "object",
            "properties": {
                "number_id": {
                    "type": "integer",
                    "description": "Id of a WhatsApp number in your workspace, from\n[listWhatsappNumbers](/docs/api-reference/whatsapp/listWhatsappNumbers).\nA number in another workspace answers `404`.\n"
                }
            },
            "required": [
                "number_id"
            ],
            "additionalProperties": true
        },
        "method": "POST",
        "path": "/whatsapp/numbers/{number_id}/templates/sync",
        "path_params": [
            "number_id"
        ],
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Sync WhatsApp templates",
            "readOnlyHint": false,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "updateAgent",
        "description": "Update agent. Update an agent. Send only the fields you want to change.\n\n`post_call_actions` replaces the agent's email, webhook, Omni CRM, Cloud WhatsApp and workflow actions as one set, but only if you send at least one of those types. Google Sheets, Slack, Salesforce, HubSpot and Zoho Bigin actions are replaced only when you send their key. Other actions are kept. If a sent action gives a variable key a new prompt, kept actions with the same key take that prompt too. To change one action alone, use `/agents/{agent_id}/post-call-actions`.\n\n> **Voicemail detection is access-gated** and turned on per account. If it is off for yours, [request access](https://omnidim.io/contact-us?reason=product&lock=1) before you configure the `voicemail` object.",
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
                    "description": "The agent's prompt sections, each with `title`, `body` and optional `is_enabled`. Sending them replaces the whole list and rebuilds the prompt from the enabled sections in order: each `title` becomes a `# title` heading on its own line, with its `body` below it, the same layout the dashboard uses. A save without `context_breakdown` leaves the prompt unchanged.",
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
                    "description": "`Incoming` for an agent that answers calls, `Outgoing` for one that places them, spelled exactly so. Any other value, `incoming` included, saves as `Outgoing` and the response lists it in `warnings`."
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
                            "description": "The speech-to-text provider to use: a `name` from the STT providers list, which returns the ones your organization can use. Leave it out to use your organization's default transcriber.",
                            "example": "deepgram_stream"
                        },
                        "model": {
                            "type": "string",
                            "description": "Transcription model for the selected provider. For\n`deepgram_stream` this is `nova-3` or `nova-2`. Saved only\nfor `deepgram_stream`, `cartesia` and `sarvam`, and only\nwhen `provider` is in the same request.\n",
                            "example": "nova-3"
                        },
                        "language": {
                            "type": [
                                "string",
                                "array"
                            ],
                            "items": {
                                "type": "string"
                            },
                            "description": "Language code for the transcriber. Format and supported\nvalues depend on the provider (e.g. `en-US` for Deepgram,\n`hi-IN` for Sarvam). `soniox` takes a list of codes, such as\n`[\"en\", \"hi\"]`, and an empty list detects the language. Saved only when `provider` is in the\nsame request and is `deepgram_stream`, `cartesia`, `sarvam`,\n`azure` or `soniox`.\n",
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
                            "description": "The language model to use: a `name` from the LLM providers list, which returns exactly the models your organization can use. Leave it out to use your organization's default model.",
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
                    "description": "Configuration for the text-to-speech voice. `provider` and `voice_id` identify the voice together, so send both to change it. `provider` on its own is not accepted, and a `voice_id` on its own leaves the voice as it was. The other fields here apply independently. Leave out `provider` and `voice_id` to use your organization's default voice.",
                    "dependentRequired": {
                        "provider": [
                            "voice_id"
                        ]
                    },
                    "properties": {
                        "provider": {
                            "type": "string",
                            "description": "The voice provider to use: the `service` of a voice from the voices list, which returns only voices your organization can use. Send `voice_id` alongside it. We recommend OmniDimension voices (list them with `provider=featured`) and Cartesia voices. An agent created without `voice` gets the platform default, a Cartesia voice, which every account can use.",
                            "example": "cartesia"
                        },
                        "voice_id": {
                            "type": "string",
                            "description": "The provider's voice identifier, returned in the `name` field of the voices list (not the numeric `id`). Takes effect when `provider` is sent alongside it.",
                            "example": "faf0731e-dfb9-4cfc-8119-259a79b27e12"
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
                    "additionalProperties": true,
                    "description": "Post-call actions: email, webhook, Omni CRM, WhatsApp, workflow, Google Sheets, Slack, Salesforce, HubSpot or Zoho Bigin. On an agent, add them one at a time with addPostCallAction instead. Full shape: https://docs.omnidim.io/docs/per-call-post-call-actions"
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
                            "type": "boolean",
                            "description": "Turn ending the call on or off. Leave it out to keep the current setting. `false` also clears `condition` and `message`."
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
                    "description": "Languages the agent should support. Pass each language as a display-name string exactly as it appears in the dashboard's language picker. Unrecognized names are skipped, and the request is refused when none is recognized. The order is not kept.",
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Update agent",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": false
        }
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Update cloned voice",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": false
        }
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
                "action": {
                    "type": "string",
                    "enum": [
                        "create",
                        "upsert"
                    ],
                    "description": "`salesforce` only: `upsert` finds the record by the caller's number\nand updates it or creates it. `create` creates a new record every\ncall. Defaults to `create`.\n"
                },
                "match_field": {
                    "type": "string",
                    "description": "`salesforce` only, with `upsert`: the phone field the caller's number is looked up in. Defaults to `Phone`.",
                    "example": "Phone"
                },
                "log_call": {
                    "type": "boolean",
                    "description": "`salesforce` only: log the call on the record, with the summary and recording link. Defaults to false."
                },
                "add_note": {
                    "type": "boolean",
                    "description": "`salesforce` only: add the call summary as a note on the record. Defaults to false."
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Update a post-call action",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": false
        }
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
        "query_params": [],
        "header_params": [],
        "annotations": {
            "title": "Upload knowledge base file",
            "readOnlyHint": false,
            "destructiveHint": false,
            "openWorldHint": false
        }
    },
    {
        "name": "whatsappCampaignActions",
        "description": "Launch, pause, resume or cancel a WhatsApp campaign.\n\nSet `action` to pick what to do.\n\n`launch`: Launch a campaign. Start a draft campaign and queue every pending contact once.\n\nIt needs at least one contact, unless `data_source` is `webhook`. Launch\nchecks the plan's monthly broadcast allowance and the wallet balance.\n`Idempotency-Key` is required, so a retry does not start it twice.\n\n`pause`: Pause a campaign. Stop sending until you resume.\n\nOnly a running campaign can be paused. A pause you make by hand is never\nresumed automatically.\n\n`resume`: Resume a campaign. Resume a paused campaign.\n\nPending contacts are sent. A contact already sent is never sent again.\nResume checks the wallet and allowance again, so it can answer `402`.\n\n`cancel`: Cancel a campaign. Stop a campaign for good. Contacts not yet sent are not sent. A completed\nor already-canceled campaign cannot be canceled.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "launch",
                        "pause",
                        "resume",
                        "cancel"
                    ],
                    "description": "What to do: launch, pause, resume, cancel."
                },
                "campaign_id": {
                    "type": "integer",
                    "description": "Id of a WhatsApp campaign, from `listWhatsappCampaigns`."
                },
                "Idempotency-Key": {
                    "type": "string",
                    "maxLength": 255,
                    "description": "Only for `launch`. A unique string you choose, up to 255 characters. Required on this\nroute. The same key with the same body replays the first answer for\n24 hours instead of acting twice. A different body with the same key\nanswers `409`."
                }
            },
            "required": [
                "action",
                "campaign_id"
            ],
            "additionalProperties": true
        },
        "annotations": {
            "title": "Control WhatsApp campaign",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": true
        },
        "field": "action",
        "actions": {
            "launch": {
                "operation": "launchWhatsappCampaign",
                "method": "POST",
                "path": "/whatsapp/campaigns/{campaign_id}/launch",
                "path_params": [
                    "campaign_id"
                ],
                "query_params": [],
                "header_params": [
                    "Idempotency-Key"
                ],
                "inputs": [
                    "campaign_id",
                    "Idempotency-Key"
                ],
                "required": [
                    "Idempotency-Key",
                    "campaign_id"
                ],
                "sends_field": false
            },
            "pause": {
                "operation": "pauseWhatsappCampaign",
                "method": "POST",
                "path": "/whatsapp/campaigns/{campaign_id}/pause",
                "path_params": [
                    "campaign_id"
                ],
                "query_params": [],
                "header_params": [],
                "inputs": [
                    "campaign_id"
                ],
                "required": [
                    "campaign_id"
                ],
                "sends_field": false
            },
            "resume": {
                "operation": "resumeWhatsappCampaign",
                "method": "POST",
                "path": "/whatsapp/campaigns/{campaign_id}/resume",
                "path_params": [
                    "campaign_id"
                ],
                "query_params": [],
                "header_params": [],
                "inputs": [
                    "campaign_id"
                ],
                "required": [
                    "campaign_id"
                ],
                "sends_field": false
            },
            "cancel": {
                "operation": "cancelWhatsappCampaign",
                "method": "POST",
                "path": "/whatsapp/campaigns/{campaign_id}/cancel",
                "path_params": [
                    "campaign_id"
                ],
                "query_params": [],
                "header_params": [],
                "inputs": [
                    "campaign_id"
                ],
                "required": [
                    "campaign_id"
                ],
                "sends_field": false
            }
        }
    },
    {
        "name": "whatsappConversationActions",
        "description": "Take a conversation from the agent so your team answers, or hand it back to the agent.\n\nSet `action` to pick what to do.\n\n`take_over`: Take over a conversation. Take the conversation from the agent, so it stops replying and your team\nanswers.\n\nRepeating it changes nothing. Hand it back with\n`whatsappConversationActions` with `action` `hand_back` when the person is done.\n\n`hand_back`: Hand a conversation back. Give the conversation back to the agent and clear any pause.\n\nThe agent answers the customer's next message. Repeating it changes nothing.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "take_over",
                        "hand_back"
                    ],
                    "description": "What to do: take_over, hand_back."
                },
                "conversation_id": {
                    "type": "string",
                    "description": "A conversation id: the number id, a dash, then the customer's phone\ndigits, such as `412-919876543210`. From\n[listWhatsappConversations](/docs/api-reference/whatsapp/listWhatsappConversations).\n"
                }
            },
            "required": [
                "action",
                "conversation_id"
            ],
            "additionalProperties": true
        },
        "annotations": {
            "title": "Take over or hand back WhatsApp conversation",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": false
        },
        "field": "action",
        "actions": {
            "take_over": {
                "operation": "takeOverWhatsappConversation",
                "method": "POST",
                "path": "/whatsapp/conversations/{conversation_id}/take_over",
                "path_params": [
                    "conversation_id"
                ],
                "query_params": [],
                "header_params": [],
                "inputs": [
                    "conversation_id"
                ],
                "required": [
                    "conversation_id"
                ],
                "sends_field": false
            },
            "hand_back": {
                "operation": "handBackWhatsappConversation",
                "method": "POST",
                "path": "/whatsapp/conversations/{conversation_id}/hand_back",
                "path_params": [
                    "conversation_id"
                ],
                "query_params": [],
                "header_params": [],
                "inputs": [
                    "conversation_id"
                ],
                "required": [
                    "conversation_id"
                ],
                "sends_field": false
            }
        }
    },
    {
        "name": "workflow",
        "description": "Read workflows and their runs: list workflows, get one, validate a draft, list\na workflow's runs and read one, and look up node types and field choices.\n\nSet `action` to pick what to do.\n\n`node_types`: List workflow node types. Search the node types a workflow can use.\n\nExamples are `whatsapp`, `voice_ai` and `conditional`. Call it first when\nyou do not know which node to add. Then call `workflow` with `action` `node_type` for one\ntype's settings.\n\n`node_type`: Get a workflow node type. Get the settings one node type reads.\n\nCall it before you add or edit a node. Its `fields` are the keys of the\nnode's `config`. Use `detail=full` only when you need help text and\nexamples.\n\n`field_options`: List choices for a node field. List the choices for one `ref` field of a node type.\n\nExamples are the phone numbers, agents or integrations in your account. Call\nit for every `ref` field and never guess an id. If it returns `400\nno_options`, the field is not a list choice, so ask the user for the value.\n\n`list`: List workflows. List your workflows, oldest first, one cursor page at a time.\n\nUse it to find a workflow id. Pass back `next_cursor` until it is `null`.\n\n`get`: Get a workflow. Get one workflow with its draft, status and `revision`.\n\nCall it before every edit to get the current `revision`. Use\n`view=structure` to see nodes and edges without config on a large workflow.\nSecrets read back as `********`.\n\n`validate`: Validate a workflow draft. Check the draft and list what blocks publish.\n\nIt changes nothing. Call it after your edits and fix every error before\n`workflowActions` with `action` `publish`.\n\n`runs`: List workflow runs. List recent runs of a workflow, newest first, with the step that failed.\n\nUse it to find the run behind \"my workflow didn't run after the call\":\nfilter by `state=failed`, or by the `call_sid` of the call that should\nhave started it. Read one run's steps with `workflow` with `action` `run`.\n\n`run`: Get a workflow run. Get one workflow run with the result of each step.\n\nUse it to read the outcome of `workflowActions` with `action` `test`. The run is finished when\n`state` is `completed`, `failed` or `cancelled`.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "node_types",
                        "node_type",
                        "field_options",
                        "list",
                        "get",
                        "validate",
                        "runs",
                        "run"
                    ],
                    "description": "What to do: node_types, node_type, field_options, list, get, validate, runs, run."
                },
                "q": {
                    "type": "string",
                    "description": "Only for `node_types`. Words to match against the type, label and description, such as `whatsapp`."
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
                    "description": "Only for `node_types`. Only types in this category."
                },
                "node_type": {
                    "type": "string",
                    "description": "Only for `node_type`, `field_options`. A node type from `listWorkflowNodeTypes`, such as `whatsapp`."
                },
                "detail": {
                    "type": "string",
                    "enum": [
                        "minimal",
                        "full"
                    ],
                    "default": "minimal",
                    "description": "Only for `node_type`. `full` adds descriptions, examples and `output_example`."
                },
                "field": {
                    "type": "string",
                    "description": "Only for `field_options`. A field name from `getWorkflowNodeType`."
                },
                "depends": {
                    "type": "integer",
                    "description": "Only for `field_options`. The value of the field this one depends on (`depends_on` in the node type), such as the chosen phone number id."
                },
                "limit": {
                    "type": "integer",
                    "default": 20,
                    "minimum": 1,
                    "maximum": 100,
                    "description": "Only for `list`, `runs`. Rows per page."
                },
                "cursor": {
                    "type": "string",
                    "description": "Only for `list`. The `next_cursor` from the previous page. Omit it on the first request. Pass it back unchanged."
                },
                "workflow_id": {
                    "type": "integer",
                    "description": "Only for `get`, `validate`, `runs`, `run`. Id of the workflow."
                },
                "view": {
                    "type": "string",
                    "enum": [
                        "structure",
                        "full"
                    ],
                    "default": "full",
                    "description": "Only for `get`. `structure` leaves node `config` out."
                },
                "state": {
                    "type": "string",
                    "enum": [
                        "running",
                        "waiting",
                        "completed",
                        "failed",
                        "cancelled"
                    ],
                    "description": "Only for `runs`. Only runs in this state."
                },
                "call_sid": {
                    "type": "string",
                    "description": "Only for `runs`. Only runs started by this call."
                },
                "execution_id": {
                    "type": "integer",
                    "description": "Only for `run`. The `execution_id` from `testWorkflow` or `listWorkflowExecutions`."
                }
            },
            "required": [
                "action"
            ],
            "additionalProperties": true
        },
        "annotations": {
            "title": "Read workflows",
            "readOnlyHint": true,
            "destructiveHint": false,
            "openWorldHint": false
        },
        "field": "action",
        "actions": {
            "node_types": {
                "operation": "listWorkflowNodeTypes",
                "method": "GET",
                "path": "/workflow-node-types",
                "path_params": [],
                "query_params": [
                    "q",
                    "category"
                ],
                "header_params": [],
                "inputs": [
                    "q",
                    "category"
                ],
                "required": [],
                "sends_field": false
            },
            "node_type": {
                "operation": "getWorkflowNodeType",
                "method": "GET",
                "path": "/workflow-node-types/{node_type}",
                "path_params": [
                    "node_type"
                ],
                "query_params": [
                    "detail"
                ],
                "header_params": [],
                "inputs": [
                    "node_type",
                    "detail"
                ],
                "required": [
                    "node_type"
                ],
                "sends_field": false
            },
            "field_options": {
                "operation": "listWorkflowFieldOptions",
                "method": "GET",
                "path": "/workflow-node-types/{node_type}/options/{field}",
                "path_params": [
                    "node_type",
                    "field"
                ],
                "query_params": [
                    "depends"
                ],
                "header_params": [],
                "inputs": [
                    "node_type",
                    "field",
                    "depends"
                ],
                "required": [
                    "field",
                    "node_type"
                ],
                "sends_field": false
            },
            "list": {
                "operation": "listWorkflows",
                "method": "GET",
                "path": "/workflows",
                "path_params": [],
                "query_params": [
                    "limit",
                    "cursor"
                ],
                "header_params": [],
                "inputs": [
                    "limit",
                    "cursor"
                ],
                "required": [],
                "sends_field": false
            },
            "get": {
                "operation": "getWorkflow",
                "method": "GET",
                "path": "/workflows/{workflow_id}",
                "path_params": [
                    "workflow_id"
                ],
                "query_params": [
                    "view"
                ],
                "header_params": [],
                "inputs": [
                    "workflow_id",
                    "view"
                ],
                "required": [
                    "workflow_id"
                ],
                "sends_field": false
            },
            "validate": {
                "operation": "validateWorkflow",
                "method": "POST",
                "path": "/workflows/{workflow_id}/validate",
                "path_params": [
                    "workflow_id"
                ],
                "query_params": [],
                "header_params": [],
                "inputs": [
                    "workflow_id"
                ],
                "required": [
                    "workflow_id"
                ],
                "sends_field": false
            },
            "runs": {
                "operation": "listWorkflowExecutions",
                "method": "GET",
                "path": "/workflows/{workflow_id}/executions",
                "path_params": [
                    "workflow_id"
                ],
                "query_params": [
                    "state",
                    "call_sid",
                    "limit"
                ],
                "header_params": [],
                "inputs": [
                    "workflow_id",
                    "state",
                    "call_sid",
                    "limit"
                ],
                "required": [
                    "workflow_id"
                ],
                "sends_field": false
            },
            "run": {
                "operation": "getWorkflowExecution",
                "method": "GET",
                "path": "/workflows/{workflow_id}/executions/{execution_id}",
                "path_params": [
                    "workflow_id",
                    "execution_id"
                ],
                "query_params": [],
                "header_params": [],
                "inputs": [
                    "workflow_id",
                    "execution_id"
                ],
                "required": [
                    "execution_id",
                    "workflow_id"
                ],
                "sends_field": false
            }
        }
    },
    {
        "name": "workflowActions",
        "description": "Create a workflow, edit its draft, publish it, test it, or turn it on or off.\nDeleting a workflow is its own tool, deleteWorkflow.\n\nSet `action` to pick what to do.\n\n`create`: Create a workflow. Create a workflow with a draft.\n\nWithout `graph`, the draft holds one `trigger` node, ready for\n`workflowActions` with `action` `edit` ops. Pass `graph` only to start from a complete graph. The\nresponse carries the `revision` you need to edit.\n\n`edit`: Edit a workflow draft. Change the draft with a list of `ops`.\n\nOps add, update, move or delete nodes, and connect or disconnect them. They\napply all together or not at all. Send the `revision` from your last read.\nOn `409 revision_conflict`, read the workflow again and retry.\n\nSecrets read back as `********`. Send them back unchanged to keep the stored\nvalue. This edits the draft only. Use `workflowActions` with `action` `publish` to make it live.\n\n`publish`: Publish a workflow. Make the draft the live version.\n\nReal events then run it, unless the workflow is paused. Publish is refused\nwhile the draft has errors, so run `workflow` with `action` `validate` first. Ask the user\nbefore you publish.\n\n`activate`: Activate a workflow. Turn the published workflow on, so real events run it. Use it to resume a workflow you paused with `workflowActions` with `action` `deactivate`.\n\n`deactivate`: Deactivate a workflow. Turn the published workflow off.\n\nReal events stop running it. The workflow and its draft stay. Use\n`workflowActions` with `action` `activate` to turn it back on.\n\n`test`: Test a workflow. Run the draft once with `payload` as the trigger data.\n\nEvery node runs for real: WhatsApp messages, SMS, emails and calls go out,\nand CRM records change. Ask the user first, and use their own phone number\nor email in the payload.\n\nIt returns an `execution_id` at once. Poll `workflow` with `action` `run` for the\nresult.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "create",
                        "edit",
                        "publish",
                        "activate",
                        "deactivate",
                        "test"
                    ],
                    "description": "What to do: create, edit, publish, activate, deactivate, test."
                },
                "name": {
                    "type": "string",
                    "description": "Only for `create`, `edit`. A non-empty name."
                },
                "graph": {
                    "type": "object",
                    "description": "Only for `create`. A complete graph to start a workflow from, in the same shape `getWorkflow`\nreturns under `draft`. A workflow you read can be sent back as a new one.\nIt is built with the same checks as `editWorkflow` ops. Most callers skip it\nand build with `editWorkflow` instead.",
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
                },
                "workflow_id": {
                    "type": "integer",
                    "description": "Only for `edit`, `publish`, `activate`, `deactivate`, `test`. Id of the workflow."
                },
                "revision": {
                    "type": "string",
                    "description": "Only for `edit`. The `draft.revision` from your last `getWorkflow` or edit."
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
                    },
                    "description": "Only for `edit`."
                },
                "payload": {
                    "type": "object",
                    "additionalProperties": true,
                    "description": "Only for `test`. The trigger data. Nodes read it as `{{ context.<trigger id>.<field> }}`. See `output_example` of the trigger node type for its shape."
                }
            },
            "required": [
                "action"
            ],
            "additionalProperties": true
        },
        "annotations": {
            "title": "Change workflows",
            "readOnlyHint": false,
            "destructiveHint": true,
            "openWorldHint": true
        },
        "field": "action",
        "actions": {
            "create": {
                "operation": "createWorkflow",
                "method": "POST",
                "path": "/workflows",
                "path_params": [],
                "query_params": [],
                "header_params": [],
                "inputs": [
                    "name",
                    "graph"
                ],
                "required": [
                    "name"
                ],
                "sends_field": false
            },
            "edit": {
                "operation": "editWorkflow",
                "method": "PATCH",
                "path": "/workflows/{workflow_id}",
                "path_params": [
                    "workflow_id"
                ],
                "query_params": [],
                "header_params": [],
                "inputs": [
                    "workflow_id",
                    "revision",
                    "ops",
                    "name"
                ],
                "required": [
                    "ops",
                    "revision",
                    "workflow_id"
                ],
                "sends_field": false
            },
            "publish": {
                "operation": "publishWorkflow",
                "method": "POST",
                "path": "/workflows/{workflow_id}/publish",
                "path_params": [
                    "workflow_id"
                ],
                "query_params": [],
                "header_params": [],
                "inputs": [
                    "workflow_id"
                ],
                "required": [
                    "workflow_id"
                ],
                "sends_field": false
            },
            "activate": {
                "operation": "activateWorkflow",
                "method": "POST",
                "path": "/workflows/{workflow_id}/activate",
                "path_params": [
                    "workflow_id"
                ],
                "query_params": [],
                "header_params": [],
                "inputs": [
                    "workflow_id"
                ],
                "required": [
                    "workflow_id"
                ],
                "sends_field": false
            },
            "deactivate": {
                "operation": "deactivateWorkflow",
                "method": "POST",
                "path": "/workflows/{workflow_id}/deactivate",
                "path_params": [
                    "workflow_id"
                ],
                "query_params": [],
                "header_params": [],
                "inputs": [
                    "workflow_id"
                ],
                "required": [
                    "workflow_id"
                ],
                "sends_field": false
            },
            "test": {
                "operation": "testWorkflow",
                "method": "POST",
                "path": "/workflows/{workflow_id}/test",
                "path_params": [
                    "workflow_id"
                ],
                "query_params": [],
                "header_params": [],
                "inputs": [
                    "workflow_id",
                    "payload"
                ],
                "required": [
                    "workflow_id"
                ],
                "sends_field": false
            }
        }
    }
]"""

TOOLS: Final[list[Tool]] = json.loads(_TOOLS_JSON)
