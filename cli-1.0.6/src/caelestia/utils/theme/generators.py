"""Template rendering and ANSI terminal-sequence generation."""
from __future__ import annotations

import re
from pathlib import Path

from caelestia.utils.colour import get_dynamic_colours


def gen_conf(colours: dict[str, str]) -> str:
    """Render colours as Hyprland ``$var = value`` config lines."""
    return "".join(f"${name} = {colour}\n" for name, colour in colours.items())


def gen_scss(colours: dict[str, str]) -> str:
    """Render colours as SCSS ``$var: #value;`` declarations."""
    return "".join(f"${name}: #{colour};\n" for name, colour in colours.items())


def gen_replace(colours: dict[str, str], template: Path, hash: bool = False) -> str:
    """Fill ``{{ $name }}`` placeholders in *template* with colour values."""
    content = template.read_text()
    for name, colour in colours.items():
        content = content.replace(f"{{{{ ${name} }}}}", f"#{colour}" if hash else colour)
    return content


def gen_replace_dynamic(colours: dict[str, str], template: Path, mode: str) -> str:
    """Fill ``{{ col.form }}`` and ``{{ mode }}`` placeholders using dynamic colour objects."""
    _DOT_FIELD  = r"\{\{((?:(?!\{\{|\}\}).)*)\}\}"
    _MODE_FIELD = r"\{\{\s*mode\s*\}\}"

    colours_dyn = get_dynamic_colours(colours)

    def _fill(match: re.Match) -> str:
        parts = match.group(1).strip().split(".")
        if len(parts) != 2:
            return match.group()
        col, form = parts
        if col not in colours_dyn or not hasattr(colours_dyn[col], form):
            return match.group()
        return getattr(colours_dyn[col], form)

    filled = re.sub(_DOT_FIELD, _fill, template.read_text())
    return re.sub(_MODE_FIELD, mode, filled)


def c2s(colour: str, *indices: int) -> str:
    """Convert a hex colour to an OSC ANSI escape sequence.

    Example: ``c2s("ffffff", 11)`` → ``\\x1b]11;rgb:ff/ff/ff\\x1b\\\\``
    """
    r, g, b = colour[0:2], colour[2:4], colour[4:6]
    return f"\x1b]{';'.join(map(str, indices))};rgb:{r}/{g}/{b}\x1b\\"


def gen_sequences(colours: dict[str, str]) -> str:
    """Build a concatenated ANSI sequence string for all 19 terminal colour slots.

    Slot assignments:
      10 = foreground, 11 = background, 12 = cursor, 17 = selection,
      4;0-7 = normal, 4;8-15 = bright, 4;16-18 = primary/secondary/tertiary.
    """
    return (
        c2s(colours["onSurface"], 10)
        + c2s(colours["surface"], 11)
        + c2s(colours["secondary"], 12)
        + c2s(colours["secondary"], 17)
        + "".join(c2s(colours[f"term{i}"], 4, i) for i in range(16))
        + c2s(colours["primary"], 4, 16)
        + c2s(colours["secondary"], 4, 17)
        + c2s(colours["tertiary"], 4, 18)
    )
