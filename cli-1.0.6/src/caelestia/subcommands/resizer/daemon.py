"""Hyprland event listener that applies window rules as windows open/retitle."""
from __future__ import annotations

import socket
import time
from pathlib import Path

from caelestia.utils import hypr
from caelestia.utils.logging import log_message
from caelestia.subcommands.resizer.rule import WindowRule, match_rule
from caelestia.subcommands.resizer.actions import apply_window_actions

_RATE_LIMIT_SECS = 1.0


class ResizerDaemon:
    """Listens on Hyprland's event socket and applies rules to matching windows."""

    def __init__(self, rules: list[WindowRule]) -> None:
        self.rules = rules
        self._throttle: dict[str, float] = {}

    # ------------------------------------------------------------------ public

    def run(self) -> None:
        socket_path = Path(hypr.socket2_path)
        if not socket_path.exists():
            log_message(f"ERROR: Hyprland socket not found at {socket_path}")
            return

        log_message(f"Resizer daemon started — {len(self.rules)} rule(s) loaded")
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                sock.connect(hypr.socket2_path)
                log_message("Connected to Hyprland event socket")
                while True:
                    data = sock.recv(4096).decode()
                    if data:
                        for line in data.strip().splitlines():
                            if line:
                                self._dispatch(line)
        except KeyboardInterrupt:
            log_message("Resizer daemon stopped")
        except Exception as e:
            log_message(f"ERROR: {e}")

    # ----------------------------------------------------------------- private

    def _dispatch(self, event: str) -> None:
        if event.startswith("windowtitle"):
            self._on_title(event)
        elif event.startswith("openwindow"):
            self._on_open(event)

    def _throttled(self, window_id: str) -> bool:
        now = time.monotonic()
        if now < self._throttle.get(window_id, 0) + _RATE_LIMIT_SECS:
            log_message(f"Rate-limited: skipping 0x{window_id}")
            return True
        self._throttle[window_id] = now
        return False

    def _get_window_info(self, window_id: str) -> dict | None:
        try:
            return next(
                (c for c in hypr.message("clients")
                 if isinstance(c, dict) and c.get("address") == f"0x{window_id}"),
                None,
            )
        except Exception:
            return None

    def _apply_if_matched(self, window_id: str, title: str, initial_title: str) -> None:
        rule = match_rule(self.rules, title, initial_title)
        if not rule or self._throttled(window_id):
            return
        log_message(f"Rule '{rule.name}' matched window 0x{window_id}")
        apply_window_actions(window_id, rule.width, rule.height, rule.actions)

    @staticmethod
    def _parse_id(raw: str) -> str | None:
        """Strip leading ``>`` characters and validate as a hex window ID."""
        wid = raw.lstrip(">")
        if not all(c in "0123456789abcdefABCDEF" for c in wid):
            log_message(f"ERROR: invalid window ID: {wid!r}")
            return None
        return wid

    def _on_title(self, event: str) -> None:
        sep = ">>>" if ">>>" in event else ">>"
        try:
            raw_id = event.split(sep)[1].split(",")[0]
        except IndexError as e:
            log_message(f"ERROR: could not parse title event: {e}")
            return

        window_id = self._parse_id(raw_id)
        if window_id is None:
            return

        info = self._get_window_info(window_id)
        if not info:
            return

        title, initial = info.get("title", ""), info.get("initialTitle", "")
        log_message(f"DEBUG: 0x{window_id} — title='{title}' initial='{initial}'")
        self._apply_if_matched(window_id, title, initial)

    def _on_open(self, event: str) -> None:
        prefix = "openwindow>>>" if "openwindow>>>" in event else "openwindow>>"
        try:
            raw_id, _workspace, _cls, title = event[len(prefix):].split(",", 3)
        except ValueError as e:
            log_message(f"ERROR: could not parse openwindow event: {e}")
            return

        window_id = self._parse_id(raw_id)
        if window_id is None:
            return

        log_message(f"DEBUG: new window 0x{window_id} — title='{title}'")
        self._apply_if_matched(window_id, title, title)
