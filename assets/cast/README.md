# The storybook cast

Five generated character cutouts for `recipes/character-scene/`. Transparent WebP, 14–20 KB each,
460 px on the long side (≈2× the largest display size). **Not** hand-drawn SVG — a sticker cast drawn in
code reads as clip-art next to an illustrated one, so these are illustrations cut out on a flat key.

## Regenerate

One prompt skeleton, only the species / colour / one feature change. Generate each character separately,
**on a solid magenta `#FF00FF` background**, no shadow, no ground:

```text
Flat vector children's picture-book illustration of ONE cute <frog>, front view, full body, centered,
standing upright. Simple rounded shapes, flat pastel <green> fill (#8fbf6b), <cream belly>, two big round
white eyes with dark pupils and a small happy smile. Uniform thick dark-brown outline (#2a2118) around every
shape, about 6px at this size. Absolutely flat colors: no gradients, no shading, no texture, no highlights.
No shadow, no ground line, no text, no props. Isolated on a completely solid flat bright magenta (#FF00FF)
background, character not touching the edges.
```

| File | Species | Fill | Distinguishing feature |
|---|---|---|---|
| `frog.webp` | frog | `#8fb069` + cream belly | two eye bumps, wide smile |
| `bird.webp` | bird | `#8b6fd8` | three-feather tuft, orange beak |
| `cat.webp` | cat | `#e08a4a` | curled tail, whiskers |
| `hamster.webp` | hamster | `#e8c9a0` | chubby cheeks, paws in front |
| `snail.webp` | snail | `#e88ba8` shell on mint body | spiral shell, eye stalks |

## Cut them out

```bash
python3 tools/cast_cut.py raw/*.png --out assets/cast --key FF00FF
```

Keys the magenta, unmixes the anti-aliased edge (no fringe), crops to the alpha box, exports WebP.
Keep each under 40 KB and never mix a generated character with an SVG one — the outline weight and the
shading give it away instantly.
