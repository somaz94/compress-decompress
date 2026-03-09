# CLAUDE.md - compress-decompress

GitHub Action to compress or decompress files using various formats (zip, tar, tgz, tbz2, txz).

## Project Structure

```
app/
  main.py                    # Entrypoint
  config.py                  # Input configuration
  executor.py                # Command orchestration
  compress.py                # Compression logic
  decompress.py              # Decompression logic
  base_processor.py          # Shared processor base class
  file_utils.py              # File/path utilities
  exceptions.py              # Custom exception types
  ui.py                      # Output formatting
  app_logger.py              # Logging setup
tests/
  conftest.py                # pytest fixtures
  test_config.py
  test_compress.py
  test_decompress.py
  test_base_processor.py
  test_executor.py
  test_file_utils.py
  test_main.py
  test_ui.py
  test_exceptions.py
Dockerfile                   # Multi-stage (python:3.14-slim)
action.yml                   # GitHub Action definition (13 inputs, 2 outputs)
cliff.toml                   # git-cliff config for release notes
.coveragerc                  # Coverage configuration
```

## Build & Test

```bash
python -m pytest tests/ -v                                    # Run all tests
python -m pytest tests/ --cov=app --cov-report=term-missing   # Test with coverage
python -m pytest tests/ --cov=app --cov-report=html           # HTML coverage report
```

## Key Inputs

- **Required**: `command` (compress/decompress), `source`, `format` (zip/tar/tgz/tbz2/txz)
- **Options**: `dest`, `destfilename`, `exclude`, `includeRoot`, `preserveGlobStructure`, `stripPrefix`
- **Advanced**: `fail_on_error`, `compression_level`, `password`, `verbose`

## Outputs

`file_path`, `checksum`

## Workflow Structure

| Workflow | Name | Trigger |
|----------|------|---------|
| `ci.yml` | `Continuous Integration` | push(main), PR, dispatch |
| `release.yml` | `Create release` | tag push `v*` |
| `changelog-generator.yml` | `Generate changelog` | after release, PR merge, issue close |
| `use-action.yml` | `Smoke Test (Released Action)` | after release, dispatch |
| `linter.yml` | `Lint Codebase` | push(main), PR |
| `contributors.yml` | `Generator Contributors` | after changelog, dispatch |

### Workflow Chain
```
tag push v* → Create release
                ├→ Smoke Test (Released Action)
                └→ Generate changelog → Generator Contributors
```

### CI Structure
```
unit-tests → build-and-push-docker → integration tests → ci-result
```

## Conventions

- **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `ci:`, `chore:`)
- **Branches**: `main` (production), `test` (integration tests)
- **Secrets**: `PAT_TOKEN` (cross-repo ops), `GITHUB_TOKEN` (changelog, releases)
- **Docker**: Multi-stage build, python:3.14-slim base
- **Comments**: English only
- **Testing**: pytest with conftest.py fixtures, .coveragerc for config
- **Release**: `git switch` (not `git checkout`), git-cliff for RELEASE.md
- **cliff.toml**: Skip `^Merge`, `^Update changelog`, `^Auto commit`
- **paths-ignore**: `.github/workflows/**`, `**/*.md`, `backup/**`
- Do NOT commit directly - recommend commit messages only
