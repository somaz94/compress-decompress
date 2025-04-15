from datetime import datetime
import os
import sys
from typing import Optional, List, Dict, Tuple
from utils import (
    UI, FileUtils, CommandExecutor, CompressionFormat,
    logger, ProcessResult, BaseProcessor
)

class Compressor(BaseProcessor):
    """Handles file/directory compression"""
    def __init__(self, source: str, format: str, include_root: str):
        super().__init__()
        self.source = source
        self.format = format
        self.include_root = include_root.lower() == "true"

    def validate(self) -> bool:
        """Validate source path exists"""
        # Strip leading/trailing whitespace from path
        self.source = self.source.strip()
        
        # Convert GitHub Actions runner path to Docker container path
        if self.source.startswith('/home/runner/work/'):
            self.source = '/github/workspace'
        
        return self.validate_path(self.source, "Source path")

    def get_compression_command(self) -> str:
        """Generate appropriate compression command based on format"""
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
        
        # Use default output location based on includeRoot setting
        output_dir = os.path.dirname(self.source) if self.include_root else self.source
        return os.path.join(output_dir, f"{base_name}{extension}")

    def _get_zip_command(self, full_dest: str, base_name: str) -> str:
        """Generate zip compression command"""
        source_path = os.path.abspath(self.source)
        source_path = os.getcwd() if source_path == '/github/workspace' else source_path
        exclude_cmd = self._process_zip_exclude_patterns(source_path)
        
        if self.include_root:
            parent_dir = os.path.dirname(source_path)
            dir_name = os.path.basename(source_path)
            return f"cd {parent_dir} && zip -r {full_dest} {dir_name} {exclude_cmd}"
        
        return f"cd {source_path} && zip -r {full_dest} . {exclude_cmd}"

    def _process_zip_exclude_patterns(self, source_path: str) -> str:
        """Process exclusion patterns for zip command"""
        if not self.exclude:
            return ""
            
        patterns = [pattern.strip() for pattern in self.exclude.split() if pattern.strip()]
        if not patterns:
            return ""
            
        dir_name = os.path.basename(source_path)
        processed_patterns = self._format_zip_exclude_patterns(patterns, source_path, dir_name)
        return " ".join([f'-x "{p}"' for p in processed_patterns])

    def _format_zip_exclude_patterns(self, patterns: List[str], source_path: str, dir_name: str) -> List[str]:
        """Format exclude patterns for zip command based on includeRoot setting"""
        processed_patterns = []
        
        for pattern in patterns:
            if self.include_root:
                processed_patterns.extend(self._format_pattern_with_root(pattern, source_path, dir_name))
            else:
                processed_patterns.extend(self._format_pattern_without_root(pattern, source_path))
                
        return processed_patterns

    def _format_pattern_with_root(self, pattern: str, source_path: str, dir_name: str) -> List[str]:
        """Format exclusion pattern when includeRoot is true"""
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
        
        exclude_cmd = self._process_tar_exclude_patterns(source_path)
        
        if self.include_root:
            parent_dir = os.path.dirname(source_path)
            dir_name = os.path.basename(source_path)
            return f"tar {exclude_cmd} -c{opt}f {full_dest} -C {parent_dir} {dir_name}"
        
        return f"tar {exclude_cmd} -c{opt}f {full_dest} -C {source_path} ."

    def _process_tar_exclude_patterns(self, source_path: str) -> str:
        """Process exclusion patterns for tar command"""
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
        """Generate special tar command for TGZ/TBZ2 formats without root"""
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
        """Process exclusion patterns for special tar command"""
        if not self.exclude:
            return ""
            
        patterns = [pattern.strip() for pattern in self.exclude.split() if pattern.strip()]
        if not patterns:
            return ""
            
        return " ".join([f'--exclude="{p}"' for p in patterns])

    def compress(self) -> ProcessResult:
        """Execute compression process"""
        try:
            UI.print_header("Compression Process Started")
            if not self.validate():
                return ProcessResult(False, "Validation failed")

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

    def _get_source_size(self) -> int:
        """Get size of source directory or file"""
        if os.path.isdir(self.source):
            return FileUtils.get_directory_size(self.source)
        return os.path.getsize(self.source)

    def _print_configuration(self, source_size: int) -> None:
        """Print compression configuration details"""
        UI.print_section("Configuration")
        print(f"  • Source: {self.source}")
        print(f"  • Format: {self.format}")
        print(f"  • Include Root: {self.include_root}")
        print(f"  • Source Size: {FileUtils.get_size(source_size)}")
        print(f"  • Initial Directory: {os.getcwd()}")
        if self.exclude:
            print(f"  • Exclude Pattern: {self.exclude}")

    def _print_results(self, start_time: datetime, source_size: int) -> None:
        """Print compression results"""
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

def compress(source: str, format: str, include_root: str) -> bool:
    """Compress a file or directory"""
    compressor = Compressor(source, format, include_root)
    result = compressor.compress()
    return result.success
