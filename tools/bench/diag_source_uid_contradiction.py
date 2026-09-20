r"""diag_source_uid_contradiction.py - which measurement is right about who feeds wire 10850?

  constant scan  (OpConstValueN_v1): constant uid 10739 -> Constant.Terminal -> Connected Wire -> UID = 10850
  wire walk      (OpWireSource_v2):  wire 10850 -> Terms[] -> element 0 -> Owner -> UID = 3628 (class DigitalNumericConstant)

and uid 3628 is NOT in the reporter's 180-object DigitalNumericConstant list at all. Read-only discriminators, using
only ops that already exist:

  1. AGREEMENT SWEEP - take N constants from opconstvaluen_scan.json that report a fed wire, and ask OpWireSource_v2
     for that wire's source uid. Systematic disagreement indicts the wire walk (its Terms[0] pick); agreement
     everywhere except 10850 makes 10850 special and indicts the constant-side chain for that object.
  2. WHAT IS 3628 - feed uid 3628 (and 10739) straight into the same op's UID lookup and read back the object's own
     uid and class. That says what kind of object 3628 is, without any traversal.

  py tools/bgrun.py --max-min 15 --log tools/bench/diag_source_uid_contradiction.log -- py -u tools/bench/diag_source_uid_contradiction.py
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))
import gscript as g  # noqa: E402
from build_opconstvalue_v1 import MAIN, fresh  # noqa: E402
from build_opwiresource_v2 import OP, MAP_OUT, read_uid  # noqa: E402

SCAN = os.path.join(HERE, "opconstvaluen_scan.json")


def main():
    md5 = hashlib.md5(open(MAIN, "rb").read()).hexdigest()
    with open(MAP_OUT, encoding="utf-8") as f:
        labels = json.load(f)
    rows = json.load(open(SCAN, encoding="utf-8"))
    wired = [r for r in rows if r.get("wire") and not r.get("errW")]
    print(f"   {len(wired)} of {len(rows)} scanned constants report a fed wire", flush=True)
    fresh()
    vi = g.op(OP)
    try:
        print("== 1. agreement sweep (constant -> its fed wire -> that wire's source, per the wire walk)", flush=True)
        agree = dis = 0
        sample = wired[:12] + [r for r in wired if r["wire"] == 10850]
        for r in sample:
            w = read_uid(vi, labels, r["wire"])
            ok = w["owner_uid"] == r["uid"]
            agree += ok; dis += (not ok)
            print(f"OBSERVED: constant {r['uid']} (value {r['val']!r:.12}) says it feeds wire {r['wire']}; the wire says "
                  f"its source is {w['owner_class']} uid {w['owner_uid']} -> {'AGREE' if ok else 'DISAGREE'}", flush=True)
        print(f"SUMMARY agreement sweep: {agree} agree, {dis} disagree", flush=True)
        print("== 2. what object is uid 3628 (and 10739)?", flush=True)
        for u in (3628, 10739):
            vi.SetControlValue(labels["cls_back"], "POISON"); vi.SetControlValue(labels["uid_back"], 0)
            vi.SetControlValue("vi path", MAIN); vi.SetControlValue(labels["uid_in"], u)
            try:
                g._run(vi); err = g._err(vi, "error out") or ""
            except Exception as e:
                err = f"EXC {str(e)[:60]}"
            errL = g._err(vi, labels["errL"]) or ""
            print(f"OBSERVED: uid {u} -> lookup readback {int(vi.GetControlValue(labels['uid_back']))} "
                  f"class {vi.GetControlValue(labels['cls_back'])!r} {err[:40]} {errL[:40]}", flush=True)
    finally:
        same = hashlib.md5(open(MAIN, "rb").read()).hexdigest() == md5
        print(f"   {'PASS' if same else 'FAIL'} main VI unchanged", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
