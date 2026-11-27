---
name: whatsapp
arguments:
  - name: problem
    description: "What fails on WhatsApp, in the user's words (e.g. 'my template messages are not delivered', 'the agent doesn't reply')."
    required: true
---

# Find why WhatsApp messages fail, templates are missing or rejected, or replies don't reach the agent.

Find why this fails on WhatsApp:

"(the problem in the user's words)"

1. Write the problem as one line: sending or receiving, templates or free text, which number, since when.
2. Read the number with `listWhatsappNumbers` (or `getWhatsappNumber` for one): `provider`, `status`, `account_restriction`, `agent_id`, `quality_rating`, `messaging_limit` and `capabilities`.
   - `status` `disconnected`: the number is missing its credentials and can't send. The user connects it again.
   - `status` `restricted`, or `account_restriction` set: WhatsApp limits this number. The fix is in the user's Meta Business Manager, not here.
   - Low `quality_rating`, or more new chats than `messaging_limit` (new chats per 24 hours, Meta numbers only): Meta caps whom the number can start chats with. Sends past the cap fail.
   - `capabilities` says what the number can send. A send it doesn't list fails.
3. Templates: read them with `listWhatsappTemplates` { "number_id": <id> }.
   - `status` rejected: give the user the `rejected_reason`. They fix the template in Meta and submit it again.
   - Missing or still pending though Meta shows it approved: the list is as last synced. Sync the templates with `syncWhatsappTemplates` if that tool is available and the user says go ahead (otherwise the user syncs them in the dashboard), then read the list again.
4. Failed messages: find the conversation with `listWhatsappConversations`, then read it with `listWhatsappMessages` { "conversation_id": "<id>" }. A failed message carries `failure` with `code` and `reason`.
   - A Meta permission error: the user's Meta Business Manager hasn't given this number or app the permission. They fix it there.
   - The recipient opted out: check `listWhatsappOptOuts` { "number_id": <id> }. Sends to them stay blocked until the opt-out is lifted.
   - Any other code: look it up with `searchDocs` before naming a cause.
5. Replies don't reach the agent: incoming text reaches an agent only when one is attached. If `agent_id` on the number is empty, that is the answer: attach the agent to the number.
6. If the number is also used in the WhatsApp Business app on a phone (coexistence), some behavior differs. These tools can't tell: ask the user.
7. Answer with the cause, the number id and the message or template ids that show it, and the fix as steps. Say plainly when the fix is in Meta's Business Manager. End with one test message.
