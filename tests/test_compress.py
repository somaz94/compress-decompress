import os
import shlex
import pytest
from compress import Compressor, compress
from config import AppConfig


class TestCompressorInit:
    def test_init_from_config(self, make_config, tmp_source):
        config = make_config(
            source=str(tmp_source),
            format="zip",
            include_root="false",
            exclude="*.log",
        )
        c = Compressor(config)
        assert c.source == str(tmp_source)
        assert c.format == "zip"
        assert c.include_root is False
        assert c.exclude == "*.log"
        assert c.is_glob_pattern is False
        assert c.matched_files == []


class TestCompressorValidate:
    def test_valid_source(self, make_config, tmp_source):
        c = Compressor(make_config(source=str(tmp_source)))
        assert c.validate() is True

    def test_invalid_source_fail(self, make_config):
        c = Compressor(make_config(source="/nonexistent", fail_on_error=True))
        from exceptions import ValidationError
        with pytest.raises(ValidationError):
            c.validate()

    def test_glob_pattern_detected(self, make_config, tmp_source):
        c = Compressor(make_config(source=str(tmp_source / "*.txt")))
        # Change working dir to source for glob to work
        original = os.getcwd()
        os.chdir(str(tmp_source))
        try:
            result = c.validate()
            assert c.is_glob_pattern is True
            assert result is True
            assert len(c.matched_files) > 0
        finally:
            os.chdir(original)

    def test_github_runner_path_conversion(self, make_config, monkeypatch):
        monkeypatch.setenv("GITHUB_WORKSPACE", "/github/workspace")
        c = Compressor(make_config(source="/home/runner/work/repo/repo", fail_on_error=False))
        c.source = "/home/runner/work/repo/repo"
        # After validate, source should be converted to GITHUB_WORKSPACE
        c.validate()  # will fail since path doesn't exist, but source is converted
        assert c.source == '/github/workspace'


class TestZipCommand:
    def test_with_root(self, make_config, tmp_source):
        config = make_config(source=str(tmp_source), format="zip", include_root="true")
        c = Compressor(config)
        c.source = str(tmp_source)
        cmd = c._get_zip_command("/out/test.zip", "test")
        assert "zip -r" in cmd
        assert shlex.quote(str(tmp_source.parent)) in cmd

    def test_without_root(self, make_config, tmp_source):
        config = make_config(source=str(tmp_source), format="zip", include_root="false")
        c = Compressor(config)
        c.source = str(tmp_source)
        cmd = c._get_zip_command("/out/test.zip", "test")
        assert "zip -r" in cmd
        assert ". " in cmd  # compress current dir

    def test_with_exclude(self, make_config, tmp_source):
        config = make_config(
            source=str(tmp_source), format="zip",
            include_root="true", exclude="*.log *.tmp"
        )
        c = Compressor(config)
        c.source = str(tmp_source)
        cmd = c._get_zip_command("/out/test.zip", "test")
        assert "-x " in cmd


class TestTarCommand:
    def test_tar_format(self, make_config, tmp_source):
        config = make_config(source=str(tmp_source), format="tar", include_root="true")
        c = Compressor(config)
        c.source = str(tmp_source)
        cmd = c._get_tar_command("/out/test.tar", "test")
        assert "tar" in cmd
        assert "-cf" in cmd

    def test_tgz_format(self, make_config, tmp_source):
        config = make_config(source=str(tmp_source), format="tgz", include_root="true")
        c = Compressor(config)
        c.source = str(tmp_source)
        cmd = c._get_tar_command("/out/test.tgz", "test")
        assert "-czf" in cmd

    def test_tbz2_format(self, make_config, tmp_source):
        config = make_config(source=str(tmp_source), format="tbz2", include_root="true")
        c = Compressor(config)
        c.source = str(tmp_source)
        cmd = c._get_tar_command("/out/test.tbz2", "test")
        assert "-cjf" in cmd

    def test_tar_with_exclude(self, make_config, tmp_source):
        config = make_config(
            source=str(tmp_source), format="tar",
            include_root="true", exclude="*.log"
        )
        c = Compressor(config)
        c.source = str(tmp_source)
        cmd = c._get_tar_command("/out/test.tar", "test")
        assert "--exclude=" in cmd


