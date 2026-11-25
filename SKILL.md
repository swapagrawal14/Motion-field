---
name: motion-field-web
description: Build outstanding interactive websites and web apps with purposeful motion (scroll-linked scenes, pinned heroes, horizontal sections, 3D card walls, shaders, three.js objects, micro-interactions, storybook character scenes), one consistent art direction, and hard QA gates for performance, accessibility and taste. Use when someone asks for a "landing page", "portfolio", "website like <reference>", "animated site", "interactive web app", "make it feel premium", or a playful brand with a mascot, kids app or pet product.
author: Swapnil Agrawal (BDS intern)
---

# Motion Field — web motion skill

> **Agents:** start with [AGENTS.md](AGENTS.md) (prerequisites, what to ask first, pipeline, **QA gates**, rules).
> This file is the craft playbook. Building blocks: [recipes/INDEX.md](recipes/INDEX.md). Starters: [templates/](templates/).

## The one rule
**Motion answers the reader.** Things move because the reader scrolled, pointed, hovered or clicked, and the
movement tells them something: where to look, what changed, what is clickable, how far along they are. A page
where every block fades up 30 px on load is not a motion site; it is a slow site.

Why: people remember the moment the page responded to them. Decoration they skip; cause and effect they feel.

## Approach
1. **Steal the system, not the pixels.** From each reference, extract palette, type scale, spacing rhythm, radii,
   imagery style and motion language. Rebuild with those rules and the human's own content.
2. **One art direction, written down** (`DESIGN.md`) before any code: tokens as CSS variables, 3–5 named moves.
   No reference yet? Run `python3 tools/treatments.py --name <slug> --brief "..."` to generate four art
   directions, show the human the three `DESIGN.md` files and wait for a letter. Have a reference?
   `python3 tools/style_ref.py <url-or-screenshot> --out DESIGN.md` reads its palette, type ladder and radii.
3. **Static first, motion second.** Layout and copy must work with zero JS. Motion is a layer on top.
4. **One big moment per screen.** A pinned hero, a horizontal gallery, a 3D wall: pick one per viewport and
   keep everything around it quiet (opacity + short translate, 400–700 ms).
5. **Recipes, not reinvention.** Copy from `recipes/`; each is self-contained vanilla code with a reduced-motion
   path and offscreen pausing already done.

## Motion principles
- **Trigger → response.** Scroll-linked (scrubbed to progress), entrance (once, on enter), pointer (follows with
  lerp 0.08–0.15), click (immediate feedback < 100 ms). Pick deliberately; don't mix on one element.
- **Easing.** Entrances: `cubic-bezier(.2,.8,.2,1)` / `power3.out`. Exits: `power2.in`, shorter. Springs for
  things you can grab. Scrubbed scroll: linear or `none` (the hand is the easing).
- **Durations.** Micro 150–250 ms, UI 300–500 ms, entrances 600–900 ms, hero moments up to 1.4 s. Never block input.
- **Stagger** 40–80 ms per item, max ~8 items; never pop two hero things on the same frame.
- **Depth.** Parallax layers at 3 speeds max (bg 0.2, mid 0.5, fg 1). Real 3D only where it carries the idea.
- **Follow-through.** Things overshoot slightly and settle (magnetic button springs home, card tilt eases back).
- **Respect.** `prefers-reduced-motion` → instant states, no scroll hijack, still images. Touch → no hover-only
  meaning, no pointer parallax. Offscreen → paused.
- **Performance.** Animate `transform`/`opacity`/`filter` only; `will-change` sparingly; one rAF loop; one WebGL
  context per page where possible; DPR ≤ 2.
- **Sound is opt-in.** Muted by default, a visible toggle, one sound at a time, peaks under 0.2. Never autoplay.

## Layout map (sections and the move that fits them)
| Section | Job | Good moves (recipe) |
|---|---|---|
| Hero | promise + one CTA in 3 seconds | pinned hero shrink, scroll-scrub video hero, three.js hero object, shader background, letter stagger, text scramble |
| Logos / proof | trust | infinite marquee (pause on hover) |
| Features | what it does | blur reveal, card tilt, hover pulse, SVG path draw linking steps |
| Showcase / work | show, don't tell | horizontal scroll section, 3D tilted card wall, image hover distortion |
| Story / process | sequence | scroll drift, SVG path draw, pinned steps with progress rail |
| Interactive toy | delight, memorable | pointer parallax, shaders, field cursor |
| Guide / explainer | host the page | character scene (cast entrance + typewriter), acting mascot (4 poses), page transition between chapters |
| Anywhere | feedback you can hear | UI sound kit — muted by default, opt-in toggle |
| Pricing / CTA | decide | magnetic button, hover pulse; keep calm and legible |
| Footer | wrap up | big wordmark with slow parallax |
| Between pages | continuity | page transition |

