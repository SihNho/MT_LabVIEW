# ---
# labview: none
# hardware: none
# evidence: tools/stage_prerun.py:14-17
# ---
"""diag_c147_a2_1_check - card 147-a2-1, OFFLINE: (1) stagexec.check_sink_gates on the s06 build recipe's declared pair (must be length 1,
sink [23166, 'Pos within cal image']), and the scratch recipe's import-time assert; (2) the gate callable sg_read on SYNTHETIC read_terms rows
(AT.read_terms and the binding stubbed): the good net -> ok True; indicator unwired, indicator on another net, a second source on the net,
an entry source that differs -> ok False each. COM is replaced by stage_prerun.install() BEFORE any recipe import, so nothing reaches LabVIEW.
PREDICTION: CSG len 1; scratch SG len 1; cases T1 True, T2..T5 False -> RESULT 7/0.
card 147-a1-7: sg_read now reads SGBackend.last_terms (the executor's final read), never AT.read_terms (stubbed to raise); + SGB (subclass
overrides only read), T6 (kept read not after the last op) False, T7 (no kept read) False -> RESULT 10/0."""
import hashlib, json, os, py_compile, sys                                          # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
for _f in ("stage_d1_ring_p4_s06v18.py", "stage_d1_ring_p4_s06v18_scratch.py"):   # gate-fp fp-54: py_compile here, not in command position
    _p = os.path.join(ROOT, "tools", "recipes", _f)
    py_compile.compile(_p, cfile=os.path.join(os.environ.get("TEMP", "."), _f + "c"), doraise=True)
    print("PY_COMPILE OK {0} md5 {1}".format(_f, hashlib.md5(open(_p, "rb").read()).hexdigest()), flush=True)
import stage_prerun as SP                                                          # noqa: E402
SP.install()
import stagexec as SX                                                              # noqa: E402
import stage_d1_ring_p4_s06v18 as R                                                # noqa: E402
import stage_d1_ring_p4_s06v18_scratch as RS                                       # noqa: E402  runs its import-time assert
ok_n, bad = 0, []


def gate(label, ok, detail=""):
    global ok_n
    print("{0}  {1}  {2}".format("PASS" if ok else "FAIL", label, detail), flush=True)
    if ok:
        ok_n += 1
    else:
        bad.append(label)


csg = SX.check_sink_gates(R.SINK_GATES, R.SINK_FNS)
gate("CSG build recipe check_sink_gates(SINK_GATES, SINK_FNS) has length 1, sink == [23166, 'Pos within cal image']",
     len(csg) == 1 and csg[0]["sink"] == [23166, "Pos within cal image"], json.dumps(csg))
gate("SSG scratch recipe's import-time SG == the build recipe's", RS.SG == csg, json.dumps(RS.SG))
a = R.SG_ACTS[0]
print("FACT SG_TERMS {0} SG_ACTS {1} SG_SRC_NAME {2}".format(R.SG_TERMS, [(x["id"], x["src"], x["dst"]) for x in R.SG_ACTS], R.SG_SRC_NAME), flush=True)


class FX(object):                                                                  # card 147-a1-7: the executor's final-read record
    bind = {"obj": {}, "term": {}, "diag": {}}
    ops = [None] * 21
    reads_real = [21]


class FS(object):
    work = "offline.vi"


class FB(object):                                                                  # card 147-a1-7: SGBackend.last_terms (the final read)
    last_terms = []


gate("SGB SGBackend subclasses LVBackend and overrides only read()", issubclass(R.SGBackend, SX.LVBackend)
     and sorted(k for k in vars(R.SGBackend) if not k.startswith("__")) == ["read"], sorted(vars(R.SGBackend)))
R.DRY = False
R.EX.update(x=FX(), s=FS(), be=FB())
td, ts, so, W = a["dst"]["term_uid"], a["src"]["term_uid"], a["src"]["uid"], 900001
row = lambda t, o, n, w, src: {"term_uid": t, "owner_uid": o, "term_name": n, "wire_uid": w, "is_source": src}   # noqa: E731
good = [row(td, 23166, "Pos within cal image", W, False), row(ts, so, R.SG_SRC_NAME[0], W, True), row(10975, 10969, "array", W, False)]
entry = {"gate": R.SG_GATE, "sink": [23166, "Pos within cal image"], "tag": "wire_indicators #5058", "err": "x", "source": [so, R.SG_SRC_NAME[0]]}
cases = [("T1 good net", good, entry, True),
         ("T2 indicator unwired", [dict(good[0], wire_uid=0)] + good[1:], entry, False),
         ("T3 indicator on another net", [dict(good[0], wire_uid=W + 1)] + good[1:], entry, False),
         ("T4 a second source on the net", good + [row(777, 778, "x", W, True)], entry, False),
         ("T5 entry source differs", good, dict(entry, source=[so, "other"]), False)]
R.AT.read_terms = lambda *a_, **k_: (_ for _ in ()).throw(AssertionError("sg_read must not read the VI"))   # card 147-a1-7: no own read
for name, rows, e, exp in cases:
    R.EX["be"].last_terms = rows
    ok, det = R.sg_read(e)
    gate("{0}: sg_read ok {1} expected {2}".format(name, ok, exp), bool(ok) == exp, det)
R.EX["be"].last_terms, R.EX["x"].reads_real = good, [20]                           # T6: the kept read is NOT the one after the last op
ok, det = R.sg_read(entry)
gate("T6 kept read not after the last op: sg_read ok {0} expected False".format(ok), not ok, det)
R.EX["be"].last_terms, R.EX["x"].reads_real = [], [21]                             # T7: no read kept
ok, det = R.sg_read(entry)
gate("T7 no kept read: sg_read ok {0} expected False".format(ok), not ok, det)
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if not bad else "FAIL", "gates": {"pass": ok_n, "fail": len(bad)},
                              "first_fail": bad[0] if bad else None, "artefacts": []}), flush=True)
sys.exit(0 if not bad else 1)
