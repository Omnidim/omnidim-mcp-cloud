# Changelog

All notable changes to this project. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [0.26.1](https://github.com/Omnidim/omnidim-mcp-cloud/compare/v0.26.0...v0.26.1) (2026-11-25)


### Fixed

* drop the sales link and voice ranking from agent and voice tool text ([#164](https://github.com/Omnidim/omnidim-mcp-cloud/issues/164)) ([ca5a5d8](https://github.com/Omnidim/omnidim-mcp-cloud/commit/ca5a5d8bd21dfa520f442df71868939df7e4d3d4))

## [0.26.0](https://github.com/Omnidim/omnidim-mcp-cloud/compare/v0.25.0...v0.26.0) (2026-11-25)


### Added

* listCallLogs filters by number and direction ([#163](https://github.com/Omnidim/omnidim-mcp-cloud/issues/163)) ([a277791](https://github.com/Omnidim/omnidim-mcp-cloud/commit/a277791facdf429c3b0a9ebad0b39cc17b1e7bcf))


### Fixed

* refresh playbooks and guides from Omnidim/skills ([#158](https://github.com/Omnidim/omnidim-mcp-cloud/issues/158)) ([40dc774](https://github.com/Omnidim/omnidim-mcp-cloud/commit/40dc7748e275809280e6848ddf7d8fb79faa8c05))
* serve each workflow operation as its own tool and drop promotional tool text ([#159](https://github.com/Omnidim/omnidim-mcp-cloud/issues/159)) ([827a652](https://github.com/Omnidim/omnidim-mcp-cloud/commit/827a652ea062aae980e8dc6e36406b4b9fbf2d2c))

## [0.25.0](https://github.com/Omnidim/omnidim-mcp-cloud/compare/v0.24.0...v0.25.0) (2026-11-25)


### Added

* **wellknown:** serve the ChatGPT plugin domain token ([#156](https://github.com/Omnidim/omnidim-mcp-cloud/issues/156)) ([c210c24](https://github.com/Omnidim/omnidim-mcp-cloud/commit/c210c24445fea36c5c2efef6b7b50e8a701953a0))

## [0.24.0](https://github.com/Omnidim/omnidim-mcp-cloud/compare/v0.23.1...v0.24.0) (2026-11-25)


### ⚠ BREAKING CHANGES

* fold the workflow tools into workflow (read) and workflowActions (write) ([#154](https://github.com/Omnidim/omnidim-mcp-cloud/issues/154))

### Added

* fold the workflow tools into workflow (read) and workflowActions (write) ([#154](https://github.com/Omnidim/omnidim-mcp-cloud/issues/154)) ([a7ba8f0](https://github.com/Omnidim/omnidim-mcp-cloud/commit/a7ba8f0e77f934c8dad5761e4723530051edfdd4))
* operator tokens with omnidim:read scope, operator-only support tools, valid-JSON trimming, BACKEND_BASE_URL, ping ([#137](https://github.com/Omnidim/omnidim-mcp-cloud/issues/137)) ([ac7630e](https://github.com/Omnidim/omnidim-mcp-cloud/commit/ac7630e9fa9e57650b8069cc192b25e871ab4cbb))

## [0.23.1](https://github.com/Omnidim/omnidim-mcp-cloud/compare/v0.23.0...v0.23.1) (2026-11-25)


### Fixed

* stop serving omnidim-onboard-client over MCP, since no MCP tool reaches the Reseller API ([#152](https://github.com/Omnidim/omnidim-mcp-cloud/issues/152)) ([4b4bf02](https://github.com/Omnidim/omnidim-mcp-cloud/commit/4b4bf0282d17995967455fd5ea7cc0da2165d859))

## [0.23.0](https://github.com/Omnidim/omnidim-mcp-cloud/compare/v0.22.0...v0.23.0) (2026-11-25)


### Added

* Claude loads the OmniDimension skills straight from the connector ([#147](https://github.com/Omnidim/omnidim-mcp-cloud/issues/147)) ([ac1f5d9](https://github.com/Omnidim/omnidim-mcp-cloud/commit/ac1f5d99f74e4bfbb01d7a76fee0ba0646cbd570))
* name the website each connected AI app signs in from ([#148](https://github.com/Omnidim/omnidim-mcp-cloud/issues/148)) ([0c5faa0](https://github.com/Omnidim/omnidim-mcp-cloud/commit/0c5faa01d8aaa40076f9bf37d09580d1430ed46e))


### Fixed

* name the merged tool where a tool description names a folded operation ([#150](https://github.com/Omnidim/omnidim-mcp-cloud/issues/150)) ([2938aa6](https://github.com/Omnidim/omnidim-mcp-cloud/commit/2938aa6a30d59b9d5215134ff2c415d0cde5ecfd))
* sync the skills from Omnidim/skills ce71fca, so served skills point at the MCP setup docs ([#151](https://github.com/Omnidim/omnidim-mcp-cloud/issues/151)) ([816a132](https://github.com/Omnidim/omnidim-mcp-cloud/commit/816a1328ff701a7673cea2d723903e80dd731eff))

## [0.22.0](https://github.com/Omnidim/omnidim-mcp-cloud/compare/v0.21.2...v0.22.0) (2026-11-24)


### Added

* list and disconnect a user's connected apps over the internal API ([#145](https://github.com/Omnidim/omnidim-mcp-cloud/issues/145)) ([e447c5c](https://github.com/Omnidim/omnidim-mcp-cloud/commit/e447c5cea0b18692c1f40e21c1057a6e50081042))

## [0.21.2](https://github.com/Omnidim/omnidim-mcp-cloud/compare/v0.21.1...v0.21.2) (2026-11-24)


### Fixed

* replace a browser's older MCP grant when it approves the same app again ([#143](https://github.com/Omnidim/omnidim-mcp-cloud/issues/143)) ([7c93539](https://github.com/Omnidim/omnidim-mcp-cloud/commit/7c935398956951d8e9f9d5d58cc5d86a2aea94db))

## [0.21.1](https://github.com/Omnidim/omnidim-mcp-cloud/compare/v0.21.0...v0.21.1) (2026-11-24)


### Fixed

* answer ping, accept every notification and list no resource templates, as the MCP spec asks ([#141](https://github.com/Omnidim/omnidim-mcp-cloud/issues/141)) ([99541ef](https://github.com/Omnidim/omnidim-mcp-cloud/commit/99541efe65278d4dcb93b2ff1d6ad5a300078efa))

## [0.21.0](https://github.com/Omnidim/omnidim-mcp-cloud/compare/v0.20.0...v0.21.0) (2026-11-24)


### ⚠ BREAKING CHANGES

* serve 101 MCP tools, folding 24 operations into 9 tools with an action field ([#140](https://github.com/Omnidim/omnidim-mcp-cloud/issues/140))

### Added

* serve 101 MCP tools, folding 24 operations into 9 tools with an action field ([#140](https://github.com/Omnidim/omnidim-mcp-cloud/issues/140)) ([661e7d0](https://github.com/Omnidim/omnidim-mcp-cloud/commit/661e7d00bb467f037bd7754eddde85a90d3a1dcc))
* serve one MCP tool for operations the spec marks as merged ([#138](https://github.com/Omnidim/omnidim-mcp-cloud/issues/138)) ([498162d](https://github.com/Omnidim/omnidim-mcp-cloud/commit/498162d0918f4518bbf478e163c17119d5521723))

## [0.20.0](https://github.com/Omnidim/omnidim-mcp-cloud/compare/v0.19.1...v0.20.0) (2026-11-24)


### Added

* export the skills as a Claude plugin the claude.ai directory accepts ([#132](https://github.com/Omnidim/omnidim-mcp-cloud/issues/132)) ([58c5345](https://github.com/Omnidim/omnidim-mcp-cloud/commit/58c5345e8dde7dee06408b836ca84b19af2c9720))
* serve the playbooks and guides written in Omnidim/skills ([#135](https://github.com/Omnidim/omnidim-mcp-cloud/issues/135)) ([9af321b](https://github.com/Omnidim/omnidim-mcp-cloud/commit/9af321ba1baf9f3567fc7cc9c1322dec56eefd25))

## [0.19.1](https://github.com/Omnidim/omnidim-mcp-cloud/compare/v0.19.0...v0.19.1) (2026-11-24)


### Fixed

* refresh tool descriptions from the updated API spec ([#130](https://github.com/Omnidim/omnidim-mcp-cloud/issues/130)) ([f652fc7](https://github.com/Omnidim/omnidim-mcp-cloud/commit/f652fc79617c761fff579af6e59c3b7be0335c48))

## [0.19.0](https://github.com/Omnidim/omnidim-mcp-cloud/compare/v0.18.0...v0.19.0) (2026-11-23)


### Added

* AI clients design, build, test and update agents with the team's playbook, in every client ([#126](https://github.com/Omnidim/omnidim-mcp-cloud/issues/126)) ([3c2f3bd](https://github.com/Omnidim/omnidim-mcp-cloud/commit/3c2f3bd37c95d79857479251aeab8bad0018c5a6))

## [0.18.0](https://github.com/Omnidim/omnidim-mcp-cloud/compare/v0.17.2...v0.18.0) (2026-11-22)


### Added

* publish a public server card built from the live tool list ([#115](https://github.com/Omnidim/omnidim-mcp-cloud/issues/115)) ([f3421c1](https://github.com/Omnidim/omnidim-mcp-cloud/commit/f3421c14515272da61492ea0543c5f78069662c7))


### Fixed

* refresh tool descriptions from the updated API spec ([#119](https://github.com/Omnidim/omnidim-mcp-cloud/issues/119)) ([a700ef5](https://github.com/Omnidim/omnidim-mcp-cloud/commit/a700ef56b92a42d968fb65081426ec9148babff2))

## [0.17.2](https://github.com/Omnidim/omnidim-mcp-cloud/compare/v0.17.1...v0.17.2) (2026-11-22)


### Fixed

* label tools that change existing data as destructive ([#118](https://github.com/Omnidim/omnidim-mcp-cloud/issues/118)) ([6c2e8f5](https://github.com/Omnidim/omnidim-mcp-cloud/commit/6c2e8f5454d657ca5cbd6d555806336d0c3b87de))

## [0.17.1](https://github.com/Omnidim/omnidim-mcp-cloud/compare/v0.17.0...v0.17.1) (2026-11-22)


### Fixed

* meet Claude and ChatGPT directory tool rules ([#116](https://github.com/Omnidim/omnidim-mcp-cloud/issues/116)) ([1f95fdf](https://github.com/Omnidim/omnidim-mcp-cloud/commit/1f95fdf9e56acac36bbc39a556661f71030d7665))

## [0.17.0](https://github.com/Omnidim/omnidim-mcp-cloud/compare/v0.16.0...v0.17.0) (2026-11-22)


### Added

* recommend OmniDimension voices first ([#112](https://github.com/Omnidim/omnidim-mcp-cloud/issues/112)) ([78aad81](https://github.com/Omnidim/omnidim-mcp-cloud/commit/78aad816df38f2d4da5cd1c62842b51e4439d94d))

## [0.16.0](https://github.com/Omnidim/omnidim-mcp-cloud/compare/v0.15.0...v0.16.0) (2026-11-20)


### Added

* add a call tips guide measured on real calls, and use it when building agents and campaigns ([#109](https://github.com/Omnidim/omnidim-mcp-cloud/issues/109)) ([abed25f](https://github.com/Omnidim/omnidim-mcp-cloud/commit/abed25f920da36bd069af0e14932a81105943628))
* add a read-only MCP endpoint at /mcp/readonly ([#105](https://github.com/Omnidim/omnidim-mcp-cloud/issues/105)) ([b727a38](https://github.com/Omnidim/omnidim-mcp-cloud/commit/b727a38258fd481f537a4cfb0e4df5e868cf7769))
* add searchDocs and readDoc tools that answer from docs.omnidim.io ([#106](https://github.com/Omnidim/omnidim-mcp-cloud/issues/106)) ([f6aad21](https://github.com/Omnidim/omnidim-mcp-cloud/commit/f6aad21874d6d6b4ac6d952854278b3ae59b8eea))
* export the agent prompts and guides as Agent Skills ([#108](https://github.com/Omnidim/omnidim-mcp-cloud/issues/108)) ([9315c30](https://github.com/Omnidim/omnidim-mcp-cloud/commit/9315c300ea3e70feaae4d8e19fbb133e2b7c1887))
* optional OpenTelemetry traces, request id equals trace id ([#74](https://github.com/Omnidim/omnidim-mcp-cloud/issues/74)) ([3e5d6b1](https://github.com/Omnidim/omnidim-mcp-cloud/commit/3e5d6b1e5129d25f8415ae27aa553b9356cfc855))
* shrink large repeated schemas in tool inputs with the spec's x-mcp-brief mark ([#110](https://github.com/Omnidim/omnidim-mcp-cloud/issues/110)) ([65fa02e](https://github.com/Omnidim/omnidim-mcp-cloud/commit/65fa02eaead9225a5fd1914a9abf1da6b0d590d8))


### Fixed

* answer pre-consent sign-in errors with an error page, never a redirect ([#65](https://github.com/Omnidim/omnidim-mcp-cloud/issues/65)) ([c21e596](https://github.com/Omnidim/omnidim-mcp-cloud/commit/c21e596698c5f19c9d7cae6fd81977b9acf13f23))
* keep long call logs as valid JSON with transcript, recording and cost ([#104](https://github.com/Omnidim/omnidim-mcp-cloud/issues/104)) ([89204a6](https://github.com/Omnidim/omnidim-mcp-cloud/commit/89204a6ee5496521717bb1148d067ed249449df8))
* refresh tool descriptions from the updated API spec ([#102](https://github.com/Omnidim/omnidim-mcp-cloud/issues/102)) ([c82d26f](https://github.com/Omnidim/omnidim-mcp-cloud/commit/c82d26fe33adaee8aed06633fa3eb3c3cf05dc2b))

## [0.15.0](https://github.com/Omnidim/omnidim-mcp-cloud/compare/v0.14.1...v0.15.0) (2026-11-20)


### Added

* add WhatsApp, agent integration, number rotation and auto-renew tools ([92be256](https://github.com/Omnidim/omnidim-mcp-cloud/commit/92be256c2354ced68254a9f7b9b912baa6ac32f2))


### Fixed

* **dispatcher:** send Idempotency-Key as a header, so WhatsApp sends and campaign launches are accepted ([92be256](https://github.com/Omnidim/omnidim-mcp-cloud/commit/92be256c2354ced68254a9f7b9b912baa6ac32f2))

## [0.14.1](https://github.com/Omnidim/omnidim-mcp-cloud/compare/v0.14.0...v0.14.1) (2026-11-20)


### Fixed

* **ci:** deploy from the release tag so the production environment accepts it ([#95](https://github.com/Omnidim/omnidim-mcp-cloud/issues/95)) ([ced6b1c](https://github.com/Omnidim/omnidim-mcp-cloud/commit/ced6b1cd810070ed22c059e582951f5225583eb9))

## [0.14.0](https://github.com/Omnidim/omnidim-mcp-cloud/compare/v0.13.0...v0.14.0) (2026-11-20)


### Added

* offer a demo call once when the user shows volume, enterprise or white-label need ([ae3e3c3](https://github.com/Omnidim/omnidim-mcp-cloud/commit/ae3e3c3996cd4cc10516e363ddc3f3460cde4fac))
* **procedures:** DEMO_OFFER_RULE offers a demo call once on a sales signal ([fa3aa1b](https://github.com/Omnidim/omnidim-mcp-cloud/commit/fa3aa1b6382d038b3c2e185d95e74d9405c36e0f))


### Fixed

* **annotations:** ask before bulkCallActions resumes paid calls ([#92](https://github.com/Omnidim/omnidim-mcp-cloud/issues/92)) ([be3bff6](https://github.com/Omnidim/omnidim-mcp-cloud/commit/be3bff69f528a9e24ab3337f47ba0688918acaab))
* one demo offer rule shared by instructions, tool text and guide; book only after a yes ([d6693f1](https://github.com/Omnidim/omnidim-mcp-cloud/commit/d6693f1af62ebff19fa645782acebdb923108c60))

## [0.13.0] - 2026-11-19

### Added

- Tools for WhatsApp numbers, templates, conversations, opt-outs and campaigns, for agent integrations, for campaign number rotation, and for phone number auto-renew. Clients that support confirmations ask before a tool sends a WhatsApp message, launches or resumes a campaign, lifts an opt-out, or connects an agent to an outside URL.
- Book a demo with the OmniDimension team from chat: `getDemoQuestions`, `requestDemo` and `bookDemo`, plus a `book_demo` prompt. The assistant asks every booking question, then either offers free times and books the one the user picks, returning the time, join link, attendees and reschedule and cancel links, or tells the user the team will be in touch. Accounts managed by an account administrator get a refusal that points them to that administrator.

### Security

- A reseller's assistant can no longer act on a client account by adding `user_id` to a tool call. The tools never offered it, and the server now drops it before the request.
- The assistant no longer offers to connect Cal.com, so a Cal.com API key never goes into a chat.

### Fixed

- The assistant now suggests Cartesia, the platform default voice, when it sets up an agent, instead of a voice provider the account may not have.

## [0.12.7] - 2026-11-12

### Fixed

- An update call with nothing to change now tells the assistant to pass a field, instead of failing with a server error.

## [0.12.6] - 2026-11-12

### Fixed

- Agents set up through the assistant now use the platform default voice, transcriber and model, which every account has.
- Cloning a voice through the assistant now sends you to the voice cloning page to upload your recording, then the assistant attaches the new voice to your agent.
- Large knowledge-base files go through the files page instead of the chat.

## [0.12.5] - 2026-11-07

### Fixed

- Sign-in from Codex and other clients that check the `iss` parameter now succeeds. Every redirect back to the client (approve, deny and error) carries the issuer.

### Security

- Denying consent now closes the authorization request, so the same consent page cannot be approved afterwards.

## [0.12.4] - 2026-11-05

### Changed

- Every call to the OmniDimension API now carries the request id of the tool call, so one id links an MCP call to the API logs.

## [0.12.3] - 2026-11-05

### Changed

- Errors an AI app hits before a tool runs (bad arguments, unknown tools, expired sign-ins) are now recorded with the app's name, so we can fix the tools and descriptions apps struggle with.

## [0.12.2] - 2026-11-05

### Changed

- Every tool call now records how it ended and how long it took, so failing or slow tools are found and fixed sooner.

## [0.12.1] - 2026-10-26

### Fixed

- Chat apps show the current workflow canvas after an update, instead of a copy they saved from an older version.

## [0.12.0] - 2026-10-26

### Changed

- The workflow canvas now opens only from a new `showWorkflow` tool, so building or editing a workflow no longer posts a canvas at every step.
- The canvas looks like the dashboard's workflow editor: node cards, arrows that follow a node while you drag it, and problem nodes marked in red.
- You can rename a node, change its settings and delete it from the canvas. If Claude changed the same setting while you were typing, the canvas refuses the save instead of overwriting either change.

### Fixed

- The canvas loads even when the chat app hands over the workflow late, and Full screen no longer fails before it loads.
- Moving a node saves, instead of failing with "revision is required".
- The bar under the canvas shows only when something failed, with a one-line message instead of raw JSON.

### Security

- Tools refuse an id that is not a whole number before calling the API.

## [0.11.0] - 2026-10-26

### Added

- Workflow canvas: in clients that support MCP Apps (such as Claude and ChatGPT), reading, creating or editing a workflow shows the draft as a canvas in the chat. You can select a node to see its settings, drag nodes to move them, ask about a node, and open the workflow in the dashboard.

## [0.10.1] - 2026-10-22

### Security

- Require certifi 2026.10.19 or later, which no longer trusts the compromised emSign ECC Root CA - G3.

## [0.10.0] - 2026-10-18

### Added
- Workflow builder: 14 tools to list node types, create, edit, validate, publish, turn on or off, test and delete workflows, and read workflow runs. A new `omnidim://guide/workflows` resource and a `build_workflow` prompt guide the client through building one.
- Post-call action tools (`listPostCallActions`, `addPostCallAction`, `updatePostCallAction`, `deletePostCallAction`) and `listIntegrations` to see which integrations an action can use.
- Cloned-voice tools (list, clone, get, update, delete, get and regenerate a sample) and `getAccountBalance`.

## [0.9.2] - 2026-09-28

### Changed
- Tool calls return about half a second faster.
- Releases no longer interrupt the service: connected clients keep working while a new version rolls out.

## [0.9.1] - 2026-09-12

### Security
- Disconnecting an MCP connection now also deactivates the account credential that was issued with it. Revoking a token previously ended MCP access but left that credential usable. The same cascade runs when a refresh token is replayed and the grant is revoked automatically.

### Fixed
- `searchPhoneNumbers` and `purchasePhoneNumber` accept a `carrier` field, matching the upstream API which now requires it in any region with more than one carrier. A region with one carrier still works without it. The refusal response lists the valid carriers for that region, so a client does not need a separate lookup.

## [0.9.0] - 2026-09-03

### Added

- `createAgent` and `updateAgent` accept a `timezone` field (IANA name, e.g. `Asia/Kolkata`) that sets the local date and time the agent works with during calls. Unset, the account timezone applies.

### Fixed

- The campaign prompt and bulk-campaigns guide described daily calling windows as following the agent's timezone; they follow the window's own `daily_stop_timezone`/`daily_start_timezone`, falling back to the campaign timezone. Both now say so and point at the agent's new `timezone` field for on-call local time.

## [0.8.1] - 2026-08-28

### Changed
- The campaign prompt sticks to the common flow: contact filtering is no longer suggested in the step list (it stays available on createBulkCall for the rare list that needs it).

## [0.8.0] - 2026-08-28

### Added
- Campaign lifecycle tools: startBulkCall, setBulkCallConcurrency, retryBulkCall, addBulkCallContacts (up to 1000 contacts per request), listBulkCallLines (per-contact results with cursor paging), listBulkCallNumbers, addBulkCallNumber, setBulkCallNumberActive (rotation pool), and setBulkCallDailyTimeControl (calling hours). Start, retry, and batch add place real calls and are marked destructive and open-world.
- createBulkCall now supports bot_id, save_as_draft, call_conditions, and rotation.
- A build_outbound_campaign prompt and an omnidim://guide/bulk-campaigns resource covering the campaign rules: the two contact shapes, draft-first building, concurrency arithmetic, rotation, calling hours, and cursor-paged results.

## [0.7.0] - 2026-08-26

### Removed
- Reseller tools are no longer exposed: `listChildOrganizations`, `addUser`, `setUserAccessControl`, `setUserExpiry`, `setChildConcurrency`, `calculateCreditOperation`, `transferCreditsToChild`, `revertCreditsFromChild`, `getResellerCreditLogs`. These act on other people's accounts, several move money, and they are not safe behind a model. Use the REST API or an SDK for them.

### Added
- Phone number provisioning: `searchPhoneNumbers`, `purchasePhoneNumber`, `releasePhoneNumber`. Purchase and release are marked destructive and open-world, so a client can confirm before either runs.
- `provision_agent` and the routing guide now tell you a number can be bought, not only imported, and to confirm the price with the user first.

### Security
- The phone number tools no longer accept `user_id`, the reseller "act on a client" switch. They only ever act on the account the key belongs to, so a reseller key cannot spend a client's balance or release their number from a model.

## [0.6.1] - 2026-08-20

### Changed
- The `createAgent` and `updateAgent` tools now spell out how `transfer_options` behaves on an update: sending the list replaces every saved transfer option, omitting it leaves them as they are, and an empty array clears them. A client that sent a single option to add one could previously drop the rest without warning.
- `voice.provider` and `voice.voice_id` are now marked as a pair. A provider sent on its own is rejected, and a voice id on its own leaves the voice unchanged.

## [0.6.0] - 2026-08-12

### Added
- Agent version-history tools: list, save, diff, restore, rename, and delete an agent's configuration snapshots (generated from the OpenAPI spec).
- `omnidim://guide/agent-versioning` resource and `restore_agent_version` prompt: when to snapshot, how to read a version diff (the `against` modes), and how to safely preview-then-restore an earlier version.

### Fixed
- The agent-version tools and `createSession` now report a display title, and restoring or deleting a version is flagged as destructive so clients confirm before overwriting or removing a saved configuration.
- `restore_agent_version` prompt and the versioning guide describe `createAgentVersion`'s flat argument shape; they showed a `requestBody` wrapper this server rejects.

### Security
- Tool arguments that fill a URL path are percent-encoded. A crafted path argument could previously redirect a tool call to an API endpoint outside the exposed tool set.

## [0.5.1] - 2026-07-12

### Changed

- The `provision_agent` prompt, `omnidim://guide/routing`, and `omnidim://reference/agent-config` now document the playable `speech_speed` range per voice provider. A speed outside the range silently produces no audio (ElevenLabs plays only within 0.7-1.2), so agents created through the API could end up with a mute voice; the guidance steers clients to a safe value.

## [0.5.0] - 2026-06-28

### Added

- Reference resources for building agents: `omnidim://reference/recommended-stack` (which transcriber, voice, and model to choose by caller language), `omnidim://reference/voices` (choosing and verifying a voice), and `omnidim://reference/agent-config` (the createAgent field shape with copy-ready examples).

## [0.4.0] - 2026-06-27

### Added

- Tool annotations. `tools/list` now reports a display title and read-only / destructive / open-world hints per tool. Clients can run read-only tools (listing, fetching) in parallel and prompt for confirmation before destructive actions (deletes) or actions that place real outbound calls (dispatch and bulk campaigns).

### Fixed

- The `provision_agent` prompt and `omnidim://guide/routing` resource now describe the correct argument shape. They told clients to wrap write-tool payloads in a `requestBody` object, but this server takes flat top-level arguments, so a client that followed the guidance built calls the backend rejected.

## [0.3.1] - 2026-06-21

### Changed

- No functional change. Re-releases 0.3.0 through the corrected deploy pipeline.

## [0.3.0] - 2026-06-21

### Added

- MCP prompts and resources. A `provision_agent` prompt walks a client through creating a working voice agent end to end (configure, attach a number, verify it can place a call and speak), an `audit_calls` prompt walks through reviewing and summarizing call logs, and an `omnidim://guide/routing` resource documents which tool to call when and the rules that are easy to get wrong. The server now advertises `prompts` and `resources` alongside `tools`.

## [0.2.8] - 2026-06-11

### Fixed

- `createAgent` now documents its full input. Its request body composes a schema reference with a required-fields clause, and the generator read neither, so the tool exposed no fields and clients had to guess the structure.
- Arguments sent as JSON-encoded strings for object or array fields are decoded before forwarding, so requests from clients that serialize nested values still succeed.
- Model and voice provider choices on `createAgent`/`updateAgent` now match the live catalog. The previous lists offered unavailable models and omitted current ones.

### Changed

- Server errors from the API now return a short, actionable message instead of the raw upstream response body.
- Responses redact credential-bearing fields (tokens, passwords, secrets) instead of only the exact key `api_key`.
- Simulation tools are no longer exposed.
- Connect-time instructions explain how to pick the number a call is placed from.

## [0.2.7] - 2026-05-29

### Fixed

- Agent and simulation tools that take an id in the path (`getAgent`, `updateAgent`, `deleteAgent`, `getSimulation`, `updateSimulation`, `deleteSimulation`) now reach the backend. The id was declared at the path-item level in the spec and the generator dropped it, so requests went to a literal `/agents/{agent_id}` and returned 404.
- `updateAgent` now documents its full input, including the nested `voice` object. Its request body was a schema reference the generator left unresolved, so the tool exposed no fields to set.

## [0.2.6] - 2026-05-27

### Changed

- Telemetry receiver accepts setup-funnel and crash events, including per-tool success and error counts, so install and runtime failures are diagnosable. Older clients keep working unchanged.

## [0.2.5] - 2026-05-25

### Added

- `POST /api/telemetry/event` accepts anonymous usage events from the npm package companion. Strict schema validation; payload structlog-logged to Loki.

## [0.2.4] - 2026-05-25

### Added

- Changelog entry for the telemetry endpoint shipped in 0.2.5.

## [0.2.3] - 2026-05-24

### Fixed

- structlog events are routed through stdlib so the Loki handler receives them.

## [0.2.2] - 2026-05-24

### Added

- Structured logs ship to Loki via `LOKI_PUSH_URL`. Labels configurable through `LOKI_LABELS`.

## [0.2.1] - 2026-05-24

### Security

- Upstream credentials at rest are encrypted with Fernet, keyed off `TOKEN_SIGNING_KEY`.
- Structured log processor strips known-sensitive keys (`api_key`, `access_token`, `refresh_token`, `client_secret`, `code_verifier`, `Authorization`) from every emitted event.

## [0.2.0] - 2026-05-24

### Added

- `POST /mcp` Streamable HTTP transport (JSON-RPC 2.0). Bearer-token gated. Supports `initialize`, `notifications/initialized`, `tools/list`, `tools/call`. Returns `WWW-Authenticate` challenge on 401.
- Auto-generated tool registry from `omnidim-docs/openapi/omnidim.yaml` plus a shared `mcp-config.yaml` exclude list. 49 tools today. Drift sentinel at `app/_generated/.spec.yml`.
- `POST /revoke` (RFC 7009). Revokes the entire grant family.
- `refresh_token` grant on `POST /token` with one-time-use rotation and grant-family revocation on replay.

## [0.1.0] - 2026-05-24

### Added

- OAuth 2.1 authorization server: `POST /register` (Dynamic Client Registration, RFC 7591), `GET /authorize` (PKCE S256 required), `POST /token` (authorization code grant with PKCE verifier). Single-use codes; refresh token issued at exchange. `omnidim:all` is the supported scope.
- Discovery endpoints `/.well-known/oauth-authorization-server` (RFC 8414) and `/.well-known/oauth-protected-resource` (RFC 9728), including `authorization_response_iss_parameter_supported` and one-hour cache headers.
- Strict redirect-URI validation: HTTPS only, with `http://localhost` and `http://127.0.0.1` allowed for loopback. URL fragments and userinfo are rejected.
- Cross-field validation per RFC 7591 §2: `authorization_code` grant requires the `code` response type and vice versa; `refresh_token` grant requires `authorization_code`.
- RFC 7591 §3.2.2 error response shape for the OAuth surface: invalid input returns 400 with `{"error": "...", "error_description": "..."}` instead of the FastAPI default 422 envelope.
- Structured audit log entry on each successful client registration. Never logs the plaintext secret, the hash, or `software_statement`.
- FastAPI application scaffold with structured logging and a lifespan-managed database engine.
- Postgres schema for OAuth clients, authorization codes, access tokens, and refresh tokens. Token columns are hash-only.
- Liveness and readiness probes at `/healthz` and `/readyz`. Readiness logs database failures.
- Request-ID middleware that binds a per-request identifier to log context and reflects it on the response.
- Multi-stage Dockerfile using a venv layout, non-root runtime user, configurable worker count, and built-in healthcheck.
- CI workflow running ruff, mypy, alembic migrations, pytest with coverage, and a container smoke test.
