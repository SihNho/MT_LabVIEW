"""finish_gpu_kernel.py - finish GPU_kernel_v1.vi from the checkpoint (GPU_kernel_v1_partial.vi: every input wired, ExecState 1).
Only the three CLFN outputs remain; the terminal indices are known from the build log (xyz_out t22, idx_out t24, good_out t26),
so this takes ~1 min instead of the 15-minute full rebuild (which hit the chain's subprocess timeout on the last output).

Per output: create a temporary indicator on the terminal (that makes the wire), branch the EXISTING pane indicator onto it with
wire_indicators, delete the temporary one (the branch survives).
  py tools/bgrun.py --max-min 15 --log tools/bench/finish_gpu_kernel.log -- py -u tools/recipes/finish_gpu_kernel.py
"""
import json, os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

CKPT = os.path.join(g.CLAUDEDEV, "GPU_kernel_v1_partial.vi"); OP = os.path.join(g.CLAUDEDEV, "GPU_kernel_v1.vi")
OUT = [("xyz_out", "x,y,z array out", 22), ("idx_out", "pos in cal image out", 24), ("good_out", "Bead is good? array out", 26)]
g._run.__defaults__ = (6.0, 60.0)


def main():
    g._lv = None
    if not os.path.exists(CKPT):
        print("no checkpoint:", CKPT, flush=True); return 2
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(CKPT, OP); g.report(OP, "SubVI"); g.open_panel(OP); time.sleep(1.0)
    print("checkpoint: nodes", g.count(OP, "Node"), "wires", g.count(OP, "Wire"), "ExecState", g.exec_state(OP), flush=True)
    if g.exec_state(OP) != 1:
        print("STOP: the checkpoint itself is broken", flush=True); return 3
    inv0 = g.uids(OP, "Invoke")

    def purge():
        for o in g.new_since(OP, "Invoke", inv0):
            ids = [x["uid"] for x in g.report(OP, "Invoke")]
            if o["uid"] in ids:
                g.delete_object(OP, "Invoke", ids.index(o["uid"]))

    def del_terms(new):
        ct = [o["uid"] for o in g.report(OP, "ControlTerminal")]
        for o in new:
            if o["uid"] in ct:
                g.delete_object(OP, "ControlTerminal", ct.index(o["uid"])); ct = [x["uid"] for x in g.report(OP, "ControlTerminal")]
        g.remove_bad_wires_scripted(OP)

    # create_indicator addresses Nodes[] in CREATION order, which is NOT the reporter's traverse order (docs/NAMES.md).  The
    # diagram was built GetImagePixelPtr, GetImageSize, CLFN, so the CLFN is Nodes[2]; try that first and fall back.
    NODE_CANDIDATES = [2, 1, 0]
    node_n = [None]
    for param, ind, hint in OUT:
        done = False
        cand_n = [node_n[0]] if node_n[0] is not None else NODE_CANDIDATES
        for n in cand_n:
          for t in ([hint] + [x for x in range(0, 40) if x != hint]):      # the known index first, then a scan as a fallback
            fp0 = {l for _, l, _ in g.fp_labels(OP)}; w0 = g.count(OP, "Wire")
            new = g.create_indicator(OP, n, t); purge(); labs = [l for _, l, _ in g.fp_labels(OP) if l not in fp0]
            if not new or not labs or g.count(OP, "Wire") <= w0:
                if new:
                    del_terms(new)
                continue
            if not labs[-1].lower().startswith(param.lower()):
                del_terms(new); continue
            try:
                g.wire_indicators(OP, 0, [param], [ind], node_class="CallLibrary")   # index WITHIN the class: the only CallLibrary
                done = True
            except Exception as e:
                print(f"   {param}: wire_indicators EXC {str(e)[:180]}", flush=True)
            del_terms(new)
            print(f"   {param} (Nodes[{n}] t{t}) -> {ind!r}: {'OK' if done else 'FAILED'} | wires {g.count(OP, 'Wire')} ExecState {g.exec_state(OP)}", flush=True)
            if done:
                node_n[0] = n                                              # remember the CLFN's Nodes[] index for the other outputs
            break
          if done:
              break
        if not done:
            print(f"STOP: {param} not wired", flush=True); return 4
    purge(); g.remove_bad_wires_scripted(OP); es = g.exec_state(OP)
    print("\nassembled: nodes", g.count(OP, "Node"), "wires", g.count(OP, "Wire"), "ExecState", es, flush=True)
    if es != 1:
        print("STOP: broken - NOT saving", flush=True); return 5
    print("saved", g.save(OP), flush=True)
    fp = [(l, ind) for _, l, ind in g.fp_labels(OP)]
    json.dump({"fp": fp}, open(os.path.join(os.path.dirname(HERE), "bench", "gpu_kernel_v1_fp.json"), "w"), indent=1)
    print("front panel:", [l for l, _ in fp], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
