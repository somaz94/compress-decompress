# Advanced Usage Guide

This guide covers advanced features and usage patterns for the Compress-Decompress action.

<br/>

## Table of Contents

- [Custom Paths and Filenames](#custom-paths-and-filenames)
- [Using Exclude Patterns](#using-exclude-patterns)
- [Matrix Strategies](#matrix-strategies)
- [includeRoot Option](#includeroot-option)
- [Error Handling](#error-handling)
- [Verbose Logging](#verbose-logging)

<br/>

## Custom Paths and Filenames

<br/>

### Understanding Output Locations

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

### Examples

#### 1. Basic Usage with Default Settings
```yaml
- name: Compress Directory
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./data-folder
    format: zip
```
**Output:** `./data-folder.zip`

<br/>

#### 2. Custom Destination Directory
```yaml
- name: Compress Directory
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./data-folder
    format: zip
    dest: './artifacts'
```
**Output:** `./artifacts/data-folder.zip`

<br/>

#### 3. Custom Filename
```yaml
- name: Compress Directory
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./data-folder
    format: zip
    destfilename: 'backup-2024'
```
**Output:** `./backup-2024.zip`

<br/>

#### 4. Custom Destination and Filename
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
**Output:** `./backups/2024/q1-backup.zip`

<br/>

#### 5. Custom Path with includeRoot: false
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
**Output:** `./archives/files-only.zip` (without parent directory)

<br/>

#### 6. Different Formats with Custom Paths
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
**Output:** `./releases/project-v1.0.tgz`

<br/>

#### 7. Decompression with Custom Path
```yaml
- name: Decompress Archive
  uses: somaz94/compress-decompress@v1
  with:
    command: decompress
    source: ./archives/backup.zip
    format: zip
    dest: './restored-files'
```
**Output:** Files will be extracted to `./restored-files/`

<br/>

## Using Exclude Patterns

The `exclude` parameter allows you to specify files, directories, or patterns that should be excluded from the compression process.

<br/>

### When to Use Exclude

Exclude patterns are particularly useful when compressing large directories that may contain:

- Version control directories (like `.git`, `.svn`)
- Build artifacts or dependencies (like `node_modules`, `vendor`, `.gradle`)
- Temporary or cache files (like `__pycache__`, `.DS_Store`, `*.log`)
- Large binary files that don't need to be included
- Test fixtures or sample data

<br/>

### Exclude Pattern Syntax

The `exclude` parameter accepts **space-separated** patterns:

- Simple filenames or directory names: `node_modules .git`
- Paths relative to the source: `src/tests/fixtures data/samples`
- Wildcards for extensions or patterns: `*.log *.tmp`
- Directory contents with trailing slash: `tmp/ cache/`

<br/>

### Basic Exclude Examples

#### 1. Excluding Version Control
```yaml
- name: Compress Repository
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: .
    format: zip
    dest: './backups'
    destfilename: 'repo-backup'
    exclude: '.git .github .svn .gitignore'
```

<br/>

#### 2. Excluding Build Artifacts
```yaml
- name: Compress Source Code
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./project
    format: tgz
    dest: './archives'
    destfilename: 'source-code'
    exclude: 'node_modules vendor build dist target'
```

<br/>

#### 3. Excluding Temp and Log Files
```yaml
- name: Compress Application
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./app
    format: zip
    dest: './releases'
    destfilename: 'app-clean'
    exclude: '*.log *.tmp *.cache tmp/ logs/'
```

<br/>

#### 4. Combining Multiple Patterns
```yaml
- name: Compress Project Files
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./project
    format: zip
    dest: './backups'
    destfilename: 'clean-project'
    exclude: '.git node_modules *.log tmp/ .DS_Store'
```

<br/>

#### 5. Excluding Specific Subdirectories
```yaml
- name: Compress Documentation
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./docs
    format: zip
    dest: './archives'
    destfilename: 'docs-without-examples'
    exclude: 'tests/fixtures docs/examples'
```

<br/>

#### 6. Using Wildcards in Exclude
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

<br/>

### Advanced Exclude Patterns

#### Excluding Test Files
```yaml
- name: Archive Production Code Only
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./src
    format: zip
    dest: './prod-archives'
    destfilename: 'production-code'
    exclude: '*_test.py test_*.py *_test.go *_test.js tests/ __tests__/'
```

<br/>

#### Excluding Development Dependencies
```yaml
- name: Archive Production Build
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: .
    format: tgz
    dest: './deployments'
    destfilename: 'production-bundle'
    exclude: 'node_modules/.cache node_modules/.bin .npm .yarn'
```

<br/>

#### Combining Glob Patterns with Exclude
```yaml
- name: Archive Source Files (excluding tests)
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: 'src/**/*.py'
    format: zip
    dest: './archives'
    destfilename: 'source-only'
    exclude: '*_test.py test_*.py'
```

<br/>

## Matrix Strategies

Matrix strategies allow you to test multiple configurations in parallel.

<br/>

### Basic Matrix Example

```yaml
name: Test Multiple Formats

on: [push]

jobs:
  test-formats:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        format: [zip, tar, tgz, tbz2]
      fail-fast: false

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Create Test Files
        run: |
          mkdir -p test-data
          echo "Test content" > test-data/file.txt

      - name: Test Compression
        uses: somaz94/compress-decompress@v1
        with:
          command: compress
          source: ./test-data
          format: ${{ matrix.format }}
```

<br/>

### Advanced Matrix Configuration

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

### Matrix with Exclude Patterns

```yaml
name: Test Compression with Exclusions

on: [push]

jobs:
  test-exclusions:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        format: [zip, tgz]
        exclude_pattern:
          - '*.log *.tmp'
          - 'node_modules .git'
          - 'tests/ __pycache__'
      fail-fast: false

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Test Compression
        uses: somaz94/compress-decompress@v1
        with:
          command: compress
          source: .
          format: ${{ matrix.format }}
          exclude: ${{ matrix.exclude_pattern }}
          dest: './test-archives'
          destfilename: 'test-${{ matrix.format }}'
```

<br/>

## includeRoot Option

The `includeRoot` option controls whether the root directory is included in the archive.

<br/>

### includeRoot: true (default)

When `includeRoot` is `true`, the archive includes the root folder itself.

```yaml
- name: Compress with Root Directory
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./data-folder
    format: zip
    includeRoot: 'true'  # This is the default
```

**Archive structure:**
```
data-folder.zip
└── data-folder/
    ├── file1.txt
    └── file2.txt
```

**Decompression:**
```yaml
- name: Decompress with Root
  uses: somaz94/compress-decompress@v1
  with:
    command: decompress
    source: ./data-folder.zip
    format: zip
    dest: './unpacked'
```

**Result:**
```
unpacked/
└── data-folder/
    ├── file1.txt
    └── file2.txt
```

<br/>

### includeRoot: false

When `includeRoot` is `false`, only the contents of the directory are archived.

```yaml
- name: Compress without Root Directory
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./data-folder
    format: zip
    includeRoot: 'false'
```

**Archive structure:**
```
data-folder.zip
├── file1.txt
└── file2.txt
```

**Decompression:**
```yaml
- name: Decompress without Root
  uses: somaz94/compress-decompress@v1
  with:
    command: decompress
    source: ./data-folder.zip
    format: zip
    dest: './unpacked'
```

**Result:**
```
unpacked/
├── file1.txt
└── file2.txt
```

<br/>

### Complete Workflow Example

```yaml
name: Backup and Restore

on: [push]

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
          exclude: '*.log __pycache__'

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

## Error Handling

The action supports flexible error handling through the `fail_on_error` option.

<br/>

### Strict Mode (default)

```yaml
- name: Compress Files (Strict)
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./data
    format: zip
    fail_on_error: 'true'  # This is the default
```

**Behavior:**
- Fails the workflow step on any error
- Provides immediate feedback
- Suitable for critical operations

<br/>

### Lenient Mode

```yaml
- name: Compress Files (Lenient)
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./optional-data
    format: zip
    fail_on_error: 'false'
```

**Behavior:**
- Continues workflow despite errors
- Logs warnings instead of failing
- Useful for non-critical operations
- Allows custom error handling in workflow

<br/>

### Conditional Error Handling

```yaml
- name: Try to Compress Optional Files
  id: compress
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: '**/*.backup'
    format: zip
    fail_on_error: 'false'
  continue-on-error: true

- name: Check Compression Result
  if: steps.compress.outcome == 'success'
  run: echo "Compression succeeded"

- name: Handle Compression Failure
  if: steps.compress.outcome == 'failure'
  run: echo "No backup files found or compression failed"
```

<br/>

## Verbose Logging

Enable detailed logging for debugging and monitoring.

<br/>

### Standard Logging (default)

```yaml
- name: Compress Files
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./data
    format: zip
    verbose: 'false'  # This is the default
```

**Output:**
- Basic operation progress
- Essential error messages
- Final status and results

<br/>

### Verbose Logging

```yaml
- name: Compress Files (Verbose)
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./data
    format: zip
    verbose: 'true'
```

**Output:**
- Detailed configuration information
- Command execution details
- Comprehensive error messages
- File size and compression statistics
- Directory content listings
- Pattern matching details (for glob patterns)

<br/>

### When to Use Verbose Logging

Use verbose logging when:
- Debugging compression/decompression issues
- Verifying which files are being processed
- Checking exclude pattern behavior
- Understanding glob pattern matches
- Investigating performance issues
- Troubleshooting workflow failures

<br/>

### Example with Verbose Logging

```yaml
- name: Debug Compression Issue
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: '**/*.log'
    format: zip
    dest: './archives'
    destfilename: 'logs'
    verbose: 'true'
    fail_on_error: 'false'
```

**This will show:**
- All files matched by the glob pattern
- Files being copied to temporary directory
- Compression command being executed
- Archive size and location
- Any warnings or errors encountered

<br/>

---

For more information, see:
- [Main README](../README.md)
- [Glob Pattern Guide](GLOB_PATTERNS.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
