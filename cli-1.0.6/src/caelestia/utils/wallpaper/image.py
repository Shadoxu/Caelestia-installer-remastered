"""Low-level image helpers — validation, GIF extraction, and thumbnail cache.

Nothing in this module knows about schemes, themes, or Hyprland.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

from caelestia.utils.paths import compute_hash, wallpapers_cache_dir

# Supported image extensions (lowercase).
VALID_SUFFIXES: frozenset[str] = frozenset(
    {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".gif"}
)

_THUMB_SIZE = (128, 128)


def is_valid_image(path: Path) -> bool:
    """Return ``True`` if *path* is a file with a supported image extension."""
    return path.is_file() and path.suffix.lower() in VALID_SUFFIXES


def check_wall(wall: Path, filter_size: tuple[int, int], threshold: float) -> bool:
    """Return ``True`` if *wall* meets the minimum-size threshold for both axes."""
    with Image.open(wall) as img:
        w, h = img.size
        return w >= filter_size[0] * threshold and h >= filter_size[1] * threshold


def get_thumb(wall: Path, cache: Path) -> Path:
    """Return a 128×128 JPEG thumbnail for *wall*, generating it if not cached."""
    thumb = cache / "thumbnail.jpg"
    if not thumb.exists():
        with Image.open(wall) as img:
            img = img.convert("RGB")
            img.thumbnail(_THUMB_SIZE, Image.NEAREST)
            thumb.parent.mkdir(parents=True, exist_ok=True)
            img.save(thumb, "JPEG")
    return thumb


def convert_gif(wall: Path) -> Path:
    """Extract the first frame of *wall* (a GIF) to a PNG and return its path."""
    cache = wallpapers_cache_dir / compute_hash(wall)
    output = cache / "first_frame.png"
    if not output.exists():
        output.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(wall) as img:
            try:
                img.seek(0)
            except EOFError:
                pass
            img.convert("RGB").save(output, "PNG")
    return output


def cache_path_for(wall: Path) -> Path:
    """Return the per-wallpaper cache directory for *wall*."""
    return wallpapers_cache_dir / compute_hash(wall)
