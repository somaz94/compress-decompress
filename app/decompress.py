from __future__ import annotations

from datetime import datetime
import os
import shlex
from typing import TYPE_CHECKING
from ui import UI
import archive
from file_utils import FileUtils
from executor import CommandExecutor, ProcessResult
from config import DECOMPRESSION_COMMANDS, CommandConfig
from app_logger import logger
from base_processor import BaseProcessor
from exceptions import ValidationError, CompressError, CommandError
from stats import OperationStats

if TYPE_CHECKING:
    from config import AppConfig


class Decompressor(BaseProcessor):
    """
    Handles archive decompression operations

    Supports different formats (zip, tar, tgz, tbz2, txz, tzst) with
    custom destination paths.
    """
    def __init__(self, config: AppConfig):
        super().__init__(config)
        self.source = config.source
        self.format = config.format
        self.password = config.password
        self.verify_checksum = config.verify_checksum
        self.path_traversal_check = config.path_traversal_check
        self.stats = OperationStats(command="decompress", format=self.format)

    def validate(self) -> bool:
        """Validate source archive file exists"""
        self.source = self.source.strip()
        return self.validate_path(self.source, "Source file")

    def get_decompression_command(self) -> str:
        """Generate appropriate decompression command based on format"""
        self._validate_format()
        cmd_config = self._get_command_config()
        options = cmd_config.options(self.dest)
        password_flag = ""
        if self.password and self.format == "zip":
            password_flag = f"-P {shlex.quote(self.password)} "
        return f"{cmd_config.command} {password_flag}{cmd_config.format(self.source, options)}"

    def _validate_format(self) -> None:
        if self.format not in DECOMPRESSION_COMMANDS:
            raise ValueError(f"Unsupported format: {self.format}")

    def _get_command_config(self) -> CommandConfig:
        return DECOMPRESSION_COMMANDS[self.format]

    def verify_integrity(self) -> None:
        """
        Compare the archive against the expected SHA256, when one was given.

        Runs before extraction so a tampered or truncated download never
        reaches the filesystem.
        """
        if not self.verify_checksum:
            return
        actual = FileUtils.sha256_of_file(self.source)
        UI.print_section("Checksum Verification")
        UI.print_kv("Expected", self.verify_checksum)
        UI.print_kv("Actual", actual)
        if actual.lower() != self.verify_checksum.lower():
            raise ValidationError(
                "Checksum mismatch: archive does not match the expected SHA256 "
                f"(expected {self.verify_checksum}, got {actual})"
            )
        UI.print_success("Checksum verified")

    def inspect_entries(self) -> list[str] | None:
        """
        Read the member list and reject archives that would escape the
        destination directory ("zip slip").

        An archive the standard library cannot open is left to `tar`/`unzip` —
        inspection is a guard, not a second format gate.
        """
        entries = archive.list_entries(self.source, self.format)
        if entries is None:
            if self.path_traversal_check:
                logger.warning(
                    "Archive could not be inspected; skipping the path traversal check"
                )
            return None

        if not self.path_traversal_check:
            return entries

        escaping, absolute = archive.find_unsafe_entries(entries)
        if absolute:
            logger.warning(
                f"Archive contains {len(absolute)} absolute path(s); "
                f"the leading separator is stripped on extraction (e.g. '{absolute[0]}')"
            )
        if escaping:
            raise ValidationError(
                f"Unsafe archive: {len(escaping)} entry/entries would extract outside "
                f"the destination directory (e.g. '{escaping[0]}'). "
                "Set path_traversal_check: 'false' to extract anyway."
            )
        return entries

    def list_contents(self) -> None:
        """List decompressed contents"""
        if not os.path.exists(self.dest):
            return
        try:
            UI.print_section("Decompressed Contents")
            for item in os.listdir(self.dest):
                item_path = os.path.join(self.dest, item)
                if os.path.isfile(item_path):
                    UI.print_kv(item, FileUtils.get_size(item_path))
                elif os.path.isdir(item_path):
                    UI.print_bullet(f"{item}/ (directory)")
        except OSError as e:
            if self.verbose:
                logger.error(f"Failed to list contents: {str(e)}")
            UI.print_error(f"Failed to list contents: {str(e)}")

    def _record_stats(self, success: bool, start_time: datetime, source_size: int,
                      entries: list[str] | None) -> None:
        """Collect the metrics exposed as action outputs and the job summary"""
        self.stats.success = success
        self.stats.duration = (datetime.now() - start_time).total_seconds()
        self.stats.original_size = source_size
        self.stats.file_count = archive.count_files(entries)
        if success:
            self.stats.output_path = self.dest

    def decompress(self) -> ProcessResult:
        """Execute the decompression process"""
        try:
            UI.print_header("Decompression Process Started")
            if not self.validate():
                return ProcessResult(False, "Validation failed")

            source_size = os.path.getsize(self.source)
            start_time = datetime.now()

            self.source = FileUtils.adjust_path(self.source)
            self.verify_integrity()
            entries = self.inspect_entries()

            UI.print_section("Configuration")
            UI.print_kv("Source", self.source)
            UI.print_kv("Format", self.format)
            UI.print_kv("Destination", self.dest or "current directory")

            self.prepare_destination()

            command = self.get_decompression_command()
            result = CommandExecutor.run(command, self.verbose, self.fail_on_error)

            if result.success:
                duration = (datetime.now() - start_time).total_seconds()
                UI.print_section("Decompression Results")
                UI.print_kv("Original Archive Size", FileUtils.get_size(source_size))
                UI.print_kv("Duration", f"{duration:.2f} seconds")
                self.list_contents()

            self._record_stats(result.success, start_time, source_size, entries)
            return result

        except (OSError, ValueError, ValidationError, CompressError, CommandError) as e:
            return self.handle_error(e, "Decompression")


def decompress(config: AppConfig) -> OperationStats:
    """
    Main decompression function called from the action.

    Args:
        config: Application configuration

    Returns:
        Operation metrics. Falsy, with an empty `output_path`, on failure.
    """
    decompressor = Decompressor(config)
    decompressor.decompress()
    return decompressor.stats
