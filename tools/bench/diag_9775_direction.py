r"""diag_9775_direction.py - does uid 9775 on startup diagram 87 READ the camera geometry, or WRITE it?

WHY THIS ONE QUESTION. `camera-acquisition-facts.md:511-515` states it as the open one: *"Still open, and it is the
whole question: is uid 9775 reading or writing? ... a WRITE means the VI sets it and the value on the wire is the
answer."* It matters because diagram 87 is the frame that opens the camera session (`stage2-plan.md:17`:
`IMAQdx Open Camera` -> `Configure Grab`), so in a COPY of the original this node runs before anything else -
and `camera-acquisition-facts.md:421-438` records a 640x512 observation with four hypotheses falsified and the
panel indicators still holding 640/512 from the last real run. **If 9775 writes, the dry run's frame size is set by
the copy and every Phase 2 budget number is against the wrong geometry** (the plan assumes 1280x1024 throughout).
It is Phase A9 of `docs/pre-rig-master-plan.md`, raised at prior-art rev4 A5 and again at rev5 A9.

WHY THE PREVIOUS ATTEMPT COULD NOT ANSWER IT, and why this one can. `tools/bench/whats_next_to_9775.py` sorted
objects by POSITION around uid 9775 and labelled them LEFT (=> write) / RIGHT (=> read). That method is invalid on
this VI and our own notes say so: the main block diagram was rearranged by LabVIEW's Clean Up Diagram, so node
positions carry NO functional meaning. Its own log calls the result "narrowed it but did not settle it" - 61
objects within 700 units, the three nearest all to the left. `read_diagram87.py` then found the two geometry
terminals ARE wired (`Height` -> wire 32937, `Width` -> wire 32938) but each net came back with only its own
terminal on it, because front-panel terminals and constants are not `Nodes[]` and are invisible to that walk.

`OpWireSource_v5` has neither limitation: it is addressed by WIRE UID, walks `Wire.Terms[]`, and reports for each
terminal whether it `Is Source?` plus its owner's class and UID (`toolkit-capabilities.md`; INDEX row 43, 12/12).
Direction then falls out of one bit, with no geometry and no traverse index involved:

    the SOURCE of wire 32937 is uid 9775 itself   =>  the terminal is an OUTPUT  =>  9775 READS Height
    the SOURCE is any other object                =>  the terminal is an INPUT   =>  9775 WRITES Height

PREDICTION CONTRACT (stated before the run; either outcome is a result, there is no "expected" one):
  P1 wire 32937 resolves to exactly ONE terminal with `Is Source?` TRUE whose reciprocal wire is 32937.
  P2 wire 32938 likewise.
  P3 Each wire's source owner is either uid 9775 (=> READ) or some other object (=> WRITE). A LabVIEW property
     node may mix read and write terminals on one node, so the two wires are NOT asserted to agree - they are
     reported separately, and a disagreement is a real finding rather than an error.
  P4 If a source is a Constant, its UID is printed so the value can be read in a follow-up step with
     `OpConstValueN_v1` - that value would BE the geometry the copy applies.
  FAIL of P1/P2 (zero or several sources) means the wire UID is stale or the op mis-walks this net; report it as a
  failed prediction and do not reason past it.

Read-only on the main VI, md5 checked before and after. Nothing is built, no lock is taken beyond the COM instance.

  py tools/bgrun.py --max-min 15 --log tools/bench/diag_9775_direction.log -- py -u tools/bench/diag_9775_direction.py
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))
import gscript as g  # noqa: E402
from build_opconstvalue_v1 import MAIN, fresh  # noqa: E402
from build_opwiresource_v5 import OP, MAP_OUT, read_terminal  # noqa: E402

TARGET = 9775
WIRES = [
    (32937, "uid 9775 terminal[4] 'Height' - diagram 87"),
    (32938, "uid 9775 terminal[5] 'Width'  - diagram 87"),
]
OUT = os.path.join(HERE, "diag_9775_direction.json")


def resolve(vi, labels, wire, why):
    print(f"\n=== wire {wire}: {why}", flush=True)
    rows = []
    for i in range(8):
        r = read_terminal(vi, labels, wire, i)
        if r["errs"] and r["owner_uid"] == 0:
            break
        rows.append(r)
    srcs = [r for r in rows if r["is_source"] and r["recip_wire"] == wire]
    sinks = [(r["owner_class"], r["owner_uid"]) for r in rows if not r["is_source"]]
    src = (srcs[0]["owner_class"], srcs[0]["owner_uid"]) if len(srcs) == 1 else None

    if src is None:
        verdict = f"**P1/P2 FAILED** - {len(srcs)} sources found, not 1. Do not reason past this."
    elif src[1] == TARGET:
        verdict = f"READ - uid {TARGET} drives wire {wire}, so the terminal is an OUTPUT (a property read)."
    else:
        verdict = (f"WRITE - wire {wire} is driven by {src[0]} uid {src[1]}, NOT by uid {TARGET}, so the terminal "
                   f"is an INPUT and the VI SETS this geometry. Read {src[0]} uid {src[1]}'s value next.")
    print(f"RESULT wire {wire}: source {src}; sinks {sinks}\nVERDICT {verdict}", flush=True)
    return dict(wire=wire, why=why, source=src, sinks=sinks, n_terms=len(rows), n_sources=len(srcs),
                verdict=verdict)


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    md5 = hashlib.md5(open(MAIN, "rb").read()).hexdigest()
    with open(MAP_OUT, encoding="utf-8") as f:
        labels = json.load(f)
    fresh()
    out = {"main_md5_before": md5, "target_uid": TARGET, "wires": []}
    try:
        vi = g.op(OP)
        for wire, why in WIRES:
            out["wires"].append(resolve(vi, labels, wire, why))
    finally:
        after = hashlib.md5(open(MAIN, "rb").read()).hexdigest()
        out["main_md5_after"] = after
        out["main_unchanged"] = after == md5
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, default=str)
        # `FAIL`, NOT `**FAIL**` (2026-09-20, cycle 53): the bold form is invisible to guard_peer's FAILURE_RE.
        print(f"\n   {'PASS' if after == md5 else 'FAIL'} main VI unchanged; wrote {OUT}", flush=True)
        g._lv = None
    n = sum(1 for w in out["wires"] if w["source"])
    print(f"\n=== SUMMARY {n}/{len(WIRES)} wires resolved to a single source ===", flush=True)
    for w in out["wires"]:
        print(f"    wire {w['wire']}: {w['verdict']}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
