#!/usr/bin/env python3
"""Regenerate the site logo and all favicons/app icons from one source image.

Usage:
    pip install pillow cairosvg
    python3 scripts/make_icons.py assets/images/logo.svg

The source can be an SVG (preferred; needs cairosvg) or a square PNG with a
transparent background of at least 1200x1200. Run it again whenever the logo
changes. The masthead shows logo.svg directly, so update that file too.
"""
import sys
from pathlib import Path

from PIL import Image

IMAGES = Path(__file__).resolve().parent.parent / "assets" / "images"

# file name -> edge length in px
SIZES = {
    "logo.png": 1200,  # og:image for link previews
    "android-chrome-512x512.png": 512,
    "android-chrome-192x192.png": 192,
    "mstile-150x150.png": 270,
    "favicon-32x32.png": 32,
    "favicon-16x16.png": 16,
}
TOUCH_ICON_SIZE = 180  # iOS ignores transparency, so this one gets a white background


def square(img: Image.Image) -> Image.Image:
    """Pad to a square canvas so nothing gets stretched."""
    side = max(img.size)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(img, ((side - img.width) // 2, (side - img.height) // 2))
    return canvas


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    path = Path(sys.argv[1])
    if path.suffix.lower() == ".svg":
        import io

        import cairosvg

        png = cairosvg.svg2png(url=str(path), output_width=2048)
        src = square(Image.open(io.BytesIO(png)).convert("RGBA"))
    else:
        src = square(Image.open(path).convert("RGBA"))

    for name, size in SIZES.items():
        src.resize((size, size), Image.LANCZOS).save(IMAGES / name, optimize=True)

    touch = Image.new("RGBA", (TOUCH_ICON_SIZE,) * 2, (255, 255, 255, 255))
    inset = round(TOUCH_ICON_SIZE * 0.08)
    inner = TOUCH_ICON_SIZE - 2 * inset
    touch.alpha_composite(src.resize((inner, inner), Image.LANCZOS), (inset, inset))
    touch.convert("RGB").save(IMAGES / "apple-touch-icon.png", optimize=True)

    src.save(IMAGES / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    print(f"Wrote {len(SIZES) + 2} images to {IMAGES}")


if __name__ == "__main__":
    main()
