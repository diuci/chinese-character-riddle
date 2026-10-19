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

当前收录 98 篇，覆盖全部 10 个谜种。谐音类已由 0 补齐（以经典歇后语谐音谜，
来源确证、谜底无歧义）。每篇均有唯一谜底与完整解析，无近似重复。

| id | 谜种 | 谜底 |
|---|---|---|
| yikou-yao-niuban | 拆字 | 告 |
| shikou-xinsi | 拆字 | 思 |
| qianli-xiangfeng | 拆字 | 重 |
| banqing-banzi | 拆字 | 素 |
| banged-bandu | 拆字 | 讲 |
| ren-zai-cao-mu-zhong | 拆字 | 茶 |
| shikou-zhangkou | 拆字 | 田 |
| yiren-zainei | 拆字 | 肉 |
| yibian-lv-yibian-hong | 拆字 | 秋 |
| yiren-yizhang-kou | 拆字 | 拿 |
| yibian-yu-yibian-yang | 拆字 | 鲜 |
| shangshan-haishui | 拆字 | 汕 |
| rifu-yiri | 拆字 | 昌 |
| chunxiang-lianye-tinqinsheng | 拆字 | 秦 |
| yijian-chuanxin | 会意 | 必 |
| yiye-you-yiye | 会意 | 多 |
| simian-boutu-feng | 会意 | 口 |
| yijia-shiyi-jiukou | 会意 | 吉 |
| shiwutian | 会意 | 胖 |
| yijia-yikou | 会意 | 问 |
| you-tou-wu-wei | 会意 | 鱼 |
| you-mian-wu-kou | 会意 | 镜 |
| waimian-yikou-quan | 会意 | 困 |
| changhe-luori-yuan | 会意 | 旦 |
| bashan-kangding | 会意 | 夯 |
| xiaochuaner-tui-kai-bolang | 会意 | 心 |
| bu-zai-zhuang-ya-xian-zhen-shen | 会意 | 显 |
| gushen-piaoling-jin-haizai | 会意 | 生 |
| si-yuan-gong-jiao-er-she-zhi | 会意 | 忒 |
| zhulan-dashui | 谐音 | 场 |
| waisheng-da-denglong | 谐音 | 照 |
| xiaotongban-doufu | 谐音 | 清 |
| erliang-mianhua | 谐音 | 谈 |
| daguniang-zuo-huajiao | 谐音 | 迎 |
| shiwu-ge-tong | 谐音 | 忍 |
| dajiao-chuan-xiaoxie | 谐音 | 难 |
| kongfuzi-banjia | 谐音 | 书 |
| shangshan-haishan | 增损 | 出 |
| duo-yiban | 增损 | 夕 |
| banbu-chunqiu | 增损 | 香 |
| chunyumianmian-qidu-su | 增损 | 一 |
| yiren-tiao-liang-xiaoren | 增损 | 夹 |
| shi'er-dian | 增损 | 斗 |
| shiba-kou | 增损 | 杏 |
| yibian-shui-yibian-huo | 增损 | 灭 |
| yishang-yixia | 增损 | 卡 |
| ermu-cheng-lin | 增损 | 林 |
| zuigai-zhanshou | 增损 | 非 |
| youmeiyou-shangbian | 增损 | 月 |
| zixiao-hao-jiejian | 增损 | 省 |
| houtou-yincang-bujianle | 增损 | 侯 |
| liangdian-zhongjian-yigeren | 增损 | 火 |
| luori-zai-liangou | 增损 | 电 |
| xuri-dongsheng | 增损 | 九 |
| guizhou-jin-tengfei | 增损 | 黑 |
| shuidiao-getou | 增损 | 河 |
| youli-jixi | 增损 | 鸟 |
| chengchi-ban-canpo | 增损 | 地 |
| shizai-gaige-jiuguo-gai | 增损 | 早 |
| cizi-yongxin-fang-wude | 增损 | 五 |
| ernv-shuangquan | 增损 | 好 |
| jianshui-zhongri-liu | 增损 | 门 |
| wangyou-zoudian | 增损 | 王 |
| renren-douyou-xiongxin | 增损 | 众 |
| ershiriyi-you-jinqian | 增损 | 错 |
| lingzhan-xinzi-lie-qianmao | 增损 | 茄 |
| yifu-zhongjian-youge-dong | 增损 | 哀 |
| sanxing-cuoluo-ying-tianya | 增损 | 六 |
| baotou-xiaxuele | 增损 | 雹 |
| ciren-zhuanggan-dangguanle | 增损 | 仕 |
| zhi-cha-bazi-weixie | 增损 | 嗟 |
| shaoshidui-duiqi-piaoyang | 增损 | 从 |
| dì-er-ci-jiànmiàn | 增损 | 观 |
| tianli-paodao-tianwai | 增损 | 叶 |
| dayu-luo-zai-hengshang | 增损 | 雪 |
| housheng-xiaozi | 增损 | 孙 |
| youde-shifen | 增损 | 对 |
| yishi-tongren-liu-guan-zhang | 增损 | 仨 |
| tianzhong-bujian-ren | 增损 | 囚 |
| erren-yuzhong-cang | 增损 | 两 |
| youxin-ru-men-nan-touqi | 增损 | 闷 |
| erren-xiangfeng-chuan-fuyin | 增损 | 夫 |
| bantui-banjiu | 离合 | 掠 |
| sanguo-qimen | 典故 | 不 |
| simazhao-zhixin | 典故 | 腹 |
| yidian-yiheng-chang | 象形 | 府 |
| yilun-wanyue | 象形 | 夕 |
| taiyang-gua-zai-shushao | 象形 | 杲 |
| taiyang-luo-zai-shushao | 象形 | 杳 |
| riyue-hebi | 象形 | 明 |
| shangxia-xianglian | 方位 | 卡 |
| jiushijiu | 数字 | 百 |
| qishier-xiaoshi | 数字 | 晶 |
| shi'er-ge-yue | 数字 | 年 |
| bashiba | 数字 | 米 |
| sansan-ri | 数字 | 晶 |
| yibian-yiban | 数字 | 秋 |
| renyan-chengxin | 当代 | 信 |

