"""test_opwhileloop.py - FUNCTIONAL test of OpWhileLoop_v0 (gscript.while_loop) on a scratch copy of HARNESS_copyloop
(runnable; controls 'Image Name', 'Image Name 2', 'File Path'; one For loop).
  T1 while_loop(scratch, pos) with no tunnels: WhileLoop 0->1, ExecState 0 (conditional terminal unwired - expected),
     the new loop node's Terminals[] printed (is the conditional terminal listed? name?).
  T2 while_loop(scratch, pos2, tunnels=['File Path'], indexing=[False]): LoopTunnel +1 whose outer wire sits on the
     'File Path' control's terminal (panel_wiring) - the by-name tunnel the For op could never make.
  T3 no junk Invoke left by the op (uids before/after).
Scratch deleted; nothing saved.
  py tools/bgrun.py --max-min 8 --log tools/bench/test_opwhileloop.log -- py -u tools/bench/test_opwhileloop.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "HARNESS_copyloop.vi")
S = os.path.join(g.CLAUDEDEV, f"SCRATCH_whileloop_{os.getpid()}.vi")
g._run.__defaults__ = (6.0, 120.0)
PASS = []


def check(name, ok, detail=""):
    PASS.append((name, bool(ok)))
    print(f"   {'PASS' if ok else 'FAIL'} {name} {detail}", flush=True)


def main():
    g._lv = None
    shutil.copyfile(SRC, S); time.sleep(0.3); g.report_all(S, "SubVI"); g.open_panel(S); time.sleep(0.8)
    try:
        inv0 = g.uids(S, "Invoke"); wl0 = len(g.report_all(S, "WhileLoop")); tun0 = {o["uid"] for o in g.report_all(S, "LoopTunnel")}
        print(f"start: WhileLoop {wl0}, ExecState {g.exec_state(S)}", flush=True)
        dt = g.while_loop(S, (200, 1400))
        wl1 = g.report_all(S, "WhileLoop"); es1 = g.exec_state(S)
        print(f"T1: while_loop returned in {dt:.2f} s; WhileLoop {len(wl1)}; ExecState {es1}", flush=True)
        check("T1 WhileLoop +1", len(wl1) == wl0 + 1)
        check("T1 ExecState 0 (conditional terminal unwired)", es1 == 0)
        loop_uids = {o["uid"] for o in wl1}
        for cand in range(40):
            nu, rows = g.node_terms_uid(S, 0, cand)
            if not nu:
                break
            if nu in loop_uids:
                print(f"   loop node uid {nu} Nodes[] {cand} terminals: {[(r['i'], r['name'], r['is_source'], r['wire']) for r in rows]}", flush=True)
        g.while_loop(S, (200, 1900), tunnels=["File Path"], indexing=[False])
        new_t = [o for o in g.report_all(S, "LoopTunnel") if o["uid"] not in tun0]
        fp = next((r for r in g.panel_wiring(S) if r["label"] == "File Path"), None)
        print(f"T2: new LoopTunnels {[(o['i'], o['uid']) for o in new_t]}; File Path control wire {fp['wire'] if fp else None}", flush=True)
        outs = [g.tunnels(S, o["i"]) for o in new_t]
        for t in outs:
            print(f"   tunnel {t['index']}: mode {t['index_mode']} outer {t['out_name']!r} src={t['out_is_source']} wire {t['out_wire']}", flush=True)
        check("T2 exactly one new tunnel", len(new_t) == 1, str(len(new_t)))
        check("T2 tunnel outer wire == File Path terminal wire", bool(new_t) and fp and fp["wire"] and outs[0]["out_wire"] == fp["wire"], f"{outs[0]['out_wire'] if outs else None} vs {fp['wire'] if fp else None}")
        junk = [u for u in g.uids(S, "Invoke") if u not in inv0]
        check("T3 no junk Invoke", not junk, str(junk))
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
