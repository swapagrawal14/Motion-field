#!/usr/bin/env python3
"""Motion Field QA runner.

Loads a page in headless Chromium (Playwright) and checks the AGENTS.md QA gates:

  * screenshots at 1440x900 and 390x844 at 0 / 25 / 50 / 75 / 100 % scroll
  * a prefers-reduced-motion pass (both widths, 0 / 50 / 100 %) + text stuck at opacity 0
  * a contact sheet of every screenshot (contact-sheet.png)
  * console errors + uncaught exceptions, failed requests (network errors and HTTP >= 400)
  * horizontal overflow (scrollWidth > innerWidth) with the worst offending elements
  * LCP (measured on a throttled "fast 3G-ish" mobile load unless --no-throttle) and page weight

Usage:
  python3 tools/qa.py http://localhost:8080/ --out qa/
  python3 tools/qa.py recipes/marquee/            # local file or folder: served automatically
  python3 tools/qa.py https://example.com --out qa/ref --no-reduced   # reference teardown screenshots

Writes <out>/report.md, <out>/report.json, <out>/contact-sheet.png and <out>/shots/*.png.
Exit code: 0 when every gate passes (WARN does not fail), 1 when a gate fails, 2 on usage / load errors.

Needs: pip install playwright pillow && python3 -m playwright install chromium
"""
from __future__ import annotations

import argparse
import functools
import http.server
import json
import os
import socket
import sys
import threading
import time
from pathlib import Path
from urllib.parse import quote

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sys.exit("qa.py needs Playwright: pip install playwright && python3 -m playwright install chromium")

VIEWPORTS = {"desktop": (1440, 900), "mobile": (390, 844)}
POSITIONS = [0, 25, 50, 75, 100]
REDUCED_POSITIONS = [0, 50, 100]

LCP_INIT = """
window.__qa = { lcp: 0, cls: 0 };
try {
  new PerformanceObserver(l => { for (const e of l.getEntries()) window.__qa.lcp = e.renderTime || e.loadTime || e.startTime; })
    .observe({ type: 'largest-contentful-paint', buffered: true });
  new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__qa.cls += e.value; })
    .observe({ type: 'layout-shift', buffered: true });
} catch (e) {}
"""

OVERFLOW_JS = """
() => {
  const vw = window.innerWidth, sw = document.documentElement.scrollWidth;
  const out = { innerWidth: vw, scrollWidth: sw, overflow: sw > vw + 1, culprits: [] };
  if (!out.overflow) return out;
  const describe = el => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') +
    (el.classList.length ? '.' + [...el.classList].slice(0, 3).join('.') : '');
  const clipped = el => { for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) {
      const o = getComputedStyle(p).overflowX; if (o === 'hidden' || o === 'clip' || o === 'auto' || o === 'scroll') return true; }
    return false; };
  for (const el of document.body.querySelectorAll('*')) {
    const r = el.getBoundingClientRect();
    if (r.width && (r.right > vw + 1 || r.left < -1) && getComputedStyle(el).position !== 'fixed' && !clipped(el))
      out.culprits.push({ el: describe(el), left: Math.round(r.left), right: Math.round(r.right) });
    if (out.culprits.length >= 8) break;
  }
  return out;
}
"""

HIDDEN_TEXT_JS = """
() => {
  const bad = [];
  for (const el of document.body.querySelectorAll('h1,h2,h3,h4,p,li,a,button,figcaption,blockquote,span,label')) {
    if (!el.textContent.trim() || el.closest('[aria-hidden="true"],[hidden],dialog:not([open]),template,noscript')) continue;
    const r = el.getBoundingClientRect(); if (!r.width || !r.height) continue;
    let op = 1, node = el;
    for (; node && node !== document.documentElement; node = node.parentElement) {
      const cs = getComputedStyle(node);
      if (cs.display === 'none') { op = -1; break; }
      if (cs.visibility === 'hidden') { op = -1; break; }  // deliberately hidden (closed menu, inactive tab)
      // a closed overlay (off-canvas menu, popover) is hidden on purpose
      if (parseFloat(cs.opacity) < 0.05 && (cs.position === 'fixed' || cs.pointerEvents === 'none' && node !== el)) { op = -1; break; }
      op *= parseFloat(cs.opacity);
    }
    if (op >= 0 && op < 0.05) bad.push(el.tagName.toLowerCase() + ': ' + el.textContent.trim().slice(0, 50));
    if (bad.length >= 10) break;
  }
  return bad;
}
"""


