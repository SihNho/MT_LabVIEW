r"""selftest_c121_3_gatefp - card 121-3: the gate-fp queue fp-1..fp-6 drained in one batch. OFFLINE, no LabVIEW, no COM:
every case is a string or a TEMP file handed to the gates' own functions; nothing live (logs, stores, markers) is read.
FOUND FIRST: selftest_chat_p1.py (gate_fp log/drain/due), selftest_launch_gate.py, selftest_c111c_launchunit.py (the
pinned pre-fix baseline pattern). Pre-fix baseline = commit 0a42260 (HEAD when this card started), pinned, not `HEAD`.
PREDICTION:
  F1  fp-1/fp-6 stage_prerun.last_failed_run_after (RE-PINNED by card 121-5, PD238(k)): a FAIL segment whose START runs
      tools/stage_prerun.py (--prerun/--dry) is not a stage run -> None now, a hit on 0a42260; the real fp-1/fp-6 START
      lines are prerun segments; N1 a FAILED stage run after t_min counts; N1b the 121-3 time filter is reverted (a stage
      FAIL that ended before t_min in a log modified after it counts, as on 0a42260); N2 no END line counts; N3 chained
      / env-prefixed / non-command-position mentions of stage_prerun.py still count; N4 segment_ended_by is gone
  F5  fp-5 stage_prerun.plan_files: one plan named by two spellings -> 1 plan now, 2 on 0a42260
  F4  fp-4 guard_bash.MATERIAL_RE: `md5sum tools/stagexec.py tools/bench/x.py` no match now (match on the old regex);
      six real launch shapes still match
  F2  fp-2 NO gate change: `import gscript` still flags labview; the accepted importlib form (selftest_op_hygiene.py:36)
      passes a labview 'none' card, a temp `import gscript` script is refused by it
  F3  fp-3 NO gate change: a temp script importing stagekit and calling a mutating verb is still VI-modifying; the accepted
      op-build form (diag_c117a_opv1.py:15, direct gscript import) is not
    py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_c121_3_gatefp.log -- py -u tools/bench/selftest_c121_3_gatefp.py"""
import ast, json, os, re, subprocess, sys, tempfile, time   # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE); ROOT = os.path.dirname(TOOLS)   # noqa: E702
sys.path[:0] = [TOOLS, os.path.join(TOOLS, "hooks")]
import protocol as P, stage_prerun as SP, guard_bash as GB   # noqa: E401,E402
BASE = "0a42260"
G = []


def gate(lab, ok, det=""):
    G.append((lab, bool(ok))); print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", lab, str(det)[:300]), flush=True)   # noqa: E702


def old_fn(rel, name, extra):
    src = subprocess.run(["git", "show", BASE + ":" + rel], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout
    fn = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == name)
    ns = dict(extra); exec(compile(ast.Module(body=[fn], type_ignores=[]), BASE + ":" + name, "exec"), ns)   # noqa: E702
    return ns[name]


TMP = tempfile.mkdtemp(prefix="c121_3_fp_")
# ------------------------------------------------------------------ F1 fp-1 / fp-6
S = "tools/recipes/stage_zz_fp.py"
T0 = time.mktime(time.strptime("2026-09-28 07:54:30", "%Y-%m-%d %H:%M:%S"))
iso = lambda t: time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))      # noqa: E731
FAILR = 'RESULT {"schema":"result-line/1","status":"FAIL","gates":{"pass":1,"fail":1},"first_fail":"X5","artefacts":[]}'
PASSR = 'RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":2,"fail":0},"first_fail":null,"artefacts":[]}'
seg = lambda t, body, end: "BGRUN START {0} limit 4.0 min: py -u tools/stage_prerun.py --prerun {1}\n{2}\n{3}".format(iso(t), S, body, end)   # noqa: E731
T_OK = T0 + 360                                                                                 # the PASS records' time


def logdir(name, text):
    d = os.path.join(TMP, name); os.makedirs(d); p = os.path.join(d, "x_prerun.log")   # noqa: E702
    open(p, "w", encoding="utf-8").write(text); os.utime(p, (T_OK + 1, T_OK + 1))       # noqa: E702
    return d


