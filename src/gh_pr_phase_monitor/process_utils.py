"""
Process detection utilities
"""

import subprocess


def is_process_running(process_name: str) -> bool:
    """Check if a process with the given name is currently running

    Args:
        process_name: Name of the process to check (e.g., "cat-window-watcher")

    Returns:
        True if the process is running, False otherwise
    """
    try:
        # Use pgrep for more reliable process detection
        # -f flag searches the full command line
        # This is more reliable than parsing ps output
        result = subprocess.run(
            ["pgrep", "-f", process_name],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

        # pgrep returns 0 if at least one process matches, 1 if no processes match
        # It prints the PIDs of matching processes to stdout
        if result.returncode == 0 and result.stdout.strip():
            return True
        return False
    except FileNotFoundError:
        # pgrep command not available, fallback to ps aux approach
        try:
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )

            if result.returncode == 0:
                # Check if process name appears in the output
                # This is a simpler fallback when pgrep is not available
                return process_name in result.stdout
            return False
        except (subprocess.SubprocessError, FileNotFoundError):
            # If both commands fail, assume process is not running
            return False
    except subprocess.SubprocessError:
        # If pgrep fails for any other reason, assume process is not running
        return False
