"""gk_out_probe.py - the one open question in GPU_kernel_v1: how to wire a CallLibrary OUTPUT terminal to an EXISTING
front-panel indicator (the pane inherited from PARALLEL_kernel_v3).  Runs on a scratch copy of the checkpoint
GPU_kernel_v1_partial.vi (everything except the output stage), so each attempt costs seconds instead of a 12-minute rebuild.

Attempts, each on a fresh copy:
  A  temp indicator on the output terminal (creates the wire) -> wire_indicators branches the pane indicator onto it
  B  wire_indicators directly (source terminal unwired - the documented failure mode, measured here for the record)
  C  temp indicator only, then rename it to the pane label after deleting the pane indicator (pane binding is lost: this
     measures whether the VI still runs and what the pane looks like, i.e. whether a pane-rebinding op is really needed)
Prints ExecState before/after every step.
  py tools/bgrun.py --max-min 12 --log tools/bench/gk_out_probe.log -- py -u tools/bench/gk_out_probe.py [A|B|C ...]
"""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
CKPT = os.path.join(g.CLAUDEDEV, "GPU_kernel_v1_partial.vi")
PARAM, IND = "xyz_out", "x,y,z array out"
SEL = [a for a in sys.argv[1:] if a in ("A", "B", "C")] or ["A", "B", "C"]


def fresh(tag):
    T = os.path.join(g.CLAUDEDEV, f"SCRATCH_gk{tag}.vi")
    if os.path.exists(T):
        os.remove(T)
    shutil.copyfile(CKPT, T); g.report(T, "SubVI"); g.open_panel(T); time.sleep(0.8)
    print(f"\n== {tag}: copy ExecState {g.exec_state(T)} nodes {g.count(T, 'Node')} wires {g.count(T, 'Wire')}", flush=True)
    return T


def clfn_node_index(T):
    uids = [o["uid"] for o in g.report(T, "Node")]
    k = g.report(T, "CallLibrary")[0]["uid"]
    return uids.index(k) if k in uids else None


def purge(T, inv0):
    for o in g.new_since(T, "Invoke", inv0):
        ids = [x["uid"] for x in g.report(T, "Invoke")]
        if o["uid"] in ids:
            g.delete_object(T, "Invoke", ids.index(o["uid"]))


def del_terms(T, new):
    ct = [o["uid"] for o in g.report(T, "ControlTerminal")]
    for o in new:
        if o["uid"] in ct:
            g.delete_object(T, "ControlTerminal", ct.index(o["uid"])); ct = [x["uid"] for x in g.report(T, "ControlTerminal")]
    g.remove_bad_wires_scripted(T)


def find_out_terminal(T, n, inv0):
    """create_indicator on ascending terminal indices until one is labelled like PARAM and made a wire; returns (t, new, label)"""
    for t in range(0, 40):
        fp0 = {l for _, l, _ in g.fp_labels(T)}; w0 = g.count(T, "Wire")
        new = g.create_indicator(T, n, t); purge(T, inv0); labs = [l for _, l, _ in g.fp_labels(T) if l not in fp0]
        if new and labs and g.count(T, "Wire") > w0 and labs[-1].lower().startswith(PARAM):
            return t, new, labs[-1]
        if new:
            del_terms(T, new)
    return None, None, None


if not os.path.exists(CKPT):
    print("no checkpoint yet:", CKPT, flush=True); sys.exit(2)

for tag in SEL:
    T = fresh(tag); inv0 = g.uids(T, "Invoke"); n = clfn_node_index(T)
    ci = 0                                                                  # the only CallLibrary node
    if tag == "B":
        try:
            g.wire_indicators(T, ci, [PARAM], [IND], node_class="CallLibrary")
            print(f"   B: wire_indicators on an UNWIRED source -> ExecState {g.exec_state(T)}", flush=True)
        except Exception as e:
            print(f"   B: EXC {str(e)[:200]} (ExecState {g.exec_state(T)})", flush=True)
    else:
        t, new, lab = find_out_terminal(T, n, inv0)
        if t is None:
            print("   could not find the output terminal", flush=True); continue
        print(f"   temp indicator {lab!r} at t{t}: ExecState {g.exec_state(T)} wires {g.count(T, 'Wire')}", flush=True)
        if tag == "A":
            try:
                g.wire_indicators(T, ci, [PARAM], [IND], node_class="CallLibrary")
                print(f"   A: branch onto the pane indicator -> ExecState {g.exec_state(T)} wires {g.count(T, 'Wire')}", flush=True)
            except Exception as e:
                print(f"   A: EXC {str(e)[:200]} (ExecState {g.exec_state(T)})", flush=True)
            del_terms(T, new)
            print(f"   A: after deleting the temp indicator -> ExecState {g.exec_state(T)} wires {g.count(T, 'Wire')}", flush=True)
        else:                                                               # C: keep the temp indicator, drop the pane one
            fps = g.fp_labels(T); idx = next((i for i, l, ind in fps if l == IND), None)
            print(f"   C: pane indicator {IND!r} is fp index {idx}", flush=True)
            try:
                g.delete_by_label(T, IND, allow_broken=True)
                print(f"   C: pane indicator deleted -> ExecState {g.exec_state(T)}", flush=True)
            except Exception as e:
                print(f"   C: delete EXC {str(e)[:160]}", flush=True)
            try:
                g.set_label(T, lab, IND) if hasattr(g, "set_label") else print("   C: no set_label helper", flush=True)
            except Exception as e:
                print(f"   C: rename EXC {str(e)[:160]}", flush=True)
            print("   C: fp now", [l for _, l, _ in g.fp_labels(T)][:16], flush=True)
    print(f"   {tag} final ExecState {g.exec_state(T)}", flush=True)
    try:
        g.close_panel(T); os.remove(T)
    except Exception as e:
        print("   cleanup:", str(e)[:80], flush=True)
