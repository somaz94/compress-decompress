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
        output_path = compress(config).output_path
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
        result = compress(config)
        output_path, checksum = result.output_path, result.checksum
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


class TestZstdDecompression:
    def test_tzst_command(self, make_config, tmp_path):
        config = make_config(
            command="decompress", source="/archives/test.tzst",
            format="tzst", dest=str(tmp_path),
        )
        d = Decompressor(config)
        cmd = d.get_decompression_command()
        assert "--zstd" in cmd
        assert "-xf" in cmd

    def test_tzst_roundtrip(self, make_config, tmp_source, tmp_path):
        from compress import compress
        dest = tmp_path / "compressed"
        dest.mkdir()
        output_path = compress(make_config(
            source=str(tmp_source), format="tzst",
            include_root="true", dest=str(dest),
        )).output_path
        assert output_path

        extract_dest = tmp_path / "extracted"
        extract_dest.mkdir()
        result = decompress(make_config(
            command="decompress", source=output_path,
            format="tzst", dest=str(extract_dest),
        ))
        assert result
        assert list(extract_dest.rglob("*.txt"))


class TestChecksumVerification:
    def _checksum_of(self, path):
        from file_utils import FileUtils
        return FileUtils.sha256_of_file(path)

    def test_matching_checksum_extracts(self, make_config, tmp_archive_zip, tmp_path):
        dest = tmp_path / "extracted"
        dest.mkdir()
        result = decompress(make_config(
            command="decompress", source=tmp_archive_zip, format="zip",
            dest=str(dest), verify_checksum=self._checksum_of(tmp_archive_zip),
        ))
        assert result
        assert list(dest.rglob("*.txt"))

    def test_uppercase_checksum_matches(self, make_config, tmp_archive_zip, tmp_path):
        dest = tmp_path / "extracted"
        dest.mkdir()
        result = decompress(make_config(
            command="decompress", source=tmp_archive_zip, format="zip",
            dest=str(dest), verify_checksum=self._checksum_of(tmp_archive_zip).upper(),
        ))
        assert result

    def test_mismatched_checksum_fails(self, make_config, tmp_archive_zip, tmp_path):
        from exceptions import CompressError
        dest = tmp_path / "extracted"
        dest.mkdir()
        config = make_config(
            command="decompress", source=tmp_archive_zip, format="zip",
            dest=str(dest), verify_checksum="b" * 64,
        )
        with pytest.raises(CompressError, match="Checksum mismatch"):
            decompress(config)

    def test_mismatched_checksum_without_fail_on_error(self, make_config,
                                                        tmp_archive_zip, tmp_path):
        dest = tmp_path / "extracted"
        dest.mkdir()
        result = decompress(make_config(
            command="decompress", source=tmp_archive_zip, format="zip",
            dest=str(dest), verify_checksum="b" * 64, fail_on_error=False,
        ))
        assert not result
        assert not list(dest.rglob("*.txt"))  # nothing was extracted

    def test_no_checksum_skips_verification(self, make_config, tmp_archive_zip, tmp_path):
        dest = tmp_path / "extracted"
        dest.mkdir()
        result = decompress(make_config(
            command="decompress", source=tmp_archive_zip, format="zip", dest=str(dest),
        ))
        assert result


