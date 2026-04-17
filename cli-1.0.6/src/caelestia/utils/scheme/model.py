"""Scheme data model and active-scheme cache."""
from __future__ import annotations

import json
import random
from pathlib import Path

from caelestia.utils.notify import notify
from caelestia.utils.paths import atomic_dump, scheme_data_dir, scheme_path
from caelestia.utils.scheme.registry import (
    get_scheme_flavours,
    get_scheme_modes,
    get_scheme_names,
    read_colours_from_file,
)


class Scheme:
    """Represents the active colour scheme; property setters validate and persist changes."""

    _name: str
    _flavour: str
    _mode: str
    _variant: str
    _colours: dict[str, str]
    notify: bool

    def __init__(self, data: dict[str, str] | None) -> None:
        if data is None:
            self._name = "catppuccin"
            self._flavour = "mocha"
            self._mode = "dark"
            self._variant = "tonalspot"
            self._colours = read_colours_from_file(self.get_colours_path())
        else:
            self._name = data["name"]
            self._flavour = data["flavour"]
            self._mode = data["mode"]
            self._variant = data["variant"]
            self._colours = data["colours"]
        self.notify = False

    # ---------------------------------------------------------------- properties

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        if name == self._name:
            return
        if name not in get_scheme_names():
            if self.notify:
                notify("-u", "critical", "Unable to set scheme",
                       f'"{name}" is not a valid scheme.\nValid schemes are: {get_scheme_names()}')
            raise ValueError(f"Invalid scheme name: {name}")
        self._name = name
        self._check_flavour()
        self._check_mode()
        self._update_colours()
        self.save()

    @property
    def flavour(self) -> str:
        return self._flavour

    @flavour.setter
    def flavour(self, flavour: str) -> None:
        if flavour == self._flavour:
            return
        valid = get_scheme_flavours(self.name)
        if flavour not in valid:
            if self.notify:
                notify("-u", "critical", "Unable to set scheme flavour",
                       f'"{flavour}" is not a valid flavour of scheme "{self.name}".\nValid flavours are: {valid}')
            raise ValueError(f'Invalid scheme flavour: "{flavour}". Valid flavours: {valid}')
        self._flavour = flavour
        self._check_mode()
        self.update_colours()

    @property
    def mode(self) -> str:
        return self._mode

    @mode.setter
    def mode(self, mode: str) -> None:
        if mode == self._mode:
            return
        valid = get_scheme_modes(self.name, self.flavour)
        if mode not in valid:
            if self.notify:
                notify("-u", "critical", "Unable to set scheme mode",
                       f'Scheme "{self.name} {self.flavour}" does not have a {mode} mode.')
            raise ValueError(f'Invalid scheme mode: "{mode}". Valid modes: {valid}')
        self._mode = mode
        self.update_colours()

    @property
    def variant(self) -> str:
        return self._variant

    @variant.setter
    def variant(self, variant: str) -> None:
        if variant == self._variant:
            return
        self._variant = variant
        self.update_colours()

    @property
    def colours(self) -> dict[str, str]:
        return self._colours

    # ------------------------------------------------------------------ public

    def get_colours_path(self) -> Path:
        return (scheme_data_dir / self.name / self.flavour / self.mode).with_suffix(".txt")

    def save(self) -> None:
        scheme_path.parent.mkdir(parents=True, exist_ok=True)
        atomic_dump(scheme_path, {
            "name": self.name, "flavour": self.flavour,
            "mode": self.mode, "variant": self.variant, "colours": self.colours,
        })

    def set_random(self) -> None:
        self._name = random.choice(get_scheme_names())
        self._flavour = random.choice(get_scheme_flavours(self.name))
        self._mode = random.choice(get_scheme_modes(self.name, self.flavour))
        self.update_colours()

    def update_colours(self) -> None:
        self._update_colours()
        self.save()

    # ----------------------------------------------------------------- private

    def _check_flavour(self) -> None:
        flavours = get_scheme_flavours(self.name)
        if self._flavour not in flavours:
            self._flavour = flavours[0]

    def _check_mode(self) -> None:
        modes = get_scheme_modes(self.name, self.flavour)
        if self._mode not in modes:
            self._mode = modes[0]

    def _update_colours(self) -> None:
        if self.name == "dynamic":
            from caelestia.utils.material import get_colours_for_image  # lazy: heavy dep
            try:
                self._colours = get_colours_for_image()
            except FileNotFoundError:
                msg = "No wallpaper set. Please set a wallpaper via `caelestia wallpaper` before setting a dynamic scheme."
                if self.notify:
                    notify("-u", "critical", "Unable to set dynamic scheme", msg)
                raise ValueError(msg)
        else:
            self._colours = read_colours_from_file(self.get_colours_path())

    def __str__(self) -> str:
        colour_lines = "\n        ".join(
            f"{n}: \x1b[38;2;{int(c[0:2],16)};{int(c[2:4],16)};{int(c[4:6],16)}m{c}\x1b[0m"
            for n, c in self.colours.items()
        )
        return (
            f"Current scheme:\n"
            f"    Name: {self.name}\n"
            f"    Flavour: {self.flavour}\n"
            f"    Mode: {self.mode}\n"
            f"    Variant: {self.variant}\n"
            f"    Colours:\n"
            f"        {colour_lines}"
        )


# ---------------------------------------------------------------------------
# Active-scheme cache
# ---------------------------------------------------------------------------

_scheme: Scheme | None = None


def get_scheme() -> Scheme:
    """Return the active scheme, loading and persisting the default if needed."""
    global _scheme
    if _scheme is None:
        try:
            _scheme = Scheme(json.loads(scheme_path.read_text()))
        except (IOError, json.JSONDecodeError):
            _scheme = Scheme(None)
            _scheme.save()
    return _scheme


def get_scheme_path() -> Path:
    return get_scheme().get_colours_path()
