#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate.py — 字谜内容仓十一项校验（任何一项失败即 exit 1）

沿用「文档即契约」：docs/scope.md 里的收录清单是第 1 项的可执行契约。
每个检查都是一个纯函数 `checkN(riddles, ctx) -> [错误串]`，这样
`--selftest` 可以直接拿坏样本喂给单个检查，证明它真的拦得住坏例子，
而不是摆设。

十一项校验：
    1. 收录范围完整性  —— scope.md 要求收录的必须齐，框架外的不得多收
    2. id 唯一性       —— 全库 id 不重复
    3. 谜底字段        —— answer 非空、answer_len 与 answer 字数一致
    4. 难度合法        —— difficulty 必须在 1–5
    5. 台账完整        —— 缺 source / license 的篇目
    6. 版权核验        —— license=cc-by-4.0 必须是我方原创（authors.json 里 ours=true）
    7. frontmatter    —— 必填字段齐全
    8. 公版证据        —— license=public-domain 且 era=当代 的署名作者，卒年须 ≤ 当前年−50
    9. 去重            —— 谜面完全重复或互为子串，须登记 known-defects.json
    10. 谜种合法       —— type 必须取自合法集
    11. 拆解自洽       —— structure 拆解数据的形状与自洽性（没有该数据的篇目跳过，走打字兜底）

用法：
    python tools/validate.py             # 完整校验（第 1 项生效）
    python tools/validate.py --partial   # 增量期：跳过第 1 项「收录范围」
    python tools/validate.py --selftest  # 证明每个护栏抓得住坏样本
