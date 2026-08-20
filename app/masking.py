"""
Secret masking shared by every component that prints a command or an error.

The zip/unzip password reaches the shell as `-P <password>`, so the command
string, the `CalledProcessError` repr, and the retry log line all carry it.
Registering the value once here keeps a secret out of the job log even when
the leak happens deep inside an exception message nobody formats by hand.
"""
from __future__ import annotations

from app_logger import logger

MASK = "***"
_MIN_MASKABLE_LENGTH = 3

_secrets: set[str] = set()


def register_secret(value: str) -> None:
    """
    Register a value to be masked from any text passed through `mask()`.

    Values shorter than `_MIN_MASKABLE_LENGTH` are refused: masking one or two
    characters would rewrite unrelated substrings across every command line.
    GitHub's own `::add-mask::` still covers the workflow log, so the warning
    is about the commands this action prints itself.
    """
    if not value:
        return
    if len(value) < _MIN_MASKABLE_LENGTH:
        logger.warning(
            f"Password is shorter than {_MIN_MASKABLE_LENGTH} characters; "
            "it cannot be masked in the commands this action prints"
        )
        return
    _secrets.add(value)


def clear_secrets() -> None:
    """Drop every registered secret (used by tests)."""
    _secrets.clear()


def mask(text: str) -> str:
    """Replace every registered secret in `text` with `***`."""
    if not text or not _secrets:
        return text
    for secret in _secrets:
        text = text.replace(secret, MASK)
    return text
