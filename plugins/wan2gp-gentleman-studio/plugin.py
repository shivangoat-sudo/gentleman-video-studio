from __future__ import annotations

import asyncio
from datetime import datetime
import copy
import json
import math
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import gradio as gr
from shared.utils.plugins import WAN2GPPlugin

try:
    import edge_tts
except Exception:
    edge_tts = None

PLUGIN_ID = "GentlemanStudio"
PLUGIN_NAME = "Gentleman Studio"

ASPECTS = {
    "9:16 (Shorts / Reels)": "9:16",
    "16:9 (YouTube)": "16:9",
    "1:1 (Square)": "1:1",
    "4:3": "4:3",
}
RESOLUTIONS = {
    "9:16": {"480p": "480x832", "720p": "720x1280", "1080p": "1088x1920"},
    "16:9": {"480p": "832x480", "720p": "1280x720", "1080p": "1920x1088"},
    "1:1": {"480p": "720x720", "720p": "960x960", "1080p": "1440x1440"},
    "4:3": {"480p": "832x624", "720p": "1104x832", "1080p": "1440x1088"},
}
THEMES = {
    "Cinematic Gentleman": "photorealistic live-action, understated masculine elegance, tailored dark clothing, natural skin texture, restrained color grading, composed body language, premium cinematic cinematography",
    "Old Money": "photorealistic live-action, quiet luxury, classic tailoring, heritage interiors, warm natural light, timeless understated elegance, authentic materials",
    "Modern Minimal": "photorealistic live-action, clean modern architecture, neutral palette, precise composition, natural movement, refined contemporary menswear",
    "Urban Discipline": "photorealistic live-action, sophisticated city streets, purposeful movement, moody natural light, realistic urban details, restrained cinematic contrast",
    "Custom": "",
}
VOICES = {
    "English": "en-US-GuyNeural",
    "Dutch": "nl-NL-MaartenNeural",
    "Spanish": "es-ES-AlvaroNeural",
    "French": "fr-FR-HenriNeural",
    "German": "de-DE-ConradNeural",
}


def read_script(manual_text: str, uploaded_path: str | None) -> str:
    text = (manual_text or "").strip()
    if uploaded_path:
        path = Path(uploaded_path)
        suffix = path.suffix.lower()
        if suffix in {".txt", ".md", ".srt"}:
            uploaded = path.read_text(encoding="utf-8", errors="replace")
        elif suffix == ".docx":
            from docx import Document
            uploaded = "\n".join(p.text for p in Document(str(path)).paragraphs)
        elif suffix == ".pdf":
            from pypdf import PdfReader
            uploaded = "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
        else:
            raise ValueError("Upload a .txt, .md, .srt, .docx or .pdf script.")
        text = uploaded.strip() or text
    if not text:
        raise ValueError("Paste a script or upload a script file first.")
    return text


def split_into_scenes(script: str, total_seconds: int) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", script) if p.strip()]
    source = " ".join(paragraphs) if paragraphs else script
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", source) if s.strip()]
    if not sentences:
        sentences = [source]
    target_count = max(1, math.ceil(total_seconds / 6.5))
    count = min(target_count, len(sentences))
    if count == 1:
        return [source]
    groups = []
    words = [max(1, len(s.split())) for s in sentences]
    total_words = sum(words)
    start = 0
    accumulated = 0
    for group_index in range(count):
        remaining_groups = count - group_index
        if group_index == count - 1:
            end = len(sentences)
        else:
            target_words = total_words * (group_index + 1) / count
            end = start
            while end < len(sentences) - (remaining_groups - 1) and accumulated < target_words:
                accumulated += words[end]
                end += 1
        groups.append(" ".join(sentences[start:end]))
        start = end
    return [g for g in groups if g.strip()]


