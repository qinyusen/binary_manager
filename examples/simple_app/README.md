# Simple App

一个简单的Python应用程序示例，用于演示Binary Manager的发布和下载功能。

## 功能

这个应用提供了一个简单的计算器功能，可以进行基本的数学运算。

## 文件结构

```
simple_app/
├── README.md           # 本文件
├── main.py            # 主程序
├── calculator.py      # 计算器模块
└── config.json        # 配置文件
```

## 使用方法

### 安装

```bash
# 从本地安装
python3 -m binary_manager_v2.cli.main download \
    --package-name simple_app \
    --version 1.0.0 \
    --output ./installed_apps
```

### 运行

```bash
cd simple_app
python3 main.py
```

### 作为模块使用

```python
from calculator import Calculator

calc = Calculator()
result = calc.add(10, 5)
print(f"10 + 5 = {result}")
```

## 发布

如果这是您自己的应用，可以使用Binary Manager发布：

```bash
python3 -m binary_manager_v2.cli.main publish \
    --source ./simple_app \
    --package-name simple_app \
    --version 1.0.0
```

## 版本历史

- **1.0.0** - 初始版本
  - 基本计算器功能（加、减、乘、除）
  - 命令行界面
  - 配置文件支持
