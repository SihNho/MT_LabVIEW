"""test_oploopcast.py - FUNCTIONAL acceptance of OpLoopCast_v0 (gscript.loop_cast) = the GUI-free cast seed.

Prediction contract (peer gate, archive/peer/2026-09-14-loopcast-typed-terminal-seed-plan.md):
  T0 the saved op reopens runnable (ExecState 1 after a fresh reference).
  T1 HARNESS_copyloop.vi, ForLoop index 0: loop_uid == 239 (build log), n_wire_uid == 346 (the N wire measured when it
     was built), shift_reg_uids == [] , no errors.
  T1b HARNESS_copyloopX (N from X Resolution): same wire uid 346 (same build recipe) and loop uid 239.
  T2 main VI (reference only): all 17 ForLoops (Traverse indices 0..16): loop_uid set == report_all(main,'ForLoop')
     uid set; every n_wire_uid printed; the frame loop (uid 637) reports its shift registers - PREDICTION: >= 3
     (docs/frame-loop-wire-graph.md pairs 3 carriers by name and estimates 54 half-edges).
  T3 WhileLoop class: main VI index 0..2 -> loop_uid set == report_all(main,'WhileLoop') (the seed is ForLoop-typed:
     Loop.Shift Registers[] is inherited, ForLoop.Loop Count on a WhileLoop -> LoopCountErr expected non-empty).
  T4 handle audit: 20 runs on the main VI flat within +-100 (post-idle).
Nothing saved; the main VI is opened by reference only.
  py tools/bgrun.py --max-min 20 --log tools/bench/test_oploopcast.log -- py -u tools/bench/test_oploopcast.py
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

TREE = json.load(open(os.path.join(HERE, "diagram_tree_main.json"), encoding="utf-8"))
MAIN = TREE["vi"]
H = os.path.join(g.CLAUDEDEV, "HARNESS_copyloop.vi")
HX = os.path.join(g.CLAUDEDEV, "HARNESS_copyloopX.vi")
FRAME_LOOP_UID = 637
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
    check("T0 op reopens runnable", g.exec_state(g.OP_LOOP_CAST) == 1)
    r = g.loop_cast(H, 0)
    print(f"T1 copyloop: {r}", flush=True)
    check("T1 loop uid 239", r["loop_uid"] == 239, str(r["loop_uid"]))
    check("T1 N wire uid 346", r["n_wire_uid"] == 346, str(r["n_wire_uid"]))
    check("T1 no shift registers", r["shift_reg_uids"] == [], str(r["shift_reg_uids"]))
    check("T1 no errors", not r["errors"], str(r["errors"]))
    rx = g.loop_cast(HX, 0)
    print(f"T1b copyloopX: {rx}", flush=True)
    check("T1b same uids", rx["loop_uid"] == 239 and rx["n_wire_uid"] == 346)

    loops = {o["uid"] for o in g.report_all(MAIN, "ForLoop")}
    print(f"T2 main VI: {len(loops)} ForLoops by Traverse", flush=True)
    got = set(); n_err = 0
    t0 = time.time()
    for i in range(len(loops)):
        r = g.loop_cast(MAIN, i)
        got.add(r["loop_uid"]); n_err += bool(r["errors"])
        print(f"   ForLoop[{i}] uid {r['loop_uid']:6d} N wire {r['n_wire_uid']:6d} shift regs {len(r['shift_reg_uids'])} {r['errors'] or ''}", flush=True)
    print(f"   {time.time() - t0:.1f} s for {len(loops)} loops", flush=True)
    check("T2 loop uid set == Traverse ForLoop set", got == loops, f"{len(got & loops)}/{len(loops)}")
    check("T2 no errors on ForLoops", n_err == 0, f"{n_err} loops with errors")

    # Run 1 (15:1x) predicted the frame loop among the ForLoops: it is WhileLoop uid 637 (diagram_tree_main.json),
    # and a ForLoop seed cannot cast a WhileLoop (error 1055 downstream) -> OpWhileCast_v0 (WhileLoop seed).
    wl = {o["uid"] for o in g.report_all(MAIN, "WhileLoop")}
    gotw = set(); sr_frame = None; w_err = 0
    for i in range(len(wl)):
        r = g.loop_cast(MAIN, i, class_name="WhileLoop")
        gotw.add(r["loop_uid"]); w_err += bool(r["errors"])
        print(f"   WhileLoop[{i}] uid {r['loop_uid']} shift regs {len(r['shift_reg_uids'])} {r['shift_reg_uids']} errors {r['errors']}", flush=True)
        if r["loop_uid"] == FRAME_LOOP_UID:
            sr_frame = r["shift_reg_uids"]
    check("T3 WhileLoop uid set == Traverse WhileLoop set", gotw == wl, f"{len(gotw & wl)}/{len(wl)}")
    check("T3 no errors on WhileLoops", w_err == 0, f"{w_err}")
    check("T3 frame loop (uid 637) found", sr_frame is not None)
    check("T3 frame loop shift registers >= 3", sr_frame is not None and len(sr_frame) >= 3, f"{sr_frame}")

    for _ in range(3):
        g.loop_cast(MAIN, 0)
    h0 = handles()
    for _ in range(20):
        g.loop_cast(MAIN, 0)
    h1 = handles(); time.sleep(20); h2 = handles()
    check("T4 handles flat (+-100 post-idle)", abs(h2 - h0) <= 100, f"{h0} -> {h1} -> idle {h2}")

    n_ok = sum(1 for _n, ok in PASS if ok)
    print(f"\nSUMMARY {n_ok}/{len(PASS)} PASS", flush=True)
    for n, ok in PASS:
        print(f"   {'PASS' if ok else 'FAIL'} {n}", flush=True)
    return 0 if n_ok == len(PASS) else 1


if __name__ == "__main__":
    sys.exit(main())
