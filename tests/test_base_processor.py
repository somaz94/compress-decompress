import os
import pytest
from base_processor import BaseProcessor
from exceptions import ValidationError, CompressError
from executor import ProcessResult


class TestBaseProcessor:
    def test_init_from_config(self, make_config):
        config = make_config(
            fail_on_error=True,
            verbose=True,
            dest="/output",
            destfilename="archive",
            exclude="*.log *.tmp",
        )
        bp = BaseProcessor(config)
        assert bp.fail_on_error is True
        assert bp.verbose is True
        assert bp.dest == "/output"
        assert bp.destfilename == "archive"
        assert bp.exclude == "*.log *.tmp"

    def test_init_effective_dest(self, make_config):
        config = make_config(dest="")
        bp = BaseProcessor(config)
        assert bp.dest != ""  # Should be cwd or GITHUB_WORKSPACE


class TestValidatePath:
    def test_valid_path(self, make_config, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("content")
        bp = BaseProcessor(make_config())
        assert bp.validate_path(str(f)) is True

    def test_invalid_path_fail_on_error(self, make_config):
        bp = BaseProcessor(make_config(fail_on_error=True))
        with pytest.raises(ValidationError, match="does not exist"):
            bp.validate_path("/nonexistent/path")

    def test_invalid_path_no_fail(self, make_config):
        bp = BaseProcessor(make_config(fail_on_error=False))
        assert bp.validate_path("/nonexistent/path") is False

    def test_broken_symlink_fail(self, make_config, tmp_path):
        link = tmp_path / "broken_link"
        link.symlink_to("/nonexistent/target")
        bp = BaseProcessor(make_config(fail_on_error=True))
        with pytest.raises(ValidationError, match="broken symbolic link"):
            bp.validate_path(str(link))

    def test_broken_symlink_no_fail(self, make_config, tmp_path):
        link = tmp_path / "broken_link2"
        link.symlink_to("/nonexistent/target2")
        bp = BaseProcessor(make_config(fail_on_error=False))
        assert bp.validate_path(str(link)) is False

    def test_valid_symlink(self, make_config, tmp_path):
        target = tmp_path / "target.txt"
        target.write_text("real")
        link = tmp_path / "link.txt"
        link.symlink_to(target)
        bp = BaseProcessor(make_config())
        assert bp.validate_path(str(link)) is True

    def test_strips_whitespace(self, make_config, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("content")
        bp = BaseProcessor(make_config())
        assert bp.validate_path(f"  {f}  ") is True


class TestPrepareDestination:
    def test_creates_directory(self, make_config, tmp_path):
        dest = tmp_path / "new_dir"
        config = make_config(dest=str(dest))
        bp = BaseProcessor(config)
        bp.dest = str(dest)
        bp.prepare_destination()
        assert dest.exists()

    def test_existing_directory_ok(self, make_config, tmp_path):
        bp = BaseProcessor(make_config(dest=str(tmp_path)))
        bp.dest = str(tmp_path)
        bp.prepare_destination()  # Should not raise


class TestHandleError:
    def test_fail_on_error_raises(self, make_config):
        bp = BaseProcessor(make_config(fail_on_error=True))
        with pytest.raises(CompressError, match="Operation failed"):
            bp.handle_error(RuntimeError("something broke"), "Operation")

    def test_no_fail_returns_result(self, make_config):
        bp = BaseProcessor(make_config(fail_on_error=False))
        result = bp.handle_error(RuntimeError("something broke"), "Operation")
        assert isinstance(result, ProcessResult)
        assert result.success is False


class TestParseExcludePatterns:
    def test_empty_exclude(self, make_config):
        bp = BaseProcessor(make_config(exclude=""))
        assert bp.parse_exclude_patterns() == []

    def test_single_pattern(self, make_config):
        bp = BaseProcessor(make_config(exclude="*.log"))
        assert bp.parse_exclude_patterns() == ["*.log"]

    def test_multiple_patterns(self, make_config):
        bp = BaseProcessor(make_config(exclude="*.log node_modules .git"))
        assert bp.parse_exclude_patterns() == ["*.log", "node_modules", ".git"]

    def test_extra_whitespace(self, make_config):
        bp = BaseProcessor(make_config(exclude="  *.log   *.tmp  "))
        assert bp.parse_exclude_patterns() == ["*.log", "*.tmp"]
