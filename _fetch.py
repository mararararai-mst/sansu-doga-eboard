# -*- coding: utf-8 -*-
"""eboard 小学算数の単元ページを集めて _src/eboard_sansu.json にする。
単元の並び順は eboard の一覧（/get_cl_part/7/）どおり。"""
import json, re, sys, time, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "_src"
UA = {"User-Agent": "Mozilla/5.0 (educational link collection; m.arararara.i@gmail.com)"}
SUBJECT = 7  # 小学算数


def get(url, cache=None):
    if cache and cache.exists():
        return cache.read_text(encoding="utf-8")
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        h = r.read().decode("utf-8", "replace")
    if cache:
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(h, encoding="utf-8")
        time.sleep(0.4)
    return h


def unit_ids():
    h = get("https://www.eboard.jp/get_cl_part/%d/" % SUBJECT)
    (SRC / "list.html").write_text(h, encoding="utf-8")
    return list(dict.fromkeys(re.findall(r'href="/content/(\d+)/"', h)))


def parse_unit(cid, h):
    t = re.search(r"<title>\s*【(.*?)】", h, re.S)
    title = t.group(1).strip() if t else ""
    g = re.search(r"(小[１２３４５６])で学習", h)
    if not g:
        g = re.search(r'name="(小[１２３４５６])"', h)
    grade = g.group(1) if g else ""
    n = re.search(r"【小学算数】小[１２３４５６]で学習する「[^」]*」の単元です。(.*?)(?:\"\s*/>|<)", h, re.S)
    nerai = re.sub(r"\s+", " ", n.group(1)).replace("**", "").strip() if n else ""
    vids = []
    for m in re.finditer(r"<article\b.*?</article>", h, re.S):
        a = m.group(0)
        v = re.search(r'href="/content/%s/v/(\d+)/"' % cid, a)
        if not v:
            continue
        h3 = re.search(r"<h3[^>]*>(.*?)</h3>", a, re.S)
        name = re.sub(r"<[^>]+>", "", h3.group(1)).strip() if h3 else ""
        name = re.sub(r"^\d+\.\s*", "", re.sub(r"\s+", " ", name))
        dur = re.search(r">(\d\d:\d\d)<", a)
        q = re.search(r"確認問題\s*(\d+)問", a)
        if name == "動画なし" or not dur:
            continue  # 確認問題だけのコマ（動画が無い）
        vids.append({
            "v": int(v.group(1)),
            "name": name,
            "min": dur.group(1),
            "q": int(q.group(1)) if q else 0,
        })
    vids.sort(key=lambda x: x["v"])
    return {"id": cid, "title": title, "grade": grade, "nerai": nerai, "videos": vids}


def main():
    SRC.mkdir(exist_ok=True)
    ids = unit_ids()
    print("単元 %d 件" % len(ids), flush=True)
    out = []
    for i, cid in enumerate(ids, 1):
        h = get("https://www.eboard.jp/content/%s/" % cid, SRC / "pages" / ("%s.html" % cid))
        u = parse_unit(cid, h)
        out.append(u)
        print("%3d/%d  %s  %s  動画%d本%s" % (
            i, len(ids), u["grade"] or "??", u["title"], len(u["videos"]),
            "" if u["videos"] else "  ★動画なし"), flush=True)
    p = SRC / "eboard_sansu.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    tv = sum(len(u["videos"]) for u in out)
    print("\n%s\n単元 %d / 動画 %d 本" % (p, len(out), tv))
    bad = [u for u in out if not u["grade"] or not u["videos"]]
    if bad:
        print("要確認 %d 件: %s" % (len(bad), ", ".join(u["title"] for u in bad)))


if __name__ == "__main__":
    main()
