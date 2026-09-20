"""test_optunnels.py - FUNCTIONAL acceptance of OpTunnels_v0 + the main-VI tunnel census that resolves the frame
loop's half-edges.

Contract:
  T1 scratch copy of OpReportAll_v0 (one For loop: 1 auto-indexed input tunnel + 4 output tunnels): the op, indexed
     0..k until TunnelUID == 0, finds exactly report_all(scratch,'LoopTunnel') tunnels; every tunnel has ONE inner
     terminal; outer wire uid is a wire of a TOP-diagram node and inner wire uid a wire of a BODY node (node_terms
     oracle); an input tunnel has outer Is Source? FALSE / inner TRUE, an output tunnel the reverse; IndexMode 1 on
     all five (the build set them).
  T2 main VI: census of ALL LoopTunnels -> tools/bench/main_vi_tunnels.json {tunnel uid: {...}}; then how many of
     the frame loop's half-edge wire uids (tools/bench/frame_loop_graph_43.json) are explained by a tunnel's inner
     or outer wire - printed, not asserted (shift registers are not LoopTunnels; those stay open).
  T3 handles over 20 runs on the main VI.
  py tools/bgrun.py --max-min 20 --log tools/bench/test_optunnels.log -- py -u tools/bench/test_optunnels.py
"""
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

OP = os.path.join(g.CLAUDEDEV, "OpTunnels_v0.vi")
MAP = json.load(open(os.path.join(HERE, "optunnels_labels.json"), encoding="utf-8"))
LAB = {v: k for k, v in MAP.items()}
TREE = json.load(open(os.path.join(HERE, "diagram_tree_main.json"), encoding="utf-8"))
MAIN = TREE["vi"]
SRC = os.path.join(g.CLAUDEDEV, "OpReportAll_v0.vi")
S = os.path.join(g.CLAUDEDEV, f"SCRATCH_test_tunnels_{os.getpid()}.vi")
for _old in [p for p in os.listdir(g.CLAUDEDEV) if p.startswith("SCRATCH_test_tunnels")]:
    try:
        os.remove(os.path.join(g.CLAUDEDEV, _old))
    except OSError:
        pass
g._run.__defaults__ = (6.0, 120.0)
RESULTS = []


def rec(name, ok, detail):
    print(f"   -> {'PASS' if ok else 'FAIL'}: {name}: {detail}", flush=True)
    RESULTS.append((name, ok, detail))


def handles():
    r = subprocess.run(["powershell", "-NoProfile", "-Command",
                        "(Get-Process LabVIEW -ErrorAction SilentlyContinue | Select-Object -First 1).HandleCount"],
                       capture_output=True, text=True)
    return int(r.stdout.strip() or 0)


def errval(vi, key):
    if key not in LAB:
        return None
    try:
        e = tuple(vi.GetControlValue(LAB[key]))
        return int(e[1]) if e[0] else 0
    except Exception:
        return None


def run_op(target, index):
    vi = g.op(OP)
    vi.SetControlValue("vi path", target)
    try:
        vi.SetControlValue("vi path 2", target)
    except Exception:
        pass
    vi.SetControlValue("Class Name", "LoopTunnel")
    vi.SetControlValue("index", index)
    t0 = time.time()
    g._run(vi)
    dt = time.time() - t0
    r = {"index": index, "uid": int(vi.GetControlValue(LAB["TunnelUID"])),
         "index_mode": int(vi.GetControlValue(LAB["IndexMode"])),
         "out_name": vi.GetControlValue(LAB["OutName"]), "out_is_source": bool(vi.GetControlValue(LAB["OutIsSource"])),
         "out_wire": int(vi.GetControlValue(LAB["OutWireUID"])),
         "out_conn_err": errval(vi, "OutConnErr"), "out_wire_err": errval(vi, "OutWireErr"),
         "in_names": list(vi.GetControlValue(LAB["InName"])),
         "in_is_source": [bool(x) for x in vi.GetControlValue(LAB["InIsSource"])],
         "in_wires": [int(x) for x in vi.GetControlValue(LAB["InWireUID"])], "seconds": round(dt, 2)}
    return r


def census(target, limit=2000):
    out = []
    for i in range(limit):
        r = run_op(target, i)
        if not r["uid"]:
            break
        out.append(r)
    return out


