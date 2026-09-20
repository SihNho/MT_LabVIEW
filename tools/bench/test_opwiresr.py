"""test_opwiresr.py - the FUNCTIONAL test of the four saved OpWireSR_*_v0 ops, rerun on its own (the ops were built
and saved by build_opwiresr_v0.py; its test phase died at the first drop_subvi behind what the watchdog called a modal
dialog - peer: archive/peer/2026-09-14-wiresr-test-fail1-watchdog-modal.md).

DISCRIMINATOR added here: every `lv_gui -Action dialogs` poll made by gscript's watchdog is LOGGED VERBATIM (the raw
window-state rows), so a 'BLOCKED' verdict shows exactly WHICH windows were blocked/enabled at that moment - a real
LabVIEW dialog has its own title; the scratch's own "... Block Diagram"/front-panel window would mean a false positive.
Prediction if the false-positive hypothesis holds: the only enabled non-floating window in a BLOCKED poll is the
scratch's Block Diagram window. Everything else = build_opwiresr_v0.test's contract (T1-T9).
  py tools/bgrun.py --max-min 15 --log tools/bench/test_opwiresr.log -- py -u tools/bench/test_opwiresr.py
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))
import gscript as g  # noqa: E402
import build_opwiresr_v0 as B  # noqa: E402

_orig = g._lv_gui


def logged(*args):
    out = _orig(*args)
    if args and args[0] == "-Action" and len(args) > 1 and args[1] == "dialogs":
        print(f"   [watchdog {time.strftime('%H:%M:%S')}] dialogs ->\n      " + out.strip().replace("\n", "\n      "), flush=True)
    return out


def main():
    g._lv = None
    g._lv_gui = logged
    with open(B.MAP_OUT, encoding="utf-8") as f:
        labels = json.load(f)
    B.test(labels)
    n_ok = sum(1 for _n, ok in B.PASS if ok)
    print(f"\nSUMMARY {n_ok}/{len(B.PASS)} PASS", flush=True)
    for n, ok in B.PASS:
        print(f"   {'PASS' if ok else 'FAIL'} {n}", flush=True)
    return 0 if B.PASS and n_ok == len(B.PASS) else 1


if __name__ == "__main__":
    sys.exit(main())
