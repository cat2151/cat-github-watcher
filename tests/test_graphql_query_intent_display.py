"""Tests for query intent and cost display in execute_graphql_query."""

import json
import subprocess

from src.gh_pr_phase_monitor.github.graphql_client import execute_graphql_query


def _make_subprocess_result(data: dict) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(
        args=["gh", "api", "graphql"],
        returncode=0,
        stdout=json.dumps(data),
        stderr="",
    )


def test_intent_is_printed_before_query(mocker, capsys):
    response = {"data": {"viewer": {"login": "testuser"}}}
    mocker.patch("subprocess.run", return_value=_make_subprocess_result(response))
    execute_graphql_query("query { viewer { login } }", intent="ユーザー情報取得")

    captured = capsys.readouterr()
    assert "[GraphQL] クエリ意図: ユーザー情報取得" in captured.out


def test_no_intent_prints_nothing_extra(mocker, capsys):
    response = {"data": {"viewer": {"login": "testuser"}}}
    mocker.patch("subprocess.run", return_value=_make_subprocess_result(response))
    execute_graphql_query("query { viewer { login } }")

    captured = capsys.readouterr()
    assert "クエリ意図" not in captured.out


def test_cost_is_printed_when_rate_limit_in_response(mocker, capsys):
    response = {
        "data": {
            "viewer": {"login": "testuser"},
            "rateLimit": {"cost": 7, "remaining": 4993},
        }
    }
    mocker.patch("subprocess.run", return_value=_make_subprocess_result(response))
    execute_graphql_query("query { viewer { login } rateLimit { cost remaining } }")

    captured = capsys.readouterr()
    assert "消費コスト: 7点" in captured.out
    assert "残=4993" in captured.out


def test_cost_not_printed_when_no_rate_limit_in_response(mocker, capsys):
    response = {"data": {"viewer": {"login": "testuser"}}}
    mocker.patch("subprocess.run", return_value=_make_subprocess_result(response))
    execute_graphql_query("query { viewer { login } }")

    captured = capsys.readouterr()
    assert "消費コスト" not in captured.out


def test_intent_and_cost_both_printed_together(mocker, capsys):
    response = {
        "data": {
            "rateLimit": {"cost": 3, "remaining": 4997},
        }
    }
    mocker.patch("subprocess.run", return_value=_make_subprocess_result(response))
    execute_graphql_query("query { rateLimit { cost remaining } }", intent="PR詳細取得 (バッチ1: 5リポジトリ)")

    captured = capsys.readouterr()
    assert "[GraphQL] クエリ意図: PR詳細取得 (バッチ1: 5リポジトリ)" in captured.out
    assert "消費コスト: 3点" in captured.out
    assert "残=4997" in captured.out