# ---------------------------------------------------------------- local serving
def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def serve_local(target: str) -> tuple[str, http.server.ThreadingHTTPServer]:
    """Serve a local file/folder. Root = cwd when the target is inside it (so ../ links work), else its folder."""
    path = Path(target).resolve()
    cwd = Path.cwd().resolve()
    root = cwd if cwd in path.parents or path == cwd else (path if path.is_dir() else path.parent)
    rel = path.relative_to(root).as_posix()
    if path.is_dir():
        rel = (rel + "/") if rel not in ("", ".") else ""
    handler = functools.partial(QuietHandler, directory=str(root))
    port = free_port()
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{port}/{quote(rel)}", httpd


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):  # keep stdout clean
        pass


# ---------------------------------------------------------------- page passes
IGNORE_HOSTS: list = []


def ignored(text: str) -> bool:
    return any(h in text for h in IGNORE_HOSTS)


def attach_listeners(page, issues: dict):
    def on_console(msg):
        loc_url = (msg.location or {}).get("url", "")
        if msg.type == "error" and not ignored(msg.text + loc_url):
            loc = msg.location or {}
            where = f" ({loc.get('url', '')}:{loc.get('lineNumber', '')})" if loc.get("url") else ""
            issues["console"].add(msg.text[:300] + where)

    page.on("console", on_console)
    page.on("pageerror", lambda exc: issues["console"].add(f"Uncaught: {str(exc)[:300]}"))
    page.on("requestfailed", lambda req: issues["requests"].add(f"{req.failure or 'failed'} {req.url[:200]}")
            if not req.url.startswith("data:") and not ignored(req.url) else None)
    page.on("response", lambda res: issues["requests"].add(f"HTTP {res.status} {res.url[:200]}")
            if res.status >= 400 and not ignored(res.url) else None)


def settle(page, wait_ms: int):
    try:
        page.wait_for_load_state("networkidle", timeout=8000)
    except Exception:
        pass
    page.wait_for_timeout(wait_ms)


def scroll_to(page, pct: int, wait_ms: int):
    # Step towards the target so scroll-linked code (ScrollTrigger, IntersectionObserver, Lenis) sees progress.
    page.evaluate("""async (pct) => {
      const max = Math.max(0, document.documentElement.scrollHeight - innerHeight);
      const target = Math.round(max * pct / 100), start = scrollY, steps = 8;
      for (let i = 1; i <= steps; i++) {
        const y = start + (target - start) * i / steps;
        if (window.lenis && window.lenis.scrollTo) window.lenis.scrollTo(y, { immediate: true });
        window.scrollTo({ top: y, behavior: 'instant' });
        await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
      }
    }""", pct)
    page.wait_for_timeout(wait_ms)


def run_pass(browser, url, label, size, positions, out: Path, args, reduced=False) -> dict:
    ctx = browser.new_context(viewport={"width": size[0], "height": size[1]}, device_scale_factor=1,
                              reduced_motion="reduce" if reduced else "no-preference",
                              is_mobile=size[0] < 600, has_touch=size[0] < 600)
    page = ctx.new_page()
    issues = {"console": set(), "requests": set()}
    attach_listeners(page, issues)
    result = {"pass": label, "viewport": f"{size[0]}x{size[1]}", "reduced_motion": reduced, "shots": [],
              "overflow": [], "hidden_text": []}
    try:
        page.goto(url, wait_until="load", timeout=args.timeout * 1000)
    except Exception as exc:
        result["load_error"] = str(exc)[:300]
        ctx.close()
        return result | {"console": sorted(issues["console"]), "requests": sorted(issues["requests"])}
    settle(page, args.wait)
    for pct in positions:
        scroll_to(page, pct, args.scroll_wait)
        name = f"{label}-{pct:03d}.png"
        page.screenshot(path=str(out / "shots" / name), full_page=False)
        result["shots"].append({"pct": pct, "file": f"shots/{name}"})
        ov = page.evaluate(OVERFLOW_JS)
        if ov["overflow"]:
            result["overflow"].append({"pct": pct} | ov)
        if reduced:
            for t in page.evaluate(HIDDEN_TEXT_JS):
                if t not in result["hidden_text"]:
                    result["hidden_text"].append(t)
    if args.full_page and not reduced:
        page.screenshot(path=str(out / "shots" / f"{label}-full.png"), full_page=True)
    result["console"] = sorted(issues["console"])
    result["requests"] = sorted(issues["requests"])
    ctx.close()
    return result


