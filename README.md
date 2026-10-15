# Cinematic Living World

Customizable moving light leaks for video, created by **Queen Mama Moon / Moon Corp**.

Choose up to three colors by name or hex code, or keep the original prismatic default. The agent asks for colors before a fresh application and clarifies ambiguous shades.

## Start with an AI coding assistant

Download this repository using **Code → Download ZIP**, extract it, and give the whole folder to an assistant that can read files and run Python and FFmpeg.

Ask:

> Read SKILL.md and apply this skill fresh to my video. Start by asking me for up to three colors or the default. Preserve my existing animation, words, branding, and audio.

The skill is an instruction package plus executable renderer, not a hosted app. A chat without code execution can read the instructions but cannot render the video. The color question is asked by the assistant following SKILL.md; the command-line renderer consumes the selected colors from JSON.

## Run the renderer directly

Tested with Python 3.12. Install FFmpeg (including ffprobe) on your PATH, then:

```sh
python -m pip install -r requirements.txt
```

Copy `references/light-leak-scene.json` to `scene.json`. Inspect your video and adapt its dimensions, safe edge regions, and protected center before rendering. The supplied example is specifically 1080 × 1920; it does not detect subjects automatically.

Set `prism_colors` to `"default"` or one to three clear color strings, for example:

```json
["#147D64", "#07513E", "#C88F87"]
```

Render a short proof, then the full video:

```sh
python scripts/render.py input.mp4 scene.json preview.mp4 --seconds 12
python scripts/render.py input.mp4 scene.json finished.mp4
```

The default `--effect prism` adds only the moving light leak. Existing background animation stays in the input video. Audio is stream-copied when compatible with MP4.

Advanced: `--effect world` applies the additional environmental recipe. It requires a separately inspected configuration; see `references/scene-contract.md` and `references/example-scene.json`.

## What is included

- SKILL.md: workflow, color clarification, preservation and verification rules.
- scripts/render.py: deterministic compositor.
- requirements.txt: Python dependencies.
- references/: design recipe and scene configuration examples.
- agents/openai.yaml: assistant-facing metadata.

## Verification and limits

The creator approved the visual result on a 40-second portrait video using Emerald, Deep Emerald and Rose Gold. That render retained 1,200 frames, 1080 × 1920 resolution, and an identical compressed audio hash. Protected center pixels were checked before encoding; lossy video encoding introduces small differences afterward.

The packaged prism-only CLI was smoke-tested. Results on other compositions require their own preview and review. The renderer expects constant-frame-rate input. There is no automatic subject tracking, true flower blooming, 3D reconstruction, or watermark removal.

No private production videos, brand artwork, credentials, or paid-course materials are included. This original package does not imply endorsement by 19Keys or Blackmagic Design and does not require DaVinci Resolve.

## Reuse terms

A public software license has not yet been selected. Public availability is not an unrestricted open-source license. Contact Queen Mama Moon / Moon Corp to confirm reuse or redistribution terms.
