# Gentleman Video Studio

A private, script-driven video-production interface for the 90-day **How to Become a Gentleman** series.

**Private repository:** this repository is private under the connected GitHub account. No collaborators were added.

## Engine choice

This project integrates with [WanGP](https://github.com/deepbeepmeep/WanGP), an open-source local video-generation application with a browser UI, multiple video model families, and a built-in Showrunner for longer multi-shot productions.

This repository is a separate integration/plugin. It does not contain a copy of WanGP's source code. WanGP is downloaded from its official repository when you set up the runtime. WanGP has its own Community License 2.0; model weights and dependencies retain their own licenses. Read the upstream license before use.

## Controls in Gentleman Studio

- Language: English, Dutch, Spanish, French or German.
- Target duration: 5–120 seconds.
- Theme: Cinematic Gentleman, Old Money, Modern Minimal, Urban Discipline or Custom.
- Aspect ratio: 9:16, 16:9, 1:1 or 4:3.
- Resolution: 480p, 720p or 1080p.
- Script: paste text or upload TXT, Markdown, SRT, DOCX or PDF.
- Video model: choose from text-to-video models available in the installed WanGP runtime.
- Optional spoken narration: Edge TTS, with language-matched voice.
- Captions: an SRT subtitle track is added to the final MP4.

The plugin splits the script into visual beats, asks WanGP to render each shot, then joins the shots and adds captions. It uses photorealistic live-action prompting and avoids stock-image slideshows.

## Important limitations of this first build

- This is a first functional integration, not a fully tested production release. It must be tested on a GPU runtime before relying on it.
- WanGP still needs a supported GPU and the chosen model's weights. A GitHub repository cannot provide free GPU compute.
- Edge TTS is an online speech service. When narration is enabled, the script text is sent to Microsoft's speech endpoint. Turn narration off if the script must remain local.
- The first version creates a sequence of separate generated shots; it does not yet guarantee the same actor/face/outfit across every shot. For stronger character continuity and director-led planning, use WanGP's built-in Showrunner.
- Exact runtime can vary slightly by the selected model's supported frame steps.
- No video is uploaded to YouTube automatically.

## Install in Google Colab

1. Open this private repository while signed in to GitHub.
2. Select **Code → Download ZIP**.
3. In a new Google Colab notebook, upload and extract the ZIP, or clone this repository using your own GitHub authentication.
4. Run:

```bash
git clone --depth 1 https://github.com/deepbeepmeep/WanGP.git /content/WanGP
bash /content/gentleman-video-studio/scripts/install_colab.sh /content/WanGP
```

If you extracted the ZIP to a different folder, replace `/content/gentleman-video-studio` with that folder.

5. Install WanGP according to its official Colab/GPU installation instructions. Then start it from the WanGP folder:

```bash
cd /content/WanGP
python wgp.py --listen --server-port 7860 --profile 4
```

6. Open WanGP in the Colab port preview. Do not use a public Gradio share link for private work. Keep the Colab notebook and runtime private to your account.

After startup, enable **Gentleman Studio** in **Apps & PlugIn Manager** if it is not already enabled.

## Output

Generated files are saved under:

`WanGP/outputs/gentleman_studio/`

The MP4 has a companion JSON file with the selected settings and original script.

## Upstream references

- WanGP source: https://github.com/deepbeepmeep/WanGP
- WanGP plugin guide: https://github.com/deepbeepmeep/WanGP/blob/main/docs/PLUGINS.md
- WanGP API guide: https://github.com/deepbeepmeep/WanGP/blob/main/docs/API.md
- WanGP Showrunner guide: https://github.com/deepbeepmeep/WanGP/blob/main/docs/SHOWRUNNER.md

This is an independent integration and is not an official WanGP project or endorsement.
