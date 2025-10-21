import os
import subprocess
import logging
import sys
from typing import Union, Optional, Dict, List, Callable, Any, TypeVar, Generic
from dataclasses import dataclass
from enum import Enum
import time
from functools import wraps
import glob
import shutil

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
        return f".{format_str}" if format_str in cls.list() else ""

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
                    logger.logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                    time.sleep(delay * (attempt + 1))
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
        # Only add handler if none exists to prevent duplicates
        if not self.logger.handlers:
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
        Also resolves symbolic links to check if the target exists.
        
        Args:
            path: File or directory path to validate (can be a symlink)
            error_prefix: Prefix for error messages
            
        Returns:
            True if path exists, False otherwise
        """
        # Remove leading/trailing whitespace
        path = path.strip()
        
        # Check if path exists (including symlinks)
        # os.path.exists() returns False for broken symlinks
        # os.path.lexists() returns True even for broken symlinks
        if not os.path.lexists(path):
            error_msg = f"{error_prefix} '{path}' does not exist"
            if self.fail_on_error:
                UI.print_error(error_msg)
                sys.exit(1)
            logger.logger.warning(error_msg)
            return False
        
        # If it's a symlink, verify the target exists
        if os.path.islink(path):
            real_path = os.path.realpath(path)
            if not os.path.exists(real_path):
                error_msg = f"{error_prefix} '{path}' is a broken symbolic link (target: '{real_path}' does not exist)"
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
        Follows symbolic links to get actual file sizes.
        
        Args:
            path: Directory path (can be a symlink to a directory)
            
        Returns:
            Total size in bytes
        """
        total = 0
        # followlinks=True makes os.walk follow symbolic links
        for dirpath, _, filenames in os.walk(path, followlinks=True):
            for f in filenames:
                filepath = os.path.join(dirpath, f)
                # Use os.path.exists which follows symlinks
                if os.path.exists(filepath):
                    # Get size of actual file (following symlink if needed)
                    total += os.path.getsize(filepath)
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

    @staticmethod
    def is_glob_pattern(path: str) -> bool:
        """
        Check if a path string contains glob pattern characters
        
        Detects patterns like *, ?, [, ], **, etc.
        
        Args:
            path: Path string to check
            
        Returns:
            True if the path contains glob pattern characters, False otherwise
        """
        glob_chars = ['*', '?', '[', ']']
        return any(char in path for char in glob_chars)

    @staticmethod
    def find_files_by_pattern(pattern: str, base_dir: Optional[str] = None) -> List[str]:
        """
        Find files matching a glob pattern
        
        Supports patterns like:
        - **/*.doc (all .doc files in all subdirectories)
        - *.txt (all .txt files in current directory)
        - folder/**/*.py (all .py files in folder and subdirectories)
        
        Args:
            pattern: Glob pattern to match files
            base_dir: Base directory to search from (defaults to current directory)
            
        Returns:
            List of absolute paths to matched files
        """
        if base_dir is None:
            base_dir = os.getcwd()
        
        # Change to base directory for pattern matching
        original_dir = os.getcwd()
        try:
            os.chdir(base_dir)
            # Use recursive glob to find all matching files
            # Note: glob doesn't follow symlinks by default in Python < 3.13
            # We need to resolve symlinks manually
            matched_files = []
            for match in glob.glob(pattern, recursive=True):
                # Resolve symlinks to actual paths
                real_path = os.path.realpath(match)
                # Check if it's a file (following symlinks)
                if os.path.isfile(real_path):
                    matched_files.append(match)
            
            # Convert to absolute paths
            absolute_paths = [os.path.abspath(f) for f in matched_files]
            return absolute_paths
        finally:
            # Always restore original directory
            os.chdir(original_dir)

    @staticmethod
    def copy_files_to_temp_directory(file_paths: List[str], temp_dir: str, preserve_structure: bool = False, strip_prefix: str = "") -> None:
        """
        Copy multiple files to a temporary directory
        
        Args:
            file_paths: List of file paths to copy
            temp_dir: Destination temporary directory
            preserve_structure: If True, preserve directory structure; if False, flatten all files
            strip_prefix: Prefix to remove from file paths when preserving structure (e.g., 'src/' or 'dir/')
        """
        os.makedirs(temp_dir, exist_ok=True)
        
        # Normalize strip_prefix for consistent comparison
        if strip_prefix:
            strip_prefix = strip_prefix.rstrip(os.sep) + os.sep
        
        for file_path in file_paths:
            if preserve_structure:
                # Preserve directory structure
                relative_path = os.path.relpath(file_path)
                
                # Strip prefix if specified
                if strip_prefix and relative_path.startswith(strip_prefix):
                    relative_path = relative_path[len(strip_prefix):]
                
                dest_path = os.path.join(temp_dir, relative_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(file_path, dest_path)
            else:
                # Flatten: copy all files to temp_dir root
                file_name = os.path.basename(file_path)
                dest_path = os.path.join(temp_dir, file_name)
                # Handle duplicate filenames by adding counter
                counter = 1
                base_name, ext = os.path.splitext(file_name)
                while os.path.exists(dest_path):
                    dest_path = os.path.join(temp_dir, f"{base_name}_{counter}{ext}")
                    counter += 1
                shutil.copy2(file_path, dest_path)

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
