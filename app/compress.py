from __future__ import annotations

from datetime import datetime
import os
import shlex
import shutil
import tempfile
from typing import TYPE_CHECKING
from config import CompressionFormat
from ui import UI
from file_utils import FileUtils
from executor import CommandExecutor, ProcessResult
from base_processor import BaseProcessor
from app_logger import logger
from exceptions import ValidationError, CompressError, CommandError
from stats import OperationStats

if TYPE_CHECKING:
    from config import AppConfig

_RUNNER_WORK_PREFIX = "/home/runner/work/"
_DEFAULT_CONTAINER_WORKSPACE = "/github/workspace"

# Single-letter tar codec flags, folded into `-c<opt>f`.
_TAR_COMPRESSION_FLAGS = {
    CompressionFormat.TAR.value: "",
    CompressionFormat.TGZ.value: "z",
    CompressionFormat.TBZ2.value: "j",
    CompressionFormat.TXZ.value: "J",
    CompressionFormat.TZST.value: "",
}

# Codecs tar only exposes as a long option.
_TAR_LONG_FLAGS = {
    CompressionFormat.TZST.value: "--zstd",
}

# Compressed tar formats take the temp-directory path when includeRoot is false.
_COMPRESSED_TAR_FORMATS = (
    CompressionFormat.TGZ.value,
    CompressionFormat.TBZ2.value,
    CompressionFormat.TXZ.value,
    CompressionFormat.TZST.value,
)


def _remap_runner_path(source: str) -> str:
    """
    Step 1 of the two-step GitHub Actions workspace remap.

    If the input is a host-side runner path (mounted from the GitHub-hosted
    runner into the action container), rewrite it to the in-container
    workspace path. Idempotent — returns the input unchanged when it is
    not a host-side path or when GITHUB_WORKSPACE is unset.

    Step 2 (Compressor._resolve_source_path) maps an absolute path equal to
    the workspace back to the current working directory.
    """
    if source.startswith(_RUNNER_WORK_PREFIX):
        workspace = os.getenv("GITHUB_WORKSPACE")
        if workspace:
            return workspace
    return source


