"""build_timing_harnesses.py - the LabVIEW-side pieces of the user's three-way comparison (sequential VI / CPU-parallel VI /
GPU), all by script (zero GUI):
  1. PARALLEL_kernel_v3clean.vi : copy of PARALLEL_kernel_v3 with the dead four-fold kernel instances (the 4 top-level
     `Track 1 of N` SubVIs outside the P=4 loop, which still EXECUTE) deleted + Remove Bad Wires; must stay ExecState 1.
     Then it REPLACES PARALLEL_kernel_v3.vi (backup PARALLEL_kernel_v3_withdead.vi) so HARNESS_* load the clean one.
  2. HARNESS_base.vi : HARNESS_compare minus both kernels   (loader + IMAQ ReadFile + windows only)   -> COM/file overhead
  3. HARNESS_seq.vi  : HARNESS_compare minus PARALLEL_kernel_v3  (the original four-fold kernel only)
  4. HARNESS_par.vi  : HARNESS_compare minus the four-fold kernel (PARALLEL_kernel_v3 = clean P=4 only)
  py tools/bgrun.py --max-min 20 --log tools/bench/build_timing.log -- py -u tools/bench/build_timing_harnesses.py
"""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
D = g.CLAUDEDEV
V3 = os.path.join(D, "PARALLEL_kernel_v3.vi"); V3C = os.path.join(D, "PARALLEL_kernel_v3clean.vi"); V3D = os.path.join(D, "PARALLEL_kernel_v3_withdead.vi")
HC = os.path.join(D, "HARNESS_compare.vi")
KERNEL = "Track 1 of N"


def fresh_copy(src, dst):
    if os.path.exists(dst):
        os.remove(dst)                      # never touch it through LabVIEW first (error 1012 lesson)
    shutil.copyfile(src, dst); g.report(dst, "SubVI"); g.open_panel(dst); time.sleep(1.0)


def delete_by_uid(target, cls, uid):
    ids = [o["uid"] for o in g.report(target, cls)]
    g.delete_object(target, cls, ids.index(uid))


def clean_v3():
    fresh_copy(V3, V3C)
    subs = g.report(V3C, "SubVI"); print("v3 SubVIs:", [(o["uid"], tuple(o["pos"]), o.get("name", "")) for o in subs], flush=True)
    loops = g.report(V3C, "ForLoop") if True else []
    print("v3 loops:", [(o["uid"], tuple(o["pos"])) for o in loops], flush=True)
    loop_x = min(o["pos"][0] for o in loops) if loops else 4000
    dead = [o for o in subs if o["pos"][0] < loop_x - 50]        # everything left of the P=4 loop = the old four-fold code
    print(f"deleting {len(dead)} dead SubVIs (x < {loop_x - 50}):", [(o['uid'], tuple(o['pos'])) for o in dead], flush=True)
    for o in dead:
        delete_by_uid(V3C, "SubVI", o["uid"])
    for cls in ("Function", "IndexArray", "Constant"):             # dead helpers left of the loop (Decimate feeds the loop: keep)
        pass
    g.remove_bad_wires_scripted(V3C)
    es = g.exec_state(V3C)
    print("v3clean: SubVIs", g.count(V3C, "SubVI"), "wires", g.count(V3C, "Wire"), "ExecState", es, flush=True)
    if es != 1:
        print("STOP: v3clean broken - not swapped", flush=True); return False
    g.save(V3C)
    for p in (V3C, V3):
        try:
            g.close_panel(p)
        except Exception:
            pass
    time.sleep(1.0)
    if not os.path.exists(V3D):
        shutil.copyfile(V3, V3D)
    shutil.copyfile(V3C, V3); print("PARALLEL_kernel_v3.vi <- clean copy (backup PARALLEL_kernel_v3_withdead.vi)", flush=True)
    return True


def harness_variant(name, keep):
    """copy HARNESS_compare, delete the kernel SubVIs not in `keep` ('v3' / 'ff'), Remove Bad Wires, save."""
    dst = os.path.join(D, f"HARNESS_{name}.vi"); fresh_copy(HC, dst)
    subs = g.report(dst, "SubVI")
    # HARNESS_compare creation order: loader (100,100), IMAQ Create (100,300), IMAQ ReadFile (300,300), windows (300,500), K3 v3 (700,150), K4 four-fold (700,550)
    k3 = [o for o in subs if o["pos"][0] >= 600 and o["pos"][1] < 400]; k4 = [o for o in subs if o["pos"][0] >= 600 and o["pos"][1] >= 400]
    assert len(k3) == 1 and len(k4) == 1, (k3, k4)
    if "v3" not in keep:
        delete_by_uid(dst, "SubVI", k3[0]["uid"])
    if "ff" not in keep:
        delete_by_uid(dst, "SubVI", k4[0]["uid"])
    g.remove_bad_wires_scripted(dst)
    es = g.exec_state(dst); print(f"{name}: SubVIs {g.count(dst, 'SubVI')} wires {g.count(dst, 'Wire')} ExecState {es}", flush=True)
    if es != 1:
        print(f"STOP: {name} broken", flush=True); return False
    g.save(dst); return True


def main():
    if not clean_v3():
        return 2
    ok = harness_variant("base", set()) and harness_variant("seq", {"ff"}) and harness_variant("par", {"v3"})
    print("ALL DONE" if ok else "FAILED", flush=True)
    return 0 if ok else 3


if __name__ == "__main__":
    sys.exit(main())
