"""Scheme discovery helpers — pure filesystem lookups, no Scheme instances."""
from __future__ import annotations

from pathlib import Path

from caelestia.utils.paths import scheme_data_dir

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

scheme_variants: list[str] = [
    "tonalspot",
    "vibrant",
    "expressive",
    "fidelity",
    "fruitsalad",
    "monochrome",
    "neutral",
    "rainbow",
    "content",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_colours_from_file(path: Path) -> dict[str, str]:
    """Parse a ``key value`` colour file into a dict."""
    return {k.strip(): v.strip() for k, v in (line.split(" ") for line in path.read_text().splitlines() if line)}


def get_scheme_names() -> list[str]:
    """Return all built-in scheme names plus the special 'dynamic' entry."""
    return [*(f.name for f in scheme_data_dir.iterdir() if f.is_dir()), "dynamic"]


def get_scheme_flavours(name: str | None = None) -> list[str]:
    """Return available flavours for *name* (defaults to the active scheme's name)."""
    if name is None:
        from caelestia.utils.scheme.model import get_scheme  # lazy — avoids circular import
        name = get_scheme().name
    if name == "dynamic":
        return ["default", "hard"]
    return [f.name for f in (scheme_data_dir / name).iterdir() if f.is_dir()]


def get_scheme_modes(name: str | None = None, flavour: str | None = None) -> list[str]:
    """Return available modes for *name* / *flavour* (defaults to the active scheme)."""
    if name is None:
        from caelestia.utils.scheme.model import get_scheme  # lazy — avoids circular import
        s = get_scheme()
        name, flavour = s.name, s.flavour
    if name == "dynamic":
        return ["light", "dark"]
    return [f.stem for f in (scheme_data_dir / name / flavour).iterdir() if f.is_file()]
