## 变更摘要


## 变更类型

- [ ] Skill 行为变更
- [ ] 非行为维护变更
- [ ] 混合变更

## 发布信息

- Release type：
  - [ ] Core Skill release
  - [ ] Plugin-only release
  - [ ] Combined release
- Core Skill 基线版本：
- Core Skill 目标版本：
- Plugin wrapper 基线版本（不适用可填 `N/A`）：
- Plugin wrapper 目标版本（不适用可填 `N/A`）：
- 对应 Issue、失败案例或维护问题：
- eval ID（可填 `N/A`，并说明原因）：
- [ ] 准备作为发布 PR 合并

## 行为对比

### 旧版行为

非行为维护改动可填写：`N/A：本次不改变 Skill 行为。`

### 候选版行为

非行为维护改动可填写：`N/A：本次不改变 Skill 行为。`

## 兼容性

- [ ] 不触及核心七步流程
- [ ] 触及核心七步流程，已在下方说明
- [ ] 不改变触发范围或默认输出契约
- [ ] 改变触发范围或默认输出契约，已在下方说明

兼容性说明：


## 版本建议

Plugin-only release 的 Core version 判断填写：`N/A — Core Skill version unchanged.`

- [ ] PATCH：文档、validator、eval 修正，或恢复已承诺行为且不扩大触发/输出契约
- [ ] MINOR：增加向后兼容的分析能力、新维度或明显扩大但兼容的触发/输出能力
- [ ] MAJOR：改变核心七步流程、分类体系、默认行为契约或产生不兼容触发/输出

版本判断依据：

Plugin-only 变更说明（不适用可填 `N/A`）：


## 检查

- [ ] 涉及 Skill 行为时，已增加或更新 eval，并完成稳定版与候选版行为对比
- [ ] 不涉及 Skill 行为时，已说明 `N/A` 原因并完成适当维护验证
- [ ] 已运行 `python3 tools/validate_repo.py`
- [ ] 已检查 `CHANGELOG.md` 包含目标版本
- [ ] 已确认版本文件和 README 当前版本一致
- [ ] 若涉及 Plugin，已确认 `PLUGIN_VERSION` 与 manifest 一致
- [ ] 若涉及 Plugin，已确认 canonical manifest source，且仓库根 compatibility manifest 不存在
- [ ] 若涉及 Plugin，已确认 wrapper 未复制或修改核心 Skill
- [ ] 若涉及 Plugin，submission golden set 和本地路径验证已通过
- [ ] 若涉及 packaging，clean build 和 `--check` 已通过，且未人工编辑 `.build`
- [ ] 若涉及 directory submission，已验证 ZIP root 结构，并将未评估的 directory assets / Portal metadata 标记为 `NOT ASSESSED`
- [ ] GitHub Actions 已通过，或 PR 创建后等待 CI
