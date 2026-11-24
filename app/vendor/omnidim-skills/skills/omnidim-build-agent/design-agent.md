# Design a new voice agent's calls before building it: ask about the gaps, stress-test the plan, then write the call script for the user to approve.

Design the calls for a new OmniDimension voice agent, before anything is built:

"(describe the agent's job)"

Work in three phases, in order. This playbook builds nothing.

Phase 1: understand and ask
1. Read everything the user gave: requirements, documents, old prompts, notes, call goals. Pull out who the agent is and who it speaks for, who it talks to, the call direction, the goal and what counts as success, the languages, the voice gender and tone, the facts it may use and the things it must never say, numbers and limits, the flow, handoff or callback, the data to capture, when the call should end, and every gap or contradiction.
2. Open with an "Understanding" block of 5 lines or fewer: who, what, goal, success, and the biggest gap.
3. Ask about the gaps in one message. Number every question, give one line on why it matters, a suggested answer, and lettered options where they help. Ask only about real gaps, never about something the material already answers. Tell the user they can reply "default" to accept every suggestion. Ask one question at a time only if the user asks for that. Log a skipped question as an assumption.

Phase 2: stress-test the plan
4. In one more message, check the plan from each angle that applies, each finding with a suggested fix: contradictions (quote both parts); the other person's objections, pushback, hostile or trick questions; edge cases (wrong person, busy, silence, unclear audio, "are you a bot?", asks for a human, off-topic, a stop request, a language switch); partial outcomes (maybe, later, a counteroffer, a vague yes); loops, each with a cap; invented claims, over-promising and compliance risk; math errors; lines that sound robotic when spoken.
5. Then give a confirmation summary: the goal and the outcomes, hard rules and limits, the assumptions, and the fixes you will make to the source. Ask "Confirm, or tell me what to change." Write no script until the user confirms.

Phase 3: the call design, for the user to proofread
6. Write it in this structure:
   - Basics, from the confirmed summary, so the build step has them all: the agent's name, role, company and who it speaks for; voice gender and tone; languages and the terms that stay in English; AI disclosure; the forms of address allowed; the goal, what counts as success, and any fallback; hard rules and limits; banned phrases; the facts the agent may use; the never-say and never-promise list; the call direction; when the call may end; the transfer number and when to transfer, if any; the voicemail line, for outbound calls; the two lines the agent says when the caller is silent; where the results go after each call; and the number plan (an existing number, or buy one: the region, and landline or mobile).
   - Welcome message. If the user gave a welcome message, use it word for word. Otherwise, for an outbound call, write a name check of 8 words or fewer, such as "Hi, am I speaking with [name]?", and say who is calling and why on the next turn. For an inbound call, greet, say who they reached, and ask how you can help. Mark a message you wrote [DRAFT].
   - Intents, grouped: Opening, FAQ, Objections, Escalation or final ask, Counteroffers and partial answers, Agreement and close, Special situations, Language switch. Drop a group that does not apply, and add one the use case needs. Number every intent as **N. `intent_name`**, with Trigger (3 to 5 realistic phrases in the caller's language mix), **Bot:** (the exact spoken line) and Next (where the call goes, and the outcome if the call ends).
   - Script rules for every bot line: 1 to 3 sentences written to be spoken; everyday words in the caller's language mix; numbers spelled out as words, never digits or symbols; verb forms that match the voice's gender; only facts from the user, with anything uncertain marked [VERIFY]; no fact repeated across intents; at most one question per turn; dynamic values in [square_brackets].
   - Then: the state variables (a table), the outcomes (a table), a pronunciation guide, the changes from the source (one line each, with the reason), and the open items (everything marked [VERIFY] or [DRAFT]).
7. End with "Proofread the intents. Tell me which number to change, add or remove." After that, change only what the user names.
8. When the user approves, build it with the `provision_agent` playbook, using this design as the approved design.

Throughout: be direct, and never invent facts, numbers, results or policies. If the material holds a script for a different bot, take its requirements, not its lines. If the user adds information midway, say in one line what changed, then continue.
