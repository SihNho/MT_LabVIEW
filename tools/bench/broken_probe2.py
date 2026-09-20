import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
D = g.CLAUDEDEV
for n in ("READONLY_fourfold_COPY.vi", "PARALLEL_kernel_v3.vi", "HARNESS_compare.vi", "HARNESS_base.vi", "HARNESS_seq.vi"):
    try:
        print(n, "ExecState", g.exec_state(os.path.join(D, n)), flush=True)
    except Exception as e:
        print(n, "ERR", str(e)[:120], flush=True)
T = os.path.join(D, "HARNESS_seq.vi")
w0 = g.count(T, "Wire"); g.remove_bad_wires_scripted(T); print("HARNESS_seq after Remove Bad Wires: wires", w0, "->", g.count(T, "Wire"), "ExecState", g.exec_state(T), flush=True)
fp0 = {l for _, l, _ in g.fp_labels(T)}
new = g.create_indicator(T, 4, 4); labs = [l for _, l, _ in g.fp_labels(T) if l not in fp0]
print("re-created indicator on t4:", [o['uid'] for o in new], labs, "wires", g.count(T, "Wire"), "ExecState", g.exec_state(T), flush=True)
