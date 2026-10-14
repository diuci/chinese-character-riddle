# 内容冻结后的变更流程（change-process）

内容一旦冻结（`data/riddles.json` 与 `riddles/索引.md` 提交入库），
后续任何改动都必须走这条流程，保证「提交进去的产物是链条跑出来的，不是手改的」。

## 流程

1. **改内容**：编辑 `riddles/**/*.md`（唯一事实源），或改 `docs/scope.md` 收录清单。
2. **重算派生产物**：
   ```bash
   python tools/build.py          # riddles.json + checksums.json
   python tools/gen-index.py      # riddles/索引.md
   ```
3. **全量校验**：
   ```bash
   python tools/validate.py       # 十项全绿
   node tools/check-legal.mjs     # 法律护栏
   ```
4. **提交**：把改动的源文件与重算后的产物**一起**提交。CI「可复现闸门」会重跑链条，
   若 `git status` 不干净（产物与源不一致）就红。

## 红线

- 不得手改 `data/` 或 `riddles/索引.md`——它们是派生物，必须能由 `riddles/` 复算。
- 不得只改源不重算产物——CI 会抓到。
- 不得为过校验而放宽 `validate.py` 的规则——改规则要提 PR 说明理由。

## 勘误

发现谜底/谜面有误，改源文件后重算。若该篇已被分站快照，更新快照是显式动作
（见分站仓的 sync 说明），不留「明知是错还照原样端出去」的死角。
