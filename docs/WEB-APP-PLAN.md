# Gentleman Video Studio — Web App Plan

## Current milestone: web application shell

The repository now has a conventional Vite + React entry point so Google AI Studio can treat it as a web application instead of mistaking the root for a WanGP Python plugin.

## Implemented
- Prompt and optional script fields
- Script file selection (TXT, MD, SRT, DOCX, PDF)
- Language, duration (10–300 seconds), aspect ratio and resolution controls
- Visual style presets and custom style text
- Optional voice-over, captions and music switches
- Optional start and end image uploads
- Library and YouTube navigation placeholders
- Netlify build configuration and API placeholder
- No public generation endpoint or embedded credentials

## Required next milestones
1. Configure private user authentication before deploying a public URL.
2. Choose and test a free GPU runtime for WanGP. Free GPU access is not guaranteed and may be time-limited.
3. Implement a private worker bridge from Netlify to WanGP, including job queue, status polling, cancellation and output retrieval.
4. Adapt the existing WanGP plugin generation flow into a documented worker API. Do not assume the current plugin API is already production-tested.
5. Add secure Google OAuth for YouTube upload. Store refresh tokens server-side only.
6. Add object storage for generated videos and reference images; enforce quotas and deletion.
7. Add end-to-end tests for durations, frame references, aspect ratios, audio, subtitles and final MP4 output.

## Architecture
- Frontend: Vite + React, deployable to Netlify.
- Backend: Netlify Functions for authenticated control-plane requests.
- Video worker: WanGP on a separate GPU runtime. Netlify is not a GPU host.
- YouTube: Google OAuth and YouTube Data API, only after user approval.

## Important
The current interface is a frontend shell, not a working video generator. The API intentionally returns HTTP 503 for generation until a private worker and authentication are in place. This avoids exposing an unauthenticated GPU proxy or falsely claiming generation works.
