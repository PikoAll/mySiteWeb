#!/usr/bin/env python3
"""Build the site's brand assets from the approved brand folder.

Source: ~/Scrivania/PikBitAvatar/brand-approvato (see its LEGGIMI.md). The
approved images are copied or resized, never redrawn:

- favicon.ico and apple-touch-icon.png (180) in the site root, where browsers
  and crawlers look for them even without a <link>;
- images/brand/favicon-{32,192,512}.png for <link rel="icon"> and the manifest;
- images/brand/pikobit-logo-512.png: the square official logo, used as
  "logo"/"image" in the JSON-LD (Google wants >= 112px, square is safest);
- images/brand/og-pikobit-1200x630.jpg: the site header band (the approved
  banner) centred on the site background #0d0f12, for social previews.

Usage:
    python3 scripts/build_brand_assets.py [BRAND_DIR]
Idempotent: running it twice gives the same files.
"""
import shutil
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SRC = Path.home() / "Scrivania/PikBitAvatar/brand-approvato"
BG = (13, 15, 18)  # #0d0f12, --color-bg in styles/style.css
OG_SIZE = (1200, 630)
# Centre crop of the 3840px banner: the wordmark (~990px) plus the inner
# circuit lines, scaled so the wordmark is about half the preview width.
OG_CROP_WIDTH = 2000


def build_og(src: Path, dest: Path) -> None:
    band = Image.open(src / "banner/pikobit-banner-3840x399.png").convert("RGB")
    left = (band.width - OG_CROP_WIDTH) // 2
    band = band.crop((left, 0, left + OG_CROP_WIDTH, band.height))
    scale = OG_SIZE[0] / OG_CROP_WIDTH
    band = band.resize((OG_SIZE[0], round(band.height * scale)), Image.LANCZOS)
    canvas = Image.new("RGB", OG_SIZE, BG)
    canvas.paste(band, (0, (OG_SIZE[1] - band.height) // 2))
    canvas.save(dest, "JPEG", quality=88, optimize=True, progressive=True)


def main(src: Path) -> None:
    brand = ROOT / "images/brand"
    brand.mkdir(parents=True, exist_ok=True)
    fav = src / "favicon"
    shutil.copyfile(fav / "favicon.ico", ROOT / "favicon.ico")
    shutil.copyfile(fav / "favicon-180.png", ROOT / "apple-touch-icon.png")
    for size in (32, 192, 512):
        shutil.copyfile(fav / f"favicon-{size}.png", brand / f"favicon-{size}.png")
    logo = Image.open(src / "logo/logo-quadrato-1080.png").convert("RGB")
    logo.resize((512, 512), Image.LANCZOS).save(brand / "pikobit-logo-512.png", optimize=True)
    build_og(src, brand / "og-pikobit-1200x630.jpg")
    print("brand assets written to", brand)


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SRC)
