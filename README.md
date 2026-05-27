# AutoWrite CLI

> AI Native 的书籍写作命令行工具。输入书名，输出一本完整的书。

## 定位

AutoWrite CLI 是一个**Agent-Friendly**的写书工具：

- 默认基于 **Hermes Agent** 运行
- 同时兼容 **Codex**、**Claude Code**、以及任何可以通过 CLI 调用的 AI Agent
- 核心逻辑在 `book-agent-core/`，CLI 只是壳

## 一句话理解

```
autowrite init mybook          # 初始化一本书
autowrite write next mybook    # 写下一章（规划→草稿→审计→修订）
autowrite status mybook        # 查看状态
```

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

## 工作原理

```
用户/Agent 调用 autowrite 命令
        ↓
    bash CLI 解析命令
        ↓
    调用 book-agent-core（Python）
        ↓
    路由到具体 Skill（Hermes）
        ↓
    执行 → 审计链 → 状态更新
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `BOOKS_DIR` | `~/books` | 书籍工作区根目录 |
| `AUTOWRITE_ROOT` | CLI 所在目录 | 框架根目录 |

## 安装

```bash
# 克隆
git clone https://github.com/<your-username>/autowrite.git
cd autowrite

# 添加到 PATH（可选）
export PATH="$PWD:$PATH"

# 或软链接
ln -s "$(pwd)/autowrite" /usr/local/bin/autowrite
```

## 快速开始

```bash
# 1. 初始化一本书
autowrite init mybook --genre non-fiction

# 2. 查看帮助
autowrite --help

# 3. 写下一章
autowrite write next mybook

# 4. 查看状态
autowrite status mybook
```

## 与 Hermes Agent 配合

AutoWrite CLI 设计上由 Hermes Agent 驱动：

```bash
# Hermes Agent 调用方式
hermes "用 autowrite 初始化一本关于产品经理AI应用的书"

# Agent 内部执行
autowrite init "AI产品实践" --genre non-fiction
autowrite write next "AI产品实践"
```

## 与其他 Agent 配合

Codex、Claude Code 等 Agent 可以直接调用 CLI：

```
# Codex
codex "用 autowrite 创建一本关于 Go 语言设计的书，然后写前五章"

# Claude Code
claude "执行: autowrite init golang-design && autowrite write next golang-design"
```

## 书籍工作区结构

```
~/books/<书名>/
├── 00-index/           # 目录 + 真相文件
├── 01-原始素材/        # 素材输入
├── 02-概念卡/          # 概念沉淀
├── 03-方法论卡/        # 方法论沉淀
├── 04-案例库/          # 案例积累
├── 05-章节草稿/        # 章节输出
└── 06-出版版/          # 终稿
```

## 审计链

每章完成后自动经过：

1. `book-auto-revisor` — 8项自动修复
2. `book-chapter-quality-audit` — 质量审计
3. `book-de-ai-audit` — 去AI味
4. `book-cn-localization-audit` — 中文本地化
5. `book-persona-audit` — 8路人物评审
6. `book-chapter-revise` — 修订

##  License

MIT
