# Caelestia

<div align="center">

![Caelestia Banner](https://img.shields.io/badge/Caelestia-Arch%20Linux-blue?style=for-the-badge)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg?style=for-the-badge)](LICENSE)
[![Discord](https://img.shields.io/badge/Discord-Join-7289da?style=for-the-badge&logo=discord)](https://discord.gg/BGDCFCmMBk)
[![GitHub Release](https://img.shields.io/github/v/release/Shadoxu/caelestia-install?style=for-the-badge&include_prereleases)](https://github.com/Shadoxu/caelestia-install/releases/latest)

**A beautiful, feature-rich Hyprland dotfiles for Arch Linux**

*Aurora-themed. Feature-complete. Self-hosted.*

</div>

---

## Overview

Caelestia is a comprehensive Hyprland-based desktop environment featuring:

- **caelestia-shell** - Beautiful Quickshell-based desktop shell with control center, launcher, and dashboard
- **caelestia CLI** - Powerful command-line tool for controlling your desktop
- **Pre-configured dotfiles** - Carefully crafted configs for Hyprland, Fish, Foot, and more
- **Standalone installer** - No AUR dependency for Caelestia packages

## Quick Start

### One-Line Install

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/Shadoxu/caelestia-install/master/caelestia-install.sh)
```

### Manual Install

1. Download the latest release from [GitHub Releases](https://github.com/Shadoxu/caelestia-install/releases/latest)
2. Extract the archive
3. Run the installer:

```bash
# Full install with all components
bash caelestia-install.sh

# Automated install
bash caelestia-install.sh --noconfirm

# Install with optional components
bash caelestia-install.sh --spotify --vscode=codium --discord --zen

# Selective module install
bash caelestia-install.sh --modules=hypr,fish,foot,fastfetch
```

## Installer Options

### Core Options
```
-h, --help                  Show help and exit
--noconfirm                Skip all prompts (fully automatic)
--aur-helper=<yay|paru>    AUR helper to use (default: auto-detect)
--skip-packages            Skip system package installation
--modules=<list>           Config modules to install
                            (hypr,fish,foot,fastfetch,btop,starship,uwsm,micro)
```

### Optional Components
```
--spotify                   Install Spotify + Spicetify + Caelestia theme
--vscode=<code|codium>      Install VSCode/VSCodium + Caelestia extension
--discord                   Install Discord + OpenAsar + Equicord
--zen                       Install Zen Browser + CaelestiaFox integration
```

### Maintenance
```
--rebuild                   Rebuild CLI and shell from source
--update                    Update system packages + rebuild
--uninstall                 Remove all Caelestia config symlinks
```

## Components

| Component | Version | Description |
|-----------|---------|-------------|
| **caelestia-shell** | 1.5.1 | Quickshell-based desktop shell |
| **caelestia-cli** | 1.0.6 | Command-line control tool |
| **hyprland** | Latest | Wayland compositor |
| **fish** | Latest | User-friendly shell |
| **foot** | Latest | Fast, feature-rich terminal |

## Key Features

### Desktop Shell
- Control center with quick toggles
- Application launcher with fuzzy search
- System dashboard with media controls
- Notification center
- Lock screen

### CLI Tools
- `caelestia shell` - Control the desktop shell
- `caelestia screenshot` - Take screenshots
- `caelestia clipboard` - Clipboard history
- `caelestia scheme` - Manage color schemes
- `caelestia wallpaper` - Wallpaper management

### Default Keybinds

| Keybind | Action |
|---------|--------|
| `Super` | Open launcher |
| `Super + T` | Open terminal |
| `Super + W` | Open browser |
| `Super + C` | Open IDE |
| `Super + E` | Open file manager |
| `Super + #` | Switch to workspace # |
| `Super + S` | Toggle special workspace |
| `Ctrl + Alt + Del` | Session menu |
| `Ctrl + Super + Alt + R` | Restart shell |

## Requirements

- **OS:** Arch Linux (or Arch-based)
- **Python:** 3.13+
- **Display:** Wayland/X11 with Hyprland
- **Shell:** Bash or Fish

## Documentation

- [Installation Guide](docs/INSTALL.md)
- [Configuration](docs/CONFIG.md)
- [Troubleshooting](docs/TROUBLESHOOT.md)
- [Changelog](CHANGES.md)

## Project Structure

```
caelestia/
├── caelestia-install.sh    # Main installer script
├── caelestia-main/         # Dotfiles and configurations
│   ├── hypr/              # Hyprland config
│   ├── fish/              # Fish shell config
│   ├── foot/              # Terminal config
│   └── ...
├── cli-1.0.6/              # caelestia-cli source
│   ├── src/               # Python source
│   └── dist/              # Built packages
├── shell-1.5.1/           # caelestia-shell source
│   ├── plugin/            # C++ plugin
│   ├── components/        # QML components
│   └── build/             # Built artifacts
├── .github/               # GitHub workflows
└── docs/                  # Documentation
```

## Updating

### Automatic Update
```bash
bash caelestia-install.sh --update
```

### Manual Update
1. Download the new release
2. Extract to the same location
3. Run:
```bash
bash caelestia-install.sh --rebuild
```

## Uninstalling

```bash
bash caelestia-install.sh --uninstall
```

To remove CLI and shell:
```bash
pip uninstall caelestia
sudo xargs rm -f < shell-1.5.1/build/install_manifest.txt
```

## Troubleshooting

### Common Issues

**Q: The installer fails with "Missing source directories"**
> Run the installer from the extracted archive root directory.

**Q: caelestia CLI not found after install**
> Add to your shell config: `export PATH="$HOME/.local/bin:$PATH"`

**Q: Shell doesn't start on login**
> Check Hyprland exec-once settings and ensure caelestia is in PATH.

For more help, join our [Discord](https://discord.gg/BGDCFCmMBk) or open an [Issue](https://github.com/Shadoxu/caelestia-install/issues).

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](.github/CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

## Credits

- [Hyprland](https://hyprland.org) - Wayland compositor
- [Quickshell](https://quickshell.outfoxxed.me) - Desktop shell framework
- [Ax-Shell](https://github.com/Axenide/Ax-Shell) - Inspiration

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Shadoxu/caelestia-install&type=Date)](https://star-history.com/#Shadoxu/caelestia-install&Date)

---

<div align="center">

**Made with 💜 by the Caelestia community**

</div>
