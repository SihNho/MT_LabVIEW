"""test_setcommand_signed.py - FUNCTIONAL test of the signed rotor read, NO HARDWARE. SetCommand_signed_TEST.vi and
SetCommand_orig_TEST.vi carry the controller reply injected through a 'string' control (VISA resource '' -> the VISA
calls error harmlessly, auto error handling off).

Prediction contract (archive/peer/2026-09-14-setcommand-signed-copy-plan.md, conditional approval):
  T0 Ring -> case mapping: with 'POS 00000064\r' (a real CR byte) injected and Baseline Startpoint 0, exactly ONE
     Ring value gives Pos_degree != 0 on BOTH copies (the read case), and 'read buffer 2' == '00000064' (the
     substring window is [4, 8]); k = Pos_degree / 100.
  T1 POSITIVE regression, bit-for-bit vs the original: 00000000, 00000001, 00000064, 7FFFFFFE, 7FFFFFFF -> identical
     Pos_degree (float repr) and 'read buffer 2' on both copies; also with Baseline Startpoint = 200.
  T2 SIGNED (signed copy): FFFFFFF6 -> -10*k, FFFFFFFF -> -1*k, 80000000 -> -2147483648*k (all three exact to 1e-9
     relative; 7FFFFFFF above distinguishes an I16 cast, the negatives a U32 pass-through).
  T3 the ORIGINAL gives +4294967286*k for FFFFFFF6 (the bug, recorded).
  py tools/bgrun.py --max-min 10 --log tools/bench/test_setcommand_signed.log -- py -u tools/bench/test_setcommand_signed.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

OPT = os.path.join(g.CLAUDEDEV, "SetCommand_signed_TEST.vi")
OPO = os.path.join(g.CLAUDEDEV, "SetCommand_orig_TEST.vi")
LAB = json.load(open(os.path.join(HERE, "setcommand_signed_labels.json"), encoding="utf-8"))
g._run.__defaults__ = (6.0, 60.0)
PASS = []


def check(name, ok, detail=""):
    PASS.append((name, bool(ok)))
    print(f"   {'PASS' if ok else 'FAIL'} {name} {detail}", flush=True)


def run(vi, inject, ring, hexs, baseline=0.0):
    vi.SetControlValue("VISA resource name", ("", 0)); vi.SetControlValue("Ring", ring)
    vi.SetControlValue("Baseline Startpoint", baseline); vi.SetControlValue("Numeric", 0.0)
    vi.SetControlValue(inject, "POS " + hexs + "\r")
    try:
        g._run(vi)
    except RuntimeError as e:
        print(f"      run: {str(e)[:100]}", flush=True)
    return float(vi.GetControlValue("Pos_degree")), str(vi.GetControlValue("read buffer 2"))


def main():
    g._lv = None
    vs, vo = g.op(OPT), g.op(OPO)
    hits = {}
    for ring in range(4):
        ps, ss = run(vs, LAB["inject"], ring, "00000064"); po, so = run(vo, LAB["inject_orig"], ring, "00000064")
        print(f"   Ring {ring}: signed Pos_degree {ps!r} sub {ss!r} | original {po!r} sub {so!r}", flush=True)
        if ps != 0.0 or po != 0.0:
            hits[ring] = (ps, po, ss)
    check("T0 exactly one read case on both copies", len(hits) == 1 and all(v[0] != 0 and v[1] != 0 for v in hits.values()), str(hits))
    if len(hits) != 1:
        return 1
    ring = next(iter(hits)); k = hits[ring][1] / 100.0
    check("T0 substring window == the 8 hex digits", hits[ring][2] == "00000064", repr(hits[ring][2]))
    print(f"   read case = Ring {ring}; k = {k!r} deg/pulse (from the original)", flush=True)
    for hexs in ("00000000", "00000001", "00000064", "7FFFFFFE", "7FFFFFFF"):
        for bl in (0.0, 200.0):
            ps, ss = run(vs, LAB["inject"], ring, hexs, bl); po, so = run(vo, LAB["inject_orig"], ring, hexs, bl)
            check(f"T1 {hexs} baseline {bl:g}: signed == original", (repr(ps), ss) == (repr(po), so), f"signed {ps!r}/{ss!r} original {po!r}/{so!r}")
    for hexs, val in (("FFFFFFF6", -10), ("FFFFFFFF", -1), ("80000000", -2147483648)):
        ps, ss = run(vs, LAB["inject"], ring, hexs)
        exp = val * k
        check(f"T2 signed {hexs} -> {val}*k", abs(ps - exp) <= 1e-9 * max(1.0, abs(exp)), f"got {ps!r} expected {exp!r}")
    po, so = run(vo, LAB["inject_orig"], ring, "FFFFFFF6")
    check("T3 original FFFFFFF6 -> +4294967286*k (the bug)", abs(po - 4294967286 * k) <= 1e-9 * abs(4294967286 * k), f"got {po!r}")
    json.dump({"read_ring": ring, "k": k}, open(os.path.join(HERE, "setcommand_signed_result.json"), "w"), indent=2)
    n_ok = sum(1 for _n, ok in PASS if ok)
    print(f"\nSUMMARY {n_ok}/{len(PASS)} PASS", flush=True)
    for n, ok in PASS:
        print(f"   {'PASS' if ok else 'FAIL'} {n}", flush=True)
    return 0 if n_ok == len(PASS) else 1


if __name__ == "__main__":
    sys.exit(main())
