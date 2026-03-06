"""
文件安全工具 - 验证上传文件的安全性
"""
import os
import magic
import logging
from typing import BinaryIO, Tuple, Optional
from urllib.parse import unquote

logger = logging.getLogger(__name__)


class FileSecurityError(Exception):
    """文件安全相关错误"""
    pass


class FileValidator:
    """文件验证器"""
    
    # 允许的 MIME 类型
    ALLOWED_MIMES = {
        'application/gzip',
        'application/x-gzip',
        'application/x-tar',
        'application/x-gtar',
        'application/zip',
        'application/x-zip',
        'application/x-zip-compressed'
    }
    
    # 允许的文件扩展名
    ALLOWED_EXTENSIONS = {'.tar.gz', '.tar', '.zip', '.tgz'}
    
    # 最大文件大小（500MB）
    MAX_FILE_SIZE = 500 * 1024 * 1024
    
    # 危险文件特征
    DANGEROUS_PATTERNS = [
        b'MZ',  # PE/Windows 可执行文件
        b'\x7fELF',  # Linux 可执行文件
        b'#!/',  # 脚本文件（如果被执行）
        b'<%',  # ASP/JSP 代码
        b'<?php',  # PHP 代码
    ]
    
    @classmethod
    def validate_file_upload(
        cls,
        filename: str,
        file_content: Optional[bytes] = None,
        file_size: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        验证上传的文件
        
        Args:
            filename: 文件名
            file_content: 文件内容（前 2048 字节用于类型检测）
            file_size: 文件大小
            
        Returns:
            (is_valid, error_message)
        """
        try:
            # 1. 检查文件名
            if not filename:
                return False, "文件名不能为空"
            
            # 2. 检查文件扩展名
            has_valid_ext = any(
                filename.lower().endswith(ext) 
                for ext in cls.ALLOWED_EXTENSIONS
            )
            if not has_valid_ext:
                return False, f"不支持的文件类型，仅支持: {', '.join(cls.ALLOWED_EXTENSIONS)}"
            
            # 3. 检查文件大小
            if file_size is not None:
                if file_size > cls.MAX_FILE_SIZE:
                    return False, f"文件过大，最大支持 {cls.MAX_FILE_SIZE // (1024*1024)}MB"
                
                if file_size == 0:
                    return False, "文件不能为空"
            
            # 4. 如果提供了文件内容，进行深度验证
            if file_content:
                # 4.1 验证 MIME 类型
                mime_valid, mime_error = cls._validate_mime_type(file_content)
                if not mime_valid:
                    return False, mime_error
                
                # 4.2 检查是否包含危险内容
                dangerous_valid, dangerous_error = cls._check_dangerous_content(file_content)
                if not dangerous_valid:
                    return False, dangerous_error
            
            return True, ""
        
        except Exception as e:
            logger.error(f"文件验证失败: {e}")
            return False, f"文件验证失败: {str(e)}"
    
    @classmethod
    def _validate_mime_type(cls, file_content: bytes) -> Tuple[bool, str]:
        """验证文件的 MIME 类型"""
        try:
            # 使用 python-magic 库检测文件类型
            mime = magic.from_buffer(file_content, mime=True)
            
            if mime not in cls.ALLOWED_MIMES:
                # 检查是否是文本文件（某些文本文件可能被误判）
                if cls._is_text_file(file_content):
                    return True, ""
                
                return False, f"检测到不安全的文件类型: {mime}"
            
            return True, ""
        
        except Exception as e:
            logger.warning(f"MIME 类型检测失败: {e}")
            # 如果 python-magic 不可用，使用简单验证
            return cls._validate_by_extension(file_content)
    
    @classmethod
    def _validate_by_extension(cls, file_content: bytes) -> Tuple[bool, str]:
        """基于扩展名的简单验证（备用方案）"""
        # 检查文件头
        if file_content[:2] == b'PK':
            # ZIP 文件
            return True, ""
        elif file_content[:2] == b'\x1f\x8b':
            # GZIP 文件
            return True, ""
        else:
            return False, "无法验证文件类型，请确保文件是有效的压缩包"
    
    @classmethod
    def _check_dangerous_content(cls, file_content: bytes) -> Tuple[bool, str]:
        """检查文件是否包含危险内容"""
        # 只检查前 2048 字节
        header = file_content[:2048]
        
        for pattern in cls.DANGEROUS_PATTERNS:
            if pattern in header:
                # 对于 tar/zip 文件，忽略这些模式（因为可能是合法内容）
                # 但对于明显的可执行文件，拒绝
                if header[:4] == b'MZ' or header[:4] == b'\x7fELF':
                    return False, "检测到可执行文件，不允许上传"
        
        return True, ""
    
    @classmethod
    def _is_text_file(cls, file_content: bytes) -> bool:
        """检查是否是文本文件"""
        try:
            file_content[:1024].decode('utf-8')
            return True
        except UnicodeDecodeError:
            return False
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """
        清理文件名，防止路径遍历攻击
        
        Args:
            filename: 原始文件名
            
        Returns:
            清理后的安全文件名
        """
        # 移除路径信息
        filename = os.path.basename(filename)
        
        # 移除危险字符
        filename = unquote(filename)
        filename = filename.replace('..', '').replace('/', '').replace('\\', '')
        
        # 限制文件名长度
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        
        # 如果文件名为空，使用默认名称
        if not filename or filename == '.':
            filename = 'package.tar.gz'
        
        return filename


def validate_uploaded_file(
    file_obj: BinaryIO,
    filename: str,
    max_size: Optional[int] = None
) -> Tuple[bool, str]:
    """
    验证上传的文件（便捷函数）
    
    Args:
        file_obj: 文件对象
        filename: 文件名
        max_size: 最大文件大小（可选，默认使用配置值）
        
    Returns:
        (is_valid, error_message)
    """
    # 读取文件内容（前 2048 字节用于类型检测）
    current_pos = file_obj.tell()
    file_obj.seek(0)
    file_content = file_obj.read(2048)
    file_obj.seek(current_pos)
    
    # 获取文件大小
    file_obj.seek(0, os.SEEK_END)
    file_size = file_obj.tell()
    file_obj.seek(current_pos)
    
    # 使用配置的最大值或传入的值
    max_file_size = max_size or FileValidator.MAX_FILE_SIZE
    
    # 验证文件
    return FileValidator.validate_file_upload(
        filename=filename,
        file_content=file_content,
        file_size=file_size
    )


# 兼容性检查
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    logger.warning("python-magic 未安装，文件类型检测功能受限")
    logger.warning("安装方法: pip install python-magic-bin (Windows) 或 pip install python-magic (Linux/Mac)")
