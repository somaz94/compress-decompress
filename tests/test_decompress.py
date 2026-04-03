import os
import pytest
from decompress import Decompressor, decompress
from config import AppConfig, CommandConfig, DECOMPRESSION_COMMANDS


class TestDecompressorInit:
    def test_init_from_config(self, make_config):
        config = make_config(source="/path/to/archive.zip", format="zip")
        d = Decompressor(config)
        assert d.source == "/path/to/archive.zip"
        assert d.format == "zip"


class TestDecompressorValidate:
    def test_valid_source(self, make_config, tmp_archive_zip):
        config = make_config(source=tmp_archive_zip, format="zip")
        d = Decompressor(config)
        assert d.validate() is True

    def test_invalid_source(self, make_config):
        from exceptions import ValidationError
        config = make_config(source="/nonexistent.zip", format="zip", fail_on_error=True)
        d = Decompressor(config)
        with pytest.raises(ValidationError):
            d.validate()


class TestDecompressorCommand:
    def test_zip_command(self, make_config, tmp_archive_zip, tmp_path):
        dest = tmp_path / "output"
        config = make_config(source=tmp_archive_zip, format="zip", dest=str(dest))
        d = Decompressor(config)
        cmd = d.get_decompression_command()
        assert "unzip" in cmd
        assert tmp_archive_zip in cmd or "'" in cmd  # quoted path

    def test_tar_command(self, make_config, tmp_archive_tar, tmp_path):
        dest = tmp_path / "output"
        config = make_config(source=tmp_archive_tar, format="tar", dest=str(dest))
        d = Decompressor(config)
        cmd = d.get_decompression_command()
        assert "tar" in cmd
        assert "-xf" in cmd

    def test_unsupported_format(self, make_config, tmp_archive_zip):
        config = make_config(source=tmp_archive_zip, format="rar")
        d = Decompressor(config)
        with pytest.raises(ValueError, match="Unsupported format"):
            d.get_decompression_command()

    def test_get_command_config_returns_command_config(self, make_config, tmp_archive_zip):
        config = make_config(source=tmp_archive_zip, format="zip")
        d = Decompressor(config)
        cmd_config = d._get_command_config()
        assert isinstance(cmd_config, CommandConfig)


class TestDecompressIntegration:
    def test_decompress_zip(self, make_config, tmp_archive_zip, tmp_path):
        dest = tmp_path / "extracted"
        dest.mkdir()
        config = make_config(source=tmp_archive_zip, format="zip", dest=str(dest))
        result = decompress(config)
        assert result
        # Verify files were extracted
        extracted = list(dest.rglob("*.txt"))
        assert len(extracted) > 0

    def test_decompress_tar(self, make_config, tmp_archive_tar, tmp_path):
        dest = tmp_path / "extracted"
        dest.mkdir()
        config = make_config(source=tmp_archive_tar, format="tar", dest=str(dest))
        result = decompress(config)
        assert result
        extracted = list(dest.rglob("*.txt"))
        assert len(extracted) > 0


class TestDecompressorListContents:
    def test_list_contents_nonexistent_dest(self, make_config):
        config = make_config(source="/dummy.zip", format="zip", dest="/nonexistent")
        d = Decompressor(config)
        d.dest = "/nonexistent"
        d.list_contents()  # Should return early without error

    def test_list_contents_with_files(self, make_config, tmp_path):
        dest = tmp_path / "contents"
        dest.mkdir()
        (dest / "file.txt").write_text("hello")
        sub = dest / "subdir"
        sub.mkdir()
        config = make_config(source="/dummy.zip", format="zip", dest=str(dest))
        d = Decompressor(config)
        d.dest = str(dest)
        d.list_contents()  # Should print file and directory

    def test_list_contents_error(self, make_config, tmp_path, monkeypatch):
        dest = tmp_path / "errdir"
        dest.mkdir()
        config = make_config(source="/dummy.zip", format="zip", verbose=True)
        d = Decompressor(config)
        d.dest = str(dest)
        monkeypatch.setattr(os, 'listdir', lambda p: (_ for _ in ()).throw(PermissionError("denied")))
        d.list_contents()  # Should handle error gracefully


