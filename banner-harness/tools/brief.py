"""原稿（brief.md）を読む。"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

OPTIONAL_MARK = re.compile(r"[（(]\s*省略可\s*[)）]\s*$")


@dataclass
class CopyLine:
    text: str
    optional: bool = False


@dataclass
class Brief:
    id: str
    brand: str
    sizes: list[str]
    link: str | None
    purpose: str
    copy: list[CopyLine] = field(default_factory=list)
    must_keep: list[str] = field(default_factory=list)
    ng_words: list[str] = field(default_factory=list)
    raw: str = ""


def _sections(body: str) -> dict[str, str]:
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    parts = re.split(r"^##\s+(.+?)\s*$", body, flags=re.M)
    return {parts[i].strip(): parts[i + 1] for i in range(1, len(parts) - 1, 2)}


def _items(text: str) -> list[str]:
    out = []
    for line in text.splitlines():
        m = re.match(r"^\s*[-*]\s+(.*\S)\s*$", line)
        if m:
            out.append(m.group(1))
    return out


def parse(path: Path) -> Brief:
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    if not m:
        raise ValueError(f"{path}: 先頭に --- で囲んだ設定（id / sizes など）がありません")
    meta = yaml.safe_load(m.group(1)) or {}
    sec = _sections(m.group(2))

    copy = []
    for item in _items(sec.get("入れる文言", "")):
        optional = bool(OPTIONAL_MARK.search(item))
        copy.append(CopyLine(OPTIONAL_MARK.sub("", item).strip(), optional))

    sizes = [str(s) for s in meta.get("sizes") or []]
    for s in sizes:
        if not re.fullmatch(r"\d+x\d+", s):
            raise ValueError(f"{path}: サイズ {s!r} は 幅x高さ（例 1200x628）で書いてください")

    return Brief(
        id=str(meta.get("id", path.parent.name)),
        brand=str(meta.get("brand", "impress-racing")),
        sizes=sizes,
        link=meta.get("link"),
        purpose=sec.get("目的", "").strip(),
        copy=copy,
        must_keep=_items(sec.get("落としてはいけない語", "")),
        ng_words=_items(sec.get("使わない語", "")),
        raw=raw,
    )
