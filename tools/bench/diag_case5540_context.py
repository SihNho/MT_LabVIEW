r"""diag_case5540_context.py - Census B step 5: name the consumer of Case #5540's outputs and the values its reseed
frame forwards.

Measured so far (all identity-checked, read-only):
  frame 5582 forwards outer wires 1681 / 6041, driven by LeftShiftRegister 1142 / 5805  (the PREVIOUS state)
  frame 5592 forwards outer wires 5746 / 5979, driven by LoopTunnel 5752 / 5569         (values from OUTSIDE the loop)
  both case outputs (5975, 5637) are consumed by SubVI 5058

That ordering contradicts the E0 note "the case sits after the kernel, before the registers": the case appears to
choose what goes INTO the consumer. This script settles it by naming SubVI 5058, and resolves the two loop tunnels'
OUTER wires (5812 and 2731, recorded by census_case5540_hop2) to whatever produces the reseed values.

  py tools/bgrun.py --max-min 12 --log tools/bench/diag_case5540_context.log -- py -u tools/bench/diag_case5540_context.py
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

OUTER = [(5812, "outer wire of LoopTunnel 5569 -> the reseed 'good' value"),
         (2731, "outer wire of LoopTunnel 5752 -> the reseed 'x,y,z' value")]
OUT = os.path.join(HERE, "case5540_context.json")


def main():
    md5 = hashlib.md5(open(MAIN, "rb").read()).hexdigest()
    with open(MAP_OUT, encoding="utf-8") as f:
        labels = json.load(f)
    fresh()
    # 1. who is SubVI 5058? - from the cached subVI census (tools/bench/main_vi_subvis.json, 98 call sites), no
    #    LabVIEW call needed: uid 5058 = 'Track N beads four-fold over-kernel-v3.vi' on diagram 43 = THE KERNEL.
    with open(os.path.join(HERE, "main_vi_subvis.json"), encoding="utf-8") as f:
        hit = json.load(f)["by_uid"].get("5058")
    print(f"   SubVI 5058 = {hit}", flush=True)
    vi = g.op(OP)
    out = {"subvi_5058": hit}
    try:
        for wire, role in OUTER:
            rows = []
            for i in range(8):
                r = read_terminal(vi, labels, wire, i)
                if r["errs"] and r["owner_uid"] == 0:
                    break
                rows.append(r)
            srcs = [r for r in rows if r["is_source"] and r["recip_wire"] == wire]
            src = (srcs[0]["owner_class"], srcs[0]["owner_uid"]) if srcs else None
            sinks = [(r["owner_class"], r["owner_uid"]) for r in rows if not r["is_source"]]
            print(f"RESULT wire {wire} ({role}): driven by {src}; sinks {sinks}", flush=True)
            out[str(wire)] = dict(role=role, source=src, sinks=sinks)
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, default=str)
    finally:
        same = hashlib.md5(open(MAIN, "rb").read()).hexdigest() == md5
        print(f"   {'PASS' if same else 'FAIL'} main VI unchanged", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