# card 121-5 (PD238(k)): RE-PINNED. The 121-3 time filter is reverted; the fix is now "a segment whose START runs
# tools/stage_prerun.py is not a stage run" (stage_prerun.is_prerun_segment). Stage-run segments keep 0a42260's time rule.
run = lambda t, cmd, body, end: "BGRUN START {0} limit 4.0 min: {1}\n{2}\n{3}".format(iso(t), cmd, body, end)   # noqa: E731
STAGE_CMD = "py -u " + S
A = logdir("a", seg(T0, FAILR, "BGRUN END rc=1 after 27s\n") + seg(T0 + 330, PASSR, "BGRUN END rc=0 after 28s\n"))
SP.LOG_DIR = A
gate("F1 fp-1/6 a FAIL --prerun segment is not a stage run", SP.last_failed_run_after(S, T_OK) is None, SP.last_failed_run_after(S, T_OK))
old_lf = old_fn("tools/stage_prerun.py", "last_failed_run_after", {"os": os, "LOG_DIR": A})
gate("F1b discriminates: 0a42260 counted it", old_lf(S, T_OK) is not None, old_lf(S, T_OK))
SP.LOG_DIR = logdir("a2", run(T_OK + 5, "py -u tools/stage_prerun.py --dry " + S, FAILR, "BGRUN END rc=1 after 3s\n"))
gate("F1c a FAIL --dry segment AFTER the records is not a stage run either", SP.last_failed_run_after(S, T_OK) is None)
for lab, line in (("fp-1", "BGRUN START 2026-09-28 07:54:30 limit 4.0 min: py -u tools/stage_prerun.py --prerun tools/recipes/stage_d1_l2r2.py"),
                  ("fp-6", "BGRUN START 2026-09-28 15:13:13 limit 5.0 min: py -u tools/stage_prerun.py --prerun tools/bench/diag_c120_fs.py")):
    gate("F1d the real %s START line is a prerun segment" % lab, SP.is_prerun_segment(line))
SP.LOG_DIR = logdir("b", run(T_OK + 5, STAGE_CMD, FAILR, "BGRUN END rc=1 after 3s\n"))
gate("N1 a FAILED stage run after the records still counts", SP.last_failed_run_after(S, T_OK) is not None)
SP.LOG_DIR = logdir("b2", run(T0, STAGE_CMD, FAILR, "BGRUN END rc=1 after 3s\n") + seg(T0 + 330, PASSR, "BGRUN END rc=0 after 28s\n"))
gate("N1b time filter REVERTED: a stage FAIL that ended before the records, in a log modified after them, counts",
     SP.last_failed_run_after(S, T_OK) is not None)
SP.LOG_DIR = logdir("c", run(T0 + 300, STAGE_CMD, FAILR, ""))
gate("N2 stage FAIL with no END line still counts", SP.last_failed_run_after(S, T_OK) is not None)
for i, cmd in enumerate(("py -u tools/stage_prerun.py --prerun {0} && py -u {0}", "py -u tools/stage_prerun.py --prerun {0}; py -u {0}",
                         "py -u tools/stage_prerun.py --dry {0} | py -u {0}", "X=1 py -u {0} tools/stage_prerun.py",
                         "py -u {0} --after tools/stage_prerun.py")):
    SP.LOG_DIR = logdir("n3_%d" % i, run(T_OK + 5, cmd.format(S), FAILR, "BGRUN END rc=1 after 3s\n"))
    gate("N3 not a plain prerun, still counts: " + cmd.format("S"), SP.last_failed_run_after(S, T_OK) is not None)
