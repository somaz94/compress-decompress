import os
import sys
from datetime import datetime
from utils import (
    print_header, print_section, print_success, print_error,
    validate_format, run_command, adjust_path, get_file_size
)
from utils import logger

def decompress(source, format):
    try:
        print_header("Decompression Process Started")
        validate_format(format)
        
        if not os.path.exists(source):
            error_msg = f"Source file '{source}' does not exist"
            if os.getenv("FAIL_ON_ERROR", "true").lower() == "true":
                print_error(error_msg)
                sys.exit(1)
            else:
                logger.warning(error_msg)
                return False
        
        source_size = os.path.getsize(source)
        start_time = datetime.now()
        
        source = adjust_path(source)
        print_section("Configuration")
        print(f"  • Source: {source}")
        print(f"  • Format: {format}")
        print(f"  • Destination: {os.getenv('DEST', 'current directory')}")

        # Set destination path and create if it doesn't exist
        dest = os.getenv("DEST", os.getenv("GITHUB_WORKSPACE", os.getcwd()))
        if dest and not os.path.exists(dest):
            os.makedirs(dest)

        print(f"Attempting to decompress {source} to {dest if dest else 'current directory'}")

        # Define decompression commands for each format
        decompression_commands = {
            "zip": {
                "command": "unzip",
                "options": lambda d: f"-d {d}" if d else "-j -d .",
                "format": lambda src, opt: f"{opt} {src}"
            },
            "tar": {
                "command": "tar",
                "options": lambda d: f"-C {d}" if d else "-C .",
                "format": lambda src, opt: f"-xf {src} {opt}"
            },
            "tgz": {
                "command": "tar",
                "options": lambda d: f"-C {d}" if d else "-C .",
                "format": lambda src, opt: f"-xzf {src} {opt}"
            },
            "tbz2": {
                "command": "tar",
                "options": lambda d: f"-C {d}" if d else "-C .",
                "format": lambda src, opt: f"-xjf {src} {opt}"
            }
        }

        if format not in decompression_commands:
            sys.exit(f"Unsupported format: {format}")

        cmd_config = decompression_commands[format]
        options = cmd_config["options"](dest)
        command = f"{cmd_config['command']} {cmd_config['format'](source, options)}"
        
        if not run_command(command):
            if os.getenv("FAIL_ON_ERROR", "true").lower() == "true":
                sys.exit(1)
            return False
            
        print_success("Decompression completed successfully")
        print("\n" + "=" * 50)
        
        # Convert to relative path for output
        relative_dest = os.path.relpath(dest if dest else os.getcwd(), os.getcwd())
        print(
            f"file_path={relative_dest}",
            file=open(os.getenv("GITHUB_OUTPUT", "/dev/stdout"), "a"),
        )

        end_time = datetime.now()
        duration = end_time - start_time
        
        print_section("Decompression Results")
        print(f"  • Original Archive Size: {get_file_size(source_size)}")
        print(f"  • Duration: {duration.total_seconds():.2f} seconds")

        # Verify and display decompressed contents
        if os.path.exists(dest):
            try:
                files = os.listdir(dest)
                print_section("Decompressed Contents")
                for file in files:
                    file_path = os.path.join(dest, file)
                    if os.path.isfile(file_path):
                        print(f"  • {file}: {get_file_size(os.path.getsize(file_path))}")
                    elif os.path.isdir(file_path):
                        print(f"  • {file}/ (directory)")
            except Exception as e:
                if os.getenv("VERBOSE", "false").lower() == "true":
                    logger.error(f"Failed to list contents: {str(e)}")
                print_error(f"Failed to list contents: {str(e)}")

        return True

    except Exception as e:
        if os.getenv("FAIL_ON_ERROR", "true").lower() == "true":
            print_error(f"Decompression failed: {str(e)}")
            sys.exit(1)
        else:
            logger.warning(f"Decompression warning: {str(e)}")
            return False
