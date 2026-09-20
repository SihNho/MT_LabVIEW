"""build_rawcmd.py - RAWCMD_rotor.vi: a copy of the Autonics driver's Configure.vi (VISA Open -> VISA Write of an init
constant, top-level diagram) with the write-buffer constant's wire deleted and a STRING CONTROL created on VISA
Write.'write buffer' - so any serial command ('CLL X\r', 'PIC -10\r') can be sent through the same VISA alias.
No hardware is touched by the build. Plan review: archive/peer/2026-09-14-rotor-negative-coordinate-test-plan.md.
  py tools/bgrun.py --max-min 8 --log tools/bench/build_rawcmd.log -- py -u tools/recipes/build_rawcmd.py
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = r"C:\Program Files\National Instruments\LabVIEW 2026\instr.lib\Autonics Motor\Configure.vi"
OP = os.path.join(g.CLAUDEDEV, "RAWCMD_rotor.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "rawcmd_labels.json")
g._run.__defaults__ = (6.0, 60.0)


def main():
    g._lv = None
    if os.path.exists(OP):
        os.remove(OP)                       # never reference it over COM before writing (NAMES rule)
    shutil.copyfile(SRC, OP); time.sleep(0.3)
    n_sub = len(g.report_all(OP, "SubVI")); g.open_panel(OP); time.sleep(0.8)
    inv0 = g.uids(OP, "Invoke")
    print(f"start: ExecState {g.exec_state(OP)} (subVIs {n_sub})", flush=True)
    labels = {r["uid"]: r["label"] for r in g.node_labels(OP, 0)}
    n_w = None
    for cand in range(20):
        nu, rows = g.node_terms_uid(OP, 0, cand)
        if not nu:
            break
        print(f"   node {cand} uid {nu} {labels.get(nu)!r}: {[(r['i'], r['name'], r['is_source'], r['wire']) for r in rows]}", flush=True)
        if labels.get(nu) == "VISA Write":
            n_w = cand; t_wb = next(r for r in rows if r["name"] == "write buffer")
    if n_w is None:
        print("STOP: VISA Write not found.", flush=True); return 2
    wires = [o["uid"] for o in g.report_all(OP, "Wire")]
    if t_wb["wire"]:
        g.delete_object(OP, "Wire", wires.index(t_wb["wire"]), verify=False)
        print(f"   deleted the write-buffer constant wire {t_wb['wire']}; ExecState {g.exec_state(OP)}", flush=True)
    c0 = {l for _i, l, ind in g.fp_labels(OP) if not ind}
    r = g.create_control(OP, n_w, t_wb["i"])
    junk = [u for u in g.uids(OP, "Invoke") if u not in inv0]
    if junk:
        order = [o["uid"] for o in g.report_all(OP, "Invoke")]
        for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
            g.delete_object(OP, "Invoke", i, verify=False)
        g.remove_bad_wires_scripted(OP)
    new_c = [l for _i, l, ind in g.fp_labels(OP) if not ind and l not in c0]
    es = g.exec_state(OP)
    print(f"   create_control -> {r}; new controls {new_c}; ExecState {es}", flush=True)
    if len(new_c) != 1 or es != 1:
        print("VERDICT: BROKEN - NOT SAVING.", flush=True)
        try:
            g.close_panel(OP)
        except Exception:
            pass
        return 4
    g.set_auto_error_handling(OP, False); g.save(OP)
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump({"cmd": new_c[0]}, f, indent=2)
    try:
        g.close_panel(OP)
    except Exception:
        pass
    print(f"\nVERDICT: RAWCMD_rotor.vi built (control {new_c[0]!r}); instr.lib original untouched", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
