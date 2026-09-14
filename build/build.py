#!/usr/bin/env python3
"""AWS入門教科書の Markdown 群を1ページのHTMLに変換するビルドスクリプト。

docs/00-introduction.md 〜 17-next-roadmap.md と APPENDIX-glossary.md を結合し、
site/index.html（完全なHTML文書）と site/artifact.html（body断片）を生成する。
外部通信は行わない（Google Fontsの<link>タグのみ例外）。
"""
import html
import re
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SITE = ROOT / "site"

CHAPTER_FILES = [f"{i:02d}" for i in range(0, 18)]  # 00..17

GROUPS = [
    ("導入", ["00", "01", "02"]),
    ("名前と住所", ["03", "04"]),
    ("VPCの中", ["05", "06", "07", "08", "09", "10"]),
    ("置いて配る", ["11", "12"]),
    ("組み立て", ["13", "14", "15"]),
    ("総まとめ", ["16", "17"]),
    ("付録", ["glossary"]),
]

TASK_RE = re.compile(r"^(\s*)-\s\[ \]\s+(.*)$", re.MULTILINE)


def preprocess_tasklist(text: str) -> str:
    """`- [ ] ...` を一旦プレースホルダのリスト項目に変換し、後処理でHTML化する。"""
    def repl(m):
        indent, rest = m.group(1), m.group(2)
        return f"{indent}- [TASKITEM]{rest}"
    return TASK_RE.sub(repl, text)


LEAD_HEADING_RE = re.compile(r"^(>\s*\*\*この章でわかること\*\*)\n(?!>\s*$)", re.MULTILINE)


def preprocess_lead_blockquote(text: str) -> str:
    """`> **この章でわかること**` の直後に `>` 空行がなければ挿入し、
    直後の `> - 項目` 箇条書きが python-markdown で <ul> として認識されるようにする。"""
    return LEAD_HEADING_RE.sub(lambda m: m.group(1) + "\n>\n", text)


def postprocess_tasklist(html_text: str) -> str:
    return html_text.replace(
        "<li>[TASKITEM]",
        '<li class="task"><input type="checkbox"> ',
    )


def rewrite_links(text: str, warnings: list) -> str:
    """Markdownリンクの相対パスを章内アンカーに書き換える。"""

    link_re = re.compile(r"\]\(([^)]+)\)")

    def repl(m):
        target = m.group(1)
        orig = target
        # アンカー部分を切り離す
        if "#" in target:
            path_part, _, _anchor = target.partition("#")
        else:
            path_part = target

        mnum = re.search(r"(\d{2})-[^./]+\.md$", path_part)
        if mnum:
            num = mnum.group(1)
            return f"](#ch-{num})"
        if path_part.endswith("APPENDIX-glossary.md"):
            return "](#glossary)"
        if path_part.endswith("README.md"):
            return "](#ch-00)"
        # 外部リンク（http等）はそのまま
        if re.match(r"^[a-zA-Z]+://", target):
            return m.group(0)
        # 未解決の相対リンク
        if target.endswith(".md") or ".md#" in target or path_part.endswith(".md"):
            warnings.append(f"未解決リンク: {orig}")
        return m.group(0)

    return link_re.sub(repl, text)


def wrap_misconceptions(html_text: str) -> str:
    """<strong>勘違い</strong> を含む <blockquote> に class="misconception" を付与する。"""
    def repl(m):
        block = m.group(0)
        if "<strong>勘違い</strong>" in block:
            return block.replace("<blockquote>", '<blockquote class="misconception">', 1)
        return block

    return re.sub(r"<blockquote>.*?</blockquote>", repl, html_text, flags=re.DOTALL)


def wrap_lead(html_text: str) -> str:
    """「この章でわかること」を含む先頭付近の <blockquote> に class="lead" を付与する。"""
    def repl(m):
        block = m.group(0)
        if "この章でわかること" in block:
            return block.replace("<blockquote>", '<blockquote class="lead">', 1)
        return block

    return re.sub(r"<blockquote>.*?</blockquote>", repl, html_text, flags=re.DOTALL, count=1)


SAA_HEADING_RE = re.compile(
    r"(?:<hr\s*/?>\s*)?(<h3[^>]*>Solutions Architect Associate ではこう問われる</h3>.*?)(?=<hr\s*/?>|\Z)",
    re.DOTALL,
)


def wrap_saa(html_text: str) -> str:
    def repl(m):
        inner = m.group(1)
        return f'<aside class="saa">\n{inner}</aside>\n'

    return SAA_HEADING_RE.sub(repl, html_text)


def wrap_tables(html_text: str) -> str:
    return re.sub(
        r"(<table>.*?</table>)",
        r'<div class="table-wrap">\1</div>',
        html_text,
        flags=re.DOTALL,
    )


