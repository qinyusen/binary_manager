"""
Web UI 蓝图
"""
from flask import Blueprint, render_template, redirect, url_for, session

ui_bp = Blueprint('ui', __name__)


@ui_bp.route('/')
def index():
    """首页"""
    # 如果已登录，重定向到仪表板
    if 'token' in session:
        return redirect(url_for('ui.dashboard'))
    
    return render_template('index.html')


@ui_bp.route('/login')
def login_page():
    """登录页面"""
    return render_template('login.html')


@ui_bp.route('/dashboard')
def dashboard():
    """仪表板"""
    # 检查登录状态
    if 'token' not in session:
        return redirect(url_for('ui.login_page'))
    
    return render_template('dashboard.html')


@ui_bp.route('/releases')
def releases():
    """发布管理页面"""
    if 'token' not in session:
        return redirect(url_for('ui.login_page'))
    
    return render_template('releases.html')


@ui_bp.route('/downloads')
def downloads():
    """下载页面"""
    if 'token' not in session:
        return redirect(url_for('ui.login_page'))
    
    return render_template('downloads.html')


@ui_bp.route('/licenses')
def licenses():
    """许可证管理页面"""
    if 'token' not in session:
        return redirect(url_for('ui.login_page'))
    
    return render_template('licenses.html')


@ui_bp.route('/logout')
def logout():
    """登出"""
    session.pop('token', None)
    session.pop('user', None)
    return redirect(url_for('ui.index'))
