# 指南

本库是**字谜分站**与**后续玩法**的单一事实源。这里说明内容怎么组织、怎么消费。

## 目录即分类

`riddles/` 下按**谜种**分目录：拆字 / 会意 / 谐音 / 增损 / 离合 / 典故 / 象形 / 方位 / 数字 / 当代。
每个 `.md` 就是一篇字谜，frontmatter 记谜面、谜底、难度、来源、版权。

另有两个交叉轴：
- **难度**（`difficulty` 1–5）：用于分站筛选与后续玩法匹配。
- **标签**（`tags`）：主题轴（动物 / 植物 / 地名 / 成语…）。

[riddles/索引](/riddles/索引) 是交叉索引页，按谜种 / 难度 / 谜底 / 标签汇总。

## 怎么消费这份数据

- **分站**（[zimi.diuci.com](https://zimi.diuci.com)）读 `data/riddles.json` 渲染页面，不直接读 md。
- **后续玩法**（M5）读 `data/riddles.json` 的 `answer` 字段做判定。
- 本浏览站直接渲染 `riddles/**/*.md`（VitePress）。

## 质量门槛

收录判据见 [quality](/sources)（八条）。任何一条不满足，`tools/validate.py` 构建失败。
宁缺毋滥——空目录比低质篇目更诚实。

## 变更流程

改内容后重算派生产物，全绿再提交。见 [change-process](/sources)。