def render_chapter(md_source: str, chapter_id: str, eyebrow: str, warnings: list) -> str:
    src = preprocess_lead_blockquote(md_source)
    src = preprocess_tasklist(src)
    src = rewrite_links(src, warnings)

    md = markdown.Markdown(extensions=["tables", "fenced_code", "attr_list", "sane_lists"])
    body_html = md.convert(src)

    body_html = postprocess_tasklist(body_html)
    body_html = wrap_misconceptions(body_html)
    body_html = wrap_lead(body_html)
    body_html = wrap_saa(body_html)
    body_html = wrap_tables(body_html)

    # ```text フェンスは pre.figure、```bash / 他は pre.code にする。
    # python-markdown の fenced_code は <pre><code class="language-xxx">...</code></pre> を出す。
    def pre_repl(m):
        lang = m.group(1)
        inner = m.group(2)
        cls = "figure" if lang == "text" or lang == "" else "code"
        return f'<pre class="{cls}"><code>{inner}</code></pre>'

    body_html = re.sub(
        r'<pre><code class="language-(\w*)">(.*?)</code></pre>',
        pre_repl,
        body_html,
        flags=re.DOTALL,
    )
    # 言語指定なしの fenced code (```のみ) は class 属性が付かない場合がある
    body_html = re.sub(
        r'<pre><code>(.*?)</code></pre>',
        lambda m: f'<pre class="code"><code>{m.group(1)}</code></pre>',
        body_html,
        flags=re.DOTALL,
    )

    # h1 の直前に eyebrow を挿入
    body_html = re.sub(
        r"(<h1[^>]*>)",
        f'<p class="eyebrow">{html.escape(eyebrow)}</p>\n\\1',
        body_html,
        count=1,
    )

    return f'<section id="{chapter_id}">\n{body_html}\n</section>'


def chapter_title(md_source: str) -> str:
    m = re.search(r"^#\s+(.*)$", md_source, re.MULTILINE)
    return m.group(1).strip() if m else ""


def short_title(full_title: str) -> str:
    """h1見出しから `—` より前のタイトル部分だけを取り出す（章番号は除く）。"""
    # "第N章 タイトル — サブタイトル" or "はじめに — サブタイトル" or "APPENDIX 用語集"
    parts = re.split(r"\s+—\s+", full_title, maxsplit=1)
    head = parts[0].strip()
    head = re.sub(r"^第\d+章\s*", "", head)
    head = re.sub(r"^はじめに\s*", "はじめに", head)
    return head


def build():
    warnings = []
    chapters = []  # list of dict: num, id, title, short, html

    for num in CHAPTER_FILES:
        matches = list(DOCS.glob(f"{num}-*.md"))
        if not matches:
            print(f"warning: chapter {num} not found", file=sys.stderr)
            continue
        path = matches[0]
        src = path.read_text(encoding="utf-8")
        title = chapter_title(src)
        eyebrow = "はじめに" if num == "00" else f"第{int(num)}章"
        chapter_id = f"ch-{num}"
        chap_html = render_chapter(src, chapter_id, eyebrow, warnings)
        chapters.append({
            "num": num,
            "id": chapter_id,
            "title": title,
            "short": short_title(title),
        })
        chapters[-1]["html"] = chap_html

    # 用語集
    gpath = ROOT / "APPENDIX-glossary.md"
    gsrc = gpath.read_text(encoding="utf-8")
    gtitle = chapter_title(gsrc)
    ghtml = render_chapter(gsrc, "glossary", "付録", warnings)
    glossary_entry = {"num": "glossary", "id": "glossary", "title": gtitle, "short": "用語集", "html": ghtml}

    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)

    all_sections_html = "\n".join(c["html"] for c in chapters) + "\n" + glossary_entry["html"]

    lookup = {c["num"]: c for c in chapters}
    lookup["glossary"] = glossary_entry

    nav_html = render_nav(lookup)

    css = CSS
    js = JS
    fonts_link = (
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@400;700&amp;'
        'family=Noto+Sans+JP:wght@400;500;700&amp;display=swap" '
        'rel="stylesheet">'
    )

    fragment_body = (
        "<title>AWS入門教科書</title>\n"
        f"{fonts_link}\n"
        f"<style>\n{css}\n</style>\n"
        '<div class="topbar"><button class="toc-btn" id="tocBtn" aria-expanded="false" aria-controls="sidebar">目次</button></div>\n'
        '<div class="layout">\n'
        f'{nav_html}\n'
        '<main id="main">\n'
        f"{all_sections_html}\n"
        "</main>\n"
        "</div>\n"
        f"<script>\n{js}\n</script>"
    )

    artifact_html = fragment_body

    full_html = (
        "<!doctype html>\n"
        '<html lang="ja">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>AWS入門教科書</title>\n"
        f"{fonts_link}\n"
        f"<style>\n{css}\n</style>\n"
        "</head>\n"
        "<body>\n"
        '<div class="topbar"><button class="toc-btn" id="tocBtn" aria-expanded="false" aria-controls="sidebar">目次</button></div>\n'
        '<div class="layout">\n'
        f'{nav_html}\n'
        '<main id="main">\n'
        f"{all_sections_html}\n"
        "</main>\n"
        "</div>\n"
        f"<script>\n{js}\n</script>\n"
        "</body>\n"
        "</html>\n"
    )

    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "index.html").write_text(full_html, encoding="utf-8")
    (SITE / "artifact.html").write_text(artifact_html, encoding="utf-8")

    size_kb = (SITE / "index.html").stat().st_size / 1024
    print(f"generated site/index.html ({size_kb:.1f} KB) and site/artifact.html")


