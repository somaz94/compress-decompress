from __future__ import annotations

import os
from typing import TYPE_CHECKING
from file_utils import FileUtils
from ui import UI
from app_logger import logger
from exceptions import ValidationError, CompressError
from executor import ProcessResult

if TYPE_CHECKING:
    from config import AppConfig


class BaseProcessor:
    """Base class for compression/decompression processors"""

    def __init__(self, config: AppConfig):
        self.fail_on_error = config.fail_on_error
        self.verbose = config.verbose
        self.dest = config.effective_dest
        self.destfilename = config.destfilename
        self.exclude = config.exclude

    def validate_path(self, path: str, error_prefix: str = "Path") -> bool:
        path = path.strip()
        if not os.path.lexists(path):
            error_msg = f"{error_prefix} '{path}' does not exist"
            if self.fail_on_error:
                raise ValidationError(error_msg)
            logger.logger.warning(error_msg)
            return False
        if os.path.islink(path):
            real_path = os.path.realpath(path)
            if not os.path.exists(real_path):
                error_msg = f"{error_prefix} '{path}' is a broken symbolic link (target: '{real_path}' does not exist)"
                if self.fail_on_error:
                    raise ValidationError(error_msg)
                logger.logger.warning(error_msg)
                return False
        return True

    def prepare_destination(self) -> None:
        if self.dest and not os.path.exists(self.dest):
            os.makedirs(self.dest)

    def handle_error(self, error: Exception, context: str = "Operation") -> ProcessResult:
        error_msg = f"{context} failed: {str(error)}"
        if self.fail_on_error:
            raise CompressError(error_msg) from error
        logger.logger.warning(f"{context} warning: {str(error)}")
        return ProcessResult(False, str(error))

    def parse_exclude_patterns(self) -> list[str]:
        """Parse exclude string into a list of individual patterns"""
        if not self.exclude:
            return []
        return [p.strip() for p in self.exclude.split() if p.strip()]