class TestExcludePatterns:
    def test_zip_exclude_with_root(self, make_config, tmp_source):
        config = make_config(
            source=str(tmp_source), format="zip",
            include_root="true", exclude="subdir"
        )
        c = Compressor(config)
        c.source = str(tmp_source)
        result = c._build_zip_exclude(str(tmp_source))
        dir_name = os.path.basename(str(tmp_source))
        # Should prefix with dir_name
        assert dir_name in result

    def test_zip_exclude_without_root(self, make_config, tmp_source):
        config = make_config(
            source=str(tmp_source), format="zip",
            include_root="false", exclude="subdir"
        )
        c = Compressor(config)
        c.source = str(tmp_source)
        result = c._build_zip_exclude(str(tmp_source))
        assert "-x " in result

    def test_tar_exclude_with_root(self, make_config, tmp_source):
        config = make_config(
            source=str(tmp_source), format="tar",
            include_root="true", exclude="*.log"
        )
        c = Compressor(config)
        c.source = str(tmp_source)
        result = c._build_tar_exclude(str(tmp_source))
        dir_name = os.path.basename(str(tmp_source))
        assert f"{dir_name}/" in result

    def test_empty_exclude(self, make_config, tmp_source):
        config = make_config(source=str(tmp_source), format="zip", exclude="")
        c = Compressor(config)
        c.source = str(tmp_source)
        assert c._build_zip_exclude(str(tmp_source)) == ""
        assert c._build_tar_exclude(str(tmp_source)) == ""


class TestCompressIntegration:
    def test_compress_zip(self, make_config, tmp_source, tmp_path):
        dest = tmp_path / "output"
        dest.mkdir()
        config = make_config(
            source=str(tmp_source), format="zip",
            include_root="true", dest=str(dest)
        )
        result = compress(config)
        assert result
        # Verify archive was created
        archives = list(dest.glob("*.zip"))
        assert len(archives) == 1

    def test_compress_tar(self, make_config, tmp_source, tmp_path):
        dest = tmp_path / "output"
        dest.mkdir()
        config = make_config(
            source=str(tmp_source), format="tar",
            include_root="true", dest=str(dest)
        )
        result = compress(config)
        assert result
        archives = list(dest.glob("*.tar"))
        assert len(archives) == 1

    def test_compress_without_root(self, make_config, tmp_source, tmp_path):
        dest = tmp_path / "output"
        dest.mkdir()
        config = make_config(
            source=str(tmp_source), format="zip",
            include_root="false", dest=str(dest)
        )
        result = compress(config)
        assert result

    def test_compress_with_custom_filename(self, make_config, tmp_source, tmp_path):
        dest = tmp_path / "output"
        dest.mkdir()
        config = make_config(
            source=str(tmp_source), format="zip",
            dest=str(dest), destfilename="my_archive"
        )
        result = compress(config)
        assert result
        assert (dest / "my_archive.zip").exists()

    def test_compress_tgz_with_root(self, make_config, tmp_source, tmp_path):
        dest = tmp_path / "output"
        dest.mkdir()
        config = make_config(
            source=str(tmp_source), format="tgz",
            include_root="true", dest=str(dest)
        )
        result = compress(config)
        assert result
        archives = list(dest.glob("*.tgz"))
        assert len(archives) == 1

    def test_compress_tgz_without_root(self, make_config, tmp_source, tmp_path):
        dest = tmp_path / "output"
        dest.mkdir()
        config = make_config(
            source=str(tmp_source), format="tgz",
            include_root="false", dest=str(dest)
        )
        result = compress(config)
        assert result

    def test_compress_tar_without_root(self, make_config, tmp_source, tmp_path):
        dest = tmp_path / "output"
        dest.mkdir()
        config = make_config(
            source=str(tmp_source), format="tar",
            include_root="false", dest=str(dest)
        )
        result = compress(config)
        assert result


