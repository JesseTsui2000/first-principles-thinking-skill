# Contributing

本项目欢迎改进，但不接受只增加抽象口号、让文本更长或让输出显得更“颠覆”的修改。禁止直接向 `main` 写入；所有修改都应在短生命周期工作分支完成，并通过 Pull Request 审查。

## 适合提交的问题

- Skill 没有在应该使用时触发；
- Skill 在普通任务中错误触发；
- 把行业惯例误当成硬约束；
- 把硬约束误当成可随意删除的假设；
- 无证据地否定专业知识；
- 忽略制造、验证、组织、维护或失败成本；
- 把理论可行误判为商业或工程可行；
- 对人类、文化和社会问题过度还原；
- 输出空泛、重复、过长或无法验证；
- 新版本导致旧能力退化。

## 贡献流程

### 通用步骤

1. 描述问题或维护缺口，并关联 Issue 或其他可追溯记录。
2. 从最新 `main` 创建短生命周期工作分支。
3. 判断是否影响 Skill 行为、触发范围或输出契约，再完成最小充分修改。
4. 根据改动类型执行适当验证。
5. 根据兼容性影响提出版本建议，并更新 `CHANGELOG.md` 和相应版本文件。
6. 运行：

```bash
python3 tools/validate_repo.py
python3 tools/build_openai_plugin.py
python3 tools/build_openai_plugin.py --check
git diff --check
```

7. 创建 PR，提供问题、验证证据和版本判断。

### Skill 行为变更的附加要求

涉及 `SKILL.md` description、触发范围、分析规则、核心七步流程、输出契约、边界、禁止事项或 eval 预期行为时：

1. 记录可复现的真实失败案例。
2. 将案例转化为 eval，明确预期行为和失败信号。
3. 使用最新不可变稳定版复现并记录旧版行为。
4. 使用相同输入对比稳定版与候选版，记录改善、退化和边界。

### 非行为维护变更

纯文档、validator、CI、安装说明、模板、链接、拼写或元数据维护不要求修改 `evals.json`，也不要求无意义的模型行为对比。PR 中应将 eval ID 和行为对比标记为 `N/A`，说明不涉及 Skill 行为的原因，并提供适当的静态验证、负向测试或文档审查证据。

OpenAI Plugin wrapper、repo-local marketplace 和 submission golden set 属于平台包装层。它们必须引用现有核心 Skill，不得复制指令或扩大触发契约。Plugin submission tests 不得替代或静默修改核心 eval。

Plugin packaging 的受版本控制事实源包括 canonical Core Skill、`packaging/openai-plugin/plugin.json`、两个版本文件和 submission golden set。`.build/plugins/first-principles-thinking/` 是 ignored generated output，不允许人工编辑或提交；其中的 `SKILL.md` 只能由构建流程从 canonical Skill 复制，并必须通过 byte 和 SHA 对比。

Skills-only Portal submission 使用包含 supported Plugin manifest 和至少一个 bundled Skill 的 ZIP。当前 generated directory 是未来 ZIP 的 Plugin root，不是已生成的 ZIP；directory branding assets 和 Portal metadata 完成并通过 preflight 后才能生成提交包。Skills-only interface listing URLs 为可选；不得添加身份、URL、logo 或 listing 占位符来伪造 directory readiness。

## 修改原则

- 新规则必须对应可复现的问题。
- 优先修改现有规则，避免无限追加相似条款。
- 不将个人价值判断写成客观第一原理。
- 不删除法律、安全、伦理、可靠性和责任边界。
- 不为了减少字数而删除关键失败防护。
- 不为了覆盖更多问题而让 description 失去触发边界。
- 对核心流程、默认输出或分类体系的修改，必须说明兼容性影响。

## 版本判断

`VERSION` 和 `PLUGIN_VERSION` 是独立版本：

- Core Skill 修改按以下规则更新 `VERSION`，并同步 Skill metadata 与 `evals.json` version；
- Plugin-only 修改只按 wrapper 兼容性更新 `PLUGIN_VERSION` 和 canonical manifest source，不强制提升 Core Skill version；
- Core Skill 修改时必须评估是否需要同步提升 Plugin version 并重新验证包装。

Core Skill version 等级仅适用于 Core Skill release 或 Combined release；Plugin-only release 的 Core version 判断记录为 `N/A — Core Skill version unchanged.`：

- `PATCH`：Core Skill 文档、validator、eval 修正，或恢复已承诺行为且不扩大触发范围或输出契约。
- `MINOR`：向后兼容的新分析能力、新维度，或明显扩大但仍兼容的触发或输出能力。
- `MAJOR`：改变核心七步流程、分类体系、默认行为契约，或产生不兼容的触发或输出变化。

仅增加回归案例但不改变行为时，应跟随对应修复版本发布，不应只为了增加版本数字而单独发版。

## Pull Request 应包含

- 对应 Issue、真实失败案例或维护问题；
- eval ID；不涉及 Skill 行为时可填写 `N/A` 并说明原因；
- 基线版本和目标版本；
- Core Skill version 和 Plugin version；
- 行为变更的旧版失败、候选版改善和旧新版对比结果，或非行为维护变更的验证证据；
- 是否改变核心七步流程、触发范围或默认输出契约；
- PATCH、MINOR 或 MAJOR 的版本建议；
- validator、适用测试和 Changelog 检查结果。
