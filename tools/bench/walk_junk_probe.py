"""walk_junk_probe.py - when does a net_map walk drop junk Invokes on its target? (anomaly discriminator, H5)

Observed 2026-09-14: 78-130 junk per walk all morning, then 0 on every walk in test_opnodeterms.py and
globals_direction_main.py (12:1x-12:2x), then 78 again in global_read_control.py (12:2x) - no restart in between.
The two zero-junk scripts never called open_panel on their targets (loaded by reference only); every non-zero walk
ran on an open_panel'ed target. HYPOTHESIS H5: the creator's junk drop is an EDIT, and "a target loaded only via
GetVIReference declines edits silently" (docs/NAMES.md, measured 2026-08-28) - so the junk lands only on an
open (editable) target. Same scratch, same process, same op:
    phase A  fresh copy, reference only       -> predict 0 junk
    phase B  open_panel(scratch), walk again  -> predict ~78 junk
Prints the donor's md5 too. Scratch deleted.
  py tools/bgrun.py --max-min 6 --log tools/bench/walk_junk_probe.log -- py -u tools/bench/walk_junk_probe.py
"""
import hashlib
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpFPLabels_v0.vi")
S = os.path.join(g.CLAUDEDEV, f"SCRATCH_walkjunk_{os.getpid()}.vi")
g._run.__defaults__ = (6.0, 120.0)


def main():
    g._lv = None
    print("OpNetInfo_v1.vi md5:", hashlib.md5(open(os.path.join(g.CLAUDEDEV, "OpNetInfo_v1.vi"), "rb").read()).hexdigest(), flush=True)
    shutil.copyfile(SRC, S)
    print("phase A: reference only (no open_panel)", flush=True)
    es0 = g.exec_state(S)
    nodes, _ = g.net_map(S, 0, max_nodes=40, max_terms=24)
    print(f"   walked {len(nodes)} nodes; ExecState {es0} -> {g.exec_state(S)}", flush=True)
    print("phase B: open_panel, then walk", flush=True)
    g.open_panel(S)
    time.sleep(0.8)
    es1 = g.exec_state(S)
    nodes, _ = g.net_map(S, 0, max_nodes=40, max_terms=24)
    print(f"   walked {len(nodes)} nodes; ExecState {es1} -> {g.exec_state(S)}", flush=True)
    try:
        g.close_panel(S); time.sleep(0.3); os.remove(S); print("scratch deleted", flush=True)
    except Exception as e:
        print("cleanup:", str(e)[:80], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
