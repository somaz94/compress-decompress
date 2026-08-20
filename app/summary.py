"""
GitHub Actions job summary rendering.

Everything the action already prints to the log is written once more as a
Markdown table to `$GITHUB_STEP_SUMMARY`, which GitHub renders on the run
page — so the archive size, ratio, and checksum are visible without opening
the step log. Outside Actions the variable is unset and nothing is written.
"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING

from app_logger import logger
from file_utils import FileUtils

if TYPE_CHECKING:
    from stats import OperationStats

_SUMMARY_ENV = "GITHUB_STEP_SUMMARY"


def _rows_for_compress(stats: OperationStats) -> list[tuple[str, str]]:
    rows = [
        ("Archive", f"`{stats.output_path}`"),
        ("Format", f"`{stats.format}`"),
        ("Original size", FileUtils.get_size(stats.original_size)),
        ("Compressed size", FileUtils.get_size(stats.compressed_size)),
        ("Compression ratio", f"{stats.compression_ratio:.1f}%"),
    ]
    if stats.file_count:
        rows.append(("Files", str(stats.file_count)))
    rows.append(("Duration", f"{stats.duration:.2f}s"))
    if stats.checksum:
        rows.append(("SHA256", f"`{stats.checksum}`"))
    return rows


def _rows_for_decompress(stats: OperationStats) -> list[tuple[str, str]]:
    rows = [
        ("Archive size", FileUtils.get_size(stats.original_size)),
        ("Format", f"`{stats.format}`"),
        ("Extracted to", f"`{stats.output_path}`"),
    ]
    if stats.file_count:
        rows.append(("Files", str(stats.file_count)))
    rows.append(("Duration", f"{stats.duration:.2f}s"))
    return rows


def render(stats: OperationStats) -> str:
    """Render the run as a GitHub-flavored Markdown section."""
    title = "Compress" if stats.command == "compress" else "Decompress"
    icon = "✅" if stats.success else "❌"
    rows = (_rows_for_compress(stats) if stats.command == "compress"
            else _rows_for_decompress(stats))

    lines = [
        f"### {icon} {title} — `{stats.format}`",
        "",
        "| | |",
        "| --- | --- |",
    ]
    lines.extend(f"| **{key}** | {value} |" for key, value in rows)
    lines.append("")
    return "\n".join(lines)


def write(stats: OperationStats, enabled: bool = True) -> bool:
    """
    Append the rendered summary to `$GITHUB_STEP_SUMMARY`.

    Returns whether anything was written. A failure to write is never fatal —
    the summary is a reporting nicety, not part of the archive contract.
    """
    if not enabled:
        return False
    summary_path = os.getenv(_SUMMARY_ENV)
    if not summary_path:
        return False
    try:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(render(stats) + "\n")
        return True
    except OSError as e:
        logger.warning(f"Failed to write job summary: {e}")
        return False
