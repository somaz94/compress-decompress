# Glob Pattern Guide

This guide provides comprehensive documentation for using glob patterns with the Compress-Decompress action.

<br/>

## Table of Contents

- [Overview](#overview)
- [Basic Usage](#basic-usage)
- [Supported Patterns](#supported-patterns)
- [Advanced Examples](#advanced-examples)
- [How It Works](#how-it-works)
- [Important Notes](#important-notes)
- [Real-World Use Cases](#real-world-use-cases)

<br/>

## Overview

Glob patterns allow you to match multiple files across your repository based on filename patterns. This is particularly useful when you need to archive specific file types or patterns without compressing entire directories.

<br/>

## Basic Usage

```yaml
- name: Compress All Documentation Files
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: '**/*.doc'
    format: zip
    dest: './artifacts'
    destfilename: 'all-docs'
```

<br/>

## Supported Patterns

| Pattern | Description | Example Match |
|---------|-------------|---------------|
| `**/*.ext` | All files with extension in all subdirectories | `docs/readme.md`, `src/test/file.md` |
| `*.ext` | All files with extension in current directory | `readme.txt`, `notes.txt` |
| `dir/**/*.ext` | All files with extension in specific directory tree | `src/utils/helper.py`, `src/main.py` |
| `**/filename.ext` | Specific filename in all subdirectories | `config.json`, `settings/config.json` |
| `dir/*.ext` | Files in specific directory (non-recursive) | `src/main.py` (not `src/sub/test.py`) |
| `**/*.{ext1,ext2}` | Multiple extensions in all subdirectories | `file.jpg`, `image.png` |

<br/>

## Advanced Examples

### 1. Compress All Markdown Files

```yaml
- name: Archive All Markdown Documentation
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: '**/*.md'
    format: tgz
    dest: './archives'
    destfilename: 'documentation'
    includeRoot: false  # Clean archive structure
```

<br/>

### 2. Compress Files from Specific Directory

```yaml
- name: Archive Source Files Only
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: 'src/**/*.py'
    format: zip
    dest: './backups'
    destfilename: 'python-sources'
    preserveGlobStructure: true
    includeRoot: false
```

<br/>

### 3. Compress Multiple File Types

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

<br/>

### 4. Archive Log Files

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

<br/>

### 5. Single Directory Wildcard

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

<br/>

### 6. Nested Path Pattern

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

<br/>

### 7. Archive Images

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

<br/>

### 8. Archive Build Artifacts

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

## How It Works

When using glob patterns, the action follows these steps:

1. **Searches for Matches**: Recursively scans the workspace for files matching the pattern
2. **Collects Files**: Gathers all matched files into a temporary directory
3. **Structure Handling**: 
   - **Default (preserveGlobStructure: false)**: Flattens all files to a single directory level
   - **Preserved (preserveGlobStructure: true)**: Maintains original directory structure with relative paths
   - **With stripPrefix**: Removes specified path prefix while preserving remaining structure
4. **Root Directory Handling**:
   - **Default (includeRoot: true)**: Includes temporary directory in archive (e.g., `compress_glob_123/`)
   - **Clean (includeRoot: false)**: Excludes temporary directory for clean archive structure
5. **Creates Archive**: Compresses the collected files into a single archive
6. **Cleans Up**: Automatically removes temporary files after compression

<br/>

## Strip Prefix Feature

The `stripPrefix` option allows you to remove a common path prefix from all matched files while preserving the remaining directory structure. This is useful when you want to archive files without their top-level directory.

### Basic Usage

```yaml
- name: Archive Source Files
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: 'project/src/**/*.ts'
    format: zip
    preserveGlobStructure: true
    stripPrefix: 'project/'
```

**Result:**
- Input: `project/src/app/main.ts`
- Output: `src/app/main.ts` (prefix `project/` removed)

<br/>

### Common Use Cases

#### 1. Remove Project Root

```yaml
- name: Archive Only Source Directory
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: 'myproject/src/**/*.py'
    format: zip
    preserveGlobStructure: true
    stripPrefix: 'myproject/'
    includeRoot: false  # Recommended
```

**Before:** `myproject/src/utils/helper.py`  
**After:** `src/utils/helper.py`

<br/>

#### 2. Clean Log Archives

```yaml
- name: Archive Application Logs
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: '/var/log/app/**/*.log'
    format: tgz
    preserveGlobStructure: true
    stripPrefix: '/var/log/app/'
    includeRoot: false  # Recommended
```

**Before:** `/var/log/app/2024/01/app.log`  
**After:** `2024/01/app.log`

<br/>

#### 3. Build Artifacts

```yaml
- name: Archive Distribution Files
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: 'build/dist/**/*.js'
    format: zip
    preserveGlobStructure: true
    stripPrefix: 'build/dist/'
    includeRoot: false  # Recommended
```

**Before:** `build/dist/assets/main.js`  
**After:** `assets/main.js`

<br/>

### Important Notes

- ✅ `stripPrefix` **only works** with `preserveGlobStructure: true`
- ✅ `stripPrefix` **only works** with glob patterns (e.g., `**/*.doc`)
- ✅ Trailing slash is optional: `'src/'` and `'src'` both work
- ✅ **Highly Recommended**: Use `includeRoot: false` to avoid including the temporary directory in the archive
- ⚠️ If a file doesn't start with the prefix, it's archived with its full path
- ⚠️ Case-sensitive on Linux/macOS, case-insensitive on Windows

<br/>

### Understanding `includeRoot` Parameter

The `includeRoot` parameter controls whether the temporary directory (used internally for glob pattern processing) is included in the final archive.

#### With `includeRoot: true` (Default)
```yaml
- name: Archive with Temporary Directory
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: 'project/src/**/*.ts'
    format: zip
    preserveGlobStructure: true
    stripPrefix: 'project/'
    # includeRoot: true (default)
```

**Archive Structure:**
```
archive.zip
├── compress_glob_123/      ← Temporary directory included
    └── src/
        └── app/
            └── main.ts
```

#### With `includeRoot: false` (Recommended)
```yaml
- name: Archive with Clean Structure
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: 'project/src/**/*.ts'
    format: zip
    preserveGlobStructure: true
    stripPrefix: 'project/'
    includeRoot: false        ← Clean output
```

**Archive Structure:**
```
archive.zip
├── src/                    ← Clean, no temporary directory
    └── app/
        └── main.ts
```

<br/>

**Best Practice Recommendation:**

When using `stripPrefix` or when you want clean archive structures, **always set `includeRoot: false`**:

```yaml
- name: Archive Source Files (Best Practice)
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: 'project/src/**/*.ts'
    format: zip
    preserveGlobStructure: true
    stripPrefix: 'project/'
    includeRoot: false        # ← Prevents temporary directory inclusion
    verbose: true
```

**Why `includeRoot: false` is recommended:**
- ✅ Creates cleaner, more professional archives
- ✅ Archives are easier to extract and use
- ✅ No confusing temporary directory names
- ✅ More portable across different systems
- ✅ Better for distribution and deployment scenarios

<br/>

## Important Notes

### Pattern Behavior

⚠️ **Understanding File Collection:**
- All matched files are collected and compressed into a single archive
- **Default behavior (preserveGlobStructure: false)**: Files are **flattened** - all files are placed at the root of the archive
  - File name conflicts are handled automatically with numeric suffixes (e.g., `file.txt`, `file_1.txt`, `file_2.txt`)
- **With preserveGlobStructure: true**: Directory structure is **preserved** - files maintain their relative paths
  - Allows files with the same name in different directories (e.g., `dir1/file.txt` and `dir2/file.txt`)
- **The `includeRoot` parameter** affects whether the temporary processing directory appears in the archive
  - `includeRoot: true` (default): Includes temporary directory (e.g., `compress_glob_123/`)
  - `includeRoot: false` (recommended): Excludes temporary directory for clean structure

**Example with preserved structure (recommended approach):**
```yaml
- name: Archive Logs with Directory Structure
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: 'logs/**/*.log'
    format: zip
    dest: './archives'
    destfilename: 'all-logs'
    preserveGlobStructure: true  # Keeps logs/2024/app.log structure
    includeRoot: false            # Clean output without temp directory
```

**Example with flattened structure:**
```yaml
- name: Archive All Config Files (Flattened)
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: '**/*.conf'
    format: zip
    dest: './archives'
    destfilename: 'configs'
    includeRoot: false  # Still recommended for clean archives
    # preserveGlobStructure defaults to false - all files at root level
```

<br/>

### Error Handling

⚠️ **No Matches Found:**
- If no files match the pattern, the action will **fail by default**
- Use `fail_on_error: false` to allow workflows to continue when no matches are found
- Enable `verbose: true` to see which files are being matched

Example with error handling:
```yaml
- name: Archive Optional Files
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: '**/*.backup'
    format: zip
    dest: './archives'
    destfilename: 'backups'
    fail_on_error: false
    verbose: true
```

<br/>

### Performance Considerations

⚠️ **Optimization Tips:**
- Glob patterns are processed from the current working directory
- Large pattern matches may take time to process and copy
- Consider using more specific patterns for better performance
- Use directory prefixes to limit search scope: `src/**/*.py` instead of `**/*.py`

<br/>

## Real-World Use Cases

### Backup Configuration Files

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

<br/>

### Archive Documentation

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

<br/>

### Collect Test Coverage Reports

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

<br/>

### Backup Database Dumps

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

### Archive Source Code by Language

```yaml
- name: Archive Python Source Files
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: '**/*.py'
    format: zip
    dest: './source-archives'
    destfilename: 'python-sources'
```

<br/>

### Collect CI/CD Artifacts

```yaml
- name: Archive Build Artifacts
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: 'build/**/*.{jar,war,zip}'
    format: tgz
    dest: './artifacts'
    destfilename: 'build-output'
```

<br/>

## Combining with Exclude Patterns

You can combine glob patterns with exclude patterns for more precise control:

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

## Troubleshooting

### Pattern Not Matching Files

1. Verify the pattern syntax is correct
2. Check that files exist in the expected locations
3. Enable `verbose: true` to see matched files
4. Test the pattern locally with `find` command:
   ```bash
   find . -path './src/**/*.py'
   ```

<br/>

### Too Many Files Matched

1. Make the pattern more specific
2. Add directory prefix to limit scope
3. Use exclude patterns to filter unwanted files
4. Consider breaking into multiple compression steps

<br/>

### Performance Issues

1. Avoid overly broad patterns like `**/*`
2. Limit search scope with directory prefixes
3. Use specific extensions instead of wildcards
4. Check workspace size before running pattern matches

<br/>

---

For more examples and usage information, see the [main README](../README.md).
