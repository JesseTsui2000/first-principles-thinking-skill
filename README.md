# First Principles Thinking Skill

一个通用的 Agent Skill，用工程化的第一性原理方法审查产品、工程、商业、工作流和复杂决策问题。

方法本身不限定用户所在地区或应用领域。当前 `v0.1.x` 的 Skill 指令、主要文档和评测案例以简体中文编写。

它不会把“第一性原理”理解为无条件反传统，而是要求先区分：

- 真实目标与现有手段
- 硬约束与行业惯例
- 已验证事实与未经验证假设
- 理论可行与现实可行
- 创新收益与新增风险

当前版本：`v0.1.1`

## 适合解决什么

- 行业主要用“历来如此”解释的问题
- 成本、耗时或系统复杂度异常高的问题
- 目标与手段可能倒置的产品和工作流
- 需要结构性重构，而非局部优化的方案
- 多种意见冲突，需要回到底层事实的决策

它不用于替代成熟安全标准、专业诊断，或为简单任务强行制造“颠覆性方案”。

## 仓库结构

```text
first-principles-thinking-skill/
├── skills/
│   └── first-principles-thinking/
│       ├── SKILL.md
│       └── evals/
│           ├── README.md
│           └── evals.json
├── tools/
│   └── validate_repo.py
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── workflows/
│   └── pull_request_template.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── PUBLISHING.md
├── RELEASE_CHECKLIST.md
├── VERSION
└── README.md
```

## 安装

仓库公开发布后，可使用 Skills CLI 安装：

```bash
npx skills add JesseTsui2000/first-principles-thinking-skill --skill first-principles-thinking
```

安装到指定 Agent：

```bash
npx skills add JesseTsui2000/first-principles-thinking-skill   --skill first-principles-thinking   --agent claude-code   --agent codex   --agent cursor
```

也可以不安装，直接复制：

```text
skills/first-principles-thinking/
```

到目标 Agent 支持的 Skills 目录。

## 使用方式

完整调用：

```text
请使用 first-principles-thinking Skill 分析以下问题：

[问题或方案]

重点判断：
[最关心的目标、成本、风险或假设]

已知限制：
[预算、周期、团队、法律、安全、工具等]
```

简化调用：

```text
用第一性原理审查这个方案。不要默认它成立，先区分目标、事实、硬约束、当前条件、惯例和未经验证的假设，再给出重构方案与最低成本验证。
```

## 示例

输入：

```text
用第一性原理审查：AI 剪辑软件是否应该直接生成完整成片？
```

理想行为包括：

1. 先定义用户真正需要减少的工作；
2. 不把“完整自动成片”直接当成产品目标；
3. 拆解素材整理、选取、排序、节奏和审美判断；
4. 区分可测量机械任务与高不确定性的审美任务；
5. 给出最小可行产品和验证方式；
6. 明确模型能力、数据、集成和采用风险。

## 版本与更新

本项目使用语义化版本：

- `PATCH`：修复表达、误触发或局部行为；
- `MINOR`：增加兼容能力或分析维度；
- `MAJOR`：改变核心流程或产生明显不兼容行为。

正式版本以 Git tag 和 GitHub Release 为准。每次修改前，优先把真实失败案例加入 `evals/evals.json`，再修改 Skill 并运行回归检查。

## 本地验证

需要 Python 3，无第三方依赖：

```bash
python3 tools/validate_repo.py
```

验证内容包括：

- Skill 目录与名称是否匹配；
- YAML frontmatter 必填字段；
- 描述与名称长度；
- `VERSION` 与 Skill metadata 是否一致；
- eval JSON 是否有效；
- 必要维护文件是否存在。

GitHub Actions 会在 push 和 pull request 时自动运行同一检查。

## 反馈与贡献

请优先提交能够复现的问题：

- 不应该触发却触发；
- 应该触发却没有触发；
- 把惯例误判为硬约束；
- 无证据地推翻专业知识；
- 过度还原人类或社会问题；
- 输出过长、空泛或不可验证；
- 新版本相较旧版本出现退化。

详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## License

MIT License。详见 [LICENSE](LICENSE)。

---

English summary: A general-purpose Agent Skill for first-principles analysis of products, engineering, business models, workflows, and complex decisions. The methodology is language-agnostic; the current v0.1.x implementation, documentation, and evals are primarily written in Simplified Chinese.
