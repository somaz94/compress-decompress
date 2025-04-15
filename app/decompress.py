from datetime import datetime
import os
import sys
from typing import Optional, Dict, List
from utils import (
    UI, FileUtils, CommandExecutor, 
    DECOMPRESSION_COMMANDS, logger, ProcessResult, BaseProcessor
)

class Decompressor(BaseProcessor):
    """
    Handles archive decompression operations
    
    This class provides functionality to decompress archives using
    different formats (zip, tar, tgz, tbz2) with support for
    custom destination paths.
    """
    def __init__(self, source: str, format: str):
        """
        Initialize Decompressor with required parameters
        
        Args:
            source: Source archive file to decompress
            format: Archive format (zip, tar, tgz, tbz2)
        """
        super().__init__()
        self.source = source
        self.format = format

    def validate(self) -> bool:
        """
        Validate source archive file exists
        
        Returns:
            True if source file is valid, False otherwise
        """
        # Strip leading/trailing whitespace from file path
        self.source = self.source.strip()
        return self.validate_path(self.source, "Source file")

    def get_decompression_command(self) -> str:
        """
        Generate appropriate decompression command based on format
        
        Uses format-specific command configurations from DECOMPRESSION_COMMANDS.
        Each format has its own command structure and options.
        
        Returns:
            Shell command string to execute decompression
            
        Raises:
            ValueError: If the specified format is not supported
        """
        self._validate_format()
        cmd_config = self._get_command_config()
        options = cmd_config.options(self.dest)
        return f"{cmd_config.command} {cmd_config.format(self.source, options)}"
    
    def _validate_format(self) -> None:
        """
        Verify the requested format is supported
        
        Raises:
            ValueError: If the format is not in DECOMPRESSION_COMMANDS
        """
        if self.format not in DECOMPRESSION_COMMANDS:
            raise ValueError(f"Unsupported format: {self.format}")
            
    def _get_command_config(self) -> object:
        """
        Get the command configuration for the specified format
        
        Returns:
            CommandConfig object with format-specific settings
        """
        return DECOMPRESSION_COMMANDS[self.format]

    def list_contents(self) -> None:
        """
        List decompressed contents
        
        Displays a structured view of extracted files and directories,
        including file sizes for regular files.
        """
        if not os.path.exists(self.dest):
            return

        try:
            UI.print_section("Decompressed Contents")
            self._display_extracted_contents()
        except Exception as e:
            self._handle_listing_error(e)

    def _display_extracted_contents(self) -> None:
        """
        Display extracted files and directories with details
        """
        for item in os.listdir(self.dest):
            item_path = os.path.join(self.dest, item)
            if os.path.isfile(item_path):
                # Show file size for regular files
                print(f"  • {item}: {FileUtils.get_size(item_path)}")
            elif os.path.isdir(item_path):
                # Mark directories with a trailing slash
                print(f"  • {item}/ (directory)")
                
    def _handle_listing_error(self, error: Exception) -> None:
        """
        Handle errors that occur when listing decompressed contents
        
        Args:
            error: Exception that occurred during listing
        """
        if self.verbose:
            logger.logger.error(f"Failed to list contents: {str(error)}")
        UI.print_error(f"Failed to list contents: {str(error)}")

    def decompress(self) -> ProcessResult:
        """
        Execute the decompression process
        
        This is the main method that orchestrates the entire decompression process:
        1. Validates the source archive
        2. Prepares the environment and configuration
        3. Executes the decompression command
        4. Handles results and displays extracted contents
        
        Returns:
            ProcessResult object with success status and message
        """
        try:
            UI.print_header("Decompression Process Started")
            if not self.validate():
                return ProcessResult(False, "Validation failed")

            return self._perform_decompression()

        except Exception as e:
            return self.handle_error(e, "Decompression")

    def _perform_decompression(self) -> ProcessResult:
        """
        Perform the actual decompression operation
        
        Returns:
            ProcessResult object with operation status
        """
        # Get size of the source archive
        source_size = os.path.getsize(self.source)
        start_time = datetime.now()
        
        # Set up for decompression
        self.source = FileUtils.adjust_path(self.source)
        self._print_configuration()
        self.prepare_destination()
        
        # Execute decompression
        command = self.get_decompression_command()
        result = CommandExecutor.run(command, self.verbose)
        
        # Handle results
        if result.success:
            self._print_results(start_time, source_size)
            self.list_contents()
        
        return result

    def _print_configuration(self) -> None:
        """
        Print decompression configuration details
        
        Displays all relevant settings to the user.
        """
        UI.print_section("Configuration")
        print(f"  • Source: {self.source}")
        print(f"  • Format: {self.format}")
        print(f"  • Destination: {self.dest or 'current directory'}")

    def _print_results(self, start_time: datetime, source_size: int) -> None:
        """
        Print decompression results
        
        Shows statistics about the decompression operation.
        
        Args:
            start_time: Time when decompression started
            source_size: Size in bytes of the source archive
        """
        end_time = datetime.now()
        duration = end_time - start_time
        
        UI.print_section("Decompression Results")
        print(f"  • Original Archive Size: {FileUtils.get_size(source_size)}")
        print(f"  • Duration: {duration.total_seconds():.2f} seconds")

def decompress(source: str, format: str) -> bool:
    """
    Main decompression function that's called from the action
    
    Creates a Decompressor instance and executes the decompression.
    
    Args:
        source: Source archive file to decompress
        format: Archive format (zip, tar, tgz, tbz2)
        
    Returns:
        True if decompression succeeded, False otherwise
    """
    decompressor = Decompressor(source, format)
    result = decompressor.decompress()
    return result.success
