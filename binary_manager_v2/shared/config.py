import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    _instance = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load(self, config_path: Optional[str] = None) -> None:
        if config_path is None:
            config_path = os.environ.get(
                'BINARY_MANAGER_CONFIG',
                str(Path(__file__).parent.parent / 'config' / 'config.json')
            )
        
        config_file = Path(config_path)
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                self._config = json.load(f)
        else:
            self._config = self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        return {
            'database': {
                'path': './database/binary_manager.db'
            },
            'storage': {
                'type': 'local',
                'local_path': './releases'
            },
            's3': {
                'enabled': False,
                'bucket': '',
                'region': 'us-east-1',
                'access_key': '',
                'secret_key': ''
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self, config_path: Optional[str] = None) -> None:
        if config_path is None:
            config_path = str(Path(__file__).parent.parent / 'config' / 'config.json')
        
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    def __getattr__(self, name: str) -> Any:
        if name.startswith('s3_'):
            key = f's3.{name[3:]}'
            defaults = {
                's3_enabled': False,
                's3_region': 'us-east-1'
            }
            return self.get(key, defaults.get(name, ''))
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    @property
    def database_path(self) -> str:
        return self.get('database.path', './database/binary_manager.db')
    
    @property
    def storage_type(self) -> str:
        return self.get('storage.type', 'local')
