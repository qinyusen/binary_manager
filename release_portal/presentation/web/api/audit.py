"""
审计日志 REST API
"""
from flask import Blueprint, request, jsonify
from ..auth_middleware import require_role
import sys
import os

# 添加项目根目录到路径
_project_root = os.path.join(os.path.dirname(__file__), '../../../..')
sys.path.insert(0, _project_root)

from release_portal.presentation.web.auth_middleware import require_role

audit_bp = Blueprint('audit', __name__)


@audit_bp.route('/logs', methods=['GET'])
@require_role('Admin')
def list_audit_logs():
    """查询审计日志
    
    Query Parameters:
        user_id: 用户ID筛选
        username: 用户名筛选（支持模糊搜索）
        action: 操作类型
        resource_type: 资源类型
        resource_id: 资源ID
        status: 状态筛选
        start_date: 开始日期 (ISO8601)
        end_date: 结束日期 (ISO8601)
        limit: 返回数量限制（默认100）
        offset: 偏移量（默认0）
    
    Response:
        {
            "logs": [...],
            "count": 100,
            "total": 1500
        }
    """
    try:
        from ...initializer import create_container
        from ...domain.entities.audit_log import AuditLogFilter, AuditAction
        
        container = create_container()
        
        # 获取查询参数
        user_id = request.args.get('user_id')
        username = request.args.get('username')
        action_str = request.args.get('action')
        resource_type = request.args.get('resource_type')
        resource_id = request.args.get('resource_id')
        status = request.args.get('status')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        # 构建过滤器
        filters = {}
        if user_id:
            filters['user_id'] = user_id
        if username:
            filters['username'] = username
        if action_str:
            filters['action'] = AuditAction.from_string(action_str)
        if resource_type:
            filters['resource_type'] = resource_type
        if resource_id:
            filters['resource_id'] = resource_id
        if status:
            filters['status'] = status
        if start_date_str:
            from datetime import datetime
            filters['start_date'] = datetime.fromisoformat(start_date_str)
        if end_date_str:
            from datetime import datetime
            filters['end_date'] = datetime.fromisoformat(end_date_str)
        
        filter_obj = AuditLogFilter(**filters) if filters else None
        
        # 查询日志
        logs = container.audit_service.query_logs(filter_obj, limit, offset)
        total = container.audit_service.get_log_count(filter_obj)
        
        # 转换为字典
        logs_data = [log.to_dict() for log in logs]
        
        return jsonify({
            'logs': logs_data,
            'count': len(logs_data),
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@audit_bp.route('/logs/statistics', methods=['GET'])
@require_role('Admin')
def get_statistics():
    """获取审计统计信息
    
    Query Parameters:
        start_date: 开始日期 (ISO8601)
        end_date: 结束日期 (ISO8601)
        user_id: 用户ID
    
    Response:
        {
            "action_stats": {
                "LOGIN": 150,
                "RELEASE_CREATE": 50,
                ...
            },
            "user_activity": {
                "total_actions": 500,
                "unique_actions": 15,
                "last_activity": "2024-03-02T12:00:00"
            }
        }
    """
    try:
        from ...initializer import create_container
        from datetime import datetime
        
        container = create_container()
        
        # 获取参数
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        user_id = request.args.get('user_id')
        
        # 默认统计最近30天
        from datetime import timedelta
        start_date = datetime.fromisoformat(start_date_str) if start_date_str else datetime.now() - timedelta(days=30)
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else datetime.now()
        
        # 获取操作统计
        action_stats = container.audit_service.get_action_statistics(start_date, end_date)
        
        # 获取用户活动统计
        user_activity = None
        if user_id:
            user_activity = container.audit_service.get_user_activity_summary(user_id)
        
        response_data = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'action_statistics': action_stats
        }
        
        if user_activity:
            response_data['user_activity'] = user_activity
        
        return jsonify(response_data), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@audit_bp.route('/logs/<int:log_id>', methods=['GET'])
@require_role('Admin')
def get_log_details(log_id: int):
    """获取单条审计日志详情"""
    try:
        from ...initializer import create_container
        
        container = create_container()
        
        # 创建过滤器
        from ...domain.entities.audit_log import AuditLogFilter
        filters = AuditLogFilter()
        filters.resource_id = str(log_id)
        
        logs = container.audit_service.query_logs(filters, limit=1)
        
        if not logs:
            return jsonify({
                'error': 'Not Found',
                'message': f'Audit log {log_id} not found'
            }), 404
        
        return jsonify({
            'log': logs[0].to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@audit_bp.route('/logs/cleanup', methods=['POST'])
@require_role('Admin')
def cleanup_old_logs():
    """清理旧的审计日志
    
    Request:
        {
            "retention_days": 90  // 保留天数，默认 90 天
        }
    
    Response:
        {
            "deleted_count": 150,
            "message": "Cleaned up 150 old audit logs"
        }
    """
    try:
        from ...initializer import create_container
        
        container = create_container()
        
        data = request.get_json() or {}
        retention_days = data.get('retention_days', 90)
        
        deleted_count = container.audit_service.cleanup_old_logs(retention_days)
        
        return jsonify({
            'deleted_count': deleted_count,
            'message': f'Cleaned up {deleted_count} old audit logs (older than {retention_days} days)'
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@audit_bp.route('/logs/export', methods=['POST'])
@require_role('Admin')
def export_logs():
    """导出审计日志为 CSV
    
    Request:
        {
            "filters": {...},  // 可选的过滤条件
            "format": "csv"  // csv 或 json
        }
    
    Response: CSV/JSON file download
    """
    try:
        from ...initializer import create_container
        from datetime import datetime
        import csv
        import io
        
        container = create_container()
        
        data = request.get_json() or {}
        filters_data = data.get('filters', {})
        export_format = data.get('format', 'csv')
        
        # 构建过滤器
        from ...domain.entities.audit_log import AuditLogFilter, AuditAction
        filters = AuditLogFilter()
        
        if filters_data:
            if 'start_date' in filters_data:
                filters['start_date'] = datetime.fromisoformat(filters_data['start_date'])
            if 'end_date' in filters_data:
                filters['end_date'] = datetime.fromisoformat(filters_data['end_date'])
            if 'user_id' in filters_data:
                filters['user_id'] = filters_data['user_id']
            if 'action' in filters_data:
                filters['action'] = AuditAction.from_string(filters_data['action'])
            if 'resource_type' in filters_data:
                filters['resource_type'] = filters_data['resource_type']
            if 'status' in filters_data:
                filters['status'] = filters_data['status']
        
        # 查询日志
        logs = container.audit_service.query_logs(filters, limit=10000)
        
        if export_format == 'json':
            # 导出为 JSON
            import json
            output = io.StringIO()
            json.dump([log.to_dict() for log in logs], output, indent=2, ensure_ascii=False)
            
            return jsonify({
                'filename': f'audit_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
                'content_type': 'application/json',
                'data': output.getvalue()
            })
        
        else:
            # 导出为 CSV
            output = io.StringIO()
            writer = csv.writer(output)
            
            # 写入表头
            writer.writerow([
                'ID', 'Action', 'User ID', 'Username', 'Role',
                'IP Address', 'Resource Type', 'Resource ID',
                'Resource Name', 'Status', 'Error Message',
                'Timestamp'
            ])
            
            # 写入数据
            for log in logs:
                writer.writerow([
                    log.id,
                    log.action.value if log.action else '',
                    log.user_id,
                    log.username,
                    log.role,
                    log.ip_address,
                    log.resource_type,
                    log.resource_id,
                    log.resource_name,
                    log.status,
                    log.error_message or '',
                    log.timestamp.isoformat()
                ])
            
            return jsonify({
                'filename': f'audit_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                'content_type': 'text/csv',
                'data': output.getvalue()
            })
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500
