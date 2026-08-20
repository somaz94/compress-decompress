from __future__ import annotations

import os
import shlex
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from exceptions import ValidationError
from file_utils import FileUtils


class CompressionFormat(Enum):
    """Supported compression formats"""
    ZIP = 'zip'
    TAR = 'tar'
    TGZ = 'tgz'
    TBZ2 = 'tbz2'
    TXZ = 'txz'
    TZST = 'tzst'

    @classmethod
    def list(cls) -> list[str]:
        return [fmt.value for fmt in cls]

    @classmethod
    def get_extension(cls, format_str: str) -> str:
        return f".{format_str}" if format_str in cls.list() else ""


@dataclass
class CommandConfig:
    """Configuration for format-specific decompression commands"""
    command: str
    options: Callable[[str | None], str]
    format: Callable[[str, str], str]


DECOMPRESSION_COMMANDS = {
    CompressionFormat.ZIP.value: CommandConfig(
        "unzip",
        lambda d: f"-d {shlex.quote(d)}" if d else "-j -d .",
        lambda src, opt: f"{opt} {shlex.quote(src)}"
    ),
    CompressionFormat.TAR.value: CommandConfig(
        "tar",
        lambda d: f"-C {shlex.quote(d)}" if d else "-C .",
        lambda src, opt: f"-xf {shlex.quote(src)} {opt}"
    ),
    CompressionFormat.TGZ.value: CommandConfig(
        "tar",
        lambda d: f"-C {shlex.quote(d)}" if d else "-C .",
        lambda src, opt: f"-xzf {shlex.quote(src)} {opt}"
    ),
    CompressionFormat.TBZ2.value: CommandConfig(
        "tar",
        lambda d: f"-C {shlex.quote(d)}" if d else "-C .",
        lambda src, opt: f"-xjf {shlex.quote(src)} {opt}"
    ),
    CompressionFormat.TXZ.value: CommandConfig(
        "tar",
        lambda d: f"-C {shlex.quote(d)}" if d else "-C .",
        lambda src, opt: f"-xJf {shlex.quote(src)} {opt}"
    ),
    CompressionFormat.TZST.value: CommandConfig(
        "tar",
        lambda d: f"-C {shlex.quote(d)}" if d else "-C .",
        lambda src, opt: f"--zstd -xf {shlex.quote(src)} {opt}"
    )
}


@dataclass
class AppConfig:
    """Centralized application configuration from environment variables"""
    command: str = ""
    source: str = ""
    format: str = ""
    include_root: str = "true"
    preserve_glob_structure: str = "false"
    strip_prefix: str = ""
    verbose: bool = False
    fail_on_error: bool = True
    dest: str = ""
    destfilename: str = ""
    exclude: str = ""
    compression_level: str = ""
    password: str = ""
    verify_checksum: str = ""
    path_traversal_check: bool = True
    step_summary: bool = True

    @classmethod
    def from_env(cls) -> 'AppConfig':
        compression_level = os.getenv("COMPRESSION_LEVEL", "")
        if compression_level and not cls._is_valid_compression_level(compression_level):
            raise ValidationError(
                f"Invalid compression_level: '{compression_level}'. Must be a number between 0 and 9."
            )
        verify_checksum = os.getenv("VERIFY_CHECKSUM", "").strip()
        if verify_checksum and not cls._is_valid_sha256(verify_checksum):
            raise ValidationError(
                f"Invalid verify_checksum: '{verify_checksum}'. "
                "Must be a 64-character hexadecimal SHA256 digest."
            )
        return cls(
            command=os.getenv("COMMAND", ""),
            source=os.getenv("SOURCE", ""),
            format=os.getenv("FORMAT", ""),
            include_root=os.getenv("INCLUDEROOT", "true"),
            preserve_glob_structure=os.getenv("PRESERVE_GLOB_STRUCTURE", "false"),
            strip_prefix=os.getenv("STRIP_PREFIX", ""),
            verbose=FileUtils.str_to_bool(os.getenv("VERBOSE", "false")),
            fail_on_error=FileUtils.str_to_bool(os.getenv("FAIL_ON_ERROR", "true")),
            dest=os.getenv("DEST", ""),
            destfilename=os.getenv("DESTFILENAME", ""),
            exclude=os.getenv("EXCLUDE", ""),
            compression_level=compression_level,
            password=os.getenv("PASSWORD", ""),
            verify_checksum=verify_checksum.lower(),
            path_traversal_check=FileUtils.str_to_bool(
                os.getenv("PATH_TRAVERSAL_CHECK", "true"), default=True
            ),
            step_summary=FileUtils.str_to_bool(
                os.getenv("STEP_SUMMARY", "true"), default=True
            ),
        )

    @staticmethod
    def _is_valid_compression_level(level: str) -> bool:
        """Validate compression level is a single digit 0-9"""
        return len(level) == 1 and level.isdigit()

    @staticmethod
    def _is_valid_sha256(digest: str) -> bool:
        """Validate a string is a 64-character hexadecimal SHA256 digest"""
        return len(digest) == 64 and all(c in "0123456789abcdefABCDEF" for c in digest)

    @property
    def effective_dest(self) -> str:
        """Destination with fallback to GITHUB_WORKSPACE or cwd"""
        return self.dest or os.getenv("GITHUB_WORKSPACE", os.getcwd())
