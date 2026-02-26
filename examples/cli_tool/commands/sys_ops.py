#!/usr/bin/env python3
"""
系统操作命令
"""
import platform
import psutil
import shutil


class SystemCommands:
    """系统操作命令类"""
    
    def info(self):
        """获取系统信息"""
        return {
            'os': platform.system(),
            'os_version': platform.version(),
            'arch': platform.machine(),
            'hostname': platform.node(),
            'python_version': platform.python_version()
        }
    
    def disk(self):
        """获取磁盘使用情况"""
        disks = []
        
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'total': self._format_bytes(usage.total),
                    'used': self._format_bytes(usage.used),
                    'free': self._format_bytes(usage.free),
                    'percent': f"{usage.percent:.1f}"
                })
            except PermissionError:
                continue
        
        return disks
    
    def processes(self):
        """获取进程列表"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu': f"{proc.info['cpu_percent']:.1f}"
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # 按CPU使用率排序
        processes.sort(key=lambda x: float(x['cpu']), reverse=True)
        
        return processes
    
    def _format_bytes(self, bytes_value):
        """格式化字节数"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
