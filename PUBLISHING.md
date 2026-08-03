# Maintenance and Publishing Guide

本文档定义 `first-principles-thinking` Core Skill 及其平台包装层的长期维护与发布流程。

## 发布对象与不变量

- GitHub `main` 是唯一公开、稳定、可安装的内容源。
- annotated tag 是 Core Skill 的不可变版本标识，必须指向对应版本合并后的 `main` commit。
- GitHub Release 是对应 tag 的发布记录和说明，二者必须一一对应。
- 已发布 tag 不得移动、覆盖、复用或删除。
- 所有修改必须在短生命周期工作分支完成；不得直接向 `main` 开发，也不得在 `main` 长期保留未发布改动。
- Core Skill 发布 PR 合并到 `main` 后，必须在同一个发布流程中立即创建 tag 和 GitHub Release。

## 多制品版本模型

- `VERSION` 表示 Core Skill version，并与 `SKILL.md` metadata、`evals.json` version 保持一致。
- `PLUGIN_VERSION` 表示 OpenAI Plugin wrapper version，并与 `packaging/openai-plugin/plugin.json` version 保持一致；generated manifest 必须与 canonical source 逐字节一致。
- 两个版本独立演进。Plugin-only 文件、validator 或本地 marketplace 维护不得强制提升 Core Skill version。
- Core Skill 发生变化时，必须评估 Plugin wrapper 是否需要新版本，以及是否需要重新执行本地打包和平台测试。
- 平台 wrapper 只引用核心 Skill，不能复制核心指令，也不能成为触发契约、分析流程或输出结构的新事实源。

当前本地包装关系是 Plugin `0.1.0` bundles Core Skill `0.1.2`。Directory branding assets、可选的 interface listing URLs、Portal metadata、publisher verification、availability 以及正式提交属于后续独立阶段。

## Plugin packaging 边界

Canonical sources 是 `skills/first-principles-thinking/SKILL.md`、`packaging/openai-plugin/plugin.json`、`VERSION`、`PLUGIN_VERSION` 和 `plugin-submission/test-cases.json`。

Clean build 输出固定为 `.build/plugins/first-principles-thinking/`，只包含 `.codex-plugin/plugin.json` 和 `skills/first-principles-thinking/SKILL.md`。`.build/` 是 ignored generated output，不允许人工编辑或提交；其中的 Skill 只是构建副本，不是第二份事实源。

构建和只读检查命令：

```bash
python3 tools/build_openai_plugin.py
python3 tools/build_openai_plugin.py --check
```

Repo-local marketplace 指向完整 generated Plugin root；fresh clone 后必须先运行 build。仓库根 compatibility manifest 必须保持不存在。

Skills-only Portal submission 使用 ZIP。ZIP 必须包含 supported Plugin manifest 和至少一个 bundled Skill；Plugin root 可以直接位于 archive root，或位于唯一顶层目录且不得有 sibling files。当前 generated directory 是未来 ZIP 的 Plugin root，但本阶段不生成 ZIP。Directory submission readiness 为 `NOT ASSESSED`；branding assets 和 Portal metadata 推迟到 Portal preflight，skills-only interface listing URLs 为可选。

## Core Skill Copy 安装

全局安装采用 Copy，是与仓库相互独立的副本，不会自动跟随仓库变化。

禁止直接编辑：

```text
~/.agents/skills/first-principles-thinking
```

Core Skill release 应进入仓库工作分支，经验证和发布后再通过 Skills CLI 更新：

```bash
npx skills update first-principles-thinking -g
```

更新后必须检查安装版本。若 `SKILL.md` 核心行为发生变化，还必须在 Codex App 中重新执行显式调用、隐式触发和简单任务边界测试；不改变行为的 Core Skill release 可以采用最小复验，但至少必须显式读取并确认安装版本。Plugin-only maintenance/release 不执行 Skills CLI Core Skill 更新。

## 完整维护与发布闭环