## Pick the register first (before the palette)
A brief has a temperature. Getting it wrong is the most common failure — a pet app built as a dark glass
SaaS page, or a fintech page built as a sticker book. Match the register, then the tokens.

| If the brief feels… | Register | Palette | Type | Motion | Illustration |
|---|---|---|---|---|---|
| Premium, technical, "trust us" | **A · Midnight** | deep navy + one cyan | tight grotesque, −0.045em | slow lerp, pinned hero, card tilt | 3D glass, low-key light |
| Editorial, human, lots of words | **B · Paper** | off-white + ink + vermilion | serif display, −0.02em | soft reveals, path draws | natural light, muted earth |
| Loud, cultural, poster-like | **C · Pop** | near-black + acid lime | hard grotesque, −0.03em | scrambles, marquees, shaders | hard flash, glossy |
| Playful, young, warm, has a mascot | **D · Sunny** | powder blue + cream + coral | chunky rounded (Baloo 2), −0.02em | spring entrances, typewriter, ambient bob | flat vector, thick outlines |
| Quiet, expensive, few words | **B · Paper**, darker | bone + charcoal | high-contrast serif | almost none, 200–400 ms | no imagery, type only |

Two tests: **would this palette embarrass the brand in a shop window?** and **would a 9-year-old and a CFO
both believe it?** If either answer is no, the register is wrong — not the tokens.

**Playful is a system, not a decoration.** Sunny means: flat fills, one outline weight everywhere, shapes
built from circles and ellipses, motion that overshoots and settles, and copy that talks like a person.
One cartoon sticker on a navy dashboard is the worst of both.

## Art direction cheatsheet
- **Palette:** 1 background, 1 surface, 1 ink, 1 muted, **one** accent (+ optional support). Accent ≤ 10 % of pixels.
- **Type:** one display (bold, tight tracking −0.02 to −0.04em, `clamp()` 40–120 px) + one text family (16–18 px,
  1.5–1.6 line height). Mono for labels if the reference uses it.
- **Imagery:** one prompt core reused for every image ("<subject>, <medium>, <lighting>, <palette>, <composition>"),
  first good image as reference for the rest. No mixed styles.
- **Grid:** 12 columns, max-width 1200–1320 px, section padding `clamp(64px, 10vw, 160px)`.
- **Four treatments, then one.** Before a big build, present four art directions (midnight / paper / pop /
  sunny) and let the human pick. Building all four is waste; building one without a choice is a guess.

## The quality bar (check it before you show anyone)
Six questions. A "no" is a bug, not a taste call.

1. **Would this page survive being screenshotted next to the reference?** Same palette temperature, same
   type contrast, same spacing rhythm. If it reads as "a template with new colours", it failed.
2. **Is there one moment a visitor would describe to a friend?** A pinned hero, a cast that takes the stage,
   a card wall that tilts. If nothing is memorable, nothing is finished.
3. **Does every move have a trigger and a reason?** If you cannot name what the reader did to earn a motion,
   delete the motion.
4. **Does it still work with motion off?** Reduced-motion pass, no JS, keyboard only. Content first.
5. **Is the copy real and specific?** Not "Empower your workflow" but "Playlists that skip the songs your
   dog hates". Specific beats polished, every time.
6. **Would you ship this on your own name?** If you are explaining away a section, cut the section.
7. **Is anything drawn in code that should have been drawn?** A character or illustration assembled from
   `<circle>`/`<path>` is clip-art. Generate it on flat magenta, key it out (`tools/cast_cut.py`), ship a
   transparent WebP. SVG is for icons, charts and stroke paths — not for art.

`python3 tools/taste_lint.py <target>` scores the first five automatically (type, tokens, motion, uniform
grids, placeholder copy). Under 60 means the page would be mistaken for a template — the register is wrong,
not the code.

## Honest limits (tell the human)
- AI images drift; check the set side by side and regenerate outliers.
- Heavy WebGL/three.js costs battery on phones; recipes degrade to a still image on low-power / reduced motion.
- Scroll-jacking styles (full-page snap, pinned everything) hurt usability; recipes avoid them by default.
- Facts, prices and claims must be checked by the human before launch.

## Workflow rules
- Show art direction + first section screenshots before building everything.
- Never deploy or publish in the person's name without asking.
- Credit line exactly as the person specifies (e.g. "Swapnil Agrawal (BDS intern)").