def render_nav(lookup):
    items = []
    items.append('<nav class="sidebar" id="sidebar">')
    items.append('<p class="site-title">AWS入門教科書</p>')
    items.append('<ul class="toc">')
    for label, nums in GROUPS:
        items.append(f'<li class="toc-group"><span class="group-label">{html.escape(label)}</span><ul>')
        for num in nums:
            c = lookup.get(num)
            if not c:
                continue
            items.append(
                f'<li><a href="#{c["id"]}" data-target="{c["id"]}">'
                f'<span class="chnum">{html.escape(num if num != "glossary" else "付録")}</span>'
                f'<span class="chtitle">{html.escape(c["short"])}</span></a></li>'
            )
        items.append("</ul></li>")
    items.append("</ul>")
    items.append("</nav>")
    return "\n".join(items)


CSS = """
:root{
  --bg:#F6F7F9; --surface:#FFFFFF; --ink:#1B2430; --muted:#5B6B7C; --line:#D9DEE4;
  --accent:#0E7C86; --accent-ink:#0A5B62; --amber:#B7791F; --fig-bg:#EEF2F5; --fig-ink:#22303C;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#0F141A; --surface:#171E26; --ink:#E6EAEE; --muted:#9AA7B4; --line:#2A3542;
    --accent:#3FB7C0; --accent-ink:#7FD3DA; --amber:#D9A441; --fig-bg:#0B1117; --fig-ink:#D7DEE6;
  }
}
:root[data-theme="dark"]{
  --bg:#0F141A; --surface:#171E26; --ink:#E6EAEE; --muted:#9AA7B4; --line:#2A3542;
  --accent:#3FB7C0; --accent-ink:#7FD3DA; --amber:#D9A441; --fig-bg:#0B1117; --fig-ink:#D7DEE6;
}

*{box-sizing:border-box;}
body{
  margin:0; background:var(--bg); color:var(--ink);
  font-family:"Noto Sans JP","Hiragino Sans",sans-serif;
  font-size:17px; line-height:1.9;
}
h1,h2,h3{
  font-family:"Zen Kaku Gothic New","Noto Sans JP",sans-serif;
  font-weight:700; text-wrap:balance; color:var(--ink);
}
h1{font-size:1.9rem; margin:0 0 1.5rem;}
h2{font-size:1.3rem; margin-top:3rem; margin-bottom:1rem;}
h3{font-size:1rem; margin-top:1.5rem;}
p,li{max-width:40rem;}
a{color:var(--accent-ink); text-decoration:underline;}
a:focus-visible, button:focus-visible{outline:2px solid var(--accent); outline-offset:2px;}

.eyebrow{
  font-family:ui-monospace, Menlo, "SF Mono", Consolas, "Liberation Mono", monospace;
  color:var(--muted); font-size:0.85rem; margin:0 0 0.5rem;
}

.topbar{
  display:none; position:fixed; top:0; left:0; right:0; height:2.75rem;
  background:var(--surface); border-bottom:1px solid var(--line); z-index:20;
  align-items:center; padding:0 1rem;
}
.toc-btn{
  font-family:"Noto Sans JP",sans-serif; font-size:0.9rem; color:var(--ink);
  background:var(--bg); border:1px solid var(--line); border-radius:4px;
  padding:0.4rem 0.8rem; cursor:pointer;
}

.layout{display:flex; align-items:flex-start;}

.sidebar{
  width:17rem; flex:none; position:sticky; top:0; height:100vh; overflow-y:auto;
  border-right:1px solid var(--line); padding:2rem 1.25rem; background:var(--bg);
}
.site-title{
  font-family:"Zen Kaku Gothic New",sans-serif; font-weight:700; font-size:1.1rem;
  margin:0 0 1.5rem;
}
.toc, .toc ul{list-style:none; margin:0; padding:0;}
.toc-group{margin-bottom:1.25rem;}
.group-label{
  display:block; font-size:0.7rem; letter-spacing:0.08em; text-transform:uppercase;
  color:var(--muted); margin-bottom:0.4rem;
}
.toc a{
  display:flex; gap:0.6rem; align-items:baseline; padding:0.25rem 0.4rem; border-radius:4px;
  text-decoration:none; color:var(--ink); font-size:0.9rem;
}
.toc a:hover{background:var(--surface);}
.toc a[aria-current="true"]{background:var(--surface); color:var(--accent-ink); font-weight:700;}
.chnum{
  font-family:ui-monospace, Menlo, "SF Mono", Consolas, "Liberation Mono", monospace; color:var(--muted); font-size:0.8rem; flex:none;
}

main{flex:1; min-width:0; padding:3rem 3rem 6rem; max-width:64rem;}

section{padding-top:2rem;}
section + section{border-top:1px solid var(--line); margin-top:5rem; padding-top:3rem;}

blockquote{
  margin:1.5rem 0; padding:1rem 1.25rem; border-left:3px solid var(--line);
  background:var(--surface); max-width:40rem;
}
blockquote.lead{border-left-color:var(--accent);}
.lead ul{margin:.5rem 0 0; padding-left:1.2rem;}
blockquote.misconception{border-left:3px solid var(--amber);}
blockquote.misconception strong{color:var(--amber);}
blockquote.misconception p strong:nth-of-type(2){color:var(--accent-ink);}

pre{
  font-family:ui-monospace, Menlo, "SF Mono", Consolas, "Liberation Mono", monospace;
  font-size:13.5px; line-height:1.45; tab-size:4; white-space:pre;
  font-variant-ligatures:none; letter-spacing:0;
  overflow-x:auto; max-width:100%; border-radius:4px; padding:1rem 1.25rem; margin:1.5rem 0;
}
pre.figure{background:var(--fig-bg); color:var(--fig-ink); border:1px solid var(--line); font-feature-settings:normal; letter-spacing:0;}
pre.code{background:var(--fig-bg); color:var(--fig-ink); border:1px solid var(--line);}
pre code{font:inherit; letter-spacing:inherit;}

.table-wrap{overflow-x:auto; max-width:100%; margin:1.5rem 0;}
table{border-collapse:collapse; width:100%;}
th,td{border:1px solid var(--line); padding:0.5rem 0.75rem; text-align:left; font-size:0.92rem;}
th{background:var(--surface);}

li.task{list-style:none; margin-left:-1.4em;}
li.task input{margin-right:0.5em;}

aside.saa{
  border-top:1px dashed var(--line); margin-top:2rem; padding-top:1.5rem;
}
aside.saa h3{color:var(--muted); font-size:1rem;}

hr{border:none; border-top:1px solid var(--line); margin:2rem 0;}

@media (prefers-reduced-motion: reduce){
  html{scroll-behavior:auto;}
}
@media (prefers-reduced-motion: no-preference){
  html{scroll-behavior:smooth;}
}

@media (max-width:899px){
  .topbar{display:flex;}
  .sidebar{
    position:fixed; top:2.75rem; left:0; bottom:0; z-index:30; box-shadow:2px 0 8px rgba(0,0,0,0.15);
    transform:translateX(-100%); transition:transform 0.2s ease;
  }
  .sidebar.open{transform:translateX(0);}
  main{padding:4.5rem 1.25rem 4rem;}
}
"""

