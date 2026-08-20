"""Metrics for a single compress/decompress run, surfaced as action outputs."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class OperationStats:
    """
    Result of one operation.

    Truthiness follows `success`, so callers can keep writing
    `if result:` the way they did with the old boolean-ish return value.
    """
    command: str = ""
    format: str = ""
    success: bool = False
    output_path: str = ""
    checksum: str = ""
    original_size: int = 0
    compressed_size: int = 0
    file_count: int = 0
    duration: float = 0.0

    def __bool__(self) -> bool:
        return self.success

    @property
    def compression_ratio(self) -> float:
        """
        Percentage of the original size saved by compression.

        Negative for incompressible input that grew, 0.0 when either size is
        unknown or the operation was a decompression.
        """
        if self.original_size <= 0 or self.compressed_size <= 0:
            return 0.0
        return (1 - (self.compressed_size / self.original_size)) * 100
