#!/usr/bin/env python3
"""全サイズを1枚のシートに並べる（人が一度に見比べるため）。

  python3 tools/sheet.py <版のディレクトリ>   → out/sheet.png
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BG = (235, 233, 226)        # --paper-2
INK = (10, 10, 10)
STATUS = {"ok": (40, 140, 80), "warn": (200, 140, 20), "error": (255, 29, 76)}
BOX = 560                   # 1枚の長辺の上限
GAP = 40
SHEET_W = 1900


def main(version_dir: Path) -> Path:
    out = version_dir / "out"
    layout = json.loads((out / "layout.json").read_text(encoding="utf-8"))
    check_path = out / "check.json"
    by_size = json.loads(check_path.read_text(encoding="utf-8"))["by_size"] if check_path.exists() else {}

    tiles = []
    for size, data in layout["sizes"].items():
        img = Image.open(out / f"{size}.png").convert("RGB")
        k = min(BOX / data["width"], BOX / data["height"], 1.0)
        tiles.append((size, img.resize((round(img.width * k), round(img.height * k)), Image.LANCZOS)))

    try:
        font = ImageFont.load_default(size=22)
    except TypeError:  # 古い Pillow
        font = ImageFont.load_default()

    # 左から詰め、幅を超えたら次の段へ
    rows, row, x = [], [], GAP
    for size, img in tiles:
        if row and x + img.width + GAP > SHEET_W:
            rows.append(row)
            row, x = [], GAP
        row.append((size, img))
        x += img.width + GAP
    if row:
        rows.append(row)

    label_h = 40
    height = GAP + sum(max(i.height for _, i in r) + label_h + GAP for r in rows)
    sheet = Image.new("RGB", (SHEET_W, height), BG)
    draw = ImageDraw.Draw(sheet)
    y = GAP
    for r in rows:
        x = GAP
        for size, img in r:
            status = by_size.get(size, "ok")
            draw.rectangle((x, y + 8, x + 14, y + 22), fill=STATUS.get(status, INK))
            draw.text((x + 24, y + 4), f"{size}  {status.upper()}", fill=INK, font=font)
            sheet.paste(img, (x, y + label_h))
            x += img.width + GAP
        y += max(i.height for _, i in r) + label_h + GAP

    path = out / "sheet.png"
    sheet.save(path, optimize=True)
    return path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    print(main(Path(sys.argv[1])))
