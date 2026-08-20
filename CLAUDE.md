# CLAUDE.md - compress-decompress

GitHub Action to compress or decompress files using various formats (zip, tar, tgz, tbz2, txz, tzst).

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
  archive.py                 # Archive inspection (entry listing, zip-slip detection)
  stats.py                   # OperationStats: the metrics behind the action outputs
  summary.py                 # $GITHUB_STEP_SUMMARY rendering
  masking.py                 # Secret masking for logs and error messages
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
  test_archive.py
  test_stats.py
  test_summary.py
  test_masking.py
Dockerfile                   # Multi-stage (python:3.14-slim)
action.yml                   # GitHub Action definition (16 inputs, 7 outputs)
cliff.toml                   # git-cliff config for release notes
.coveragerc                  # Coverage configuration
```

## Build & Test

```bash
make venv          # Create virtualenv and install dev dependencies
make test          # Run unit tests with coverage
make coverage      # Generate HTML coverage report
make clean         # Remove venv, cache, and build artifacts
make help          # Show all available commands
```

## Key Inputs

- **Required**: `command` (compress/decompress), `source`, `format` (zip/tar/tgz/tbz2/txz/tzst)
- **Options**: `dest`, `destfilename`, `exclude`, `includeRoot`, `preserveGlobStructure`, `stripPrefix`
- **Advanced**: `fail_on_error`, `compression_level`, `password`, `verbose`
- **Integrity**: `verify_checksum`, `path_traversal_check`, `step_summary`

## Outputs

`file_path`, `checksum`, `original_size`, `compressed_size`, `compression_ratio`,
`file_count`, `duration`

## Workflow Structure

| Workflow | Name | Trigger |
|----------|------|---------|
| `ci.yml` | `Continuous Integration` | push(main), PR, dispatch |
| `release.yml` | `Create release` | tag push `v*` |
| `changelog-generator.yml` | `Generate changelog` | after release, PR merge, issue close |
| `use-action.yml` | `Smoke Test (Released Action)` | after release, dispatch |
| `contributors.yml` | `Generator Contributors` | after changelog, dispatch |

### Workflow Chain
```
tag push v* → Create release
                ├→ Smoke Test (Released Action)
                └→ Generate changelog → Generator Contributors
```

### CI Structure
```
unit-tests ─┐
            ├→ ci-result
integration jobs (uses: ./, runs the PUBLISHED image) ─┤
test-image-from-source (builds the Dockerfile, runs the BRANCH code) ─┘
```

Note: `uses: ./` resolves `action.yml`, which pins a published image — the
integration jobs therefore test the released action, not the branch.
`test-image-from-source` is the job that exercises the code under review.

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
