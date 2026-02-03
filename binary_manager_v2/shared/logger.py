import logging
import sys
from pathlib import Path
from typing import Optional


class Logger:
    _loggers = {}
    
    @classmethod
    def get(cls, name: str) -> logging.Logger:
        if name not in cls._loggers:
            cls._loggers[name] = cls._create_logger(name)
        return cls._loggers[name]
    
    @classmethod
    def _create_logger(cls, name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.INFO)
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            
            logger.addHandler(handler)
        
        return logger
    
    @classmethod
    def set_level(cls, level: str) -> None:
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        
        for logger in cls._loggers.values():
            logger.setLevel(numeric_level)
            for handler in logger.handlers:
                handler.setLevel(numeric_level)
    
    @classmethod
    def configure(cls, config_path: Optional[str] = None) -> None:
        try:
            from .config import Config
            config = Config()
            config.load(config_path)
            
            level = config.get('logging.level', 'INFO')
            cls.set_level(level)
            
            format_str = config.get('logging.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            formatter = logging.Formatter(format_str)
            
            for logger in cls._loggers.values():
                for handler in logger.handlers:
                    handler.setFormatter(formatter)
        except Exception:
            pass