class TestPathTraversalProtection:
    @pytest.fixture
    def zip_slip_archive(self, tmp_path):
        import zipfile
        archive_path = tmp_path / "slip.zip"
        with zipfile.ZipFile(archive_path, "w") as zf:
            zf.writestr("safe.txt", "fine")
            zf.writestr("../escaped.txt", "owned")
        return str(archive_path)

    def test_traversal_archive_is_rejected(self, make_config, zip_slip_archive, tmp_path):
        from exceptions import CompressError
        dest = tmp_path / "extracted"
        config = make_config(
            command="decompress", source=zip_slip_archive, format="zip", dest=str(dest),
        )
        with pytest.raises(CompressError, match="Unsafe archive"):
            decompress(config)

    def test_rejection_happens_before_extraction(self, make_config, zip_slip_archive,
                                                  tmp_path):
        dest = tmp_path / "extracted"
        result = decompress(make_config(
            command="decompress", source=zip_slip_archive, format="zip",
            dest=str(dest), fail_on_error=False,
        ))
        assert not result
        assert not (tmp_path / "escaped.txt").exists()

    def test_check_can_be_disabled(self, make_config, zip_slip_archive, tmp_path):
        """With the guard off the traversal entry is reported, not rejected."""
        from decompress import Decompressor
        d = Decompressor(make_config(
            command="decompress", source=zip_slip_archive, format="zip",
            dest=str(tmp_path), path_traversal_check=False,
        ))
        assert "../escaped.txt" in d.inspect_entries()

    def test_clean_archive_passes_the_check(self, make_config, tmp_archive_zip, tmp_path):
        dest = tmp_path / "extracted"
        dest.mkdir()
        result = decompress(make_config(
            command="decompress", source=tmp_archive_zip, format="zip", dest=str(dest),
        ))
        assert result

    def test_absolute_entries_only_warn(self, make_config, tmp_path):
        """An absolute member is stripped by tar/unzip, so it warns instead of failing."""
        import zipfile
        from decompress import Decompressor
        archive_path = tmp_path / "absolute.zip"
        with zipfile.ZipFile(archive_path, "w") as zf:
            zf.writestr("/rooted.txt", "fine")
        d = Decompressor(make_config(
            command="decompress", source=str(archive_path), format="zip",
            dest=str(tmp_path),
        ))
        assert d.inspect_entries() == ["/rooted.txt"]

    def test_unreadable_archive_skips_the_check(self, make_config, tmp_path):
        """A format the stdlib cannot open is left to tar/unzip, not rejected here."""
        from decompress import Decompressor
        broken = tmp_path / "broken.zip"
        broken.write_text("not an archive")
        d = Decompressor(make_config(
            command="decompress", source=str(broken), format="zip", dest=str(tmp_path),
        ))
        assert d.inspect_entries() is None


class TestDecompressStats:
    def test_stats_populated_on_success(self, make_config, tmp_archive_zip, tmp_path):
        dest = tmp_path / "extracted"
        dest.mkdir()
        result = decompress(make_config(
            command="decompress", source=tmp_archive_zip, format="zip", dest=str(dest),
        ))
        assert result.command == "decompress"
        assert result.format == "zip"
        assert result.output_path == str(dest)
        assert result.original_size > 0
        assert result.file_count == 3
        assert result.compression_ratio == 0.0  # not meaningful for decompression

    def test_stats_empty_on_failure(self, make_config, tmp_path):
        result = decompress(make_config(
            command="decompress", source=str(tmp_path / "absent.zip"),
            format="zip", dest=str(tmp_path), fail_on_error=False,
        ))
        assert not result
        assert result.output_path == ""


class TestFileCountAcrossFormats:
    """file_count must not depend on the archive format."""

    @pytest.mark.parametrize("fmt", ["zip", "tar", "tgz", "tbz2", "txz"])
    def test_same_tree_same_count(self, make_config, tmp_source, tmp_path, fmt,
                                  monkeypatch):
        from compress import compress
        # macOS bsdtar stores extended attributes as extra `._name` members,
        # which the Linux tar in the action image never emits. Suppress them so
        # this asserts the tar/zip parity it is about, on either platform.
        monkeypatch.setenv("COPYFILE_DISABLE", "1")
        packed = tmp_path / f"packed-{fmt}"
        packed.mkdir()
        output_path = compress(make_config(
            source=str(tmp_source), format=fmt, include_root="true", dest=str(packed),
        )).output_path
        assert output_path

        extract_dest = tmp_path / f"out-{fmt}"
        extract_dest.mkdir()
        result = decompress(make_config(
            command="decompress", source=output_path, format=fmt, dest=str(extract_dest),
        ))
        assert result
        assert result.file_count == 3  # tmp_source holds three files, two directories


class TestStatsOnRejectedArchive:
    def test_checksum_mismatch_still_reports_what_it_read(self, make_config,
                                                          tmp_archive_zip, tmp_path):
        dest = tmp_path / "extracted"
        result = decompress(make_config(
            command="decompress", source=tmp_archive_zip, format="zip",
            dest=str(dest), verify_checksum="b" * 64, fail_on_error=False,
        ))
        assert not result
        assert result.original_size > 0   # the archive was read, not zero
        assert result.output_path == ""

    def test_missing_source_reports_zero_size(self, make_config, tmp_path):
        result = decompress(make_config(
            command="decompress", source=str(tmp_path / "absent.zip"),
            format="zip", dest=str(tmp_path), fail_on_error=False,
        ))
        assert not result
        assert result.original_size == 0
