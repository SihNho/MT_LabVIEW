r"""make_tasks - write ucbench tasks.json (L1/L2/L3) from the fixed answer sources (card chat-B3).

    py tools/bgrun.py --material --max-min 5 --log tools/bench/ucbench/make_tasks.log -- py -u tools/bench/ucbench/make_tasks.py

Sources (all at base 1d4caf8 = 9635538^, the commit before the full Opus ingest's fixes landed):
  L1  archive/ingest/2026-09-25-full-20260925-protocol-simulator.md (added in 9635538): 9 pairs, all 9 confirmed and
      fixed in the same commit ("What was done with it"); line numbers re-checked at base in this card.
  L2  keys/l2_missing_citations.txt: the base's own doc_lint citation rule (active_docs + citation_candidates), every
      cited project path missing at base (23; doc_lint prints 3 FAIL + the first 6 of 20 plan WARNs).
  L3  keys/violations_base.txt: the base's own violations.py table (10 slugs, each named in >= 2 retrospectives);
      since card chat-B4 one key item per (slug, retrospective file) pair = 110, per-slug counts kept for count accuracy.
PREDICTION: 3 tasks, key sizes 9 / 23 / 110, every key item's regexes hit its own ref (checked again by --lock).
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "1d4caf891ce60ecf981f198449d93fc23be286e2"


def side(f, line, span=2):
    nums = "|".join(str(n) for n in range(max(1, line - span), line + span + 1))
    return r"%s[^0-9\n]{0,12}(?:%s)\b" % (re.escape(f), nums)


PREAMBLE = ("You are auditing the repository checked out in the current directory. It is READ-ONLY for you: use Read, "
            "Grep, Glob and read-only shell commands; do not use git (it is blocked); do not modify files. Work until "
            "you are confident the answer is COMPLETE - completeness is scored (recall) as well as correctness "
            "(precision). Do not include anything you have not checked in the files.")
FORMAT = ("ANSWER FORMAT (mandatory - only these lines are scored): one line per finding, each starting with "
          "`CLAIM <n>:` (n = 1, 2, 3, ...), stating the finding, followed by ` | EVIDENCE: ` and the file:line "
          "citation(s). After the last claim, one line `CLAIMS: <count>`. Nothing after it.")

L1_PAIRS = [
    ("K1", ("STATUS.md", 47), [("STATUS.md", 58)],
     "STATUS.md:47 says motor limits were LEFT ON since 2026-09-18 (PI TMN 0/TMX 39); STATUS.md:58 says limits were "
     "RELEASED and read back on 2026-09-23 (PI 0..52, ASI +-500)"),
    ("K2", ("STATUS.md", 57), [("STATUS.md", 58)],
     "STATUS.md:57 says limits LEFT ON (PI TMN 0/TMX 39 in RAM, ASI SL/SU persistent); STATUS.md:58 records them "
     "released with readback"),
    ("K3", ("STATUS.md", 109), [("STATUS.md", 58)],
     "STATUS.md:109 'No motor, no camera, no ASI' vs STATUS.md:58 user grant: motors (PI, rotor, ASI) may be driven "
     "by the gate and by a running main VI while assembled"),
    ("K4", ("STATUS.md", 100), [("m8-real-run-plan.md", 14), ("STATUS.md", 58)],
     "STATUS.md:100 a functional run of D1_s3_loop15.vi drives motors directly so in assembled state it is not "
     "permitted vs docs/m8-real-run-plan.md:14 (and STATUS.md:58) motors granted until withdrawn, real run allowed"),
    ("K5", ("STATUS.md", 72), [("STATUS.md", 77)],
     "STATUS.md:72 FIRST ACT when the runner resumes = M8 real run vs STATUS.md:77 FIRST ACT (cycle 74) = tool fix "
     "computation_diff blind spot"),
    ("K6", ("STATUS.md", 107), [("STATUS.md", 75), ("violation-decisions.md", 1103)],
     "STATUS.md:107 treats the 2026-09-18 no-new-device order as still in force vs STATUS.md:75 (and "
     "docs/violation-decisions.md:1103) tool building allowed again / order lifted 2026-09-24"),
    ("K7", ("CLAUDE.md", 258), [("CLAUDE.md", 603)],
     "CLAUDE.md:258 hypothesis reviews max->high, priorart medium (table re-set 2026-09-23) vs CLAUDE.md:603 role "
     "table priorart opus/high, hypothesis opus/max"),
    ("K8", ("cycle27-plan.md", 54), [("STATUS.md", 102)],
     "docs/cycle27-plan.md:54 failed prediction -> single hypothesis arm at opus effort max vs STATUS.md:102 models: "
     "hypothesis high"),
    ("K9", ("STATUS.md", 16), [("d1-route-b-plan.md", 4)],
     "STATUS.md:16 says the D1 route-B plan docs/d1-route-b-plan.md is paused vs docs/d1-route-b-plan.md:4 "
     "frontmatter status: current"),
]


def l1():
    key = []
    for kid, a, bs, text in L1_PAIRS:
        ref = "%s:%d vs %s | EVIDENCE: %s:%d; %s:%d" % (a[0], a[1], bs[0][0], a[0], a[1], bs[0][0], bs[0][1])
        sp = 0 if kid in ("K1", "K2") else 1         # 47/57 vs 58: a +-1 window would let 57 and 58 alias
        key.append({"id": kid, "text": text, "ref": ref,
                    "re": [[side(a[0], a[1], sp)], [side(f, ln, sp) for f, ln in bs]]})
    return {"id": "L1", "base": BASE, "copy": [], "size": "71 docs/*.md + CLAUDE.md + STATUS.md",
            "remove": ["archive/ingest/*", "tools/bench/ingest_*.log", "tools/bench/cards/review_*ingest*.json",
                       "tools/bench/cards/verdict_*ingest*.json", "tools/doc_ingest.py"],
            "leak": [r"full-20260925-protocol-simulator", r"CONTRADICTIONS:\s*9\b"],
            "question": (
                "TASK L1 - WHOLE-DOCUMENT CONTRADICTION AUDIT. The active documents of this project are CLAUDE.md, "
                "STATUS.md and every docs/*.md file (not archive/). Find EVERY pair of statements in these documents "
                "that CONTRADICT each other (two statements that cannot both be true: a value, count, time, state, "
                "rule or plan status stated differently), including a document contradicting itself and a document "
                "contradicting CLAUDE.md or STATUS.md. Not stylistic differences, not a document merely being older, "
                "not a history line that is clearly marked as history/superseded. Cite file:line for BOTH sides of "
                "every pair and quote both statements briefly; one claim per pair; no recommendations."),
            "key": key}


def l2():
    t = open(os.path.join(HERE, "keys", "l2_missing_citations.txt"), encoding="utf-8").read()
    d = json.loads(t[t.index("\n[\n") + 1:])
    key = []
    for i, x in enumerate(d, 1):
        doc = os.path.basename(x["doc"])
        ref = "%s:%d cites %s which does not exist | EVIDENCE: %s:%d" % (x["doc"], x["line"], x["path"], x["doc"],
                                                                        x["line"])
        key.append({"id": "K%d" % i, "text": "%s:%d cites `%s`, which does not exist in the repository" % (
            x["doc"], x["line"], x["path"]), "ref": ref,
                    "re": [[side(doc, x["line"], 1)], [re.escape(x["path"].split("/")[-1])]]})
    return {"id": "L2", "base": BASE, "copy": [], "size": "every backticked/linked path in 73 active docs",
            "blank": ["tools/doc_lint.py", "tools/audit_cycle.py"],   # emptied, NOT removed: docs cite them
            "absent": sorted({x["path"] for x in d}),
            # old doc_lint outputs quoted in retrospectives/logs list some key paths (lock run 1: cycle14/15 retros);
            # redact those LINES only - the files stay, their existence is part of the key; active docs untouched
            "redact": [{"roots": ["archive", "tools"],
                        "re": r"DANGLING of \d+|forward reference\(s\)|[\w./-]+\.md:\d+ -> (?:tools|docs|archive)/"}],
            "leak": [r"DANGLING of \d+ citations", r"forward reference\(s\) in plan documents",
                     r"docs/[\w.-]+\.md:\d+ -> (?:tools|docs|archive)/"],
            "question": (
                "TASK L2 - DANGLING-CITATION CENSUS. In the active documents (CLAUDE.md, STATUS.md and every docs/*.md "
                "file; not archive/), a CITATION is a span in backticks `like/this.py` or a markdown link target "
                "](like/this.md) that (a) starts with one of docs/ tools/ archive/ project-requirements/ .claude/, "
                "(b) contains a '/', (c) ends in one of .md .py .ps1 .json .log .txt .vi .ctl .toml .yaml .yml "
                "(an optional :<line> or :<a>-<b> suffix is stripped first), and (d) contains none of the characters "
                "* < > | ? \" ' { } or a space, and no '...', and is not a URL or an absolute path. List EVERY "
                "citation whose path does NOT exist as a file in this checkout - one claim per occurrence (the same "
                "path cited on two lines is two claims), giving the citing document, the line number of the "
                "citation, and the missing path."),
            "key": key}


def l3():
    """card chat-B4 (chat decision 1): the key is the (slug, retrospective) PAIRS of the base's violations.py table,
    one item per pair (~110), with the per-slug count kept on every item for the separate count-accuracy score."""
    key, counts = [], {}
    for ln in open(os.path.join(HERE, "keys", "violations_base.txt"), encoding="utf-8"):
        m = re.match(r"^([a-z]+(?:-[a-z]+)+)\s+(\d+)\s+\S+\s+(\d{4}-\d\d-\d\d-retro.*)$", ln)   # table rows only
        if not m:
            continue
        slug, n = m.group(1), int(m.group(2))
        files = re.findall(r"(\d{4}-\d\d-\d\d-retrospective-cycle(\d+[\w-]*?))\.md", m.group(3))
        if len(files) != n:
            raise SystemExit("L3 key: %s count %d but %d files parsed" % (slug, n, len(files)))
        counts[slug] = n
        for stem, cyc in files:
            key.append({"id": "K%d" % (len(key) + 1),
                        "text": "`%s` named in archive/peer/%s.md (cycle %s)" % (slug, stem, cyc),
                        "ref": "%s | archive/peer/%s.md | EVIDENCE: archive/peer/%s.md" % (slug, stem, stem),
                        "re": [[re.escape(slug)], [r"cycle[ _-]?%s(?![0-9A-Za-z-])" % re.escape(cyc)]],
                        "slug": slug, "cycle": cyc, "count": n})
    return {"id": "L3", "base": BASE, "copy": [], "size": "58 retrospective archives (cycles 7-73)",
            "counts": counts,
            "blank": ["tools/violations.py", "tools/audit_cycle.py", "tools/retro_due.py",
                      "tools/bench/retro_v2_compare.log",       # lock runs 1-2: older violations tables
                      "tools/bench/reverse_census_walk.json", "tools/bench/reverse_census_walk.log"],
            "leak": [r"slug\s+count\s+loss_min\s+retrospectives", r"reported loss across all slugs"],
            "question": (
                "TASK L3 - CROSS-CYCLE FAILURE-CLASS AUDIT. Every cycle of this project ended with a retrospective "
                "archived as archive/peer/*retrospective*.md; each names the cycle's structural faults as VIOLATION "
                "slugs (two formats: `VIOLATION: <slug>` and `VIOLATION: <slug> | loss_min=... | ...`). Find EVERY "
                "failure class (slug) that was named in TWO OR MORE retrospectives, and EVERY retrospective that named "
                "it. One claim per (slug, retrospective) pair: the slug and the retrospective's file name "
                "(archive/peer/<date>-retrospective-cycle<N...>.md; a cycle with several retrospectives, e.g. "
                "cycle15 and cycle15-routeb, gives one pair per file), with the file:line of the VIOLATION line. "
                "Before the first CLAIM line, write one line `COUNT <slug> = <number of retrospectives that named "
                "it>` for each such slug."),
            "key": key}


doc = {"schema": "ucbench-tasks/1", "preamble": PREAMBLE, "answer_format": FORMAT, "tasks": [l1(), l2(), l3()]}
p = os.path.join(HERE, "tasks.json")
json.dump(doc, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
sizes = [len(t["key"]) for t in doc["tasks"]]
ok = sizes == [9, 23, 110]                       # L3 = (slug, retrospective) pairs since card chat-B4
print("TASKS %s key sizes %s" % ([t["id"] for t in doc["tasks"]], sizes))
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if ok else "FAIL",
                              "gates": {"pass": int(ok), "fail": int(not ok)},
                              "first_fail": None if ok else "key sizes %s" % sizes, "artefacts": [
                                  {"path": "tools/bench/ucbench/tasks.json"}]}))
