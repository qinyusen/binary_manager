import os
import json
import boto3
from pathlib import Path
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SyncManager:
    """AWS S3同步管理器"""
    
    def __init__(self, bucket_name: str, access_key: str = None, 
                 secret_key: str = None, region: str = 'us-east-1'):
        self.bucket_name = bucket_name
        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key or os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=secret_key or os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=region or os.environ.get('AWS_REGION', 'us-east-1')
        )
        
        logger.info(f"S3 Sync Manager initialized for bucket: {bucket_name}")
    
    def upload_file(self, local_path: str, s3_key: str, 
                   metadata: Dict = None) -> bool:
        """上传文件到S3"""
        try:
            local_path_obj = Path(local_path)
            if not local_path_obj.exists():
                logger.error(f"File not found: {local_path}")
                return False
            
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata
            
            self.s3_client.upload_file(
                str(local_path_obj),
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )
            
            logger.info(f"Uploaded {local_path} to s3://{self.bucket_name}/{s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload {local_path}: {e}")
            return False
    
    def download_file(self, s3_key: str, local_path: str) -> bool:
        """从S3下载文件"""
        try:
            local_path_obj = Path(local_path)
            local_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            self.s3_client.download_file(
                self.bucket_name,
                s3_key,
                str(local_path_obj)
            )
            
            logger.info(f"Downloaded s3://{self.bucket_name}/{s3_key} to {local_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download {s3_key}: {e}")
            return False
    
    def upload_database(self, db_path: str, s3_key: str = None) -> bool:
        """上传数据库文件到S3"""
        if s3_key is None:
            s3_key = f"databases/binary_manager_{int(os.path.getmtime(db_path))}.db"
        
        metadata = {
            'source': 'binary_manager',
            'type': 'sqlite_database',
            'upload_time': os.path.getmtime(db_path)
        }
        
        return self.upload_file(db_path, s3_key, metadata)
    
    def download_database(self, s3_key: str, local_path: str) -> bool:
        """从S3下载数据库文件"""
        return self.download_file(s3_key, local_path)
    
    def upload_package(self, package_info: Dict, local_path: str) -> bool:
        """上传包文件到S3"""
        s3_key = f"packages/{package_info['package_name']}/{package_info['version']}/{package_info['file_info']['archive_name']}"
        
        metadata = {
            'package_name': package_info['package_name'],
            'version': package_info['version'],
            'git_commit': package_info.get('git_info', {}).get('commit_hash', ''),
            'publisher_id': package_info.get('publisher', {}).get('publisher_id', ''),
            'upload_time': package_info.get('created_at', '')
        }
        
        return self.upload_file(local_path, s3_key, metadata)
    
    def download_package(self, package_name: str, version: str, 
                       archive_name: str, local_path: str) -> bool:
        """从S3下载包文件"""
        s3_key = f"packages/{package_name}/{version}/{archive_name}"
        return self.download_file(s3_key, local_path)
    
    def upload_group_config(self, group_info: Dict, local_path: str) -> bool:
        """上传Group配置到S3"""
        s3_key = f"groups/{group_info['group_name']}/{group_info['version']}/group.json"
        
        metadata = {
            'group_name': group_info['group_name'],
            'version': group_info['version'],
            'created_by': group_info.get('created_by', ''),
            'upload_time': group_info.get('created_at', '')
        }
        
        return self.upload_file(local_path, s3_key, metadata)
    
    def download_group_config(self, group_name: str, version: str, 
                            local_path: str) -> bool:
        """从S3下载Group配置"""
        s3_key = f"groups/{group_name}/{version}/group.json"
        return self.download_file(s3_key, local_path)
    
    def list_packages(self, prefix: str = 'packages/') -> list:
        """列出S3中的包"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                return []
            
            return response['Contents']
            
        except Exception as e:
            logger.error(f"Failed to list packages: {e}")
            return []
    
    def list_databases(self, prefix: str = 'databases/') -> list:
        """列出S3中的数据库文件"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                return []
            
            databases = sorted(
                response['Contents'],
                key=lambda x: x['LastModified'],
                reverse=True
            )
            
            return databases
            
        except Exception as e:
            logger.error(f"Failed to list databases: {e}")
            return []
    
    def get_latest_database(self) -> Optional[str]:
        """获取最新的数据库S3 key"""
        databases = self.list_databases()
        if not databases:
            return None
        
        return databases[0]['Key']
    
    def file_exists(self, s3_key: str) -> bool:
        """检查S3中文件是否存在"""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except self.s3_client.exceptions.ClientError:
            return False
    
    def delete_file(self, s3_key: str) -> bool:
        """删除S3中的文件"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info(f"Deleted s3://{self.bucket_name}/{s3_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete {s3_key}: {e}")
            return False
    
    def get_file_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:
        """生成S3文件的临时访问URL"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate URL for {s3_key}: {e}")
            return None


if __name__ == '__main__':
    import sys
    
    bucket = os.environ.get('AWS_S3_BUCKET', 'test-bucket')
    
    sync_manager = SyncManager(bucket)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'upload':
            if len(sys.argv) > 2:
                success = sync_manager.upload_file(sys.argv[2], sys.argv[3])
                print(f"Upload: {'Success' if success else 'Failed'}")
        
        elif command == 'download':
            if len(sys.argv) > 3:
                success = sync_manager.download_file(sys.argv[2], sys.argv[3])
                print(f"Download: {'Success' if success else 'Failed'}")
        
        elif command == 'list':
            packages = sync_manager.list_packages()
            print(f"Found {len(packages)} packages")
            for pkg in packages:
                print(f"  - {pkg['Key']}")
    
    else:
        print("Usage: python sync_manager.py <upload|download|list> [args]")