"""

import datetime
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RIDDLES_DIR = ROOT / 'riddles'
SCOPE = ROOT / 'docs' / 'scope.md'
AUTHORS = ROOT / 'data' / 'authors.json'
DEFECTS = ROOT / 'data' / 'known-defects.json'
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fm  # noqa: E402

# 必填字段（第 7 项）。copyright 允许为 dict 或缺失时报错，下面单独处理。
REQUIRED = ['id', 'title', 'answer', 'answer_len', 'type', 'difficulty',
            'author', 'era', 'source', 'license']

# 谜种合法集（第 10 项），与 docs/scope.md 的分类一致。
TYPES = ['拆字', '会意', '谐音', '增损', '离合', '典故', '象形', '方位', '数字', '当代']

# 拆解操作合法集（第 11 项）。part 永远是「拼装时用的那个部件字」：
#   full   全取（part 必须等于 from）
#   half   取左半（如 推 → 扌）   half_r  取右半（如 推 → 京）
#   part   取某部件，不问方位（字形部件，如 夜 → 夕、草 → 艹）
#   free   会意取件：部件不是 from 的字形部件，而是由 from 所在的谜面句子
#          会意得出（如 绿 → 禾、一家 → 门、十五天 → 半月）
#   minus  减笔（如 山 减一横 → 彐）   plus  加笔
STRUCT_OPS = ['full', 'half', 'half_r', 'part', 'free', 'minus', 'plus']

# 我国《著作权法》：自然人作品保护期为作者终生及其死亡后第 50 年的 12 月 31 日。
COPYRIGHT_YEARS = 50

# 调色
class C:
    OK, FAIL, WARN, BOLD, DIM, END = '\033[32m', '\033[31m', '\033[33m', '\033[1m', '\033[2m', '\033[0m'
    @classmethod
    def off(cls):
        for k in ('OK', 'FAIL', 'WARN', 'BOLD', 'DIM', 'END'):
            setattr(cls, k, '')
if not sys.stdout.isatty():
    C.off()


# -------------------------------------------------- 装载
def load_riddles(riddles_dir):
    """返回 [(rec, relpath)]，rec 是 frontmatter dict。跳过 索引.md。

    另带 __body__（frontmatter 之后的正文）供第 11 项核「from 在谜面或解析」，
    双下划线键不会被 build.py 的 FIELDS 白名单序列化。
    """
    out = []
    if not riddles_dir.exists():
        return out
    for p in sorted(riddles_dir.rglob('*.md')):
        if p.name == '索引.md':
            continue
        data, body = fm.parse_frontmatter(p.read_text(encoding='utf-8'))
        data['__body__'] = body
        data['__path__'] = p.relative_to(riddles_dir).as_posix()
        out.append(data)
    return out


def load_authors(path):
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding='utf-8'))
    return {a.get('name'): a for a in raw.get('authors', [])}


def load_defects(path):
    if not path.exists():
        return set()
    raw = json.loads(path.read_text(encoding='utf-8'))
    return {d.get('key') for d in raw.get('defects', []) if d.get('key')}


def parse_scope(path):
    """解析 scope.md 的「收录清单（契约）」表 → {id: (type, answer)}。"""
    if not path.exists():
        return {}
    text = path.read_text(encoding='utf-8')
    out = {}
    in_sec = False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith('## ') and '收录清单' in s:
            in_sec = True
            continue
        if in_sec and s.startswith('## '):
            break
        if not in_sec or not s.startswith('|'):
            continue
        cells = [c.strip() for c in s.strip('|').split('|')]
        if len(cells) < 3:
            continue
        idc, typ, ans = cells[0], cells[1], cells[2]
        if idc in ('id', '') or set(idc) <= set('-: '):
            continue  # 表头 / 分隔行
        out[idc] = (typ, ans)
    return out


# -------------------------------------------------- 十个检查（纯函数）
def check1_scope(riddles, scope):
    errs = []
    have = {r.get('id'): r for r in riddles}
    for sid in sorted(scope):
        if sid not in have:
            errs.append('收录清单要求收录但缺失：%s' % sid)
            continue
        typ, ans = scope[sid]
        r = have[sid]
        if typ and r.get('type') != typ:
            errs.append('%s 谜种不符：清单=%s 实=%s' % (sid, typ, r.get('type')))
        if ans and str(r.get('answer')) != ans:
            errs.append('%s 谜底不符：清单=%s 实=%s' % (sid, ans, r.get('answer')))
    for r in riddles:
        if r.get('id') not in scope:
            errs.append('多收框架外篇目：%s（%s）' % (r.get('id'), r.get('title')))
    return errs


def check2_id_unique(riddles):
    seen, errs = {}, []
    for r in riddles:
        i = r.get('id')
        if i is None:
            continue  # 第 7 项会报缺 id
        if i in seen:
            errs.append('id 重复：%s（%s 与 %s）' % (i, seen[i], r.get('__path__')))
        else:
            seen[i] = r.get('__path__')
    return errs


def check3_answer(riddles):
    errs = []
    for r in riddles:
        a = r.get('answer')
        if a is None or str(a).strip() == '':
            errs.append('%s 谜底为空' % r.get('id'))
            continue
        al = r.get('answer_len')
        if al is not None and int(al) != len(str(a)):
            errs.append('%s answer_len=%s 与谜底字数 %d 不符' % (r.get('id'), al, len(str(a))))
    return errs


def check4_difficulty(riddles):
    errs = []
    for r in riddles:
        d = r.get('difficulty')
        if d is None:
            continue  # 第 7 项报缺
        try:
            d = int(d)
        except (TypeError, ValueError):
            errs.append('%s difficulty 非整数：%r' % (r.get('id'), d))
            continue
        if not (1 <= d <= 5):
            errs.append('%s difficulty=%s 超出 1–5' % (r.get('id'), d))
    return errs


def check5_ledger(riddles):
    errs = []
    for r in riddles:
        for f in ('source', 'license'):
            if not r.get(f):
                errs.append('%s 缺台账字段：%s' % (r.get('id'), f))
    return errs


def check6_copyright(riddles, authors):
    """cc-by-4.0 的原文必须是我方原创。"""
    errs = []
    for r in riddles:
        lic = r.get('license')
        if lic != 'cc-by-4.0':
            continue
        a = authors.get(r.get('author'))
        if not a or not a.get('ours'):
            errs.append('%s 原文为 cc-by-4.0 但作者 %r 非我方原创（authors.json 无 ours=true）'
                        % (r.get('id'), r.get('author')))
    return errs


def check7_frontmatter(riddles):
    errs = []
    for r in riddles:
        missing = [f for f in REQUIRED if r.get(f) in (None, '')]
        if missing:
            errs.append('%s 缺必填字段：%s' % (r.get('id'), '/'.join(missing)))
        if not isinstance(r.get('copyright'), dict):
            errs.append('%s copyright 必须是映射 {text, annotations}' % r.get('id'))
    return errs


def check8_publicdomain(riddles, authors, year):
    """public-domain 且 era=当代 的署名作者，卒年须 ≤ 当前年−50。"""
    errs = []
    cutoff = year - COPYRIGHT_YEARS
    for r in riddles:
        if r.get('license') != 'public-domain':
            continue
        if r.get('era') != '当代':
            continue  # 古典 / 匿名 → 显然公版
        author = r.get('author')
        if author in (None, '', '佚名'):
            continue
        a = authors.get(author)
        if a is None:
            errs.append('%s 当代署名作者 %r 不在 authors.json' % (r.get('id'), author))
            continue
        died = a.get('died')
        if died is None:
            errs.append('%s 当代作者 %r 缺卒年（仍在保护期）' % (r.get('id'), author))
        elif died > cutoff:
            errs.append('%s 作者 %r 卒于 %s，晚于「当前年 − 50 = %d」，仍在保护期'
                        % (r.get('id'), author, died, cutoff))
    return errs


def check9_dedup(riddles, defects):
    """完全重复或互为子串的谜面，须登记 known-defects。"""
    errs = []
    titles = [(str(r.get('title')), r.get('id')) for r in riddles if r.get('title')]
    for i in range(len(titles)):
        for j in range(i + 1, len(titles)):
            t1, id1 = titles[i]
            t2, id2 = titles[j]
            if t1 == t2 or t1 in t2 or t2 in t1:
                if id1 not in defects and id2 not in defects:
                    errs.append('谜面重复/包含未登记：%r(%s) 与 %r(%s)' % (t1, id1, t2, id2))
    return errs


def check10_type(riddles):
    errs = []
    for r in riddles:
        t = r.get('type')
        if t is None:
            continue  # 第 7 项报缺
        if t not in TYPES:
            errs.append('%s 谜种非法：%r（合法集：%s）' % (r.get('id'), t, '/'.join(TYPES)))
    return errs


def check11_structure(riddles):
    """structure 拆解数据的形状与自洽性。

    只查「形状 + 声明自洽」：部件怎么拼成 result（拼装关系）没有
    程序化数据可验（无 IDS 部件库），部件选得对不对靠人审与玩法呈现。
    没写 structure 的篇目直接跳过 —— 打字兜底是合法状态，不是缺失。
    """
    errs = []
    for r in riddles:
        st = r.get('structure')
        if st is None:
            continue
        rid = r.get('id')
        if not isinstance(st, dict):
            errs.append('%s structure 必须是映射 {ops, result}，实得 %s'
                        % (rid, type(st).__name__))
            continue
        ops = st.get('ops')
        result = st.get('result')
        if not isinstance(ops, list) or not ops:
            errs.append('%s structure.ops 必须是非空列表' % rid)
            continue
        if result is None or str(result) == '':
            errs.append('%s structure.result 缺失' % rid)
            continue
        if str(result) != str(r.get('answer')):
            errs.append('%s 拆解结果 %r 与谜底 %r 不一致'
                        % (rid, result, r.get('answer')))
        title = str(r.get('title') or '')
        hay = title + str(r.get('__body__') or '')  # from 允许出自谜面或解析
        for i, op in enumerate(ops):
            where = '%s structure.ops[%d]' % (rid, i)
            if not isinstance(op, dict):
                errs.append('%s 必须是映射 {part, from, op}' % where)
                continue
            o = op.get('op')
            frm = op.get('from')
            part = op.get('part')
            if o not in STRUCT_OPS:
                errs.append('%s op 非法：%r（合法集：%s）' % (where, o, '/'.join(STRUCT_OPS)))
            if frm is None or len(str(frm)) != 1:
                errs.append('%s from 必须是单字，实得 %r' % (where, frm))
            elif str(frm) not in hay:
                errs.append('%s from %r 不在谜面或解析里' % (where, frm))
            if part is None or len(str(part)) != 1:
                errs.append('%s part 必须是单字部件，实得 %r' % (where, part))
            elif o == 'full' and str(part) != str(frm):
                errs.append('%s op=full 时 part 必须等于 from' % where)
    return errs


# -------------------------------------------------- 汇总
def run_checks(riddles, ctx, partial=False):
    scope, authors, defects, year = ctx['scope'], ctx['authors'], ctx['defects'], ctx['year']
    groups = [
        ('收录范围完整性', check1_scope(riddles, scope), partial),
        ('id 唯一性', check2_id_unique(riddles), False),
        ('谜底字段', check3_answer(riddles), False),
        ('难度合法', check4_difficulty(riddles), False),
        ('台账完整', check5_ledger(riddles), False),
        ('版权核验', check6_copyright(riddles, authors), False),
        ('frontmatter', check7_frontmatter(riddles), False),
        ('公版证据', check8_publicdomain(riddles, authors, year), False),
        ('去重', check9_dedup(riddles, defects), False),
        ('谜种合法', check10_type(riddles), False),
        ('拆解自洽', check11_structure(riddles), False),
    ]
    total_err, total_warn = 0, 0
    for name, errs, skipped in groups:
        if skipped:
            print('%s [skip] %s（--partial）' % (C.DIM, name))
            continue
        if errs:
            total_err += len(errs)
            print('%s [FAIL] %s：%d 项' % (C.FAIL, name, len(errs)))
            for e in errs:
                print('         - ' + e)
        else:
            print('%s [ok] %s' % (C.OK, name))
    n_st = sum(1 for r in riddles if r.get('structure'))
    print('%s[info] 拆解数据覆盖：%d / %d 篇（其余走打字兜底）%s' % (C.DIM, n_st, len(riddles), C.END))
    return total_err


def ctx_for(root):
    return {
        'scope': parse_scope(root / 'docs' / 'scope.md'),
        'authors': load_authors(root / 'data' / 'authors.json'),
        'defects': load_defects(root / 'data' / 'known-defects.json'),
        'year': datetime.date.today().year,
    }


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    partial = '--partial' in argv
    if '--selftest' in argv:
        return selftest()
    root = ROOT
    riddles = load_riddles(root / 'riddles')
    ctx = ctx_for(root)
    errs = run_checks(riddles, ctx, partial)
    print()
    if errs:
        print('%s%d 项校验共 %d 个错误%s' % (C.FAIL, 11, errs, C.END))
        return 1
    print('%s十一项校验全绿（%d 篇谜目）%s' % (C.OK, len(riddles), C.END))
    return 0


# -------------------------------------------------- 自检：每个护栏必须抓得住坏样本
def selftest():
    def rec(**kw):
        base = dict(id='x', title='谜面', answer='出', answer_len=1, type='增损',
                    difficulty=1, author='佚名', era='清', source='S1',
                    license='public-domain', copyright={'text': 'public-domain',
                                                        'annotations': 'cc-by-4.0'})
        base.update(kw)
        return base

    authors = {'丢词大作战': {'ours': True, 'died': None},
               '在世作者': {'ours': False, 'died': 2020}}
    cases = [
        ('check1 收录范围', lambda: check1_scope([rec(id='a')], {'b': ('增损', '出')})),
        ('check1 多收框架外', lambda: check1_scope([rec(id='a')], {})),
        ('check2 id 重复', lambda: check2_id_unique([rec(id='a'), rec(id='a', title='别的')])),
        ('check3 谜底为空', lambda: check3_answer([rec(answer=None)])),
        ('check3 字数不符', lambda: check3_answer([rec(answer='出山', answer_len=1)])),
        ('check4 难度越界', lambda: check4_difficulty([rec(difficulty=9)])),
        ('check5 缺台账', lambda: check5_ledger([rec(source=None)])),
        ('check6 非我方 cc-by', lambda: check6_copyright([rec(license='cc-by-4.0', author='别人')], authors)),
        ('check7 缺必填', lambda: check7_frontmatter([rec(type=None)])),
        ('check8 当代未过保护期', lambda: check8_publicdomain(
            [rec(license='public-domain', era='当代', author='在世作者')], authors, 2026)),
        ('check9 谜面重复', lambda: check9_dedup([rec(title='谜面'), rec(id='y', title='谜面')], set())),
        ('check10 谜种非法', lambda: check10_type([rec(type='乱造')])),
        # check11 坏样本：七个角度
        ('check11 structure 非映射', lambda: check11_structure([rec(structure=' ops ')])),
        ('check11 ops 空列表', lambda: check11_structure(
            [rec(structure={'ops': [], 'result': '出'})])),
        ('check11 result 缺失', lambda: check11_structure(
            [rec(structure={'ops': [{'part': '山', 'from': '山', 'op': 'full'}]})])),
        ('check11 result 与谜底不符', lambda: check11_structure(
            [rec(structure={'ops': [{'part': '山', 'from': '山', 'op': 'full'}], 'result': '山'})])),
        ('check11 op 非法', lambda: check11_structure(
            [rec(structure={'ops': [{'part': '山', 'from': '山', 'op': 'swap'}], 'result': '出'})])),
        ('check11 from 不在谜面', lambda: check11_structure(
            [rec(structure={'ops': [{'part': '口', 'from': '口', 'op': 'full'}], 'result': '出'})])),
        ('check11 part 非单字', lambda: check11_structure(
            [rec(structure={'ops': [{'part': '山山', 'from': '山', 'op': 'full'}], 'result': '出'})])),
        ('check11 full 但 part 不等于 from', lambda: check11_structure(
            [rec(structure={'ops': [{'part': '口', 'from': '山', 'op': 'full'}], 'result': '出'})])),
        ('check11 op 项非映射', lambda: check11_structure(
            [rec(structure={'ops': ['山'], 'result': '出'})])),
    ]
    failures = []
    for name, fn in cases:
        try:
            errs = fn()
        except Exception as e:  # noqa: BLE001
            failures.append('%s 抛异常：%s' % (name, e))
            continue
        if not errs:
            failures.append('%s 没抓到坏样本（护栏是摆设）' % name)
    # 反向：干净样本必须全过
    clean = [rec(id='a', title='谜面A'), rec(id='b', title='谜面B', type='会意', answer='心',
                                                answer_len=1, difficulty=2)]
    for name, fn in [('clean-check1', lambda: check1_scope(clean,
                            {'a': ('增损', '出'), 'b': ('会意', '心')})),
                     ('clean-check2', lambda: check2_id_unique(clean)),
                     ('clean-check3', lambda: check3_answer(clean)),
                     ('clean-check4', lambda: check4_difficulty(clean)),
                     ('clean-check5', lambda: check5_ledger(clean)),
                     ('clean-check6', lambda: check6_copyright(clean, authors)),
                     ('clean-check7', lambda: check7_frontmatter(clean)),
                     ('clean-check8', lambda: check8_publicdomain(clean, authors, 2026)),
                     ('clean-check9', lambda: check9_dedup(clean, set())),
                     ('clean-check10', lambda: check10_type(clean)),
                     ('clean-check11', lambda: check11_structure(clean)),
                     ('clean-check11 拆解合法', lambda: check11_structure(
                         [rec(id='s', title='山上还有山',
                              structure={'ops': [{'part': '山', 'from': '山', 'op': 'full'},
                                                 {'part': '山', 'from': '山', 'op': 'full'}],
                                        'result': '出'})])),
                     ('clean-check11 无structure跳过', lambda: check11_structure([rec(id='p')])),
                     ('clean-check11 from在解析', lambda: check11_structure(
                         [rec(id='q', title='谜面X', __body__='解析里提到「手」',
                              structure={'ops': [{'part': '手', 'from': '手', 'op': 'free'}],
                                        'result': '出'})]))]:
        try:
            errs = fn()
        except Exception as e:  # noqa: BLE001
            failures.append('%s 干净样本抛异常：%s' % (name, e))
            continue
        if errs:
            failures.append('%s 干净样本被误报：%s' % (name, errs))
    if failures:
        print('validate.py selftest FAILED:')
        for f in failures:
            print('  - ' + f)
        return 1
    print('validate.py selftest ok（%d 个坏样本全部拦下，%d 个干净样本无误报）'
          % (len(cases), 13))
    return 0


if __name__ == '__main__':
    sys.exit(main())
