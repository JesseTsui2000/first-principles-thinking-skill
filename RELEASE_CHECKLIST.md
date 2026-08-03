# Release Checklist

## Release type

- [ ] Core Skill release
- [ ] Plugin-only release
- [ ] Combined release

必须且只能选择一种。Plugin-only release 中，Core Skill version、Core tag、Core GitHub Release、Skills CLI Core update、Core Skill 行为对比和核心 eval 修改均记录为：`N/A — Core Skill version unchanged.`；Plugin 安装和 wrapper 验证不能标记为 `N/A`。

## A. 发布 PR 前

- [ ] 当前位于正确的短生命周期工作分支，未直接向 `main` 开发
- [ ] 已记录对应 Issue、问题或维护缺口
- [ ] 已判断是否影响 Skill 行为、触发范围或输出契约

### 若影响 Skill 行为

- [ ] 已记录可复现的真实失败案例
- [ ] 行为变更所需 eval 已增加或更新
- [ ] 已使用最新稳定版复现并记录行为和失败
- [ ] 已使用相同输入完成稳定版与候选版行为对比

Plugin-only release：`N/A — Core Skill version unchanged.`

### 若不影响 Skill 行为

- [ ] eval ID 和行为对比已标为 `N/A`，并说明原因
- [ ] 已完成适当的静态验证、负向测试或文档审查
- [ ] Plugin-only release 的核心 eval 修改：`N/A — Core Skill version unchanged.`

### 通用检查

- [ ] 已检查候选版没有意外改变 Skill 核心行为
- [ ] Core Skill/Combined release 已判断 Core PATCH、MINOR 或 MAJOR；Plugin-only release 记为 `N/A — Core Skill version unchanged.`
- [ ] `VERSION`、`SKILL.md` 的 `metadata.version`、`evals.json` 的 `version` 一致
- [ ] README 当前版本与 `VERSION` 一致
- [ ] `CHANGELOG.md` 包含当前版本条目
- [ ] 已分别判断 Core Skill version 和适用的平台包装版本
- [ ] `PLUGIN_VERSION` 与 canonical Plugin manifest source version 一致
- [ ] 仓库根 `.codex-plugin/plugin.json` 不存在
- [ ] Plugin wrapper 只引用现有核心 Skill，没有第二份 `SKILL.md`
- [ ] `python3 tools/validate_repo.py` 通过
- [ ] `python3 tools/build_openai_plugin.py` 通过
- [ ] `python3 tools/build_openai_plugin.py --check` 通过
- [ ] `git diff --check` 通过
- [ ] 发布 PR 的 GitHub Actions 已通过

### OpenAI Plugin wrapper 本地包装

- [ ] canonical sources、generated package 和 release/submission material 边界已记录
- [ ] `.build/` 已被 ignore，生成物不会人工编辑或纳入版本控制
- [ ] package 仅含 `.codex-plugin/plugin.json` 和 `skills/first-principles-thinking/SKILL.md` 两个普通文件
- [ ] 两次 clean build 的文件清单、SHA 和逐字节内容一致
- [ ] manifest name、version 和 `skills: "./skills/"` 已验证
- [ ] repo-local marketplace JSON 和路径边界已验证
- [ ] marketplace 精确指向 `./.build/plugins/first-principles-thinking`
- [ ] submission golden set 至少包含 5 个正向和 3 个负向测试
- [ ] 核心 `SKILL.md` 和 `evals.json` 无 diff
- [ ] 已记录 Core Skill version、Plugin version 和 Core Skill SHA-256
- [ ] 已记录 bundled Core Skill version、Git commit、本地 Plugin Directory 验证结果，以及实际产生后的 Portal submission/revision ID 和 Published URL
- [ ] 未修改用户级 Plugin/Skill 配置
- [ ] Plugin Directory 人工安装若不属于当前阶段，已明确留待后续验证
- [ ] Skills-only Portal ZIP 结构包含 manifest 和至少一个 bundled Skill；唯一顶层目录模式下没有 sibling files
- [ ] Directory submission readiness 报告为 `NOT ASSESSED`，directory assets 和 Portal metadata 留到 submission 阶段评估
- [ ] ZIP 自动生成留到 Portal preflight，未把当前 generated directory 误称为可直接提交的 ZIP
- [ ] `plugin-creator` validator 仅针对最终生成 package 运行，且不会安装项目依赖或修改系统 Python

## B. 合并和发版

- [ ] 发布 PR 已合并到 `main`
- [ ] 合并后 `main` 的 GitHub Actions 已通过

### Core Skill release / Combined release

- [ ] 本地 `main`、`origin/main`、`HEAD` 指向同一发布 commit
- [ ] 已创建新的 Core `vX.Y.Z` annotated tag
- [ ] Core tag 指向发布后的 `main` commit
- [ ] 已推送 Core tag
- [ ] Core GitHub Release 对应同一 tag
- [ ] Release notes 与 Changelog 一致
- [ ] 未移动、覆盖、复用或删除任何旧 tag

### Plugin-only release

- [ ] Core tag：`N/A — Core Skill version unchanged.`
- [ ] Core GitHub Release：`N/A — Core Skill version unchanged.`
- [ ] 未创建或复用现有 Core tag
- [ ] 已记录 Plugin manifest version、commit SHA 和适用的 Portal revision 映射
- [ ] 独立 `plugin-vX.Y.Z` tag 未被视为强制流程；首次公开发布前另行决策

## C. 发布后

### Core Skill release / Combined release

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

### Plugin-only release

- [ ] Skills CLI Core update：`N/A — Core Skill version unchanged.`
- [ ] 已完成 Plugin Directory 安装测试和 wrapper 验证，不得标记为 `N/A`
- [ ] 已记录 Plugin version、bundled Core Skill version、Git commit 和 Core Skill SHA-256
- [ ] 已记录实际产生的 Portal submission/revision ID 和 Published URL；尚未产生时明确标记 pending

### 收尾

- [ ] 已检查工作区干净
- [ ] 已删除本地和远程工作分支
- [ ] 已确认 `main` 不含待发布内容
