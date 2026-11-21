# Motion Field — an agent skill for outstanding interactive motion websites

> **AI agents: start with [AGENTS.md](AGENTS.md).** It is the whole loop: prerequisites, what to ask the human,
> the build pipeline, the QA gates every page must pass, and the rules. Craft playbook: [SKILL.md](SKILL.md).
> Building blocks: [recipes/INDEX.md](recipes/INDEX.md). Starter pages: [templates/](templates/).

Motion Field turns any coding agent (Claude Code, Codex, Cursor, Gemini CLI, Hark, Copilot…) into a motion
designer that ships. Give it this repo and a brief, and it builds fast, accessible websites where things move
because the reader did something: pinned heroes, horizontal galleries, 3D card walls, shaders, three.js objects,
magnetic buttons. Every move is plain vanilla HTML/CSS/JS with a reduced-motion path and offscreen pausing, and
`tools/qa.py` checks the result before a human ever sees it.

## Use it with any agent

Paste this into your agent (swap the bracketed parts):

```text
Read https://github.com/swapagrawal14/Motion-field — start with AGENTS.md, then SKILL.md and recipes/INDEX.md.
Build me [a landing page for my dental clinic / a portfolio for my 3D work / ...].
Reference I like: [https://example.com] — match its visual system, not my old look.
Follow the pipeline, use the recipes, run tools/qa.py and fix every gate before showing me screenshots.
Don't deploy or publish anything without asking me.
```

Working locally instead? Clone it and point the agent at the folder:

```bash
git clone https://github.com/swapagrawal14/Motion-field.git
cd Motion-field
pip install playwright && playwright install chromium   # for tools/qa.py
python3 -m http.server 8080                             # preview anything in the repo
```

## Repo map

```text
AGENTS.md             agent quickstart: prerequisites, questions to ask, pipeline, QA gates, rules
SKILL.md              craft: motion principles, layout map (section → move), art direction cheatsheet
recipes/INDEX.md      every recipe at a glance: when to use, weight, dependencies
recipes/<name>/       index.html (self-contained live demo) + README.md (when, knobs, a11y/perf) + prompt.md
templates/landing/    polished product landing page built from the recipes
templates/portfolio/  polished creative portfolio built from the recipes
tools/qa.py           Playwright QA runner: screenshots, contact sheet, console/network/overflow/LCP/weight report
index.html, app.js, styles.css, assets/   the Motion Field showcase site (below)
```

## Quick QA

```bash
python3 -m http.server 8080 &
python3 tools/qa.py http://localhost:8080/recipes/magnetic-button/ --out qa/magnetic
# → qa/magnetic/contact-sheet.png, qa/magnetic/report.md, qa/magnetic/report.json
```

Exit code is non-zero when a gate fails (console errors, failed requests, horizontal overflow, LCP or weight
over budget), so agents can loop on it.

---

## Showcase: the Motion Field site

The repo root is also a live showcase: a cinematic, scroll-driven library of motion studies (scroll cues,
reveals, type play, depth, live GPU shaders and micro-interactions), each with a copy-ready AI prompt and plain
vanilla code. Static site, no build step, no framework.

### What's on the page

- **Announcement strip and sticky nav.** Frosted glass on scroll, full-screen menu on mobile, magnetic pill CTA.
- **Pinned cinematic hero.** A looping video tucks into a rounded frame as you scroll while the headline lifts
  away; on desktop the video, copy and a soft light follow the pointer at different depths.
- **Tech marquee.** An infinite strip that pauses on hover.
- **Library.** Fourteen studies with Featured / Popular / Recent tabs, category chips, search (press `/`), tilt
  cards, and a modal per card with an **AI prompt / Code** toggle and copy-to-clipboard.
- **Live lab.** The six founding studies running for real (tide turn, orbit, soft-focus reveal, letters in the
  wind, the long way round, a page with a pulse) plus a playground with a wiggle-energy dial.
- **Components strip.** Ten live micro-interactions (magnetic button, tilt card, text scramble, spring switch…).
- **Shaders strip.** Twelve real-time GPU backgrounds painted from one shared WebGL context, only while visible.
- **Sections and UI strips, workflow rail, stats, FAQ, shader CTA, parallax footer wordmark.**
- Site-wide: reading progress bar, field-marker cursor (desktop only), Lenis smooth scroll with native fallback.

### Accessibility and performance

- `prefers-reduced-motion` turns off smooth scroll, the pinned hero, marquees, the cursor and loops; shaders
  render one still frame.
- Keyboard focus states on every control; the modal is a native `<dialog>`.
- 900 px WebP thumbs, full art only in the modal; the 1.3 MB hero loop pauses off screen.

### Preview

```bash
python3 -m http.server 8080   # then open http://localhost:8080
```

---

Crafted by Swapnil Agrawal (BDS intern).
