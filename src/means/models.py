"""Dataclasses that model a dictionary entry.

These encapsulate the JSON shape returned by dictionaryapi.dev so the rest of
the application never touches raw dicts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

# Verbosity levels (kept here so the CLI can reference them without importing
# the Textual UI layer).
VERBOSITY_DEFAULT = 0
VERBOSITY_VERBOSE = 1
VERBOSITY_ALL = 2


@dataclass
class Definition:
    text: str
    example: Optional[str] = None
    synonyms: List[str] = field(default_factory=list)


@dataclass
class Meaning:
    part_of_speech: str
    definitions: List[Definition] = field(default_factory=list)


@dataclass
class Entry:
    word: str
    phonetic: Optional[str]
    meanings: List[Meaning] = field(default_factory=list)

    @classmethod
    def parse(cls, raw_json: List[dict]) -> "Entry":
        """Build an Entry from the API's list-of-entries payload.

        The API returns a list (one item per homograph). We merge their
        meanings into a single Entry and take the first available phonetic.
        """
        if not raw_json:
            raise ValueError("empty payload")

        first = raw_json[0]
        word = first.get("word", "")
        phonetic = _first_phonetic(raw_json)

        meanings: List[Meaning] = []
        for entry in raw_json:
            for raw_meaning in entry.get("meanings", []):
                meanings.append(_parse_meaning(raw_meaning))

        meanings.sort(key=_pos_priority)
        return cls(word=word, phonetic=phonetic, meanings=meanings)


_POS_ORDER = ["adjective", "adverb", "verb", "noun", "pronoun", "preposition", "conjunction", "interjection"]


def _pos_priority(meaning: "Meaning") -> int:
    pos = meaning.part_of_speech.lower()
    try:
        return _POS_ORDER.index(pos)
    except ValueError:
        return len(_POS_ORDER)


def _first_phonetic(raw_json: List[dict]) -> Optional[str]:
    for entry in raw_json:
        if entry.get("phonetic"):
            return entry["phonetic"]
        for ph in entry.get("phonetics", []):
            if ph.get("text"):
                return ph["text"]
    return None


def _parse_meaning(raw_meaning: dict) -> Meaning:
    definitions = [
        _parse_definition(d) for d in raw_meaning.get("definitions", [])
    ]
    return Meaning(
        part_of_speech=raw_meaning.get("partOfSpeech", ""),
        definitions=definitions,
    )


def _parse_definition(raw: dict) -> Definition:
    return Definition(
        text=raw.get("definition", ""),
        example=raw.get("example"),
        synonyms=list(raw.get("synonyms", []) or []),
    )
