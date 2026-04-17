"""Shell subcommand — start, control, and inspect the Caelestia Quickshell instance."""
from __future__ import annotations

import subprocess
from argparse import Namespace

from caelestia.utils.paths import c_cache_dir

_QS_BIN = "qs"
_QS_CONFIG = "caelestia"

# Image-cache lines are noisy and unactionable; filter them from all log output.
# FIXME: remove this filter once upstream adds proper logging-rule support.
_IMAGE_CACHE_NOISE = f"Cannot open: file://{c_cache_dir}/imagecache/"


def register_parser(subparsers) -> None:
    p = subparsers.add_parser("shell", help="start or message the shell")
    p.set_defaults(cls=Command)
    p.add_argument("message", nargs="*", help="a message to send to the shell")
    p.add_argument("-d", "--daemon",    action="store_true", help="start the shell detached")
    p.add_argument("-s", "--show",      action="store_true", help="print all shell IPC commands")
    p.add_argument("-l", "--log",       action="store_true", help="print the shell log")
    p.add_argument("-k", "--kill",      action="store_true", help="kill the shell")
    p.add_argument("--log-rules", metavar="RULES", help="log rules to apply")


def _qs_cmd(*extra: str) -> list[str]:
    """Return the base ``qs -c caelestia`` command extended with *extra* args."""
    return [_QS_BIN, "-c", _QS_CONFIG, *extra]


def _run_qs(*args: str) -> str:
    """Run a ``qs`` sub-command and return its stdout as a string."""
    return subprocess.check_output(_qs_cmd(*args), text=True)


def _is_log_noise(line: str) -> bool:
    """Return ``True`` for image-cache lines that should be suppressed."""
    return _IMAGE_CACHE_NOISE in line


class Command:
    """Entry point for the ``caelestia shell`` sub-command."""

    def __init__(self, args: Namespace) -> None:
        self.args = args

    def run(self) -> None:
        """Dispatch to the appropriate action based on the CLI flags."""
        if self.args.show:
            self._print_ipc()
        elif self.args.log:
            self._print_log()
        elif self.args.kill:
            self._kill()
        elif self.args.message:
            self._send_message(*self.args.message)
        else:
            self._start()

    def _build_start_cmd(self) -> list[str]:
        """Assemble the ``qs`` launch command from the current args."""
        cmd = _qs_cmd("-n")
        if self.args.log_rules:
            cmd.extend(["--log-rules", self.args.log_rules])
        if self.args.daemon:
            cmd.append("-d")
        return cmd

    def _start(self) -> None:
        """Launch the Quickshell instance, streaming filtered log output."""
        cmd = self._build_start_cmd()
        if self.args.daemon:
            subprocess.run(cmd)
        else:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
            for line in proc.stdout:
                if not _is_log_noise(line):
                    print(line, end="")

    def _kill(self) -> None:
        """Send the kill signal to the running shell instance."""
        _run_qs("kill")

    def _print_ipc(self) -> None:
        """Print all available IPC commands exposed by the shell."""
        print(_run_qs("ipc", "show"), end="")

    def _print_log(self) -> None:
        """Print the shell log, suppressing image-cache noise lines."""
        extra = ["-r", self.args.log_rules] if self.args.log_rules else []
        log = _run_qs("log", *extra)
        for line in log.splitlines():
            if not _is_log_noise(line):
                print(line)

    def _send_message(self, *args: str) -> None:
        """Send an IPC message to the running shell instance."""
        print(_run_qs("ipc", "call", *args), end="")
