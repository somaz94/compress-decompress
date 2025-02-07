import os
import subprocess
import sys
import logging
from datetime import datetime

def print_header(title):
    print("\n" + "=" * 50)
    print(f"🚀 {title}")
    print("=" * 50 + "\n")

def print_section(title):
    print(f"\n📋 {title}:")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def get_file_size(file_path):
    """Return human readable file size"""
    size = os.path.getsize(file_path)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"

def validate_format(format):
    """Validate compression format"""
    valid_formats = ['zip', 'tar', 'tgz', 'tbz2']
    if format not in valid_formats:
        print_error(f"Invalid format: {format}")
        print(f"Supported formats: {', '.join(valid_formats)}")
        sys.exit(1)
    return True

def get_directory_size(path):
    """Calculate total size of a directory"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def run_command(command):
    print(f"⚙️  Executing: {command}")
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True, check=True)
        if result.stdout:
            logger.info(f"Command output:\n{result.stdout.strip()}")
        if result.stderr:
            logger.warning(f"Command stderr:\n{result.stderr.strip()}")
        print_success("Command executed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {e}")
        logger.error(f"Error output:\n{e.stderr}")
        sys.exit(1)


def get_extension(format):
    return {"zip": ".zip", "tar": ".tar", "tgz": ".tgz", "tbz2": ".tbz2"}.get(
        format, ""
    )


def adjust_path(path):
    adjusted_path = (
        path
        if os.path.isabs(path)
        else os.path.join(os.getenv("GITHUB_WORKSPACE", os.getcwd()), path)
    )
    print(f"Adjusted path: {adjusted_path}")
    return adjusted_path


def compress(source, format, include_root):
    print_header("Compression Process Started")
    validate_format(format)
    
    if not os.path.exists(source):
        print_error(f"Source path '{source}' does not exist")
        sys.exit(1)
    
    # Calculate source size
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
    print(f"Destination Path: {full_dest}")  # Debug: Show full destination path

    if os.path.isdir(source):
        # Compress a directory with the option of including root
        print(f"Attempting to compress directory {source} to {full_dest}")
        if include_root == "true":
            compress_target = base_name
            os.chdir(os.path.dirname(source))  # Change to directory of the source
        else:
            compress_target = "."
            os.chdir(
                source
            )  # Change to the source directory itself to compress its contents
        print(
            f"Changed CWD for Compression: {os.getcwd()}"
        )  # Debug: Show CWD for compression
    else:
        # Compress a file - include_root has no effect here
        print(f"Attempting to compress file {source} to {full_dest}")
        compress_target = base_name
        # os.chdir(os.path.dirname(source))  # Change to directory of the source

    if format == "zip":
        run_command(f"zip -r {full_dest} {compress_target}")
    elif format == "tar":
        run_command(f"tar --absolute-names -cvf {full_dest} {compress_target}")
    elif format == "tgz":
        run_command(f"tar -P -czvf {full_dest} {compress_target}")
    elif format == "tbz2":
        run_command(f"tar -P -cjvf {full_dest} {compress_target}")
    else:
        sys.exit(f"Unsupported format: {format}")
    os.chdir(cwd)  # Restore original working directory.
    print(f"Restored CWD: {os.getcwd()}")  # Debug: Show restored working directory
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

    print(
        f"Attempting to decompress {source} to {dest if dest else 'current directory'}"
    )

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


if __name__ == "__main__":
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
        print(f"  • GitHub Workspace: {os.getenv('GITHUB_WORKSPACE', 'Not in GitHub Actions')}")
        
        if command == "compress":
            compress(source, format, include_root)
        elif command == "decompress":
            decompress(source, format)
        else:
            print_error(f"Invalid command: {command}")
            sys.exit(1)
            
    except Exception as e:
        print_error(f"Unexpected error occurred: {str(e)}")
        logger.exception("Detailed error information:")
        sys.exit(1)
