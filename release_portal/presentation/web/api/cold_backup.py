"""
冷备份 REST API
"""
from flask import Blueprint, request, jsonify, send_file
from ..auth_middleware import require_role
import sys
import os

# 添加项目根目录到路径
_project_root = os.path.join(os.path.dirname(__file__), '../../../..')
sys.path.insert(0, _project_root)

from release_portal.presentation.web.auth_middleware import require_role

cold_backup_bp = Blueprint('cold_backup', __name__)


def get_cold_backup_service():
    """获取冷备份服务实例"""
    from release_portal.application.cold_backup_service import ColdBackupManager
    
    manager = ColdBackupManager()
    
    # 从配置或请求中获取配置
    storage_type = request.args.get('storage_type', 'local')
    storage_config = {
        'storage_path': request.args.get('storage_path', './cold_storage'),
        'bucket': request.args.get('bucket', ''),
        'prefix': request.args.get('prefix', 'cold_backups/'),
        'region': request.args.get('region', 'us-east-1'),
        'retention_days': int(request.args.get('retention_days', 365))
    }
    
    try:
        return manager.initialize(
            backup_dir=request.args.get('backup_dir', './backups'),
            storage_type=storage_type,
            storage_config=storage_config
        )
    except Exception as e:
        return None


@cold_backup_bp.route('', methods=['GET'])
@require_role('Admin')
def list_cold_archives():
    """列出所有冷归档
    
    Response:
        {
            "archives": [
                {
                    "archive_id": "archive_20240302",
                    "hot_backup_name": "hot_backup_20240302_120000",
                    "created_at": "2024-03-02T12:00:00",
                    "expires_at": "2025-03-02T12:00:00",
                    "status": "archived"
                }
            ]
        }
    """
    try:
        service = get_cold_backup_service()
        
        if not service:
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'Failed to initialize cold backup service'
            }), 500
        
        archives = service.list_cold_archives()
        
        return jsonify({
            'archives': archives,
            'count': len(archives)
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@cold_backup_bp.route('/create', methods=['POST'])
@require_role('Admin')
def create_cold_backup():
    """创建冷备份
    
    Request:
        {
            "backup_name": "my_backup",  // 可选
            "include_storage": true,      // 可选
            "storage_type": "local",      // local 或 s3
            "storage_config": {...}        // 存储配置
        }
    
    Response:
        {
            "archive_id": "archive_20240302",
            "storage_type": "local",
            "size": 1024000,
            "stored_at": "2024-03-02T12:00:00"
        }
    """
    try:
        data = request.get_json() or {}
        
        backup_name = data.get('backup_name')
        include_storage = data.get('include_storage', True)
        storage_type = data.get('storage_type', 'local')
        storage_config = data.get('storage_config', {})
        
        from release_portal.application.cold_backup_service import ColdBackupManager
        
        manager = ColdBackupManager()
        service = manager.initialize(
            backup_dir=data.get('backup_dir', './backups'),
            storage_type=storage_type,
            storage_config=storage_config
        )
        
        archive_info = service.create_cold_backup(
            backup_name=backup_name,
            include_storage=include_storage
        )
        
        return jsonify(archive_info), 201
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@cold_backup_bp.route('/<archive_id>', methods=['GET'])
@require_role('Admin')
def get_cold_archive_info(archive_id: str):
    """获取冷归档详情
    
    Response:
        {
            "archive_id": "archive_20240302",
            "created_at": "2024-03-02T12:00:00",
            "expires_at": "2025-03-02T12:00:00",
            "metadata": {...}
        }
    """
    try:
        service = get_cold_backup_service()
        
        if not service:
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'Failed to initialize cold backup service'
            }), 500
        
        archives = service.list_cold_archives()
        archive = next((a for a in archives if a['archive_id'] == archive_id), None)
        
        if not archive:
            return jsonify({
                'error': 'Not Found',
                'message': f'Archive {archive_id} not found'
            }), 404
        
        return jsonify(archive), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@cold_backup_bp.route('/<archive_id>/retrieve', methods=['POST'])
