import os
import subprocess
import shlex
import pytest
from compress import Compressor, compress, _remap_runner_path
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

    @pytest.mark.parametrize("host_path, expected", [
        # The repo root maps to the workspace root.
        ("/home/runner/work/repo/repo", "/github/workspace"),
        # A sub-path must survive the remap. Collapsing it to the workspace
        # root makes the action archive the whole repository instead.
        ("/home/runner/work/repo/repo/dist", "/github/workspace/dist"),
        ("/home/runner/work/repo/repo/build/out", "/github/workspace/build/out"),
        # Not the <repo>/<repo> layout: ${{ runner.temp }} and _actions are
        # not mounted into the container, so the path is left alone and
        # validate_path reports it honestly instead of silently archiving
        # the whole workspace.
        ("/home/runner/work/_temp/build", "/home/runner/work/_temp/build"),
        ("/home/runner/work/a/b/c", "/home/runner/work/a/b/c"),
        ("/some/other/path", "/some/other/path"),
    ])
    def test_runner_path_keeps_the_sub_path(self, monkeypatch, host_path, expected):
        monkeypatch.setenv("GITHUB_WORKSPACE", "/github/workspace")
        assert _remap_runner_path(host_path) == expected

    def test_runner_path_unchanged_without_a_workspace(self, monkeypatch):
        monkeypatch.delenv("GITHUB_WORKSPACE", raising=False)
        assert _remap_runner_path("/home/runner/work/repo/repo/dist") == \
            "/home/runner/work/repo/repo/dist"


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
        assert path == os.path.join(os.getcwd(), "source.zip")

    def test_default_destination_without_root(self, make_config, tmp_source):
        config = make_config(
            source=str(tmp_source), format="zip",
            include_root="false", dest="",
        )
        c = Compressor(config)
        c.source = str(tmp_source)
        c.dest = os.getcwd()
        path = c._determine_destination_path("source", ".zip")
        assert path == os.path.join(os.getcwd(), "source.zip")

    @pytest.mark.parametrize("depth", ["direct-child", "nested"])
    def test_include_root_does_not_move_the_output(self, make_config, tmp_path, monkeypatch, depth):
        """
        Regression for #58: includeRoot decides what goes INSIDE the archive,
        never where the archive lands. With no `dest`, both values must land
        in the workspace root -- the reported bug put the includeRoot=false
        archive inside the source directory instead.

        cwd is moved onto the workspace on purpose: that is the action
        container's layout, and it is the only shape in which the bug fired.
        """
        monkeypatch.setenv("GITHUB_WORKSPACE", str(tmp_path))
        monkeypatch.chdir(tmp_path)
        source = tmp_path / "build" / "dist" if depth == "nested" else tmp_path / "output"
        source.mkdir(parents=True)

        paths = []
        for include_root in ("true", "false"):
            config = make_config(
                source=str(source), format="zip",
                include_root=include_root, dest="",
            )
            c = Compressor(config)
            c.source = str(source)
            paths.append(c._determine_destination_path("archive", ".zip"))

        assert paths[0] == paths[1] == str(tmp_path / "archive.zip")


