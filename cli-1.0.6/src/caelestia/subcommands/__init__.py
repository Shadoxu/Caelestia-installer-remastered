"""Subcommands package.

Defines the ``BaseCommand`` structural protocol that every command class must
satisfy.  Type-checkers use this for static verification; it is also
``@runtime_checkable`` so ``isinstance(obj, BaseCommand)`` works at runtime.

Adding a new command
--------------------
1. Create ``caelestia/subcommands/mycommand.py`` (or a ``mycommand/`` package).
2. Define a ``Command`` class that satisfies ``BaseCommand``.
3. Define ``register_parser(subparsers)`` at module level.
4. Add ``"mycommand"`` to ``_SUBCOMMANDS`` in ``caelestia/parser.py``.
"""
from __future__ import annotations

from argparse import Namespace
from typing import Protocol, runtime_checkable


@runtime_checkable
class BaseCommand(Protocol):
    def __init__(self, args: Namespace) -> None: ...
    def run(self) -> None: ...
