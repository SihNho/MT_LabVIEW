r"""census_0a_names.py - resolve the NAMES step 0a needs, before the recipe is written.

The project's own work cycle says every name is resolved at planning time and never discovered mid-run. Step 0a
run 1 broke that rule - it guessed a wiring source (`Terminal`[0], empty terminal name) and got error 1057 - and
the plan reviewer's cheapest discriminating test needs three names this session does not have:

  * the terminal names on StrToPath.vi's connector pane (the sink of the border wire);
  * a Boolean front-panel control on HARNESS_copyloop to wire into the new loop's conditional terminal;
  * what `while_loop()` actually returns, since the reviewer showed it returns elapsed run time, not a UID.

Read-only: a scratch copy is made under claudeDev with a UNIQUE name (LabVIEW caches a VI by path, so reusing one
scratch path serves the previous run's in-memory edits - that is what corrupted 0a run 2's baseline), inspected,
and deleted. No original, no hardware.
  py tools/bgrun.py --max-min 10 --log tools/bench/census_0a_names.log -- py -u tools/bench/census_0a_names.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

CLAUDEDEV = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
DONOR = os.path.join(CLAUDEDEV, "HARNESS_copyloop.vi")
DROPPEE = os.path.join(CLAUDEDEV, "StrToPath.vi")
SCRATCH = os.path.join(CLAUDEDEV, f"SCRATCH_0a_names_{int(time.time())}.vi")


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    g._lv = None
    shutil.copy2(DONOR, SCRATCH)
    print(f"scratch = {os.path.basename(SCRATCH)}", flush=True)
    try:
        print("\n=== StrToPath.vi terminals (the border wire's sink) ===", flush=True)
        for d in range(2):
            try:
                nm = g.net_map(DROPPEE, diagram_index=d, max_nodes=60, max_terms=30)
                print(f"  diagram {d}: {nm}"[:1500], flush=True)
            except Exception as e:
                print(f"  diagram {d}: {e}", flush=True)

        print("\n=== HARNESS_copyloop front-panel controls ===", flush=True)
        for cls in ("Control", "Terminal"):
            try:
                objs = g.report(SCRATCH, cls)
                for o in objs[:30]:
                    print(f"  {cls}: uid {o['uid']} class {o['class']} owner {o['owner']} pos {o['pos']}", flush=True)
            except Exception as e:
                print(f"  {cls}: {e}", flush=True)

        print("\n=== what while_loop() returns, and the UID deltas that identify the new body ===", flush=True)
        wl_before, dg_before = g.uids(SCRATCH, "WhileLoop"), g.uids(SCRATCH, "Diagram")
        ret = g.while_loop(SCRATCH, (40, 400), tunnels=["File Path"])
        wl_after, dg_after = g.uids(SCRATCH, "WhileLoop"), g.uids(SCRATCH, "Diagram")
        print(f"  while_loop() returned: {ret!r}  (type {type(ret).__name__})", flush=True)
        print(f"  WhileLoop uids {wl_before} -> {wl_after}   new: {[u for u in wl_after if u not in wl_before]}",
              flush=True)
        print(f"  Diagram uids {dg_before} -> {dg_after}   new: {[u for u in dg_after if u not in dg_before]}",
              flush=True)
        print(f"  Diagram TRAVERSE index of the new body: "
              f"{[i for i, u in enumerate(dg_after) if u not in dg_before]}", flush=True)
    finally:
        g._lv = None
        if os.path.exists(SCRATCH):
            try:
                os.remove(SCRATCH)
                print("\nscratch deleted", flush=True)
            except Exception as e:
                print(f"\nscratch NOT deleted: {e}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
