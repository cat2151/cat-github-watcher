"""Cargo subprocess operations for local repository monitoring."""

from __future__ import annotations

import subprocess


def _run_cargo_install(path: str) -> tuple[bool, str]:
    """Run `cargo install --force --path <path>`. Returns (success, message)."""
    try:
        result = subprocess.run(
            ["cargo", "install", "--force", "--path", path],
            cwd=path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,
        )
        if result.returncode != 0:
            err = result.stderr.strip() or result.stdout.strip() or "cargo install 失敗"
            return False, _summarize_cargo_error(err)
        return True, "cargo install 完了"
    except FileNotFoundError:
        return False, "cargo コマンドが見つかりません (PATH を確認してください)"
    except subprocess.TimeoutExpired:
        return False, "cargo install がタイムアウトしました"


def _summarize_cargo_error(raw: str, max_len: int = 120) -> str:
    """Return a concise single-line summary of cargo error output.

    Cargo compiler errors can span hundreds of lines. This function picks the
    most informative line (first line starting with "error") and truncates it
    so that terminal output stays readable.
    """
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    if not lines:
        return "cargo install 失敗"

    def _truncate(ln: str) -> str:
        return ln[:max_len] + ("…" if len(ln) > max_len else "")

    # Prefer the first "error:" summary line (e.g. "error: could not compile …")
    for ln in lines:
        if ln.startswith("error"):
            return _truncate(ln)
    # Fall back to the last non-empty line
    return _truncate(lines[-1])
