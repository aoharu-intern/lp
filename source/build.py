#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POKEKUN LP build script.
master(index.html) を入力に (channel, grade) の6通りを固定ルールで生成する。
判断は入れない。href のみ変更し、本文・デザイン・data-cta属性は変更しない。
"""
import json
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent          # .../POKEKUN LP/source
ROOT = HERE.parent                               # .../POKEKUN LP
MASTER = ROOT / "index.html"
CTA_MAP = HERE / "cta_map.json"
DIST = ROOT / "dist"

CHANNELS = ["meta", "listing"]                   # lp_channel 値
GRADES = ["index", "y1", "y2"]
CTA_POSITIONS = ["header", "hero", "mid", "closing"]  # sticky は closing 流用

ROBOTS_META = '<meta name="robots" content="noindex">'

# 学年別の見出し差し替えマップ（y1/y2 のみ適用。index は不変）
HEADLINE = {
    'y1': {
        'title': '<title>AOHARUインターン｜大学1年生のあなたへ</title>',
        'h1': '<h1>1年生で始める人は、まだ少数派。<br>だから、差になる。<span class="spark">✦</span></h1>',
    },
    'y2': {
        'title': '<title>AOHARUインターン｜大学2年生のあなたへ</title>',
        'h1': '<h1>サマーのESに、<br>「実務経験」を書けるか。<span class="spark">✦</span></h1>',
    },
}

TITLE_SRC = '<title>AOHARUインターン｜キャリアは、体験で磨かれる。</title>'
H1_SRC = '<h1>キャリアは、<br>体験で磨かれる。<span class="spark">✦</span></h1>'


def set_headline(html: str, grade: str) -> str:
    """grade が y1/y2 のときだけ <title> と <h1> を学年見出しに置換（index は不変）"""
    if grade not in HEADLINE:
        return html
    html = html.replace(TITLE_SRC, HEADLINE[grade]['title'], 1)
    html = html.replace(H1_SRC, HEADLINE[grade]['h1'], 1)
    return html


def add_robots(html: str) -> str:
    """<head> 直後に noindex を1つ追加（既に無い前提）"""
    return html.replace("<head>", "<head>\n" + ROBOTS_META, 1)


def set_cta_href(html: str, position: str, url: str) -> str:
    """href="..." data-cta="<position>" の href のみ差し替え（属性は不変）"""
    pat = re.compile(r'href="[^"]*"(\s+data-cta="%s")' % re.escape(position))
    return pat.sub(lambda m: 'href="%s"%s' % (url, m.group(1)), html)


def relativize_links(html: str, grade: str) -> str:
    if grade == "index":
        html = html.replace('href="y1.html"', 'href="y1/"')
        html = html.replace('href="y2.html"', 'href="y2/"')
    else:  # y1, y2
        html = html.replace('href="y1.html"', 'href="../y1/"')
        html = html.replace('href="y2.html"', 'href="../y2/"')
    return html


def build_page(master: str, cta_map: dict, channel: str, grade: str) -> str:
    html = master
    # (a) __LP_CHANNEL__ -> channel 値
    html = html.replace("__LP_CHANNEL__", channel)
    # (b) lp_grade:'index' -> lp_grade:'<grade>'
    html = html.replace("lp_grade:'index'", "lp_grade:'%s'" % grade)
    # (c) CTA href 設定
    m = cta_map[grade][channel]
    for pos in CTA_POSITIONS:
        html = set_cta_href(html, pos, m[pos])
    html = set_cta_href(html, "sticky", m["closing"])  # 追従は closing 流用
    # (d) 内部リンク相対化
    html = relativize_links(html, grade)
    # (e) 学年別見出し差し替え（y1/y2 のみ。index は不変）
    html = set_headline(html, grade)
    # (f) noindex 追加
    html = add_robots(html)
    return html


def out_path(folder: str, grade: str) -> Path:
    if grade == "index":
        return DIST / folder / "index.html"
    return DIST / folder / grade / "index.html"


def main():
    master = MASTER.read_text(encoding="utf-8")
    cta_map = json.loads(CTA_MAP.read_text(encoding="utf-8"))

    if DIST.exists():
        shutil.rmtree(DIST)

    generated = []
    for channel in CHANNELS:
        folder = "lis" if channel == "listing" else "meta"
        for grade in GRADES:
            html = build_page(master, cta_map, channel, grade)
            p = out_path(folder, grade)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(html, encoding="utf-8")
            generated.append(p)

    # dist/.nojekyll
    (DIST / ".nojekyll").write_text("", encoding="utf-8")

    # dist/source/ : 再生成ソース（master.html=noindex付与版, build.py, cta_map.json）
    src_out = DIST / "source"
    src_out.mkdir(parents=True, exist_ok=True)
    (src_out / "master.html").write_text(add_robots(master), encoding="utf-8")
    shutil.copy2(__file__, src_out / "build.py")
    shutil.copy2(CTA_MAP, src_out / "cta_map.json")

    for p in generated:
        print("GENERATED", p)
    print("OK", len(generated), "pages")


if __name__ == "__main__":
    main()
