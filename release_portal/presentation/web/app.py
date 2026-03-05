"""
Release Portal Web Application

Flask REST API 和 Web UI
"""
from flask import Flask, jsonify
from flask_cors import CORS
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from shared import Config


def create_app(db_path: str = None):
    """创建 Flask 应用
    
    Args:
        db_path: 数据库路径
        
    Returns:
        Flask 应用实例
    """
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')
    
    # 配置
    app.config['SECRET_KEY'] = Config.get_secret_key()
    app.config['JSON_AS_ASCII'] = False
    app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB
    app.config['DB_PATH'] = db_path  # 存储数据库路径
    
    # 启用 CORS
    CORS(app)
    
    # 注册蓝图
    from .api import auth_bp, releases_bp, downloads_bp, licenses_bp, backup_bp, cold_backup_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(releases_bp, url_prefix='/api/releases')
    app.register_blueprint(downloads_bp, url_prefix='/api/downloads')
    app.register_blueprint(licenses_bp, url_prefix='/api/licenses')
    app.register_blueprint(backup_bp, url_prefix='/api/backup')
    app.register_blueprint(cold_backup_bp, url_prefix='/api/cold-backup')
    
    # 注册 Web UI 路由
    from .ui import ui_bp
    app.register_blueprint(ui_bp)
    
    # 错误处理
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad Request', 'message': str(error)}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized', 'message': str(error)}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden', 'message': str(error)}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not Found', 'message': str(error)}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal Server Error', 'message': str(error)}), 500
    
    # 健康检查
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'version': '3.0.0',
            'service': 'Release Portal V3'
        })
    
    return app


# 创建应用实例
app = create_app()
