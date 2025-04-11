from datetime import datetime
import os
import sys
from typing import Optional
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
        # Example: /home/runner/work/repo/repo -> /github/workspace
        if self.source.startswith('/home/runner/work/'):
            repo_path = '/'.join(self.source.split('/')[-2:])  # 'compress-decompress/compress-decompress'
            self.source = f'/github/workspace'
        
        return self.validate_path(self.source, "Source path")

    def get_compression_command(self) -> str:
        """Generate appropriate compression command based on format"""
        base_name = self.destfilename or os.path.basename(self.source)
        extension = f".{self.format}"
        
        # Convert destination path to absolute path if specified
        if self.dest and self.dest != os.getcwd():
            full_dest = os.path.abspath(os.path.join(self.dest, f"{base_name}{extension}"))
        else:
            # Maintain existing behavior for output directory
            output_dir = os.path.dirname(self.source) if self.include_root else self.source
            full_dest = os.path.join(output_dir, f"{base_name}{extension}")

        if self.format == CompressionFormat.ZIP.value:
            return self._get_zip_command(full_dest, base_name)
        return self._get_tar_command(full_dest, base_name)

    def _get_zip_command(self, full_dest: str, base_name: str) -> str:
        """Generate zip compression command"""
        source_path = os.path.abspath(self.source)

        # Handle exclusion - zip requires specific path patterns
        exclude_cmd = ""
        if self.exclude:
            # For zip, the exclude pattern must match the full path inside the archive
            # Split by spaces, process each pattern
            patterns = [pattern.strip() for pattern in self.exclude.split() if pattern.strip()]
            if patterns:
                dir_name = os.path.basename(source_path)
                # For each pattern, we need to prefix it with the directory name when using includeRoot
                if self.include_root:
                    exclude_patterns = []
                    for pattern in patterns:
                        # If pattern doesn't already start with the dir name, prefix it
                        if not pattern.startswith(f"{dir_name}/") and not pattern == dir_name:
                            exclude_patterns.append(f"{dir_name}/{pattern}")
                        else:
                            exclude_patterns.append(pattern)
                    exclude_cmd = " ".join([f'-x "{p}"' for p in exclude_patterns])
                else:
                    # When not including root, patterns are relative to source path
                    exclude_cmd = " ".join([f'-x "{p}"' for p in patterns])
        
        # Handle GitHub Actions environment path
        # Convert /github/workspace to actual working directory if needed
        if source_path == '/github/workspace':
            source_path = os.getcwd()
        
        if self.include_root:
            # Include the root directory in the archive
            parent_dir = os.path.dirname(source_path)
            dir_name = os.path.basename(source_path)
            return f"cd {parent_dir} && zip -r {full_dest} {dir_name} {exclude_cmd}"
        # Archive contents only, without root directory
        return f"cd {source_path} && zip -r {full_dest} . {exclude_cmd}"

    def _get_tar_command(self, full_dest: str, base_name: str) -> str:
        """Generate tar compression command"""
        tar_options = {
            CompressionFormat.TAR.value: "",
            CompressionFormat.TGZ.value: "z",
            CompressionFormat.TBZ2.value: "j"
        }
        
        source_path = os.path.abspath(self.source)

        # Handle exclusion - tar uses different pattern syntax
        exclude_cmd = ""
        if self.exclude:
            # Split by spaces, process each pattern
            patterns = [pattern.strip() for pattern in self.exclude.split() if pattern.strip()]
            if patterns:
                # Tar exclude patterns work differently and need full paths or patterns
                exclude_cmd = " ".join([f'--exclude="{p}"' for p in patterns])
        
        # Handle GitHub Actions environment path
        # Convert /github/workspace to actual working directory if needed
        if source_path == '/github/workspace':
            source_path = os.getcwd()
        
        # Special handling for TGZ/TBZ2 formats when not including root
        if self.format in [CompressionFormat.TGZ.value, CompressionFormat.TBZ2.value] and not self.include_root:
            return self._get_special_tar_command(full_dest, base_name, tar_options[self.format])
        
        opt = tar_options.get(self.format, "")
        if self.include_root:
            # Include the root directory in the archive
            parent_dir = os.path.dirname(source_path)
            dir_name = os.path.basename(source_path)
            return f"tar {exclude_cmd} -c{opt}f {full_dest} -C {parent_dir} {dir_name}"
        # Archive contents only, without root directory
        return f"tar {exclude_cmd} -c{opt}f {full_dest} -C {source_path} ."

    def _get_special_tar_command(self, full_dest: str, base_name: str, opt: str) -> str:
        """Generate special tar command for TGZ/TBZ2 formats without root"""
        source_path = os.path.abspath(self.source)
        temp_dir = os.path.join(os.path.dirname(source_path), f"temp_{base_name}_{self.format}")

        # Handle exclusion
        exclude = "--exclude '" + self.exclude + "'" if self.exclude else ""

        # Create temporary directory, copy files, create archive, then cleanup
        return f"""
            mkdir -p {temp_dir} &&
            cp -r {source_path}/* {temp_dir}/ &&
            tar -c{opt}f {exclude} {full_dest} -C {temp_dir} . &&
            rm -rf {temp_dir}
        """

    def compress(self) -> ProcessResult:
        """Execute compression process"""
        try:
            UI.print_header("Compression Process Started")
            if not self.validate():
                return ProcessResult(False, "Validation failed")

            source_size = (FileUtils.get_directory_size(self.source) 
                         if os.path.isdir(self.source) 
                         else os.path.getsize(self.source))
            
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
