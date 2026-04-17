"""Low-level file writers and terminal-sequence appliers."""
from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

from caelestia.utils.logging import log_exception
from caelestia.utils.paths import c_state_dir


def write_file(path: Path, content: str) -> None:
    """Atomically write *content* to *path*, creating parent dirs as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    # delete=False: shutil.move() relocates the file before the context exits,
    # so default delete=True would raise FileNotFoundError during cleanup.
    tmp = tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False, suffix=".tmp")
    try:
        tmp.write(content)
        tmp.flush()
        tmp.close()
        shutil.move(tmp.name, path)
    except Exception:
        tmp.close()
        Path(tmp.name).unlink(missing_ok=True)
        raise


@log_exception
def apply_terms(sequences: str) -> None:
    """Write *sequences* to every open pseudo-terminal (best-effort, non-blocking)."""
    state = c_state_dir / "sequences.txt"
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(sequences)

    for pt in Path("/dev/pts").iterdir():
        if not pt.name.isdigit():
            continue
        try:
            fd = os.open(str(pt), os.O_WRONLY | os.O_NONBLOCK | os.O_NOCTTY)
            try:
                os.write(fd, sequences.encode())
            finally:
                os.close(fd)
        except (PermissionError, OSError, BlockingIOError):
            pass  # terminal is busy, closed, or inaccessible — skip silently
