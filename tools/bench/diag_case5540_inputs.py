r"""diag_case5540_inputs.py - Census B step 4: which outer value each frame of Case #5540 forwards.

Measured (tools/bench/diag_case5540_frame_sources.log, 4/4 identity checks OK): BOTH frames are pure pass-throughs -
each output wire is driven by one of the case's INPUT tunnels:

  frame 5582: x,y,z array <- SelectorTunnel 5825   | Bead is good? array <- SelectorTunnel 5702
  frame 5592: x,y,z array <- SelectorTunnel 5725   | Bead is good? array <- SelectorTunnel 5967

The E0 census (docs/stage2-assembly-step-e.md) recorded the case's outer input wires: t5 = 1681 (the kernel's
`x,y,z array out`), t3 = 6041 (`Bead is good? array out`), t1 = 5979 and t4 = 5746 (two values from outside the
diagram). This script resolves those four OUTER wires with OpWireSource_v5 and prints each wire's source AND its
sinks - the sink list names the tunnel the wire enters, which maps outer wire -> tunnel uid without another op.

predict: 1681 and 6041 enter two of {5825, 5702, 5725, 5967} (the pass-through frame), and 5979 / 5746 enter the
other two (the reseed frame, carrying the calibration array and an all-TRUE good array).

  py tools/bgrun.py --max-min 12 --log tools/bench/diag_case5540_inputs.log -- py -u tools/bench/diag_case5540_inputs.py
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))
import gscript as g  # noqa: E402
from build_opconstvalue_v1 import MAIN, fresh  # noqa: E402
from build_opwiresource_v5 import OP, MAP_OUT, read_terminal  # noqa: E402

OUTER = [(1681, "t5 = the kernel's x,y,z array out"),
         (6041, "t3 = the kernel's Bead is good? array out"),
         (5979, "t1 = a value from outside diagram 43"),
         (5746, "t4 = a value from outside diagram 43")]
FRAME_TUNNELS = {5825: "frame 5582 -> x,y,z", 5702: "frame 5582 -> good",
                 5725: "frame 5592 -> x,y,z", 5967: "frame 5592 -> good"}
OUT = os.path.join(HERE, "case5540_inputs.json")


def main():
    md5 = hashlib.md5(open(MAIN, "rb").read()).hexdigest()
    with open(MAP_OUT, encoding="utf-8") as f:
        labels = json.load(f)
    fresh()
    vi = g.op(OP)
    out = []
    try:
        for wire, role in OUTER:
            rows = []
            for i in range(8):
                r = read_terminal(vi, labels, wire, i)
                if r["errs"] and r["owner_uid"] == 0:
                    break
                rows.append(r)
            srcs = [r for r in rows if r["is_source"] and r["recip_wire"] == wire]
            sinks = [(r["owner_class"], r["owner_uid"]) for r in rows if not r["is_source"]]
            hits = [FRAME_TUNNELS[u] for _c, u in sinks if u in FRAME_TUNNELS]
            src = (srcs[0]["owner_class"], srcs[0]["owner_uid"]) if srcs else None
            print(f"RESULT outer wire {wire} ({role}): driven by {src}; sinks {sinks}"
                  f"{'  -> ' + '; '.join(hits) if hits else ''}", flush=True)
            out.append(dict(wire=wire, role=role, source=src, sinks=sinks, frame_roles=hits))
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, default=str)
        mapped = sum(1 for r in out if r["frame_roles"])
        print(f"SUMMARY {mapped}/{len(out)} outer wires mapped to a frame tunnel", flush=True)
    finally:
        same = hashlib.md5(open(MAIN, "rb").read()).hexdigest() == md5
        print(f"   {'PASS' if same else 'FAIL'} main VI unchanged", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
