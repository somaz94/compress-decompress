import os
import sys
import pytest

# Add app directory to path so tests can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))


@pytest.fixture
def tmp_source(tmp_path):
    """Create a temporary source directory with test files"""
    src = tmp_path / "source"
    src.mkdir()
    (src / "file1.txt").write_text("Hello World")
    (src / "file2.txt").write_text("Test content")

    sub = src / "subdir"
    sub.mkdir()
    (sub / "file3.txt").write_text("Nested file")

    return src


@pytest.fixture
def tmp_archive_zip(tmp_path, tmp_source):
    """Create a test zip archive"""
    import shutil
    archive = shutil.make_archive(str(tmp_path / "test_archive"), 'zip', str(tmp_source))
    return archive


@pytest.fixture
def tmp_archive_tar(tmp_path, tmp_source):
    """Create a test tar archive"""
    import shutil
    archive = shutil.make_archive(str(tmp_path / "test_archive"), 'tar', str(tmp_source))
    return archive


@pytest.fixture
def make_config():
    """Factory fixture to create AppConfig instances"""
    from config import AppConfig

    def _make(
        command="compress",
        source="",
        format="zip",
        include_root="true",
        dest="",
        destfilename="",
        exclude="",
        verbose=False,
        fail_on_error=True,
        preserve_glob_structure="false",
        strip_prefix="",
        compression_level="",
    ):
        return AppConfig(
            command=command,
            source=source,
            format=format,
            include_root=include_root,
            dest=dest,
            destfilename=destfilename,
            exclude=exclude,
            verbose=verbose,
            fail_on_error=fail_on_error,
            preserve_glob_structure=preserve_glob_structure,
            strip_prefix=strip_prefix,
            compression_level=compression_level,
        )

    return _make
