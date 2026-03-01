"""Window manager module for browser automation

Provides utilities for finding, activating, and maximizing browser windows
to ensure the correct window is in focus before automated button clicking.
"""

from typing import Any, Dict, Optional

from .notification_window import _sanitize_notification_text

# PyGetWindow imports are optional - will be imported only if automation is enabled
try:
    import pygetwindow as gw

    PYGETWINDOW_AVAILABLE = True
except ImportError:
    PYGETWINDOW_AVAILABLE = False
    gw = None  # Set to None when not available


def _should_maximize_on_first_fail(config: Dict[str, Any]) -> bool:
    """Check whether maximize-on-fail retry is enabled (default: True)."""
    value = config.get("maximize_on_first_fail", True)
    if isinstance(value, bool):
        return value
    return True


def _maximize_window(config: Dict[str, Any]) -> bool:
    """Attempt to maximize the target or active window for better visibility."""
    if not PYGETWINDOW_AVAILABLE or gw is None:
        print("  ℹ pygetwindow is not available; skipping window maximization")
        return False

    window_title = config.get("window_title")
    try:
        target_window = None
        if window_title:
            print(f"  → Searching for window to maximize (title contains '{window_title}')")
            all_windows = gw.getAllWindows()
            matches = [w for w in all_windows if window_title.lower() in w.title.lower()]
            if matches:
                target_window = matches[0]

        if target_window is None:
            try:
                target_window = gw.getActiveWindow()
            except Exception:
                target_window = None

        if target_window is None:
            print("  ⚠ Could not find a window to maximize")
            return False

        if getattr(target_window, "isMinimized", False):
            target_window.restore()

        try:
            target_window.activate()
        except Exception:
            # Some platforms/window managers may not support activate; continue without failing
            pass

        try:
            target_window.maximize()
        except Exception:
            # Some platforms may not support maximize; rely on activate/restore
            pass

        print("  → Maximized target window to improve button detection")
        return True
    except Exception as e:
        print(f"  ⚠ Failed to maximize window: {e}")
        return False


def _maybe_maximize_window(config: Dict[str, Any]) -> bool:
    """Maximize window only when configured to do so."""
    if not _should_maximize_on_first_fail(config):
        return False
    return _maximize_window(config)


def _activate_window_by_title(window_title: Optional[str], config: Dict[str, Any]) -> bool:
    """Activate a window by its title to bring it to the foreground

    Args:
        window_title: The title (or partial title) of the window to activate
        config: Configuration dict (currently unused, reserved for future options)

    Returns:
        True if window was found and activated, False otherwise

    Raises:
        SystemExit: If pygetwindow is not available when window_title is configured (fail-fast)
    """
    if not window_title:
        print("  ⚠ No window_title configured, skipping window activation")
        return False

    if not PYGETWINDOW_AVAILABLE or gw is None:
        error_msg = (
            "\n" + "=" * 80 + "\n"
            "ERROR: PyGetWindow library is not available\n" + "=" * 80 + "\n"
            "\nWindow activation is configured (window_title is set) but the required\n"
            "pygetwindow library is not installed.\n"
            "\nPlease install the required dependencies:\n"
            "  pip install -r requirements-automation.txt\n"
            "\nOr install pygetwindow directly:\n"
            "  pip install pygetwindow\n"
            "\nAlternatively, remove the 'window_title' setting from your config.toml\n"
            "if you don't need window activation.\n" + "=" * 80
        )
        print(error_msg)
        raise SystemExit(1)

    active_window = None
    try:
        active_window = gw.getActiveWindow()
    except Exception:
        active_window = None

    active_title = getattr(active_window, "title", None)
    if isinstance(active_title, str) and window_title.lower() in active_title.lower():
        print(f"  ℹ Active window already matches title '{window_title}', skipping search")
        return True

    try:
        print(f"  → Looking for window with title containing: '{window_title}'")

        # Get all windows
        all_windows = gw.getAllWindows()

        # Find windows matching the title (case-insensitive partial match)
        matching_windows = [w for w in all_windows if window_title.lower() in w.title.lower()]

        if not matching_windows:
            print(f"  ⚠ No window found with title containing: '{window_title}'")
            print(f"     Available windows: {[w.title for w in all_windows[:10]]}")
            return False

        # Activate the first matching window
        target_window = matching_windows[0]
        print(f"  → Activating window: '{target_window.title}'")

        # Try to activate/restore the window
        if target_window.isMinimized:
            target_window.restore()

        target_window.activate()
        print("  ✓ Window activated successfully")
        return True

    except Exception as e:
        print(f"  ⚠ Failed to activate window: {e}")
        return False


def _get_active_window_title() -> Optional[str]:
    """Return the active window title if available, sanitized for display."""
    if not PYGETWINDOW_AVAILABLE or gw is None:
        return None
    try:
        window = gw.getActiveWindow()
    except Exception:
        return None

    title = getattr(window, "title", None)
    if isinstance(title, str) and title.strip():
        return _sanitize_notification_text(title)
    return None
