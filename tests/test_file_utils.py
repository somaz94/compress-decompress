import os
import pytest
from file_utils import FileUtils


class TestStrToBool:
    def test_true_values(self):
        assert FileUtils.str_to_bool("true") is True
        assert FileUtils.str_to_bool("True") is True
        assert FileUtils.str_to_bool("TRUE") is True
        assert FileUtils.str_to_bool("yes") is True
        assert FileUtils.str_to_bool("1") is True

    def test_false_values(self):
        assert FileUtils.str_to_bool("false") is False
        assert FileUtils.str_to_bool("no") is False
        assert FileUtils.str_to_bool("0") is False
        assert FileUtils.str_to_bool("anything") is False

    def test_empty_and_none(self):
        assert FileUtils.str_to_bool("") is False
        assert FileUtils.str_to_bool(None) is False

    def test_default_value(self):
        assert FileUtils.str_to_bool("", default=True) is True
        assert FileUtils.str_to_bool(None, default=True) is True


class TestGetSize:
    def test_bytes(self):
        assert FileUtils.get_size(500) == "500.00 B"

    def test_kilobytes(self):
        assert FileUtils.get_size(2048) == "2.00 KB"

    def test_megabytes(self):
        assert FileUtils.get_size(1048576) == "1.00 MB"

    def test_gigabytes(self):
        assert FileUtils.get_size(1073741824) == "1.00 GB"

    def test_from_file_path(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("x" * 1024)
        result = FileUtils.get_size(str(f))
        assert "KB" in result

    def test_nonexistent_path(self):
        # Should return the number as-is since path doesn't exist
        result = FileUtils.get_size("/nonexistent/path")
        assert result == "Unknown size"


class TestGetPathSize:
    def test_file_size(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("Hello World")
        size = FileUtils.get_path_size(str(f))
        assert size == 11

    def test_directory_size(self, tmp_source):
        size = FileUtils.get_path_size(str(tmp_source))
        assert size > 0

    def test_symlink_size(self, tmp_path):
        f = tmp_path / "real.txt"
        f.write_text("content")
        link = tmp_path / "link.txt"
        link.symlink_to(f)
        size = FileUtils.get_path_size(str(link))
        assert size == 7


    def test_circular_symlink_no_hang(self, tmp_path):
        sub = tmp_path / "dir"
        sub.mkdir()
        (sub / "file.txt").write_text("content")
        (sub / "loop").symlink_to(str(sub))
        size = FileUtils.get_directory_size(str(sub))
        assert size > 0


class TestAdjustPath:
    def test_absolute_path_unchanged(self):
        path = "/absolute/path/to/file"
        assert FileUtils.adjust_path(path) == path

    def test_relative_path_made_absolute(self):
        result = FileUtils.adjust_path("relative/path")
        assert os.path.isabs(result)
        assert result.endswith("relative/path")

    def test_strips_whitespace(self):
        result = FileUtils.adjust_path("  /some/path  ")
        assert result == "/some/path"

    def test_github_workspace(self, monkeypatch):
        monkeypatch.setenv("GITHUB_WORKSPACE", "/github/workspace")
        result = FileUtils.adjust_path("src/main.py")
        assert result == "/github/workspace/src/main.py"


class TestIsGlobPattern:
    def test_star_pattern(self):
        assert FileUtils.is_glob_pattern("*.txt") is True

    def test_double_star(self):
        assert FileUtils.is_glob_pattern("**/*.py") is True

    def test_question_mark(self):
        assert FileUtils.is_glob_pattern("file?.txt") is True

    def test_brackets(self):
        assert FileUtils.is_glob_pattern("file[0-9].txt") is True

    def test_regular_path(self):
        assert FileUtils.is_glob_pattern("/some/path/file.txt") is False
        assert FileUtils.is_glob_pattern("relative/path") is False


class TestFindFilesByPattern:
    def test_find_txt_files(self, tmp_source):
        files = FileUtils.find_files_by_pattern("*.txt", str(tmp_source))
        assert len(files) == 2  # file1.txt, file2.txt (not subdir ones)

    def test_find_recursive(self, tmp_source):
        files = FileUtils.find_files_by_pattern("**/*.txt", str(tmp_source))
        assert len(files) == 3  # all txt files including subdir

    def test_no_matches(self, tmp_source):
        files = FileUtils.find_files_by_pattern("*.xyz", str(tmp_source))
        assert files == []


class TestCopyFilesToTempDirectory:
    def test_flatten_copy(self, tmp_path, tmp_source):
        dest = tmp_path / "flat"
        files = [
            str(tmp_source / "file1.txt"),
            str(tmp_source / "subdir" / "file3.txt"),
        ]
        FileUtils.copy_files_to_temp_directory(files, str(dest))
        assert (dest / "file1.txt").exists()
        assert (dest / "file3.txt").exists()

    def test_preserve_structure(self, tmp_path, tmp_source):
        dest = tmp_path / "structured"
        files = [
            str(tmp_source / "file1.txt"),
            str(tmp_source / "subdir" / "file3.txt"),
        ]
        # chdir to tmp_path so relpath resolves correctly
        original = os.getcwd()
        os.chdir(str(tmp_path))
        try:
            FileUtils.copy_files_to_temp_directory(
                files, str(dest), preserve_structure=True
            )
            assert dest.exists()
            copied = list(dest.rglob("*.txt"))
            assert len(copied) == 2
        finally:
            os.chdir(original)

    def test_duplicate_filename_handling(self, tmp_path):
        dest = tmp_path / "dup"
        src1 = tmp_path / "a"
        src1.mkdir()
        (src1 / "file.txt").write_text("a")
        src2 = tmp_path / "b"
        src2.mkdir()
        (src2 / "file.txt").write_text("b")

        FileUtils.copy_files_to_temp_directory(
            [str(src1 / "file.txt"), str(src2 / "file.txt")], str(dest)
        )
        # Should have file.txt and file_1.txt
        assert (dest / "file.txt").exists()
        assert (dest / "file_1.txt").exists()
