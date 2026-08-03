# OpenAI Plugin Wrapper

本文档说明 `first-principles-thinking` 的 OpenAI skills-only Plugin 本地技术包装。当前阶段只准备本地文件、验证和提交测试资料，不进行公开提交或发布。

## Canonical sources

受版本控制的包装输入是：

```text
skills/first-principles-thinking/SKILL.md
packaging/openai-plugin/plugin.json
VERSION
PLUGIN_VERSION
plugin-submission/test-cases.json
```

`skills/first-principles-thinking/SKILL.md` 是唯一 Core Skill 事实源；`packaging/openai-plugin/plugin.json` 是唯一 Plugin wrapper manifest source。不得复制、改写或人工维护第二份核心指令；wrapper、marketplace、listing 文案和 submission tests 都不能扩大 Skill 的触发契约、七步流程、输出结构、边界或禁止事项。

仓库根目录不再包含 `.codex-plugin/plugin.json`；validator 会拒绝 compatibility manifest 再次出现，避免仓库根重新成为 Plugin root。

## Generated package

使用仅依赖 Python 标准库的构建器生成或只读检查：

```bash
python3 tools/build_openai_plugin.py
python3 tools/build_openai_plugin.py --check
```

固定输出：

```text
.build/plugins/first-principles-thinking/
├── .codex-plugin/
│   └── plugin.json
└── skills/
    └── first-principles-thinking/
        └── SKILL.md
```

`.build/` 是 ignored generated output，不允许人工编辑。生成目录中的 `SKILL.md` 只是 canonical Skill 的构建副本，不是第二份 canonical source，也不得纳入版本控制。

构建器先在安全的 sibling temporary directory 中复制并验证，成功后才替换最终输出。Package 只能包含图示中的两个普通文件；`--check` 不创建、修改或删除文件，并拒绝缺失、stale、污染、symlink、hardlink 或特殊文件。

## Release and submission material

- 本地 Plugin root：完整的 `.build/plugins/first-principles-thinking/`。
- Skills-only Portal submission 使用 ZIP，ZIP 必须包含 supported Plugin manifest 和至少一个 bundled Skill。
- ZIP 可以直接以 Plugin root 为 archive root；也可以使用唯一一个顶层 Plugin 目录，但该目录不得有 sibling files。
- 当前 generated directory 是未来 ZIP 的 Plugin root；当前不生成 ZIP，也不引入 dist branch、独立发行仓库、npm package 或 archive 自动化。
- ZIP 自动生成推迟到真实 publisher/listing 字段补齐后的 Portal preflight 阶段。

当前 manifest 缺少用户待确认的 publisher/listing 字段。本地 package 可以验证为有效，但不得声明为 Portal-ready；不得添加身份、URL、logo 或 listing 占位符绕过该状态。

## 多制品版本

- `VERSION` 表示 Core Skill version，当前为 `0.1.2`。
- `PLUGIN_VERSION` 表示 OpenAI Plugin wrapper version，当前为 `0.1.0`。
- `packaging/openai-plugin/plugin.json` 的 `version` 必须等于 `PLUGIN_VERSION`；generated manifest 必须与它逐字节一致。
- 两个版本独立演进：Plugin `0.1.0` bundles Core Skill `0.1.2`。
- Plugin-only 维护不得强制提升 Core Skill version；Core Skill 变化时应评估 wrapper 是否需要新版本和重新验证。

## 本地 marketplace

Repo-local marketplace 文件是：

```text
.agents/plugins/marketplace.json
```

目标 entry 使用 `source.path: "./.build/plugins/first-principles-thinking"`。路径相对 marketplace root，不能包含 `..`、不能指向仓库根，并必须与固定 build output 一致。fresh clone 后应先运行 builder；generated package 不受版本控制，禁止人工编辑。

当前只验证 marketplace 的路径和文件系统解析。ChatGPT/Codex 是否能发现该 repo-local marketplace、旧 Plugin 卸载、从 generated root 重装及新 cache 审计均留到 Phase 3，不能将本阶段结果描述为桌面端发现成功。

## 本地测试计划

1. 运行 repository validator、clean build 和 package `--check`。
2. 确认 manifest 只引用 package 内 `skills/`，不包含 MCP、App 或 screenshot 配置。
3. 连续两次 clean build，比较文件清单、每个文件 SHA 和逐字节内容。
4. 确认核心 `SKILL.md` 和 `evals.json` 无 diff，核心 SHA-256 不变。
5. Phase 3 经单独授权后，从 generated root 重装并使用 `plugin-submission/test-cases.json` 做 Plugin-only 行为回归；不得直接修改用户级 Skill copy。

### plugin-creator preflight 状态

官方 `plugin-creator` helper 是推荐的脚手架和 preflight 路径之一，但当前环境运行 helper 时因 Python 环境没有 PyYAML 而失败，尚未通过：

```text
ModuleNotFoundError: No module named 'yaml'
```

Packaging Phase 2 遵守约束，不安装 PyYAML、不修改系统 Python，也不运行该 helper。PyYAML 不会成为项目依赖。后续 helper 只允许针对最终生成 package 运行，不得用它重写 canonical source；正式 Portal submission 前，应在单独授权的隔离环境中补跑 helper，或使用届时官方提供的等效 validator。

`.build` source.path 的文件系统解析已经验证；category 和完整 ingestion 仍必须由后续 Plugin Directory 实测确认，不能将当前静态验证视为已经完成安装验证。

## Submission golden set

`plugin-submission/test-cases.json` 是 OpenAI Plugin submission golden set，不替代核心 `evals.json`。Portal 公开提交至少需要 5 个正向测试和 3 个负向测试；本仓库准备 7 个正向和 4 个负向案例。

## 后续阶段

Publisher identity、logo、website、support、privacy、terms、category 和 availability 均属于后续阶段。本地 wrapper 不添加这些字段的占位符，也不推断尚未确认的信息。

每次公开提交或更新应记录以下映射：

```text
Plugin version
Core Skill version
Git commit
Core Skill SHA-256
Portal submission/revision ID
Published URL
```
