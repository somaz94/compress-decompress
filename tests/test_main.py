import pytest
from unittest.mock import patch, MagicMock
from config import AppConfig
from main import ActionRunner, main
from exceptions import ValidationError, CompressError


class TestActionRunnerValidation:
    def test_missing_command(self, make_config):
        runner = ActionRunner(make_config(command=""))
        with pytest.raises(ValidationError, match="Command is required"):
            runner.validate_inputs()

    def test_missing_source(self, make_config):
        runner = ActionRunner(make_config(command="compress", source=""))
        with pytest.raises(ValidationError, match="Source is required"):
            runner.validate_inputs()

    def test_missing_format(self, make_config):
        runner = ActionRunner(make_config(command="compress", source="./src", format=""))
        with pytest.raises(ValidationError, match="Format is required"):
            runner.validate_inputs()

    def test_invalid_format(self, make_config):
        runner = ActionRunner(make_config(command="compress", source="./src", format="rar"))
        with pytest.raises(ValidationError, match="Invalid format"):
            runner.validate_inputs()

    def test_valid_inputs(self, make_config):
        runner = ActionRunner(make_config(
            command="compress", source="./src", format="zip"
        ))
        runner.validate_inputs()  # Should not raise

    def test_invalid_command(self, make_config, tmp_path):
        runner = ActionRunner(make_config(
            command="invalid", source=str(tmp_path), format="zip"
        ))
        runner.validate_inputs()  # Passes validation
        with pytest.raises(ValidationError, match="Invalid command"):
            runner.execute_command()

    def test_all_formats_valid(self, make_config):
        for fmt in ["zip", "tar", "tgz", "tbz2"]:
            runner = ActionRunner(make_config(
                command="compress", source="./src", format=fmt
            ))
            runner.validate_inputs()  # Should not raise


class TestActionRunnerConfiguration:
    def test_print_configuration(self, make_config, capsys):
        runner = ActionRunner(make_config(
            command="compress", source="./src", format="zip",
            dest="/output", exclude="*.log"
        ))
        runner.print_configuration()
        output = capsys.readouterr().out
        assert "compress" in output
        assert "./src" in output
        assert "zip" in output
        assert "/output" in output
        assert "*.log" in output

    def test_print_configuration_all_optional_fields(self, make_config, capsys):
        runner = ActionRunner(make_config(
            command="compress", source="./src", format="zip",
            dest="/output", destfilename="my_archive",
            exclude="*.log", strip_prefix="/prefix",
        ))
        runner.print_configuration()
        output = capsys.readouterr().out
        assert "Strip Prefix" in output
        assert "/prefix" in output
        assert "Destination Filename" in output
        assert "my_archive" in output
        assert "Destination" in output
        assert "Exclude Pattern" in output


class TestActionRunnerExecute:
    def test_execute_compress(self, make_config, tmp_source, tmp_path):
        dest = tmp_path / "output"
        dest.mkdir()
        runner = ActionRunner(make_config(
            command="compress", source=str(tmp_source),
            format="zip", dest=str(dest),
        ))
        runner.execute_command()  # Should not raise

    def test_execute_decompress(self, make_config, tmp_archive_zip, tmp_path):
        dest = tmp_path / "extracted"
        dest.mkdir()
        runner = ActionRunner(make_config(
            command="decompress", source=tmp_archive_zip,
            format="zip", dest=str(dest),
        ))
        runner.execute_command()  # Should not raise

    def test_run_method(self, make_config, tmp_source, tmp_path):
        dest = tmp_path / "output"
        dest.mkdir()
        runner = ActionRunner(make_config(
            command="compress", source=str(tmp_source),
            format="zip", dest=str(dest),
        ))
        runner.run()  # Should not raise


class TestMainFunction:
    def test_main_compress_error(self, monkeypatch):
        monkeypatch.setenv("INPUT_COMMAND", "compress")
        monkeypatch.setenv("INPUT_SOURCE", "")
        monkeypatch.setenv("INPUT_FORMAT", "zip")
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

    def test_main_unexpected_error(self, monkeypatch):
        monkeypatch.setenv("INPUT_COMMAND", "compress")
        monkeypatch.setenv("INPUT_SOURCE", "/some/path")
        monkeypatch.setenv("INPUT_FORMAT", "zip")
        with patch('main.ActionRunner.run', side_effect=RuntimeError("unexpected")):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
