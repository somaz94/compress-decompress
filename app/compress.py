from __future__ import annotations

from datetime import datetime
import os
import shlex
import shutil
import tempfile
from typing import List, TYPE_CHECKING
from config import CompressionFormat
from ui import UI
from file_utils import FileUtils
from executor import CommandExecutor, ProcessResult
from base_processor import BaseProcessor
from app_logger import logger
from exceptions import ValidationError

if TYPE_CHECKING:
    from config import AppConfig


class Compressor(BaseProcessor):
    """
    Handles file/directory compression operations

    Supports compression using zip, tar, tgz, tbz2 formats with options
    like preserving root directory structure, excluding files, and
    glob patterns for matching multiple files.
    """
    def __init__(self, config: AppConfig):
        super().__init__(config)
        self.source = config.source
        self.format = config.format
        self.include_root = FileUtils.str_to_bool(config.include_root)
        self.preserve_glob_structure = FileUtils.str_to_bool(config.preserve_glob_structure)
        self.strip_prefix = config.strip_prefix
        self.is_glob_pattern = False
        self.matched_files: List[str] = []
        self.temp_dir = None

    def validate(self) -> bool:
        """Validate that source path exists or glob pattern matches files"""
        self.source = self.source.strip()

        # Convert GitHub Actions runner path to Docker container path
        if self.source.startswith('/home/runner/work/'):
            self.source = '/github/workspace'

        # Check if source is a glob pattern
        if FileUtils.is_glob_pattern(self.source):
            self.is_glob_pattern = True
            UI.print_section("Glob Pattern Detected")
            print(f"  \u2022 Pattern: {self.source}")

            self.matched_files = FileUtils.find_files_by_pattern(self.source)

            if not self.matched_files:
                error_msg = f"No files matched the pattern: {self.source}"
                if self.fail_on_error:
                    raise ValidationError(error_msg)
                logger.logger.warning(error_msg)
                return False

            print(f"  \u2022 Matched {len(self.matched_files)} file(s)")
            if self.verbose:
                for i, file_path in enumerate(self.matched_files[:10], 1):
                    print(f"    {i}. {file_path}")
                if len(self.matched_files) > 10:
                    print(f"    ... and {len(self.matched_files) - 10} more files")

            return True

        return self.validate_path(self.source, "Source path")

    def get_compression_command(self) -> str:
        """Generate the appropriate compression command based on format"""
        base_name = self.destfilename or os.path.basename(self.source)
        extension = f".{self.format}"
        full_dest = self._determine_destination_path(base_name, extension)

        if self.format == CompressionFormat.ZIP.value:
            return self._get_zip_command(full_dest, base_name)
        return self._get_tar_command(full_dest, base_name)

    def _determine_destination_path(self, base_name: str, extension: str) -> str:
        """Determine the full destination path for the compressed file"""
        if self.dest and self.dest != os.getcwd():
            return os.path.abspath(os.path.join(self.dest, f"{base_name}{extension}"))

        output_dir = os.path.dirname(self.source) if self.include_root else self.source
        return os.path.join(output_dir, f"{base_name}{extension}")

    def _get_zip_command(self, full_dest: str, base_name: str) -> str:
        """Generate zip compression command"""
        source_path = os.path.abspath(self.source)
        source_path = os.getcwd() if source_path == '/github/workspace' else source_path
        exclude_cmd = self._build_zip_exclude(source_path)

        if self.include_root:
            parent_dir = os.path.dirname(source_path)
            dir_name = os.path.basename(source_path)
            return f"cd {shlex.quote(parent_dir)} && zip -r {shlex.quote(full_dest)} {shlex.quote(dir_name)} {exclude_cmd}"

        return f"cd {shlex.quote(source_path)} && zip -r {shlex.quote(full_dest)} . {exclude_cmd}"

    def _build_zip_exclude(self, source_path: str) -> str:
        """Build zip exclusion flags from parsed patterns"""
        patterns = self.parse_exclude_patterns()
        if not patterns:
            return ""

        dir_name = os.path.basename(source_path)
        processed = []
        for pattern in patterns:
            if self.include_root:
                processed.extend(self._format_pattern_with_root(pattern, source_path, dir_name))
            else:
                processed.extend(self._format_pattern_without_root(pattern, source_path))

        return " ".join([f'-x {shlex.quote(p)}' for p in processed])

    def _format_pattern_with_root(self, pattern: str, source_path: str, dir_name: str) -> List[str]:
        """Format exclusion pattern when includeRoot is true"""
        if pattern.startswith(f"{dir_name}/") or pattern == dir_name:
            return [pattern]
        if os.path.isdir(os.path.join(source_path, pattern)) and not pattern.endswith('/*'):
            if pattern.endswith('/'):
                return [f"{dir_name}/{pattern}*"]
            return [f"{dir_name}/{pattern}/*", f"{dir_name}/{pattern}/"]
        return [f"{dir_name}/{pattern}"]

    def _format_pattern_without_root(self, pattern: str, source_path: str) -> List[str]:
        """Format exclusion pattern when includeRoot is false"""
        if os.path.isdir(os.path.join(source_path, pattern)) and not pattern.endswith('/*'):
            return [f"{pattern}/*", f"{pattern}/"]
        return [pattern]

    def _get_tar_command(self, full_dest: str, base_name: str) -> str:
        """Generate tar compression command"""
        source_path = os.path.abspath(self.source)
        source_path = os.getcwd() if source_path == '/github/workspace' else source_path

        tar_options = {
            CompressionFormat.TAR.value: "",
            CompressionFormat.TGZ.value: "z",
            CompressionFormat.TBZ2.value: "j"
        }
        opt = tar_options.get(self.format, "")

        # Special case for TGZ/TBZ2 without root
        if self.format in [CompressionFormat.TGZ.value, CompressionFormat.TBZ2.value] and not self.include_root:
            return self._get_special_tar_command(full_dest, base_name, opt)

        exclude_cmd = self._build_tar_exclude(source_path)

        if self.include_root:
            parent_dir = os.path.dirname(source_path)
            dir_name = os.path.basename(source_path)
            return f"tar {exclude_cmd} -c{opt}f {shlex.quote(full_dest)} -C {shlex.quote(parent_dir)} {shlex.quote(dir_name)}"

        return f"tar {exclude_cmd} -c{opt}f {shlex.quote(full_dest)} -C {shlex.quote(source_path)} ."

    def _build_tar_exclude(self, source_path: str) -> str:
        """Build tar exclusion flags from parsed patterns"""
        patterns = self.parse_exclude_patterns()
        if not patterns:
            return ""

        dir_name = os.path.basename(source_path)
        processed = []
        for pattern in patterns:
            if self.include_root and not pattern.startswith(dir_name):
                processed.append(f"{dir_name}/{pattern}")
            else:
                processed.append(pattern)

        return " ".join([f'--exclude={shlex.quote(p)}' for p in processed])

    def _get_special_tar_command(self, full_dest: str, base_name: str, opt: str) -> str:
        """Generate special tar command for TGZ/TBZ2 formats without root"""
        source_path = os.path.abspath(self.source)
        temp_dir = os.path.join(os.path.dirname(source_path), f"temp_{base_name}_{self.format}")

        patterns = self.parse_exclude_patterns()
        exclude_cmd = " ".join([f'--exclude={shlex.quote(p)}' for p in patterns]) if patterns else ""

        q_temp = shlex.quote(temp_dir)
        q_src = shlex.quote(source_path)
        q_dest = shlex.quote(full_dest)
        return f"""
            mkdir -p {q_temp} &&
            cp -r {q_src}/* {q_temp}/ &&
            tar {exclude_cmd} -c{opt}f {q_dest} -C {q_temp} . &&
            rm -rf {q_temp}
        """

    def compress(self) -> ProcessResult:
        """Execute the compression process"""
        try:
            UI.print_header("Compression Process Started")
            if not self.validate():
                return ProcessResult(False, "Validation failed")

            if self.is_glob_pattern:
                return self._compress_glob_pattern()

            source_size = FileUtils.get_path_size(self.source)
            start_time = datetime.now()
            self.source = FileUtils.adjust_path(self.source)

            self._print_configuration(source_size)
            self.prepare_destination()

            command = self.get_compression_command()
            result = CommandExecutor.run(command, self.verbose, self.fail_on_error)

            if result.success:
                self._print_results(start_time, source_size)

            return result

        except Exception as e:
            return self.handle_error(e, "Compression")
        finally:
            self._cleanup_temp_directory()

    def _print_configuration(self, source_size: int) -> None:
        """Print compression configuration details"""
        UI.print_section("Configuration")
        print(f"  \u2022 Source: {self.source}")
        print(f"  \u2022 Format: {self.format}")
        print(f"  \u2022 Include Root: {self.include_root}")
        print(f"  \u2022 Source Size: {FileUtils.get_size(source_size)}")
        print(f"  \u2022 Initial Directory: {os.getcwd()}")
        if self.exclude:
            print(f"  \u2022 Exclude Pattern: {self.exclude}")

    def _print_results(self, start_time: datetime, source_size: int) -> None:
        """Print compression results"""
        duration = (datetime.now() - start_time).total_seconds()

        if os.path.exists(self.dest):
            compressed_size = os.path.getsize(self.dest)
            ratio = (1 - (compressed_size / source_size)) * 100 if source_size > 0 else 0

            UI.print_section("Compression Results")
            print(f"  \u2022 Original Size: {FileUtils.get_size(source_size)}")
            print(f"  \u2022 Compressed Size: {FileUtils.get_size(compressed_size)}")
            print(f"  \u2022 Compression Ratio: {ratio:.1f}%")
            print(f"  \u2022 Duration: {duration:.2f} seconds")

    def _compress_glob_pattern(self) -> ProcessResult:
        """Compress files matched by glob pattern"""
        start_time = datetime.now()
        source_size = sum(os.path.getsize(f) for f in self.matched_files if os.path.exists(f))

        temp_base = tempfile.gettempdir()
        self.temp_dir = os.path.join(temp_base, f"compress_glob_{os.getpid()}")

        UI.print_section("Preparing Files")
        print(f"  \u2022 Creating temporary directory: {self.temp_dir}")
        print(f"  \u2022 Copying {len(self.matched_files)} matched file(s)")
        print(f"  \u2022 Preserve structure: {self.preserve_glob_structure}")
        if self.strip_prefix:
            print(f"  \u2022 Strip prefix: {self.strip_prefix}")

        FileUtils.copy_files_to_temp_directory(
            self.matched_files,
            self.temp_dir,
            preserve_structure=self.preserve_glob_structure,
            strip_prefix=self.strip_prefix
        )

        original_source = self.source
        self.source = self.temp_dir

        self._print_configuration(source_size)
        self.prepare_destination()

        command = self.get_compression_command()
        result = CommandExecutor.run(command, self.verbose, self.fail_on_error)

        if result.success:
            self._print_results(start_time, source_size)
            UI.print_success(f"Successfully compressed {len(self.matched_files)} file(s) matching pattern: {original_source}")

        return result

    def _cleanup_temp_directory(self) -> None:
        """Clean up temporary directory created for glob pattern compression"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                if self.verbose:
                    logger.logger.debug(f"Cleaned up temporary directory: {self.temp_dir}")
            except Exception as e:
                logger.logger.warning(f"Failed to clean up temporary directory: {str(e)}")


def compress(config: AppConfig) -> bool:
    """
    Main compression function called from the action.

    Args:
        config: Application configuration

    Returns:
        True if compression succeeded, False otherwise
    """
    compressor = Compressor(config)
    result = compressor.compress()
    return result.success
