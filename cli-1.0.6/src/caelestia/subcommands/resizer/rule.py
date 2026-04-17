"""WindowRule dataclass and title/class pattern matching."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from caelestia.utils.logging import log_message


@dataclass
class WindowRule:
    """Describes how to match and resize a window."""
    name:       str
    match_type: str          # titleContains | titleExact | titleRegex | initialTitle
    width:      str
    height:     str
    actions:    list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Default built-in rules
# ---------------------------------------------------------------------------

DEFAULT_RULES: list[WindowRule] = [
    WindowRule("(Bitwarden",                    "titleContains", "20%",  "54%",  ["float", "center"]),
    WindowRule("Sign in - Google Accounts",     "titleContains", "35%",  "65%",  ["float", "center"]),
    WindowRule("oauth",                         "titleContains", "30%",  "60%",  ["float", "center"]),
    WindowRule(r"^[Pp]icture(-| )in(-| )[Pp]icture$", "titleRegex", "", "",    ["pip"]),
]


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------

def match_rule(rules: list[WindowRule], title: str, initial_title: str) -> WindowRule | None:
    """Return the first rule in *rules* that matches *title* / *initial_title*."""
    for rule in rules:
        matched = False
        try:
            if rule.match_type == "initialTitle":
                matched = initial_title == rule.name
            elif rule.match_type == "titleContains":
                matched = rule.name in title
            elif rule.match_type == "titleExact":
                matched = title == rule.name
            elif rule.match_type == "titleRegex":
                matched = bool(re.search(rule.name, title))
        except re.error:
            log_message(f"ERROR: invalid regex pattern in rule '{rule.name}'")
        if matched:
            return rule
    return None
