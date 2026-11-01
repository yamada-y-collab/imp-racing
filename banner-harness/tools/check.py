#!/usr/bin/env python3
"""機械の検査：文言・はみ出し・重なり・コントラスト。

  python3 tools/check.py <版のディレクトリ> --brief <brief.md>

out/layout.json と out/<size>.bg.png を読み、out/check.json に所見を書く。
error が1つでもあれば終了コード 1。

所見の種類（code）:
  missing-size      原稿にあるサイズの HTML がない                         error
  no-canvas         data-canvas の要素がない                               error
  canvas-size       data-canvas の実寸がファイル名のサイズと違う           error
  page-overflow     ページ全体がスクロールする（キャンバスからはみ出し）   error
  asset-missing     写真・ロゴが読み込めていない                           error
  must-keep         落としてはいけない語がない                             error
  copy-missing      入れる文言がない（省略可でないもの）                   error
  copy-omitted      省略可の文言を省いた                                   info
  ng-word           使わない語がある                                       error
  nested-role       text の中に別の data-role がある                       error
  text-overflow     文字が自分の箱からはみ出している                       error
  out-of-canvas     要素がキャンバスの外に出ている                         error
  safe-area         文字が安全域（短辺の5%）にかかる                       warn
  story-ui          1080x1920 で UI に隠れる帯に文字がある                 warn
  overlap           文字同士・文字とロゴが重なっている                     error
  font-too-small    10px 未満の文字                                        error
  contrast          地とのコントラストが 3:1 未満                          error
  contrast-small    小さな文字で 4.5:1 未満                                warn
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from brief import Brief, parse  # noqa: E402

TOL = 2.0  # px：測りの誤差として許す量


# ---------------------------------------------------------------- 文字の正規化
def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"\s+", "", s)
    return s.replace("–", "-").replace("—", "-").replace("―", "-").lower()


# ---------------------------------------------------------------- 色
def parse_color(css: str) -> tuple[float, float, float, float]:
    m = re.match(r"rgba?\(([^)]+)\)", css or "")
    if not m:
        return (0.0, 0.0, 0.0, 1.0)
    parts = [p.strip() for p in m.group(1).replace("/", ",").split(",")]
    r, g, b = (float(p) for p in parts[:3])
    a = float(parts[3]) if len(parts) > 3 else 1.0
    return (r, g, b, a)


def _lin(c: float) -> float:
    c /= 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb) -> float:
    r, g, b = rgb[:3]
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(l1: float, l2: float) -> float:
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def text_contrast(bg: Image.Image, box: dict, color: str, opacity: float) -> float | None:
    """文字の箱の中の地の画素ごとにコントラストを出し、悪い側から1割の値を返す。"""
    x0, y0 = max(0, int(box["x"])), max(0, int(box["y"]))
    x1, y1 = min(bg.width, int(box["x"] + box["w"])), min(bg.height, int(box["y"] + box["h"]))
    if x1 <= x0 or y1 <= y0:
        return None
    crop = bg.crop((x0, y0, x1, y1)).convert("RGB")
    crop.thumbnail((80, 80))  # 間引いて数える
    tr, tg, tb, ta = parse_color(color)
    a = ta * opacity
    ratios = []
    pixels = crop.get_flattened_data() if hasattr(crop, "get_flattened_data") else crop.getdata()
    for px in pixels:
        fg = (tr * a + px[0] * (1 - a), tg * a + px[1] * (1 - a), tb * a + px[2] * (1 - a))
        ratios.append(contrast(luminance(fg), luminance(px)))
    ratios.sort()
    return ratios[len(ratios) // 10]


# ---------------------------------------------------------------- 箱
def intersect(a: dict, b: dict) -> float:
    w = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])
    h = min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])
    return w * h if w > TOL and h > TOL else 0.0


def is_large(el: dict) -> bool:
    w = int(el.get("font_weight") or 400)
    return el["font_size"] >= 24 or (el["font_size"] >= 18.66 and w >= 700)


# ---------------------------------------------------------------- 本体
def check_size(size: str, data: dict, brief: Brief, out_dir: Path) -> list[dict]:
    f: list[dict] = []

    def add(level: str, code: str, msg: str, el: dict | None = None):
        f.append({"size": size, "level": level, "code": code, "message": msg,
                  **({"element": el["id"]} if el else {})})

    W, H = data["width"], data["height"]
    if not data["canvas"]["found"]:
        add("error", "no-canvas", "<main data-canvas> がありません")
    elif abs(data["canvas"]["w"] - W) > TOL or abs(data["canvas"]["h"] - H) > TOL:
        add("error", "canvas-size", f"キャンバスの実寸が {data['canvas']['w']:.0f}x{data['canvas']['h']:.0f} です")
    if data.get("document_overflow"):
        add("error", "page-overflow", "ページがキャンバスより大きく、スクロールします")
    for w in data.get("warnings", []):
        add("warn", "load", w)

    els = [e for e in data["elements"] if e["visible"]]
    texts = [e for e in els if e["role"] == "text"]
    logos = [e for e in els if e["role"] == "logo"]

    # 文言
    joined = norm(" ".join(e["text"] for e in texts))
    for word in brief.must_keep:
        if norm(word) not in joined:
            add("error", "must-keep", f"落としてはいけない語がありません：「{word}」")
    for line in brief.copy:
        if norm(line.text) not in joined:
            if line.optional:
                add("info", "copy-omitted", f"省略可の文言を省きました：「{line.text}」")
            else:
                add("error", "copy-missing", f"入れる文言がありません：「{line.text}」")
    for word in brief.ng_words:
        if norm(word) in joined:
            add("error", "ng-word", f"使わない語があります：「{word}」")

    # 素材
    for e in els:
        if e["role"] in ("image", "logo") and not e.get("loaded", True):
            add("error", "asset-missing", f"読み込めていません：{e.get('src')}", e)

    # 箱
    safe = min(W, H) * 0.05
    for e in els:
        b = e["box"]
        if b["x"] < -TOL or b["y"] < -TOL or b["x"] + b["w"] > W + TOL or b["y"] + b["h"] > H + TOL:
            if e["role"] in ("text", "logo"):
                add("error", "out-of-canvas", "キャンバスの外に出ています", e)
            continue
        if e["role"] == "text":
            if b["x"] < safe - TOL or b["y"] < safe - TOL or b["x"] + b["w"] > W - safe + TOL or b["y"] + b["h"] > H - safe + TOL:
                add("warn", "safe-area", f"安全域（端から {safe:.0f}px）にかかっています", e)
            if size == "1080x1920" and (b["y"] < 250 or b["y"] + b["h"] > 1920 - 340):
                add("warn", "story-ui", "ストーリーズの UI に隠れる帯（上250px・下340px）に入っています", e)

    for e in texts:
        if e.get("nested_roles"):
            add("error", "nested-role", "text の中に別の data-role があります", e)
        sc = e["scroll"]
        # 横は1pxでもはみ出せば error。縦は字面の上下の余白で数px出るのが普通なので、
        # 字の大きさの半分を超えたとき（＝1行余計に折り返した・切れた）だけ error にする
        if sc["w"] > sc["client_w"] + 1 or sc["h"] - sc["client_h"] > e["font_size"] * 0.5:
            add("error", "text-overflow", "文字が箱からはみ出しています", e)
        if e["font_size"] < 10:
            add("error", "font-too-small", f"{e['font_size']:.1f}px は小さすぎます（10px 以上）", e)

    pool = texts + logos
    for i, a in enumerate(pool):
        for b in pool[i + 1:]:
            if intersect(a["box"], b["box"]) > 0:
                f.append({"size": size, "level": "error", "code": "overlap",
                          "message": f"「{a['id']}」と「{b['id']}」が重なっています",
                          "element": a["id"], "other": b["id"]})

    # コントラスト
    bg_path = out_dir / f"{size}.bg.png"
    if bg_path.exists():
        bg = Image.open(bg_path)
        for e in texts:
            ratio = text_contrast(bg, e["box"], e["color"], e["opacity"])
            if ratio is None:
                continue
            e_ratio = round(ratio, 2)
            if ratio < 3.0:
                add("error", "contrast", f"地とのコントラストが {e_ratio}:1 です（3:1 以上）", e)
            elif ratio < 4.5 and not is_large(e):
                add("warn", "contrast-small", f"小さな文字のコントラストが {e_ratio}:1 です（4.5:1 推奨）", e)
    return f


def run(version_dir: Path, brief: Brief) -> dict:
    out_dir = version_dir / "out"
    layout = json.loads((out_dir / "layout.json").read_text(encoding="utf-8"))
    findings: list[dict] = []
    for size in brief.sizes:
        if size not in layout["sizes"]:
            findings.append({"size": size, "level": "error", "code": "missing-size",
                             "message": f"{size}.html がありません"})
            continue
        findings += check_size(size, layout["sizes"][size], brief, out_dir)
    summary = {lv: sum(1 for x in findings if x["level"] == lv) for lv in ("error", "warn", "info")}
    by_size = {s: ("error" if any(x["size"] == s and x["level"] == "error" for x in findings)
                   else "warn" if any(x["size"] == s and x["level"] == "warn" for x in findings)
                   else "ok") for s in brief.sizes}
    return {"summary": summary, "by_size": by_size, "findings": findings}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("version_dir", type=Path)
    ap.add_argument("--brief", type=Path, required=True)
    args = ap.parse_args()

    result = run(args.version_dir, parse(args.brief))
    (args.version_dir / "out" / "check.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for x in result["findings"]:
        mark = {"error": "✗", "warn": "!", "info": "·"}[x["level"]]
        el = f" [{x['element']}]" if "element" in x else ""
        print(f"{mark} {x['size']:>9} {x['code']:<15}{el} {x['message']}")
    s = result["summary"]
    print(f"error {s['error']} / warn {s['warn']} / info {s['info']}")
    return 1 if s["error"] else 0


if __name__ == "__main__":
    sys.exit(main())
