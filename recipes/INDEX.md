# Recipes index

Each recipe is one folder with a **self-contained `index.html` demo** (open it directly or serve the repo),
a **`README.md`** (what it is, when to use it, knobs, reduced-motion and performance notes) and a
**`prompt.md`** you can paste to an agent to rebuild it in another project.

How to use: pick the section you are building in [SKILL.md's layout map](../SKILL.md#layout-map-sections-and-the-move-that-fits-them),
find the move here, read its README, copy the CSS/JS block from its `index.html` into your page and rename the
tokens to your art direction. **One big moment per screen**; the rest stay quiet.

Every recipe already handles `prefers-reduced-motion`, pauses work offscreen, and animates only
`transform` / `opacity` / `filter`. Check yours with `python3 tools/qa.py recipes/<slug>/`.

Weight: **tiny** < 3 KB JS, **small** < 10 KB, **heavy** = pulls a library. Vanilla unless the deps column says otherwise.

## Scroll-linked & entrances

| Recipe | Best for | Trigger | What it does | Weight | Deps |
|---|---|---|---|---|---|
| [**Scroll drift**](scroll-drift/) · [demo](scroll-drift/index.html) · [prompt](scroll-drift/prompt.md) | Story / chapter break | scroll-linked | rows of type and images slide sideways as the page scrolls down; manifesto lines, proof strips | tiny | none |
| [**Pointer parallax (orbit)**](pointer-parallax/) · [demo](pointer-parallax/index.html) · [prompt](pointer-parallax/prompt.md) | Interactive toy / hero | pointer | bodies at 3 depths follow the pointer with lerp, idle drift on touch | tiny | none |
| [**Soft-focus reveal**](blur-reveal/) · [demo](blur-reveal/index.html) · [prompt](blur-reveal/prompt.md) | Features / any entrance | entrance (once) | blur → clear + short lift when a block enters view | tiny | none |
| [**Letter stagger**](letter-stagger/) · [demo](letter-stagger/index.html) · [prompt](letter-stagger/prompt.md) | Hero / section titles | entrance + hover replay | headline letters ease in one by one, replay on hover | tiny | none |
| [**SVG path draw**](svg-path-draw/) · [demo](svg-path-draw/index.html) · [prompt](svg-path-draw/prompt.md) | Process / story | scroll-linked | a line draws (and retraces) with scroll to connect steps | tiny | none |
| [**Hover pulse**](hover-pulse/) · [demo](hover-pulse/index.html) · [prompt](hover-pulse/prompt.md) | Features / pricing cards | hover + focus | cards lift, glow and pulse a ring on hover and keyboard focus | tiny | none |

## Micro-interactions & backgrounds

| Recipe | Best for | Trigger | What it does | Weight | Deps |
|---|---|---|---|---|---|
| [**Field cursor**](field-cursor/) · [demo](field-cursor/index.html) · [prompt](field-cursor/prompt.md) | Site-wide | pointer | custom ring + dot cursor with a label per target ("View", "Drag"); desktop only | small | none |
| [**Magnetic button**](magnetic-button/) · [demo](magnetic-button/index.html) · [prompt](magnetic-button/prompt.md) | CTA / pricing | pointer | primary CTA pulls toward the pointer and springs home | tiny | none |
| [**Card tilt + glare**](card-tilt/) · [demo](card-tilt/index.html) · [prompt](card-tilt/prompt.md) | Features / showcase | pointer + focus | cards tilt in 3D under the pointer with a moving highlight | tiny | none |
| [**Text scramble (Cipher)**](text-scramble/) · [demo](text-scramble/index.html) · [prompt](text-scramble/prompt.md) | Hero / labels / nav | entrance + hover | characters scramble then resolve into the real word | tiny | none |
| [**WebGL shader background**](shader-background/) · [demo](shader-background/index.html) · [prompt](shader-background/prompt.md) | Hero / CTA backdrop | time (+ pointer) | full-bleed animated gradient/noise behind a hero; pauses offscreen, still frame on reduced motion | small | WebGL (no library) |
| [**UI sound kit**](ui-sound/) · [demo](ui-sound/index.html) · [prompt](ui-sound/prompt.md) | Nav / CTA / forms | hover + click | procedural WebAudio pops, ticks, whooshes and chimes; **muted by default** | tiny | none |
| [**Character scene**](character-scene/) · [demo](character-scene/index.html) · [prompt](character-scene/prompt.md) | Hero / kids / pets / brand mascot | entrance + hover | a cast of illustrated characters takes the stage one by one (spring + 85 ms stagger), typewriter headline, ambient bob + blink, poke reaction on hover | small | none |

## Big moments (one per screen)

| Recipe | Best for | Trigger | What it does | Weight | Deps |
|---|---|---|---|---|---|
| [**Pinned hero shrink**](pinned-hero-shrink/) · [demo](pinned-hero-shrink/index.html) · [prompt](pinned-hero-shrink/prompt.md) | Hero | scroll-linked (pinned) | full-bleed hero media pins, then shrinks into a rounded card as the headline lifts away | small | none |
| [**Horizontal scroll section**](horizontal-scroll/) · [demo](horizontal-scroll/index.html) · [prompt](horizontal-scroll/prompt.md) | Showcase / work | scroll-linked (pinned) | vertical scroll drives a sideways gallery; native swipe row on mobile / reduced motion | small | none |
| [**3D tilted card wall**](card-wall-3d/) · [demo](card-wall-3d/index.html) · [prompt](card-wall-3d/prompt.md) | Showcase / hero backdrop | scroll-linked + pointer | a perspective-tilted wall of preview cards drifting in columns | small–medium (images) | none |
| [**three.js hero object**](threejs-hero/) · [demo](threejs-hero/index.html) · [prompt](threejs-hero/prompt.md) | Hero | time + pointer + scroll | a lit 3D object that turns with the pointer and scroll; CSS fallback | heavy (~150 KB gz three.js) | three.js (CDN/ESM) |
| [**Image hover distortion**](image-hover-distortion/) · [demo](image-hover-distortion/index.html) · [prompt](image-hover-distortion/prompt.md) | Showcase / work list | pointer (hover) | images ripple/displace under the pointer; SVG filter (WebGL upgrade path) | small | SVG filter |
| [**Infinite marquee**](marquee/) · [demo](marquee/index.html) · [prompt](marquee/prompt.md) | Logos / proof | time (pause on hover) | seamless looping strip of logos or words; static row on reduced motion | tiny | none |
| [**Page transition**](page-transition/) · [demo](page-transition/index.html) · [prompt](page-transition/prompt.md) | Between pages | click (navigation) | a wipe covers the old page and reveals the next; View Transitions API with curtain fallback | tiny | none |
| [**Scroll-scrub video hero**](scroll-scrub-hero/) · [demo](scroll-scrub-hero/index.html) · [prompt](scroll-scrub-hero/prompt.md) | Hero | scroll-linked (pinned) | a WebP frame sequence on canvas; scroll position picks the frame (Apple-style) | medium (frames) | none |

## Characters

| Recipe | Best for | Trigger | What it does | Weight | Deps |
|---|---|---|---|---|---|
| [**Acting mascot**](acting-mascot/) · [demo](acting-mascot/index.html) · [prompt](acting-mascot/prompt.md) | Guide / explainer | scroll + buttons | a painted-cutout mascot changes pose per section: idle, read, surprised, wave | small | none |
| [**Expression cast (Chai Chalo)**](expression-cast/) · [demo](expression-cast/index.html) · [prompt](expression-cast/prompt.md) | Hero / brand mascots / storybook sites | time + scroll + hover + click | a cast of cutout characters blinks, sings and gasps by swapping aligned face patches (rigpop-forge packs); kettle-whistle chorus, CTA gasp, pour; directed trailer via promo.py | small (~560 KB art + fonts) | none |

## Pairing guide

- **Landing page:** pinned-hero-shrink *or* shader-background + text-scramble → marquee (proof) → card-tilt / hover-pulse
  features → svg-path-draw process → magnetic-button CTA.
- **Portfolio:** threejs-hero *or* letter-stagger hero → horizontal-scroll or card-wall-3d work → image-hover-distortion
  list → page-transition between case studies → field-cursor site-wide.
- **Product story:** scroll-scrub-hero (turntable) → svg-path-draw (how it works) → acting-mascot as the guide →
  magnetic-button CTA.
- **Never stack two pinned sections back to back**, and keep at most one WebGL context alive per screen.

## Recipe folder contract (for agents adding a recipe)

```text
recipes/<slug>/
  index.html   one file, inline CSS + JS, no build; CDN only when the deps column says so; works from file://
  README.md    # Title · what it is · When to use it · How it works · Knobs table · Reduced motion · Performance
  prompt.md    a standalone prompt that rebuilds the effect in someone else's stack and art direction
```

Add the slug to this index, then run `python3 tools/qa.py recipes/<slug>/ --out qa/<slug>`: zero console errors,
zero overflow at 390 and 1440, nothing stuck invisible with reduced motion.

For frame-sequence recipes, build the frames with `python3 tools/frames.py` (video via ffmpeg, or the built-in
turntable via Playwright) and keep the sequence under ~30 frames.

Crafted by Swapnil Agrawal (BDS intern).
