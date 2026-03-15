# 自动化测试功能文档

## 功能概述

发布系统现在支持**发布前自动运行测试**，确保发布的版本通过质量验证。

### 核心特性

✅ **自动测试验证** - 发布前自动运行测试套件  
✅ **多级测试** - 支持关键测试、完整测试、API 测试、集成测试  
✅ **失败阻止** - 测试失败自动阻止发布  
✅ **详细报告** - 提供清晰的测试结果和错误信息  
✅ **CLI 集成** - 命令行工具支持  
✅ **API 集成** - Web API 支持  

---

## 快速开始

### 安装测试依赖

```bash
pip install pytest pytest-cov pytest-flask
```

### CLI 使用

#### 基本用法

```bash
# 发布时运行关键测试（快速）
release-portal publish \
  --type bsp \
  --version v1.0.0 \
  --binary-dir ./build \
  --test

# 运行完整测试
release-portal publish \
  --type bsp \
  --version v1.0.0 \
  --binary-dir ./build \
  --test \
  --test-level all
```

#### 测试级别

```bash
--test-level critical  # 关键测试（默认，约30秒）
--test-level all       # 所有测试（约2分钟）
--test-level api       # 只运行 API 测试
--test-level integration  # 只运行集成测试
```

### Web API 使用

```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "run_tests": true,
    "test_level": "critical"
  }' \
  http://localhost:5000/api/releases/{release_id}/publish
```

---

## 测试级别详解

### 1. Critical（关键测试）✅ 推荐日常使用

**描述**: 快速验证核心功能

**测试内容**:
- 用户认证测试
- 创建发布测试
- 发布流程测试
- 完整工作流测试

**耗时**: 约 30 秒

**适用场景**:
- 日常开发发布
- 快速迭代

### 2. All（所有测试）🔍 完整验证

**描述**: 运行测试套件中的所有测试

**测试内容**:
- 所有 API 测试
- 所有集成测试
- 所有单元测试

**耗时**: 约 2 分钟

**适用场景**:
- 重要版本发布
- 生产环境部署前

### 3. API（API 测试）

**描述**: 只运行 API 端点测试

**测试内容**:
- 认证 API
- 发布 API
- 下载 API
- 许可证 API

**耗时**: 约 1 分钟

**适用场景**:
- API 变更后
- 接口验证

### 4. Integration（集成测试）

**描述**: 只运行集成测试

**测试内容**:
- 端到端工作流
- 许可证管理
- 完整业务流程

**耗时**: 约 1 分钟

**适用场景**:
- 验证业务流程
- 跨模块测试

---

## 工作流程

### 发布流程（带测试）

```
1. 创建发布草稿
   ↓
2. 添加包文件
   ↓
3. 发布（带测试）
   ↓
4. 自动运行测试
   ├─ 测试通过 → 发布成功 ✅
   └─ 测试失败 → 发布被阻止 ❌
```

### 测试验证流程

```
发布前验证启动
   ↓
检查测试环境
   ├─ pytest 未安装 → 失败 ❌
   ├─ 测试文件不存在 → 失败 ❌
   └─ 环境就绪 → 继续 ✅
   ↓
运行测试（根据级别）
   ↓
收集测试结果
   ├─ 通过率统计
   ├─ 错误收集
   └─ 耗时统计
   ↓
判断是否可以发布
   ├─ 全部通过 → 允许发布 ✅
   └─ 有失败 → 阻止发布 ❌
```

---

## 编程接口

### TestRunner 类

```python
from release_portal.application.test_runner import TestRunner

# 创建测试运行器
runner = TestRunner(project_root="/path/to/project")

# 运行所有测试
result = runner.run_all_tests(verbose=True)

# 运行特定测试
result = runner.run_specific_tests("tests/api/test_auth_api.py")

# 运行关键测试
result = runner.run_critical_tests(verbose=False)

# 检查环境
checks = runner.check_test_environment()
```

### PrePublishValidator 类

```python
from release_portal.application.test_runner import PrePublishValidator

# 创建验证器
validator = PrePublishValidator()

# 发布前验证
result = validator.validate_before_publish(
    release_id="rel_123",
    test_level="critical"
)

# 检查是否可以发布
if validator.can_publish(result):
    print("可以发布")
else:
    print("不能发布")

# 获取验证历史
history = validator.get_validation_history()
```

### TestResult 数据类

```python
@dataclass
class TestResult:
    passed: bool              # 是否通过
    total_tests: int          # 总测试数
    passed_tests: int         # 通过数
    failed_tests: int         # 失败数
    skipped_tests: int        # 跳过数
    duration: float           # 耗时（秒）
    output: str               # 输出文本
    errors: List[str]         # 错误列表
```

---

## 集成到 ReleaseService

### 服务配置

```python
from release_portal.application.release_service import ReleaseService

# 方式1: 创建服务时启用测试
service = ReleaseService(
    release_repository=repo,
    storage_service=storage,
    enable_pre_publish_tests=True,  # 启用测试
    test_level="critical"            # 默认测试级别
)

# 方式2: 发布时指定是否测试
service.publish_release(
    release_id="rel_123",
    user_id="user_123",
    run_tests=True,        # 本次发布运行测试
    test_level="all"       # 使用完整测试
)
```

### 测试失败处理

```python
try:
    release = service.publish_release(
        release_id="rel_123",
        run_tests=True
    )
except ValueError as e:
    # 测试失败会抛出 ValueError
    print(f"发布失败: {e}")
    # 输出: "发布前测试失败，无法发布版本。"
    #       "测试结果: 5/10 通过"
    #       "失败: 5"
    #       "错误: ..."
```

---

## 配置选项

### 环境变量

