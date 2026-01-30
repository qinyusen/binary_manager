#!/usr/bin/env python3
import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from binary_manager.downloader.downloader import Downloader, download_package
from binary_manager.downloader.verifier import Verifier, verify_package


def main():
    parser = argparse.ArgumentParser(
        description='Binary Manager Downloader - Download and install packages'
    )
    parser.add_argument(
        '--config', '-c',
        help='URL or local path to JSON config file'
    )
    parser.add_argument(
        '--output', '-o',
        default='./downloads',
        help='Output directory for downloaded packages (default: ./downloads)'
    )
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Only verify config structure without downloading'
    )
    parser.add_argument(
        '--extract-only',
        help='Extract existing zip file to specified directory (no config needed)'
    )

    args = parser.parse_args()

    print(f"========================================")
    print(f"Binary Manager - Downloader")
    print(f"========================================")

    if args.extract_only:
        print(f"Extracting zip: {args.extract_only}")
        print(f"Target directory: {args.output}")
        print(f"========================================")
        
        verifier = Verifier()
        result = verifier.extract_zip(args.extract_only, args.output)
        if result:
            print(f"\nExtraction completed successfully!")
            print(f"Extracted to: {args.output}")
        else:
            print(f"\nExtraction failed!")
            sys.exit(1)
        return

    if not args.config:
        print("Error: --config/-c is required unless using --extract-only")
        parser.print_help()
        sys.exit(1)

    verifier = Verifier()

    print(f"Config: {args.config}")
    print(f"Output: {args.output}")
    print(f"========================================")

    config = None

    if args.config.startswith('http://') or args.config.startswith('https://'):
        from binary_manager.downloader.downloader import Downloader
        
        print(f"\nDownloading config from URL...")
        downloader = Downloader()
        config_path = os.path.join(args.output, 'config.json')
        result = downloader.download_file(args.config, config_path)
        
        if not result:
            print(f"\nError: Failed to download config")
            sys.exit(1)
        
        config = verifier.load_config(config_path)
    else:
        print(f"\nLoading config from local path...")
        config = verifier.load_config(args.config)

    if not config:
        print(f"\nError: Failed to load config")
        sys.exit(1)

    if not verifier.validate_config_structure(config):
        print(f"\nError: Invalid config structure")
        sys.exit(1)

    print(f"\nPackage: {config['package_name']}")
    print(f"Version: {config['version']}")
    print(f"Files: {config['file_info']['file_count']}")
    print(f"Size: {config['file_info']['size']} bytes")

    if args.verify_only:
        print(f"\n========================================")
        print(f"Config verification complete!")
        print(f"========================================")
        return

    download_url = config.get('download_url')
    
    print(f"\nLocating package...")
    zip_path = os.path.join(args.output, config['file_info']['archive_name'])
    
    if not os.path.exists(zip_path):
        if args.config and not (args.config.startswith('http://') or args.config.startswith('https://')):
            config_dir = os.path.dirname(args.config)
            potential_zip_path = os.path.join(config_dir, config['file_info']['archive_name'])
            if os.path.exists(potential_zip_path):
                print(f"Found package in config directory: {potential_zip_path}")
                zip_path = potential_zip_path
    
    if os.path.exists(zip_path):
        print(f"Package found: {zip_path}")
        print("Verifying package...")
    elif download_url:
        print(f"\nDownload URL: {download_url}")
        print(f"Downloading package...")
        result = download_package(download_url, zip_path)
        if not result:
            print(f"\nError: Failed to download package")
            sys.exit(1)
    else:
        print(f"\nError: Package not found and no download URL provided")
        sys.exit(1)
    
    print(f"\nVerifying package...")
    if not verify_package(zip_path, config):
        print(f"\nError: Package verification failed")
        sys.exit(1)

    print(f"Package verified successfully!")

    print(f"\nExtracting package...")
    extract_dir = os.path.join(args.output, config['package_name'])
    
    if not verifier.extract_zip(zip_path, extract_dir):
        print(f"\nError: Failed to extract package")
        sys.exit(1)

    print(f"Package extracted successfully!")

    print(f"\nVerifying extracted files...")
    if not verifier.verify_extracted_files(config, extract_dir):
        print(f"\nWarning: Some files failed verification")
        print(f"Package extraction may be incomplete")
    else:
        print(f"All files verified successfully!")

    print(f"\n========================================")
    print(f"Package installation complete!")
    print(f"========================================")
    print(f"Package: {config['package_name']} v{config['version']}")
    print(f"Location: {extract_dir}")
    print(f"========================================")


if __name__ == '__main__':
    main()
