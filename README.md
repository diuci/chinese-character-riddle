# 字谜开源库 · chinese-character-riddle

> 全网质量最高、收录最完整的**开源字谜库**。
> 古典谜面/谜底/解析为**公有领域**；我方原创当代谜、注释、解析与选篇编排 © 丢词大作战，采用 **CC BY 4.0**。

**English**: A curated open-source corpus of Chinese character riddles (字谜).
Classical riddle texts are **public domain**; our original contemporary riddles,
annotations and commentary are **CC BY 4.0**.

[![收录](https://img.shields.io/badge/收录-26%20篇-0f766e)](docs/scope.md)
[![法律风险](https://img.shields.io/badge/版权风险-0%20风险-2ea44f)](pending/INDEX.md)
[![许可](https://img.shields.io/badge/许可-公有领域%20%2B%20CC%20BY%204.0-blue)](LICENSE)

---

## 这是什么

一个**纯 Markdown** 的中文字谜内容库，是字谜分站与后续玩法的**单一事实源**：

| 消费者 | 说明 |
|---|---|
| **字谜分站** | [zimi.diuci.com](https://zimi.diuci.com)（[diuci/zimi-site](https://github.com/diuci/zimi-site)）——谜面、谜底、解析，可浏览、搜索、打印 |
| **后续玩法** | 读谜面输答案字判定的互动玩法（M5 后置），经 `tools/build.py` 编译为 `data/riddles.json` |

本仓只存放内容与内容工具；站点代码独立成仓。

## 收录范围与质量

「最完整」的契约基准是 **[docs/scope.md](docs/scope.md)**——`validate.py` 第 1 项逐条比对，漏收或多收即失败。
「质量优先」是 **[docs/quality.md](docs/quality.md)** 里的八条收录判据——任何一条不满足，构建失败。

当前 26 篇，覆盖 9 个谜种（谐音仍按「宁缺毋滥」留给后续，不强塞低质篇目）。

## 数据来源与版权

五类来源交叉校验，每篇 frontmatter 记录来源代号。完整说明见 **[docs/sources.md](docs/sources.md)**，
汇总台账见 **[PROVENANCE.md](PROVENANCE.md)**。

> **公有领域逐篇核验**：判定只有一条——作者卒年 ≤ 当前年 − 50。古典匿名谜记 `era` 年代上限，
> 当代作者总表见 `data/authors.json`。`tools/validate.py` 第 8 项逐篇核验，不满足即构建失败。
> 仍在保护期内的当代作品**不收录原文**，登记在 [pending/](pending/INDEX.md)。

## 目录结构

```
riddles/<谜种>/<谜面>.md   # 按谜种组织的篇目（唯一事实源）
├── data/                  # 构建产物（勿手改）
│   ├── riddles.json       # build.py 编译，分站与玩法的唯一数据源
│   ├── checksums.json     # 内容哈希，消费端校验用
│   ├── authors.json       # 当代作者卒年总表
│   └── known-defects.json # 已知未修登记
├── docs/
│   ├── scope.md           # ★ 收录范围契约（校验基准）
│   ├── sources.md         # 数据来源与许可
│   ├── quality.md         # 质量门槛（收录判据）
│   ├── change-process.md  # 冻结后变更流程
│   └── contributing.md    # 贡献规范
├── tools/
│   ├── build.py           # Markdown → riddles.json + checksums.json
│   ├── validate.py        # 十项校验（+ --selftest）
│   ├── gen-index.py       # 生成 riddles/索引.md
│   └── check-legal.mjs    # 法律护栏
├── site/                  # VitePress 浏览站（直接浏览 markdown）
└── pending/               # ⏸️ 保护期内作品，暂不收录
```

## 工具

内容工具零依赖，纯 Python 3 标准库（无需 pip install）。

```bash
python tools/build.py             # 生成 data/riddles.json + checksums.json
python tools/validate.py          # 十项校验，须全绿
python tools/validate.py --partial # 增量期校验，跳过"收录范围"
python tools/gen-index.py         # 生成 riddles/索引.md
node tools/check-legal.mjs        # 法律护栏
```

### `validate.py` 的十项校验

| # | 检查 | 失败示例 |
|---|------|---------|
| 1 | 收录范围完整性 | scope.md 要求收录但缺失 / 多收框架外 |
| 2 | id 唯一性 | 两谜共用一个 id |
| 3 | 谜底字段 | `answer` 空 / 字数与 `answer_len` 不符 |
| 4 | 难度合法 | `difficulty` 超出 1–5 |
| 5 | 台账完整 | 缺 `source` / `license` |
| 6 | 版权核验 | `license=cc-by-4.0` 但作者非我方原创 |
| 7 | frontmatter | 必填字段缺失 |
| 8 | 公版证据 | 当代作者卒年晚于「当前年 − 50」 |
| 9 | 去重 | 谜面重复/包含未登记 |
| 10 | 谜种合法 | `type` 不在合法集 |

## 篇目格式

每谜就是一个 Markdown 文件，**人读与机读同一份**：

```markdown
---
id: shangshan-haishan
title: 山上还有山
answer: 出
answer_len: 1
type: 增损
subtype: 叠字
difficulty: 1
author: 佚名
era: 清
source: S1+S3
license: public-domain
copyright: { text: public-domain, annotations: cc-by-4.0 }
tags: [叠字, 方位]
---

# 山上还有山

> 增损类 · 清 · 难度 ★

**谜面**：山上还有山
**谜底**：出

## 解析
「山」字上下再叠一个「山」，即为「出」字。属典型的叠字增损。

## 出处
见《字謎大全》卷三（S1），CC-Riddle 数据集亦有收录（S3）。
```

完整字段说明见 [PLAN.md](PLAN.md) §2.2。

## 网站

字谜分站：**<https://zimi.diuci.com>**（[diuci/zimi-site](https://github.com/diuci/zimi-site)）。
本仓 `site/` 提供直接浏览入口，按**谜种 / 难度 / 标签**三轴筛选，可搜索可打印。

## 关联项目

| 项目 | 说明 |
|------|------|
| [zimi.diuci.com](https://zimi.diuci.com) | 字谜分站（[diuci/zimi-site](https://github.com/diuci/zimi-site)） |
| `zimi-site` | 分站仓，消费本仓 `data/riddles.json` |

## 许可

- **古典谜面/谜底/解析**：公有领域（卒年 ≤ 当前年 − 50，逐篇可核验）
- **我方原创当代谜 / 注释 / 解析 / 选篇编排**：[CC BY 4.0](LICENSE)
- **本仓脚本**：MIT，见 [LICENSE](LICENSE) 与 [tools/](tools/)

使用时请署名「来源：chinese-character-riddle / 丢词大作战」。
