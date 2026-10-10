# ---
# labview: none
# hardware: none
# offline-args: selftest list write
# evidence: tools/bench/cards/task_chat-X1.json
# ---
"""rules_coverage.py - prove that no rule of the old CLAUDE.md was dropped when it was split into docs/rules/.

Card chat-X1 (user 2026-10-10, discussion token-efficiency-01): the 88k-char CLAUDE.md was frozen byte-for-byte at
`docs/rules/CLAUDE-full-2026-10-10.md` (footer appended only, so every old `CLAUDE.md:N` citation still means line N
there) and restated briefly in topic files `docs/rules/<topic>.md`. Every topic-file entry cites the frozen line
range it restates (`CLAUDE-full-2026-10-10.md:<a>-<b>`). This checker extracts every HEADING and every BOLD span
(`**...**`, the old file's way of marking a rule sentence) of the frozen copy and maps each one to the topic-file line
whose cited range contains it (the narrowest range wins). An item no range contains is UNMAPPED -> FAIL.
`docs/rules/coverage.md` is the generated table (item -> new home file:line); a coverage.md that differs from what
this script would write is STALE -> FAIL, so the table cannot drift from the topic files.

  py tools/rules_coverage.py            # check: 0 unmapped and coverage.md current, else rc 1
  py tools/rules_coverage.py write      # regenerate docs/rules/coverage.md, then check
  py tools/rules_coverage.py list       # print the items (line, kind, text) - for writing topic files
  py tools/rules_coverage.py selftest   # extraction / mapping on an in-memory sample

Existing tools checked first: tools/doc_lint.py checks that citations EXIST, not that a source is fully covered;
tools/bench/freeze_docs_d1.py freezes long plans in place (same footer convention, no coverage check).
"""
import glob
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RULES = os.path.join(ROOT, "docs", "rules")
FROZEN_NAME = "CLAUDE-full-2026-10-10.md"
FROZEN = os.path.join(RULES, FROZEN_NAME)
COVERAGE = os.path.join(RULES, "coverage.md")
FOOTER_RE = re.compile(r"^## FROZEN \d{4}-\d{2}-\d{2}", re.M)
HEAD_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
BOLD_RE = re.compile(r"\*\*(?=\S)(.+?)(?<=\S)\*\*", re.S)
CITE_RE = re.compile(re.escape(FROZEN_NAME) + r":(\d+)(?:-(\d+))?")


def frozen_body(text):
    """The text above the FROZEN footer (the footer is not rule text)."""
    m = FOOTER_RE.search(text)
    return text[:m.start()] if m else text


