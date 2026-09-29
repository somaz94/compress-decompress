from __future__ import annotations


class CompressError(Exception):
    """Base exception for compress-decompress operations"""


class ValidationError(CompressError):
    """Raised when input validation fails"""


class CommandError(CompressError):
    """Raised when a shell command fails"""
