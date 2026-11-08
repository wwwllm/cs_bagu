# -*- coding: utf-8 -*-
"""把小林coding的 PDF 书转成按章节拆分的 Markdown（含插图）。v2

用法：.venv/bin/python convert2.py [书名关键字]
"""
import os, re, sys, time, json, glob, unicodedata
import pymupdf
import pymupdf4llm

SRC = "/Users/wlm/code/八股/小林coding合集PDF"
OUT = "/Users/wlm/code/八股/小林codingMarkdown"

# 每个书名只保留一个版本（亮白/浅色），暗黑版、浅黄版视为重复不处理
BOOKS = [
    ("图解网络", "图解网络-小林coding/图解网络-小林coding-亮白风格-v4.0.pdf"),
    ("图解系统", "图解系统-小林coding/图解系统-亮白风格-小林coding-v1.0.pdf"),
    ("图解MySQL", "图解MySQL-小林coding/图解MySQL-小林coding-亮白版-v2.0.pdf"),
    ("图解Redis", "图解Redis-小林coding/图解Redis-小林coding-亮白版-v2.0.pdf"),
    ("100道CPP面试题", "小林八股面试题汇总/100道+CPP面试题（基础+面向对象+STL+内存管理+新特性）-小林coding-v2.0.pdf"),
    ("100道Golang面试题", "小林八股面试题汇总/100道+Golang面试题（基础+数据类型+并发+GMP+内存管理+垃圾回收）-小林coding-v2.0.pdf"),
    ("150道MySQL+Redis面试题", "小林八股面试题汇总/150道MySQL+Redis面试题-小林coding-v2.0.pdf"),
    ("150道计算机网络+操作系统+数据结构与算法面试题", "小林八股面试题汇总/150道计算机网络+操作系统+数据结构与算法面试题-小林coding-v2.0.pdf"),
    ("300道Java面试题", "小林八股面试题汇总/300道+Java面试题（Java基础+集合+并发+JVM+Spring）-小林coding-v2.0.pdf"),
    ("30道Linux命令+Git面试题", "小林八股面试题汇总/30道Linux命令+Git面试题-小林coding-v2.0.pdf"),
    ("350道测试开发面试题", "小林八股面试题汇总/350道测试开发面试题-小林coding-v2.0.pdf"),
    ("50道消息队列+分布式+系统设计", "小林八股面试题汇总/50道消息队列+分布式+系统设计-小林coding-v2.0.pdf"),
    ("大厂后端面试真题", "小林八股面试题汇总/大厂后端面试真题-小林coding-白色.pdf"),
]

# ---------- 字符级修正 ----------
# 康熙部首（U+2F00-2FDF）NFKC 可解；CJK 部首补充区（U+2E80-2EFF）NFKC 无效，必须显式映射
RADICAL_MAP = {
    "\u2ed3": "长", "\u2eda": "页", "\u2ec9": "贝", "\u2ec5": "见", "\u2ed4": "门",
    "\u2ec6": "角", "\u2ec4": "西", "\u2edb": "风", "\u2ecb": "车", "\u2ee2": "马",
    "\u2edc": "飞", "\u2ea0": "民", "\u2eec": "齐", "\u2ee6": "鸟", "\u2ee4": "鬼",
    "\u2ef0": "龙", "\u2ee9": "黄", "\u2ee3": "骨", "\u2e9f": "母", "\u2ef3": "龟",
}
HAN = r"\u3400-\u4dbf\u4e00-\u9fff"


def fix_char(ch):
    if ch in RADICAL_MAP:
        return RADICAL_MAP[ch]
    o = ord(ch)
    if 0x2F00 <= o <= 0x2FDF or 0xF900 <= o <= 0xFAFF or 0x2F800 <= o <= 0x2FA1F:
        return unicodedata.normalize("NFKC", ch)
    return ch


def fix_chars(text):
    return "".join(fix_char(c) for c in text) if text else text


