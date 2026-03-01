from typing import Protocol, Union


class IStorageService(Protocol):
    """存储服务接口，用于发布和下载包"""
    
    def publish_package(
        self,
        source_dir: str,
        package_name: str,
        version: str,
        extract_git: bool = True
    ) -> dict:
        """发布包到存储系统
        
        Args:
            source_dir: 源代码目录
            package_name: 包名
            version: 版本号
            extract_git: 是否从 git 提取信息
            
        Returns:
            包含 package_id 的字典
        """
        ...
    
    def download_package(self, package_id: Union[str, int], output_dir: str) -> None:
        """从存储系统下载包
        
        Args:
            package_id: 包ID（可以是字符串或整数）
            output_dir: 输出目录
        """
        ...
    
    def get_package_info(self, package_id: Union[str, int]) -> dict:
        """获取包信息
        
        Args:
            package_id: 包ID（可以是字符串或整数）
            
        Returns:
            包信息字典
        """
        ...
