"""
测试配置和工具函数
"""

import pytest
import tempfile
import tarfile
import os
import shutil


def create_test_bsp_package(version='1.0.0', board_name='rdk_x3'):
    """
    创建测试用的 BSP 包
    
    Args:
        version: 版本号
        board_name: 板卡名称
    
    Returns:
        (package_path, temp_dir) - 包路径和临时目录
    """
    temp_dir = tempfile.mkdtemp()
    bsp_dir = os.path.join(temp_dir, board_name)
    os.makedirs(bsp_dir)
    
    # 创建 BSP 目录结构
    os.makedirs(os.path.join(bsp_dir, 'bootloader'))
    os.makedirs(os.path.join(bsp_dir, 'kernel'))
    os.makedirs(os.path.join(bsp_dir, 'rootfs'))
    os.makedirs(os.path.join(bsp_dir, 'docs'))
    
    # 创建测试文件
    with open(os.path.join(bsp_dir, 'bootloader', 'bootloader.bin'), 'w') as f:
        f.write(f'{board_name} Bootloader v{version}')
    
    with open(os.path.join(bsp_dir, 'kernel', 'kernel.img'), 'w') as f:
        f.write(f'{board_name} Kernel v5.10')
    
    with open(os.path.join(bsp_dir, 'rootfs', 'rootfs.squashfs'), 'w') as f:
        f.write(f'{board_name} Root Filesystem')
    
    with open(os.path.join(bsp_dir, 'docs', 'README.md'), 'w') as f:
        f.write(f'# {board_name} BSP\n\nVersion {version}')
    
    # 创建 board_info.json
    import json
    board_info = {
        'board_name': board_name.upper(),
        'manufacturer': '地瓜机器人',
        'cpu_arch': 'arm64',
        'memory_size': '4GB',
        'storage_size': '32GB',
        'network_interfaces': ['eth0', 'wlan0'],
        'usb_ports': 4,
        'gpio_count': 40,
        'supported_os': ['Linux 5.10', 'Linux 5.15']
    }
    
    with open(os.path.join(bsp_dir, 'board_info.json'), 'w') as f:
        json.dump(board_info, f, indent=2)
    
    # 打包
    package_path = os.path.join(temp_dir, f'{board_name}_{version}.tar.gz')
    with tarfile.open(package_path, 'w:gz') as tar:
        tar.add(bsp_dir, arcname=board_name)
    
    return package_path, temp_dir


def create_test_driver_package(version='1.0.0', driver_name='wifi_driver'):
    """创建测试驱动包"""
    temp_dir = tempfile.mkdtemp()
    driver_dir = os.path.join(temp_dir, driver_name)
    os.makedirs(driver_dir)
    
    # 创建驱动文件
    with open(os.path.join(driver_dir, 'driver.ko'), 'w') as f:
        f.write(f'{driver_name} Kernel Module v{version}')
    
    with open(os.path.join(driver_dir, 'README.md'), 'w') as f:
        f.write(f'# {driver_name}\n\nVersion {version}')
    
    # 打包
    package_path = os.path.join(temp_dir, f'{driver_name}_{version}.tar.gz')
    with tarfile.open(package_path, 'w:gz') as tar:
        tar.add(driver_dir, arcname=driver_name)
    
    return package_path, temp_dir


def cleanup_temp_directory(temp_dir):
    """清理临时目录"""
    if temp_dir and os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)


class APIClient:
    """API 客户端包装类，简化测试代码"""
    
    def __init__(self, client, token=None):
        self.client = client
        self.token = token
    
    def get_headers(self):
        """获取请求头"""
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers
    
    def get(self, url, **kwargs):
        """GET 请求"""
        headers = self.get_headers()
        if 'headers' in kwargs:
            headers.update(kwargs.pop('headers'))
        return self.client.get(url, headers=headers, **kwargs)
    
    def post(self, url, **kwargs):
        """POST 请求"""
        headers = self.get_headers()
        if 'headers' in kwargs:
            headers.update(kwargs.pop('headers'))
        return self.client.post(url, headers=headers, **kwargs)
    
    def put(self, url, **kwargs):
        """PUT 请求"""
        headers = self.get_headers()
        if 'headers' in kwargs:
            headers.update(kwargs.pop('headers'))
        return self.client.put(url, headers=headers, **kwargs)
    
    def delete(self, url, **kwargs):
        """DELETE 请求"""
        headers = self.get_headers()
        if 'headers' in kwargs:
            headers.update(kwargs.pop('headers'))
        return self.client.delete(url, headers=headers, **kwargs)


@pytest.fixture
def api_client(client):
    """API 客户端 fixture"""
    return APIClient(client)


@pytest.fixture
def authenticated_api_client(client, auth_tokens):
    """已认证的 API 客户端 fixture"""
    return APIClient(client, auth_tokens['admin'])


@pytest.fixture
def publisher_api_client(client, auth_tokens):
    """发布者 API 客户端 fixture"""
    return APIClient(client, auth_tokens['publisher'])


@pytest.fixture
def customer_api_client(client, auth_tokens):
    """客户 API 客户端 fixture"""
    return APIClient(client, auth_tokens['customer'])
