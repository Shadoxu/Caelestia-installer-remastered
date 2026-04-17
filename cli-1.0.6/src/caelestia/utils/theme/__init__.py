"""Theme package — orchestrates all per-application colour changes.

Public surface (backward-compatible):
    apply_colours(colours, mode)  — the only function callers need.

Internal layout:
    generators.py  — template rendering, ANSI sequence building
    writers.py     — atomic file writing, pseudo-terminal broadcasting
    appliers.py    — one apply_* function per supported application
"""
from __future__ import annotations

import fcntl
import json

from caelestia.utils.paths import c_state_dir, user_config_path
from caelestia.utils.theme.appliers import (
    apply_btop,
    apply_cava,
    apply_discord,
    apply_fuzzel,
    apply_gtk,
    apply_htop,
    apply_hypr,
    apply_nvtop,
    apply_pandora,
    apply_qt,
    apply_spicetify,
    apply_user_templates,
    apply_warp,
)
from caelestia.utils.theme.generators import gen_conf, gen_scss, gen_sequences
from caelestia.utils.theme.writers import apply_terms

__all__ = ["apply_colours"]

# ---------------------------------------------------------------------------
# Config key → applier mapping
# ---------------------------------------------------------------------------

def _load_cfg() -> dict:
    try:
        return json.loads(user_config_path.read_text()).get("theme", {})
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _enabled(cfg: dict, key: str) -> bool:
    return cfg.get(key, True)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def apply_colours(colours: dict[str, str], mode: str) -> None:
    """Apply *colours* and *mode* to every enabled application.

    Uses a file-based exclusive lock so concurrent calls (e.g. from the
    wallpaper hook and a manual ``caelestia scheme set``) don't race.
    """
    lock_file = c_state_dir / "theme.lock"
    c_state_dir.mkdir(parents=True, exist_ok=True)

    try:
        with open(lock_file, "w") as lock_fd:
            try:
                fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return  # another instance is already applying — skip

            cfg = _load_cfg()

            if _enabled(cfg, "enableTerm"):      apply_terms(gen_sequences(colours))
            if _enabled(cfg, "enableHypr"):      apply_hypr(gen_conf(colours))
            if _enabled(cfg, "enableDiscord"):   apply_discord(gen_scss(colours))
            if _enabled(cfg, "enableSpicetify"): apply_spicetify(colours, mode)
            if _enabled(cfg, "enablePandora"):   apply_pandora(colours, mode)
            if _enabled(cfg, "enableFuzzel"):    apply_fuzzel(colours)
            if _enabled(cfg, "enableBtop"):      apply_btop(colours)
            if _enabled(cfg, "enableNvtop"):     apply_nvtop(colours)
            if _enabled(cfg, "enableHtop"):      apply_htop(colours)
            if _enabled(cfg, "enableGtk"):       apply_gtk(colours, mode)
            if _enabled(cfg, "enableQt"):        apply_qt(colours, mode)
            if _enabled(cfg, "enableWarp"):      apply_warp(colours, mode)
            if _enabled(cfg, "enableCava"):      apply_cava(colours)
            apply_user_templates(colours, mode)

    finally:
        try:
            lock_file.unlink()
        except FileNotFoundError:
            pass
