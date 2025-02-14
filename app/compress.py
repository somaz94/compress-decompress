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
    
    # 압축 파일 경로 설정
    if include_root == "true":
        full_dest = os.path.join(dest, f"{base_name}{extension}")
    else:
        full_dest = os.path.join(source, f"{base_name}{extension}")
    
    print(f"Destination Path: {full_dest}")

    # 압축 명령어 설정
    if format == "zip":
        if include_root == "true":
            command = f"cd {os.path.dirname(source)} && zip -r {full_dest} {base_name}"
        else:
            command = f"cd {source} && zip -r {full_dest} ."
    elif format == "tar":
        if include_root == "true":
            command = f"tar -cf {full_dest} -C {os.path.dirname(source)} {base_name}"
        else:
            command = f"tar -cf {full_dest} -C {source} ."
    else:  # tgz, tbz2
        tar_options = {
            "tgz": "z",
            "tbz2": "j"
        }
        temp_tar = os.path.join(os.path.dirname(full_dest), f"temp_{base_name}.tar")
        if include_root == "true":
            command = f"tar -cf {temp_tar} -C {os.path.dirname(source)} {base_name} && tar -c{tar_options[format]}f {full_dest} -C {os.path.dirname(temp_tar)} {os.path.basename(temp_tar)} && rm {temp_tar}"
        else:
            command = f"tar -cf {temp_tar} -C {source} . && tar -c{tar_options[format]}f {full_dest} -C {os.path.dirname(temp_tar)} {os.path.basename(temp_tar)} && rm {temp_tar}"

    print(f"⚙️  Executing: {command}")
    run_command(command)
        
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
