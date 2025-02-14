import os
import subprocess
import logging
import sys

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

def get_file_size(size_or_path):
    """Return human readable file size"""
    try:
        if isinstance(size_or_path, str):
            size = os.path.getsize(size_or_path)
        else:
            size = size_or_path

        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"
    except Exception as e:
        logger.error(f"Error calculating size: {e}")
        return "Unknown size"

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
    return {"zip": ".zip", "tar": ".tar", "tgz": ".tgz", "tbz2": ".tbz2"}.get(format, "")

def adjust_path(path):
    adjusted_path = (
        path
        if os.path.isabs(path)
        else os.path.join(os.getenv("GITHUB_WORKSPACE", os.getcwd()), path)
    )
    print(f"Adjusted path: {adjusted_path}")
    return adjusted_path

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
