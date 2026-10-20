"""Shared URL policy coverage for community search result adapters."""

import ast
from pathlib import Path
from unittest.mock import patch

import pytest

from deerflow.community.url_safety import screen_public_result_urls

_COMMUNITY = Path(__file__).parents[1] / "packages" / "harness" / "deerflow" / "community"
_SEARCH_ADAPTERS = (
    "brave",
    "ddg_search",
    "exa",
    "fastcrw",
    "firecrawl",
    "groundroute",
    "searxng",
    "serper",
    "serply",
    "sofya",
    "tavily",
    "tencent_wsa",
    "webz",
    "youcom",
)


@pytest.mark.parametrize("provider", _SEARCH_ADAPTERS)
def test_search_provider_calls_the_shared_result_url_policy(provider: str) -> None:
    source = (_COMMUNITY / provider / "tools.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    calls = {node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}

    assert calls & {"safe_public_result_url", "screen_public_result_urls"}


def test_search_results_drop_non_public_urls_and_keep_the_screened_value() -> None:
    rows = [
        {"title": "private", "url": "http://169.254.169.254/latest/meta-data"},
        {"title": "bad scheme", "url": "file:///etc/passwd"},
        {"title": "public", "url": "  https://example.com/result  "},
    ]

    with patch("socket.getaddrinfo", side_effect=AssertionError("screening must not do DNS")):
        assert screen_public_result_urls(rows) == [{"title": "public", "url": "https://example.com/result"}]
