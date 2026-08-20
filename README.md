# Compress-Decompress Action

<!-- [![GitHub Super-Linter](https://github.com/somaz94/compress-decompress/actions/workflows/linter.yml/badge.svg)](https://github.com/somaz94/compress-decompress) -->
![CI](https://github.com/somaz94/compress-decompress/actions/workflows/ci.yml/badge.svg)
[![License](https://img.shields.io/github/license/somaz94/compress-decompress)](https://github.com/somaz94/compress-decompress)
![Latest Tag](https://img.shields.io/github/v/tag/somaz94/compress-decompress)
![Top Language](https://img.shields.io/github/languages/top/somaz94/compress-decompress?color=green&logo=python&logoColor=blue)
[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-Compress/Decompress-blue?logo=github)](https://github.com/marketplace/actions/compress-decompress)

<br/>

## Description

A single GitHub Action to **compress and decompress** files in your CI/CD
workflow — with **password-protected zip encryption**, **verified SHA256
checksums**, a **job summary**, and **six archive formats** (`zip`, `tar`,
`tgz`, `tbz2`, `txz`, `tzst`) in one step. Use it to package build artifacts,
encrypt release bundles, or unpack downloaded archives without hand-writing
`tar`/`zip` shell commands. Glob patterns, tunable compression levels, exclude
filters, and path stripping are all built in.

**Key Features:**
- **Six Archive Formats** - `zip`, `tar`, `tgz`, `tbz2`, `txz`, and `tzst` (zstd) from one action
- **Job Summary** - Sizes, ratio, file count, duration, and checksum rendered on the run page, no extra step
- **Rich Outputs** - `checksum`, `original_size`, `compressed_size`, `compression_ratio`, `file_count`, `duration`
- **Verified Decompression** - Pass `verify_checksum` and a tampered or truncated archive is rejected before anything is written to disk
- **Zip-Slip Protection** - Archives whose entries would escape the destination directory are refused
- **Password-Protected Zip** - Encrypt and decrypt `zip` archives with a secret, kept masked in the log
- **Compression Level Control** - Tune from `0` (store only) to `9` (maximum) for size vs. speed
- **Glob Pattern Support** - Match multiple files with patterns like `**/*.doc`
- **Symbolic Link Support** - Automatically follows symlinks (Bazel, Buck, and build tool integration)
- **Path Stripping** - Remove path prefixes while preserving directory structure
- **Flexible Options** - Custom destinations, exclude patterns, and root control

<br/>

## Inputs

| Input         | Description                                                                                                      | Required | Default |
| ------------- | ---------------------------------------------------------------------------------------------------------------- | -------- | ------- |
| `command`     | The operation to perform. It can be either "compress" or "decompress"                                            | Yes      | -       |
| `source`      | The source directory, file, or glob pattern to compress or decompress. Supports glob patterns like `**/*.doc` to match multiple files. | Yes      | -       |
| `dest`        | The destination directory for the output. If not provided, it defaults to the current working directory. | No       | -       |
| `destfilename` | The destination filename for the output (extension is appended depending on the format). If not provided, it defaults to the current working directory's name. | No       | -       |
| `exclude` | Filename (or pattern) to exclude from compression process. | No       | -       |
| `format`      | The compression format to use. Supported formats are `zip`, `tar`, `tgz`, `tbz2`, `txz`, and `tzst`.              | Yes      | -       |
| `includeRoot` | Whether to include the root folder itself in the compressed file.                                                | No       | yes     |
| `preserveGlobStructure` | When using glob patterns, preserve the directory structure in the archive. If false, all matched files are flattened to the root level. | No       | false   |
| `stripPrefix` | Remove this prefix from file paths when preserving directory structure. Works only with glob patterns and `preserveGlobStructure: true`. Example: `'src/'` changes `src/app/main.py` to `app/main.py` in the archive. | No       | ""      |
| `fail_on_error` | Whether to fail the action if compression/decompression fails.                                                 | No       | true    |
| `compression_level` | Compression level from `0` (store only) to `9` (maximum). Applies to `zip`, `tgz`, `tbz2`, `txz`, and `tzst`. | No   | -       |
| `password`    | Password for `zip` encryption/decryption. Pass it via a secret. Only applies to the `zip` format.                | No       | ""      |
| `verbose`     | Enable verbose logging for debugging purposes.                                                                   | No       | false   |
| `verify_checksum` | Expected SHA256 of the archive. Decompression aborts **before extracting anything** when it does not match. Decompress only. | No | ""      |
| `path_traversal_check` | Reject archives whose entries would extract outside the destination directory (zip slip). Decompress only. | No  | true    |
| `step_summary` | Write the result table to the workflow job summary (`$GITHUB_STEP_SUMMARY`).                                    | No       | true    |

<br/>

## Outputs

| Output              | Description                                                                  |
| ------------------- | ---------------------------------------------------------------------------- |
| `file_path`         | The path to the compressed archive, or the directory files were extracted to. |
| `checksum`          | SHA256 checksum of the compressed archive (compress operation only).          |
| `original_size`     | Size in bytes of the source (compress) or of the archive (decompress).        |
| `compressed_size`   | Size in bytes of the produced archive (compress operation only).              |
| `compression_ratio` | Percentage of the original size saved, e.g. `75.0` (compress operation only). |
| `file_count`        | Number of files compressed, or entries extracted.                             |
| `duration`          | Seconds the operation took, e.g. `1.42`.                                      |

<br/>

## Usage

You can use this action in your GitHub workflow by specifying the action with
its required inputs.

<br/>

## Documentation

### Comprehensive Guides:
- [Glob Pattern Guide](docs/GLOB_PATTERNS.md) - Match multiple files with patterns like `**/*.doc`
- [Advanced Usage Guide](docs/ADVANCED_USAGE.md) - Custom paths, exclude patterns, matrix strategies, and more
- [Troubleshooting Guide](docs/TROUBLESHOOTING.md) - Solutions for common issues and debugging tips
- [Testing Guide](tests/README.md) - Test setup, structure, and running tests locally

<br/>

## Example Workflows

### Job Summary at a Glance

Every run writes its result to the workflow **job summary**, so the archive
size, ratio, and checksum are on the run page without opening the step log —
nothing to configure:

> ### ✅ Compress — `tgz`
>
> | | |
> | --- | --- |
> | **Archive** | `dist/release.tgz` |
> | **Format** | `tgz` |
> | **Original size** | 42.60 MB |
> | **Compressed size** | 8.10 MB |
> | **Compression ratio** | 81.0% |
> | **Files** | 1204 |
> | **Duration** | 2.13s |
> | **SHA256** | `9f2c…` |

Set `step_summary: 'false'` to turn it off.

<br/>

### Using the Outputs

Sizes, ratio, file count, and duration are exposed as step outputs, so a later
step can gate on them or report them:

```yaml
- name: Compress Build Output
  id: pack
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./dist
    format: tgz
    dest: ./artifacts

- name: Report
  run: |
    echo "archive:  ${{ steps.pack.outputs.file_path }}"
    echo "files:    ${{ steps.pack.outputs.file_count }}"
    echo "size:     ${{ steps.pack.outputs.compressed_size }} bytes"
    echo "ratio:    ${{ steps.pack.outputs.compression_ratio }}%"
    echo "took:     ${{ steps.pack.outputs.duration }}s"
    echo "sha256:   ${{ steps.pack.outputs.checksum }}"

- name: Fail On A Suspiciously Small Archive
  if: ${{ fromJSON(steps.pack.outputs.file_count) < 10 }}
  run: exit 1
```

<br/>

### Verified Decompression

Pass the SHA256 you expect and the archive is checked **before a single file is
written**. A mismatch fails the step with the expected and actual digests:

```yaml
- name: Download Release Bundle
  run: curl -sSLo bundle.tgz "$BUNDLE_URL"

- name: Unpack Only If It Matches
  uses: somaz94/compress-decompress@v1
  with:
    command: decompress
    source: ./bundle.tgz
    format: tgz
    dest: ./unpacked
    verify_checksum: ${{ secrets.BUNDLE_SHA256 }}
```

The pair of steps below is the round trip — the `checksum` output of a compress
step feeds the `verify_checksum` input of the decompress step:

```yaml
- name: Compress
  id: pack
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./dist
    format: zip

- name: Decompress With Verification
  uses: somaz94/compress-decompress@v1
  with:
    command: decompress
    source: ${{ steps.pack.outputs.file_path }}
    format: zip
    dest: ./unpacked
    verify_checksum: ${{ steps.pack.outputs.checksum }}
```

Independently of `verify_checksum`, decompression refuses archives whose entries
would extract **outside** the destination directory (`../../etc/cron.d/evil`, the
"zip slip" pattern). Set `path_traversal_check: 'false'` to opt out.

<br/>

### Faster Compression With zstd

`tzst` (`tar` + zstd) compresses close to `tgz` ratios at a fraction of the
time, which is what you want for a cache or a large build artifact:

```yaml
- name: Compress Build Cache
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./build-cache
    format: tzst
    compression_level: '3'
    dest: ./artifacts
```

| Format | Codec  | Typical use                                   |
| ------ | ------ | --------------------------------------------- |
| `zip`  | deflate | Cross-platform sharing, optional password     |
| `tar`  | none   | Fast bundling when the payload is already compressed |
| `tgz`  | gzip   | The safe default, readable everywhere         |
| `tbz2` | bzip2  | Smaller than gzip, noticeably slower          |
| `txz`  | xz     | Smallest output, slowest to produce           |
| `tzst` | zstd   | Near-gzip size at much higher speed           |

<br/>

### Custom Destination and Filename

This example demonstrates how to use custom destination and filename options:

```yaml
name: Compress Files with Custom Path

on: [push]

jobs:
  compress-job:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Compress Directory
        uses: somaz94/compress-decompress@v1
        with:
          command: compress
          source: ./data-folder
          format: zip
          dest: './custom_output'
          destfilename: 'my_archive'

      - name: Upload Artifact
        uses: actions/upload-artifact@v4
        with:
          name: compressed-data
          path: ./custom_output/my_archive.zip
```

<br/>

### Using Exclude Patterns

Exclude specific files or directories from compression:

```yaml
- name: Compress Repository Excluding Git Files
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: .
    format: zip
    dest: './artifacts'
    destfilename: 'repo-backup'
    exclude: '.git .github node_modules *.log'
```

#### Common exclusions:
- Version control: `.git .svn`
- Dependencies: `node_modules vendor`
- Temporary files: `*.log *.tmp`

📖 **[View Advanced Usage Guide →](docs/ADVANCED_USAGE.md)**

<br/>

### Using Glob Patterns

This action supports glob patterns for matching multiple files across your repository. This is useful when you need to archive specific file types without compressing entire directories.

```yaml
- name: Compress All Documentation Files
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: '**/*.md'
    format: zip
    dest: './artifacts'
    destfilename: 'all-docs'
```

#### Common Patterns:
- `**/*.ext` - All files with extension in all subdirectories
- `dir/**/*.ext` - All files with extension in specific directory
- `**/*.{ext1,ext2}` - Multiple file types

#### Key Behaviors:
- Files are collected into a flattened archive structure by default
- Use `preserveGlobStructure: true` to maintain directory structure
- Use `stripPrefix` to remove path prefixes (e.g., `'src/'` removes src/ from all paths)
- No matches will fail by default (use `fail_on_error: false` to override)
- Enable `verbose: true` to see matched files

#### Example with preserved structure:
```yaml
- name: Archive Logs with Directory Structure
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: '**/*.log'
    format: zip
    preserveGlobStructure: true  # Preserves dir/subdir1/file.log structure
```

#### Example with stripped prefix:
```yaml
- name: Archive Source Files Without Project Root
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: 'project/src/**/*.ts'
    format: zip
    preserveGlobStructure: true
    stripPrefix: 'project/'  # Changes project/src/app/main.ts to src/app/main.ts
```

📖 **[View Complete Glob Pattern Guide →](docs/GLOB_PATTERNS.md)**

<br/>

### Basic Compression and Decompression

#### Compress a directory:
```yaml
- name: Compress Directory
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./data-folder
    format: zip
```

#### Decompress an archive:
```yaml
- name: Decompress Archive
  uses: somaz94/compress-decompress@v1
  with:
    command: decompress
    source: ./data-folder.zip
    format: zip
    dest: './unpacked'
```

<br/>

## Troubleshooting

<br/>

#### Common Issues:

<details>
<summary>Compression fails with "Source not found"?</summary>

1. Verify source path exists: `ls -la ./data-folder`
2. Use absolute paths: `${{ github.workspace }}/data-folder`
3. Check workspace state: `ls -la ${{ github.workspace }}`
4. See [Troubleshooting Guide](docs/TROUBLESHOOTING.md#compression-issues)

</details>

<details>
<summary>Glob pattern not matching files?</summary>

1. Verify files exist: `find . -name "*.doc"`
2. Enable verbose mode: `verbose: true`
3. Check pattern syntax: Use single quotes `'**/*.doc'`
4. See [Glob Pattern Guide](docs/GLOB_PATTERNS.md#troubleshooting)

</details>

<details>
<summary>Archive size is too large?</summary>

1. Use exclude patterns: `exclude: 'node_modules .git *.log'`
2. Use better compression: `format: tbz2` instead of `zip`
3. Split into multiple archives
4. See [Troubleshooting Guide](docs/TROUBLESHOOTING.md#archive-size-is-too-large)

</details>

<details>
<summary>Exclude patterns not working?</summary>

**Correct syntax** (space-separated):
```yaml
exclude: 'node_modules .git *.log'
```

**Incorrect** (comma-separated):
```yaml
exclude: 'node_modules,.git,*.log'  # Wrong!
```

See [Advanced Usage - Exclude Patterns](docs/ADVANCED_USAGE.md#using-exclude-patterns)

</details>

<details>
<summary>Decompression fails with "Checksum mismatch"?</summary>

The archive on disk is not the one the digest was taken from — it was re-created,
truncated mid-download, or tampered with.

1. Recompute the digest of what you actually have: `sha256sum ./bundle.tgz`
2. Make sure the digest was taken from the **compressed archive**, not from its contents
3. When chaining two steps, pass `${{ steps.<compress-step>.outputs.checksum }}` directly
4. Nothing was extracted — the check runs before any file is written

</details>

<details>
<summary>Decompression fails with "Unsafe archive"?</summary>

The archive contains an entry that would be written outside `dest`
(`../../something`), which is the "zip slip" pattern. Inspect it before trusting it:

```bash
unzip -l archive.zip     # or: tar -tf archive.tgz
```

If the layout is intentional and the source is trusted, opt out with
`path_traversal_check: 'false'`.

</details>

<details>
<summary>Nothing appears in the job summary?</summary>

1. The summary is written on `compress` and `decompress` alike — check the step actually ran
2. `step_summary: 'false'` disables it
3. Job summaries are a GitHub-hosted/self-hosted runner feature; on a runner without
   `$GITHUB_STEP_SUMMARY` the action skips it silently and the step still succeeds

</details>

[→ See full troubleshooting guide](docs/TROUBLESHOOTING.md)

<br/>

## Contributing

<br/>

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes and test locally
4. Commit: `git commit -am "feat: Add new feature"`
5. Push and create a Pull Request

### Running Tests

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pytest
python -m pytest tests/ -v
```

[→ See full testing guide](tests/README.md) | [→ See development and testing guide](docs/ADVANCED_USAGE.md)

<br/>

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<br/>

## Support

- **Issues**: [GitHub Issues](https://github.com/somaz94/compress-decompress/issues)
- **Discussions**: [GitHub Discussions](https://github.com/somaz94/compress-decompress/discussions)
- **Documentation**: [Full Documentation](docs/)

<br/>

## Contributors

Thanks to all contributors:

<a href="https://github.com/somaz94/compress-decompress/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=somaz94/compress-decompress" />
</a>

---

<br/>

## Star History
<picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=somaz94/compress-decompress&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=somaz94/compress-decompress&type=date&legend=top-left" />
   <img alt="Compress-Decompress Star History Chart" src="https://api.star-history.com/svg?repos=somaz94/compress-decompress&type=date&legend=top-left" />
</picture>

---

<div align="center">

**Made with efficiency for GitHub Actions workflows**

[Documentation](docs/) | [Examples](docs/ADVANCED_USAGE.md) | [Troubleshooting](docs/TROUBLESHOOTING.md)

</div>
