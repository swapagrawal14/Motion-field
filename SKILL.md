---
name: motion-field-web
description: Build outstanding interactive websites and web apps with purposeful motion (scroll-linked scenes, pinned heroes, horizontal sections, 3D card walls, shaders, three.js objects, micro-interactions), one consistent art direction, and hard QA gates for performance and accessibility. Use when someone asks for a "landing page", "portfolio", "website like <reference>", "animated site", "interactive web app" or "make it feel premium".
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
   No reference yet? Run `python3 tools/treatments.py --name <slug> --brief "..."` to generate three art
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
| Guide / explainer | host the page | acting mascot (4 poses), page transition between chapters |
| Anywhere | feedback you can hear | UI sound kit — muted by default, opt-in toggle |
| Pricing / CTA | decide | magnetic button, hover pulse; keep calm and legible |
| Footer | wrap up | big wordmark with slow parallax |
| Between pages | continuity | page transition |

## Art direction cheatsheet
- **Palette:** 1 background, 1 surface, 1 ink, 1 muted, **one** accent (+ optional support). Accent ≤ 10 % of pixels.
- **Type:** one display (bold, tight tracking −0.02 to −0.04em, `clamp()` 40–120 px) + one text family (16–18 px,
  1.5–1.6 line height). Mono for labels if the reference uses it.
- **Imagery:** one prompt core reused for every image ("<subject>, <medium>, <lighting>, <palette>, <composition>"),
  first good image as reference for the rest. No mixed styles.
- **Grid:** 12 columns, max-width 1200–1320 px, section padding `clamp(64px, 10vw, 160px)`.
- **Three treatments, then one.** Before a big build, present three art directions (midnight / paper / pop) and
  let the human pick. Building all three is waste; building one without a choice is a guess.

## Honest limits (tell the human)
- AI images drift; check the set side by side and regenerate outliers.
- Heavy WebGL/three.js costs battery on phones; recipes degrade to a still image on low-power / reduced motion.
- Scroll-jacking styles (full-page snap, pinned everything) hurt usability; recipes avoid them by default.
- Facts, prices and claims must be checked by the human before launch.

## Workflow rules
- Show art direction + first section screenshots before building everything.
- Never deploy or publish in the person's name without asking.
- Credit line exactly as the person specifies (e.g. "Swapnil Agrawal (BDS intern)").
