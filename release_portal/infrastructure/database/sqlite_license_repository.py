import json
from typing import List, Optional
from datetime import datetime
from ...domain.entities.license import License
from ...domain.value_objects import ResourceType, AccessLevel
from ...domain.repositories import LicenseRepository
from .base_repository import BaseSQLiteRepository


class SQLiteLicenseRepository(BaseSQLiteRepository, LicenseRepository):
    def save(self, license_obj: License) -> None:
        self._execute_update(
            """INSERT OR REPLACE INTO licenses 
               (license_id, organization, access_level, expires_at, is_active, created_at, metadata) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                license_obj.license_id,
                license_obj.organization,
                str(license_obj.access_level),
                license_obj.expires_at.isoformat() if license_obj.expires_at else None,
                license_obj.is_active,
                license_obj.created_at.isoformat(),
                json.dumps(license_obj.metadata)
            )
        )
        
        self._execute_update(
            "DELETE FROM license_resource_types WHERE license_id = ?",
            (license_obj.license_id,)
        )
        
        for resource_type in license_obj.allowed_resource_types:
            self._execute_update(
                "INSERT INTO license_resource_types (license_id, resource_type) VALUES (?, ?)",
                (license_obj.license_id, str(resource_type))
            )
    
    def find_by_id(self, license_id: str) -> Optional[License]:
        rows = self._execute_query(
            "SELECT * FROM licenses WHERE license_id = ?",
            (license_id,)
        )
        if not rows:
            return None
        return self._row_to_license(rows[0])
    
    def find_by_organization(self, organization: str) -> List[License]:
        rows = self._execute_query(
            "SELECT * FROM licenses WHERE organization = ? ORDER BY created_at DESC",
            (organization,)
        )
        return [self._row_to_license(row) for row in rows]
    
    def find_all(self) -> List[License]:
        rows = self._execute_query("SELECT * FROM licenses ORDER BY created_at DESC")
        return [self._row_to_license(row) for row in rows]
    
    def find_active(self) -> List[License]:
        rows = self._execute_query(
            "SELECT * FROM licenses WHERE is_active = 1 ORDER BY created_at DESC"
        )
        return [self._row_to_license(row) for row in rows]
    
    def delete(self, license_id: str) -> None:
        self._execute_update(
            "DELETE FROM licenses WHERE license_id = ?",
            (license_id,)
        )
    
    def exists_by_id(self, license_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM licenses WHERE license_id = ?",
                (license_id,)
            )
            return cursor.fetchone() is not None
    
    def _row_to_license(self, row) -> License:
        rt_rows = self._execute_query(
            "SELECT resource_type FROM license_resource_types WHERE license_id = ?",
            (row['license_id'],)
        )
        resource_types = {
            ResourceType.from_string(rt_row['resource_type'])
            for rt_row in rt_rows
        }
        
        license_obj = License(
            license_id=row['license_id'],
            organization=row['organization'],
            access_level=AccessLevel.from_string(row['access_level']),
            allowed_resource_types=resource_types,
            expires_at=datetime.fromisoformat(row['expires_at']) if row['expires_at'] else None,
            metadata=json.loads(row['metadata']) if row['metadata'] else {}
        )
        license_obj._created_at = datetime.fromisoformat(row['created_at'])
        license_obj._is_active = bool(row['is_active'])
        return license_obj
