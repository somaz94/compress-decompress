import os
import pytest
from config import AppConfig, CompressionFormat


class TestCompressionFormat:
    def test_list_returns_all_formats(self):
        formats = CompressionFormat.list()
        assert formats == ['zip', 'tar', 'tgz', 'tbz2', 'txz', 'tzst']

    def test_get_extension_valid(self):
        assert CompressionFormat.get_extension('zip') == '.zip'
        assert CompressionFormat.get_extension('tar') == '.tar'
        assert CompressionFormat.get_extension('tgz') == '.tgz'
        assert CompressionFormat.get_extension('tbz2') == '.tbz2'
        assert CompressionFormat.get_extension('txz') == '.txz'
        assert CompressionFormat.get_extension('tzst') == '.tzst'

    def test_get_extension_invalid(self):
        assert CompressionFormat.get_extension('rar') == ''
        assert CompressionFormat.get_extension('') == ''


class TestAppConfig:
    def test_default_values(self):
        config = AppConfig()
        assert config.command == ""
        assert config.source == ""
        assert config.format == ""
        assert config.include_root == "true"
        assert config.preserve_glob_structure == "false"
        assert config.strip_prefix == ""
        assert config.verbose is False
        assert config.fail_on_error is True
        assert config.dest == ""
        assert config.destfilename == ""
        assert config.exclude == ""

    def test_effective_dest_with_dest(self):
        config = AppConfig(dest="/custom/path")
        assert config.effective_dest == "/custom/path"

    def test_effective_dest_fallback_to_cwd(self):
        config = AppConfig(dest="")
        # Should fall back to GITHUB_WORKSPACE or cwd
        assert config.effective_dest == os.getenv("GITHUB_WORKSPACE", os.getcwd())

    def test_effective_dest_fallback_to_github_workspace(self, monkeypatch):
        monkeypatch.setenv("GITHUB_WORKSPACE", "/github/workspace")
        config = AppConfig(dest="")
        assert config.effective_dest == "/github/workspace"

    def test_from_env(self, monkeypatch):
        monkeypatch.setenv("COMMAND", "compress")
        monkeypatch.setenv("SOURCE", "./src")
        monkeypatch.setenv("FORMAT", "zip")
        monkeypatch.setenv("INCLUDEROOT", "false")
        monkeypatch.setenv("VERBOSE", "true")
        monkeypatch.setenv("FAIL_ON_ERROR", "false")
        monkeypatch.setenv("DEST", "/output")
        monkeypatch.setenv("DESTFILENAME", "archive")
        monkeypatch.setenv("EXCLUDE", "*.log node_modules")

        config = AppConfig.from_env()

        assert config.command == "compress"
        assert config.source == "./src"
        assert config.format == "zip"
        assert config.include_root == "false"
        assert config.verbose is True
        assert config.fail_on_error is False
        assert config.dest == "/output"
        assert config.destfilename == "archive"
        assert config.exclude == "*.log node_modules"

    def test_from_env_defaults(self, monkeypatch):
        # Clear all relevant env vars
        for var in ["COMMAND", "SOURCE", "FORMAT", "INCLUDEROOT", "VERBOSE",
                     "FAIL_ON_ERROR", "DEST", "DESTFILENAME", "EXCLUDE",
                     "PRESERVE_GLOB_STRUCTURE", "STRIP_PREFIX",
                     "COMPRESSION_LEVEL", "PASSWORD"]:
            monkeypatch.delenv(var, raising=False)

        config = AppConfig.from_env()
        assert config.command == ""
        assert config.verbose is False
        assert config.fail_on_error is True

    def test_valid_compression_levels(self):
        for level in "0123456789":
            assert AppConfig._is_valid_compression_level(level) is True

    def test_invalid_compression_levels(self):
        for bad in ["", "10", "-1", "abc", "9;rm", " 5", "5 "]:
            assert AppConfig._is_valid_compression_level(bad) is False

    def test_from_env_invalid_compression_level(self, monkeypatch):
        from exceptions import ValidationError
        monkeypatch.setenv("COMPRESSION_LEVEL", "9;rm -rf /")
        with pytest.raises(ValidationError, match="Invalid compression_level"):
            AppConfig.from_env()

    def test_from_env_valid_compression_level(self, monkeypatch):
        monkeypatch.setenv("COMPRESSION_LEVEL", "5")
        config = AppConfig.from_env()
        assert config.compression_level == "5"


class TestChecksumValidation:
    def test_valid_sha256(self):
        assert AppConfig._is_valid_sha256("a" * 64) is True
        assert AppConfig._is_valid_sha256("0123456789abcdef" * 4) is True

    def test_uppercase_sha256_is_valid(self):
        assert AppConfig._is_valid_sha256("ABCDEF0123456789" * 4) is True

    def test_invalid_sha256(self):
        for bad in ["", "a" * 63, "a" * 65, "z" * 64, "a" * 32]:
            assert AppConfig._is_valid_sha256(bad) is False

    def test_from_env_rejects_malformed_checksum(self, monkeypatch):
        from exceptions import ValidationError
        monkeypatch.setenv("VERIFY_CHECKSUM", "not-a-digest")
        with pytest.raises(ValidationError, match="Invalid verify_checksum"):
            AppConfig.from_env()

    def test_from_env_normalizes_checksum_case(self, monkeypatch):
        monkeypatch.setenv("VERIFY_CHECKSUM", "A" * 64)
        assert AppConfig.from_env().verify_checksum == "a" * 64

    def test_from_env_trims_whitespace(self, monkeypatch):
        monkeypatch.setenv("VERIFY_CHECKSUM", f"  {'b' * 64}  ")
        assert AppConfig.from_env().verify_checksum == "b" * 64


class TestSafetyAndSummaryDefaults:
    def test_defaults_are_enabled(self, monkeypatch):
        for var in ["PATH_TRAVERSAL_CHECK", "STEP_SUMMARY", "VERIFY_CHECKSUM"]:
            monkeypatch.delenv(var, raising=False)
        config = AppConfig.from_env()
        assert config.path_traversal_check is True
        assert config.step_summary is True
        assert config.verify_checksum == ""

    def test_empty_input_keeps_the_default(self, monkeypatch):
        """An unset action input arrives as an empty string, not as 'false'."""
        monkeypatch.setenv("PATH_TRAVERSAL_CHECK", "")
        monkeypatch.setenv("STEP_SUMMARY", "")
        config = AppConfig.from_env()
        assert config.path_traversal_check is True
        assert config.step_summary is True

    def test_can_be_disabled(self, monkeypatch):
        monkeypatch.setenv("PATH_TRAVERSAL_CHECK", "false")
        monkeypatch.setenv("STEP_SUMMARY", "false")
        config = AppConfig.from_env()
        assert config.path_traversal_check is False
        assert config.step_summary is False
