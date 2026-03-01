"""Notification window module for browser automation

Provides an on-screen notification window shown during automated button clicking,
along with theme utilities and notification management helpers.
"""

import re
import subprocess
import sys
import threading
import time
import traceback
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from .colors import Colors

# tkinter imports are optional - used for on-screen notification window
try:
    import tkinter as tk
    from tkinter import messagebox

    TKINTER_AVAILABLE = True
except Exception:
    TKINTER_AVAILABLE = False
    tk = None
    messagebox = None

_SUBPROCESS_TIMEOUT_SECONDS = 0.5

# Default notification window settings for button-based automation
DEFAULT_NOTIFICATION_WIDTH = 400
DEFAULT_NOTIFICATION_HEIGHT = 150
DEFAULT_NOTIFICATION_POSITION_X = 100
DEFAULT_NOTIFICATION_POSITION_Y = 100

_SIMPLE_ANSI_HEX = {
    "30": "#000000",
    "31": "#ff0000",
    "32": "#00ff00",
    "33": "#ffff00",
    "34": "#0000ff",
    "35": "#ff00ff",
    "36": "#00ffff",
    "37": "#ffffff",
    "90": "#555555",
    "91": "#ff5555",
    "92": "#55ff55",
    "93": "#ffff55",
    "94": "#5555ff",
    "95": "#ff55ff",
    "96": "#55ffff",
    "97": "#ffffff",
}


def _log_error(message: str, exc: Exception | BaseException | None = None) -> None:
    """Append an error entry to logs/error.log without raising further exceptions."""
    try:
        log_dir = Path("logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "error.log"
        timestamp = datetime.now(UTC).isoformat(timespec="seconds")
        with log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(f"[{timestamp} UTC] {message}\n")
            if exc:
                log_file.writelines(traceback.format_exception(type(exc), exc, exc.__traceback__))
            log_file.write("\n")
    except Exception as log_exc:
        # Logging must never raise; emit minimal message to stderr as last resort.
        print(
            f"[notification_window._log_error] Failed to write to error.log: {log_exc!r} (original message: {message})",
            file=sys.stderr,
        )


def _ansi_to_hex(color_code: str) -> Optional[str]:
    if not color_code:
        return None

    match = re.search(r"\x1b\[([0-9;]+)m", color_code)
    if not match:
        return None

    params = match.group(1).split(";")

    if len(params) >= 5 and params[0] == "38" and params[1] == "2":
        try:
            red, green, blue = (int(params[2]), int(params[3]), int(params[4]))
            return f"#{red:02x}{green:02x}{blue:02x}"
        except ValueError:
            return None

    for param in reversed(params):
        if param in _SIMPLE_ANSI_HEX:
            return _SIMPLE_ANSI_HEX[param]
    return None


def _sanitize_notification_text(text: str) -> str:
    """Convert newlines to spaces for splash display and trim whitespace."""
    if not isinstance(text, str):
        return ""
    sanitized = text.replace("\r", " ").replace("\n", " ")
    return " ".join(sanitized.split())


def _is_dark_mode_enabled() -> bool:
    try:
        if sys.platform == "darwin":
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
                timeout=_SUBPROCESS_TIMEOUT_SECONDS,
            )
            return result.stdout.strip().lower() == "dark"

        if sys.platform.startswith("win"):
            try:
                import winreg

                with winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
                ) as key:
                    apps_use_light, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return apps_use_light == 0
            except Exception:
                return False

        # Linux / other POSIX (best-effort GNOME detection)
        gsettings_cmds = [
            ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
            ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
        ]
        for cmd in gsettings_cmds:
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    check=False,
                    timeout=_SUBPROCESS_TIMEOUT_SECONDS,
                )
                output = result.stdout.strip().lower()
                if result.returncode == 0 and output:
                    if "dark" in output:
                        return True
                    if "light" in output:
                        return False
            except subprocess.TimeoutExpired:
                return False
            except Exception:
                continue
    except Exception:
        return False

    return False


def _get_notification_theme() -> Dict[str, str]:
    dark_mode = _is_dark_mode_enabled()
    background = "#111111" if dark_mode else "#ffffff"
    fallback_text = "#f5f5f5" if dark_mode else "#111111"

    accent = _ansi_to_hex(Colors.BLUE) or _ansi_to_hex(Colors.CYAN) or _ansi_to_hex(Colors.GREEN)
    text_color = accent or fallback_text

    return {"background": background, "text": text_color, "accent": accent or text_color}


