import re
from pathlib import Path

from src.gh_pr_phase_monitor.main import log_error_to_file


def test_log_error_to_file_writes_message_and_trace(tmp_path):
    base_dir: Path = tmp_path / "logs"
    exc = ValueError("boom")

    log_error_to_file("first message", exc, base_dir=base_dir)
    log_error_to_file("second message", None, base_dir=base_dir)

    log_path = base_dir / "error.log"
    content = log_path.read_text(encoding="utf-8")

    entries = [chunk for chunk in content.strip().split("\n\n") if chunk]
    assert len(entries) == 2

    first_lines = entries[0].splitlines()
    second_lines = entries[1].splitlines()

    timestamp_pattern = r"^\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+00:00 UTC\] first message$"

    assert re.match(timestamp_pattern, first_lines[0])
    assert "ValueError: boom" in "\n".join(first_lines[1:])
    assert first_lines[0] in content.splitlines()[0]

    assert second_lines[0].endswith("second message")
    assert content.index("first message") < content.index("second message")


def test_log_error_to_file_swallows_internal_errors(monkeypatch, tmp_path):
    base_dir: Path = tmp_path / "logs"

    def raise_on_open(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(Path, "open", raise_on_open)

    # Should not raise even if writing fails
    log_error_to_file("message", None, base_dir=base_dir)