gate("N4 time filter code removed (no segment_ended_by)", not hasattr(SP, "segment_ended_by"))
# ------------------------------------------------------------------ F5 fp-5
PD = os.path.join(TMP, "p5"); os.makedirs(PD); PLAN = os.path.join(PD, "plan_fp5.json")   # noqa: E702
json.dump({"decisions": [{"id": "r1", "action": "wire"}]}, open(PLAN, "w", encoding="utf-8"))
REC = os.path.join(PD, "rec_fp5.py")
open(REC, "w", encoding="utf-8").write("A = 'plan_fp5.json'\nB = %r\n" % PLAN.replace("\\", "/"))
gate("F5 fp-5 one plan named by two spellings -> 1 plan", len(SP.plan_files(REC)[0]) == 1, SP.plan_files(REC)[0])
old_pf = old_fn("tools/stage_prerun.py", "plan_files", {"os": os, "ast": ast, "json": json, "BENCH": SP.BENCH, "ROOT": SP.ROOT})
gate("F5b discriminates: 0a42260 kept 2", len(old_pf(REC)[0]) == 2, old_pf(REC)[0])
# ------------------------------------------------------------------ F4 fp-4
OLD_MRE = re.compile(r"\bpy(?:thon)?[\w.]*\s+(?:-\S+\s+)*[^\s|;&]*tools[\\/](?:recipes|bench)[\\/][^\s|;&]*\.py", re.I)
MD5 = "md5sum tools/stagexec.py tools/bench/selftest_c120_routes.py"
gate("F4 fp-4 md5sum of a .py then a bench .py is not a launch", not GB.MATERIAL_RE.search(MD5))
gate("F4b discriminates: the old regex matched it", bool(OLD_MRE.search(MD5)))
for c in ("py -u tools/bench/x.py", "python3 tools/recipes/stage_x.py", "C:\\Python\\python.exe tools/bench/x.py",
          "py tools/bgrun.py --material --max-min 5 --log x.log -- py -u tools/bench/x.py", "cd y && py -u tools/bench/x.py",
          "(py tools/recipes/stage_x.py)"):
    gate("F4 still a launch: " + c, bool(GB.MATERIAL_RE.search(c)))
# ------------------------------------------------------------------ F2 fp-2 (no gate change)
CARD = {"schema": "task/1", "id": "fp-selftest", "flags": {"labview": "none", "write": ["tools/**"], "peers": []}}
gate("F2 `import gscript` still flags LabVIEW", bool(P.LV_IMPORT_RE.search("import gscript as g\n")))
OH = os.path.join(HERE, "selftest_op_hygiene.py")
gate("F2b accepted form selftest_op_hygiene.py:36 loads gscript by importlib", "importlib.import_module(\"gscript\")" in open(OH, encoding="utf-8").read().splitlines()[35])
gate("F2c ... and passes a labview 'none' card", P.check_command(CARD, "py -u tools/bench/selftest_op_hygiene.py") is None,
     P.check_command(CARD, "py -u tools/bench/selftest_op_hygiene.py"))
LVS = os.path.join(TMP, "lv_fp2.py"); open(LVS, "w", encoding="utf-8").write("import gscript\n")   # noqa: E702
gate("F2d a script with `import gscript` is refused by the same card", bool(P.check_command(CARD, 'py -u "%s"' % LVS)), P.check_command(CARD, 'py -u "%s"' % LVS))
# ------------------------------------------------------------------ F3 fp-3 (no gate change)
V = sorted(SP.MODIFY_VERBS)[0]
MS = os.path.join(TMP, "opbuild_fp3.py"); open(MS, "w", encoding="utf-8").write("import stagekit as K\nK.Stage('x').%s()\n" % V)   # noqa: E702
gate("F3 stagekit import + mutating verb is still VI-modifying (%s)" % V, SP.is_vi_modifying(MS))
gate("F3b accepted op-build form diag_c117a_opv1.py (gscript direct) is not", not SP.is_vi_modifying(os.path.join(HERE, "diag_c117a_opv1.py")))
npass = sum(1 for _l, ok in G if ok); nfail = len(G) - npass
print("=== GATES: {0} pass / {1} fail".format(npass, nfail), flush=True)
print(P.result_line(P.make_result(npass, nfail, next((lab for lab, ok in G if not ok), None), status="PASS" if not nfail else "FAIL")), flush=True)
sys.exit(0 if not nfail else 1)
