#!/usr/bin/env python3
"""正典（サイト側）からブランドを一方向に写す。

  python3 tools/sync_brand.py          # 正典と SOURCE.json を比べ、変わったところを報告する（何も書かない）
  python3 tools/sync_brand.py --write  # ロゴを写し直し、SOURCE.json のハッシュを更新する

brand.md の本文は自動では書き換えない。変わった節を人（か Claude）が読んで直す。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1]
REPO = HARNESS.parent
BRAND = HARNESS / "brands" / "impress-racing"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def extract_sources() -> dict[str, dict]:
    """正典の中から、ブランドに効く部分だけを切り出してハッシュする。"""
    out: dict[str, dict] = {}

    readme = (REPO / "README.md").read_text(encoding="utf-8")
    m = re.search(r"^## デザインコンセプト\n(.*?)(?=^---|^## )", readme, re.S | re.M)
    section = m.group(1).strip() if m else ""
    out["README.md#デザインコンセプト"] = {"sha256": _sha(section.encode()), "excerpt": section[:200]}

    css = (REPO / "assets" / "shared.css").read_text(encoding="utf-8")
    m = re.search(r":root\s*\{(.*?)\}", css, re.S)
    tokens = dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", m.group(1))) if m else {}
    out["assets/shared.css#:root"] = {
        "sha256": _sha(json.dumps(tokens, sort_keys=True).encode()),
        "tokens": tokens,
    }

    for logo in sorted((REPO / "assets" / "logos").glob("*.png")):
        rel = logo.relative_to(REPO).as_posix()
        out[rel] = {"sha256": _sha(logo.read_bytes())}
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true", help="ロゴを写し、SOURCE.json を更新する")
    args = ap.parse_args()

    current = extract_sources()
    source_json = BRAND / "SOURCE.json"
    recorded = json.loads(source_json.read_text(encoding="utf-8"))["sources"] if source_json.exists() else {}

    changed = [k for k in current if recorded.get(k, {}).get("sha256") != current[k]["sha256"]]
    removed = [k for k in recorded if k not in current]
    if not changed and not removed:
        print("正典と一致しています。")
    for k in changed:
        print(f"変更あり: {k}")
        if "tokens" in current[k]:
            old = recorded.get(k, {}).get("tokens", {})
            for t, v in current[k]["tokens"].items():
                if old.get(t) != v:
                    print(f"    {t}: {old.get(t)} -> {v}")
    for k in removed:
        print(f"正典から消えた: {k}")

    if args.write:
        (BRAND / "assets").mkdir(parents=True, exist_ok=True)
        for k in current:
            if k.startswith("assets/logos/"):
                shutil.copy2(REPO / k, BRAND / "assets" / Path(k).name)
        source_json.write_text(
            json.dumps({"canon": "imp-racing リポジトリ直下（サイト本体）", "sources": current},
                       ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"書き込みました: {source_json.relative_to(REPO)}")
        if changed:
            print("→ brand.md の該当箇所を読み直して直してください（本文は自動では変えません）。")
        return 0
    return 1 if (changed or removed) else 0


if __name__ == "__main__":
    sys.exit(main())
