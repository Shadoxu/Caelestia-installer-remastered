"""Per-application theme appliers.

Each ``apply_*`` function is decorated with ``@log_exception`` so that a failure
in one application never prevents the others from being themed.

Adding a new target: write one ``apply_foo`` function here and call it from
``caelestia.utils.theme.apply_colours``.
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from caelestia.utils.logging import log_exception
from caelestia.utils.paths import config_dir, data_dir, templates_dir, theme_dir, user_templates_dir
from caelestia.utils.theme.generators import gen_replace, gen_replace_dynamic, gen_scss
from caelestia.utils.theme.writers import write_file


@log_exception
def apply_hypr(conf: str) -> None:
    write_file(config_dir / "hypr/scheme/current.conf", conf)


@log_exception
def apply_discord(scss: str) -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        (Path(tmp_dir) / "_colours.scss").write_text(scss)
        css = subprocess.check_output(["sass", "-I", tmp_dir, templates_dir / "discord.scss"], text=True)
    for client in ("Equicord", "Vencord", "BetterDiscord", "equibop", "vesktop", "legcord"):
        write_file(config_dir / client / "themes/caelestia.theme.css", css)


@log_exception
def apply_pandora(colours: dict[str, str], mode: str) -> None:
    content = gen_replace(colours, templates_dir / "pandora.json", hash=True).replace("{{ $mode }}", mode)
    write_file(data_dir / "PandoraLauncher/themes/caelestia.json", content)


@log_exception
def apply_spicetify(colours: dict[str, str], mode: str) -> None:
    write_file(config_dir / "spicetify/Themes/caelestia/color.ini",
               gen_replace(colours, templates_dir / f"spicetify-{mode}.ini"))


@log_exception
def apply_fuzzel(colours: dict[str, str]) -> None:
    write_file(config_dir / "fuzzel/fuzzel.ini", gen_replace(colours, templates_dir / "fuzzel.ini"))


@log_exception
def apply_btop(colours: dict[str, str]) -> None:
    write_file(config_dir / "btop/themes/caelestia.theme",
               gen_replace(colours, templates_dir / "btop.theme", hash=True))
    subprocess.run(["killall", "-USR2", "btop"], stderr=subprocess.DEVNULL)


@log_exception
def apply_nvtop(colours: dict[str, str]) -> None:
    write_file(config_dir / "nvtop/nvtop.colors",
               gen_replace(colours, templates_dir / "nvtop.colors", hash=True))


@log_exception
def apply_htop(colours: dict[str, str]) -> None:
    write_file(config_dir / "htop/htoprc", gen_replace(colours, templates_dir / "htop.theme", hash=True))
    subprocess.run(["killall", "-USR2", "htop"], stderr=subprocess.DEVNULL)


@log_exception
def apply_gtk(colours: dict[str, str], mode: str) -> None:
    gtk_css    = gen_replace(colours, templates_dir / "gtk.css",    hash=True)
    thunar_css = gen_replace(colours, templates_dir / "thunar.css", hash=True)
    for ver in ("gtk-3.0", "gtk-4.0"):
        write_file(config_dir / ver / "gtk.css",    gtk_css)
        write_file(config_dir / ver / "thunar.css", thunar_css)
    subprocess.run(["dconf", "write", "/org/gnome/desktop/interface/gtk-theme",     "'adw-gtk3-dark'"])
    subprocess.run(["dconf", "write", "/org/gnome/desktop/interface/color-scheme",  f"'prefer-{mode}'"])
    subprocess.run(["dconf", "write", "/org/gnome/desktop/interface/icon-theme",    f"'Papirus-{mode.capitalize()}'"])
    _sync_papirus_colors(colours["primary"])


@log_exception
def apply_qt(colours: dict[str, str], mode: str) -> None:
    write_file(config_dir / "qtengine/caelestia.colors",
               gen_replace(colours, templates_dir / f"qt{mode}.colors", hash=True))
    config = (templates_dir / "qtengine.json").read_text().replace("{{ $mode }}", mode.capitalize())
    write_file(config_dir / "qtengine/config.json", config)


@log_exception
def apply_warp(colours: dict[str, str], mode: str) -> None:
    warp_mode = "darker" if mode == "dark" else "lighter"
    content = gen_replace(colours, templates_dir / "warp.yaml", hash=True).replace("{{ $warp_mode }}", warp_mode)
    write_file(data_dir / "warp-terminal/themes/caelestia.yaml", content)


@log_exception
def apply_cava(colours: dict[str, str]) -> None:
    write_file(config_dir / "cava/config", gen_replace(colours, templates_dir / "cava.conf", hash=True))
    subprocess.run(["killall", "-USR2", "cava"], stderr=subprocess.DEVNULL)


@log_exception
def apply_user_templates(colours: dict[str, str], mode: str) -> None:
    if not user_templates_dir.is_dir():
        return
    for file in user_templates_dir.iterdir():
        if file.is_file():
            write_file(theme_dir / file.name, gen_replace_dynamic(colours, file, mode))


# ---------------------------------------------------------------------------
# Papirus icon sync (helper for apply_gtk)
# ---------------------------------------------------------------------------

def _sync_papirus_colors(hex_color: str) -> None:
    """Sync Papirus folder icon colour to match the primary theme colour."""
    try:
        if subprocess.run(["which", "papirus-folders"], capture_output=True, check=False).returncode != 0:
            return
    except Exception:
        return

    papirus_roots = [
        Path("/usr/share/icons/Papirus"),
        Path("/usr/share/icons/Papirus-Dark"),
        Path.home() / ".local/share/icons/Papirus",
        Path.home() / ".icons/Papirus",
    ]
    if not any(p.exists() for p in papirus_roots):
        return

    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    max_v, min_v = max(r, g, b), min(r, g, b)
    brightness   = max_v
    saturation   = 0 if max_v == 0 else ((max_v - min_v) * 100) // max_v

    if saturation < 20:
        color = "black" if brightness < 85 else ("grey" if brightness < 170 else "white")
    elif saturation < 60 and brightness > 180:
        color = _hue_color(r, g, b, brightness, pale=True)
    else:
        color = _hue_color(r, g, b, brightness, pale=False)

    try:
        subprocess.Popen(["sudo", "-n", "papirus-folders", "-C", color, "-u"],
                         stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, start_new_session=True)
    except Exception:
        pass


def _hue_color(r: int, g: int, b: int, brightness: int, *, pale: bool) -> str:
    if b > r and b > g:
        r_ratio = (r * 100) // b if b else 0
        g_ratio = (g * 100) // b if b else 0
        if r_ratio > 70 and g_ratio > 70:
            return "blue" if abs(r - g) < 15 else ("violet" if r > g else "cyan")
        return "violet" if (r_ratio > 60 and r > g) else ("cyan" if (g_ratio > 60 and g > r) else "blue")
    if r > g and r > b:
        if g > b + 30:
            rg = (g * 100) // r if r else 0
            if pale:
                return "palebrown" if (rg > 70 and brightness < 220) else "paleorange"
            return "brown" if (rg > 70 and brightness < 180) else "orange"
        return "pink" if b > g + 20 else ("pink" if pale else "red")
    if g > r and g > b:
        return "yellow" if r > b + 30 else "green"
    return "grey"
