# 字谜项目完整计划（chinese-character-riddle + zimi-site）

> 本文档即第一阶段交付物（M0）：一份完整计划文档。
> 后续步骤只按本计划执行，不再做设计决策。

## 0. 交付物与本次动作

- **本次交付**：本计划文档，落在内容仓未来位置 `chinese-character-riddle/PLAN.md`。
- **后续**：按第 6 节里程碑推进。

## 1. 目标与成功标准

沿用 K12 的「单一事实源 + 分站」双仓结构，做字谜版：

| 部分 | 仓库 / 域名 | 角色 | 成功标准 |
|---|---|---|---|
| **第一部分：开源字谜库** | `diuci/chinese-character-riddle` | **唯一事实源**：纯 Markdown 字谜内容 + 内容工具 + 派生数据 + 可直接浏览的站点 | `validate.py` 全绿；CI「可复现闸门」绿；`data/riddles.json` 可由 `riddles/` 逐字节重算；用户可在 GitHub/Pages 直接浏览与搜索 |
| **第二部分：字谜分站** | `diuci/zimi-site` → `zimi.diuci.com` | **纯浏览/查阅站**（玩法后置，见 M5）：按分类/难度/谜底浏览，展示谜面+谜底+解析，可搜索可打印 | CI 从内容仓生成页面并部署成功；产物体检（空正文/法律/UI 闸门）全绿 |

「质量优先、收录最完整」的**契约基准** = `docs/scope.md`：它列明收录哪些谜书与哪些当代来源、每类目标篇数，`validate.py` 第 1 项逐条比对，漏收/多收即失败（对应 K12 的 `syllabus-2022.md` 契约）。

## 2. 内容仓 `chinese-character-riddle`（第一部分）

### 2.1 目录结构（与 k12-chinese-poetry 同构）

```
chinese-character-riddle/
├── riddles/                      # 内容（唯一事实源，手写 md，人读机读同一份）
│   ├── 拆字/  会意/  谐音/  增损/  离合/  典故/  象形/  方位/  数字/   # 主分类：按谜种
│   ├── 当代/                       # 当代优作（须署名+来源确证或已授权）
│   └── 索引.md                     # 生成：按难度/谜底/标签的交叉索引（gen-index.py）
├── data/                         # 构建产物（勿手改）
│   ├── riddles.json              # build.py 编译，分站与后续玩法的唯一数据源
│   ├── checksums.json            # 内容哈希，消费端校验用
│   └── authors.json              # 当代作者卒年总表（公版核验用）
├── docs/                         # 契约文档
│   ├── scope.md                # ★ 收录范围契约（「最完整」的基准）
│   ├── sources.md              # 数据来源与许可（S1–S5 代号说明）
│   ├── quality.md              # 质量门槛（收录判据，见 §2.3）
│   ├── change-process.md       # 内容冻结后的变更流程
│   └── contributing.md         # 贡献规范
├── tools/                        # 零依赖，纯 Python 标准库
│   ├── build.py                # Markdown → riddles.json + checksums.json
│   ├── validate.py             # 十项校验（见 §2.4），支持 --selftest
│   ├── gen-index.py            # 生成 riddles/索引.md
│   └── check-legal.mjs         # 法律护栏（绝对化表述、许可证、联系入口）
├── pending/                      # ⏸ 保护期内 / 版权未确认的当代谜
│   └── INDEX.md
├── site/                         # VitePress 浏览站（用户可直接浏览 markdown）
│   ├── index.md / guide.md / sources.md / print.md
│   ├── .vitepress/ (config.mts + 主题)
│   └── public/ (catalog.json, CNAME)
├── .github/workflows/verify.yml  # CI：自检 → 离线检查 → 派生产物重算 → 可复现闸门
├── PROVENANCE.md                 # 版权台账（汇总视图）
├── README.md
├── LICENSE
└── PLAN.md                       # 本文档
```

> 本仓**只管内容**：分站代码在 `zimi-site`，由它 CI 检出本仓生成页面（同 K12）。

### 2.2 篇目格式（每谜一个 md，frontmatter + 正文）

```markdown
---
id: shangshan-haishan              # 稳定标识（拼音 slug），联机/游戏引用用
title: 山上还有山                  # 谜面
answer: 出                         # 谜底（单字或词）
answer_len: 1                     # 谜底字数（校验用）
type: 增损                         # 谜种（主分类，见 §2.5 合法集）
subtype: 叠字                      # 可选细分类
difficulty: 2                     # 1–5
author: 佚名                      # 当代优作必须署名
era: 清                          # 朝代（古典）或「当代」
source: S1+S3                    # 来源台账代号
license: public-domain
copyright: { text: public-domain, annotations: cc-by-4.0 }
tags: [叠字, 方位]
---

# 山上还有山

> 增损类 · 清 · 难度 ★★

**谜面**：山上还有山
**谜底**：出

## 解析
「山」上再叠一个「山」，即为「出」字。上下两「山」相叠，属典型增损法。

## 出处
见《字謎大全》卷三（S1）。
```

