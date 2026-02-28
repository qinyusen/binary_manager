# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Project now focuses exclusively on V2 Onion Architecture
- Reduced dependencies from ~105MB to ~6MB (94% reduction) by using urllib3 instead of boto3

### Removed
- Removed V1 basic version including all related files and directories:
  - `binary_manager/` directory (V1 main code)
  - `examples/` directory (V1 example projects)
  - `tools/` directory (V1 tools)
  - `installed_apps/` directory
  - V1 test files and test directories
- Removed V1 documentation files:
  - `TUTORIAL.md`
  - `README_REFACTORING.md`
  - `REFACTORING_SUMMARY.md`
  - `REFACTORING_SUMMARY_CN.md`
  - `UPGRADE_DESIGN.md`
  - `RELEASE_APP_GUIDE.md`
  - `V2_TEST_REPORT.md`
  - `QUICKSTART.md`

## [2.0.0] - 2026-02-26

### Added
- **Complete V2 Onion Architecture Implementation**
  - Domain Layer with zero external dependencies
    - Entities: Package, Version, Group, FileInfo, Publisher
    - Value Objects: PackageName, Hash, GitInfo, StorageLocation
    - Services: FileScanner, HashCalculator, Packager
    - Repository Interfaces: PackageRepository, GroupRepository, StorageRepository
  
  - Infrastructure Layer
    - Storage implementations: LocalStorage, S3Storage (using urllib3)
    - Git service for Git information extraction
    - SQLite database implementations for all repositories
    - Database migration support
  
  - Application Layer
    - PublisherService - Publishing workflow orchestration
    - DownloaderService - Download workflow management
    - GroupService - Group management functionality
  
  - Presentation Layer (CLI)
    - Complete command-line interface
    - Commands: publish, download, group, list
    - Support for local and S3 storage

- **Enhanced Git Integration**
  - Added `commit_message` field to GitInfo value object
  - Added `remotes` field to GitInfo value object (JSON array of remote repositories)
  - Git service automatically extracts Git repository information

- **Database Schema Enhancements**
  - Extended `packages` table with `git_commit_message` and `git_remotes` columns
  - Extended `group_packages` table with `package_name` and `package_version` columns
  - Automatic database migration support

- **Comprehensive Test Suite**
  - Complete test coverage for all layers (Domain, Infrastructure, Application, CLI)
  - Integration tests for end-to-end workflows
  - Edge case testing
  - All tests passing (100% success rate)

- **Updated Documentation**
  - Complete README.md rewrite (V2 only)
  - BINARY_MANAGER_V2.md - Detailed architecture documentation
  - V2_QUICKSTART.md - 5-minute quick start guide
  - PROJECT_FILES.md - Complete file documentation and statistics
  - Simplified install_dependencies.sh script

### Fixed
- Fixed logger initialization order in SQLite repositories
- Fixed FileScanner to include missing HashCalculator import
- Fixed PublisherService parameter passing:
  - FileScanner usage (ignore_patterns to constructor)
  - Packager.create_zip() parameters (package_name, version)
  - HashCalculator method calls (calculate_file not calculate_file_hash)
  - Archive path handling from Packager result dict
- Fixed GroupService:
  - GroupPackage creation (added package_name, package_version)
  - Group creation (use PackageName value object, created_by field)
  - Export/import serialization (handle PackageName)
- Fixed SQLite repositories:
  - Added _initialize_database() method
  - Added database migration support
  - Added id property to Package entity

### Changed
- **Dependency Reduction**: Replaced boto3 (~99MB) with urllib3 (~1MB) for S3 operations
- **Architecture**: Migrated from V1 monolithic structure to V2 Onion Architecture
- **Code Organization**: Restructured into clear layer separation (Domain, Infrastructure, Application, Presentation)
- **Type Safety**: Enhanced use of value objects and type hints throughout
- **Database**: Added proper schema initialization and migration support

### Technical Details
- **Total Lines of Code**: ~3,571 lines (V2 only)
- **Python Files**: 26 files
- **Dependencies**: 2 core dependencies (urllib3, requests)
- **Test Coverage**: Comprehensive tests for all layers
- **Database**: SQLite with automatic migrations

## [1.2.0] - 2026-02-09

### Added
- **Release App Tool** - Interactive release management tool
  - CLI-based interactive interface
  - Support for multiple compilers (C, Generic)
  - Version tracking capabilities
  - Release manager for automation
  - C++ demo example

### Documentation
- Added RELEASE_APP_GUIDE.md with complete usage instructions

## [1.1.0] - 2026-02-03

### Added
- **V2 Onion Architecture Design**
  - Domain layer entities and value objects
  - Repository interfaces
  - Domain services (FileScanner, HashCalculator, Packager)
  - Infrastructure layer framework
  - Application layer framework

### Documentation
- Added Chinese refactoring summary (REFACTORING_SUMMARY_CN.md)
- Added detailed V2 design documentation (UPGRADE_DESIGN.md)
- Added V2 architecture documentation (BINARY_MANAGER_V2.md)
- Added V2 quick start guide (V2_QUICKSTART.md)
- Added V2 test report (V2_TEST_REPORT.md)

## [1.0.0] - 2026-01-31

### Added
- **Initial Release - V1 Basic Version**
  - Publisher functionality (scan, package, publish)
  - Downloader functionality (download, verify)
  - Local storage support
  - Hash verification (SHA256)
  - Configuration management
  - Example projects (simple_app, web_app, cli_tool)
  - Installation script
  - Complete documentation (README.md, TUTORIAL.md, QUICKSTART.md)

### Features
- File scanning and packaging
- SHA256 hash calculation and verification
- Local file storage
- Command-line interfaces for publish and download
- JSON-based configuration
- Example applications

---

## Version Convention

- **Major version (X.0.0)**: Breaking changes, architectural redesigns
- **Minor version (0.X.0)**: New features, functionality additions
- **Patch version (0.0.X)**: Bug fixes, minor improvements

## Migration Notes

### From V1 to V2
V2 represents a complete architectural redesign using Onion Architecture patterns. V1 has been removed from the codebase. Key differences:

1. **Architecture**: V2 uses clean Onion Architecture with clear layer separation
2. **Dependencies**: V2 has 94% smaller dependency footprint
3. **Type Safety**: V2 uses value objects and enhanced type hints
4. **Extensibility**: V2 is designed for easier testing and extension
5. **Git Integration**: V2 has enhanced Git metadata support
6. **Storage**: V2 supports multiple storage backends (Local, S3)

For migration guidance, refer to the V2 documentation in `BINARY_MANAGER_V2.md` and `V2_QUICKSTART.md`.
