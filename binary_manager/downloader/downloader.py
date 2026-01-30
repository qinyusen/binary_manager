import os
import requests
from pathlib import Path
from typing import Optional
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Downloader:
    def __init__(self, chunk_size: int = 8192, timeout: int = 30):
        self.chunk_size = chunk_size
        self.timeout = timeout

    def download_file(self, url: str, output_path: str, 
                     show_progress: bool = True) -> str:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Downloading from: {url}")
        logger.info(f"Saving to: {output_path}")

        response = requests.get(url, stream=True, timeout=self.timeout)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))

        mode = 'wb'
        progress_bar = None

        if show_progress and total_size > 0:
            progress_bar = tqdm(
                total=total_size,
                unit='B',
                unit_scale=True,
                desc=f"Downloading {output_file.name}"
            )

        with open(output_file, mode) as f:
            for chunk in response.iter_content(chunk_size=self.chunk_size):
                if chunk:
                    f.write(chunk)
                    if progress_bar:
                        progress_bar.update(len(chunk))

        if progress_bar:
            progress_bar.close()

        file_size = output_file.stat().st_size
        logger.info(f"Download completed: {file_size} bytes")

        return str(output_file)

    def download_with_retry(self, url: str, output_path: str,
                           max_retries: int = 3, show_progress: bool = True) -> Optional[str]:
        for attempt in range(max_retries):
            try:
                return self.download_file(url, output_path, show_progress)
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed after {max_retries} attempts")
                    return None
                logger.info(f"Retrying...")

        return None

    def get_remote_file_info(self, url: str) -> dict:
        try:
            response = requests.head(url, timeout=self.timeout)
            response.raise_for_status()

            info = {
                'url': url,
                'size': int(response.headers.get('content-length', 0)),
                'content_type': response.headers.get('content-type', 'unknown')
            }

            return info
        except Exception as e:
            logger.error(f"Error getting remote file info: {e}")
            return {}


def download_package(url: str, output_path: str, max_retries: int = 3) -> Optional[str]:
    downloader = Downloader()
    return downloader.download_with_retry(url, output_path, max_retries)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 2:
        url = sys.argv[1]
        output = sys.argv[2]
        result = download_package(url, output)
        if result:
            print(f"Downloaded: {result}")
        else:
            print("Download failed")
            sys.exit(1)
