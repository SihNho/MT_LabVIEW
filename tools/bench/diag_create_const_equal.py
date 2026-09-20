"""diag_create_const_equal.py - READ-ONLY census of the two erdosmiller creators route (c) wraps
(`docs/d1-build-plan.md` §11g.1): `Create Constant.vi` and `Create Equal.vi`.

WHY THIS RUN EXISTS. `build_opqueue.py`'s wrapper shape sets every creator input by SetControlValue on a control
that `create_control` made, so the Python wrapper must know what each input's DATA TYPE is. For the four queue
creators the answer was obvious (refnums + a cluster `location`). Here it is NOT:
  Create Constant.vi : Diagram in(0) location(2) Diagram out(4) **Type(5,IN)** Terminal(6,OUT) **Value(7,IN)**
  Create Equal.vi    : Diagram in(0) location(2) Diagram out(4) x(5,IN) x = y?(6,OUT) y(7,IN) CompareAgg?(9,IN)
(`archive/bench-2026-09-14-stage2-toolkit/probe_queue_vis.log:9-10` - the pane is already censused; the TYPES are
not.) Whether `Type` is a TERMINAL REFERENCE (LabVIEW's own right-click "Create Constant", which would also WIRE
the constant to that terminal and would settle D1's constant->Equal.y wiring in one call) or a type STRING
(the library ships `String to Type.vi` / `Type to String.vi` / `Get Term Type.vi`) changes the op's whole shape.
Guessing it costs a build; reading it costs one run.

PRIOR ART CHECKED: `grep -ril "create constant" tools/ docs/` -> only the §11g/§11d prose and the probe log above;
no recipe wraps either VI. `docs/toolkit-capabilities.md:46-47` covers READING a constant's value
(`OpConstValue_v1`, `OpConstValueN_v1`), never creating one.

PREDICTION CONTRACT (each line is pass/fail, nothing is inferred):
  C1  both library files exist on disk at the LV-Scripting path                       -> PASS
  C2  `conpane()` of each reproduces probe_queue_vis.log:9-10 exactly                 -> PASS
  C3  every connector control of each VI yields a value through GetControlValue, and
      its Python type is REPORTED (this is the measurement, not a gate)               -> PASS if no exception
  C4  neither library file's md5 changes across the run (rule 1: originals are read)  -> PASS

NO EDIT, NO SAVE, NO PANEL OPEN, NO TARGET. Nothing under user.lib is written.
"""
import hashlib
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

LIB = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting"
VIS = ["Create Constant.vi", "Create Equal.vi"]
EXPECT = {
    "Create Constant.vi": {0: "Diagram in", 2: "location (0, 0)", 4: "Diagram out", 5: "Type", 6: "Terminal",
                           7: "Value", 11: "error in (no error)", 15: "error out"},
    "Create Equal.vi": {0: "Diagram in", 2: "location (0, 0)", 4: "Diagram out", 5: "x", 6: "x = y?", 7: "y",
                        9: "Compare Aggregates?", 11: "error in (no error)", 15: "error out"},
}
P, F = [], []


def gate(name, ok, detail=""):
    (P if ok else F).append(name)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}", flush=True)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def main():
    g._lv = None
    g._run.__defaults__ = (6.0, 120.0)
    paths = [os.path.join(LIB, v) for v in VIS]
    before = {}
    for p in paths:
        gate("C1 " + os.path.basename(p), os.path.isfile(p), p)
        if os.path.isfile(p):
            before[p] = md5(p)
    if F:
        return 1

    for p in paths:
        name = os.path.basename(p)
        print(f"\n######## {name} ########", flush=True)
        cp = g.conpane(p, max_terminals=20)
        got = {i: v for i, v in cp.items() if v}
        exp = EXPECT[name]
        gate(f"C2 {name} conpane", got == exp, f"got {got}")
        vi = g.op(p)                       # GetVIReference only - no panel open, no edit
        for i, label in sorted(exp.items()):
            try:
                v = vi.GetControlValue(label)
                tn = type(v).__name__
                if isinstance(v, tuple) and v:
                    tn += "[%d] of %s" % (len(v), ", ".join(type(e).__name__ for e in v[:4]))
                print(f"   t{i:>2} {label!r:<24} -> {tn:<28} value={str(v)[:70]!r}", flush=True)
            except Exception as e:
                print(f"   t{i:>2} {label!r:<24} -> EXC {str(e)[:120]}", flush=True)
        gate(f"C3 {name} control types read", True)

    for p in paths:
        gate("C4 md5 " + os.path.basename(p), md5(p) == before[p], before[p])

    print(f"\nVERDICT: {len(P)} pass / {len(F)} fail" + (f"  failing: {F}" if F else ""), flush=True)
    return 0 if not F else 1


if __name__ == "__main__":
    t0 = time.time()
    rc = main()
    print(f"elapsed {time.time() - t0:.1f} s", flush=True)
    sys.exit(rc)
