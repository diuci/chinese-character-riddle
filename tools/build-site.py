#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build-site.py — 从内容生成浏览站的站点副本

把 `riddles/**/*.md` 拷到 `site/riddles/`（VitePress 直接渲染成页面），
并从 `data/riddles.json` 生成 `site/public/catalog.json` 与 `site/riddles/索引.md`。
站点侧的页面骨架（index/guide/sources/print）是手写的，不进本脚本。

用法：
    python tools/build-site.py            # 用本仓
    python tools/build-site.py --selftest # 临时目录自检

零依赖。产物可复算（同输入同输出）。
"""

import argparse
import json
import sys
import tempfile
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def build(root):
    riddles_dir = root / 'riddles'
    site_dir = root / 'site'
    data_json = root / 'data' / 'riddles.json'
    out_riddles = site_dir / 'riddles'
    out_public = site_dir / 'public'

    payload = {}
    if data_json.exists():
        payload = json.loads(data_json.read_text(encoding='utf-8'))

    # 清空旧的 site/riddles 与 catalog，避免残留
    if out_riddles.exists():
        shutil.rmtree(out_riddles)
    out_riddles.mkdir(parents=True, exist_ok=True)
    out_public.mkdir(parents=True, exist_ok=True)

    copied = 0
    for p in sorted(riddles_dir.rglob('*.md')):
        if p.name == '索引.md':
            continue  # 索引单独生成
        rel = p.relative_to(riddles_dir)
        dest = out_riddles / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, dest)
        copied += 1

    # catalog.json：站点首页与筛选用
    catalog = {
        'version': payload.get('version', 1),
        'count': payload.get('count', 0),
        'types': payload.get('types', {}),
        'riddles': payload.get('riddles', []),
    }
    (out_public / 'catalog.json').write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    # 索引页：从 riddles.json 渲染成 markdown，作为浏览入口
    index_text = render_index(payload.get('riddles', []))
    (out_riddles / '索引.md').write_text(index_text, encoding='utf-8')
    return copied, payload.get('count', 0)


def render_index(riddles):
    lines = ['# 字谜索引', '',
             '> 由 `tools/build-site.py` 从 `data/riddles.json` 生成，共 %d 篇。' % len(riddles), '',
             '按谜种分组，组内按难度排序。']
    bytype = {}
    for r in riddles:
        bytype.setdefault(str(r.get('type') or '?'), []).append(r)
    for t in sorted(bytype):
        items = sorted(bytype[t], key=lambda r: (r.get('difficulty') or 0, str(r.get('id') or '')))
        lines.append('')
        lines.append('## %s（%d）' % (t, len(items)))
        lines.append('')
        for r in items:
            lines.append('- [%s](%s) → **%s**（难度 %d）' % (
                r.get('title'), r.get('path').replace('riddles/', '', 1), r.get('answer'), r.get('difficulty') or 0))
    return '\n'.join(lines).rstrip() + '\n'


def selftest():
    with tempfile.TemporaryDirectory() as td:
        tdr = Path(td)
        (tdr / 'riddles' / '增损').mkdir(parents=True)
        (tdr / 'riddles' / '增损' / '山上还有山.md').write_text(
            '---\nid: t\ntitle: 山上还有山\nanswer: 出\nanswer_len: 1\ntype: 增损\n'
            'difficulty: 1\nauthor: 佚名\nera: 清\nsource: S1\nlicense: public-domain\n'
            'copyright: { text: public-domain, annotations: cc-by-4.0 }\n---\n\n# 山上还有山\n', encoding='utf-8')
        (tdr / 'data').mkdir()
        (tdr / 'data' / 'riddles.json').write_text(json.dumps({
            'version': 1, 'count': 1, 'types': {'增损': 1},
            'riddles': [{'id': 't', 'title': '山上还有山', 'answer': '出', 'answer_len': 1,
                         'type': '增损', 'difficulty': 1, 'author': '佚名', 'era': '清',
                         'source': 'S1', 'license': 'public-domain',
                         'copyright': {'text': 'public-domain', 'annotations': 'cc-by-4.0'},
                         'tags': [], 'path': 'riddles/增损/山上还有山.md'}]}), encoding='utf-8')
        copied, count = build(tdr)
        failures = []
        if copied != 1:
            failures.append('应拷贝 1 个谜目，实 %d' % copied)
        if count != 1:
            failures.append('catalog count 错')
        if not (tdr / 'site' / 'riddles' / '增损' / '山上还有山.md').exists():
            failures.append('谜目页未生成')
        if not (tdr / 'site' / 'public' / 'catalog.json').exists():
            failures.append('catalog.json 未生成')
        if not (tdr / 'site' / 'riddles' / '索引.md').exists():
            failures.append('索引页未生成')
        cat = json.loads((tdr / 'site' / 'public' / 'catalog.json').read_text(encoding='utf-8'))
        if cat.get('count') != 1 or cat.get('types', {}).get('增损') != 1:
            failures.append('catalog 内容错：%s' % cat)
    if failures:
        print('build-site.py selftest FAILED:')
        for f in failures:
            print('  - ' + f)
        return 1
    print('build-site.py selftest ok')
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description='生成浏览站站点副本')
    ap.add_argument('--root', default=str(ROOT))
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    root = Path(args.root)
    copied, count = build(root)
    print('built site: %d riddle pages, catalog %d' % (copied, count))
    return 0


if __name__ == '__main__':
    sys.exit(main())
