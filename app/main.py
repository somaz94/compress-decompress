import os
import sys
import summary
from config import CompressionFormat, AppConfig
from masking import register_secret
from stats import OperationStats
from ui import UI
from app_logger import logger
from exceptions import CompressError, ValidationError
from compress import compress
from decompress import decompress


class ActionRunner:
    """
    Main action runner for compression/decompression operations

    Handles execution of compression and decompression operations
    based on environment variables provided by the GitHub Action.
    """
    def __init__(self, config: AppConfig):
        self.config = config

    def validate_inputs(self) -> None:
        """Validate required inputs are provided and valid"""
        if not self.config.command:
            raise ValidationError("Command is required")
        if not self.config.source:
            raise ValidationError("Source is required")
        if not self.config.format:
            raise ValidationError("Format is required")
        if self.config.format not in CompressionFormat.list():
            raise ValidationError(
                f"Invalid format: {self.config.format}. "
                f"Supported formats: {', '.join(CompressionFormat.list())}"
            )

    def print_configuration(self) -> None:
        """Print action configuration"""
        UI.print_header("Compress/Decompress Action")
        UI.print_section("Environment Configuration")

        UI.print_kv("Command", self.config.command)
        UI.print_kv("Source", self.config.source)
        UI.print_kv("Format", self.config.format)
        UI.print_kv("Include Root", self.config.include_root)
        UI.print_kv("Preserve Glob Structure", self.config.preserve_glob_structure)
        if self.config.strip_prefix:
            UI.print_kv("Strip Prefix", self.config.strip_prefix)
        UI.print_kv("Verbose", self.config.verbose)
        UI.print_kv("Fail on Error", self.config.fail_on_error)

        if self.config.dest:
            UI.print_kv("Destination", self.config.dest)
        if self.config.destfilename:
            UI.print_kv("Destination Filename", self.config.destfilename)
        if self.config.exclude:
            UI.print_kv("Exclude Pattern", self.config.exclude)
        if self.config.password:
            UI.print_kv("Password", "***")
        if self.config.verify_checksum:
            UI.print_kv("Verify Checksum", self.config.verify_checksum)
        if self.config.command == "decompress":
            UI.print_kv("Path Traversal Check", self.config.path_traversal_check)

    def execute_command(self) -> None:
        """Execute the appropriate compression or decompression command"""
        if self.config.command == "compress":
            result = compress(self.config)
        elif self.config.command == "decompress":
            result = decompress(self.config)
        else:
            raise ValidationError(
                f"Invalid command: {self.config.command}. "
                f"Supported commands: compress, decompress"
            )
        self._publish_results(result)

    def _publish_results(self, result: OperationStats) -> None:
        """Expose the run as action outputs and as a job summary"""
        if result.checksum:
            self._set_output("checksum", result.checksum)
        if result.output_path:
            self._set_output("file_path", result.output_path)
        self._set_output("original_size", str(result.original_size))
        self._set_output("compressed_size", str(result.compressed_size))
        self._set_output("compression_ratio", f"{result.compression_ratio:.1f}")
        self._set_output("file_count", str(result.file_count))
        self._set_output("duration", f"{result.duration:.2f}")
        summary.write(result, self.config.step_summary)

    @staticmethod
    def _set_output(name: str, value: str) -> None:
        """Write output to GITHUB_OUTPUT for use in subsequent steps"""
        github_output = os.getenv("GITHUB_OUTPUT")
        if github_output:
            with open(github_output, "a") as f:
                f.write(f"{name}={value}\n")

    def register_secrets(self) -> None:
        """
        Keep the password out of the log.

        `::add-mask::` covers everything GitHub renders afterwards; the local
        registry covers the command strings this action prints itself, which
        the workflow-level masking never sees on a `fail_on_error: false` run
        that keeps going.
        """
        if self.config.password:
            register_secret(self.config.password)
            print(f"::add-mask::{self.config.password}")

    def run(self) -> None:
        """Main execution flow: validate, configure, execute"""
        self.register_secrets()
        self.validate_inputs()
        self.print_configuration()
        logger.set_verbose(self.config.verbose)
        self.execute_command()


def main():
    """
    Main entry point for the application.
    sys.exit() is called only here to keep exception flow clean.
    """
    try:
        config = AppConfig.from_env()
        runner = ActionRunner(config)
        runner.run()
    except CompressError as e:
        UI.print_error(str(e))
        sys.exit(1)
    except Exception as e:
        UI.print_error(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
