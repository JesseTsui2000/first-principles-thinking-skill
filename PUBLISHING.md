# Maintenance and Publishing Guide

本文档定义 `first-principles-thinking` 的长期维护与发布流程。

## 发布对象与不变量

- GitHub `main` 是唯一公开、稳定、可安装的内容源。
- annotated tag 是不可变的版本标识，必须指向对应版本合并后的 `main` commit。
- GitHub Release 是对应 tag 的发布记录和说明，二者必须一一对应。
- 已发布 tag 不得移动、覆盖、复用或删除。
- 所有修改必须在短生命周期工作分支完成；不得直接向 `main` 开发，也不得在 `main` 长期保留未发布改动。
- 发布 PR 合并到 `main` 后，必须在同一个发布流程中立即创建 tag 和 GitHub Release。

## 安装副本

全局安装采用 Copy，是与仓库相互独立的副本，不会自动跟随仓库变化。

禁止直接编辑：

```text
~/.agents/skills/first-principles-thinking
```

所有改动都应进入仓库工作分支，经验证和发布后再通过 Skills CLI 更新：

```bash
npx skills update first-principles-thinking -g
```

更新后必须检查安装版本。若 `SKILL.md` 核心行为发生变化，还必须在 Codex App 中重新执行显式调用、隐式触发和简单任务边界测试；纯维护版本可以采用最小复验，但至少必须显式读取并确认安装版本。

## 完整维护与发布闭环

```text
真实失败案例、维护问题或发行流程缺口
→ Issue 或可追溯记录
→ 工作分支
→ 判断是否影响 Skill 行为
→ 若影响行为：增加 eval、复现稳定版、完成旧新版行为对比
→ 若不影响行为：记录 N/A 理由并完成适当的静态或负向验证
→ 版本判断
→ 发布 PR
→ 合并 main
→ annotated tag
→ GitHub Release
→ Skills CLI 更新
→ Codex App 复验（仅适用部分）
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
git switch -c <short-lived-branch>
```

只提交与对应问题、修复、验证和必要发布文档相关的改动。

### 3. 条件式验证和版本判断

行为变更应使用相同输入对比稳定版与候选版，记录旧版行为、候选版行为及退化风险。非行为维护变更应根据改动性质执行静态验证、负向测试或文档审查，并记录 `N/A` 理由。两类修改都必须依据 [CONTRIBUTING.md](CONTRIBUTING.md) 判断 PATCH、MINOR 或 MAJOR，并同步所有版本文件与 Changelog。

发布 PR 前运行：

```bash
python3 tools/validate_repo.py
git diff --check
```

同时按 [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) 完成发布前检查。

发布 PR 的 GitHub Actions 未通过时不得合并。

### 4. 合并和发布

发布 PR 通过审查且 GitHub Actions 通过后合并到 `main`。合并后的 `main` GitHub Actions 必须通过；否则不得创建或继续发布 tag 和 GitHub Release。

确认本地 `main`、`origin/main` 与 `HEAD` 指向同一发布 commit：

```bash
git switch main
git pull --ff-only
git rev-parse HEAD
git rev-parse main
git rev-parse origin/main
```

用实际版本替换占位符，创建并推送新的 annotated tag：

```bash
git tag -a "v<VERSION>" -m "first-principles-thinking v<VERSION>"
git show --no-patch --decorate "v<VERSION>"
git push origin "v<VERSION>"
```

随后立即创建对应同一 tag 的 GitHub Release，Release notes 应与该版本 Changelog 一致。

### 5. 发布后更新和复验

先测试公开仓库可识别该 Skill，再更新全局 Copy 安装：

```bash
npx skills add JesseTsui2000/first-principles-thinking-skill --list
npx skills update first-principles-thinking -g
```

即使是非行为维护版本，也必须检查公开仓库识别、安装副本版本，以及仓库与安装副本的内容哈希。

若 `SKILL.md` 核心行为发生变化，必须在 Codex App 完成显式调用、隐式触发和简单任务边界三项复验。纯维护文档版本可以执行最小复验：至少显式读取安装版本，隐式触发和简单任务边界可标记为 `N/A` 并解释原因。若某个纯维护版本已经计划完整执行三项测试，也可以全部执行。

适用检查全部通过后，删除本地和远程工作分支，并确认 `main` 干净且不含待发布内容。

```bash
git branch -d <short-lived-branch>
git push origin --delete <short-lived-branch>
```

## 失败停止条件

出现以下任一情况时必须停止发布，修复并重新验证，不得绕过：

- repository validator 或相关回归检查失败；
- 行为变更的旧新版对比无法证明修复，或出现未解释的退化；
- 非行为维护变更缺少适当的静态验证、负向测试或文档审查；
- 发布 PR 或合并后 `main` 的 GitHub Actions 未通过；
- 版本文件、README 或 Changelog 不一致；
- `main`、`origin/main`、`HEAD` 不一致；
- tag 已存在、类型不是 annotated tag，或未指向发布后的 `main` commit；
- GitHub Release 与 tag 不一致；
- Skills CLI 无法更新 Copy 安装副本，或安装版本、哈希不符合预期；
- 适用的 Codex App 复验失败。

失败时不得移动或覆盖旧 tag，也不得通过直接编辑全局安装副本补救。
