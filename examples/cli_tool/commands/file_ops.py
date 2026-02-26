#!/usr/bin/env python3
"""
文件操作命令
"""
import os
import hashlib
from pathlib import Path


class FileCommands:
    """文件操作命令类"""
    
    def stats(self, file_path):
        """获取文件统计信息"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"不是文件: {file_path}")
        
        size = path.stat().st_size
        
        # 统计行数和单词数（如果是文本文件）
        lines = 0
        words = 0
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    lines += 1
                    words += len(line.split())
        except UnicodeDecodeError:
            # 二进制文件
            pass
        
        return {
            'path': str(path.absolute()),
            'size': size,
            'lines': lines,
            'words': words
        }
    
    def find_duplicates(self, dir_path):
        """查找重复文件"""
        path = Path(dir_path)
        
        if not path.exists():
            raise FileNotFoundError(f"目录不存在: {dir_path}")
        
        if not path.is_dir():
            raise ValueError(f"不是目录: {dir_path}")
        
        # 按哈希分组文件
        hash_groups = {}
        
        for file_path in path.rglob('*'):
            if file_path.is_file():
                try:
                    file_hash = self._calculate_hash(file_path)
                    if file_hash not in hash_groups:
                        hash_groups[file_hash] = []
                    hash_groups[file_hash].append(str(file_path))
                except (PermissionError, OSError):
                    continue
        
        # 返回有重复的组
        duplicates = []
        for i, (hash_val, files) in enumerate(hash_groups.items()):
            if len(files) > 1:
                duplicates.append({
                    'id': i + 1,
                    'hash': hash_val,
                    'files': files
                })
        
        return duplicates
    
    def rename(self, dir_path, pattern='*', prefix=''):
        """批量重命名文件"""
        path = Path(dir_path)
        
        if not path.exists():
            raise FileNotFoundError(f"目录不存在: {dir_path}")
        
        if not path.is_dir():
            raise ValueError(f"不是目录: {dir_path}")
        
        count = 0
        for file_path in path.glob(pattern):
            if file_path.is_file():
                new_name = prefix + file_path.name
                new_path = file_path.parent / new_name
                
                if not new_path.exists():
                    file_path.rename(new_path)
                    count += 1
        
        return count
    
    def _calculate_hash(self, file_path, chunk_size=8192):
        """计算文件哈希"""
        hasher = hashlib.md5()
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        
        return hasher.hexdigest()