**字段说明**：`id`/`title`/`answer`/`answer_len` 为谜面与谜底的最小完备集；`type`+`subtype` 决定目录归属；`difficulty` 用于分站难度轴与后续玩法匹配；`author`/`era`+`license` 支撑公版核验；`source` 是来源台账，无来源即不收；`tags` 支撑主题轴。`data/riddles.json` 完整序列化全部字段。

### 2.3 收录判据（质量门槛，「质量差的不要收入」）

`validate.py` 强制，任一不满足即失败：

1. **唯一谜底**——谜底明确、无歧义；歧义谜面剔除或登记 `known-defects.json`。
2. **解析完备**——每谜必须有「解析」段（推演链），不能只给谜底。
3. **来源可溯**——`source` 必填，无来源孤谜不收。
4. **无近似重复**——谜面做模糊去重（同面不同底须分别标注，否则拒收）。
5. **无低质内容**——低俗、歧义、政治敏感一律拒收（由 `check-legal.mjs` 与人工审核共同把关）。
6. **难度评级**——`difficulty` 必填且在 1–5。
7. **公版安全**——古典匿名/古早 = 公版；当代作品须署名且卒年 ≤ 当前年 − 50，或来源确证/已授权，否则进 `pending/`。
8. **谜种合法**——`type` 必须取自合法集（§2.5）。

### 2.4 校验（`tools/validate.py`，十项，`--selftest` 用坏样本证明护栏真拦得住）

| # | 检查 | 失败示例 |
|---|------|---------|
| 1 | 收录范围完整性 | `docs/scope.md` 契约要求收录却缺失 / 多收框架外来源 |
| 2 | id 唯一性 | 两谜共用一个 id |
| 3 | 谜底字段 | `answer` 缺失 / 空 / 字数与 `answer_len` 不符 |
| 4 | 难度合法 | `difficulty` 不在 1–5 |
| 5 | 台账完整 | 缺 `source` / `license` |
| 6 | 版权核验 | `license != public-domain` 的当代谜混入 `riddles/` |
| 7 | frontmatter | 必填字段缺失 |
| 8 | 公版证据 | 当代作者卒年晚于「当前年 − 50」，或缺 `author`/`era` |
| 9 | 去重 | 谜面近似重复未登记 |
| 10 | 谜种合法 | `type` 不在合法集 |

### 2.5 分门别类（分类轴）

- **主分类（目录，按谜种）**：`拆字` `会意` `谐音` `增损` `离合` `典故` `象形` `方位` `数字` `当代`。合法集即 `validate.py` 第 10 项。
- **难度轴**：`difficulty` 1–5。
- **谜底轴**：按谜底字/词索引（`gen-index.py` 生成，「猜出某字的所有谜」）。
- **主题轴**：`tags`（动物、植物、地名、成语、物品、自然现象…）。
- **时代轴**：`era`（古典 / 当代）。
- `riddles/索引.md` 汇总交叉索引，分站首页按主分类×难度×标签三轴筛选。

### 2.6 数据来源与版权（`docs/sources.md`，S 代号台账）

| 代号 | 来源 | 许可 | 用途 |
|---|---|---|---|
| S1 | 古典灯谜/字谜古籍（公版书：《文虎联珠集》(明)、《文虎偶存》、《玉荷隐语》、《字謎大全》(清) 等） | 公有领域 | 古典谜面谜底初稿与解析 |
| S2 | 网络开放收藏（如 daizhige 集藏·谜语/文虎 等开源谜集） | 以各自许可为准 | 交叉比对、补漏 |
| S3 | CC-Riddle 汉字谜语数据集（HuggingFace） | 开源 | 校验谜底一致性、补当代高质谜 |
| S4 | 当代高质量字谜（来源确证或已授权） | CC BY 4.0 / 授权 | 当代优作 |
| S5 | 商业站点 | 版权 | **仅比对用字，不复制** |

**公版规则**（与 K12 完全一致）：判定只有一条——作者卒年 ≤ 当前年 − 50。古典匿名谜记 `era` 年代上限；当代作者记 `author` + `authors.json` 卒年。`validate.py` 第 8 项逐篇核验，不满足即构建失败。仍在保护期的当代谜进 `pending/`，只登记不收录。

### 2.7 内容仓 CI（`.github/workflows/verify.yml`，同 k12-chinese-poetry）

1. **检查器自检**：`validate.py --selftest`、`build.py --selftest`、`gen-index.py --selftest`、`check-legal.mjs --selftest`（每个护栏先证明抓得住坏例子）。
2. **离线检查**：`validate.py`、`build.py`、`gen-index.py` 等全跑。
3. **派生产物重算与审计**：重算 `riddles.json`/`checksums.json`/`索引.md`，`check-legal.mjs`。
4. **可复现闸门**：跑完 `git status` 必须干净——提交的产物必须是链条跑出来的，不是手改的。