def measure_load(browser, url, args) -> dict:
    """One clean mobile load: LCP, CLS and transferred bytes (optionally throttled)."""
    w, h = VIEWPORTS["mobile"]
    ctx = browser.new_context(viewport={"width": w, "height": h}, is_mobile=True, has_touch=True,
                              device_scale_factor=2)
    ctx.add_init_script(LCP_INIT)
    page = ctx.new_page()
    cdp = ctx.new_cdp_session(page)
    cdp.send("Network.enable")
    cdp.send("Network.setCacheDisabled", {"cacheDisabled": True})
    if args.throttle:
        cdp.send("Network.emulateNetworkConditions", {
            "offline": False, "latency": 150,
            "downloadThroughput": 1.6 * 1024 * 1024 / 8 * 4,  # ~6.4 Mbps: "fast 3G-ish / slow 4G"
            "uploadThroughput": 750 * 1024 / 8})
        cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
    sizes, kinds = {}, {}
    cdp.on("Network.responseReceived", lambda e: kinds.__setitem__(e["requestId"], e.get("type", "Other")))
    cdp.on("Network.loadingFinished", lambda e: sizes.__setitem__(e["requestId"], e.get("encodedDataLength", 0)))
    t0 = time.time()
    try:
        page.goto(url, wait_until="load", timeout=args.timeout * 1000 * (3 if args.throttle else 1))
    except Exception as exc:
        ctx.close()
        return {"error": str(exc)[:300]}
    load_s = time.time() - t0
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass
    page.wait_for_timeout(1000)
    perf = page.evaluate("() => window.__qa || {}")
    ctx.close()
    by_type = {}
    for rid, n in sizes.items():
        t = kinds.get(rid, "Other")
        by_type[t] = by_type.get(t, 0) + n
    big = sorted(((n, rid) for rid, n in sizes.items()), reverse=True)[:1]
    return {"throttled": args.throttle, "lcp_ms": round(perf.get("lcp", 0)), "cls": round(perf.get("cls", 0), 3),
            "load_event_s": round(load_s, 2), "requests": len(sizes),
            "weight_bytes": sum(sizes.values()), "weight_by_type": dict(sorted(by_type.items(), key=lambda x: -x[1])),
            "largest_bytes": big[0][0] if big else 0}


# ---------------------------------------------------------------- contact sheet
def contact_sheet(passes: list, out: Path):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return None
    cols, thumb_w, pad, label_h = len(POSITIONS), 300, 14, 22
    rows = []
    for p in passes:
        ims = []
        for s in p.get("shots", []):
            im = Image.open(out / s["file"]).convert("RGB")
            ratio = thumb_w / im.width if im.width > im.height else (thumb_w * 0.62) / im.width
            ims.append((s["pct"], im.resize((int(im.width * ratio), int(im.height * ratio)))))
        if ims:
            rows.append((f'{p["pass"]}  {p["viewport"]}{"  reduced-motion" if p["reduced_motion"] else ""}', ims))
    if not rows:
        return None
    width = pad + cols * (thumb_w + pad)
    height = pad + sum(label_h + max(i.height for _, i in ims) + label_h + pad for _, ims in rows)
    sheet = Image.new("RGB", (width, height), (18, 20, 28))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 13)
    except Exception:
        font = ImageFont.load_default()
    y = pad
    for title, ims in rows:
        draw.text((pad, y), title, fill=(230, 235, 245), font=font)
        y += label_h
        for idx, (pct, im) in enumerate(ims):
            x = pad + idx * (thumb_w + pad)
            sheet.paste(im, (x, y))
            draw.rectangle([x - 1, y - 1, x + im.width, y + im.height], outline=(70, 80, 100))
            draw.text((x, y + im.height + 4), f"{pct}%", fill=(150, 160, 180), font=font)
        y += max(i.height for _, i in ims) + label_h + pad
    path = out / "contact-sheet.png"
    sheet.save(path, optimize=True)
    return path


