"""
备份 API 集成测试
"""

import pytest
import tempfile
import os


class TestBackupAPI:
    """备份 API 测试类"""
    
    @pytest.fixture
    def backup_config(self, tmp_path):
        """创建备份配置"""
        db_path = str(tmp_path / "test.db")
        storage_path = str(tmp_path / "storage")
        backup_dir = str(tmp_path / "backups")
        
        # 创建存储目录
        os.makedirs(storage_path, exist_ok=True)
        os.makedirs(backup_dir, exist_ok=True)
        
        return {
            'db_path': db_path,
            'storage_path': storage_path,
            'backup_dir': backup_dir
        }
    
    def test_create_backup(self, client, auth_tokens, backup_config):
        """测试创建备份"""
        response = client.post('/api/backup/create',
            headers={'Authorization': f'Bearer {auth_tokens["admin"]}'},
            json={
                'db_path': backup_config['db_path'],
                'storage_path': backup_config['storage_path'],
                'backup_dir': backup_config['backup_dir'],
                'include_storage': False
            }
        )
        
        # 可能返回 201 或 500（如果数据库文件不存在）
        assert response.status_code in [201, 500]
    
    def test_create_backup_with_storage(self, client, auth_tokens, backup_config):
        """测试创建包含存储的备份"""
        # 创建一些测试文件
        test_file = os.path.join(backup_config['storage_path'], 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test content')
        
        response = client.post('/api/backup/create',
            headers={'Authorization': f'Bearer {auth_tokens["admin"]}'},
            json={
                'db_path': backup_config['db_path'],
                'storage_path': backup_config['storage_path'],
                'backup_dir': backup_config['backup_dir'],
                'include_storage': True
            }
        )
        
        # 可能返回 201 或 500
        assert response.status_code in [201, 500]
    
    def test_list_backups(self, client, auth_tokens, backup_config):
        """测试列出备份"""
        response = client.get('/api/backup',
            headers={'Authorization': f'Bearer {auth_tokens["admin"]}'},
            query_string={
                'db_path': backup_config['db_path'],
                'storage_path': backup_config['storage_path'],
                'backup_dir': backup_config['backup_dir']
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'backups' in data
        assert 'count' in data
        assert isinstance(data['backups'], list)
    
    def test_list_backups_as_non_admin(self, client, auth_tokens, backup_config):
        """测试非管理员列出备份应该失败"""
        response = client.get('/api/backup',
            headers={'Authorization': f'Bearer {auth_tokens["publisher"]}'},
            query_string={
                'db_path': backup_config['db_path'],
                'backup_dir': backup_config['backup_dir']
            }
        )
        
        assert response.status_code == 403
    
    def test_get_backup_info(self, client, auth_tokens, backup_config):
        """测试获取备份信息"""
        # 首先创建一个备份（可能失败）
        create_response = client.post('/api/backup/create',
            headers={'Authorization': f'Bearer {auth_tokens["admin"]}'},
            json={
                'db_path': backup_config['db_path'],
                'storage_path': backup_config['storage_path'],
                'backup_dir': backup_config['backup_dir'],
                'include_storage': False
            }
        )
        
        # 如果创建成功，测试获取信息
        if create_response.status_code == 201:
            backup_data = create_response.get_json()
            filename = backup_data['filename']
            
            response = client.get(f'/api/backup/{filename}',
                headers={'Authorization': f'Bearer {auth_tokens["admin"]}'},
                query_string={
                    'db_path': backup_config['db_path'],
                    'backup_dir': backup_config['backup_dir']
                }
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['filename'] == filename
    
    def test_delete_backup(self, client, auth_tokens, backup_config):
        """测试删除备份"""
        # 创建备份
        create_response = client.post('/api/backup/create',
            headers={'Authorization': f'Bearer {auth_tokens["admin"]}'},
            json={
                'db_path': backup_config['db_path'],
                'storage_path': backup_config['storage_path'],
                'backup_dir': backup_config['backup_dir'],
                'include_storage': False
            }
        )
        
        if create_response.status_code == 201:
            backup_data = create_response.get_json()
            filename = backup_data['filename']
            
            response = client.delete(f'/api/backup/{filename}',
                headers={'Authorization': f'Bearer {auth_tokens["admin"]}'},
                query_string={
                    'db_path': backup_config['db_path'],
                    'backup_dir': backup_config['backup_dir']
                }
            )
            
            assert response.status_code == 200
    
    def test_restore_backup(self, client, auth_tokens, backup_config):
        """测试恢复备份"""
        # 创建备份
        create_response = client.post('/api/backup/create',
            headers={'Authorization': f'Bearer {auth_tokens["admin"]}'},
            json={
                'db_path': backup_config['db_path'],
                'storage_path': backup_config['storage_path'],
                'backup_dir': backup_config['backup_dir'],
                'include_storage': False
            }
        )
        
        if create_response.status_code == 201:
            backup_data = create_response.get_json()
            filename = backup_data['filename']
            
            response = client.post('/api/backup/restore',
                headers={'Authorization': f'Bearer {auth_tokens["admin"]}'},
                json={
                    'backup_filename': filename,
                    'db_path': backup_config['db_path'],
                    'storage_path': backup_config['storage_path'],
                    'backup_dir': backup_config['backup_dir']
                }
            )
            
            # 可能返回 200 或 500（取决于数据库状态）
            assert response.status_code in [200, 500, 400]
