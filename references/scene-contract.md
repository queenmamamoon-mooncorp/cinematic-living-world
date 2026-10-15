# Scene contract
Provide JSON with source-pixel coordinates:
- size: [width,height], exactly matching the source.
- strip: [top,bottom] containing the environment.
- environment_polygon: polygon points in full-image coordinates, within the strip.
- protected_rectangles: [left,top,right,bottom] rectangles excluded from strip effects.
- water_x, water_y: center of the water effect in the strip.
- flowers: [center_x,center_y,radius_x,radius_y,phase_radians] for each breathing effect.
- glints: [x,y,phase_radians]. Each uses a 34-pixel radius (69-pixel-wide footprint).
- moon_emblem: [x,y], using a 68-pixel radius (137-pixel-wide footprint).
- light_rails: [x,phase_radians]. Light moves vertically between y=300 and height-350, in a 22-pixel radius (45-pixel-wide footprint).
- verify_unchanged: protected rectangles checked every 300 source frames before encoding.

IMPORTANT: glints, moon halo and rails are independent additive branches and bypass the environment mask. Keep their entire patches outside presenter/captions/branding that must remain unchanged. Rail placement requires checking the entire swept path. Omit unwanted glints/rails with empty arrays. The supplied implementation always renders a moon-emblem halo, so use it only when an appropriate safe emblem region exists, or adapt the code to disable that branch.
The example is for a specific 1080 × 1920 portrait layout; it is not a universal face protection system. Coordinate checks do not detect a moving face or hand.

Timing: this compositor assumes constant-frame-rate input and maps the first audio stream only. Inspect timestamps before using VFR source; normalize explicitly or use a timestamp-aware renderer to preserve timing. Check copied audio compatibility with MP4. These checks are the invoking agent’s responsibility.

Prismatic frame light: optional prism_regions entries [left,top,right,bottom,orientation,phase_radians]. Orientation is vertical or horizontal. Each safe rectangle contains a feathered, broad spectral screen blend that travels along the rectangle on a nine-second cycle, with six-second lateral color drift. Explicitly keep rectangles outside the presenter and captions. Set light_rails to [] to replace the tiny traveling dots. Empty or omitted prism_regions disables this treatment.

Palette: prism_colors may be omitted, null or "default" (approved original four bands), or a list of one to three clear names/hex strings. Example: ["navy", "#FFD700", "white"]. Supported hex forms are #RGB and #RRGGBB (six digits without # also accepted). Named colors use Pillow's standard color-name table; common spaces are normalized. Unclear names, malformed values, more than three custom colors, empty lists, and all-black light palettes raise an actionable error. Ask the user; never silently replace them. Only the prism effect uses these colors.

Effect selection: the CLI defaults to --effect prism. In this mode only prism_regions and prism_colors affect pixels; the remaining required scene fields initialize the compositor but do not animate the environment. Use --effect world for the full environment recipe.