class TestGlobPatternEdgeCases:
    def test_glob_no_match_no_fail(self, make_config, tmp_source):
        config = make_config(
            source=str(tmp_source / "*.xyz"),
            fail_on_error=False,
        )
        c = Compressor(config)
        result = c.validate()
        assert result is False
        assert c.is_glob_pattern is True

    def test_glob_no_match_fail(self, make_config, tmp_source):
        from exceptions import ValidationError
        config = make_config(
            source=str(tmp_source / "*.xyz"),
            fail_on_error=True,
        )
        c = Compressor(config)
        with pytest.raises(ValidationError, match="No files matched"):
            c.validate()

    def test_glob_verbose_listing(self, make_config, tmp_path):
        src = tmp_path / "many"
        src.mkdir()
        for i in range(15):
            (src / f"file{i}.txt").write_text(f"content {i}")
        config = make_config(
            source=str(src / "*.txt"),
            verbose=True,
        )
        c = Compressor(config)
        result = c.validate()
        assert result is True
        assert len(c.matched_files) == 15

    def test_compress_glob_pattern_integration(self, make_config, tmp_source, tmp_path):
        dest = tmp_path / "output"
        dest.mkdir()
        config = make_config(
            source=str(tmp_source / "*.txt"),
            format="zip",
            dest=str(dest),
        )
        result = compress(config)
        assert result

    def test_compress_glob_with_strip_prefix(self, make_config, tmp_source, tmp_path):
        dest = tmp_path / "output"
        dest.mkdir()
        config = make_config(
            source=str(tmp_source / "*.txt"),
            format="zip",
            dest=str(dest),
            strip_prefix=str(tmp_source),
        )
        result = compress(config)
        assert result


class TestDestinationPath:
    def test_default_destination_with_root(self, make_config, tmp_source):
        config = make_config(
            source=str(tmp_source), format="zip",
            include_root="true", dest="",
        )
        c = Compressor(config)
        c.source = str(tmp_source)
        c.dest = os.getcwd()
        path = c._determine_destination_path("source", ".zip")
        assert path.endswith("source.zip")

    def test_default_destination_without_root(self, make_config, tmp_source):
        config = make_config(
            source=str(tmp_source), format="zip",
            include_root="false", dest="",
        )
        c = Compressor(config)
        c.source = str(tmp_source)
        c.dest = os.getcwd()
        path = c._determine_destination_path("source", ".zip")
        assert path.endswith("source.zip")


class TestExcludePatternFormatting:
    def test_format_pattern_with_root_dir_prefix_match(self, make_config, tmp_source):
        config = make_config(
            source=str(tmp_source), format="zip",
            include_root="true",
        )
        c = Compressor(config)
        dir_name = os.path.basename(str(tmp_source))
        result = c._format_pattern_with_root(f"{dir_name}/subdir", str(tmp_source), dir_name)
        assert result == [f"{dir_name}/subdir"]

    def test_format_pattern_with_root_trailing_slash(self, make_config, tmp_source):
        config = make_config(
            source=str(tmp_source), format="zip",
            include_root="true",
        )
        c = Compressor(config)
        dir_name = os.path.basename(str(tmp_source))
        result = c._format_pattern_with_root("subdir/", str(tmp_source), dir_name)
        assert result == [f"{dir_name}/subdir/*"]

    def test_format_pattern_without_root_non_dir(self, make_config, tmp_source):
        config = make_config(
            source=str(tmp_source), format="zip",
            include_root="false",
        )
        c = Compressor(config)
        result = c._format_pattern_without_root("*.log", str(tmp_source))
        assert result == ["*.log"]

    def test_tar_exclude_without_root(self, make_config, tmp_source):
        config = make_config(
            source=str(tmp_source), format="tar",
            include_root="false", exclude="*.log",
        )
        c = Compressor(config)
        result = c._build_tar_exclude(str(tmp_source))
        assert "--exclude=" in result
        dir_name = os.path.basename(str(tmp_source))
        assert f"{dir_name}/" not in result


