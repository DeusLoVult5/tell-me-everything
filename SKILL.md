---
name: tell-me-everything
description: 原生 prompt 的 DLC——把模糊的用户意图翻译成结构化的 AI 输入。用户说"帮我做个记账app"，skill 追问补齐技术栈、架构、安全边界、编码偏好等所有用户知道但没说的信息，然后在动手前出路线图确认。TRIGGER：新项目首次对话、用户说"/tell-me-everything"、用户要求搭建新功能但信息严重不足时。也适合用户说"帮我分析一下这个项目怎么做""从零开始做X"。USE WHEN：用户开始一个新项目、表达了一个模糊的功能需求、或希望生成高质量可落地的代码。
hooks:
  PreToolUse:
    - matcher: "Write|Edit|MultiEdit"
      hooks:
        - type: "command"
          command: "python \"${CLAUDE_SKILL_DIR}/scripts/check-plan-mode.py\""
          timeout: 10
    - matcher: "Write|Edit|MultiEdit"
      hooks:
        - type: "command"
          command: "python \"${CLAUDE_SKILL_DIR}/scripts/check-boundary.py\""
          timeout: 10
  Stop:
    - matcher: ""
      hooks:
        - type: "prompt"
          prompt: "Check if this session made code changes (Write/Edit/MultiEdit tools were used). If yes, verify that a log entry was written to logs/agent/YYYY-MM-DD.md for today in the project directory. If no log entry exists when code changes were made, block the stop with reason 'Log hard gate: write the change log (step 5 of the protocol) before stopping.'. If no code changes were made, approve the stop."
          timeout: 30
---

# tell-me-everything / 告诉我一切

> 用户与 AI 之间的翻译层。把模糊意图翻译成结构化输入。
> 问完了再动手。问不完，不动手。

## Modes

| 触发 | 模式 | 做什么 | 耗时 |
|------|------|--------|------|
| `/tell-me-everything quick` / "帮我分析一下X" | **quick** | 3 个快捷问题 → 快速诊断 + 路线图。默认参数补位 | ~30s |
| `/tell-me-everything full` / "初始化这个项目" | **full** | S → A → B 全维度访谈。已有答案跳过 | ~3-5min |
| `/tell-me-everything ship` / "上线"/"发版本" | **ship** | R1-R6 发布安全检查 | ~1min |
| 任何改动请求 | **maintain** | 规模评判 → 门控 → 实现 → M7+日志 | 按需 |

未指定模式时默认走 `quick`。

## First Move — quick mode

```
用户触发 TME（无显式模式）
  →
"我帮你补全了再动手。先问三个问题："

弹 AskUserQuestion（3个快捷问题）：
  Q1: 纯前端还是前后端？    → 决定 I5技术栈 + I6架构
  Q2: 数据存哪（本地/云端）？→ 决定 I1隐私 + I5数据库
  Q3: 谁用（练手/自用/上线）？→ 决定 I4目标 + I7部署

用户答完 →
  自动分析 + 弹框：
  "快速分析：{摘要}。风险点：{2-3个}。
   建议Phase 1：{技术栈+交付物}。

   接下来你想："
  ├─ "完整初始化" → 切 full 模式（S+A+B，跳过已答3问）
  ├─ "先出方案"   → 基于3个答案+默认参数，直接出路线图
  └─ "就按这个来"  → 切 IMPLEMENT，开始动手
```

如果用户连 3 个问题都答不上来 → "我不懂"处理协议（见下）。

## First Move — full mode

```
触达 full →
  "完整初始化。S级4问先过掉。"

  按 interview-guide.md S级模板逐问弹框：
    I1 隐私安全 → I2 项目边界 → I3 确认阈值 → Env 环境路径

  → 根据 S 级答案决定 A 级追问深度
  → B 级只在用户说"更多"时展开
```

## Default Output Template — 方案输出

Agent 出方案时，用此模板。不增不减。

