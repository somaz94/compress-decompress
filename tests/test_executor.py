import pytest
from executor import ProcessResult, CommandExecutor
from exceptions import CommandError


class TestProcessResult:
    def test_success_result(self):
        r = ProcessResult(True, "ok")
        assert r.success is True
        assert r.message == "ok"
        assert r.data == {}

    def test_failure_with_data(self):
        r = ProcessResult(False, "fail", {"stderr": "error output"})
        assert r.success is False
        assert r.data["stderr"] == "error output"

    def test_default_data_is_empty_dict(self):
        r = ProcessResult(True, "ok")
        assert r.data == {}
        # Verify not shared reference
        r2 = ProcessResult(True, "ok2")
        assert r.data is not r2.data


class TestCommandExecutor:
    def test_successful_command(self):
        result = CommandExecutor.run("echo hello", verbose=False)
        assert result.success is True

    def test_failed_command_raises(self):
        with pytest.raises(CommandError):
            CommandExecutor.run("false", fail_on_error=True)

    def test_failed_command_no_raise(self):
        result = CommandExecutor.run("false", fail_on_error=False)
        assert result.success is False

    def test_verbose_mode(self, capsys):
        CommandExecutor.run("echo verbose_test", verbose=True)
        # Command should have been printed
        captured = capsys.readouterr()
        assert "echo verbose_test" in captured.out

    def test_command_output(self):
        result = CommandExecutor.run("echo test_output", verbose=False)
        assert result.success is True
        assert result.message == "Command executed successfully"

    def test_timeout_raises(self):
        with pytest.raises(CommandError, match="timed out"):
            CommandExecutor.run("sleep 10", timeout=1)

    def test_timeout_no_raise(self):
        result = CommandExecutor.run("sleep 10", fail_on_error=False, timeout=1)
        assert result.success is False
        assert "timed out" in result.message

    def test_custom_timeout(self):
        result = CommandExecutor.run("echo fast", timeout=5)
        assert result.success is True
