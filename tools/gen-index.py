#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen-index.py — 从 data/riddles.json 生成 riddles/索引.md

索引是交叉视图（按谜种 / 难度 / 谜底 / 标签），不是内容事实源——
改谜目后重新生成，不要手改。生成物入库，CI「可复现闸门」会核对它
是否等于链条跑出来的结果。

用法：
    python tools/gen-index.py            # 用 data/riddles.json 生成 riddles/索引.md
    python tools/gen-index.py --selftest # 临时数据自检

零依赖。
"""

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def render(riddles):
    lines = ['# 索引', '', '> 由 `tools/gen-index.py` 从 `data/riddles.json` 生成，勿手改。共 %d 篇。' % len(riddles), '']

    # 按谜种
    lines += ['## 按谜种', '']
    bytype = {}
    for r in riddles:
        bytype.setdefault(str(r.get('type') or '?'), []).append(r)
    for t in sorted(bytype):
        items = sorted(bytype[t], key=lambda r: (r.get('difficulty') or 0, str(r.get('id') or '')))
        lines.append('### %s（%d）' % (t, len(items)))
        for r in items:
            lines.append('- [%s](%s) → **%s**（难度 %d）' % (r.get('title'), r.get('path'), r.get('answer'), r.get('difficulty') or 0))
        lines.append('')

    # 按难度
    lines += ['## 按难度', '']
    bydiff = {}
    for r in riddles:
        bydiff.setdefault(int(r.get('difficulty') or 0), []).append(r)
    for d in sorted(bydiff):
        items = sorted(bydiff[d], key=lambda r: str(r.get('id') or ''))
        lines.append('### %d 星（%d）' % (d, len(items)))
        for r in items:
            lines.append('- [%s](%s) → **%s**' % (r.get('title'), r.get('path'), r.get('answer')))
        lines.append('')

    # 按谜底
    lines += ['## 按谜底', '']
    byans = {}
    for r in riddles:
        byans.setdefault(str(r.get('answer') or '?'), []).append(r)
    for a in sorted(byans):
        items = sorted(byans[a], key=lambda r: str(r.get('id') or ''))
        lines.append('### %s（%d）' % (a, len(items)))
        for r in items:
            lines.append('- [%s](%s)（%s，难度 %d）' % (r.get('title'), r.get('path'), r.get('type'), r.get('difficulty') or 0))
        lines.append('')

    # 按标签
    lines += ['## 按标签', '']
    bytag = {}
    for r in riddles:
        for tag in (r.get('tags') or []):
            bytag.setdefault(str(tag), []).append(r)
    for tag in sorted(bytag):
        items = sorted(bytag[tag], key=lambda r: str(r.get('id') or ''))
        lines.append('### %s（%d）' % (tag, len(items)))
        for r in items:
            lines.append('- [%s](%s) → **%s**' % (r.get('title'), r.get('path'), r.get('answer')))
        lines.append('')

    return '\n'.join(lines).rstrip() + '\n'


def build_index(data_json, out_md):
    payload = json.loads(Path(data_json).read_text(encoding='utf-8'))
    text = render(payload.get('riddles', []))
    out_md.write_text(text, encoding='utf-8')
    return text


def main(argv=None):
    ap = argparse.ArgumentParser(description='生成 riddles/索引.md')
    ap.add_argument('--root', default=str(ROOT))
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    root = Path(args.root)
    data = root / 'data' / 'riddles.json'
    if not data.exists():
        print('先跑 python tools/build.py 生成 data/riddles.json')
        return 1
    out = root / 'riddles' / '索引.md'
    build_index(data, out)
    print('index → %s' % out)
    return 0


def selftest():
    with tempfile.TemporaryDirectory() as td:
        tdr = Path(td)
        data = tdr / 'riddles.json'
        payload = {'count': 2, 'riddles': [
            {'id': 'a', 'title': '谜面A', 'answer': '出', 'answer_len': 1, 'type': '增损',
             'difficulty': 1, 'author': '佚名', 'era': '清', 'source': 'S1',
             'license': 'public-domain', 'copyright': {'text': 'public-domain', 'annotations': 'cc-by-4.0'},
             'tags': ['叠字'], 'path': 'riddles/增损/A.md'},
            {'id': 'b', 'title': '谜面B', 'answer': '心', 'answer_len': 1, 'type': '会意',
             'difficulty': 2, 'author': '佚名', 'era': '清', 'source': 'S1',
             'license': 'public-domain', 'copyright': {'text': 'public-domain', 'annotations': 'cc-by-4.0'},
             'tags': ['会意'], 'path': 'riddles/会意/B.md'},
        ]}
        data.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
        out = tdr / '索引.md'
        text = build_index(data, out)
        failures = []
        for needle in ('按谜种', '按难度', '按谜底', '按标签', '### 增损（1）', '### 出（1）', '### 叠字（1）', '### 2 星（1）'):
            if needle not in text:
                failures.append('索引缺 %r' % needle)
        if out.read_text(encoding='utf-8') != text:
            failures.append('写盘与内存不一致')
    if failures:
        print('gen-index.py selftest FAILED:')
        for f in failures:
            print('  - ' + f)
        return 1
    print('gen-index.py selftest ok')
    return 0


if __name__ == '__main__':
    sys.exit(main())
