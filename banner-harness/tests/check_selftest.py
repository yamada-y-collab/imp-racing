#!/usr/bin/env python3
"""わざと壊した入力で、検査が鳴るかを確かめる（ブラウザは使わない）。

  python3 banner-harness/tests/check_selftest.py

layout.json と地の画像を手で作り、壊し方ごとに check.py が期待どおりの code を出すかを見る。
壊していない入力では error も warn も出ないことも確かめる。
"""
from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import check  # noqa: E402
from brief import parse  # noqa: E402

BRIEF = """---
id: selftest
sizes:
  - 600x400
---

## 入れる文言

- SUPER FORMULA
- 鈴鹿サーキット
- VIEW SF SITE →（省略可）

## 落としてはいけない語

- チャーリー・ブルツ

## 使わない語

- ヴルツ
"""


def text(id_, x, y, w, h, s, *, color="rgb(255, 255, 255)", size=24.0):
    return {
        "index": 0, "role": "text", "id": id_, "box": {"x": x, "y": y, "w": w, "h": h},
        "opacity": 1.0, "visible": True, "background_color": "rgba(0, 0, 0, 0)",
        "text": s, "color": color, "font_family": "Anton", "font_size": size, "font_weight": "400",
        "letter_spacing": "normal", "line_height": "normal", "text_align": "left", "line_count": 1,
        "scroll": {"w": w, "h": h, "client_w": w, "client_h": h}, "nested_roles": False,
    }


GOOD = {
    "width": 600, "height": 400, "html": "600x400.html", "warnings": [],
    "canvas": {"w": 600, "h": 400, "found": True}, "document_overflow": False,
    "elements": [
        text("series", 40, 60, 360, 60, "SUPER FORMULA", size=48),
        text("circuit", 40, 140, 300, 40, "鈴鹿サーキット"),
        text("driver", 40, 200, 300, 40, "チャーリー・ブルツ"),
        {"index": 3, "role": "logo", "id": "logo", "box": {"x": 480, "y": 300, "w": 60, "h": 60},
         "opacity": 1.0, "visible": True, "background_color": "rgba(0, 0, 0, 0)", "src": "x.png", "loaded": True},
    ],
}


def run_case(name: str, mutate, expect: set[str], bg_color=(10, 10, 10)) -> bool:
    data = copy.deepcopy(GOOD)
    mutate(data)
    with tempfile.TemporaryDirectory() as tmp:
        vdir = Path(tmp)
        (vdir / "out").mkdir()
        (vdir / "out" / "layout.json").write_text(json.dumps({"sizes": {"600x400": data}}), encoding="utf-8")
        Image.new("RGB", (600, 400), bg_color).save(vdir / "out" / "600x400.bg.png")
        (vdir / "brief.md").write_text(BRIEF, encoding="utf-8")
        result = check.run(vdir, parse(vdir / "brief.md"))
    got = {f["code"] for f in result["findings"] if f["level"] in ("error", "warn")}
    ok = got == expect
    print(f"{'ok ' if ok else 'NG '} {name:<28} 期待 {sorted(expect)} / 実際 {sorted(got)}")
    return ok


def el(data, id_):
    return next(e for e in data["elements"] if e["id"] == id_)


CASES = [
    ("壊していない", lambda d: None, set()),
    ("落としてはいけない語が消えた", lambda d: el(d, "driver").update(text="CHARLIE WURZ"), {"must-keep"}),
    ("入れる文言が消えた", lambda d: el(d, "circuit").update(text="SUZUKA"), {"copy-missing"}),
    ("使わない語", lambda d: el(d, "driver").update(text="チャーリー・ブルツ（ヴルツ）"), {"ng-word"}),
    ("文字同士が重なる", lambda d: el(d, "circuit")["box"].update(y=100), {"overlap"}),
    ("文字とロゴが重なる", lambda d: el(d, "logo")["box"].update(x=60, y=200), {"overlap"}),
    ("キャンバスの外", lambda d: el(d, "series")["box"].update(x=420), {"out-of-canvas"}),
    ("安全域にかかる", lambda d: el(d, "series")["box"].update(x=8), {"safe-area"}),
    ("横にはみ出す", lambda d: el(d, "series")["scroll"].update(w=420), {"text-overflow"}),
    ("縦に1行余計", lambda d: el(d, "circuit")["scroll"].update(h=80), {"text-overflow"}),
    ("縦の字面の余白は許す", lambda d: el(d, "series")["scroll"].update(h=66), set()),
    ("小さすぎる文字", lambda d: el(d, "circuit").update(font_size=9.0), {"font-too-small"}),
    ("画像が読めない", lambda d: el(d, "logo").update(loaded=False), {"asset-missing"}),
    ("キャンバスの寸法違い", lambda d: d["canvas"].update(w=640), {"canvas-size"}),
]


def main() -> int:
    results = [run_case(n, m, e) for n, m, e in CASES]
    # 地を明るくすると、白文字はすべてコントラスト不足になる
    results.append(run_case("明るい地に白文字", lambda d: None, {"contrast"}, bg_color=(235, 233, 226)))
    # 中間の灰色の地（白との比 約3.6:1）：24px 以上は通り、16px の文字だけ warn
    results.append(run_case("灰色の地に小さな白文字", lambda d: el(d, "driver").update(font_size=16.0),
                            {"contrast-small"}, bg_color=(135, 135, 135)))
    failed = results.count(False)
    print(f"{len(results) - failed}/{len(results)} 通過")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
