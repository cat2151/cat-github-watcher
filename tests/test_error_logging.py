from pathlib import Path

from src.gh_pr_phase_monitor.main import log_error_to_file


def test_log_error_to_file_writes_message_and_trace(tmp_path):
    base_dir: Path = tmp_path / "logs"
    exc = ValueError("boom")

    log_error_to_file("first message", exc, base_dir=base_dir)
    log_error_to_file("second message", None, base_dir=base_dir)

    log_path = base_dir / "error.log"
    content = log_path.read_text(encoding="utf-8")

    assert "first message" in content
    assert "ValueError: boom" in content
    assert "second message" in content