def main():
    g._lv = None
    shutil.copyfile(SRC, S)
    n_expect = len(g.report_all(S, "LoopTunnel"))
    tuns = census(S)
    print(f"T1 scratch: {len(tuns)} tunnels (report_all says {n_expect})", flush=True)
    for t in tuns:
        print("   ", t, flush=True)
    rec("T1 tunnel count == report_all LoopTunnel", len(tuns) == n_expect, f"{len(tuns)} vs {n_expect}")
    rec("T1 every tunnel has exactly one inner terminal", all(len(t["in_wires"]) == 1 for t in tuns), f"{[len(t['in_wires']) for t in tuns]}")
    # oracle: wires on the top diagram vs the loop body (node_terms per node)
    dias = g.report_all(S, "Diagram")
    body = next(d["i"] for d in dias if "For" in str(d["owner"]))
    top_w, body_w = set(), set()
    for di, acc in ((0, top_w), (body, body_w)):
        for n in range(60):
            uid, rows = g.node_terms_uid(S, di, n)
            if not uid:
                break
            acc |= {r["wire"] for r in rows if r["wire"]}
    rec("T1 outer wires are top-diagram wires, inner wires are body wires",
        all(t["out_wire"] in top_w for t in tuns if t["out_wire"]) and all(t["in_wires"][0] in body_w for t in tuns if t["in_wires"] and t["in_wires"][0]),
        f"outer {[t['out_wire'] for t in tuns]} in top {sorted(top_w)[:12]}...; inner {[t['in_wires'] for t in tuns]}")
    rec("T1 direction: outer and inner terminals of a tunnel are opposite (input: outer sink/inner source; output: reverse)",
        all(t["out_is_source"] != t["in_is_source"][0] for t in tuns if t["in_is_source"]),
        f"{[(t['out_is_source'], t['in_is_source']) for t in tuns]}")
    rec("T1 IndexMode 1 on all (the build set them)", all(t["index_mode"] == 1 for t in tuns), f"{[t['index_mode'] for t in tuns]}")
    n_in = sum(1 for t in tuns if not t["out_is_source"]); n_out = len(tuns) - n_in
    rec("T1 one input tunnel, four output tunnels", (n_in, n_out) == (1, 4), f"inputs {n_in}, outputs {n_out}")

    # T2 main VI census
    t0 = time.time()
    n_main = len(g.report_all(MAIN, "LoopTunnel"))
    print(f"T2 main VI: report_all says {n_main} LoopTunnels", flush=True)
    main_t = census(MAIN, limit=n_main + 5)
    print(f"   census {len(main_t)} tunnels in {time.time() - t0:.0f} s", flush=True)
    rec("T2 main census count == report_all", len(main_t) == n_main, f"{len(main_t)} vs {n_main}")
    with open(os.path.join(HERE, "main_vi_tunnels.json"), "w", encoding="utf-8") as f:
        json.dump({"vi": MAIN, "tunnels": main_t, "class": "LoopTunnel"}, f, indent=1, ensure_ascii=False)
    gpath = os.path.join(HERE, "frame_loop_graph_43.json")
    if os.path.exists(gpath):
        G = json.load(open(gpath, encoding="utf-8"))
        half = {b["wire"] for b in G["boundary"]}
        known = set()
        for t in main_t:
            if t["out_wire"]:
                known.add(t["out_wire"])
            known |= {w for w in t["in_wires"] if w}
        resolved = half & known
        rec("T2 frame-loop half-edges explained by a LoopTunnel wire (informational)", True,
            f"{len(resolved)} of {len(half)} resolved; {len(half - known)} remain (shift registers / loop terminals / other)")

    # T3 handles
    for _ in range(3):
        run_op(MAIN, 0)
    time.sleep(2); samples = [(0, handles())]; t0 = time.time()
    for k in range(1, 21):
        run_op(MAIN, 0)
        if k % 10 == 0:
            samples.append((k, handles()))
    time.sleep(5); h_idle = handles()
    rec("T3 handles over 20 runs on main VI", abs(h_idle - samples[0][1]) <= 100,
        f"samples {samples}; post-idle {h_idle} ({h_idle - samples[0][1]:+d}); {time.time() - t0:.0f} s")

    print("\n################ SUMMARY ################", flush=True)
    for name, ok, detail in RESULTS:
        print(f"  {'PASS' if ok else 'FAIL'}  {name:70} {detail[:170]}", flush=True)
    try:
        os.remove(S); print("scratch deleted", flush=True)
    except Exception as e:
        print("cleanup:", str(e)[:80], flush=True)
    return 0 if all(ok for _n, ok, _d in RESULTS) else 3


if __name__ == "__main__":
    sys.exit(main())
