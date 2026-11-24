---
name: "Building workflows"
description: "How to build a workflow end to end: the tool order, lifecycle, triggers (entry), outputs and edges, exit, passing data, moving nodes, notes, ops, credentials, real test runs, errors, and a worked example."
---

# Building workflows

A workflow is a graph: one trigger node, then action and flow nodes joined by
edges. It runs on OmniDimension's servers each time its trigger fires.

## The tools, in the order you use them

1. `listWorkflowNodeTypes` (with `q`, e.g. "whatsapp") to find node types.
2. `getWorkflowNodeType` (`detail: minimal`) for the fields one type needs.
   Ask for `detail: full` only when you need the examples.
3. `listWorkflowFieldOptions` for any field of type `ref` (a number, an
   integration, a template, an agent). Never guess an id. If it returns
   `no_options`, ask the user for the value.
4. `createWorkflow` with a `name`. It starts with one node, `trigger`. You may
   pass a complete first `graph` instead, in the same shape `getWorkflow`
   returns under `draft` (node `config`, edges with `from`, `to`, `handle`).
5. `editWorkflow` with the `revision` from the last read and a list of `ops`.
6. `validateWorkflow`, then fix what it reports with another `editWorkflow`.
7. `testWorkflow` only after the user agrees (see "Test runs are real").
8. Show the user the flow and get a yes, then `publishWorkflow`. The workflow is live at once: real events run it. Do not call `workflowActions` with `action: "activate"` after it.

`getWorkflow` with `view: structure` shows nodes and edges without config.
Use it to orient in a large workflow. Use `view: full` before you edit config.

## Lifecycle

- You always edit the **draft**. A published workflow is never changed in place.
- `publishWorkflow` copies the draft to the live version and leaves a fresh draft
  for the next round of edits. It refuses while `validateWorkflow` has errors.
- `workflowActions` with `action: "deactivate"` pauses a published workflow, and `action: "activate"`
  resumes a paused one. Neither is needed to go live.
- Every edit needs the current `revision`. On `409 revision_conflict`, someone
  (often the user in the dashboard) saved first. Call `getWorkflow` and retry.

## Do not break a workflow that is already running

Most harm comes from changing a workflow the user did not ask you to touch.

- Default to creating a NEW workflow. Edit an existing one only when the user names it.
- Call `getWorkflow` first and read what it does before any edit. Keep its `revision`.
- Your edits land on the draft and change nothing live until you publish, except
  `webhook_enabled` on the trigger: it switches the live webhook URL at once. Ask
  before you change it on an existing workflow.
- `publishWorkflow` overwrites the live version that real events run. Publishing a
  paused workflow turns it back on. `workflowActions`
  with `action: "deactivate"` pauses automation the user depends on. `deleteWorkflow` stops it for good. Before any of
  these on an existing workflow, tell the user exactly what will change and get a yes.
- Never publish, activate, deactivate, delete or test a workflow as a side effect of another task.

## Entry: the trigger

Every workflow has exactly one trigger node. Its output is the event payload,
which later nodes read as `{{ context.<trigger id>.<field> }}`.

| Trigger type | Fires when | How it is attached |
|---|---|---|
| `trigger` | After a call (post-call), or on a POST to the webhook URL | Post-call: the agent's post-call actions point at this workflow. Webhook: `update_node` the trigger with `config: { webhook_enabled: true }`, then `getWorkflow` returns `webhook_url` |
| `whatsapp_inbound` | A media message (image, video, document, audio) arrives. Text still goes to the agent. Publishing moves the number off any other inbound workflow, so check with the user first | Its `phone_number_id` |
| `twilio_sms_inbound` | An SMS arrives | Its Twilio integration |
| `email_event_trigger` | A sent email is opened, clicked, replied to, or bounces | The source workflow |
| `omnidim_crm_trigger`, `leadsquared_trigger`, `shopify_trigger`, `instantly_event_trigger` | An event in that system | Its integration |

`getWorkflowNodeType` shows each trigger's `output_example`. The post-call
trigger carries `customer_number`, `call_status`, `summary`, `sentiment`,
`extracted_variables` and the transcript.

## Connecting nodes

An edge runs from one node's **output** to the next node. Plain nodes have one
output, `default`. Branching nodes have named outputs, and you must say which.
`getWorkflowNodeType` lists each type's outputs; this table is a summary:

| Node | Outputs |
|---|---|
| `conditional` | `True`, `False` |
| `switch_condition` | each case `id`, plus `else` |
| `time_condition` | `Yes`, `No` |
| `photo_analyzer` | `pass`, `fail` |
| `voice_ai` | `Completed`, `Not Completed` |
| `zoho_bigin` | `Created`, `Found`, `Ambiguous`, `Failed`, `Success` |

- One output can feed several nodes. They all run.
- `add_node` with `after` and `handle` places and connects a node in one step.
- To rewire, send `disconnect` and `connect` in the same batch.
- Every node except notes must be reachable from the trigger.

## Exit

