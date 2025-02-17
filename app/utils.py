import os
import subprocess
import logging
import sys
from typing import Union, Optional, Dict, List, Callable, Any
from dataclasses import dataclass
from enum import Enum
import time
from functools import wraps


class CompressionFormat(Enum):
    ZIP = 'zip'
    TAR = 'tar'
    TGZ = 'tgz'
    TBZ2 = 'tbz2'

    @classmethod
    def list(cls) -> List[str]:
        return [format.value for format in cls]

@dataclass
class CommandConfig:
    command: str
    options: Callable[[Optional[str]], str]
    format: Callable[[str, str], str]

class ProcessResult:
    def __init__(self, success: bool, message: str, data: Optional[Dict] = None):
        self.success = success
        self.message = message
        self.data = data or {}

def retry_on_failure(max_retries: int = 3, delay: int = 1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    time.sleep(delay * (attempt + 1))
            return None
        return wrapper
    return decorator

class Logger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._setup_logging()

    def _setup_logging(self):
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def set_verbose(self, verbose: bool):
        self.logger.setLevel(logging.DEBUG if verbose else logging.INFO)

logger = Logger()

class CommandExecutor:
    @staticmethod
    @retry_on_failure()
    def run(command: str, verbose: bool = False) -> ProcessResult:
        print(f"⚙️  Executing: {command}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                text=True,
                capture_output=True,
                check=True
            )
            if result.stdout and verbose:
                logger.logger.debug(f"Command output:\n{result.stdout.strip()}")
            if result.stderr:
                logger.logger.warning(f"Command stderr:\n{result.stderr.strip()}")
            return ProcessResult(True, "Command executed successfully")
        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed: {e}"
            if os.getenv("FAIL_ON_ERROR", "true").lower() == "true":
                raise RuntimeError(f"{error_msg}\nError output:\n{e.stderr}")
            return ProcessResult(False, error_msg, {"stderr": e.stderr})

class FileUtils:
    @staticmethod
    def get_size(size_or_path: Union[int, str]) -> str:
        try:
            size = (os.path.getsize(size_or_path) 
                   if isinstance(size_or_path, str) 
                   else size_or_path)
            
            units = ['B', 'KB', 'MB', 'GB', 'TB']
            for unit in units:
                if size < 1024:
                    return f"{size:.2f} {unit}"
                size /= 1024
            return f"{size:.2f} {units[-1]}"
        except Exception as e:
            logger.logger.error(f"Error calculating size: {e}")
            return "Unknown size"

    @staticmethod
    def get_directory_size(path: str) -> int:
        total = 0
        for dirpath, _, filenames in os.walk(path):
            total += sum(
                os.path.getsize(os.path.join(dirpath, f))
                for f in filenames
            )
        return total

    @staticmethod
    def adjust_path(path: str) -> str:
        if os.path.isabs(path):
            return path
        return os.path.join(
            os.getenv("GITHUB_WORKSPACE", os.getcwd()),
            path
        )

class UI:
    @staticmethod
    def print_header(title: str):
        print("\n" + "=" * 50)
        print(f"🚀 {title}")
        print("=" * 50 + "\n")

    @staticmethod
    def print_section(title: str):
        print(f"\n📋 {title}:")

    @staticmethod
    def print_success(message: str):
        print(f"✅ {message}")

    @staticmethod
    def print_error(message: str):
        print(f"❌ {message}")

def print_error(message: str):
    UI.print_error(message)

def print_success(message: str):
    UI.print_success(message)

def print_header(title: str):
    UI.print_header(title)

def print_section(title: str):
    UI.print_section(title)

DECOMPRESSION_COMMANDS = {
    CompressionFormat.ZIP.value: CommandConfig(
        "unzip",
        lambda d: f"-d {d}" if d else "-j -d .",
        lambda src, opt: f"{opt} {src}"
    ),
    CompressionFormat.TAR.value: CommandConfig(
        "tar",
        lambda d: f"-C {d}" if d else "-C .",
        lambda src, opt: f"-xf {src} {opt}"
    ),
    CompressionFormat.TGZ.value: CommandConfig(
        "tar",
        lambda d: f"-C {d}" if d else "-C .",
        lambda src, opt: f"-xzf {src} {opt}"
    ),
    CompressionFormat.TBZ2.value: CommandConfig(
        "tar",
        lambda d: f"-C {d}" if d else "-C .",
        lambda src, opt: f"-xjf {src} {opt}"
    )
}

def validate_format(format):
    """Validate compression format"""
    valid_formats = ['zip', 'tar', 'tgz', 'tbz2']
    if format not in valid_formats:
        error_msg = f"Invalid format: {format}"
        if os.getenv("FAIL_ON_ERROR", "true").lower() == "true":
            print_error(error_msg)
            print(f"Supported formats: {', '.join(valid_formats)}")
            sys.exit(1)
        else:
            logger.warning(error_msg)
            logger.warning(f"Supported formats: {', '.join(valid_formats)}")
            return False
    return True

def get_extension(format):
    return {"zip": ".zip", "tar": ".tar", "tgz": ".tgz", "tbz2": ".tbz2"}.get(format, "")
