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

<br/>

## Inputs

| Input         | Description                                                                                                      | Required | Default |
| ------------- | ---------------------------------------------------------------------------------------------------------------- | -------- | ------- |
| `command`     | The operation to perform. It can be either "compress" or "decompress"                                            | Yes      | -       |
| `source`      | The source directory or file to compress or decompress.                                                          | Yes      | -       |
| `dest`        | The destination directory for the output. If not provided, it defaults to the current working directory. | No       | -       |
| `destfilename` | The destination filename for the output (extension is appended depending on the format). If not provided, it defaults to the current working directory's name. | No       | -       |
| `exclude` | Filename (or pattern) to exclude from compression process. | No       | -       |
| `format`      | The compression format to use. Supported formats are `zip`, `tar`, `tgz`, and `tbz2`.                            | Yes      | -       |
| `includeRoot` | Whether to include the root folder itself in the compressed file.                                                | No       | yes     |
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

## Example Workflow

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

This example demonstrates how to exclude specific files or directories from the compression:

```yaml
name: Compress Files with Exclusions

on: [push]

jobs:
  compress-job:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Compress Repository Excluding Git Files
        uses: somaz94/compress-decompress@v1
        with:
          command: compress
          source: .
          format: zip
          dest: './artifacts'
          destfilename: 'repo-backup'
          exclude: '.git .github node_modules *.log'

      - name: Upload Artifact
        uses: actions/upload-artifact@v4
        with:
          name: repo-backup
          path: ./artifacts/repo-backup.zip
```

<br/>

### Using Glob Patterns

This action supports glob patterns for matching multiple files across your repository. This is particularly useful when you need to archive specific file types or patterns without compressing entire directories.

<br/>

#### Basic Glob Pattern Example

```yaml
name: Compress Files by Pattern

on: [push]

jobs:
  compress-pattern:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Compress All Documentation Files
        uses: somaz94/compress-decompress@v1
        with:
          command: compress
          source: '**/*.doc'
          format: zip
          dest: './artifacts'
          destfilename: 'all-docs'

      - name: Upload Artifact
        uses: actions/upload-artifact@v4
        with:
          name: documentation-archive
          path: ./artifacts/all-docs.zip
```

<br/>

#### Advanced Glob Pattern Examples

**1. Compress All Markdown Files:**
```yaml
- name: Archive All Markdown Documentation
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: '**/*.md'
    format: tgz
    dest: './archives'
    destfilename: 'documentation'
```

**2. Compress Files from Specific Directory:**
```yaml
- name: Archive Source Files Only
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: 'src/**/*.py'
    format: zip
    dest: './backups'
    destfilename: 'python-sources'
```

**3. Compress Multiple File Types:**
```yaml
- name: Archive Configuration Files
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: '**/*.{yml,yaml,json,toml}'
    format: tar
    dest: './configs'
    destfilename: 'all-configs'
```

**4. Archive Log Files:**
```yaml
- name: Collect and Archive Logs
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: 'logs/**/*.log'
    format: tgz
    dest: './archived-logs'
    destfilename: 'application-logs'
```

**5. Single Directory Wildcard:**
```yaml
- name: Archive Top-Level Text Files
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: '*.txt'
    format: zip
    dest: './output'
    destfilename: 'text-files'
```

**6. Nested Path Pattern:**
```yaml
- name: Archive Test Results
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: 'tests/**/results/*.xml'
    format: zip
    dest: './test-archives'
    destfilename: 'test-results'
```

**7. Archive Images:**
```yaml
- name: Backup All Images
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: '**/*.{jpg,jpeg,png,gif,svg}'
    format: zip
    dest: './image-backups'
    destfilename: 'all-images'
```

**8. Archive Build Artifacts:**
```yaml
- name: Archive Build Output
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: 'dist/**/*.js'
    format: tgz
    dest: './releases'
    destfilename: 'build-artifacts'
```

<br/>

#### Supported Glob Patterns

| Pattern | Description | Example Match |
|---------|-------------|---------------|
| `**/*.ext` | All files with extension in all subdirectories | `docs/readme.md`, `src/test/file.md` |
| `*.ext` | All files with extension in current directory | `readme.txt`, `notes.txt` |
| `dir/**/*.ext` | All files with extension in specific directory tree | `src/utils/helper.py`, `src/main.py` |
| `**/filename.ext` | Specific filename in all subdirectories | `config.json`, `settings/config.json` |
| `dir/*.ext` | Files in specific directory (non-recursive) | `src/main.py` (not `src/sub/test.py`) |
| `**/*.{ext1,ext2}` | Multiple extensions in all subdirectories | `file.jpg`, `image.png` |

<br/>

#### How Glob Patterns Work

When using glob patterns, the action:

