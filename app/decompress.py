from datetime import datetime
import os
import sys
from typing import Optional, Dict
from utils import (
    UI, FileUtils, CommandExecutor, 
    DECOMPRESSION_COMMANDS, logger, ProcessResult, BaseProcessor
)

class Decompressor(BaseProcessor):
    """Handles archive decompression"""
    def __init__(self, source: str, format: str):
        super().__init__()
        self.source = source
        self.format = format

    def validate(self) -> bool:
        """Validate source file exists"""
        return self.validate_path(self.source, "Source file")

    def get_decompression_command(self) -> str:
        """Generate appropriate decompression command based on format"""
        if self.format not in DECOMPRESSION_COMMANDS:
            raise ValueError(f"Unsupported format: {self.format}")

        cmd_config = DECOMPRESSION_COMMANDS[self.format]
        options = cmd_config.options(self.dest)
        return f"{cmd_config.command} {cmd_config.format(self.source, options)}"

    def list_contents(self) -> None:
        """List decompressed contents"""
        if not os.path.exists(self.dest):
            return

        try:
            UI.print_section("Decompressed Contents")
            for item in os.listdir(self.dest):
                item_path = os.path.join(self.dest, item)
                if os.path.isfile(item_path):
                    print(f"  • {item}: {FileUtils.get_size(item_path)}")
                elif os.path.isdir(item_path):
                    print(f"  • {item}/ (directory)")
        except Exception as e:
            if self.verbose:
                logger.logger.error(f"Failed to list contents: {str(e)}")
            UI.print_error(f"Failed to list contents: {str(e)}")

    def decompress(self) -> ProcessResult:
        """Execute decompression process"""
        try:
            UI.print_header("Decompression Process Started")
            if not self.validate():
                return ProcessResult(False, "Validation failed")

            source_size = os.path.getsize(self.source)
            start_time = datetime.now()
            
            self.source = FileUtils.adjust_path(self.source)
            self._print_configuration()
            self.prepare_destination()
            
            command = self.get_decompression_command()
            result = CommandExecutor.run(command, self.verbose)
            
            if result.success:
                self._print_results(start_time, source_size)
                self.list_contents()
            
            return result

        except Exception as e:
            return self.handle_error(e, "Decompression")

    def _print_configuration(self) -> None:
        """Print decompression configuration details"""
        UI.print_section("Configuration")
        print(f"  • Source: {self.source}")
        print(f"  • Format: {self.format}")
        print(f"  • Destination: {self.dest or 'current directory'}")

    def _print_results(self, start_time: datetime, source_size: int) -> None:
        """Print decompression results"""
        end_time = datetime.now()
        duration = end_time - start_time
        
        UI.print_section("Decompression Results")
        print(f"  • Original Archive Size: {FileUtils.get_size(source_size)}")
        print(f"  • Duration: {duration.total_seconds():.2f} seconds")

def decompress(source: str, format: str) -> bool:
    """Decompress an archive file"""
    decompressor = Decompressor(source, format)
    result = decompressor.decompress()
    return result.success
