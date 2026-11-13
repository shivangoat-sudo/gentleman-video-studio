# Gentleman Video Studio

A private web application for creating AI videos with open video models, designed around WanGP as the generation engine.

## Project status

The repository now includes a conventional **Vite + React web application** at its root. This makes it a recognizable web-app project for Google AI Studio and Netlify, while preserving the existing WanGP plugin integration under `plugins/`.

**Important:** the current web interface is a frontend shell. Video generation, authentication, private GPU-worker connection and YouTube OAuth are not yet enabled. The API deliberately returns a clear 503 response until those systems are implemented. Do not deploy this publicly as a private service until authentication is configured.

## Web app controls

- Prompt and optional script
- Script file selection: TXT, Markdown, SRT, DOCX or PDF
- Language: English, Dutch, Spanish, French or German
- Duration: 10–300 seconds
- Aspect ratio: 9:16, 16:9, 1:1 or 4:3
- Resolution: 480p, 720p or 1080p
- Visual styles: Photorealistic, Cinematic, Old Money, Documentary, Commercial, Modern Minimal, Anime or Custom
- Optional voice-over, captions and music
- Optional start and end reference images
- Planned video library and YouTube channel sections

## Run locally

Requires Node.js 20 or newer.

```bash
npm install
npm run dev
```

Build for Netlify:

```bash
npm run build
```

Netlify publishes the `dist` directory. See `netlify.toml`.

## Architecture

- Frontend: Vite + React
- Hosting: Netlify
- Generation engine: WanGP on a separate GPU runtime (not Netlify)
- Backend control plane: Netlify Functions
- YouTube: Google OAuth + YouTube Data API, to be implemented

A GitHub repository or Netlify website cannot provide free GPU compute. Free GPU availability is not guaranteed. No paid generation API is part of the design.

## Existing WanGP integration

The independent WanGP plugin remains under `plugins/wan2gp-gentleman-studio/`. It is a prototype and has not yet passed an end-to-end GPU render test. See `docs/ROADMAP.md` and `docs/WEB-APP-PLAN.md`.

## Privacy and security

- Keep the GitHub repository private.
- Configure authentication before exposing the Netlify site.
- Never put Google OAuth client secrets, refresh tokens, WanGP worker tokens or other secrets in frontend code or Vite environment variables prefixed with `VITE_`.
- Do not expose a public Gradio share URL as the production worker endpoint.
- Use a private authenticated worker bridge for all generation requests.
