from typing import NewType
import hashlib


HashAlgorithm = NewType('HashAlgorithm', str)


class InvalidHashError(Exception):
    pass


class Hash:
    VALID_ALGORITHMS = {'sha256', 'sha512', 'md5'}
    
    def __init__(self, value: str, algorithm: str = 'sha256'):
        if not value:
            raise InvalidHashError("Hash value cannot be empty")
        
        if algorithm not in self.VALID_ALGORITHMS:
            raise InvalidHashError(f"Invalid hash algorithm: {algorithm}")
        
        self._value = value.lower()
        self._algorithm = algorithm
    
    @classmethod
    def from_string(cls, hash_string: str) -> 'Hash':
        if ':' in hash_string:
            algorithm, value = hash_string.split(':', 1)
            return cls(value, algorithm)
        return cls(hash_string, 'sha256')
    
    @classmethod
    def from_file(cls, file_path: str, algorithm: str = 'sha256') -> 'Hash':
        hash_func = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_func.update(chunk)
        return cls(hash_func.hexdigest(), algorithm)
    
    @property
    def algorithm(self) -> str:
        return self._algorithm
    
    @property
    def value(self) -> str:
        return self._value
    
    def __str__(self) -> str:
        return f"{self._algorithm}:{self._value}"
    
    def __repr__(self) -> str:
        return f"Hash(algorithm='{self._algorithm}', value='{self._value}')"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Hash):
            return False
        return self._algorithm == other._algorithm and self._value == other._value
    
    def __hash__(self) -> int:
        return hash((self._algorithm, self._value))
