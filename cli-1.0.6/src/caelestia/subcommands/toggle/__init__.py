"""Toggle subcommand — toggle special Hyprland workspaces."""
from __future__ import annotations

import shlex
import shutil
from argparse import Namespace

from caelestia.utils import hypr
from caelestia.subcommands.toggle.config import is_subset, load_config


def register_parser(subparsers) -> None:
    p = subparsers.add_parser("toggle", help="toggle a special workspace")
    p.set_defaults(cls=Command)
    p.add_argument("workspace", help="the workspace to toggle")


class Command:
    """Toggle (or spawn into) a named Hyprland special workspace."""

    def __init__(self, args: Namespace) -> None:
        self.args = args
        self.cfg = load_config()
        self._clients: list[dict] | None = None

    # ------------------------------------------------------------------ public

    def run(self) -> None:
        if self.args.workspace == "specialws":
            self._toggle_active_special()
            return

        spawned = False
        if self.args.workspace in self.cfg:
            for client in self.cfg[self.args.workspace].values():
                if client.get("enable") and self._handle_client(client):
                    spawned = True

        if not spawned:
            hypr.dispatch("togglespecialworkspace", self.args.workspace)

    # ----------------------------------------------------------------- private

    def _clients(self) -> list[dict]:
        if self._clients is None:
            self._clients = hypr.message("clients")
        return self._clients

    def _selector(self, client_cfg: dict):
        """Return a callable that matches Hyprland client dicts against *client_cfg*."""
        def match(c: dict) -> bool:
            return any(is_subset(c, m) for m in client_cfg["match"])
        return match

    def _spawn(self, selector, command: list[str]) -> bool:
        if (command[0].endswith(".desktop") or shutil.which(command[0])) \
                and not any(selector(c) for c in self._clients()):
            hypr.dispatch("exec",
                          f"[workspace special:{self.args.workspace}] app2unit -- {shlex.join(command)}")
            return True
        return False

    def _move(self, selector) -> None:
        ws_name = f"special:{self.args.workspace}"
        for client in self._clients():
            if selector(client) and client["workspace"]["name"] != ws_name:
                hypr.dispatch("movetoworkspacesilent", f"{ws_name},address:{client['address']}")

    def _handle_client(self, client_cfg: dict) -> bool:
        selector = self._selector(client_cfg)
        spawned = False
        if client_cfg.get("command"):
            spawned = self._spawn(selector, client_cfg["command"])
        if client_cfg.get("move"):
            self._move(selector)
        return spawned

    def _toggle_active_special(self) -> None:
        focused = next(m for m in hypr.message("monitors") if m["focused"])
        name = focused["specialWorkspace"]["name"]
        hypr.dispatch("togglespecialworkspace", name[8:] or "special")