@require_role('Admin')
def retrieve_cold_archive(archive_id: str):
    """从冷存储检索归档
    
    Request:
        {
            "restore_path": "/tmp/restore.tar.gz"
        }
    
    Response:
        {
            "success": true,
            "local_path": "/tmp/restore.tar.gz"
        }
    """
    try:
        data = request.get_json() or {}
        restore_path = data.get('restore_path', f'/tmp/{archive_id}.tar.gz')
        
        service = get_cold_backup_service()
        
        if not service:
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'Failed to initialize cold backup service'
            }), 500
        
        success = service.retrieve_from_cold_storage(archive_id, restore_path)
        
        if not success:
            return jsonify({
                'error': 'Not Found',
                'message': f'Failed to retrieve archive {archive_id}'
            }), 404
        
        return jsonify({
            'success': True,
            'archive_id': archive_id,
            'local_path': restore_path
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@cold_backup_bp.route('/<archive_id>', methods=['DELETE'])
@require_role('Admin')
def delete_cold_archive(archive_id: str):
    """删除冷归档
    
    Response:
        {
            "success": true,
            "message": "Archive deleted successfully"
        }
    """
    try:
        service = get_cold_backup_service()
        
        if not service:
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'Failed to initialize cold backup service'
            }), 500
        
        success = service.delete_cold_archive(archive_id)
        
        if not success:
            return jsonify({
                'error': 'Not Found',
                'message': f'Archive {archive_id} not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Archive deleted successfully'
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@cold_backup_bp.route('/cleanup', methods=['POST'])
@require_role('Admin')
def cleanup_expired_archives():
    """清理过期的归档
    
    Response:
        {
            "deleted_count": 3,
            "message": "Cleaned up 3 expired archives"
        }
    """
    try:
        service = get_cold_backup_service()
        
        if not service:
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'Failed to initialize cold backup service'
            }), 500
        
        deleted_count = service.cleanup_expired_archives()
        
        return jsonify({
            'deleted_count': deleted_count,
            'message': f'Cleaned up {deleted_count} expired archives'
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@cold_backup_bp.route('/policy', methods=['GET'])
@require_role('Admin')
def get_backup_policy():
    """获取备份策略
    
    Response:
        {
            "retention_days": 365,
            "scheduler_running": false,
            "storage_backend": "LocalFileSystemBackend",
            "archive_count": 10
        }
    """
    try:
        service = get_cold_backup_service()
        
        if not service:
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'Failed to initialize cold backup service'
            }), 500
        
        policy = service.get_backup_policy()
        
        return jsonify(policy), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@cold_backup_bp.route('/schedule', methods=['POST'])
@require_role('Admin')
def schedule_automatic_backup():
    """设置定时自动备份
    
    Request:
        {
            "interval_hours": 24
        }
    
    Response:
        {
            "success": true,
            "message": "Scheduled automatic backup every 24 hours"
        }
    """
    try:
        data = request.get_json() or {}
        interval_hours = data.get('interval_hours', 24)
        
        service = get_cold_backup_service()
        
        if not service:
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'Failed to initialize cold backup service'
            }), 500
        
        service.schedule_automatic_backup(interval_hours)
        
        return jsonify({
            'success': True,
            'message': f'Scheduled automatic backup every {interval_hours} hours'
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@cold_backup_bp.route('/storage-info', methods=['GET'])
@require_role('Admin')
def get_storage_info():
    """获取存储信息
    
    Response:
        {
            "storage_type": "local",
            "storage_path": "./cold_storage",
            "archive_count": 10,
            "total_size": 10240000
        }
    """
    try:
        service = get_cold_backup_service()
        
        if not service:
            return jsonify({
                'error': 'Internal Server Error',
                'message': 'Failed to initialize cold backup service'
            }), 500
        
        storage_info = service.get_storage_info()
        
        return jsonify(storage_info), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500
