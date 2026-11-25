# Prompt — character scene

Paste this to an agent. Replace the bracketed parts.

```text
Build a "character scene" hero for [a pet playlist app / a kids reading app / a snack brand].

What I want:
- A powder-blue stage with a cream ground band, a flat sun and two soft hills — no gradients on the
  characters, flat pastel fills with a thick dark outline (3–4 px).
- 5 illustrated characters as **separate generated PNG cutouts with transparent backgrounds** (WebP, under
  40 KB each) — NOT inline SVG, NOT clip-art. One prompt skeleton, five species: same thick dark-brown
  outline weight, same flat pastel palette, front view, full body, no gradients, no shading.
- The headline types on one character at a time (45 ms each) with a block caret, starting 420 ms after load.
- The cast arrives AFTER the headline: each character springs in from 46 px below, scaled to 0.55 and
  tilted -8°, on a stagger of 85 ms per character, with a spring easing
  cubic-bezier(.34, 1.56, .64, 1).
- Then the page keeps breathing: each character bobs on a 4.2 s ease-in-out loop with a NEGATIVE delay
  (var(--i) * -820ms) so they never sync; eyes blink every ~5 s; a few ♪ notes drift upward.
- Hover or focus a character: squash (scale 1.12/0.86), then stretch (0.94/1.08), then settle — a poke.
  Put the bob loop on a wrapper element so the two animations never fight.

Rules:
- Vanilla HTML/CSS/JS only. No libraries, no build step. Raster is allowed only for the character
  cutouts (transparent WebP) — everything else is CSS.
- Animate transform/opacity/filter only. Respect prefers-reduced-motion: print the full headline at once,
  show the cast in place, no loops. Keep the real headline text in aria-label so screen readers never hear
  a half-typed word. Each character is role="img" with an aria-label and tabindex="0".
- Must pass: no horizontal overflow at 390 and 1440, no console errors, LCP under 2.5 s.
```

## Variations to ask for

- **More cast:** 7 characters at 70 ms stagger — never more than 8, the entrance turns to noise.
- **A narrator:** one character stays centre-stage and the others arrive around it.
- **A scene change:** on scroll, the sun sets (translateY on the sun, sky to dusk) and the cast settles.
