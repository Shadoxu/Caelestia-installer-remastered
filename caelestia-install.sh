#!/usr/bin/env bash
# =============================================================================
#   ______           __          __  _
#  / ____/___ ____  / /__  _____/ /_(_)___ _
# / /   / __ `/ _ \/ / _ \/ ___/ __/ / __ `/
#/ /___/ /_/ /  __/ /  __(__  ) /_/ / /_/ /
#\____/\__,_/\___/_/\___/____/\__/_/\__,_/
#
# CAELESTIA DOTFILES INSTALLER  v3.0.0
# Arch Linux — Standalone · Builds from Bundled Source · No AUR for Caelestia
# =============================================================================
#
# WHAT THIS DOES:
#   • Installs ALL system dependencies from pacman + AUR
#   • Builds caelestia-cli   from bundled source  (cli-1.0.6/)   via pip
#   • Builds caelestia-shell from bundled source  (shell-1.5.1/) via cmake
#   • Installs dotfile configs by symlinking them into ~/.config
#   • Never fetches caelestia-cli or caelestia-shell from the AUR
#
# USAGE:
#   bash caelestia-install.sh [OPTIONS]
#
#   One-line install (auto-clones repo):
#     bash <(curl -fsSL https://raw.githubusercontent.com/Shadoxu/caelestia-install/master/caelestia-install.sh)
#
#   Local install (from cloned/extracted repo):
#     bash caelestia-install.sh
#
# OPTIONS:
#   -h, --help                Show this help and exit
#   --noconfirm               Skip all prompts (fully automatic)
#   --aur-helper=<yay|paru>   AUR helper to use (default: auto-detect/install)
#   --skip-packages           Skip system package installation
#   --modules=<list>          Config modules to install, comma-separated
#                             Options: hypr,fish,foot,fastfetch,btop,starship,uwsm,micro
#                             Default: all of the above
#   --spotify                 Install Spotify + Spicetify + Caelestia theme
#   --vscode=<code|codium>    Install VSCode/VSCodium + Caelestia extension
#   --discord                 Install Discord + OpenAsar + Equicord
#   --zen                     Install Zen Browser + CaelestiaFox integration
#   --rebuild                 Rebuild + reinstall CLI and shell from source
#   --update                  Update system packages + rebuild CLI/shell
#   --uninstall               Remove all Caelestia config symlinks
#
# EXAMPLES:
#   One-line:       bash <(curl -fsSL https://raw.githubusercontent.com/Shadoxu/caelestia-install/master/caelestia-install.sh)
#   Auto (noconf): bash <(curl -fsSL https://raw.githubusercontent.com/Shadoxu/caelestia-install/master/caelestia-install.sh) --noconfirm
#   Local install:  bash caelestia-install.sh
#   With extras:   bash caelestia-install.sh --spotify --vscode=codium --zen
#   Modules:       bash caelestia-install.sh --modules=hypr,fish --skip-packages
#   Rebuild:       bash caelestia-install.sh --rebuild     # rebuild after editing source
#   Update:        bash caelestia-install.sh --update      # update system + rebuild
#
# NOTES:
#   • Configs are SYMLINKED — do NOT move this directory after install
#   • Recommended location: ~/.local/share/caelestia
#   • Full log: /tmp/caelestia-install.log
#
# =============================================================================

set -eo pipefail

# =============================================================================
# SECTION 1 — CONSTANTS & COLORS
# =============================================================================

readonly VERSION="3.0.0"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly DOTS_DIR="${SCRIPT_DIR}/caelestia-main"
readonly SHELL_SRC="${SCRIPT_DIR}/shell-1.5.1"
readonly CLI_SRC="${SCRIPT_DIR}/cli-1.0.6"
readonly CONFIG_DIR="${XDG_CONFIG_HOME:-${HOME}/.config}"
readonly STATE_DIR="${XDG_STATE_HOME:-${HOME}/.local/state}"
readonly LOCAL_BIN="${HOME}/.local/bin"
readonly LOCAL_LIB="${HOME}/.local/lib/caelestia"
readonly LOCK_FILE="/tmp/caelestia-install.lock"
readonly LOG_FILE="/tmp/caelestia-install.log"

if [[ -t 1 ]]; then
  C_RED='\033[0;31m'   C_GREEN='\033[0;32m'  C_YELLOW='\033[1;33m'
  C_BLUE='\033[0;34m'  C_MAGENTA='\033[35m'  C_CYAN='\033[0;36m'
  C_DIM='\033[2m'      C_BOLD='\033[1m'       C_RESET='\033[0m'
else
  C_RED='' C_GREEN='' C_YELLOW='' C_BLUE='' C_MAGENTA=''
  C_CYAN='' C_DIM='' C_BOLD='' C_RESET=''
fi

# =============================================================================
# SECTION 2 — GLOBAL FLAGS
# =============================================================================

NOCONFIRM=false
INSTALL_SPOTIFY=false
INSTALL_VSCODE=""
INSTALL_DISCORD=false
INSTALL_ZEN=false
AUR_HELPER=""
SKIP_PACKAGES=false
DO_REBUILD=false
DO_UPDATE=false
DO_UNINSTALL=false
MODULES="hypr,fish,foot,fastfetch,btop,starship,uwsm,micro"
STEP_NUM=0
START_TIME=$SECONDS

# =============================================================================
# SECTION 3 — LOGGING & UI
# =============================================================================

_log_raw() { echo -e "$*" | tee -a "${LOG_FILE}" 2>/dev/null || echo -e "$*"; }
log()      { _log_raw "${C_CYAN}  :: ${C_RESET}$*"; }
success()  { _log_raw "${C_GREEN}  ✓  ${C_RESET}$*"; }
warn()     { _log_raw "${C_YELLOW}  ⚠  ${C_RESET}$*"; }
err()      { _log_raw "${C_RED}  ✗  ${C_RESET}$*" >&2; }
info()     { _log_raw "${C_DIM}     $*${C_RESET}"; }
die()      { err "$*"; exit 1; }

