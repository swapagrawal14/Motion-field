# The acting mascot

Four poses of one character for `recipes/acting-mascot/`. Transparent WebP, 466×456 each, 14–17 KB,
anchored on a shared feet baseline so a pose change never moves the character.

**Why not SVG:** a rigged vector face can only rotate, scale and swap shapes — it reads as a doll. A drawn
pose reads as acting. These are four separate illustrations of the same character.

## Regenerate

Generate **one pose sheet**, then split it — four separate calls drift in proportions:

```text
Character pose sheet, 2x2 grid on one image, showing the SAME character four times. The character: a small
round mint-green creature with a cream belly, two big round white eyes with dark pupils, a tiny smile, two
short arms and two short legs, drawn as a flat vector children's picture-book illustration with a uniform
thick dark-brown outline (#2a2118) around every shape and absolutely flat colors — no gradients, no shading,
no texture. Top-left: standing idle, arms at sides. Top-right: holding and reading an open cream book with
both hands, looking down at it. Bottom-left: surprised, arms raised up, mouth open in a small O.
Bottom-right: waving one arm high, happy. Each pose full body, centered in its own quadrant, same size and
same proportions in all four. Solid flat bright magenta (#FF00FF) background across the whole image, no
shadows, no ground line, no grid lines, no borders, no text.
```

Split into quadrants, key the magenta (`max(red, blue) − green`, robust to an off key colour), crop each to
its alpha box, then paste onto a shared canvas with the **feet on the same baseline and the feet centred**:

```bash
python3 tools/cast_cut.py raw/sheet.png --out assets/mascot --key FF00FF   # single cutout
```

For the four-up sheet, split first — `tools/cast_cut.py` handles one image at a time.
