---
name: billing
arguments:
  - name: question
    description: "The billing question, in the user's words (e.g. 'my balance dropped overnight', 'where is my GST invoice', 'my number was released')."
    required: true
---

# Answer a billing question from the account's own data: balance, charges, plan, GST, auto-renew and released numbers.

Answer this billing question from the account's own data:

"(the question in the user's words)"

Never promise a refund, credit or waiver, and never say one is likely. That is the billing team's decision: pass them the facts.

1. Write the question as one line: a charge or drop they don't recognize, a failed payment, an invoice or GST question, a renewal, a released number, or a plan question.
2. Read the account with `getAccountBalance`: balance, plan, auto-recharge state, the minutes the balance buys and `plan.is_usage_based`. A `403` means the user lacks Billing access: an administrator can grant it.
3. If `getPlanAndAddons` is available to you, read it: plan status and renewal or expiry date, add-ons, and the numbers that renew in the next 14 days with whether the balance covers each.
4. Then follow the branch:
   - Balance dropped or a charge they don't recognize: list the calls for the days around the drop with `listCallLogs` { "date_from": "<day>", "date_to": "<day>", "include_details": false, "pagesize": 5 }, paging with `pageno`. Each row carries its cost. Look for the day with many more calls than usual and check `bulk_call_id`: a campaign explains a spike (read it with `getBulkCall`). Number renewals also charge the balance: check `expiry_date` in `listPhoneNumbers`.
   - Number released: it is no longer in `listPhoneNumbers`. A number with auto-renew off works until the end of its paid period and is then released. A number whose renewal the balance didn't cover can be released too. These tools can't read the release history: say which of the two fits what you saw, and hand the number to staff. Don't promise it can be got back.
   - Renewal coming: name the number and its `expiry_date`, and whether the balance covers it (step 3). The user turns auto-renew on or off per number.
   - Failed payment, invoice or GST: these tools can't read payments or invoices. Ask for the payment date, amount and the transaction or invoice id, and hand it to staff. Don't state tax rules from memory: check `searchDocs` first.
5. Answer with the figures you read (balance, plan, dates, call ids behind a charge) and what they mean. If something needs the billing team (refund, credit, payment or invoice fix, a released number), say you passed it on, with what you found, and leave the decision to them.

Handing over: where a step says to hand it to staff or pass it on, open a case with `createSupportCase` (or add to the open one with `addCaseMessage`) holding those ids, if those tools are available; otherwise tell the user to contact support with the same ids.
