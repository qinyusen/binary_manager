"""
临时文件管理器 - 自动清理临时文件
"""
import os
import time
import shutil
import threading
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Set

logger = logging.getLogger(__name__)


class TempFileManager:
    """临时文件管理器"""
    
    def __init__(self, max_age_hours: int = 1, cleanup_interval_minutes: int = 30):
        """
        初始化临时文件管理器
        
        Args:
            max_age_hours: 文件最大保留时间（小时）
            cleanup_interval_minutes: 清理间隔（分钟）
        """
        self.max_age = timedelta(hours=max_age_hours)
        self.cleanup_interval = cleanup_interval_minutes * 60
        self.temp_directories: Set[str] = set()
        self._running = False
        self._cleanup_thread: Optional[threading.Thread] = None
        
    def register_temp_dir(self, temp_dir: str) -> None:
        """
        注册临时目录，由管理器跟踪和清理
        
        Args:
            temp_dir: 临时目录路径
        """
        self.temp_directories.add(temp_dir)
        logger.debug(f"注册临时目录: {temp_dir}")
    
    def create_temp_dir(self, prefix: str = 'release_portal_') -> str:
        """
        创建临时目录并自动注册
        
        Args:
            prefix: 目录名前缀
            
        Returns:
            临时目录路径
        """
        temp_dir = tempfile.mkdtemp(prefix=prefix)
        self.register_temp_dir(temp_dir)
        return temp_dir
    
    def cleanup_temp_dir(self, temp_dir: str) -> bool:
        """
        立即清理指定的临时目录
        
        Args:
            temp_dir: 临时目录路径
            
        Returns:
            是否成功清理
        """
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
                self.temp_directories.discard(temp_dir)
                logger.debug(f"清理临时目录: {temp_dir}")
                return True
            return False
        except Exception as e:
            logger.error(f"清理临时目录失败 {temp_dir}: {e}")
            return False
    
    def cleanup_old_files(self) -> Dict[str, int]:
        """
        清理所有过期的临时文件
        
        Returns:
            清理统计信息 {'cleaned_dirs': 数量, 'freed_space': 字节数}
        """
        cleaned_dirs = 0
        freed_space = 0
        now = datetime.now()
        
        for temp_dir in list(self.temp_directories):
            try:
                if not os.path.exists(temp_dir):
                    self.temp_directories.discard(temp_dir)
                    continue
                
                # 检查目录年龄
                dir_stat = os.stat(temp_dir)
                dir_mtime = datetime.fromtimestamp(dir_stat.st_mtime)
                dir_age = now - dir_mtime
                
                if dir_age > self.max_age:
                    # 计算目录大小
                    dir_size = self._get_dir_size(temp_dir)
                    
                    # 删除目录
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    self.temp_directories.discard(temp_dir)
                    
                    cleaned_dirs += 1
                    freed_space += dir_size
                    logger.info(f"清理过期临时目录: {temp_dir} (年龄: {dir_age}, 大小: {dir_size} 字节)")
            
            except Exception as e:
                logger.error(f"清理临时目录失败 {temp_dir}: {e}")
        
        return {
            'cleaned_dirs': cleaned_dirs,
            'freed_space': freed_space
        }
    
    def _get_dir_size(self, directory: str) -> int:
        """计算目录大小"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        continue
        except Exception:
            pass
        return total_size
    
    def start_auto_cleanup(self) -> None:
        """启动自动清理线程"""
        if self._running:
            logger.warning("自动清理线程已在运行")
            return
        
        self._running = True
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()
        logger.info(f"自动清理线程已启动 (间隔: {self.cleanup_interval}秒)")
    
    def stop_auto_cleanup(self) -> None:
        """停止自动清理线程"""
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5)
            logger.info("自动清理线程已停止")
    
    def _cleanup_loop(self) -> None:
        """清理循环"""
        while self._running:
            try:
                time.sleep(self.cleanup_interval)
                if not self._running:
                    break
                
                stats = self.cleanup_old_files()
                if stats['cleaned_dirs'] > 0:
                    logger.info(
                        f"清理完成: {stats['cleaned_dirs']} 个目录, "
                        f"释放 {stats['freed_space'] / (1024*1024):.2f} MB"
                    )
            
            except Exception as e:
                logger.error(f"自动清理失败: {e}")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        total_size = 0
        dir_count = 0
        
        for temp_dir in self.temp_directories:
            if os.path.exists(temp_dir):
                total_size += self._get_dir_size(temp_dir)
                dir_count += 1
        
        return {
            'tracked_dirs': dir_count,
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'directories': list(self.temp_directories)
        }


# 全局单例
_temp_file_manager: Optional[TempFileManager] = None
_manager_lock = threading.Lock()


def get_temp_file_manager() -> TempFileManager:
    """获取全局临时文件管理器单例"""
    global _temp_file_manager
    
    if _temp_file_manager is None:
        with _manager_lock:
            if _temp_file_manager is None:
                _temp_file_manager = TempFileManager()
                _temp_file_manager.start_auto_cleanup()
    
    return _temp_file_manager


def cleanup_temp_dirs() -> None:
    """清理所有临时目录（便捷函数）"""
    manager = get_temp_file_manager()
    manager.cleanup_old_files()


import tempfile
from typing import Optional
import threading