class Compressor(BaseProcessor):
    """
    Handles file/directory compression operations

    Supports compression using zip, tar, tgz, tbz2, txz, tzst formats with options
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
        self.matched_files: list[str] = []
        self.compression_level = config.compression_level
        self.password = config.password
        self.temp_dir = None
        self.output_path = ""
        self.checksum = ""
        self.stats = OperationStats(command="compress", format=self.format)
        self._start_time = datetime.now()

    def validate(self) -> bool:
        """Validate that source path exists or glob pattern matches files"""
        self.source = _remap_runner_path(self.source.strip())

        # Check if source is a glob pattern
        if FileUtils.is_glob_pattern(self.source):
            self.is_glob_pattern = True
            UI.print_section("Glob Pattern Detected")
            UI.print_kv("Pattern", self.source)

            self.matched_files = FileUtils.find_files_by_pattern(self.source)

            if not self.matched_files:
                error_msg = f"No files matched the pattern: {self.source}"
                if self.fail_on_error:
                    raise ValidationError(error_msg)
                logger.warning(error_msg)
                return False

            UI.print_bullet(f"Matched {len(self.matched_files)} file(s)")
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
        self.output_path = full_dest

        if self.format == CompressionFormat.ZIP.value:
            return self._get_zip_command(full_dest, base_name)
        return self._get_tar_command(full_dest, base_name)

    def _determine_destination_path(self, base_name: str, extension: str) -> str:
        """Determine the full destination path for the compressed file"""
        if self.dest and self.dest != os.getcwd():
            return os.path.abspath(os.path.join(self.dest, f"{base_name}{extension}"))

        output_dir = os.path.dirname(self.source) if self.include_root else self.source
        return os.path.join(output_dir, f"{base_name}{extension}")

    def _resolve_source_path(self) -> str:
        """
        Step 2 of the two-step workspace remap: when the absolute source path
        equals the container workspace, use cwd as the operational source.
        See module-level `_remap_runner_path` for step 1.
        """
        source_path = os.path.abspath(self.source)
        workspace = os.getenv("GITHUB_WORKSPACE", _DEFAULT_CONTAINER_WORKSPACE)
        if source_path == workspace:
            return os.getcwd()
        return source_path

    def _get_zip_command(self, full_dest: str, base_name: str) -> str:
        """Generate zip compression command"""
        source_path = self._resolve_source_path()
        exclude_cmd = self._build_zip_exclude(source_path)
        level_flag = f" -{shlex.quote(self.compression_level)}" if self.compression_level else ""
        password_flag = f" -P {shlex.quote(self.password)}" if self.password else ""

        if self.include_root:
            parent_dir = os.path.dirname(source_path)
            dir_name = os.path.basename(source_path)
            return f"cd {shlex.quote(parent_dir)} && zip{level_flag}{password_flag} -r {shlex.quote(full_dest)} {shlex.quote(dir_name)} {exclude_cmd}"

        return f"cd {shlex.quote(source_path)} && zip{level_flag}{password_flag} -r {shlex.quote(full_dest)} . {exclude_cmd}"

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

    def _format_pattern_with_root(self, pattern: str, source_path: str, dir_name: str) -> list[str]:
        """Format exclusion pattern when includeRoot is true"""
        if pattern.startswith(f"{dir_name}/") or pattern == dir_name:
            return [pattern]
        if os.path.isdir(os.path.join(source_path, pattern)) and not pattern.endswith('/*'):
            if pattern.endswith('/'):
                return [f"{dir_name}/{pattern}*"]
            return [f"{dir_name}/{pattern}/*", f"{dir_name}/{pattern}/"]
        return [f"{dir_name}/{pattern}"]

    def _format_pattern_without_root(self, pattern: str, source_path: str) -> list[str]:
        """Format exclusion pattern when includeRoot is false"""
        if os.path.isdir(os.path.join(source_path, pattern)) and not pattern.endswith('/*'):
            return [f"{pattern}/*", f"{pattern}/"]
        return [pattern]

    def _get_tar_level_env(self) -> str:
        """Get environment variable prefix for tar compression level"""
        if not self.compression_level:
            return ""
        level = shlex.quote(self.compression_level)
        env_map = {
            CompressionFormat.TGZ.value: f"GZIP=-{level}",
            CompressionFormat.TBZ2.value: f"BZIP2=-{level}",
            CompressionFormat.TXZ.value: f"XZ_OPT=-{level}",
            # zstd reads a bare integer, not a dash-prefixed flag.
            CompressionFormat.TZST.value: f"ZSTD_CLEVEL={level}",
        }
        env = env_map.get(self.format, "")
        return f"{env} " if env else ""

    def _get_tar_command(self, full_dest: str, base_name: str) -> str:
        """Generate tar compression command"""
        source_path = self._resolve_source_path()

        opt = _TAR_COMPRESSION_FLAGS.get(self.format, "")
        # zstd has no single-letter tar flag; it is selected with --zstd.
        extra = f"{_TAR_LONG_FLAGS[self.format]} " if self.format in _TAR_LONG_FLAGS else ""
        level_env = self._get_tar_level_env()

        # Special case for the compressed tar formats without root
        if self.format in _COMPRESSED_TAR_FORMATS and not self.include_root:
            return self._get_special_tar_command(full_dest, base_name, opt)

        exclude_cmd = self._build_tar_exclude(source_path)

        if self.include_root:
            parent_dir = os.path.dirname(source_path)
            dir_name = os.path.basename(source_path)
            return f"{level_env}tar {extra}{exclude_cmd} -c{opt}f {shlex.quote(full_dest)} -C {shlex.quote(parent_dir)} {shlex.quote(dir_name)}"

        return f"{level_env}tar {extra}{exclude_cmd} -c{opt}f {shlex.quote(full_dest)} -C {shlex.quote(source_path)} ."

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
        """Generate special tar command for TGZ/TBZ2/TXZ formats without root"""
        source_path = self._resolve_source_path()
        temp_dir = os.path.join(os.path.dirname(source_path), f"temp_{base_name}_{self.format}")

        patterns = self.parse_exclude_patterns()
        exclude_cmd = " ".join([f'--exclude={shlex.quote(p)}' for p in patterns]) if patterns else ""

        q_temp = shlex.quote(temp_dir)
        q_src = shlex.quote(source_path)
        q_dest = shlex.quote(full_dest)
        level_env = self._get_tar_level_env()
        extra = f"{_TAR_LONG_FLAGS[self.format]} " if self.format in _TAR_LONG_FLAGS else ""
        return f"""
            mkdir -p {q_temp} &&
            cp -r {q_src}/* {q_temp}/ &&
            {level_env}tar {extra}{exclude_cmd} -c{opt}f {q_dest} -C {q_temp} . &&
            rm -rf {q_temp}
        """

    def compress(self) -> ProcessResult:
        """Execute the compression process"""
        # Seeded so the `finally` below always has a result to record, including
        # on the path where `handle_error` re-raises.
        result = ProcessResult(False, "Compression did not run")
        try:
            self._start_time = datetime.now()
            UI.print_header("Compression Process Started")
            if not self.validate():
                return result

            if self.is_glob_pattern:
                result = self._compress_glob_pattern()
                return result

            source_size = FileUtils.get_path_size(self.source)
            self.stats.original_size = source_size
            self.stats.file_count = FileUtils.count_files(self.source)
            start_time = self._start_time
            self.source = FileUtils.adjust_path(self.source)

            self._print_configuration(source_size)
            self.prepare_destination()

            command = self.get_compression_command()
            result = CommandExecutor.run(command, self.verbose, self.fail_on_error)

            if result.success:
                self._print_results(start_time, source_size)
                self._compute_checksum()

            return result

        except (OSError, ValueError, ValidationError, CompressError, CommandError) as e:
            return self.handle_error(e, "Compression")
        finally:
            self._record_stats(result.success)
            self._cleanup_temp_directory()

    def _print_configuration(self, source_size: int) -> None:
        """Print compression configuration details"""
        UI.print_section("Configuration")
        UI.print_kv("Source", self.source)
        UI.print_kv("Format", self.format)
        UI.print_kv("Include Root", self.include_root)
        UI.print_kv("Source Size", FileUtils.get_size(source_size))
        UI.print_kv("Initial Directory", os.getcwd())
        if self.exclude:
            UI.print_kv("Exclude Pattern", self.exclude)

    def _print_results(self, start_time: datetime, source_size: int) -> None:
        """Print compression results"""
        duration = (datetime.now() - start_time).total_seconds()

        if self.output_path and os.path.exists(self.output_path):
            compressed_size = os.path.getsize(self.output_path)
            ratio = (1 - (compressed_size / source_size)) * 100 if source_size > 0 else 0

            UI.print_section("Compression Results")
            UI.print_kv("Original Size", FileUtils.get_size(source_size))
            UI.print_kv("Compressed Size", FileUtils.get_size(compressed_size))
            UI.print_kv("Compression Ratio", f"{ratio:.1f}%")
            UI.print_kv("Duration", f"{duration:.2f} seconds")

    def _compress_glob_pattern(self) -> ProcessResult:
        """Compress files matched by glob pattern"""
        start_time = self._start_time
        source_size = sum(os.path.getsize(f) for f in self.matched_files if os.path.exists(f))
        self.stats.original_size = source_size
        self.stats.file_count = len(self.matched_files)

        temp_base = tempfile.gettempdir()
        self.temp_dir = os.path.join(temp_base, f"compress_glob_{os.getpid()}")

        UI.print_section("Preparing Files")
        UI.print_kv("Creating temporary directory", self.temp_dir)
        UI.print_bullet(f"Copying {len(self.matched_files)} matched file(s)")
        UI.print_kv("Preserve structure", self.preserve_glob_structure)
        if self.strip_prefix:
            UI.print_kv("Strip prefix", self.strip_prefix)

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
            self._compute_checksum()
            UI.print_success(f"Successfully compressed {len(self.matched_files)} file(s) matching pattern: {original_source}")

        return result

    def _record_stats(self, success: bool) -> None:
        """
        Collect the metrics exposed as action outputs and the job summary.

        Runs from a `finally`, so a run that failed validation or raised still
        reports the size it read and the time it spent rather than zeroes.
        """
        self.stats.success = success
        self.stats.duration = (datetime.now() - self._start_time).total_seconds()
        if success:
            self.stats.output_path = self.output_path
            self.stats.checksum = self.checksum
            if self.output_path and os.path.exists(self.output_path):
                self.stats.compressed_size = os.path.getsize(self.output_path)

    def _compute_checksum(self) -> None:
        """Compute SHA256 checksum of the output archive"""
        if self.output_path and os.path.exists(self.output_path):
            self.checksum = FileUtils.sha256_of_file(self.output_path)

    def _cleanup_temp_directory(self) -> None:
        """Clean up temporary directory created for glob pattern compression"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                if self.verbose:
                    logger.debug(f"Cleaned up temporary directory: {self.temp_dir}")
            except OSError as e:
                logger.warning(f"Failed to clean up temporary directory: {str(e)}")


def compress(config: AppConfig) -> OperationStats:
    """
    Main compression function called from the action.

    Args:
        config: Application configuration

    Returns:
        Operation metrics. Falsy, with an empty `output_path`, on failure.
    """
    compressor = Compressor(config)
    compressor.compress()
    return compressor.stats
