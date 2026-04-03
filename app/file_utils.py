from __future__ import annotations

import os
import glob
import shutil
from app_logger import logger


class FileUtils:
    """File and directory utility methods"""

    @staticmethod
    def str_to_bool(value: str, default: bool = False) -> bool:
        if not value:
            return default
        return value.lower() in ("true", "yes", "1")

    @staticmethod
    def get_size(size_or_path: int | str) -> str:
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
        except (OSError, TypeError, ValueError) as e:
            logger.logger.error(f"Error calculating size: {e}")
            return "Unknown size"

    @staticmethod
    def get_directory_size(path: str) -> int:
        total = 0
        for dirpath, _, filenames in os.walk(path, followlinks=False):
            for f in filenames:
                filepath = os.path.join(dirpath, f)
                if os.path.exists(filepath):
                    total += os.path.getsize(filepath)
        return total

    @staticmethod
    def get_path_size(path: str) -> int:
        real_path = os.path.realpath(path)
        if os.path.isdir(real_path):
            return FileUtils.get_directory_size(real_path)
        return os.path.getsize(real_path)

    @staticmethod
    def adjust_path(path: str) -> str:
        path = path.strip()
        if os.path.isabs(path):
            return path
        github_workspace = os.getenv("GITHUB_WORKSPACE")
        if github_workspace:
            return os.path.abspath(os.path.join(github_workspace, path))
        return os.path.abspath(os.path.join(os.getcwd(), path))

    @staticmethod
    def is_glob_pattern(path: str) -> bool:
        glob_chars = ['*', '?', '[', ']']
        return any(char in path for char in glob_chars)

    @staticmethod
    def find_files_by_pattern(pattern: str, base_dir: str | None = None) -> list[str]:
        if base_dir is None:
            base_dir = os.getcwd()
        original_dir = os.getcwd()
        try:
            os.chdir(base_dir)
            matched_files = []
            for match in glob.glob(pattern, recursive=True):
                real_path = os.path.realpath(match)
                if os.path.isfile(real_path):
                    matched_files.append(match)
            return [os.path.abspath(f) for f in matched_files]
        finally:
            os.chdir(original_dir)

    @staticmethod
    def copy_files_to_temp_directory(file_paths: list[str], temp_dir: str,
                                      preserve_structure: bool = False,
                                      strip_prefix: str = "") -> None:
        os.makedirs(temp_dir, exist_ok=True)
        if strip_prefix:
            strip_prefix = strip_prefix.rstrip(os.sep) + os.sep
        for file_path in file_paths:
            if preserve_structure:
                relative_path = os.path.relpath(file_path)
                if strip_prefix and relative_path.startswith(strip_prefix):
                    relative_path = relative_path[len(strip_prefix):]
                dest_path = os.path.join(temp_dir, relative_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(file_path, dest_path)
            else:
                file_name = os.path.basename(file_path)
                dest_path = os.path.join(temp_dir, file_name)
                counter = 1
                base_name, ext = os.path.splitext(file_name)
                while os.path.exists(dest_path):
                    dest_path = os.path.join(temp_dir, f"{base_name}_{counter}{ext}")
                    counter += 1
                shutil.copy2(file_path, dest_path)
