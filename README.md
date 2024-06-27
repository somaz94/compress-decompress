# Compress-Decompress Action

[![GitHub Super-Linter](https://github.com/actions/container-action/actions/workflows/linter.yml/badge.svg)](https://github.com/super-linter/super-linter)
![CI](https://github.com/actions/container-action/actions/workflows/ci.yml/badge.svg)

## Description

This GitHub Action provides the functionality to compress or decompress files using various 
compression formats including zip, tar, tgz, and tbz2. It is designed to be easy to use within 
GitHub workflows for handling file compression and decompression tasks efficiently.

## Inputs

| Input      | Description                                                                                                      | Required |
|------------|------------------------------------------------------------------------------------------------------------------|----------|
| `command`  | The operation to perform. It can be either "compress" or "decompress"                                            | Yes      |
| `source`   | The source directory or file to compress or decompress.                                                          | Yes      |
| `dest`     | The destination directory or file for the output. If not provided, it defaults to the current working directory. | No       |
| `format`   | The compression format to use. Supported formats are `zip`, `tar`, `tgz`, and `tbz2.                             | Yes      |

## Outputs

| Output       | Description                                      |
|--------------|--------------------------------------------------|
| `file_path`  | The path to the compressed or decompressed file. |

## Usage

You can use this action in your GitHub workflow by specifying the action with its required inputs.

## Example Workflow

This example demonstrates how to use the Compress-Decompress action to compress a directory:

```yaml
name: Compress Files

on: [push]

jobs:
  compress-job:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout Repository
      uses: actions/checkout@v2

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
      uses: actions/checkout@v2

    - name: Download Artifact
      uses: actions/download-artifact@v2
      with:
        name: compressed-data

    - name: Decompress Directory
      uses: somaz94/compress-decompress@v1
      with:
        command: decompress
        source: ./data-folder.zip
        format: zip
```

## License

This project is licensed under the [MIT License](LICENSE) file for details.
