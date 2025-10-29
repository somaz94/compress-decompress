# Documentation Index

Complete documentation for the Compress-Decompress Action.

<br/>

## Documentation Structure

<br/>

### Core Documentation

1. **[Main README](../README.md)** - Overview, quick start, and basic usage

2. **[Glob Pattern Guide](GLOB_PATTERNS.md)** - Match multiple files with patterns
   - Pattern syntax and examples
   - How glob patterns work
   - Strip prefix feature
   - Symbolic link support
   - Performance considerations

3. **[Advanced Usage Guide](ADVANCED_USAGE.md)** - Advanced features and patterns
   - Custom paths and filenames
   - Exclude patterns
   - Matrix strategies
   - includeRoot option
   - Error handling
   - Verbose logging

4. **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Common issues and solutions
   - Compression issues
   - Decompression issues
   - Glob pattern problems
   - Permission problems
   - Performance issues
   - Debugging tips

---

## Quick Navigation

<br/>

### By Use Case

**I want to...**

- **Get started** → [Main README](../README.md)
- **Match multiple files** → [Glob Pattern Guide](GLOB_PATTERNS.md)
- **Exclude files** → [Advanced Usage - Exclude Patterns](ADVANCED_USAGE.md#using-exclude-patterns)
- **Customize output** → [Advanced Usage - Custom Paths](ADVANCED_USAGE.md#custom-paths-and-filenames)
- **Fix an issue** → [Troubleshooting Guide](TROUBLESHOOTING.md)
- **Test multiple formats** → [Advanced Usage - Matrix Strategies](ADVANCED_USAGE.md#matrix-strategies)

<br/>

### By Topic

**Glob Patterns:**
- [Basic glob usage](GLOB_PATTERNS.md#basic-usage)
- [Supported patterns](GLOB_PATTERNS.md#supported-patterns)
- [Advanced examples](GLOB_PATTERNS.md#advanced-examples)
- [Strip prefix feature](GLOB_PATTERNS.md#strip-prefix-feature)
- [Symbolic link support](GLOB_PATTERNS.md#symbolic-link-support)

**Advanced Features:**
- [Custom destinations](ADVANCED_USAGE.md#custom-paths-and-filenames)
- [Exclude patterns](ADVANCED_USAGE.md#using-exclude-patterns)
- [Matrix strategies](ADVANCED_USAGE.md#matrix-strategies)
- [Error handling](ADVANCED_USAGE.md#error-handling)
- [Verbose logging](ADVANCED_USAGE.md#verbose-logging)

**Troubleshooting:**
- [Compression issues](TROUBLESHOOTING.md#compression-issues)
- [Decompression issues](TROUBLESHOOTING.md#decompression-issues)
- [Glob pattern problems](TROUBLESHOOTING.md#glob-pattern-problems)
- [Permission problems](TROUBLESHOOTING.md#permission-problems)
- [Debugging tips](TROUBLESHOOTING.md#debugging-tips)

---

## Reading Guide

<br/>

### For New Users

1. Start with [Main README](../README.md) for overview and basic examples
2. Learn about [Glob Patterns](GLOB_PATTERNS.md) for file matching
3. Explore [Advanced Usage](ADVANCED_USAGE.md) for more features

<br/>

### For Troubleshooting

1. Check [Troubleshooting Guide](TROUBLESHOOTING.md) for common issues
2. Enable `verbose: true` in your workflow for detailed logs
3. Test locally with Docker before pushing changes

<br/>

### For Advanced Users

1. Review [Advanced Usage Guide](ADVANCED_USAGE.md) for all features
2. Check [Glob Pattern Guide](GLOB_PATTERNS.md) for complex patterns
3. Use [Matrix Strategies](ADVANCED_USAGE.md#matrix-strategies) for testing

---

## Document Summaries

<br/>

### [Glob Pattern Guide](GLOB_PATTERNS.md)

Comprehensive guide to using glob patterns for matching multiple files across your repository.

**Key Sections:**
- Pattern syntax and wildcards
- Directory structure preservation
- Strip prefix feature for clean archives
- Symbolic link handling (Bazel/Buck support)
- Performance optimization tips

<br/>

### [Advanced Usage Guide](ADVANCED_USAGE.md)

Advanced features and usage patterns for power users.

**Key Sections:**
- Custom output paths and filenames
- Exclude patterns for filtering files
- Matrix strategies for testing multiple configurations
- includeRoot option for archive structure control
- Error handling and verbose logging

<br/>

### [Troubleshooting Guide](TROUBLESHOOTING.md)

Solutions to common problems and debugging strategies.

**Key Sections:**
- Compression and decompression issues
- Glob pattern troubleshooting
- Permission and performance problems
- Step-by-step debugging process
- Command-line equivalents for local testing

---

## Getting Help

<br/>

### Documentation Not Helpful?

1. **Search existing issues**: [GitHub Issues](https://github.com/somaz94/compress-decompress/issues)
2. **Ask a question**: [GitHub Discussions](https://github.com/somaz94/compress-decompress/discussions)
3. **Report a bug**: [Create an issue](https://github.com/somaz94/compress-decompress/issues/new)

<br/>

### Before Asking

- [ ] Checked relevant documentation section
- [ ] Enabled `verbose: true` for detailed logs
- [ ] Tested locally if possible
- [ ] Searched existing issues

<br/>

### When Reporting Issues

Include:
- Your workflow YAML (relevant section)
- Error messages or unexpected behavior
- Verbose output logs
- Expected vs actual results
- Steps to reproduce

---

## Documentation Updates

<br/>

This documentation is maintained alongside the codebase. When contributing:

1. **Keep it current**: Update docs with code changes
2. **Add examples**: Include real-world usage patterns
3. **Link between docs**: Cross-reference related sections
4. **Test examples**: Ensure all code examples work

---

## Version History

<br/>

- **v1.x** - Initial release with glob patterns and symbolic link support
- See [CHANGELOG.md](../CHANGELOG.md) for detailed version history (if available)

---

<div align="center">

**Complete | Searchable | Practical**

[Back to Main README](../README.md) | [Report Issue](https://github.com/somaz94/compress-decompress/issues)

</div>
