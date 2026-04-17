"""Smart wallpaper analysis — auto-detect light/dark mode and colour variant.

'Smart' opts are derived from the wallpaper's dominant hue and colourfulness,
then cached alongside the thumbnail so repeated calls are free.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image
from materialyoucolor.hct import Hct
from materialyoucolor.utils.color_utils import argb_from_rgb

from caelestia.utils.wallpaper.image import get_thumb


def _compute_smart_opts(thumb_path: Path) -> dict[str, str]:
    """Analyse *thumb_path* and return ``{"mode": ..., "variant": ...}``."""
    from caelestia.utils.colourfulness import get_variant

    with Image.open(thumb_path) as img:
        variant = get_variant(img)
        img.thumbnail((1, 1), Image.LANCZOS)
        hct = Hct.from_int(argb_from_rgb(*img.getpixel((0, 0))))

    return {
        "variant": variant,
        "mode": "light" if hct.tone > 60 else "dark",
    }


def get_smart_opts(wall: Path, cache: Path) -> dict[str, str]:
    """Return smart opts for *wall*, reading from *cache* when available.

    The cache entry is a tiny JSON file (``smart.json``) stored alongside the
    thumbnail.  On a cache miss the opts are computed from the thumbnail and
    written back before returning.
    """
    opts_cache = cache / "smart.json"
    try:
        return json.loads(opts_cache.read_text())
    except (IOError, json.JSONDecodeError):
        pass

    opts = _compute_smart_opts(get_thumb(wall, cache))

    opts_cache.parent.mkdir(parents=True, exist_ok=True)
    opts_cache.write_text(json.dumps(opts))
    return opts
