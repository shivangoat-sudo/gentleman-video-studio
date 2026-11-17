# Google AI Studio processing prompt — Character & Timeline Video Studio

Use this prompt after importing the complete repository root into Google AI Studio. This is an implementation brief for the existing Vite + React application, not a request to replace it with a new project.

## Goal
Upgrade Gentleman Video Studio into a character-reference, timecoded, multi-shot AI video production interface. Preserve the existing visual design, project structure, WanGP integration, and current settings. Do not rebuild from scratch or remove working features.

## Required user controls
1. **Character references:** allow adding multiple named characters. Each character has one or more uploaded reference images, a short visual description, and an optional role. Show previews, allow removal/reordering, validate image types and sizes, and submit the files with the job. Do not treat the opening/ending frame uploads as character references; keep those separate.
2. **Duration:** exact total duration from 10 to 300 seconds, editable as a number in seconds as well as the existing slider. Validate the value and display mm:ss.
3. **Aspect ratio:** retain 9:16, 16:9, 1:1 and 4:3.
4. **Prompt and timeline:** provide a main creative prompt plus a timecoded scene editor. Each scene has start time, end time, visual action, camera direction, location, characters present, and optional spoken dialogue / sound notes. Allow adding, deleting and reordering scenes. Include an “AI structure my prompt” action only if an LLM provider is configured; never silently call a paid API.
5. **Validation:** timeline must start at 0, have no overlaps or gaps unless the user explicitly allows gaps, have positive scene durations, and end at the exact requested duration. Show validation errors before submission.
6. **Output:** retain resolution and language controls. Produce MP4 plus a JSON manifest containing duration, aspect ratio, resolution, scene timecodes, character IDs, prompt, and output file path/URL.

## Generation architecture
- Treat 5 minutes as the **final assembled video duration**, not a single model generation. Generate short clips per scene (model-supported lengths), then concatenate/assemble with FFmpeg. Never claim that Wan/LTX natively generates a continuous 5-minute clip.
- Use the existing WanGP plugin/API as the first generation adapter. Inspect the installed WanGP API and supported model capabilities before coding request fields. Do not invent endpoints, parameters, or model capabilities.
- Pass each scene's relevant character reference images to the generator using the actual supported reference-image mechanism. If the selected model cannot accept multiple references, use a supported character-sheet / reference-preparation workflow or clearly report the limitation; do not pretend identity consistency is guaranteed.
- Maintain continuity by using the previous clip's final frame as the next clip's starting/reference frame when supported. Preserve character IDs, appearance descriptions, wardrobe, location, lighting and style across shots.
- Assemble scene clips in timeline order with FFmpeg; normalize dimensions, frame rate, audio format and aspect ratio before concatenation. Add optional narration, dialogue audio, subtitles and music only when configured. Keep original scene audio where appropriate.
- Add job progress, per-scene status, retry/regenerate controls and clear failure messages. Never report success until the MP4 exists and passes validation.
- Keep generation compute separate from Netlify. Netlify Functions are the control plane only; do not attempt GPU inference inside Netlify.

## Handoff to the existing clipping/publishing tool
Create a provider-neutral export/handoff adapter. On successful render, save the MP4 and a sidecar manifest. Add a configurable destination URL and optional bearer token stored server-side only. If configured, POST the completed MP4 (multipart upload) and manifest to that destination; otherwise expose a download action and a “Send to clipping tool” action that reports “not configured”. Do not guess the user's clipping tool endpoint, OAuth credentials, or API contract. Keep the adapter isolated so the real endpoint can be connected later without rewriting the generator.

## Security and reliability
- Never put API keys, OAuth secrets, bearer tokens or worker credentials in frontend code or VITE_ variables.
- Validate uploads server-side; use safe filenames and bounded file sizes.
- Keep the repository private and do not expose public unauthenticated GPU-worker URLs.
- Do not add paid APIs, subscriptions, or card-required services as dependencies.
- Make the UI honest about free GPU availability: open-source code/models can be free, but hosted GPU compute is not guaranteed to be free.
- Add tests for timeline validation, duration calculation, manifest creation, and handoff failure handling.

## Implementation order
1. Inspect current code and WanGP plugin/API; summarize the actual supported capabilities.
2. Implement character-reference uploads and the timecoded timeline editor in the existing UI.
3. Implement request validation and a typed job/manifest contract.
4. Implement the WanGP scene-generation adapter only against verified API capabilities.
5. Implement FFmpeg assembly and MP4 validation.
6. Implement the configurable handoff adapter to the clipping/publishing tool.
7. Run the production build and tests; fix all errors.

## Non-negotiable
Do not replace real generation with stock footage, placeholder videos, random clips, or fake progress. Do not claim the full pipeline works until an end-to-end render and handoff have been tested. Preserve the existing app and report any missing external credentials or GPU runtime honestly.
