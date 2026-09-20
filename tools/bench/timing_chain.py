"""timing_chain.py - (1) remove the dead four-fold For Loop (uid 248, holding the 4 old kernel instances) from a fresh copy of
PARALLEL_kernel_v3_withdead.vi -> verify ExecState 1 -> save as PARALLEL_kernel_v3clean.vi -> swap into PARALLEL_kernel_v3.vi;
(2) restart LabVIEW (drop stale in-memory copies); (3) run_timing.py.
  py tools/bgrun.py --max-min 60 --log tools/bench/timing_chain.log -- py -u tools/bench/timing_chain.py
"""
import os, shutil, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE); sys.path.insert(0, TOOLS)
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
D = g.CLAUDEDEV
V3 = os.path.join(D, "PARALLEL_kernel_v3.vi"); V3C = os.path.join(D, "PARALLEL_kernel_v3clean.vi"); V3D = os.path.join(D, "PARALLEL_kernel_v3_withdead.vi")
DEAD_LOOP_UID = 248; DEAD_CASE_UID = 107


def clean():
    if os.path.exists(V3C):
        os.remove(V3C)
    shutil.copyfile(V3D, V3C); g.report(V3C, "SubVI"); g.open_panel(V3C); time.sleep(1.0)
    loops = g.report(V3C, "ForLoop"); subs0 = g.count(V3C, "SubVI"); w0 = g.count(V3C, "Wire")
    print("loops:", [(o["uid"], tuple(o["pos"])) for o in loops], "SubVIs", subs0, "wires", w0, flush=True)
    # structure read 2026-09-08 (tools/bench/v3_structure.json): the old four-fold code = For Loop 248 (2 x 2-bead kernels
    # per 4-pack, diagram 6) + Case Structure 107 (the 0..3-bead remainder cases, diagrams 2-5, 4 kernels); their outputs
    # are dangling (the P=4 loop 3447 + Interleave feed the connector pane). Delete both; 6 SubVIs must disappear.
    for cls, uid in (("ForLoop", DEAD_LOOP_UID), ("CaseStructure", DEAD_CASE_UID)):
        ids = [o["uid"] for o in g.report(V3C, cls)]
        if uid not in ids:
            print(f"STOP: {cls} uid {uid} not found in {ids}", flush=True); return False
        g.delete_object(V3C, cls, ids.index(uid))
    g.remove_bad_wires_scripted(V3C)
    subs1 = g.count(V3C, "SubVI"); w1 = g.count(V3C, "Wire"); es = g.exec_state(V3C)
    print(f"after delete: SubVIs {subs0} -> {subs1}, wires {w0} -> {w1}, ExecState {es}", flush=True)
    if es != 1 or subs1 != subs0 - 6:
        print("STOP: unexpected result - not swapped", flush=True); return False
    g.save(V3C)
    for p in (V3C, V3):
        try:
            g.close_panel(p)
        except Exception:
            pass
    time.sleep(1.0)
    shutil.copyfile(V3C, V3); print("PARALLEL_kernel_v3.vi <- clean (4 dead kernels + loop removed)", flush=True)
    return True


def restart():
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "lv_restart.py")], timeout=400); print("lv_restart rc", r.returncode, flush=True)


def main():
    restart()                                   # the previous client was killed mid-Run: start from a fresh instance
    # v3 already cleaned + swapped (2026-09-08 00:38: 7 -> 1 SubVIs, ExecState 1); rebuild only if the clean copy is missing
    if not os.path.exists(V3C):
        g._lv = None; g._cache.clear()
        if not clean():
            return 2
    for name in ("base", "seq", "par"):
        r = subprocess.run([sys.executable, "-u", os.path.join(TOOLS, "recipes", "build_harness_variant.py", ), f"--name={name}"], timeout=900)
        print(f"build {name} rc {r.returncode}", flush=True)
        if r.returncode != 0:
            return 3
        restart()                               # each build leaves the reentrant kernels loaded; start the next from clean
    r = subprocess.run([sys.executable, "-u", os.path.join(HERE, "run_timing.py"), "--n=200"], timeout=2400); print("run_timing rc", r.returncode, flush=True)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
