"""test_opexitwhile.py - FUNCTIONAL test of OpExitWhile_v0 (gscript.exit_while): a scripted While loop made RUNNABLE
and STOPPABLE by a control, deterministically (no manual Stop).
  Scratch = copy of HARNESS_copyloop (runnable). A Boolean control is brought in with copy_into from OpForLoop_v0
  ('Shift Registers?' - the label is irrelevant, it is the stop button). Then:
  T1 while_loop(scratch) -> WhileLoop +1, ExecState 0; the new body diagram found by UID.
  T2 exit_while(scratch, 'Shift Registers?', body) -> ExecState 1 (conditional terminal wired from the control).
  T3 run the scratch over COM with the control TRUE: returns (the loop iterates once and stops) - a run that does not
     return within the deadline = FAIL (the bgrun cap protects the session).
  T4 no junk Invoke; scratch deleted.
  py tools/bgrun.py --max-min 8 --log tools/bench/test_opexitwhile.log -- py -u tools/bench/test_opexitwhile.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "HARNESS_copyloop.vi")
S = os.path.join(g.CLAUDEDEV, f"SCRATCH_exitwhile_{os.getpid()}.vi")
DONOR = g.OP_FORLOOP
STOP = "Shift Registers?"
g._run.__defaults__ = (6.0, 60.0)
PASS = []


def check(name, ok, detail=""):
    PASS.append((name, bool(ok)))
    print(f"   {'PASS' if ok else 'FAIL'} {name} {detail}", flush=True)


def main():
    g._lv = None
    shutil.copyfile(SRC, S); time.sleep(0.3)
    try:
        g.copy_into(DONOR, STOP, S)                       # file-level: a Boolean control arrives on the scratch panel
        g.report_all(S, "SubVI"); g.open_panel(S); time.sleep(0.8)
        inv0 = g.uids(S, "Invoke")
        ctl = [l for _i, l, ind in g.fp_labels(S) if l == STOP and not ind]
        check("T0 stop control present", bool(ctl))
        dia0 = {d["uid"] for d in g.report_all(S, "Diagram")}; wl0 = len(g.report_all(S, "WhileLoop"))
        g.while_loop(S, (200, 1400))
        es1 = g.exec_state(S)
        new_d = [(i, d) for i, d in enumerate(g.report_all(S, "Diagram")) if d["uid"] not in dia0]
        print(f"T1: WhileLoop {len(g.report_all(S, 'WhileLoop'))} (was {wl0}), ExecState {es1}, new diagram {[(i, d['uid'], d.get('owner')) for i, d in new_d]}", flush=True)
        check("T1 loop created, broken", len(g.report_all(S, "WhileLoop")) == wl0 + 1 and es1 == 0 and len(new_d) == 1)
        body = new_d[0][0]
        vi = g.op(S); vi.SetControlValue(STOP, True)
        dt = g.exit_while(S, STOP, body)
        es2 = g.exec_state(S)
        print(f"T2: exit_while {dt:.2f} s -> ExecState {es2}", flush=True)
        check("T2 ExecState 1 after the stop wire", es2 == 1)
        if es2 == 1:
            vi.SetControlValue(STOP, True); vi.SetControlValue("Image Name", "ewA"); vi.SetControlValue("Image Name 2", "ewB")
            t0 = time.time()
            try:
                g._run(vi); ok = True
            except RuntimeError as e:
                ok = False; print(f"   run: {str(e)[:120]}", flush=True)
            print(f"T3: run returned {ok} in {time.time() - t0:.2f} s", flush=True)
            check("T3 run returns with stop TRUE", ok)
        junk = [u for u in g.uids(S, "Invoke") if u not in inv0]
        check("T4 no junk Invoke", not junk, str(junk))
    finally:
        try:
            g.close_panel(S)
        except Exception:
            pass
        os.remove(S)
    n_ok = sum(1 for _n, ok in PASS if ok)
    print(f"\nSUMMARY {n_ok}/{len(PASS)} PASS", flush=True)
    for n, ok in PASS:
        print(f"   {'PASS' if ok else 'FAIL'} {n}", flush=True)
    return 0 if n_ok == len(PASS) else 1


if __name__ == "__main__":
    sys.exit(main())
