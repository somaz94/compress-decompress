from __future__ import annotations

class CompressError(Exception):
    """Base exception for compress-decompress operations"""
    pass

class ValidationError(CompressError):
    """Raised when input validation fails"""
    pass

class CommandError(CompressError):
    """Raised when a shell command fails"""
    pass