def srt_time(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    hours, ms = divmod(ms, 3_600_000)
    minutes, ms = divmod(ms, 60_000)
    secs, ms = divmod(ms, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{ms:03}"


def make_srt(script: str, duration: float, destination: Path) -> None:
    parts = [s.strip() for s in re.split(r"(?<=[.!?])\s+", script) if s.strip()]
    if not parts:
        parts = [script]
    weights = [max(1, len(p.split())) for p in parts]
    total = sum(weights)
    cursor = 0.0
    rows = []
    for index, (part, weight) in enumerate(zip(parts, weights), 1):
        end = duration if index == len(parts) else cursor + duration * weight / total
        rows.append(f"{index}\n{srt_time(cursor)} --> {srt_time(end)}\n{part}\n")
        cursor = end
    destination.write_text("\n".join(rows), encoding="utf-8")


async def make_voiceover(script: str, language: str, destination: Path) -> None:
    voice = VOICES.get(language, VOICES["English"])
    communicate = edge_tts.Communicate(script, voice=voice)
    await communicate.save(str(destination))


def run_ffmpeg(args: list[str]) -> None:
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        detail = (result.stderr or result.stdout or "Unknown FFmpeg error")[-2500:]
        raise RuntimeError(f"FFmpeg failed: {detail}")


def make_final_video(clips: list[str], script: str, language: str, duration: int,
                     aspect: str, resolution: str, voiceover: bool) -> str:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg is not installed in this WanGP environment.")
    output_dir = Path.cwd() / "outputs" / "gentleman_studio"
    output_dir.mkdir(parents=True, exist_ok=True)
    width, height = (int(v) for v in resolution.split("x"))
    with tempfile.TemporaryDirectory(prefix="gentleman_studio_") as temp:
        temp_dir = Path(temp)
        concat_file = temp_dir / "clips.txt"
        concat_file.write_text(
            "".join("file '" + str(Path(p).resolve()).replace("'", "'\\''") + "'\n" for p in clips),
            encoding="utf-8",
        )
        silent_video = temp_dir / "picture.mp4"
        run_ffmpeg([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
            "-r", "24", "-t", str(duration), "-an", "-c:v", "libx264", "-preset", "veryfast",
            "-crf", "18", "-pix_fmt", "yuv420p", str(silent_video),
        ])
        subtitles = temp_dir / "captions.srt"
        make_srt(script, duration, subtitles)
        final_path = output_dir / f"gentleman_studio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        if voiceover:
            if edge_tts is None:
                raise RuntimeError("Edge TTS is missing. Install the plugin requirements or disable voiceover.")
            audio = temp_dir / "narration.mp3"
            asyncio.run(make_voiceover(script, language, audio))
            run_ffmpeg([
                "ffmpeg", "-y", "-i", str(silent_video), "-i", str(audio), "-i", str(subtitles),
                "-map", "0:v:0", "-map", "1:a:0", "-map", "2:s:0",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-af", "apad",
                "-c:s", "mov_text", "-t", str(duration), str(final_path),
            ])
        else:
            run_ffmpeg([
                "ffmpeg", "-y", "-i", str(silent_video), "-i", str(subtitles),
                "-map", "0:v:0", "-map", "1:s:0", "-c:v", "copy",
                "-c:s", "mov_text", "-t", str(duration), str(final_path),
            ])
    return str(final_path)


class GentlemanStudioPlugin(WAN2GPPlugin):
    def __init__(self):
        super().__init__()
        self.name = PLUGIN_NAME
        self.version = "0.1.0"
        self.description = "Script-driven realistic short-video production with language, duration, theme and format controls."

    def setup_ui(self):
        self.add_tab(
            tab_id=PLUGIN_ID,
            label=PLUGIN_NAME,
            component_constructor=self.create_config_ui,
        )

    def create_config_ui(self, api_session):
        try:
            definitions = api_session.list_model_defs(main_output="video", inputs="text")
            model_choices = [
                (item.get("name", item.get("model_type", "Video model")), item.get("model_type"))
                for item in definitions
                if item.get("model_type")
            ]
        except Exception:
            model_choices = []
        if not model_choices:
            model_choices = [("LTX-2.3 Distilled (if installed)", "ltx2_22B_distilled")]

        default_model = next(
            (value for label, value in model_choices if "ltx2" in str(value).lower()),
            model_choices[0][1],
        )

        with gr.Blocks() as ui:
            gr.Markdown(
                "# Gentleman Studio\n"
                "Create realistic, faceless video scenes from your script. "
                "The original WanGP engine renders the footage; this panel handles your series settings, narration and captions."
            )
            with gr.Row():
                language = gr.Dropdown(
                    choices=list(VOICES.keys()), value="English", label="Video language"
                )
                duration = gr.Slider(
                    minimum=5, maximum=120, value=25, step=1, label="Final length (seconds)"
                )
            with gr.Row():
                theme = gr.Dropdown(
                    choices=list(THEMES.keys()), value="Cinematic Gentleman", label="Visual theme"
                )
                custom_theme = gr.Textbox(
                    label="Custom theme / visual direction", placeholder="Optional: rainy London streets, navy tailoring..."
                )
            with gr.Row():
                aspect_label = gr.Dropdown(
                    choices=list(ASPECTS.keys()), value="9:16 (Shorts / Reels)", label="Dimensions / aspect ratio"
                )
                resolution = gr.Dropdown(
                    choices=["480p", "720p", "1080p"], value="720p", label="Resolution"
                )
            model = gr.Dropdown(
                choices=model_choices, value=default_model, label="Video model"
            )
            script_file = gr.File(
                label="Upload script (.txt, .md, .srt, .docx, .pdf)",
                file_types=[".txt", ".md", ".srt", ".docx", ".pdf"],
                type="filepath",
            )
            script_text = gr.Textbox(
                label="Script / narration", lines=10,
                placeholder="Paste your complete script here, or upload it above..."
            )
            voiceover = gr.Checkbox(
                value=True,
                label="Generate spoken narration (Edge TTS; sends the script text to Microsoft's online speech service)",
            )
            create = gr.Button("Generate video", variant="primary")
            output = gr.Video(label="Generated video")
            status = gr.Textbox(label="Production status", lines=5, interactive=False)

            def generate(script, upload, lang, seconds, theme_name, custom, aspect_name,
                         quality, model_id, add_voice, progress=gr.Progress(track_tqdm=False)):
                try:
                    full_script = read_script(script, upload)
                    estimated_wpm = len(full_script.split()) * 60 / max(1, float(seconds))
                    if voiceover and estimated_wpm > 185:
                        minimum_seconds = math.ceil(len(full_script.split()) * 60 / 185)
                        raise ValueError(f"This script is too long for {int(seconds)} seconds at a natural speaking pace. Use at least {minimum_seconds} seconds or shorten the script.")
                    aspect = ASPECTS[aspect_name]
                    size = RESOLUTIONS[aspect][quality]
                    scenes = split_into_scenes(full_script, int(seconds))
                    per_scene = float(seconds) / len(scenes)
                    visual_style = THEMES.get(theme_name, THEMES["Cinematic Gentleman"])
                    if theme_name == "Custom" and not (custom or "").strip():
                        raise ValueError("Enter a custom visual direction when Custom theme is selected.")
                    if (custom or "").strip():
                        visual_style = (visual_style + ", " + custom.strip()).strip(", ")
                    tasks = []
                    for index, scene in enumerate(scenes, 1):
                        prompt = (
                            "Photorealistic live-action cinematic footage for a premium men's self-improvement short. "
                            f"Visual direction: {visual_style}. "
                            f"Show this moment naturally: {scene}. "
                            "Keep the subject anonymous and faceless: frame from behind, over the shoulder, or crop above the mouth; never show a recognizable face. "
                            "Use realistic human proportions, believable gestures, natural skin and fabric texture, "
                            "physically plausible motion, controlled camera movement and coherent lighting. "
                            "One continuous cinematic shot. No visible words, captions, logos, watermarks, UI or collage."
                        )
                        settings = copy.deepcopy(api_session.get_default_settings(model_id))
                        settings.update({
                            "model_type": model_id,
                            "prompt": prompt,
                            "resolution": size,
                            "video_length": f"{per_scene:.2f}s",
                            "duration_seconds": per_scene,
                            "force_fps": 24,
                        })
                        tasks.append(settings)

                    progress(0.02, desc=f"Preparing {len(tasks)} shots")
                    job = api_session.submit_manifest(tasks)
                    completed_events = 0
                    try:
                        for event in job.events.iter(timeout=0.2):
                            if event.kind == "progress":
                                data = event.data
                                ratio = float(getattr(data, "progress", 0) or 0) / 100
                                progress(min(0.9, 0.05 + ratio * 0.82), desc=str(getattr(data, "phase", "Rendering scenes")))
                            elif event.kind == "status":
                                progress(min(0.9, 0.08 + completed_events * 0.1), desc=str(getattr(event.data, "text", "Rendering")))
                            elif event.kind == "output":
                                completed_events += 1
                    except Exception:
                        pass
                    result = job.result()
                    if not getattr(result, "success", False):
                        errors = "; ".join(getattr(e, "message", str(e)) for e in getattr(result, "errors", []))
                        raise RuntimeError(errors or "The video model did not complete the render.")
                    clips = [
                        str(p) for p in getattr(result, "generated_files", [])
                        if Path(str(p)).suffix.lower() in {".mp4", ".mov", ".webm", ".mkv"}
                    ]
                    if not clips:
                        raise RuntimeError("WanGP finished but returned no video files.")
                    progress(0.92, desc="Assembling the final video and captions")
                    final = make_final_video(
                        clips, full_script, lang, int(seconds), aspect, size, bool(add_voice)
                    )
                    meta = {
                        "language": lang, "duration_seconds": int(seconds), "theme": theme_name,
                        "custom_theme": custom, "aspect_ratio": aspect, "resolution": size,
                        "model": model_id, "script": full_script, "source_clips": clips,
                        "voiceover": bool(add_voice),
                    }
                    Path(final).with_suffix(".json").write_text(
                        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
                    )
                    progress(1, desc="Ready")
                    return final, f"Completed: {len(clips)} generated shots\nSaved to: {final}"
                except Exception as exc:
                    return None, f"Generation failed: {type(exc).__name__}: {exc}"

            create.click(
                fn=generate,
                inputs=[script_text, script_file, language, duration, theme, custom_theme,
                        aspect_label, resolution, model, voiceover],
                outputs=[output, status],
            )
        return ui
