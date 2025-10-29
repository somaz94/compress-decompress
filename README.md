# Compress-Decompress Action

<!-- [![GitHub Super-Linter](https://github.com/somaz94/compress-decompress/actions/workflows/linter.yml/badge.svg)](https://github.com/somaz94/compress-decompress) -->
![CI](https://github.com/somaz94/compress-decompress/actions/workflows/ci.yml/badge.svg)
[![License](https://img.shields.io/github/license/somaz94/compress-decompress)](https://github.com/somaz94/compress-decompress)
![Latest Tag](https://img.shields.io/github/v/tag/somaz94/compress-decompress)
![Top Language](https://img.shields.io/github/languages/top/somaz94/compress-decompress?color=green&logo=python&logoColor=blue)
[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-Compress/Decompress-blue?logo=github)](https://github.com/marketplace/actions/compress-decompress)

## Description

This GitHub Action provides the functionality to compress or decompress files
using various compression formats including `zip`, `tar`, `tgz`, and `tbz2`. It
is designed to be easy to use within GitHub workflows for handling file
compression and decompression tasks efficiently.

**Key Features:**
- **Glob Pattern Support** - Match multiple files with patterns like `**/*.doc`
- **Symbolic Link Support** - Automatically follows symlinks (Bazel, Buck, and build tool integration)
- **Path Stripping** - Remove path prefixes while preserving directory structure
- **Multiple Formats** - Support for zip, tar, tgz, and tbz2
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
| `format`      | The compression format to use. Supported formats are `zip`, `tar`, `tgz`, and `tbz2`.                            | Yes      | -       |
| `includeRoot` | Whether to include the root folder itself in the compressed file.                                                | No       | yes     |
| `preserveGlobStructure` | When using glob patterns, preserve the directory structure in the archive. If false, all matched files are flattened to the root level. | No       | false   |
| `stripPrefix` | Remove this prefix from file paths when preserving directory structure. Works only with glob patterns and `preserveGlobStructure: true`. Example: `'src/'` changes `src/app/main.py` to `app/main.py` in the archive. | No       | ""      |
| `fail_on_error` | Whether to fail the action if compression/decompression fails.                                                 | No       | true    |
| `verbose`     | Enable verbose logging for debugging purposes.                                                                   | No       | false   |

<br/>

## Outputs

| Output      | Description                                      |
| ----------- | ------------------------------------------------ |
| `file_path` | The path to the compressed or decompressed file. |

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

<br/>

## Example Workflows

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

**Common exclusions:**
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

**Common Patterns:**
- `**/*.ext` - All files with extension in all subdirectories
- `dir/**/*.ext` - All files with extension in specific directory
- `**/*.{ext1,ext2}` - Multiple file types

**Key Behaviors:**
- Files are collected into a flattened archive structure by default
- Use `preserveGlobStructure: true` to maintain directory structure
- Use `stripPrefix` to remove path prefixes (e.g., `'src/'` removes src/ from all paths)
- No matches will fail by default (use `fail_on_error: false` to override)
- Enable `verbose: true` to see matched files

**Example with preserved structure:**
```yaml
- name: Archive Logs with Directory Structure
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: '**/*.log'
    format: zip
    preserveGlobStructure: true  # Preserves dir/subdir1/file.log structure
```

**Example with stripped prefix:**
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

**Compress a directory:**
```yaml
- name: Compress Directory
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./data-folder
    format: zip
```

**Decompress an archive:**
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

[→ See development and testing guide](docs/ADVANCED_USAGE.md)

<br/>

## License

This project is licensed under the [MIT License](LICENSE) file for details.

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

<div align="center">

**Made with efficiency for GitHub Actions workflows**

[Documentation](docs/) | [Examples](docs/ADVANCED_USAGE.md) | [Troubleshooting](docs/TROUBLESHOOTING.md)

</div>
