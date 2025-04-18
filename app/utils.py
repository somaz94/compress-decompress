import os
import subprocess
import logging
import sys
from typing import Union, Optional, Dict, List, Callable, Any, TypeVar, Generic
from dataclasses import dataclass
from enum import Enum
import time
from functools import wraps

# Type variable for generic typing
T = TypeVar('T')

# ======================================================================
# Compression Format Configuration
# ======================================================================

class CompressionFormat(Enum):
    """
    Enum defining supported compression formats
    
    These formats are used throughout the application for compression and
    decompression operations.
    """
    ZIP = 'zip'
    TAR = 'tar'
    TGZ = 'tgz'
    TBZ2 = 'tbz2'

    @classmethod
    def list(cls) -> List[str]:
        """
        Get a list of all supported format values
        
        Returns:
            List of format string values (e.g., ['zip', 'tar', 'tgz', 'tbz2'])
        """
        return [format.value for format in cls]

    @classmethod
    def validate(cls, format_str: str) -> bool:
        """
        Validate that a format string is supported
        
        Handles error reporting based on FAIL_ON_ERROR environment variable.
        
        Args:
            format_str: Format string to validate
            
        Returns:
            True if format is valid, False otherwise
        """
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
        """
        Get file extension for a format
        
        Args:
            format_str: Format string
            
        Returns:
            File extension with leading dot (e.g., '.zip')
        """
        for format_enum in cls:
            if format_enum.value == format_str:
                return f".{format_str}"
        return ""

# ======================================================================
# Command Configuration
# ======================================================================

@dataclass
class CommandConfig:
    """
    Configuration for format-specific commands
    
    Defines how commands should be executed for a specific compression format,
    including the base command, options formatting, and argument formatting.
    """
    command: str
    options: Callable[[Optional[str]], str]
    format: Callable[[str, str], str]

# Define decompression commands for each supported format
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

# ======================================================================
# Process Result Handling
# ======================================================================

class ProcessResult(Generic[T]):
    """
    Container for operation results
    
    Provides a standardized way to return success/failure status, messages,
    and optional data from operations.
    """
    def __init__(self, success: bool, message: str, data: Optional[T] = None):
        """
        Initialize process result
        
        Args:
            success: Whether the operation succeeded
            message: Descriptive message about the operation result
            data: Optional data associated with the result
        """
        self.success = success
        self.message = message
        self.data = data or {}

# ======================================================================
# Utility Functions and Decorators
# ======================================================================

def retry_on_failure(max_retries: int = 3, delay: int = 1):
    """
    Decorator to retry a function on failure
    
    Automatically retries the decorated function when an exception is raised,
    with increasing delay between attempts.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Base delay in seconds between retries (increases with each attempt)
        
    Returns:
        Decorated function that will retry on failure
    """
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

# ======================================================================
# Logging
# ======================================================================

