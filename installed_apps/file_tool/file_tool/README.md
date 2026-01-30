# File Tool

A command-line tool for file processing operations.

## Features

- Count files in a directory
- List files with optional pattern filtering
- JSON output support
- Recursive directory scanning

## Usage

### Count files
```bash
python3 file_tool.py /path/to/directory --count
```

### List files
```bash
python3 file_tool.py /path/to/directory --list
```

### List files with pattern
```bash
python3 file_tool.py /path/to/directory --list --pattern "*.py"
```

### Output as JSON
```bash
python3 file_tool.py /path/to/directory --count --json
python3 file_tool.py /path/to/directory --list --json
```

## Examples

```bash
# Count all files in current directory
python3 file_tool.py . --count

# List all Python files
python3 file_tool.py . --list --pattern "*.py"

# Get JSON output
python3 file_tool.py . --count --json
```

## Version

1.0.0
