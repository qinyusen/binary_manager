#!/usr/bin/env python3
"""
文件处理工具 - 命令行工具
"""
import os
import argparse
import json
from pathlib import Path

def count_files(directory):
    """统计目录中的文件数量"""
    path = Path(directory)
    files = list(path.rglob('*'))
    file_count = sum(1 for f in files if f.is_file())
    dir_count = sum(1 for f in files if f.is_dir())
    
    return {
        'files': file_count,
        'directories': dir_count,
        'total': file_count + dir_count
    }

def list_files(directory, pattern=None):
    """列出目录中的文件"""
    path = Path(directory)
    if pattern:
        files = list(path.rglob(pattern))
    else:
        files = list(path.rglob('*'))
    
    return [str(f.relative_to(path)) for f in files if f.is_file()]

def main():
    parser = argparse.ArgumentParser(description='File Processing Tool')
    parser.add_argument('directory', help='Directory to process')
    parser.add_argument('--count', '-c', action='store_true', help='Count files')
    parser.add_argument('--list', '-l', action='store_true', help='List files')
    parser.add_argument('--pattern', '-p', help='Filter by pattern (e.g. *.py)')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} is not a directory")
        return 1
    
    if args.count:
        result = count_files(args.directory)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Files: {result['files']}")
            print(f"Directories: {result['directories']}")
            print(f"Total: {result['total']}")
    
    elif args.list:
        files = list_files(args.directory, args.pattern)
        if args.json:
            print(json.dumps({'files': files}, indent=2))
        else:
            for f in files:
                print(f)
    
    else:
        parser.print_help()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
