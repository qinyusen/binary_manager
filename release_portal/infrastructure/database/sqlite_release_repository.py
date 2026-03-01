from typing import List, Optional
from datetime import datetime
from ...domain.entities.release import Release
from ...domain.value_objects import ResourceType, ReleaseStatus, ContentType
from ...domain.repositories import ReleaseRepository
from .base_repository import BaseSQLiteRepository


class SQLiteReleaseRepository(BaseSQLiteRepository, ReleaseRepository):
    def save(self, release: Release) -> None:
        self._execute_update(
            """INSERT OR REPLACE INTO releases 
               (release_id, resource_type, version, publisher_id, description, changelog, 
                source_package_id, binary_package_id, doc_package_id, status, created_at, published_at) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                release.release_id,
                str(release.resource_type),
                release.version,
                release.publisher_id,
                release.description,
                release.changelog,
                release.get_package_id(ContentType.SOURCE),
                release.get_package_id(ContentType.BINARY),
                release.get_package_id(ContentType.DOCUMENT),
                str(release.status),
                release.created_at.isoformat(),
                release.published_at.isoformat() if release.published_at else None
            )
        )
    
    def find_by_id(self, release_id: str) -> Optional[Release]:
        rows = self._execute_query(
            "SELECT * FROM releases WHERE release_id = ?",
            (release_id,)
        )
        if not rows:
            return None
        return self._row_to_release(rows[0])
    
    def find_by_resource_type(self, resource_type: ResourceType) -> List[Release]:
        rows = self._execute_query(
            "SELECT * FROM releases WHERE resource_type = ? ORDER BY created_at DESC",
            (str(resource_type),)
        )
        return [self._row_to_release(row) for row in rows]
    
    def find_by_version(self, resource_type: ResourceType, version: str) -> Optional[Release]:
        rows = self._execute_query(
            "SELECT * FROM releases WHERE resource_type = ? AND version = ?",
            (str(resource_type), version)
        )
        if not rows:
            return None
        return self._row_to_release(rows[0])
    
    def find_by_status(self, status: ReleaseStatus) -> List[Release]:
        rows = self._execute_query(
            "SELECT * FROM releases WHERE status = ? ORDER BY created_at DESC",
            (str(status),)
        )
        return [self._row_to_release(row) for row in rows]
    
    def find_by_publisher(self, publisher_id: str) -> List[Release]:
        rows = self._execute_query(
            "SELECT * FROM releases WHERE publisher_id = ? ORDER BY created_at DESC",
            (publisher_id,)
        )
        return [self._row_to_release(row) for row in rows]
    
    def find_all(self) -> List[Release]:
        rows = self._execute_query("SELECT * FROM releases ORDER BY created_at DESC")
        return [self._row_to_release(row) for row in rows]
    
    def delete(self, release_id: str) -> None:
        self._execute_update(
            "DELETE FROM releases WHERE release_id = ?",
            (release_id,)
        )
    
    def exists_by_id(self, release_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM releases WHERE release_id = ?",
                (release_id,)
            )
            return cursor.fetchone() is not None
    
    def _row_to_release(self, row) -> Release:
        release = Release(
            release_id=row['release_id'],
            resource_type=ResourceType.from_string(row['resource_type']),
            version=row['version'],
            publisher_id=row['publisher_id'],
            description=row['description'],
            changelog=row['changelog']
        )
        
        if row['source_package_id']:
            release.add_package(ContentType.SOURCE, row['source_package_id'])
        if row['binary_package_id']:
            release.add_package(ContentType.BINARY, row['binary_package_id'])
        if row['doc_package_id']:
            release.add_package(ContentType.DOCUMENT, row['doc_package_id'])
        
        release._status = ReleaseStatus.from_string(row['status'])
        release._created_at = datetime.fromisoformat(row['created_at'])
        if row['published_at']:
            release._published_at = datetime.fromisoformat(row['published_at'])
        
        return release
