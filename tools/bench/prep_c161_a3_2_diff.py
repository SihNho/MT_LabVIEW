# ---
# labview: none
# hardware: none
# offline-args: --diff
# evidence: tools/bench/cards/brief_161-a3-2.md
# ---
r"""prep_c161_a3_2_diff - card 161-a3-2 (OFFLINE, json only): `--snap` copies the p5s02b pred and the SG census file to *_before copies
(prep_c161_a3_2_*_before.json) before the pred maker re-runs; `--diff` lists every leaf path that moved and gates it against the keys that follow
from the checkpoint set alone (PD394(b)): memory_pred R / peaks / MAIN, the SG file's MAIN keys, and the SG file md5 the pred cites.
Also: md5 of plan, stagesim, stagexec, stage_prerun, licence, EL unchanged. No generic json leaf-diff exists in tools/ (grep 'def .*leaves|flatten').
PREDICTION: --diff 2/0; moved keys a subset of ALLOWED; checkpoint lists NOT moved (pred 18729409 already held (0,1,2,3,4,5,7,8,9,10)).
    py tools/bgrun.py --material --max-min 2 --log tools/bench/prep_c161_a3_2_diff.log -- py -u tools/bench/prep_c161_a3_2_diff.py --diff"""
import os, shutil, sys                                                                      # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import prep_c156_a1_1_lib as L                                                              # noqa: E402
B, T = os.path.join(ROOT, "tools", "bench"), os.path.join(ROOT, "tools")
PAIRS = {"pred": (os.path.join(B, "plan_ring_p5s02b_pred.json"), os.path.join(B, "prep_c161_a3_2_pred_before.json")),
         "sg": (os.path.join(B, "prep_c160_c3_1_session.json"), os.path.join(B, "prep_c161_a3_2_sgsession_before.json"))}
ALLOWED = {"pred": {"memory_pred.R", "memory_pred.peak_mb", "memory_pred.main_peak_mb", "memory_pred.peak_at_start_assumed_mb",
                    "memory_pred.main_peak_at_start_assumed_mb", "sg_census_file.md5"},
           "sg": {"main_peak_mb", "main_peak_at_start_assumed_mb"}}
UNCH = {os.path.join(B, "plan_ring_p5s02b.json"): "f4520b10", os.path.join(T, "stagesim.py"): "95a162ba", os.path.join(T, "stagexec.py"): "a4df7e15",
        os.path.join(T, "stage_prerun.py"): "7605116f", os.path.join(B, "plan_ring_p5s02b_licence.json"): "f61a2514",
        os.path.join(B, "errorlist_predicted_D1_ring_p5s02b_end.json"): "79ec3207"}


def leaves(v, pre=""):
    if isinstance(v, dict):
        return dict(kv for k, x in v.items() for kv in leaves(x, pre + ("." if pre else "") + str(k)).items())
    if isinstance(v, list):
        return dict(kv for i, x in enumerate(v) for kv in leaves(x, "{0}[{1}]".format(pre, i)).items())
    return {pre: v}


if "--snap" in sys.argv:
    for k, (cur, bef) in PAIRS.items():
        shutil.copyfile(cur, bef)
        print("FACT SNAP {0} {1} -> {2} md5 {3}".format(k, L.rel(cur), L.rel(bef), L.md5(bef)), flush=True)
    sys.exit(L.Gate().result([{"path": L.rel(b_), "md5": L.md5(b_)} for _c, b_ in PAIRS.values()]))
gate = L.Gate(fatal_default=False)
for k, (cur, bef) in PAIRS.items():
    a, b = leaves(L.J(bef)), leaves(L.J(cur))
    moved = sorted(p for p in set(a) | set(b) if a.get(p, "<absent>") != b.get(p, "<absent>"))
    for p in moved:
        print("FACT MOVED {0} {1}: {2} -> {3}".format(k, p, a.get(p, "<absent>"), b.get(p, "<absent>")), flush=True)
    gate("D {0} {1} -> {2}: {3} key(s) moved, all from the checkpoint set".format(k, L.md5(bef)[:8], L.md5(cur)[:8], len(moved)), set(moved) <= ALLOWED[k],
         sorted(set(moved) - ALLOWED[k]))
got = dict((L.rel(p), L.md5(p)[:8]) for p in UNCH)
gate("U md5 unchanged {0}".format(got), all(L.md5(p).startswith(w) for p, w in UNCH.items()), got)
sys.exit(gate.result([{"path": L.rel(c), "md5": L.md5(c)} for c, _b in PAIRS.values()]))
