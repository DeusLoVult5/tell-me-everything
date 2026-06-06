# CLAUDE.md 生成模板

## O1：CLAUDE.md（≤200行）

只放"被忘了会出事故"的信息。

```markdown
# {项目名} — 项目配置

【当前模式：PLAN】

## 信号词
- {实现信号词} → 切 IMPLEMENT
- 模糊（搞吧/都实现/直接改）→ 弹框确认
- {禁止信号词} → 保持 PLAN

## 安全边界
- 操作范围：{I2}
- 隐私：{I1}
- API：{I1 API约束}

## 操作确认阈值
- 读/写/删/命令/Git/依赖：各是自动还是先问
- 环境操作：{谁来建/谁来排查}
- 错误处理：{I13}

## 项目决策
- 目标：{I4} | 技术栈：{I5} | 架构：{I6}
- 技术路线：Phase 1 {...} → Phase 2 {...}
- 项目目录：{Env}

## 代码默认规范
- 缩进：Tab | 命名：snake_case + PascalCase
- 类型注解：强制（所有函数参数+返回值）
- 格式化：ruff，pre-commit hook
- import 排序：系统级 → 标准库 → 三方库 → 本地库
- 最简原则：不用类不嵌套函数（非必要），重复 ≥3 次才抽
- 注释：{用户语言}，功能说明+参数说明
- 功能间空一行；import与功能间空三行
- 测试文件：`功能名_test`

## 日志硬门
- 不写日志不许 IMPLEMENT→PLAN 切换
- 每次改动自动写，双线：`logs/agent/` + Git commit
- 格式：JSON `{"timestamp":"...", "summary":"...", "files":["..."], "impact":"..."}`

## 交互
- 回复风格：{I15} | 日志：{I14}

## 方法论摘要
- 用户没说的必须问，不猜不代选
- 先出方案再动手，模糊信号弹框确认
- S/A/B 信息分级，S 级不过不动手
- 遵守反推动计数器

## 参考索引
详细规范见 CLAUDE.d/ 目录
```

### 不放的内容
编码风格（I10）、测试细节（I11）、日志格式（I14）等 B 级信息 → 放 CLAUDE.d/。

## O2：CLAUDE.d/ 目录

按需读取，每文件 ≤150 行：

```
CLAUDE.d/
├── tech-stack.md        I5+I7 完整答案
├── architecture.md      I6 完整答案 + 目录结构
├── coding-style.md      I10 完整答案 + 格式化配置
├── testing.md           I11 完整答案
├── repo-boundary.md     I8 完整答案
├── error-handling.md    I13 完整答案
├── logging.md           I14 完整答案
└── interaction.md       I15 完整答案 + 信号词完整列表
```

## O3：触发方式

- **新项目**：空目录/无 CLAUDE.md → 自动 quick 模式
- **手动**：`/tell-me-everything` 或 `/tell-me-everything quick|full|ship`
- **模糊需求**：信息严重不足 → 自动加载
- **发布**："上线"/"发版本"/"release" → ship 模式
