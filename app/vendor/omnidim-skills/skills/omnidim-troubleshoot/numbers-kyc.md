---
name: numbers_kyc
arguments:
  - name: problem
    description: "The number or KYC problem, in the user's words (e.g. 'my KYC is stuck', 'my new number is not active')."
    required: true
---

# Find the state of a phone number and its KYC, and get what staff need to finish a stuck verification.

Find the state of the number and its verification:

"(the problem in the user's words)"

1. Write the problem as one line: which number, bought or imported, since when, and what the user sees (number not active, KYC pending or rejected, calls blocked).
2. Read the number with `listPhoneNumbers`: `number_provider`, `carrier_label`, `expiry_date` and `active_bot_id`. If the number isn't listed, the purchase didn't finish or the number was released: say which, from what you saw.
3. These tools can't read KYC status. Ask the user what the dashboard shows for it, and which number and carrier it is for.
4. If KYC is stuck or rejected, a name mismatch is the usual cause. Ask the user to type their name exactly as it is on the ID they used, letter by letter. Don't ask for the document or open one: the typed name is all staff need to compare.
5. If the account is new (its first number, or no calls yet in `listCallLogs`), mark the case urgent: the user can't start until this is done.
6. Hand it to staff with the number id, `carrier_label`, the KYC state the user saw, and the name as typed. Tell the user what you passed on and that staff finish the verification. Don't promise a time unless a doc found with `searchDocs` states one.

Handing over: where a step says to hand it to staff or pass it on, open a case with `createSupportCase` (or add to the open one with `addCaseMessage`) holding those ids, if those tools are available; otherwise tell the user to contact support with the same ids.
