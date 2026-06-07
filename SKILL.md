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

## 预模式闸门 — S1-S3

**任何模式触发后，第一步不是进 First Move——是确认 S1-S3。这三项不知道，后面的方案都建在沙子上。**

```
S1 — 隐私与安全
    "项目是个人的还是公司的？涉及敏感数据吗？能上传代码/调外部API吗？"
    选项（单选）：个人项目，无限制 / 个人项目，有限制（需说明） / 公司项目，有合规要求

S2 — 项目边界
    "AI 能碰哪些文件？不能碰哪些？"
    选项（单选）：限定项目目录内 / 可读工作区不写 / 工作区内自由 / 别碰代码之外的文件

S3 — 操作确认阈值
    "哪些操作需要先问你？"
    逐项确认（单选 ×6）：读文件 / 写文件 / 删文件 / 跑命令 / Git操作 / 安装依赖
    每项：自动 / 先问我
    确认有效期：仅本次 / 本次会话 / 永久

S1-S3 全部确认 ✔ → 进入对应模式的 First Move。
```

## Modes

| 触发 | 模式 | 做什么 | 耗时 |
|------|------|--------|------|
| `/tell-me-everything` / 新项目/新功能/重构请求 | **full** | S4-S6 → A → B 全维度访谈。已有答案跳过 | ~3-5min |
| 任何改动请求（bugfix/格式变更等） | **maintain** | 规模评判 → 门控 → 实现 → M7+日志 | 按需 |
| `/tell-me-everything ship` / "上线"/"发版本" | **ship** | R1-R6 发布安全检查 | ~1min |
| `/debug-tme` / `/debug-tme session\|compliance\|files\|state` | **debug** | 对话审计 + 协议合规 + 文件追踪 + 状态快照。详见 `references/debug-guide.md` | ~30s |

未指定模式时默认走 `full`。

## First Move — full mode

```
触达 full（闸门 S1-S3 已过）→
  "S1-S3 确认了。继续 S4-S6。"

  按 references/quick-diagnosis.md S级模板逐问弹框：
    S4 Env 环境路径 → S5 确认后有效期 → S6 环境操作"谁来"

  S 级全部完成 ✔ → 进入 A 级

  A 级第一问 — A10 参考优先（不可跳过）
    "有没有参考项目或类似效果的东西？有就发给我，没有我帮你搜。"

  → 根据 S 级答案决定其余 A 级追问深度
  → B 级只在用户说"更多"时展开
```

## First Move — debug mode

```
/debug-tme [mode] 触发
  →
1. 运行 python scripts/debug-tme.py init [mode]
   → 创建 .claude/debug/YYYY-MM-DD-HHmmss/ 目录及占位文件
2. 按 references/debug-guide.md 各文件内容规范逐文件填充
   → 从当前对话上下文提取信息
   → 证据坐标精确到文件:行号或具体原文
3. 写入对应文件（Write 工具 — check-plan-mode.py 已豁免 .claude/debug/）
4. 报告输出路径："Debug 输出：.claude/debug/YYYY-MM-DD-HHmmss/"
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

### 隐式信号快速索引

| 用户行为 | 含义 | Agent 行为 |
|----------|------|-----------|
| "我说的是X" / "我的意思是X" | 纠正了目标，没有授权动手 | 更新方案。弹框：加到方案里还是动手改文件？ |
| "[动词]完告诉我效果" / "改完给我看" | 谓语"告诉/给/看"→信息请求 | 不实现。出方案。 |
| "你必须展示出来" / "展示一下" | 谓语"展示/显示"→信息请求 | 查证+展示+停止。不实现。 |
| "可以" + 追加要求 | 方案方向可以 ≠ 授权动手 | 完善方案。弹框确认。 |
| "你又走捷径了" / "偷懒了" | 规则违规 | 查违规点。 |

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
| `references/debug-guide.md` | Debug 协议卡片 — 5 个触发命令、输出规范、审计硬约束 |
