# Debug 协议卡片

> 触发后 Agent 按本指南逐文件生成内容，写入当前项目 `.claude/debug/` 目录。

## 触发命令

| 命令 | 模式 | 输出文件 |
|------|------|----------|
| `/debug-tme` | 全量 | session.md + raw.md + compliance.md + files.md + state-snapshot.md |
| `/debug-tme session` | 对话审计 | session.md + raw.md |
| `/debug-tme compliance` | 协议合规对账 | compliance.md + raw.md |
| `/debug-tme files` | 文件变动追踪 | files.md + raw.md |
| `/debug-tme state` | 状态快照 | state-snapshot.md + raw.md |

部分触发 = 该模式文件 + raw.md（raw.md 始终输出）。

## 输出目录结构

```
.claude/debug/
└── YYYY-MM-DD-HHmmss/
    ├── session.md
    ├── raw.md
    ├── compliance.md
    ├── files.md
    └── state-snapshot.md
```

输出到当前项目的 `.claude/debug/`，非 skill 库目录。目录名取触发时刻的时间戳。全量 = 5 文件，部分触发 = 2 文件。

## 各文件内容规范

### session.md — 对话审计

```markdown
# 对话审计 — YYYY-MM-DD HH:mm:ss

## PLAN/IMPLEMENT 切换时间线
| 时间 | 切换方向 | 触发原因 |
|------|----------|----------|
| HH:mm | PLAN → IMPLEMENT | 信号词"实现" / 用户自定义信号词 |
| HH:mm | IMPLEMENT → PLAN | 自动切回（任务完成） |

## M5 门控判定记录
| 时间 | 判定点 | 结果 | 证据 |
|------|--------|------|------|
| HH:mm | 规模评判 | 通过/未通过 | 弹框确认记录 |

## 反推动计数器变动
| 时间 | 变动 | 新值 | 原因 |
|------|------|:----:|------|

## 隐式信号触发记录
| 时间 | 用户行为 | 判定含义 | Agent 响应 |
|------|----------|----------|-----------|
```

### raw.md — 原始对话

最近 20 轮，从最后一轮往前数。逐轮完整转录，不概括不省略。

```markdown
# 原始对话 — YYYY-MM-DD HH:mm:ss

> 最近 20 轮完整转录

---

### 轮次 1（倒数第 20 轮）
**用户：** {完整原文}

**AI：** {完整原文}

---

### 轮次 2（倒数第 19 轮）
...
```

### compliance.md — 协议合规对账

逐条检查，每条必须附带证据坐标。

```markdown
# 协议合规对账 — YYYY-MM-DD HH:mm:ss

| # | 门控项 | 状态 | 证据 |
|:--:|--------|:--:|------|
| 1 | 规模声明是否在对话中呈现并确认？ | ✅/❌/— | 文件:行号 |
| 2 | S 级信息是否全部确认？ | ✅/❌/— | 文件:行号 |
| 3 | 是否有推结束暗示？ | ✅/❌/— | 具体语句 |
| 4 | 文档类改动是否走副本流程？ | ✅/❌/— | 文件:行号 |
| 5 | 是否有 Bash 绕过 Write 钩子？ | ✅/❌/— | 具体命令 |
| 6 | 日志硬门是否执行？ | ✅/❌/— | 文件:行号 |
| 7 | 自检清单是否逐条通过？ | ✅/❌/— | 文件:行号 |
| 8 | 方案是否在对话中完整呈现？ | ✅/❌/— | 文件:行号 |
| 9 | 输出是否以"其余不变"代替？ | ✅/❌/— | 具体语句 |
| 10 | 一个弹框是否只问一个决策？ | ✅/❌/— | 弹框内容摘要 |

状态：✅ 合规 / ❌ 违规 / — 本轮不适用
```

### files.md — 文件变动追踪

```markdown
# 文件变动追踪 — YYYY-MM-DD HH:mm:ss

## 当前 Git 状态
- 分支：{branch}
- 最新 commit：{hash} — {message}

## 本次会话写入记录
| 时间 | 工具 | 文件路径 | 操作 | 是否拦截 |
|------|------|----------|------|:--:|
| HH:mm | Write | path/to/file | 新建/修改 | 否/是(原因) |

## 被门控拦截的操作
| 时间 | 工具 | 目标文件 | 拦截原因 |
|------|------|----------|----------|
```

### state-snapshot.md — 状态快照

```markdown
# 状态快照 — YYYY-MM-DD HH:mm:ss

## 基本信息
- 当前分支：{branch}
- 模式标记：PLAN / IMPLEMENT

## CLAUDE.md 当前内容
{完整转录 CLAUDE.md 内容}

## 规模声明
{当前规模声明内容，无则写"无"}

## 反推动计数器
当前值：{N}

## 上次日志写入
{时间 — YYYY-MM-DD HH:mm:ss，无则写"无记录"}

## 钩子状态
- check-plan-mode.py：{活跃/异常/不存在}
- check-boundary.py：{活跃/异常/不存在}
```

## 结构化审计硬约束

- 每项门状态必须附带**证据坐标**（文件路径 + 行号 + 时间戳）
- 异常必须带具体**工具名/操作名**
- **不设"总结"/"评价"字段**——只记事实
- 无记录 = 写 **"无记录"**，不能跳过留空
- compliance.md 的 10 项逐条填写，不能省略任一行

## Agent 执行流程

```
/debug-tme [mode] 触发
  ↓
1. 运行 python scripts/debug-tme.py init [mode]
   → 创建 .claude/debug/YYYY-MM-DD-HHmmss/ 目录及占位文件
  ↓
2. 按本指南逐文件生成内容
   → 从当前对话上下文中提取所需信息
   → 证据坐标必须精确到文件:行号或具体原文
  ↓
3. 写入对应文件（使用 Write 工具）
  ↓
4. 报告输出路径："Debug 输出：.claude/debug/YYYY-MM-DD-HHmmss/"
```

## 与 Issue 模块隔离

本 Debug 模块独立运行，不与 Issue 模块耦合。
Issue 模块（`/tme issue`、`/tme issue debug`）单独设计实现时，
其 debug 文件打包逻辑以本模块输出为基础，不修改本模块。
