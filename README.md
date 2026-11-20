# Motion Field — Cursor Field Notes

A locally reviewable update to Motion Field, keeping its editorial field-guide art direction while adding more hands-on pointer interaction.

## What's interactive

- **Field-marker cursor:** On desktop, an orbiting star marker leaves a small color-seed trail and changes its label/shape as it moves over the hero, study cards, and playground.
- **Hero field:** Pointer movement shifts the video, title, and study sticker at different depths; a soft light follows the pointer, and the main CTA leans toward it.
- **Study specimens:** Cards tilt toward the pointer, catch a moving highlight, and nudge their study stamp. Hover the artwork; click to open a study and inspect its snippet.
- **Touch and accessibility:** Tap-friendly card controls and a short press response work on touchscreens. The custom cursor is desktop-only; reduced-motion preferences tone down or disable the added motion.

## Preview

No build step or package installation is required. From this directory run:

```bash
python3 -m http.server 8080
```

Then open `http://localhost:8080`.

## Files

- `index.html` — page structure and metadata
- `styles.css` — responsive design system and interaction styling
- `app.js` — study data, filters/search, modal/snippet copy, motion playground, and pointer interactions
- `assets/` — existing hero artwork, loop, and study artwork

This revision is local only. It has not been pushed to GitHub or deployed.
