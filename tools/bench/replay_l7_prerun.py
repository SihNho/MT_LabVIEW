r"""replay_l7_prerun - card chat-C1: the 6 FAILED loop-1.7 LabVIEW runs of 2026-09-24 replayed through the offline
checks (tools/stage_prerun.py --prerun, no LabVIEW, --no-record), each on the recipe version it most plausibly ran
(git), to show which of them the dry run + pre-run would have caught before LabVIEW, and by which check.

VERSIONS (git log of each recipe vs the run's BGRUN START; checked below by comparing the docstring's first line that
the run PRINTED with the version's): l7_1 run1 f1d52ee (committed 03:10:11, run 03:10:33); l7_1 r2 9068ab0 (03:46,
the next commit after the 03:26 run); l7_1a da795e4 (only version); l7_1b run1 + r2 da795e4 (the only commit before
r3's fix; r1 04:14 has no exact version); l7_r run1 = 740b019 with its one fix REVERTED from the traceback line
(stage_d1_l7_r.log:459: `sorted(nm(e) ...)`, the committed file has `T4(...)` = key=repr). The replay runs with
TODAY's stagekit (PD174 already in it), so a failure that lived in the old stagekit cannot reproduce.
The failure -> "knowable by" mapping is docs/stage-simulator-plan.md "Why" table, not chosen here.
    py tools/bgrun.py --material --max-min 20 --log tools/bench/replay_l7_prerun.log -- py -u tools/bench/replay_l7_prerun.py
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import protocol as P   # noqa: E402

TMP = os.path.join(os.environ.get("TEMP", "."), "replay_l7")
os.makedirs(TMP, exist_ok=True)
LOOP15 = os.path.join(HERE, "graph_s3_loop15_20260924.json")
FIX = ("rem, add = T4(nm(e) for e in E0 - En), T4(nm(e) for e in En - E0)",
       "rem, add = sorted(nm(e) for e in E0 - En), sorted(nm(e) for e in En - E0)")
# log, rev, recipe, failure (log line), plan-table "knowable by", the check that implements it here
RUNS = (("stage_d1_l7_1.log", "f1d52ee", "stage_d1_l7_1.py", "P2a init: Jev undecided on chain rows",
         "chain rule + every row decided", ("X7", "X3")),
        ("stage_d1_l7_1_r2.log", "9068ab0", "stage_d1_l7_1.py", "P2a body: Jev undecided on chain rows",
         "chain rule + every row decided", ("X7", "X3")),
        ("stage_d1_l7_1a.log", "da795e4", "stage_d1_l7_1a.py", "PD3 observed cut set != hand prediction",
         "cut set computed from the graph (simulator, build order 4 - NOT in this card)", ()),
        ("stage_d1_l7_1b.log", "da795e4", "stage_d1_l7_1b.py", "address 'total data array out' on #23041: 0 matches",
         "rows only from the plan file", ("X2", "X4", "X6")),
        ("stage_d1_l7_1b_r2.log", "da795e4", "stage_d1_l7_1b.py", "uid addressing on an unwired terminal (#3934)",
         "pre-run addressability", ("X4",)),
        ("stage_d1_l7_r.log", "740b019~fixrevert", "stage_d1_l7_r.py", "TypeError '<' str vs int after 11 min",
         "dry run", ("X1",)))
res = []


def gate(label, ok, detail=""):
    res.append(bool(ok))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:300]), flush=True)


def show(rev, f):
    r = subprocess.run(["git", "show", "{0}:tools/recipes/{1}".format(rev.split("~")[0], f)], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    src = r.stdout
    if rev.endswith("~fixrevert"):
        src = src.replace(FIX[0], FIX[1]) if FIX[0] in src else src
    return src


def prerun(path, graph=None):
    out = path + (".approx" if graph else "") + ".json"
    if os.path.exists(out):
        os.remove(out)
    cmd = [sys.executable, "-u", os.path.join(TOOLS, "stage_prerun.py"), "--prerun", path, "--no-record", "--json-out", out]
    if graph:
        cmd += ["--graph", graph]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=240)
    try:
        return json.load(open(out, encoding="utf-8")), r.stdout
    except (OSError, ValueError):
        return None, r.stdout + r.stderr


rows = []
for log, rev, f, failure, knowable, checks in RUNS:
    print("\n---------- {0}  ({1}:{2})".format(log, rev, f), flush=True)
    src = show(rev, f)
    path = os.path.join(TMP, "{0}__{1}".format(log[:-4], f))
    open(path, "w", encoding="utf-8").write(src)
    head = open(os.path.join(HERE, log), encoding="utf-8", errors="replace").read().splitlines()[1:2]
    m = re.search(r'r"""(.*)', src)
    same = bool(head and m and head[0].strip()[:90] == m.group(1).strip()[:90])
    reverted = (not rev.endswith("~fixrevert")) or (FIX[1] in src)
    print("  FACT  version: {0} bytes; the log's printed docstring line 1 == this version's: {1}; fix-revert applied: {2}".format(
        len(src), same, reverted), flush=True)
    tr, out = prerun(path)
    approx = False
    if tr and tr.get("graph") is None:
        tr2, out2 = prerun(path, LOOP15)
        if tr2:
            tr, out, approx = tr2, out2, True
    gate("{0}: the replay produced a pre-run record".format(log), tr is not None, "" if tr else out[-400:])
    if not tr:
        rows.append((log, rev, "-", "-", "-", "not run"))
        continue
    pr = tr["prerun"]
    failed = [g[0].split(" ")[0] for g in pr["gates"] if not g[1]]
    for g in pr["gates"]:
        print("  FACT  {0} {1}  {2}".format("pass" if g[1] else "FAIL", g[0], g[2][:260]), flush=True)
    # SPECIFIC = the check failed FOR THIS RUN'S REASON (its detail names the failure's object), not merely failed:
    # X2/X3/X5/X6 fail on every pre-v1 recipe (no plan file) and X1 on any stub limit, so a bare FAIL is generic.
    WHY = {"X7": r"#?376\b|376,", "X3": r"llm|undecided", "X4": r"total data array out|3934|UNWIRED",
           "X1": r"TypeError", "X2": r"^$", "X6": r"^$"}
    det = dict((g[0].split(" ")[0], g[2]) for g in pr["gates"] if not g[1])
    spec = [c for c in checks if c in det and re.search(WHY.get(c, r"^$"), det[c] + " " + (tr["first_fail"] or "" if c == "X1" else ""))]
    rows.append((log, rev + (" (docstring match)" if same else " (NEAREST version)"),
                 "{0} ({1})".format(tr["status"], (tr["first_fail"] or "")[:90]),
                 ",".join(failed) or "none", ("input graph exact" if not approx else "NO graph for the input md5 {0} -> loop15 graph (approx)".format(tr["input_md5"])),
                 ("CAUGHT by " + ",".join(spec)) if spec else ("NOT caught specifically (" + knowable + ")" +
                                                                (" - generic refusal by " + ",".join(failed) if failed else ""))))
print("\n==================== REPLAY TABLE: 6 failed L7 runs x the offline checks")
print("run | version | dry | pre-run checks failing | graph | caught? by which (failure -> plan's 'knowable by')")
for (log, rev, dryv, failing, graph, verdict), run in zip(rows, RUNS):
    print("{0} | {1} | {2} | {3} | {4} | {5}  [failure: {6}; knowable by: {7}]".format(
        log, rev, dryv, failing, graph, verdict, run[3], run[4]))
n_caught = sum(1 for r in rows if r[5].startswith("CAUGHT"))
n_refused = sum(1 for r in rows if r[3] not in ("none", "-"))
print("=== CAUGHT specifically {0}/6; launch REFUSED (any pre-run check failing) {1}/6".format(n_caught, n_refused))
npass, nfail = sum(res), len(res) - sum(res)
print("=== GATES: {0} pass / {1} fail".format(npass, nfail))
print(P.result_line(P.make_result(npass, nfail, None if nfail == 0 else "a replay did not produce a record")))
sys.exit(0 if nfail == 0 else 1)
