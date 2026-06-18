# CLAUDE.md — TELL-ME-EVERYTHING 项目自身

> TME 项目使用 TME 自身的门控协议。以下为项目级配置。

## 信号词
- 实现 / deal

## 安全边界
- S1: 个人项目，公开（MIT 协议），无敏感数据
- S2: 限定项目目录内（d:/PythonProjects/tell-me-everything/）
- S3: 写文件/删文件/Git操作=先问我；读文件/跑命令=自动；安装依赖=先问我

## 代码默认规范
- Python 项目。缩进：Tab。命名：snake_case + PascalCase。类型注解：强注解
- 测试框架：pytest。格式化：ruff。commit：Conventional Commits（中文）
- 日志输出到 logs/agent/YYYY-MM-DD.md（JSON Lines）

---

## 高优先级待办

### TODO-H1: `${CLAUDE_SKILL_DIR}` 变量跨环境兼容性

**状态:** 已知故障，当前用硬编码绝对路径绕过，未从根本上解决。

**现象:**
SKILL.md frontmatter hooks 中使用 `${CLAUDE_SKILL_DIR}` 引用脚本路径时，在部分环境（非 Git 仓库、非标准项目目录）中该变量被解析为错误路径（如 `D:\Git`），导致 `check-plan-mode.py` 和 `check-boundary.py` 无法执行。Harness 将 hook command 失败视为 DENY，造成项目所有 Write/Edit 操作被阻塞。

**影响面:**
- 任何安装了 TME 的用户，在非标准项目目录中触发 TME 时，Write/Edit 全部失效
- S1-S3 闸门结果无法写入 CLAUDE.md，闸门形同虚设
- Debug 模块 `.claude/debug/` 写入也被连坐拦截

**当前绕过方案 (2026-06-18):**
SKILL.md L9/L14 中 `${CLAUDE_SKILL_DIR}` 已替换为硬编码绝对路径 `C:/Users/Dle/.claude/skills/tell-me-everything/scripts/`。

```yaml
# 当前（硬编码）
command: "python \"C:/Users/Dle/.claude/skills/tell-me-everything/scripts/check-plan-mode.py\""
```

**绕过方案的局限:**
- 换用户名、换机器、非 Windows 系统 → 路径失效
- 每次换环境需要手动修改 SKILL.md frontmatter
- 不适合公开发布（GitHub 上的 SKILL.md 包含特定用户路径）

**可能的根本修复方向:**
1. 等待 Claude Code 修复 `${CLAUDE_SKILL_DIR}` 跨环境解析一致性
2. 改用 `${SKILL_DIR}`（如果 Claude Code 有提供的话）
3. 改用 hook type `prompt` 替代 `command`（不依赖外部脚本执行），但 prompt-type hook 的拦截粒度不如 command-type
4. 提供安装脚本，安装时自动替换 SKILL.md 中的占位符为实际路径

**发现来源:** Debug 日志 `2026-06-18-104034/`（用户项目：d:\PythonProjects\Embedded AI Practical Project）
