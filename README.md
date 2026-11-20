# Motion Field

**A field guide of web motion studies and prompts.** Motion Field is a cinematic, scroll-driven library of motion studies: scroll cues, reveals, type play, depth, live GPU shaders and micro-interactions. Every piece comes with a copy-ready AI prompt and plain vanilla code.

It's a static site: plain HTML, CSS and JavaScript, no build step and no framework.

## What's on the page

- **Announcement strip and sticky nav.** The nav turns to frosted glass on scroll, opens a full-screen menu on mobile, and has a magnetic pill CTA.
- **Pinned cinematic hero.** The looping video sits full-bleed, then tucks into a rounded frame as you scroll while the headline lifts away and a second line fades in. On desktop the video, copy and a soft light follow the pointer at different depths.
- **Tech marquee.** An infinite strip that pauses on hover.
- **Library at a glance.** Fourteen studies: the six original artworks plus eight live previews (WebGL halftone, aurora, swirl and ripple, a magnetic button, ink line draw, kinetic type, CSS 3D depth stack).
  - **Featured / Popular / Recent** tabs with a sliding indicator.
  - **Category chips** with counts, plus search (press `/`).
  - Cards tilt and catch a highlight under the pointer.
  - A mid-grid studio promo card.
  - Every card opens a modal with an **AI prompt / Code** toggle and copy-to-clipboard. Studies 01 to 06 also link to their live demo.
- **Live lab.** The six founding studies run for real:
  1. *The tide turn*: a band of type and images drifts sideways, linked to scroll.
  2. *Orbit, gently*: pointer-parallax bodies at different depths, with an idle drift on touch.
  3. *Soft-focus reveal*: goes from blur to clear when it enters view, with a replay button.
  4. *Letters in the wind*: a letter-stagger headline that replays on hover.
  5. *The long way round*: an SVG path that draws, and retraces, with scroll.
  6. *A page with a pulse*: a hover and focus breath on cards.
  - **The little playground**: the wiggle-energy dial drives orbit speed, ribbon wiggle and orb bounce. The orbs and light follow the pointer.
- **Components strip.** Ten live mini interactions with filter chips: magnetic button, orbit loader, tilt card, text scramble, spring switch, wave loader, click ripple, spotlight card, sliding tabs and the energy dial.
- **Shaders strip.** Twelve real-time GPU backgrounds (mesh gradient, swirl, halftone, aurora, flow lines and ripple), all painted from a single shared WebGL context and only while on screen. Each one opens to show its fragment shader.
- **Sections and UI strips.** Animated blueprint mockups (hero, pricing, bento, testimonials, CTA, footer; analytics, wallet, player, rings, kanban), each with a copyable prompt.
- **Workflow.** "Pick. Paste. Play." A sticky heading, a progress rail and steps that light up as you scroll.
- **Stats** that count up, an **FAQ** accordion, and a **shader CTA** with a newsletter form. The form is front-end only: it validates and shows a success state, with no backend yet.
- **Footer** with link columns, socials and a parallax wordmark.
- Site-wide: a reading progress bar, the **field-marker cursor** with a colour-seed trail (desktop only; its label changes by context), Lenis smooth scrolling (from a CDN, with a native fallback), and scroll-triggered reveals.

## Accessibility and performance

- `prefers-reduced-motion` turns off smooth scroll, the pinned hero, marquees, the cursor and the loops. Shaders render a single still frame instead.
- Keyboard focus states are on all controls, and the modal is a native `<dialog>`.
- Card images are 900px WebP thumbs and the full artwork loads only in the modal. The hero uses a 1.3 MB web-encoded loop (`assets/hero-loop-web.mp4`) that pauses when off screen.
- Every shader tile shares one WebGL context and renders only while it is visible.

## Preview

```bash
python3 -m http.server 8080
```

Then open `http://localhost:8080`.

## Files

- `index.html`: page structure
- `styles.css`: design system, layouts, live previews, cursor and responsive rules
- `app.js`: library data and prompts, shader engine, filters and tabs, modal and copy, live lab, playground, hero depth, cursor, and scroll choreography
- `assets/`: original hero loop, still and study artwork
  - `assets/thumbs/`: lightweight thumbnails and the hero poster
  - `assets/hero-loop-web.mp4`: compressed hero loop

Crafted by Swapnil Agrawal (BDS intern).
