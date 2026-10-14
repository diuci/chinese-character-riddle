#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把字谜内容（谜面 / 谜底 / 解析 / 出处 / 界面词）从简体派生为繁体。

这是全站繁简转换的**唯一一台引擎**。站点（zimi-site）不自己转繁简——
它只载入本引擎产出的派生产物 data/traditional.json，再渲染 /trad/ 页。
这里再写一台，就是允许两台给出不同答案（规范：转繁简的引擎只有一份）。

规矩（质量优先，宁缺毋滥）：
  1) 繁简表只收录本站真正用到的字；查不到的字原样保留（简体字留在繁体里 = 漏转，闸门拦）。
  2) 一个简体字对应多个繁体（复/里/干/发/余）——表里给候选，裁定表决定用哪个。
     裁定表没说的字，不许静默择一：build 时直接失败，逼你补裁定。
  3) 派生产物 traditional.json 逐字可复核：每个字的繁体形、依据（表/裁定/本来就那样）都记下。

用法：
    python tools/build-traditional.py            # 生成 data/traditional.json
    python tools/build-traditional.py --selftest # 证明闸门抓得住漏转 / 静默择一
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RIDDLES = ROOT / 'riddles'
OUT = ROOT / 'data' / 'traditional.json'

# ---------------------------------------------------------------- 繁简表
# 简体字 → 繁体候选（列表）。只有一个候选的写单元素列表，和歧义字同构，好统一处理。
# 只收录本站内容用到的字；没列出的字 = 繁简同形，原样保留。
STC = {
    '为': ['為'], '与': ['與'], '个': ['個'], '传': ['傳'], '仅': ['僅'],
    '创': ['創'], '剥': ['剝'], '减': ['減'], '叠': ['疊'], '层': ['層'],
    '属': ['屬'], '复': ['複', '復'], '头': ['頭'], '夹': ['夾'], '实': ['實'],
    '对': ['對'], '广': ['廣'], '张': ['張'], '弯': ['彎'], '归': ['歸'],
    '当': ['當'], '录': ['錄'], '态': ['態'], '战': ['戰'], '户': ['戶'],
    '挂': ['掛'], '损': ['損'], '据': ['據'], '数': ['數'], '断': ['斷'],
    '权': ['權'], '来': ['來'], '构': ['構'], '标': ['標'], '没': ['沒'],
    '点': ['點'], '状': ['狀'], '独': ['獨'], '画': ['畫'], '确': ['確'],
    '离': ['離'], '种': ['種'], '竖': ['豎'], '笔': ['筆'], '签': ['簽'],
    '类': ['類'], '组': ['組'], '结': ['結'], '绵': ['綿'], '编': ['編'],
    '见': ['見'], '讲': ['講'], '词': ['詞'], '诚': ['誠'], '话': ['話'],
    '说': ['說'], '读': ['讀'], '谐': ['諧'], '谜': ['謎'], '责': ['責'],
    '贯': ['貫'], '跃': ['躍'], '轮': ['輪'], '边': ['邊'], '过': ['過'],
    '还': ['還'], '这': ['這'], '进': ['進'], '远': ['遠'], '连': ['連'],
    '选': ['選'], '释': ['釋'], '里': ['裡', '裏'], '钩': ['鉤'], '键': ['鍵'],
    '长': ['長'], '门': ['門'], '闭': ['閉'], '问': ['問'], '间': ['間'],
    '阴': ['陰'], '隐': ['隱'], '难': ['難'], '顺': ['順'], '领': ['領'],
    '风': ['風'], '两': ['兩'], '会': ['會'], '势': ['勢'], '处': ['處'],
    '从': ['從'], '历': ['歷'], '余': ['餘'], '发': ['發', '髮'],
    '干': ['幹', '乾', '干'], '余': ['餘'],
}

# 裁定表：歧义字在**本站语境**下用哪个繁体，以及理由。
# key = 简体字，value = 用哪个候选 + 理由。没有裁定表的歧义字 = build 失败。
RULES = {
    '复': ('複', '本站只有「重复 / 复字」义，无「恢复 / 报复」义，取「複」。'),
    '里': ('裡', '本站「里」只表「内部 / 里面」（如「人在内里」），无里程义，取「裡」。'),
    '干': ('干', '本站「干」只作「干支 / 天干」义（增损谜「干」），非「乾燥 / 幹事」，保留「干」。'),
    '发': ('發', '本站「发」只表「发出 / 发明」义，无头发义，取「發」。'),
    '余': ('餘', '本站「余」只表「剩余」义，无第一人称义，取「餘」。'),
}


def is_cjk(ch):
    return '\u4e00' <= ch <= '\u9fff'


