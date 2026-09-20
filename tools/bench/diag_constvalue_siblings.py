r"""diag_constvalue_siblings.py - discriminator for the void numeric Constant.Value (peer archive/peer/2026-09-15-opconstvalue-numeric-void-variant.md
§4, ranks 3-4): read BooleanConstant and PathConstant objects of the main VI through the UNCHANGED OpConstValue_v1 op
(byte route), read-only. Interpretation matrix from the review: Boolean data + Path data + numeric void -> numeric
read-side defect; both void -> shared op/reference problem despite strings working.
predict (review's leading explanation): Boolean and Path carry DATA (Boolean TD 0x21, 1 byte; Path TD 0x32).

  py tools/bgrun.py --max-min 8 --log tools/bench/diag_constvalue_siblings.log -- py -u tools/bench/diag_constvalue_siblings.py
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))
import gscript as g  # noqa: E402
from build_opconstvalue_v1 import OP, MAIN, MAP_OUT, com_preflight  # noqa: E402
from build_opconstvalue_v1b import decode_flat  # noqa: E402
from build_opconstvalue_v1c import normalize_u8  # noqa: E402

with open(MAP_OUT, encoding="utf-8") as f:
    L = json.load(f)


def main():
    g.reset(); com_preflight()
    vi = g.op(OP)
    md5 = hashlib.md5(open(MAIN, "rb").read()).hexdigest()
    try:
        for cls, k in (("BooleanConstant", 4), ("PathConstant", 3), ("StringConstant", 1), ("DigitalNumericConstant", 1)):
            man = g.report(MAIN, cls)
            print(f"== {cls}: {len(man)} on the top diagram", flush=True)
            for i in range(min(k, len(man))):
                vi.SetControlValue(L["hex"], "POISON"); vi.SetControlValue("UID", 0); vi.SetControlValue(L["size"], False)
                vi.SetControlValue("vi path", MAIN); vi.SetControlValue("Class Name", cls); vi.SetControlValue("index", i)
                try:
                    g._run(vi); err = g._err(vi, "error out") or ""
                except Exception as e:
                    err = f"EXC {str(e)[:80]}"
                uid = int(vi.GetControlValue("UID")); b = normalize_u8(vi.GetControlValue(L["u8"])); hx = vi.GetControlValue(L["hex"])
                code, val, note = decode_flat(b) if b else (None, None, "no bytes")
                ident = uid == man[i]["uid"]
                print(f"OBSERVED: {cls}[{i}] uid={uid} ident={ident} len={len(b) if b else None} hex={hx!r:.60} -> TD={code!r} val={val!r:.30} {note} {err[:40]}", flush=True)
    finally:
        same = hashlib.md5(open(MAIN, "rb").read()).hexdigest() == md5
        print(f"   {'PASS' if same else 'FAIL'} main VI file unchanged", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
