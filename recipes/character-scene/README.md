# Character scene

A cast of illustrated characters takes the stage one at a time, a headline types itself on, and the page
keeps breathing while it waits. This is the **storybook / kids / pets / brand mascot** register — the one
that makes a page feel like a picture book instead of a SaaS landing page.

Open `index.html`. Vanilla HTML/CSS/JS, no build step. The five characters are **generated PNG cutouts**
(`assets/cast/*.webp`, 14–20 KB each, transparent) — not hand-drawn SVG, because a sticker cast drawn in code
reads as clip-art next to an illustrated one.

## What happens

| Beat | Timing | How |
|---|---|---|
| Eyebrow pill pops in | 120 ms | scale + rotate, spring |
| Headline types on | 420 ms → 45 ms/char | `setTimeout` writes one character at a time |
| Cast arrives | 420 ms + `--i` × 85 ms | translateY(46px) scale(.55) rotate(−8°) → none |
| Subtitle rises | 1.5 s | opacity + translateY |
| CTA pops | 1.9 s | opacity + translateY, then a 3D offset shadow on hover |
| Ambient | forever | 4.2 s bob per character, drifting ♪ notes, ground shadow breathing in sync |

## Why it works

- **One beat at a time.** The headline owns the first 1.5 s; the cast arrives after it, on a stagger, so the
  eye is never asked to watch two things on the same frame.
- **Overshoot sells it.** `cubic-bezier(.34, 1.56, .64, 1)` goes past the target and settles — a plain
  `ease-out` looks like a fade, a spring looks like a landing.
- **Negative delays fake variety.** `animation-delay: calc(var(--i) * -820ms)` puts every character at a
  different point in its bob loop on the first frame, so they never move in sync.
- **The cast is a real asset set, not code art.** One illustration prompt, five characters, same outline
  weight and palette. Cut out on flat magenta and keyed to alpha, so the transparent WebP drops onto any
  background. See "Making your own cast" below.
- **It answers the hand.** Hover a character: squash → stretch → settle on its own wrapper (the bob loop
  lives on a different element, so the two animations never fight).

## Knobs

| Knob | Value in the demo | Change it to |
|---|---|---|
| Stagger | `--i * 85ms` | 60–110 ms; over 120 ms reads as slow |
| Spring | `cubic-bezier(.34, 1.56, .64, 1)` | drop the 1.56 to 1.2 for a calmer bounce |
| Type speed | 45 ms/char | 30–60 ms; slower than 80 ms feels broken |
| Bob | 4.2 s, −9 px | 3–6 s, 6–12 px |
| Cast size | `clamp(84px, 15vw, 182px)` | keep the middle character biggest |

## Making your own cast

Generate each character separately with the same prompt skeleton — only the species, colour and one
distinguishing feature change:

```text
Flat vector children's picture-book illustration of ONE cute <frog>, front view, full body, centered,
standing upright. Simple rounded shapes, flat pastel <green> fill (#8fbf6b), <cream belly>, two big round
white eyes with dark pupils and a small happy smile. Uniform thick dark-brown outline (#2a2118) around every
shape. Absolutely flat colors: no gradients, no shading, no texture. No shadow, no ground line, no text, no
props. Isolated on a completely solid flat bright magenta (#FF00FF) background, character not touching the
edges.
```

Then key the magenta out (any chroma-key or `tools/cast_cut.py`), crop to the alpha bounding box, export WebP
at ~2× the display size. Keep each under 40 KB. **Never** mix an SVG character with a generated one — the
outline weight and the shading give it away instantly.

## Reduced motion & performance

Everything is `transform` and `opacity`. `prefers-reduced-motion` prints the whole headline at once,
shows the cast in place, and stops the bob, blink and notes. The bob loops run even when the section is
offscreen — for a long page, gate them with an `IntersectionObserver` (see `recipes/acting-mascot`).

## Accessibility

Each character is a `role="img"` with an `aria-label`, and focusable with `tabindex="0"` so keyboard users
get the same poke reaction. The headline keeps its real text in `aria-label`, so screen readers never hear
a half-typed word.

## Use it for

A kids brand, a pet product, a food delivery mascot, a learning app, a game landing page — anywhere the
product has a face and the page should feel like it is happy to see you.