There is no end node. A branch ends at a node with no outgoing edge, and the
run finishes when every branch has ended. `wait`, `wait_for_time`, `voice_ai`
and `send_email` pause the run and resume it later. `sub_workflow` starts
another workflow and continues at once. The target must be published and active, or the run
fails with "Target workflow has no published version".

## Passing data

`{{ context.<node id>.<field> }}` reads an earlier node's output. The engine
also provides `{{ context.webhook }}` (the trigger payload) and
`{{ context.execution_link }}`. Only nodes that run earlier have output. A
reference to a later node renders empty, and `validateWorkflow` warns about it.

Node ids appear in these references, so pick readable ones: `check_interest`,
`wa_followup`, `notify_sales`. Use lowercase letters, digits and underscores.
These names are taken: `webhook`, `execution_id`, `execution_link`, `get`,
`items`, `keys`, `values`.

Id fields (a number, template, integration, agent) always hold a literal id.
A `{{ }}` template there is refused, because it could resolve to a record in
another workspace.

## Moving things around

- `move_node` sets `{x, y}` on the dashboard canvas.
- `add_node` without a `position` lands to the right of its parent, below any
  siblings, so the canvas stays readable for the user.

## Notes

A `notes` node holds `note_text` for people reading the canvas. It is never
connected and never runs. Add one that says what the workflow is for, so the
next person to open it in the dashboard understands it.

## Ops

| Op | Fields |
|---|---|
| `add_node` | `id`, `type`, `config?`, `label?`, `position?`, `after?`, `handle?` |
| `update_node` | `id`, `config` (merged; `null` removes a key), `label?` |
| `move_node` | `id`, `position {x, y}` |
| `delete_node` | `id` (its edges go too) |
| `connect` | `from`, `to`, `handle?` (default `default`) |
| `disconnect` | `from`, `to`, `handle?` |

A batch applies completely or not at all. A failing op returns
`422 invalid_op` with its `op_index`.

## Credentials

Never put secrets in config when an integration exists. Pick integrations,
numbers and templates from `listWorkflowFieldOptions`. Secret fields (a Slack
webhook URL, API headers) read back as `********`. Send `********` back
unchanged and the stored value is kept. If the user has no matching
integration, tell them to connect one in the dashboard first.

## Test runs are real

`testWorkflow` runs the draft once with your `payload` as the trigger data.
**Every node runs for real**: WhatsApp messages, SMS, emails and calls go out,
and CRM records change. Before you call it, tell the user what will happen and
get a yes. Use their own phone number or email in the payload. The call returns `202` with an
`execution_id` at once. Check `getWorkflowExecution` up to 10 times, a few seconds apart,
until `state` is `completed`, `failed` or `cancelled`, then read each node's status, output
and error. A run that reaches a wait, call or email step can stay `waiting` for hours: then
report the steps so far and stop.

## Errors you will see

| Error | Meaning | What to do |
|---|---|---|
| `422 validation_failed` with `not_found` | An id is not in this workspace | Pick from `listWorkflowFieldOptions` |
| `422 validation_failed` on publish | Missing fields, an unconnected node, a bad handle | Fix each one, then publish again |
| `422 invalid_op` | An op is malformed | Fix the op at `op_index` |
| `409 revision_conflict` | The draft changed since you read it | `getWorkflow`, then retry |
| `409 no_draft` | There is no draft to edit, validate or publish | No tool can make a draft. Tell the user and stop |
| `400 no_options` | The field holds an id from another system | Ask the user for the value |
| `422` with `templated_ref` | An id field holds a `{{ }}` template | Put a literal id from `listWorkflowFieldOptions` |

## Worked example

"After a call, if the lead is interested, send our follow-up WhatsApp template
and tell #sales in Slack."

1. `createWorkflow { name: "Interested lead follow-up" }` gives you `trigger`
   and a `revision`.
2. `listWorkflowFieldOptions` for `whatsapp.phone_number_id`, then for
   `whatsapp.template_id` with `depends` set to that number. Confirm both with
   the user.
3. One `editWorkflow` batch:
   - `add_node { id: "check_interest", type: "conditional", after: "trigger",
     config: { conditions: [{ variable: "{{ context.trigger.extracted_variables.interested }}",
     operator: "==", value: "yes" }] } }`
   - `add_node { id: "wa_followup", type: "whatsapp", after: "check_interest",
     handle: "True", config: { phone_number_id: <id>, message_type: "template",
     template_id: <id>, to_number: "{{ context.trigger.customer_number }}" } }`
   - `add_node { id: "notify_sales", type: "slack", after: "wa_followup",
     config: { integration_id: <from listWorkflowFieldOptions>, channel: "<channel id the user confirms>",
     message: "Follow-up sent to {{ context.trigger.customer_number }}" } }`
   - `add_node { id: "about", type: "notes", config: { note_text: "Follows up
     interested leads after a call." } }`
4. `validateWorkflow` and fix anything reported. Show the user the flow and get a
   yes, then `publishWorkflow`.
5. Tell the user to point the agent's post-call action at this workflow.
