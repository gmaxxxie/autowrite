# AutoWrite CLI

<p align="center">
  <img src="https://img.shields.io/badge/GitHub%20Stars-Open-blue?style=flat-square" alt="Stars">
  <img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Python-3.8+-yellow.svg?style=flat-square" alt="Python">
</p>



> **AI Native 的书籍写作命令行工具。输入书名，输出一本完整的书。**

AutoWrite CLI 是一个 **Agent-Friendly** 的写书框架——默认基于 **Hermes Agent** 驱动，同时兼容 Codex、Claude Code 等任何能调用命令行的 AI Agent。

---

## 适用书籍类型

AutoWrite CLI 专为**非虚构类书籍**设计，尤其擅长：

| 类型 | 示例 |
|------|------|
| 商业经管 | 产品方法论、商业策略、管理实践 |
| 科技技术 | AI 应用、编程指南、技术思维 |
| 自我提升 | 职场成长、学习方法、职业规划 |
| 投资理财 | 投资理念、财务规划、经济思维 |

**为什么适合这类书籍？**

- **有结构**——商业/科技书有清晰的章节能效仿，AI 能把握
- **有案例**——概念卡 → 案例库 → 正文，层层递进，AI 不会空对空
- **有审计**——六层审计链确保论点有依据、数据不捏造、表达不机器
- **有风格**——风格指纹确保全书语气一致，不前后割裂

> 虚构类、文学类书籍不是 AutoWrite 的目标场景——这类书更依赖个人叙事和创意，AutoWrite 的结构化审计链反而可能限制发挥。

---

## 一句话快速上手

```bash
# 安装
git clone https://github.com/gmaxxxie/autowrite.git && cd autowrite
export PATH="$PWD:$PATH"

# 使用
autowrite init mybook --genre non-fiction     # 初始化一本书
autowrite write next mybook                    # 写下一章
autowrite status mybook                        # 查看状态
```

---

## 目录

