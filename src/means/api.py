"""Networking layer: fetch raw definition data from dictionaryapi.dev.

This module has no dependency on the UI. It either returns the raw JSON payload
(a list of entry dicts) or raises one of the typed errors below.
"""

from __future__ import annotations

from typing import List

import httpx

API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
DEFAULT_TIMEOUT = 10.0


class MeansError(Exception):
    """Base class for all means lookup errors."""


class WordNotFound(MeansError):
    """The dictionary has no entry for the requested word."""

    def __init__(self, word: str):
        self.word = word
        super().__init__(f"No definition found for {word!r}")


class LookupServiceError(MeansError):
    """The dictionary service could not be reached or returned an error."""


def fetch_word(word: str, *, timeout: float = DEFAULT_TIMEOUT) -> List[dict]:
    """Fetch the raw JSON payload for ``word``.

    Raises:
        WordNotFound: the API returned 404 for this word.
        LookupServiceError: timeout, connection failure, or unexpected status.
    """
    url = API_URL.format(word=word)
    try:
        response = httpx.get(url, timeout=timeout)
    except httpx.RequestError as exc:
        raise LookupServiceError(
            "Could not reach the dictionary service"
        ) from exc

    if response.status_code == 404:
        raise WordNotFound(word)
    if response.status_code != 200:
        raise LookupServiceError(
            f"Dictionary service returned status {response.status_code}"
        )

    try:
        return response.json()
    except ValueError as exc:
        raise LookupServiceError(
            "Dictionary service returned an invalid response"
        ) from exc
