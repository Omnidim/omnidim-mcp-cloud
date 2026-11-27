---
name: "Building an agent with createAgent"
description: "The createAgent field shape with two complete, copy-ready example configurations (Indian-English support, Hindi/Hinglish reminder)."
---

# Building an agent with createAgent

On this server `createAgent` takes flat top-level arguments (no `requestBody`
wrapper; see the routing guide). The fields:

- `name` -- agent name.
- `welcome_message` -- the first line the agent speaks.
- `context_breakdown` -- a list of `{ title, body }` sections that form the
  agent's instructions.
- `call_type` -- "Incoming" or "Outgoing".
- `model` -- `{ model?, temperature? }`, e.g. `{ "temperature": 0.3 }`. Leave
  `model` out to keep the organization's default model.
- `voice` -- `{ provider, voice_id, speech_speed? }`. `speech_speed` is a playback
  multiplier (default `1.0`); leave it out unless the user asks for faster or
  slower speech. If you do set it, stay within **0.7-1.2**, or some voices go
  silent.
- `transcriber` -- `{ provider, language? }`, with `provider` `soniox`.

## Reading an agent back

`getAgent` returns flat names, and sending them back is not saved. Rename them
first, and send only the fields you change. If `updateAgent` returns `warnings`,
a field was not saved: fix it and send it again.

| `getAgent` returns | Send to `updateAgent` |
|---|---|
| `context_breakdown[].context_title`, `.context_body`, `.is_enabled` | `context_breakdown[].title`, `.body`, `.is_enabled` (drop `id`, `is_auto_generated`; send the whole list) |
| `voice_provider`, `voice_external_id`, `speech_speed` | `voice.provider`, `voice.voice_id`, `voice.speech_speed` (never `voice`, which is an internal id) |
| `llm_service`, `llm_temperature` | `model.model`, `model.temperature` |
| `asr_service`, `asr_<provider>_language`, `silence_timeout`, `should_apply_noise_reduction`, `interruption_min_words`, `max_call_duration_in_sec`, `first_ideal_message`, `is_first_ideal_message_dynamic` (and second) | `transcriber.provider`, `transcriber.language` (send `transcriber.provider` with it), `transcriber.silence_timeout_ms`, and the rest under `transcriber` with the same names |
| `bot_call_type` | `call_type` ("Incoming" or "Outgoing") |
| `languages[].label` | `languages` (the labels as plain strings) |
| `is_end_call_enabled`, `end_call_condition`, `end_call_message`, `end_call_message_type`, `end_call_message_prompt` | `end_call.enabled`, `.condition`, `.message`, `.message_type`, `.message_prompt` (send `end_call.enabled` only to turn it on or off) |
| `voicemail_enabled`, `voicemail_message` | `voicemail.enabled`, `voicemail.message` |
| `is_transfer_enabled`, `transfer_options` | `transfer.enabled`, `transfer.transfer_options` (the list replaces all options) |
| `enable_web_search`, `web_search_engine` | `web_search.enabled`, `web_search.provider` |
| `background_noise_enabled`, `background_noice_name`, `background_audio_volume` | `background_track.enabled`, `.name`, `.volume` |
| `post_call_config_ids` | change post-call actions with `updatePostCallAction` and `addPostCallAction`, never through `updateAgent` |

`name`, `welcome_message`, `is_welcome_message_dynamic`,
`is_welcome_message_interruption`, `is_interruption_allowed`, `timezone`,
`initial_ringing_sound_enabled` and `dynamic_variables` keep their names.

## Example: Indian-English support agent (inbound)

{
  "name": "Support agent",
  "welcome_message": "Hi, thanks for calling. How can I help you today?",
  "context_breakdown": [
    { "title": "Role", "body": "You are a friendly customer-support agent. Answer questions, and if you cannot help, offer to connect the caller to a human." }
  ],
  "call_type": "Incoming",
  "model": { "temperature": 0.3 },
  "voice": { "provider": "cartesia", "voice_id": "b521b304-7672-4cf9-9a34-b4eb1df1bde0" },
  "transcriber": { "provider": "soniox" }
}

## Example: Hindi / Hinglish appointment reminder (outbound)

{
  "name": "Appointment reminder",
  "welcome_message": "Namaste, kya aap [name] bol rahe hain?",
  "context_breakdown": [
    { "title": "Role", "body": "You remind customers about an upcoming appointment and confirm whether they can attend. Speak naturally in the caller's language, Hindi or English." }
  ],
  "call_type": "Outgoing",
  "model": { "temperature": 0.3 },
  "voice": { "provider": "cartesia", "voice_id": "<a Hindi voice from listVoices provider=featured>" },
  "transcriber": { "provider": "soniox" }
}

These show the field shape only. A real agent gets the full prompt and
settings from the `provision_agent` playbook.
