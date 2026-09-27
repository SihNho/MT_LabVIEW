r"""diag_c115c_headcmp_disc - card 115-3: the discriminating tests of archive/peer/2026-09-28-c115c-headcmp.md s4 for the
H1 failure in tools/bench/selftest_stage_prerun_headcmp_79-6_c115c_after.log (HEAD copy FAILS [L3, L4b]). OFFLINE, no
LabVIEW, no guard_bash.py.new staged (checked: aborts if one exists).
  D1 %TEMP%\lg_selftest_22500: creation / mtime of the dir and its stage_runs.jsonl (peer: stale dir reused at 05:33).
     Count of %TEMP%\lg_selftest_*\stage_runs.jsonl with >= 2 lines (stale RETRY-CAP seeds).
  D2 a COPY of tools/bench/selftest_launch_gate.py with SAND fixed to %TEMP%\c115c_lg_seeded (fresh), stage_runs.jsonl
     PRE-SEEDED with the two lines of lg_selftest_22500, run against the WORKING-TREE stage_prerun.py.
     Prediction (peer): FAILS == [L3, L4b], each FAIL line's why starts 'RETRY CAP'.
  D3 control: the same copy, SAND fixed to a fresh empty dir %TEMP%\c115c_lg_clean -> 28/0, FAILS [].
The copy lives at tools/bench/diag_c115c_lgcopy_tmp.py only during the run (HERE/TOOLS must resolve to the project).
"""
import glob, os, re, shutil, subprocess, sys, time                                 # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE); ROOT = os.path.dirname(TOOLS)  # noqa: E702
sys.path.insert(0, TOOLS)
import protocol  # noqa: E402
TEMP = os.environ["TEMP"]
G = []


def gate(l, ok, d=""):
    G.append((l, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", l, str(d)[:700]), flush=True)


assert not os.path.exists(os.path.join(TOOLS, "hooks", "guard_bash.py.new")), "a guard_bash.py.new is staged - abort"
st = os.path.join(TEMP, "lg_selftest_22500")
sj = os.path.join(st, "stage_runs.jsonl")
fmt = lambda t: time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))  # noqa: E731
seed = open(sj, encoding="utf-8").read() if os.path.exists(sj) else ""
d1 = {"dir_ctime": fmt(os.path.getctime(st)) if os.path.exists(st) else None,
      "runs_ctime": fmt(os.path.getctime(sj)) if os.path.exists(sj) else None,
      "runs_mtime": fmt(os.path.getmtime(sj)) if os.path.exists(sj) else None, "runs_lines": len(seed.splitlines())}
stale = [p for p in glob.glob(os.path.join(TEMP, "lg_selftest_*", "stage_runs.jsonl"))
         if len(open(p, encoding="utf-8", errors="replace").read().splitlines()) >= 2]
print("FACT D1 lg_selftest_22500 {0}; stale seeds (>=2 lines) {1}".format(d1, len(stale)), flush=True)
gate("D1 lg_selftest_22500 existed before the after-run (created < 05:28) and holds 2 counted lines",
     d1["dir_ctime"] and d1["dir_ctime"] < "2026-09-28 05:28:00" and d1["runs_lines"] == 2, d1)
src = open(os.path.join(HERE, "selftest_launch_gate.py"), encoding="utf-8").read()
line = 'SAND = os.path.join(os.environ.get("TEMP", "."), "lg_selftest_{0}".format(os.getpid()))'
assert src.count(line) == 1
CP = os.path.join(HERE, "diag_c115c_lgcopy_tmp.py")


def run(tag, seeded):
    sand = os.path.join(TEMP, "c115c_lg_" + tag)
    shutil.rmtree(sand, ignore_errors=True)
    os.makedirs(sand)
    if seeded:
        open(os.path.join(sand, "stage_runs.jsonl"), "w", encoding="utf-8").write(seed)
    open(CP, "w", encoding="utf-8").write(src.replace(line, "SAND = {0!r}".format(sand)))
    try:
        p = subprocess.run([sys.executable, "-u", CP], cwd=ROOT, capture_output=True, text=True, timeout=200)
    finally:
        os.remove(CP)
        shutil.rmtree(sand, ignore_errors=True)
    fl = [ln.strip() for ln in p.stdout.splitlines() if re.match(r"^\s+FAIL\s+[A-Z]\d+b?\b", ln)]
    ids = sorted(set(re.match(r"FAIL\s+([A-Z]\d+b?)", x).group(1) for x in fl))
    summ = [ln for ln in p.stdout.splitlines() if ln.startswith("=== GATES")]
    print("RUN {0}: rc {1} {2} FAILS {3}".format(tag, p.returncode, summ, ids), flush=True)
    for x in fl:
        print("    " + x[:400], flush=True)
    return ids, fl


ids2, fl2 = run("seeded", True)
gate("D2 seeded sandbox, WORKING-TREE stage_prerun: FAILS == [L3, L4b], each why 'RETRY CAP'",
     ids2 == ["L3", "L4b"] and all("RETRY CAP" in x for x in fl2), (ids2, [x[:160] for x in fl2]))
ids3, fl3 = run("clean", False)
gate("D3 fresh empty sandbox, same copy: FAILS []", ids3 == [], ids3)
n = sum(1 for _l, ok in G if ok)
first = next((l for l, ok in G if not ok), None)
print("=== GATES: {0} pass / {1} fail".format(n, len(G) - n))
print(protocol.result_line(protocol.make_result(n, len(G) - n, first)))
sys.exit(0 if first is None else 1)
