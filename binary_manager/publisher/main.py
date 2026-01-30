#!/usr/bin/env python3
import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from binary_manager.publisher.scanner import FileScanner, generate_file_list
from binary_manager.publisher.packager import Packager


def main():
    parser = argparse.ArgumentParser(
        description='Binary Manager Publisher - Package files and generate configuration'
    )
    parser.add_argument(
        '--source', '-s',
        required=True,
        help='Source directory to package'
    )
    parser.add_argument(
        '--output', '-o',
        default='./releases',
        help='Output directory for packages (default: ./releases)'
    )
    parser.add_argument(
        '--version', '-v',
        default='1.0.0',
        help='Package version (default: 1.0.0)'
    )
    parser.add_argument(
        '--name', '-n',
        help='Package name (default: basedir name)'
    )
    parser.add_argument(
        '--url', '-u',
        help='Download URL for the package'
    )
    parser.add_argument(
        '--ignore', '-i',
        action='append',
        help='Ignore patterns (can be specified multiple times)'
    )

    args = parser.parse_args()

    if not os.path.exists(args.source):
        print(f"Error: Source directory does not exist: {args.source}")
        sys.exit(1)

    if not os.path.isdir(args.source):
        print(f"Error: Source path is not a directory: {args.source}")
        sys.exit(1)

    package_name = args.name or os.path.basename(os.path.normpath(args.source))

    print(f"========================================")
    print(f"Binary Manager - Publisher")
    print(f"========================================")
    print(f"Package: {package_name}")
    print(f"Version: {args.version}")
    print(f"Source: {args.source}")
    print(f"Output: {args.output}")
    print(f"========================================")

    try:
        scanner = FileScanner(args.ignore)
        print(f"\nScanning files...")
        file_list, scan_info = scanner.scan_directory(args.source)
        print(f"Found {scan_info['total_files']} files ({scan_info['total_size']} bytes)")

        packager = Packager(args.output)
        print(f"\nCreating package...")
        zip_info = packager.create_zip(args.source, file_list, package_name, args.version)
        print(f"Created: {zip_info['archive_name']} ({zip_info['size']} bytes)")

        config = packager.generate_json_config(
            package_name, args.version, file_list, zip_info, args.url
        )
        config_path = packager.save_config(config, package_name, args.version)
        print(f"Created: {config_path}")

        print(f"\n========================================")
        print(f"Package created successfully!")
        print(f"========================================")
        print(f"Config file: {config_path}")
        print(f"Archive: {zip_info['archive_path']}")
        print(f"SHA256: {zip_info['hash']}")
        print(f"========================================")

    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
