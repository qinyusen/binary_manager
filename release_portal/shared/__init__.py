import os
from pathlib import Path


class Config:
    BASE_DIR = Path(__file__).parent.parent
    
    @staticmethod
    def get_default_db_path() -> str:
        db_path = os.environ.get('RELEASE_PORTAL_DB', str(Config.BASE_DIR / 'data' / 'portal.db'))
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        return db_path
    
    @staticmethod
    def get_storage_path() -> str:
        storage = os.environ.get('RELEASE_PORTAL_STORAGE', str(Config.BASE_DIR / 'storage'))
        Path(storage).mkdir(parents=True, exist_ok=True)
        return storage
    
    @staticmethod
    def get_secret_key() -> str:
        return os.environ.get('RELEASE_PORTAL_SECRET', 'default-secret-key-change-in-production')
    
    @staticmethod
    def get_token_expiry_hours() -> int:
        return int(os.environ.get('RELEASE_PORTAL_TOKEN_EXPIRY_HOURS', '24'))


class ReleasePortalError(Exception):
    pass


class AuthenticationError(ReleasePortalError):
    pass


class AuthorizationError(ReleasePortalError):
    pass


class ValidationError(ReleasePortalError):
    pass


class NotFoundError(ReleasePortalError):
    pass
