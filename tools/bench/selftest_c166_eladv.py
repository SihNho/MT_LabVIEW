# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_166-a1-3.md
# ---
r"""selftest_c166_eladv - card 166-a1-3 (OFFLINE, json only): the adoption Error List step judged by stagekit.el_advisory (PD403(d)(1)).
Found before writing: stagekit.el_advisory / el_advisory_print / el_advisory_selftest (tools/stagekit.py:2782-2837, synthetic reads only);
errorlist_check.reverdict (compare only, no by-design, no advisory). This file CALLS errorlist_check.advisory_inputs / final_verdict /
rejudge_read (new, card 166-a1-3) and stagekit.el_advisory; it holds inputs and checks only. %TEMP% copies only; it writes nothing in the repo.
Inputs: the stored cycle-165 adoption read errorlist_D1_ring_p5s02e_20261010_172913_20261010_173731.json (0c0664d8, 47 items), its expected file
= the PREDICTED end errorlist_predicted_D1_ring_p5s02e_end.json (2a8e2984), plan_ring_p5s02e.json (fd23974e), plan_ring_p5s02e_pred.json.
PREDICTION CONTRACT:
  A  el_advisory(read 47, pred, plan) rc 0 RECORDED, total diff -2, unseen []        A2 advisory_inputs(predicted file) -> the pred + plan
  B  + ONE planted item 'Feedback Node: Initializer terminal is not wired' (class in neither start read nor prediction): el_advisory rc 1;
     B2 the same through rejudge_read (the adoption path): MISMATCH, rc 1
  C  rejudge_read(stored read): verdict OK, rc 0, EL-ADVISORY decided, by-design verdict MISMATCH recorded; the literal log had rc 1
     (diag_c165_a3_4_el.log:85-86)
  D  stricter-only: |total diff| > 3 still rc 1 - read minus 4 known items (43, diff -6) and plus 6 known items (53, diff +4), both direct
     and through rejudge_read; +3 (diff +1) stays rc 0
  E  without a pred: the expected file copied WITHOUT its plan key -> advisory not applied, verdict MISMATCH rc 1 == the stored verdict;
     E2 a byte copy at another path (pred does not name it) -> not applied, MISMATCH rc 1
  F  stored file md5 unchanged (read, predicted file, pred, plan). PREDICTION: 11/0 (M0 A A2 B0 B B2 C D E E2 F).
    py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_c166_eladv.log -- py -u tools/bench/selftest_c166_eladv.py"""
import collections, copy, json, os, sys, tempfile                                          # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for _p in (ROOT, os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import errorlist_check as EC                                                                # noqa: E402
import stagekit as K                                                                        # noqa: E402
import prep_c156_a1_1_lib as L                                                              # noqa: E402  Gate / md5 / J (shared)
md5, J = L.md5, L.J
B = os.path.join(ROOT, "tools", "bench")
READ = os.path.join(B, "errorlist_D1_ring_p5s02e_20261010_172913_20261010_173731.json")
EXPF = os.path.join(B, "errorlist_predicted_D1_ring_p5s02e_end.json")
PLAN, PRED = os.path.join(B, "plan_ring_p5s02e.json"), os.path.join(B, "plan_ring_p5s02e_pred.json")
LOG165 = os.path.join(B, "diag_c165_a3_4_el.log")
PINS = {READ: "0c0664d8", EXPF: "2a8e2984", PLAN: "fd23974e"}
import glob, shutil                                                                         # noqa: E401,E402
for _d in glob.glob(os.path.join(tempfile.gettempdir(), "c166_eladv_*")):                  # a crashed earlier run's %TEMP% dir
    shutil.rmtree(_d, ignore_errors=True)
    print("FACT removed stale %TEMP% dir {0}: {1}".format(_d, not os.path.exists(_d)), flush=True)
TMP = tempfile.mkdtemp(prefix="c166_eladv_")
PLANT = {"raw": "Feedback Node: Initializer terminal is not wired", "detail": "", "index": 47}
g = L.Gate(width=700, fatal_default=False)
before = dict((p, md5(p)) for p in (READ, EXPF, PLAN, PRED))
g("M0 pins {0}".format(dict((os.path.basename(p), w) for p, w in PINS.items())), all(md5(p).startswith(w) for p, w in PINS.items()),
  dict((os.path.basename(p), md5(p)[:8]) for p in PINS))
R0 = J(READ)
items = [dict((k, v) for k, v in it.items() if k != "licensed_by") for it in R0["items"]]


def tmp_read(its, name):
    """A %TEMP% copy of the stored read with its items replaced (bed, gates, expected_file kept)."""
    R = copy.deepcopy(R0)
    R["items"], R["n_reported"], R["item_count"] = its, len(its), len(its)
    p = os.path.join(TMP, name)
    json.dump(R, open(p, "w", encoding="utf-8"), indent=1)
    return p


# A / A2
rc, rep = K.el_advisory(items, PRED, PLAN)
K.el_advisory_print(rc, rep)
g("A el_advisory(stored read {0} items, pred, plan) rc {1} verdict {2} total diff {3} unseen {4}".format(len(items), rc, rep.get("verdict"), rep.get("total_diff"), rep.get("unseen")),
  rc == 0 and rep.get("total_diff") == -2 and not rep.get("unseen"), rep)