class TestDestinationFilename:
    """`destfilename` and the format extension appended to it."""

    @staticmethod
    def _output_name(make_config, tmp_path, monkeypatch, destfilename, fmt, dedupe="true"):
        monkeypatch.setenv("GITHUB_WORKSPACE", str(tmp_path))
        source = tmp_path / "output"
        source.mkdir(exist_ok=True)
        config = make_config(
            source=str(source), format=fmt,
            include_root="false", dest="", destfilename=destfilename,
        )
        config.dedupe_extension = dedupe
        c = Compressor(config)
        c.source = str(source)
        c.get_compression_command()
        return os.path.basename(c.output_path)

    @pytest.mark.parametrize("destfilename, fmt, expected", [
        # The extension is appended when the name does not already carry it.
        ("archive", "zip", "archive.zip"),
        ("archive", "tgz", "archive.tgz"),
        # ...and not appended twice when it does. Writing `archive.zip` is the
        # natural thing to do and used to produce archive.zip.zip.
        ("archive.zip", "zip", "archive.zip"),
        ("archive.tgz", "tgz", "archive.tgz"),
        # A different extension is left alone -- it is part of the name.
        ("archive.tar", "zip", "archive.tar.zip"),
        # tgz is not treated as an alias of tar.gz, so this one still doubles.
        ("archive.tar.gz", "tgz", "archive.tar.gz.tgz"),
        # An extension with no stem would otherwise collapse to a dotfile.
        (".zip", "zip", ".zip.zip"),
    ])
    def test_extension_is_appended_at_most_once(
        self, make_config, tmp_path, monkeypatch, destfilename, fmt, expected
    ):
        assert self._output_name(make_config, tmp_path, monkeypatch, destfilename, fmt) == expected

    @pytest.mark.parametrize("suffix", ["", "/"])
    def test_a_trailing_slash_does_not_empty_the_name(
        self, make_config, tmp_path, monkeypatch, suffix
    ):
        """A trailing slash used to make basename empty, naming the archive ".zip"."""
        monkeypatch.setenv("GITHUB_WORKSPACE", str(tmp_path))
        source = tmp_path / "output"
        source.mkdir(exist_ok=True)
        config = make_config(
            source=str(source), format="zip", include_root="false", dest="",
        )
        c = Compressor(config)
        c.source = f"{source}{suffix}"
        c.get_compression_command()
        assert os.path.basename(c.output_path) == "output.zip"

    def test_default_name_comes_from_the_source(self, make_config, tmp_path, monkeypatch):
        """Not from the working directory, which is what the README used to claim."""
        monkeypatch.chdir(tmp_path)
        assert self._output_name(make_config, tmp_path, monkeypatch, "", "zip") == "output.zip"

    @pytest.mark.parametrize("dedupe, expected", [
        # dedupeExtension is the opt-out for the de-duplication above: false
        # restores the unconditional append.
        ("false", "archive.zip.zip"),
        ("true", "archive.zip"),
        # An unset value must not read as "off" -- the default is on.
        ("", "archive.zip"),
    ])
    def test_dedupe_extension_can_be_turned_off(
        self, make_config, tmp_path, monkeypatch, dedupe, expected
    ):
        name = self._output_name(make_config, tmp_path, monkeypatch, "archive.zip", "zip", dedupe)
        assert name == expected

    def test_dedupe_off_does_not_touch_a_name_without_the_extension(
        self, make_config, tmp_path, monkeypatch
    ):
        name = self._output_name(make_config, tmp_path, monkeypatch, "archive", "zip", "false")
        assert name == "archive.zip"


