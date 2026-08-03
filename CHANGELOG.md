# Changelog

本项目的重要变化记录在此文件中。

格式参考 Keep a Changelog，版本号采用 Semantic Versioning。

## [Unreleased]

### Added

- 首次引入 OpenAI skills-only Plugin wrapper `v0.1.0`，bundles Core Skill `v0.1.2`。
- 增加 canonical Plugin manifest source `packaging/openai-plugin/plugin.json`。
- 增加 repo-local marketplace，指向 `.build/plugins/first-principles-thinking` generated Plugin root。
- 增加仅使用 Python 标准库的 clean builder，以及不产生写入的 generated package `--check`。
- 增加 `.build` Plugin package ignore 规则和仅允许 manifest、canonical Skill copy 两个普通文件的 allowlist。

### Changed

- 扩展 repository validator，分别报告 source repository 和 local generated package，并将 directory submission readiness 准确标记为 `NOT ASSESSED`。
- 修正 Skills-only Portal 提交说明：使用同时包含 supported Plugin manifest 和至少一个 bundled Skill 的 ZIP；当前 generated directory 是未来 ZIP 的 Plugin root。
- 记录已完成 canonical manifest、deterministic builder、repository/package validation、`plugin-creator` ingestion validation、本地安装、exact two-file cache audit、positive activation、simple-task non-activation 和 privacy audit。
- 明确本次 Core Skill 内容、行为和版本均未变化；仓库根保持不存在 compatibility `.codex-plugin/plugin.json`，本轮不重装 Plugin 或进行 Portal submission。

### Fixed

- 将 `interface.category` 修正为官方枚举值 `Productivity`，并增加小写 `productivity` 拒绝检查。
- 将 `interface.shortDescription` 修正为 `First-principles analysis`，并执行最终目录的 listing 字段长度限制。
- 移除错误的顶层 Portal 必填字段和 Portal-ready 判断；skills-only listing URLs 不再被报告为缺失错误。
- 更新实际提交边界：directory branding assets、Portal metadata/publisher verification、submission ZIP、Portal upload/final scans 和 public directory publication 尚未完成。

### Removed

## [0.1.2] - 2026-07-31

### Changed

- 重写维护与发布工作流。
- 明确 `main`、tag、GitHub Release 的关系。
- 增加 Copy 安装更新和 Codex App 发布后验证。
- 加强 release checklist 和 PR 模板。
- 增加 README、Changelog 和 eval README 的 validator 检查。
- 区分 Skill 行为变更与非行为维护变更的验证要求。

## [0.1.1] - 2026-07-30

### Changed

- 明确该 Skill 的方法本身适用于通用、全球化场景，而不是仅面向中文用户。
- 更新 README 的中文定位说明与英文摘要。
- 如实说明当前 `v0.1.x` 的指令、主要文档和评测案例仍以简体中文编写。
- 将 `VERSION`、`SKILL.md` metadata 和 `evals.json` 版本统一更新为 `0.1.1`。

## [0.1.0] - 2026-07-25

### Added

- 首个公开测试版 Skill。
- 增加启动判断，允许明确得出“不需要第一性原理重构”。
- 增加目标、前提、拆解、瓶颈、重构和验证的七步流程。
- 增加硬约束、已验证事实、当前条件、惯例与假设的分类。
- 增加人类与社会问题的反过度还原边界。
- 增加理论可行与现实可行的区分。
- 增加初始回归测试集、仓库验证脚本和 GitHub Actions。
- 增加发布、贡献和版本维护文档。
