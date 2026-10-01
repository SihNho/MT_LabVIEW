r"""freeze_docs_d1.py - card chat-D1 step 1 (user 2026-10-02 "문서 정리안 전체", brief_chat-D1.md).

FREEZE IN PLACE, LINE NUMBERS UNCHANGED. For each long plan/decision document: the existing frontmatter `status:`
VALUE becomes `frozen` on the same line (no line added or removed), and a short footer is APPENDED at the end. Then
the script PROVES it: for every k up to the old line count, new line k == old line k (line terminator ignored only on
the old LAST line, which gains a newline if it had none); the one exception is the status line, whose new text must be
exactly `status: frozen`. Everything is recorded in tools/bench/freeze_docs_d1.json (old/new md5, line counts).

Prior art checked: tools/frontmatter.py WRITES frontmatter for files lacking it (it does not edit a status value);
no existing script freezes a doc. Offline only - no LabVIEW, no COM.

Prediction contract: 5 files frozen; per file 1 status line changed, 0 old lines otherwise different, new line count
== old + footer lines; idempotent (a file already `status: frozen` with the footer marker is verified, not re-written).
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402

MARK = "<!-- FROZEN-FOOTER chat-D1 -->"
INDEX = "docs/d1/INDEX.md"
COMMON = ("Frozen IN PLACE on 2026-10-02 by card chat-D1 (user 2026-10-02: \"문서 정리안 전체\" / \"이렇게 하고 한번 "
          "테스트해보자\"). Every line above this footer is unchanged and keeps its line number, so every `file:line` "
          "citation in logs, cards and reviews still resolves. Only the frontmatter `status:` value changed (to "
          "`frozen`).")
FILES = {
    "docs/d1-loop12-17-split-plan.md": [
        "Why: 3,000 lines that every judgement agent re-read each cycle; the items still in force (PD238 and later, "
        "plus the older items they cite) are one line each in `docs/d1/INDEX.md`.",
        "Do NOT append new Pre-decided items here. New decisions go to the per-topic files under `docs/d1/` that the "
        "index lists; numbering continues at 268.",
    ],
    "docs/cycle27-plan.md": [
        "Why: 3,800 lines; the cycle plans since cycle ~69 were written in `docs/d1-loop12-17-split-plan.md`. The "
        "items of this file still cited as in force are listed in `docs/d1/INDEX.md` (section \"In force from other "
        "frozen documents\").",
        "Do NOT append here. The current plan is `docs/d1/INDEX.md`.",
    ],
    "docs/violation-decisions.md": [
        "Why: 1,800 lines. The decision blocks still cited as in force are listed in `docs/d1/INDEX.md`.",
        "APPEND-ONLY CONTINUES BELOW THIS FOOTER: `tools/violations.py`, `tools/retro_due.py`, the retrospective "
        "dispatcher (`DECISIONS` path) and `tools/doc_lint.py` L8 read THIS file, so a new `## <slug> - YYYY-MM-DD "
        "HH:MM` decision block is still appended at the END of this file (never above, never edited) until those "
        "readers are pointed at a new location. Appending keeps every cited line number.",
    ],
    "docs/d1-build-plan.md": [
        "Why: 1,300 lines; its §9 pool queues were superseded by `docs/ring-buffer-design.md` (PD238(a)); the facts "
        "still cited are reached through `docs/d1/INDEX.md`.",
        "Do NOT append here.",
    ],
    "docs/d1-route-b-plan.md": [
        "Why: 720 lines, `status: paused` since 2026-09-18 (route B was replaced by the staged loop split). Index: "
        "`docs/d1/INDEX.md`.",
        "Do NOT append here.",
    ],
}


def md5(b):
    return hashlib.md5(b).hexdigest()


def strip_eol(line):
    return line.rstrip(b"\r\n")


def status_line_index(lines):
    """0-based index of the `status:` line INSIDE the leading frontmatter block, or None."""
    if not lines or strip_eol(lines[0]).lstrip(b"\xef\xbb\xbf") != b"---":
        return None
    for i in range(1, min(len(lines), 80)):
        s = strip_eol(lines[i])
        if s == b"---":
            return None
        if s.startswith(b"status:"):
            return i
    return None


def freeze(rel, extra):
    p = os.path.join(ROOT, rel)
    old = open(p, "rb").read()
    olines = old.splitlines(keepends=True)
    si = status_line_index(olines)
    if si is None:
        return {"file": rel, "ok": False, "why": "no frontmatter status line"}
    eol = b"\r\n" if olines[0].endswith(b"\r\n") else b"\n"
    already = MARK.encode() in old and strip_eol(olines[si]) == b"status: frozen"
    if already:
        return {"file": rel, "ok": True, "already": True, "md5": md5(old), "lines": len(olines)}
    new_lines = list(olines)
    new_lines[si] = b"status: frozen" + eol
    if not new_lines[-1].endswith((b"\n", b"\r")):
        new_lines[-1] = new_lines[-1] + eol
    footer = ["", "---", MARK, "## FROZEN 2026-10-02 (card chat-D1) - index: `%s`" % INDEX, "", COMMON, ""]
    for e in extra:
        footer += [e, ""]
    footer_b = [(f.encode("utf-8") + eol) for f in footer]
    new = b"".join(new_lines + footer_b)
    with open(p, "wb") as fh:
        fh.write(new)
    # ---- proof: re-read from disk
    back = open(p, "rb").read().splitlines(keepends=True)
    diff = []
    for k in range(len(olines)):
        if k == si:
            if strip_eol(back[k]) != b"status: frozen":
                diff.append(k + 1)
            continue
        if strip_eol(back[k]) != strip_eol(olines[k]):
            diff.append(k + 1)
    old_status = strip_eol(olines[si]).decode("utf-8", "replace")
    return {"file": rel, "ok": not diff and len(back) == len(olines) + len(footer_b),
            "old_md5": md5(old), "new_md5": md5(open(p, "rb").read()), "old_lines": len(olines),
            "new_lines": len(back), "status_line": si + 1, "old_status": old_status, "changed_old_lines": diff,
            "footer_lines": len(footer_b)}


def main():
    recs, n_pass, n_fail, first = [], 0, 0, None
    for rel, extra in FILES.items():
        r = freeze(rel, extra)
        recs.append(r)
        line = "FREEZE %s | %s" % ("PASS" if r["ok"] else "FAIL", json.dumps(r, ensure_ascii=False))
        print(line, flush=True)
        if r["ok"]:
            n_pass += 1
        else:
            n_fail += 1
            first = first or ("freeze " + rel)
    out = os.path.join(HERE, "freeze_docs_d1.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(recs, fh, ensure_ascii=False, indent=1)
    arts = [{"path": "tools/bench/freeze_docs_d1.json", "md5": md5(open(out, "rb").read())}]
    print(protocol.result_line(protocol.make_result(n_pass, n_fail, first, arts)), flush=True)
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
