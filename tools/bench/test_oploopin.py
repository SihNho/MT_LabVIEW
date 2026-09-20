"""test_oploopin.py - FUNCTIONAL test of the diagram-indexed loop creators (gscript.loop_in) = the nesting stage 2 needs.
Scratch = copy of HARNESS_copyloop (top level: IMAQ Create/ReadFile/Create/Copy/GetImageSize; a For loop N = 1024
with an inner IMAQ Copy in its body).
  T1 loop_in('for', body, ...) with inputs from the inner IMAQ Copy's outputs ['Image Dst Out'] (non-indexed):
     ForLoop +1 whose body diagram is NEW and whose owner chain sits inside the outer loop's body (diagram census by UID);
     exactly one new LoopTunnel on the NEW loop, outer wire from IMAQ Copy 'Image Dst Out' (census: wire on both sides).
     ExecState 0 expected (nested For with no N and no indexed input) - a structural test; the kernel loop will have
     indexed array inputs.
  T2 loop_in('while', body, ...) with no inputs: WhileLoop +1 inside the outer body (owner census).
  T3 the peer's decisive routing test: wire a TOP-LEVEL control ('File Path') into the nested For loop's body
     (drop IMAQ ReadFile inside the nested For body; wire_control(['File Path'] -> its 'File Path')): census exactly
     ONE new LoopTunnel on the outer loop and ONE on the nested loop (two borders), the inner node's terminal wired.
  T4 no junk Invoke. Scratch deleted.
  py tools/bgrun.py --max-min 10 --log tools/bench/test_oploopin.log -- py -u tools/bench/test_oploopin.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "HARNESS_copyloop.vi")
S = os.path.join(g.CLAUDEDEV, f"SCRATCH_loopin_{os.getpid()}.vi")
RF = os.path.join(r"C:\Program Files\NI\LVAddons\nivisioncommon\1\vi.lib\vision", "Files.llb", "IMAQ ReadFile")
g._run.__defaults__ = (6.0, 120.0)
PASS = []


def check(name, ok, detail=""):
    PASS.append((name, bool(ok)))
    print(f"   {'PASS' if ok else 'FAIL'} {name} {detail}", flush=True)


def terms(target, diagram, uid):
    for cand in range(60):
        nu, rows = g.node_terms_uid(target, diagram, cand)
        if not nu:
            return None
        if nu == uid:
            return [(r["i"], r["name"], r["is_source"], r["wire"]) for r in rows]
    return None


def main():
    g._lv = None
    shutil.copyfile(SRC, S); time.sleep(0.3); g.report_all(S, "SubVI"); g.open_panel(S); time.sleep(0.8)
    try:
        inv0 = g.uids(S, "Invoke")
        dias = g.report_all(S, "Diagram")
        body = next(i for i, d in enumerate(dias) if "For" in str(d.get("owner"))); body_uid = dias[body]["uid"]
        labels_b = {r["uid"]: r["label"] for r in g.node_labels(S, body)}
        u_copy = next(u for u, l in labels_b.items() if l == "IMAQ Copy")
        i_copy = [o["uid"] for o in g.report_all(S, "SubVI")].index(u_copy)
        print(f"outer body diagram {body} (uid {body_uid}); inner IMAQ Copy uid {u_copy} SubVI index {i_copy}; ExecState {g.exec_state(S)}", flush=True)
        dia0 = {d["uid"] for d in dias}; tun0 = {o["uid"] for o in g.report_all(S, "LoopTunnel")}; fl0 = {o["uid"] for o in g.report_all(S, "ForLoop")}
        u_for = g.loop_in("for", S, body, (300, 300), "SubVI", i_copy, ["Image Dst Out"], [False], 0)
        new_d = [(i, d) for i, d in enumerate(g.report_all(S, "Diagram")) if d["uid"] not in dia0]
        new_t = [o for o in g.report_all(S, "LoopTunnel") if o["uid"] not in tun0]
        print(f"T1: new ForLoop {u_for}; new diagrams {[(i, d['uid'], d.get('owner')) for i, d in new_d]}; new tunnels {[(o['i'], o['uid'], o.get('owner')) for o in new_t]}; ExecState {g.exec_state(S)}", flush=True)
        check("T1 one new ForLoop, one new diagram owned by ForLoop", isinstance(u_for, int) and len(new_d) == 1 and "For" in str(new_d[0][1].get("owner")))
        # is the new loop inside the outer body? its uid must appear among the outer body's nodes
        in_outer = u_for in [r["uid"] for r in g.node_labels(S, next(i for i, d in enumerate(g.report_all(S, "Diagram")) if d["uid"] == body_uid))]
        check("T1 new loop is a node of the OUTER body", in_outer)
        tinfo = [g.tunnels(S, o["i"]) for o in new_t]
        for t in tinfo:
            print(f"   tunnel {t['index']}: outer {t['out_name']!r} wire {t['out_wire']} src={t['out_is_source']} inner {t['in_names']} {t['in_wires']} mode {t['index_mode']}", flush=True)
        w_dst = next(w for i, n, s, w in terms(S, next(i for i, d in enumerate(g.report_all(S, "Diagram")) if d["uid"] == body_uid), u_copy) if n == "Image Dst Out")
        check("T1 one new tunnel, outer wire == IMAQ Copy 'Image Dst Out'", len(new_t) == 1 and tinfo and tinfo[0]["out_wire"] == w_dst, f"{[t['out_wire'] for t in tinfo]} vs {w_dst}")
        nested_uid = new_d[0][1]["uid"] if new_d else None

        dia1 = {d["uid"] for d in g.report_all(S, "Diagram")}; wl0 = {o["uid"] for o in g.report_all(S, "WhileLoop")}
        body_now = next(i for i, d in enumerate(g.report_all(S, "Diagram")) if d["uid"] == body_uid)
        u_wh = g.loop_in("while", S, body_now, (300, 900))
        new_d2 = [(i, d) for i, d in enumerate(g.report_all(S, "Diagram")) if d["uid"] not in dia1]
        in_outer2 = u_wh in [r["uid"] for r in g.node_labels(S, next(i for i, d in enumerate(g.report_all(S, "Diagram")) if d["uid"] == body_uid))]
        print(f"T2: new WhileLoop {u_wh}; new diagrams {[(i, d['uid'], d.get('owner')) for i, d in new_d2]}; inside outer body {in_outer2}", flush=True)
        check("T2 nested While loop inside the outer body", isinstance(u_wh, int) and len(new_d2) == 1 and in_outer2)

        # T3 routing across two borders
        nested_i = next(i for i, d in enumerate(g.report_all(S, "Diagram")) if d["uid"] == nested_uid)
        sub0 = g.uids(S, "SubVI"); tun1 = {o["uid"] for o in g.report_all(S, "LoopTunnel")}
        g.drop_subvi(S, RF, nested_i, (400, 400))
        u_rf = [u for u in g.uids(S, "SubVI") if u not in sub0][0]
        junk = [u for u in g.uids(S, "Invoke") if u not in inv0]
        if junk:
            order = [o["uid"] for o in g.report_all(S, "Invoke")]
            for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(S, "Invoke", i, verify=False)
            g.remove_bad_wires_scripted(S)
        i_rf = [o["uid"] for o in g.report_all(S, "SubVI")].index(u_rf)
        try:
            g.wire_control(S, ["File Path"], "SubVI", i_rf, ["File Path"], branch=True)
        except Exception as e:
            print(f"   wire_control raised: {str(e)[:160]}", flush=True)
        nested_i = next(i for i, d in enumerate(g.report_all(S, "Diagram")) if d["uid"] == nested_uid)
        rf_terms = terms(S, nested_i, u_rf)
        w_fp = next((w for i, n, s, w in rf_terms if n == "File Path"), None) if rf_terms else None
        new_t3 = [o for o in g.report_all(S, "LoopTunnel") if o["uid"] not in tun1]
        owners = [o.get("owner") for o in new_t3]
        print(f"T3: ReadFile 'File Path' wire {w_fp}; new tunnels {[(o['i'], o['uid'], o.get('owner')) for o in new_t3]}", flush=True)
        for o in new_t3:
            t = g.tunnels(S, o["i"]); print(f"   tunnel {t['index']}: outer {t['out_name']!r} {t['out_wire']} -> inner {t['in_wires']}", flush=True)
        check("T3 control wired through two borders: 2 new tunnels, inner terminal wired", len(new_t3) == 2 and bool(w_fp), f"{len(new_t3)} tunnels, wire {w_fp}")
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
