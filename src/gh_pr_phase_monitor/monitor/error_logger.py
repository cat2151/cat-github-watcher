"""
Error logging utilities for GitHub PR Phase Monitor
"""

import traceback
from datetime import UTC, datetime
from pathlib import Path

LOG_DIR = Path("logs")


def log_error_to_file(message: str, exc: Exception | None = None, base_dir: Path | str | None = None) -> None:
    """Append an error entry to logs/error.log without interrupting execution"""
    try:
        log_dir = Path(base_dir) if base_dir else LOG_DIR
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "error.log"
        timestamp = datetime.now(UTC).isoformat(timespec="seconds")
        with log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(f"[{timestamp} UTC] {message}\n")
            if exc:
                log_file.writelines(traceback.format_exception(type(exc), exc, exc.__traceback__))
            log_file.write("\n")
    except Exception:
        # Avoid any logging-related failures impacting the main loop
        pass