pp, pl, why = EC.advisory_inputs(os.path.relpath(EXPF, ROOT))
g("A2 advisory_inputs(the predicted end file, relative path as the literal command) -> {0} / {1} ({2})".format(pp and os.path.basename(pp), pl and os.path.basename(pl), why),
  why is None and os.path.normcase(os.path.abspath(pp)) == os.path.normcase(PRED) and os.path.normcase(os.path.abspath(pl)) == os.path.normcase(PLAN))
# B / B2
pr = J(PRED)["errorlist"]["per_class"]
cls = K.el_class(PLANT)
g("B0 planted class {0} is in neither the start read classes nor the prediction".format(cls), cls not in pr["start_read"]["classes"] and cls not in pr["predicted"])
rcb, repb = K.el_advisory(items + [PLANT], PRED, PLAN)
K.el_advisory_print(rcb, repb)
g("B el_advisory(read + 1 planted) rc {0} unseen {1}".format(rcb, repb.get("unseen")), rcb == 1 and repb.get("unseen") == [cls], repb)
vb, rcb2, _R = EC.rejudge_read(tmp_read(items + [PLANT], "read_planted.json"), os.path.relpath(EXPF, ROOT))
g("B2 rejudge_read(read + 1 planted) verdict {0} rc {1}".format(vb, rcb2), vb == "MISMATCH" and rcb2 == 1 and (_R.get("el_advisory") or {}).get("rc") == 1)
# C
lit = [ln.strip() for ln in open(LOG165, encoding="utf-8", errors="replace").read().splitlines() if ln.startswith(("ERRORLIST-VERDICT", "BGRUN END"))]
print("FACT literal cycle-165 log {0}: {1}".format(os.path.basename(LOG165), lit), flush=True)
vc, rcc, RC = EC.rejudge_read(READ)
g("C rejudge_read(stored read, its own expected_file {0}): verdict {1} rc {2}; by-design verdict {3} recorded; literal log rc 1".format(
  R0.get("expected_file"), vc, rcc, RC.get("verdict_by_design")),
  vc == "OK" and rcc == 0 and RC.get("verdict_by_design") == "MISMATCH" and (RC.get("el_advisory") or {}).get("rc") == 0
  and any("BGRUN END rc=1" in x for x in lit) and any(x.startswith("ERRORLIST-VERDICT: MISMATCH") for x in lit), RC.get("el_advisory"))
# D stricter-only
known = next(it for it in items if K.el_class(it) == "other:wirewirehaslooseends")
loose = [n for n, it in enumerate(items) if K.el_class(it) == "other:wirewirehaslooseends"][:4]
minus4 = [it for n, it in enumerate(items) if n not in loose]
cases = [("minus 4 known (diff -6)", minus4, 1), ("plus 6 known (diff +4)", items + [dict(known)] * 6, 1), ("plus 3 known (diff +1)", items + [dict(known)] * 3, 0)]
okd = True
for name, its, want in cases:
    r1, rp = K.el_advisory(its, PRED, PLAN)
    K.el_advisory_print(r1, rp)
    v2, r2, _x = EC.rejudge_read(tmp_read(its, "read_%d.json" % len(its)), os.path.relpath(EXPF, ROOT))
    print("FACT D {0}: el_advisory rc {1}; rejudge_read {2} rc {3} (want {4})".format(name, r1, v2, r2, want), flush=True)
    okd = okd and r1 == want and r2 == want
g("D |total diff| > 3 -> rc 1 (direct and adoption path); +1 -> rc 0", okd)
# E without a pred
ex = J(EXPF)
ex.pop("plan")
noplan = os.path.join(TMP, "expected_noplan.json")
json.dump(ex, open(noplan, "w", encoding="utf-8"), indent=1)
ve, rce, RE = EC.rejudge_read(READ, noplan)
g("E expected file without a plan: verdict {0} rc {1} == stored verdict {2}; no advisory".format(ve, rce, R0.get("verdict")),
  ve == R0.get("verdict") == "MISMATCH" and rce == 1 and "el_advisory" not in RE and "verdict_by_design" not in RE)
cp = os.path.join(TMP, "expected_bytecopy.json")
open(cp, "wb").write(open(EXPF, "rb").read())
v3, rc3, R3 = EC.rejudge_read(READ, cp)
g("E2 byte copy at another path (the pred names the original): verdict {0} rc {1}; no advisory".format(v3, rc3), v3 == "MISMATCH" and rc3 == 1 and "el_advisory" not in R3)
# F
after = dict((p, md5(p)) for p in before)
g("F stored files unchanged: {0}".format(dict((os.path.basename(p), m[:8]) for p, m in after.items())), after == before)
for f in os.listdir(TMP):
    os.remove(os.path.join(TMP, f))
os.rmdir(TMP)
print("FACT %TEMP% dir removed: {0}".format(not os.path.exists(TMP)), flush=True)
sys.exit(g.result([]))
