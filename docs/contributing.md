# 贡献规范（contributing）

发现错字、想补解析、或想加篇目，都欢迎提 PR。请先读本文件与 [quality.md](quality.md)。

## 加一篇谜

1. 确认谜种（`type`）取自合法集：拆字 / 会意 / 谐音 / 增损 / 离合 / 典故 / 象形 / 方位 / 数字 / 当代。
2. 在对应目录建 `riddles/<谜种>/<谜面>.md`，frontmatter 按 [PLAN.md](../PLAN.md) §2.2 的字段填全。
3. 写「解析」段（推演链）与「出处」段（来源代号）。
4. 在 `docs/scope.md` 的收录清单表里加一行（id / 谜种 / 谜底）。
5. 跑 `python tools/build.py && python tools/gen-index.py && python tools/validate.py`，全绿再提交。

## 字段最小集

`id`、`title`、`answer`、`answer_len`、`type`、`difficulty`、`author`、`era`、`source`、`license`、`copyright` 必填；
`subtype`、`tags` 可选。`answer_len` 必须等于 `answer` 的字数。

## 版权

- 古典谜：`license: public-domain`，`author: 佚名`，`era` 记朝代。
- 当代署名作者：`license: public-domain`（卒年 ≤ 当前年 − 50）或 `cc-by-4.0`（我方原创），
  并在 `data/authors.json` 登记卒年。
- 仍在保护期：不收录原文，登记 `pending/`。

## 红线

请勿直接粘贴商业站点的译文与解析（S5 仅比对用字）。质量差的不要收入——
低俗、歧义、谜底不唯一、无来源，一律不收。
