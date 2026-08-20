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
        for fmt in ["zip", "tar", "tgz", "tbz2", "txz"]:
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

    def test_print_configuration_security_fields(self, make_config, capsys):
        runner = ActionRunner(make_config(
            command="decompress", source="./a.zip", format="zip",
            password="example-password-1", verify_checksum="c" * 64,
        ))
        runner.print_configuration()
        output = capsys.readouterr().out
        assert "example-password-1" not in output
        assert "Password: ***" in output
        assert "Verify Checksum" in output
        assert "Path Traversal Check" in output


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


class TestActionOutputs:
    def _outputs(self, output_file):
        return dict(
            line.split("=", 1)
            for line in output_file.read_text().splitlines() if "=" in line
        )

    def test_compress_writes_every_output(self, make_config, tmp_source, tmp_path,
                                          monkeypatch):
        output_file = tmp_path / "outputs.txt"
        monkeypatch.setenv("GITHUB_OUTPUT", str(output_file))
        dest = tmp_path / "output"
        dest.mkdir()
        runner = ActionRunner(make_config(
            command="compress", source=str(tmp_source), format="zip", dest=str(dest),
        ))
        runner.execute_command()

        outputs = self._outputs(output_file)
        assert outputs["file_path"].endswith(".zip")
        assert len(outputs["checksum"]) == 64
        assert int(outputs["original_size"]) > 0
        assert int(outputs["compressed_size"]) > 0
        assert float(outputs["compression_ratio"])
        assert outputs["file_count"] == "3"
        assert float(outputs["duration"]) >= 0

    def test_decompress_writes_metric_outputs(self, make_config, tmp_archive_zip,
                                              tmp_path, monkeypatch):
        output_file = tmp_path / "outputs.txt"
        monkeypatch.setenv("GITHUB_OUTPUT", str(output_file))
        dest = tmp_path / "extracted"
        dest.mkdir()
        runner = ActionRunner(make_config(
            command="decompress", source=tmp_archive_zip, format="zip", dest=str(dest),
        ))
        runner.execute_command()

        outputs = self._outputs(output_file)
        assert outputs["file_path"] == str(dest)
        assert "checksum" not in outputs
        assert outputs["file_count"] == "3"

    def test_no_outputs_without_github_output(self, make_config, tmp_source, tmp_path,
                                              monkeypatch):
        monkeypatch.delenv("GITHUB_OUTPUT", raising=False)
        dest = tmp_path / "output"
        dest.mkdir()
        runner = ActionRunner(make_config(
            command="compress", source=str(tmp_source), format="zip", dest=str(dest),
        ))
        runner.execute_command()  # Should not raise


class TestJobSummary:
    def test_summary_is_written(self, make_config, tmp_source, tmp_path, monkeypatch):
        summary_file = tmp_path / "summary.md"
        monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary_file))
        monkeypatch.delenv("GITHUB_OUTPUT", raising=False)
        dest = tmp_path / "output"
        dest.mkdir()
        ActionRunner(make_config(
            command="compress", source=str(tmp_source), format="zip", dest=str(dest),
        )).execute_command()
        assert "Compression ratio" in summary_file.read_text()

    def test_summary_can_be_disabled(self, make_config, tmp_source, tmp_path,
                                     monkeypatch):
        summary_file = tmp_path / "summary.md"
        monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary_file))
        monkeypatch.delenv("GITHUB_OUTPUT", raising=False)
        dest = tmp_path / "output"
        dest.mkdir()
        ActionRunner(make_config(
            command="compress", source=str(tmp_source), format="zip", dest=str(dest),
            step_summary=False,
        )).execute_command()
        assert not summary_file.exists()


class TestSecretRegistration:
    def test_password_is_registered_and_masked(self, make_config, capsys):
        from masking import clear_secrets, mask
        clear_secrets()
        try:
            runner = ActionRunner(make_config(
                command="compress", source="./src", format="zip", password="example-password-1",
            ))
            runner.register_secrets()
            assert "::add-mask::example-password-1" in capsys.readouterr().out
            assert mask("zip -P example-password-1") == "zip -P ***"
        finally:
            clear_secrets()

    def test_no_password_registers_nothing(self, make_config, capsys):
        runner = ActionRunner(make_config(
            command="compress", source="./src", format="zip",
        ))
        runner.register_secrets()
        assert "::add-mask::" not in capsys.readouterr().out
