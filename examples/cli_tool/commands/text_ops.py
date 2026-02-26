#!/usr/bin/env python3
"""
文本处理命令
"""
import json
from pathlib import Path


class TextCommands:
    """文本处理命令类"""
    
    def count(self, file_path):
        """统计文本"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"不是文件: {file_path}")
        
        chars = 0
        words = 0
        lines = 0
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                chars = len(content)
                words = len(content.split())
                lines = content.count('\n') + 1
        except UnicodeDecodeError:
            raise ValueError(f"不是文本文件: {file_path}")
        
        return {
            'chars': chars,
            'words': words,
            'lines': lines
        }
    
    def replace(self, file_path, old_text, new_text):
        """搜索替换"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"不是文件: {file_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            count = content.count(old_text)
            new_content = content.replace(old_text, new_text)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return count
        except UnicodeDecodeError:
            raise ValueError(f"不是文本文件: {file_path}")
    
    def format_json(self, file_path):
        """格式化JSON"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"不是文件: {file_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON格式错误: {e}")
        except UnicodeDecodeError:
            raise ValueError(f"不是文本文件: {file_path}")
