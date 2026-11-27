---
name: "Recommended provider stacks by language"
description: "Which transcriber (STT), voice (TTS), and language model to choose, grouped by the caller's language. Reflects what works in production."
---

# Recommended provider stacks

Each agent uses a transcriber (speech-to-text), a voice (text-to-speech), and a
language model, all set on `createAgent`. The pairings below work well in
production, grouped by the language your callers speak. Use `listProviders`
(`type` `stt`, `tts` or `llm`) and `listVoices` for the live catalog.

## Language model

- Default: leave `model.model` out, and the agent gets the organization's
  default model. An organization can set its own default, so do not replace it
  unless the user names a model. Without one, the platform default applies
  (`gpt-4.1-mini` today).
- Alternatives: any other `name` from `listProviders` with `type: "llm"`, which lists only the
  models your organization can use.

## Voice

- Default: one of the OmniDimension voices, our most recommended voices. Our
  team picks them for each language and tests them on real calls. List them
  with `listVoices` `provider=featured`, and save one under its `service`.
  See `omnidim://reference/voices`.

## By caller language

- **Indian English (en-IN):** transcriber `soniox`; an OmniDimension voice
  for English (India).
- **Hindi / Hinglish (mixed Hindi and English):** transcriber `soniox`
  (handles code-mixed speech in one stream); an OmniDimension voice for Hindi.
- **Other Indian languages (Tamil, Telugu, Marathi, Bengali, Gujarati,
  Kannada, Malayalam, Punjabi):** transcriber `soniox`; an OmniDimension voice
  for that language.
- **US English:** transcriber `soniox`; an OmniDimension voice for English
  (American).
- **No OmniDimension voice for the language:** another `cartesia` voice.

## Field notes

- `transcriber.provider` is `soniox` unless the user asks for another one by
  name. Any other choice must be a `name` from `listProviders` with `type: "stt"`, which lists
  only the transcribers your organization can use.
- `voice.provider` is the `service` of a voice from `listVoices`, which lists
  only voices your organization can use. Send only `provider` and `voice_id`:
  the platform picks the voice model.

## Responsiveness

- Keep the system prompt focused. Long prompts add latency to every turn.
- Verify your chosen voice on a short test call before launch (see
  `omnidim://reference/voices`).
