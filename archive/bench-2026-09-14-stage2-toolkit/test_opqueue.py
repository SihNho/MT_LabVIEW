"""test_opqueue.py - FUNCTIONAL test of the four queue ops (gscript.queue_node) on a scratch copy of HARNESS_copyloop
(top level: IMAQ Create/ReadFile/Create/Copy/GetImageSize; a For loop N = Y Resolution with an inner IMAQ Copy).
  T1 obtain : element data type <- GetImageSize.'Y Resolution' (I32) on diagram 0 -> an 'Obtain Queue' Function node
  T2 enqueue: inside the loop body, queue <- Obtain.'queue out'; element wired afterwards from GetImageSize.'X Resolution'
              (crosses the loop border: a tunnel) -> 1024 enqueues of 1280 per run
  T3 dequeue: top level, queue <- Obtain.'queue out'; create_indicator on 'element' and on 'timed out?'
  T4 release: queue <- Dequeue.'queue out'
  T5 ExecState 1; run once over COM: element indicator == 1280, timed out? == False
Scratch deleted; nothing saved.
  py tools/bgrun.py --max-min 10 --log tools/bench/test_opqueue.log -- py -u tools/bench/test_opqueue.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "HARNESS_copyloop.vi")
S = os.path.join(g.CLAUDEDEV, f"SCRATCH_queue_{os.getpid()}.vi")
g._run.__defaults__ = (6.0, 60.0)
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
        labels = {r["uid"]: r["label"] for r in g.node_labels(S, 0)}
        u_gis = next(u for u, l in labels.items() if l == "IMAQ GetImageSize")
        i_gis = [o["uid"] for o in g.report_all(S, "SubVI")].index(u_gis)
        body = next(i for i, d in enumerate(g.report_all(S, "Diagram")) if "For" in str(d.get("owner")))
        print(f"GetImageSize SubVI index {i_gis}; loop body diagram {body}; ExecState {g.exec_state(S)}", flush=True)

        new = g.queue_node("obtain", S, "SubVI", i_gis, "Y Resolution", 0, (330, 900))
        check("T1 obtain: one new Function node", len(new) == 1, str(new))
        u_ob = new[0]; print(f"   Obtain Queue node {u_ob}: {terms(S, 0, u_ob)}; ExecState {g.exec_state(S)}", flush=True)
        f_ob = [o["uid"] for o in g.report_all(S, "Function")].index(u_ob)

        new = g.queue_node("enqueue", S, "Function", f_ob, "queue out", body, (800, 900))
        check("T2 enqueue: one new node in the body", len(new) == 1, str(new))
        u_en = new[0]; print(f"   Enqueue node {u_en}: {terms(S, body, u_en)}", flush=True)
        f_en = [o["uid"] for o in g.report_all(S, "Function")].index(u_en)
        g.wire(S, "SubVI", i_gis, "X Resolution", "Function", f_en, "element")
        print(f"   after element wire: {terms(S, body, u_en)}; ExecState {g.exec_state(S)}", flush=True)

        new = g.queue_node("dequeue", S, "Function", f_ob, "queue out", 0, (330, 1100))
        check("T3 dequeue: one new node", len(new) == 1, str(new))
        u_de = new[0]; rows = terms(S, 0, u_de); print(f"   Dequeue node {u_de}: {rows}", flush=True)
        n_de = next(c for c in range(60) if g.node_terms_uid(S, 0, c)[0] == u_de)
        i0 = {l for _i, l, ind in g.fp_labels(S) if ind}; c0 = {l for _i, l, ind in g.fp_labels(S) if not ind}
        g.create_indicator(S, n_de, next(i for i, n, s, w in rows if n == "element"))
        g.create_indicator(S, n_de, next(i for i, n, s, w in rows if n == "timed out?"))
        # run 1 (20:55) hung: no File Path -> ReadFile error -> Y Resolution 0 -> N = 0 -> no enqueue -> Dequeue(-1)
        # waited forever. A FINITE dequeue timeout (control) makes any such failure visible instead of a hang.
        g.create_control(S, n_de, next(i for i, n, s, w in rows if n.startswith("timeout")))
        new_ind = [l for _i, l, ind in g.fp_labels(S) if ind and l not in i0]
        to_ctl = [l for _i, l, ind in g.fp_labels(S) if not ind and l not in c0]
        print(f"   indicators: {new_ind}; timeout control: {to_ctl}", flush=True)
        f_de = [o["uid"] for o in g.report_all(S, "Function")].index(u_de)
        # pre-run census (peer): the queue/element tunnels' outer and inner wires, Obtain/Dequeue/Release wires
        ob_rows = terms(S, 0, u_ob); w_qout = next(w for i, n, s, w in ob_rows if n == "queue out")
        en_rows = terms(S, body, u_en)
        print(f"   census: Obtain.queue out wire {w_qout}; Enqueue queue/element wires {[(n, w) for i, n, s, w in en_rows if n in ('queue', 'element')]}; "
              f"Dequeue.queue wire {next(w for i, n, s, w in terms(S, 0, u_de) if n == 'queue')}", flush=True)
        for o in g.report_all(S, "LoopTunnel"):
            t = g.tunnels(S, o["i"])
            print(f"   tunnel {o['i']}: outer {t['out_name']!r} wire {t['out_wire']} src={t['out_is_source']} -> inner {t['in_names']} wires {t['in_wires']}", flush=True)

        new = g.queue_node("release", S, "Function", f_de, "queue out", 0, (600, 1100))
        check("T4 release: one new node", len(new) == 1, str(new))
        junk = [u for u in g.uids(S, "Invoke") if u not in inv0]
        if junk:
            order = [o["uid"] for o in g.report_all(S, "Invoke")]
            for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(S, "Invoke", i, verify=False)
            g.remove_bad_wires_scripted(S)
        es = g.exec_state(S)
        check("T5 ExecState 1", es == 1, str(es))
        if es == 1:
            g.set_auto_error_handling(S, False)
            import glob
            sys.path.insert(0, os.path.join(os.path.dirname(HERE), "gpu")); import fixture  # noqa: E402
            frame = sorted(glob.glob(os.path.join(fixture.DATA, "img*.tif")))[0]
            vi = g.op(S); vi.SetControlValue("Image Name", "qA"); vi.SetControlValue("Image Name 2", "qB")
            vi.SetControlValue("File Path", frame)
            if to_ctl:
                vi.SetControlValue(to_ctl[0], 2000)
            t0 = time.time(); g._run(vi); dt = time.time() - t0
            vals = {l: vi.GetControlValue(l) for l in new_ind}
            print(f"   run {dt:.2f} s: {vals}", flush=True)
            el = next((v for l, v in vals.items() if "element" in l), None); to = next((v for l, v in vals.items() if "timed" in l), None)
            check("T5 dequeued element == 1280 (X Resolution)", el == 1280, str(el))
            check("T5 not timed out", to is False, str(to))
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