# ---------------------------------------------------------------- report
def kb(n):
    return f"{n / 1024:.0f} KB" if n < 1024 * 1024 else f"{n / 1024 / 1024:.2f} MB"


def build_report(url, passes, load, args) -> tuple[dict, list]:
    console = sorted({c for p in passes for c in p.get("console", [])})
    requests = sorted({r for p in passes for r in p.get("requests", [])})
    overflow = [{"pass": p["pass"], **o} for p in passes for o in p.get("overflow", [])]
    hidden = sorted({t for p in passes for t in p.get("hidden_text", [])})
    load_errors = [f'{p["pass"]}: {p["load_error"]}' for p in passes if p.get("load_error")]
    gates = []

    def gate(name, ok, detail="", warn_only=False):
        gates.append({"gate": name, "ok": ok, "detail": detail, "warn_only": warn_only})

    gate("page loads", not load_errors and not load.get("error"), "; ".join(load_errors) or load.get("error", ""))
    gate("B console clean", not console, f"{len(console)} error(s)")
    gate("B no failed requests", not requests, f"{len(requests)} failed")
    gate("C no horizontal overflow", not overflow,
         ", ".join(dict.fromkeys(f'{o["pass"]}@{o["pct"]}% ({o["scrollWidth"]}>{o["innerWidth"]})' for o in overflow)))
    gate("E reduced motion: no text stuck invisible", not hidden,
         f"{len(hidden)} element(s); check hover-only labels and reveals" if hidden else "", warn_only=True)
    if not load.get("error"):
        lcp = load.get("lcp_ms", 0)
        gate("F LCP < %.1fs%s" % (args.lcp_budget, " (throttled)" if args.throttle else ""),
             0 < lcp < args.lcp_budget * 1000 or lcp == 0, f"{lcp} ms" + (" (no LCP entry)" if lcp == 0 else ""))
        gate("F page weight <= %.1f MB" % args.weight_budget, load["weight_bytes"] <= args.weight_budget * 1024 * 1024,
             kb(load["weight_bytes"]))
    report = {"url": url, "generated": time.strftime("%Y-%m-%d %H:%M:%S"), "ok": all(g["ok"] or g["warn_only"] for g in gates),
              "gates": gates, "console_errors": console, "failed_requests": requests, "overflow": overflow,
              "reduced_motion_hidden_text": hidden, "load": load, "passes": passes}
    return report, gates