JS = """
(function(){
  var btn = document.getElementById('tocBtn');
  var sidebar = document.getElementById('sidebar');
  if (btn && sidebar) {
    btn.addEventListener('click', function(){
      var open = sidebar.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    sidebar.addEventListener('click', function(e){
      if (e.target.closest('a')) {
        sidebar.classList.remove('open');
        btn.setAttribute('aria-expanded', 'false');
      }
    });
  }

  var links = Array.prototype.slice.call(document.querySelectorAll('.toc a'));
  var linkByTarget = {};
  links.forEach(function(a){ linkByTarget[a.getAttribute('data-target')] = a; });

  var sections = Array.prototype.slice.call(document.querySelectorAll('main > section'));
  if ('IntersectionObserver' in window && sections.length) {
    var observer = new IntersectionObserver(function(entries){
      entries.forEach(function(entry){
        var link = linkByTarget[entry.target.id];
        if (!link) return;
        if (entry.isIntersecting) {
          links.forEach(function(a){ a.removeAttribute('aria-current'); });
          link.setAttribute('aria-current', 'true');
        }
      });
    }, { rootMargin: '-10% 0px -70% 0px', threshold: 0 });
    sections.forEach(function(s){ observer.observe(s); });
  }
})();
"""


if __name__ == "__main__":
    build()
