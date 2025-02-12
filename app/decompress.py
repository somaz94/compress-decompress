import os
from datetime import datetime
from .utils import (
    print_header, print_section, print_success, print_error,
    validate_format, run_command, adjust_path, get_file_size
)
import sys

def decompress(source, format):
    print_header("Decompression Process Started")
    validate_format(format)
    
    if not os.path.exists(source):
        print_error(f"Source file '{source}' does not exist")
        sys.exit(1)
    
    source_size = os.path.getsize(source)
    start_time = datetime.now()
    
    source = adjust_path(source)
    print_section("Configuration")
    print(f"  • Source: {source}")
    print(f"  • Format: {format}")
    print(f"  • Destination: {os.getenv('DEST', 'current directory')}")

    dest = os.getenv("DEST", os.getenv("GITHUB_WORKSPACE", os.getcwd()))
    if dest and not os.path.exists(dest):
        os.makedirs(dest)

    print(f"Attempting to decompress {source} to {dest if dest else 'current directory'}")

    if format == "zip":
        unzip_options = f"-d {dest}" if dest else "-j -d ."
        run_command(f"unzip {unzip_options} {source}")
    elif format == "tar":
        tar_options = f"-C {dest}" if dest else "-C ."
        run_command(f"tar --absolute-names -xvf {source} {tar_options}")
    elif format == "tgz":
        tar_options = f"-C {dest}" if dest else "-C ."
        run_command(f"tar -P -xzvf {source} {tar_options}")
    elif format == "tbz2":
        tar_options = f"-C {dest}" if dest else "-C ."
        run_command(f"tar -P -xjvf {source} {tar_options}")
    else:
        sys.exit(f"Unsupported format: {format}")
        
    print_success("Decompression completed successfully")
    print("\n" + "=" * 50)
    print(
        f"file_path={dest if dest else 'current directory'}",
        file=open(os.getenv("GITHUB_OUTPUT", "/dev/stdout"), "a"),
    )

    end_time = datetime.now()
    duration = end_time - start_time
    
    print_section("Decompression Results")
    print(f"  • Original Archive Size: {get_file_size(source_size)}")
    print(f"  • Duration: {duration.total_seconds():.2f} seconds")