class TestDecompressEdgeCases:
    def test_decompress_validation_failed(self, make_config):
        config = make_config(
            source="/nonexistent.zip", format="zip",
            fail_on_error=False,
        )
        d = Decompressor(config)
        result = d.decompress()
        assert result.success is False

    def test_decompress_exception_handling(self, make_config, tmp_archive_zip, monkeypatch):
        config = make_config(
            source=tmp_archive_zip, format="zip",
            fail_on_error=False,
        )
        d = Decompressor(config)
        monkeypatch.setattr(d, 'get_decompression_command', lambda: (_ for _ in ()).throw(OSError("test")))
        result = d.decompress()
        assert result.success is False


class TestTxzDecompression:
    def test_txz_command_config_exists(self):
        assert "txz" in DECOMPRESSION_COMMANDS
        cmd_config = DECOMPRESSION_COMMANDS["txz"]
        assert cmd_config.command == "tar"

    def test_txz_command_format(self, make_config, tmp_path):
        archive = tmp_path / "test.txz"
        archive.write_bytes(b"")
        config = make_config(source=str(archive), format="txz", dest=str(tmp_path))
        d = Decompressor(config)
        cmd = d.get_decompression_command()
        assert "-xJf" in cmd

    def test_decompress_txz_integration(self, make_config, tmp_source, tmp_path):
        from compress import compress
        # First compress as txz
        dest = tmp_path / "compressed"
        dest.mkdir()
        config = make_config(
            source=str(tmp_source), format="txz",
            include_root="true", dest=str(dest),
        )
        output_path, _ = compress(config)
        assert output_path

        # Then decompress
        extract_dest = tmp_path / "extracted"
        extract_dest.mkdir()
        config2 = make_config(
            command="decompress", source=output_path,
            format="txz", dest=str(extract_dest),
        )
        result = decompress(config2)
        assert result
        extracted = list(extract_dest.rglob("*.txt"))
        assert len(extracted) > 0


class TestPasswordDecompression:
    def test_unzip_command_with_password(self, make_config, tmp_archive_zip, tmp_path):
        dest = tmp_path / "output"
        config = make_config(
            source=tmp_archive_zip, format="zip",
            dest=str(dest), password="secret",
        )
        d = Decompressor(config)
        cmd = d.get_decompression_command()
        assert "-P" in cmd
        assert "secret" in cmd

    def test_unzip_command_without_password(self, make_config, tmp_archive_zip, tmp_path):
        dest = tmp_path / "output"
        config = make_config(
            source=tmp_archive_zip, format="zip",
            dest=str(dest),
        )
        d = Decompressor(config)
        cmd = d.get_decompression_command()
        assert "-P" not in cmd

    def test_password_ignored_for_tar(self, make_config, tmp_archive_tar, tmp_path):
        dest = tmp_path / "output"
        config = make_config(
            source=tmp_archive_tar, format="tar",
            dest=str(dest), password="secret",
        )
        d = Decompressor(config)
        cmd = d.get_decompression_command()
        assert "-P" not in cmd

    def test_compress_decompress_with_password(self, make_config, tmp_source, tmp_path):
        from compress import compress
        # Compress with password
        dest = tmp_path / "compressed"
        dest.mkdir()
        config = make_config(
            source=str(tmp_source), format="zip",
            dest=str(dest), password="mypass123",
        )
        output_path, checksum = compress(config)
        assert output_path
        assert checksum

        # Decompress with password
        extract_dest = tmp_path / "extracted"
        extract_dest.mkdir()
        config2 = make_config(
            command="decompress", source=output_path,
            format="zip", dest=str(extract_dest),
            password="mypass123",
        )
        result = decompress(config2)
        assert result
        extracted = list(extract_dest.rglob("*.txt"))
        assert len(extracted) > 0
