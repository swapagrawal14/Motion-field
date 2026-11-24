# Shader background

A full-bleed WebGL fragment shader: layered value noise flows through deep navy, curls into cyan and warms around the pointer. No library, one context, and it stops the moment it leaves the viewport.

Demo: [`index.html`](index.html).

## When to use it

- A hero, a CTA backdrop or a section divider that needs atmosphere without imagery.
- Dark visual systems where a flat gradient would look empty.

Don't use it behind small text without a scrim, and don't run two WebGL contexts on one screen. If the page already has a three.js hero, use a CSS gradient here instead.

## How it works

1. One full-screen triangle (`-1,-1 / 3,-1 / -1,3`) covers the canvas; the fragment shader does everything.
2. Three levels of value noise (`fbm`, 5 octaves) are sampled at different offsets and times to make a flowing field.
3. `smoothstep` maps the field between deep navy, mid blue and a cyan glow; a `exp(-d * 7)` halo tracks the pointer.
4. A single rAF loop draws only while the section is visible and the tab is active. Reduced motion renders one still frame (or falls back to the CSS gradient).

## Knobs

| Knob | Where | Default | Effect |
|---|---|---|---|
| speed | GLSL | `u_t * 0.12` | flow rate; halve it for a calmer field. |
| octaves | `fbm()` | `5` | detail vs cost; 4 is noticeably cheaper. |
| glow | GLSL | `pow(f, 3.0) * 0.5` | how much cyan breaks through. |
| pointer halo | GLSL | `0.10 * exp(-d * 7.0)` | strength and falloff. |
| DPR | JS | `1.5` | cap for retina; lower on low-end devices. |
| `prefers-reduced-motion` | JS/CSS | still frame | one draw or the CSS gradient. |

## Reduced motion

With reduced motion the canvas is hidden and the CSS gradient stands in (or a single frame is rendered if you prefer the shader look). The loop never starts.

## Performance

- One WebGL context, one draw call per frame; no textures, no geometry beyond a triangle.
- Pauses offscreen (IntersectionObserver), on `visibilitychange`, and when paused by the button.
- Device pixel ratio capped at 1.5 and `powerPreference: low-power`; the canvas is `display: none` under reduced motion so it costs nothing.

## Files

- `index.html` – self-contained demo (HTML, CSS and JS inline; Google Fonts via CDN only).
- `prompt.md` – copy-paste prompt for an agent.
