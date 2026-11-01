#!/usr/bin/env python3
"""layout.json → PPTX（サイズごとに1ファイル。Canva にドラッグして仕上げる）。

  python3 tools/layout2pptx.py <版のディレクトリ>   → out/pptx/<幅>x<高さ>.pptx

1枚のスライドに次の順で重ねる。
  1. 背景：out/<size>.bg.png（写真・scrim・図形を焼き込んだ地。文字とロゴは入っていない）
  2. ロゴ：画像として配置（差し替えられる）
  3. 文字：テキストボックスとして配置（直せる）

写真や図形を個別に動かしたいときは Canva 側で背景を差し替える。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Pt

EMU_PER_PX = 9525  # 96dpi
ALIGN = {"left": PP_ALIGN.LEFT, "start": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER,
         "right": PP_ALIGN.RIGHT, "end": PP_ALIGN.RIGHT}


def px(v: float) -> Emu:
    return Emu(int(round(v * EMU_PER_PX)))


def first_family(css: str) -> str:
    return re.split(r",", css or "")[0].strip().strip('"\'') or "Noto Sans JP"


def rgb(css: str) -> tuple[RGBColor, float]:
    m = re.match(r"rgba?\(([^)]+)\)", css or "")
    if not m:
        return RGBColor(0, 0, 0), 1.0
    parts = [p.strip() for p in m.group(1).replace("/", ",").split(",")]
    return RGBColor(*(int(float(p)) for p in parts[:3])), float(parts[3]) if len(parts) > 3 else 1.0


def build(size: str, data: dict, out: Path) -> Path:
    prs = Presentation()
    prs.slide_width, prs.slide_height = px(data["width"]), px(data["height"])
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # 白紙

    slide.shapes.add_picture(str(out / f"{size}.bg.png"), 0, 0, prs.slide_width, prs.slide_height)

    for el in data["elements"]:
        if not el["visible"]:
            continue
        b = el["box"]
        if el["role"] == "logo" and el.get("src_path") and Path(el["src_path"]).exists():
            # object-fit: contain を想定し、元画像の縦横比で箱の中に収める
            nat = el.get("natural") or {}
            w, h = b["w"], b["h"]
            if nat.get("w") and nat.get("h"):
                k = min(b["w"] / nat["w"], b["h"] / nat["h"])
                w, h = nat["w"] * k, nat["h"] * k
            pic = slide.shapes.add_picture(el["src_path"], px(b["x"] + (b["w"] - w) / 2),
                                           px(b["y"] + (b["h"] - h) / 2), px(w), px(h))
            pic.name = el["id"]
        elif el["role"] == "text":
            tb = slide.shapes.add_textbox(px(b["x"]), px(b["y"]), px(b["w"]), px(b["h"]))
            tb.name = el["id"]
            tf = tb.text_frame
            tf.word_wrap = el.get("line_count", 1) > 1
            tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
            tf.vertical_anchor = MSO_ANCHOR.TOP
            color, alpha = rgb(el["color"])
            for i, line in enumerate(el["text"].split("\n")):
                p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                p.alignment = ALIGN.get(el.get("text_align"), PP_ALIGN.LEFT)
                run = p.add_run()
                run.text = line
                f = run.font
                f.name = first_family(el["font_family"])
                f.size = Pt(el["font_size"] * 0.75)
                f.bold = int(el.get("font_weight") or 400) >= 700
                f.color.rgb = color
                if alpha < 1 or el.get("opacity", 1) < 1:
                    # python-pptx に透明度の API がないので XML に直接書く
                    srgb = f.color._xFill.find(".//{http://schemas.openxmlformats.org/drawingml/2006/main}srgbClr")
                    a = srgb.makeelement("{http://schemas.openxmlformats.org/drawingml/2006/main}alpha",
                                         {"val": str(int(alpha * el.get("opacity", 1) * 100000))})
                    srgb.append(a)

    path = out / "pptx" / f"{size}.pptx"
    path.parent.mkdir(exist_ok=True)
    prs.save(path)
    return path


def main(version_dir: Path) -> list[Path]:
    out = version_dir / "out"
    layout = json.loads((out / "layout.json").read_text(encoding="utf-8"))
    return [build(size, data, out) for size, data in layout["sizes"].items()]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    for p in main(Path(sys.argv[1])):
        print(p)
