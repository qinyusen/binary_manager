from typing import NewType


PackageName = NewType('PackageName', str)


class InvalidPackageNameError(Exception):
    pass


class PackageName:
    VALID_PATTERN = r'^[a-zA-Z0-9_-]+$'
    
    def __init__(self, value: str):
        if not value:
            raise InvalidPackageNameError("Package name cannot be empty")
        
        if len(value) > 100:
            raise InvalidPackageNameError("Package name too long (max 100 characters)")
        
        if not self._is_valid(value):
            raise InvalidPackageNameError(f"Invalid package name: {value}")
        
        self._value = value
    
    def _is_valid(self, value: str) -> bool:
        import re
        return bool(re.match(self.VALID_PATTERN, value))
    
    @property
    def value(self) -> str:
        return self._value
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, PackageName):
            return False
        return self._value == other._value
    
    def __hash__(self) -> int:
        return hash(self._value)
    
    def __str__(self) -> str:
        return self._value
    
    def __repr__(self) -> str:
        return f"PackageName('{self._value}')"
