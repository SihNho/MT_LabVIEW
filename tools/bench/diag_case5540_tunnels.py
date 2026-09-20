r"""diag_case5540_tunnels.py - step 1 of Census B: name the TUNNEL objects behind Case #5540's two output wires.

`OpWireSource_v5` (12/12 PASS) resolves any wire uid to the object that drives it, with the identity checks the
reviews demanded (exactly one `Is Source?` terminal whose reciprocal `Connected Wire` is the wire asked about, and the
cast-output class equal to the owner class). Read-only; the main VI is only opened by reference.

Wires (docs/stage2-assembly-step-e.md, E0 census):
  5975 -> `x,y,z array` right shift register
  5637 -> `Bead is good? array in` right shift register
predict: the source of each is a tunnel object (concrete class `ConditionalTunnel` per the case-tunnel API answer),
whose uid is what the per-frame inner-terminal reader will address next.

  py tools/bgrun.py --max-min 12 --log tools/bench/diag_case5540_tunnels.log -- py -u tools/bench/diag_case5540_tunnels.py
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

WIRES = {5975: "#5540 output -> x,y,z array (right shift register)",
         5637: "#5540 output -> Bead is good? array in (right shift register)",
         10850: "control: Less?.y, already settled (constant 10739 = I32 0)"}
OUT = os.path.join(HERE, "case5540_tunnel_uids.json")


def main():
    md5 = hashlib.md5(open(MAIN, "rb").read()).hexdigest()
    with open(MAP_OUT, encoding="utf-8") as f:
        labels = json.load(f)
    fresh()
    vi = g.op(OP)
    out = []
    try:
        for wu, role in WIRES.items():
            rows = []
            for i in range(6):
                r = read_terminal(vi, labels, wu, i)
                if r["errs"] and r["owner_uid"] == 0:
                    break
                rows.append(r)
            srcs = [r for r in rows if r["is_source"] and r["recip_wire"] == wu]
            sinks = [r for r in rows if not r["is_source"] and r["recip_wire"] == wu]
            ok = len(srcs) == 1 and all(r["cast_class"] == r["owner_class"] for r in rows)
            print(f"RESULT wire {wu} ({role}): {len(rows)} terminals, source = "
                  f"{(srcs[0]['owner_class'], srcs[0]['owner_uid']) if srcs else None}, sinks = "
                  f"{[(r['owner_class'], r['owner_uid']) for r in sinks]}, identity checks {'OK' if ok else 'FAILED'}", flush=True)
            out.append(dict(wire=wu, role=role, source=(srcs[0]["owner_class"], srcs[0]["owner_uid"]) if srcs else None,
                            sinks=[(r["owner_class"], r["owner_uid"]) for r in sinks], ok=ok))
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, default=str)
    finally:
        same = hashlib.md5(open(MAIN, "rb").read()).hexdigest() == md5
        print(f"   {'PASS' if same else 'FAIL'} main VI unchanged", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
