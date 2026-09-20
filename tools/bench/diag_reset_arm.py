r"""diag_reset_arm.py - is the PERIODIC auto-reset gated by the `Auto-Reset` control, or not?

WHY THIS ONE QUESTION. The master plan says a dry run holds `Auto-Reset` OFF and therefore cannot self-terminate.
The third prior-art review attacked that (`archive/peer/2026-09-16-priorart-master-plan-rev3.md`, A3) with
`stage2-assembly-step-e.md:36-38`, which records a SECOND, periodic auto-reset term whose period an in-VI comment
puts at "~27 mins/100000" - far longer than the 1.9-minute fixture, which is why it never fired there. If that arm
is ungated, an hours-long dry run accumulates auto-resets and can hit `Limit of Program`'s exact-equality
stop-and-save on its own, and the plan's claim is wrong.

WHAT IS ALREADY KNOWN, offline, from tools/bench/main_netmap_diag43.json (no LabVIEW needed, read this session):

  And #9647     : `Auto-Reset`(wire 9806) AND (wire 9868 from `x < y?` #10950)  ->  wire 9921
  wire 9921     : selector of Case #10445  AND  (negated) the autofocus enable #10886
  Q&R #10068    : x <- wire 3268 (the frame counter, shared with the autofocus modulo #2136)
                  y <- wire 10103   (source is NOT a node on diagram 43)
                  remainder -> wire 10187, which NO node on diagram 43 consumes
  Equal? #10019 : `# of Auto-Reset`.Value (#9879) == wire 10142 (`Limit of Program`)  ->  wire 10249
  CompArith #11639: 12070 (out of Case #12589) o 6929 o 10249  ->  wire 3457

So the decisive unknowns are the three wires whose other end is a TUNNEL, a constant or a shift register - exactly
what the node-to-node dumps cannot see, and exactly what `OpWireSource_v5` reads. `stage2-assembly-step-e.md:75-76`
has carried `remainder 10187 -> (sink to find)` as open since it was written; this run is meant to close it.

PREDICTION CONTRACT:
  P1 wire 10187 (the periodic remainder) resolves to exactly one source and at least one sink.
  P2 If its sink chain reaches the same `And #9647` (or anything downstream of `Auto-Reset`), the periodic arm IS
     gated and the plan's claim stands. If it reaches the reseed `Or` / Case #10445 WITHOUT passing the control,
     the arm is ungated and rev3's A3 is right. Either outcome is a result; there is no "expected" one.
  P3 wire 10103 (the divisor) resolves to a source - most likely a control terminal (`Diagram`-owned, the
     signature recorded at INDEX.md row 43) or a constant.
  P4 wire 3457 (the stop/save chain) resolves to a sink outside the compound-arithmetic node.

Read-only on the main VI, md5 checked before and after. Nothing is built.

  py tools/bgrun.py --max-min 15 --log tools/bench/diag_reset_arm.log -- py -u tools/bench/diag_reset_arm.py
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
    (10187, "the PERIODIC modulo's remainder - the A3 question"),
    (10103, "the periodic modulo's DIVISOR (the period itself)"),
    (9868, "the other input of the reseed And #9647, from `x < y?` #10950"),
    (3457, "the compound-arithmetic output carrying `# of Auto-Reset == Limit of Program`"),
]
OUT = os.path.join(HERE, "reset_arm.json")


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
    print(f"RESULT wire {wire}: source {src}; sinks {sinks}", flush=True)
    return dict(wire=wire, why=why, source=src, sinks=sinks, n_terms=len(rows), n_sources=len(srcs))


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    md5 = hashlib.md5(open(MAIN, "rb").read()).hexdigest()
    with open(MAP_OUT, encoding="utf-8") as f:
        labels = json.load(f)
    fresh()
    out = {"main_md5_before": md5, "wires": []}
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
