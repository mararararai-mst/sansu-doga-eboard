# -*- coding: utf-8 -*-
"""eboard 動画系統表ビルド

  _src/eboard_sansu.json  単元と動画の一覧（手元のみ）
  keito.json              系統（枠組み）＋動画の当てはめ（_map.py）
  _template.html          ひな形
  → index.html と 日本語名のコピー（フォント埋め込みの1枚もの）
"""
import base64, json, re, shutil, subprocess, sys, tempfile
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


def check_js(html):
    """書き出すHTMLの中のJavaScriptが文法として通るか（node があるときだけ）。
    ここを素通りさせると、表が1つも出ないページをそのまま公開してしまう。"""
    node = shutil.which("node")
    if not node:
        print("  ※ node が無いのでJSの文法チェックは飛ばした")
        return
    js = re.findall(r"<script>([\s\S]*?)</script>", html)
    if not js:
        sys.exit("NG ひな形に <script> が無い")
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "page.js"
        f.write_text("\n".join(js), encoding="utf-8")
        r = subprocess.run([node, "--check", str(f)], capture_output=True, text=True)
    if r.returncode:
        sys.exit("NG JSの文法エラー\n" + (r.stderr or r.stdout))


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
    check_js(html)
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

    handover(cfg, tpl, apps, nchip)


