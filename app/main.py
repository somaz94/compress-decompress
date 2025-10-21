import os
import sys
from typing import Optional, Dict, List
from utils import UI, CompressionFormat, logger, FileUtils
from compress import compress
from decompress import decompress

class ActionRunner:
    """
    Main action runner for compression/decompression operations
    
    This class handles the execution of compression and decompression operations
    based on environment variables provided by the GitHub Action.
    """
    def __init__(self):
        """
        Initialize configuration from environment variables
        
        Loads and stores all settings from environment variables that control
        the behavior of compression/decompression operations.
        """
        # Command and source settings
        self.command = os.getenv("COMMAND")
        self.source = os.getenv("SOURCE")
        self.format = os.getenv("FORMAT")
        
        # Behavior settings
        self.include_root = os.getenv("INCLUDEROOT", "true")
        self.preserve_glob_structure = os.getenv("PRESERVE_GLOB_STRUCTURE", "false")
        self.strip_prefix = os.getenv("STRIP_PREFIX", "")
        self.verbose = FileUtils.str_to_bool(os.getenv("VERBOSE", "false"))
        self.fail_on_error = FileUtils.str_to_bool(os.getenv("FAIL_ON_ERROR", "true"))
        
        # Destination settings
        self.dest = os.getenv("DEST", "")
        self.destfilename = os.getenv("DESTFILENAME", "")
        self.exclude = os.getenv("EXCLUDE", "")

    def validate_inputs(self) -> None:
        """
        Validate required inputs are provided and valid
        
        Checks that all required parameters are present and valid before
        proceeding with the operation. Exits with error code if validation fails.
        """
        # Validate command parameter
        if not self.command:
            UI.print_error("Command is required")
            sys.exit(1)
            
        # Validate source parameter
        if not self.source:
            UI.print_error("Source is required")
            sys.exit(1)
            
        # Validate format parameter
        if not self.format:
            UI.print_error("Format is required")
            sys.exit(1)
            
        # Validate compression format is supported
        if self.format not in CompressionFormat.list():
            UI.print_error(f"Invalid format: {self.format}")
            print(f"Supported formats: {', '.join(CompressionFormat.list())}")
            sys.exit(1)

    def print_configuration(self) -> None:
        """
        Print action configuration
        
        Displays all configuration parameters to provide visibility into
        the current operation settings.
        """
        UI.print_header("Compress/Decompress Action")
        UI.print_section("Environment Configuration")
        
        # Print required parameters
        print(f"  • Command: {self.command}")
        print(f"  • Source: {self.source}")
        print(f"  • Format: {self.format}")
        
        # Print behavior settings
        print(f"  • Include Root: {self.include_root}")
        print(f"  • Preserve Glob Structure: {self.preserve_glob_structure}")
        if self.strip_prefix:
            print(f"  • Strip Prefix: {self.strip_prefix}")
        print(f"  • Verbose: {self.verbose}")
        print(f"  • Fail on Error: {self.fail_on_error}")
        
        # Print optional parameters if provided
        if self.dest:
            print(f"  • Destination: {self.dest}")
        if self.destfilename:
            print(f"  • Destination Filename: {self.destfilename}")
        if self.exclude:
            print(f"  • Exclude Pattern: {self.exclude}")

    def execute_command(self) -> None:
        """
        Execute the appropriate compression or decompression command
        
        Dispatches to the correct handler based on the command parameter.
        Raises an error for unsupported commands.
        """
        if self.command == "compress":
            compress(self.source, self.format, self.include_root, self.preserve_glob_structure, self.strip_prefix)
        elif self.command == "decompress":
            decompress(self.source, self.format)
        else:
            UI.print_error(f"Invalid command: {self.command}")
            print("Supported commands: compress, decompress")
            sys.exit(1)

    def run(self) -> None:
        """
        Run the appropriate action based on command
        
        Main execution flow that validates inputs, displays configuration,
        sets up logging, and executes the requested command.
        """
        try:
            # Validate and prepare for execution
            self.validate_inputs()
            self.print_configuration()
            
            # Configure logging based on verbosity setting
            logger.set_verbose(self.verbose)

            # Execute the command
            self.execute_command()
            
        except Exception as e:
            UI.print_error(f"An error occurred: {str(e)}")
            sys.exit(1)


def main():
    """
    Main entry point for the application
    
    Creates and runs the ActionRunner to handle compression/decompression operations.
    """
    runner = ActionRunner()
    runner.run()


if __name__ == "__main__":
    main()