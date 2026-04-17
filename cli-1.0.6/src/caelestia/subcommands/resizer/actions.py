"""Window action applicators — resize, float, center, and picture-in-picture."""
from __future__ import annotations

from caelestia.utils import hypr
from caelestia.utils.logging import log_message


def _get_window(window_id: str) -> dict | None:
    """Return the Hyprland client dict for *window_id*, or ``None`` if not found."""
    try:
        clients = hypr.message("clients")
        if isinstance(clients, list):
            return next((c for c in clients if isinstance(c, dict) and c.get("address") == f"0x{window_id}"), None)
    except Exception:
        pass
    return None


def apply_window_actions(window_id: str, width: str, height: str, actions: list[str]) -> bool:
    """Apply *actions* to the window identified by *window_id*.

    Returns ``True`` on success, ``False`` on failure.
    """
    cmds: list[str] = []

    if "pip" in actions:
        return apply_pip(window_id)

    if "float" in actions:
        info = _get_window(window_id)
        if info and not info.get("floating", False):
            cmds.append(f"dispatch togglefloating address:0x{window_id}")

    cmds.append(f"dispatch resizewindowpixel exact {width} {height},address:0x{window_id}")

    if "center" in actions:
        cmds.append("dispatch centerwindow")

    try:
        hypr.batch(*cmds)
        log_message(f"Applied actions to window 0x{window_id}: {width}x{height} ({', '.join(actions)})")
        return True
    except Exception as e:
        log_message(f"ERROR: failed to apply window actions for 0x{window_id}: {e}")
        return False


def apply_pip(window_id: str) -> bool:
    """Scale and reposition a floating window into a picture-in-picture corner."""
    address = f"0x{window_id}"
    try:
        clients = hypr.message("clients")
        window  = next((c for c in clients if isinstance(c, dict) and c.get("address") == address), None)
        if not window or not window.get("floating", False):
            return False

        workspaces = hypr.message("workspaces")
        ws_name    = window.get("workspace", {}).get("name")
        workspace  = next((w for w in workspaces if isinstance(w, dict) and w.get("name") == ws_name), None)
        if not workspace:
            return False

        monitors  = hypr.message("monitors")
        monitor   = next((m for m in monitors if isinstance(m, dict) and m.get("id") == workspace.get("monitorID")), None)
        if not monitor:
            return False

        w, h   = window["size"]
        mh     = monitor["height"]  / monitor["scale"]
        mw     = monitor["width"]   / monitor["scale"]
        mx, my = monitor["x"], monitor["y"]

        scale  = mh / 4 / h
        sw     = max(int(w * scale), 200)
        sh     = max(int(h * scale), 150)
        offset = min(mw, mh) * 0.03

        hypr.batch(
            f"dispatch resizewindowpixel exact {sw} {sh},address:{address}",
            f"dispatch movewindowpixel exact {int(mx + mw - sw - offset)} {int(my + mh - sh - offset)},address:{address}",
        )
        log_message(f"PiP applied to window {address}: {sw}x{sh}")
        return True

    except Exception as e:
        log_message(f"ERROR: failed to apply PiP to window 0x{window_id}: {e}")
        return False
