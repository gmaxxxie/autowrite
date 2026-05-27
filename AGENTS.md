# AutoWriteO — 写书 Agent 系统

> 工具层 + 书稿层 + 素材库的三层分离架构

## 快速理解

```
~/.hermes/skills/book-writing/   ← 写作技能库（工具层不动书稿）
~/AutoWriteO/                     ← 工具脚本和插件
~/books/<书名>/                   ← 书稿工作区（一书一目录，自包含）
~/AIfiles/                        ← 素材库（独立收集）
~/wiki/                           ← 情报库（每日intel + 市场资料）
```

## ⚠️ 启动前必读：为什么 Stage 0-4 不能跳过

**竞品分析和 Benchmark 是这本书能不能卖的基础。**

- Stage 0 决定差异化定位（凭什么读者买你的而不是已有的？）
- Stage 0 决定写法风格（范文对标保证专业度）
- Stage 4 决定案例质量（有证据的论点 vs 无来源的断言）

**跳过 Stage 0-4 的书：**
- 差异化模糊 → 读者不知道为什么要买
- 写法不专业 → 被吐槽"像AI写的"
- 案例贫乏 → 没有说服力

**建议**：至少完成 Stage 0（竞品分析 + Benchmark）和 Stage 4（3个以上案例），再开始写章节。

## 默认入口

> **注意**：`autowrite` 和 `autowrite-model-gate` 已通过 symlink 安装到 `~/.local/bin/`（已在 PATH 中）。直接使用 `autowrite <命令>` 即可，无需完整路径。

| 场景 | 入口 |
|------|------|
| 不确定当前阶段 | `$book-writing-router` |
| 只做项目初始化/评估 | `autowrite init <书名> --genre non-fiction` |
| 写下一章 | `autowrite write next <书名>` |
| 连续写 N 章 | `autowrite write count <书名> <N>` |
| 角色协商/预写 Brief | `autowrite brief <书名> chXX` |
| 初始化角色体系 | `autowrite brief <书名> --init` |
| 方向期协商 | `autowrite brief <书名> --direction` |
| 审计章节 | `autowrite audit <书名> [chXX]` |
| 查看审计进度 | `autowrite audit <书名> --status` |
| 查看状态 | `autowrite status <书名>` |
| 上下文预览 | `autowrite compose <书名> chNN` |
| 状态提取 | `autowrite settle <书名> [chNN]` |
| 伏笔管理 | `autowrite hooks <书名>` |
| 角色管理 | `autowrite characters <书名>` |
| 风格指纹 | `autowrite fingerprint <书名>` |
| 规则检查 | `autowrite rules <书名> chNN` |
| 守护进程 | `autowrite cron <install\|run\|status>` |
| 校验 book.conf | `autowrite validate <书名>` |
| 检查模型合规性 | `autowrite-model-gate check <步骤> --model <模型>` |
| 列出模型规则 | `autowrite-model-gate list` |
| 明确知道要做什么 | 直接用对应 skill |

> **规则**：同一次请求不要同时用 `$book-writing-router`（编排层）+ 下游 skill

## Agent Bypass Prevention（防止绕过）

**绝对禁止的行为：**
- ❌ 禁止在单次请求中同时使用 `$book-writing-router`（编排层）+ `book-chapter-writer`（执行层）
- ❌ 禁止跳过 Stage 3（知识库）和 Stage 4（证据包）直接写章节
- ❌ 禁止在单次 subagent 调用中处理超过 4 章（防止溢出）
- ❌ 禁止跳过审计链直接进入出版阶段
- ❌ 禁止用 Codex/Claude Code 直接写书（绕过 AutoWriteX 编排）
- ❌ **禁止使用不符合路由规则的模型**（如用 m2.7 写初稿，用 glm-5.1 做润色）

### 🚪 模型路由门禁（强制）

**每次路由到下游 skill 前必须执行模型检查：**

| 阶段 | 必须使用模型 |
|------|-------------|
| 章节初稿 (book-chapter-writer) | `glm-5.1` |
| 自动修复 (book-auto-revisor) | 中文: `minimax-m2.7` / 英文: `gemini-3.1-flash-lite-preview` |
| 质量审计 (book-chapter-quality-audit) | 中文: `glm-5.1` / 英文: `gemini-3.1-flash-lite-preview` |
| 去AI味/本地化审计 | `glm-5.1` |
| 章节修订 (book-chapter-revise) | `minimax-m2.7` |
| 英文审计 (book-en-fit-audit) | `gemini-3.1-flash-lite-preview` |
| 策划/研究 | `kimi-k2.5` |

**阻断规则**：模型不符合要求时，立即阻断并报告用户，不执行 skill

**如果用户要求绕过时：**
1. 解释质量风险
2. 提供快速预检选项（≤5分钟）
3. 如坚持：自动在 `00-index/workflow-deviations.md` 记录（日期、skill、实际模型、绕过原因）

