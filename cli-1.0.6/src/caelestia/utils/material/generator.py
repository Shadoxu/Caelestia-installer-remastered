"""Material You colour-scheme generator.

Takes a primary HCT seed colour + a Scheme config object and produces a full
hex-colour dict that covers Material Dynamic Colours, harmonized terminal
colours, named palette colours, KDE semantic colours, Catppuccin-compat
aliases, and extended success tokens.

Public API:
    gen_scheme(scheme, primary: Hct) -> dict[str, str]
"""
from __future__ import annotations

from materialyoucolor.blend import Blend
from materialyoucolor.dynamiccolor.material_dynamic_colors import MaterialDynamicColors
from materialyoucolor.hct import Hct
from materialyoucolor.scheme.scheme_content import SchemeContent
from materialyoucolor.scheme.scheme_expressive import SchemeExpressive
from materialyoucolor.scheme.scheme_fidelity import SchemeFidelity
from materialyoucolor.scheme.scheme_fruit_salad import SchemeFruitSalad
from materialyoucolor.scheme.scheme_monochrome import SchemeMonochrome
from materialyoucolor.scheme.scheme_neutral import SchemeNeutral
from materialyoucolor.scheme.scheme_rainbow import SchemeRainbow
from materialyoucolor.scheme.scheme_tonal_spot import SchemeTonalSpot
from materialyoucolor.scheme.scheme_vibrant import SchemeVibrant
from materialyoucolor.utils.math_utils import (
    difference_degrees,
    rotation_direction,
    sanitize_degrees_double,
)

try:
    from materialyoucolor.dynamiccolor.dynamic_scheme import DynamicScheme
except ImportError:
    from materialyoucolor.scheme.dynamic_scheme import DynamicScheme

from caelestia.utils.material._palettes import (
    COLOUR_NAMES,
    K_COLOURS,
    NAMED_DARK,
    NAMED_LIGHT,
    TERM_DARK,
    TERM_LIGHT,
)

# ---------------------------------------------------------------------------
# Variant → DynamicScheme class map
# ---------------------------------------------------------------------------

_VARIANT_MAP: dict[str, type] = {
    "content":    SchemeContent,
    "expressive": SchemeExpressive,
    "fidelity":   SchemeFidelity,
    "fruitsalad": SchemeFruitSalad,
    "monochrome": SchemeMonochrome,
    "neutral":    SchemeNeutral,
    "rainbow":    SchemeRainbow,
    "tonalspot":  SchemeTonalSpot,
    "vibrant":    SchemeVibrant,
}


def _variant_class(variant: str) -> type:
    return _VARIANT_MAP.get(variant, SchemeVibrant)


# ---------------------------------------------------------------------------
# HCT colour-math helpers
# ---------------------------------------------------------------------------

def _mix(a: Hct, b: Hct, weight: float) -> Hct:
    return Hct.from_int(Blend.cam16_ucs(a.to_int(), b.to_int(), weight))


def _lighten(colour: Hct, amount: float) -> Hct:
    diff = (100 - colour.tone) * amount
    return Hct.from_hct(colour.hue, colour.chroma + diff / 5, colour.tone + diff)


def _darken(colour: Hct, amount: float) -> Hct:
    diff = colour.tone * amount
    return Hct.from_hct(colour.hue, colour.chroma - diff / 5, colour.tone - diff)


def _grayscale(colour: Hct, light: bool) -> Hct:
    c = _darken(colour, 0.35) if light else _lighten(colour, 0.65)
    c.chroma = 0
    return c


def _harmonize(src: Hct, target: Hct, tone_boost: float) -> Hct:
    diff  = difference_degrees(src.hue, target.hue)
    rot   = min(diff * 0.8, 100)
    hue   = sanitize_degrees_double(src.hue + rot * rotation_direction(src.hue, target.hue))
    return Hct.from_hct(hue, src.chroma, src.tone * (1 + tone_boost))


# ---------------------------------------------------------------------------
# Material Dynamic Colours extraction
# ---------------------------------------------------------------------------

def _extract_material_colours(primary_scheme: DynamicScheme) -> dict[str, Hct]:
    """Return all Material Dynamic Colour tokens as a name→HCT dict."""
    colours: dict[str, Hct] = {}
    dyn = MaterialDynamicColors()
    if hasattr(dyn, "all_colors"):               # materialyoucolor-python ≥ 3.0
        for c in dyn.all_colors:
            colours[c.name] = c.get_hct(primary_scheme)
    else:
        for attr in vars(MaterialDynamicColors):
            c = getattr(MaterialDynamicColors, attr)
            if hasattr(c, "get_hct"):
                colours[attr] = c.get_hct(primary_scheme)
    return colours


def _backfill_palette_key_aliases(colours: dict[str, Hct]) -> None:
    """Add snake_case aliases for camelCase palette-key colours (≥ 3.0 compat)."""
    if "primaryPaletteKeyColor" not in colours:
        return
    for name in ("primary", "secondary", "tertiary", "neutral"):
        colours[f"{name}_paletteKeyColor"] = colours[f"{name}PaletteKeyColor"]
    colours["neutral_variant_paletteKeyColor"] = colours["neutralVariantPaletteKeyColor"]


# ---------------------------------------------------------------------------
# Per-category harmonization passes
# ---------------------------------------------------------------------------

