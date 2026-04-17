"""Dominant-colour scoring — picks the most perceptually salient HCT colour.

Public API:
    score(image_path) -> Hct
"""
from __future__ import annotations

from materialyoucolor.dislike.dislike_analyzer import DislikeAnalyzer
from materialyoucolor.hct import Hct
from materialyoucolor.quantize import ImageQuantizeCelebi
from materialyoucolor.utils.math_utils import sanitize_degrees_int

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_TARGET_CHROMA          = 48.0
_WEIGHT_PROPORTION      = 0.7
_WEIGHT_CHROMA_ABOVE    = 0.3
_WEIGHT_CHROMA_BELOW    = 0.1
_CUTOFF_CHROMA          = 5.0
_CUTOFF_EXCITED_PROP    = 0.01
_HUE_SPREAD             = 15     # ± hues considered "excited" neighbours


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _excited_proportions(hue_population: list[int], total: int) -> list[float]:
    """Spread each hue's proportion across its ±_HUE_SPREAD neighbours."""
    props = [0.0] * 360
    for hue, pop in enumerate(hue_population):
        proportion = pop / total
        for offset in range(-_HUE_SPREAD, _HUE_SPREAD + 1):
            props[int(sanitize_degrees_int(hue + offset))] += proportion
    return props


def _score_colors(
    colors_to_population: dict[int, int],
    excited_props: list[float],
    *,
    filter_enabled: bool,
) -> list[dict]:
    """Score every quantised colour; return descending-score list of dicts."""
    scored = []
    for rgb, _ in colors_to_population.items():
        hct  = Hct.from_int(rgb)
        hue  = int(sanitize_degrees_int(round(hct.hue)))
        prop = excited_props[hue]

        if filter_enabled and (
            hct.chroma < _CUTOFF_CHROMA or prop <= _CUTOFF_EXCITED_PROP
        ):
            continue

        chroma_weight = (
            _WEIGHT_CHROMA_BELOW if hct.chroma < _TARGET_CHROMA else _WEIGHT_CHROMA_ABOVE
        )
        item_score = (
            prop * 100.0 * _WEIGHT_PROPORTION
            + (hct.chroma - _TARGET_CHROMA) * chroma_weight
        )
        scored.append({"hct": hct, "score": item_score})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


def _pick_primary(scored: list[dict]) -> Hct | None:
    """Walk decreasing chroma cutoffs until a suitable primary candidate is found."""
    for cutoff in range(20, -1, -1):
        for item in scored:
            if item["hct"].chroma > cutoff and item["hct"].tone > cutoff * 3:
                return item["hct"]
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _score_population(
    colors_to_population: dict[int, int],
    *,
    filter_enabled: bool = True,
) -> Hct:
    """Pick the most salient HCT colour from a pixel→count dict."""
    hue_population: list[int] = [0] * 360
    total = 0
    for rgb, pop in colors_to_population.items():
        hct = Hct.from_int(rgb)
        hue_population[int(hct.hue)] += pop
        total += pop

    excited = _excited_proportions(hue_population, total)
    scored  = _score_colors(colors_to_population, excited, filter_enabled=filter_enabled)
    primary = _pick_primary(scored)

    if primary is None:
        # No candidate passed the filter — retry without it
        return _score_population(colors_to_population, filter_enabled=False)

    return DislikeAnalyzer.fix_if_disliked(primary)


def score(image_path: str) -> Hct:
    """Quantise *image_path* and return its dominant HCT colour."""
    population = ImageQuantizeCelebi(image_path, 1, 128)
    return _score_population(population)
