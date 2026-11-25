#!/usr/bin/env python3
"""Expression sheets: one pose, many faces, zero jitter.

    # 1. one character: neutral base + variants made by EDITING that base image
    python3 tools/expressions.py build --id dog --name "Biscuit the dog" \\
        --base raw/dog_neutral.png --expr blink=raw/dog_blink.png \\
        --expr sing=raw/dog_sing.png --expr surprised=raw/dog_surprised.png \\
        --out assets/cast-expr --max 760 --bleed left,bottom

    # 2. every character folder -> assets/cast-expr/cast.js (works from file://) + weight report
    python3 tools/expressions.py bundle assets/cast-expr

    # 3. rigpop-forge interop (character.rigpop.json, spec 1)
    python3 tools/expressions.py qa assets/cast-expr/dog            # Forge QA rules on a pack
    python3 tools/expressions.py export-forge assets/cast-expr/dog --out forge/dog   # strict PNG pack
    python3 tools/expressions.py import-forge path/to/kiko.rigpop-pack --out assets/cast-expr

Why: swapping a whole pose reads as a slideshow; keeping the body pixel-identical and changing only
the face reads as acting. Image models never return the edit at exactly the same offset, so every
variant is keyed (tools/cast_cut.py), aligned to the base on its outline (coarse-to-fine offset search,
then sub-pixel phase correlation), and only the changed region is kept as a small face patch with its
rect on the base canvas. The patch's outer ring is the base's own pixels, feathered into the new face,
so pasting it can never leave a seam. Residual misalignment over 2 px fails the build.

Output per character (a rigpop-forge "talk" pack, WebP for the web):
    <out>/<id>/character.rigpop.json   talk.canvas / base / files / patches + an `expressions` block
    <out>/<id>/talk/base.webp          neutral, exactly canvas-sized
    <out>/<id>/talk/<expr>.webp        patch, exactly rect-sized
Needs numpy + Pillow.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import numpy as np
    from PIL import Image, ImageDraw
except ImportError:  # pragma: no cover
    sys.exit("expressions.py needs numpy and Pillow: pip install numpy pillow")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cast_cut import key_array  # noqa: E402  (same folder)

MAX_RESIDUAL = 2.0      # px, at source resolution — the brief's hard gate
DRIFT_REJECT = 0.45     # a variant that differs over >45% of the canvas is a redraw, not an edit (Forge rule)
FEATHER = 6             # px at output size: patch border = base pixels, ramps to the new face
# Forge talk keys every rigpop app expects, mapped onto our expressions (and back on import)
TALK_FROM_EXPR = {"A": "sing", "O": "surprised", "E": "sing", "blink": "blink"}
EXPR_FROM_TALK = {"sing": "A", "surprised": "O", "blink": "blink"}


# ---------------------------------------------------------------- image helpers
def box_blur(a: np.ndarray, r: int) -> np.ndarray:
    if r <= 0:
        return a
    k = 2 * r + 1
    p = np.pad(a, r, mode="edge")
    c = p.cumsum(0).cumsum(1)
    c = np.pad(c, ((1, 0), (1, 0)))
    return (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / (k * k)


def dilate(m: np.ndarray, r: int) -> np.ndarray:
    return box_blur(m.astype(np.float32), r) > 1e-6 if r > 0 else m


def erode(m: np.ndarray, r: int) -> np.ndarray:
    return box_blur(m.astype(np.float32), r) > 1 - 1e-6 if r > 0 else m


def ink(rgba: np.ndarray) -> np.ndarray:
    """The outline: dark, opaque pixels. The one feature every edit keeps."""
    lum = rgba[..., :3] @ np.array([0.299, 0.587, 0.114], np.float32)
    return ((lum < 95) & (rgba[..., 3] > 0.5)).astype(np.float32)


def shift(a: np.ndarray, dx: int, dy: int) -> np.ndarray:
    out = np.zeros_like(a)
    h, w = a.shape[:2]
    xs, xd = (slice(0, w - dx), slice(dx, w)) if dx >= 0 else (slice(-dx, w), slice(0, w + dx))
    ys, yd = (slice(0, h - dy), slice(dy, h)) if dy >= 0 else (slice(-dy, h), slice(0, h + dy))
    out[yd, xd] = a[ys, xs]
    return out


def subpixel_shift(rgba: np.ndarray, dx: float, dy: float) -> np.ndarray:
    """Premultiplied bilinear translate (keeps edges clean)."""
    pm = rgba.copy()
    pm[..., :3] *= pm[..., 3:4]
    chans = []
    for c in range(4):
        im = Image.fromarray(pm[..., c].astype(np.float32), "F")
        im = im.transform(im.size, Image.AFFINE, (1, 0, -dx, 0, 1, -dy), resample=Image.BILINEAR)
        chans.append(np.asarray(im))
    out = np.dstack(chans).astype(np.float32)
    a = np.clip(out[..., 3:4], 1e-6, 1)
    out[..., :3] = np.where(out[..., 3:4] > 1e-4, out[..., :3] / a, 0)
    return out


def best_offset(fa: np.ndarray, fb: np.ndarray, radius: int, step: int = 1,
                center: tuple[int, int] = (0, 0)) -> tuple[int, int, float]:
    """Integer offset (dx, dy) that moves fb onto fa, minimising mean |fa - fb|."""
    best = (0, 0, float("inf"))
    cx, cy = center
    for dy in range(cy - radius, cy + radius + 1, step):
        for dx in range(cx - radius, cx + radius + 1, step):
            err = float(np.abs(fa - shift(fb, dx, dy)).mean())
            if err < best[2]:
                best = (dx, dy, err)
    return best


def phase_residual(fa: np.ndarray, fb: np.ndarray) -> tuple[float, float]:
    """Sub-pixel translation of fb relative to fa (phase correlation + parabolic peak)."""
    h, w = fa.shape
    win = np.outer(np.hanning(h), np.hanning(w)).astype(np.float32)
    A, B = np.fft.fft2(fa * win), np.fft.fft2(fb * win)
    R = A * np.conj(B)
    R /= np.abs(R) + 1e-9
    r = np.fft.ifft2(R).real
    py, px = np.unravel_index(np.argmax(r), r.shape)

    def para(m1, c, p1):
        d = m1 - 2 * c + p1
        return 0.0 if abs(d) < 1e-12 else 0.5 * (m1 - p1) / d

    ox = px + para(r[py, (px - 1) % w], r[py, px], r[py, (px + 1) % w])
    oy = py + para(r[(py - 1) % h, px], r[py, px], r[(py + 1) % h, px])
    if ox > w / 2:
        ox -= w
    if oy > h / 2:
        oy -= h
    return float(ox), float(oy)  # fb must move by (+ox, +oy) to land on fa


def subpixel_search(fa: np.ndarray, fb: np.ndarray) -> tuple[float, float]:
    """Sub-pixel (dx, dy) in [-1, 1] that moves fb onto fa: grid 0.25 px, then 0.05 px."""
    ys, xs = np.nonzero(fa > 0.05)
    if len(xs) < 50:
        return 0.0, 0.0
    y0, y1, x0, x1 = max(0, ys.min() - 4), ys.max() + 5, max(0, xs.min() - 4), xs.max() + 5
    A, B = fa[y0:y1, x0:x1], Image.fromarray(np.ascontiguousarray(fb[y0:y1, x0:x1]).astype(np.float32), "F")

    def err(dx, dy):
        m = np.asarray(B.transform(B.size, Image.AFFINE, (1, 0, -dx, 0, 1, -dy), resample=Image.BILINEAR))
        return float(np.abs(A[2:-2, 2:-2] - m[2:-2, 2:-2]).mean())

    best = (0.0, 0.0)
    for step, span in ((0.25, 4), (0.05, 5)):
        cx, cy = best
        cands = [(cx + i * step, cy + j * step) for j in range(-span, span + 1) for i in range(-span, span + 1)]
        best = min(cands, key=lambda c: err(*c))
    return best


def change_core(base: np.ndarray, var: np.ndarray, block: int = 8, min_px: int = 10) -> np.ndarray:
    """Mask of what the edit really changed: colour or alpha moved a lot, thin wobble lines removed."""
    ab, av = base[..., 3], var[..., 3]
    rgb = np.abs(base[..., :3] - var[..., :3]).max(axis=2) / 255.0 * np.maximum(ab, av)
    d = np.maximum(rgb, np.abs(ab - av))
    m = d > 0.3
    m = dilate(erode(m, 2), 2)          # opening: 1–3 px outline wobble disappears, real features stay
    h, w = m.shape
    H, W = (h + block - 1) // block, (w + block - 1) // block
    pad = np.zeros((H * block, W * block), bool)
    pad[:h, :w] = m
    cnt = pad.reshape(H, block, W, block).sum(axis=(1, 3))
    keep = cnt >= min_px
    # an isolated block is a speck; a feature spans neighbouring blocks
    nb = box_blur(keep.astype(np.float32), 1) * 9
    keep &= nb >= 2
    out = np.repeat(np.repeat(keep, block, 0), block, 1)[:h, :w] & m
    return out


def bbox(mask: np.ndarray):
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def to_img(rgba: np.ndarray) -> Image.Image:
    a = np.dstack([rgba[..., :3], rgba[..., 3:4] * 255])
    return Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8), "RGBA")


def from_img(im: Image.Image) -> np.ndarray:
    a = np.asarray(im.convert("RGBA")).astype(np.float32)
    a[..., 3] /= 255.0
    return a


def resize_rgba(rgba: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    """Premultiplied LANCZOS resize, so edges never pick up dark or magenta halos."""
    pm = rgba.copy()
    pm[..., :3] *= pm[..., 3:4]
    chans = [np.asarray(Image.fromarray(pm[..., c], "F").resize(size, Image.LANCZOS)) for c in range(4)]
    out = np.dstack(chans).astype(np.float32)
    out[..., 3] = np.clip(out[..., 3], 0, 1)
    a = np.clip(out[..., 3:4], 1e-6, 1)
    out[..., :3] = np.where(out[..., 3:4] > 1e-3, np.clip(out[..., :3] / a, 0, 255), 0)
    return out


# ---------------------------------------------------------------- align one variant
def align(base: np.ndarray, var: np.ndarray, radius: int = 32) -> dict:
    h, w = base.shape[:2]
    if var.shape[:2] != (h, w):
        var = resize_rgba(var, (w, h))
    fa, fb = box_blur(ink(base), 2), box_blur(ink(var), 2)
    # coarse at 1/4, then fine at full res
    q = 4
    ca, cb = fa[::q, ::q], fb[::q, ::q]
    cdx, cdy, _ = best_offset(ca, cb, radius // q)
    dx, dy, err = best_offset(fa, fb, 3, center=(cdx * q, cdy * q))
    var = shift(var, dx, dy)

    # pixels that came from outside the variant's frame are not information: ignore them
    valid = erode(shift(np.ones((h, w), bool), dx, dy), 3) if (dx or dy) else np.ones((h, w), bool)

    # what changed (with the integer alignment), then the sub-pixel remainder everywhere else
    core = change_core(base, var) & valid
    keep_out = ~dilate(core, 18) & valid
    fa = box_blur(ink(base), 2) * keep_out
    sx, sy = subpixel_search(fa, box_blur(ink(var), 2) * keep_out)
    applied = (0.0, 0.0)
    if abs(sx) >= 0.1 or abs(sy) >= 0.1:
        var = subpixel_shift(var, sx, sy)
        applied = (sx, sy)
        core = change_core(base, var) & valid
    # residual: re-measure after the correction (search resolution 0.05 px)
    rx, ry = subpixel_search(fa, box_blur(ink(var), 2) * keep_out)
    residual = float(np.hypot(rx, ry))
    changed = float(core.mean())
    drift_mask = change_core(base, var, block=8, min_px=4) & keep_out
    return {"var": var, "core": core, "offset": [dx + applied[0], dy + applied[1]],
            "residual": residual, "changed": changed, "drift": float(drift_mask.mean())}


# ---------------------------------------------------------------- build
def cmd_build(a) -> int:
    out_dir = Path(a.out) / a.id
    (out_dir / "talk").mkdir(parents=True, exist_ok=True)
    base = key_array(Image.open(a.base))
    H, W = base.shape[:2]
    variants, failures, report = {}, [], []
    for spec in a.expr:
        name, path = spec.split("=", 1)
        r = align(base, key_array(Image.open(path)), radius=a.radius)
        variants[name] = r
        ok = r["residual"] <= MAX_RESIDUAL and r["changed"] < DRIFT_REJECT and bbox(r["core"]) is not None
        report.append(f"  {a.id:8} {name:10} offset ({r['offset'][0]:+.2f}, {r['offset'][1]:+.2f}) px   "
                      f"residual {r['residual']:.2f} px   face {r['changed']*100:4.1f}% of canvas   "
                      f"body drift {r['drift']*100:.2f}%   {'OK' if ok else 'FAIL'}")
        if not ok:
            failures.append(name)

    # canvas = base silhouette ∪ every patch rect (an open beak can reach outside the neutral)
    rects_src = {}
    margin = a.margin
    for name, r in variants.items():
        b = bbox(r["core"])
        if b is None:
            continue
        x0, y0, x1, y1 = b
        rects_src[name] = [max(0, x0 - margin), max(0, y0 - margin), min(W, x1 + margin), min(H, y1 + margin)]
    union = base[..., 3] > 0.02
    for name, (x0, y0, x1, y1) in rects_src.items():
        union[y0:y1, x0:x1] |= variants[name]["var"][y0:y1, x0:x1, 3] > 0.02
    bx0, by0, bx1, by1 = bbox(union)
    bleed = set(filter(None, (a.bleed or "").split(",")))
    pad = a.pad
    bx0 = bx0 if "left" in bleed else max(0, bx0 - pad)
    by0 = by0 if "top" in bleed else max(0, by0 - pad)
    bx1 = bx1 if "right" in bleed else min(W, bx1 + pad)
    by1 = by1 if "bottom" in bleed else min(H, by1 + pad)
    cw, ch = bx1 - bx0, by1 - by0
    s = min(1.0, a.max / max(cw, ch))
    ow, oh = max(1, round(cw * s)), max(1, round(ch * s))

    def crop_scale(rgba):
        return resize_rgba(np.ascontiguousarray(rgba[by0:by1, bx0:bx1]), (ow, oh))

    base_o = crop_scale(base)
    # bleed edges: the model draws the cut a few px short of the frame; make the cut sit on the canvas edge
    for side in bleed:
        sl = {"left": (slice(None), slice(0, 2)), "right": (slice(None), slice(ow - 2, ow)),
              "top": (slice(0, 2), slice(None)), "bottom": (slice(oh - 2, oh), slice(None))}[side]
        edge = base_o[sl]
        edge[..., 3] = np.where(edge[..., 3] > 0.5, 1.0, edge[..., 3])

    to_img(base_o).save(out_dir / "talk" / "base.webp", "WEBP", quality=a.quality, method=6, alpha_quality=90)
    manifest_patches, files, sheet_faces = {}, {}, {"neutral": base_o}
    for name, r in variants.items():
        if name not in rects_src:
            continue
        x0, y0, x1, y1 = rects_src[name]
        X0 = max(0, int(np.floor((x0 - bx0) * s)))
        Y0 = max(0, int(np.floor((y0 - by0) * s)))
        X1 = min(ow, int(np.ceil((x1 - bx0) * s)))
        Y1 = min(oh, int(np.ceil((y1 - by0) * s)))
        var_o = crop_scale(r["var"])
        pb, pv = base_o[Y0:Y1, X0:X1], var_o[Y0:Y1, X0:X1]
        ph, pw = pb.shape[:2]
        # weight ramps 0 -> 1 from the rect border inward, so the outer ring IS the base
        yy = np.minimum(np.arange(ph), np.arange(ph)[::-1])[:, None]
        xx = np.minimum(np.arange(pw), np.arange(pw)[::-1])[None, :]
        wgt = np.clip((np.minimum(yy, xx) - 1) / FEATHER, 0, 1).astype(np.float32)
        # canvas edges that are real silhouette cuts (bleed) don't need a ramp
        pbm, pvm = pb.copy(), pv.copy()
        pbm[..., :3] *= pbm[..., 3:4]
        pvm[..., :3] *= pvm[..., 3:4]
        mix = pbm * (1 - wgt[..., None]) + pvm * wgt[..., None]
        al = np.clip(mix[..., 3:4], 1e-6, 1)
        mix[..., :3] = np.where(mix[..., 3:4] > 1e-3, mix[..., :3] / al, 0)
        fname = f"talk/{name}.webp"
        to_img(mix).save(out_dir / fname, "WEBP", quality=a.quality, method=6, alpha_quality=90)
        manifest_patches[name] = {"x": X0, "y": Y0, "w": pw, "h": ph}
        files[name] = fname
        comp = base_o.copy()
        comp[Y0:Y1, X0:X1] = mix          # clearRect + drawImage, exactly what the recipe does
        sheet_faces[name] = comp

    talk_files, talk_patches = {}, {}
    for k, e in TALK_FROM_EXPR.items():
        if e in files:
            talk_files[k], talk_patches[k] = files[e], manifest_patches[e]
    manifest = {
        "spec": 1,
        "id": a.id,
        "name": a.name or a.id,
        "author": a.author,
        "license": "MIT",
        "talk": {"canvas": {"w": ow, "h": oh}, "base": "talk/base.webp", "files": talk_files,
                 "patches": talk_patches, "bg": a.bg},
        "expressions": {"neutral": {"file": "talk/base.webp"},
                        **{n: {"file": files[n], "rect": manifest_patches[n]} for n in files}},
        "motionField": {
            "bleed": sorted(bleed),
            "talkMap": "A and E = sing, O = surprised (expression faces, not true visemes)",
            "align": {n: {"offsetPx": [round(v["offset"][0], 2), round(v["offset"][1], 2)],
                          "residualPx": round(v["residual"], 2), "bodyDriftPct": round(v["drift"] * 100, 2)}
                      for n, v in variants.items()},
            "source": {"canvas": {"w": W, "h": H}, "crop": [bx0, by0, bx1, by1], "scale": round(s, 4)},
        },
        "style": {"bible": a.style, "palette": []},
    }
    (out_dir / "character.rigpop.json").write_text(json.dumps(manifest, indent=2) + "\n")

    weight = sum(p.stat().st_size for p in (out_dir / "talk").glob("*.webp"))
    print("\n".join(report))
    print(f"  {a.id:8} canvas {ow}x{oh}  base {(out_dir/'talk/base.webp').stat().st_size/1024:.1f} KB  "
          f"patches {', '.join(f'{n} {p['w']}x{p['h']}' for n, p in manifest_patches.items())}  "
          f"total {weight/1024:.1f} KB")
    if a.sheet:
        write_sheet([(a.id, sheet_faces, manifest_patches)], Path(a.sheet), a.bg)
    if failures:
        print(f"FAIL {a.id}: {', '.join(failures)} — residual > {MAX_RESIDUAL} px, no change found, "
              f"or the edit redrew the character. Regenerate that variant from the neutral image.")
        return 1
    return 0


def write_sheet(rows, dest: Path, bg: str, cell_h: int = 260):
    order = ["neutral", "blink", "sing", "surprised"]
    bgc = tuple(int(bg.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
    tiles = []
    for cid, faces, rects in rows:
        row = []
        for n in order:
            if n not in faces:
                continue
            im = to_img(faces[n])
            t = Image.new("RGBA", im.size, bgc)
            t.alpha_composite(im)
            if n in rects:
                r = rects[n]
                ImageDraw.Draw(t).rectangle([r["x"], r["y"], r["x"] + r["w"] - 1, r["y"] + r["h"] - 1],
                                            outline=(255, 255, 255, 160), width=1)
            sc = cell_h / t.height
            row.append(t.resize((max(1, int(t.width * sc)), cell_h), Image.LANCZOS))
        tiles.append(row)
    Wd = max(sum(t.width + 8 for t in r) for r in tiles)
    sheet = Image.new("RGBA", (Wd, (cell_h + 8) * len(tiles)), (255, 255, 255, 255))
    y = 0
    for r in tiles:
        x = 0
        for t in r:
            sheet.alpha_composite(t, (x, y))
            x += t.width + 8
        y += cell_h + 8
    dest.parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(dest, quality=88)
    print(f"  sheet -> {dest}")


# ---------------------------------------------------------------- forge QA + bundle + interop
def image_size(p: Path):
    with Image.open(p) as im:
        return im.size


def qa_pack(d: Path, strict_png: bool = False) -> list[str]:
    errs = []
    m = json.loads((d / "character.rigpop.json").read_text())
    if m.get("spec") != 1:
        errs.append("spec must be 1")
    import re
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", m.get("id", "")):
        errs.append(f"id {m.get('id')!r} is not lowercase-dash")
    t = m.get("talk", {})
    cw, ch = t.get("canvas", {}).get("w"), t.get("canvas", {}).get("h")
    paths = [("base", t.get("base"))] + [(f"pose {k}", v) for k, v in t.get("poses", {}).items()]
    for label, rel in paths:
        if not rel or not (d / rel).exists():
            errs.append(f"{label}: missing file {rel}")
            continue
        if strict_png and not rel.endswith(".png"):
            errs.append(f"{label}: {rel} is not a PNG")
        if image_size(d / rel) != (cw, ch):
            errs.append(f"{label}: {image_size(d / rel)} != canvas {(cw, ch)}")
    for k in ("A", "O", "E", "blink"):
        rel, r = t.get("files", {}).get(k), t.get("patches", {}).get(k)
        if not rel or not r:
            errs.append(f"talk.{k}: missing file or rect")
            continue
        if not (d / rel).exists():
            errs.append(f"talk.{k}: missing {rel}")
            continue
        if image_size(d / rel) != (r["w"], r["h"]):
            errs.append(f"talk.{k}: image {image_size(d / rel)} != rect {(r['w'], r['h'])}")
        if r["x"] < 0 or r["y"] < 0 or r["x"] + r["w"] > cw or r["y"] + r["h"] > ch:
            errs.append(f"talk.{k}: rect off canvas")
    for n, e in m.get("expressions", {}).items():
        if "rect" in e and image_size(d / e["file"]) != (e["rect"]["w"], e["rect"]["h"]):
            errs.append(f"expressions.{n}: image size != rect size")
    return errs


def cmd_qa(a) -> int:
    bad = 0
    for p in a.packs:
        errs = qa_pack(Path(p), a.strict_png)
        print(f"{Path(p).name:10} {'PASS' if not errs else 'FAIL'}" + "".join(f"\n  - {e}" for e in errs))
        bad += bool(errs)
    return 1 if bad else 0


def cmd_bundle(a) -> int:
    root = Path(a.root)
    cast, total, bad = {}, 0, 0
    for d in sorted(p for p in root.iterdir() if (p / "character.rigpop.json").exists()):
        errs = qa_pack(d)
        if errs:
            print(f"{d.name}: Forge QA FAIL\n  - " + "\n  - ".join(errs))
            bad += 1
        m = json.loads((d / "character.rigpop.json").read_text())
        t = m["talk"]
        ex = m.get("expressions") or {}
        if not ex:  # a plain Forge pack: blink <- blink, sing <- A, surprised <- O
            ex = {"neutral": {"file": t["base"]}}
            for e, k in EXPR_FROM_TALK.items():
                if k in t.get("files", {}):
                    ex[e] = {"file": t["files"][k], "rect": t["patches"][k]}
        cast[m["id"]] = {"name": m.get("name", m["id"]), "dir": d.name, "w": t["canvas"]["w"],
                         "h": t["canvas"]["h"], "base": t["base"],
                         "faces": {n: {"file": e["file"], **e.get("rect", {})} for n, e in ex.items() if n != "neutral"}}
        size = sum((d / f).stat().st_size for f in {t["base"], *[e["file"] for e in ex.values()]})
        total += size
        print(f"{d.name:10} {t['canvas']['w']}x{t['canvas']['h']}  {len(ex)} faces  {size/1024:6.1f} KB")
    js = ("/* generated by tools/expressions.py bundle — do not edit by hand */\n"
          f"window.MF_EXPR_CAST = {json.dumps(cast, separators=(',', ':'))};\n")
    (root / "cast.js").write_text(js)
    print(f"total cast weight {total/1024:.1f} KB (budget {a.budget} KB)  -> {root/'cast.js'}")
    if total / 1024 > a.budget:
        print("FAIL: over budget — lower --max or --quality on the biggest character")
        return 1
    return 1 if bad else 0


def cmd_export_forge(a) -> int:
    src, dst = Path(a.pack), Path(a.out)
    m = json.loads((src / "character.rigpop.json").read_text())
    (dst / "talk").mkdir(parents=True, exist_ok=True)
    t = m["talk"]
    Image.open(src / t["base"]).convert("RGBA").save(dst / "talk/base.png")
    files = {}
    for k, rel in t["files"].items():
        Image.open(src / rel).convert("RGBA").save(dst / f"talk/{k}.png")
        files[k] = f"talk/{k}.png"
    out = {k: v for k, v in m.items() if k not in ("expressions", "motionField")}
    out["talk"] = {**t, "base": "talk/base.png", "files": files}
    (dst / "character.rigpop.json").write_text(json.dumps(out, indent=2) + "\n")
    errs = qa_pack(dst, strict_png=True)
    print(f"exported {m['id']} -> {dst}  Forge QA {'PASS' if not errs else 'FAIL'}" + "".join(f"\n  - {e}" for e in errs))
    return 1 if errs else 0


def cmd_import_forge(a) -> int:
    src = Path(a.pack)
    m = json.loads((src / "character.rigpop.json").read_text())
    errs = qa_pack(src)
    if errs:
        print("source pack fails Forge QA:\n  - " + "\n  - ".join(errs))
        return 1
    dst = Path(a.out) / m["id"]
    (dst / "talk").mkdir(parents=True, exist_ok=True)
    t = m["talk"]
    q = a.quality
    Image.open(src / t["base"]).convert("RGBA").save(dst / "talk/base.webp", "WEBP", quality=q, method=6)
    files, ex = {}, {"neutral": {"file": "talk/base.webp"}}
    for k, rel in t["files"].items():
        Image.open(src / rel).convert("RGBA").save(dst / f"talk/{k}.webp", "WEBP", quality=q, method=6)
        files[k] = f"talk/{k}.webp"
    for e, k in EXPR_FROM_TALK.items():
        if k in files:
            ex[e] = {"file": files[k], "rect": t["patches"][k]}
    out = {**m, "talk": {**t, "base": "talk/base.webp", "files": files}, "expressions": ex,
           "motionField": {"bleed": [], "talkMap": "imported from rigpop-forge: sing <- A, surprised <- O"}}
    out["talk"].pop("poses", None)  # gesture poses are whole-pose swaps; the recipe acts with faces only
    (dst / "character.rigpop.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"imported {m['id']} -> {dst}; run `bundle` to add it to cast.js")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Aligned expression sheets as rigpop-forge talk packs.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="key + align + patch one character")
    b.add_argument("--id", required=True)
    b.add_argument("--name")
    b.add_argument("--base", required=True, help="neutral image on flat magenta")
    b.add_argument("--expr", action="append", default=[], metavar="NAME=PNG", help="variant edited from the base")
    b.add_argument("--out", default="assets/cast-expr")
    b.add_argument("--max", type=int, default=640, help="longest canvas side in px")
    b.add_argument("--quality", type=int, default=82)
    b.add_argument("--margin", type=int, default=22, help="px (source) around the changed region")
    b.add_argument("--pad", type=int, default=6, help="px (source) of transparent canvas padding")
    b.add_argument("--radius", type=int, default=32, help="max offset search in px (source)")
    b.add_argument("--bleed", default="", help="edges the art is cut by: left,right,top,bottom")
    b.add_argument("--bg", default="#a3bccf")
    b.add_argument("--author", default="Swapnil Agrawal")
    b.add_argument("--style", default="flat pastel cartoon, thick near-black outline, coral blush cheeks")
    b.add_argument("--sheet", help="write a contact sheet of every composed face")
    q = sub.add_parser("qa", help="Forge QA rules on one or more packs")
    q.add_argument("packs", nargs="+")
    q.add_argument("--strict-png", action="store_true", help="require PNG files (Forge's own format)")
    u = sub.add_parser("bundle", help="every pack in a folder -> cast.js + weight gate")
    u.add_argument("root")
    u.add_argument("--budget", type=float, default=400, help="KB for the whole cast")
    e = sub.add_parser("export-forge", help="web pack -> strict PNG rigpop-forge pack")
    e.add_argument("pack")
    e.add_argument("--out", required=True)
    i = sub.add_parser("import-forge", help="rigpop-forge pack -> web pack for the recipe")
    i.add_argument("pack")
    i.add_argument("--out", default="assets/cast-expr")
    i.add_argument("--quality", type=int, default=82)
    a = ap.parse_args()
    return {"build": cmd_build, "qa": cmd_qa, "bundle": cmd_bundle,
            "export-forge": cmd_export_forge, "import-forge": cmd_import_forge}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
