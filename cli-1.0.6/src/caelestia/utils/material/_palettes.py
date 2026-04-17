"""Static HCT colour palettes used when harmonizing terminal and named colours.

These lists are data, not logic — keeping them here lets generator.py stay
focused on colour-math algorithms.
"""
from __future__ import annotations

from materialyoucolor.hct import Hct


def _hct(hex_colour: str) -> Hct:
    return Hct.from_int(int(f"0xFF{hex_colour}", 16))


# ---------------------------------------------------------------------------
# Terminal palettes (indices 0–15 map to ANSI term0–term15)
# ---------------------------------------------------------------------------

TERM_LIGHT: list[Hct] = [
    _hct("FDF9F3"), _hct("FF6188"), _hct("A9DC76"), _hct("FC9867"),
    _hct("FFD866"), _hct("F47FD4"), _hct("78DCE8"), _hct("333034"),
    _hct("121212"), _hct("FF6188"), _hct("A9DC76"), _hct("FC9867"),
    _hct("FFD866"), _hct("F47FD4"), _hct("78DCE8"), _hct("333034"),
]

TERM_DARK: list[Hct] = [
    _hct("282828"), _hct("CC241D"), _hct("98971A"), _hct("D79921"),
    _hct("458588"), _hct("B16286"), _hct("689D6A"), _hct("A89984"),
    _hct("928374"), _hct("FB4934"), _hct("B8BB26"), _hct("FABD2F"),
    _hct("83A598"), _hct("D3869B"), _hct("8EC07C"), _hct("EBDBB2"),
]

# ---------------------------------------------------------------------------
# Named colour palettes (indices map to COLOUR_NAMES)
# ---------------------------------------------------------------------------

NAMED_LIGHT: list[Hct] = [
    _hct("dc8a78"), _hct("dd7878"), _hct("ea76cb"), _hct("8839ef"),
    _hct("d20f39"), _hct("e64553"), _hct("fe640b"), _hct("df8e1d"),
    _hct("40a02b"), _hct("179299"), _hct("04a5e5"), _hct("209fb5"),
    _hct("1e66f5"), _hct("7287fd"),
]

NAMED_DARK: list[Hct] = [
    _hct("f5e0dc"), _hct("f2cdcd"), _hct("f5c2e7"), _hct("cba6f7"),
    _hct("f38ba8"), _hct("eba0ac"), _hct("fab387"), _hct("f9e2af"),
    _hct("a6e3a1"), _hct("94e2d5"), _hct("89dceb"), _hct("74c7ec"),
    _hct("89b4fa"), _hct("b4befe"),
]

COLOUR_NAMES: list[str] = [
    "rosewater", "flamingo", "pink",     "mauve",
    "red",       "maroon",   "peach",    "yellow",
    "green",     "teal",     "sky",      "sapphire",
    "blue",      "lavender",
]

# ---------------------------------------------------------------------------
# KDE / Qt semantic colours
# ---------------------------------------------------------------------------

K_COLOURS: list[dict] = [
    {"name": "klink",     "hct": _hct("2980b9")},
    {"name": "kvisited",  "hct": _hct("9b59b6")},
    {"name": "knegative", "hct": _hct("da4453")},
    {"name": "kneutral",  "hct": _hct("f67400")},
    {"name": "kpositive", "hct": _hct("27ae60")},
]
