---
name: referrals
arguments:
  - name: question
    description: "The referral question, in the user's words (e.g. 'my friend joined but I got no reward')."
    required: true
---

# Explain the state of a referral reward without revealing how rewards are checked.

Explain this referral reward:

"(the question in the user's words)"

1. Write the question as one line: which referral, when the friend joined, and what the user expected.
2. These tools can't read referral rewards. Ask the user what their referral page shows for this one: pending, granted, withheld or expired. Read the program's rules with `searchDocs`.
3. Explain the state:
   - Pending: the reward isn't due yet. Say what the program's documented condition is, if the docs give one.
   - Granted: the reward was paid. Point to where the user sees it.
   - Withheld: the sign-up didn't pass the program's checks for a genuine new customer. This is the check working as meant, not a fault. Say it in one general sentence. Never say what the check looks at or why this one matched, even if asked.
   - Expired: the reward's time ran out under the program's rules.
4. Don't promise to release a withheld reward. If the user disputes it, pass it to staff with the date and the state, and say staff will review it.

Handing over: where a step says to hand it to staff or pass it on, open a case with `createSupportCase` (or add to the open one with `addCaseMessage`) holding those ids, if those tools are available; otherwise tell the user to contact support with the same ids.
