"""test_opshiftregs.py - FUNCTIONAL acceptance of OpShiftRegs_v0 (gscript.shift_reg) on the frame loop.

Prediction contract (peer archive/peer/2026-09-14-opshiftregs-v0-plan.md, its inferences made explicit):
  T1 main VI, WhileLoop index 1 (uid 637 = the frame loop), registers 0..13: the census runs without errors and the
     UID column equals loop_cast's shift_reg_uids in order.
  T2 class name: every element 'LeftShiftRegister' (peer's likelier reading: the array lists LEFT registers) - a
     mixed/other answer is recorded, not failed (the point of v0).
  T3 one inside terminal per register (a While loop has one frame) and its Is Source? is TRUE (inner side of a left
     register is a source); the outside terminal's Is Source? is FALSE (initial-value input) - an uninitialised
     register has outside wire 0 (valid, peer).
  T4 handle audit: 20 runs flat within +-100 (post-idle).
Output tools/bench/main_vi_shiftregs.json (per-register rows) for the stitch into docs/frame-loop-wire-graph.md.
  py tools/bgrun.py --max-min 20 --log tools/bench/test_opshiftregs.log -- py -u tools/bench/test_opshiftregs.py
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

MAIN = json.load(open(os.path.join(HERE, "diagram_tree_main.json"), encoding="utf-8"))["vi"]
FRAME_LOOP_INDEX, FRAME_LOOP_UID = 1, 637
g._run.__defaults__ = (6.0, 120.0)
PASS = []


def check(name, ok, detail=""):
    PASS.append((name, bool(ok)))
    print(f"   {'PASS' if ok else 'FAIL'} {name} {detail}", flush=True)


def handles():
    r = subprocess.run(["powershell", "-NoProfile", "-Command",
                        "(Get-Process LabVIEW -ErrorAction SilentlyContinue | Select-Object -First 1).HandleCount"],
                       capture_output=True, text=True)
    return int(r.stdout.strip() or 0)


def main():
    g._lv = None
    lc = g.loop_cast(MAIN, FRAME_LOOP_INDEX, "WhileLoop")
    check("T0 frame loop uid", lc["loop_uid"] == FRAME_LOOP_UID, str(lc["loop_uid"]))
    uids = lc["shift_reg_uids"]
    print(f"frame loop shift registers: {len(uids)} {uids}", flush=True)
    rows = []; errs = 0; t0 = time.time()
    for k in range(len(uids)):
        r = g.shift_reg(MAIN, FRAME_LOOP_INDEX, k, "WhileLoop")
        rows.append(r); errs += bool(r["errors"])
        print(f"   reg {k:2d} uid {r['uid']:6d} {r['class']:20s} OUT {r['out']['name']!r:30s} src={r['out']['is_source']} wire {r['out']['wire']:6d} | "
              f"IN {[(t['name'], t['is_source'], t['wire']) for t in r['inside']]} {r['errors'] or ''}", flush=True)
    print(f"   {time.time() - t0:.1f} s for {len(uids)} registers", flush=True)
    check("T1 no errors", errs == 0, str(errs))
    check("T1 UID column == loop_cast order", [r["uid"] for r in rows] == uids)
    classes = sorted({r["class"] for r in rows})
    print(f"   classes seen: {classes}", flush=True)
    check("T2 all LeftShiftRegister (peer inference; a miss is recorded)", classes == ["LeftShiftRegister"], str(classes))
    check("T3 one inside terminal each", all(len(r["inside"]) == 1 for r in rows), str([len(r["inside"]) for r in rows]))
    check("T3 inside Is Source? TRUE", all(t["is_source"] for r in rows for t in r["inside"]))
    check("T3 outside Is Source? FALSE", all(not r["out"]["is_source"] for r in rows))
    n_init = sum(1 for r in rows if r["out"]["wire"])
    print(f"   initialised registers (outside wired): {n_init}/{len(rows)}", flush=True)
    json.dump({"vi": MAIN, "loop_uid": FRAME_LOOP_UID, "registers": rows},
              open(os.path.join(HERE, "main_vi_shiftregs.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    for _ in range(3):
        g.shift_reg(MAIN, FRAME_LOOP_INDEX, 0, "WhileLoop")
    h0 = handles()
    for _ in range(20):
        g.shift_reg(MAIN, FRAME_LOOP_INDEX, 0, "WhileLoop")
    h1 = handles(); time.sleep(20); h2 = handles()
    check("T4 handles flat (+-100 post-idle)", abs(h2 - h0) <= 100, f"{h0} -> {h1} -> idle {h2}")
    n_ok = sum(1 for _n, ok in PASS if ok)
    print(f"\nSUMMARY {n_ok}/{len(PASS)} PASS", flush=True)
    for n, ok in PASS:
        print(f"   {'PASS' if ok else 'FAIL'} {n}", flush=True)
    return 0 if n_ok == len(PASS) else 1


if __name__ == "__main__":
    sys.exit(main())