def items(text):
    """[(line, kind, text)] - every heading and every bold span of `text` (a bold span may wrap lines, never a
    blank line; fenced code blocks are skipped)."""
    body = frozen_body(text)
    out = []
    lines = body.split("\n")
    in_code = False
    code_lines = set()
    for i, ln in enumerate(lines, 1):
        if ln.strip().startswith("```"):
            in_code = not in_code
            code_lines.add(i)
            continue
        if in_code:
            code_lines.add(i)
            continue
        m = HEAD_RE.match(ln)
        if m:
            out.append((i, "heading", m.group(2)))
    starts = [0]
    for ln in lines:
        starts.append(starts[-1] + len(ln) + 1)

    def lineno(off):
        lo, hi = 0, len(starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if starts[mid] <= off:
                lo = mid
            else:
                hi = mid - 1
        return lo + 1

    for m in BOLD_RE.finditer(body):
        span = m.group(1)
        if "\n\n" in span or len(span) > 1200:
            continue
        n = lineno(m.start())
        if n in code_lines or HEAD_RE.match(lines[n - 1]):
            continue
        out.append((n, "bold", " ".join(span.split())))
    return sorted(out)


def topic_files():
    return sorted(p for p in glob.glob(os.path.join(RULES, "*.md"))
                  if os.path.basename(p) not in (FROZEN_NAME, "coverage.md"))


def rule_docs():
    """The rule topic files as project-relative paths (`docs/rules/<topic>.md`), sorted - what a tool attaches or
    names when it needs "the rules" (it used to name CLAUDE.md, now the short core). Self-test: `selftest` below."""
    return [os.path.relpath(p, ROOT).replace(os.sep, "/") for p in topic_files()]


def ranges(paths):
    """[(a, b, relpath, line)] - every cited frozen range in the topic files."""
    out = []
    for p in paths:
        rp = os.path.relpath(p, ROOT).replace(os.sep, "/")
        with open(p, encoding="utf-8") as f:
            for i, ln in enumerate(f, 1):
                for m in CITE_RE.finditer(ln):
                    a = int(m.group(1))
                    b = int(m.group(2) or a)
                    out.append((a, b, rp, i))
    return out


def mapping(its, rngs):
    """[(item, home or None)] - home = 'path:line' of the narrowest cited range containing the item's line."""
    res = []
    for it in its:
        best = None
        for a, b, rp, i in rngs:
            if a <= it[0] <= b and (best is None or (b - a) < (best[1] - best[0])):
                best = (a, b, rp, i)
        res.append((it, None if best is None else "%s:%d" % (best[2], best[3])))
    return res


def cell(s, n=110):
    s = s.replace("|", "/").replace("`", "'")
    return s if len(s) <= n else s[:n - 1] + "…"


def coverage_md(mapped, frozen_md5):
    out = ["---", "type: index", "status: reference", "date: 2026-10-10", "tags: [rules, coverage]", "---", "",
           "# Rules coverage - every heading and bold rule of the old CLAUDE.md, and where it lives now", "",
           "GENERATED by `py tools/rules_coverage.py write` (card chat-X1) - do not edit by hand. Source: the frozen",
           "copy `docs/rules/%s` (md5 %s). A row's *new home* is the topic-file line whose" % (FROZEN_NAME, frozen_md5),
           "cited range contains the item; the frozen line keeps the full wording and the quote.", "",
           "| frozen line | kind | item | new home |", "|---|---|---|---|"]
    for (n, kind, text), home in mapped:
        out.append("| %d | %s | %s | %s |" % (n, kind, cell(text), home or "**UNMAPPED**"))
    out.append("")
    return "\n".join(out)


def check(write=False):
    with open(FROZEN, encoding="utf-8") as f:
        text = f.read()
    md5 = hashlib.md5(open(FROZEN, "rb").read()).hexdigest()
    its = items(text)
    tf = topic_files()
    mapped = mapping(its, ranges(tf))
    unmapped = [it for it, h in mapped if h is None]
    want = coverage_md(mapped, md5)
    if write:
        with open(COVERAGE, "w", encoding="utf-8", newline="\n") as f:
            f.write(want)
    have = open(COVERAGE, encoding="utf-8").read() if os.path.isfile(COVERAGE) else ""
    stale = have != want
    print("RULES-COVERAGE: %d items (%d headings, %d bold) in %s; %d topic files; %d unmapped; coverage.md %s"
          % (len(its), sum(1 for i in its if i[1] == "heading"), sum(1 for i in its if i[1] == "bold"), FROZEN_NAME,
             len(tf), len(unmapped), "STALE" if stale else "current"))
    for n, kind, t in unmapped[:40]:
        print("  UNMAPPED %s:%d %s %s" % (FROZEN_NAME, n, kind, cell(t, 90)))
    return len(its), unmapped, stale


def selftest():
    sample = ("# Top\n\nsome **Rule one.** text\n```\n**not a rule**\n```\n## Sub\n**wraps\nlines** end\n"
              "## FROZEN 2026-10-10\n**footer bold**\n")
    its = items(sample)
    ok = []
    ok.append(("headings + bold found, code and footer skipped",
               its == [(1, "heading", "Top"), (3, "bold", "Rule one."), (7, "heading", "Sub"),
                       (8, "bold", "wraps lines")]))
    m = mapping(its, [(1, 3, "docs/rules/a.md", 5), (3, 3, "docs/rules/b.md", 9)])
    ok.append(("narrowest range wins", m[1][1] == "docs/rules/b.md:9" and m[0][1] == "docs/rules/a.md:5"))
    ok.append(("uncovered -> None", m[3][1] is None))
    ok.append(("citation regex", [x.groups() for x in CITE_RE.finditer("x `docs/rules/%s:12-30` y %s:7"
                                                                      % (FROZEN_NAME, FROZEN_NAME))]
               == [("12", "30"), ("7", None)]))
    rd = rule_docs()
    ok.append(("rule_docs: relative docs/rules/*.md, frozen copy and coverage excluded",
               all(p.startswith("docs/rules/") and p.endswith(".md") for p in rd)
               and not any(p.endswith((FROZEN_NAME, "coverage.md")) for p in rd)))
    for label, good in ok:
        print("  %s  %s" % ("PASS" if good else "FAIL", label))
    return sum(1 for _, g in ok if g), sum(1 for _, g in ok if not g)


def main():
    sys.path.insert(0, HERE)
    import protocol
    arg = sys.argv[1] if len(sys.argv) > 1 else "check"
    if arg == "selftest":
        p, f = selftest()
        print(protocol.result_line({"status": "PASS" if not f else "FAIL", "gates": {"pass": p, "fail": f},
                                    "first_fail": None if not f else "selftest", "artefacts": []}))
        return 1 if f else 0
    if arg == "list":
        for n, kind, t in items(open(FROZEN, encoding="utf-8").read()):
            print("%4d %-7s %s" % (n, kind, cell(t, 150)))
        return 0
    n, unmapped, stale = check(write=(arg == "write"))
    fails = len(unmapped) + (1 if stale else 0)
    first = None
    if unmapped:
        first = "UNMAPPED %s:%d" % (FROZEN_NAME, unmapped[0][0])
    elif stale:
        first = "coverage.md STALE - run py tools/rules_coverage.py write"
    art = [{"path": "docs/rules/coverage.md", "md5": hashlib.md5(open(COVERAGE, "rb").read()).hexdigest()}] \
        if os.path.isfile(COVERAGE) else []
    print(protocol.result_line({"status": "PASS" if not fails else "FAIL",
                                "gates": {"pass": n - len(unmapped), "fail": fails},
                                "first_fail": first, "artefacts": art}))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