class Logger:
    """
    Logging utility class
    
    Provides standardized logging configuration and methods for the application.
    """
    def __init__(self):
        """Initialize logger with standard configuration"""
        self.logger = logging.getLogger(__name__)
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging format and handlers"""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def set_verbose(self, verbose: bool):
        """
        Set logging verbosity level
        
        Args:
            verbose: If True, set to DEBUG level, otherwise INFO level
        """
        self.logger.setLevel(logging.DEBUG if verbose else logging.INFO)

# Initialize logger as a singleton
logger = Logger()

# ======================================================================
# Base Processor
# ======================================================================

class BaseProcessor:
    """
    Base class for compression/decompression processors
    
    Provides common functionality and configuration for both compression and
    decompression operations.
    """
    def __init__(self):
        """Initialize with environment variables and default settings"""
        # Load configuration from environment variables
        self.fail_on_error = os.getenv("FAIL_ON_ERROR", "true").lower() == "true"
        self.verbose = os.getenv("VERBOSE", "false").lower() == "true"
        self.dest = os.getenv("DEST", os.getenv("GITHUB_WORKSPACE", os.getcwd()))
        self.destfilename = os.getenv("DESTFILENAME", "")
        self.exclude = os.getenv("EXCLUDE", "")

    def validate_path(self, path: str, error_prefix: str = "Path") -> bool:
        """
        Validate that a path exists
        
        Handles error reporting based on fail_on_error setting.
        
        Args:
            path: File or directory path to validate
            error_prefix: Prefix for error messages
            
        Returns:
            True if path exists, False otherwise
        """
        # Remove leading/trailing whitespace
        path = path.strip()
        
        if not os.path.exists(path):
            error_msg = f"{error_prefix} '{path}' does not exist"
            if self.fail_on_error:
                UI.print_error(error_msg)
                sys.exit(1)
            logger.logger.warning(error_msg)
            return False
        return True

    def prepare_destination(self) -> None:
        """
        Create destination directory if it doesn't exist
        
        Ensures the target directory exists before attempting file operations.
        """
        if self.dest and not os.path.exists(self.dest):
            os.makedirs(self.dest)

    def handle_error(self, error: Exception, context: str = "Operation") -> ProcessResult:
        """
        Handle exceptions consistently
        
        Standardizes error handling across the application based on fail_on_error setting.
        
        Args:
            error: Exception that occurred
            context: Description of the operation context
            
        Returns:
            ProcessResult with failure status
        """
        error_msg = f"{context} failed: {str(error)}"
        if self.fail_on_error:
            UI.print_error(error_msg)
            sys.exit(1)
        logger.logger.warning(f"{context} warning: {str(error)}")
        return ProcessResult(False, str(error))

# ======================================================================
# Command Execution
# ======================================================================

class CommandExecutor:
    """
    Utility for executing shell commands
    
    Provides standardized command execution with error handling and retry capability.
    """
    @staticmethod
    @retry_on_failure()
    def run(command: str, verbose: bool = False) -> ProcessResult:
        """
        Execute a shell command with error handling
        
        Args:
            command: Shell command to execute
            verbose: Whether to enable verbose output
            
        Returns:
            ProcessResult with execution status and output
        """
        print(f"⚙️  Executing: {command}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                text=True,
                capture_output=True,
                check=True
            )
            # Log stdout in verbose mode
            if result.stdout and verbose:
                logger.logger.debug(f"Command output:\n{result.stdout.strip()}")
            # Always log stderr as warnings
            if result.stderr:
                logger.logger.warning(f"Command stderr:\n{result.stderr.strip()}")
            return ProcessResult(True, "Command executed successfully")
        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed: {e}"
            if os.getenv("FAIL_ON_ERROR", "true").lower() == "true":
                raise RuntimeError(f"{error_msg}\nError output:\n{e.stderr}")
            return ProcessResult(False, error_msg, {"stderr": e.stderr})

# ======================================================================
# File Utilities
# ======================================================================

class FileUtils:
    """
    File and directory utilities
    
    Provides helper methods for file operations, path handling, and size calculations.
    """
    @staticmethod
    def get_size(size_or_path: Union[int, str]) -> str:
        """
        Convert bytes to human-readable size format
        
        Can accept either a file path or a size in bytes.
        
        Args:
            size_or_path: File path or size in bytes
            
        Returns:
            Human-readable size string (e.g., "4.20 MB")
        """
        try:
            # Get size from path if a string and path exists
            size = (os.path.getsize(size_or_path) 
                   if isinstance(size_or_path, str) and os.path.exists(size_or_path)
                   else size_or_path)
            
            # Convert to appropriate unit
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
        """
        Calculate total size of a directory
        
        Recursively traverses directory to sum the size of all files.
        
        Args:
            path: Directory path
            
        Returns:
            Total size in bytes
        """
        total = 0
        for dirpath, _, filenames in os.walk(path):
            total += sum(
                os.path.getsize(os.path.join(dirpath, f))
                for f in filenames if os.path.exists(os.path.join(dirpath, f))
            )
        return total

    @staticmethod
    def adjust_path(path: str) -> str:
        """
        Convert relative path to absolute path
        
        Handles GitHub Actions workspace paths and relative paths.
        
        Args:
            path: File or directory path
            
        Returns:
            Absolute path
        """
        # Strip leading/trailing whitespace
        path = path.strip()
        
        # If the path is already absolute, return it as is
        if os.path.isabs(path):
            return path
            
        # Check the GITHUB_WORKSPACE environment variable
        github_workspace = os.getenv("GITHUB_WORKSPACE")
        if github_workspace:
            # If GITHUB_WORKSPACE is set, create an absolute path based on it
            return os.path.abspath(os.path.join(github_workspace, path))
            
        # If GITHUB_WORKSPACE is not set, create an absolute path based on the current directory
        return os.path.abspath(os.path.join(os.getcwd(), path))

# ======================================================================
# User Interface
# ======================================================================

class UI:
    """
    User interface utilities
    
    Provides standardized output formatting for the application.
    """
    @staticmethod
    def print_header(title: str):
        """
        Print a section header
        
        Args:
            title: Header title
        """
        print("\n" + "=" * 50)
        print(f"🚀 {title}")
        print("=" * 50 + "\n")

    @staticmethod
    def print_section(title: str):
        """
        Print a subsection header
        
        Args:
            title: Section title
        """
        print(f"\n📋 {title}:")

    @staticmethod
    def print_success(message: str):
        """
        Print a success message
        
        Args:
            message: Success message
        """
        print(f"✅ {message}")

    @staticmethod
    def print_error(message: str):
        """
        Print an error message
        
        Args:
            message: Error message
        """
        print(f"❌ {message}")
