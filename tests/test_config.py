import os
import pytest
from config import AppConfig, CompressionFormat


class TestCompressionFormat:
    def test_list_returns_all_formats(self):
        formats = CompressionFormat.list()
        assert formats == ['zip', 'tar', 'tgz', 'tbz2']

    def test_get_extension_valid(self):
        assert CompressionFormat.get_extension('zip') == '.zip'
        assert CompressionFormat.get_extension('tar') == '.tar'
        assert CompressionFormat.get_extension('tgz') == '.tgz'
        assert CompressionFormat.get_extension('tbz2') == '.tbz2'

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
                     "PRESERVE_GLOB_STRUCTURE", "STRIP_PREFIX"]:
            monkeypatch.delenv(var, raising=False)

        config = AppConfig.from_env()
        assert config.command == ""
        assert config.verbose is False
        assert config.fail_on_error is True
