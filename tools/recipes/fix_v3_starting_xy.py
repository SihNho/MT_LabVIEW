"""fix_v3_starting_xy.py - wire Decimate outputs 1/2 into the P=4 loop's kernel 'starting x 1'/'starting y 1' on a COPY of
PARALLEL_kernel_v3 (spec §32), flip the two new tunnels to auto-indexing, verify, save as PARALLEL_kernel_v3fix.vi,
then (with --swap) back up PARALLEL_kernel_v3.vi and put the fixed VI in its place for the harness.

OpConnect2/OpNetInfo carry an un-deletable erdosmiller creator that drops one junk Invoke node on the TARGET diagram
per run (spec §33); every use is followed by deleting the Invokes that appeared (new_since) + Remove Bad Wires.

  py tools/bgrun.py --max-min 12 --log tools/bench/fixture_probe.log -- py -u tools/recipes/fix_v3_starting_xy.py [--swap]
"""
import os, sys, time, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
V3 = os.path.join(g.CLAUDEDEV, "PARALLEL_kernel_v3.vi"); FIX = os.path.join(g.CLAUDEDEV, "PARALLEL_kernel_v3fix.vi")


def purge_junk(target, before):
    """delete every Invoke that appeared since `before` (the creators' junk), then Remove Bad Wires."""
    junk = g.new_since(target, "Invoke", before)
    for o in junk:
        ids = [x["uid"] for x in g.report(target, "Invoke")]
        if o["uid"] in ids:
            g.delete_object(target, "Invoke", ids.index(o["uid"]))
    if junk:
        g.remove_bad_wires_scripted(target)
    return len(junk)


def main():
    if os.path.exists(FIX):
        try:
            g.close_panel(FIX)
        except Exception:
            pass
    shutil.copyfile(V3, FIX); g.report(FIX, "SubVI"); g.open_panel(FIX); time.sleep(1.0)
    inv0 = g.uids(FIX, "Invoke")
    print("copy: ExecState", g.exec_state(FIX), "wires", g.count(FIX, "Wire"), "LoopTunnels", g.count(FIX, "LoopTunnel"), "Invokes", len(inv0), flush=True)
    t0 = g.uids(FIX, "LoopTunnel")
    print("connect x: Decimate(Nodes[3]) t1 -> loop kernel t0:", g.connect2(FIX, 1, 0, 0, 3, 1), flush=True)
    print("connect y: Decimate t2 -> loop kernel t1:", g.connect2(FIX, 1, 0, 1, 3, 2), flush=True)
    print("junk Invokes purged:", purge_junk(FIX, inv0), "ExecState", g.exec_state(FIX), flush=True)
    new = g.new_since(FIX, "LoopTunnel", t0); print("new tunnels:", [(o["uid"], o["pos"]) for o in new], flush=True)
    if len(new) != 2:
        print("STOP: expected 2 new tunnels", flush=True); return 2
    tunnels = [x["uid"] for x in g.report(FIX, "LoopTunnel")]
    for o in new:
        g.set_index_mode(FIX, tunnels.index(o["uid"]), 1)
        print("   tunnel", o["uid"], "-> auto-index; ExecState", g.exec_state(FIX), flush=True)
    es = g.exec_state(FIX); print("after fix: ExecState", es, "wires", g.count(FIX, "Wire"), "Invokes", g.count(FIX, "Invoke"), flush=True)
    if es != 1:
        print("NOT SAVED (broken)", flush=True); return 3
    print("saved", g.save(FIX), flush=True)
    # verification read: kernel node 0 terminals 0..3 of diagram 1 (4 runs of OpNetInfo -> 4 junk nodes -> purged)
    inv1 = g.uids(FIX, "Invoke"); vi = g.op(g.OP_NET_INFO)
    vi.SetControlValue("vi path", FIX); vi.SetControlValue("Class Name", "Diagram"); vi.SetControlValue("index", 1)
    vi.SetControlValue("error in (no error)", (False, 0, "")); vi.SetControlValue("index 2", 0)
    for t in range(4):
        vi.SetControlValue("index 3", t); g._run(vi)
        print(f"   kernel t{t} {vi.GetControlValue('Name')!r} wire={vi.GetControlValue('UID 2')} broken={vi.GetControlValue('Is Broken?')}", flush=True)
    print("junk purged after read:", purge_junk(FIX, inv1), "ExecState", g.exec_state(FIX), flush=True)
    if g.exec_state(FIX) != 1:
        print("STOP: broken after purge; file on disk is the pre-read save", flush=True); return 4
    if "--swap" in sys.argv:
        bak = V3 + ".bak_20260907_prefix"
        if not os.path.exists(bak):
            shutil.copyfile(V3, bak)
        for p in (V3, FIX):
            try:
                g.close_panel(p)
            except Exception:
                pass
        time.sleep(1.0)
        shutil.copyfile(FIX, V3); print("swapped: PARALLEL_kernel_v3.vi <- fixed copy (backup", os.path.basename(bak) + ")", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
