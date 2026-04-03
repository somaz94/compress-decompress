from __future__ import annotations

import subprocess
import time
from functools import wraps
from app_logger import logger
from exceptions import CommandError

DEFAULT_TIMEOUT = 3600  # 1 hour


class ProcessResult:
    """Container for operation results"""

    def __init__(self, success: bool, message: str, data: dict | None = None):
        self.success = success
        self.message = message
        self.data = data or {}


def retry_on_failure(max_retries: int = 3, delay: int = 1):
    """Decorator to retry a function on failure with increasing delay"""
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


class CommandExecutor:
    """Shell command execution with error handling and retry"""

    @staticmethod
    @retry_on_failure()
    def run(command: str, verbose: bool = False, fail_on_error: bool = True,
            timeout: int = DEFAULT_TIMEOUT) -> ProcessResult:
        print(f"\u2699\ufe0f  Executing: {command}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                text=True,
                capture_output=True,
                check=True,
                timeout=timeout
            )
            if result.stdout and verbose:
                logger.logger.debug(f"Command output:\n{result.stdout.strip()}")
            if result.stderr:
                logger.logger.warning(f"Command stderr:\n{result.stderr.strip()}")
            return ProcessResult(True, "Command executed successfully")
        except subprocess.TimeoutExpired as e:
            error_msg = f"Command timed out after {timeout}s: {command}"
            if fail_on_error:
                raise CommandError(error_msg) from e
            return ProcessResult(False, error_msg)
        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed: {e}"
            if fail_on_error:
                raise CommandError(f"{error_msg}\nError output:\n{e.stderr}") from e
            return ProcessResult(False, error_msg, {"stderr": e.stderr})
