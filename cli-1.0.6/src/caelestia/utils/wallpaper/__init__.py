"""Wallpaper package — set, get, and analyse the active wallpaper.

Public surface (unchanged from the old flat module):
    get_wallpaper()          → str | None
    get_wallpapers(args)     → list[Path]
    get_colours_for_wall()   → dict
    set_wallpaper()          → None
    set_random()             → None

Internal layout:
    image.py   — is_valid_image, check_wall, get_thumb, convert_gif
    smart.py   — get_smart_opts (mode/variant auto-detection + cache)
"""
from __future__ import annotations

import json
import os
import random
import subprocess
from argparse import Namespace
from pathlib import Path

from caelestia.utils.hypr import message
from caelestia.utils.material import get_colours_for_image
from caelestia.utils.paths import (
    user_config_path,
    wallpaper_link_path,
    wallpaper_path_path,
    wallpaper_thumbnail_path,
    wallpapers_cache_dir,
)
from caelestia.utils.scheme import Scheme, get_scheme
from caelestia.utils.theme import apply_colours
from caelestia.utils.wallpaper.image import (
    cache_path_for,
    check_wall,
    convert_gif,
    get_thumb,
    is_valid_image,
)
from caelestia.utils.wallpaper.smart import get_smart_opts

__all__ = [
    "get_wallpaper",
    "get_wallpapers",
    "get_colours_for_wall",
    "set_wallpaper",
    "set_random",
    # image helpers re-exported for callers that imported them from the old flat module
    "is_valid_image",
    "check_wall",
    "get_thumb",
    "convert_gif",
]


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def get_wallpaper() -> str | None:
    """Return the path of the active wallpaper, or ``None`` if none is set."""
    try:
        return wallpaper_path_path.read_text()
    except IOError:
        return None


def get_wallpapers(args: Namespace) -> list[Path]:
    """Return all wallpaper paths under ``args.random``, optionally size-filtered."""
    directory = Path(args.random)
    if not directory.is_dir():
        return []

    walls = [f for f in directory.rglob("*") if is_valid_image(f)]

    if args.no_filter:
        return walls

    monitors = message("monitors")
    min_w = min(m["width"]  for m in monitors)
    min_h = min(m["height"] for m in monitors)
    return [w for w in walls if check_wall(w, (min_w, min_h), args.threshold)]


# ---------------------------------------------------------------------------
# Analyse
# ---------------------------------------------------------------------------

def get_colours_for_wall(wall: Path | str, no_smart: bool) -> dict:
    """Return a full colour dict for *wall* without changing the active wallpaper."""
    wall  = Path(wall)
    cache = cache_path_for(wall)

    if wall.suffix.lower() == ".gif":
        wall = convert_gif(wall)

    scheme = get_scheme()
    name   = "dynamic"

    if not no_smart:
        opts = get_smart_opts(wall, cache)
        scheme = Scheme({
            "name":    name,
            "flavour": scheme.flavour,
            "mode":    opts["mode"],
            "variant": opts["variant"],
            "colours": scheme.colours,
        })

    return {
        "name":    name,
        "flavour": scheme.flavour,
        "mode":    scheme.mode,
        "variant": scheme.variant,
        "colours": get_colours_for_image(get_thumb(wall, cache), scheme),
    }


# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------

def set_wallpaper(wall: Path | str, no_smart: bool) -> None:
    """Set *wall* as the active wallpaper and apply a matching colour scheme."""
    wall = Path(wall).resolve()

    if not is_valid_image(wall):
        raise ValueError(f'"{wall}" is not a valid image')

    # GIFs: use first frame for thumbnail / colour analysis only
    wall_cache_src = convert_gif(wall) if wall.suffix.lower() == ".gif" else wall
    cache          = cache_path_for(wall_cache_src)

    # Persist path + symlink
    wallpaper_path_path.parent.mkdir(parents=True, exist_ok=True)
    wallpaper_path_path.write_text(str(wall))
    wallpaper_link_path.parent.mkdir(parents=True, exist_ok=True)
    wallpaper_link_path.unlink(missing_ok=True)
    wallpaper_link_path.symlink_to(wall)

    # Persist thumbnail symlink
    thumb = get_thumb(wall_cache_src, cache)
    wallpaper_thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
    wallpaper_thumbnail_path.unlink(missing_ok=True)
    wallpaper_thumbnail_path.symlink_to(thumb)

    # Apply smart mode/variant if active scheme is dynamic
    scheme = get_scheme()
    if scheme.name == "dynamic" and not no_smart:
        opts           = get_smart_opts(wall_cache_src, cache)
        scheme.mode    = opts["mode"]
        scheme.variant = opts["variant"]

    scheme.update_colours()
    apply_colours(scheme.colours, scheme.mode)

    _run_post_hook(wall)


def set_random(args: Namespace) -> None:
    """Pick a random wallpaper from ``args.random`` and apply it."""
    walls = get_wallpapers(args)
    if not walls:
        raise ValueError("No valid wallpapers found")

    # Exclude the current wallpaper so we always switch to something new
    try:
        walls.remove(Path(wallpaper_path_path.read_text()))
    except (FileNotFoundError, ValueError):
        pass

    if not walls:
        raise ValueError("Only valid wallpaper is the current one")

    set_wallpaper(random.choice(walls), args.no_smart)


# ---------------------------------------------------------------------------
# Post-hook
# ---------------------------------------------------------------------------

def _run_post_hook(wall: Path) -> None:
    """Run the user-configured ``wallpaper.postHook`` shell command, if any."""
    try:
        cfg = json.loads(user_config_path.read_text()).get("wallpaper", {})
        if post_hook := cfg.get("postHook"):
            subprocess.run(
                post_hook,
                shell=True,
                env={**os.environ, "WALLPAPER_PATH": str(wall)},
                stderr=subprocess.DEVNULL,
            )
    except (FileNotFoundError, json.JSONDecodeError):
        pass