step() {
  (( STEP_NUM++ )) || true
  _log_raw "\n${C_BOLD}${C_MAGENTA}▶ [Step ${STEP_NUM}] $*${C_RESET}"
}

print_banner() {
  : > "${LOG_FILE}" 2>/dev/null || true
  echo -e "${C_MAGENTA}"
  cat <<'BANNER'
 ╭──────────────────────────────────────────────────────────────╮
 │    ______           __          __  _                        │
 │   / ____/___ ____  / /__  _____/ /_(_)___ _                  │
 │  / /   / __ `/ _ \/ / _ \/ ___/ __/ / __ `/                  │
 │ / /___/ /_/ /  __/ /  __(__  ) /_/ / /_/ /                   │
 │ \____/\__,_/\___/_/\___/____/\__/_/\__,_/                    │
 │                                                              │
 │    Installer v3.0.0  ·  Arch Linux  ·  Standalone            │
 │    Builds caelestia from bundled source — no AUR needed      │
 │                                                              │
 ╰──────────────────────────────────────────────────────────────╯
BANNER
  echo -e "${C_RESET}"
}

# =============================================================================
# SECTION 4 — ARGUMENT PARSING
# =============================================================================

usage() {
  cat <<EOF
${C_BOLD}${C_MAGENTA}Caelestia Installer v${VERSION}${C_RESET}
${C_DIM}Standalone · Arch Linux · Builds caelestia from bundled source${C_RESET}

${C_BOLD}USAGE:${C_RESET}
  bash caelestia-install.sh [OPTIONS]

${C_BOLD}CORE:${C_RESET}
  -h, --help                  Show this help
  --noconfirm                 Skip all prompts
  --aur-helper=<yay|paru>     AUR helper (default: auto-detect)
  --skip-packages             Skip system package installation
  --modules=<list>            Comma-separated config modules
                              (hypr,fish,foot,fastfetch,btop,starship,uwsm,micro)

${C_BOLD}OPTIONAL COMPONENTS:${C_RESET}
  --spotify                   Spotify + Spicetify + Caelestia theme
  --vscode=<code|codium>      VSCode/VSCodium + Caelestia extension
  --discord                   Discord + OpenAsar + Equicord
  --zen                       Zen Browser + CaelestiaFox

${C_BOLD}MAINTENANCE:${C_RESET}
  --rebuild                   Rebuild + reinstall CLI and shell from source
  --update                    Update system packages + rebuild CLI/shell
  --uninstall                 Remove all Caelestia config symlinks

${C_BOLD}HOW IT WORKS:${C_RESET}
  System deps      → pacman + AUR (hyprland, quickshell-git, fonts, etc.)
  caelestia-cli    → built from bundled cli-1.0.6/   via pip
  caelestia-shell  → built from bundled shell-1.5.1/ via cmake + ninja
  Dotfiles         → symlinked from this directory into ~/.config

${C_BOLD}NOTE:${C_RESET}
  Do NOT move this directory after install — configs are symlinked from here.
  Recommended location: ~/.local/share/caelestia
  Log: ${LOG_FILE}
EOF
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -h|--help)           usage; exit 0 ;;
      --noconfirm)         NOCONFIRM=true ;;
      --spotify)           INSTALL_SPOTIFY=true ;;
      --vscode=code)       INSTALL_VSCODE="code" ;;
      --vscode=codium)     INSTALL_VSCODE="codium" ;;
      --vscode)            INSTALL_VSCODE="codium" ;;
      --discord)           INSTALL_DISCORD=true ;;
      --zen)               INSTALL_ZEN=true ;;
      --aur-helper=yay)    AUR_HELPER="yay" ;;
      --aur-helper=paru)   AUR_HELPER="paru" ;;
      --skip-packages)     SKIP_PACKAGES=true ;;
      --modules=*)         MODULES="${1#*=}" ;;
      --rebuild)           DO_REBUILD=true ;;
      --update)            DO_UPDATE=true ;;
      --uninstall)         DO_UNINSTALL=true ;;
      *)                   die "Unknown option: '$1'  (run --help for usage)" ;;
    esac
    shift
  done
}

# =============================================================================
# SECTION 5 — AUTO-CLONE (for one-line install)
# =============================================================================

auto_clone() {
  if [[ -d "${DOTS_DIR}" && -d "${SHELL_SRC}" && -d "${CLI_SRC}" ]]; then
    return
  fi

  step "Auto-cloning repository"

  local repo_url="https://github.com/Shadoxu/caelestia-install.git"
  local install_dir="${HOME}/.local/share/caelestia"

  log "One-line install detected — cloning repository..."
  info "Target: ${install_dir}"

  if [[ -d "${install_dir}" ]]; then
    if [[ "${NOCONFIRM}" == "true" ]]; then
      log "Removing existing ${install_dir}..."
      rm -rf "${install_dir}"
    else
      if confirm "'${install_dir}' already exists. Overwrite?"; then
        rm -rf "${install_dir}"
      else
        die "Installation cancelled."
      fi
    fi
  fi

  log "Cloning ${repo_url}..."
  mkdir -p "$(dirname "${install_dir}")"
  git clone --depth=1 "${repo_url}" "${install_dir}" || \
    die "Failed to clone repository."

  log "Changing to repo directory..."
  cd "${install_dir}" || die "Failed to cd to ${install_dir}"

  exec bash "${install_dir}/caelestia-install.sh" "$@"
}

# =============================================================================
# SECTION 6 — LOCKFILE & CLEANUP TRAP
# =============================================================================

