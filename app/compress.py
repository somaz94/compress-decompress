from datetime import datetime
import os
import sys
from typing import Optional
from utils import (
    UI, FileUtils, CommandExecutor, CompressionFormat,
    logger, ProcessResult
)

class Compressor:
    def __init__(self, source: str, format: str, include_root: str):
        self.source = source
        self.format = format
        self.include_root = include_root.lower() == "true"
        self.dest = os.getenv("DEST", os.getenv("GITHUB_WORKSPACE", os.getcwd()))
        self.fail_on_error = os.getenv("FAIL_ON_ERROR", "true").lower() == "true"

    def validate(self) -> bool:
        if not os.path.exists(self.source):
            error_msg = f"Source path '{self.source}' does not exist"
            if self.fail_on_error:
                print_error(error_msg)
                sys.exit(1)
            logger.logger.warning(error_msg)
            return False
        return True

    def prepare_destination(self) -> None:
        if self.dest and not os.path.exists(self.dest):
            os.makedirs(self.dest)

    def get_compression_command(self) -> str:
        base_name = os.path.basename(self.source)
        extension = f".{self.format}"
        full_dest = os.path.join(
            self.dest if self.include_root else self.source,
            f"{base_name}{extension}"
        )

        if self.format == CompressionFormat.ZIP.value:
            return self._get_zip_command(full_dest, base_name)
        return self._get_tar_command(full_dest, base_name)

    def _get_zip_command(self, full_dest: str, base_name: str) -> str:
        if self.include_root:
            return f"cd {os.path.dirname(self.source)} && zip -r {full_dest} {base_name}"
        return f"cd {self.source} && zip -r {full_dest} ."

    def _get_tar_command(self, full_dest: str, base_name: str) -> str:
        tar_options = {
            CompressionFormat.TAR.value: "",
            CompressionFormat.TGZ.value: "z",
            CompressionFormat.TBZ2.value: "j"
        }
        
        if self.format in [CompressionFormat.TGZ.value, CompressionFormat.TBZ2.value] and not self.include_root:
            return self._get_special_tar_command(full_dest, base_name, tar_options[self.format])
        
        opt = tar_options.get(self.format, "")
        if self.include_root:
            return f"tar -c{opt}f {full_dest} -C {os.path.dirname(self.source)} {base_name}"
        return f"tar -c{opt}f {full_dest} -C {self.source} ."

    def _get_special_tar_command(self, full_dest: str, base_name: str, opt: str) -> str:
        temp_dir = os.path.join(os.path.dirname(self.source), f"temp_{base_name}_{self.format}")
        return f"""
            mkdir -p {temp_dir} &&
            cp -r {self.source}/* {temp_dir}/ &&
            tar -c{opt}f {full_dest} -C {temp_dir} . &&
            rm -rf {temp_dir}
        """

    def compress(self) -> ProcessResult:
        try:
            print_header("Compression Process Started")
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
            result = CommandExecutor.run(command)
            
            if result.success:
                self._print_results(start_time, source_size)
            
            return result
            
        except Exception as e:
            if self.fail_on_error:
                print_error(f"Compression failed: {str(e)}")
                sys.exit(1)
            logger.logger.warning(f"Compression warning: {str(e)}")
            return ProcessResult(False, str(e))

    def _print_configuration(self, source_size: int) -> None:
        print_section("Configuration")
        print(f"  • Source: {self.source}")
        print(f"  • Format: {self.format}")
        print(f"  • Include Root: {self.include_root}")
        print(f"  • Source Size: {FileUtils.get_size(source_size)}")
        print(f"  • Initial Directory: {os.getcwd()}")

    def _print_results(self, start_time: datetime, source_size: int) -> None:
        end_time = datetime.now()
        duration = end_time - start_time
        
        if os.path.exists(self.dest):
            compressed_size = os.path.getsize(self.dest)
            compression_ratio = (1 - (compressed_size / source_size)) * 100 if source_size > 0 else 0
            
            print_section("Compression Results")
            print(f"  • Original Size: {FileUtils.get_size(source_size)}")
            print(f"  • Compressed Size: {FileUtils.get_size(compressed_size)}")
            print(f"  • Compression Ratio: {compression_ratio:.1f}%")
            print(f"  • Duration: {duration.total_seconds():.2f} seconds")

def compress(source: str, format: str, include_root: str) -> bool:
    compressor = Compressor(source, format, include_root)
    result = compressor.compress()
    return result.success
