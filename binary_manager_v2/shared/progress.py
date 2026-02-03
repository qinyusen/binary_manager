from abc import ABC, abstractmethod
from typing import Optional


class ProgressReporter(ABC):
    
    @abstractmethod
    def start(self, total: int, description: str = "") -> None:
        pass
    
    @abstractmethod
    def update(self, progress: int, description: Optional[str] = None) -> None:
        pass
    
    @abstractmethod
    def finish(self) -> None:
        pass
    
    @abstractmethod
    def set_description(self, description: str) -> None:
        pass


class ConsoleProgress(ProgressReporter):
    
    def __init__(self):
        self._total = 0
        self._progress = 0
        self._description = ""
        self._started = False
    
    def start(self, total: int, description: str = "") -> None:
        self._total = total
        self._progress = 0
        self._description = description
        self._started = True
        self._print()
    
    def update(self, progress: int, description: Optional[str] = None) -> None:
        self._progress = progress
        if description:
            self._description = description
        if self._started:
            self._print()
    
    def finish(self) -> None:
        if self._started:
            print(f"{self._description} completed!")
        self._started = False
    
    def set_description(self, description: str) -> None:
        self._description = description
        if self._started:
            self._print()
    
    def _print(self) -> None:
        if self._total > 0:
            percent = (self._progress / self._total) * 100
            print(f"\r{self._description}: {percent:.1f}% ({self._progress}/{self._total})", end='', flush=True)
        else:
            print(f"\r{self._description}: {self._progress}", end='', flush=True)


class TqdmProgress(ProgressReporter):
    
    def __init__(self):
        self._tqdm = None
        self._available = False
        
        try:
            from tqdm import tqdm
            self._tqdm_class = tqdm
            self._available = True
        except ImportError:
            pass
    
    def start(self, total: int, description: str = "") -> None:
        if self._available:
            self._tqdm = self._tqdm_class(
                total=total,
                desc=description,
                unit='B',
                unit_scale=True,
                unit_divisor=1024
            )
        else:
            self._console = ConsoleProgress()
            self._console.start(total, description)
    
    def update(self, progress: int, description: Optional[str] = None) -> None:
        if self._available and self._tqdm:
            delta = progress - self._tqdm.n
            self._tqdm.update(delta)
            if description:
                self._tqdm.set_description(description)
        elif hasattr(self, '_console'):
            self._console.update(progress, description)
    
    def finish(self) -> None:
        if self._available and self._tqdm:
            self._tqdm.close()
            self._tqdm = None
        elif hasattr(self, '_console'):
            self._console.finish()
    
    def set_description(self, description: str) -> None:
        if self._available and self._tqdm:
            self._tqdm.set_description(description)
        elif hasattr(self, '_console'):
            self._console.set_description(description)


def create_progress(use_tqdm: bool = False) -> ProgressReporter:
    if use_tqdm:
        return TqdmProgress()
    return ConsoleProgress()