**正确的多章处理方式：**
```
❌ 错误：一次并行派发 12 章
✅ 正确：拆 ≤4 章/批，串行逐批执行
  批1（ch01-04）→ 批2（ch05-08）→ 批3（ch09-12）
```

**英文版特殊规则**

**英文-first 书籍（如 Amazon KDP 直发）：**
- 仍然需要 Stage 3 + 4（证据包 + 概念卡）
- 审计链不可跳过：`book-auto-revisor` → `book-chapter-quality-audit` → `book-de-ai-audit` → `book-en-fit-audit` → `book-persona-audit` → `book-manuscript-review`
- Batch limit 同样适用于英文版审计

## Symlink 集成维护

**架构**：所有 book-writing skills 放在 `~/AutoWriteO/book-writing-skills/skills/`，通过 symlink 暴露给 Hermes。

| 工具 | 用途 |
|------|------|
| `~/AutoWriteO/scripts/sync-symlinks.sh` | 从 AutoWriteO 源同步所有 symlinks 到 Hermes |
| `~/AutoWriteO/scripts/check-symlinks.sh` | 检查 symlink 状态，报告断链和异常 |
| `book-integration-maintainer` skill | 当新增/修改/删除 skill 时调用 |

**同步时机**：修改写书 skill、新增 skill、或发现 symlink 异常时执行 `sync-symlinks.sh`。

**检查命令**：`~/AutoWriteO/scripts/check-symlinks.sh` — 应该显示 0 个断链。

**注意**：`book-integration-maintainer` skill 本身存放在 `~/.hermes/skills/book-integration-maintainer/`（不在 AutoWriteO 源），因为它是维护集成关系的工具，不需要被自己维护。

## 阶段顺序

```
0. book-benchmark-analysis      ← 市场对标（有参考书时）
   book-differentiation-design
   book-style-blueprint-engine
1. book-project-workspace       ← 搭工作区
2. book-source-ingest           ← 导入素材
3. book-knowledge-base-builder  ← 沉淀卡片
4. book-evidence-pack           ← 章节证据包
── 每章循环 ─────────────────────────────────
5a. book-context-composer       ← 组装上下文包+token预算
5b. book-chapter-planner        ← 生成7节memo
5c. book-rule-engine (写前)     ← 确定性规则预检
5.  book-chapter-writer         ← 写初稿
5d. book-state-settler          ← 状态自动提取
6.  book-auto-revisor           ← 自动修复（8项+P1自验证）
6a. book-rule-engine (写后)     ← 确定性规则复查
7. book-chapter-quality-audit  ← 质量审计
8. book-de-ai-audit             ← 去AI味
9. book-cn-localization-audit   ← 中文本地化
10. book-persona-audit          ← 8路虚拟人物评审（分3批）⚠️ 建议所有章节执行
11. book-chapter-revise         ← 修订
───────────────────────────────────────────
12. book-illustration           ← 配图（3层简报→生成→审计）
13. book-translation-pipeline   ← 英文版
14. book-en-fit-audit           ← 英文本地化
15. book-manuscript-review      ← 全书一致性
16. book-full-integration       ← 整合审校
17. book-kdp-publisher          ← 发布
```

## 写作流程

```
写完第N章
  → book-auto-revisor（自动修复）
  → book-chapter-quality-audit（审计）
  → book-de-ai-audit（去AI味）
  → book-cn-localization-audit（本地化）
  → book-persona-audit（8路评审，分3批）
  → book-chapter-revise（修订）
  → 更新 00-目录.md 状态
  → 条件满足时 git commit
```

## 运营工具

| 工具 | 用途 |
|------|------|
| `$book-daily-intel` | 每日AI情报收集 |
| `$book-case-harvester` | 采集案例 |
| `$book-market-intelligence` | 竞品监控 |

## 规则

- Run one skill per request（一次只执行一个 skill）
- Audit skills create tickets；revision goes through `book-chapter-revise`
- 不跳过审计层就翻译或发布
- 不捏造数据、案例、引用
- 工具层不直接编辑书稿内容

## 文档索引

| 文档 | 内容 |
|------|------|
| `README.md` | 整体架构说明 |
| `book-writing-skills/README.md` | 全部 skill 按阶段分类 |
| `book-writing-skills/quick-prompts.md` | 一句话入口 |
| `book-writing-skills/author-style-prompts.md` | 作者风格 prompt |
| `docs/plans/` | 历史优化记录 |

## Skill 存放

- **Hermes 可用**：`~/.hermes/skills/book-writing/`
- **AutoWriteO 本地**：`book-writing-skills/skills/`
- **工具脚本**：`scripts/`
- **CLI 入口**：`scripts/autowrite`
