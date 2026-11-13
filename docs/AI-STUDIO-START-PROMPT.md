# Google AI Studio — Start Here

Use this repository as an existing Vite + React web application. Do not scaffold a new application over it.

## What this project is

Gentleman Video Studio is a private web app frontend for a free/open-model video production workflow. The intended generation engine is WanGP running separately on a GPU worker. Google AI Studio is used to help develop the web app; it is not the GPU host for WanGP.

## Rules for AI Studio

1. Inspect the existing project before editing anything.
2. Preserve the Vite + React structure and current dark, premium interface.
3. Make small, incremental changes. Do not replace the project with a generic Gemini chat app.
4. Do not move the WanGP plugin into the browser or try to run WanGP inside the AI Studio frontend.
5. Do not add paid video APIs, paid stock footage, or stock-video substitutes.
6. Never put API keys, OAuth client secrets, refresh tokens, or worker credentials in frontend code or variables prefixed with VITE_.
7. Do not enable public Gradio sharing. The worker must be private and authenticated.
8. Keep Netlify as the deployment target. Keep the frontend build command as `npm run build` and publish directory as `dist`.
9. Preserve the user controls already present: prompt, optional script/file, language, duration 10–300 seconds, aspect ratio, resolution, visual style, voice-over/captions/music options, and optional start/end reference images.
10. Do not claim video generation, YouTube upload, authentication, or storage works until each is implemented and tested end-to-end.

## Current state

The UI is a frontend shell. The `/api/generate` endpoint intentionally returns HTTP 503 because the private WanGP worker and authentication are not connected yet. The library and YouTube screens are placeholders.

## First task

Review the existing interface and fix only concrete defects. Then propose a staged implementation plan for:
- private sign-in / access control;
- authenticated Netlify backend;
- a private WanGP worker bridge with job queue, progress, cancellation and output retrieval;
- scene planning and stitching for 10–300 second videos;
- optional voice-over, captions and audio;
- secure Google OAuth and YouTube upload after explicit user approval;
- private video storage and deletion.

Before implementing a new integration, explain the required free-tier limits and whether the integration is actually free. Do not create or deploy paid resources.
