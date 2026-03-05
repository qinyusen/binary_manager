"""
发布 API 集成测试
"""

import pytest
import tempfile
import tarfile
import os


class TestReleasesAPI:
    """发布 API 测试类"""
    
    @pytest.fixture
    def create_test_package(self):
        """创建测试包文件"""
        def _create_package():
            temp_dir = tempfile.mkdtemp()
            bsp_dir = os.path.join(temp_dir, 'test_bsp')
            os.makedirs(bsp_dir)
            
            # 创建测试文件
            with open(os.path.join(bsp_dir, 'bootloader.bin'), 'w') as f:
                f.write('test bootloader')
            with open(os.path.join(bsp_dir, 'kernel.img'), 'w') as f:
                f.write('test kernel')
            
            # 打包
            package_path = os.path.join(temp_dir, 'test_bsp.tar.gz')
            with tarfile.open(package_path, 'w:gz') as tar:
                tar.add(bsp_dir, arcname='test_bsp')
            
            return package_path, temp_dir
        return _create_package
    
    def test_list_releases(self, client, auth_tokens):
        """测试列出所有发布"""
        response = client.get('/api/releases', 
            headers={'Authorization': f'Bearer {auth_tokens["admin"]}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'releases' in data
        assert 'count' in data
        assert isinstance(data['releases'], list)
    
    def test_create_release_draft(self, client, auth_tokens):
        """测试创建发布草稿"""
        response = client.post('/api/releases',
            headers={'Authorization': f'Bearer {auth_tokens["publisher"]}'},
            json={
                'resource_type': 'BSP',
                'version': '1.0.0',
                'description': '测试 BSP 发布',
                'changelog': '初始版本'
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'release_id' in data
        assert data['status'] == 'DRAFT'
        assert data['version'] == '1.0.0'
    
    def test_create_release_missing_fields(self, client, auth_tokens):
        """测试创建发布缺少必填字段"""
        response = client.post('/api/releases',
            headers={'Authorization': f'Bearer {auth_tokens["publisher"]}'},
            json={
                'resource_type': 'BSP'
                # 缺少 version
            }
        )
        
        assert response.status_code == 400
    
    def test_get_release_details(self, client, auth_tokens, container):
        """测试获取发布详情"""
        # 先创建一个发布
        from release_portal.domain.value_objects import ResourceType
        release = container.release_service.create_draft(
            resource_type=ResourceType.BSP,
            version='1.0.0',
            publisher_id='test_publisher',
            description='测试发布'
        )
        
        # 获取详情
        response = client.get(f'/api/releases/{release.release_id}',
            headers={'Authorization': f'Bearer {auth_tokens["admin"]}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'release' in data
        assert data['release']['release_id'] == release.release_id
    
    def test_get_nonexistent_release(self, client, auth_tokens):
        """测试获取不存在的发布"""
        response = client.get('/api/releases/nonexistent_id',
            headers={'Authorization': f'Bearer {auth_tokens["admin"]}'}
        )
        
        assert response.status_code == 404
    
    def test_publish_release(self, client, auth_tokens, container):
        """测试发布版本"""
        # 创建草稿
        from release_portal.domain.value_objects import ResourceType
        release = container.release_service.create_draft(
            resource_type=ResourceType.BSP,
            version='1.0.0',
            publisher_id='test_publisher',
            description='测试发布'
        )
        
        # 发布
        response = client.post(f'/api/releases/{release.release_id}/publish',
            headers={'Authorization': f'Bearer {auth_tokens["publisher"]}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'PUBLISHED'
    
    def test_archive_release(self, client, auth_tokens, container):
        """测试归档版本"""
        # 创建并发布
        from release_portal.domain.value_objects import ResourceType
        release = container.release_service.create_draft(
            resource_type=ResourceType.BSP,
            version='1.0.0',
            publisher_id='test_publisher',
            description='测试发布'
        )
        container.release_service.publish_release(release.release_id, 'test_publisher')
        
        # 归档
        response = client.post(f'/api/releases/{release.release_id}/archive',
            headers={'Authorization': f'Bearer {auth_tokens["publisher"]}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ARCHIVED'
    
    def test_upload_package_to_release(self, client, auth_tokens, container, create_test_package):
        """测试上传包文件到发布"""
        # 创建草稿
        from release_portal.domain.value_objects import ResourceType
        release = container.release_service.create_draft(
            resource_type=ResourceType.BSP,
            version='1.0.0',
            publisher_id='test_publisher',
            description='测试发布'
        )
        
        # 创建测试包
        package_path, temp_dir = create_test_package()
        
        try:
            # 上传包
            with open(package_path, 'rb') as f:
                response = client.post(
                    f'/api/releases/{release.release_id}/packages',
                    headers={
                        'Authorization': f'Bearer {auth_tokens["publisher"]}'
                    },
                    data={
                        'package_file': (f, 'test_bsp.tar.gz'),
                        'content_type': 'BINARY'
                    },
                    content_type='multipart/form-data'
                )
            
            assert response.status_code == 201
            data = response.get_json()
            assert 'package_id' in data
        finally:
            # 清理
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_filter_releases_by_type(self, client, auth_tokens):
        """测试按类型筛选发布"""
        response = client.get('/api/releases?type=BSP',
            headers={'Authorization': f'Bearer {auth_tokens["admin"]}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'releases' in data
    
    def test_filter_releases_by_status(self, client, auth_tokens):
        """测试按状态筛选发布"""
        response = client.get('/api/releases?status=PUBLISHED',
            headers={'Authorization': f'Bearer {auth_tokens["admin"]}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'releases' in data
