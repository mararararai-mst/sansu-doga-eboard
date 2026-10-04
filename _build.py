# -*- coding: utf-8 -*-
"""eboard 動画系統表ビルド

  _src/eboard_sansu.json  eboard.jp から取った単元・動画（_fetch.py）
  keito.json              系統（枠組み）＋動画の当てはめ（_map.py）
  _template.html          ひな形
  → index.html と 日本語名のコピー（フォント埋め込みの1枚もの）
"""
import base64, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = "index.html"
JP = "算数動画系統表.html"
UNITS = {u["id"]: u for u in json.loads((HERE / "_src" / "eboard_sansu.json").read_text(encoding="utf-8"))}
# 同梱フォント(Zen Maru Gothic)に無い字は、形も意味も変わらない字へ置き換える
# （1字だけ別フォントになるのを防ぐ）。eboardの動画タイトルに出てくる3種類。
FONT_SUB = {"－": "−", "↔": "⇔", "◻︎": "□"}

# 4枚を行き来するナビ。アプリ系統表は別のリポジトリなので、リンクは絶対URLで持つ
TKK = "https://mararararai-mst.github.io/sansu-keito-tkk/"
SELF = "https://mararararai-mst.github.io/sansu-doga-eboard/"
BOARDS = [
    {"label": "算数アプリ", "href": TKK},
    {"label": "算数動画", "href": SELF},
    {"label": "国語", "href": TKK + "kokugo.html"},
    {"label": "自立活動", "href": TKK + "jiritsu.html"},
]

V = "https://www.eboard.jp/content/%s/v/%d/"
Q = "https://www.eboard.jp/content/%s/q/%d/1/"


def card(key):
    """"158-1" -> 動画1本のカード。ひな形の appCard() が読む形に合わせる"""
    cid, n = key.split("-")
    n = int(n)
    u = UNITS[cid]
    v = next((x for x in u["videos"] if x["v"] == n), None)
    if not v:
        sys.exit("NG %s に v%d が無い" % (cid, n))
    sub = v["min"].lstrip("0")        # 単元名はパネルの見出しに出ているので時間だけ
    return {"name": v["name"], "sub": sub, "app": V % (cid, n),
            "quiz": Q % (cid, n) if v["q"] else "", "q": v["q"]}


def main():
    cfg = json.loads((HERE / "keito.json").read_text(encoding="utf-8"))
    tpl = (HERE / "_template.html").read_text(encoding="utf-8")

    apps = {}
    for g in cfg["groups"]:
        for r in g["rows"]:
            for chips in r["cells"].values():
                for ch in chips:
                    for k in ch["apps"]:
                        if k in apps:
                            sys.exit("NG %s が二重" % k)
                        apps[k] = card(k)

    data = {
        "grades": cfg["grades"],
        "groups": cfg["groups"],
        "tools": {"name": "", "sub": "", "items": []},
        "apps": apps,
        "boards": BOARDS,
        "self": SELF,
        "colHead": cfg["colHead"],
        "chainTitle": cfg["chainTitle"],
        "beforeTitle": cfg["beforeTitle"],
        "nowLabel": cfg["nowLabel"],
    }
    nchip = sum(len(c) for g in cfg["groups"] for r in g["rows"] for c in r["cells"].values())

    blob = json.dumps(data, ensure_ascii=False)
    for x, y in FONT_SUB.items():
        blob = blob.replace(x, y)
    bad = [x for x in FONT_SUB if x in blob]
    if bad:
        sys.exit("NG 置き換え残り: %r" % bad)
    html = tpl.replace("/*__DATA__*/", blob)
    for k, v in cfg["text"].items():
        html = html.replace("__%s__" % k, v)
    html = html.replace("__NAPPS__", str(len(apps))).replace("__NCHIPS__", str(nchip))
    html = html.replace("__NUNITS__", str(len(UNITS)))
    left = [t for t in ("__TITLE__", "__DESC__", "__SUB__", "__CANON__", "__SOURCE__",
                        "__HOWTO__", "__UNIT__", "__LEG1__", "__LEG2__", "__LEG3__",
                        "__NAPPS__", "__NCHIPS__", "__NUNITS__") if t in html]
    if left:
        sys.exit("NG 置き換え残り: %s" % left)
    (HERE / OUT).write_text(html, encoding="utf-8")

    # 日本語名の配布用コピー。フォントを埋め込んだ1枚もの（学校のフィルタでURLが開けないとき用）。
    # 検索エンジンには英語名の方を正とみなしてもらう（noindex＋canonical）。
    noindex = '<meta name="robots" content="noindex">' + chr(10) + '<link rel="canonical"'
    jp = html.replace('<link rel="canonical"', noindex, 1)
    for w in ("Medium", "Bold"):
        f = HERE / "font" / ("ZenMaruGothic-%s.subset.woff2" % w)
        uri = "data:font/woff2;base64," + base64.b64encode(f.read_bytes()).decode()
        jp = jp.replace('url("font/ZenMaruGothic-%s.subset.woff2")' % w, "url(%s)" % uri)
    assert "font/ZenMaruGothic" not in jp, "フォントの埋め込みに失敗"
    (HERE / JP).write_text(jp, encoding="utf-8")

    print("OK 動画%d / チップ%d / 単元%d -> %s（%.0fKB） / %s（%.0fKB）"
          % (len(apps), nchip, len(UNITS), OUT, (HERE / OUT).stat().st_size / 1024,
             JP, (HERE / JP).stat().st_size / 1024))


main()
