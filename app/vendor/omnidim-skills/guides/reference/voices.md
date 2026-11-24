---
name: "Choosing a voice"
description: "Start with OmniDimension voices (listVoices provider=featured), our most recommended; how to save one, and what to pick when none fits."
---

# Choosing a voice

`listVoices` returns only the voices your organization can use. Use a voice's
`name` field as the `voice_id` and its `service` as the `voice.provider` you
pass to `createAgent`.

## Start with OmniDimension voices

OmniDimension voices are our most recommended voices. Our team picks them for
each language and tests them on real calls. Use one unless the user asks for
something else.

- List them with `listVoices` `provider=featured`. Each one has a `gender` and
  the `featured_languages` it speaks: pick one that matches the agent. If those
  fields are missing, show the user a few names with their `sample_url` and
  let them pick.
- They cover English (India), English (American), Hindi, Tamil, Telugu,
  Marathi, Bengali, Gujarati, Kannada, Malayalam and Punjabi.
- Each one runs on Cartesia: save it as `voice.provider` `cartesia` with its
  `name` as `voice_id`.
- A Cartesia `search` does not find them. Only `provider=featured` lists them.

Example: Aadya, English (India) and Hindi, voice_id
`b521b304-7672-4cf9-9a34-b4eb1df1bde0`.

## If none fits

Pick another `cartesia` voice. `listVoices` `provider=cartesia` filters by
`search`, `language`, `accent` and `gender`. Not every catalog voice
synthesizes cleanly, so place a short test call and listen before launch.
