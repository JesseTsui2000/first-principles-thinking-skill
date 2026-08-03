# First Principles Thinking Skill

一个通用的 Agent Skill，用工程化的第一性原理方法审查产品、工程、商业、工作流和复杂决策问题。

方法本身不限定用户所在地区或应用领域。当前 `v0.1.x` 的 Skill 指令、主要文档和评测案例以简体中文编写。

它不会把“第一性原理”理解为无条件反传统，而是要求先区分：

- 真实目标与现有手段
- 硬约束与行业惯例
- 已验证事实与未经验证假设
- 理论可行与现实可行
- 创新收益与新增风险

当前版本：`v0.1.2`

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
├── .agents/
│   └── plugins/
│       └── marketplace.json
├── .build/                          # ignored generated output
│   └── plugins/
│       └── first-principles-thinking/
├── packaging/
│   └── openai-plugin/
│       └── plugin.json              # canonical Plugin manifest source
├── skills/
│   └── first-principles-thinking/
│       ├── SKILL.md
│       └── evals/
│           ├── README.md
│           └── evals.json
├── tools/
│   ├── build_openai_plugin.py
│   └── validate_repo.py
├── plugin-submission/
│   └── test-cases.json
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── workflows/
│   └── pull_request_template.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── PUBLISHING.md
├── OPENAI_PLUGIN.md
├── PLUGIN_VERSION
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

### OpenAI Plugin 本地包装

Plugin wrapper 的 canonical manifest source 是 `packaging/openai-plugin/plugin.json`；核心 Skill 的 canonical source 仍是 `skills/first-principles-thinking/SKILL.md`。两者与 `VERSION`、`PLUGIN_VERSION`、`plugin-submission/test-cases.json` 构成包装阶段的受版本控制输入。

生成本地 Plugin root：

```bash
python3 tools/build_openai_plugin.py
python3 tools/build_openai_plugin.py --check
```

固定输出位于 `.build/plugins/first-principles-thinking/`，只包含 manifest 和 canonical Skill 的 ignored copy。`.build` 不得人工编辑或提交，生成的 `SKILL.md` 也不是第二份事实源。仓库根不再包含 compatibility manifest。

本地 marketplace 位于 `.agents/plugins/marketplace.json`，其 `source.path` 指向上述 generated Plugin root；fresh clone 后必须先运行 build。generated Plugin 已完成本地安装，并通过 exact two-file cache audit；本轮不重装 Plugin，也不修改 Plugin cache。

Skills-only Portal 提交使用 ZIP；ZIP 必须包含 supported Plugin manifest 和至少一个 bundled Skill。Plugin root 可以直接位于 archive root，或位于唯一顶层目录且不得有 sibling files。当前生成目录是未来 ZIP 的 Plugin root，但现阶段不生成 ZIP。Directory submission readiness 为 `NOT ASSESSED`：`interface.logo`、`interface.composerIcon`、Portal metadata、publisher verification、submission ZIP、upload/final scans 和 public directory publication 均尚未完成；skills-only package 的 interface listing URLs 为可选。详细边界见 [OPENAI_PLUGIN.md](OPENAI_PLUGIN.md)。

现有包装已经完成 canonical manifest、deterministic builder、repository/package validation、`plugin-creator` ingestion validation、本地安装、exact two-file cache audit、positive activation、simple-task non-activation 和 privacy audit。

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

本项目维护两个独立的语义化版本：

- `VERSION`：Core Skill version；
- `PLUGIN_VERSION`：OpenAI Plugin wrapper version。

Plugin-only 维护不会强制提升 Core Skill version。Core Skill 更新时，应评估是否需要同步发布新的 Plugin wrapper，以便重新验证打包和平台行为。

Core Skill 版本规则：

- `PATCH`：修复表达、误触发或局部行为；
- `MINOR`：增加兼容能力或分析维度；
- `MAJOR`：改变核心流程或产生明显不兼容行为。

GitHub `main` 是唯一公开、稳定、可安装的内容源。Core Skill 的 `vX.Y.Z` tag 和对应 GitHub Release 是不可变的发布记录；Plugin-only release 不创建或复用 Core tag。

Copy 安装是独立副本，不会自动跟随仓库变化。禁止直接修改 `~/.agents/skills/first-principles-thinking`；新版本发布后应主动更新：

```bash
npx skills update first-principles-thinking -g
```

涉及 Skill 行为、触发范围或输出契约时，应先将真实失败案例加入 eval。纯文档、工具或发布流程维护应记录对应问题，并完成适当的静态或负向验证。详细维护与发布政策见 [PUBLISHING.md](PUBLISHING.md)。

## 本地验证

需要 Python 3，无第三方依赖：

```bash
python3 tools/validate_repo.py
python3 tools/build_openai_plugin.py
python3 tools/build_openai_plugin.py --check
```

验证内容包括：

- Skill 目录与名称是否匹配；
- YAML frontmatter 必填字段；
- 描述与名称长度；
- `VERSION` 与 Skill metadata 是否一致；
- `PLUGIN_VERSION` 与 Plugin manifest version 是否一致；
- canonical Plugin manifest、repo-local marketplace 和 submission golden set 是否有效；
- generated package 是否只有 allowlist 中的两个普通文件、内容是否最新且没有 symlink；
- `.build` 是否被 ignore 且没有 tracked 文件，仓库根 manifest 是否保持不存在；
- source 中是否只有一份 canonical `SKILL.md`；
- eval JSON 是否有效；
- 必要维护文件是否存在。

Validator 分别报告 repository 和 local generated package 状态。fresh clone 在尚未 build 时 repository validation 可以通过；build 后必须同时通过 package `--check`。Directory submission readiness 固定报告 `NOT ASSESSED`，directory assets 和 Portal metadata 留到 Portal submission 阶段评估。

GitHub Actions 会在 fresh checkout 中运行 source validation、两次 clean build、package `--check`、文件清单/SHA/逐字节可重现性比较，并确认构建未改变 tracked source 或 Git status。

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
