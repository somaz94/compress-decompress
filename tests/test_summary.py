import summary
from stats import OperationStats


def _compress_stats(**overrides):
    base = dict(
        command="compress", format="zip", success=True,
        output_path="/out/archive.zip",
        checksum="a" * 64,
        original_size=2048, compressed_size=512,
        file_count=7, duration=1.25,
    )
    base.update(overrides)
    return OperationStats(**base)


class TestRender:
    def test_compress_summary_contains_metrics(self):
        rendered = summary.render(_compress_stats())
        assert "### ✅ Compress — `zip`" in rendered
        assert "/out/archive.zip" in rendered
        assert "75.0%" in rendered
        assert "| **Files** | 7 |" in rendered
        assert "1.25s" in rendered
        assert "a" * 64 in rendered

    def test_compress_summary_without_checksum_or_files(self):
        rendered = summary.render(_compress_stats(checksum="", file_count=0))
        assert "SHA256" not in rendered
        assert "Files" not in rendered

    def test_failed_run_uses_failure_icon(self):
        rendered = summary.render(_compress_stats(success=False))
        assert rendered.startswith("### ❌ Compress")

    def test_failed_compress_omits_the_empty_archive_row(self):
        rendered = summary.render(_compress_stats(success=False, output_path=""))
        assert "Archive" not in rendered
        assert "``" not in rendered

    def test_failed_decompress_omits_the_empty_destination_row(self):
        stats = OperationStats(
            command="decompress", format="zip", success=False,
            output_path="", original_size=2048, duration=0.1,
        )
        rendered = summary.render(stats)
        assert "Extracted to" not in rendered
        assert "``" not in rendered

    def test_decompress_summary(self):
        stats = OperationStats(
            command="decompress", format="tgz", success=True,
            output_path="/unpacked", original_size=4096,
            file_count=3, duration=0.5,
        )
        rendered = summary.render(stats)
        assert "### ✅ Decompress — `tgz`" in rendered
        assert "Extracted to" in rendered
        assert "/unpacked" in rendered
        assert "Compression ratio" not in rendered


class TestWrite:
    def test_writes_to_step_summary_file(self, tmp_path, monkeypatch):
        summary_file = tmp_path / "summary.md"
        monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary_file))
        assert summary.write(_compress_stats()) is True
        assert "Compression ratio" in summary_file.read_text()

    def test_appends_instead_of_overwriting(self, tmp_path, monkeypatch):
        summary_file = tmp_path / "summary.md"
        summary_file.write_text("existing\n")
        monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary_file))
        summary.write(_compress_stats())
        assert summary_file.read_text().startswith("existing\n")

    def test_disabled_writes_nothing(self, tmp_path, monkeypatch):
        summary_file = tmp_path / "summary.md"
        monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary_file))
        assert summary.write(_compress_stats(), enabled=False) is False
        assert not summary_file.exists()

    def test_no_env_var_writes_nothing(self, monkeypatch):
        monkeypatch.delenv("GITHUB_STEP_SUMMARY", raising=False)
        assert summary.write(_compress_stats()) is False

    def test_unwritable_path_is_not_fatal(self, tmp_path, monkeypatch):
        monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(tmp_path / "missing-dir" / "s.md"))
        assert summary.write(_compress_stats()) is False
