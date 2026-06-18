"""Parsing tests: a captured API payload becomes the right dataclasses."""

import pytest

from means.models import Entry

SAMPLE = [
    {
        "word": "beautiful",
        "phonetic": "/ˈbjuːtɪfʊl/",
        "phonetics": [{"text": "/ˈbjuːtɪfʊl/"}],
        "meanings": [
            {
                "partOfSpeech": "adjective",
                "definitions": [
                    {
                        "definition": "Attractive and possessing beauty.",
                        "example": "She was a beautiful woman.",
                        "synonyms": ["lovely", "gorgeous"],
                    },
                    {
                        "definition": "Of a very high standard; excellent.",
                        "example": "a beautiful piece of music",
                        "synonyms": [],
                    },
                ],
            }
        ],
    }
]


def test_parse_basic_fields():
    entry = Entry.parse(SAMPLE)
    assert entry.word == "beautiful"
    assert entry.phonetic == "/ˈbjuːtɪfʊl/"
    assert len(entry.meanings) == 1


def test_parse_definitions_and_example():
    entry = Entry.parse(SAMPLE)
    meaning = entry.meanings[0]
    assert meaning.part_of_speech == "adjective"
    assert len(meaning.definitions) == 2
    first = meaning.definitions[0]
    assert first.text == "Attractive and possessing beauty."
    assert first.example == "She was a beautiful woman."
    assert first.synonyms == ["lovely", "gorgeous"]


def test_parse_phonetic_falls_back_to_phonetics_list():
    payload = [
        {
            "word": "test",
            "phonetics": [{"text": ""}, {"text": "/tɛst/"}],
            "meanings": [],
        }
    ]
    assert Entry.parse(payload).phonetic == "/tɛst/"


def test_parse_missing_example_is_none():
    payload = [
        {
            "word": "x",
            "meanings": [
                {
                    "partOfSpeech": "noun",
                    "definitions": [{"definition": "A thing."}],
                }
            ],
        }
    ]
    entry = Entry.parse(payload)
    assert entry.phonetic is None
    assert entry.meanings[0].definitions[0].example is None
    assert entry.meanings[0].definitions[0].synonyms == []


def test_parse_empty_payload_raises():
    with pytest.raises(ValueError):
        Entry.parse([])
