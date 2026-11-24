# Build an automation workflow from a plain-language goal: pick the trigger and nodes, wire them, validate, test with the user's consent, then publish.

Build an OmniDimension workflow for this goal:

"(describe what should happen, and when)"

Read the `omnidim://guide/workflows` resource first. It explains triggers, outputs, ops and errors.

1. Pick the trigger, then find each node type with `listWorkflowNodeTypes` and read its fields with
   `getWorkflowNodeType`.
2. For every field that takes an id (a number, template, integration or agent), list real choices with
   `listWorkflowFieldOptions` and confirm them with the user. Never guess an id.
3. `createWorkflow`, then build it with `editWorkflow` batches. Use readable node ids, wire branches with
   `after` and `handle`, and add a notes node that says what the workflow is for.
4. `validateWorkflow` and fix every error.
5. A test run happens for real: messages, calls and CRM writes go out. Only call `testWorkflow` after the
   user says yes, with their own phone number or email in the payload. It returns at once, so check
   `getWorkflowExecution` up to 10 times, a few seconds apart, until `state` is `completed`, `failed`
   or `cancelled`. If `state` is `waiting`, report the steps so far and stop.
6. Show the user the finished flow, then `publishWorkflow` when they approve. Publishing makes it live.
   If the trigger is post-call, ask which agent it is for. After the user's yes, run `addPostCallAction`
   with `type: workflow` on that agent: until then the workflow never fires.
7. Prefer creating a new workflow. Never publish, activate, deactivate, delete or test an existing
   workflow without the user's explicit yes, and read it with `getWorkflow` first.

