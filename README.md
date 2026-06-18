# means

A small terminal dictionary. Run `means <word>` to see its meaning and an
example, rendered as a styled [Textual](https://textual.textualize.io/) card.
Definitions come from the free [dictionaryapi.dev](https://dictionaryapi.dev/)
service.

## Install

```bash
pip install -e .
```

## Usage

```bash
means beautiful          # word, part of speech, first definition + example
means beautiful -v       # every part of speech, first definition each
means beautiful --all    # all definitions, examples, synonyms, phonetics
```

Press `q`, `Enter`, or `Esc` to dismiss the card.

| Flag         | Shows                                                       |
|--------------|-------------------------------------------------------------|
| _(default)_  | word, part of speech, first definition, first example       |
| `-v`         | each part of speech with its first definition + example     |
| `-a`/`--all` | all definitions, all examples, synonyms, phonetics          |

If a word isn't found, or the dictionary service can't be reached, a friendly
card explains what happened.

## Development

```bash
pip install -e ".[dev]"
pytest
```
