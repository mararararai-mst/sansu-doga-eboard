# -*- coding: utf-8 -*-
"""eboard の 91 単元を、学習指導要領の系統（領域×学年）に当てはめて keito.json にする。

書き方： "158" = その単元の動画ぜんぶ ／ "161:1" = v1 だけ ／ "183:7-9" = v7〜v9
1単元＝1チップ。置く行はその単元の主な内容で決める。
1つの単元が明らかに2つの系統に割れているものだけ、動画を分けて2つのチップにした（5件）。
"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
UNITS = {u["id"]: u for u in json.loads((HERE / "_src" / "eboard_sansu.json").read_text(encoding="utf-8"))}
UNITS["700"]["grade"] = "小５"          # eboard側に学年タグが無い。単元名が「変わり方調べ（５年生）」
G = ["1年", "2年", "3年", "4年", "5年", "6年"]

# 行の定義（学習指導要領 解説 算数編 図1 の領域）。before = つまずいたときに戻る別の系統
ROWS = [
 ("A　数と計算", [
  ("kazu", "数のしくみ", "数える・位取り・大きな数・概数・整数の性質", None),
  ("tashihiki", "たし算・ひき算", "加法・減法", [
    ("kazu", "10の補数・位取りがあいまいだと、くり上がり・くり下がりで止まる", "1年", "10までのかず")]),
  ("kake", "かけ算", "乗法", [
    ("tashihiki", "かけ算は同じ数を何回もたす（累加）。たし算が止まるなら先にそこへ", "1年", "たしざん")]),
  ("wari", "わり算", "除法", [
    ("kake", "わり算はかけ算の逆。九九が言えないと商が立たない", "2年", "かけ算と九九"),
    ("tashihiki", "あまりを出すにはひき算。筆算は「たてる・かける・ひく・おろす」", "2年", "２けたのひっさん")]),
  ("shosu", "小数", "", [
    ("kazu", "小数は位取りの延長（1/10の位）。位の部屋が見えていないと読めない", "3年", "10倍"),
    ("tashihiki", "小数の加減は整数の筆算と同じ手順", "2年", "２けたのひっさん")]),
  ("bunsu", "分数", "", [
    ("wari", "分数は「等分」から。等分除のイメージが土台", "3年", "わり算"),
    ("kake", "約分・通分は約数・倍数（＝九九）を使う", "2年", "かけ算と九九")]),
  ("shiki", "式と文字", "□を使った式・文字を用いた式", [
    ("tashihiki", "式に表す前に、たし算・ひき算の場面を言葉で言えるか", "2年", "文しょうだい")]),
 ]),
 ("B　図形", [
  ("zukei", "図形", "形・角・面積・体積（4年以上の面積・角・体積はB図形）", [
    ("kake", "面積・体積の公式はかけ算。単位の換算は位取り", "2年", "かけ算と九九")]),
 ]),
 ("C　測定（1〜3年）→ 変化と関係（4〜6年）", [
  ("ryou", "量と単位", "長さ・かさ・重さ・メートル法", [
    ("kazu", "単位の換算は10倍・100倍・1/10の位取りそのもの", "3年", "10倍")]),
  ("jikoku", "時こくと時間", "", [
    ("kazu", "60進法の前に、5とび・10とびで数えられるか", "1年", "10までのかず")]),
  ("henka", "変化と関係", "割合・比例・速さ・比", [
    ("wari", "割合・単位量あたりは「わり算の意味」の拡張", "3年", "わり算"),
    ("shosu", "百分率・小数倍は小数のかけ算・わり算", "5年", "小数×小数")]),
 ]),
 ("D　データの活用", [
  ("data", "データの活用", "表・グラフ・代表値・場合の数", None),
 ]),
]

# (行, 学年) -> [(チップ名, 動画の指定)]。チップ名を省くと eboard の単元名をそのまま使う
MAP = {
 ("kazu", "1年"): ["158", ("20までのかず", "161:1"), "163"],
 ("kazu", "2年"): [("100より大きい数（3けたの数）", "170:1-4"), "177"],
 ("kazu", "3年"): [("大きな数と数直線", "183:1-6"), ("10倍・100倍、÷10", "183:7-9")],
 ("kazu", "4年"): [("大きな数（億・兆）", "222:1-2"), "258"],
 ("kazu", "5年"): ["554", "268"],

 ("tashihiki", "1年"): ["159", "160", ("20までのたしざん・ひきざん", "161:2-5"), "162", "544", "164"],
 ("tashihiki", "2年"): ["166", "167", "169", "172", "173",
                        ("3けたのたし算・ひき算", "170:5"), "536",
                        ("文しょうだい（図・ちがい）", "179:1-4")],
 ("tashihiki", "3年"): ["182", "547"],
 ("tashihiki", "4年"): ["223"],

 ("kake", "2年"): ["174", "537", ("文しょうだい（かけ算）", "179:5")],
 ("kake", "3年"): ["540", "212", "217", "219"],
 ("kake", "4年"): [("×3けたのかけ算", "222:3-4")],

 ("wari", "3年"): ["180", "546", "187"],
 ("wari", "4年"): ["221", "257"],

 ("shosu", "3年"): ["216"],
 ("shosu", "4年"): ["225", "260", "263"],
 ("shosu", "5年"): ["265", "266"],

 ("bunsu", "2年"): ["538"],
 ("bunsu", "3年"): ["214"],
 ("bunsu", "4年"): ["261"],
 ("bunsu", "5年"): ["269", "271"],
 ("bunsu", "6年"): ["282", "556"],

 ("shiki", "3年"): ["218"],
 ("shiki", "6年"): ["283"],

 ("zukei", "2年"): ["175", "539"],
 ("zukei", "3年"): ["181", "186"],
 ("zukei", "4年"): ["220", "259", "226", "262"],
 ("zukei", "5年"): ["264", "267", "270", "276", "555"],
 ("zukei", "6年"): ["281", "285", "288"],

 ("ryou", "2年"): ["168", "171", "545"],
 ("ryou", "3年"): ["185", "213"],

 ("jikoku", "1年"): ["534"],
 ("jikoku", "2年"): ["165"],
 ("jikoku", "3年"): ["184"],

 ("henka", "4年"): ["541", "542"],
 ("henka", "5年"): ["272", "286", "273", "274", "553", "700"],
 ("henka", "6年"): ["284", "287"],

 ("data", "2年"): ["535"],
 ("data", "3年"): ["215"],
 ("data", "4年"): ["224"],
 ("data", "5年"): ["275"],
 ("data", "6年"): ["290", "289"],
}

# 検索用の別の言い方。eboardの単元名はひらがなが多く、先生は漢字で打つ。
# 実際に空振りした語（時計／くり上がり／くり下がり／箱／位取り）を拾えるようにする。
ALT = {
 "とけいをよむ": "時計 時こく 何時",
 "時間と生活": "時計 時こく",
 "時間と時こく": "時計",
 "10よりおおきいたしざん、ひきざん": "くり上がり くり下がり",
 "２けたのひっさん": "くり上がり くり下がり 筆算",
 "２けた+１けたのたしざん": "くり上がり",
 "２けた－１けたのひきざん": "くり下がり",
 "３けた－２けたのひき算": "くり下がり",
 "２けたのたし算": "くり上がり",
 "はこの形": "箱 立体 面 辺 頂点",
 "100までのかず": "位取り くらい",
 "100より大きい数（3けたの数）": "位取り くらい",
 "1000より大きい数": "位取り くらい",
 "大きな数と数直線": "位取り くらい",
 "整数と小数": "位取り くらい",
 "ながさをはかる": "長さ ものさし",
 "かさをあらわす": "かさ 水のかさ",
}

GRADE_JP = {"小１": "1年", "小２": "2年", "小３": "3年", "小４": "4年", "小５": "5年", "小６": "6年"}


def pick(spec):
    """183:7-9 -> ("183", [7,8,9])"""
    if ":" not in spec:
        return spec, [v["v"] for v in UNITS[spec]["videos"]]
    cid, sel = spec.split(":")
    out = []
    for part in sel.split(","):
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    have = {v["v"] for v in UNITS[cid]["videos"]}
    bad = [v for v in out if v not in have]
    if bad:
        sys.exit("NG %s に v%s が無い" % (cid, bad))
    return cid, out


def main():
    used = {}            # (cid, v) -> チップ名。重複・漏れの検査用
    alt_used = set()     # ALT のキーが実在するチップ名か（名前を変えたら気づけるように）
    groups = []
    for gname, rows in ROWS:
        grows = []
        for rid, rname, rsub, bef in rows:
            cells = {}
            for g in G:
                chips = []
                for item in MAP.get((rid, g), []):
                    name, spec = item if isinstance(item, tuple) else (None, item)
                    cid, vs = pick(spec)
                    u = UNITS[cid]
                    if GRADE_JP.get(u["grade"]) != g:
                        sys.exit("NG %s %s は eboard では %s。%s に置こうとしている"
                                 % (cid, u["title"], u["grade"], g))
                    c = name or u["title"]
                    for v in vs:
                        key = (cid, v)
                        if key in used:
                            sys.exit("NG %s v%d が %s と %s で二重" % (cid, v, used[key], c))
                        used[key] = c
                    # 単元を分けたチップは、eboard側の単元名も出す（あちらで探せるように）
                    full = u["nerai"] if c == u["title"] else                         "eboardの単元「%s」より。%s" % (u["title"], u["nerai"])
                    ch = {"c": c, "full": full,
                          "apps": ["%s-%d" % (cid, v) for v in vs]}
                    if c in ALT:
                        ch["alt"] = ALT[c]
                        alt_used.add(c)
                    chips.append(ch)
                if chips:
                    cells[g] = chips
            grows.append({"id": rid, "name": rname, "sub": rsub, "cells": cells,
                          "before": [{"row": b[0], "why": b[1], "grade": b[2], "chip": b[3]}
                                     for b in bef] if bef else None})
        groups.append({"name": gname, "rows": grows})

    # 検査：全部の動画が1回だけ置かれているか
    allv = {(u["id"], v["v"]) for u in UNITS.values() for v in u["videos"]}
    miss = sorted(allv - set(used))
    if miss:
        for cid, v in miss:
            print("NG 置き忘れ %s v%d %s（%s）"
                  % (cid, v, UNITS[cid]["title"], UNITS[cid]["grade"]), file=sys.stderr)
        sys.exit("NG %d 本の動画がどこにも置かれていない" % len(miss))
    # 検査：戻り先の row と chip が実在するか
    index = {r["id"]: r for g in groups for r in g["rows"]}
    for r in index.values():
        for b in (r["before"] or []):
            t = index.get(b["row"])
            if not t:
                sys.exit("NG %s の戻り先 row %s が無い" % (r["id"], b["row"]))
            hit = [c for c in t["cells"].get(b["grade"], []) if b["chip"] in c["c"]]
            if not hit:
                sys.exit("NG %s の戻り先 %s %s %s が見つからない"
                         % (r["id"], b["row"], b["grade"], b["chip"]))

    bad = sorted(set(ALT) - alt_used)
    if bad:
        sys.exit("NG ALT のキーに合うチップが無い: %s" % bad)

    cfg = {
        "_note": "系統（領域・行・戻り先）は 文科省『小学校学習指導要領（平成29年告示）解説 算数編』"
                 "第1章 図1（pp.12-15）にもとづく。どの単元をどの行に置くかは あらい の判断で、"
                 "eboard公式の分類ではない。",
        "grades": G,
        "colHead": "領域／系統",
        "chainTitle": "この系統をたどる（上が下の学年）",
        "beforeTitle": "もっと前に戻るなら（別の系統）",
        "nowLabel": "いま見ている学年",
        "text": {
            "TITLE": "小学校算数 動画系統表",
            "DESC": "ICT教材eboardの無料映像授業__NAPPS__本を、学習指導要領の系統（領域×学年）にならべたリンク集。"
                    "単元を押すと動画と確認問題、つまずいた子には「戻る先」が出ます。",
            "SUB": "ICT教材eboardの無料映像授業 __NAPPS__ 本を、学習指導要領の系統でならべたリンク集",
            "CANON": "https://mararararai-mst.github.io/sansu-doga-eboard/",
            "SOURCE": "文部科学省『小学校学習指導要領（平成29年告示）解説 算数編』"
                      "第1章 図1「小学校算数科の内容の構成」（pp.12-15）の文言を短くしたもの。"
                      "「式と文字」は図1の「A 数と計算」のうち、□を使った式・文字を用いた式をまとめた行",
            "HOWTO": "授業で使う → その学年の列から選ぶ／"
                     "つまずいている子に → 単元を押して「この系統をたどる」を左（下の学年）へ戻る",
            "UNIT": "単元名",
            "LEG1": "単元を押すと",
            "LEG2": "、動画と「つまずいたら戻る先」が出ます",
            "LEG3": "動画なし（戻る先だけ出ます）",
        },
        "groups": groups,
    }
    p = HERE / "keito.json"
    p.write_text(json.dumps(cfg, ensure_ascii=False, indent=1), encoding="utf-8")
    nchip = sum(len(c) for g in groups for r in g["rows"] for c in r["cells"].values())
    print("OK 単元%d / 動画%d / チップ%d -> %s" % (len(UNITS), len(used), nchip, p.name))
    for g in groups:
        for r in g["rows"]:
            per = {k: sum(len(c["apps"]) for c in v) for k, v in r["cells"].items()}
            print("  %-10s %s" % (r["id"], "  ".join("%s:%d本" % (k, per[k]) for k in G if k in per) or "（なし）"))


main()
