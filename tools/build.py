#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build.py — Markdown 字谜 → data/riddles.json + data/checksums.json

内容仓的「编译」步骤：把 `riddles/**/*.md`（唯一事实源）编译成
机读数据。分站、玩法、索引都只读这份 `riddles.json`，不直接读 md。

用法：
    python tools/build.py                 # 用仓库根目录，写到 data/
    python tools/build.py --root X --out Y   # 指向别的目录（自检/测试用）
    python tools/build.py --selftest        # 在临时目录跑通全流程，证明产物可复算

零依赖：纯 Python 标准库。
"""

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fm  # noqa: E402

# 篇目 frontmatter 里序列化进 riddles.json 的字段（固定顺序 → 产物可复算）
# structure 是解字台/字谜工坊用的拆解数据 {ops, result}，没有的篇目为 null（打字兜底）
FIELDS = [
    'id', 'title', 'answer', 'answer_len', 'type', 'subtype',
    'difficulty', 'author', 'era', 'source', 'license', 'copyright', 'tags',
    'structure',
]


def parse_riddle_file(path):
    """读一个 .md，返回 (frontmatter dict, 相对路径 str)。"""
    text = path.read_text(encoding='utf-8')
    data, _body = fm.parse_frontmatter(text)
    return data, path


def collect(riddles_dir):
    """扫 riddles 目录，返回按 (type, difficulty, id) 排序的谜目列表。"""
    out = []
    if not riddles_dir.exists():
        return out
    for p in sorted(riddles_dir.rglob('*.md')):
        if p.name == '索引.md':
            continue  # 生成的索引不是内容
        data, _ = parse_riddle_file(p)
        rec = {}
        for f in FIELDS:
            rec[f] = data.get(f)
        rec['path'] = p.relative_to(riddles_dir.parent).as_posix()
        out.append(rec)
    out.sort(key=lambda r: (str(r.get('type') or ''), r.get('difficulty') or 0, str(r.get('id') or '')))
    return out


def type_counts(riddles):
    c = {}
    for r in riddles:
        t = r.get('type')
        if t:
            c[t] = c.get(t, 0) + 1
    return c


def build(riddles_dir, out_dir):
    riddles = collect(riddles_dir)
    payload = {
        'version': 1,
        'count': len(riddles),
        'types': type_counts(riddles),
        'riddles': riddles,
    }
    json_text = json.dumps(payload, ensure_ascii=False, indent=2) + '\n'

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'riddles.json').write_text(json_text, encoding='utf-8')

    # checksums：每个源 md 的 sha256（相对路径 → 哈希），供消费端校验未被篡改
    sums = {}
    for p in sorted(riddles_dir.rglob('*.md')):
        if p.name == '索引.md':
            continue
        rel = p.relative_to(riddles_dir).as_posix()
        sums[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    sums_text = json.dumps(sums, ensure_ascii=False, indent=2, sort_keys=True) + '\n'
    (out_dir / 'checksums.json').write_text(sums_text, encoding='utf-8')
    return payload


def main(argv=None):
    ap = argparse.ArgumentParser(description='Markdown 字谜 → riddles.json')
    ap.add_argument('--root', default=str(ROOT), help='仓库根目录（默认本仓）')
    ap.add_argument('--out', default=None, help='输出目录（默认 <root>/data）')
    ap.add_argument('--selftest', action='store_true', help='在临时目录自检')
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    root = Path(args.root)
    out_dir = Path(args.out) if args.out else root / 'data'
    payload = build(root / 'riddles', out_dir)
    print('built %d riddles → %s' % (payload['count'], out_dir / 'riddles.json'))
    return 0


# -------------------------------------------------------- 自检
def selftest():
    """在临时目录造两个合法谜目 + 一个坏样本，验证 build 与复算一致。"""
    failures = []
    with tempfile.TemporaryDirectory() as td:
        tdr = Path(td)
        rdir = tdr / 'riddles'
        (rdir / '增损').mkdir(parents=True)
        good = (
            '---\n'
            'id: t1\n'
            'title: 山上还有山\n'
            'answer: 出\n'
            'answer_len: 1\n'
            'type: 增损\n'
            'difficulty: 1\n'
            'author: 佚名\n'
            'era: 清\n'
            'source: S1\n'
            'license: public-domain\n'
            'copyright: { text: public-domain, annotations: cc-by-4.0 }\n'
            'tags: [叠字]\n'
            '---\n\n# 山上还有山\n\n**谜面**：山上还有山\n**谜底**：出\n\n## 解析\n两山相叠为出。\n'
        )
        (rdir / '增损' / '山上还有山.md').write_text(good, encoding='utf-8')
        out1 = tdr / 'out1'
        build(rdir, out1)
        j1 = json.loads((out1 / 'riddles.json').read_text(encoding='utf-8'))
        c1 = (out1 / 'checksums.json').read_text(encoding='utf-8')

        # 再跑一次：产物必须逐字节一致（可复算）
        out2 = tdr / 'out2'
        build(rdir, out2)
        j2 = json.loads((out2 / 'riddles.json').read_text(encoding='utf-8'))
        c2 = (out2 / 'checksums.json').read_text(encoding='utf-8')

        if j1 != j2:
            failures.append('两次构建产物不一致（不可复算）')
        if c1 != c2:
            failures.append('两次 checksums 不一致')
        if j1['count'] != 1:
            failures.append('应只有 1 个谜目，实得 %s' % j1['count'])
        if j1['riddles'][0]['id'] != 't1' or j1['riddles'][0]['answer'] != '出':
            failures.append('谜目字段解析错误：%s' % j1['riddles'][0])
        if '增损/山上还有山.md' not in j1['riddles'][0]['path']:
            failures.append('path 未记录：%s' % j1['riddles'][0]['path'])
        if len(j1['types']) != 1 or j1['types'].get('增损') != 1:
            failures.append('types 统计错误：%s' % j1['types'])
        # checksums 必须覆盖该文件
        if not any('山上还有山.md' in k for k in __import__('json').loads(c1)):
            failures.append('checksums 未覆盖源文件')
        # 无 structure 的篇目必须是 null（打字兜底），不能是缺键或字符串
        if j1['riddles'][0].get('structure') is not None:
            failures.append('未标注 structure 应为 null：%s' % j1['riddles'][0]['structure'])

        # 带行内嵌套 structure 的篇目：fm 递归解析 → dict 完整往返进 riddles.json
        # （structure 必须真的一行写完——fm 按行解析，拆行会被当成新键，正好被这个用例挡住）
        rich = good.replace(
            'tags: [叠字]\n',
            'tags: [叠字]\n'
            'structure: { ops: [{ part: 山, from: 山, op: full }, { part: 山, from: 山, op: full }], result: 出 }\n',
        )
        (rdir / '增损' / '山上还有山.md').write_text(rich, encoding='utf-8')
        out4 = tdr / 'out4'
        build(rdir, out4)
        j4 = json.loads((out4 / 'riddles.json').read_text(encoding='utf-8'))
        st = j4['riddles'][0].get('structure')
        ok_st = (
            isinstance(st, dict)
            and st.get('result') == '出'
            and isinstance(st.get('ops'), list) and len(st['ops']) == 2
            and all(isinstance(o, dict) and o.get('op') == 'full'
                    and o.get('part') == '山' and o.get('from') == '山'
                    for o in st['ops'])
        )
        if not ok_st:
            failures.append('structure 嵌套解析失败：%r' % (st,))
        # 还原成无 structure，保证后面的索引用例不受影响
        (rdir / '增损' / '山上还有山.md').write_text(good, encoding='utf-8')

        # 索引.md 不应被当成内容
        (rdir / '增损' / '索引.md').write_text('# 索引\n', encoding='utf-8')
        out3 = tdr / 'out3'
        build(rdir, out3)
        j3 = json.loads((out3 / 'riddles.json').read_text(encoding='utf-8'))
        if j3['count'] != 1:
            failures.append('索引.md 被当成谜目收录（count=%s）' % j3['count'])

    if failures:
        print('build.py selftest FAILED:')
        for f in failures:
            print('  - ' + f)
        return 1
    print('build.py selftest ok')
    return 0


if __name__ == '__main__':
    sys.exit(main())
