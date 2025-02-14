import os
import sys
from datetime import datetime
from utils import (
    print_header, print_section, print_success, print_error,
    validate_format, get_directory_size, run_command,
    get_extension, adjust_path, get_file_size
)


def compress(source, format, include_root):
    print_header("Compression Process Started")
    validate_format(format)
    
    if not os.path.exists(source):
        print_error(f"Source path '{source}' does not exist")
        sys.exit(1)
    
    source_size = get_directory_size(source) if os.path.isdir(source) else os.path.getsize(source)
    start_time = datetime.now()
    
    source = adjust_path(source)
    print_section("Configuration")
    print(f"  • Source: {source}")
    print(f"  • Format: {format}")
    print(f"  • Include Root: {include_root}")
    print(f"  • Source Size: {get_file_size(source_size)}")
    
    cwd = os.getcwd()
    print(f"  • Initial Directory: {cwd}")

    dest = os.getenv("DEST", os.getenv("GITHUB_WORKSPACE", os.getcwd()))
    if dest and not os.path.exists(dest):
        os.makedirs(dest)

    base_name = os.path.basename(source)
    extension = get_extension(format)
    full_dest = os.path.join(dest, f"{base_name}{extension}")
    print(f"Destination Path: {full_dest}")

    compression_commands = {
        "zip": {
            "true": f"zip -r {full_dest} {base_name}",
            "false": f"cd {source} && zip -r {full_dest} ."
        },
        "tar": {
            "true": f"tar -cf {full_dest} {base_name}",
            "false": f"tar -C {source} -cf {full_dest} ."
        },
        "tgz": {
            "true": f"tar -czf {full_dest} {base_name}",
            "false": f"tar -C {source} -czf {full_dest} ."
        },
        "tbz2": {
            "true": f"tar -cjf {full_dest} {base_name}",
            "false": f"tar -C {source} -cjf {full_dest} ."
        }
    }

    if format not in compression_commands:
        sys.exit(f"Unsupported format: {format}")

    if include_root == "true":
        os.chdir(os.path.dirname(source))
    else:
        os.chdir(source)
    print(f"Changed CWD for Compression: {os.getcwd()}")

    command = compression_commands[format][include_root]
    run_command(command)
        
    os.chdir(cwd)
    print(f"Restored CWD: {os.getcwd()}")
    print_success(f"Compression completed: {full_dest}")
    print("\n" + "=" * 50)
    print(
        f"file_path={full_dest}",
        file=open(os.getenv("GITHUB_OUTPUT", "/dev/stdout"), "a"),
    )

    end_time = datetime.now()
    duration = end_time - start_time
    
    if os.path.exists(full_dest):
        compressed_size = os.path.getsize(full_dest)
        compression_ratio = (1 - (compressed_size / source_size)) * 100 if source_size > 0 else 0
        
        print_section("Compression Results")
        print(f"  • Original Size: {get_file_size(source_size)}")
        print(f"  • Compressed Size: {get_file_size(compressed_size)}")
        print(f"  • Compression Ratio: {compression_ratio:.1f}%")
        print(f"  • Duration: {duration.total_seconds():.2f} seconds")
