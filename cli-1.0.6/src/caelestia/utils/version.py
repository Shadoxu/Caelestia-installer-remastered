import shutil
import subprocess
from pathlib import Path

from caelestia.utils.paths import config_dir


def _get_bundled_version() -> str | None:
    """Try to get version from the _version.py written by hatch-vcs at build time."""
    try:
        from caelestia._version import __version__
        return __version__
    except ImportError:
        pass
    return None


def print_version() -> None:
    # ── caelestia-cli version ──────────────────────────────────────────────────
    cli_ver = _get_bundled_version() or "1.0.6 (bundled)"
    print(f"caelestia-cli:   {cli_ver}")

    # ── caelestia-shell version (via installed version binary) ─────────────────
    try:
        shell_ver = subprocess.check_output(
            ["/usr/lib/caelestia/version", "-s"], text=True
        ).strip()
        print(f"caelestia-shell: {shell_ver}")
    except FileNotFoundError:
        print("caelestia-shell: not installed (run installer first)")
    except subprocess.CalledProcessError:
        print("caelestia-shell: version binary returned an error")

    # ── Quickshell version ─────────────────────────────────────────────────────
    if shutil.which("qs"):
        qs_ver = subprocess.check_output(["qs", "--version"], text=True).strip()
        print(f"quickshell:      {qs_ver}")
    else:
        print("quickshell:      not in PATH")

    # ── Dotfiles (git) ─────────────────────────────────────────────────────────
    # The hypr config symlink points back into the caelestia-main/ repo dir.
    print()
    try:
        caelestia_dir = (config_dir / "hypr").resolve().parent
        git_log = subprocess.check_output(
            ["git", "--git-dir", str(caelestia_dir / ".git"),
             "rev-list", "--format=%B", "--max-count=1", "HEAD"],
            text=True, stderr=subprocess.DEVNULL,
        )
        lines = git_log.splitlines()
        print("Dotfiles (caelestia-main):")
        print(f"    Commit:  {lines[1] if len(lines) > 1 else 'unknown'}")
        if len(lines) > 2:
            print(f"    Message: {lines[2]}")
    except (subprocess.CalledProcessError, IndexError, FileNotFoundError):
        print("Dotfiles: git history not available (bundled install)")

    # ── Install location ───────────────────────────────────────────────────────
    print()
    local_shell_dir = config_dir / "quickshell/caelestia"
    if local_shell_dir.exists():
        print(f"Local shell copy: {local_shell_dir}")