### 2.8 内容仓浏览站（`site/`，VitePress）

用户**直接浏览**的入口（对应 K12 的 `k12-chinese-poetry/site/`）：

| 页面 | 内容 |
|---|---|
| `/` | 全部谜总览，按**谜种 / 难度 / 标签**三轴筛选 |
| `/riddles/<谜种>/<slug>` | 单谜页：谜面 + 谜底 + 解析 + 出处 |
| `/print` | A4 打印版 |
| `/sources` | 数据来源与版权 |
| `/guide` | 指南 |

本地：`python tools/build.py && python tools/gen-index.py && npm run dev`；内置 minisearch 中文按字切分。部署到 GitHub Pages（项目页或子域）。

## 3. 分站 `zimi-site`（第二部分）

与 `k12-site` **完全同构**，只存放呈现层，内容全部来自 `chinese-character-riddle`，CI 构建时检出。

```
zimi-site/
├── site/                          # 手写 VitePress 骨架
│   ├── .vitepress/ (config.mts + 主题)
│   ├── index.md / guide.md / sources.md / print.md
│   └── public/ (CNAME=zimi.diuci.com, catalog.json)
├── tools/
│   ├── build-site.py             # 从 CONTENT_ROOT 生成站点页面（--selftest）
│   ├── check-legal.mjs          # 法律护栏（--selftest）
│   ├── check-pages.py           # 产物体检：抓「生成出来是空的」静默故障（--selftest）
│   ├── check-typography.mjs     # 字号结构闸门（--selftest）
│   └── check-ui.mjs             # UI 闸门（--selftest）
├── .github/workflows/deploy.yml  # 检出内容仓 → 生成 → 各闸门 → 构建 → 部署 Pages
├── package.json
└── README.md
```

- 数据流：`zimi-site` 只读内容仓快照（单向、按需取字段），不读其他分站。
- CI：`check-* --selftest` 先证明护栏有效，再跑正式闸门；`check-pages.py` 阻断空正文部署。
- 部署：`SITE_BASE=/`，自定义域 `zimi.diuci.com`。
- 分站**玩法后置**：本部分先交付纯浏览站（用户已确认「先浏览站，玩法后置」）。玩法（读谜面输答案字判定）列为 M5，届时参考 `lian-site` 的快照+每日题历史冻结机制单独规划。

## 4. 里程碑

| 里程碑 | 内容 | 出口标准 |
|---|---|---|
| **M0（本次）** | 完整计划文档 `PLAN.md` | 用户批准 |
| **M1** | 内容仓骨架：目录、frontmatter 格式、`build.py`/`validate.py`/`gen-index.py`/`check-legal.mjs`、CI 绿、种子谜若干 | `validate.py` 全绿；CI 可复现闸门绿；`riddles.json` 可复算 |
| **M2** | 内容扩充到「最完整」：系统性收录 S1–S4，达成 `docs/scope.md` 契约 | 第 1 项校验通过；`PROVENANCE.md` 台账齐全 |
| **M3** | 内容仓浏览站（VitePress）上线，可直接浏览 | 三轴筛选可用；`/print` 可打印 |
| **M4** | `zimi-site` 分站 + CI + 部署 `zimi.diuci.com` | 各闸门绿；Pages 部署成功 |
| **M5（后置）** | 玩法站（读谜面输答案字判定），参考 `lian-site` 快照+每日题冻结 | 另行规划后交付 |

## 5. 验收标准（整体）

- `python tools/validate.py` 十项全绿；`--selftest` 证明每项护栏抓得住坏样本。
- CI「可复现闸门」绿：提交的 `data/` 与 `索引.md` 与链条重算逐字节一致。
- `data/riddles.json` 是分站与后续玩法的**唯一数据源**，可由 `riddles/` 完整复算。
- 内容仓浏览站与 `zimi-site` 均可正常浏览、搜索、打印。
- 公版证据逐篇可核验，`pending/` 与 `PROVENANCE.md` 台账完整。
- 分站产物体检（空正文/法律/UI/字号）全绿，部署到 `zimi.diuci.com` 成功。

## 6. 执行顺序（批准后）

1. 建 `chinese-character-riddle/` 文件夹，写入本计划文档 `PLAN.md`（即本文件）。
2. 按 M1 初始化内容仓骨架与工具链，使 CI 可跑绿。
3. M2 扩充内容、M3 浏览站、M4 分站、M5 玩法（后置）。

> 说明：本次仅交付计划文档（M0），不初始化 git、不写任何谜面内容、不动 K12 现有文件。`PLAN.md` 写入后即为「完整计划文档」，后续按里程碑推进。
