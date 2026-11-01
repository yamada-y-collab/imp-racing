#!/usr/bin/env python3
"""バナー制作の入口：init / generate / revise / export / status

  python3 banner-harness/tools/banner.py init <id>              原稿のひな形を work/<id>/brief.md に置く
  python3 banner-harness/tools/banner.py generate <id> [--run]  v1 の指示文（PROMPT.md）を組み立てる
  python3 banner-harness/tools/banner.py revise <id> "直し" [--run]
                                                                前の版を写して次の版を作り、直しの指示文を組み立てる
  python3 banner-harness/tools/banner.py export <id> [--version vN] [--strict]
                                                                実測 → 検査 → シート → PPTX（検査で止めない）
  python3 banner-harness/tools/banner.py status                 依頼ごとの最新版と検査の結果

--run を付けると `claude -p` で生成（直し）から export までを続けて回す。
付けなければ指示文を書くだけなので、Claude Code の会話の中で PROMPT.md に従って HTML を書く。
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1]
REPO = HARNESS.parent
TOOLS = HARNESS / "tools"
WORK = HARNESS / "work"
sys.path.insert(0, str(TOOLS))
from brief import parse  # noqa: E402


def rel(p: Path) -> str:
    try:
        return p.resolve().relative_to(REPO).as_posix()
    except ValueError:
        return str(p)


def versions(job: Path) -> list[Path]:
    vs = [p for p in job.glob("v*") if p.is_dir() and re.fullmatch(r"v\d+", p.name)]
    return sorted(vs, key=lambda p: int(p.name[1:]))


def job_dir(job_id: str, must_exist: bool = True) -> Path:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", job_id):
        sys.exit(f"id は英小文字・数字・ハイフンで：{job_id!r}")
    job = WORK / job_id
    if must_exist and not (job / "brief.md").exists():
        sys.exit(f"{rel(job / 'brief.md')} がありません。先に init してください。")
    return job


def compose_prompt(job: Path, out_dir: Path, revision: str | None) -> Path:
    brief = parse(job / "brief.md")
    brand = HARNESS / "brands" / brief.brand
    parts = [
        (HARNESS / "prompts" / f"generate-{brief.brand}.md").read_text(encoding="utf-8"),
        "---\n\n# 1. brand.md\n\n" + (brand / "brand.md").read_text(encoding="utf-8"),
        "---\n\n# 2. banner.md\n\n" + (brand / "banner.md").read_text(encoding="utf-8"),
        "---\n\n# 3. 原稿（brief.md）\n\n" + brief.raw,
    ]
    if revision:
        history = (job / "revisions.md").read_text(encoding="utf-8") if (job / "revisions.md").exists() else ""
        parts.append(
            "---\n\n# 4. 前の版への直し\n\n"
            f"今回の直し：\n\n> {revision}\n\n"
            f"`{rel(out_dir)}/` には前の版の HTML を写してある。**直しに関係するところだけ**を変え、"
            "ほかの組みは保つこと。\n\n" + (f"これまでの直し（古い順）：\n\n{history}\n" if history else "")
        )
    parts.append(
        "---\n\n# 出力\n\n"
        f"- 出力先：`{rel(out_dir)}/`（リポジトリ直下から）\n"
        f"- サイズ：{', '.join(brief.sizes)}\n"
        f"- 書き終えたら：`python3 banner-harness/tools/banner.py export {brief.id}`\n"
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    prompt = out_dir / "PROMPT.md"
    prompt.write_text("\n\n".join(parts), encoding="utf-8")
    return prompt


def run_claude(prompt: Path) -> None:
    if not shutil.which("claude"):
        sys.exit("claude コマンドが見つかりません。--run を外して、会話の中で PROMPT.md に従ってください。")
    subprocess.run(
        ["claude", "-p", prompt.read_text(encoding="utf-8"),
         "--allowedTools", "Read,Write,Edit,Glob,Grep,Bash(python3 banner-harness/tools/*),Bash(node banner-harness/tools/*)"],
        cwd=REPO, check=True,
    )


# ---------------------------------------------------------------- commands
def cmd_init(a) -> None:
    job = job_dir(a.id, must_exist=False)
    target = job / "brief.md"
    if target.exists():
        sys.exit(f"{rel(target)} はもうあります。")
    job.mkdir(parents=True, exist_ok=True)
    text = (HARNESS / "templates" / "brief.md").read_text(encoding="utf-8").replace("{{id}}", a.id)
    target.write_text(text, encoding="utf-8")
    print(f"原稿のひな形を置きました：{rel(target)}")


def cmd_generate(a) -> None:
    job = job_dir(a.id)
    if versions(job) and not a.force:
        sys.exit(f"もう {versions(job)[-1].name} があります。直しは revise、作り直しは --force。")
    v1 = job / "v1"
    if a.force and v1.exists():
        shutil.rmtree(v1)
    prompt = compose_prompt(job, v1, None)
    print(f"指示文：{rel(prompt)}")
    if a.run:
        run_claude(prompt)
        cmd_export(argparse.Namespace(id=a.id, version=None, strict=False))


def cmd_revise(a) -> None:
    job = job_dir(a.id)
    vs = versions(job)
    if not vs:
        sys.exit("まだ版がありません。先に generate。")
    prev, nxt = vs[-1], job / f"v{int(vs[-1].name[1:]) + 1}"
    nxt.mkdir()
    for html in prev.glob("*.html"):
        shutil.copy2(html, nxt / html.name)
    stamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    with (job / "revisions.md").open("a", encoding="utf-8") as fp:
        fp.write(f"- {stamp} {prev.name} → {nxt.name}：{a.note}\n")
    prompt = compose_prompt(job, nxt, a.note)
    print(f"{prev.name} を {nxt.name} に写しました。指示文：{rel(prompt)}")
    print("この直しが次の依頼にも効くなら、brands/<brand>/banner.md にも戻すこと。")
    if a.run:
        run_claude(prompt)
        cmd_export(argparse.Namespace(id=a.id, version=nxt.name, strict=False))


def cmd_export(a) -> None:
    job = job_dir(a.id)
    vs = versions(job)
    if not vs:
        sys.exit("まだ版がありません。")
    vdir = job / a.version if a.version else vs[-1]
    if not vdir.exists():
        sys.exit(f"{rel(vdir)} がありません。")
    brief = job / "brief.md"
    print(f"== {rel(vdir)}")
    subprocess.run(["node", str(TOOLS / "html2layout.mjs"), str(vdir)], cwd=REPO, check=True)
    code = subprocess.run([sys.executable, str(TOOLS / "check.py"), str(vdir), "--brief", str(brief)], cwd=REPO).returncode
    subprocess.run([sys.executable, str(TOOLS / "sheet.py"), str(vdir)], cwd=REPO, check=True)
    subprocess.run([sys.executable, str(TOOLS / "layout2pptx.py"), str(vdir)], cwd=REPO, check=True,
                   stdout=subprocess.DEVNULL)
    print(f"シート：{rel(vdir / 'out' / 'sheet.png')} ／ PPTX：{rel(vdir / 'out' / 'pptx')}/")
    # 検査は事故を見つけるためのもので、流れは止めない（所見は check.json として成果物と一緒に渡す）。
    # 止めたいとき（CI・無人実行で error を落としたいとき）だけ --strict を付ける。
    if code:
        print("検査で error が出ています。所見は out/check.json。人に見せる前に直すこと。")
    sys.exit(code if a.strict else 0)


def cmd_status(_a) -> None:
    jobs = sorted(p for p in WORK.glob("*") if (p / "brief.md").exists())
    if not jobs:
        print("依頼はまだありません。")
        return
    print(f"{'id':<28} {'版':<4} {'検査':<22} サイズ")
    for job in jobs:
        vs = versions(job)
        latest = vs[-1] if vs else None
        result = "未生成"
        if latest and (latest / "out" / "check.json").exists():
            s = json.loads((latest / "out" / "check.json").read_text(encoding="utf-8"))["summary"]
            result = f"error {s['error']} / warn {s['warn']}"
        elif latest:
            result = "未書き出し"
        sizes = len(parse(job / "brief.md").sizes)
        print(f"{job.name:<28} {latest.name if latest else '-':<4} {result:<22} {sizes}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init"); p.add_argument("id"); p.set_defaults(fn=cmd_init)
    p = sub.add_parser("generate"); p.add_argument("id"); p.add_argument("--run", action="store_true")
    p.add_argument("--force", action="store_true"); p.set_defaults(fn=cmd_generate)
    p = sub.add_parser("revise"); p.add_argument("id"); p.add_argument("note"); p.add_argument("--run", action="store_true")
    p.set_defaults(fn=cmd_revise)
    p = sub.add_parser("export"); p.add_argument("id"); p.add_argument("--version")
    p.add_argument("--strict", action="store_true", help="検査で error があれば終了コード 1"); p.set_defaults(fn=cmd_export)
    p = sub.add_parser("status"); p.set_defaults(fn=cmd_status)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