```text
真实失败案例、维护问题或发行流程缺口
→ Issue 或可追溯记录
→ 工作分支
→ 判断是否影响 Skill 行为
→ 若影响行为：增加 eval、复现稳定版、完成旧新版行为对比
→ 若不影响行为：记录 N/A 理由并完成适当的静态或负向验证
→ 分别判断 Core Skill version 与适用的平台包装版本
→ 发布 PR
→ 合并 main
→ 若为 Core Skill release 或 Combined release：Core annotated tag、GitHub Release、Skills CLI 更新和适用的 Codex App 复验
→ 若为 Plugin-only release：Plugin Directory 验证及 wrapper/Portal 映射记录；Core tag、Core GitHub Release、Skills CLI Core 更新均为 N/A
→ 删除工作分支
```

### 1. 从问题或缺口开始

入口可以是 Skill 行为失败案例，也可以是文档、validator、CI、安装或发行流程问题。每项修改都应关联 Issue 或其他可追溯记录，并先判断是否影响 Skill 行为、触发范围或输出契约。

- 涉及 Skill 行为、触发范围或输出契约时，eval、稳定版复现和模型行为对比是强制项。
- 不涉及 Skill 行为时，不得为了满足形式而修改无关 eval 或进行无意义的模型行为对比；应在 PR 中将 eval ID 和行为对比标为 `N/A`、解释原因，并提供适当的静态验证、负向测试或文档审查证据。

### 2. 使用短生命周期工作分支

从最新 `main` 创建工作分支：

```bash
git switch main
git pull --ff-only
BRANCH_NAME=codex/example-change
git switch -c "$BRANCH_NAME"
```

只提交与对应问题、修复、验证和必要发布文档相关的改动。

### 3. 条件式验证和版本判断

行为变更应使用相同输入对比稳定版与候选版，记录旧版行为、候选版行为及退化风险。非行为维护变更应根据改动性质执行静态验证、负向测试或文档审查，并记录 `N/A` 理由。Core Skill 变更必须依据 [CONTRIBUTING.md](CONTRIBUTING.md) 判断 PATCH、MINOR 或 MAJOR，并同步 Core Skill 版本文件与 Changelog；Plugin-only 变更只同步 `PLUGIN_VERSION`、manifest 和对应包装记录。

发布 PR 前运行：

```bash
python3 tools/validate_repo.py
python3 tools/build_openai_plugin.py
python3 tools/build_openai_plugin.py --check
git diff --check
```

同时按 [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) 完成发布前检查。

发布 PR 的 GitHub Actions 未通过时不得合并。

### 4. 合并和发布

发布 PR 通过审查且 GitHub Actions 通过后合并到 `main`。合并后的 `main` GitHub Actions 必须通过，再根据 release type 进入对应流程。

#### 4A. Core Skill release / Combined release

以下任一情况适用 Core Skill release：`VERSION` 改变，`SKILL.md` 核心行为或 `metadata.version` 改变，核心 `evals.json` version 改变，或正式发布新的 Core Skill version。Combined release 同时包含 Core Skill release 和 Plugin release。

确认本地 `main`、`origin/main` 与 `HEAD` 指向同一发布 commit：

```bash
git switch main
git pull --ff-only
git rev-parse HEAD
git rev-parse main
git rev-parse origin/main
```

读取实际 Core Skill version，创建并推送新的 annotated tag：

```bash
RELEASE_VERSION=$(tr -d '\n' < VERSION)
git tag -a "v$RELEASE_VERSION" -m "first-principles-thinking v$RELEASE_VERSION"
git show --no-patch --decorate "v$RELEASE_VERSION"
git push origin "v$RELEASE_VERSION"
```

随后立即创建对应同一 tag 的 GitHub Release，Release notes 应与该版本 Changelog 一致。

#### 4B. Plugin-only maintenance / release

仅改变 manifest、marketplace、Plugin wrapper、Plugin submission tests、Portal listing、Plugin 文档、Plugin validator、logo、website、support、privacy、terms 或其他平台适配，且不改变 Core Skill 行为和 Core version 时，属于 Plugin-only maintenance/release。

