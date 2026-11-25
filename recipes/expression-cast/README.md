# Expression cast · Chai Chalo

A desi chai stall that sings. Flat storybook cutouts (thick dark outline, blush cheeks) **act**: they blink on
their own, notice you when you scroll in, sing in a staggered wave when Kettle Kaka whistles, all gasp when
you hover "Ek chai, please", and when you click it the kettle tilts and pours into the kulhad, which goes
happy. Pastel colour-block sections, a chunky self-hosted display face, white outlined cards with hard
offset shadows, speech-bubble cards, characters big and bleeding off the viewport and the section seams.

Demo: [`index.html`](index.html) · runtime [`chai.js`](chai.js) · trailer [`promo.py`](promo.py) · prompt [`prompt.md`](prompt.md)

## When to use it

- A brand, menu, kids or pet product, a launch page: anywhere a cast of characters can host the page.
- When you have (or can generate) a character in **one pose** and want it to feel alive without a rig,
  Lottie or a sprite sheet.

## The page

| Section (`data-beat`) | Colour | What happens |
|---|---|---|
| `hero` | marigold + slow sunburst | A rolling shutter goes up (0.45 s after load, 1.1 s), the scalloped awning and marigold toran drop in, Kettle Kaka swings in from the top right, the cast pops up behind the counter, then the kettle whistles and the whole counter sings. Chotu Bhaiya (chai-wala) bleeds off the left, a customer off the right. |
| `menu` | mint | Outlined menu cards, each fronted by its dish (kulhad, cutting glass, kettle peeking in from the card's corner, samosa, jalebi) with sample ₹ stamps, plus an ink combo strip. Samosa Singh peeks in from the right edge when the section arrives. |
| `gang` | pink-chai | Four speech bubbles pop in with a spring while each character "talks" (sing/neutral flap at 150 ms); the characters stand across the seam into the next section. |
| `chorus` | sky | "Kettle ki seeti": every ~8 s while on screen (or on **Seeti bajao**) the kettle gasps and shakes, steam bursts from the spout, the lyrics light word by word and the choir sings left to right, 140 ms apart, throwing notes. |
| `order` | butter | "Ek chai, please?" form. Hover/focus the button: every visible character goes surprised. Submit: the kettle tilts (−38°, transform only), the pour arc unrolls, the kulhad gasps then goes happy with sparkles, a toast confirms (demo, nothing is sent). |
| `footer` | cream | Toran, a row of heads, the credit. |

## How the expression swap works

Each character is a **rigpop-forge talk pack** (`character.rigpop.json`): one neutral `base.webp` on a fixed
canvas, and small face patches (`blink`, `sing`, `surprised`) with their rect on that canvas
(`tools/expressions.py build` makes them by aligning image-model edits of the base to sub-pixel and keeping
only the changed region). `assets/cast-expr/cast.js` bundles the rects so it works from `file://`.

`chai.js` mounts every `<div class="rig" data-char="kulhad">` as

```
.rig (position, size, --ar from the canvas)      <- placement, entrances, tilt
  .bob (infinite 3.6 s bob, negative delay)      <- ambient life, never synced
    .act (hop / shake / pour pivot)              <- one-shot reactions
      img.base + img.face.f-blink / f-sing / f-surprised   <- absolutely placed at their rect, in %
```

and acting is one attribute: `data-face="sing"`. CSS shows the matching patch (`opacity`, no transition, so
the face snaps like a cartoon cut). The body never moves a pixel, so it reads as a face changing, not a
slideshow. Face patches get a 14 % feathered edge mask so a re-compressed patch never shows a seam.

Faces have a priority so moments never fight: blink (1) < scroll reaction (2) < chorus / CTA / pour (3).
Blinks are random per character, 2.5–6 s apart, and only for characters whose section is on screen.

## Knobs

| Knob | Where | Default | Effect |
|---|---|---|---|
| blink interval | `chai.js` `scheduleBlink` | 2.5–6 s random, 140 ms closed | how alive idle characters look |
| chorus cadence | `chai.js` `setInterval(…, 8000)` | 8 s, chorus section only | the auto whistle; also on any `[data-seeti]` button |
| wave stagger | `chai.js` `chorus()` | 140 ms per character, 900 ms sing | the "Mexican wave" of the choir |
| reaction | `chai.js` `react()` | hop + surprised 520 ms → sing 420 ms, 110 ms stagger | what a section does when it scrolls in |
| bob | CSS `--bob` | 3.6 s, −2.4 %, squash .985/1.018 | ambient breathing |
| pour | CSS `.o-kettle.tilt .act`, `.pour` | −38°, 0.6 s spring; arc 0.45 s after 0.3 s | the pay-off |
| shutter | CSS `.shutter`, `chai.js` | 1.1 s, opens 450 ms after load | the hero moment (skipped under reduced motion) |
| palette | `:root` | terracotta / marigold / cream + mint, pink-chai, sky, butter | one flat colour per section |
| accent | `--accent` | `#d8402e` | CTAs only (design lint budget 10 %; it uses ~5 %) |
| type | `@font-face` | Titan One (display) + Baloo 2 (text), self-hosted in `assets/fonts/` | no Google Fonts request |

## Sound

Muted by default. The **Awaaz** toggle (`data-sfx-toggle`, `assets/ui-sound.js`) opts in; then UI blips play
from ui-sound.js and the kettle whistle is a small WebAudio patch in `chai.js` (sine 1.5 → 2.35 kHz glide with
9 Hz vibrato and a harmonic). No audio files.

## Reduced motion, offscreen, hidden tab

- `prefers-reduced-motion`: no shutter, no entrances, no bob, no rays, no steam or notes, no auto chorus.
  Faces still change (they are state, not motion): blink, gasp on CTA hover, happy on pour, sing on **Seeti bajao**.
- Sections only animate while intersecting (`.sec:not(.is-on) * { animation-play-state: paused }`), blinks
  skip offscreen characters, and a hidden tab pauses everything (`html.paused`).
- Characters are `role="img"` with names; pokeable ones are focusable (Enter/Space pokes).

## Mobile (390 px)

Characters are re-arranged, not shrunk in place: the kettle bleeds in smaller from the top right, the
counter is 170 vw wide (bleeds both sides), Chotu Bhaiya peeks from the left, the menu stacks with the
characters still breaking the card tops, the gang becomes a 2 × 2 grid, and the pour stage is zoomed to fit.

## Bring your own rigpop-forge character

```bash
# a pack exported from rigpop-forge (character.rigpop.json + talk/*.png)
python3 tools/expressions.py import-forge path/to/kiko.rigpop-pack --out assets/cast-expr
python3 tools/expressions.py qa assets/cast-expr/kiko
python3 tools/expressions.py bundle assets/cast-expr      # rewrites cast.js (+ weight gate)
```

Then drop `<div class="rig poke" data-char="kiko" style="--w:220px; --i:3"></div>` anywhere: it blinks,
reacts, sings in the chorus and gasps on the CTA with no further code. A pack that lives next to the page
(like `art/chaiwala/`, Chotu Bhaiya, who has no blink because his eyes are closed in a grin) can be added
to the `CAST` map at the top of `chai.js`.

Making a new character from scratch: generate a neutral cutout, then edit that same image for each face
("keep everything identical, change only the face"), and build:

```bash
python3 tools/expressions.py build --id kiko --name "Kiko" --base raw/kiko.png \
  --expr blink=raw/kiko_blink.png --expr sing=raw/kiko_sing.png --expr surprised=raw/kiko_surprised.png \
  --out assets/cast-expr --max 640 --bleed bottom
```

Note: `build` keys a flat magenta background. Inputs that are already transparent (or keyed from chroma
green) come out with an opaque base; re-save the base and patches with their alpha, as was done for
`art/chaiwala/`.

## The trailer

```bash
python3 recipes/expression-cast/promo.py --aspect 16:9 --out chai_reel_16x9.mp4   # 1280x720
python3 recipes/expression-cast/promo.py --aspect 9:16 --out chai_reel_9x16.mp4   # 1080x1920, phone layout
```

A directed piece on `tools/trailer.py`'s `Director`: cold open on Kettle Kaka's face (blink, blink, gasp,
pull back into a whistle), title card built from the page's own awning, toran, rays, type and cast, the live
shutter rolling up and the counter singing, a push-in on the choir, the CTA gasp, the pour, and an end card
"Chai Chalo · Motion Field". Scored with `tools/sfx.py` plus a kettle whistle added in the script.

## Performance

About 560 KB of images and fonts in total (cast ~200 KB, extra art ~270 KB, fonts 45 KB); characters below
the fold are `loading="lazy"`. One IntersectionObserver, no scroll listener, transform/opacity only.

## Files

- `index.html` – the page (HTML + CSS inline).
- `chai.js` – the expression-cast runtime (mount, faces, blinks, reactions, chorus, CTA, pour, whistle).
- `art/` – generated storybook pieces: `counter`, `customer`, `glass`, `marigold`, `steam`, `pour`, `note`,
  `sparkle`, and the `chaiwala/` talk pack. No real people, no brands.
- `promo.py` – the directed trailer.
- `prompt.md` – copy-paste prompt for an agent.
- Uses `assets/cast-expr/` (the five-character cast), `assets/ui-sound.js`, `assets/fonts/` (Titan One and
  Baloo 2, SIL OFL 1.1, licences alongside).

Crafted by Swapnil Agrawal (BDS intern).
