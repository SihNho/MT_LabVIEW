"""case_out_probe.py - the last unknown for TRACK_kernel_v1: getting a subVI's OUTPUT out of a case frame onto the pane
indicator (an output tunnel).  The input side is settled (case_probe.log: wire_control from a top-level control to a node
inside the frame creates the tunnel, +2 wires).

Two candidate routes, each on a fresh scratch copy:
  A  wire_indicators straight from the inside node to the outside pane indicator (its documented contract wants the source
     terminal already wired, but that was measured on a flat diagram - maybe the tunnel is made for us)
  B  create_indicator on the inside node first (that makes a wire inside the frame), then wire_indicators branches the pane
     indicator onto it, then the temporary indicator is deleted - the pattern that worked for the CLFN on a flat diagram
Prints wire counts and ExecState around every step; nothing is saved.
  py tools/bgrun.py --max-min 15 --log tools/bench/case_out_probe.log -- py -u tools/bench/case_out_probe.py
"""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
SRC = os.path.join(g.CLAUDEDEV, "PARALLEL_kernel_v3.vi")
KERN = os.path.join(g.CLAUDEDEV, "PARALLEL_kernel_v3.vi")
IND = "x,y,z array out"; OUTTERM = "x,y,z array out"


def build(tag):
    T = os.path.join(g.CLAUDEDEV, f"SCRATCH_caseout{tag}.vi")
    if os.path.exists(T):
        os.remove(T)
    shutil.copyfile(SRC, T); g.report(T, "SubVI"); g.open_panel(T); time.sleep(0.8)
    while g.count(T, "Node"):
        try:
            g.delete_object(T, "Node", 0)
        except RuntimeError as e:
            if "expected 1 object gone" not in str(e):
                raise
            break
    g.remove_bad_wires_scripted(T)
    inv0 = g.uids(T, "Invoke")

    def purge():
        for o in g.new_since(T, "Invoke", inv0):
            ids = [x["uid"] for x in g.report(T, "Invoke")]
            if o["uid"] in ids:
                g.delete_object(T, "Invoke", ids.index(o["uid"]))
    # OpBuildCase_v1 (2026-09-10): selector + input tunnels by control NAME, frame names must match the 2 numeric frames
    case = g.build_case(T, (400, 300), "# of bead 4 packs", ["x,y,z array", "Image In"]); purge()
    print(f"   case {case['uid']} @ {case['pos']} | wires {g.count(T, 'Wire')} ExecState {g.exec_state(T)}", flush=True)
    g.drop_subvi(T, KERN, 1, (470, 330)); purge()
    print(f"== {tag}: case + inner subVI | SubVIs {g.count(T, 'SubVI')} diagrams {g.count(T, 'Diagram')} wires {g.count(T, 'Wire')} ExecState {g.exec_state(T)}", flush=True)
    return T, purge


# A: straight from the inside node to the outside indicator
T, purge = build("A")
w0 = g.count(T, "Wire")
try:
    g.wire_indicators(T, 0, [OUTTERM], [IND], node_class="SubVI")
    print(f"   A: wire_indicators -> wires {w0} -> {g.count(T, 'Wire')} ExecState {g.exec_state(T)}", flush=True)
except Exception as e:
    print(f"   A: EXC {str(e)[:200]} | wires {w0} -> {g.count(T, 'Wire')} ExecState {g.exec_state(T)}", flush=True)
g.remove_bad_wires_scripted(T)
print(f"   A: after remove_bad_wires wires {g.count(T, 'Wire')} ExecState {g.exec_state(T)}", flush=True)
try:
    g.close_panel(T); os.remove(T)
except Exception:
    pass

# B: temporary indicator inside the frame first, then branch the pane indicator onto that wire
T, purge = build("B")
nodes = [o["uid"] for o in g.report(T, "Node")]
n_inner = None
for cand in range(0, 6):
    fp0 = {l for _, l, _ in g.fp_labels(T)}; w0 = g.count(T, "Wire")
    new = g.create_indicator(T, cand, 0); purge()
    labs = [l for _, l, _ in g.fp_labels(T) if l not in fp0]
    if new and labs and g.count(T, "Wire") > w0:
        n_inner = cand; print(f"   B: Nodes[{cand}] terminal 0 -> temp indicator {labs[-1]!r} (wires {w0} -> {g.count(T, 'Wire')})", flush=True)
        ct = [o["uid"] for o in g.report(T, "ControlTerminal")]
        for o in new:
            if o["uid"] in ct:
                g.delete_object(T, "ControlTerminal", ct.index(o["uid"])); ct = [x["uid"] for x in g.report(T, "ControlTerminal")]
        g.remove_bad_wires_scripted(T)
        break
    if new:
        ct = [o["uid"] for o in g.report(T, "ControlTerminal")]
        for o in new:
            if o["uid"] in ct:
                g.delete_object(T, "ControlTerminal", ct.index(o["uid"])); ct = [x["uid"] for x in g.report(T, "ControlTerminal")]
        g.remove_bad_wires_scripted(T)
print("   B: inner node index =", n_inner, flush=True)
if n_inner is not None:
    fp0 = {l for _, l, _ in g.fp_labels(T)}; w0 = g.count(T, "Wire")
    new = g.create_indicator(T, n_inner, 0); purge()
    labs = [l for _, l, _ in g.fp_labels(T) if l not in fp0]
    print(f"   B: temp indicator {labs[-1] if labs else None!r} wires {w0} -> {g.count(T, 'Wire')} ExecState {g.exec_state(T)}", flush=True)
    try:
        g.wire_indicators(T, 0, [OUTTERM], [IND], node_class="SubVI")
        print(f"   B: branch pane indicator -> wires {g.count(T, 'Wire')} ExecState {g.exec_state(T)}", flush=True)
    except Exception as e:
        print(f"   B: EXC {str(e)[:200]} | ExecState {g.exec_state(T)}", flush=True)
try:
    g.close_panel(T); os.remove(T); print("scratches removed", flush=True)
except Exception as e:
    print("cleanup:", str(e)[:80], flush=True)
