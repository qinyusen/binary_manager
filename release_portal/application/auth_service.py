from typing import Optional
from ..domain.entities.user import User
from ..domain.repositories import UserRepository, LicenseRepository, RoleRepository
from ..infrastructure.auth import PasswordHasher, TokenService, UUIDGenerator


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        license_repository: LicenseRepository,
        token_service: TokenService,
        password_hasher: PasswordHasher
    ):
        self._user_repository = user_repository
        self._role_repository = role_repository
        self._license_repository = license_repository
        self._token_service = token_service
        self._password_hasher = password_hasher
    
    def register(
        self,
        username: str,
        email: str,
        password: str,
        role_id: str,
        license_id: Optional[str] = None
    ) -> User:
        if self._user_repository.exists_by_username(username):
            raise ValueError(f"Username '{username}' already exists")
        if self._user_repository.exists_by_email(email):
            raise ValueError(f"Email '{email}' already exists")
        
        from ..infrastructure.auth import UUIDGenerator
        
        role = self._role_repository.find_by_id(role_id)
        if not role:
            raise ValueError(f"Role '{role_id}' not found")
        
        user_id = UUIDGenerator.generate_user_id()
        password_hash = self._password_hasher.hash_password(password)
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            license_id=license_id
        )
        
        self._user_repository.save(user)
        return user
    
    def login(self, username: str, password: str) -> str:
        user = self._user_repository.find_by_username(username)
        if not user:
            raise ValueError("Invalid username or password")
        
        if not user.is_active:
            raise ValueError("User account is inactive")
        
        if not self._password_hasher.verify_password(password, user.password_hash):
            raise ValueError("Invalid username or password")
        
        token = self._token_service.generate_token(
            user_id=user.user_id,
            username=user.username,
            role=user.role.name
        )
        
        return token
    
    def verify_token(self, token: str) -> Optional[dict]:
        return self._token_service.verify_token(token)
    
    def get_user_from_token(self, token: str) -> Optional[User]:
        user_info = self._token_service.extract_user_info(token)
        if not user_info:
            return None
        return self._user_repository.find_by_id(user_info['user_id'])
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> None:
        user = self._user_repository.find_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        if not self._password_hasher.verify_password(old_password, user.password_hash):
            raise ValueError("Invalid old password")
        
        user._password_hash = self._password_hasher.hash_password(new_password)
        self._user_repository.save(user)
    
    def assign_license_to_user(self, user_id: str, license_id: str) -> None:
        """分配许可证给用户
        
        Args:
            user_id: 用户ID
            license_id: 许可证ID
        """
        user = self._user_repository.find_by_id(user_id)
        if not user:
            raise ValueError(f"User '{user_id}' not found")
        
        license = self._license_repository.find_by_id(license_id)
        if not license:
            raise ValueError(f"License '{license_id}' not found")
        
        user._license_id = license_id
        self._user_repository.save(user)
