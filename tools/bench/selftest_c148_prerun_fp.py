# ---
# labview: none
# hardware: none
# ---
r"""selftest_c148_prerun_fp - card 148-a1-1: the stage_prerun.py fixes for gate-fp fp-52, fp-56, fp-58. No LabVIEW, no COM,
no subprocess; reads two project scripts as bytes/headers and writes only a TEMP stage_runs file (STAGE_RUNS env).

WHAT EXISTED: selftest_retry_cap.py (card 78-2: recorder at child start, cap, --retry-card) and selftest_c103d_hooks.py
(VI_MOD_EXEMPT_PATHS pin, card 103-4); neither covers an offline-args run nor the 0007d034 bytes. This file adds those cases.

PREDICTION CONTRACT
  P1 fp-56: tools/bench/selftest_stagekit.py at its current bytes (md5 29df9b64; stage_prerun.sha256, header-stripped,
     5708c2d6...; raw-file sha256 0007d034...) is NOT vi-modifying (pin matches)
     and a bgrun launch of it names no gated script
  P2 fp-56 negative: the SAME bytes copied to a temp path ARE classified vi-modifying (pin is path+bytes, not a name rule)
  P3 fp-52/58: offline_run_of() True for the s06 scratch recipe with `--el-advisory-selftest` (its header offline-args),
     False for the same recipe with no argument and with an unknown argument
  P4 fp-58: with 2 counted runs of the stage in the temp cycle, check_cap ALLOWS the offline-args run and still REFUSES
     the plain run (cap 2)
  P5 fp-52: record_started() records NOTHING for the offline-args command line (temp file unchanged)
  P6 the real tools/bench/stage_runs.jsonl is byte-unchanged
  P7 fp-51: dry_read_only True for diag_c147_a1_1_graph.py (only discard_work), False for the s06 scratch recipe (edits)
     and for a script importing no stagekit
  P8 fp-51: the dry gate text routes through dry_read_only (source check; the live dry is run separately)
"""
import hashlib
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOLS = os.path.join(ROOT, "tools")
REAL_RUNS = os.path.join(TOOLS, "bench", "stage_runs.jsonl")
TMP = tempfile.mkdtemp(prefix="c148pre_")
RUNS = os.path.join(TMP, "stage_runs.jsonl")
CK = "selftest 148-a1-1"
os.environ["STAGE_RUNS"] = RUNS
os.environ["STAGE_RUNS_CYCLE"] = CK
sys.path.insert(0, TOOLS)
import stage_prerun as SP  # noqa: E402
import protocol as P  # noqa: E402

G = []


def gate(label, ok, detail=""):
    G.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:300]), flush=True)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


real_md5 = md5(REAL_RUNS)
ST = os.path.join(TOOLS, "bench", "selftest_stagekit.py")
SCR_REL = "tools/recipes/stage_d1_ring_p4_s06v18_scratch.py"
SCR = os.path.join(ROOT, SCR_REL)
try:
    calls = SP.vi_modifying_calls(ST)
    lv = SP.launched_vi_modifying("py tools/bgrun.py --material --max-min 2 --log x.log -- py -u tools/bench/selftest_stagekit.py")
    gate("P1 fp-56: selftest_stagekit.py sha256 {0}.. not vi-modifying; launch gates nothing".format(SP.sha256(ST)[:8]),
         calls == [] and lv == [] and SP.sha256(ST).startswith("5708c2d6") and md5(ST).startswith("29df9b64"),
         (calls, lv, md5(ST)[:8]))
    cp = os.path.join(TMP, "selftest_stagekit.py")
    shutil.copyfile(ST, cp)
    gate("P2 fp-56 negative: same bytes at another path ARE classified", bool(SP.vi_modifying_calls(cp)),
         SP.vi_modifying_calls(cp))

    OFF = "py -u {0} --el-advisory-selftest".format(SCR_REL)
    PLAIN = "py -u {0}".format(SCR_REL)
    UNK = "py -u {0} --no-such-flag".format(SCR_REL)
    u = [SP.offline_run_of(c, SCR) for c in (OFF, PLAIN, UNK)]
    gate("P3 offline_run_of [offline-args, plain, unknown arg] == [True, False, False]", u == [True, False, False], u)

    key = SP.stage_key(SCR)
    with open(RUNS, "w", encoding="utf-8") as f:
        for i in range(2):
            f.write(json.dumps({"t": i, "cycle": CK, "stage": key, "by": SP.COUNTED_BY, "card": None}) + "\n")
    runs = SP.read_stage_runs()
    ok_off, _w, _c = SP.check_cap(OFF, SCR, runs, CK)
    ok_pl, why_pl, _c2 = SP.check_cap(PLAIN, SCR, runs, CK)
    gate("P4 fp-58: cap 2 reached - offline-args run ALLOWED, plain run REFUSED", ok_off and not ok_pl,
         (ok_off, ok_pl, why_pl[:90]))

    before = md5(RUNS)
    recs = SP.record_started(OFF, log=None, pid=0)
    gate("P5 fp-52: record_started records nothing for the offline-args run", recs == [] and md5(RUNS) == before,
         (len(recs), md5(RUNS) == before))
    # fp-51: the dry's input-graph gate is not fatal for a script whose only MODIFY verb is discard_work
    ro = [SP.dry_read_only(os.path.join(TOOLS, "bench", "diag_c147_a1_1_graph.py")), SP.dry_read_only(SCR),
          SP.dry_read_only(os.path.join(TOOLS, "bench", "selftest_retry_cap.py"))]
    gate("P7 fp-51: dry_read_only [graph-read diag (discard_work only), s06 scratch recipe, no-stagekit selftest] == "
         "[True, False, False]", ro == [True, False, False], ro)
    src = open(os.path.join(TOOLS, "stage_prerun.py"), encoding="utf-8").read()
    gate("P8 fp-51: the dry's 'DRY graph JSON for input md5' gate passes on G is not None OR dry_read_only (still fatal "
         "otherwise)", "G is not None or ro," in src and "ro = G is None and not getattr(D, \"graph_error\", None) and "
         "dry_read_only(D.recipe)" in src)
finally:
    shutil.rmtree(TMP, ignore_errors=True)
gate("P6 real stage_runs.jsonl byte-unchanged", md5(REAL_RUNS) == real_md5)
n_pass = sum(1 for _l, ok in G if ok)
n_fail = len(G) - n_pass
first = next((lb for lb, ok in G if not ok), None)
print("=== GATES: {0} pass / {1} fail".format(n_pass, n_fail))
print(P.result_line(P.make_result(n_pass, n_fail, first)))
sys.exit(0 if n_fail == 0 else 1)
