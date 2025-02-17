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
| `dest`        | The destination directory or file for the output. If not provided, it defaults to the current working directory. | No       | -       |
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

## Understanding IncludeRoot Option

The `includeRoot` option controls how files are structured within the compressed archive:

<br/>

### includeRoot: true (Default)
- Creates the archive with the source folder as the root directory
- Preserves the original directory structure
- Example structure:
  ```
  data-folder.zip
  └── data-folder/
      ├── file1.txt
      ├── file2.txt
      └── subfolder/
          └── file3.txt
  ```
- Output location: `./data-folder.zip`

<br/>

### includeRoot: false
- Compresses only the contents of the source folder without the parent directory
- Files are directly at the root of the archive
- Example structure:
  ```
  data-folder.zip
  ├── file1.txt
  ├── file2.txt
  └── subfolder/
      └── file3.txt
  ```
- Output location: `./data-folder/data-folder.zip`

<br/>

### When to Use Each Option
- Use `includeRoot: true` when you want to preserve the directory structure and need the parent folder name in the archive
- Use `includeRoot: false` when you only want to compress the contents without the parent directory name

<br/>

## Advanced Usage Examples

<br/>

### 1. Error Handling with fail_on_error

```yaml
- name: Compress with Error Handling
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./data-folder
    format: zip
    fail_on_error: 'false'  # Continue even if compression fails
    verbose: 'true'         # Enable detailed logging
```

<br/>

### 2. Debugging with Verbose Logging

```yaml
- name: Decompress with Verbose Output
  uses: somaz94/compress-decompress@v1
  with:
    command: decompress
    source: ./archive.tgz
    format: tgz
    dest: './unpacked'
    verbose: 'true'  # Show detailed progress and debug information
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