def write_markdown(report, out: Path, sheet):
    L = [f"# QA report — {report['url']}", "", f"Generated {report['generated']}. "
         f"**{'ALL GATES PASS' if report['ok'] else 'GATES FAILING'}**", "", "| Gate | Result | Detail |", "|---|---|---|"]
    for g in report["gates"]:
        L.append(f"| {g['gate']} | {'PASS' if g['ok'] else ('WARN' if g['warn_only'] else '**FAIL**')} | {g['detail']} |")
    ld = report["load"]
    if not ld.get("error"):
        L += ["", "## Load (mobile 390x844, DPR 2" + (", throttled ~fast-3G + 4x CPU" if ld["throttled"] else "") + ")", "",
              f"- LCP: {ld['lcp_ms']} ms · CLS: {ld['cls']} · load event: {ld['load_event_s']} s",
              f"- Weight: {kb(ld['weight_bytes'])} over {ld['requests']} requests · largest single response {kb(ld['largest_bytes'])}",
              "- By type: " + ", ".join(f"{k} {kb(v)}" for k, v in ld["weight_by_type"].items())]
    for title, items in (("Console errors", report["console_errors"]), ("Failed requests", report["failed_requests"]),
                         ("Text invisible with reduced motion", report["reduced_motion_hidden_text"])):
        if items:
            L += ["", f"## {title}", ""] + [f"- `{i}`" for i in items]
    if report["overflow"]:
        L += ["", "## Horizontal overflow", ""]
        for o in report["overflow"]:
            cul = "; ".join(f"{c['el']} [{c['left']}→{c['right']}]" for c in o["culprits"]) or "culprit not found"
            L.append(f"- {o['pass']} @ {o['pct']}%: scrollWidth {o['scrollWidth']} > {o['innerWidth']} — {cul}")
    L += ["", "## Screenshots", ""]
    if sheet:
        L.append(f"Contact sheet: `{sheet.name}` (open it and look: gates A, D, G are visual).")
    for p in report["passes"]:
        L.append(f"- {p['pass']} {p['viewport']}{' reduced' if p['reduced_motion'] else ''}: " +
                 ", ".join(s["file"] for s in p.get("shots", [])))
    (out / "report.md").write_text("\n".join(L) + "\n")


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Screenshot + QA gate runner for Motion Field pages.",
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__.split("Usage:")[1])
    ap.add_argument("target", help="URL (http://localhost:8080/) or a local .html file / folder (served automatically)")
    ap.add_argument("--out", default="qa", help="output folder (default: qa/)")
    ap.add_argument("--only", choices=["desktop", "mobile"], help="run one viewport only")
    ap.add_argument("--no-reduced", action="store_true", help="skip the prefers-reduced-motion pass")
    ap.add_argument("--no-throttle", dest="throttle", action="store_false", help="measure LCP without network/CPU throttling")
    ap.add_argument("--ignore-host", action="append", default=[], metavar="HOST",
                    help="ignore console errors / failed requests mentioning HOST (repeatable), e.g. a CDN your sandbox blocks")
    ap.add_argument("--full-page", action="store_true", help="also save a full-page screenshot per viewport")
    ap.add_argument("--wait", type=int, default=1200, help="ms to wait after load before screenshots (default 1200)")
    ap.add_argument("--scroll-wait", type=int, default=700, help="ms to wait after each scroll step (default 700)")
    ap.add_argument("--timeout", type=int, default=30, help="navigation timeout in seconds (default 30)")
    ap.add_argument("--lcp-budget", type=float, default=2.5, help="LCP budget in seconds (default 2.5)")
    ap.add_argument("--weight-budget", type=float, default=2.5, help="page weight budget in MB (default 2.5)")
    args = ap.parse_args()

    IGNORE_HOSTS.extend(args.ignore_host)
    httpd = None
    url = args.target
    if not url.startswith(("http://", "https://", "file://")):
        if not Path(url).exists():
            ap.error(f"not a URL and not a local path: {url}")
        url, httpd = serve_local(url)

    out = Path(args.out)
    (out / "shots").mkdir(parents=True, exist_ok=True)
    for old in (out / "shots").glob("*.png"):
        old.unlink()

    passes = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        sizes = {k: v for k, v in VIEWPORTS.items() if not args.only or k == args.only}
        for label, size in sizes.items():
            print(f"· {label} {size[0]}x{size[1]}", flush=True)
            passes.append(run_pass(browser, url, label, size, POSITIONS, out, args))
        if not args.no_reduced:
            for label, size in sizes.items():
                print(f"· {label} reduced-motion", flush=True)
                passes.append(run_pass(browser, url, f"{label}-reduced", size, REDUCED_POSITIONS, out, args, reduced=True))
        print("· load metrics" + (" (throttled)" if args.throttle else ""), flush=True)
        load = measure_load(browser, url, args)
        browser.close()
    if httpd:
        httpd.shutdown()

    sheet = contact_sheet(passes, out)
    report, gates = build_report(url, passes, load, args)
    (out / "report.json").write_text(json.dumps(report, indent=2))
    write_markdown(report, out, sheet)

    print()
    for g in gates:
        print(f"  {'PASS' if g['ok'] else ('WARN' if g['warn_only'] else 'FAIL')}  {g['gate']}  {g['detail']}")
    print(f"\n{'All gates pass.' if report['ok'] else 'Gates failing.'}  Report: {out / 'report.md'}"
          + (f"  Contact sheet: {sheet}" if sheet else ""))
    if any(p.get("load_error") for p in passes) or load.get("error"):
        sys.exit(2)
    sys.exit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