acquire_lock() {
  if [[ -f "${LOCK_FILE}" ]]; then
    local pid; pid=$(cat "${LOCK_FILE}")
    kill -0 "${pid}" 2>/dev/null && \
      die "Another installer instance is running (PID ${pid})."
    rm -f "${LOCK_FILE}"
  fi
  echo "$$" > "${LOCK_FILE}"
}

cleanup() {
  rm -f "${LOCK_FILE}"
  local elapsed=$(( SECONDS - START_TIME ))
  echo
  warn "Installer exited after ${elapsed}s.  Full log: ${LOG_FILE}"
}
trap cleanup EXIT INT TERM

# =============================================================================
# SECTION 6 — SYSTEM CHECKS
# =============================================================================

check_not_root() {
  if [[ ${EUID} -eq 0 ]]; then
    die "Do NOT run as root. sudo will be called when needed."
  fi
}

check_arch() {
  command -v pacman &>/dev/null || die "pacman not found — Arch Linux only."
  if [[ -f /etc/os-release ]]; then
    local pretty; pretty=$(grep -oP '(?<=^PRETTY_NAME=).*' /etc/os-release | tr -d '"')
    info "Distro: ${pretty}"
  fi
  success "Arch-compatible system"
}

check_internet() {
  log "Checking internet..."
  ping -c 1 -W 4 archlinux.org &>/dev/null 2>&1 || \
    die "No internet connection — connect and try again."
  success "Internet: OK"
}

