#!/usr/bin/env python3
"""
Web服务器示例
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver

class MyHTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return SimpleHTTPRequestHandler.do_GET(self)
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)

def run_server(port=8000):
    with socketserver.TCPServer(("", port), MyHTTPRequestHandler) as httpd:
        print(f"Server running at http://localhost:{port}")
        print("Press Ctrl+C to stop")
        httpd.serve_forever()

if __name__ == '__main__':
    run_server()
