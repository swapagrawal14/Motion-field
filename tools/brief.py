#!/usr/bin/env python3
"""Motion Field brief triage — one line in, a build plan out.

    python3 tools/brief.py --brief "a pet playlist app for dog owners"
    python3 tools/brief.py --brief "fintech dashboard for CFOs" --stack next --out PLAN.md
    python3 tools/brief.py --brief "..." --json

Reads the brief, picks a register (A Midnight / B Paper / C Pop / D Sunny), names the starter
template, shortlists recipes per section, picks the one big moment, and lists the failure modes
for that register. Deterministic — no model, no network, so the same brief always gets the same
plan and you can diff it against what you actually built.

Exit 0 always (it is a planner, not a gate). Add --ask to get the three questions to send the human.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REGISTERS = {
    "A": {
        "label": "A · Midnight",
        "line": "Premium, technical, trust-me. Deep navy, one cyan, tight grotesque, slow lerp.",
        "words": [
            "saas", "fintech", "finance", "bank", "pay", "invoice", "crypto", "blockchain", "ai",
            "ml", "model", "startup", "scale", "growth", "analytics", "dashboard", "metrics", "bi",
            "devtool", "developer", "api", "sdk", "cloud", "infra", "security", "compliance", "b2b",
            "enterprise", "crm", "automation", "workflow", "agent", "copilot", "hosting", "terminal",
            "premium", "trust", "secure", "professional", "minimal dark",
        ],
        "template": "templates/landing/",
        "recipes": ["pinned-hero-shrink", "shader-background", "blur-reveal", "card-wall-3d",
                    "marquee", "magnetic-button", "field-cursor"],
        "moment": "pinned hero that shrinks into the nav while the headline splits",
        "avoid": [
            "Rainbow gradients and emoji in the hero — the register is one accent, not five.",
            "Bouncy springs on a trust page. 200–400 ms ease-out, never overshoot.",
            "Three.js for its own sake; if the object does not explain the product, use a shader.",
        ],
    },
    "B": {
        "label": "B · Paper",
        "line": "Editorial, human, lots of words. Off-white, ink, vermilion, serif display.",
        "words": [
            "editorial", "magazine", "journal", "portfolio", "photographer", "writer", "author",
            "studio", "agency", "architecture", "interior", "restaurant", "cafe", "coffee", "bakery",
            "wedding", "gallery", "museum", "law", "legal", "clinic", "doctor", "dental", "therapy",
            "wellness", "yoga", "nonprofit", "foundation", "university", "school", "course", "book",
            "elegant", "refined", "quiet", "luxury", "craft", "handmade", "ceramic", "fashion",
        ],
        "template": "templates/portfolio/",
        "recipes": ["scroll-drift", "svg-path-draw", "letter-stagger", "blur-reveal",
                    "image-hover-distortion", "page-transition", "hover-pulse"],
        "moment": "a scroll-drift hero where the serif headline and the photo separate at different speeds",
        "avoid": [
            "Dark mode by default; Paper lives in daylight.",
            "Marquees and scrambles — they fight the reading voice.",
            "More than two type families. Serif display + one workhorse text face is the whole system.",
        ],
    },
    "C": {
        "label": "C · Pop",
        "line": "Loud, cultural, poster-like. Near-black, acid lime, hard grotesque.",
        "words": [
            "streetwear", "sneaker", "music", "record", "label", "band", "dj", "festival", "concert",
            "tour", "nightclub", "bar", "energy drink", "snack", "gaming", "esports", "arcade",
            "skate", "surf", "tattoo", "magazine", "zine", "poster", "gen z", "hype", "drop",
            "merch", "clothing", "fashion week", "bold", "loud", "edgy", "brutalist",
        ],
        "template": "templates/event/",
        "recipes": ["text-scramble", "marquee", "card-wall-3d", "image-hover-distortion",
                    "shader-background", "page-transition", "horizontal-scroll", "hover-pulse"],
        "moment": "a letter-scramble headline that resolves on load over a full-bleed shader",
        "avoid": [
            "Pastels and soft shadows — they read as a kids brand, not a drop.",
            "Rounded corners over 12 px. Pop is cut, not cushioned.",
            "Long calm scenes. Cut hard, cut often, keep type enormous.",
        ],
    },
    "D": {
        "label": "D · Sunny",
        "line": "Playful, young, warm, has a face. Powder blue, cream, coral, chunky rounded type.",
        "words": [
            "kids", "kid", "child", "children", "baby", "toddler", "pet", "dog", "cat", "puppy",
            "kitten", "animal", "toy", "toys", "game", "play", "learning", "school", "nursery",
            "rhyme", "story", "book", "cartoon", "mascot", "character", "cute", "fun", "playful",
            "ice cream", "candy", "chocolate", "birthday", "party", "family", "parent", "mom", "dad",
        ],
        "template": "templates/landing/",
        "recipes": ["character-scene", "acting-mascot", "letter-stagger", "hover-pulse",
                    "blur-reveal", "magnetic-button"],
        "moment": "a cast of characters taking the stage one by one, then a poke reaction on hover",
        "avoid": [
            "Dark navy + cyan SaaS framing — this is the single most common failure for this brief.",
            "Gradients and 3D gloss on the characters. Flat fills, one outline weight, no shading.",
            "Only fade-ups. The register needs overshoot: spring entrances, ambient bob, a poke.",
        ],
    },
}

STACK_NOTE = {
    "next": "Next.js / React: port each recipe into a client component; keep CSS keyframes, move the "
            "IntersectionObserver/pointer logic into useEffect with a cleanup.",
    "react": "React: same as next — recipes are DOM-level, so wrap the markup and keep the CSS verbatim.",
    "astro": "Astro: drop the recipe markup into an .astro component; the <script> stays vanilla.",
    "vue": "Vue: put the recipe's IIFE in onMounted, keep the class names identical.",
    "html": "Plain HTML/CSS/JS (default): copy the recipe block verbatim, no build step.",
}


def score(text: str) -> dict[str, int]:
    t = re.sub(r"[^a-z0-9 ]", " ", text.lower())
    t = f" {t} "
    out = {}
    for key, reg in REGISTERS.items():
        hits = sum(1 for w in reg["words"] if f" {w} " in t or (len(w) > 4 and w in t))
        out[key] = hits
    return out


TEMPLATE_HINTS = [
    ("templates/event/", ["event", "wedding", "concert", "festival", "conference", "invite", "party",
                          "launch party", "rsvp"]),
    ("templates/gallery/", ["gallery", "portfolio", "photography", "photo", "artwork", "archive",
                            "lookbook", "moodboard"]),
    ("templates/product-launch/", ["launch", "waitlist", "pre-order", "preorder", "coming soon",
                                   "sign up", "early access"]),
    ("templates/landing/", ["shop", "store", "buy", "subscribe", "subscription", "price", "pricing",
                            "order", "product", "booking", "book a", "demo", "app", "saas"]),
]


def pick_template(brief: str, key: str) -> str:
    t = " " + re.sub(r"[^a-z0-9 ]", " ", brief.lower()) + " "
    for tpl, words in TEMPLATE_HINTS:
        if any(w in t for w in words):
            return tpl
    return REGISTERS[key]["template"]


def triage(brief: str) -> tuple[str, dict, list[str]]:
    s = score(brief)
    order = sorted(s.items(), key=lambda kv: (-kv[1], kv[0]))
    best_key, best = order[0]
    runner_key, runner = order[1]
    matched = [w for w in REGISTERS[best_key]["words"] if w in brief.lower()]
    if best == 0:
        return "B", {"score": s, "matched": []}, [
            "No register matched the brief — I defaulted to B · Paper. Tell me the brand in one line "
            "and I will re-run the triage.",
        ]
    warns = []
    if best - runner <= 0 and runner > 0:
        warns.append(f"Register is a coin flip between {REGISTERS[best_key]['label']} and "
                     f"{REGISTERS[runner_key]['label']} ({best} vs {runner}). Send two references and I "
                     f"will pick from them instead of guessing.")
    return best_key, {"score": s, "matched": matched}, warns


def plan_markdown(brief: str, key: str, meta: dict, warns: list[str], stack: str) -> str:
    reg = REGISTERS[key]
    others = [REGISTERS[k]["label"] for k in "ABCD" if k != key]
    lines = [
        f"# Build plan — {brief}",
        "",
        f"**Register: {reg['label']}** — {reg['line']}",
        f"Matched on: {', '.join(meta['matched']) or 'fallback'} · rejected: {', '.join(others)}",
        "",
        "## Start from",
        "",
        f"`{pick_template(brief, key)}` — copy it, keep its spacing/type scale, replace the content. "
        "It already passes `tools/qa.py`; do not rebuild the layout from zero.",
        "",
        "## The one big moment",
        "",
        f"{reg['moment'].capitalize()}.",
        "Everything else on the page stays quiet so this reads. One hero-scale move per screen.",
        "",
        "## Recipe shortlist",
        "",
        "| Section | Recipe | Why |",
        "|---|---|---|",
    ]
    why = {
        "pinned-hero-shrink": "hero owns the first scroll; the shrink is the transition",
        "shader-background": "depth behind type without an image",
        "blur-reveal": "sections arrive in focus, not at once",
        "card-wall-3d": "the work is the proof; let it tilt",
        "marquee": "logos / proof, pauses on hover",
        "magnetic-button": "the CTA answers the hand",
        "field-cursor": "site-wide pointer language",
        "scroll-drift": "headline and image separate at different speeds",
        "svg-path-draw": "a hand-drawn line connects two ideas",
        "letter-stagger": "type arrives with a rhythm",
        "image-hover-distortion": "portfolio images respond to the pointer",
        "page-transition": "chapters feel continuous",
        "hover-pulse": "tactile hover + focus, never decoration",
        "text-scramble": "headline resolves out of noise",
        "horizontal-scroll": "a gallery that travels sideways",
        "character-scene": "the cast takes the stage, then answers a poke",
        "acting-mascot": "a guide with four poses hosts the page",
    }
    for slug in reg["recipes"]:
        lines.append(f"| {slug.replace('-', ' ').title()} | `recipes/{slug}/` | {why.get(slug, '')} |")
    lines += [
        "",
        "## Motion budget",
        "",
        "- 1 hero-scale moment, 2–3 supporting moves, 1 micro-interaction language used everywhere.",
        "- Durations: entrances 400–700 ms, hover 150–300 ms, ambient loops 4–8 s with negative delays.",
        "- Animate `transform` / `opacity` / `filter` only. `prefers-reduced-motion` from the first commit.",
        "",
        "## Do not do",
        "",
    ]
    lines += [f"- {a}" for a in reg["avoid"]]
    lines += [
        "",
        "## Ship gate",
        "",
        "```bash",
        f"python3 tools/qa.py <target> --out qa/",
        f"python3 tools/design_lint.py <target> --out qa/lint",
        "```",
        "Both green, then open `qa/contact-sheet.png` and look at it before anyone else does.",
        "",
    ]
    if warns:
        lines += ["## Questions for the human", ""] + [f"- {w}" for w in warns] + [""]
    if stack in STACK_NOTE:
        lines += [f"## Stack note ({stack})", "", STACK_NOTE[stack], ""]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Triage a one-line brief into a build plan.")
    ap.add_argument("--brief", required=True, help="the brief, e.g. 'a pet playlist app for dog owners'")
    ap.add_argument("--stack", default="html", help="html (default) | next | react | astro | vue")
    ap.add_argument("--out", help="write the plan to this .md file instead of stdout")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--ask", action="store_true", help="print the three questions to send the human")
    a = ap.parse_args()

    key, meta, warns = triage(a.brief)
    reg = REGISTERS[key]

    if a.ask:
        print("Send the human one short message, with a default for each:\n")
        print("1. What is the site for, and the ONE action a visitor should take? "
              f"(default from brief: {a.brief})")
        print(f"2. Does this register feel right — {reg['label']}? Yes / no, show me another. "
              f"(I would not build a second one without asking.)")
        print("3. Real copy, logo, photos, brand colours — or should I use clearly marked placeholders?")
        return 0

    if a.json:
        print(json.dumps({
            "brief": a.brief, "register": key, "label": reg["label"], "matched": meta["matched"],
            "scores": meta["score"], "template": pick_template(a.brief, key), "recipes": reg["recipes"],
            "moment": reg["moment"], "avoid": reg["avoid"], "warnings": warns,
        }, indent=2))
        return 0

    md = plan_markdown(a.brief, key, meta, warns, a.stack)
    if a.out:
        Path(a.out).write_text(md, encoding="utf-8")
        print(f"wrote {a.out} — register {reg['label']}")
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
