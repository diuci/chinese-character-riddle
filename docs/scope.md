# 收录范围契约（scope）

> 本文件是 `tools/validate.py` 第 1 项「收录范围完整性」的**可执行契约**。
> 下表列出的篇目必须全部收录，且框架外不得多收。改篇目必须同步改这张表。
> 增量期可跑 `python tools/validate.py --partial` 跳过本项。

## 分类轴

| 轴 | 取值 |
|---|---|
| **主分类（目录 / `type`）** | 拆字 · 会意 · 谐音 · 增损 · 离合 · 典故 · 象形 · 方位 · 数字 · 当代 |
| 难度（`difficulty`） | 1–5 |
| 谜底轴 | 按 `answer` 字/词索引（`gen-index.py` 生成） |
| 主题轴 | `tags`（动物 / 植物 / 地名 / 成语 / 物品 / 自然现象…） |
| 时代轴（`era`） | 古典（先秦…清）/ 当代 |

## 收录清单（契约）

当前收录 26 篇，覆盖 9 个谜种。**谐音**为合法谜种，但现阶段不强塞低质篇目——
待从 S1/S3 找到来源确证、谜底无歧义的高质篇目再补齐（质量优先，宁缺毋滥）。

| id | 谜种 | 谜底 |
|---|---|---|
| shangshan-haishan | 增损 | 出 |
| duo-yiban | 增损 | 夕 |
| banbu-chunqiu | 增损 | 香 |
| chunyumianmian-qidu-su | 增损 | 一 |
| yikou-yao-niuban | 拆字 | 告 |
| shikou-xinsi | 拆字 | 思 |
| qianli-xiangfeng | 拆字 | 重 |
| banqing-banzi | 拆字 | 素 |
| banged-bandu | 拆字 | 讲 |
| ren-zai-cao-mu-zhong | 拆字 | 茶 |
| shikou-zhangkou | 拆字 | 田 |
| yiren-zainei | 拆字 | 肉 |
| yijian-chuanxin | 会意 | 必 |
| yiye-you-yiye | 会意 | 多 |
| simian-boutu-feng | 会意 | 口 |
| yijia-shiyi-jiukou | 会意 | 吉 |
| shiwutian | 会意 | 胖 |
| yijia-yikou | 会意 | 问 |
| bantui-banjiu | 离合 | 掠 |
| sanguo-qimen | 典故 | 不 |
| shangxia-xianglian | 方位 | 卡 |
| jiushijiu | 数字 | 百 |
| qishier-xiaoshi | 数字 | 晶 |
| yidian-yiheng-chang | 象形 | 府 |
| yilun-wanyue | 象形 | 夕 |
| renyan-chengxin | 当代 | 信 |

## 来源与「最完整」的边界

- **S1 古典谜书（公版）**：《文虎联珠集》(明)、《文虎偶存》、《玉荷隐语》、《字謎大全》(清) 等。
- **S2 网络开放收藏**：如 daizhige 集藏·谜语/文虎 等开源谜集，交叉比对补漏。
- **S3 CC-Riddle 汉字谜语数据集**（HuggingFace）：校验谜底一致性、补当代高质谜。
- **S4 当代高质量字谜**：来源确证或已授权，署名 + cc-by-4.0。
- **S5 商业站点**：仅比对用字，不复制。

「收录最完整」= S1 所列古典谜书里**谜底无歧义、可给出完整解析**的字谜全部收录；
S3 里符合质量门槛的当代谜补入。达不到门槛的宁可不收（见 `quality.md`）。

## 里程碑对照

- **M1**：12 篇种子，骨架与工具链全绿。
- **M2（进行中）**：系统性收录 S1–S4，已扩到 26 篇（典故类已从 0 到 1）；继续补 S1/S3 高质篇目，本表随篇目同步更新。
