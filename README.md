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

## License

This project is licensed under the [MIT License](LICENSE) file for details.

<br/>

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
