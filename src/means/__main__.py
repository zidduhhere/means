"""CLI entry point for ``means``.

Parses arguments, fetches and parses the entry, then hands it to the Textual UI.
Lookup failures are shown as a friendly card rather than a traceback.
"""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .api import LookupServiceError, WordNotFound, fetch_word
from .models import (
    VERBOSITY_ALL,
    VERBOSITY_DEFAULT,
    VERBOSITY_VERBOSE,
    Entry,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="means",
        description="Show the meaning of a word and an example.",
    )
    parser.add_argument("word", help="the word to look up")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="show every part of speech (first definition each)",
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        dest="all_details",
        help="show all definitions, examples, synonyms and phonetics",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def _verbosity(args: argparse.Namespace) -> int:
    if args.all_details:
        return VERBOSITY_ALL
    if args.verbose:
        return VERBOSITY_VERBOSE
    return VERBOSITY_DEFAULT


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    # Imported lazily so --help / --version don't pay the Textual import cost.
    from .app import show_entry, show_error

    try:
        raw = fetch_word(args.word)
        entry = Entry.parse(raw)
    except WordNotFound as exc:
        show_error(str(exc))
        return 1
    except LookupServiceError as exc:
        show_error(str(exc))
        return 2
    except ValueError:
        show_error(f"No definition found for {args.word!r}")
        return 1

    show_entry(entry, _verbosity(args))
    return 0


if __name__ == "__main__":
    sys.exit(main())
