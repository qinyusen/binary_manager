# Release Portal V3 - 集成测试套件

## 📋 测试概述

这是 Release Portal V3 的完整集成测试套件，使用 **pytest** 框架编写。

### 测试覆盖范围

✅ **API 端点测试**
  - 认证 API（登录、注册、token 验证）
  - 发布 API（创建、发布、归档、文件上传）
  - 下载 API（列表、包信息、许可证）
  - 许可证 API（创建、延期、激活、撤销）

✅ **Web UI 测试**
  - 页面可访问性
  - 认证重定向
  - 用户交互

✅ **端到端测试**
  - 完整发布工作流
  - 许可证管理工作流
  - 错误处理

✅ **集成测试**
  - 服务层集成
  - 数据库操作
  - 文件系统操作

## 🚀 快速开始

### 安装依赖

```bash
# 安装 pytest 和相关插件
pip3 install pytest pytest-cov pytest-flask pytest-xdist

# 或者安装所有测试依赖
pip3 install -r requirements-test.txt
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/api/test_auth_api.py

# 运行特定测试类
pytest tests/api/test_auth_api.py::TestAuthAPI

# 运行特定测试函数
pytest tests/api/test_auth_api.py::TestAuthAPI::test_login_success

# 运行带详细输出的测试
pytest -v

# 运行带覆盖率的测试
pytest --cov=release_portal --cov-report=html

# 并行运行测试（更快）
pytest -n auto
```

## 📁 测试目录结构

```
tests/
├── conftest.py                 # pytest 配置和 fixtures
├── fixtures/
│   └── test_utils.py          # 测试工具函数和辅助类
├── api/                        # API 测试
│   ├── test_auth_api.py       # 认证 API 测试
│   ├── test_releases_api.py   # 发布 API 测试
│   └── test_downloads_licenses_api.py  # 下载和许可证 API 测试
├── ui/                         # UI 测试（待添加）
└── integration/                # 集成测试
    └── test_end_to_end.py     # 端到端测试

pytest.ini                      # pytest 配置文件
```

## 🧪 测试 Fixtures

### 核心 fixtures

```python
# 测试数据库
@pytest.fixture
def test_db_path(tmp_path_factory):
    """创建测试数据库路径"""

# 数据库初始化器
@pytest.fixture
def db_initializer(test_db_path):
    """初始化测试数据库"""

# 服务容器
@pytest.fixture
def container(db_initializer, test_db_path):
    """创建服务容器"""

# Flask 应用
@pytest.fixture
def app(container):
    """创建 Flask 应用"""

# 测试客户端
@pytest.fixture
def client(app):
    """创建 Flask 测试客户端"""

# 测试用户
@pytest.fixture
def test_users(container):
    """创建测试用户（admin, publisher, customer）"""

# 认证 tokens
@pytest.fixture
def auth_tokens(container, test_users):
    """获取测试用户的认证 token"""

# 认证请求头
@pytest.fixture
def auth_headers(auth_tokens):
    """获取带认证的请求头"""

# API 客户端
@pytest.fixture
def api_client(client):
    """API 客户端包装类"""

# 已认证的 API 客户端
@pytest.fixture
def authenticated_api_client(client, auth_tokens):
    """已认证的 API 客户端"""
```

## 📝 测试示例

### API 测试示例

```python
def test_login_success(client, test_users):
    """测试成功登录"""
    response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'token' in data
    assert 'user' in data
```

### 端到端测试示例

```python
def test_complete_release_workflow(client, auth_tokens):
    """测试完整的发布工作流"""
    
    # 1. 创建发布草稿
    response = client.post('/api/releases',
        headers={'Authorization': f'Bearer {auth_tokens["publisher"]}'},
        json={
            'resource_type': 'BSP',
            'version': '1.0.0',
            'description': '测试发布'
        }
    )
    assert response.status_code == 201
    release_id = response.get_json()['release_id']
    
    # 2. 发布版本
    response = client.post(f'/api/releases/{release_id}/publish',
        headers={'Authorization': f'Bearer {auth_tokens["publisher"]}'}
    )
    assert response.status_code == 200
```

## 🔧 测试工具函数

### 创建测试包

```python
from tests.fixtures.test_utils import create_test_bsp_package

# 创建 BSP 包
package_path, temp_dir = create_test_bsp_package(
    version='1.0.0',
    board_name='rdk_x3'
)

# 使用包文件进行测试
with open(package_path, 'rb') as f:
    response = client.post('/api/releases/<id>/packages',
        data={'package_file': f}
    )

# 清理
cleanup_temp_directory(temp_dir)
```

### API 客户端包装类

