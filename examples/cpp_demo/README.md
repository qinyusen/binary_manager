# C++ Demo Project

这是一个简单的C++示例项目，用于测试 Release App 工具。

## 构建方法

### 使用 CMake

```bash
mkdir build
cd build
cmake ..
make
```

### 运行

```bash
./build/cpp_demo
```

## 使用 Release App 发布

在项目根目录运行：

```bash
cd /Users/yusen/test/examples/cpp_demo
python3 -m tools.release_app
```

然后按照提示选择发布类型、输入版本号等信息。

## 项目结构

```
cpp_demo/
├── CMakeLists.txt    # CMake构建配置
├── main.cpp          # 主程序源码
├── README.md         # 项目说明
└── versions/         # 发布版本文件（自动创建）
```
