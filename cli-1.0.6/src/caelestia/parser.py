"""CLI entry point — discovers subcommands and builds the argument parser.

Adding a new subcommand
-----------------------
1. Create ``caelestia/subcommands/mycommand.py`` (or ``mycommand/`` package).
2. Define ``register_parser(subparsers)`` and a ``Command`` class in it.
3. Add the module name string to ``_SUBCOMMANDS`` below — nothing else changes.
"""
from __future__ import annotations

import argparse
import importlib

# ---------------------------------------------------------------------------
# Subcommand registry — the only place that needs editing when adding a command
# ---------------------------------------------------------------------------

_SUBCOMMANDS = [
    "shell",
    "toggle",
    "scheme",
    "screenshot",
    "record",
    "clipboard",
    "emoji",
    "wallpaper",
    "resizer",
]


def parse_args() -> tuple[argparse.ArgumentParser, argparse.Namespace]:
    parser = argparse.ArgumentParser(
        prog="caelestia",
        description="Main control script for the Caelestia dotfiles",
    )
    parser.add_argument("-v", "--version", action="store_true", help="print the current version")

    subparsers = parser.add_subparsers(
        title="subcommands",
        description="valid subcommands",
        metavar="COMMAND",
        help="the subcommand to run",
    )

    for name in _SUBCOMMANDS:
        module = importlib.import_module(f"caelestia.subcommands.{name}")
        module.register_parser(subparsers)

    return parser, parser.parse_args()