```
## 方案：{≤15字的标题}

### 改动范围
| 文件 | 操作 | 预计行数 |
|------|------|:--------:|
| {路径} | {新建/修改/删除} | {N} |

### 步骤
1. {步骤1 — ≤20字}
2. {步骤2}
...（≤5步）

### 验证
{1句话：怎么验证正确}

### 风险（如果有）
| 风险 | 概率 |
|------|:----:|
| {具体风险} | {高/中/低} |
...（≤2行）
```

## Default Limits

| 项 | 上限 |
|----|:----:|
| 方案标题 | ≤15 字 |
| 改动范围表 | ≤5 行 |
| 实现步骤 | ≤5 步，每步 ≤20 字 |
| 风险表 | ≤2 行 |
| 方案全文 | ≤200 字 |

## 门控卡片 — 每次改动必经 6 步

```
步骤0 M0追问   → 缺要素（哪/做了什么/什么现象/期望什么）→ 不问完不动手
步骤1 规模评判 → Agent陈述事实 → 弹AskUserQuestion确认
步骤2 写入声明 → CLAUDE.md：【规模：X改动 — N文件】
步骤3.5 自检   → 逐条过自检清单（见 references/maintenance-protocol.md）
步骤4 实现     → 边界内写代码
步骤5 M7+日志  → /review审查 → 写日志 → 日志硬门 → 切回PLAN
```

详细门控见 `references/gate-protocol.md`。

## 修改类型分流

```
代码类（源码/配置/脚本）
  → 门控卡片6步（上面那条）→ 方案必须在对话呈现 → 确认后直接写源文件

文档类（README/CHANGELOG/skill文件）
  → 副本流程：
    ① cp → _draft.md
    ② 改草案
    ③ 告知路径
    ④ 弹AskUserQuestion：合并/保留/丢弃
    ⑤ 日志照写

同步更新（CHANGELOG/README附属更新，前面紧邻完整IMPLEMENT链路）
  → 副本仍创建，不弹合并框，直接合并
  → 判定条件缺一不可，详见 references/maintenance-protocol.md
```

## 阶段锚定

```
没有实现信号词（"实现"/"deal"/用户自定义）时：
  "加入/加上/同步/可以/更新" → 锚定PLAN → 指"加入方案中"
  "[动词]完告诉我效果" → 信息请求，不实现
  "可以" + 追加要求 → 方案方向可以，不授权动手

实现信号词后跟"但是/不过/等一下/？"→ 不是信号词，是在追问。
```

## 实现前检查（P1-P5）

每轮动手前：当前 Phase / 有无参考 / 需要手册吗 / 怎么测试 / 配置放哪。

## "我不懂"处理

```
用户说"我不懂" →
  ✅ 降低门槛（术语→白话，场景→具体）
  ✅ 给锚点（"一般 A 或 B"）
  ❌ 不替用户做决定

还答不上来 → "我先用最常见方案，优点X，风险Y。你记着有Y的风险。"
只有用户明确说"你帮我选" + M5 确认后才能代选。
```

## 输出

| 输出 | 内容 |
|------|------|
| CLAUDE.md（≤200行） | 信号词 + 安全边界 + 确认阈值 + 代码默认规范 + 日志硬门 + 指向 CLAUDE.d/ |
| CLAUDE.d/ | I1-I15 完整回答 + 技术规范 |

## 不做的事

- 不教用户写提示词（独立 skill 方向）
- 不承诺消除 LLM 视觉理解偏差
- 不承诺补上小众语言训练数据
- 不扮演任何角色
- 不判断用户水平 / 不要求用户自评
- 不替用户决定 S 级信息

## 参考索引

| 文件 | 内容 |
|------|------|
| `references/defaults.md` | 43项默认参数 |
| `references/gate-protocol.md` | 门控卡片完整版 + 反推动计数器 |
| `references/maintenance-protocol.md` | 后段协议 + 规模分级 + 自检清单 + 文档副本流程 |
| `references/review-protocol.md` | M7 审查 + 重构六步骤 |
| `references/output-template.md` | CLAUDE.md + CLAUDE.d/ 生成模板 |
| `references/quick-diagnosis.md` | S 级快捷访谈 + A/B 级完整访谈指南 |
