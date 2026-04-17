"""Resizer subcommand — window resizer daemon and one-shot resize utility.

Package layout
--------------
rule.py     WindowRule dataclass + pattern matching
actions.py  apply_window_actions + apply_pip
daemon.py   ResizerDaemon (event loop)
__init__.py Command entry point + register_parser
"""
from __future__ import annotations

import json
from argparse import Namespace

from caelestia.utils import hypr
from caelestia.utils.logging import log_message
from caelestia.utils.paths import user_config_path
from caelestia.subcommands.resizer.rule import DEFAULT_RULES, WindowRule, match_rule
from caelestia.subcommands.resizer.actions import apply_pip, apply_window_actions
from caelestia.subcommands.resizer.daemon import ResizerDaemon


def register_parser(subparsers) -> None:
    p = subparsers.add_parser("resizer", help="window resizer daemon")
    p.set_defaults(cls=Command)
    p.add_argument("-d", "--daemon",  action="store_true", help="start the resizer daemon")
    p.add_argument("pattern",    nargs="?", help="pattern to match ('active' or 'pip' for quick modes)")
    p.add_argument("match_type", nargs="?", metavar="match_type",
                   choices=["titleContains", "titleExact", "titleRegex", "initialTitle"],
                   help="type of pattern matching")
    p.add_argument("width",   nargs="?", help="width to resize to")
    p.add_argument("height",  nargs="?", help="height to resize to")
    p.add_argument("actions", nargs="?", help="comma-separated actions (float,center,pip)")


def _load_rules() -> list[WindowRule]:
    try:
        cfg = json.loads(user_config_path.read_text())
        rules_cfg = cfg.get("resizer", {}).get("rules", [])
        if rules_cfg:
            return [
                WindowRule(r["name"], r["matchType"], r["width"], r["height"], r["actions"])
                for r in rules_cfg
            ]
    except (json.JSONDecodeError, KeyError):
        log_message("ERROR: invalid resizer config — using defaults")
    except FileNotFoundError:
        pass
    return DEFAULT_RULES


class Command:
    """Entry point for ``caelestia resizer``."""

    def __init__(self, args: Namespace) -> None:
        self.args = args
        self.rules = _load_rules()

    def run(self) -> None:
        if self.args.daemon:
            ResizerDaemon(self.rules).run()
        elif getattr(self.args, "pattern", None) == "pip":
            self._run_pip()
        elif all(getattr(self.args, a, None) for a in ("pattern", "match_type", "width", "height", "actions")):
            self._run_one_shot()
        else:
            print("Resizer: use --daemon, 'pip', or provide pattern match_type width height actions")

    # ----------------------------------------------------------------- private

    def _run_pip(self) -> None:
        """Apply PiP to the currently active floating window."""
        try:
            win = hypr.message("activewindow")
            if not isinstance(win, dict) or not win.get("address", "").startswith("0x"):
                print("ERROR: no active window found")
                return
            if not win.get("floating", False):
                print(f"Window '{win.get('title','')}' is not floating — make it floating first.")
                return
            print(f"Applying PiP to '{win.get('title', '')}'…")
            apply_pip(win["address"][2:])
            print("Done.")
        except Exception as e:
            print(f"ERROR: {e}")

    def _run_one_shot(self) -> None:
        """Apply a one-shot rule to all matching windows (or just the active one)."""
        actions = self.args.actions.split(",") if self.args.actions else []
        rule = WindowRule(self.args.pattern, self.args.match_type,
                          self.args.width, self.args.height, actions)

        if rule.name.lower() == "active":
            self._apply_to_active(rule)
            return

        clients = hypr.message("clients") or []
        matches = [
            c for c in clients
            if isinstance(c, dict) and match_rule([rule], c.get("title",""), c.get("initialTitle",""))
        ]

        if not matches:
            print(f"No windows matched '{rule.name}' ({rule.match_type})")
            return

        ok = sum(apply_window_actions(c["address"][2:], rule.width, rule.height, rule.actions) for c in matches)
        print(f"Applied to {ok}/{len(matches)} window(s)")

    def _apply_to_active(self, rule: WindowRule) -> None:
        try:
            win = hypr.message("activewindow")
            if not isinstance(win, dict) or not win.get("address", "").startswith("0x"):
                print("ERROR: no active window")
                return
            success = apply_window_actions(win["address"][2:], rule.width, rule.height, rule.actions)
            print("Done." if success else "Failed.")
        except Exception as e:
            print(f"ERROR: {e}")
