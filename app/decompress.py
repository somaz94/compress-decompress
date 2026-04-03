from __future__ import annotations

from datetime import datetime
import os
import shlex
from typing import TYPE_CHECKING
from ui import UI
from file_utils import FileUtils
from executor import CommandExecutor, ProcessResult
from config import DECOMPRESSION_COMMANDS, CommandConfig
from app_logger import logger
from base_processor import BaseProcessor
from exceptions import ValidationError, CompressError, CommandError

if TYPE_CHECKING:
    from config import AppConfig


class Decompressor(BaseProcessor):
    """
    Handles archive decompression operations

    Supports different formats (zip, tar, tgz, tbz2, txz) with
    custom destination paths.
    """
    def __init__(self, config: AppConfig):
        super().__init__(config)
        self.source = config.source
        self.format = config.format
        self.password = config.password

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

    def list_contents(self) -> None:
        """List decompressed contents"""
        if not os.path.exists(self.dest):
            return
        try:
            UI.print_section("Decompressed Contents")
            for item in os.listdir(self.dest):
                item_path = os.path.join(self.dest, item)
                if os.path.isfile(item_path):
                    print(f"  \u2022 {item}: {FileUtils.get_size(item_path)}")
                elif os.path.isdir(item_path):
                    print(f"  \u2022 {item}/ (directory)")
        except OSError as e:
            if self.verbose:
                logger.logger.error(f"Failed to list contents: {str(e)}")
            UI.print_error(f"Failed to list contents: {str(e)}")

    def decompress(self) -> ProcessResult:
        """Execute the decompression process"""
        try:
            UI.print_header("Decompression Process Started")
            if not self.validate():
                return ProcessResult(False, "Validation failed")

            source_size = os.path.getsize(self.source)
            start_time = datetime.now()

            self.source = FileUtils.adjust_path(self.source)

            UI.print_section("Configuration")
            print(f"  \u2022 Source: {self.source}")
            print(f"  \u2022 Format: {self.format}")
            print(f"  \u2022 Destination: {self.dest or 'current directory'}")

            self.prepare_destination()

            command = self.get_decompression_command()
            result = CommandExecutor.run(command, self.verbose, self.fail_on_error)

            if result.success:
                duration = (datetime.now() - start_time).total_seconds()
                UI.print_section("Decompression Results")
                print(f"  \u2022 Original Archive Size: {FileUtils.get_size(source_size)}")
                print(f"  \u2022 Duration: {duration:.2f} seconds")
                self.list_contents()

            return result

        except (OSError, ValueError, ValidationError, CompressError, CommandError) as e:
            return self.handle_error(e, "Decompression")


def decompress(config: AppConfig) -> str:
    """
    Main decompression function called from the action.

    Args:
        config: Application configuration

    Returns:
        Destination path if decompression succeeded, empty string otherwise
    """
    decompressor = Decompressor(config)
    result = decompressor.decompress()
    return decompressor.dest if result.success else ""