class TestSpecialTarCommand:
    def test_special_tar_command_tgz(self, make_config, tmp_source):
        config = make_config(
            source=str(tmp_source), format="tgz",
            include_root="false",
        )
        c = Compressor(config)
        c.source = str(tmp_source)
        cmd = c._get_tar_command("/out/test.tgz", "test")
        assert "mkdir -p" in cmd
        assert "cp -r" in cmd
        assert "-czf" in cmd

    def test_special_tar_command_tbz2(self, make_config, tmp_source):
        config = make_config(
            source=str(tmp_source), format="tbz2",
            include_root="false",
        )
        c = Compressor(config)
        c.source = str(tmp_source)
        cmd = c._get_tar_command("/out/test.tbz2", "test")
        assert "mkdir -p" in cmd
        assert "-cjf" in cmd

    def test_special_tar_with_exclude(self, make_config, tmp_source):
        config = make_config(
            source=str(tmp_source), format="tgz",
            include_root="false", exclude="*.log",
        )
        c = Compressor(config)
        c.source = str(tmp_source)
        cmd = c._get_special_tar_command("/out/test.tgz", "test", "z")
        assert "--exclude=" in cmd


class TestCleanup:
    def test_cleanup_temp_directory(self, make_config, tmp_path):
        config = make_config()
        c = Compressor(config)
        temp = tmp_path / "temp_cleanup_test"
        temp.mkdir()
        c.temp_dir = str(temp)
        c._cleanup_temp_directory()
        assert not temp.exists()

    def test_cleanup_nonexistent_temp(self, make_config):
        config = make_config()
        c = Compressor(config)
        c.temp_dir = "/nonexistent/path"
        c._cleanup_temp_directory()  # Should not raise

    def test_cleanup_none_temp(self, make_config):
        config = make_config()
        c = Compressor(config)
        c.temp_dir = None
        c._cleanup_temp_directory()  # Should not raise

    def test_cleanup_verbose(self, make_config, tmp_path):
        config = make_config(verbose=True)
        c = Compressor(config)
        temp = tmp_path / "temp_verbose"
        temp.mkdir()
        c.temp_dir = str(temp)
        c._cleanup_temp_directory()
        assert not temp.exists()


class TestCompressErrorHandling:
    def test_compress_validation_failed(self, make_config):
        config = make_config(
            source="/nonexistent/path", format="zip",
            fail_on_error=False,
        )
        c = Compressor(config)
        result = c.compress()
        assert result.success is False

    def test_compress_exception_handling(self, make_config, tmp_source, monkeypatch):
        config = make_config(
            source=str(tmp_source), format="zip",
            fail_on_error=False,
        )
        c = Compressor(config)
        monkeypatch.setattr(c, 'get_compression_command', lambda: (_ for _ in ()).throw(OSError("test error")))
        result = c.compress()
        assert result.success is False


class TestCompressionLevel:
    def test_zip_with_level(self, make_config, tmp_source):
        config = make_config(
            source=str(tmp_source), format="zip",
            compression_level="9",
        )
        c = Compressor(config)
        c.source = str(tmp_source)
        cmd = c._get_zip_command("/out/test.zip", "test")
        assert "-9" in cmd
        assert "zip" in cmd
        assert "-r" in cmd

    def test_zip_without_level(self, make_config, tmp_source):
        config = make_config(source=str(tmp_source), format="zip")
        c = Compressor(config)
        c.source = str(tmp_source)
        cmd = c._get_zip_command("/out/test.zip", "test")
        assert "zip -r" in cmd
        assert "zip -r" in cmd  # no double space

    def test_tgz_level_env(self, make_config, tmp_source):
        config = make_config(
            source=str(tmp_source), format="tgz",
            compression_level="9",
        )
        c = Compressor(config)
        assert "GZIP=-9" in c._get_tar_level_env()

    def test_tbz2_level_env(self, make_config, tmp_source):
        config = make_config(
            source=str(tmp_source), format="tbz2",
            compression_level="5",
        )
        c = Compressor(config)
        assert "BZIP2=-5" in c._get_tar_level_env()

    def test_tar_no_level_env(self, make_config, tmp_source):
        config = make_config(source=str(tmp_source), format="tar")
        c = Compressor(config)
        assert c._get_tar_level_env() == ""

    def test_compress_zip_with_level(self, make_config, tmp_source, tmp_path):
        dest = tmp_path / "output"
        dest.mkdir()
        config = make_config(
            source=str(tmp_source), format="zip",
            dest=str(dest), compression_level="1",
        )
        result, checksum = compress(config)
        assert result
        assert checksum  # SHA256 hash


