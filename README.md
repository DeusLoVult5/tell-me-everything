# tell-me-everything

> 原生 prompt 的 DLC。把"帮我做个记账app"翻译成 AI 能正确执行的结构化输入。

## 解决什么问题

AI 编程助手的最大瓶颈不是 AI 不够聪明，而是**用户不知道怎么说**。

你说 7 个字，AI 猜 100 个决策，猜错是常态。tell-me-everything 在中间架一层——把你知道但没说出口的信息全部问出来，问完了再动手。

## 怎么工作的

```
你："帮我做个记账app"
  ↓
skill 追问：隐私边界？技术栈？架构偏好？编码风格？测试？部署？
  ↓
每个决策点你选一下（大部分是弹框选择题，不用打字）
  ↓
skill 输出 CLAUDE.md，AI 拿到完整的结构化输入
  ↓
AI 不再猜 → 输出的代码接近你的预期
```

## 安装

```bash
# 克隆到 Claude Code skills 目录
git clone https://github.com/DeusLoVult5/tell-me-everything.git \
  ~/.claude/skills/tell-me-everything
```

或者直接复制 `SKILL.md` 和 `references/` 到 `~/.claude/skills/tell-me-everything/`。

## 使用

- **新项目**：空目录打开 Claude Code → skill 自动触发
- **手动调用**：输入 `/init` 或"帮我分析一下这个项目怎么做"
- **模糊需求**：你的第一条需求信息不足时自动加载

## 核心设计

| 机制 | 做什么 |
|------|--------|
| **7 个核心方法** | M0-M7，从联想补全到审查重构，全程不要 AI 猜 |
| **15 维度分级访谈** | S/A/B 三级，S 级（安全/隐私/路径）死也要问出来 |
| **混合状态门** | 信号词=动手，模糊=弹框确认，禁止=不动。不靠语义判断 |
| **反推动计数器** | AI 催"可以写了吧？"被拒 2 次→锁死讨论模式 |
| **隐式信号解读** | 不问你"我做得好吗"，从你的行为中读真实评价 |
| **决策原子性** | 一个弹框只问一个决策，what 和 who 分两个弹框 |

## 输出

- `CLAUDE.md`（≤200行）：只放压缩也不会丢的核心约束
- `CLAUDE.d/`：技术细节按需读取

## 适用人群

科班生 / 想学 vibe coding 的人。你需要懂一些基础术语，但不需要知道怎么把脑子里想的翻译成 prompt——skill 帮你翻译。

## 协议

MIT

## 更新日志

[CHANGELOG.md](CHANGELOG.md)
