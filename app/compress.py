import os
import sys
import shutil
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
        work_dir = os.path.dirname(source)
        target = base_name
    else:
        full_dest = os.path.join(dest, f"{base_name}{extension}")
        work_dir = source
        target = "."

    print(f"Destination Path: {full_dest}")
    
    # 임시 디렉토리 생성
    temp_dir = os.path.join(dest, f"temp_{base_name}_{format}")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    try:
        # 파일 복사
        if include_root == "true":
            shutil.copytree(source, os.path.join(temp_dir, base_name))
        else:
            for item in os.listdir(source):
                src_path = os.path.join(source, item)
                dst_path = os.path.join(temp_dir, item)
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dst_path)
                else:
                    shutil.copy2(src_path, dst_path)

        # 압축 명령어 실행
        os.chdir(temp_dir)
        if format == "zip":
            run_command(f"zip -r {full_dest} {target}")
        elif format == "tar":
            run_command(f"tar -cf {full_dest} {target}")
        elif format == "tgz":
            run_command(f"tar -czf {full_dest} {target}")
        elif format == "tbz2":
            run_command(f"tar -cjf {full_dest} {target}")
        
        os.chdir(cwd)
        print_success(f"Compression completed: {full_dest}")
        
    finally:
        # 임시 디렉토리 정리
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
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
