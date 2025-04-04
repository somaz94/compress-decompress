import os
import sys
from typing import Optional, Dict, List
from utils import UI, CompressionFormat, logger
from compress import compress
from decompress import decompress

class ActionRunner:
    """Main action runner for compression/decompression operations"""
    def __init__(self):
        # Initialize configuration from environment variables
        self.command = os.getenv("COMMAND")
        self.source = os.getenv("SOURCE")
        self.format = os.getenv("FORMAT")
        self.include_root = os.getenv("INCLUDEROOT", "true")
        self.verbose = os.getenv("VERBOSE", "false").lower() == "true"
        self.fail_on_error = os.getenv("FAIL_ON_ERROR", "true").lower() == "true"
        # Custom destination and filename options
        self.dest = os.getenv("DEST", "")
        self.destfilename = os.getenv("DESTFILENAME", "")

    def validate_inputs(self) -> None:
        """Validate required inputs are provided and valid"""
        # Check for required command parameter
        if not self.command:
            UI.print_error("Command is required")
            sys.exit(1)
        # Check for required source parameter
        if not self.source:
            UI.print_error("Source is required")
            sys.exit(1)
        # Check for required format parameter
        if not self.format:
            UI.print_error("Format is required")
            sys.exit(1)
        # Validate compression format is supported
        if self.format not in CompressionFormat.list():
            UI.print_error(f"Invalid format: {self.format}")
            print(f"Supported formats: {', '.join(CompressionFormat.list())}")
            sys.exit(1)

    def print_configuration(self) -> None:
        """Print action configuration"""
        UI.print_header("Compress/Decompress Action")
        UI.print_section("Environment Configuration")
        # Display all configuration parameters
        print(f"  • Command: {self.command}")
        print(f"  • Source: {self.source}")
        print(f"  • Format: {self.format}")
        print(f"  • Include Root: {self.include_root}")
        print(f"  • Verbose: {self.verbose}")
        print(f"  • Fail on Error: {self.fail_on_error}")
        # Display optional destination parameters if set
        if self.dest:
            print(f"  • Destination: {self.dest}")
        if self.destfilename:
            print(f"  • Destination Filename: {self.destfilename}")

    def run(self) -> None:
        """Run the appropriate action based on command"""
        try:
            # Validate input parameters before proceeding
            self.validate_inputs()
            self.print_configuration()
            # Set logging verbosity based on configuration
            logger.set_verbose(self.verbose)

            # Execute the appropriate command
            if self.command == "compress":
                compress(self.source, self.format, self.include_root)
            elif self.command == "decompress":
                decompress(self.source, self.format)
            else:
                UI.print_error(f"Invalid command: {self.command}")
                print("Supported commands: compress, decompress")
                sys.exit(1)

        except Exception as e:
            UI.print_error(f"An error occurred: {str(e)}")
            sys.exit(1)

def main():
    """Main entry point"""
    # Create and run the action runner
    runner = ActionRunner()
    runner.run()

if __name__ == "__main__":
    main()