class TestIncludeHidden:
    """`includeHidden` must behave identically across every format."""

    @staticmethod
    def _cmd(make_config, tmp_source, fmt, include_root, include_hidden):
        config = make_config(
            source=str(tmp_source), format=fmt,
            include_root=include_root, include_hidden=include_hidden,
        )
        c = Compressor(config)
        c.source = str(tmp_source)
        return c._get_zip_command("/out/a.zip", "a") if fmt == "zip" \
            else c._get_tar_command(f"/out/a.{fmt}", "a")

    @pytest.mark.parametrize("fmt", ["zip", "tar", "tgz", "tbz2", "txz", "tzst"])
    @pytest.mark.parametrize("include_root", ["true", "false"])
    def test_on_by_default_adds_no_exclusion(self, make_config, tmp_source, fmt, include_root):
        cmd = self._cmd(make_config, tmp_source, fmt, include_root, "true")
        assert ".*" not in cmd

    @pytest.mark.parametrize("fmt", ["zip", "tar", "tgz", "tbz2", "txz", "tzst"])
    @pytest.mark.parametrize("include_root", ["true", "false"])
    def test_off_excludes_top_level_and_nested_dotfiles(
        self, make_config, tmp_source, fmt, include_root
    ):
        cmd = self._cmd(make_config, tmp_source, fmt, include_root, "false")
        prefix = f"{tmp_source.name}/" if include_root == "true" else ""
        assert f"{prefix}.*" in cmd
        assert "*/.*" in cmd

    @pytest.mark.parametrize("fmt", ["tar", "tgz", "tbz2", "txz", "tzst"])
    def test_tar_anchors_the_top_level_pattern(self, make_config, tmp_source, fmt):
        """
        A bare `.*` also matches the `.` that `-C <dir> .` archives, which
        empties the archive instead of dropping dotfiles.
        """
        cmd = self._cmd(make_config, tmp_source, fmt, "false", "false")
        assert "--exclude='./.*'" in cmd
        assert "--exclude='.*'" not in cmd

    def test_zip_does_not_anchor_the_top_level_pattern(self, make_config, tmp_source):
        """zip entries carry no `./` prefix, so the tar anchoring would miss."""
        cmd = self._cmd(make_config, tmp_source, "zip", "false", "false")
        assert "-x '.*'" in cmd

    def test_user_exclude_patterns_are_kept_alongside(self, make_config, tmp_source):
        config = make_config(
            source=str(tmp_source), format="zip",
            include_root="false", include_hidden="false", exclude="*.log",
        )
        c = Compressor(config)
        c.source = str(tmp_source)
        cmd = c._get_zip_command("/out/a.zip", "a")
        assert "*.log" in cmd and "'.*'" in cmd


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
        # `cp -a src/.` rather than `cp -r src/*`: the glob skips dotfiles and
        # exits non-zero on an empty source directory.
        assert "cp -a" in cmd
        assert "/*" not in cmd
        assert "-czf" in cmd

    @pytest.mark.parametrize("fmt, flag", [("tgz", "z"), ("tbz2", "j")])
    def test_the_generated_command_keeps_dotfiles(self, make_config, tmp_path, fmt, flag):
        """Executed for real: `cp -r src/*` silently dropped every dotfile."""
        source = tmp_path / "src"
        (source / "sub").mkdir(parents=True)
        (source / "visible.txt").write_text("v")
        (source / ".hidden").write_text("h")
        dest = tmp_path / f"out.{fmt}"

        config = make_config(source=str(source), format=fmt, include_root="false")
        c = Compressor(config)
        c.source = str(source)
        cmd = c._get_tar_command(str(dest), "out")
        assert subprocess.run(cmd, shell=True, capture_output=True).returncode == 0

        listed = subprocess.run(["tar", f"-t{flag}f", str(dest)],
                                capture_output=True, text=True).stdout
        assert "./.hidden" in listed.split()
        assert "./visible.txt" in listed.split()

    def test_the_generated_command_survives_an_empty_source(self, make_config, tmp_path):
        """`cp -r empty/*` exits 1, which aborted the && chain."""
        source = tmp_path / "empty"
        source.mkdir()
        dest = tmp_path / "out.tgz"

        config = make_config(source=str(source), format="tgz", include_root="false")
        c = Compressor(config)
        c.source = str(source)
        cmd = c._get_tar_command(str(dest), "out")
        assert subprocess.run(cmd, shell=True, capture_output=True).returncode == 0
        assert dest.exists()

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
        result = compress(config)
        checksum = result.checksum
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
        result = compress(config)
        output_path, checksum = result.output_path, result.checksum
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
        result = compress(config)
        output_path, checksum = result.output_path, result.checksum
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
        result = compress(config)
        output_path, checksum = result.output_path, result.checksum
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
        result = compress(config)
        output_path, checksum = result.output_path, result.checksum
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
        result = compress(config)
        output_path, checksum = result.output_path, result.checksum
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
        result = compress(config)
        output_path, checksum = result.output_path, result.checksum
        assert output_path
        assert checksum
        archives = list(dest.glob("*.zip"))
        assert len(archives) == 1


