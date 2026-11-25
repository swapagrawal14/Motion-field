# Prompt — expression cast (Chai Chalo)

Paste this to an agent working in the Motion Field repo. Replace the bracketed parts for another brand.

```text
Build "[Chai Chalo]", [a desi chai stall that sings], as recipes/expression-cast/index.html (+ chai.js).
Look: a storybook picture book, not a website template. Flat illustrated cutouts with a thick near-black
outline and blush cheeks, characters BIG and bleeding off the viewport edges and across section seams.
Every section is one flat pastel colour: [marigold hero, mint menu, pink-chai gang, sky chorus, butter
order, cream footer]. Palette [terracotta #c4572f, marigold #f6a71c, cream #fff3df]; one accent
[#d8402e] for CTAs only (under 10 % of any screen).

Type: self-host the fonts. Download the woff2/ttf from github.com/google/fonts (OFL) into assets/fonts/,
subset to Latin (+ the few Devanagari glyphs you use), @font-face with font-display: swap, preload them.
No Google Fonts link. Display: [Titan One] as a sticker (cream fill, .14em ink -webkit-text-stroke,
paint-order: stroke fill, hard ink text-shadow). Text: [Baloo 2]. Check screenshots show the real fonts.

Characters: use the rigpop-forge talk packs in assets/cast-expr/ (one neutral base.webp + face patches
blink / sing / surprised with their rect, bundled in cast.js). NEVER draw characters in SVG. Mount each
<div class="rig" data-char="..."> as .rig > .bob > .act > img.base + img.face.f-<name> placed at its rect
in %, and act by setting data-face. Faces snap (no transition); feather each patch edge with a mask.
Generate extra art in the same style with an image model (cutouts on chroma green, keyed, WebP < 80 KB):
[a stall counter, a cutting-chai glass, marigold toran, steam puff, a pour arc, a music note, a sparkle,
a chai-wala and a customer] — no real people, no logos. Extra characters: generate the neutral, then
edit THAT image per face and run tools/expressions.py build.

Acting (all transform/opacity, nothing finite over 1.4 s):
- Random blinks per character every 2.5–6 s, only while its section is on screen.
- A section scrolling in: its cast hops and goes surprised → sing, 110 ms stagger. The gang "talks"
  (sing/neutral every 150 ms) while speech bubbles pop in with a spring.
- Kettle whistle every ~8 s in the chorus section and on any "Seeti bajao" button: kettle gasps + shakes,
  steam bursts from the spout, lyrics light word by word, the choir sings in a 140 ms wave throwing notes.
- Hover/focus "Ek chai, please": every visible character goes surprised. Submit: the kettle tilts −38°
  around its handle, the pour arc unrolls (scaleY), the kulhad gasps then goes happy with sparkles, a
  toast confirms it was a demo.
- Hero moment: a rolling shutter goes up 0.45 s after load, awning and toran drop, the kettle swings in
  from the top right, the cast pops up behind the counter, then everyone sings once.
- Ambient bob 3.6 s with negative per-character delays; squash on hop.
- Sound muted by default: an "Awaaz" toggle (data-sfx-toggle, assets/ui-sound.js) + a WebAudio whistle.
- Pause animations offscreen (IntersectionObserver class) and on a hidden tab. Reduced motion: no
  shutter, entrances, bob, steam or auto chorus; faces still change on interaction.
- 390 px: re-arrange the characters (still bleeding), don't just shrink them. No horizontal overflow.

Sections carry data-beat="hero|menu|gang|chorus|order|footer" for the trailer. Hinglish microcopy,
warm and playful; prices marked as samples. README ends with exactly:
"Crafted by [Swapnil Agrawal (BDS intern)]."

Gate: python3 tools/qa.py recipes/expression-cast/ --ignore-host fonts.googleapis.com --ignore-host
fonts.gstatic.com exits 0; tools/design_lint.py and tools/taste_lint.py recipes/expression-cast/ pass; no
console errors. Then put a 1280x800 (6 positions) and 390x844 (4) contact sheet beside the reference
and fix whatever looks flatter, emptier or more generic. Twice.

Trailer: recipes/expression-cast/promo.py on tools/trailer.py's Director — cold open on the kettle's face
blinking, title card from the page's own type/colours/cast, the shutter and the chorus live, push in on
characters reacting, CTA hover gasp, click → pour → kulhad happy, end card "Chai Chalo · Motion Field".
Score with tools/sfx.py. Render 16:9 and 9:16, 14–20 s, and check extracted frames.
```
