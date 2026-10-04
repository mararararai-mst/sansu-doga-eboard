# -*- coding: utf-8 -*-
"""ページに書き出したリンクが、eboard のページに実在する href と一致するか確かめる。

ネットは叩かず、_fetch.py が保存した _src/pages/*.html の中の href と突き合わせる
（組み立てたURLではなく、向こうが書いている href が正）。
  python _linkcheck.py           保存済みページと突き合わせる
  python _linkcheck.py --net N   そのうち N 本を実際に叩いて200が返るか見る
"""
import json, re, sys, time, urllib.error, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGES = HERE / "_src" / "pages"
UA = {"User-Agent": "Mozilla/5.0 (educational link collection; m.arararara.i@gmail.com)"}


def links_in_page():
    """単元ページの <article> から、実在する 動画href / 問題href を拾う"""
    v, q = set(), set()
    for p in sorted(PAGES.glob("*.html")):
        h = p.read_text(encoding="utf-8")
        for m in re.finditer(r"<article\b[\s\S]*?</article>", h):
            v |= set(re.findall(r'href="(/content/\d+/v/\d+/)"', m.group(0)))
            q |= set(re.findall(r'href="(/content/\d+/q/\d+/1/)"', m.group(0)))
    return v, q


def links_in_html():
    """index.html に埋め込んだ DATA.apps から、使っているURLを拾う"""
    h = (HERE / "index.html").read_text(encoding="utf-8")
    m = re.search(r"const DATA = (\{[\s\S]*?\});\n", h)
    if not m:
        sys.exit("NG index.html の DATA が読めない")
    apps = json.loads(m.group(1))["apps"]
    v = {a["app"].replace("https://www.eboard.jp", "") for a in apps.values()}
    q = {a["quiz"].replace("https://www.eboard.jp", "") for a in apps.values() if a["quiz"]}
    return v, q, len(apps)


def main():
    if not PAGES.exists():
        sys.exit("NG _src/pages/ が無い。先に python _fetch.py")
    pv, pq = links_in_page()
    hv, hq, n = links_in_html()
    ng = 0
    for name, mine, theirs in (("動画", hv, pv), ("確認問題", hq, pq)):
        bad = sorted(mine - theirs)
        print("%s %d本 … eboard側に無いもの %d" % (name, len(mine), len(bad)))
        for b in bad[:20]:
            print("   NG", b)
        ng += len(bad)
    extra = sorted(pv - hv)
    if extra:
        print("※ eboardにあるがこの表に載せていない動画 %d本: %s" % (len(extra), extra[:10]))
    print("カード %d枚" % n)

    if "--net" in sys.argv:
        k = int(sys.argv[sys.argv.index("--net") + 1])
        import random
        pick = random.sample(sorted(hv | hq), min(k, len(hv) + len(hq)))
        for u in pick:
            url = "https://www.eboard.jp" + u
            try:
                req = urllib.request.Request(url, headers=UA, method="HEAD")
                code = urllib.request.urlopen(req, timeout=20).status
            except urllib.error.HTTPError as e:
                code = e.code
            except Exception as e:
                code = repr(e)
            print("  %s %s" % (code, u))
            if code != 200:
                ng += 1
            time.sleep(0.4)
    sys.exit(1 if ng else 0)


main()