def fix_prose(s):
    """只对非代码行做排版修正。"""
    s = re.sub(rf"(?<=[{HAN}])[ \t]+(?=[{HAN}])", "", s)
    s = re.sub(rf"[ \t]+(?=[，。！？；：、）】》」』…])", "", s)
    s = re.sub(rf"(?<=[（【《「『])[ \t]+", "", s)
    return s


PIC_START = "<!-- Start of picture text -->"
PIC_END = "<!-- End of picture text -->"
BR_RE = re.compile(r"<br\s*/?>")


def clean_body(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"</?mark>", "", text)
    text = text.replace("\u00a0", " ")          # NBSP → 普通空格（代码缩进也要）
    text = fix_chars(text)

    out, in_fence = [], False
    for ln in text.split("\n"):
        if ln.strip().startswith("```"):
            in_fence = not in_fence
            out.append(ln.rstrip())
            continue
        ln = ln.rstrip()
        if PIC_START in ln or PIC_END in ln:
            ln = ln.replace(PIC_START, "").replace(PIC_END, "").rstrip()
            if not ln.strip():
                continue
        is_row = ln.lstrip().startswith("|")
        if not is_row:
            ln = BR_RE.sub("\n", ln)
        if not in_fence:
            if re.fullmatch(r"[-—–\s]*\d{1,4}[-—–\s]*", ln.strip()):
                continue
            if re.fullmatch(r"[|:.\-_=~·\s]{1,6}", ln.strip()):
                continue
            ln = fix_prose(ln)
        out.extend(ln.split("\n"))

    # 合并松散列表项之间的空行
    LIST = r"^\s*(?:[-*+]|\d+[.)])\s+"
    merged, i, in_fence = [], 0, False
    while i < len(out):
        ln = out[i]
        if ln.strip().startswith("```"):
            in_fence = not in_fence
            merged.append(ln)
            i += 1
            continue
        if ln.strip() == "" and not in_fence:
            j = i
            while j < len(out) and out[j].strip() == "":
                j += 1
            prev = merged[-1] if merged else ""
            nxt = out[j] if j < len(out) else ""
            if re.match(LIST, prev) and re.match(LIST, nxt):
                i = j
                continue
            merged.append("")
            i = j
            continue
        merged.append(ln)
        i += 1
    return re.sub(r"\n{3,}", "\n\n", "\n".join(merged)).strip()


