# Release Checklist

## A. 发布 PR 前

- [ ] 当前位于正确的短生命周期工作分支，未直接向 `main` 开发
- [ ] 已记录对应 Issue、问题或维护缺口
- [ ] 已判断是否影响 Skill 行为、触发范围或输出契约

### 若影响 Skill 行为

- [ ] 已记录可复现的真实失败案例
- [ ] 行为变更所需 eval 已增加或更新
- [ ] 已使用最新稳定版复现并记录行为和失败
- [ ] 已使用相同输入完成稳定版与候选版行为对比

### 若不影响 Skill 行为

- [ ] eval ID 和行为对比已标为 `N/A`，并说明原因
- [ ] 已完成适当的静态验证、负向测试或文档审查

### 通用检查

- [ ] 已检查候选版没有意外改变 Skill 核心行为
- [ ] 已判断 PATCH、MINOR 或 MAJOR
- [ ] `VERSION`、`SKILL.md` 的 `metadata.version`、`evals.json` 的 `version` 一致
- [ ] README 当前版本与 `VERSION` 一致
- [ ] `CHANGELOG.md` 包含当前版本条目
- [ ] `python3 tools/validate_repo.py` 通过
- [ ] `git diff --check` 通过
- [ ] 发布 PR 的 GitHub Actions 已通过

## B. 合并和发版

- [ ] 发布 PR 已合并到 `main`
- [ ] 合并后 `main` 的 GitHub Actions 已通过
- [ ] 本地 `main`、`origin/main`、`HEAD` 指向同一发布 commit
- [ ] 已创建新的 annotated tag
- [ ] tag 指向发布后的 `main` commit
- [ ] 已推送 tag
- [ ] GitHub Release 对应同一 tag
- [ ] Release notes 与 Changelog 一致
- [ ] 未移动、覆盖、复用或删除任何旧 tag

## C. 发布后

- [ ] 已测试公开仓库能够识别 `first-principles-thinking`
- [ ] 已执行 `npx skills update first-principles-thinking -g`
- [ ] 已检查 `~/.agents/skills/first-principles-thinking` 中的版本
- [ ] 已检查仓库与安装副本的内容哈希
- [ ] 已显式读取并确认安装版本

### Skill 核心行为发生变化

- [ ] 已在 Codex App 完成显式调用测试
- [ ] 已在 Codex App 完成隐式触发测试
- [ ] 已在 Codex App 完成简单任务边界测试

### 纯维护改动

- [ ] 已完成公开识别、安装版本和显式读取的最小复验
- [ ] 隐式触发和简单任务边界已执行，或已标记为 `N/A` 并说明原因

### 收尾

- [ ] 已检查工作区干净
- [ ] 已删除本地和远程工作分支
- [ ] 已确认 `main` 不含待发布内容
