"""test_count_tunnel.py - does an auto-indexed INPUT tunnel whose inner wire was DELETED still set a For loop's N,
and leave the VI runnable? (step-C recipe's 'count tunnel' trick; reviewer archive/peer/2026-09-15-stage2-queue-core-
recipe.md asked for exactly this scratch first.)
  scratch = EMPTY copy + String[] control (Get Controls trick) + For loop + StrToPath inside; wire_control(ctl ->
  StrToPath.string) -> set_index_mode(1) -> delete the INNER wire; then exit_loop(StrToPath, ['path']) as an indexed
  output (StrToPath.path is unwired-input -> default path each iteration) -> indicator; run with 0, 1, 3 elements ->
  output lengths 0, 1, 3.  PREDICT: ExecState 1; lengths match.
  py tools/bgrun.py --max-min 8 --log tools/bench/test_count_tunnel.log -- py -u tools/bench/test_count_tunnel.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))
import gscript as g  # noqa: E402
import build_track_v6_core as B  # noqa: E402

S = os.path.join(g.CLAUDEDEV, f"SCRATCH_count_{os.getpid()}.vi")
g._run.__defaults__ = (6.0, 90.0)


def main():
    g._lv = None
    shutil.copyfile(B.BASE, S); time.sleep(0.3)
    try:
        g.open_panel(S); time.sleep(0.8)
        ctl = B.string_array_control(S, "C")
        dia0 = {d["uid"] for d in g.report_all(S, "Diagram")}
        g.for_loop(S, (500, 200))
        bu = next(d["uid"] for d in g.report_all(S, "Diagram") if d["uid"] not in dia0)
        body = lambda: next(i for i, d in enumerate(g.report_all(S, "Diagram")) if d["uid"] == bu)
        u = B.drop(S, B.S_VI, body(), (60, 60))
        ti = B.tunnel_route(S, ctl, u, body(), "C")
        w = B.term(B.walk(S, body())[u][2], "string", False)["wire"]
        ws = [o["uid"] for o in g.report_all(S, "Wire")]
        g.delete_object(S, "Wire", ws.index(w), verify=False)
        t = g.tunnels(S, ti)
        B.must("C inner wire deleted, tunnel still IndexMode 1", t["index_mode"] == 1 and not any(t["in_wires"]), str(t))
        tun0 = {o["uid"] for o in g.report_all(S, "LoopTunnel")}
        g.exit_loop(S, [o["uid"] for o in g.report_all(S, "SubVI")].index(u), ["path"], body(), node_class="SubVI")
        new_t = [o for o in g.report_all(S, "LoopTunnel") if o["uid"] not in tun0]
        B.must("C output tunnel", len(new_t) == 1)
        b0 = {l for _i, l, ind in g.fp_labels(S) if ind}; g.tunnel_indicator(S, new_t[0]["i"])
        out = [l for _i, l, ind in g.fp_labels(S) if ind and l not in b0][-1]
        es = g.exec_state(S); B.must("C ExecState 1 with an unwired indexed input tunnel", es == 1, str(es))
        vi = g.op(S)
        for n in (0, 1, 3):
            vi.SetControlValue(ctl, ["x"] * n); g._run(vi)
            got = len(list(vi.GetControlValue(out)))
            B.must(f"C {n} elements -> {n} iterations", got == n, f"got {got}")
    except B.Stop as e:
        print(f"STOP at {e}", flush=True)
    finally:
        try:
            g.close_panel(S)
        except Exception:
            pass
        if os.path.exists(S):
            os.remove(S)
    n_ok = sum(1 for _n, p in B.PASS if p)
    print(f"\nSUMMARY {n_ok}/{len(B.PASS)} PASS", flush=True)
    return 0 if B.PASS and n_ok == len(B.PASS) else 1


if __name__ == "__main__":
    sys.exit(main())
