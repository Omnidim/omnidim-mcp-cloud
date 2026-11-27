---
name: feature_request
arguments:
  - name: request
    description: "What the user asks the product to do, in their words (e.g. 'can the agent send an SMS after the call?')."
    required: true
---

# Answer a feature request with what the product does today and the closest documented way to get there.

Answer this request with what works today:

"(the request in the user's words)"

1. Write the goal behind the request as one line: what the user wants to achieve, not only the feature they named.
2. Search with `searchDocs` for the feature and for the goal, and read the best pages with `readDoc`.
3. If the product already does it, it is not a request: give the steps from the doc, with its link.
4. If it doesn't, say so plainly, then give the closest documented way to reach the goal, as numbered steps the user can take (for example an after-call webhook to their own system, a workflow, or an API call). Every step comes from a doc page or a tool result: link the page.
5. If there is no workaround, say that too. Never answer only "noted", and never promise the feature or a date.
6. Pass the request on with the goal in the user's words and the workaround you gave: open a case with `createSupportCase` if that tool is available; otherwise tell the user how to send the request to support.