def handover(cfg, tpl, apps, nchip):
    """NPO法人eboardさんに渡す一式を eboardへ渡す/ に書き出す。

    先方のサイトに置いてもらう前提なので、こちら側のURLに依存するものは全部外す
    （ほかの表へのナビ・canonical・og:url・OGP画像・JSON-LD・noindex）。
    フォントは埋め込むので、1ファイルを置くだけで動く。
    """
    out = HERE / "handover"   # 公開ページからダウンロードしてもらうので、URLに出る名前は英字
    out.mkdir(exist_ok=True)

    data = {
        "grades": cfg["grades"], "groups": cfg["groups"],
        "tools": {"name": "", "sub": "", "items": []}, "apps": apps,
        "boards": [], "self": "",
        "colHead": cfg["colHead"], "chainTitle": cfg["chainTitle"],
        "beforeTitle": cfg["beforeTitle"], "nowLabel": cfg["nowLabel"],
    }
    blob = json.dumps(data, ensure_ascii=False)
    for x, y in FONT_SUB.items():
        blob = blob.replace(x, y)
    html = tpl.replace("/*__DATA__*/", blob)
    for k, v in cfg["text"].items():
        html = html.replace("__%s__" % k, v)
    html = html.replace("__NAPPS__", str(len(apps))).replace("__NCHIPS__", str(nchip))
    html = html.replace("__NUNITS__", str(len(UNITS)))

    # こちらのURLに結びつくものを落とす
    # robots(noindex) は残す。こちらのサーバーに置いている間は検索に出したくないため。
    # 先方のサイトに移すときに外してもらう（README に書いた）。
    for pat in (r'<link rel="canonical"[^>]*>\s*',
                r'<meta property="og:url"[^>]*>\s*', r'<meta property="og:image[^>]*>\s*',
                r'<meta name="twitter:[^>]*>\s*',
                r'<script type="application/ld\+json">[\s\S]*?</script>\s*'):
        html = re.sub(pat, "", html)
    for leak in ("mararararai-mst", "github.io"):
        if leak in html:
            sys.exit("NG 渡す版にこちらのURLが残っている: %s" % leak)

    # 提供元を1行足す（先方が中身を直したときに、こちらの判断だと誤解されないように）
    mark = "  <b>注意</b>："
    if mark not in html:
        sys.exit("NG フッターの注意書きが見つからない")
    html = html.replace(mark, "  <b>この表</b>：箕面市立とどろみの森学園 新井が作成し、"
                              "NPO法人eboardに提供したものです。自由に直してお使いください<br>" + mark, 1)

    check_js(html)
    for w in ("Medium", "Bold"):
        f = HERE / "font" / ("ZenMaruGothic-%s.subset.woff2" % w)
        uri = "data:font/woff2;base64," + base64.b64encode(f.read_bytes()).decode()
        html = html.replace('url("font/ZenMaruGothic-%s.subset.woff2")' % w, "url(%s)" % uri)
    assert "font/ZenMaruGothic" not in html, "フォントの埋め込みに失敗"
    (out / "sansu-doga-keito.html").write_text(html, encoding="utf-8")

    # 当てはめのデータ（枠＋どの単元をどこに置いたか＋戻り先と理由）
    (out / "keito.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=1), encoding="utf-8")

    # 人が読める形の一覧。直すときはこちらを見てもらう
    rows = ["領域,行,学年,この表での単元名,eboardの単元ID,eboardの単元名,動画の本数"]
    for g in cfg["groups"]:
        for r in g["rows"]:
            for grade in cfg["grades"]:
                for ch in r["cells"].get(grade, []):
                    cid = ch["apps"][0].split("-")[0]
                    rows.append(",".join('"%s"' % x for x in (
                        g["name"].replace("　", " "), r["name"], grade, ch["c"],
                        cid, UNITS[cid]["title"], str(len(ch["apps"])))))
    (out / "wariate.csv").write_text("﻿" + "\n".join(rows), encoding="utf-8")

    (out / "README.txt").write_text(README, encoding="utf-8")
    print("   渡す用 -> handover/（%d件の割り当て）" % (len(rows) - 1))


README = """小学校算数 動画系統表 — NPO法人eboard様へお渡しする一式

作成：箕面市立とどろみの森学園　研究部長　新井
（2026年10月。support@eboard.jp・杉山様とのやりとりを受けてお渡しするものです）


■ 中身

sansu-doga-keito.html   表そのもの。1ファイルで動きます。
                        サーバーに置いても、ダウンロードして開いても使えます。
                        フォント（Zen Maru Gothic / SIL OFL）は中に埋め込んであります。
                        外部から読み込むものは一切ありません。

keito.json              系統の枠と、どの単元をどこに置いたかのデータ。
                        表を作り直すときはこれを直します。

wariate.csv             同じ内容を人が読める形にしたもの（割り当て一覧）。
                        割り当てを見直すときはこちらが早いです。

README.txt              このファイル。


■ 表の作り

・縦が「領域」、横が「学年」です。枠組みは
  文部科学省『小学校学習指導要領（平成29年告示）解説 算数編』
  第1章 図1「小学校算数科の内容の構成」（pp.12-15）に合わせました。

・「A 数と計算」だけは、図1の内容を
  数のしくみ／たし算・ひき算／かけ算／わり算／小数／分数／式と文字
  の7行に分けています。先生が単元名から引きやすくするためです。

・マスを押すと、その単元の動画と確認問題へのリンクが出ます。
  あわせて下に2つ出ます。
    「この系統をたどる」   同じ行を学年順に並べたもの。左に戻るほど前の学年です。
    「もっと前に戻るなら」 別の行へ戻る道。理由もつけています。
      例：4年「わり算の筆算」→ 2年「かけ算と九九」
          （わり算はかけ算の逆。九九が言えないと商が立たない）

・この「戻る道」が、この表を作った理由そのものです。
  つまずいている子に、どこまで戻ればよいかを見えるようにしたいと考えました。


■ 割り当てについて

・91単元・484本すべてを、どこか1つのマスに1回だけ置いてあります。
・どの動画をどの単元に置くかは新井の判断で、貴団体の公式な分類ではありません。
  おかしいところは自由に直してください。
・1つの単元が明らかに2つの系統に分かれるものだけ、動画を分けて2つのマスに置きました
  （161 / 170 / 179 / 183 / 222 の5単元）。
・確認問題だけで動画が無いコマ（166 / 167 / 174 / 544 / 546 の末尾）は載せていません。
・単元名がひらがなのものには、検索用に別の言い方を持たせています
  （例：「とけいをよむ」を「時計」でも引けるようにしています）。


■ 貴団体のサイトに置かれる場合

sansu-doga-keito.html の <head> に、次の1行が入っています。

    <meta name="robots" content="noindex,follow">

これは当方のサーバーに置いている間、検索に出さないようにするためのものです。
貴団体のサイトで公開される場合は、この1行を削除してください。


■ お願い

・こちらで公開していたページは、ご案内のあった範囲（校内・家庭）にとどめ、
  検索にも出ないようにしてあります。貴団体のサイトに置いていただける場合は、
  こちらのページは取り下げても構いません。ご指示ください。
・取得に使ったプログラムは公開しておりません。今後も公開しません。
"""


main()