class TestZstdFormat:
    def test_tzst_uses_long_flag(self, make_config, tmp_source):
        config = make_config(source=str(tmp_source), format="tzst", include_root="true")
        c = Compressor(config)
        c.source = str(tmp_source)
        cmd = c._get_tar_command("/out/test.tzst", "test")
        assert "--zstd" in cmd
        assert "-cf" in cmd

    def test_tzst_without_root(self, make_config, tmp_source):
        config = make_config(source=str(tmp_source), format="tzst", include_root="false")
        c = Compressor(config)
        c.source = str(tmp_source)
        cmd = c._get_tar_command("/out/test.tzst", "test")
        assert "mkdir -p" in cmd
        assert "--zstd" in cmd

    def test_tzst_level_env(self, make_config, tmp_source):
        config = make_config(
            source=str(tmp_source), format="tzst", compression_level="9",
        )
        c = Compressor(config)
        assert "ZSTD_CLEVEL=9" in c._get_tar_level_env()

    def test_compress_tzst_integration(self, make_config, tmp_source, tmp_path):
        dest = tmp_path / "output"
        dest.mkdir()
        config = make_config(
            source=str(tmp_source), format="tzst",
            include_root="true", dest=str(dest),
        )
        result = compress(config)
        assert result
        assert result.checksum
        assert len(list(dest.glob("*.tzst"))) == 1

    def test_compress_tzst_without_root_integration(self, make_config, tmp_source, tmp_path):
        dest = tmp_path / "output"
        dest.mkdir()
        config = make_config(
            source=str(tmp_source), format="tzst",
            include_root="false", dest=str(dest),
        )
        result = compress(config)
        assert result
        assert result.output_path


class TestCompressStats:
    def test_stats_populated_on_success(self, make_config, tmp_source, tmp_path):
        dest = tmp_path / "output"
        dest.mkdir()
        config = make_config(source=str(tmp_source), format="zip", dest=str(dest))
        result = compress(config)
        assert result.command == "compress"
        assert result.format == "zip"
        assert result.success is True
        assert result.original_size > 0
        assert result.compressed_size > 0
        assert result.file_count == 3  # tmp_source holds three files
        assert result.duration >= 0

    def test_stats_empty_on_failure(self, make_config):
        config = make_config(source="/nonexistent", format="zip", fail_on_error=False)
        result = compress(config)
        assert not result
        assert result.output_path == ""
        assert result.checksum == ""
        assert result.file_count == 0

    def test_stats_file_count_for_glob(self, make_config, tmp_source, tmp_path):
        dest = tmp_path / "output"
        dest.mkdir()
        config = make_config(
            source=str(tmp_source / "*.txt"), format="zip", dest=str(dest),
        )
        result = compress(config)
        assert result.file_count == 2  # file1.txt and file2.txt, not the nested one


class TestStatsOnFailurePaths:
    def test_validation_failure_still_records_a_duration(self, make_config):
        result = compress(make_config(
            source="/nonexistent", format="zip", fail_on_error=False,
        ))
        assert not result
        assert result.duration >= 0
        assert result.original_size == 0

    def test_command_failure_reports_the_source_size(self, make_config, tmp_source,
                                                     tmp_path):
        """A failing command must not zero out what was already measured."""
        from unittest.mock import patch
        from executor import ProcessResult
        dest = tmp_path / "output"
        dest.mkdir()
        config = make_config(
            source=str(tmp_source), format="zip", dest=str(dest), fail_on_error=False,
        )
        with patch("compress.CommandExecutor.run",
                   return_value=ProcessResult(False, "boom")):
            result = compress(config)
        assert not result
        assert result.original_size > 0
        assert result.file_count == 3
