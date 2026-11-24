---
name: "Tips from real calls"
description: "What the best agents do on real calls: a short name-check greeting (measured), who and why on the second turn, call screening, placeholders, temperature (measured), ending calls."
---

# Tips from real calls: what the best agents do

Where this comes from: answered calls in the 30 days to 20 November 2026, from
200 agents in 86 accounts (165 outbound agents in 79 accounts, 35 inbound
agents in 17), each with at least 100 answered calls. For each agent we took
two shares of its answered calls:

- **Early drop**: the person hung up within 15 seconds.
- **Natural end**: the agent ended or transferred the call when it was done.

The tables show the median agent in each group. Tips 1 and 5 come from these
numbers. The other tips come from reading calls of the agents with the fewest
early drops, and from the docs. None of this proves cause, so test a change
on a few calls before you roll it out.

## 1. Outbound: open with a name check of 8 words or fewer

| Outbound `welcome_message` length | Early drop | Natural end |
|---|---|---|
| 8 words or fewer | 31% | 26% |
| 9 to 15 words | 37% | 15% |
| 16 to 25 words | 49% | 15% |
| More than 25 words | 46% | 8% |

In 11 accounts that run outbound agents with both a short greeting (15 words
or fewer) and a longer one, the short one had fewer early drops in 10. A good
first line asks only for the person: "Hi, am I speaking with [name]?" Say who
you are and why on the next turn, after they answer.

Inbound is different: the caller chose to call. Inbound agents with a greeting
of 16 to 25 words had a median early drop of 19% (26 agents in 12 accounts).
Greet, say who they reached, and ask how you can help.

## 2. Outbound: on the second turn, say who, why, and ask for a minute

One sentence: the agent's name, the company, and the thing the person did,
such as "You asked about our evening course" or "You applied for the sales
role". Then ask for permission with a time: "Is now a good time for two
minutes?" If they are busy, ask when to call back, repeat the time, and end
the call politely.

## 3. Outbound: get past call screening

Many phones now answer unknown numbers with a screening assistant ("If you
record your name and reason for calling..."). Tell the agent to answer with
one sentence that holds its name, the company and the reason, then wait. If
the person says "please hold", the agent waits and does not repeat itself.

## 4. Fill in the person's details, and check every placeholder

Put variables in square brackets, like `[name]` or `[course]`. In a campaign
they come from the contact list columns, so each name must match a column
header, and every row needs a value. A missing value makes the agent skip the
placeholder, so the line sounds broken ("Hi, am I speaking with ?").

## 5. Outbound: keep the temperature low for scripted calls

Outbound agents with `model.temperature` 0.3 or lower had a median early drop
of 37% and natural end of 21% (52 agents in 21 accounts), against 45% and 14%
above 0.3 up to 0.7 (105 agents in 62 accounts). There were too few inbound agents
to tell.

## 6. One short question per turn

Ask one thing, then listen. Answer the person's point directly, without
filler openers or repeating their words back.

## 7. Speak the caller's language

Tell the agent to answer in the language the caller uses, and to keep the
words people really say for products and forms (often English terms inside
Hindi or another language). Pick the transcriber and voice from the
`omnidim://reference/recommended-stack` guide for that language.

## 8. End the call on purpose

Set `end_call` to `{ "enabled": true, "condition": "..." }` with a plain
condition, for example "End the call once the appointment is confirmed or the
person says they are not interested." Then the call ends when the job is done
instead of waiting for a silence timeout.

## What did not show a clear pattern

The language model, the prompt length and the speech speed showed no steady
difference once accounts with very different call types were compared. Pick
the model by language and cost (`omnidim://reference/recommended-stack`), and
keep `voice.speech_speed` near 1.0 unless the user asks for a change.

If something here is unclear, call `searchDocs`.
