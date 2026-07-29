# Publishing Guide

本文件记录从本地发布包到 GitHub 公共 Skill 的标准流程。

## 0. 发布前确认

先运行：

```bash
python3 tools/validate_repo.py
```

确认输出：

```text
PASS: repository validation completed
```

## 1. 创建 GitHub 仓库

建议：

- Repository name：`first-principles-thinking-skill`
- Description：`A Chinese Agent Skill for first-principles analysis and solution reconstruction.`
- Visibility：Public
- 不要在 GitHub 页面额外创建 README、LICENSE 或 .gitignore，因为本地发布包已经包含这些文件。

## 2. 在本地解压并进入目录

```bash
cd /你解压的位置/first-principles-thinking-skill-v0.1.0
```

检查：

```bash
ls
```

## 3. 初始化 Git

```bash
git init
git branch -M main
git add .
git commit -m "feat: release first-principles-thinking v0.1.0"
```

若 Git 提示没有设置作者信息：

```bash
git config --global user.name "Jesse Tsui"
git config --global user.email "你的公开或GitHub noreply邮箱"
```

然后重新提交。

## 4. 连接 GitHub 仓库

将下面地址替换成 GitHub 新仓库页面提供的实际地址：

```bash
git remote add origin git@github.com:JesseTsui2000/first-principles-thinking-skill.git
git push -u origin main
```

使用 HTTPS 时：

```bash
git remote add origin https://github.com/JesseTsui2000/first-principles-thinking-skill.git
git push -u origin main
```

## 5. 检查 GitHub Actions

进入仓库的 **Actions** 页面，确认 `Validate Skill Repository` 为绿色通过。

若失败，打开运行记录，查看具体错误；不要在验证未通过时发布 Release。

## 6. 创建首个版本标签

本地执行：

```bash
git tag -a v0.1.0 -m "first-principles-thinking v0.1.0"
git push origin v0.1.0
```

## 7. 创建 GitHub Release

在仓库页面：

1. 点击右侧 `Releases`；
2. 点击 `Draft a new release`；
3. 选择 tag：`v0.1.0`；
4. Release title：`first-principles-thinking v0.1.0`；
5. 从 `CHANGELOG.md` 复制 `0.1.0` 内容；
6. 将本地 ZIP 作为可选附件上传；
7. 这是测试版，不要勾选 `Set as a pre-release` 也可以；若希望强调早期状态，则可勾选；
8. 点击 `Publish release`。

## 8. 验证公开安装

在一个临时目录运行：

```bash
npx skills add JesseTsui2000/first-principles-thinking-skill --list
```

确认能识别：

```text
first-principles-thinking
```

再执行安装：

```bash
npx skills add JesseTsui2000/first-principles-thinking-skill   --skill first-principles-thinking
```

## 9. 发布后的更新循环

每次改动按此顺序：

```text
收集失败案例
→ 添加或修改 eval
→ 修改 SKILL.md
→ 运行验证
→ 对比旧版与新版
→ 更新 CHANGELOG
→ 修改 VERSION 与 metadata.version
→ commit
→ tag
→ GitHub Release
```

不要直接覆盖已经发布的 tag。

## 10. 常用更新命令

普通修改：

```bash
git checkout main
git pull
# 修改文件
python3 tools/validate_repo.py
git add .
git commit -m "fix: improve activation boundary"
git push
```

发布新版本示例：

```bash
git tag -a v0.1.1 -m "first-principles-thinking v0.1.1"
git push origin v0.1.1
```

已安装用户可通过 Skills CLI 更新：

```bash
npx skills update first-principles-thinking
```
