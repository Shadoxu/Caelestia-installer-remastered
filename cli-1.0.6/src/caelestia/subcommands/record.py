"""Record subcommand — start, pause, and stop screen recordings."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import time
from argparse import Namespace
from datetime import datetime
from pathlib import Path

from caelestia.utils.notify import close_notification, notify
from caelestia.utils.paths import recording_notif_path, recording_path, recordings_dir, user_config_path

_RECORDER = "gpu-screen-recorder"


def register_parser(subparsers) -> None:
    p = subparsers.add_parser("record", help="start a screen recording")
    p.set_defaults(cls=Command)
    p.add_argument("-r", "--region",    nargs="?", const="slurp", help="record a region")
    p.add_argument("-s", "--sound",     action="store_true",       help="record audio")
    p.add_argument("-p", "--pause",     action="store_true",       help="pause/resume the recording")
    p.add_argument("-c", "--clipboard", action="store_true",       help="copy recording path to clipboard")


class Command:
    """Toggle, pause, or start a gpu-screen-recorder session."""

    def __init__(self, args: Namespace) -> None:
        self.args = args

    # ------------------------------------------------------------------ public

    def run(self) -> None:
        if self.args.pause:
            subprocess.run(["pkill", "-USR2", "-f", _RECORDER], stdout=subprocess.DEVNULL)
        elif self._is_running():
            self._stop()
        else:
            self._start()

    # ----------------------------------------------------------------- private

    def _is_running(self) -> bool:
        return subprocess.run(["pidof", _RECORDER], stdout=subprocess.DEVNULL).returncode == 0

    @staticmethod
    def _intersects(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
        """Return True if rectangles *a* and *b* overlap."""
        return (
            a[0] < b[0] + b[2] and a[0] + a[2] > b[0]
            and a[1] < b[1] + b[3] and a[1] + a[3] > b[1]
        )

    def _build_recorder_args(self, monitors: list[dict]) -> list[str]:
        """Assemble the gpu-screen-recorder argument list from the current flags."""
        args = ["-w"]

        if self.args.region:
            region = (
                subprocess.check_output(["slurp", "-f", "%wx%h+%x+%y"], text=True)
                if self.args.region == "slurp"
                else self.args.region.strip()
            )
            args += ["region", "-region", region]
            args += ["-f", str(self._region_refresh_rate(region, monitors))]
        else:
            focused = next((m for m in monitors if m["focused"]), None)
            if focused:
                args += [focused["name"], "-f", str(round(focused["refreshRate"]))]

        if self.args.sound:
            args += ["-a", "default_output"]

        args += self._extra_args_from_config()
        return args

    def _region_refresh_rate(self, region: str, monitors: list[dict]) -> int:
        """Return the highest refresh rate of monitors that intersect *region*."""
        m = re.match(r"(\d+)x(\d+)\+(\d+)\+(\d+)", region)
        if not m:
            raise ValueError(f"Invalid region: {region}")
        w, h, x, y = map(int, m.groups())
        rect = (x, y, w, h)
        return max(
            (
                round(mon["refreshRate"])
                for mon in monitors
                if self._intersects((mon["x"], mon["y"], mon["width"], mon["height"]), rect)
            ),
            default=60,
        )

    @staticmethod
    def _extra_args_from_config() -> list[str]:
        """Return ``record.extraArgs`` from the user config, or an empty list."""
        try:
            cfg = json.loads(user_config_path.read_text())
            extra = cfg.get("record", {}).get("extraArgs", [])
            if not isinstance(extra, list):
                raise TypeError(f"record.extraArgs must be an array, got {type(extra)}")
            return extra
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _start(self) -> None:
        monitors = json.loads(subprocess.check_output(["hyprctl", "monitors", "-j"]))
        rec_args = self._build_recorder_args(monitors)

        recording_path.parent.mkdir(parents=True, exist_ok=True)
        proc = subprocess.Popen(
            [_RECORDER, *rec_args, "-o", str(recording_path)], start_new_session=True
        )
        notif_id = notify("-p", "Recording started", "Recording…")
        recording_notif_path.write_text(notif_id)

        try:
            if proc.wait(1) != 0:
                close_notification(notif_id)
                notify(
                    "Recording failed",
                    f"Command `{' '.join(proc.args)}` failed with exit code {proc.returncode}",
                )
        except subprocess.TimeoutExpired:
            pass  # still running — good

    def _stop(self) -> None:
        subprocess.run(["pkill", "-f", _RECORDER], stdout=subprocess.DEVNULL)
        while self._is_running():
            time.sleep(0.1)

        dest = recordings_dir / f"recording_{datetime.now().strftime('%Y%m%d_%H-%M-%S')}.mp4"
        recordings_dir.mkdir(exist_ok=True, parents=True)
        shutil.move(recording_path, dest)

        try:
            close_notification(recording_notif_path.read_text())
        except IOError:
            pass

        if self.args.clipboard:
            uri = Path(dest).resolve().as_uri() + "\n"
            subprocess.run(["wl-copy", "--type", "text/uri-list"], input=uri.encode())

        self._handle_stop_action(dest)

    def _handle_stop_action(self, dest: Path) -> None:
        action = notify(
            "--action=watch=Watch",
            "--action=open=Open",
            "--action=delete=Delete",
            "Recording stopped",
            f"Recording saved in {dest}",
        )
        if action == "watch":
            subprocess.Popen(["app2unit", "-O", dest], start_new_session=True)
        elif action == "open":
            result = subprocess.run([
                "dbus-send", "--session",
                "--dest=org.freedesktop.FileManager1",
                "--type=method_call",
                "/org/freedesktop/FileManager1",
                "org.freedesktop.FileManager1.ShowItems",
                f"array:string:file://{dest}", "string:",
            ])
            if result.returncode != 0:
                subprocess.Popen(["app2unit", "-O", dest.parent], start_new_session=True)
        elif action == "delete":
            dest.unlink()