1. **Searches for Matches**: Recursively scans the workspace for files matching the pattern
2. **Collects Files**: Gathers all matched files into a temporary directory
3. **Flattens Structure**: Places all files at the root of the archive (no subdirectories)
4. **Creates Archive**: Compresses the collected files into a single archive
5. **Cleans Up**: Automatically removes temporary files after compression

<br/>

#### Important Notes on Glob Patterns

⚠️ **Pattern Behavior:**
- All matched files are collected and compressed into a single archive
- The directory structure is **flattened** - all files are placed at the root of the archive
- File name conflicts are handled automatically with numeric suffixes
- The `includeRoot` option is automatically handled

⚠️ **Error Handling:**
- If no files match the pattern, the action will **fail by default**
- Use `fail_on_error: false` to allow workflows to continue when no matches are found
- Enable `verbose: true` to see which files are being matched

⚠️ **Performance Considerations:**
- Glob patterns are processed from the current working directory
- Large pattern matches may take time to process and copy
- Consider using more specific patterns for better performance

<br/>

#### Real-World Glob Pattern Use Cases

**Backup Configuration Files:**
```yaml
- name: Backup All Config Files
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: '**/*.{conf,cfg,ini,config}'
    format: tgz
    dest: './config-backups'
    destfilename: 'configs-backup'
```

**Archive Documentation:**
```yaml
- name: Create Documentation Archive
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: '**/*.{md,rst,adoc}'
    format: zip
    dest: './docs-archive'
    destfilename: 'documentation'
```

**Collect Test Coverage Reports:**
```yaml
- name: Archive Coverage Reports
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: 'coverage/**/*.{html,xml,json}'
    format: zip
    dest: './test-reports'
    destfilename: 'coverage-reports'
```

**Backup Database Dumps:**
```yaml
- name: Archive Database Backups
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: 'backups/**/*.{sql,dump}'
    format: tgz
    dest: './db-archives'
    destfilename: 'database-backups'
```

<br/>

### includeRoot: true(default)

This example demonstrates how to use the Compress-Decompress action to compress
a directory:

```yaml
name: Compress Files

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

      - name: Upload Artifact
        uses: actions/upload-artifact@v4
        with:
          name: compressed-data
          path: ./data-folder.zip
```

To decompress files, you can modify the workflow like so:

```yaml
name: Decompress Files

on: [push]

jobs:
  decompress-job:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Download Artifact
        uses: actions/download-artifact@v4
        with:
          name: compressed-data

      - name: List contents in the workspace
        run: ls -la ${{ github.workspace }}

      - name: Decompress Directory
        uses: somaz94/compress-decompress@v1
        with:
          command: decompress
          source: ./data-folder.zip
          format: zip
          dest: './unpacked'

      - name: Display Content of the Unpacked Files
        run: |
          ls -la ${{ github.workspace }}/unpacked
          cat ${{ github.workspace }}/unpacked/data-folder
```

<br/>

### includeRoot: false(option)

This example demonstrates how to use the Compress-Decompress action to compress
a directory:

```yaml
name: Compress Files

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
          includeRoot: 'false'

      - name: Upload Artifact
        uses: actions/upload-artifact@v4
        with:
          name: compressed-data
          path: ./data-folder/data-folder.zip
```

To decompress files, you can modify the workflow like so:

```yaml
name: Decompress Files

on: [push]

jobs:
  decompress-job:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Download Artifact
        uses: actions/download-artifact@v4
        with:
          name: compressed-data

      - name: List contents in the workspace
        run: ls -la ${{ github.workspace }}

      - name: Decompress Directory
        uses: somaz94/compress-decompress@v1
        with:
          command: decompress
          source: ./data-folder.zip
          format: zip
          dest: './unpacked'

      - name: Display Content of the Unpacked Files
        run: |
          ls -la ${{ github.workspace }}/unpacked
          cat ${{ github.workspace }}/unpacked/data-folder.txt # You'll have all the files in that directory. This is an example
```

<br/>

To use Matrix, you can modify the workflow like so:

