#!/usr/bin/env python3
"""
Binary Manager V2 CLI
命令行界面 - 提供发布、下载、分组管理等功能
"""
import sys
import argparse
from pathlib import Path
from typing import Optional

from ..application import PublisherService, GroupService, DownloaderService
from ..infrastructure.storage import LocalStorage, S3Storage
from ..infrastructure.database import SQLitePackageRepository, SQLiteGroupRepository
from ..shared.logger import Logger


class BinaryManagerCLI:
    """Binary Manager V2 命令行界面"""
    
    def __init__(self):
        self.logger = Logger.get(self.__class__.__name__)
    
    def run(self, args):
        """运行CLI命令"""
        if not args.command:
            self.parser.print_help()
            return 1
        
        try:
            if args.command == 'publish':
                return self.cmd_publish(args)
            elif args.command == 'download':
                return self.cmd_download(args)
            elif args.command == 'group':
                return self.cmd_group(args)
            elif args.command == 'list':
                return self.cmd_list(args)
            else:
                self.parser.print_help()
                return 1
        except Exception as e:
            self.logger.error(f"Command failed: {e}")
            return 1
    
    def cmd_publish(self, args) -> int:
        """发布包"""
        self.logger.info(f"Publishing {args.package_name} v{args.version}")
        
        storage = LocalStorage(args.output)
        publisher = PublisherService(storage_path=args.output)
        
        if args.s3_bucket:
            s3_storage = S3Storage(
                bucket_name=args.s3_bucket,
                access_key=args.s3_access_key,
                secret_key=args.s3_secret_key,
                region=args.s3_region
            )
            result = publisher.publish_to_s3(
                source_dir=args.source,
                package_name=args.package_name,
                version=args.version,
                s3_storage=s3_storage,
                description=args.description,
                metadata={'metadata': args.metadata} if args.metadata else None,
                ignore_patterns=args.ignore.split(',') if args.ignore else None,
                extract_git=not args.no_git
            )
        else:
            result = publisher.publish(
                source_dir=args.source,
                package_name=args.package_name,
                version=args.version,
                description=args.description,
                metadata={'metadata': args.metadata} if args.metadata else None,
                ignore_patterns=args.ignore.split(',') if args.ignore else None,
                extract_git=not args.no_git
            )
        
        print(f"✓ Package published successfully!")
        print(f"  Package ID: {result['package_id']}")
        print(f"  Archive: {result.get('archive_path', result.get('s3_key'))}")
        
        return 0
    
    def cmd_download(self, args) -> int:
        """下载包"""
        self.logger.info(f"Downloading package...")
        
        downloader = DownloaderService()
        
        if args.config:
            result = downloader.download_by_config(args.config, args.output)
        elif args.package_id:
            result = downloader.download_by_id(args.package_id, args.output)
        elif args.package_name and args.version:
            result = downloader.download_by_name_version(
                args.package_name, args.version, args.output
            )
        elif args.group_id:
            result = downloader.download_group(args.group_id, args.output)
        else:
            self.logger.error("No download source specified")
            return 1
        
        print(f"✓ Package downloaded successfully!")
        print(f"  Location: {result['output_path']}")
        
        return 0
    
    def cmd_group(self, args) -> int:
        """分组管理"""
        group_service = GroupService()
        
        if args.group_action == 'create':
            return self._group_create(group_service, args)
        elif args.group_action == 'list':
            return self._group_list(group_service, args)
        elif args.group_action == 'export':
            return self._group_export(group_service, args)
        elif args.group_action == 'import':
            return self._group_import(group_service, args)
        elif args.group_action == 'delete':
            return self._group_delete(group_service, args)
        else:
            self.logger.error("No group action specified")
            return 1
    
    def _group_create(self, service, args) -> int:
        """创建分组"""
        packages = []
        for pkg_spec in args.packages or []:
            name, version = pkg_spec.split(':')
            packages.append({
                'package_name': name,
                'version': version,
                'install_order': len(packages),
                'required': True
            })
        
        result = service.create_group(
            group_name=args.group_name,
            version=args.version,
            packages=packages,
            description=args.description
        )
        
        print(f"✓ Group created successfully!")
        print(f"  Group ID: {result['group_id']}")
        print(f"  Packages: {len(result['packages'])}")
        
        return 0
    
    def _group_list(self, service, args) -> int:
        """列出分组"""
        groups = service.list_groups()
        
        if not groups:
            print("No groups found")
            return 0
        
        print(f"Found {len(groups)} groups:\n")
        for group in groups:
            print(f"  {group.group_name} v{group.version}")
            print(f"    ID: {group.id if hasattr(group, 'id') else 'N/A'}")
            print(f"    Description: {group.description or 'N/A'}")
            print(f"    Packages: {len(group.packages)}")
            print()
        
        return 0
    
    def _group_export(self, service, args) -> int:
        """导出分组"""
        export_path = service.export_group(args.group_id, args.output)
        
        if export_path:
            print(f"✓ Group exported to: {export_path}")
            return 0
        return 1
    
    def _group_import(self, service, args) -> int:
        """导入分组"""
        group_id = service.import_group(args.config)
        
        if group_id:
            print(f"✓ Group imported with ID: {group_id}")
            return 0
        return 1
    
    def _group_delete(self, service, args) -> int:
        """删除分组"""
        if service.delete_group(args.group_id):
            print(f"✓ Group deleted")
            return 0
        return 1
    
    def cmd_list(self, args) -> int:
        """列出包"""
        repo = SQLitePackageRepository()
        
        if args.package_name:
            packages = repo.find_all({'package_name': args.package_name})
        else:
            packages = repo.find_all()
        
        if not packages:
            print("No packages found")
            return 0
        
        print(f"Found {len(packages)} packages:\n")
        for pkg in packages:
            print(f"  {pkg.package_name} v{pkg.version}")
            print(f"    ID: {pkg.id if hasattr(pkg, 'id') else 'N/A'}")
            print(f"    Size: {pkg.archive_size} bytes")
            print(f"    Files: {pkg.file_count}")
            if pkg.git_info:
                print(f"    Git: {pkg.git_info.commit_short}")
            print()
        
        return 0
    
    @property
    def parser(self):
        """创建参数解析器"""
        parser = argparse.ArgumentParser(
            prog='binary-manager-v2',
            description='Binary Manager V2 - 发布和下载管理系统'
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # 发布命令
        publish_parser = subparsers.add_parser('publish', help='发布包')
        publish_parser.add_argument('-s', '--source', required=True, help='源目录')
        publish_parser.add_argument('-n', '--package-name', required=True, help='包名称')
        publish_parser.add_argument('-v', '--version', required=True, help='版本号')
        publish_parser.add_argument('-o', '--output', default='./releases', help='输出目录')
        publish_parser.add_argument('--description', help='包描述')
        publish_parser.add_argument('--metadata', help='元数据(JSON)')
        publish_parser.add_argument('--ignore', help='忽略模式(逗号分隔)')
        publish_parser.add_argument('--no-git', action='store_true', help='不提取Git信息')
        publish_parser.add_argument('--s3-bucket', help='S3存储桶')
        publish_parser.add_argument('--s3-access-key', help='S3访问密钥')
        publish_parser.add_argument('--s3-secret-key', help='S3秘密密钥')
        publish_parser.add_argument('--s3-region', default='us-east-1', help='S3区域')
        
        # 下载命令
        download_parser = subparsers.add_parser('download', help='下载包')
        download_parser.add_argument('-c', '--config', help='配置文件路径')
        download_parser.add_argument('--package-id', type=int, help='包ID')
        download_parser.add_argument('--package-name', help='包名称')
        download_parser.add_argument('--version', help='版本号')
        download_parser.add_argument('--group-id', type=int, help='分组ID')
        download_parser.add_argument('-o', '--output', default='./downloads', help='输出目录')
        
        # 分组命令
        group_parser = subparsers.add_parser('group', help='分组管理')
        group_subparsers = group_parser.add_subparsers(dest='group_action')
        
        create_parser = group_subparsers.add_parser('create', help='创建分组')
        create_parser.add_argument('--group-name', required=True, help='分组名称')
        create_parser.add_argument('--version', required=True, help='版本号')
        create_parser.add_argument('--packages', nargs='+', help='包列表(name:version)')
        create_parser.add_argument('--description', help='分组描述')
        
        list_parser = group_subparsers.add_parser('list', help='列出分组')
        
        export_parser = group_subparsers.add_parser('export', help='导出分组')
        export_parser.add_argument('--group-id', type=int, required=True, help='分组ID')
        export_parser.add_argument('-o', '--output', default='./groups', help='输出目录')
        
        import_parser = group_subparsers.add_parser('import', help='导入分组')
        import_parser.add_argument('--config', required=True, help='配置文件路径')
        
        delete_parser = group_subparsers.add_parser('delete', help='删除分组')
        delete_parser.add_argument('--group-id', type=int, required=True, help='分组ID')
        
        # 列出命令
        list_parser = subparsers.add_parser('list', help='列出包')
        list_parser.add_argument('--package-name', help='按名称过滤')
        
        return parser


def main():
    """主入口函数"""
    cli = BinaryManagerCLI()
    parser = cli.parser
    args = parser.parse_args()
    
    sys.exit(cli.run(args))


if __name__ == '__main__':
    main()
