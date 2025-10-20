from datetime import datetime
import os
import sys
from typing import Optional, List, Dict, Tuple
from utils import (
    UI, FileUtils, CommandExecutor, CompressionFormat,
    logger, ProcessResult, BaseProcessor
)

class Compressor(BaseProcessor):
    """
    Handles file/directory compression operations
    
    This class provides functionality to compress directories or files using
    different compression formats (zip, tar, tgz, tbz2) with various options
    like preserving root directory structure or excluding specific files.
    Supports glob patterns for matching multiple files (e.g., **/*.doc).
    """
    def __init__(self, source: str, format: str, include_root: str):
        """
        Initialize Compressor with required parameters
        
        Args:
            source: Source directory, file, or glob pattern to compress
            format: Compression format (zip, tar, tgz, tbz2)
            include_root: Whether to include root directory in compressed file ("true" or "false")
        """
        super().__init__()
        self.source = source
        self.format = format
        self.include_root = include_root.lower() == "true"
        self.is_glob_pattern = False
        self.matched_files = []
        self.temp_dir = None

    def validate(self) -> bool:
        """
        Validate that source path exists or glob pattern matches files
        
        Also handles GitHub Actions runner path conversion for Docker container compatibility.
        Supports glob patterns like **/*.doc to match multiple files.
        
        Returns:
            True if source path is valid or pattern matches files, False otherwise
        """
        # Strip leading/trailing whitespace from path
        self.source = self.source.strip()
        
        # Convert GitHub Actions runner path to Docker container path
        # This converts paths like /home/runner/work/repo/repo to /github/workspace
        if self.source.startswith('/home/runner/work/'):
            self.source = '/github/workspace'
        
        # Check if source is a glob pattern
        if FileUtils.is_glob_pattern(self.source):
            self.is_glob_pattern = True
            UI.print_section("Glob Pattern Detected")
            print(f"  • Pattern: {self.source}")
            
            # Find files matching the pattern
            self.matched_files = FileUtils.find_files_by_pattern(self.source)
            
            if not self.matched_files:
                error_msg = f"No files matched the pattern: {self.source}"
                if self.fail_on_error:
                    UI.print_error(error_msg)
                    sys.exit(1)
                logger.logger.warning(error_msg)
                return False
            
            print(f"  • Matched {len(self.matched_files)} file(s)")
            if self.verbose:
                for i, file_path in enumerate(self.matched_files[:10], 1):
                    print(f"    {i}. {file_path}")
                if len(self.matched_files) > 10:
                    print(f"    ... and {len(self.matched_files) - 10} more files")
            
            return True
        
        # Regular path validation
        return self.validate_path(self.source, "Source path")

    def get_compression_command(self) -> str:
        """
        Generate the appropriate compression command based on format
        
        Determines output destination and calls format-specific command generator.
        
        Returns:
            Shell command string to execute compression
        """
        base_name = self.destfilename or os.path.basename(self.source)
        extension = f".{self.format}"
        full_dest = self._determine_destination_path(base_name, extension)

        if self.format == CompressionFormat.ZIP.value:
            return self._get_zip_command(full_dest, base_name)
        return self._get_tar_command(full_dest, base_name)

    def _determine_destination_path(self, base_name: str, extension: str) -> str:
        """
        Determine the full destination path for the compressed file
        
        Handles both custom destination paths and default paths based on includeRoot option.
        
        Args:
            base_name: Base filename for the output
            extension: File extension (.zip, .tar, etc.)
            
        Returns:
            Absolute path to the destination file
        """
        if self.dest and self.dest != os.getcwd():
            return os.path.abspath(os.path.join(self.dest, f"{base_name}{extension}"))
        
        # Use default output location based on includeRoot setting
        # - If includeRoot=true: Place file next to the source directory
        # - If includeRoot=false: Place file inside the source directory
        output_dir = os.path.dirname(self.source) if self.include_root else self.source
        return os.path.join(output_dir, f"{base_name}{extension}")

    def _get_zip_command(self, full_dest: str, base_name: str) -> str:
        """
        Generate zip compression command
        
        Creates a zip command with proper handling of:
        - Source path
        - Exclusion patterns
        - Root directory inclusion/exclusion
        
        Args:
            full_dest: Full destination path for the output file
            base_name: Base name of the output file
            
        Returns:
            Shell command string for zip compression
        """
        source_path = os.path.abspath(self.source)
        source_path = os.getcwd() if source_path == '/github/workspace' else source_path
        exclude_cmd = self._process_zip_exclude_patterns(source_path)
        
        if self.include_root:
            # When including root directory, we cd to parent dir and zip the source dir
            parent_dir = os.path.dirname(source_path)
            dir_name = os.path.basename(source_path)
            return f"cd {parent_dir} && zip -r {full_dest} {dir_name} {exclude_cmd}"
        
        # When not including root directory, we cd into source dir and zip its contents
        return f"cd {source_path} && zip -r {full_dest} . {exclude_cmd}"

    def _process_zip_exclude_patterns(self, source_path: str) -> str:
        """
        Process exclusion patterns for zip command
        
        Handles parsing of exclude patterns from space-separated string to
        properly formatted zip exclusion parameters.
        
        Args:
            source_path: Absolute path to the source directory
            
        Returns:
            Formatted zip exclusion command string (e.g., -x "pattern1" -x "pattern2")
        """
        if not self.exclude:
            return ""
            
        patterns = [pattern.strip() for pattern in self.exclude.split() if pattern.strip()]
        if not patterns:
            return ""
            
        dir_name = os.path.basename(source_path)
        processed_patterns = self._format_zip_exclude_patterns(patterns, source_path, dir_name)
        return " ".join([f'-x "{p}"' for p in processed_patterns])

    def _format_zip_exclude_patterns(self, patterns: List[str], source_path: str, dir_name: str) -> List[str]:
        """
        Format exclude patterns for zip command based on includeRoot setting
        
        This is a crucial method that ensures exclude patterns work correctly
        regardless of whether we're including the root directory or not.
        
        Args:
            patterns: List of raw exclusion patterns
            source_path: Absolute path to source directory
            dir_name: Name of the source directory
            
        Returns:
            List of properly formatted exclusion patterns
        """
        processed_patterns = []
        
        for pattern in patterns:
            if self.include_root:
                processed_patterns.extend(self._format_pattern_with_root(pattern, source_path, dir_name))
            else:
                processed_patterns.extend(self._format_pattern_without_root(pattern, source_path))
                
        return processed_patterns

    def _format_pattern_with_root(self, pattern: str, source_path: str, dir_name: str) -> List[str]:
        """
        Format exclusion pattern when includeRoot is true
        
        Handles different cases like:
        - Pattern already including directory prefix
        - Directory patterns (need to exclude content and directory itself)
        - Regular file patterns
        
        Args:
            pattern: Raw exclusion pattern
            source_path: Absolute path to source directory
            dir_name: Name of the source directory
            
        Returns:
            List of formatted patterns for zip command
        """
        # Pattern already includes directory prefix
        if pattern.startswith(f"{dir_name}/") or pattern == dir_name:
            return [pattern]
            
        # Directory without trailing slash
        if os.path.isdir(os.path.join(source_path, pattern)) and not pattern.endswith('/*'):
            if pattern.endswith('/'):
                return [f"{dir_name}/{pattern}*"]
            return [f"{dir_name}/{pattern}/*", f"{dir_name}/{pattern}/"]
            
        # Regular file or pattern
        return [f"{dir_name}/{pattern}"]

    def _format_pattern_without_root(self, pattern: str, source_path: str) -> List[str]:
        """
        Format exclusion pattern when includeRoot is false
        
        Handles the case when we're compressing the contents directly without
        the parent directory name.
        
        Args:
            pattern: Raw exclusion pattern
            source_path: Absolute path to source directory
            
        Returns:
            List of formatted patterns for zip command
        """
        if os.path.isdir(os.path.join(source_path, pattern)) and not pattern.endswith('/*'):
            return [f"{pattern}/*", f"{pattern}/"]
        return [pattern]

    def _get_tar_command(self, full_dest: str, base_name: str) -> str:
        """
        Generate tar compression command
        
        Handles different tar formats (tar, tgz, tbz2) and options like
        including/excluding root directory.
        
        Args:
            full_dest: Full destination path for the output file
            base_name: Base name of the output file
            
        Returns:
            Shell command string for tar compression
        """
        source_path = os.path.abspath(self.source)
        source_path = os.getcwd() if source_path == '/github/workspace' else source_path
        
        tar_options = {
            CompressionFormat.TAR.value: "",
            CompressionFormat.TGZ.value: "z",
            CompressionFormat.TBZ2.value: "j"
        }
        opt = tar_options.get(self.format, "")
        
        # Special case for TGZ/TBZ2 without root
        # These formats require a special approach when not including root directory
        if self.format in [CompressionFormat.TGZ.value, CompressionFormat.TBZ2.value] and not self.include_root:
            return self._get_special_tar_command(full_dest, base_name, opt)
        
        exclude_cmd = self._process_tar_exclude_patterns(source_path)
        
        if self.include_root:
            # When including root, use the parent directory as base and specify the dir name
            parent_dir = os.path.dirname(source_path)
            dir_name = os.path.basename(source_path)
            return f"tar {exclude_cmd} -c{opt}f {full_dest} -C {parent_dir} {dir_name}"
        
        # When not including root, use the source directory as base and compress everything
        return f"tar {exclude_cmd} -c{opt}f {full_dest} -C {source_path} ."

    def _process_tar_exclude_patterns(self, source_path: str) -> str:
        """
        Process exclusion patterns for tar command
        
        Tar uses a different exclusion syntax than zip, so we need to handle
        patterns differently.
        
        Args:
            source_path: Absolute path to source directory
            
        Returns:
            Formatted tar exclusion command string
        """
        if not self.exclude:
            return ""
            
        patterns = [pattern.strip() for pattern in self.exclude.split() if pattern.strip()]
        if not patterns:
            return ""
            
        dir_name = os.path.basename(source_path)
        processed_patterns = []
        
        for pattern in patterns:
            if self.include_root and not pattern.startswith(dir_name):
                processed_patterns.append(f"{dir_name}/{pattern}")
            else:
                processed_patterns.append(pattern)
        
        return " ".join([f'--exclude="{p}"' for p in processed_patterns])

    def _get_special_tar_command(self, full_dest: str, base_name: str, opt: str) -> str:
        """
        Generate special tar command for TGZ/TBZ2 formats without root
        
        This creates a temporary directory, copies files there, compresses them,
        and then cleans up. This approach is needed for some tar formats when
        not including the root directory.
        
        Args:
            full_dest: Full destination path for output file
            base_name: Base name of output file
            opt: Tar format option (z for gzip, j for bzip2)
            
        Returns:
            Shell command string for special tar compression
        """
        source_path = os.path.abspath(self.source)
        temp_dir = os.path.join(os.path.dirname(source_path), f"temp_{base_name}_{self.format}")
        exclude_cmd = self._process_special_tar_exclude_patterns()

        return f"""
            mkdir -p {temp_dir} &&
            cp -r {source_path}/* {temp_dir}/ &&
            tar {exclude_cmd} -c{opt}f {full_dest} -C {temp_dir} . &&
            rm -rf {temp_dir}
        """

    def _process_special_tar_exclude_patterns(self) -> str:
        """
        Process exclusion patterns for special tar command
        
        In the special tar case, exclusion patterns are relative to the
        temporary directory we create.
        
        Returns:
            Formatted tar exclusion command string
        """
        if not self.exclude:
            return ""
            
        patterns = [pattern.strip() for pattern in self.exclude.split() if pattern.strip()]
        if not patterns:
            return ""
            
        return " ".join([f'--exclude="{p}"' for p in patterns])

    def compress(self) -> ProcessResult:
        """
        Execute the compression process
        
        This is the main method that orchestrates the entire compression process:
        1. Validates the source (including glob pattern matching)
        2. Prepares the environment and configuration
        3. If glob pattern: copies matched files to temp directory
        4. Executes the compression command
        5. Cleans up temporary files if needed
        6. Handles results and errors
        
        Returns:
            ProcessResult object with success status and message
        """
        try:
            UI.print_header("Compression Process Started")
            if not self.validate():
                return ProcessResult(False, "Validation failed")

            # Handle glob pattern by creating temp directory with matched files
            if self.is_glob_pattern:
                return self._compress_glob_pattern()
            
            # Regular compression flow
            source_size = self._get_source_size()
            start_time = datetime.now()
            self.source = FileUtils.adjust_path(self.source)
            
            self._print_configuration(source_size)
            self.prepare_destination()
            
            command = self.get_compression_command()
            result = CommandExecutor.run(command, self.verbose)
            
            if result.success:
                self._print_results(start_time, source_size)
            
            return result
            
        except Exception as e:
            return self.handle_error(e, "Compression")
        finally:
            # Clean up temporary directory if it was created
            self._cleanup_temp_directory()

    def _get_source_size(self) -> int:
        """
        Get size of source directory or file
        
        Handles both directory and file size calculations.
        
        Returns:
            Size in bytes of the source
        """
        if os.path.isdir(self.source):
            return FileUtils.get_directory_size(self.source)
        return os.path.getsize(self.source)

    def _print_configuration(self, source_size: int) -> None:
        """
        Print compression configuration details
        
        Displays all relevant configuration settings to the user.
        
        Args:
            source_size: Size in bytes of the source
        """
        UI.print_section("Configuration")
        print(f"  • Source: {self.source}")
        print(f"  • Format: {self.format}")
        print(f"  • Include Root: {self.include_root}")
        print(f"  • Source Size: {FileUtils.get_size(source_size)}")
        print(f"  • Initial Directory: {os.getcwd()}")
        if self.exclude:
            print(f"  • Exclude Pattern: {self.exclude}")

    def _print_results(self, start_time: datetime, source_size: int) -> None:
        """
        Print compression results
        
        Shows statistics about the compression operation, including size
        reduction and performance metrics.
        
        Args:
            start_time: Time when compression started
            source_size: Size in bytes of the source
        """
        end_time = datetime.now()
        duration = end_time - start_time
        
        if os.path.exists(self.dest):
            compressed_size = os.path.getsize(self.dest)
            compression_ratio = (1 - (compressed_size / source_size)) * 100 if source_size > 0 else 0
            
            UI.print_section("Compression Results")
            print(f"  • Original Size: {FileUtils.get_size(source_size)}")
            print(f"  • Compressed Size: {FileUtils.get_size(compressed_size)}")
            print(f"  • Compression Ratio: {compression_ratio:.1f}%")
            print(f"  • Duration: {duration.total_seconds():.2f} seconds")

    def _compress_glob_pattern(self) -> ProcessResult:
        """
        Compress files matched by glob pattern
        
        Creates a temporary directory, copies matched files, compresses them,
        and cleans up the temporary directory.
        
        Returns:
            ProcessResult object with success status and message
        """
        import tempfile
        
        start_time = datetime.now()
        
        # Calculate total size of matched files
        source_size = sum(os.path.getsize(f) for f in self.matched_files if os.path.exists(f))
        
        # Create temporary directory for matched files
        temp_base = tempfile.gettempdir()
        self.temp_dir = os.path.join(temp_base, f"compress_glob_{os.getpid()}")
        
        UI.print_section("Preparing Files")
        print(f"  • Creating temporary directory: {self.temp_dir}")
        print(f"  • Copying {len(self.matched_files)} matched file(s)")
        
        # Copy matched files to temp directory (flattened)
        FileUtils.copy_files_to_temp_directory(
            self.matched_files, 
            self.temp_dir, 
            preserve_structure=False
        )
        
        # Update source to temp directory
        original_source = self.source
        self.source = self.temp_dir
        
        # Print configuration
        self._print_configuration(source_size)
        self.prepare_destination()
        
        # Execute compression
        command = self.get_compression_command()
        result = CommandExecutor.run(command, self.verbose)
        
        if result.success:
            self._print_results(start_time, source_size)
            UI.print_success(f"Successfully compressed {len(self.matched_files)} file(s) matching pattern: {original_source}")
        
        return result

    def _cleanup_temp_directory(self) -> None:
        """
        Clean up temporary directory created for glob pattern compression
        """
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                import shutil
                shutil.rmtree(self.temp_dir)
                if self.verbose:
                    logger.logger.debug(f"Cleaned up temporary directory: {self.temp_dir}")
            except Exception as e:
                logger.logger.warning(f"Failed to clean up temporary directory: {str(e)}")

def compress(source: str, format: str, include_root: str) -> bool:
    """
    Main compression function that's called from the action
    
    Creates a Compressor instance and executes the compression.
    
    Args:
        source: Source directory or file to compress
        format: Compression format (zip, tar, tgz, tbz2)
        include_root: Whether to include root directory ("true" or "false")
        
    Returns:
        True if compression succeeded, False otherwise
    """
    compressor = Compressor(source, format, include_root)
    result = compressor.compress()
    return result.success
