from typing import Optional, List, Dict
from datetime import datetime


class Version:
    def __init__(
        self,
        major: int,
        minor: int,
        patch: int,
        prerelease: Optional[str] = None,
        build: Optional[str] = None
    ):
        self._major = major
        self._minor = minor
        self._patch = patch
        self._prerelease = prerelease
        self._build = build
    
    @property
    def major(self) -> int:
        return self._major
    
    @property
    def minor(self) -> int:
        return self._minor
    
    @property
    def patch(self) -> int:
        return self._patch
    
    @property
    def prerelease(self) -> Optional[str]:
        return self._prerelease
    
    @property
    def build(self) -> Optional[str]:
        return self._build
    
    @classmethod
    def parse(cls, version_string: str) -> 'Version':
        import re
        pattern = r'(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?:-(?P<prerelease>[a-zA-Z0-9.-]+))?(?:\+(?P<build>[a-zA-Z0-9.-]+))?'
        match = re.match(pattern, version_string)
        
        if not match:
            raise ValueError(f"Invalid version string: {version_string}")
        
        return cls(
            major=int(match.group('major')),
            minor=int(match.group('minor')),
            patch=int(match.group('patch')),
            prerelease=match.group('prerelease'),
            build=match.group('build')
        )
    
    def __str__(self) -> str:
        version = f"{self._major}.{self._minor}.{self._patch}"
        if self._prerelease:
            version += f"-{self._prerelease}"
        if self._build:
            version += f"+{self._build}"
        return version
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Version):
            return False
        return (self._major == other._major and
                self._minor == other._minor and
                self._patch == other._patch and
                self._prerelease == other._prerelease and
                self._build == other._build)
    
    def __lt__(self, other) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        
        if self._major != other._major:
            return self._major < other._major
        if self._minor != other._minor:
            return self._minor < other._minor
        if self._patch != other._patch:
            return self._patch < other._patch
        
        self_pre = self._prerelease or ''
        other_pre = other._prerelease or ''
        
        if not self_pre and not other_pre:
            return False
        if not self_pre:
            return False
        if not other_pre:
            return True
        
        return self_pre < other_pre
    
    def __hash__(self) -> int:
        return hash((self._major, self._minor, self._patch, self._prerelease, self._build))
    
    def __repr__(self) -> str:
        return f"Version('{self}')"
