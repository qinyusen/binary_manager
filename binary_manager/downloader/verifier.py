import os
import json
import zipfile
import hashlib
from pathlib import Path
from typing import Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Verifier:
    @staticmethod
    def extract_hash_string(hash_str: str) -> tuple:
        if ':' in hash_str:
            algorithm, hash_value = hash_str.split(':', 1)
            return algorithm, hash_value
        else:
            return 'sha256', hash_str

    @staticmethod
    def calculate_file_hash(file_path: Path, algorithm='sha256') -> str:
        hash_func = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()

    def verify_file_hash(self, file_path: str, expected_hash: str) -> bool:
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            logger.error(f"File does not exist: {file_path}")
            return False

        algorithm, expected_value = self.extract_hash_string(expected_hash)
        actual_hash = self.calculate_file_hash(file_path_obj, algorithm)

        if actual_hash == expected_value:
            logger.info(f"Hash verified: {file_path}")
            return True
        else:
            logger.error(f"Hash mismatch for {file_path}")
            logger.error(f"Expected: {expected_value}")
            logger.error(f"Actual: {actual_hash}")
            return False

    def extract_zip(self, zip_path: str, target_dir: str) -> bool:
        zip_file = Path(zip_path)
        target_path = Path(target_dir)
        
        if not zip_file.exists():
            logger.error(f"Zip file does not exist: {zip_path}")
            return False

        target_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Extracting {zip_path} to {target_dir}")

        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(target_path)
            
            logger.info("Extraction completed successfully")
            return True
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return False

    def load_config(self, config_path: str) -> Dict:
        config_file = Path(config_path)
        
        if not config_file.exists():
            logger.error(f"Config file does not exist: {config_path}")
            return {}

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"Config loaded: {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}

    def validate_config_structure(self, config: Dict) -> bool:
        required_fields = [
            'package_name',
            'version',
            'created_at',
            'file_info',
            'files'
        ]

        for field in required_fields:
            if field not in config:
                logger.error(f"Missing required field: {field}")
                return False

        required_file_info = ['archive_name', 'size', 'file_count', 'hash']
        for field in required_file_info:
            if field not in config['file_info']:
                logger.error(f"Missing file_info field: {field}")
                return False

        logger.info("Config structure is valid")
        return True

    def verify_extracted_files(self, config: Dict, target_dir: str) -> bool:
        target_path = Path(target_dir)
        all_valid = True

        logger.info("Verifying extracted files...")

        for file_info in config['files']:
            file_path = target_path / file_info['path']
            
            if not file_path.exists():
                logger.error(f"File missing: {file_info['path']}")
                all_valid = False
                continue

            if not self.verify_file_hash(str(file_path), file_info['hash']):
                all_valid = False

        if all_valid:
            logger.info("All files verified successfully")
        else:
            logger.error("Some files failed verification")

        return all_valid


def verify_package(zip_path: str, config: Dict) -> bool:
    verifier = Verifier()
    archive_hash = config['file_info']['hash']
    return verifier.verify_file_hash(zip_path, archive_hash)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        verifier = Verifier()
        
        if sys.argv[1] == 'verify':
            if len(sys.argv) > 3:
                file_path = sys.argv[2]
                hash_value = sys.argv[3]
                result = verifier.verify_file_hash(file_path, hash_value)
                print(f"Verification: {'PASSED' if result else 'FAILED'}")
                sys.exit(0 if result else 1)
        
        elif sys.argv[1] == 'extract':
            if len(sys.argv) > 3:
                zip_path = sys.argv[2]
                target_dir = sys.argv[3]
                result = verifier.extract_zip(zip_path, target_dir)
                print(f"Extraction: {'SUCCESS' if result else 'FAILED'}")
                sys.exit(0 if result else 1)
        
        elif sys.argv[1] == 'load':
            if len(sys.argv) > 2:
                config = verifier.load_config(sys.argv[2])
                if config:
                    print(json.dumps(config, indent=2))
                else:
                    sys.exit(1)
