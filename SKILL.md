---
name: cinematic-living-world
description: Enhance existing video with cinematic lighting, depth, jewel color, and visibly animated environments. Use for a reusable design and motion treatment that preserves the presenter, voice, captions, and brand. Produces a full video with available rendering tools; does not require DaVinci Resolve or build a design studio.
---

# Cinematic Living World
Use this original Queen Mama Moon / Moon Corp creative recipe to turn a static world into a living environment. Apply Align → Design → Develop. Treat cinematic as a visual direction, not a software brand or proof of professional quality.

## Align
Inspect the original master, audio, aspect ratio, duration, caption layout, background assets, and brand rules. Preserve the source and work on a copy. Ask only for missing inputs that block execution.
Record the desired feeling, focal subject, motion hierarchy, and forbidden changes. For presenter footage, preserve likeness, natural skin, hair, expressions, gestures, voice timing, captions, and branding.
Use available production tools. Do not require installation of Resolve, create a studio application, or substitute software tutorials for the requested video.
Keep user media and brand presets separate from the reusable package. Do not assume rights to publish footage or course material.
Read references/design-recipe.md before choosing the treatment.

## Choose light-leak colors
Before the first render for a new recipient/project, ask: "Which colors would you like for the moving light leak? Choose up to three by name or hex code, or say ‘keep the default.’"
For an explicit fresh start or first-use test, ask again unless the user supplies colors in that request. Never treat an assistant-selected default as a user selection.
Skip this question if the user has already supplied colors or chosen the default in the conversation. Keep the approved palette on revisions unless asked to change it.
Accept one, two, or three named colors, #RGB or #RRGGBB values. Use standard named colors only where unambiguous and show the resolved hex values with the render brief. Common spaced names such as "royal blue" are accepted when they map exactly to a standard name.
For unclear shades ("champagne," "our brand blue," "warm gold"), malformed hex values, conflicting references, or more than three colors, ask a short clarification question and wait before rendering. Do not invent a hex value, silently truncate, or fall back to the default after an error. Offer a swatch choice if useful.
If the user selects the default, preserve the approved original four-band prismatic palette exactly. The up-to-three limit applies to custom palettes only.
Write custom choices to scene.prism_colors as a list of strings. Use "default", null, or omit the field to retain the default. The renderer rejects unclear input so the agent can ask the user. An all-black light palette cannot emit visible light; explain and ask for a highlight color.
Apply this palette to the prismatic light leak only. Do not recolor the person's skin, existing art, frame, or other effect branches. Light compositing naturally blends the chosen colors with the underlying image.

## Design
Plan one dominant subject, then supporting light and environmental motion.
Use rich but legible shadows, restrained jewel color, warm highlights, and a coherent light direction. Preserve skin tones. Avoid global haze and heavy smoothing.
Separate background, environment elements, presenter, captions, and frame when layers are available. For flattened masters, define visibly unobstructed regions; never infer hidden layers. Inspect representative frames including the widest gestures before choosing masks.
Map each effect to a visible object and a measurable change in time. Use timed masks or tracked mattes for moving subjects. If a safe effect area is too small, redesign the composition or obtain layers instead of increasing distortion across the person.
Honor the distinction between petal breathing and blooming: scaling/warping a flat flower is breathing; blooming requires independently unfolding petals.
Prioritize visible environmental motion over ornamental additions. Background motion should remain secondary to speaking.

## Develop
Use scripts/render.py as an available deterministic compositor for suitable flattened video. It supports localized contrast, water displacement and traveling reflection light, flower breathing, crystal highlights, moon-emblem halo, moving frame light, and broad prismatic light leaks.
Dependencies: Python, numpy, OpenCV, Pillow, ffmpeg, ffprobe. Check their availability. This renderer assumes a portrait composition with a protected center, a lower environment strip, and decorative rails. Use another composition/render method when these assumptions do not fit.
For a visibly moving light leak, use prism_regions for broad spectral washes across safe frame regions. Disable light_rails when replacing the tiny moving dots. Inspect a proof for washed-out details and excessive white clipping.
Read references/scene-contract.md. Supply a separate scene JSON for each video; never silently reuse pixel coordinates on unrelated footage.
Run:
python scripts/render.py INPUT.mp4 SCENE.json OUTPUT.mp4 --seconds 12
For the full video, omit --seconds. The default --effect prism applies only the moving light leak and preserves existing environmental animation. Use --effect world only when the user requests the additional configured environment treatment.
The compositor uses original source pixels for the subject and stream-copies source audio. Check audio codec compatibility with MP4 before execution; use an explicitly documented audio conversion when required. Do not claim copy preservation if re-encoding was necessary.
Treat example-scene.json as a geometry example only. All glints, halos and rails must be outside protected content; they are not automatically masked by the environment polygon.
For layered blooms, use separate petals and a clean plate, animate each petal pivot, then composite beneath the protected presenter. Generate new assets with the available image-generation tool when appropriate; never claim a hand-coded flat deformation is AI video generation.

## Verification
Render a 10–12 second proof, plus a late-source sample if source geometry changes.
Check normal-speed phone-size playback: can a viewer see the water, light, and petal motion without instructions? Pixel differences alone are not perceptual acceptance.
Check source vs output: face and caption legibility, no matte chatter, warped gestures, duplicate outlines, flashing, or loop jumps. Inspect distinct times and listen for audio sync.
Check protected pixels before encoding and compare decoded output, allowing only codec differences. Verify the full output duration, resolution, frame rate, audio, first/middle/last frames and render completion.
After technical checks, render the requested full duration. Clearly label user visual approval as pending until received; do not deliver only a proof when a full video was requested.
Deliver the finished video and concise notes stating actual effects, compromises, and remaining review. Avoid claims of true bloom, 3D scene reconstruction, or full-body watercolor unless actually implemented.

## Reuse and release
Keep the skill, reusable compositor, dependencies, design recipe, and example configuration together. Keep production media, local source paths, private URLs, private identifiers and credentials out of the public package.
Record what was actually tested. A valid SKILL.md does not prove a pleasing render.
When the user conditions public release on quality approval, retain a private draft until they approve the demonstrated result. Then package and publish only the approved shareable files to a separate public repository; never make an existing private operational repository public.
Credit Queen Mama Moon / Moon Corp for the original recipe. Do not imply endorsement or coauthorship by 19Keys or Blackmagic Design.
