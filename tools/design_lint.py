#!/usr/bin/env python3
"""Motion Field design lint — the gates that screenshots cannot see.

    python3 tools/design_lint.py http://localhost:8080/ --out qa/lint
    python3 tools/design_lint.py recipes/marquee/ --out qa/lint-marquee
    python3 tools/design_lint.py templates/landing/ --budget-accent 8

Checks (each is a FAIL unless noted):
  accent      accent-coloured pixels must stay under --budget-accent % of the viewport (default 10)
  pinned      no more than one pinned section visible at a time
  layout      no transition / @keyframes animating top, left, width, height or margin
  duration    no finite transition or animation longer than --max-duration seconds (default 1.4)
  will-change WARN when more than 8 elements declare will-change at once

Writes <out>/report.md + report.json. Exit 1 when a gate fails.
Needs: pip install playwright pillow && python3 -m playwright install chromium
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
    sys.exit("design_lint.py needs Playwright: pip install playwright && python3 -m playwright install chromium")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from qa import serve_local  # noqa: E402  (same folder)

LAYOUT_PROPS = r"(?:top|left|right|bottom|width|height|margin(?:-\w+)?|padding(?:-\w+)?)"
TRANSITION_RE = re.compile(r"transition(?:-property)?\s*:[^;{}]*\b" + LAYOUT_PROPS + r"\b", re.I)
KEYFRAMES_RE = re.compile(r"@keyframes\s+([\w-]+)\s*\{((?:[^{}]|\{[^{}]*\})*)\}", re.I)
PROP_RE = re.compile(r"(?:^|[;{\s])(" + LAYOUT_PROPS + r")\s*:", re.I)

COLLECT_JS = r"""
() => {
  const out = { transitions: [], animations: [], willChange: [], sticky: [] };
  const vh = innerHeight, vw = innerWidth;
  for (const el of document.body.querySelectorAll('*')) {
    const cs = getComputedStyle(el);
    if (cs.transitionProperty && cs.transitionProperty !== 'none' && cs.transitionDuration
        && !el.closest('[aria-hidden="true"]')) {
      out.transitions.push({ prop: cs.transitionProperty, dur: cs.transitionDuration });
    }
    if (cs.animationName && cs.animationName !== 'none') {
      out.animations.push({ name: cs.animationName, dur: cs.animationDuration, count: cs.animationIterationCount });
    }
    if (cs.willChange && cs.willChange !== 'auto') out.willChange.push(el.tagName.toLowerCase() + '.' + (el.className || ''));
    if (cs.position === 'sticky' || cs.position === 'fixed') {
      const r = el.getBoundingClientRect();
      if (r.height >= vh * 0.9 && r.width > vw * 0.5) {
        out.sticky.push({ el: el.tagName.toLowerCase() + '.' + (el.className || ''), h: Math.round(r.height), top: Math.round(r.top) });
      }
    }
  }
  return out;
}
"""

CSS_TEXT_JS = r"""
() => {
  const chunks = [];
  for (const s of document.styleSheets) {
    try { for (const r of s.cssRules) chunks.push(r.cssText); } catch (e) {}
  }
  for (const s of document.querySelectorAll('style')) chunks.push(s.textContent);
  for (const el of document.querySelectorAll('[style]')) chunks.push(el.getAttribute('style'));
  return chunks.join('\n');
}
"""


def parse_seconds(value: str) -> float:
    total = 0.0
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if part.endswith("ms"):
            total = max(total, float(part[:-2]) / 1000)
        elif part.endswith("s"):
            total = max(total, float(part[:-1]))
    return total


def accent_ratio(png: Path, accent: str, tol: int = 46) -> float:
    from PIL import Image
    im = Image.open(png).convert("RGB")
    im.thumbnail((720, 720))
    px = im.load()
    w, h = im.size
    try:
        target = tuple(int(accent[i:i + 2], 16) for i in (1, 3, 5))
    except Exception:
        return 0.0
    hits = total = 0
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            r, g, b = px[x, y]
            total += 1
            if abs(r - target[0]) < tol and abs(g - target[1]) < tol and abs(b - target[2]) < tol:
                hits += 1
    return hits / max(1, total)


def main() -> None:
    ap = argparse.ArgumentParser(description="Design lint for Motion Field pages.")
    ap.add_argument("target", help="URL or local file/folder (served automatically)")
    ap.add_argument("--out", default="qa/lint", help="output folder (default qa/lint)")
    ap.add_argument("--budget-accent", type=float, default=10.0, help="max %% of viewport that may be accent (default 10)")
    ap.add_argument("--max-duration", type=float, default=1.4, help="max finite transition/animation seconds (default 1.4)")
    ap.add_argument("--wait", type=int, default=1200, help="ms to wait after load")
    ap.add_argument("--timeout", type=int, default=30)
    a = ap.parse_args()

    url, httpd = a.target, None
    if not url.startswith(("http://", "https://", "file://")):
        if not Path(url).exists():
            ap.error(f"not a URL and not a local path: {url}")
        url, httpd = serve_local(url)
    out = Path(a.out)
    (out / "shots").mkdir(parents=True, exist_ok=True)

    gates, details = [], {}

    def gate(name, ok, detail="", warn=False):
        gates.append({"gate": name, "ok": bool(ok), "warn_only": warn, "detail": detail})

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1).new_page()
        page.goto(url, wait_until="load", timeout=a.timeout * 1000)
        page.wait_for_timeout(a.wait)
        css = page.evaluate(CSS_TEXT_JS)
        data = page.evaluate(COLLECT_JS)
        accent = page.evaluate("() => getComputedStyle(document.documentElement).getPropertyValue('--accent').trim() || '#3fdcff'")
        shot = out / "shots" / "top.png"
        page.screenshot(path=str(shot))
        browser.close()
    if httpd:
        httpd.shutdown()

    # accent
    ratio = accent_ratio(shot, accent)
    details["accent"] = {"color": accent, "ratio_pct": round(ratio * 100, 2), "budget_pct": a.budget_accent}
    gate("accent", ratio * 100 <= a.budget_accent, f"{ratio*100:.1f}% accent {accent} (budget {a.budget_accent:g}%)")

    # pinned
    sticky = data.get("sticky", [])
    details["sticky"] = sticky
    visible = [s for s in sticky if s["top"] < 900 and s["top"] + s["h"] > 0]
    gate("pinned", len(visible) <= 1, f"{len(visible)} pinned section(s) visible at once" if visible else "0 pinned sections")

    # layout animation
    bad_trans = []
    for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        for m in TRANSITION_RE.finditer(body):
            # progress bars / meters legitimately animate width; everything else should not
            if re.search(r"width|height", m.group(0), re.I) and re.search(r"bar|progress|loader|meter|track|fill", sel, re.I):
                continue
            bad_trans.append(f"{sel.strip()[:48]} → {m.group(0)[:52]}")
    bad_kf = []
    for m in KEYFRAMES_RE.finditer(css):
        props = {p.group(1).lower() for p in PROP_RE.finditer(m.group(2))}
        hit = props & {"top", "left", "right", "bottom", "width", "height", "margin", "padding"}
        if hit:
            bad_kf.append(f"@keyframes {m.group(1)} → {', '.join(sorted(hit))}")
    details["layout_animation"] = {"transitions": bad_trans[:8], "keyframes": bad_kf[:8]}
    gate("layout", not bad_trans and not bad_kf,
         (f"{len(bad_trans)} transition(s), {len(bad_kf)} keyframe(s) animate layout" if (bad_trans or bad_kf) else "no layout properties animated"))

    # duration (skip infinite loops)
    long_trans = [t for t in data["transitions"] if parse_seconds(t["dur"]) > a.max_duration]
    long_anim = [x for x in data["animations"]
                 if parse_seconds(x["dur"]) > a.max_duration and "infinite" not in x["count"]]
    details["duration"] = {"transitions": long_trans[:8], "animations": long_anim[:8], "budget_s": a.max_duration}
    gate("duration", not long_trans and not long_anim,
         (f"{len(long_trans)} transition(s), {len(long_anim)} animation(s) over {a.max_duration}s" if (long_trans or long_anim)
          else f"no finite motion over {a.max_duration}s"))

    # will-change (warn only)
    wc = data.get("willChange", [])
    gate("will-change", len(wc) <= 8, f"{len(wc)} elements declare will-change", warn=True)

    ok = all(g["ok"] for g in gates if not g["warn_only"])
    report = {"url": url, "ok": ok, "gates": gates, "details": details}
    (out / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    L = [f"# Design lint — {url}", "", f"**{'PASS' if ok else 'FAIL'}**", "", "| gate | result | detail |", "|---|---|---|"]
    for g in gates:
        L.append(f"| {g['gate']} | {'PASS' if g['ok'] else ('WARN' if g['warn_only'] else 'FAIL')} | {g['detail']} |")
    L += ["", "## Details", "", "```json", json.dumps(details, indent=2), "```", ""]
    (out / "report.md").write_text("\n".join(L), encoding="utf-8")

    for g in gates:
        print(f"  {'PASS' if g['ok'] else ('WARN' if g['warn_only'] else 'FAIL')}  {g['gate']}  {g['detail']}")
    print(f"\n{'All gates pass.' if ok else 'Gates failing.'}  Report: {out / 'report.md'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
