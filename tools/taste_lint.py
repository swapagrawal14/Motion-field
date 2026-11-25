#!/usr/bin/env python3
"""Motion Field taste lint — catches the page that is technically fine and creatively empty.

    python3 tools/taste_lint.py http://localhost:8080/ --out qa/taste
    python3 tools/taste_lint.py templates/landing/ --out qa/taste
    python3 tools/taste_lint.py recipes/character-scene/ --json

design_lint.py answers "is it broken?". This answers "is it generic?" — the failure mode that no
screenshot gate catches, and the one that makes a client say "this looks like a template".

Gates (FAIL blocks a score >= 60):
  type      only system / Inter / Roboto-class faces on the page          FAIL
  tokens    no CSS custom properties on :root (no design system)          FAIL
  motion    fewer than 2 distinct animations and no hover/focus/scroll    FAIL
  grid      >= 6 identical siblings (same box, same child count)          WARN
  variety   every animation name is a fade/up/reveal variant              WARN
  depth     no 3D transform, blend mode, filter, gradient or shadow       WARN
  radius    every corner is 0 px (or every one is the browser default)    WARN
  body      fewer than 3 sections / landmarks on the page                 WARN
  copy      >= 3 headings/paragraphs are lorem / TODO / placeholder         WARN

Score = 100 - 25 per FAIL - 8 per WARN. Exit 1 when a gate fails (score < 60).
Calibrated so every template and recipe in this repo scores >= 75 — if one drops below, the repo
got blander, not the tool stricter.

Needs: pip install playwright && python3 -m playwright install chromium
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sys.exit("taste_lint.py needs Playwright: pip install playwright && python3 -m playwright install chromium")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qa import serve_local  # noqa: E402  (same folder)

# Faces the browser picks for you. A page that only ever names these has no type system.
SYSTEM_FACES = {
    "system-ui", "-apple-system", "blinkmacsystemfont", "segoe ui", "roboto", "helvetica", "arial",
    "sans-serif", "serif", "monospace", "ui-sans-serif", "ui-serif", "ui-monospace", "helvetica neue",
    "times new roman", "courier new", "verdana", "tahoma", "trebuchet ms", "georgia", "palatino",
    "garamond", "menlo", "monaco", "consolas", "sfmono-regular", "liberation sans", "dejavavu sans",
}
# The three faces every agent reaches for first. One of them alone is not a type system.
DEFAULT_DISPLAY = {"inter", "inter tight", "roboto", "dm sans", "open sans", "lato", "poppins"}
GENERIC_ANIMS = re.compile(r"fade|up|reveal|in\b|appear|enter|aosl|animate", re.I)

COLLECT_JS = r"""
() => {
  const out = { fonts: new Set(), webfonts: new Set(), tokens: 0, anims: new Set(), hoverRules: 0, transitionEls: 0,
                shadows: 0, gradients: 0, transforms3d: 0, blends: 0, filters: 0,
                radii: new Set(), sections: 0, placeholderHeadings: 0, grids: [] };
  const pushFont = (f) => { if (!f) return; f.split(',').forEach((x) => out.fonts.add(x.trim().replace(/^['"]|['"]$/g, '').toLowerCase())); };
  const seen = new Set();
  const rootCS = getComputedStyle(document.documentElement);
  for (const sheet of document.styleSheets) {
    let rules; try { rules = sheet.cssRules; } catch (e) { continue; }
    const walk = (list) => {
      for (const r of list) {
        if (r.cssRules) walk(r.cssRules);
        if (r.selectorText && /:hover|:focus|:active/.test(r.selectorText)) out.hoverRules++;
        if (r.style) for (const p of r.style) if (p.startsWith('--')) out.tokens++;
        if (r.style && r.style.animationName && r.style.animationName !== 'none') out.anims.add(r.style.animationName);
        if (r.style && r.style.transform && /matrix3d|perspective|rotate[XYZ]|translateZ/.test(r.style.transform)) out.transforms3d++;
      }
    };
    walk(rules);
  }
  out.tokens += [...rootCS].filter((p) => p.startsWith('--')).length;
  document.fonts.forEach((f) => { if (f.family) out.webfonts.add(f.family.replace(/['"]/g, '').toLowerCase()); });

  const els = document.body.querySelectorAll('*');
  for (const el of els) {
    if (el.closest('[aria-hidden="true"]')) continue;
    const cs = getComputedStyle(el);
    if (/^(H[1-6]|P|A|BODY)$/.test(el.tagName)) pushFont(cs.fontFamily);
    if (cs.animationName && cs.animationName !== 'none') out.anims.add(cs.animationName);
    if (cs.transitionProperty !== 'none' && cs.transitionDuration !== '0s') out.transitionEls++;
    if (cs.boxShadow && cs.boxShadow !== 'none') out.shadows++;
    if (cs.backgroundImage.includes('gradient')) out.gradients++;
    if (cs.transform && /matrix3d/.test(cs.transform)) out.transforms3d++;
    if (cs.mixBlendMode && cs.mixBlendMode !== 'normal') out.blends++;
    if (cs.filter && cs.filter !== 'none') out.filters++;
    if (cs.borderRadius && cs.borderRadius !== '0px') out.radii.add(cs.borderTopLeftRadius);
  }
  out.sections = document.querySelectorAll('section, header, footer, nav, main, article, [id]').length;
  document.querySelectorAll('h1,h2,h3,p').forEach((h) => {
    if (/lorem|ipsum|todo|placeholder|your (title|headline)|heading goes|insert (text|copy)/i.test((h.textContent || '').slice(0, 120))) out.placeholderHeadings++;
  });

  // largest group of identical siblings: same box size, same number of children
  const groups = new Map();
  for (const parent of document.body.querySelectorAll('*')) {
    const kids = [...parent.children].filter((k) => k.offsetParent !== null || getComputedStyle(k).position === 'fixed');
    if (kids.length < 3) continue;
    const byShape = new Map();
    for (const k of kids) {
      const r = k.getBoundingClientRect();
      const key = `${Math.round(r.width / 4)}x${Math.round(r.height / 4)}:${k.children.length}`;
      byShape.set(key, (byShape.get(key) || 0) + 1);
    }
    for (const [key, n] of byShape) if (n >= 3) groups.set(key, Math.max(groups.get(key) || 0, n));
  }
  out.grids = [...groups.entries()].map(([k, n]) => ({ shape: k, n }));

  return {
    fonts: [...out.fonts], webfonts: [...out.webfonts], tokens: out.tokens, anims: [...out.anims], hoverRules: out.hoverRules,
    transitionEls: out.transitionEls, shadows: out.shadows, gradients: out.gradients,
    transforms3d: out.transforms3d, blends: out.blends, filters: out.filters,
    radii: [...out.radii], sections: out.sections, placeholderHeadings: out.placeholderHeadings,
    grids: out.grids,
  };
}
"""


def analyse(d: dict) -> tuple[list[dict], int]:
    checks: list[dict] = []

    def add(name: str, level: str, detail: str) -> None:
        checks.append({"gate": name, "level": level, "detail": detail})

    faces = [f for f in d["fonts"] if f]
    web = [f for f in d.get("webfonts", []) if f]
    declared = [f for f in faces if not any(s in f for s in SYSTEM_FACES)]
    custom = sorted(set(web) | set(declared))
    if not custom:
        add("type", "FAIL", "no webfont and only system faces — the browser chose the type")
    elif len(custom) == 1 and custom[0] in DEFAULT_DISPLAY:
        add("type", "WARN", f"one default-family type system ({custom[0]}) — pair a display face or push the contrast")
    else:
        add("type", "PASS", f"{len(custom)} face(s): {', '.join(custom[:3])}")

    if d["tokens"] < 4:
        add("tokens", "FAIL", f"{d['tokens']} custom properties on :root — no design system")
    else:
        add("tokens", "PASS", f"{d['tokens']} custom properties")

    anims = [a for a in d["anims"] if a]
    interactive = d["hoverRules"] + d["transitionEls"]
    if len(anims) < 2 and interactive < 3:
        add("motion", "FAIL", f"{len(anims)} animation(s), {interactive} interactive rule(s) — the page barely moves")
    else:
        add("motion", "PASS", f"{len(anims)} animations, {interactive} interactive rule(s)")

    biggest = max((g["n"] for g in d["grids"]), default=0)
    if biggest >= 6:
        add("grid", "WARN", f"{biggest} identical siblings in one row — vary the size or the content, not just the label")
    elif biggest >= 3:
        add("grid", "PASS", f"{biggest} identical siblings (normal for a card row)")
    else:
        add("grid", "PASS", "no uniform card grid")

    if anims and all(GENERIC_ANIMS.search(a) for a in anims):
        add("variety", "WARN", "every animation is a fade/up/reveal variant — one trick")
    else:
        add("variety", "PASS", f"{len(anims)} distinct animation names")

    depth = d["transforms3d"] + d["blends"] + d["filters"] + (1 if d["gradients"] else 0) + (1 if d["shadows"] else 0)
    if depth == 0:
        add("depth", "WARN", "no 3D, blend, filter, gradient or shadow anywhere")
    else:
        add("depth", "PASS", f"{depth} depth cue(s)")

    if d["radii"] and len(d["radii"]) == 1 and d["radii"][0] == "0px":
        add("radius", "WARN", "every corner is 0 px")
    elif not d["radii"]:
        add("radius", "PASS", "no border-radius used")
    else:
        add("radius", "PASS", f"{len(d['radii'])} distinct radii")

    if d["sections"] < 3:
        add("body", "WARN", f"{d['sections']} landmarks — a thin page")
    else:
        add("body", "PASS", f"{d['sections']} landmarks")

    if d["placeholderHeadings"] >= 3:
        add("copy", "WARN", f"{d['placeholderHeadings']} headings are lorem/placeholder")
    else:
        add("copy", "PASS", "no placeholder headings")

    score = 100
    for c in checks:
        if c["level"] == "FAIL":
            score -= 25
        elif c["level"] == "WARN":
            score -= 8
    return checks, max(0, score)


def main() -> int:
    ap = argparse.ArgumentParser(description="Detect a generic, template-looking page.")
    ap.add_argument("target", help="URL, folder or file")
    ap.add_argument("--out", default="qa/taste", help="output folder (default qa/taste)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--min-score", type=int, default=60, help="fail below this score (default 60)")
    a = ap.parse_args()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    url, httpd = serve_local(a.target)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_context(viewport={"width": 1440, "height": 900}).new_page()
            pg.goto(url, wait_until="networkidle")
            pg.wait_for_timeout(1800)
            d = pg.evaluate(COLLECT_JS)
            b.close()
    finally:
        httpd.shutdown()

    checks, score = analyse(d)
    failed = any(c["level"] == "FAIL" for c in checks) or score < a.min_score

    if a.json:
        print(json.dumps({"target": a.target, "score": score, "checks": checks}, indent=2))
    else:
        print(f"\n  taste  {a.target}  score {score}/100\n")
        for c in checks:
            mark = "PASS" if c["level"] == "PASS" else c["level"]
            print(f"  {mark:<4}  {c['gate']:<8} {c['detail']}")
        print()

    lines = [f"# Taste lint — {a.target}", "", f"**Score: {score}/100** — "
             + ("FAIL (below 60 or a hard gate)" if failed else "pass"), "",
             "| Gate | Level | Detail |", "|---|---|---|"]
    lines += [f"| {c['gate']} | {c['level']} | {c['detail']} |" for c in checks]
    lines += ["", "FAIL = generic by construction. WARN = thin, fix if the section is meant to carry the page.", ""]
    (out / "report.md").write_text("\n".join(lines), encoding="utf-8")
    (out / "report.json").write_text(json.dumps({"target": a.target, "score": score, "checks": checks}, indent=2), encoding="utf-8")
    print(f"Report: {out/'report.md'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
