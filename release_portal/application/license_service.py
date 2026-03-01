from typing import List, Optional
from datetime import datetime, timedelta
from ..domain.entities.license import License
from ..domain.value_objects import ResourceType, AccessLevel
from ..domain.repositories import LicenseRepository
from ..infrastructure.auth import UUIDGenerator


class LicenseService:
    def __init__(self, license_repository: LicenseRepository):
        self._license_repository = license_repository
    
    def create_license(
        self,
        organization: str,
        access_level: AccessLevel,
        allowed_resource_types: list,
        expires_at: Optional[datetime] = None,
        metadata: Optional[dict] = None
    ) -> License:
        license_id = UUIDGenerator.generate_license_id()
        
        resource_types = {
            ResourceType.from_string(rt) if isinstance(rt, str) else rt
            for rt in allowed_resource_types
        }
        
        license = License(
            license_id=license_id,
            organization=organization,
            access_level=access_level,
            allowed_resource_types=resource_types,
            expires_at=expires_at,
            metadata=metadata or {}
        )
        
        self._license_repository.save(license)
        return license
    
    def get_license(self, license_id: str) -> Optional[License]:
        return self._license_repository.find_by_id(license_id)
    
    def get_licenses_by_organization(self, organization: str) -> List[License]:
        return self._license_repository.find_by_organization(organization)
    
    def list_licenses(self, active_only: bool = False) -> List[License]:
        if active_only:
            return self._license_repository.find_active()
        return self._license_repository.find_all()
    
    def revoke_license(self, license_id: str) -> None:
        license = self._license_repository.find_by_id(license_id)
        if not license:
            raise ValueError(f"License '{license_id}' not found")
        
        license.deactivate()
        self._license_repository.save(license)
    
    def activate_license(self, license_id: str) -> None:
        license = self._license_repository.find_by_id(license_id)
        if not license:
            raise ValueError(f"License '{license_id}' not found")
        
        license.activate()
        self._license_repository.save(license)
    
    def extend_license(self, license_id: str, days: int) -> License:
        license = self._license_repository.find_by_id(license_id)
        if not license:
            raise ValueError(f"License '{license_id}' not found")
        
        if license.expires_at:
            license._expires_at = license.expires_at + timedelta(days=days)
        else:
            license._expires_at = datetime.utcnow() + timedelta(days=days)
        
        self._license_repository.save(license)
        return license
    
    def update_license_metadata(self, license_id: str, metadata: dict) -> License:
        license = self._license_repository.find_by_id(license_id)
        if not license:
            raise ValueError(f"License '{license_id}' not found")
        
        license._metadata = metadata
        self._license_repository.save(license)
        return license
