# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_159-a4-1.md
# ---
"""diag_c159_a4_1_taint - card 159-a4-1, OFFLINE (COM stubbed, the stage_prerun dry in this process): which stub use taints the
RingSession result gates D and PB in the dry of tools/recipes/stage_d1_ring_p5s02a.py. Every taint increment (Fake use, or a static
base-graph read after the first mutation) is recorded with the innermost tools/*.py frames; printed grouped by location, for the
increments that happen inside RingSession.gates_ng_fr_d / gate_pb. Writes nothing outside %TEMP% (the dry's own fences).
PREDICTION: at least one TAINT line inside gates_ng_fr_d or gate_pb (the self-test saw D and PB UNVERIFIED-DRY)."""
import collections
import os
import sys
import traceback

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import builtins  # noqa: E402
import stage_prerun as SP  # noqa: E402

EV = collections.Counter()


def where():
    st = traceback.extract_stack()[:-2]
    inside = [f.name for f in st if f.name in ("gates_ng_fr_d", "gate_pb", "gate_td", "gate_cen2")]
    if not inside:
        return None
    tools = [f for f in st if os.sep + "tools" + os.sep in f.filename and "stage_prerun" not in f.filename
             and "diag_c159" not in f.filename]
    return inside[-1] + " | " + " > ".join("{0}:{1} {2}".format(os.path.basename(f.filename), f.lineno, f.name) for f in tools[-4:])


orig_t = SP.Fake._t


def _t(self):
    w = where()
    if w:
        EV["FAKE " + object.__getattribute__(self, "_n") + " | " + w] += 1
    return orig_t(self)


SP.Fake._t = _t
orig_gc = SP._graph_call


def _gc(meth, default):
    f0 = orig_gc(meth, default)

    def f(*a, **k):
        if SP.D.mutated:
            w = where()
            if w:
                EV["GRAPH " + meth + " | " + w] += 1
        return f0(*a, **k)
    f._dry = True
    return f


SP._graph_call = _gc
try:
    tr = SP.dry(os.path.join(HERE, "recipes", "stage_d1_ring_p5s02a.py"))
finally:
    builtins.open = SP.REAL_OPEN
print("\n=== TAINT EVENTS inside RingSession result gates: {0} locations".format(len(EV)), flush=True)
for k, n in EV.most_common(40):
    print("TAINT x{0}  {1}".format(n, k[:600]), flush=True)
print("FACT dry status {0} unverified {1}".format(tr["status"], [u[:40] for u in tr["unverified"]]), flush=True)
import protocol  # noqa: E402
print(protocol.result_line(protocol.make_result(len(EV), 0, None, status="PASS")), flush=True)
