"""
备份 REST API
"""
from flask import Blueprint, request, jsonify, send_file
from release_portal.presentation.web.auth_middleware import require_role
import sys
import os

# 添加项目根目录到路径
_project_root = os.path.join(os.path.dirname(__file__), '../../../..')
sys.path.insert(0, _project_root)

from release_portal.presentation.web.auth_middleware import require_role

backup_bp = Blueprint('backup', __name__)


@backup_bp.route('', methods=['GET'])
@require_role('Admin')
def list_backups():
    """列出所有备份
    
    Response:
        {
            "backups": [
                {
                    "filename": "backup_20240302_120000.tar.gz",
                    "size": 1024000,
                    "created_at": "2024-03-02T12:00:00",
                    "checksum": "abc123...",
                    "metadata": {...}
                }
            ]
        }
    """
    try:
        from release_portal.application.backup_service import BackupService
        
        # 从配置获取数据库和存储路径
        db_path = request.args.get('db_path', './data/portal.db')
        storage_path = request.args.get('storage_path', './releases')
        backup_dir = request.args.get('backup_dir', './backups')
        
        backup_service = BackupService(
            db_path=db_path,
            storage_path=storage_path,
            backup_dir=backup_dir
        )
        
        backups = backup_service.list_backups()
        
        return jsonify({
            'backups': backups,
            'count': len(backups)
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@backup_bp.route('/create', methods=['POST'])
@require_role('Admin')
def create_backup():
    """创建备份
    
    Request:
        {
            "name": "my_backup",  // 可选
            "include_storage": true  // 可选，默认 true
        }
    
    Response:
        {
            "backup_id": "backup_20240302_120000",
            "filename": "backup_20240302_120000.tar.gz",
            "size": 1024000,
            "checksum": "abc123...",
            "created_at": "2024-03-02T12:00:00",
            "includes_storage": true
        }
    """
    try:
        from release_portal.application.backup_service import BackupService
        
        data = request.get_json() or {}
        
        name = data.get('name')
        include_storage = data.get('include_storage', True)
        
        db_path = data.get('db_path', './data/portal.db')
        storage_path = data.get('storage_path', './releases')
        backup_dir = data.get('backup_dir', './backups')
        
        backup_service = BackupService(
            db_path=db_path,
            storage_path=storage_path,
            backup_dir=backup_dir
        )
        
        backup_info = backup_service.create_backup(
            name=name,
            include_storage=include_storage
        )
        
        return jsonify(backup_info), 201
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@backup_bp.route('/<backup_filename>', methods=['GET'])
@require_role('Admin')
def get_backup_info(backup_filename: str):
    """获取备份详情
    
    Response:
        {
            "filename": "backup_20240302_120000.tar.gz",
            "size": 1024000,
            "created_at": "2024-03-02T12:00:00",
            "checksum": "abc123...",
            "metadata": {...}
        }
    """
    try:
        from release_portal.application.backup_service import BackupService
        
        db_path = request.args.get('db_path', './data/portal.db')
        storage_path = request.args.get('storage_path', './releases')
        backup_dir = request.args.get('backup_dir', './backups')
        
        backup_service = BackupService(
            db_path=db_path,
            storage_path=storage_path,
            backup_dir=backup_dir
        )
        
        backup_info = backup_service.get_backup_info(backup_filename)
        
        if not backup_info:
            return jsonify({
                'error': 'Not Found',
                'message': f'Backup {backup_filename} not found'
            }), 404
        
        return jsonify(backup_info), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@backup_bp.route('/<backup_filename>/download', methods=['GET'])
@require_role('Admin')
def download_backup(backup_filename: str):
    """下载备份文件
    
    Response: Binary file stream
    """
    try:
        from release_portal.application.backup_service import BackupService
        
        db_path = request.args.get('db_path', './data/portal.db')
        storage_path = request.args.get('storage_path', './releases')
        backup_dir = request.args.get('backup_dir', './backups')
        
        backup_service = BackupService(
            db_path=db_path,
            storage_path=storage_path,
            backup_dir=backup_dir
        )
        
        backup_path = backup_service.download_backup(backup_filename)
        
        if not backup_path:
            return jsonify({
                'error': 'Not Found',
                'message': f'Backup {backup_filename} not found'
            }), 404
        
        return send_file(
            backup_path,
            as_attachment=True,
            download_name=backup_filename
        )
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@backup_bp.route('/restore', methods=['POST'])
@require_role('Admin')
def restore_backup():
    """恢复备份
    
    Request:
        {
            "backup_filename": "backup_20240302_120000.tar.gz",
            "target_db_path": "./data/portal.db",  // 可选
            "target_storage_path": "./releases"  // 可选
        }
    
    Response:
        {
            "success": true,
            "backup_filename": "backup_20240302_120000.tar.gz",
            "restored_at": "2024-03-02T12:30:00",
            "metadata": {...}
        }
    """
    try:
        from release_portal.application.backup_service import BackupService
        
        data = request.get_json()
        
        if not data or 'backup_filename' not in data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'backup_filename is required'
            }), 400
        
        backup_filename = data['backup_filename']
        target_db_path = data.get('target_db_path')
        target_storage_path = data.get('target_storage_path')
        
        db_path = data.get('db_path', './data/portal.db')
        storage_path = data.get('storage_path', './releases')
        backup_dir = data.get('backup_dir', './backups')
        
        backup_service = BackupService(
            db_path=db_path,
            storage_path=storage_path,
            backup_dir=backup_dir
        )
        
        restore_info = backup_service.restore_backup(
            backup_filename=backup_filename,
            target_db_path=target_db_path,
            target_storage_path=target_storage_path
        )
        
        return jsonify(restore_info), 200
    
    except ValueError as e:
        return jsonify({
            'error': 'Bad Request',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@backup_bp.route('/<backup_filename>', methods=['DELETE'])
@require_role('Admin')
def delete_backup(backup_filename: str):
    """删除备份
    
    Response:
        {
            "success": true,
            "message": "Backup deleted successfully"
        }
    """
    try:
        from release_portal.application.backup_service import BackupService
        
        db_path = request.args.get('db_path', './data/portal.db')
        storage_path = request.args.get('storage_path', './releases')
        backup_dir = request.args.get('backup_dir', './backups')
        
        backup_service = BackupService(
            db_path=db_path,
            storage_path=storage_path,
            backup_dir=backup_dir
        )
        
        success = backup_service.delete_backup(backup_filename)
        
        if not success:
            return jsonify({
                'error': 'Not Found',
                'message': f'Backup {backup_filename} not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Backup deleted successfully'
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500
