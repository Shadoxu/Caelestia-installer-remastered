"""Colour-scheme package — re-exports everything for backward compatibility.

Existing code that imports from ``caelestia.utils.scheme`` continues to work
unchanged.  New code should import directly from the sub-modules.
"""
from caelestia.utils.scheme.model import Scheme, get_scheme, get_scheme_path
from caelestia.utils.scheme.registry import (
    get_scheme_flavours,
    get_scheme_modes,
    get_scheme_names,
    read_colours_from_file,
    scheme_variants,
)

__all__ = [
    "Scheme",
    "get_scheme",
    "get_scheme_path",
    "get_scheme_flavours",
    "get_scheme_modes",
    "get_scheme_names",
    "read_colours_from_file",
    "scheme_variants",
]
