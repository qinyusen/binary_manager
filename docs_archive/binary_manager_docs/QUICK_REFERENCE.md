# Release App 快速参考

快速查询常用操作和快捷键。

## 🚀 快速开始

```bash
# TUI模式（推荐）
python3 -m tools.release_app

# CLI模式
python3 -m tools.release_app --cli
```

## ⌨️ 快捷键

| TUI模式 | 功能 |
|---------|------|
| `↑`/`↓` | 上下选择 |
| `Enter` | 确认 |
| `Esc` | 返回/退出 |
| `1-9` | 快速选择 |
| `Y`/`N` | 确认/取消 |

## 📋 发布类型

- **仅二进制**: 编译+打包
- **仅提交**: 记录Git
- **完整发布**: 二进制+提交 ⭐

## 📝 典型流程

**首次发布**:
1. 选择 "完整发布"
2. 版本号: `1.0.0`
3. 发布说明: `首次发布`
4. 确认

**详细文档**: [INTERFACE_GUIDE.md](../../test/INTERFACE_GUIDE.md)
