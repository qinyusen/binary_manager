"""
冷备份管理器
提供定时调度、任务管理等功能
"""

import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
import logging

# 可选依赖，用于调度功能
try:
    import schedule
    import time

    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    schedule = None
    time = None

from .service import ColdBackupService
from ...shared import Config

logger = logging.getLogger(__name__)


class ColdBackupManager:
    """冷备份管理器，负责调度和管理冷备份任务"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """单例模式"""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, backup_service: Optional[ColdBackupService] = None):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.backup_service = backup_service
        self.scheduler_thread = None
        self.running = False
        self.tasks: Dict[str, Dict] = {}
        self.executing_tasks: Dict[str, threading.Thread] = {}
        self._initialized = True

    def initialize(
        self,
        backup_dir: str,
        storage_type: str = "local",
        storage_config: Optional[Dict] = None,
    ):
        """初始化备份管理器（兼容原有接口）"""
        from .service import ColdBackupService
        from .backends import LocalFileSystemBackend, S3ColdStorageBackend

        storage_config = storage_config or {}

        # 创建存储后端
        if storage_type == "local":
            backend = LocalFileSystemBackend(
                storage_path=storage_config.get("path", backup_dir)
            )
        elif storage_type == "s3":
            backend = S3ColdStorageBackend(
                bucket_name=storage_config["bucket"],
                access_key=storage_config.get("access_key"),
                secret_key=storage_config.get("secret_key"),
                endpoint_url=storage_config.get("endpoint_url"),
                region_name=storage_config.get("region", "us-east-1"),
                storage_class=storage_config.get("storage_class", "GLACIER"),
            )
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")

        # 创建服务
        self.backup_service = ColdBackupService(backend)
        logger.info(f"Cold backup manager initialized with {storage_type} storage")
        return {"status": "success", "message": "Cold backup manager initialized"}

    def add_scheduled_backup(
        self,
        task_id: str,
        task_type: str = "release",
        schedule_expr: str = "0 0 * * *",  # cron表达式
        config: Optional[Dict] = None,
        enabled: bool = True,
    ) -> bool:
        """添加定时备份任务"""
        if task_id in self.tasks:
            logger.warning(f"Task {task_id} already exists")
            return False

        self.tasks[task_id] = {
            "task_id": task_id,
            "type": task_type,
            "schedule": schedule_expr,
            "config": config or {},
            "enabled": enabled,
            "last_run": None,
            "last_status": None,
            "last_error": None,
        }

        if enabled and self.running and SCHEDULE_AVAILABLE:
            self._schedule_task(task_id)

        logger.info(f"Added scheduled backup task: {task_id}")
        return True

    def remove_scheduled_backup(self, task_id: str) -> bool:
        """移除定时备份任务"""
        if task_id not in self.tasks:
            return False

        del self.tasks[task_id]
        logger.info(f"Removed scheduled backup task: {task_id}")
        return True

    def _schedule_task(self, task_id: str):
        """调度任务"""
        if not SCHEDULE_AVAILABLE:
            logger.warning("schedule library not available, scheduled tasks disabled")
            return

        task = self.tasks.get(task_id)
        if not task or not task["enabled"]:
            return

        # 解析cron表达式并添加调度
        # 这里使用schedule库简化处理
        schedule.every().day.at("00:00").do(self._run_scheduled_task, task_id=task_id)

    def _run_scheduled_task(self, task_id: str):
        """运行定时任务"""
        if task_id in self.executing_tasks:
            logger.warning(f"Task {task_id} is already running, skipping")
            return

        task = self.tasks.get(task_id)
        if not task:
            return

        def task_wrapper():
            try:
                logger.info(f"Starting scheduled backup task: {task_id}")
                task["last_run"] = datetime.now().isoformat()

                # 执行备份
                if not self.backup_service:
                    raise ValueError("Backup service not initialized")

                if task["type"] == "release":
                    release_id = task["config"].get("release_id")
                    if release_id:
                        result = self.backup_service.create_release_backup(release_id)
                        task["last_status"] = "success"
                        logger.info(
                            f"Scheduled backup task {task_id} completed successfully: {result['backup_id']}"
                        )

                elif task["type"] == "full":
                    backup_name = task["config"].get(
                        "name", f"full_backup_{datetime.now().strftime('%Y%m%d')}"
                    )
                    result = self.backup_service.create_full_backup(backup_name)
                    task["last_status"] = "success"
                    logger.info(
                        f"Scheduled full backup {task_id} completed successfully: {result['backup_id']}"
                    )

            except Exception as e:
                task["last_status"] = "failed"
                task["last_error"] = str(e)
                logger.error(f"Scheduled backup task {task_id} failed: {str(e)}")
            finally:
                if task_id in self.executing_tasks:
                    del self.executing_tasks[task_id]

        thread = threading.Thread(target=task_wrapper, daemon=True)
        self.executing_tasks[task_id] = thread
        thread.start()

    def start_scheduler(self):
        """启动调度器"""
        if not SCHEDULE_AVAILABLE:
            logger.warning("schedule library not available, scheduler cannot start")
            return

        if self.running:
            logger.warning("Scheduler is already running")
            return

        self.running = True

        def scheduler_loop():
            logger.info("Cold backup scheduler started")

            # 调度所有启用的任务
            for task_id in self.tasks:
                if self.tasks[task_id]["enabled"]:
                    self._schedule_task(task_id)

            while self.running:
                schedule.run_pending()
                time.sleep(60)

            logger.info("Cold backup scheduler stopped")

        self.scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        self.scheduler_thread.start()

    def stop_scheduler(self):
        """停止调度器"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)

    def run_backup_now(
        self,
        task_type: str = "release",
        config: Optional[Dict] = None,
        background: bool = True,
    ):
        """立即执行备份任务"""
        task_id = f"manual_{task_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        config = config or {}

        def task_wrapper():
            try:
                logger.info(f"Starting manual {task_type} backup")

                if not self.backup_service:
                    raise ValueError("Backup service not initialized")

                if task_type == "release":
                    release_id = config.get("release_id")
                    if not release_id:
                        raise ValueError("release_id is required for release backup")

                    result = self.backup_service.create_release_backup(release_id)
                    logger.info(
                        f"Manual release backup completed: {result['backup_id']}"
                    )
                    return result

                elif task_type == "full":
                    backup_name = config.get(
                        "name", f"manual_full_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    )
                    result = self.backup_service.create_full_backup(backup_name)
                    logger.info(f"Manual full backup completed: {result['backup_id']}")
                    return result

            except Exception as e:
                logger.error(f"Manual backup failed: {str(e)}")
                raise
            finally:
                if task_id in self.executing_tasks:
                    del self.executing_tasks[task_id]

        if background:
            thread = threading.Thread(target=task_wrapper, daemon=True)
            self.executing_tasks[task_id] = thread
            thread.start()
            return task_id
        else:
            return task_wrapper()

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """获取任务状态"""
        if task_id in self.tasks:
            return self.tasks[task_id]

        if task_id in self.executing_tasks:
            return {"task_id": task_id, "status": "running"}

        return None

    def list_tasks(self) -> List[Dict]:
        """列出所有任务"""
        return list(self.tasks.values())

    def get_running_tasks(self) -> List[str]:
        """获取正在运行的任务"""
        return list(self.executing_tasks.keys())

    def get_backup_history(self, limit: int = 100) -> List[Dict]:
        """获取备份历史"""
        if not self.backup_service:
            return []

        backups = self.backup_service.list_backups()
        backups.sort(key=lambda x: x.get("stored_at", ""), reverse=True)
        return backups[:limit]


# 全局管理器实例
backup_manager = ColdBackupManager()


def initialize_backup_manager(backup_service: ColdBackupService):
    """初始化全局备份管理器"""
    backup_manager.backup_service = backup_service

    # 从配置加载定时任务
    scheduled_tasks = []  # 简化处理，暂时不加载配置
    for task in scheduled_tasks:
        backup_manager.add_scheduled_backup(
            task_id=task["id"],
            task_type=task.get("type", "release"),
            schedule_expr=task.get("schedule", "0 0 * * *"),
            config=task.get("config", {}),
            enabled=task.get("enabled", True),
        )

    # 自动启动调度器
    if SCHEDULE_AVAILABLE:
        backup_manager.start_scheduler()

    return backup_manager
