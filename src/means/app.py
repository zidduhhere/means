"""Textual UI: render a dictionary entry (or an error) as a styled card.

Verbosity levels drive how much of the entry is shown:
    0 (default) - first part of speech, first definition + example
    1 (-v)      - every part of speech, first definition + example each
    2 (-a/--all)- every definition, all examples, synonyms, phonetics
"""

from __future__ import annotations

from rich.console import Group
from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Center, Middle, VerticalScroll
from textual.widgets import Static

from .models import (
    VERBOSITY_ALL,
    VERBOSITY_VERBOSE,
    Entry,
)


def render_entry(entry: Entry, verbosity: int) -> Group:
    """Build a Rich renderable for an entry at the given verbosity."""
    parts: list = []

    title = Text(entry.word, style="bold cyan")
    if verbosity >= VERBOSITY_ALL and entry.phonetic:
        title.append(f"  {entry.phonetic}", style="dim italic")
    parts.append(title)
    parts.append(Text())

    meanings = entry.meanings if verbosity >= VERBOSITY_VERBOSE else entry.meanings[:1]
    for meaning in meanings:
        if not meaning.definitions:
            continue
        parts.append(Text(meaning.part_of_speech, style="italic yellow"))

        defs = (
            meaning.definitions
            if verbosity >= VERBOSITY_ALL
            else meaning.definitions[:1]
        )
        for i, definition in enumerate(defs, start=1):
            number = f"{i}. " if verbosity >= VERBOSITY_ALL else "• "
            parts.append(Text(f"{number}{definition.text}"))
            if definition.example:
                example = Text("   ")
                example.append(f'"{definition.example}"', style="green italic")
                parts.append(example)
            if verbosity >= VERBOSITY_ALL and definition.synonyms:
                syn = Text("   synonyms: ", style="dim")
                syn.append(", ".join(definition.synonyms), style="dim magenta")
                parts.append(syn)
        parts.append(Text())

    return Group(*parts)


def render_error(message: str) -> Group:
    return Group(Text(message, style="bold red"))


class MeansApp(App):
    """One-shot card app. Renders content, dismisses on any key."""

    CSS = """
    Screen {
        align: center middle;
    }
    #card {
        border: round cyan;
        padding: 1 2;
        width: auto;
        max-width: 80%;
        height: auto;
        max-height: 90%;
    }
    .error #card {
        border: round red;
    }
    """

    BINDINGS = [
        ("q", "dismiss", "Quit"),
        ("escape", "dismiss", "Quit"),
        ("enter", "dismiss", "Quit"),
        ("space", "dismiss", "Quit"),
    ]

    def __init__(self, renderable: Group, *, is_error: bool = False):
        super().__init__()
        self._renderable = renderable
        self._is_error = is_error

    def compose(self) -> ComposeResult:
        with Middle():
            with Center():
                yield VerticalScroll(Static(self._renderable, id="card"))

    def on_mount(self) -> None:
        if self._is_error:
            self.add_class("error")

    def action_dismiss(self) -> None:
        self.exit()


def show_entry(entry: Entry, verbosity: int) -> None:
    MeansApp(render_entry(entry, verbosity)).run()


def show_error(message: str) -> None:
    MeansApp(render_error(message), is_error=True).run()
