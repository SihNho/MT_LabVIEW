"""build_opforloop_v1.py - OpForLoop_v1.vi = OpForLoop_v0 + the ONE wire it always lacked:
Get Controls.'Control Terminals' -> Create For Loop.'Inputs' (probe_opforloop.log: both ends wire 0, which is why
for_loop(tunnels=...) never made a tunnel - INDEX row 32; OpWhileLoop_v0 got the same wire on 2026-09-14).
Stage-2 step B (docs/stage2-assembly-step-b.md, revised route): the replay core is a FOR loop whose `Frame IDs`
array control must arrive through an AUTO-INDEXED input tunnel (which also sets N).

PREDICTION: copy ExecState 1; after the wire the creator's 'Inputs' sink and Get Controls' 'Control Terminals'
source report the SAME wire uid; ExecState 1; saved. Functional test (T): scratch copy of EMPTY_v0 with a control
brought in by copy_into (the Boolean 'Shift Registers?' from OpForLoop_v0 - any control does), for_loop(tunnels=
[that label], indexing=[True]) -> exactly one new LoopTunnel whose outer terminal carries the control terminal's
wire and whose IndexMode is 1; the loop counts as 'N from the indexed input' (no N wire). Scratch deleted.
  py tools/bgrun.py --max-min 10 --log tools/bench/build_opforloop_v1.log -- py -u tools/recipes/build_opforloop_v1.py
"""
import hashlib
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = g.OP_FORLOOP
OP = os.path.join(g.CLAUDEDEV, "OpForLoop_v1.vi")
S = os.path.join(g.CLAUDEDEV, f"SCRATCH_forv1_{os.getpid()}.vi")
CTL = "Shift Registers?"
g._run.__defaults__ = (6.0, 120.0)
PASS = []


def check(name, ok, detail=""):
    PASS.append((name, bool(ok)))
    print(f"   {'PASS' if ok else 'FAIL'} {name} {detail}", flush=True)


def walk(target, diagram=0):
    labels = {r["uid"]: r["label"] for r in g.node_labels(target, diagram)}
    out = {}
    for n in range(80):
        u, rows = g.node_terms_uid(target, diagram, n)
        if not u:
            break
        out[u] = (n, labels.get(u), rows)
    return out


def term(rows, name, source):
    return next((r for r in rows if r["name"] == name and r["is_source"] == source), None)


def build():
    if os.path.exists(OP):
        os.remove(OP)
    md5 = hashlib.md5(open(SRC, "rb").read()).hexdigest()
    shutil.copyfile(SRC, OP); time.sleep(0.3); g.open_panel(OP); time.sleep(0.8)
    print(f"copy ExecState {g.exec_state(OP)}", flush=True)
    w = walk(OP)
    gc = next(u for u, v in w.items() if v[1] == "Get Controls.vi")
    cf = next(u for u, v in w.items() if v[1] == "Create For Loop.vi")
    si = lambda u: [o["uid"] for o in g.report_all(OP, "SubVI")].index(u)
    before = (term(w[gc][2], "Control Terminals", True)["wire"], term(w[cf][2], "Inputs", False)["wire"])
    print(f"before: Control Terminals wire {before[0]}, Inputs wire {before[1]} (predict 0, 0)", flush=True)
    g.wire(OP, "SubVI", si(gc), "Control Terminals", "SubVI", si(cf), "Inputs")
    w = walk(OP)
    a = term(w[gc][2], "Control Terminals", True)["wire"]; b = term(w[cf][2], "Inputs", False)["wire"]
    es = g.exec_state(OP)
    check("B1 the wire is on both ends", a and a == b, f"{a} / {b}")
    check("B2 ExecState 1", es == 1, str(es))
    ok = a and a == b and es == 1
    if ok:
        g.set_auto_error_handling(OP, False); g.save(OP)
    try:
        g.close_panel(OP)
    except Exception:
        pass
    print(f"donor md5 unchanged: {hashlib.md5(open(SRC, 'rb').read()).hexdigest() == md5}", flush=True)
    return ok


GC = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting\Get Controls.vi"


