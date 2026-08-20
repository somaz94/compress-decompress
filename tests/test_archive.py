import tarfile
import zipfile

import archive


class TestListEntries:
    def test_list_zip_entries(self, tmp_archive_zip):
        entries = archive.list_entries(tmp_archive_zip, "zip")
        assert entries is not None
        assert any(name.endswith("file1.txt") for name in entries)

    def test_list_tar_entries(self, tmp_archive_tar):
        entries = archive.list_entries(tmp_archive_tar, "tar")
        assert entries is not None
        assert any(name.endswith("file1.txt") for name in entries)

    def test_unreadable_archive_returns_none(self, tmp_path):
        broken = tmp_path / "broken.zip"
        broken.write_text("not an archive")
        assert archive.list_entries(str(broken), "zip") is None

    def test_missing_archive_returns_none(self, tmp_path):
        assert archive.list_entries(str(tmp_path / "absent.tar"), "tar") is None


class TestCountFiles:
    def test_counts_files_only(self):
        assert archive.count_files(["a.txt", "dir/", "dir/b.txt"]) == 2

    def test_none_counts_zero(self):
        assert archive.count_files(None) == 0

    def test_empty_counts_zero(self):
        assert archive.count_files([]) == 0


class TestDirectoryMembersAcrossFormats:
    """tar reports a directory without a trailing slash, zip with one."""

    def _build(self, tmp_path):
        root = tmp_path / "d" / "sub"
        root.mkdir(parents=True)
        (tmp_path / "d" / "b.txt").write_text("x")
        (root / "a.txt").write_text("y")
        return tmp_path / "d"

    def test_tar_directories_are_not_counted_as_files(self, tmp_path):
        src = self._build(tmp_path)
        tar_path = tmp_path / "t.tar"
        with tarfile.open(tar_path, "w") as tf:
            tf.add(src, arcname="d")
        entries = archive.list_entries(str(tar_path), "tar")
        assert archive.count_files(entries) == 2

    def test_zip_and_tar_agree_on_the_same_tree(self, tmp_path):
        src = self._build(tmp_path)
        tar_path = tmp_path / "t.tar"
        with tarfile.open(tar_path, "w") as tf:
            tf.add(src, arcname="d")
        zip_path = tmp_path / "t.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("d/sub/", "")
            zf.write(src / "b.txt", "d/b.txt")
            zf.write(src / "sub" / "a.txt", "d/sub/a.txt")
        tar_count = archive.count_files(archive.list_entries(str(tar_path), "tar"))
        zip_count = archive.count_files(archive.list_entries(str(zip_path), "zip"))
        assert tar_count == zip_count == 2

    def test_directory_members_still_pass_the_traversal_check(self, tmp_path):
        src = self._build(tmp_path)
        tar_path = tmp_path / "t.tar"
        with tarfile.open(tar_path, "w") as tf:
            tf.add(src, arcname="d")
        entries = archive.list_entries(str(tar_path), "tar")
        assert archive.find_unsafe_entries(entries) == ([], [])


class TestPathSafety:
    def test_plain_entry_is_safe(self):
        assert archive.escapes_destination("dir/file.txt") is False

    def test_dot_segments_are_safe(self):
        assert archive.escapes_destination("./dir/./file.txt") is False

    def test_parent_within_bounds_is_safe(self):
        assert archive.escapes_destination("dir/../file.txt") is False

    def test_leading_parent_escapes(self):
        assert archive.escapes_destination("../evil.txt") is True

    def test_nested_parent_escapes(self):
        assert archive.escapes_destination("dir/../../evil.txt") is True

    def test_backslash_parent_escapes(self):
        assert archive.escapes_destination("..\\evil.txt") is True

    def test_absolute_posix_path(self):
        assert archive.is_absolute("/etc/passwd") is True

    def test_windows_drive_path(self):
        assert archive.is_absolute("C:/Windows/system32") is True

    def test_relative_path_is_not_absolute(self):
        assert archive.is_absolute("dir/file.txt") is False

    def test_find_unsafe_entries_splits_buckets(self):
        escaping, absolute = archive.find_unsafe_entries(
            ["ok.txt", "../evil.txt", "/etc/passwd"]
        )
        assert escaping == ["../evil.txt"]
        assert absolute == ["/etc/passwd"]

    def test_find_unsafe_entries_on_clean_archive(self):
        assert archive.find_unsafe_entries(["a.txt", "dir/b.txt"]) == ([], [])


class TestInspectionAgainstRealArchives:
    def test_zip_slip_archive_is_detected(self, tmp_path):
        malicious = tmp_path / "slip.zip"
        with zipfile.ZipFile(malicious, "w") as zf:
            zf.writestr("../escaped.txt", "owned")
        entries = archive.list_entries(str(malicious), "zip")
        escaping, _ = archive.find_unsafe_entries(entries)
        assert escaping == ["../escaped.txt"]

    def test_tar_slip_archive_is_detected(self, tmp_path):
        payload = tmp_path / "payload.txt"
        payload.write_text("owned")
        malicious = tmp_path / "slip.tar"
        with tarfile.open(malicious, "w") as tf:
            tf.add(payload, arcname="../escaped.txt")
        entries = archive.list_entries(str(malicious), "tar")
        escaping, _ = archive.find_unsafe_entries(entries)
        assert escaping == ["../escaped.txt"]