```yaml
name: Test Compression Formats

on: [push]

jobs:
  test-compression-formats:
    name: Test Compression Formats
    runs-on: ubuntu-latest
    strategy:
      matrix:
        format: [zip, tar, tgz, tbz2]
        include_root: [true, false]
        source: [test2]
        dest_config:
          - type: default
            dest: ''
            destfilename: ''
          - type: custom
            dest: 'custom_output'
            destfilename: 'custom_archive'
      fail-fast: false

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Create Test Files
        run: |
          mkdir -p test2 test3
          echo "Test content for test2" > test2/test2.txt

      - name: Test Compression
        id: compress
        uses: somaz94/compress-decompress@v1
        with:
          command: 'compress'
          source: './${{ matrix.source }}'
          format: ${{ matrix.format }}
          includeRoot: ${{ matrix.include_root }}
          dest: ${{ matrix.dest_config.dest }}
          destfilename: ${{ matrix.dest_config.destfilename }}

      - name: List Workspace Contents
        run: |
          echo "Current directory contents:"
          ls -la
          echo "Source directory contents:"
          ls -la ./${{ matrix.source }}

      # Set the correct source path based on includeRoot
      - name: Set Source Path
        id: set-path
        run: |
          if [ "${{ matrix.include_root }}" = "true" ]; then
            echo "source_path=./${{ matrix.source }}.${{ matrix.format }}" >> $GITHUB_OUTPUT
          else
            echo "source_path=./${{ matrix.source }}/${{ matrix.source }}.${{ matrix.format }}" >> $GITHUB_OUTPUT
          fi

      - name: Upload Compressed Artifact
        uses: actions/upload-artifact@v4
        with:
          name: compressed-${{ matrix.format }}-${{ matrix.source }}-root-${{ matrix.include_root }}
          path: ${{ steps.set-path.outputs.source_path }}
          if-no-files-found: error

      - name: Test Decompression
        uses: somaz94/compress-decompress@v1
        with:
          command: 'decompress'
          source: ${{ steps.set-path.outputs.source_path }}
          format: ${{ matrix.format }}
          dest: './unpacked-${{ matrix.format }}-${{ matrix.source }}'

      - name: Verify Contents
        run: |
          echo "Verifying ${{ matrix.format }} format with includeRoot: ${{ matrix.include_root }}"
          echo "Listing unpacked directory contents:"
          ls -la ./unpacked-${{ matrix.format }}-${{ matrix.source }}
          
          if [ "${{ matrix.include_root }}" = "true" ]; then
            echo "Contents with root directory:"
            ls -la ./unpacked-${{ matrix.format }}-${{ matrix.source }}/${{ matrix.source }}
            cat ./unpacked-${{ matrix.format }}-${{ matrix.source }}/${{ matrix.source }}/${{ matrix.source }}.txt
          else
            echo "Contents without root directory:"
            ls -la ./unpacked-${{ matrix.format }}-${{ matrix.source }}
            cat ./unpacked-${{ matrix.format }}-${{ matrix.source }}/${{ matrix.source }}.txt
          fi

      - name: Print Compression Output
        run: |
          echo "Compression output for ${{ matrix.format }} (includeRoot: ${{ matrix.include_root }}): ${{ steps.compress.outputs.file_path }}"
```

<br/>

## Understanding Output Locations

The location of the compressed file depends on several factors:

1. **Default Behavior (no dest/destfilename specified)**:
   - With `includeRoot: true`: `./source-folder.zip`
   - With `includeRoot: false`: `./source-folder/source-folder.zip`

2. **Custom Destination**:
   - When `dest` is specified: `{dest}/{destfilename or source-name}.{format}`
   - Example: `./custom_output/my_archive.zip`

3. **Custom Filename**:
   - When `destfilename` is specified: Uses this name instead of the source folder name
   - Example: `my_archive.zip` instead of `source-folder.zip`

<br/>

## Additional Usage Examples

<br/>

### 1. Basic Usage with Default Settings
```yaml
- name: Compress Directory
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./data-folder
    format: zip
```
Output: `./data-folder.zip`

<br/>

### 2. Custom Destination Directory
```yaml
- name: Compress Directory
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./data-folder
    format: zip
    dest: './artifacts'
```
Output: `./artifacts/data-folder.zip`

<br/>

### 3. Custom Filename
```yaml
- name: Compress Directory
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./data-folder
    format: zip
    destfilename: 'backup-2024'
```
Output: `./backup-2024.zip`

<br/>

### 4. Custom Destination and Filename
```yaml
- name: Compress Directory
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./data-folder
    format: zip
    dest: './backups/2024'
    destfilename: 'q1-backup'
```
Output: `./backups/2024/q1-backup.zip`

<br/>

### 5. Custom Path with includeRoot: false
```yaml
- name: Compress Directory
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./data-folder
    format: zip
    dest: './archives'
    destfilename: 'files-only'
    includeRoot: 'false'
```
Output: `./archives/files-only.zip` (without parent directory)

<br/>

### 6. Different Formats with Custom Paths
```yaml
- name: Create TGZ Archive
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./project
    format: tgz
    dest: './releases'
    destfilename: 'project-v1.0'
```
Output: `./releases/project-v1.0.tgz`

<br/>

### 7. Decompression with Custom Path
```yaml
- name: Decompress Archive
  uses: somaz94/compress-decompress@v1
  with:
    command: decompress
    source: ./archives/backup.zip
    format: zip
    dest: './restored-files'
```
Output: Files will be extracted to `./restored-files/`