def _parse_int_setting(value: Any, default: int) -> int:
    """Parse an integer setting with a safe fallback."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class NotificationWindow:
    """Lightweight topmost notification window shown during automation."""

    def __init__(
        self,
        message: str,
        width: int,
        height: int,
        x: int,
        y: int,
        cancel_message: Optional[str] = None,
        on_user_cancel: Optional[Callable[[], None]] = None,
    ):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.root = None
        self._should_close = False
        self._closed_by_user = False
        self.cancel_message = cancel_message
        self._on_user_cancel = on_user_cancel
        self._message_var = None
        self.message = _sanitize_notification_text(message)
        self._last_rendered_message = self.message

    def show(self) -> None:
        """Show the notification window on a separate thread."""
        if not TKINTER_AVAILABLE or tk is None:
            return

        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()

    def _run(self) -> None:
        """Render the window and block in its own Tk event loop."""
        try:
            self.root = tk.Tk()
            self.root.title("処理中")
            theme = _get_notification_theme()
            self.root.configure(
                bg=theme["background"],
                highlightbackground=theme["accent"],
                highlightcolor=theme["accent"],
                highlightthickness=2,
            )
            geometry = f"{self.width}x{self.height}+{self.x}+{self.y}"
            self.root.geometry(geometry)
            self.root.attributes("-topmost", True)
            self.root.protocol("WM_DELETE_WINDOW", self._on_user_close)

            wraplength = max(0, self.width - 50)
            self._message_var = tk.StringVar(value=self.message)
            label = tk.Label(
                self.root,
                textvariable=self._message_var,
                font=("Arial", 16),
                wraplength=wraplength,
                bg=theme["background"],
                fg=theme["text"],
            )
            label.pack(expand=True, padx=20, pady=20)

            def _check_close() -> None:
                """Poll for close requests from other threads and shut down Tk safely."""
                if self.root is None or not bool(self.root.winfo_exists()):
                    return
                if self.message != self._last_rendered_message and self._message_var is not None:
                    try:
                        self._message_var.set(self.message)
                        self._last_rendered_message = self.message
                    except Exception:
                        pass
                if self._should_close and self.root is not None:
                    try:
                        self.root.quit()
                        self.root.destroy()
                    except Exception as e:
                        print(f"  ⚠ Failed to close notification window cleanly: {e}")
                    return
                if self.root is not None:
                    self.root.after(100, _check_close)

            self.root.after(100, _check_close)
            self.root.mainloop()
        except Exception:
            self.root = None

    def close(self) -> None:
        """Request the notification window to close."""
        self._should_close = True

    def _on_user_close(self) -> None:
        """Handle manual close from the user."""
        self._closed_by_user = True
        self._should_close = True
        if self._on_user_cancel is not None:
            self._on_user_cancel()
        self._show_cancel_dialog()
        try:
            if self.root is not None:
                self.root.quit()
                self.root.destroy()
        except Exception as e:
            print(f"  ⚠ Failed to close notification window cleanly: {e}")

    def _show_cancel_dialog(self) -> None:
        """Display a one-button dialog when the user cancels automation."""
        if not self.cancel_message or messagebox is None:
            return
        try:
            parent = self.root if self.root is not None else None
            messagebox.showinfo("auto assign", self.cancel_message, parent=parent)
        except Exception as e:
            print(f"  ⚠ Failed to show cancellation dialog: {e}")

    @property
    def closed_by_user(self) -> bool:
        return self._closed_by_user

    def update_message(self, message: str) -> None:
        """Update the notification text safely from other threads."""
        sanitized = _sanitize_notification_text(message)
        self.message = sanitized


def _was_closed_by_user(notification: Optional[NotificationWindow]) -> bool:
    """Check whether the notification window was explicitly closed by the user."""
    if notification is None:
        return False
    return getattr(notification, "closed_by_user", False) is True


def _wait_with_cancellation(duration: float, notification: Optional[NotificationWindow]) -> bool:
    """Wait for a duration while honoring user cancellation requests.

    Returns:
        True if the user closed the notification window during the wait, False otherwise.
    """
    if duration <= 0:
        return _was_closed_by_user(notification)

    remaining = float(duration)
    interval = 0.5

    while remaining > 0:
        if _was_closed_by_user(notification):
            return True
        sleep_time = min(interval, remaining)
        time.sleep(sleep_time)
        remaining -= sleep_time

    return _was_closed_by_user(notification)


def _start_button_notification(
    config: Dict[str, Any],
    default_message: str,
    cancel_message: Optional[str] = None,
    on_user_cancel: Optional[Callable[[], None]] = None,
) -> Optional[NotificationWindow]:
    """Create and show a notification window when configured."""
    if not config.get("notification_enabled", True):
        return None

    if not TKINTER_AVAILABLE or tk is None:
        print("  ℹ Tkinter is not available; skipping notification window")
        return None

    width = _parse_int_setting(config.get("notification_width", DEFAULT_NOTIFICATION_WIDTH), DEFAULT_NOTIFICATION_WIDTH)
    height = _parse_int_setting(
        config.get("notification_height", DEFAULT_NOTIFICATION_HEIGHT), DEFAULT_NOTIFICATION_HEIGHT
    )
    pos_x = _parse_int_setting(
        config.get("notification_position_x", DEFAULT_NOTIFICATION_POSITION_X), DEFAULT_NOTIFICATION_POSITION_X
    )
    pos_y = _parse_int_setting(
        config.get("notification_position_y", DEFAULT_NOTIFICATION_POSITION_Y), DEFAULT_NOTIFICATION_POSITION_Y
    )
    message = _sanitize_notification_text(str(config.get("notification_message", default_message)))

    window = NotificationWindow(message, width, height, pos_x, pos_y, cancel_message=cancel_message, on_user_cancel=on_user_cancel)
    try:
        window.show()
        return window
    except Exception as e:
        print(f"  ⚠ Failed to show notification window: {e}")
        return None


def _close_notification_window(window: Optional[NotificationWindow]) -> None:
    """Close notification window safely."""
    if window:
        try:
            window.close()
        except Exception as e:
            print(f"  ⚠ Failed to close notification window: {e}")


def _compose_status_message(status: str, active_window_title: Optional[str]) -> str:
    base_status = _sanitize_notification_text(status)
    active_title = _sanitize_notification_text(active_window_title) if active_window_title else ""
    if not active_title:
        return base_status
    return f"active window titleは、{active_title} です / {base_status}"


def _update_notification_status(
    notification: Optional[NotificationWindow], status: str, active_window_title: Optional[str]
) -> None:
    """Update splash window text with current search status."""
    if notification is None or _was_closed_by_user(notification):
        return
    message = _compose_status_message(status, active_window_title)
    try:
        notification.update_message(message)
    except Exception as exc:
        _log_error("Failed to update notification message", exc)
