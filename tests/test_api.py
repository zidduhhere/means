"""Networking tests with a mocked HTTP transport (no live network)."""

import httpx
import pytest

from means import api
from means.api import LookupServiceError, WordNotFound, fetch_word


def _mock_get(monkeypatch, *, response=None, exc=None):
    def fake_get(url, timeout=None):
        if exc is not None:
            raise exc
        return response

    monkeypatch.setattr(api.httpx, "get", fake_get)


def test_fetch_word_success(monkeypatch):
    payload = [{"word": "hi", "meanings": []}]
    response = httpx.Response(200, json=payload, request=httpx.Request("GET", "http://x"))
    _mock_get(monkeypatch, response=response)

    assert fetch_word("hi") == payload


def test_fetch_word_404_raises_word_not_found(monkeypatch):
    response = httpx.Response(404, request=httpx.Request("GET", "http://x"))
    _mock_get(monkeypatch, response=response)

    with pytest.raises(WordNotFound):
        fetch_word("asdfqwerty")


def test_fetch_word_timeout_raises_service_error(monkeypatch):
    _mock_get(
        monkeypatch,
        exc=httpx.ConnectTimeout("timed out", request=httpx.Request("GET", "http://x")),
    )

    with pytest.raises(LookupServiceError):
        fetch_word("beautiful")


def test_fetch_word_other_status_raises_service_error(monkeypatch):
    response = httpx.Response(500, request=httpx.Request("GET", "http://x"))
    _mock_get(monkeypatch, response=response)

    with pytest.raises(LookupServiceError):
        fetch_word("beautiful")