```bash
# 启用发布前测试（全局）
export RELEASE_PORTAL_ENABLE_TESTS=true

# 默认测试级别
export RELEASE_PORTAL_TEST_LEVEL=critical
```

### pytest.ini 配置

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# 标记
markers =
    unit: Unit tests
    integration: Integration tests
    api: API tests
    e2e: End-to-end tests
```

---

## 最佳实践

### 1. 日常开发

使用关键测试，快速验证：

```bash
release-portal publish --test --test-level critical ...
```

### 2. 重要版本

使用完整测试，确保质量：

```bash
release-portal publish --test --test-level all ...
```

### 3. CI/CD 集成

在 CI/CD 流水线中使用完整测试：

```yaml
# .github/workflows/publish.yml
- name: Run tests
  run: |
    pytest --cov=release_portal

- name: Publish
  if: success()
  run: |
    release-portal publish --test --test-level all ...
```

### 4. 快速迭代

跳过测试（仅限开发环境）：

```bash
release-portal publish ...  # 不加 --test 参数
```

---

## 故障排查

### 问题 1: pytest 未安装

**错误**: `pytest 未安装，无法运行测试`

**解决**:
```bash
pip install pytest pytest-cov pytest-flask
```

### 问题 2: 测试文件不存在

**错误**: `没有找到测试文件`

**解决**: 确保项目中有 `tests/` 目录和测试文件

### 问题 3: 测试超时

**错误**: `测试运行超时（5分钟）`

**解决**:
- 检查测试是否有死循环
- 优化慢速测试
- 增加超时时间（修改 `test_runner.py` 中的 `timeout` 参数）

### 问题 4: 测试失败

**错误**: `发布前测试失败，无法发布版本`

**解决**:
1. 查看测试输出，找出失败原因
2. 修复代码或测试
3. 重新运行测试验证

---

## 进阶功能

### 自定义测试钩子

```python
from release_portal.application.test_runner import TestHook

class CustomTestHook(TestHook):
    def execute(self, release):
        # 自定义验证逻辑
        # 例如: 检查包大小、版本格式等
        pass

# 添加到验证器
validator._test_runner.hooks.append(CustomTestHook())
```

### 测试报告

```python
# 生成 HTML 测试报告
pytest --cov=release_portal --cov-report=html

# 查看
open htmlcov/index.html
```

### 并行测试

```bash
# 使用 pytest-xdist 并行运行
pytest -n auto  # 自动检测 CPU 核心数
```

---

## 示例

### 完整发布流程（CLI）

```bash
# 1. 登录
release-portal login admin

# 2. 创建并发布（带测试）
release-portal publish \
  --type bsp \
  --version v1.0.0 \
  --binary-dir ./build/bsp \
  --source-dir ./src/bsp \
  --doc-dir ./doc/bsp \
  --description "RDK X3 BSP v1.0.0" \
  --test \
  --test-level critical

# 输出:
# ============================================================
# 🧪 发布前验证 - Release ID: rel_xxx
# 📋 测试级别: critical
# ============================================================
# 
# ✅ 测试环境检查通过
#    - pytest: 已安装
#    - 测试文件: 54 个
# 
# 🔍 运行关键测试...
# 
# ============================================================
# ✅ 测试通过！
# 📊 测试统计:
#    - 总计: 10 个
#    - 通过: 10 个
#    - 失败: 0 个
#    - 跳过: 0 个
#    - 耗时: 28.45 秒
# ============================================================
# 
# ✅ 测试验证通过，继续发布...
# ✓ 发布成功!
```

### Web API 完整示例

```python
import requests

# 1. 登录获取 token
response = requests.post('http://localhost:5000/api/auth/login', json={
    'username': 'admin',
    'password': 'admin123'
})
token = response.json()['token']

# 2. 发布（带测试）
headers = {'Authorization': f'Bearer {token}'}
data = {
    'run_tests': True,
    'test_level': 'critical'
}

response = requests.post(
    'http://localhost:5000/api/releases/rel_123/publish',
    headers=headers,
    json=data
)

if response.status_code == 200:
    print("✅ 发布成功!")
    print(response.json())
elif response.status_code == 400:
    print("❌ 发布失败")
    print(response.json()['message'])
```

---

## 性能考虑

### 测试耗时

| 级别 | 测试数 | 耗时 | 适用 |
|-----|--------|------|------|
| critical | ~10 | 30秒 | 日常开发 |
| api | ~31 | 60秒 | API 验证 |
| integration | ~15 | 60秒 | 流程验证 |
| all | ~54 | 120秒 | 重要版本 |

### 优化建议

1. **使用 critical 级别** - 平衡速度和覆盖率
2. **并行测试** - 使用 `pytest -n auto`
3. **测试隔离** - 每个测试独立，提高并行效率
4. **缓存依赖** - 安装依赖后缓存

---

## 相关文档

- [测试指南](tests/README.md) - 完整测试指南
- [集成测试总结](INTEGRATION_TESTS_SUMMARY.md) - 测试开发总结
- [用户手册](USER_MANUAL.md) - 系统使用手册
- [API 文档](doc/design.md#6-api-设计) - API 设计文档

---

## 总结

自动化测试功能已完全集成到发布系统，提供：

✅ **质量保障** - 发布前自动验证  
✅ **灵活配置** - 多个测试级别  
✅ **易于使用** - CLI 和 API 支持  
✅ **详细报告** - 清晰的测试结果  
✅ **失败保护** - 自动阻止问题发布  

**立即开始使用**: `python3 demo_auto_tests.py`

---

**文档版本**: 1.0  
**创建日期**: 2026-03-05  
**功能状态**: ✅ 生产就绪