def _apply_terminal_colours(
    colours: dict[str, Hct], light: bool, monochrome: bool
) -> None:
    palette = TERM_LIGHT if light else TERM_DARK
    primary = colours["primary_paletteKeyColor"]
    for i, hct in enumerate(palette):
        if monochrome:
            colours[f"term{i}"] = _grayscale(hct, light)
        else:
            boost = (0.35 if i < 8 else 0.2) * (-1 if light else 1)
            colours[f"term{i}"] = _harmonize(hct, primary, boost)


def _apply_named_colours(
    colours: dict[str, Hct], light: bool, monochrome: bool
) -> None:
    palette = NAMED_LIGHT if light else NAMED_DARK
    primary = colours["primary_paletteKeyColor"]
    for i, hct in enumerate(palette):
        name = COLOUR_NAMES[i]
        if monochrome:
            colours[name] = _grayscale(hct, light)
        else:
            colours[name] = _harmonize(hct, primary, -0.2 if light else 0.05)


def _apply_k_colours(
    colours: dict[str, Hct], monochrome: bool, light: bool
) -> None:
    for entry in K_COLOURS:
        name = entry["name"]
        colours[name] = _harmonize(entry["hct"], colours["primary"], 0.1)
        colours[f"{name}Selection"] = _harmonize(
            entry["hct"], colours["onPrimaryFixedVariant"], 0.1
        )
        if monochrome:
            colours[name] = _grayscale(colours[name], light)
            colours[f"{name}Selection"] = _grayscale(colours[f"{name}Selection"], light)


# ---------------------------------------------------------------------------
# Post-processing passes
# ---------------------------------------------------------------------------

def _apply_neutral_desaturation(colours: dict[str, Hct]) -> None:
    for hct in colours.values():
        hct.chroma -= 15


def _apply_hard_flavour(colours: dict[str, Hct], light: bool) -> None:
    """Darken (dark mode) or lighten (light mode) surfaces for the 'hard' flavour."""
    surface_keys = ["background"] + [k for k in colours if k.startswith("surface")]
    for key in surface_keys:
        colours[key] = _lighten(colours[key], 0.4) if light else _darken(colours[key], 0.8)
    colours["term0"] = _lighten(colours["term0"], 0.4) if light else _darken(colours["term0"], 0.9)

    for prefix in ("overlay", "surface", "base", "mantle", "crust"):
        for i in range(3):
            key = f"{prefix}{i}"
            if key in colours:
                colours[key] = (
                    _lighten(colours[key], 0.4) if light else _darken(colours[key], 0.8)
                )
    for key in ("base", "mantle", "crust"):
        if key in colours:
            colours[key] = (
                _lighten(colours[key], 0.4) if light else _darken(colours[key], 0.9)
            )


def _add_catppuccin_aliases(colours: dict[str, Hct]) -> None:
    """Add FIXME deprecated aliases expected by older templates."""
    surf    = colours["surface"]
    outline = colours["outline"]
    colours["text"]     = colours["onBackground"]
    colours["subtext1"] = colours["onSurfaceVariant"]
    colours["subtext0"] = colours["outline"]
    for i, w in enumerate((0.86, 0.71, 0.57, 0.43, 0.29, 0.14)):
        colours[f"overlay{i // 2 + (0 if i < 3 else 3)}"] = _mix(surf, outline, w)
    # simpler naming used in practice
    colours["overlay2"] = _mix(surf, outline, 0.86)
    colours["overlay1"] = _mix(surf, outline, 0.71)
    colours["overlay0"] = _mix(surf, outline, 0.57)
    colours["surface2"] = _mix(surf, outline, 0.43)
    colours["surface1"] = _mix(surf, outline, 0.29)
    colours["surface0"] = _mix(surf, outline, 0.14)
    colours["base"]   = surf
    colours["mantle"] = _darken(surf, 0.03)
    colours["crust"]  = _darken(surf, 0.05)


def _add_success_tokens(colours: dict[str, str], light: bool) -> None:
    """Inject extended success semantic tokens (already hex at this point)."""
    if light:
        colours.update({
            "success": "4F6354", "onSuccess": "FFFFFF",
            "successContainer": "D1E8D5", "onSuccessContainer": "0C1F13",
        })
    else:
        colours.update({
            "success": "B5CCBA", "onSuccess": "213528",
            "successContainer": "374B3E", "onSuccessContainer": "D1E9D6",
        })


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def gen_scheme(scheme, primary: Hct) -> dict[str, str]:
    """Generate a full hex-colour dict from *scheme* config and *primary* HCT seed.

    Pipeline:
      1. Build Material Dynamic Colours from the chosen variant + primary.
      2. Harmonize terminal and named palette colours toward the primary.
      3. Harmonize KDE semantic colours.
      4. Apply neutral desaturation or hard-flavour darkening if configured.
      5. Add Catppuccin-compat aliases (deprecated).
      6. Serialise all HCT values to 6-char hex strings.
      7. Inject extended success tokens.
    """
    light      = scheme.mode == "light"
    monochrome = scheme.variant == "monochrome"

    primary_scheme = _variant_class(scheme.variant)(primary, not light, 0)
    colours: dict[str, Hct] = _extract_material_colours(primary_scheme)
    _backfill_palette_key_aliases(colours)

    _apply_terminal_colours(colours, light, monochrome)
    _apply_named_colours(colours, light, monochrome)
    _apply_k_colours(colours, monochrome, light)

    if scheme.variant == "neutral":
        _apply_neutral_desaturation(colours)

    _add_catppuccin_aliases(colours)

    if scheme.flavour == "hard":
        _apply_hard_flavour(colours, light)

    hex_colours: dict[str, str] = {k: hex(v.to_int())[4:] for k, v in colours.items()}
    _add_success_tokens(hex_colours, light)

    return hex_colours