```python
from tests.fixtures.test_utils import APIClient

# 创建 API 客户端
api = APIClient(client, token=auth_token)

# 简化的 API 调用
response = api.get('/api/releases')
response = api.post('/api/releases', json={...})
response = api.put('/api/releases/<id>', json={...})
response = api.delete('/api/releases/<id>')
```

## 📊 测试标记

使用标记来组织测试：

```bash
# 运行特定标记的测试
pytest -m api
pytest -m integration
pytest -m e2e
pytest -m "not slow"

# 组合标记
pytest -m "api and not slow"
pytest -m "e2e or integration"
```

### 可用标记

- `unit`: 单元测试
- `integration`: 集成测试
- `e2e`: 端到端测试
- `api`: API 测试
- `ui`: UI 测试
- `slow`: 慢速测试
- `auth`: 认证相关测试
- `release`: 发布相关测试
- `download`: 下载相关测试
- `license`: 许可证相关测试

## 📈 覆盖率报告

### 生成覆盖率报告

```bash
# 生成终端报告
pytest --cov=release_portal --cov-report=term

# 生成 HTML 报告
pytest --cov=release_portal --cov-report=html

# 查看报告
open htmlcov/index.html
```

### 覆盖率目标

- **总体覆盖率**: > 80%
- **核心业务逻辑**: > 90%
- **API 端点**: 100%

## 🐛 调试测试

### 查看详细输出

```bash
# 显示打印输出
pytest -s

# 显示更详细的错误信息
pytest --tb=long

# 在第一个失败时停止
pytest -x

# 进入调试器
pytest --pdb
```

### 运行特定测试

```bash
# 运行失败的测试
pytest --lf

# 先运行失败的测试
pytest --ff

# 运行上次失败的测试
pytest --failed-first
```

## 🚨 已知问题

### 1. 导入错误

某些模块可能无法导入，这是正常的，因为测试环境与生产环境不同。

**解决方案**：在 `conftest.py` 中已经添加了路径设置。

### 2. 临时文件清理

某些测试可能会留下临时文件。

**解决方案**：使用 `cleanup_temp_directory()` 函数清理。

### 3. 数据库锁定

并行测试可能导致数据库锁定。

**解决方案**：每个测试使用独立的数据库文件。

## 📚 最佳实践

### 1. 使用 fixtures

```python
# ✅ 好的做法
def test_something(client, auth_tokens):
    token = auth_tokens['admin']
    ...

# ❌ 不好的做法
def test_something(client):
    # 手动创建用户
    user = create_user(...)
    # 手动登录
    token = login(...)
```

### 2. 保持测试独立

```python
# ✅ 好的做法
def test_create_release(client, auth_tokens):
    # 创建新的发布
    ...

def test_publish_release(client, auth_tokens):
    # 创建另一个发布
    ...

# ❌ 不好的做法
def test_create_and_publish(client, auth_tokens):
    # 这个测试做了两件事
    ...
```

### 3. 使用有意义的断言

```python
# ✅ 好的做法
assert response.status_code == 200, f"Expected 200, got {response.status_code}"
assert 'release_id' in data, "Response should contain release_id"

# ❌ 不好的做法
assert response.status_code == 200
```

### 4. 清理资源

```python
def test_with_temp_files():
    temp_dir = tempfile.mkdtemp()
    try:
        # 测试代码
        ...
    finally:
        # 清理
        shutil.rmtree(temp_dir, ignore_errors=True)
```

## 🔄 持续集成

### GitHub Actions 示例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest --cov=release_portal
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 📖 参考资源

- [pytest 文档](https://docs.pytest.org/)
- [pytest-cov 文档](https://pytest-cov.readthedocs.io/)
- [Flask 测试文档](https://flask.palletsprojects.com/en/latest/testing/)

## 🤝 贡献指南

### 添加新测试

1. 在适当的目录创建测试文件
2. 使用清晰的测试名称
3. 添加 docstring 说明测试目的
4. 使用适当的标记
5. 确保测试独立且可重复

### 测试命名规范

```python
# 测试类: Test<功能名>
class TestAuthAPI:
    ...

# 测试函数: test_<具体场景>
def test_login_success():
    ...

def test_login_with_wrong_password():
    ...

def test_login_with_nonexistent_user():
    ...
```

## ✅ 检查清单

在提交代码前，确保：

- [ ] 所有测试通过
- [ ] 覆盖率 > 80%
- [ ] 没有跳过的测试
- [ ] 测试文档完整
- [ ] 使用了适当的标记

## 📞 支持

如有问题，请查看：
- 项目文档
- 代码注释
- GitHub Issues

---

**Happy Testing! 🧪**
