# Tests

Unit and integration tests for the Compress/Decompress Action.

<br/>

## Quick Start (Makefile)

```bash
cd /path/to/compress-decompress
make venv          # Create virtualenv and install dev dependencies
make test          # Run unit tests with coverage
make coverage      # Generate HTML coverage report (+ terminal output)
make clean         # Remove venv, cache, and build artifacts
make help          # Show all available commands
```

<br/>

## Manual Setup (without Makefile)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pytest pytest-cov
```

<br/>

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_compress.py -v

# Run specific test class
python -m pytest tests/test_compress.py::TestCompressIntegration -v

# Run with output capture disabled (useful for debugging)
python -m pytest tests/ -v -s
```

<br/>

## Coverage

```bash
# Terminal report with missing lines
python -m pytest tests/ --cov=app --cov-report=term-missing

# HTML report (opens in browser)
python -m pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html

# Exclude backwards-compat re-export file from coverage
python -m pytest tests/ --cov=app --cov-report=term-missing --cov-config=.coveragerc
```

<br/>

### Coverage Report

#### Terminal Output
Running `make test` or `make coverage` displays per-file coverage and missing lines in the terminal.

#### HTML Report
After running `make coverage`, the `htmlcov/index.html` file is generated.

```bash
make coverage
open htmlcov/index.html    # macOS
# xdg-open htmlcov/index.html  # Linux
```

Click on individual files in the browser to visually inspect uncovered lines.

<br/>

## Test Structure

| Test File | Module | Coverage |
|-----------|--------|----------|
| `test_config.py` | `config.py` | `AppConfig`, `CompressionFormat`, env var loading |
| `test_compress.py` | `compress.py` | Zip/tar command generation, exclude patterns, glob patterns, integration |
| `test_decompress.py` | `decompress.py` | Decompression commands, format validation, integration |
| `test_base_processor.py` | `base_processor.py` | Path validation, symlink handling, error handling, exclude parsing |
| `test_executor.py` | `executor.py` | `ProcessResult`, `CommandExecutor` success/failure/retry |
| `test_file_utils.py` | `file_utils.py` | `str_to_bool`, size calculation, path adjustment, glob, file copy |
| `test_main.py` | `main.py` | `ActionRunner` input validation, configuration display |
| `test_ui.py` | `ui.py` | Output formatting (header, section, success, error) |
| `test_exceptions.py` | `exceptions.py` | Exception hierarchy (`CompressError` > `ValidationError`, `CommandError`) |

<br/>

## Test Categories

<br/>

### Unit Tests
- Config defaults and env var parsing
- String-to-bool conversion
- File size formatting
- Glob pattern detection
- Path validation and symlink handling
- Exclude pattern parsing and formatting
- Shell command generation (zip, tar, tgz, tbz2)
- Exception hierarchy

<br/>

### Integration Tests
- End-to-end compression (zip, tar) with real files
- End-to-end decompression (zip, tar) with real archives
- Custom destination and filename
- Include/exclude root directory
- Glob pattern file matching

<br/>

## Fixtures

Defined in `conftest.py`:

| Fixture | Description |
|---------|-------------|
| `tmp_source` | Temporary directory with test files (`file1.txt`, `file2.txt`, `subdir/file3.txt`) |
| `tmp_archive_zip` | Pre-built zip archive from `tmp_source` |
| `tmp_archive_tar` | Pre-built tar archive from `tmp_source` |
| `make_config` | Factory to create `AppConfig` instances with custom parameters |
