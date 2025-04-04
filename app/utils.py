import os
import subprocess
import logging
import sys
from typing import Union, Optional, Dict, List, Callable, Any, TypeVar, Generic
from dataclasses import dataclass
from enum import Enum
import time
from functools import wraps

T = TypeVar('T')

class CompressionFormat(Enum):
    ZIP = 'zip'
    TAR = 'tar'
    TGZ = 'tgz'
    TBZ2 = 'tbz2'

    @classmethod
    def list(cls) -> List[str]:
        return [format.value for format in cls]

    @classmethod
    def validate(cls, format_str: str) -> bool:
        """Validate compression format"""
        if format_str not in cls.list():
            error_msg = f"Invalid format: {format_str}"
            if os.getenv("FAIL_ON_ERROR", "true").lower() == "true":
                UI.print_error(error_msg)
                print(f"Supported formats: {', '.join(cls.list())}")
                sys.exit(1)
            else:
                logger.logger.warning(error_msg)
                logger.logger.warning(f"Supported formats: {', '.join(cls.list())}")
                return False
        return True

    @classmethod
    def get_extension(cls, format_str: str) -> str:
        """Get file extension for a format"""
        for format_enum in cls:
            if format_enum.value == format_str:
                return f".{format_str}"
        return ""

@dataclass
class CommandConfig:
    command: str
    options: Callable[[Optional[str]], str]
    format: Callable[[str, str], str]

class ProcessResult(Generic[T]):
    def __init__(self, success: bool, message: str, data: Optional[T] = None):
        self.success = success
        self.message = message
        self.data = data or {}

class BaseProcessor:
    """Base class for compression/decompression processors"""
    def __init__(self):
        self.fail_on_error = os.getenv("FAIL_ON_ERROR", "true").lower() == "true"
        self.verbose = os.getenv("VERBOSE", "false").lower() == "true"
        self.dest = os.getenv("DEST", os.getenv("GITHUB_WORKSPACE", os.getcwd()))
        self.destfilename = os.getenv("DESTFILENAME", "")

    def validate_path(self, path: str, error_prefix: str = "Path") -> bool:
        """Validate that a path exists"""
        if not os.path.exists(path):
            error_msg = f"{error_prefix} '{path}' does not exist"
            if self.fail_on_error:
                UI.print_error(error_msg)
                sys.exit(1)
            logger.logger.warning(error_msg)
            return False
        return True

    def prepare_destination(self) -> None:
        """Create destination directory if it doesn't exist"""
        if self.dest and not os.path.exists(self.dest):
            os.makedirs(self.dest)

    def handle_error(self, error: Exception, context: str = "Operation") -> ProcessResult:
        """Handle exceptions consistently"""
        error_msg = f"{context} failed: {str(error)}"
        if self.fail_on_error:
            UI.print_error(error_msg)
            sys.exit(1)
        logger.logger.warning(f"{context} warning: {str(error)}")
        return ProcessResult(False, str(error))

def retry_on_failure(max_retries: int = 3, delay: int = 1):
    """Decorator to retry a function on failure"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    time.sleep(delay * (attempt + 1))
            return None
        return wrapper
    return decorator

class Logger:
    """Logging utility class"""
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
    """Utility for executing shell commands"""
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
    """File and directory utilities"""
    @staticmethod
    def get_size(size_or_path: Union[int, str]) -> str:
        """Convert bytes to human-readable size format"""
        try:
            size = (os.path.getsize(size_or_path) 
                   if isinstance(size_or_path, str) and os.path.exists(size_or_path)
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
        """Calculate total size of a directory"""
        total = 0
        for dirpath, _, filenames in os.walk(path):
            total += sum(
                os.path.getsize(os.path.join(dirpath, f))
                for f in filenames if os.path.exists(os.path.join(dirpath, f))
            )
        return total

    @staticmethod
    def adjust_path(path: str) -> str:
        """Convert relative path to absolute path"""
        # 앞뒤 공백 제거
        path = path.strip()
        
        # GitHub Actions의 두 가지 경로 형식 처리
        if path.startswith('/github/workspace'):
            # Docker 컨테이너 내부 경로를 실제 러너 경로로 변환
            runner_workspace = os.getenv("RUNNER_WORKSPACE", "")
            if runner_workspace:
                repo_name = os.getenv("GITHUB_REPOSITORY", "").split('/')[-1]
                return path.replace('/github/workspace', 
                                 os.path.join(runner_workspace, repo_name))
            
        elif path.startswith('/home/runner/work/'):
            # 이미 러너 경로면 그대로 사용
            return path
            
        # 상대 경로나 다른 절대 경로 처리
        if os.path.isabs(path):
            return path
            
        # GITHUB_WORKSPACE 환경변수 확인
        github_workspace = os.getenv("GITHUB_WORKSPACE", "")
        if github_workspace:
            # GitHub Actions 환경에서는 러너 경로 사용
            runner_workspace = os.getenv("RUNNER_WORKSPACE", "")
            if runner_workspace:
                repo_name = os.getenv("GITHUB_REPOSITORY", "").split('/')[-1]
                base_path = os.path.join(runner_workspace, repo_name)
                return os.path.abspath(os.path.join(base_path, path))
                
        # 기본값: 현재 디렉토리 기준
        return os.path.abspath(os.path.join(os.getcwd(), path))

class UI:
    """User interface utilities"""
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

# Define decompression commands
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
