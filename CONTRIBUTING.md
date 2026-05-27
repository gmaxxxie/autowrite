# 贡献指南

感谢你考虑为 AutoWrite CLI 贡献代码！

## 如何贡献

### 报告 Bug

- 在 GitHub Issues 中创建 Bug Report
- 描述清楚：环境、操作步骤、预期结果、实际结果
- 附上相关日志和截图（如果有）

### 提出新功能

- 在 GitHub Issues 中创建 Feature Request
- 说明使用场景和价值
- 讨论后觉得合理再动手实现

### 提交代码

1. **Fork** 本仓库
2. **创建特性分支**：`git checkout -b feat/your-feature`
3. **编写代码**，确保通过测试
4. **提交**：`git commit -m "feat: add your feature"`
5. **推送**：`git push origin feat/your-feature`
6. **创建 Pull Request**

## 代码规范

### Bash 脚本

- 使用 `set -e` 开启错误退出
- 使用 `${VAR:-default}` 处理默认值
- 颜色输出使用统一变量：

```bash
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'
```

### Python（book-agent-core）

- 遵循 PEP 8
- 使用类型注解（type hints）
- 每个模块有 docstring

```python
"""模块说明

Args:
    param1: 参数说明
Returns:
    返回值说明
"""

def function(param1: str, param2: int) -> bool:
    """函数说明"""
    return True
```

### Commit Message 格式

```
<type>: <简短描述>

<可选的详细说明>

<可选的关联 Issue>
```

**Type 类型：**
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档改动
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

## 测试

```bash
# 运行 Python 测试（待补充）
pytest

# Bash 脚本 lint
shellcheck autowrite*
```

## 开发环境

```bash
# 克隆你的 Fork
git clone https://github.com/<your-username>/autowrite.git
cd autowrite

# 添加上游仓库
git remote add upstream https://github.com/<original-owner>/autowrite.git

# 创建特性分支
git checkout -b feat/your-feature
```

## 问题讨论

有疑问欢迎在 GitHub Issues 中讨论，或者提交 PR 前先开 Issue 讨论方向是否合适。
