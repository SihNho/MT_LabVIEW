r"""diag_autofocus_border.py - name the two objects the autofocus criterion depends on (master plan A6 remainder).

A6 established the criterion OFFLINE, from dumps we already had (docs/camera-acquisition-facts.md, "MEASURED
2026-09-16"): `CaseStructure #10407` on diagram 43 fires on

    AND( (frame index mod N) == 0 , NOT(x) )

and two names in that expression are still unresolved, because both are LOOP-BORDER objects that the node-to-node
edge dumps cannot see:

  * **wire 3362** -> `.not. x?` #10825 input. `frame_loop_state.json` classes it "one-sided ... inner_feeds_body",
    i.e. it enters the frame loop from a tunnel / shift register / constant. **This one decides whether a dry run
    auto-disarms the ASI focus axis**, which is the forbidden instrument - so it gates master plan 0.5.
  * **wire 31234** -> the `y` (divisor) input of `x-y*floor(x/y)` #2136, driven by Property Node **#30146**'s
    `Value` whose own `reference` terminal is UNWIRED, i.e. an implicit property node linked to a front-panel
    object. Panel candidates from `main-vi-panel-map.md`: `Limit of Auto-Focus` #48, `Focus Deviation from the
    Center` #33, `Auto-Focus` #38.

And one confirmation worth its single call: **wire 3268**, which the netmap shows feeding `save trace.vi` t7
"frame index" and `WLC function sub.vi` t0 "index i", is assumed here to be the loop's frame counter. It is the
modulo's dividend, so if it is something else the whole "every N-th frame" reading is wrong.

NOTHING IS BUILT. This runs the existing `OpWireSource_v5` (verified 12/12 on inner wires,
tools/bench/diag_case5540_frame_sources.py) and the existing reporter. The main VI is opened READ-ONLY and its
md5 is checked before and after (rule 1).

PREDICTION CONTRACT - what would make this a failed prediction:
  P1 wire 3362 resolves to exactly ONE source terminal, whose owner is a border object
     (LoopTunnel / LeftShiftRegister / SelectorTunnel / a constant / a ControlTerminal).
  P2 wire 3268 resolves to exactly ONE source, and it is a counter-shaped object (shift register or an
     increment), not a subVI output.
  P3 `report_all(MAIN, "PropertyNode")` contains uid 30146. Whether any returned field names the LINKED control
     is UNKNOWN and is the thing being measured - if no field does, that is a recorded capability gap, not a
     failure, and the next step is an API question to a peer, not a new op built on a guess.

  py tools/bgrun.py --max-min 20 --log tools/bench/diag_autofocus_border.log -- py -u tools/bench/diag_autofocus_border.py
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

WIRES = [
    (3362, "the NOT's input - the boolean that can block autofocus (gates master plan 0.5)"),
    (31234, "Property Node #30146 `Value` -> the modulo divisor N"),
    (3268, "the modulo's dividend - assumed to be the frame index"),
]
PROP_UID = 30146
OUT = os.path.join(HERE, "autofocus_border.json")


def resolve(vi, labels, wire, why):
    print(f"\n=== wire {wire}: {why}", flush=True)
    rows = []
    for i in range(6):
        r = read_terminal(vi, labels, wire, i)
        if r["errs"] and r["owner_uid"] == 0:
            break
        rows.append(r)
    srcs = [r for r in rows if r["is_source"] and r["recip_wire"] == wire]
    sinks = [(r["owner_class"], r["owner_uid"]) for r in rows if not r["is_source"]]
    src = (srcs[0]["owner_class"], srcs[0]["owner_uid"]) if len(srcs) == 1 else None
    print(f"RESULT wire {wire} driven by {src}; sinks {sinks}; "
          f"{len(srcs)} source terminal(s) of {len(rows)} read", flush=True)
    return dict(wire=wire, why=why, source=src, sinks=sinks, n_terms=len(rows), n_sources=len(srcs))


def property_node_fields():
    """P3: what does the reporter actually know about a PropertyNode? Print EVERY field, do not assume."""
    print(f"\n=== Property Node #{PROP_UID}: every field the reporter returns", flush=True)
    try:
        objs = g.report_all(MAIN, "PropertyNode")
    except Exception as e:
        print(f"  report_all raised: {e}", flush=True)
        return {"error": str(e)[:200]}
    print(f"  {len(objs)} PropertyNode objects in the VI", flush=True)
    hit = [o for o in objs if o.get("uid") == PROP_UID]
    if not hit:
        print(f"  !! uid {PROP_UID} NOT among them - P3 failed", flush=True)
        return {"found": False, "count": len(objs), "sample_keys": sorted(objs[0].keys()) if objs else []}
    rec = hit[0]
    for k in sorted(rec):
        print(f"    {k:<14} = {rec[k]!r}", flush=True)
    names = [k for k in rec if any(t in k.lower() for t in ("label", "name", "link", "caption", "terminal"))]
    print(f"  fields that could carry the linked control: {names or 'NONE - capability gap, record it'}", flush=True)
    return {"found": True, "record": {k: str(rec[k]) for k in rec}, "name_like_fields": names}


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    md5 = hashlib.md5(open(MAIN, "rb").read()).hexdigest()
    with open(MAP_OUT, encoding="utf-8") as f:
        labels = json.load(f)
    fresh()
    out = {"main_md5_before": md5, "wires": [], "property_node": None}
    try:
        vi = g.op(OP)
        for wire, why in WIRES:
            out["wires"].append(resolve(vi, labels, wire, why))
        out["property_node"] = property_node_fields()
    finally:
        after = hashlib.md5(open(MAIN, "rb").read()).hexdigest()
        out["main_md5_after"] = after
        out["main_unchanged"] = after == md5
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, default=str)
        # `FAIL`, NOT `**FAIL**` (2026-09-20, cycle 53): the bold form is invisible to guard_peer's FAILURE_RE.
        print(f"\n   {'PASS' if after == md5 else 'FAIL'} main VI unchanged", flush=True)
        print(f"   wrote {OUT}", flush=True)
        g._lv = None
    resolved = sum(1 for w in out["wires"] if w["source"])
    print(f"\n=== SUMMARY {resolved}/{len(WIRES)} wires resolved to a single source; "
          f"property-node fields {'read' if out['property_node'] else 'NOT read'} ===", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