def convert(text, stc=STC, rules=RULES):
    """把一段简体文本转成繁体，返回 (trad, marks)。
    marks: 每个被转的字的记录 {ch, cands, pick, decision}。
    decision ∈ {'table','rule','identity'}。歧义字无裁定 → 抛错。
    """
    out = []
    marks = []
    for ch in text:
        if not is_cjk(ch) or ch not in stc:
            out.append(ch)
            continue
        cands = stc[ch]
        if len(cands) == 1:
            out.append(cands[0])
            marks.append({'ch': ch, 'cands': cands, 'pick': cands[0], 'decision': 'table'})
        else:
            if ch not in rules:
                raise ValueError('歧义字「%s」候选 %s 无裁定，不许静默择一' % (ch, '/'.join(cands)))
            pick, reason = rules[ch]
            if pick not in cands:
                raise ValueError('裁定「%s」=%s 不在候选 %s 里' % (ch, pick, '/'.join(cands)))
            out.append(pick)
            marks.append({'ch': ch, 'cands': cands, 'pick': pick, 'decision': 'rule', 'reason': reason})
    return ''.join(out), marks


def load_riddles():
    """读所有谜 md，提取要转的字段 + 整篇原文（供整篇转繁）。"""
    rows = []
    for f in sorted(RIDDLES.rglob('*.md')):
        if f.name == '索引.md':
            continue
        text = f.read_text(encoding='utf-8')
        if text.count('---') < 2:
            continue
        parts = text.split('---', 2)
        fm = parts[1]
        body = parts[2]
        def grab(key):
            for line in fm.splitlines():
                if line.strip().startswith(key + ':'):
                    return line.split(':', 1)[1].strip()
            return ''
        title = grab('title')
        answer = grab('answer')
        def section(name):
            import re
            m = re.search(r'##\s*%s\s*\n(.*?)(?=\n##|\Z)' % name, body, re.S)
            return m.group(1).strip() if m else ''
        jie = section('解析')
        chu = section('出处')
        rows.append({'id': grab('id'), 'title': title, 'answer': answer,
                     'jie': jie, 'chu': chu, 'full': text})
    return rows


# 界面词（UI 标签）：站点顶栏 / 侧栏 / 索引轴名 / 打印版等用到的固定词。
UI_WORDS = [
    '猜字谜', '索引', '谜面', '谜底', '解析', '出处', '谜种', '难度', '标签',
    '打印版', '指南', '数据来源', '版权与免责', '公版', '我方原创', '注释',
    '选篇编排', '拆字', '会意', '谐音', '增损', '离合', '典故', '象形',
    '方位', '数字', '当代', '繁体版', '简体版', '难度等级', '按谜种', '按难度',
    '按谜底', '按标签', '共', '篇', '难度', '谜种',
]


def build():
    rows = load_riddles()
    out_rows = []
    for r in rows:
        # 谜面 / 谜底 / 解析 / 出处 逐字段转
        title_t, m1 = convert(r['title'])
        answer_t, m2 = convert(r['answer'])
        jie_t, m3 = convert(r['jie'])
        chu_t, m4 = convert(r['chu'])
        marks = m1 + m2 + m3 + m4
        # 整篇繁体 md：frontmatter + 正文全转。站点直接写入 /trad/，不自己转。
        full_t, _ = convert(r['full'])
        out_rows.append({
            'id': r['id'],
            'title': r['title'], 'title_t': title_t,
            'answer': r['answer'], 'answer_t': answer_t,
            'jie': r['jie'], 'jie_t': jie_t,
            'chu': r['chu'], 'chu_t': chu_t,
            'body_t': full_t,
            'converted': len([m for m in marks if m['decision'] != 'identity']),
            'marks': marks,
        })
    # 界面词
    ui_out = {}
    for w in UI_WORDS:
        t, _ = convert(w)
        ui_out[w] = t
    doc = {
        'version': 1,
        'count': len(out_rows),
        'note': '繁简派生产物。引擎 tools/build-traditional.py 唯一事实源。',
        'rows': out_rows,
        'ui': ui_out,
        'rules': {k: {'pick': v[0], 'reason': v[1]} for k, v in RULES.items()},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding='utf-8')
    print('build-traditional: %d 篇 → %s' % (len(out_rows), OUT))
    return doc


def selftest():
    problems = []
    # 1) 歧义字无裁定 → 必须抛错（不许静默择一）
    try:
        convert('里面', {'里': ['裡', '裏']}, {})
        problems.append('无裁定的歧义字「里」没抛错')
    except ValueError:
        pass
    # 2) 歧义字有裁定 → 按裁定转
    t, _ = convert('里面', {'里': ['裡', '裏']}, {'里': ('裡', '内部义')})
    if t != '裡面':
        problems.append('「里面」应裁定转「裡面」，实为 %s' % t)
    # 3) 单候选字正常转，简体字不许留在繁体输出里（「重」繁简同形，不在列）
    t2, _ = convert('重复归来看过讲问', STC, RULES)
    for s in ('复', '归', '来', '过', '讲', '问'):
        if s in t2:
            problems.append('简体字「%s」漏转，仍留在繁体输出 %s' % (s, t2))
    if '過' not in t2 or '講' not in t2 or '問' not in t2:
        problems.append('繁体形缺失：過/講/問 未出现')
    # 4) 本来就繁简同形的字原样保留
    t3, _ = convert('山出夕', STC, RULES)
    if t3 != '山出夕':
        problems.append('同形字被误改：%s' % t3)
    if problems:
        print('build-traditional selftest FAILED:')
        for p in problems:
            print('  - ' + p)
        return 1
    print('build-traditional selftest ok')
    return 0


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        sys.exit(selftest())
    build()