check_source_dirs() {
  local missing=()
  [[ -d "${DOTS_DIR}"  ]] || missing+=("caelestia-main/")
  [[ -d "${SHELL_SRC}" ]] || missing+=("shell-1.5.1/")
  [[ -d "${CLI_SRC}"   ]] || missing+=("cli-1.0.6/")
  [[ ${#missing[@]} -gt 0 ]] && \
    die "Missing source directories: ${missing[*]}\nRun from the extracted zip root."
  success "Source directories: OK"
}

check_python_version() {
  # caelestia-cli pyproject.toml requires python >= 3.13
  if ! python3 -c 'import sys; assert sys.version_info >= (3,13)' 2>/dev/null; then
    local ver; ver=$(python3 --version 2>&1)
    die "caelestia-cli requires Python 3.13+.\nFound: ${ver}\nInstall python 3.13+ and retry."
  fi
  info "Python: $(python3 --version)"
}

# =============================================================================
# SECTION 7 — PROMPTS
# =============================================================================

confirm() {
  [[ "${NOCONFIRM}" == "true" ]] && return 0
  local reply
  read -rp "$(echo -e "${C_BLUE}  ? ${C_RESET}${1:-Continue?} [Y/n] ")" reply
  [[ "${reply,,}" != "n" ]]
}

# Returns 0 = proceed (path removed if existed), 1 = skip
confirm_overwrite() {
  local path="$1"
  if [[ -e "${path}" || -L "${path}" ]]; then
    if [[ "${NOCONFIRM}" == "true" ]]; then
      log "Overwriting: ${path}"
      rm -rf "${path}"
      return 0
    fi
    if confirm "'${path}' already exists. Overwrite?"; then
      rm -rf "${path}"; return 0
    else
      warn "Skipping: ${path}"; return 1
    fi
  fi
  return 0
}

# =============================================================================
# SECTION 8 — AUR HELPER
# =============================================================================

detect_aur_helper() {
  if [[ -n "${AUR_HELPER}" ]]; then
    info "AUR helper: ${AUR_HELPER} (specified)"; return
  fi
  if   command -v paru &>/dev/null; then AUR_HELPER="paru"
  elif command -v yay  &>/dev/null; then AUR_HELPER="yay"
  else AUR_HELPER="paru"
    info "No AUR helper found — paru will be installed"
  fi
  info "AUR helper: ${AUR_HELPER}"
}

bootstrap_aur_helper() {
  if command -v "${AUR_HELPER}" &>/dev/null; then
    success "${AUR_HELPER} already installed"; return
  fi

  log "Bootstrapping ${AUR_HELPER}..."
  sudo pacman -S --needed --noconfirm git base-devel

  local tmp; tmp=$(mktemp -d)
  (
    cd "${tmp}"
    git clone --depth=1 "https://aur.archlinux.org/${AUR_HELPER}.git"
    cd "${AUR_HELPER}"
    [[ "${NOCONFIRM}" == "true" ]] && makepkg -si --noconfirm || makepkg -si
  )
  rm -rf "${tmp}"

  if [[ "${AUR_HELPER}" == "yay" ]]; then
    yay -Y --gendb 2>/dev/null || true
    yay -Y --devel --save 2>/dev/null || true
  else
    paru --gendb 2>/dev/null || true
  fi

  success "${AUR_HELPER} installed"
}

noconfirm_flag() { [[ "${NOCONFIRM}" == "true" ]] && echo "--noconfirm" || echo ""; }

# =============================================================================
# SECTION 9 — PACKAGE LISTS
# =============================================================================

# Official pacman packages
readonly -a PACMAN_PKGS=(
  # Hyprland
  hyprland xdg-desktop-portal-hyprland xdg-desktop-portal-gtk

  # Wayland utils
  wl-clipboard cliphist inotify-tools

  # Audio
  wireplumber pipewire pipewire-pulse pipewire-alsa libpipewire
  bluez-utils aubio

  # System
  trash-cli lm_sensors ddcutil brightnessctl

  # Network
  networkmanager fuzzel

  # Location + night light
  geoclue gammastep

  # Notifications + screenshots
  libnotify grim slurp swappy

  # Calculator
  libqalculate

  # Terminal + shell
  foot fish bash

  # CLI tools
  eza fastfetch starship btop jq micro zoxide direnv

  # Fonts
  ttf-jetbrains-mono-nerd

  # Theming
  papirus-icon-theme adw-gtk-theme

  # File manager
  thunar

  # Auth
  gnome-keyring polkit-gnome

  # Qt6 runtime (required by quickshell + caelestia-shell)
  qt6-base qt6-declarative

  # Build tools for caelestia-shell
  git cmake ninja base-devel clang pkg-config

  # Python for caelestia-cli
  python python-pip
)

# AUR — system deps only; caelestia-cli and caelestia-shell are NOT here
readonly -a AUR_PKGS=(
  hyprpicker
  app2unit
  qtengine-git
  ttf-material-symbols-variable-git
  libcava
  gpu-screen-recorder
  dart-sass
  uwsm
  quickshell-git           # required to build + run caelestia-shell
)

# Cursor theme — AUR name changed; try both, skip gracefully if unavailable
readonly -a CURSOR_PKG_CANDIDATES=(
  sweet-cursors-hyprcursor-git   # current AUR name (Hyprland-native hyprcursor)
  sweet-cursors-theme-git        # old AUR name (fallback)
)

# =============================================================================
# SECTION 10 — PACKAGE INSTALLATION
# =============================================================================

install_packages() {
  step "Installing system packages"

  # ── pacman ──
  log "Checking official packages..."
  local missing_pacman=()
  for pkg in "${PACMAN_PKGS[@]}"; do
    pacman -Q "${pkg}" &>/dev/null || missing_pacman+=("${pkg}")
  done

  if [[ ${#missing_pacman[@]} -gt 0 ]]; then
    info "Installing ${#missing_pacman[@]} package(s) via pacman..."
    # shellcheck disable=SC2086
    sudo pacman -S --needed $(noconfirm_flag) "${missing_pacman[@]}"
    success "pacman: ${#missing_pacman[@]} new package(s) installed"
  else
    success "All pacman packages already present"
  fi

  # ── AUR ──
  log "Checking AUR packages..."
  local missing_aur=()
  for pkg in "${AUR_PKGS[@]}"; do
    pacman -Q "${pkg}" &>/dev/null || missing_aur+=("${pkg}")
  done

  if [[ ${#missing_aur[@]} -gt 0 ]]; then
    info "Installing ${#missing_aur[@]} package(s) from AUR: ${missing_aur[*]}"
    # shellcheck disable=SC2086
    "${AUR_HELPER}" -S --needed $(noconfirm_flag) "${missing_aur[@]}"
    success "AUR: ${#missing_aur[@]} new package(s) installed"
  else
    success "All AUR packages already present"
  fi

  # ── Cursor theme (optional — AUR name changed, try both gracefully) ──
  local cursor_found=false
  for candidate in "${CURSOR_PKG_CANDIDATES[@]}"; do
    if pacman -Q "${candidate}" &>/dev/null; then
      success "Cursor theme already installed: ${candidate}"
      cursor_found=true; break
    fi
  done

  if [[ "${cursor_found}" == "false" ]]; then
    log "Installing sweet cursor theme (optional)..."
    for candidate in "${CURSOR_PKG_CANDIDATES[@]}"; do
      # shellcheck disable=SC2086
      if "${AUR_HELPER}" -S --needed $(noconfirm_flag) "${candidate}" 2>/dev/null; then
        success "Cursor theme installed: ${candidate}"
        cursor_found=true; break
      fi
      info "  '${candidate}' not available, trying next..."
    done
    if [[ "${cursor_found}" == "false" ]]; then
      warn "Sweet cursor theme unavailable in AUR — skipping (non-fatal)"
      info "  To use a different cursor, set in: ~/.config/caelestia/hypr-vars.conf"
      info "  Variable: \$cursorTheme = <your-cursor-theme-name>"
    fi
  fi
}

# =============================================================================
# SECTION 11 — BUILD caelestia-cli FROM BUNDLED SOURCE
# =============================================================================

build_cli() {
  step "Building caelestia-cli from bundled source (cli-1.0.6/)"
  check_python_version

  log "Ensuring build backend (hatchling + hatch-vcs)..."
  pip install --break-system-packages --quiet hatchling hatch-vcs 2>/dev/null || \
    pip install --user --quiet hatchling hatch-vcs

  # hatch-vcs reads the version from git tags. When building from a bundled
  # zip (no .git history / no tags), it falls back to the fallback-version
  # in pyproject.toml. Read it dynamically so pip never errors out.
  local cli_version
  cli_version=$(grep -oP '(?<=fallback-version = ")[^"]+' "${CLI_SRC}/pyproject.toml" 2>/dev/null || echo "1.0.6")
  export SETUPTOOLS_SCM_PRETEND_VERSION="${cli_version}"
  info "CLI version: ${cli_version}"

  # Editable install so that modifying source in cli-1.0.6/ takes effect immediately
  log "Installing caelestia-cli (editable)..."
  if pip install --break-system-packages --editable "${CLI_SRC}" >>"${LOG_FILE}" 2>&1; then
    success "caelestia-cli installed (system editable)"
  elif pip install --user --editable "${CLI_SRC}" >>"${LOG_FILE}" 2>&1; then
    success "caelestia-cli installed (user editable)"
    export PATH="${LOCAL_BIN}:${PATH}"
  else
    die "caelestia-cli build failed — check ${LOG_FILE}"
  fi

if command -v caelestia &>/dev/null; then
    success "caelestia CLI ready: $(caelestia --version 2>/dev/null || echo 'ok')"
  else
    warn "caelestia installed but not in PATH. Adding to shell config automatically..."
    if [[ -f "${HOME}/.config/fish/config.fish" ]]; then
      if ! grep -q '~/.local/bin' "${HOME}/.config/fish/config.fish" 2>/dev/null; then
        echo -e '\n# Caelestia PATH\nexport PATH="$HOME/.local/bin:$PATH"' >> "${HOME}/.config/fish/config.fish"
        success "Added PATH to fish config"
      fi
    fi
    if [[ -f "${HOME}/.bashrc" ]]; then
      if ! grep -q '~/.local/bin' "${HOME}/.bashrc" 2>/dev/null; then
        echo -e '\n# Caelestia PATH\nexport PATH="$HOME/.local/bin:$PATH"' >> "${HOME}/.bashrc"
        success "Added PATH to bashrc"
      fi
    fi
    if [[ -f "${HOME}/.zshrc" ]]; then
      if ! grep -q '~/.local/bin' "${HOME}/.zshrc" 2>/dev/null; then
        echo -e '\n# Caelestia PATH\nexport PATH="$HOME/.local/bin:$PATH"' >> "${HOME}/.zshrc"
        success "Added PATH to zshrc"
      fi
    fi
    export PATH="${HOME}/.local/bin:${PATH}"
    info "PATH set for current session. Restart your shell or run: set -gx PATH \$HOME/.local/bin \$PATH"
  fi

  # ── Fish shell completions ──────────────────────────────────────────────────
  local completions_src="${CLI_SRC}/completions/caelestia.fish"
  local completions_dst="${CONFIG_DIR}/fish/completions/caelestia.fish"

  if [[ -f "${completions_src}" ]]; then
    log "Installing fish completions..."
    mkdir -p "${CONFIG_DIR}/fish/completions"
    # Copy (not symlink) completions — they should survive a fish config reset
    cp -f "${completions_src}" "${completions_dst}"
    success "Fish completions → ${completions_dst}"
  fi
}

# =============================================================================
# SECTION 12 — BUILD caelestia-shell FROM BUNDLED SOURCE
# =============================================================================

build_shell() {
  step "Building caelestia-shell from bundled source (shell-1.5.1/)"

  if ! pacman -Q quickshell-git &>/dev/null && ! command -v qs &>/dev/null; then
    die "quickshell-git is not installed. Run the package installation step first."
  fi

  local build_dir="${SHELL_SRC}/build"
  log "Cleaning previous build..."
  rm -rf "${build_dir}"
  mkdir -p "${build_dir}"

  local shell_version="v${VERSION}"
  local shell_git_rev="standalone-${VERSION}"
  info "Shell version: ${shell_version} (${shell_git_rev})"

  log "Configuring (cmake + ninja)..."
  cmake -B "${build_dir}" -G Ninja             \
    -DCMAKE_BUILD_TYPE=Release                 \
    -DCMAKE_INSTALL_PREFIX=/                   \
    -DVERSION="${shell_version}"                \
    -DGIT_REVISION="${shell_git_rev}"          \
    -DDISTRIBUTOR="caelestia-standalone-v${VERSION}" \
    -S "${SHELL_SRC}"                          \
    >>"${LOG_FILE}" 2>&1 \
    || die "cmake configure failed — check ${LOG_FILE}"

  log "Compiling with $(nproc) threads (this may take a few minutes)..."
  cmake --build "${build_dir}" -- -j"$(nproc)" >>"${LOG_FILE}" 2>&1 \
    || die "cmake build failed — check ${LOG_FILE}"

  log "Installing (requires sudo)..."
  sudo cmake --install "${build_dir}" >>"${LOG_FILE}" 2>&1 \
    || die "cmake install failed — check ${LOG_FILE}"

  success "caelestia-shell built and installed"
}

# =============================================================================
# SECTION 13 — CONFIG BACKUP
# =============================================================================

backup_config() {
  [[ ! -d "${CONFIG_DIR}" ]] && { info "No existing ~/.config — skipping backup"; return; }

  local bak="${CONFIG_DIR}.bak"
  if [[ -e "${bak}" ]]; then
    confirm "Backup '${bak}' already exists. Overwrite?" || { warn "Skipping backup"; return; }
    rm -rf "${bak}"
  fi
  log "Backing up ${CONFIG_DIR} → ${bak}"
  cp -r "${CONFIG_DIR}" "${bak}"
  success "Backed up to ${bak}"
}

# =============================================================================
# SECTION 14 — SYMLINK HELPERS
# =============================================================================

install_symlink() {
  local src="$1" dst="$2"
  confirm_overwrite "${dst}" || return 1
  mkdir -p "$(dirname "${dst}")"
  ln -s "$(realpath "${src}")" "${dst}"
}

module_enabled() { [[ ",${MODULES}," == *",${1},"* ]]; }

# =============================================================================
# SECTION 15 — BUG PATCH: configs.fish
# =============================================================================

patch_configs_fish() {
  # BUG FIX: 'if _reload' in fish executes $_reload as a command, not tests it.
  # Correct fish syntax is: 'if test $_reload = true'
  local script
  script=$(realpath "${CONFIG_DIR}/hypr/scripts/configs.fish" 2>/dev/null) || return
  if [[ -f "${script}" ]] && grep -q "^if _reload$" "${script}" 2>/dev/null; then
    warn "Patching bug in configs.fish: 'if _reload' → 'if test \$_reload = true'"
    sed -i 's/^if _reload$/if test $_reload = true/' "${script}"
    success "configs.fish patched"
  fi
}

# =============================================================================
# SECTION 16 — CORE CONFIG INSTALLATION
# =============================================================================

install_core_configs() {
  step "Installing dotfile config modules"

  if module_enabled "hypr"; then
    log "Installing Hyprland configs..."
    if install_symlink "${DOTS_DIR}/hypr" "${CONFIG_DIR}/hypr"; then
      chmod +x "${CONFIG_DIR}/hypr/scripts/wsaction.fish" 2>/dev/null || true
      chmod +x "${CONFIG_DIR}/hypr/scripts/configs.fish"  2>/dev/null || true
      patch_configs_fish
      if [[ -n "${HYPRLAND_INSTANCE_SIGNATURE:-}" ]] && command -v hyprctl &>/dev/null; then
        hyprctl reload 2>/dev/null || warn "hyprctl reload failed (non-fatal)"
      fi
      success "Hyprland configs installed"
    fi
  fi

  module_enabled "fish"      && { install_symlink "${DOTS_DIR}/fish"          "${CONFIG_DIR}/fish"          && success "Fish installed";      } || true
  module_enabled "foot"      && { install_symlink "${DOTS_DIR}/foot"          "${CONFIG_DIR}/foot"          && success "Foot installed";      } || true
  module_enabled "fastfetch" && { install_symlink "${DOTS_DIR}/fastfetch"     "${CONFIG_DIR}/fastfetch"     && success "Fastfetch installed"; } || true
  module_enabled "btop"      && { install_symlink "${DOTS_DIR}/btop"          "${CONFIG_DIR}/btop"          && success "Btop installed";      } || true
  module_enabled "starship"  && { install_symlink "${DOTS_DIR}/starship.toml" "${CONFIG_DIR}/starship.toml" && success "Starship installed";  } || true
  module_enabled "uwsm"      && { install_symlink "${DOTS_DIR}/uwsm"          "${CONFIG_DIR}/uwsm"          && success "UWSM installed";      } || true
  module_enabled "micro"     && { install_symlink "${DOTS_DIR}/micro"         "${CONFIG_DIR}/micro"         && success "Micro installed";     } || true
}

# =============================================================================
# SECTION 17 — OPTIONAL: SPOTIFY + SPICETIFY
# =============================================================================

install_spotify() {
  [[ "${INSTALL_SPOTIFY}" != "true" ]] && return
  step "Installing Spotify + Spicetify"

  local had_spicetify=false
  pacman -Q spicetify-cli &>/dev/null && had_spicetify=true

  # shellcheck disable=SC2086
  "${AUR_HELPER}" -S --needed spotify spicetify-cli spicetify-marketplace-bin $(noconfirm_flag)

  if [[ "${had_spicetify}" == "false" ]]; then
    sudo chmod a+wr /opt/spotify
    sudo chmod a+wr /opt/spotify/Apps -R
    if [[ -d "${HOME}/.config/spotify" ]]; then
      spicetify backup apply 2>/dev/null || warn "Run 'spicetify backup apply' after launching Spotify once"
    else
      warn "Launch Spotify once first, then run: spicetify backup apply"
    fi
  fi

  if install_symlink "${DOTS_DIR}/spicetify" "${CONFIG_DIR}/spicetify"; then
    spicetify config current_theme caelestia color_scheme caelestia custom_apps marketplace 2>/dev/null || true
    if pgrep -x spotify &>/dev/null; then
      warn "Spotify is running — close it, then run: spicetify apply"
    else
      spicetify apply 2>/dev/null || warn "Run 'spicetify apply' manually if needed"
    fi
    success "Spicetify configured"
  fi
}

# =============================================================================
# SECTION 18 — OPTIONAL: VSCODE / VSCODIUM
# =============================================================================

install_vscode() {
  [[ -z "${INSTALL_VSCODE}" ]] && return
  local vs="${INSTALL_VSCODE}"
  step "Installing VS${vs^} + Caelestia extension"

  local pkgs folder prog
  if [[ "${vs}" == "code" ]]; then
    pkgs="code";                                  folder="Code";    prog="code"
  else
    pkgs="vscodium-bin vscodium-bin-marketplace"; folder="VSCodium"; prog="codium"
  fi

  # shellcheck disable=SC2086
  "${AUR_HELPER}" -S --needed ${pkgs} $(noconfirm_flag)

  local user_dir="${CONFIG_DIR}/${folder}/User"
  mkdir -p "${user_dir}"

  install_symlink "${DOTS_DIR}/vscode/settings.json"    "${user_dir}/settings.json"    || true
  install_symlink "${DOTS_DIR}/vscode/keybindings.json" "${user_dir}/keybindings.json" || true
  install_symlink "${DOTS_DIR}/vscode/flags.conf"       "${CONFIG_DIR}/${prog}-flags.conf" || true

  local vsix
  vsix=$(find "${DOTS_DIR}/vscode/caelestia-vscode-integration" -name "*.vsix" 2>/dev/null | head -1)
  if [[ -n "${vsix}" ]]; then
    "${prog}" --install-extension "${vsix}" 2>/dev/null || \
      warn "Install extension manually: ${prog} --install-extension ${vsix}"
  fi
  success "VS${vs^} configured"
}

# =============================================================================
# SECTION 19 — OPTIONAL: DISCORD + EQUICORD
# =============================================================================

install_discord() {
  [[ "${INSTALL_DISCORD}" != "true" ]] && return
  step "Installing Discord + OpenAsar + Equicord"

  # shellcheck disable=SC2086
  "${AUR_HELPER}" -S --needed discord equicord-installer-bin $(noconfirm_flag)

  if command -v Equilotl &>/dev/null; then
    sudo Equilotl -install -location /opt/discord          || warn "Equicord install failed"
    sudo Equilotl -install-openasar -location /opt/discord || warn "OpenAsar install failed"
    # shellcheck disable=SC2086
    "${AUR_HELPER}" -Rns equicord-installer-bin $(noconfirm_flag) 2>/dev/null || true
    success "Discord + Equicord + OpenAsar installed"
  else
    warn "Equilotl not found after install — install Equicord manually: https://equicord.app"
  fi
}

# =============================================================================
# SECTION 20 — OPTIONAL: ZEN BROWSER + CAELESTIAFOX
# =============================================================================

install_zen() {
  [[ "${INSTALL_ZEN}" != "true" ]] && return
  step "Installing Zen Browser + CaelestiaFox"

  # shellcheck disable=SC2086
  "${AUR_HELPER}" -S --needed zen-browser-bin $(noconfirm_flag)

  local chrome_dir=""
  while IFS= read -r -d '' profile_dir; do
    local name; name=$(basename "${profile_dir}")
    [[ "${name}" == "Crash Reports" || "${name}" == "Pending Pings" || "${name}" == "storage" ]] && continue
    chrome_dir="${profile_dir}/chrome"
    break
  done < <(find "${HOME}/.zen" -maxdepth 1 -mindepth 1 -type d -print0 2>/dev/null)

  if [[ -n "${chrome_dir}" ]]; then
    mkdir -p "${chrome_dir}"
    install_symlink "${DOTS_DIR}/zen/userChrome.css" "${chrome_dir}/userChrome.css" && \
      success "Zen userChrome → ${chrome_dir}"
  else
    warn "No Zen profile found — launch Zen once, then re-run this installer"
  fi

  local hosts_dir="${HOME}/.mozilla/native-messaging-hosts"
  mkdir -p "${hosts_dir}" "${LOCAL_LIB}"

  install_symlink "${DOTS_DIR}/zen/native_app/app.fish" "${LOCAL_LIB}/caelestiafox" && \
    success "CaelestiaFox native app installed"

  if confirm_overwrite "${hosts_dir}/caelestiafox.json"; then
    cp "${DOTS_DIR}/zen/native_app/manifest.json" "${hosts_dir}/caelestiafox.json"
    # Use absolute path — tilde is NOT expanded inside sed replacement strings
    sed -i "s|{{ \$lib }}|${LOCAL_LIB}|g" "${hosts_dir}/caelestiafox.json"
    success "CaelestiaFox manifest installed"
  fi

  echo
  log "👉  Install the CaelestiaFox extension:"
  info "    https://addons.mozilla.org/en-US/firefox/addon/caelestiafox"
}

# =============================================================================
# SECTION 21 — PAPIRUS-FOLDERS SUDOERS
# =============================================================================

setup_papirus_sudoers() {
  step "Configuring papirus-folders (passwordless sudo)"
  command -v papirus-folders &>/dev/null || { info "papirus-folders not installed — skipping"; return; }

  local sudoers_file="/etc/sudoers.d/papirus-folders"
  [[ -f "${sudoers_file}" ]] && { success "papirus-folders sudoers already configured"; return; }

  local pf_path; pf_path=$(command -v papirus-folders)
  echo "${USER} ALL=(ALL) NOPASSWD: ${pf_path}" | sudo tee "${sudoers_file}" >/dev/null
  sudo chmod 440 "${sudoers_file}"

  if sudo visudo -c -f "${sudoers_file}" &>/dev/null; then
    success "papirus-folders sudoers configured"
  else
    sudo rm -f "${sudoers_file}"
    warn "sudoers validation failed — configure manually (see CLI README)"
  fi
}

# =============================================================================
# SECTION 22 — COLOR SCHEME INIT
# =============================================================================

init_scheme() {
  step "Initialising color scheme"

  if ! command -v caelestia &>/dev/null; then
    warn "caelestia not in PATH — skipping scheme init"
    info "Run manually later: caelestia scheme set"
    return
  fi

  local scheme_file="${STATE_DIR}/caelestia/scheme.json"
  if [[ -f "${scheme_file}" ]]; then
    success "Scheme already initialised"; return
  fi

  mkdir -p "$(dirname "${scheme_file}")"
  caelestia scheme set 2>/dev/null || warn "Scheme init failed — run 'caelestia scheme set' manually"
  sleep 0.5

  if [[ -n "${HYPRLAND_INSTANCE_SIGNATURE:-}" ]] && command -v hyprctl &>/dev/null; then
    hyprctl reload 2>/dev/null || true
  fi
  success "Color scheme initialised"
}

# =============================================================================
# SECTION 23 — SHELL DAEMON STARTUP
# =============================================================================

start_shell_daemon() {
  step "Starting shell daemon"

  if ! command -v caelestia &>/dev/null; then
    info "caelestia not in PATH — shell will start via exec-once on next Hyprland login"
    return
  fi

  if [[ -z "${HYPRLAND_INSTANCE_SIGNATURE:-}" ]]; then
    info "Not inside a Hyprland session — shell will start automatically on next login"
    return
  fi

  caelestia shell -d >/dev/null 2>&1 & disown
  success "Shell daemon started (PID $!)"
}

# =============================================================================
# SECTION 24 — REBUILD MODE
# =============================================================================

do_rebuild() {
  step "Rebuilding from bundled source"
  info "Rebuilding caelestia-cli and caelestia-shell — no package changes"
  echo

  build_cli
  build_shell

  if [[ -n "${HYPRLAND_INSTANCE_SIGNATURE:-}" ]] && command -v caelestia &>/dev/null; then
    log "Restarting shell daemon..."
    qs -c caelestia kill 2>/dev/null || true
    sleep 0.3
    caelestia shell -d >/dev/null 2>&1 & disown
    success "Shell daemon restarted"
  fi

  local elapsed=$(( SECONDS - START_TIME ))
  echo; success "Rebuild complete in ${elapsed}s"
  exit 0
}

# =============================================================================
# SECTION 25 — UPDATE MODE
# =============================================================================

do_update() {
  step "Updating Caelestia"
  info "This updates system packages AND rebuilds CLI/shell from bundled source"
  echo

  log "Updating system packages..."
  # shellcheck disable=SC2086
  "${AUR_HELPER}" -Syu $(noconfirm_flag)
  success "System packages updated"

  build_cli
  build_shell

  if [[ -n "${HYPRLAND_INSTANCE_SIGNATURE:-}" ]] && command -v caelestia &>/dev/null; then
    log "Restarting shell daemon..."
    qs -c caelestia kill 2>/dev/null || true
    sleep 0.3
    caelestia shell -d >/dev/null 2>&1 & disown
    success "Shell daemon restarted"
  fi

  local elapsed=$(( SECONDS - START_TIME ))
  echo; success "Update complete in ${elapsed}s"
  exit 0
}

# =============================================================================
# SECTION 26 — UNINSTALL MODE
# =============================================================================

do_uninstall() {
  step "Uninstalling Caelestia"
  warn "This removes all Caelestia config symlinks from ${CONFIG_DIR}"
  confirm "Proceed?" || exit 0

  local -a links=(
    "${CONFIG_DIR}/hypr"        "${CONFIG_DIR}/fish"
    "${CONFIG_DIR}/foot"        "${CONFIG_DIR}/fastfetch"
    "${CONFIG_DIR}/btop"        "${CONFIG_DIR}/starship.toml"
    "${CONFIG_DIR}/uwsm"        "${CONFIG_DIR}/micro"
    "${CONFIG_DIR}/spicetify"
    "${LOCAL_LIB}/caelestiafox"
    "${HOME}/.mozilla/native-messaging-hosts/caelestiafox.json"
  )

  local removed=0
  for link in "${links[@]}"; do
    if [[ -L "${link}" ]]; then
      rm -f "${link}"; success "Removed: ${link}"
      (( removed++ )) || true
    fi
  done

  [[ ${removed} -eq 0 ]] && info "No symlinks found" || success "${removed} symlink(s) removed"

  echo
  info "To uninstall caelestia-cli (pip editable install):"
  info "  pip uninstall caelestia"
  info "To uninstall caelestia-shell (cmake installed files):"
  info "  sudo xargs rm -f < ${SHELL_SRC}/build/install_manifest.txt"
  info "To restore config backup:"
  info "  cp -r ${CONFIG_DIR}.bak ${CONFIG_DIR}"
  exit 0
}

# =============================================================================
# SECTION 27 — POST-INSTALL SUMMARY
# =============================================================================

print_summary() {
  local elapsed=$(( SECONDS - START_TIME ))

  echo
  echo -e "${C_BOLD}${C_GREEN}╔══════════════════════════════════════════════════════════╗${C_RESET}"
  echo -e "${C_BOLD}${C_GREEN}║          Installation Complete!  🎉                     ║${C_RESET}"
  printf  "${C_BOLD}${C_GREEN}║  Completed in %-42s ║${C_RESET}\n" "${elapsed}s"
  echo -e "${C_BOLD}${C_GREEN}╚══════════════════════════════════════════════════════════╝${C_RESET}"
  echo
  echo -e "${C_BOLD}Built from bundled source:${C_RESET}"
  echo -e "  ${C_CYAN}caelestia-cli${C_RESET}    ← ${CLI_SRC}"
  echo -e "  ${C_CYAN}caelestia-shell${C_RESET}  ← ${SHELL_SRC}"
  echo
  echo -e "${C_BOLD}Installed modules:${C_RESET} ${MODULES}"
  echo
  echo -e "${C_BOLD}Keybinds:${C_RESET}"
  echo -e "  ${C_CYAN}Super${C_RESET}              Launcher"
  echo -e "  ${C_CYAN}Super + T / W / C / E${C_RESET}  Terminal / Browser / IDE / Files"
  echo -e "  ${C_CYAN}Super + #${C_RESET}          Switch workspace"
  echo -e "  ${C_CYAN}Super+Alt + #${C_RESET}      Move window to workspace"
  echo -e "  ${C_CYAN}Super + S${C_RESET}          Special workspace"
  echo -e "  ${C_CYAN}Ctrl+Alt+Del${C_RESET}       Session menu"
  echo -e "  ${C_CYAN}Ctrl+Super+Alt+R${C_RESET}   Restart shell"
  echo
  echo -e "${C_DIM}Repo (do NOT move): ${SCRIPT_DIR}${C_RESET}"
  echo -e "${C_DIM}Config:             ${CONFIG_DIR}${C_RESET}"
  echo -e "${C_DIM}Log:                ${LOG_FILE}${C_RESET}"
  echo
  echo -e "${C_BOLD}${C_YELLOW}⚡  Log out and start a Hyprland session to enjoy Caelestia!${C_RESET}"
  echo
  echo -e "${C_DIM}After editing source → bash caelestia-install.sh --rebuild${C_RESET}"
  echo -e "${C_DIM}System update        → bash caelestia-install.sh --update${C_RESET}"
  echo
}

# =============================================================================
# SECTION 28 — MAIN
# =============================================================================

main() {
  parse_args "$@"

  mkdir -p "$(dirname "${LOG_FILE}")"
  print_banner
  acquire_lock

  log "Caelestia Installer v${VERSION}"
  info "Mode: standalone (caelestia-cli + shell always built from bundled source)"
  info "Log:  ${LOG_FILE}"
  info "Repo: ${SCRIPT_DIR}"
  echo

  check_not_root
  check_arch
  auto_clone
  check_source_dirs
  detect_aur_helper

  # Maintenance modes exit early
  [[ "${DO_UNINSTALL}" == "true" ]] && do_uninstall

  if [[ "${DO_UPDATE}" == "true" ]]; then
    bootstrap_aur_helper
    check_internet
    do_update
  fi

  [[ "${DO_REBUILD}" == "true" ]] && do_rebuild

  # ── Full install ──
  check_internet

  step "Config backup"
  if confirm "Back up your existing ~/.config before starting?"; then
    backup_config
  else
    warn "Skipping backup"
  fi

  step "AUR helper"
  bootstrap_aur_helper

  if [[ "${SKIP_PACKAGES}" != "true" ]]; then
    install_packages
  else
    info "Skipping package installation (--skip-packages)"
  fi

  build_cli
  build_shell

  install_core_configs
  setup_papirus_sudoers

  install_spotify
  install_vscode
  install_discord
  install_zen

  init_scheme
  start_shell_daemon

  print_summary

  trap 'rm -f "${LOCK_FILE}"' EXIT
}

main "$@"
