import os
import sys
from config import CompressionFormat, AppConfig
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

    def execute_command(self) -> None:
        """Execute the appropriate compression or decompression command"""
        if self.config.command == "compress":
            output_path, checksum = compress(self.config)
            if checksum:
                self._set_output("checksum", checksum)
        elif self.config.command == "decompress":
            output_path = decompress(self.config)
        else:
            raise ValidationError(
                f"Invalid command: {self.config.command}. "
                f"Supported commands: compress, decompress"
            )
        if output_path:
            self._set_output("file_path", output_path)

    @staticmethod
    def _set_output(name: str, value: str) -> None:
        """Write output to GITHUB_OUTPUT for use in subsequent steps"""
        github_output = os.getenv("GITHUB_OUTPUT")
        if github_output:
            with open(github_output, "a") as f:
                f.write(f"{name}={value}\n")

    def run(self) -> None:
        """Main execution flow: validate, configure, execute"""
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
