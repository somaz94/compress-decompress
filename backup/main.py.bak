import os
import sys
from utils import print_header, print_section, print_error
from compress import compress
from decompress import decompress

def main():
    try:
        command = os.getenv("COMMAND")
        source = os.getenv("SOURCE")
        format = os.getenv("FORMAT")
        include_root = os.getenv("INCLUDEROOT", "true")

        print_header("Compress/Decompress Action")
        print_section("Environment Configuration")
        print(f"  • Command: {command}")
        print(f"  • Source: {source}")
        print(f"  • Format: {format}")
        print(f"  • Include Root: {include_root}")

        if not command:
            print_error("Command is required")
            sys.exit(1)
        if not source:
            print_error("Source is required")
            sys.exit(1)
        if not format:
            print_error("Format is required")
            sys.exit(1)

        if command == "compress":
            compress(source, format, include_root)
        elif command == "decompress":
            decompress(source, format)
        else:
            print_error(f"Invalid command: {command}")
            print("Supported commands: compress, decompress")
            sys.exit(1)

    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()