def sanitize(name, maxlen=60):
    name = re.sub(r'[\\/:*?"<>|]', "_", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name[:maxlen].strip() or "未命名"


def cmp_key(s):
    """标题匹配用的归一化：去掉 markdown/HTML 标记与空白。"""
    s = re.sub(r"<[^>]*>", "", s or "")
    return re.sub(r"[*_`#>|<>\-\[\]()（）　\s/]", "", s)


# ---------- 原始文本索引（把被压平的代码还原） ----------
class RawIndex:
    def __init__(self, raw):
        self.lines = [l.rstrip() for l in raw.replace("\r", "\n").split("\n")]
        self.flat, self.line_of = self._build("")
        self.flat_np, self.line_of_np = self._build("|`")

    def _build(self, skip):
        chars, line_of = [], []
        for i, ln in enumerate(self.lines):
            for ch in ln:
                if ch.isspace() or ch in skip:
                    continue
                chars.append(ch)
                line_of.append(i)
        return "".join(chars), line_of

    def span(self, text, skip=""):
        flat, line_of = (self.flat_np, self.line_of_np) if "|" in skip else (self.flat, self.line_of)
        if skip:
            text = "".join(c for c in text if c not in skip)
        key = re.sub(r"\s+", "", text)
        if len(key) < 6:
            return None
        s = flat.find(key)
        if s < 0:
            if len(key) < 40:
                return None
            key = key[:40]
            s = flat.find(key)
            if s < 0:
                return None
        e = s + len(key) - 1
        if e >= len(line_of):
            return None
        return "\n".join(self.lines[line_of[s]:line_of[e] + 1]).rstrip()


FENCE_RE = re.compile(r"```([^\n`]*)\n(.*?)```", re.S)


def fix_code_blocks(md, idx):
    """已有围栏里被吃掉空格的代码，用 PDF 原文还原。"""
    def repl(m):
        lang, code = m.group(1), m.group(2)
        got = idx.span(code, skip="`")
        if not got:
            return m.group(0)
        return "```" + lang.rstrip() + "\n" + got + "\n```"

    return FENCE_RE.sub(repl, md)


CODE_SIGNALS = re.compile(
    r"[;{}]|#include|#define|\bdef\s+\w+\(|\bclass\s+\w+|\bstruct\s+\w+|"
    r"\bint\s+\w+|\bvoid\s+\w+\(|\breturn\b|mysql>|\bSELECT\b|\bINSERT\b|\bCREATE\b|"
    r"->|==|\.\.\.|println|\bprint\(|\bfunc\s+\w+\(|\bpublic\s|\bstatic\s|127\.0\.0\.1:\d+>"
)


def promote_code(md, idx):
    """把被压成一行的代码段落还原成围栏代码块。"""
    out, in_fence = [], False
    for ln in md.split("\n"):
        if ln.strip().startswith("```"):
            in_fence = not in_fence
            out.append(ln)
            continue
        s = ln.strip()
        if in_fence or s.startswith("|") or s.startswith("!"):
            out.append(ln)
            continue
        n_sig = len(CODE_SIGNALS.findall(s))
        has_tick = "`" in s
        if (len(s) >= 110 and n_sig >= 2) or (has_tick and len(s) >= 60 and n_sig >= 3):
            got = idx.span(s, skip="`")
            if got and "\n" in got:
                out.append("```\n" + got + "\n```")
                continue
            if s.count("`") >= 4:      # 原文对不上，至少把碎片化的反引号去掉
                out.append(re.sub(r"\s*`\s*", " ", ln))
                continue
        out.append(ln)
    return "\n".join(out)


def unwrap_prose_fences(md):
    """围栏里其实是中文说明文字的，拆回普通段落。"""
    def repl(m):
        lang, code = m.group(1), m.group(2)
        body = re.sub(r"\s", "", code)
        if not body:
            return m.group(0)
        cjk = sum(1 for c in body if "\u4e00" <= c <= "\u9fff")
        code_marks = len(re.findall(r"[;{}=<>\[\]#]", body))
        if cjk / len(body) > 0.55 and code_marks < 3:
            return code.strip()
        return m.group(0)

    return FENCE_RE.sub(repl, md)


# ---------- 表格 ----------
SEP_RE = re.compile(r"^\|[\s:\-|]+\|?\s*$")
CODEISH = re.compile(r"[;{}]|//|typedef|struct|#include|\+--|^`?\|`")


def fix_tables(md, idx):
    """表格补分隔行；误判成表格的代码改回代码块；空单元格标题改回标题。"""
    lines = md.split("\n")
    out, i, in_fence = [], 0, False
    while i < len(lines):
        ln = lines[i]
        if ln.strip().startswith("```"):
            in_fence = not in_fence
            out.append(ln)
            i += 1
            continue
        if not in_fence and ln.strip().startswith("|"):
            j = i
            while j < len(lines) and lines[j].strip().startswith("|"):
                j += 1
            block = lines[i:j]
            cells = [c.strip() for c in block[0].strip().strip("|").split("|")]
            counts = {b.count("|") for b in block}
            codeish = sum(1 for b in block if CODEISH.search(b.strip())) >= max(2, len(block) * 0.8)
            nonempty = [c for c in cells if c]

            # 孤立的单行 |xxx|（没有分隔行、没有数据行）不是表格
            if len(block) == 1 and len(nonempty) == 1 and not SEP_RE.match(block[0].strip()):
                txt = nonempty[0].strip("*` ")
                out.append("### " + txt if len(txt) <= 20 else txt)
                i = j
                continue

            # ||C++面试篇|| + |---| 这类“单格表格”其实是被识别成表格的小标题
            if len(block) == 2 and SEP_RE.match(block[1].strip()) and len(nonempty) == 1:
                out.append("### " + nonempty[0].strip("*` "))
                i = j
                continue
            if len(block) >= 2 and (len(counts) > 1 or codeish):
                got = idx.span("\n".join(block), skip="|`") or idx.span("\n".join(block), skip="`")
                if got is None:
                    got = "\n".join(re.sub(r"^\||\|$|`", "", b).strip() for b in block)
                out.append("```\n" + got + "\n```")
            else:
                if len(block) >= 2 and not SEP_RE.match(block[1].strip()):
                    ncol = max(1, block[0].count("|") - 1)
                    block.insert(1, "|" + "---|" * ncol)
                out.extend(block)
            i = j
            continue
        out.append(ln)
        i += 1
    return "\n".join(out)


# ---------- 图片 ----------
IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def process_images(body, img_dir, page_no):
    def repl(m):
        path = m.group(1)
        if not os.path.isabs(path):
            path = os.path.join(img_dir, os.path.basename(path))
        if not os.path.exists(path):
            return ""
        base = os.path.basename(path)
        mt = re.match(r".*-(\d{4})-(\d+)\.png$", base)
        newname = f"p{mt.group(1)}-{mt.group(2)}.png" if mt else f"p{page_no:04d}-{abs(hash(base)) % 100:02d}.png"
        try:
            px = pymupdf.Pixmap(path)
            small = px.width < 120 or px.height < 120 or px.width * px.height < 20000
            del px
        except Exception:
            small = False
        if small:
            try:
                os.remove(path)
            except OSError:
                pass
            return ""
        dst = os.path.join(img_dir, newname)
        if path != dst:
            os.replace(path, dst)
        return f"![](images/{newname})"

    body = IMG_RE.sub(repl, body)
    return re.sub(r"\n{3,}", "\n\n", body)


# ---------- 章节切分 ----------
def chapter_ranges(toc, npages):
    l1, seen = [], set()
    for lvl, t, p in toc:
        if lvl != 1:
            continue
        p = max(0, min(p - 1, npages - 1))
        if p in seen:
            continue
        seen.add(p)
        l1.append((t, p))
    if not l1:
        return [("全文", 0, npages - 1)]
    ranges = []
    if l1[0][1] > 0:
        ranges.append(("封面与前言", 0, l1[0][1] - 1))
    for i, (t, p) in enumerate(l1):
        end = l1[i + 1][1] - 1 if i + 1 < len(l1) else npages - 1
        ranges.append((t, p, max(end, p)))
    return ranges


def find_title_line(lines, title, limit=None):
    t = cmp_key(title)
    if len(t) < 2:
        return None
    for i, ln in enumerate(lines[:limit] if limit else lines):
        k = cmp_key(re.sub(r"^#+\s*", "", ln.strip()))
        if k == t:
            return i
    return None


def convert(title, rel):
    pdf = os.path.join(SRC, rel)
    book_dir = os.path.join(OUT, sanitize(title, 80))
    img_dir = os.path.join(book_dir, "images")
    if os.path.isdir(img_dir):
        for f in glob.glob(os.path.join(img_dir, "*.png")):
            os.remove(f)
    os.makedirs(img_dir, exist_ok=True)
    t0 = time.time()

    doc = pymupdf.open(pdf)
    toc, npages = doc.get_toc(), doc.page_count
    chunks = pymupdf4llm.to_markdown(pdf, page_chunks=True, write_images=True,
                                     image_path=img_dir, image_format="png", show_progress=False)
    pages = {int(c["metadata"]["page_number"]) - 1: c.get("text", "") for c in chunks}
    raw_pages = {i: doc[i].get_text("text") for i in range(npages)}
    doc.close()

    drafts = []
    for name, start, end in chapter_ranges(toc, npages):
        raw = "\n\n".join(pages.get(p, "") for p in range(start, end + 1))
        idx = RawIndex("\n".join(raw_pages.get(p, "") for p in range(start, end + 1)))
        body = clean_body(raw)
        body = process_images(body, img_dir, start + 1)
        body = fix_code_blocks(body, idx)
        body = promote_code(body, idx)
        body = fix_tables(body, idx)
        body = unwrap_prose_fences(body)
        body = clean_body(body)
        drafts.append({"name": name, "start": start, "end": end, "body": body})

    # 章界校正：开头若还是上一章尾巴则裁到本章标题行；末尾若出现下一章标题则裁掉
    for k, d in enumerate(drafts):
        lines = d["body"].split("\n")
        pos = find_title_line(lines, d["name"])
        if pos is not None and pos > 0:
            lines = lines[pos:]
        elif pos is None and k > 0:
            lines = [f"# **<u>{d['name']}</u>**", ""] + lines
        # 标题存在但不是一级标题（原书就没写 #），补一个
        head = next((i for i, l in enumerate(lines) if l.strip()), None)
        if head is not None and cmp_key(re.sub(r"^#+\s*", "", lines[head].strip())) == cmp_key(d["name"]) \
                and not lines[head].lstrip().startswith("#"):
            lines[head] = "# " + lines[head].strip()
        if k + 1 < len(drafts):
            nxt = find_title_line(lines, drafts[k + 1]["name"])
            if nxt is not None and nxt > 0:
                lines = lines[:nxt]
        d["body"] = "\n".join(lines).strip()

    written = []
    for i, d in enumerate(drafts, 1):
        body = d["body"]
        if len(re.sub(r"\s", "", body)) < 20:
            continue
        fname = f"{i:02d}-{sanitize(d['name'])}.md"
        fm = ("---\n"
              f"title: {d['name']}\n"
              f"book: {title}\n"
              f"source: {os.path.basename(rel)}\n"
              f"pages: {d['start'] + 1}-{d['end'] + 1}\n"
              "---\n\n")
        with open(os.path.join(book_dir, fname), "w", encoding="utf-8") as f:
            f.write(fm + body + "\n")
        written.append((fname, d["name"], d["start"] + 1, d["end"] + 1, len(body)))

    cmap = {n: fn for fn, n, *_ in written}
    lines = [f"# {title}", "", f"> 来源 PDF：`{os.path.basename(rel)}`　共 {npages} 页", "", "## 目录", ""]
    for lvl, t, p in toc:
        if lvl == 1:
            f = cmap.get(t)
            if not f:
                for fn, n, s, e, _ in written:
                    if s <= p <= e:
                        f = fn
                        break
            lines.append(f"- [{t}]({f})　p.{p}" if f else f"- {t}　p.{p}")
        elif lvl == 2:
            lines.append(f"    - {t}　p.{p}")
    lines += ["", "## 章节文件", ""]
    for fname, name, s, e, n in written:
        lines.append(f"- [{name}]({fname})　p.{s}-{e}　{n} 字")
    with open(os.path.join(book_dir, "index.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    used = set()
    for fn, *_ in written:
        used |= set(re.findall(r"images/([^)]+)", open(os.path.join(book_dir, fn), encoding="utf-8").read()))
    for f in glob.glob(os.path.join(img_dir, "*.png")):
        if os.path.basename(f) not in used:
            os.remove(f)

    nimg = len(glob.glob(os.path.join(img_dir, "*.png")))
    total = sum(w[4] for w in written)
    print(f"[OK] {title}: {npages}p → {len(written)} 章, {total} 字, {nimg} 图, {time.time()-t0:.0f}s", flush=True)
    return {"book": title, "pdf": rel, "pages": npages, "chapters": len(written),
            "chars": total, "images": nimg, "seconds": round(time.time() - t0)}


if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    rp = os.path.join(OUT, "_convert_report.json")
    results = json.load(open(rp, encoding="utf-8")) if os.path.exists(rp) else []
    for title, rel in BOOKS:
        if only and only not in title:
            continue
        results = [r for r in results if r["book"] != title] + [convert(title, rel)]
        json.dump(results, open(rp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps(results, ensure_ascii=False, indent=2))