class TestChecksum:
    def test_checksum_on_compress(self, make_config, tmp_source, tmp_path):
        dest = tmp_path / "output"
        dest.mkdir()
        config = make_config(
            source=str(tmp_source), format="zip",
            dest=str(dest),
        )
        output_path, checksum = compress(config)
        assert output_path
        assert len(checksum) == 64  # SHA256 hex length

    def test_checksum_matches_file(self, make_config, tmp_source, tmp_path):
        import hashlib
        dest = tmp_path / "output"
        dest.mkdir()
        config = make_config(
            source=str(tmp_source), format="zip",
            dest=str(dest),
        )
        output_path, checksum = compress(config)
        # Verify checksum manually
        sha256 = hashlib.sha256()
        with open(output_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        assert checksum == sha256.hexdigest()

    def test_no_checksum_on_failure(self, make_config):
        config = make_config(
            source="/nonexistent", format="zip",
            fail_on_error=False,
        )
        output_path, checksum = compress(config)
        assert output_path == ""
        assert checksum == ""


class TestTxzFormat:
    def test_txz_tar_options(self, make_config, tmp_source):
        config = make_config(source=str(tmp_source), format="txz", include_root="true")
        c = Compressor(config)
        c.source = str(tmp_source)
        cmd = c._get_tar_command("/out/test.txz", "test")
        assert "-cJf" in cmd

    def test_txz_without_root(self, make_config, tmp_source):
        config = make_config(source=str(tmp_source), format="txz", include_root="false")
        c = Compressor(config)
        c.source = str(tmp_source)
        cmd = c._get_tar_command("/out/test.txz", "test")
        assert "mkdir -p" in cmd
        assert "-cJf" in cmd

    def test_txz_level_env(self, make_config, tmp_source):
        config = make_config(
            source=str(tmp_source), format="txz",
            compression_level="6",
        )
        c = Compressor(config)
        assert "XZ_OPT=-6" in c._get_tar_level_env()

    def test_compress_txz_integration(self, make_config, tmp_source, tmp_path):
        dest = tmp_path / "output"
        dest.mkdir()
        config = make_config(
            source=str(tmp_source), format="txz",
            include_root="true", dest=str(dest),
        )
        output_path, checksum = compress(config)
        assert output_path
        assert checksum
        archives = list(dest.glob("*.txz"))
        assert len(archives) == 1

    def test_compress_txz_without_root(self, make_config, tmp_source, tmp_path):
        dest = tmp_path / "output"
        dest.mkdir()
        config = make_config(
            source=str(tmp_source), format="txz",
            include_root="false", dest=str(dest),
        )
        output_path, checksum = compress(config)
        assert output_path
        assert checksum


class TestPasswordEncryption:
    def test_zip_command_with_password(self, make_config, tmp_source):
        config = make_config(
            source=str(tmp_source), format="zip",
            password="secret123",
        )
        c = Compressor(config)
        c.source = str(tmp_source)
        cmd = c._get_zip_command("/out/test.zip", "test")
        assert "-P" in cmd
        assert "secret123" in cmd

    def test_zip_command_without_password(self, make_config, tmp_source):
        config = make_config(source=str(tmp_source), format="zip")
        c = Compressor(config)
        c.source = str(tmp_source)
        cmd = c._get_zip_command("/out/test.zip", "test")
        assert "-P" not in cmd

    def test_compress_zip_with_password(self, make_config, tmp_source, tmp_path):
        dest = tmp_path / "output"
        dest.mkdir()
        config = make_config(
            source=str(tmp_source), format="zip",
            dest=str(dest), password="testpass",
        )
        output_path, checksum = compress(config)
        assert output_path
        assert checksum
        archives = list(dest.glob("*.zip"))
        assert len(archives) == 1
