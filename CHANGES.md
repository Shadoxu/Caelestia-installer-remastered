# Caelestia — Patched Release Notes

## v2.0.0 — Arch Linux Bug-Fix + Modular Installer Release

### Overview

This release ships a fully rewritten installer (`caelestia-install.sh`) and
applies 22 bug fixes across the dotfiles, PKGBUILD, and shell scripts.
All changes are backwards-compatible — the directory structure is unchanged.

---

### Installer (`caelestia-install.sh`)

Completely rewrites the original `install.fish` in **Bash** (no fish
dependency at install time) with the following improvements:

- **22 bugs fixed** (see INSTALLER-README.md for the full table)
- **Modular** — install individual config modules with `--modules=hypr,fish`
- **Auto-detects AUR helper** (yay or paru) or bootstraps one automatically
- **`--from-source`** mode builds CLI + shell from bundled source for developers
- **`--update`** fast path for AUR package updates without reinstalling configs
- **`--uninstall`** cleanly removes all symlinks
- **Lockfile** prevents concurrent installer runs
- **Spinner UI** with full log to `/tmp/caelestia-install.log`
- **Noconfirm** mode is now actually fully automatic (was broken in original)

---

### Bug Fixes — Config Files

#### `hypr/scripts/configs.fish` (Critical)
- **Bug:** `if _reload` executed `_reload` as a shell command, not tested its value.
  Every Hyprland start logged `fish: Unknown command: false`.
- **Fix:** Changed to `if test $_reload = true`. Also added
  `HYPRLAND_INSTANCE_SIGNATURE` guard so `hyprctl reload` isn't called
  outside an active session.

#### `hypr/hyprland/execs.conf`
- **Bug:** `gammastep` started without first launching the `geoclue` agent —
  gammastep has no location data and exits immediately.
- **Fix:** Added `exec-once = /usr/lib/geoclue-2.0/demos/agent` before
  gammastep, with a 2-second delay.
- **Bug:** `mpris-proxy` (from `bluez-utils`) started unconditionally —
  fails on systems without Bluetooth hardware, logging errors every boot.
- **Fix:** Wrapped in `command -v mpris-proxy && mpris-proxy || true`.

#### `hypr/hyprland/keybinds.conf`
- **Bug:** `exec = hyprctl dispatch submap global` used `exec` (runs on every
  reload) instead of `exec-once`. On some setups the submap was re-triggered
  mid-session, resetting state.
- **Fix:** Changed to `exec-once = hyprctl dispatch submap global`.

#### `fish/config.fish`
- **Bug:** `source ~/.config/caelestia/user-config.fish` used a hardcoded
  `~/.config` path instead of `$XDG_CONFIG_HOME`, breaking setups where
  XDG_CONFIG_HOME is set to a non-default location.
- **Bug:** `direnv hook fish | source` and `zoxide init fish | source`
  had no `command -v` guard — fish config errors on systems where these
  are not yet installed.
- **Fix:** Both issues corrected.

---

### Bug Fixes — PKGBUILD

**16 missing or misplaced packages** added/moved:

| Package | Direction | Reason |
|---|---|---|
| `fuzzel` | Added to `depends` | Clipboard/emoji picker (required by CLI) |
| `geoclue` | Added to `depends` | Location provider for gammastep |
| `gammastep` | Added to `depends` | Night light daemon (exec-once in execs.conf) |
| `grim` | Added to `depends` | Screenshot tool (required by CLI) |
| `slurp` | Added to `depends` | Area selection (required by CLI) |
| `sweet-cursors-theme-git` | Added to `depends` | Cursor theme set in variables.conf |
| `gpu-screen-recorder` | Added to `depends` | Screen recording (required by CLI) |
| `dart-sass` | Added to `depends` | Discord theming (required by CLI) |
| `lm_sensors` | Added to `depends` | System temp (required by shell) |
| `ddcutil` | Added to `depends` | Display brightness (required by shell) |
| `brightnessctl` | Added to `depends` | Keyboard brightness fallback |
| `libnotify` | Added to `depends` | Notifications (required by CLI) |
| `swappy` | Added to `depends` | Screenshot annotation |
| `libqalculate` | Added to `depends` | Shell launcher calculator |
| `gnome-keyring` | Moved `optdepends→depends` | exec-once in execs.conf |
| `polkit-gnome` | Moved `optdepends→depends` | exec-once in execs.conf |
| `thunar` | Moved `optdepends→depends` | Super+E keybind hardcoded |
| `zoxide` | Moved `optdepends→depends` | Used in fish/config.fish |
| `direnv` | Moved `optdepends→depends` | Used in fish/config.fish |
| `pipewire`, `pipewire-pulse`, `pipewire-alsa` | Added to `depends` | Audio stack |
| `bluez-utils` | Added to `depends` | mpris-proxy |
| `micro` | Added to `depends` | Text editor config included |

---

### New Files

| File | Purpose |
|---|---|
| `caelestia-install.sh` | Rewritten modular Arch installer (replaces install.fish) |
| `INSTALLER-README.md` | Complete installer documentation |
| `CHANGES.md` | This file |
| `caelestia-user-templates/hypr-vars.conf` | Template for Hyprland variable overrides |
| `caelestia-user-templates/hypr-user.conf` | Template for Hyprland config extensions |
| `caelestia-user-templates/user-config.fish` | Template for Fish config extensions |

---

## v3.0.0 — Standalone Build (no AUR for Caelestia)

### What changed

**`caelestia-cli` and `caelestia-shell` removed from AUR entirely.**
The installer now always builds both from the bundled source directories.
AUR is only used for system-level dependencies (hyprland, quickshell-git, fonts, etc.).

### New installer flags
- `--rebuild` — rebuild both CLI + shell from source, restart daemon (for after source edits)
- `--update` — update system packages via AUR helper, then rebuild CLI + shell from source
- `--from-source` removed (it was always implied; now it's the only mode)

### Bug fixes in v3.0.0

| # | File | Bug | Fix |
|---|---|---|---|
| 23 | `cli-1.0.6/pyproject.toml` | `hatch-vcs` fails to determine version when building outside a git repo (zip extract has no tags) | Added `fallback-version = "1.0.6"` and `SETUPTOOLS_SCM_PRETEND_VERSION` export |
| 24 | `cli-1.0.6/src/caelestia/utils/version.py` | `caelestia -v` queries `pacman -Q caelestia-cli caelestia-shell caelestia-meta` which all return "not installed" for standalone builds | Rewritten to show bundled version, shell binary version, and dotfiles git info |
| 25 | `caelestia-install.sh` | Fish completions (`completions/caelestia.fish`) existed in CLI source but were never installed anywhere | Installed to `~/.config/fish/completions/caelestia.fish` after CLI build |
| 26 | `caelestia-main/PKGBUILD` | `caelestia-cli` and `caelestia-shell` listed as AUR depends — incompatible with standalone build approach | Removed; `quickshell-git` added as runtime dep |
| 27 | `caelestia-install.sh` | `sweet-cursors-theme-git` no longer exists in AUR (orphaned/renamed) | Tries `sweet-cursors-hyprcursor-git` first, falls back gracefully with warning |

### Uninstall instructions (updated for v3)

```bash
# Remove CLI (pip editable install)
pip uninstall caelestia

# Remove shell (cmake install manifest)
sudo xargs rm -f < shell-1.5.1/build/install_manifest.txt

# Remove config symlinks
bash caelestia-install.sh --uninstall
```
