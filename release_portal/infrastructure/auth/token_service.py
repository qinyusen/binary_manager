import hashlib
import uuid
from typing import Dict, Optional
from datetime import datetime, timedelta


class TokenService:
    def __init__(self, secret_key: str, token_expiry_hours: int = 24):
        self._secret_key = secret_key
        self._token_expiry_hours = token_expiry_hours
    
    def generate_token(self, user_id: str, username: str, role: str) -> str:
        import json
        import base64
        payload = {
            'user_id': user_id,
            'username': username,
            'role': role,
            'exp': int((datetime.utcnow() + timedelta(hours=self._token_expiry_hours)).timestamp()),
            'iat': int(datetime.utcnow().timestamp())
        }
        
        payload_json = json.dumps(payload, sort_keys=True)
        payload_b64 = base64.b64encode(payload_json.encode()).decode()
        signature = hashlib.sha256(f"{payload_b64}.{self._secret_key}".encode()).hexdigest()
        return f"{payload_b64}.{signature}"
    
    def verify_token(self, token: str) -> Optional[Dict]:
        try:
            import json
            import base64
            parts = token.split('.')
            if len(parts) != 2:
                return None
            
            payload_b64, signature = parts
            expected_signature = hashlib.sha256(f"{payload_b64}.{self._secret_key}".encode()).hexdigest()
            
            if signature != expected_signature:
                return None
            
            payload_json = base64.b64decode(payload_b64.encode()).decode()
            payload = json.loads(payload_json)
            
            exp = datetime.fromtimestamp(payload['exp'])
            if datetime.utcnow() > exp:
                return None
            
            return payload
        except Exception:
            return None
    
    def extract_user_info(self, token: str) -> Optional[Dict]:
        payload = self.verify_token(token)
        if not payload:
            return None
        return {
            'user_id': payload['user_id'],
            'username': payload['username'],
            'role': payload['role']
        }


class PasswordHasher:
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        return hashlib.sha256(password.encode()).hexdigest() == password_hash


class UUIDGenerator:
    @staticmethod
    def generate_user_id() -> str:
        return f"user_{uuid.uuid4().hex[:16]}"
    
    @staticmethod
    def generate_role_id() -> str:
        return f"role_{uuid.uuid4().hex[:16]}"
    
    @staticmethod
    def generate_license_id() -> str:
        return f"lic_{uuid.uuid4().hex}"
    
    @staticmethod
    def generate_release_id() -> str:
        return f"rel_{uuid.uuid4().hex[:16]}"
