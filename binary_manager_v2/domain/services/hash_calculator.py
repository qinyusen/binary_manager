import hashlib
from typing import BinaryIO
from ..value_objects import Hash


class HashCalculator:
    
    def __init__(self, algorithm: str = 'sha256'):
        if algorithm not in Hash.VALID_ALGORITHMS:
            raise ValueError(f"Invalid hash algorithm: {algorithm}")
        self._algorithm = algorithm
    
    def calculate_file(self, file_path: str) -> Hash:
        hash_func = hashlib.new(self._algorithm)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_func.update(chunk)
        return Hash(hash_func.hexdigest(), self._algorithm)
    
    def calculate_string(self, data: str, encoding: str = 'utf-8') -> Hash:
        hash_func = hashlib.new(self._algorithm)
        hash_func.update(data.encode(encoding))
        return Hash(hash_func.hexdigest(), self._algorithm)
    
    def calculate_bytes(self, data: bytes) -> Hash:
        hash_func = hashlib.new(self._algorithm)
        hash_func.update(data)
        return Hash(hash_func.hexdigest(), self._algorithm)
    
    def calculate_stream(self, stream: BinaryIO) -> Hash:
        hash_func = hashlib.new(self._algorithm)
        for chunk in iter(lambda: stream.read(8192), b''):
            hash_func.update(chunk)
        return Hash(hash_func.hexdigest(), self._algorithm)
    
    @property
    def algorithm(self) -> str:
        return self._algorithm
