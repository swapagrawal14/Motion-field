#!/usr/bin/env python3
"""Cut a generated character out of its flat background into a transparent WebP.

    python3 tools/cast_cut.py assets/cast/raw/*.png --out assets/cast --key FF00FF
    python3 tools/cast_cut.py raw/frog.png --out assets/cast --key FFFFFF --max 460 --quality 84

Why: image models will not reliably give you a transparent PNG, but they will reliably give you a
character on a solid colour. Key that colour out, unmix the anti-aliased edge (so no magenta fringe),
crop to the alpha bounding box and export WebP at 2x the display size. That is the whole difference
between a sticker cast and a cut-out that looks wrong on every background.

--key accepts RRGGBB. Use a colour that appears nowhere in the character (magenta is the usual pick).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import numpy as np
    from PIL import Image
except ImportError:  # pragma: no cover
    sys.exit("cast_cut.py needs numpy and Pillow: pip install numpy pillow")


def key_array(im: "Image.Image", key: tuple[float, float, float] = (255, 0, 255),
              low: float = 28.0, high: float = 52.0) -> "np.ndarray":
    """Key a flat background out of a character image; return float RGBA (H, W, 4), alpha 0..1.

    No crop, no resize: tools/expressions.py relies on every variant keeping its own canvas.
    """
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    k = np.array(key, dtype=np.float32)

    if key[1] < 90 and key[0] > 150 and key[2] > 150:
        # magenta-ness: min(red, blue) - green. Robust to a slightly off key colour, a vignette or
        # a haze. min (not max) matters: coral blush (#f37f73) and pink fur have high red but low
        # blue, and a max(red, blue) score keys them half-transparent.
        m = np.minimum(a[..., 0], a[..., 2]) - a[..., 1]
        alpha = 1.0 - np.clip((m - 60.0) / 60.0, 0.0, 1.0)
        # unmix against the background the model actually painted (often #FD22F9, not #FF00FF)
        bg = a[m > 150]
        if len(bg) > 100:
            k = np.median(bg, axis=0)
    else:
        dist = np.sqrt(((a - k) ** 2).sum(axis=2))
        alpha = np.clip((dist - low) / high, 0.0, 1.0)

    # edge pixels are a blend of character and key colour: solve for the character colour
    af = np.clip(alpha, 1e-3, 1.0)[..., None]
    unmixed = (a - (1 - af) * k) / af
    rgb = np.clip(np.where(af > 0.995, a, unmixed), 0, 255)
    rgb = np.where(alpha[..., None] > 0.004, rgb, 0)
    return np.dstack([rgb, alpha * 255]).astype(np.float32) / np.array([1, 1, 1, 255], np.float32)


def key_out(src: Path, dest: Path, key: tuple[float, float, float], max_side: int, quality: int,
            low: float = 28.0, high: float = 52.0, pad_pct: float = 0.03) -> tuple[int, int, int]:
    rgba = key_array(Image.open(src), key, low, high)
    cut = Image.fromarray(np.dstack([rgba[..., :3], rgba[..., 3] * 255]).astype(np.uint8), "RGBA")
    bbox = cut.getchannel("A").point(lambda v: 255 if v > 128 else 0).getbbox()
    if not bbox:
        raise SystemExit(f"{src}: nothing left after keying — is --key the background colour?")
    cut = cut.crop(bbox)

    pad = int(max(cut.size) * pad_pct)
    canvas = Image.new("RGBA", (cut.width + pad * 2, cut.height + pad * 2), (0, 0, 0, 0))
    canvas.alpha_composite(cut, (pad, pad))
    canvas.thumbnail((max_side, max_side), Image.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest, "WEBP", quality=quality, method=6)
    return canvas.width, canvas.height, dest.stat().st_size


def main() -> int:
    ap = argparse.ArgumentParser(description="Key out a flat background and export a transparent WebP.")
    ap.add_argument("images", nargs="+", help="PNG files to cut out")
    ap.add_argument("--out", default="assets/cast", help="output folder")
    ap.add_argument("--key", default="FF00FF", help="background colour to remove, RRGGBB (default FF00FF)")
    ap.add_argument("--max", type=int, default=460, help="longest side in px (default 460, ~2x display size)")
    ap.add_argument("--quality", type=int, default=84)
    a = ap.parse_args()

    key = tuple(int(a.key[i:i + 2], 16) for i in (0, 2, 4))
    out = Path(a.out)
    for src in a.images:
        w, h, size = key_out(Path(src), out / (Path(src).stem + ".webp"), key, a.max, a.quality)
        print(f"{Path(src).stem:12} {w}x{h}  {size/1024:.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
