import sqlite3
from pathlib import Path
from .shared import Config
from .infrastructure.database import (
    SQLiteRoleRepository,
    SQLiteUserRepository,
    SQLiteLicenseRepository,
    SQLiteReleaseRepository
)
from .infrastructure.auth import TokenService, PasswordHasher, UUIDGenerator
from .domain.value_objects import ResourceType, AccessLevel, Permission
from .domain.entities.role import Role
from .domain.entities.license import License


class DatabaseInitializer:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.get_default_db_path() or ":memory:"
    
    def initialize(self) -> None:
        self._create_schema()
        self._create_default_roles()
    
    def _create_schema(self) -> None:
        schema_path = Path(__file__).parent / 'infrastructure' / 'database' / 'schema.sql'
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Ensure database directory exists
        db_path_obj = Path(self.db_path)
        db_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()
        conn.close()
    
    def _create_default_roles(self) -> None:
        role_repo = SQLiteRoleRepository(self.db_path)
        
        admin_role = Role(
            role_id='role_admin',
            name='Admin',
            description='Administrator with full access'
        )
        admin_role.add_permission(Permission('publish', {ResourceType.BSP, ResourceType.DRIVER, ResourceType.EXAMPLES}))
        admin_role.add_permission(Permission('download', {ResourceType.BSP, ResourceType.DRIVER, ResourceType.EXAMPLES}))
        admin_role.add_permission(Permission('manage_users', set()))
        admin_role.add_permission(Permission('manage_licenses', set()))
        role_repo.save(admin_role)
        
        publisher_role = Role(
            role_id='role_publisher',
            name='Publisher',
            description='Can publish resources'
        )
        publisher_role.add_permission(Permission('publish', {ResourceType.BSP, ResourceType.DRIVER, ResourceType.EXAMPLES}))
        publisher_role.add_permission(Permission('download', {ResourceType.BSP, ResourceType.DRIVER, ResourceType.EXAMPLES}))
        role_repo.save(publisher_role)
        
        customer_role = Role(
            role_id='role_customer',
            name='Customer',
            description='Customer with download permissions based on license'
        )
        customer_role.add_permission(Permission('download', {ResourceType.BSP, ResourceType.DRIVER, ResourceType.EXAMPLES}))
        role_repo.save(customer_role)


def create_container(db_path: str = None):
    from .application import (
        AuthService, ReleaseService, DownloadService, 
        LicenseService, AuthorizationService, StorageServiceAdapter
    )
    from binary_manager_v2.application import PublisherService, DownloaderService
    from binary_manager_v2.infrastructure.database import SQLitePackageRepository
    
    db_path = db_path or Config.get_default_db_path() or ":memory:"
    
    role_repo = SQLiteRoleRepository(db_path)
    user_repo = SQLiteUserRepository(db_path, role_repo)
    license_repo = SQLiteLicenseRepository(db_path)
    release_repo = SQLiteReleaseRepository(db_path)
    package_repo = SQLitePackageRepository(db_path)
    
    token_service = TokenService(
        secret_key=Config.get_secret_key(),
        token_expiry_hours=Config.get_token_expiry_hours()
    )
    password_hasher = PasswordHasher()
    
    auth_service = AuthService(
        user_repository=user_repo,
        role_repository=role_repo,
        license_repository=license_repo,
        token_service=token_service,
        password_hasher=password_hasher
    )
    
    authorization_service = AuthorizationService(
        user_repository=user_repo,
        license_repository=license_repo
    )
    
    publisher_service = PublisherService(package_repository=package_repo)
    downloader_service = DownloaderService(package_repository=package_repo)
    
    storage_service = StorageServiceAdapter(
        publisher_service=publisher_service,
        downloader_service=downloader_service,
        package_repository=package_repo
    )
    
    release_service = ReleaseService(
        release_repository=release_repo,
        storage_service=storage_service,
        authorization_service=authorization_service
    )
    
    download_service = DownloadService(
        user_repository=user_repo,
        release_repository=release_repo,
        storage_service=storage_service,
        authorization_service=authorization_service
    )
    
    license_service = LicenseService(
        license_repository=license_repo
    )
    
    class Container:
        def __init__(self):
            self.auth_service = auth_service
            self.release_service = release_service
            self.download_service = download_service
            self.license_service = license_service
            self.authorization_service = authorization_service
            self.role_repository = role_repo
            self.user_repository = user_repo
            self.license_repository = license_repo
            self.release_repository = release_repo
            self.package_repository = package_repo
    
    return Container()
