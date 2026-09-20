"""build_harness_copyloop2.py - HARNESS_copyloop.vi, N-source variant: the loop count comes from IMAQ GetImageSize
'Y Resolution' (1024 for the fixture) wired into the For loop's N terminal with connect_terminals (node terminal ->
node terminal, proven), because (measured, build_harness_copyloop.log) erdosmiller Create For Loop's 'Control Names'
does not wire an existing control, and build_index_array cannot place inside a subdiagram.

Base: a copy of HARNESS_copy1 (IMAQ Create A -> ReadFile -> Create B -> IMAQ Copy A->B). Steps:
  1  copy, open_panel                                                         ExecState 1
  2  drop IMAQ GetImageSize (top); wire ReadFile 'Image Out' -> its 'Image' (branch)     ExecState 1
  3  for_loop (empty);  node_terms on the loop node -> find its N terminal (name 'N'; STOP if ambiguous)
  4  connect_terminals(loop N <- GetImageSize 'Y Resolution')                 ExecState 1 (empty loop with N)
  5  drop IMAQ Copy INSIDE the body; outer Copy 'Image Dst Out' -> inner 'Image Dst'; ReadFile 'Image Out' -> inner
     'Image Src' (branch)                                                     ExecState 1
  6  auto error handling OFF; save iff every step ok -> HARNESS_copyloop.vi; then HARNESS_copyloop0.vi = a copy with
     the inner Copy deleted (the loop still runs N times empty) for the baseline
  py tools/bgrun.py --max-min 15 --log tools/bench/build_harness_copyloop2.log -- py -u tools/recipes/build_harness_copyloop2.py
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

VIS = r"C:\Program Files\NI\LVAddons\nivisioncommon\1\vi.lib\vision"
S_VI = os.path.join(VIS, "Basics.llb", "IMAQ GetImageSize")
K_VI = os.path.join(r"C:\Program Files\NI\LVAddons\nivision\1\vi.lib\vision", "Management.llb", "IMAQ Copy")
SRC = os.path.join(g.CLAUDEDEV, "HARNESS_copy1.vi")
# argv[1] = the GetImageSize output that feeds N: 'Y Resolution' (1024, default -> HARNESS_copyloop/copyloop0) or
# 'X Resolution' (1280 -> HARNESS_copyloopX/copyloopX0): a second N gives the peer's linearity check for free.
N_SRC = sys.argv[1] if len(sys.argv) > 1 else "Y Resolution"
SFX = "" if N_SRC == "Y Resolution" else "X"
OP = os.path.join(g.CLAUDEDEV, f"HARNESS_copyloop{SFX}.vi")
OP0 = os.path.join(g.CLAUDEDEV, f"HARNESS_copyloop{SFX}0.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "harness_copyloop_labels.json")
g._run.__defaults__ = (6.0, 90.0)
STEPS = []


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    t0 = time.time()
    try:
        r = fn()
        print(f"   result : {r}  ({time.time() - t0:.1f} s)", flush=True)
        STEPS.append((name, "ok"))
        return r
    except Exception as e:
        print(f"   OBSERVED: EXC {str(e)[:300]}", flush=True)
        STEPS.append((name, "exc"))
        return None


def main():
    g._lv = None
    for p in (OP, OP0):
        try:
            g.close_panel(p); time.sleep(0.2)
        except Exception:
            pass
        if os.path.exists(p):
            os.remove(p)
    shutil.copyfile(SRC, OP); g.report_all(OP, "SubVI"); g.open_panel(OP); time.sleep(1.0)
    inv0 = g.uids(OP, "Invoke")

    def purge():
        junk = [u for u in g.uids(OP, "Invoke") if u not in inv0]
        if junk:
            order = [o["uid"] for o in g.report_all(OP, "Invoke")]
            for idx in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(OP, "Invoke", idx, verify=False)
            g.remove_bad_wires_scripted(OP)

    def snap(tag=""):
        return (f"{tag} SubVI={len(g.report_all(OP, 'SubVI'))} ForLoop={len(g.report_all(OP, 'ForLoop'))} "
                f"LoopTunnel={len(g.report_all(OP, 'LoopTunnel'))} Wire={len(g.report_all(OP, 'Wire'))} ExecState={g.exec_state(OP)}")

    NODE = {}

    def scan(diagram=0):
        for cand in range(40):
            nu, rows = g.node_terms_uid(OP, diagram, cand)
            if not nu:
                break
            NODE[nu] = (cand, {r["name"]: (r["i"], r["is_source"], r["wire"]) for r in rows if r["name"]}, [(r["i"], r["name"], r["is_source"], r["wire"]) for r in rows])

    def drop(path, pos, diagram=0):
        purge(); before = g.uids(OP, "SubVI"); g.drop_subvi(OP, path, diagram, pos)
        new = [u for u in g.uids(OP, "SubVI") if u not in before]
        assert len(new) == 1, f"drop: {len(new)} new"
        scan(diagram)
        print(f"   dropped {os.path.basename(path)} uid {new[0]} diagram {diagram} Nodes[] {NODE[new[0]][0]}: {list(NODE[new[0]][1].keys())}", flush=True)
        return new[0]

    def sub_i(uid):
        return [o["uid"] for o in g.report_all(OP, "SubVI")].index(uid)

    print(snap("base:"), flush=True)
    if g.exec_state(OP) != 1:
        print("STOP: base copy not runnable.", flush=True); return 2
    scan(0)
    uR = next(u for u, (n, t, _r) in NODE.items() if "Image Out" in t and "File Path" in t)
    uK = next(u for u, (n, t, _r) in NODE.items() if "Image Dst Out" in t)
    uS = step("2a drop IMAQ GetImageSize (top)", "+1", lambda: drop(S_VI, (330, 560)))
    if not uS:
        return 3
    step("2b ReadFile 'Image Out' -> GetImageSize 'Image' (branch)", "ExecState 1",
         lambda: (g.wire(OP, "SubVI", sub_i(uR), "Image Out", "SubVI", sub_i(uS), "Image", branch=True), snap("after"))[1])
    if g.exec_state(OP) != 1:
        print("STOP: not runnable after GetImageSize.", flush=True); return 3
    step("3a empty For Loop", "ForLoop +1, ExecState 0 (no N)", lambda: (g.for_loop(OP, (700, 700)), snap("after"))[1])
    scan(0)
    loops = [u for u in {o["uid"] for o in g.report_all(OP, "ForLoop")} if u in NODE]
    if len(loops) != 1:
        print(f"STOP: loop node not found in Nodes[]: {loops}", flush=True); return 3
    uL = loops[0]; n_loop, tmap, raw = NODE[uL]
    print(f"   loop node uid {uL} Nodes[] {n_loop} terminals: {raw}", flush=True)
    # Run 1 (build_harness_copyloop2.log 14:28): Terminals[] of an empty For loop = ONE entry, name '' (no 'N'),
    # sink, unwired. Peer-reviewed hypothesis (archive/peer/2026-09-14-copyloop2-forloop-terminals-unnamed.md):
    # that single unnamed sink is the count terminal. Discriminating test: wire the I32 into it; an empty loop
    # with N wired is runnable (ExecState 1), anything else is not.
    n_term = next((ti for ti, nm, src, w in raw if nm == "N" and not src), None)
    if n_term is None:
        sinks = [(ti, nm) for ti, nm, src, w in raw if not src and not w]
        if len(sinks) == 1:
            n_term = sinks[0][0]
            print(f"   no terminal named 'N'; the single unwired sink {sinks[0]} is taken as the count terminal (test: ExecState)", flush=True)
        else:
            print(f"STOP: no terminal named 'N' and {len(sinks)} unwired sinks {sinks} - ambiguous, nothing saved.", flush=True); return 4
    y_term = NODE[uS][1][N_SRC][0]
    step(f"4 connect_terminals: loop N <- GetImageSize '{N_SRC}'", "wire +1, ExecState 1 (empty loop with N)",
         lambda: (g.connect_terminals(OP, n_loop, n_term, NODE[uS][0], y_term), snap("after"))[1])
    # peer (copyloop2-forloop-terminals-unnamed): ExecState alone is not proof - check the SAME wire sits on both
    # terminals (the loop's terminal 0 and GetImageSize 'Y Resolution') and that the VI is runnable.
    scan(0)
    w_loop = NODE[uL][2][n_term][3] if n_term < len(NODE[uL][2]) else 0
    w_src = NODE[uS][1][N_SRC][2]
    print(f"   N check: loop terminal {n_term} wire {w_loop}, '{N_SRC}' wire {w_src}, ExecState {g.exec_state(OP)}", flush=True)
    if not (w_loop and w_loop == w_src and g.exec_state(OP) == 1):
        print("STOP: N wire check failed (different/absent wire or VI broken) - nothing saved.", flush=True); return 4
    body = next(i for i, d in enumerate(g.report_all(OP, "Diagram")) if "For" in str(d.get("owner")))
    uKi = step("5a drop IMAQ Copy inside the body", "+1", lambda: drop(K_VI, (760, 760), body))
    if not uKi:
        return 3
    step("5b outer Copy 'Image Dst Out' -> inner 'Image Dst'", "tunnel +1",
         lambda: (g.wire(OP, "SubVI", sub_i(uK), "Image Dst Out", "SubVI", sub_i(uKi), "Image Dst"), snap("after"))[1])
    step("5c ReadFile 'Image Out' -> inner 'Image Src' (branch)", "tunnel +1, ExecState 1",
         lambda: (g.wire(OP, "SubVI", sub_i(uR), "Image Out", "SubVI", sub_i(uKi), "Image Src", branch=True), snap("after"))[1])
    es = g.exec_state(OP)
    if es != 1 or any(k == "exc" for _n, k in STEPS):
        print(f"\nVERDICT: BROKEN or INCOMPLETE (ExecState {es}, steps {STEPS}) - NOT SAVING.", flush=True); return 4
    g.set_auto_error_handling(OP, False); g.save(OP)
    if not SFX:
        with open(MAP_OUT, "w", encoding="utf-8") as f:
            json.dump({"labels": {"Image Name": "Image Name", "Image Name B": "Image Name 2", "File Path": "File Path"}, "N": "Y Resolution of the image (1024)"}, f, indent=2)
    # baseline copy: same loop, inner copy deleted
    shutil.copyfile(OP, OP0); g.report_all(OP0, "SubVI"); g.open_panel(OP0); time.sleep(0.8)
    ids = [o["uid"] for o in g.report_all(OP0, "SubVI")]
    g.delete_object(OP0, "SubVI", ids.index(uKi), verify=False); g.remove_bad_wires_scripted(OP0)
    es0 = g.exec_state(OP0)
    print(f"   copyloop0: SubVI={len(g.report_all(OP0, 'SubVI'))} ForLoop={len(g.report_all(OP0, 'ForLoop'))} ExecState={es0}", flush=True)
    if es0 == 1:
        g.set_auto_error_handling(OP0, False); g.save(OP0)
    for p in (OP, OP0):
        try:
            g.close_panel(p)
        except Exception:
            pass
    print(f"\nVERDICT: HARNESS_copyloop{SFX}{' and copyloop' + SFX + '0' if es0 == 1 else ' (copyloop' + SFX + '0 BROKEN)'} built (structural) - run tools/bench/run_copyloop_bench.py next", flush=True)
    return 0 if es0 == 1 else 4


if __name__ == "__main__":
    sys.exit(main())
