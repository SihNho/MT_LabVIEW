r"""errorlist_expect_p3b2 - card 132-1 (PD275(d), retrospective-cycle131 finding 3a): P3b-2's expected Error List CLASS totals,
COMPUTED from the simulator's retired (LOST) / stub wire sets and P3b-1's expected file - never typed. Offline, no LabVIEW.
RULE (stated before the run; PD274(b) class debit):
  LOST = wires of the stage's sim step_00 absent from its last step (stagexec D gate's "lost"); profile = (sources, sinks) in step_00.
  - a LOST source-only wire (1/0, base uid > 0) carried a `wire has loose ends` item  -> CERTAIN debit 1 each
    (P3b-1: w3040 #6810 Image Out, 0 sinks, diag_c131_5_stubs.log:20);
  - a LOST sink-only wire (0/n) carried `connects ... sinks but has no source`        -> CERTAIN debit 1 each;
  - a LOST two-sided wire of the BASE (uid > 0) MAY carry a dangling-branch loose end (invisible in terminal data: the Error
    List items carry no uid, result_131-5.json:13)                                   -> UNCERTAIN debit 0..1 each;
  - a LOST wire created by the previous stage (sim uid < 0) was RLE'd by it (PD256(b))  -> 0;
  - a NEW stub in the last step (one-sided, not in step_00) -> CERTAIN credit to its class; + pred errorlist new_items_predicted.
CALIBRATION (gate K1): the same rule on ring_p3b1 (step_00 = P3a graph) must bracket P3b-1's MEASURED per-class change
(per_class_p3a -> per_class_read in the P3b-1 expected file: loose ends 24 -> 22) - lo <= measured <= hi, other classes exact.
OUTPUT: tools/bench/errorlist_expect_p3b2.json {per_class lo/hi, total lo/hi, exact?}; re-run after the rebase (card 132-3).
    py tools/bgrun.py --material --max-min 2 --log tools/bench/errorlist_expect_p3b2.log -- py -u tools/bench/errorlist_expect_p3b2.py"""
import collections, glob, json, os, sys                                            # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(B), ""))
import protocol as P                                                                # noqa: E402
EXP1 = os.path.join(B, "errorlist_expected_D1_ring_p3b1_20261002_060910.json")
PRED2 = os.path.join(B, "plan_ring_p3b2_pred.json")
OUT = os.path.join(B, "errorlist_expect_p3b2.json")
LOOSE, NOSRC = "wirewirehaslooseends", "thiswireconnectsoneormoredatasinksbuthasnosource"
J = lambda p: json.load(open(p, encoding="utf-8"))                                  # noqa: E731
res = []