- [亮点](#亮点)
- [适用书籍类型](#适用书籍类型)
- [安装](#安装)
- [快速开始](#快速开始)
- [详细用法](#详细用法)
- [与 AI Agent 配合](#与-ai-agent-配合)
- [核心架构](#核心架构)
- [审计链](#审计链)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)
- [License](#license)

---

## 亮点

- **Agent-Native 设计**：CLI 作为 Agent 的操作界面，Hermes / Codex / Claude Code 均可驱动
- **端到端写书流程**：初始化 → 规划 → 写作 → 审计 → 修订，全流程覆盖
- **Token 预算控制**：内置 `budget.py` 引擎，确保长书不爆 Token
- **上下文组装**：`composer.py` 自动聚合概念卡、案例库、真相文件
- **风格指纹**：`fingerprint.py` 保持全书风格一致
- **模块化 CLI**：每个命令独立，可单独调用也可组合使用
- **纯 Bash + Python**：无重型依赖，`book-agent-core` 仅用标准库

<p align="center">
  <img src="https://cdn.hiapi.ai/relays/ali_image/2026-05/a8e1a717b533bad3.png" width="100%" alt="AutoWrite CLI Workflow">
</p>

---

## 安装

### 环境要求

| 依赖 | 版本 | 说明 |
|------|------|------|
| Bash | ≥ 4.0 | 主 CLI 入口 |
| Python | ≥ 3.8 | 仅在使用 `book-agent-core` 时需要 |
| `pyyaml` | — | 可选，仅在使用 token 预算配置文件时需要 |

### 方式一：Git 克隆（推荐）

```bash
git clone https://github.com/gmaxxxie/autowrite.git
cd autowrite

# 添加到 PATH（二选一）
export PATH="$PWD:$PATH"                    # 当前终端有效
echo 'export PATH="$PWD:$PATH"' >> ~/.bashrc  # 永久生效
```

### 方式二：软链接到 `~/.local/bin`

```bash
git clone https://github.com/gmaxxxie/autowrite.git
cd autowrite
mkdir -p ~/.local/bin
ln -s "$(pwd)/autowrite" ~/.local/bin/autowrite
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

### 方式三：直接运行脚本

```bash
# 无需安装，直接运行主入口
./autowrite --help
./autowrite init mybook
```

### 验证安装

```bash
autowrite --help
```

---

## 快速开始

### Step 1：初始化一本书

```bash
autowrite init mybook --genre non-fiction
```

**输出示例：**

```
[autowrite] 初始化书籍工作区：mybook
[✓] 创建目录结构
[✓] 生成真相文件（truth/）
[✓] 初始化 git
[✓] 完成

书籍工作区：~/books/mybook/
├── 00-index/
├── 01-原始素材/
├── 02-概念卡/
├── 03-方法论卡/
├── 04-案例库/
├── 05-章节草稿/
└── 06-出版版/
```

### Step 2：写下一章

```bash
autowrite write next mybook
```

**输出示例：**

```
[autowrite] 开始写章节：mybook / 第 1 章
[autowrite] 组装上下文包...
[autowrite] Token 预算：32000 / 当前使用：12450
[autowrite] 生成章节规划...
[✓] 规划完成（7 节）
[autowrite] 执行写作管道...
[✓] 初稿完成（3,240 字）
[autowrite] 执行审计链...
[✓] auto-revisor 通过（8 项）
[✓] quality-audit 通过
[✓] de-ai-audit 通过
[✓] 本地化审计通过
[✓] 修订完成
[✓] 第 1 章完成
```

### Step 3：查看状态

```bash
autowrite status mybook
```

**输出示例：**

```
mybook — 非虚构类
状态：进行中

进度：1/12 章

第 1 章  ████████████████████ 完成
第 2 章  ░░░░░░░░░░░░░░░░░░░  待写
第 3 章  ░░░░░░░░░░░░░░░░░░░  待写
...
```

---

## 详细用法

### 主命令

```bash
autowrite --help              # 主命令帮助
autowrite init --help         # init 子命令帮助
autowrite write --help        # write 子命令帮助
autowrite audit --help        # audit 子命令帮助
```

### 命令一览

| 命令 | 说明 |
|------|------|
| `autowrite init <书名>` | 初始化书籍工作区 |
| `autowrite write next <书名>` | 写下一章（完整管道） |
| `autowrite write count <书名> <N>` | 连续写 N 章 |
| `autowrite audit <书名> [章节]` | 审计指定章节 |
| `autowrite revise <书名> [章节]` | 修订章节 |
| `autowrite status <书名>` | 查看状态 |
| `autowrite status <书名> --detail` | 详细状态 |
| `autowrite plan <书名>` | 生成章节规划 |
| `autowrite brief <书名> --direction` | 方向协商 |
| `autowrite validate <书名>` | 校验书稿 |
| `autowrite list` | 列出所有书籍 |

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `BOOKS_DIR` | `~/books` | 书籍工作区根目录 |
| `AUTOWRITE_ROOT` | CLI 所在目录 | 框架根目录 |

```bash
# 自定义书籍目录
BOOKS_DIR=/data/my-books autowrite init mybook
```

### 书籍工作区结构

```
~/books/<书名>/
├── 00-index/              # 目录 + 真相文件
│   ├── book-structure.md
│   ├── book-review.md
│   └── style-composition.md
├── 01-原始素材/           # 原始材料（PDF/Word/文本）
├── 02-概念卡/             # 概念沉淀
├── 03-方法论卡/           # 方法论沉淀
├── 04-案例库/             # 案例积累
├── 05-章节草稿/           # 章节输出
│   ├── CN/               # 中文初稿
│   └── tickets/          # 审计票据
└── 06-出版版/             # 终稿
```

---

## 与 AI Agent 配合

### Hermes Agent（默认）

AutoWrite CLI 默认由 **Hermes** 驱动。Hermes 读取 `AGENTS.md` 中的路由规范，自动调度 Skill 完成写作。

```bash
# Hermes Agent 接收自然语言指令
hermes "帮我创建一本关于 AI 产品经理的书，写前 3 章"

# Agent 内部执行
autowrite init "AI产品经理"
autowrite write count "AI产品经理" 3
```

### Codex

```
# 直接用自然语言驱动 Codex
codex "用 autowrite 创建一本关于 Go 语言设计的书，然后写前五章"
# Codex 内部调用
autowrite init "Go语言设计"
autowrite write count "Go语言设计" 5
```

### Claude Code

```bash
# Claude Code 执行
claude "执行: autowrite init golang-design && autowrite write count golang-design 5"
```

### 任何 Agent

任何能执行 shell 命令的 AI Agent 都可以驱动 AutoWrite——只需要调用 `autowrite <命令>`。

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
├── autowrite-model-gate        # 模型路由门禁
├── book-agent-core/            # 核心框架（Python）
│   ├── budget.py              # Token 预算引擎
│   ├── composer.py            # 上下文组装（概念卡/案例库/真相文件）
│   ├── planner.py             # 章节规划
│   ├── settler.py             # 状态自动提取
│   ├── rule_engine.py         # 确定性规则引擎
│   └── fingerprint.py         # 风格指纹
└── AGENTS.md                  # Agent 路由规范
```

### 执行流程

```
用户/Agent 调用 autowrite 命令
        ↓
    bash CLI 解析命令
        ↓
    调用 book-agent-core（Python）
        ↓
    组装上下文包（预算 + 上下文）
        ↓
    路由到具体 Skill（Hermes）
        ↓
    执行 → 审计链 → 状态更新 → git commit
```

---

## 审计链

每章完成后自动经过六层审计，确保书稿质量：

| 步骤 | Skill | 说明 |
|------|-------|------|
| 1 | `book-auto-revisor` | 8项自动修复（逻辑/事实/格式） |
| 2 | `book-chapter-quality-audit` | 质量审计（论点/论据/结构） |
| 3 | `book-de-ai-audit` | 去AI味（消除机器腔） |
| 4 | `book-cn-localization-audit` | 中文本地化（表达地道） |
| 5 | `book-persona-audit` | 8路人物评审（角色视角检验） |
| 6 | `book-chapter-revise` | 根据审计结果修订 |

---

## 常见问题

**Q: 需要额外的 AI API Key 吗？**

A: AutoWrite CLI 本身不调用 AI，它依赖上层 Agent（如 Hermes）提供 AI 能力。请确保你的 Agent 已配置 AI API。

**Q: 支持英文书吗？**

A: 支持。在 `autowrite init` 时指定 `--genre en` 即可。审计链会自动切换英文评审模型。

**Q: 可以不用 Hermes 吗？**

A: 可以。AutoWrite CLI 只依赖 shell 命令，任何 Agent 只要能执行 `autowrite <命令>` 即可驱动。

**Q: 如何自定义 Token 预算？**

A: 通过环境变量或 `book.conf` 配置。详见 `book-agent-core/budget.py`。

---

## 贡献指南

欢迎贡献代码！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

**开发流程：**

```bash
# 1. Fork 本仓库
# 2. 创建特性分支
git checkout -b feat/your-feature

# 3. 提交改动
git commit -m "feat: add your feature"

# 4. 推送分支
git push origin feat/your-feature

# 5. 创建 Pull Request
```

**开发环境要求：**
- Bash 4.0+
- Python 3.8+
- `shellcheck`（可选，用于 lint bash 脚本）

---

## License

MIT License - 详见 [LICENSE](LICENSE) 文件。
