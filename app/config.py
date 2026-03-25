import os
import shlex
from dataclasses import dataclass
from typing import List, Optional, Callable
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

    @classmethod
    def list(cls) -> List[str]:
        return [fmt.value for fmt in cls]

    @classmethod
    def get_extension(cls, format_str: str) -> str:
        return f".{format_str}" if format_str in cls.list() else ""


@dataclass
class CommandConfig:
    """Configuration for format-specific decompression commands"""
    command: str
    options: Callable[[Optional[str]], str]
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

    @classmethod
    def from_env(cls) -> 'AppConfig':
        compression_level = os.getenv("COMPRESSION_LEVEL", "")
        if compression_level and not cls._is_valid_compression_level(compression_level):
            raise ValidationError(
                f"Invalid compression_level: '{compression_level}'. Must be a number between 0 and 9."
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
        )

    @staticmethod
    def _is_valid_compression_level(level: str) -> bool:
        """Validate compression level is a single digit 0-9"""
        return len(level) == 1 and level.isdigit()

    @property
    def effective_dest(self) -> str:
        """Destination with fallback to GITHUB_WORKSPACE or cwd"""
        return self.dest or os.getenv("GITHUB_WORKSPACE", os.getcwd())
