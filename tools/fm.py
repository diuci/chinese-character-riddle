#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fm.py — 极简 frontmatter 解析器（零依赖，纯标准库）

只支持本仓用到的 YAML 子集：
    - `key: value`            （value 可为 int / 裸字符串 / 引号字符串）
    - `key: [a, b, c]`        （行内列表，元素递归解析 → 可嵌套 {…} 映射）
    - `key: { a: b, c: d }`   （行内映射，值递归解析 → 可嵌套 […] 列表）
    - `key: null` / 空        （None）

嵌套支持（structure 拆解数据需要）：列表元素与映射的值都按「值」递归解析，
因此 `[{ part: 上, from: 上, op: full }]` 会得到 dict 列表，
而不是一串原始字符串。行内形式是刻意的：解析器不碰块式 YAML，
structure 必须写成一行（换行会被当成新键）。

不引第三方库，是为了让工具链在 CI 上无需 pip install 就能跑。
解析失败会抛 `FmError`，由调用方决定是报错还是自检。
"""

import re


class FmError(ValueError):
    """frontmatter 解析错误。"""


_INT_RE = re.compile(r'^-?\d+$')
# 行内值：裸串 / "引号" / '引号' / 负数
_SCALAR_RE = re.compile(r'^(?:"([^"]*)"|\'([^\']*)\'|(-?\d+)|(.+))$')


def _parse_scalar(token):
    """把一个行内标量 token 解析成 int / str / None。"""
    token = token.strip()
    if token == '' or token == 'null' or token == '~':
        return None
    m = _SCALAR_RE.match(token)
    if not m:
        raise FmError('无法解析标量：%r' % token)
    dq, sq, num, plain = m.groups()
    if dq is not None:
        return dq
    if sq is not None:
        return sq
    if num is not None:
        return int(num)
    return plain.strip()


def _split_inline(value):
    """按顶层逗号切分行内列表/映射项（忽略引号与括号内的逗号）。"""
    items, depth, quote, buf = [], 0, None, []
    for ch in value:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in ('"', "'"):
            quote = ch
            buf.append(ch)
        elif ch in '[{':
            depth += 1
            buf.append(ch)
        elif ch in ']}':
            depth -= 1
            buf.append(ch)
        elif ch == ',' and depth == 0:
            items.append(''.join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    tail = ''.join(buf).strip()
    if tail:
        items.append(tail)
    return items


def parse_frontmatter(text):
    """从 markdown 文本里解析 frontmatter，返回 (dict, body)。

    没有 frontmatter（不以 `---` 起头）时返回 ({}, text)。
    解析出的 dict 保持字段出现顺序（Python 3.7+ 有序 dict）。
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != '---':
        return {}, text

    # 找结束符
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end = i
            break
    if end is None:
        raise FmError('frontmatter 未闭合（找不到结束的 ---）')

    fm_lines = lines[1:end]
    body = '\n'.join(lines[end + 1:])
    data = {}
    for raw in fm_lines:
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        if ':' not in line:
            raise FmError('frontmatter 行缺少冒号：%r' % line)
        key, _, rest = line.partition(':')
        key = key.strip()
        val = rest.strip()
        data[key] = _parse_value(val)
    return data, body


def _parse_value(val):
    if val == '':
        return None
    if val.startswith('[') and val.endswith(']'):
        inner = val[1:-1].strip()
        if not inner:
            return []
        # 列表元素递归按「值」解析：{…} 项才能得到映射而不是字符串
        return [_parse_value(x) for x in _split_inline(inner)]
    if val.startswith('{') and val.endswith('}'):
        inner = val[1:-1].strip()
        out = {}
        if inner:
            for part in _split_inline(inner):
                k, _, v = part.partition(':')
                # 映射的值同样递归：{ ops: [{…}], result: 卡 } 这种嵌套才立得住。
                # v 必须先 strip——partition 后的值带前导空格，不去掉就会
                # 错过列表/映射分支、退化成纯字符串（自检当场抓到过）。
                out[k.strip()] = _parse_value(v.strip())
        return out
    return _parse_scalar(val)
