# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the Compress-Decompress action.

<br/>

## Table of Contents

- [Compression Issues](#compression-issues)
- [Decompression Issues](#decompression-issues)
- [Glob Pattern Problems](#glob-pattern-problems)
- [Exclude Pattern Issues](#exclude-pattern-issues)
- [Permission Problems](#permission-problems)
- [Performance Issues](#performance-issues)
- [Artifact Upload/Download Issues](#artifact-uploaddownload-issues)
- [Debugging Tips](#debugging-tips)

<br/>

## Compression Issues

<br/>

### Issue: Compression Fails with "Source not found"

**Symptoms:**
```
Error: Source directory/file not found: ./data-folder
```

**Solutions:**

1. **Verify source path exists:**
   ```yaml
   - name: Check if source exists
     run: |
       ls -la ./data-folder
       # or
       test -d ./data-folder && echo "Directory exists" || echo "Directory not found"
   ```

2. **Use absolute paths:**
   ```yaml
   - name: Compress Directory
     uses: somaz94/compress-decompress@v1
     with:
       command: compress
       source: ${{ github.workspace }}/data-folder
       format: zip
   ```

3. **Check workspace state:**
   ```yaml
   - name: List workspace contents
     run: ls -la ${{ github.workspace }}
   ```

<br/>

### Issue: Compression Succeeds but File is Empty

**Symptoms:**
- Archive is created but has 0 bytes or very small size
- No files are included in the archive

**Solutions:**

1. **Check if source directory has files:**
   ```yaml
   - name: Verify source contents
     run: |
       find ./data-folder -type f
       du -sh ./data-folder
   ```

2. **Verify exclude patterns aren't too broad:**
   ```yaml
   - name: Test without exclude
     uses: somaz94/compress-decompress@v1
     with:
       command: compress
       source: ./data-folder
       format: zip
       # Remove or comment out exclude parameter
   ```

3. **Enable verbose logging:**
   ```yaml
   - name: Compress with verbose output
     uses: somaz94/compress-decompress@v1
     with:
       command: compress
       source: ./data-folder
       format: zip
       verbose: 'true'
   ```

<br/>

### Issue: "Permission denied" During Compression

**Symptoms:**
```
Error: Permission denied: cannot access './data-folder'
```

**Solutions:**

1. **Check file permissions:**
   ```yaml
   - name: Check permissions
     run: ls -la ./data-folder
   ```

2. **Fix permissions before compression:**
   ```yaml
   - name: Fix permissions
     run: chmod -R 755 ./data-folder

   - name: Compress Directory
     uses: somaz94/compress-decompress@v1
     with:
       command: compress
       source: ./data-folder
       format: zip
   ```

3. **Run with sudo (not recommended):**
   ```yaml
   - name: Create archive with elevated permissions
     run: sudo tar -czf archive.tgz ./data-folder
   ```

<br/>

### Issue: Archive Size is Too Large

**Symptoms:**
- Archive size exceeds expectations
- Upload artifact fails due to size limits

**Solutions:**

1. **Use exclude patterns:**
   ```yaml
   - name: Compress without large files
     uses: somaz94/compress-decompress@v1
     with:
       command: compress
       source: ./project
       format: tgz
       exclude: 'node_modules vendor *.mp4 *.zip'
   ```

2. **Use more efficient format:**
   ```yaml
   # Use tgz or tbz2 instead of zip for better compression
   - name: Compress with better compression
     uses: somaz94/compress-decompress@v1
     with:
       command: compress
       source: ./project
       format: tbz2  # Better compression than zip
   ```

3. **Split into multiple archives:**
   ```yaml
   - name: Compress source code
     uses: somaz94/compress-decompress@v1
     with:
       command: compress
       source: ./src
       format: tgz
       destfilename: 'source-code'

   - name: Compress documentation
     uses: somaz94/compress-decompress@v1
     with:
       command: compress
       source: ./docs
       format: tgz
       destfilename: 'documentation'
   ```

<br/>

## Decompression Issues

<br/>

### Issue: Decompression Fails with "Invalid archive"

**Symptoms:**
```
Error: Invalid or corrupted archive: ./archive.zip
```

**Solutions:**

1. **Verify archive integrity:**
   ```yaml
   - name: Check archive
     run: |
       file ./archive.zip
       unzip -t ./archive.zip  # For zip files
       # or
       tar -tzf ./archive.tgz  # For tar/tgz files
   ```

2. **Re-download the artifact:**
   ```yaml
   - name: Download Artifact
     uses: actions/download-artifact@v4
     with:
       name: compressed-data
       path: ./downloads

   - name: Verify downloaded file
     run: |
       ls -lh ./downloads
       file ./downloads/archive.zip
   ```

3. **Check format parameter matches:**
   ```yaml
   # Ensure format matches the actual file format
   - name: Decompress
     uses: somaz94/compress-decompress@v1
     with:
       command: decompress
       source: ./archive.tgz
       format: tgz  # Must match the actual format
   ```

<br/>

### Issue: Files Not Found After Decompression

**Symptoms:**
- Decompression succeeds but files are in unexpected location
- Cannot find extracted files

**Solutions:**

1. **Check extraction location:**
   ```yaml
   - name: Decompress and list contents
     uses: somaz94/compress-decompress@v1
     with:
       command: decompress
       source: ./archive.zip
       format: zip
       dest: './unpacked'

   - name: List extraction results
     run: |
       echo "Destination directory:"
       ls -laR ./unpacked
   ```

2. **Consider includeRoot setting:**
   ```yaml
   # If compressed with includeRoot: true
   - name: Access files
     run: |
       ls -la ./unpacked/source-folder/  # Files are in subdirectory

   # If compressed with includeRoot: false
   - name: Access files
     run: |
       ls -la ./unpacked/  # Files are at root
   ```

<br/>

### Issue: "Destination already exists"

**Symptoms:**
```
Error: Destination directory already exists: ./unpacked
```

**Solutions:**

1. **Clean destination before decompression:**
   ```yaml
   - name: Clean destination
     run: rm -rf ./unpacked

   - name: Decompress
     uses: somaz94/compress-decompress@v1
     with:
       command: decompress
       source: ./archive.zip
       format: zip
       dest: './unpacked'
   ```

2. **Use different destination:**
   ```yaml
   - name: Decompress to unique location
     uses: somaz94/compress-decompress@v1
     with:
       command: decompress
       source: ./archive.zip
       format: zip
       dest: './unpacked-${{ github.run_number }}'
   ```

<br/>

## Glob Pattern Problems

<br/>

### Issue: Glob Pattern Not Matching Files

**Symptoms:**
```
Error: No files matched the pattern: **/*.doc
```

**Solutions:**

1. **Verify files exist:**
   ```yaml
   - name: Check for matching files
     run: |
       find . -name "*.doc"
       # or
       ls -la **/*.doc
   ```

2. **Test pattern syntax:**
   ```yaml
   # Use verbose mode to see what's being matched
   - name: Test glob pattern
     uses: somaz94/compress-decompress@v1
     with:
       command: compress
       source: '**/*.doc'
       format: zip
       verbose: 'true'
       fail_on_error: 'false'
   ```

3. **Check pattern escaping:**
   ```yaml
   # Ensure pattern is properly quoted
   - name: Compress with glob
     uses: somaz94/compress-decompress@v1
     with:
       command: compress
       source: '**/*.doc'  # Use single quotes
       format: zip
   ```

4. **Make pattern more specific:**
   ```yaml
   # Instead of broad pattern
   source: '**/*'  # Too broad

   # Use specific pattern
   source: 'docs/**/*.md'  # More specific
   ```

<br/>

### Issue: Too Many Files Matched by Glob

**Symptoms:**
- Process takes too long
- Archive is too large
- Runs out of disk space

**Solutions:**

1. **Make pattern more specific:**
   ```yaml
   # Instead of
   source: '**/*.log'

   # Use
   source: 'logs/2024/**/*.log'
   ```

2. **Combine with exclude patterns:**
   ```yaml
   - name: Compress specific logs
     uses: somaz94/compress-decompress@v1
     with:
       command: compress
       source: '**/*.log'
       format: tgz
       exclude: 'debug.log trace.log node_modules/**'
   ```

3. **Split into multiple archives:**
   ```yaml
   - name: Compress by subdirectory
     uses: somaz94/compress-decompress@v1
     with:
       command: compress
       source: 'src/**/*.py'
       format: zip
       destfilename: 'src-files'

   - name: Compress tests separately
     uses: somaz94/compress-decompress@v1
     with:
       command: compress
       source: 'tests/**/*.py'
       format: zip
       destfilename: 'test-files'
   ```

<br/>

### Issue: Glob Pattern with Special Characters

**Symptoms:**
- Pattern not working as expected with brackets, braces, etc.

**Solutions:**

1. **Use proper escaping:**
   ```yaml
   # For multiple extensions
   source: '**/*.{yml,yaml,json}'

   # For character classes
   source: '**/*[0-9].log'
   ```

2. **Test pattern locally:**
   ```bash
   # Test in bash
   ls **/*.{yml,yaml}
   
   # Test with find
   find . -name "*.yml" -o -name "*.yaml"
   ```

3. **Use simpler patterns:**
   ```yaml
   # Instead of complex pattern
   source: '**/*.{js,jsx,ts,tsx}'

   # Split into multiple operations
   - name: Compress JS files
     source: '**/*.js'
   
   - name: Compress TS files
     source: '**/*.ts'
   ```

<br/>

## Exclude Pattern Issues

### Issue: Exclude Pattern Not Working

**Symptoms:**
- Files that should be excluded are still in the archive

**Solutions:**

1. **Verify exclude syntax:**
   ```yaml
   # Correct: space-separated
   exclude: 'node_modules .git *.log'

   # Incorrect: comma-separated
   exclude: 'node_modules,.git,*.log'  # Wrong!
   ```

2. **Check path relativity:**
   ```yaml
   # Paths are relative to source
   - name: Compress
     uses: somaz94/compress-decompress@v1
     with:
       command: compress
       source: ./project
       format: zip
       exclude: 'tests/fixtures'  # Relative to ./project
   ```

3. **Use verbose mode:**
   ```yaml
   - name: Test exclude pattern
     uses: somaz94/compress-decompress@v1
     with:
       command: compress
       source: ./project
       format: zip
       exclude: 'node_modules *.log'
       verbose: 'true'
   ```

4. **Try different pattern variations:**
   ```yaml
   # Try multiple variations
   exclude: 'node_modules'           # Directory name
   exclude: './node_modules'         # With prefix
   exclude: 'node_modules/'          # With trailing slash
   exclude: '*/node_modules'         # With wildcard
   ```

<br/>

### Issue: Need to Exclude Multiple Patterns

**Solutions:**

1. **Use space-separated list:**
   ```yaml
   exclude: 'node_modules vendor .git *.log *.tmp __pycache__'
   ```

2. **Use YAML multi-line string:**
   ```yaml
   exclude: >
     node_modules
     vendor
     .git
     *.log
     *.tmp
     __pycache__
   ```

3. **Combine wildcards:**
   ```yaml
   exclude: '*.log *.tmp *.cache test_* *_test.py'
   ```

<br/>

## Permission Problems

### Issue: Permission Denied Errors

**Symptoms:**
```
Error: Permission denied: cannot read/write files
```

**Solutions:**

1. **Check file ownership:**
   ```yaml
   - name: Check ownership
     run: |
       ls -la ./data-folder
       id
   ```

2. **Fix permissions:**
   ```yaml
   - name: Fix file permissions
     run: |
       chmod -R 644 ./data-folder/*
       chmod -R 755 ./data-folder
   ```

3. **Use appropriate user:**
   ```yaml
   # Specify container user if needed
   jobs:
     compress:
       runs-on: ubuntu-latest
       container:
         image: ubuntu:latest
         options: --user root
   ```

<br/>

## Performance Issues

### Issue: Compression Takes Too Long

**Symptoms:**
- Workflow times out
- Compression step runs for many minutes

**Solutions:**

1. **Use faster format:**
   ```yaml
   # zip is fastest (but larger)
   format: zip

   # tgz is balanced
   format: tgz

   # tbz2 is slowest (but smallest)
   format: tbz2
   ```

2. **Reduce scope:**
   ```yaml
   # Use more specific source
   source: 'src/**/*.py'  # Instead of '.'
   
   # Use exclude patterns
   exclude: 'node_modules vendor .git'
   ```

3. **Check for large files:**
   ```yaml
   - name: Find large files
     run: |
       find ./project -type f -size +100M
       du -sh ./project/*
   ```

<br/>

### Issue: Running Out of Disk Space

**Symptoms:**
```
Error: No space left on device
```

**Solutions:**

1. **Clean before compression:**
   ```yaml
   - name: Clean workspace
     run: |
       rm -rf node_modules
       rm -rf .git
       docker system prune -af
   ```

2. **Use streaming compression:**
   ```yaml
   # For very large directories, compress incrementally
   - name: Compress in chunks
     run: |
       tar -czf part1.tgz ./data/part1
       tar -czf part2.tgz ./data/part2
   ```

3. **Check available space:**
   ```yaml
   - name: Check disk space
     run: df -h
   ```

<br/>

## Artifact Upload/Download Issues

<br/>

### Issue: Artifact Upload Fails

**Symptoms:**
```
Error: Unable to upload artifact
```

**Solutions:**

1. **Verify file exists:**
   ```yaml
   - name: Check file before upload
     run: |
       ls -lh ./archive.zip
       test -f ./archive.zip && echo "File exists" || echo "File not found"
   ```

2. **Use correct path:**
   ```yaml
   - name: Upload Artifact
     uses: actions/upload-artifact@v4
     with:
       name: my-archive
       path: ./archive.zip  # Must match actual location
       if-no-files-found: error
   ```

3. **Check file size limits:**
   ```yaml
   - name: Check artifact size
     run: |
       SIZE=$(stat -f%z ./archive.zip)
       echo "Archive size: $SIZE bytes"
       if [ $SIZE -gt 2147483648 ]; then
         echo "Warning: File larger than 2GB"
       fi
   ```

<br/>

### Issue: Artifact Download Fails

**Solutions:**

1. **Verify artifact name:**
   ```yaml
   - name: Download Artifact
     uses: actions/download-artifact@v4
     with:
       name: my-archive  # Must match upload name exactly
       path: ./downloads
   ```

2. **List available artifacts:**
   ```yaml
   - name: List artifacts
     uses: actions/github-script@v7
     with:
       script: |
         const artifacts = await github.rest.actions.listWorkflowRunArtifacts({
           owner: context.repo.owner,
           repo: context.repo.repo,
           run_id: context.runId,
         });
         console.log(artifacts.data);
   ```

<br/>

## Debugging Tips

### Enable Verbose Logging

Always start with verbose logging when troubleshooting:

```yaml
- name: Debug compression issue
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./data
    format: zip
    verbose: 'true'
    fail_on_error: 'false'
```

<br/>

### Add Diagnostic Steps

Add steps to gather information:

```yaml
- name: Diagnostic Information
  run: |
    echo "=== System Information ==="
    uname -a
    df -h
    
    echo "=== Workspace Contents ==="
    ls -laR ${{ github.workspace }}
    
    echo "=== Environment Variables ==="
    env | sort
    
    echo "=== Current Directory ==="
    pwd
    ls -la
```

<br/>

### Test Locally with Docker

Test the action locally:

```bash
# Build the Docker image
docker build -t compress-decompress .

# Run compression
docker run -v $(pwd)/test-data:/workspace \
  compress-decompress \
  compress /workspace/data zip

# Check results
ls -la test-data/
```

<br/>

### Check Action Logs

Enable debug logging in GitHub Actions:

1. Go to repository Settings → Secrets and variables → Actions
2. Add a repository secret: `ACTIONS_STEP_DEBUG` = `true`
3. Re-run the workflow

<br/>

### Use Incremental Testing

Test components separately:

```yaml
# Test 1: Basic compression
- name: Test basic compression
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./simple-folder
    format: zip

# Test 2: Add exclude
- name: Test with exclude
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: ./simple-folder
    format: zip
    exclude: '*.log'

# Test 3: Add glob pattern
- name: Test glob pattern
  uses: somaz94/compress-decompress@v1
  with:
    command: compress
    source: '**/*.txt'
    format: zip
```

<br/>

### Common Command-Line Equivalents

For manual testing:

```bash
# Test compression
tar -czf test.tgz ./data-folder
zip -r test.zip ./data-folder
tar -cjf test.tbz2 ./data-folder

# Test decompression
tar -xzf test.tgz
unzip test.zip
tar -xjf test.tbz2

# Test with exclusions
tar -czf test.tgz --exclude='*.log' --exclude='node_modules' ./data-folder
zip -r test.zip ./data-folder -x "*.log" "node_modules/*"

# Test glob patterns
find . -name "*.doc" -exec zip docs.zip {} +
tar -czf docs.tgz $(find . -name "*.doc")
```

<br/>

---

## Still Having Issues?

If you're still experiencing problems:

1. **Check existing issues:** [GitHub Issues](https://github.com/somaz94/compress-decompress/issues)
2. **Create a new issue:** Include:
   - Full workflow YAML
   - Complete error messages
   - Verbose output logs
   - Steps to reproduce
3. **Review documentation:**
   - [Main README](../README.md)
   - [Glob Pattern Guide](GLOB_PATTERNS.md)
   - [Advanced Usage Guide](ADVANCED_USAGE.md)

<br/>

---

For more information, see:
- [Main README](../README.md)
- [Glob Pattern Guide](GLOB_PATTERNS.md)
- [Advanced Usage Guide](ADVANCED_USAGE.md)