def gate(name, ok, det=""):
    res.append((name, bool(ok)))
    print("{0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(det)[:900]), flush=True)


def prof(terms):
    w = collections.defaultdict(lambda: [0, 0])
    for t in terms:
        if t.get("wire_uid") not in (None, 0, -1):
            w[int(t["wire_uid"])][0 if t.get("is_source") else 1] += 1
    return w


def debit(stage):
    fs = sorted(glob.glob(os.path.join(B, "sim", stage, "step_*.json")))
    b, e = prof(J(fs[0])["state"]["terminals"]), prof(J(fs[-1])["state"]["terminals"])
    lost = sorted(set(b) - set(e))
    d = {"stage": stage, "base": os.path.basename(fs[0]), "end": os.path.basename(fs[-1]), "lost": lost,
         "certain": collections.Counter(), "uncertain": collections.Counter(), "zero": [], "why": {}}
    for k in lost:
        s_, n_ = b[k]
        if k < 0:
            d["zero"].append(k); d["why"][k] = "created by the previous stage (RLE'd)"            # noqa: E702
        elif s_ and not n_:
            d["certain"][LOOSE] -= 1; d["why"][k] = "source-only stub {0}/0".format(s_)           # noqa: E702
        elif n_ and not s_:
            d["certain"][NOSRC] -= 1; d["why"][k] = "sink-only stub 0/{0}".format(n_)             # noqa: E702
        else:
            d["uncertain"][LOOSE] -= 1; d["why"][k] = "two-sided {0}/{1}: dangling branch unknown".format(s_, n_)   # noqa: E702
    for k in sorted(set(e) - set(b)):
        if not e[k][0] or not e[k][1]:
            d["certain"][LOOSE if e[k][0] else NOSRC] += 1; d["why"][k] = "NEW stub {0}/{1}".format(*e[k])   # noqa: E702
    return d


def apply(per_class, d, new_items=0):
    lo, hi = dict(per_class), dict(per_class)
    for c, v in d["certain"].items():
        lo[c] = lo.get(c, 0) + v; hi[c] = hi.get(c, 0) + v                                       # noqa: E702
    for c, v in d["uncertain"].items():
        lo[c] = lo.get(c, 0) + v                                                                   # v < 0: the lower bound
    return lo, hi, sum(lo.values()) + new_items, sum(hi.values()) + new_items


E1 = J(EXP1)
d1 = debit("ring_p3b1")
print("  FACT  P3b-1 rule: lost {0}; {1}".format(d1["lost"], d1["why"]), flush=True)
lo1, hi1, tlo1, thi1 = apply(E1["per_class_p3a"], d1)
meas = E1["per_class_read"]
bad = [c for c in set(meas) | set(lo1) if not lo1.get(c, 0) <= meas.get(c, 0) <= hi1.get(c, 0)]
gate("K1 calibration on P3b-1: the rule brackets the measured per-class read (loose ends {0} in [{1}, {2}]; total {3} in [{4}, {5}])".format(
    meas.get(LOOSE), lo1.get(LOOSE), hi1.get(LOOSE), E1["total"], tlo1, thi1), not bad and tlo1 <= E1["total"] <= thi1, bad)
gate("K2 P3b-1 expected file is the measured final read (PD274(b)): total 53 == sum(per_class_read)", E1["total"] == sum(meas.values()),
     (E1["total"], sum(meas.values())))
pr = J(PRED2)
d2 = debit("ring_p3b2")
ni = int(pr["errorlist"]["new_items_predicted"])
print("  FACT  P3b-2 rule (provisional plan {0}): lost {1}; {2}; new_items_predicted {3} (pred)".format(
    pr["plan"]["md5"][:8], d2["lost"], d2["why"], ni), flush=True)
lo2, hi2, tlo2, thi2 = apply(meas, d2, ni)
out = {"schema": "errorlist-expect-computed/1", "card": "132-1", "stage": "D1_ring_p3b2", "plan": pr["plan"], "base_file": os.path.relpath(EXP1, os.path.dirname(os.path.dirname(B))),
       "rule": __doc__.split("RULE")[1].split("CALIBRATION")[0].strip(), "lost": d2["lost"], "why": dict((str(k), v) for k, v in d2["why"].items()),
       "per_class_lo": lo2, "per_class_hi": hi2, "total_lo": tlo2, "total_hi": thi2, "exact": tlo2 == thi2,
       "calibration_p3b1": {"lo": lo1.get(LOOSE), "hi": hi1.get(LOOSE), "measured": meas.get(LOOSE)},
       "provisional": "P3b-2 base is P3b-1's SIMULATED end; re-run after stage_prerun --rebase (card 132-3)"}
json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1)
print("  FACT  P3b-2 PREDICTED: total {0}..{1}; loose ends {2}..{3}; no-source {4}..{5}; exact {6} -> {7}".format(
    tlo2, thi2, lo2.get(LOOSE), hi2.get(LOOSE), lo2.get(NOSRC), hi2.get(NOSRC), out["exact"], os.path.relpath(OUT, os.path.dirname(os.path.dirname(B)))), flush=True)
gate("K3 P3b-2 prediction written (lo <= hi for every class)", all(lo2[c] <= hi2[c] for c in lo2) and os.path.isfile(OUT), OUT)
npass, nfail = sum(1 for _n, c in res if c), sum(1 for _n, c in res if not c)
print(P.result_line(P.make_result(npass, nfail, next((n for n, c in res if not c), None))), flush=True)
sys.stdout.flush()
os._exit(1 if nfail else 0)
