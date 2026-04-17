"""Scheme subcommand — list, get, and set the active colour scheme."""
from __future__ import annotations

import json
from argparse import Namespace

from caelestia.utils.scheme import (
    Scheme,
    get_scheme,
    get_scheme_flavours,
    get_scheme_modes,
    get_scheme_names,
    scheme_variants,
)
from caelestia.utils.theme import apply_colours


def register_parser(subparsers) -> None:
    p = subparsers.add_parser("scheme", help="manage the colour scheme")
    sub = p.add_subparsers(title="subcommands")

    lp = sub.add_parser("list", help="list available schemes")
    lp.set_defaults(cls=List)
    lp.add_argument("-n", "--names",    action="store_true", help="list scheme names")
    lp.add_argument("-f", "--flavours", action="store_true", help="list scheme flavours")
    lp.add_argument("-m", "--modes",    action="store_true", help="list scheme modes")
    lp.add_argument("-v", "--variants", action="store_true", help="list scheme variants")

    gp = sub.add_parser("get", help="get scheme properties")
    gp.set_defaults(cls=Get)
    gp.add_argument("-n", "--name",    action="store_true", help="print the current scheme name")
    gp.add_argument("-f", "--flavour", action="store_true", help="print the current scheme flavour")
    gp.add_argument("-m", "--mode",    action="store_true", help="print the current scheme mode")
    gp.add_argument("-v", "--variant", action="store_true", help="print the current scheme variant")

    sp = sub.add_parser("set", help="set the current scheme")
    sp.set_defaults(cls=Set)
    sp.add_argument("--notify",        action="store_true",       help="send a notification on error")
    sp.add_argument("-r", "--random",  action="store_true",       help="switch to a random scheme")
    sp.add_argument("-n", "--name",    choices=get_scheme_names(), help="the name of the scheme to switch to")
    sp.add_argument("-f", "--flavour",                             help="the flavour to switch to")
    sp.add_argument("-m", "--mode",    choices=["dark", "light"],  help="the mode to switch to")
    sp.add_argument("-v", "--variant", choices=scheme_variants,    help="the variant to switch to")


# ---------------------------------------------------------------------------
# set
# ---------------------------------------------------------------------------

class Set:
    """Apply one or more scheme property changes."""

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        scheme = get_scheme()
        if self.args.notify:
            scheme.notify = True

        if self.args.random:
            scheme.set_random()
            apply_colours(scheme.colours, scheme.mode)
        elif self.args.name or self.args.flavour or self.args.mode or self.args.variant:
            if self.args.name:    scheme.name    = self.args.name
            if self.args.flavour: scheme.flavour = self.args.flavour
            if self.args.mode:    scheme.mode    = self.args.mode
            if self.args.variant: scheme.variant = self.args.variant
            apply_colours(scheme.colours, scheme.mode)
        else:
            print("No args given. Use --name, --flavour, --mode, --variant or --random to set a scheme")


# ---------------------------------------------------------------------------
# get
# ---------------------------------------------------------------------------

class Get:
    """Print one or more scheme properties of the active scheme."""

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        scheme = get_scheme()
        if self.args.name or self.args.flavour or self.args.mode or self.args.variant:
            if self.args.name:    print(scheme.name)
            if self.args.flavour: print(scheme.flavour)
            if self.args.mode:    print(scheme.mode)
            if self.args.variant: print(scheme.variant)
        else:
            print(scheme)


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------

class List:
    """List all available schemes, flavours, modes, or variants."""

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        flags = (self.args.names, self.args.flavours, self.args.modes, self.args.variants)
        if any(flags):
            self._print_specific(multi=sum(flags) > 1)
        else:
            print(json.dumps(self._all_colours_json()))

    # ----------------------------------------------------------------- private

    def _print_specific(self, *, multi: bool) -> None:
        def emit(label: str, items: list[str]) -> None:
            if multi:
                print(label, *items)
            else:
                print("\n".join(items))

        if self.args.names:    emit("Names:",    get_scheme_names())
        if self.args.flavours: emit("Flavours:", get_scheme_flavours())
        if self.args.modes:    emit("Modes:",    get_scheme_modes())
        if self.args.variants: emit("Variants:", scheme_variants)

    def _all_colours_json(self) -> dict:
        """Build a nested dict of all scheme × flavour → colour maps."""
        current = get_scheme()
        result: dict = {}

        for name in get_scheme_names():
            result[name] = {}
            for flavour in get_scheme_flavours(name):
                s = Scheme({
                    "name":    name,
                    "flavour": flavour,
                    "mode":    current.mode,
                    "variant": current.variant,
                    "colours": current.colours,
                })
                # Fall back to first available mode if current mode is absent
                modes = get_scheme_modes(name, flavour)
                if s.mode not in modes:
                    s._mode = modes[0]
                try:
                    s._update_colours()
                    result[name][flavour] = s.colours
                except ValueError:
                    pass  # dynamic scheme with no wallpaper set — skip silently

        return result
