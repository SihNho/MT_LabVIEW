r"""diag_case5540_frame_sources.py - Census B step 3: what does each FRAME of Case #5540 put on its two outputs?

Measured so far (tools/bench/build_optunnelread_v0.log, 24/24 PASS):
  the case has exactly TWO frames, diagrams 5582 and 5592
  tunnel 6016 (-> x,y,z array):          frame 5582 <- inner wire 6071 | frame 5592 <- inner wire 6030
  tunnel 5680 (-> Bead is good? array):  frame 5582 <- inner wire 5710 | frame 5592 <- inner wire 6011

This resolves each of those four inner wires to the object that DRIVES it, with OpWireSource_v5 (verified 12/12:
exactly one `Is Source?` terminal whose reciprocal `Connected Wire` is the wire asked about, cast-output class equal
to the owner class). Read-only; the main VI is only opened by reference.

predict (the driver's paraphrase, which this census exists to confirm or refute): in ONE frame both wires come
straight from the case's input tunnels (the passthrough), and in the OTHER the x,y,z wire comes from the calibration
array and the good wire from an all-TRUE array builder.

  py tools/bgrun.py --max-min 12 --log tools/bench/diag_case5540_frame_sources.log -- py -u tools/bench/diag_case5540_frame_sources.py
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

INNER = [(6071, 5582, "x,y,z array", "frame A (diagram 5582)"),
         (6030, 5592, "x,y,z array", "frame B (diagram 5592)"),
         (5710, 5582, "Bead is good? array", "frame A (diagram 5582)"),
         (6011, 5592, "Bead is good? array", "frame B (diagram 5592)")]
OUT = os.path.join(HERE, "case5540_frame_sources.json")


def main():
    md5 = hashlib.md5(open(MAIN, "rb").read()).hexdigest()
    with open(MAP_OUT, encoding="utf-8") as f:
        labels = json.load(f)
    fresh()
    vi = g.op(OP)
    out = []
    try:
        for wire, frame, output, role in INNER:
            rows = []
            for i in range(6):
                r = read_terminal(vi, labels, wire, i)
                if r["errs"] and r["owner_uid"] == 0:
                    break
                rows.append(r)
            srcs = [r for r in rows if r["is_source"] and r["recip_wire"] == wire]
            ok = len(srcs) == 1 and all(r["cast_class"] == r["owner_class"] for r in rows)
            src = (srcs[0]["owner_class"], srcs[0]["owner_uid"]) if srcs else None
            sinks = [(r["owner_class"], r["owner_uid"]) for r in rows if not r["is_source"]]
            print(f"RESULT {role} {output}: inner wire {wire} is driven by {src}; sinks {sinks}; "
                  f"identity checks {'OK' if ok else 'FAILED'}", flush=True)
            out.append(dict(wire=wire, frame=frame, output=output, role=role, source=src, sinks=sinks, ok=ok))
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, default=str)
        print(f"SUMMARY {sum(1 for r in out if r['ok'])}/{len(out)} inner wires resolved with identity checks OK", flush=True)
    finally:
        same = hashlib.md5(open(MAIN, "rb").read()).hexdigest() == md5
        print(f"   {'PASS' if same else 'FAIL'} main VI unchanged", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