<br/>

### 8. Complete Workflow Example with Custom Paths
```yaml
name: Backup and Restore
jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Compress Project Files
        uses: somaz94/compress-decompress@v1
        with:
          command: compress
          source: ./src
          format: tgz
          dest: './backups'
          destfilename: 'project-backup'
          includeRoot: 'true'

      - name: Upload Backup
        uses: actions/upload-artifact@v4
        with:
          name: project-backup
          path: ./backups/project-backup.tgz

      - name: Restore from Backup
        uses: somaz94/compress-decompress@v1
        with:
          command: decompress
          source: ./backups/project-backup.tgz
          format: tgz
          dest: './restored'
```

<br/>

### 9. Excluding Files and Directories
```yaml
- name: Compress Project Files
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./project
    format: zip
    dest: './backups'
    destfilename: 'clean-project'
    exclude: 'node_modules vendor .git tests/tmp'
```
Output: `./backups/clean-project.zip` (without excluded directories and files)

<br/>

### 10. Using Wildcards in Exclude Patterns
```yaml
- name: Compress Source Code
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./src
    format: zip
    dest: './releases'
    destfilename: 'source-code'
    exclude: '*.log *.tmp __pycache__/* .DS_Store'
```
Output: `./releases/source-code.zip` (without log files, temp files, Python cache, and macOS metadata)

<br/>

## Using the Exclude Feature

The `exclude` parameter allows you to specify files, directories, or patterns that should be excluded from the compression process. This is particularly useful when compressing large directories that may contain:

- Version control directories (like `.git`, `.svn`)
- Build artifacts or dependencies (like `node_modules`, `vendor`, `.gradle`)
- Temporary or cache files (like `__pycache__`, `.DS_Store`, `*.log`)
- Large binary files that don't need to be included

<br/>

### Exclude Pattern Syntax

The `exclude` parameter accepts space-separated patterns:

- Simple filenames or directory names: `node_modules .git`
- Paths relative to the source: `src/tests/fixtures data/samples`
- Wildcards for extensions or patterns: `*.log *.tmp`
- Directory contents with trailing slash: `tmp/ cache/`

<br/>

### Examples of Exclude Patterns

1. **Excluding Version Control:**
   ```yaml
   exclude: '.git .github .svn .gitignore'
   ```

2. **Excluding Build Artifacts:**
   ```yaml
   exclude: 'node_modules vendor build dist target'
   ```

3. **Excluding Temp and Log Files:**
   ```yaml
   exclude: '*.log *.tmp *.cache tmp/ logs/'
   ```

4. **Combining Multiple Patterns:**
   ```yaml
   exclude: '.git node_modules *.log tmp/ .DS_Store'
   ```

5. **Excluding Specific Subdirectories:**
   ```yaml
   exclude: 'tests/fixtures docs/examples'
   ```

<br/>

## Troubleshooting

<br/>

### Common Issues and Solutions

1. **Compression Failures**
   - Check if source directory/files exist
   - Verify write permissions
   - Enable verbose logging for detailed error messages
   - Use `fail_on_error: 'false'` to continue workflow despite errors

2. **Decompression Issues**
   - Verify archive format matches the specified format
   - Check if destination directory is writable
   - Enable verbose mode to see detailed progress
   - Look for corruption in source archives

3. **Permission Problems**
   - Ensure proper file permissions
   - Check workspace directory permissions
   - Verify user/group access rights

4. **Exclude Pattern Issues**
   - Ensure patterns are space-separated
   - Check path relativity (patterns are relative to source directory)
   - For stubborn files, try multiple pattern formats
   - Use verbose mode to see which files are being included/excluded

<br/>

### Logging and Debugging

The action provides two levels of logging:

1. **Standard Logging (default)**
   - Basic operation progress
   - Essential error messages
   - Final status and results

2. **Verbose Logging (`verbose: 'true'`)**
   - Detailed configuration information
   - Command execution details
   - Comprehensive error messages
   - File size and compression statistics
   - Directory content listings

<br/>

### Error Handling Options

The action supports flexible error handling through the `fail_on_error` option:

1. **Strict Mode (`fail_on_error: 'true'`)**
   - Fails the workflow step on any error
   - Provides immediate feedback
   - Suitable for critical operations

2. **Lenient Mode (`fail_on_error: 'false'`)**
   - Continues workflow despite errors
   - Logs warnings instead of failing
   - Useful for non-critical operations
   - Allows custom error handling in workflow

<br/>

## License

This project is licensed under the [MIT License](LICENSE) file for details.

<br/>

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

<br/>

## Contributors

Thanks to all contributors:

<a href="https://github.com/somaz94/compress-decompress/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=somaz94/compress-decompress" />
</a>
