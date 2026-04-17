"""Toggle workspace configuration — defaults, deep-merge map, and subset check."""
from __future__ import annotations

import json
from collections import ChainMap

from caelestia.utils.paths import user_config_path

# ---------------------------------------------------------------------------
# Default workspace registry
# ---------------------------------------------------------------------------

DEFAULT_CFG: dict = {
    "communication": {
        "discord":  {"enable": True, "match": [{"class": "discord"}],  "command": ["discord"],                    "move": True},
        "whatsapp": {"enable": True, "match": [{"class": "whatsapp"}],                                             "move": True},
    },
    "music": {
        "spotify": {
            "enable": True,
            "match":   [{"class": "Spotify"}, {"initialTitle": "Spotify"}, {"initialTitle": "Spotify Free"}],
            "command": ["spicetify", "watch", "-s"],
            "move":    True,
        },
        "feishin": {"enable": True, "match": [{"class": "feishin"}], "move": True},
    },
    "sysmon": {
        "btop": {
            "enable":  True,
            "match":   [{"class": "btop", "title": "btop", "workspace": {"name": "special:sysmon"}}],
            "command": ["foot", "-a", "btop", "-T", "btop", "fish", "-C", "exec btop"],
        },
    },
    "todo": {
        "todoist": {"enable": True, "match": [{"class": "Todoist"}], "command": ["todoist"], "move": True},
    },
}


def load_config() -> "DeepChainMap | dict":
    """Return user config deep-merged over ``DEFAULT_CFG``, falling back to defaults."""
    try:
        user = json.loads(user_config_path.read_text())["toggles"]
        return DeepChainMap(user, DEFAULT_CFG)
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return DEFAULT_CFG


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_subset(superset: dict, subset: dict) -> bool:
    """Return ``True`` if every key/value in *subset* is present in *superset*."""
    for key, value in subset.items():
        if key not in superset:
            return False
        sup_val = superset[key]
        if isinstance(value, dict):
            if not is_subset(sup_val, value):
                return False
        elif isinstance(value, str):
            if value not in sup_val:
                return False
        elif isinstance(value, (list, set)):
            if not set(value) <= set(sup_val):
                return False
        elif value != sup_val:
            return False
    return True


class DeepChainMap(ChainMap):
    """A ``ChainMap`` that recurses into nested dicts instead of shadowing them."""

    def __getitem__(self, key):
        values = [m[key] for m in self.maps if key in m]
        if not values:
            return self.__missing__(key)
        if isinstance(values[0], dict):
            return self.__class__(*values)
        return values[0]

    def __repr__(self) -> str:
        return repr(dict(self))