def string_array_control(target):
    """The assembly's own trick (step B): a 1-D STRING array control from Get Controls.vi's 'Control Names' terminal
    (create_control), then the wire and the helper node are deleted. Returns the control's label. Gate: the control
    persists (panel_wiring), its terminal is unwired."""
    sub0 = g.uids(target, "SubVI"); g.drop_subvi(target, GC, 0, (200, 600))
    u_gc = [u for u in g.uids(target, "SubVI") if u not in sub0][0]
    n = rows = None
    for cand in range(40):
        nu, rr = g.node_terms_uid(target, 0, cand)
        if not nu:
            break
        if nu == u_gc:
            n, rows = cand, rr; break
    t = next(r["i"] for r in rows if r["name"] == "Control Names" and not r["is_source"])
    before = {l for _i, l, ind in g.fp_labels(target) if not ind}
    g.create_control(target, n, t)
    label = [l for _i, l, ind in g.fp_labels(target) if not ind and l not in before][-1]
    pw = {r["label"]: r for r in g.panel_wiring(target)}
    w = pw[label]["wire"]
    ws = [o["uid"] for o in g.report_all(target, "Wire")]
    g.delete_object(target, "Wire", ws.index(w), verify=False)
    g.delete_object(target, "SubVI", [o["uid"] for o in g.report_all(target, "SubVI")].index(u_gc), verify=False)
    g.remove_bad_wires_scripted(target)
    pw = {r["label"]: r for r in g.panel_wiring(target)}
    print(f"   string-array control {label!r}: uid {pw[label]['uid']} wire {pw[label]['wire']} (0 = free) ; ExecState {g.exec_state(target)}", flush=True)
    return label


def test():
    # Run 1 (23:46) used a SCALAR Boolean control and read IndexMode 0: a scalar cannot auto-index, so the library
    # made a plain tunnel (peer: archive/peer/2026-09-14-opforloop-v1-fail1-indexmode-zero.md). The discriminating
    # test is an ARRAY control - here the String[] the replay loop will actually use.
    shutil.copyfile(os.path.join(g.CLAUDEDEV, "EMPTY_v0.vi"), S); time.sleep(0.3)
    try:
        g.open_panel(S); time.sleep(0.8)
        ctl = string_array_control(S)
        pw = {r["label"]: r for r in g.panel_wiring(S)}
        check("T0 a free String[] control is on the scratch", ctl in pw and pw[ctl]["wire"] == 0)
        tun0 = {o["uid"] for o in g.report_all(S, "LoopTunnel")}
        g.OP_FORLOOP = OP                       # point the wrapper at v1 for this run
        g.for_loop(S, (300, 300), tunnels=[ctl], indexing=[True])
        new = [o for o in g.report_all(S, "LoopTunnel") if o["uid"] not in tun0]
        print(f"   new tunnels: {[(o['i'], o['uid']) for o in new]}", flush=True)
        check("T1 exactly one new tunnel", len(new) == 1)
        if new:
            t = g.tunnels(S, new[0]["i"])
            pw = {r["label"]: r for r in g.panel_wiring(S)}
            print(f"   tunnel: outer wire {t['out_wire']} mode {t['index_mode']} inner {t['in_wires']}; control wire {pw[ctl]['wire']}", flush=True)
            check("T2 outer wire == the control terminal's wire", t["out_wire"] and t["out_wire"] == pw[ctl]["wire"])
            check("T3 IndexMode 1 (auto-indexed array input)", t["index_mode"] == 1, str(t["index_mode"]))
        es = g.exec_state(S)
        check("T4 ExecState 1 (an indexed array input alone makes a legal For loop: N = array length)", es == 1, str(es))
        if es == 1:
            vi = g.op(S); vi.SetControlValue(ctl, ["a", "b", "c"])
            t0 = time.time()
            try:
                g._run(vi); ok = True
            except RuntimeError as e:
                ok = False; print(f"   run: {str(e)[:120]}", flush=True)
            check("T5 runs with 3 elements and returns", ok, f"{time.time() - t0:.2f} s")
            vi.SetControlValue(ctl, [])
            try:
                g._run(vi); ok = True
            except RuntimeError as e:
                ok = False
            check("T6 runs with an EMPTY array (zero iterations) and returns", ok)
    finally:
        try:
            g.close_panel(S)
        except Exception:
            pass
        if os.path.exists(S):
            os.remove(S)


def main():
    g._lv = None
    if build():
        test()
    n = sum(1 for _k, ok in PASS if ok)
    print(f"\nSUMMARY {n}/{len(PASS)} PASS", flush=True)
    for k, ok in PASS:
        print(f"   {'PASS' if ok else 'FAIL'} {k}", flush=True)
    return 0 if PASS and n == len(PASS) else 1


if __name__ == "__main__":
    sys.exit(main())
