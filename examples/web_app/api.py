#!/usr/bin/env python3
"""
API Module
提供API相关的功能
"""


class APIResponse:
    """API响应类"""
    
    @staticmethod
    def success(data=None, message="Success"):
        """成功响应"""
        response = {
            "status": "success",
            "message": message
        }
        if data is not None:
            response["data"] = data
        return response
    
    @staticmethod
    def error(message="Error", code=400):
        """错误响应"""
        return {
            "status": "error",
            "message": message,
            "code": code
        }


def get_server_info():
    """获取服务器信息"""
    return {
        "name": "Web App",
        "version": "1.0.0",
        "description": "简单的Web服务器示例",
        "author": "Binary Manager Team",
        "endpoints": [
            {
                "path": "/api/health",
                "method": "GET",
                "description": "健康检查"
            },
            {
                "path": "/api/info",
                "method": "GET",
                "description": "服务器信息"
            }
        ]
    }


def get_health_status():
    """获取健康状态"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "uptime": "running"
    }


if __name__ == "__main__":
    # 测试API功能
    print("Server Info:")
    print(get_server_info())
    print("\nHealth Status:")
    print(get_health_status())
