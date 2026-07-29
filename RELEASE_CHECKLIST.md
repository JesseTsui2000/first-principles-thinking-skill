# Release Checklist

## 内容

- [ ] 新增或更新了对应失败案例的 eval
- [ ] `SKILL.md` 没有不必要的重复
- [ ] description 仍明确说明“做什么”和“何时使用”
- [ ] 没有把个人判断包装成事实
- [ ] 没有删除安全、法律、专业知识和现实可行性边界
- [ ] 默认输出仍可根据问题复杂度压缩

## 版本

- [ ] `VERSION` 已更新
- [ ] `SKILL.md` 的 `metadata.version` 与 `VERSION` 一致
- [ ] `CHANGELOG.md` 已更新
- [ ] 已判断是 PATCH、MINOR 还是 MAJOR

## 测试

- [ ] `python3 tools/validate_repo.py` 通过
- [ ] 旧版与新版已使用相同 eval 对比
- [ ] 至少检查一个“应该触发”案例
- [ ] 至少检查一个“不应该强行触发”案例
- [ ] 至少检查一个高风险或专业边界案例
- [ ] 至少检查一个人类或社会问题案例

## GitHub

- [ ] main 分支已 push
- [ ] GitHub Actions 通过
- [ ] 创建了不可复用的新 tag
- [ ] 创建了 GitHub Release
- [ ] Release notes 与 Changelog 一致
- [ ] 从公开仓库重新安装测试成功
