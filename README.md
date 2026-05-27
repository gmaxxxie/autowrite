# AutoWrite CLI

> AI Native 的书籍写作命令行工具。输入书名，输出一本完整的书。

**一句话理解：**
```bash
autowrite init mybook          # 初始化一本书
autowrite write next mybook    # 写下一章（规划→草稿→审计→修订）
autowrite status mybook        # 查看状态
```

---

## 安装

### 环境要求

- Bash 4.0+
- Python 3.8+（仅在使用 `book-agent-core` 时需要）
- 可选：`pyyaml`（仅在使用 token 预算配置时需要）

### 步骤

```bash
# 1. 克隆
git clone https://github.com/<your-username>/autowrite.git
cd autowrite

# 2. 添加到 PATH（二选一）
# 方式 A：直接加到 PATH（当前终端有效）
export PATH="$PWD:$PATH"

# 方式 B：软链接到 ~/.local/bin（永久）
mkdir -p ~/.local/bin
ln -s "$(pwd)/autowrite" ~/.local/bin/autowrite
export PATH="$HOME/.local/bin:$PATH"

# 3. 验证
autowrite --help
```

---

## 使用

### 1. 初始化一本书

```bash
autowrite init mybook --genre non-fiction
```

这会在 `$BOOKS_DIR/mybook`（默认 `~/books/mybook`）下创建书籍工作区：

```
~/books/mybook/
├── 00-index/              # 目录 + 真相文件
├── 01-原始素材/           # 原始材料
├── 02-概念卡/             # 概念沉淀
├── 03-方法论卡/           # 方法论沉淀
├── 04-案例库/             # 案例积累
├── 05-章节草稿/           # 章节输出
└── 06-出版版/             # 终稿
```

### 2. 查看帮助

```bash
autowrite --help           # 主命令帮助
autowrite write --help     # write 子命令帮助
autowrite audit --help     # audit 子命令帮助
```

### 3. 写下一章

```bash
autowrite write next mybook
```

这会执行完整管道：**规划 → 草稿 → 审计 → 修订**

### 4. 查看状态

```bash
autowrite status mybook           # 概览
autowrite status mybook --detail  # 详细
```

### 5. 其他命令

| 命令 | 说明 |
|------|------|
| `autowrite init <书名>` | 初始化书籍工作区 |
| `autowrite write next <书名>` | 写下一章（完整管道） |
| `autowrite write count <书名> <N>` | 连续写 N 章 |
| `autowrite audit <书名> [章节]` | 审计指定章节 |
| `autowrite revise <书名> [章节]` | 修订章节 |
| `autowrite status <书名>` | 查看状态 |
| `autowrite plan <书名>` | 生成章节规划 |
| `autowrite brief <书名> --direction` | 方向协商 |
| `autowrite validate <书名>` | 校验书稿 |
| `autowrite list` | 列出所有书籍 |

---

## 与 AI Agent 配合

### Hermes Agent（推荐）

AutoWrite CLI 默认基于 **Hermes** 运行。Hermes Agent 读取 `AGENTS.md` 中的路由规范，自动调度 Skill 完成写作。

```bash
# Hermes Agent 收到指令后执行
autowrite init "AI产品实践"
autowrite write next "AI产品实践"
```

### Codex / Claude Code

任何 Agent 只要能调用 shell 命令，就能操作 AutoWrite：

```
# Codex
codex "用 autowrite 创建一本关于 Go 语言设计的书，然后写前五章"

# Claude Code
claude "执行: autowrite init golang-design && autowrite write count golang-design 5"
```

---

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `BOOKS_DIR` | `~/books` | 书籍工作区根目录 |
| `AUTOWRITE_ROOT` | CLI 所在目录 | 框架根目录 |

```bash
# 自定义书籍目录
BOOKS_DIR=/data/my-books autowrite init mybook
```

---

## 核心架构

```
autowrite/
├── autowrite                   # 主入口（bash）
├── autowrite-init              # 初始化书籍工作区
├── autowrite-write             # 章节写作管道
├── autowrite-audit             # 审计链
├── autowrite-status            # 状态查看
├── autowrite-brief             # 方向/Brief 协商
├── autowrite-plan              # 章节规划
├── autowrite-validate          # 书稿校验
├── autowrite-state             # 状态机
├── book-agent-core/            # 核心框架（Python）
│   ├── budget.py               # Token 预算
│   ├── composer.py             # 上下文组装
│   ├── planner.py              # 章节规划
│   ├── settler.py              # 状态提取
│   ├── rule_engine.py          # 规则引擎
│   └── fingerprint.py          # 风格指纹
└── AGENTS.md                   # Agent 路由规范
```

---

## 审计链

每章完成后自动经过：

1. `book-auto-revisor` — 8项自动修复
2. `book-chapter-quality-audit` — 质量审计
3. `book-de-ai-audit` — 去AI味
4. `book-cn-localization-audit` — 中文本地化
5. `book-persona-audit` — 8路人物评审
6. `book-chapter-revise` — 修订

---

## License

MIT
