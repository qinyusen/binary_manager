import os
import hashlib
import base64
import hmac
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from urllib3 import PoolManager, HTTPResponse
from ...domain.repositories import StorageRepository
from ...shared.logger import Logger


class S3Storage(StorageRepository):
    """AWS S3存储实现（使用urllib3）"""
    
    def __init__(
        self,
        bucket_name: str,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        region: str = 'us-east-1',
        endpoint_url: Optional[str] = None
    ):
        self.bucket_name = bucket_name
        self.access_key = access_key or os.environ.get('AWS_ACCESS_KEY_ID')
        self.secret_key = secret_key or os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.region = region
        
        if endpoint_url:
            self.endpoint = endpoint_url
        else:
            self.endpoint = f"s3.{region}.amazonaws.com"
        
        self.http = PoolManager()
        self.logger = Logger.get(self.__class__.__name__)
    
    def _get_host(self) -> str:
        if self.region == 'us-east-1':
            return f"{self.bucket_name}.s3.amazonaws.com"
        return f"{self.bucket_name}.s3.{self.region}.amazonaws.com"
    
    def _get_signed_url(self, key: str, expiration: int = 3600) -> str:
        """生成预签名URL"""
        expiration_time = datetime.utcnow() + timedelta(seconds=expiration)
        timestamp = expiration_time.strftime('%Y%m%dT%H%M%SZ')
        date_stamp = expiration_time.strftime('%Y%m%d')
        
        method = 'GET'
        canonical_uri = f'/{key}'
        canonical_querystring = f'X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential={self.access_key}/{date_stamp}/{self.region}/s3/aws4_request&X-Amz-Date={timestamp}&X-Amz-Expires={expiration}&X-Amz-SignedHeaders=host'
        
        canonical_headers = f'host:{self._get_host()}\n'
        signed_headers = 'host'
        
        payload_hash = hashlib.sha256(b'').hexdigest()
        
        canonical_request = (
            f'{method}\n{canonical_uri}\n{canonical_querystring}\n'
            f'{canonical_headers}\n{signed_headers}\n{payload_hash}'
        )
        
        credential_scope = f'{date_stamp}/{self.region}/s3/aws4_request'
        string_to_sign = (
            f'AWS4-HMAC-SHA256\n{timestamp}\n{credential_scope}\n'
            f'{hashlib.sha256(canonical_request.encode()).hexdigest()}'
        )
        
        def sign(key: bytes, msg: str) -> bytes:
            return hmac.new(key, msg.encode(), hashlib.sha256).digest()
        
        k_date = sign(f'AWS4{self.secret_key}'.encode(), date_stamp)
        k_region = sign(k_date, self.region)
        k_service = sign(k_region, 's3')
        k_signing = sign(k_service, 'aws4_request')
        
        signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()
        
        canonical_querystring += f'&X-Amz-Signature={signature}'
        
        return f'https://{self._get_host()}/{key}?{canonical_querystring}'
    
    def upload_file(
        self,
        local_path: str,
        remote_path: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        try:
            with open(local_path, 'rb') as f:
                file_data = f.read()
            
            url = f'https://{self._get_host()}/{remote_path}'
            headers = {
                'Content-Type': 'application/octet-stream',
                'x-amz-content-sha256': hashlib.sha256(file_data).hexdigest()
            }
            
            if metadata:
                for key, value in metadata.items():
                    headers[f'x-amz-meta-{key}'] = str(value)
            
            response: HTTPResponse = self.http.request(
                'PUT',
                url,
                body=file_data,
                headers=headers
            )
            
            if response.status >= 200 and response.status < 300:
                self.logger.info(f"Uploaded {local_path} to s3://{self.bucket_name}/{remote_path}")
                return True
            else:
                self.logger.error(f"Upload failed: {response.status} {response.data}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to upload file: {e}")
            return False
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        try:
            from pathlib import Path
            local_file = Path(local_path)
            local_file.parent.mkdir(parents=True, exist_ok=True)
            
            url = f'https://{self._get_host()}/{remote_path}'
            response: HTTPResponse = self.http.request('GET', url)
            
            if response.status >= 200 and response.status < 300:
                with open(local_path, 'wb') as f:
                    f.write(response.data)
                self.logger.info(f"Downloaded s3://{self.bucket_name}/{remote_path} to {local_path}")
                return True
            else:
                self.logger.error(f"Download failed: {response.status}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to download file: {e}")
            return False
    
    def file_exists(self, remote_path: str) -> bool:
        try:
            url = f'https://{self._get_host()}/{remote_path}'
            response: HTTPResponse = self.http.request('HEAD', url)
            return response.status == 200
        except Exception:
            return False
    
    def delete_file(self, remote_path: str) -> bool:
        try:
            url = f'https://{self._get_host()}/{remote_path}'
            response: HTTPResponse = self.http.request('DELETE', url)
            
            if response.status >= 200 and response.status < 300:
                self.logger.info(f"Deleted s3://{self.bucket_name}/{remote_path}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to delete file: {e}")
            return False
    
    def list_files(self, prefix: str) -> List[str]:
        try:
            url = f'https://{self._get_host()}/?list-type=2&prefix={prefix}'
            response: HTTPResponse = self.http.request('GET', url)
            
            if response.status == 200:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.data)
                ns = {'s3': 'http://s3.amazonaws.com/doc/2006-03-01/'}
                contents = root.findall('s3:Contents', ns)
                return [c.find('s3:Key', ns).text for c in contents]
            return []
        except Exception as e:
            self.logger.error(f"Failed to list files: {e}")
            return []
    
    def get_file_url(self, remote_path: str, expiration: int = 3600) -> Optional[str]:
        return self._get_signed_url(remote_path, expiration)
    
    def verify_file(self, local_path: str, expected_hash: str) -> bool:
        try:
            if ':' in expected_hash:
                algorithm, hash_value = expected_hash.split(':', 1)
            else:
                algorithm = 'sha256'
                hash_value = expected_hash
            
            hash_func = hashlib.new(algorithm)
            with open(local_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hash_func.update(chunk)
            
            actual_hash = hash_func.hexdigest()
            return actual_hash.lower() == hash_value.lower()
        except Exception as e:
            self.logger.error(f"Failed to verify file: {e}")
            return False
