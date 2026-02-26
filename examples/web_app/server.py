#!/usr/bin/env python3
"""
Simple HTTP Server
一个简单的Web服务器，演示Binary Manager的使用
"""
import http.server
import socketserver
import json
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import sys


class WebAPIHandler(http.server.SimpleHTTPRequestHandler):
    """自定义HTTP请求处理器"""
    
    def do_GET(self):
        """处理GET请求"""
        parsed_path = urlparse(self.path)
        
        # API路由
        if parsed_path.path.startswith('/api/'):
            self.handle_api(parsed_path.path)
        else:
            # 静态文件服务
            super().do_GET()
    
    def handle_api(self, path):
        """处理API请求"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        if path == '/api/health':
            response = {
                "status": "healthy",
                "version": "1.0.0"
            }
        elif path == '/api/info':
            response = {
                "name": "Web App",
                "version": "1.0.0",
                "description": "简单的Web服务器示例",
                "endpoints": [
                    "/api/health",
                    "/api/info"
                ]
            }
        else:
            response = {
                "error": "Not found",
                "path": path
            }
            self.send_response(404)
        
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{self.log_date_time_string()}] {format % args}")


def start_server(port=8080):
    """启动Web服务器"""
    handler = WebAPIHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"\n{'='*50}")
        print(f"Web App Server 启动成功!")
        print(f"{'='*50}")
        print(f"访问地址: http://localhost:{port}")
        print(f"API端点:")
        print(f"  - http://localhost:{port}/api/health")
        print(f"  - http://localhost:{port}/api/info")
        print(f"\n按 Ctrl+C 停止服务器")
        print(f"{'='*50}\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n服务器已停止")
            sys.exit(0)


if __name__ == "__main__":
    port = 8080
    
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("错误: 端口必须是数字")
            sys.exit(1)
    
    start_server(port)