Plugin-only 流程不得提升 `VERSION`，不得修改 Skill `metadata.version` 或核心 `evals.json` version，不得创建或复用 Core `vX.Y.Z` tag，不得创建新的 Core GitHub Release，也不得执行 Skills CLI Core Skill 更新。

Plugin-only 流程必须记录：Plugin version、bundled Core Skill version、Git commit、Core Skill SHA-256、Portal submission/revision ID、Published URL 和本地 Plugin Directory 验证结果。尚未产生的 Portal ID 或 Published URL 应明确记录为 pending，不能捏造。

是否采用独立的 `plugin-vX.Y.Z` Git tag 尚未决定。首次公开 Plugin 发布前应单独决策；在此之前以 Plugin manifest version、commit SHA 和 Portal revision 建立映射，不把 Plugin-specific Git tag 作为强制流程。

### 5. Core Skill 发布后更新和复验

先测试公开仓库可识别该 Skill，再更新全局 Copy 安装：

```bash
npx skills add JesseTsui2000/first-principles-thinking-skill --list
npx skills update first-principles-thinking -g
```

即使是不改变行为的 Core Skill release，也必须检查公开仓库识别、安装副本版本，以及仓库与安装副本的内容哈希。本节不适用于 Plugin-only release。

若 `SKILL.md` 核心行为发生变化，必须在 Codex App 完成显式调用、隐式触发和简单任务边界三项复验。纯维护文档版本可以执行最小复验：至少显式读取安装版本，隐式触发和简单任务边界可标记为 `N/A` 并解释原因。若某个纯维护版本已经计划完整执行三项测试，也可以全部执行。

适用检查全部通过后，删除本地和远程工作分支，并确认 `main` 干净且不含待发布内容。

```bash
BRANCH_NAME=codex/example-change
git branch -d "$BRANCH_NAME"
git push origin --delete "$BRANCH_NAME"
```

## OpenAI Plugin wrapper 本地维护

本地包装阶段只允许：

1. 更新 canonical manifest source、`PLUGIN_VERSION`、适用的 repo-local marketplace、submission golden set 和维护文档；
2. 运行 repository validator、clean builder、package `--check`、JSON、路径、版本、唯一 Skill 和隔离负向验证；
3. 记录 Plugin version、bundled Core Skill version、Git commit、Core Skill SHA-256，以及实际产生后的 Portal submission/revision ID、Published URL 和本地 Plugin Directory 验证结果。

不得把 submission golden set 写回核心 eval，不得直接修改用户级 Plugin/Skill 安装，不得人工编辑 `.build`。本地 marketplace 的桌面端安装验证、Portal submission/revision ID 和 Published URL 只有在对应后续阶段实际产生后才能记录。

`plugin-creator` validator 只用于验证最终生成 package，不得改写 canonical manifest 或 Core Skill，也不得为此安装项目依赖或修改系统 Python。

## 失败停止条件

出现以下任一情况时必须停止发布，修复并重新验证，不得绕过：

- repository validator 或相关回归检查失败；
- 行为变更的旧新版对比无法证明修复，或出现未解释的退化；
- 非行为维护变更缺少适当的静态验证、负向测试或文档审查；
- 发布 PR 或合并后 `main` 的 GitHub Actions 未通过；
- Core Skill 版本文件、Plugin wrapper 版本文件、README 或 Changelog 不一致；
- `main`、`origin/main`、`HEAD` 不一致；
- 适用 Core Skill release 时，tag 已存在、类型不是 annotated tag，或未指向发布后的 `main` commit；
- 适用 Core Skill release 时，GitHub Release 与 tag 不一致；
- 适用 Core Skill release 时，Skills CLI 无法更新 Copy 安装副本，或安装版本、哈希不符合预期；
- 适用的 Codex App 复验失败。

失败时不得移动或覆盖旧 tag，也不得通过直接编辑全局安装副本补救。
