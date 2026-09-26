r"""selftest_c100_v5wrap.py - card 100-4 V5: the stagekit.Stage.create_local_write WRAPPER logic, OFFLINE (no LabVIEW).
Its LabVIEW behaviour is gscript.create_local_write's, measured FUNCTIONAL in tools/bench/diag_c100_verbs_build3.log:74-98
(that harness may not import stagekit: guard_bash gates a script that imports it and calls delete_object/save as a STAGE).
What the wrapper adds (stagekit.py:685-697) is tested here with the two gscript calls it makes replaced by fakes:
exact-label -> panel index (exactly one row, else Stop), explicit panel_index passed through, the verb's ValueError
recorded in the op record's `err` (never raised), the result dict returned as `result`, one ops[] record per call.
PREDICTION: 6/0.   py tools/bgrun.py --material --max-min 2 --log tools/bench/selftest_c100_v5wrap.log -- py -u tools/bench/selftest_c100_v5wrap.py
"""
import os, sys                                                                             # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))  # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                                      # noqa: E402
import stagekit as K                                                                      # noqa: E402
G = []


def gate(k, ok, d=""):
    G.append((k, bool(ok))); print("  GATE %s  %s  %s" % ("PASS" if ok else "FAIL", k, str(d)[:300]), flush=True)  # noqa: E702


ROWS = [{"label": "a"}, {"label": "Force (pN) vs Extension (nm) "}, {"label": "dup"}, {"label": "dup"}]
SEEN = []


def fake_pw(target):
    return [dict(r) for r in ROWS]


def fake_clw(target, panel_index, dest, position):
    SEEN.append((target, panel_index, dest, tuple(position)))
    if dest == 44143:
        raise ValueError("#44143 is not a Diagram of fake.vi")
    return {"uid": 900 + panel_index, "owner_class": "Diagram", "owner": dest, "is_source": [False], "err": ""}


K.g.panel_wiring, K.g.create_local_write = fake_pw, fake_clw
s = K.Stage("in.vi", "0" * 32, "c100_v5wrap", fresh=False, pins=(), preload=False, work_dir=os.environ.get("TEMP", HERE),
            out_json=os.path.join(os.environ.get("TEMP", HERE), "c100_v5wrap.json"))
s.node_mark = lambda tag="": []
rec = s.create_local_write("Force (pN) vs Extension (nm) ", None, 44125, (60, 60))
gate("W1 exact label -> panel index 1, dest/position passed through", SEEN[-1][1:] == (1, 44125, (60, 60)), SEEN[-1])
gate("W2 the verb's result dict is returned as `result`, err ''",
     rec["result"] == {"uid": 901, "owner_class": "Diagram", "owner": 44125, "is_source": [False], "err": ""} and not rec["err"], rec)
rec = s.create_local_write("a", None, 44143, (1, 2))
gate("W3 the verb's ValueError is RECORDED in `err`, not raised", "ValueError" in (rec["err"] or "") and rec["result"] is None, rec)
for lab in ("no such label", "dup"):
    try:
        s.create_local_write(lab, None, 44125); ok = False                                # noqa: E702
    except K.Stop as e:
        ok = True; print("  FACT  Stop for %r: %s" % (lab, e), flush=True)               # noqa: E702
    gate("W4 label %r (0 or 2 rows) -> Stop before the verb" % lab, ok and SEEN[-1][1] == 0, SEEN[-1])
rec = s.create_local_write("ignored", 3, 44125, (5, 5))
gate("W5 explicit panel_index passed through, one ops[] record per verb call",
     SEEN[-1][1] == 3 and len([o for o in s.R["ops"] if o["verb"] == "create_local_write"]) == 3, (SEEN[-1], len(s.R["ops"])))
bad = [k for k, ok in G if not ok]
print("=== GATES: %d pass / %d fail" % (len(G) - len(bad), len(bad)), flush=True)
print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, [])), flush=True)
sys.exit(1 if bad else 0)
