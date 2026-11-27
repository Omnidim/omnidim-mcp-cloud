---
name: call_audio_behavior
arguments:
  - name: problem
    description: "What sounds or behaves wrong on calls, in the user's words (e.g. 'the agent is silent for 5 seconds', 'it talks over callers')."
    required: true
  - name: call_id
    description: "Optional call log id of a call that went wrong."
    required: false
---

# Find why a call sounds or behaves wrong: silence, slow replies, talking over the caller, cut off, wrong voice or sounds.

Find why calls sound or behave like this:

"(the problem in the user's words)"

1. Write the problem as one line: what the caller hears, at which point of the call, on every call or some. Get one bad call id: the one given, or find it with `listCallLogs` { "agentid": <id>, "date_from": "<day>", "date_to": "<day>", "include_details": false, "pagesize": 5 }. Get one good call of the same agent too, if one exists.
2. Read what happened on the bad call.
   - `getCallEvents` { "call_log_id": <id> }: the call step by step. Each turn has `speaker`, `text`, `t_ms` (time into the call), `latency_ms` (how long the agent took to reply), `kind` (speech, tool_call, transfer, voicemail_detected, language_switch, interrupt, silence_nudge, hangup, error) and `reason`. The top has `end_reason` (caller_hung_up, agent_ended, silence_timeout, voicemail, transferred, carrier_ended and so on), `duration_s`, `answered_by`, `amd_detected`, `voicemail_detection_on`, `transfer_attempted` and `transfer_connected`.
   - Calls older than 30 days have `timeline_available: false` and the transcript only. For those use `getCallLog`: `call_conversation`, `interactions` (per turn, with latency), `call_status` and `hangup_reason`. An empty `call_conversation` means the agent never spoke.
3. Read the agent's settings with `getAgent`: `voice_provider`, `voice_external_id`, `speech_speed`, `llm_service`, `is_interruption_allowed`, `interruption_min_words`, `is_welcome_message_interruption`, `initial_ringing_sound_enabled`, `background_noise_enabled`, `silence_timeout`, `max_call_duration_in_sec`, `end_call_condition` and `published_state`.
4. Match the symptom to the setting:
   - Agent never speaks: check the voice. Not every listed voice can speak, and `speech_speed` outside 0.7 to 1.2 can give a silent call (see `omnidim://guide/routing`). Compare with the voice of a good call's agent.
   - Ringing or a tone before the agent speaks: `initial_ringing_sound_enabled`. Sound under the voice: `background_noise_enabled`.
   - Calls end at the same length every time: `max_call_duration_in_sec`. Calls end after the caller goes quiet: `silence_timeout`. Calls end after the agent says goodbye early: `end_call_condition`.
   - Agent stops mid-sentence on noise or short words: `is_interruption_allowed` and `interruption_min_words`. Callers can't cut in at all: interruption is off.
   - Slow replies: find the turns with the highest `latency_ms` in the events. If only some turns are slow, look at what those turns did (a tool, a transfer, a long answer). Compare with a good call's turn times.
   - The user changed a setting but callers don't hear it: the agent is published and the change is only in the draft.
5. If no setting explains it, compare the good call with the bad call field by field, following the [troubleshoot.md](troubleshoot.md) playbook from its step 4.
6. Answer with the cause, the call id (and the good call id when you compared), the setting with its current value, and the value to set. If the settings are right and the call still went wrong, it is the platform's: hand it to staff with both call ids and the turn where it went wrong. End with one test call.

Handing over: where a step says to hand it to staff or pass it on, open a case with `createSupportCase` (or add to the open one with `addCaseMessage`) holding those ids, if those tools are available; otherwise tell the user to contact support with the same ids.