## 来源与「最完整」的边界

- **S1 古典谜书（公版）**：《文虎联珠集》(明)、《文虎偶存》、《玉荷隐语》、《字謎大全》(清) 等，及民间歇后语。
- **S2 网络开放收藏**：如 daizhige 集藏·谜语/文虎 等开源谜集，交叉比对补漏。
- **S3 CC-Riddle 汉字谜语数据集**（HuggingFace）：校验谜底一致性、补当代高质谜。
- **S4 当代高质量字谜**：来源确证或已授权，署名 + cc-by-4.0。
- **S5 商业站点**：仅比对用字，不复制。

「收录最完整」= S1 所列古典谜书里**谜底无歧义、可给出完整解析**的字谜全部收录；
S3 里符合质量门槛的当代谜补入。达不到门槛的宁可不收（见 `quality.md`）。

### 谜种现状的诚实口径（2026-10-19）

- **离合（1）/ 方位（1）/ 典故（2）已收尽**：S1/S2/S3 三条来源线扫完，公版可核的
  就这几篇；这不是缺失，是矿的边界。有新公版来源再扩，不硬凑。
- **拆解数据（structure）覆盖 61 / 98**：拆字 11/14、会意 7/15、增损 43/45。
  未标注的 37 篇：纯会意/象形类（如 显/生/鱼/镜）没有部件可拆，硬造拆解就是编数据；
  另有拆字 3 篇（肉——近形歧义、告/素——部件字 ⺧/龶 字体覆盖风险）与增损 2 篇
  （六——纯算术、两——解析部件账不齐）如实跳过；它们照常走打字玩法。

## 里程碑对照

- **M1**：12 篇种子，骨架与工具链全绿。
- **M2**：已扩到 48 篇，覆盖全部 10 个谜种（谐音类已从 0 补齐到 8）；继续系统性扫 S1/S3，本表随篇目同步更新。
