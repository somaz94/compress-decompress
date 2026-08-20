"""
Read-only archive inspection.

Used before extraction for two things the shell tools do not report back:
the entry count that becomes the `file_count` output, and path-traversal
entries ("zip slip") that would write outside the destination directory.

Inspection is best-effort — an archive the standard library cannot open
(an unsupported codec, a format built by another tool) yields `None` rather
than an error, so a readable archive is never rejected for being unreadable
*here* while the real `tar`/`unzip` handles it fine.
"""
from __future__ import annotations

import tarfile
import zipfile

from app_logger import logger
from config import CompressionFormat

# Entries whose extracted path would escape the destination directory.
_PARENT = ".."
_CURRENT = "."


def list_entries(archive_path: str, archive_format: str) -> list[str] | None:
    """
    Return the member names of an archive, or None when it cannot be read.

    Encrypted zips still list — only the entry *data* is encrypted, so the
    password is not needed to inspect names.
    """
    try:
        if archive_format == CompressionFormat.ZIP.value:
            with zipfile.ZipFile(archive_path) as zf:
                return zf.namelist()
        # Transparent mode auto-detects gzip/bzip2/xz, and zstd on Python 3.14+.
        with tarfile.open(archive_path, "r") as tf:
            # tar stores a directory member without a trailing slash, zip with
            # one. Normalize to the zip form so `count_files` needs one rule.
            return [f"{m.name}/" if m.isdir() else m.name for m in tf.getmembers()]
    except (OSError, ValueError, tarfile.TarError, zipfile.BadZipFile) as e:
        logger.debug(f"Could not inspect archive '{archive_path}': {e}")
        return None


def count_files(entries: list[str] | None) -> int:
    """Count file members, ignoring directory entries."""
    if not entries:
        return 0
    return sum(1 for name in entries if not name.endswith("/"))


def escapes_destination(name: str) -> bool:
    """
    True when extracting `name` would land outside the destination directory.

    Only `..` traversal counts. A leading `/` is stripped by both `tar` and
    `unzip`, so an absolute member is surprising but not an escape — it is
    reported separately as a warning.
    """
    normalized = name.replace("\\", "/")
    depth = 0
    for part in normalized.split("/"):
        if part in ("", _CURRENT):
            continue
        if part == _PARENT:
            depth -= 1
            if depth < 0:
                return True
        else:
            depth += 1
    return False


def is_absolute(name: str) -> bool:
    """True for members stored with an absolute path or a Windows drive letter."""
    normalized = name.replace("\\", "/")
    return normalized.startswith("/") or (len(normalized) > 1 and normalized[1] == ":")


def find_unsafe_entries(entries: list[str]) -> tuple[list[str], list[str]]:
    """Split entries into (traversal escapes, absolute paths)."""
    escaping = [name for name in entries if escapes_destination(name)]
    absolute = [name for name in entries if is_absolute(name)]
    return escaping, absolute
