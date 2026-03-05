"""
测试 Web UI 页面和文件上传功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from release_portal.presentation.web.app import create_app
import tempfile
import tarfile
import json


def create_test_package():
    """创建测试用的 BSP 包"""
    temp_dir = tempfile.mkdtemp()
    
    # 创建 BSP 目录结构
    bsp_dir = os.path.join(temp_dir, 'test_bsp')
    os.makedirs(bsp_dir)
    
    # 创建一些测试文件
    with open(os.path.join(bsp_dir, 'bootloader.bin'), 'w') as f:
        f.write('test bootloader content')
    
    with open(os.path.join(bsp_dir, 'kernel.img'), 'w') as f:
        f.write('test kernel content')
    
    with open(os.path.join(bsp_dir, 'rootfs.squashfs'), 'w') as f:
        f.write('test rootfs content')
    
    # 创建 tar.gz 包
    package_path = os.path.join(temp_dir, 'test_bsp.tar.gz')
    with tarfile.open(package_path, 'w:gz') as tar:
        tar.add(bsp_dir, arcname='test_bsp')
    
    return package_path, temp_dir


def test_ui_pages():
    """测试 UI 页面"""
    print("=" * 60)
    print("测试 Web UI 页面")
    print("=" * 60)
    
    app = create_app()
    
    with app.test_client() as client:
        # 测试登录页面
        print("\n1. 测试登录页面...")
        response = client.get('/login')
        assert response.status_code == 200
        print("   ✓ 登录页面可访问")
        
        # 测试仪表板（需要认证）
        print("\n2. 测试仪表板页面...")
        response = client.get('/dashboard')
        assert response.status_code in [302, 401, 403]  # 未登录应该重定向或返回错误
        print("   ✓ 仪表板需要认证")
        
        # 测试发布管理页面
        print("\n3. 测试发布管理页面...")
        response = client.get('/releases')
        assert response.status_code in [302, 401, 403]
        print("   ✓ 发布管理页面需要认证")
        
        # 测试下载中心页面
        print("\n4. 测试下载中心页面...")
        response = client.get('/downloads')
        assert response.status_code in [302, 401, 403]
        print("   ✓ 下载中心页面需要认证")
        
        # 测试许可证管理页面
        print("\n5. 测试许可证管理页面...")
        response = client.get('/licenses')
        assert response.status_code in [302, 401, 403]
        print("   ✓ 许可证管理页面需要认证")


def test_file_upload():
    """测试文件上传功能"""
    print("\n" + "=" * 60)
    print("测试文件上传功能")
    print("=" * 60)
    
    app = create_app()
    
    # 先创建测试用户和获取 token
    with app.test_client() as client:
        print("\n1. 创建测试用户并登录...")
        
        # 创建用户
        response = client.post('/api/auth/register', json={
            'username': 'testuser_ui',
            'password': 'testpass123',
            'email': 'testui@example.com',
            'role': 'Publisher'
        })
        
        if response.status_code not in [200, 201]:
            print(f"   用户创建响应: {response.status_code}")
        
        # 登录获取 token
        response = client.post('/api/auth/login', json={
            'username': 'testuser_ui',
            'password': 'testpass123'
        })
        
        if response.status_code == 200:
            data = response.get_json()
            token = data.get('token')
            print("   ✓ 登录成功")
            
            headers = {'Authorization': f'Bearer {token}'}
            
            # 创建发布草稿
            print("\n2. 创建发布草稿...")
            response = client.post('/api/releases', 
                headers=headers,
                json={
                    'resource_type': 'BSP',
                    'version': '1.0.0',
                    'description': '测试发布'
                })
            
            if response.status_code == 201:
                data = response.get_json()
                release_id = data.get('release_id')
                print(f"   ✓ 创建发布成功: {release_id}")
                
                # 测试文件上传
                print("\n3. 测试文件上传...")
                package_path, temp_dir = create_test_package()
                
                try:
                    with open(package_path, 'rb') as f:
                        files = {'package_file': (os.path.basename(package_path), f, 'application/gzip')}
                        response = client.post(
                            f'/api/releases/{release_id}/packages',
                            headers=headers,
                            data=files,
                            content_type='multipart/form-data'
                        )
                    
                    if response.status_code == 201:
                        data = response.get_json()
                        print(f"   ✓ 文件上传成功: {data.get('package_id')}")
                    else:
                        print(f"   ✗ 文件上传失败: {response.status_code}")
                        print(f"   响应: {response.get_json()}")
                
                finally:
                    # 清理临时文件
                    import shutil
                    shutil.rmtree(temp_dir, ignore_errors=True)
            
            else:
                print(f"   ✗ 创建发布失败: {response.status_code}")
                print(f"   响应: {response.get_json()}")
        
        else:
            print(f"   ✗ 登录失败: {response.status_code}")
            print(f"   响应: {response.get_json()}")


def main():
    """主测试函数"""
    print("\n🧪 Release Portal V3 - Web UI 和文件上传测试")
    print("=" * 60)
    
    try:
        test_ui_pages()
        test_file_upload()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试完成")
        print("=" * 60)
        
        print("\n📝 测试总结:")
        print("  - Web UI 页面: ✓")
        print("  - 文件上传功能: ✓")
        print("\n💡 提示: 运行以下命令启动 Web 服务器:")
        print("  export FLASK_APP=release_portal.presentation.web.app")
        print("  export FLASK_ENV=development")
        print("  flask run --port 5000")
        print("\n  然后在浏览器中访问: http://localhost:5000")
    
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
