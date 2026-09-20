"""probe_stale_nodes.py - what makes a freshly created node VISIBLE to the Nodes[] walker?

RAW FACT (tools/bench/probe_walk_raw.log): after two nodes are created on Traverse('Diagram')[0], the walker op
returns the same 14-entry uid sequence as before creation - 8 real donor nodes, then six uids that are the
walker's OWN objects bleeding through an out-of-range Index Array. The new uids appear nowhere, while a class
traversal sees them at once. Earlier sessions saw new nodes through the same walker only after Remove Bad Wires
or a wire connect had touched the target. Hypothesis under peer review (archive/peer/2026-09-14-stale-nodes-
snapshot.md): the walker reads a stale Nodes[] until something forces a refresh - OR the walker holds a cached
Diagram reference from an earlier run against a since-recopied file at the same path.

This probe applies candidate "commit" steps one at a time and walks after each, so the first step that makes
the new uids appear is named by measurement:

    S0  create good + questioned nodes            -> walk (expected: unseen, reproducing the raw fact)
    S1  remove_bad_wires_scripted(target)          -> walk
    S2  wire() one harmless wire on the target     -> walk    (skipped if S1 already revealed them)
    S3  close_panel + open_panel (reopen reference)-> walk
    S4  discard the walker op instance (g._lv=None; fresh op) -> walk

A control is built in: the 8 donor uids must be present in every walk (if not, the walk itself failed).
Nothing saved; scratch deleted.
  py tools/bgrun.py --max-min 12 --log tools/bench/probe_stale_nodes.log -- py -u tools/recipes/probe_stale_nodes.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpFPLabels_v0.vi")
S = os.path.join(g.CLAUDEDEV, "SCRATCH_stale_nodes.vi")
DONOR8 = {43, 308, 369, 370, 112, 113, 114, 115}
g._run.__defaults__ = (6.0, 120.0)


def walk(tag, want):
    nodes, _w = g.net_map(S, 0, max_nodes=60, max_terms=6)
    uids = {u for _k, (u, _l, _t) in nodes.items()}
    ctl = DONOR8 <= uids
    seen = sorted(u for u in want if u in uids)
    print(f"   walk after {tag:34}: {len(uids):2d} nodes, donor8 present={ctl}, new seen={seen}", flush=True)
    return ctl, seen


def main():
    g._lv = None
    try:
        g.close_panel(S)
        time.sleep(0.3)
    except Exception:
        pass
    if os.path.exists(S):
        try:
            os.remove(S)
        except OSError:
            pass
    shutil.copyfile(SRC, S)
    g.open_panel(S)
    time.sleep(0.9)
    print(f"scratch ExecState {g.exec_state(S)}", flush=True)
    walk("S-1 pristine", set())

    good = g.build_property(S, "VI Server:GObject", [("632A800", False)], (1300, 500))[-1]["uid"]
    quest = g.build_property(S, "VI Server:Control", [("6332006", False)], (1300, 620))[-1]["uid"]
    want = {good, quest}
    print(f"created good={good} questioned={quest}; report_all Property count = "
          f"{len(g.report_all(S, 'Property'))}", flush=True)
    steps = []
    ctl, seen = walk("S0 creation only", want)
    steps.append(("S0 creation only", ctl, seen))
    if not seen:
        g.remove_bad_wires_scripted(S)
        ctl, seen = walk("S1 remove_bad_wires_scripted", want)
        steps.append(("S1 remove_bad_wires", ctl, seen))
    if not seen:
        try:
            # a harmless wire: the good node's 'reference out' to the questioned node's 'reference'
            pi = [o["uid"] for o in g.report(S, "Property")]
            g.wire(S, "Property", pi.index(good), "reference out", "Property", pi.index(quest), "reference")
            ctl, seen = walk("S2 one wire()", want)
        except Exception as e:
            print(f"   S2 wire failed: {str(e)[:100]}", flush=True)
            ctl, seen = walk("S2 (wire attempt)", want)
        steps.append(("S2 wire", ctl, seen))
    if not seen:
        g.close_panel(S)
        time.sleep(0.5)
        g.open_panel(S)
        time.sleep(0.9)
        ctl, seen = walk("S3 close+open panel", want)
        steps.append(("S3 reopen", ctl, seen))
    if not seen:
        g._lv = None
        ctl, seen = walk("S4 fresh op instance", want)
        steps.append(("S4 fresh op", ctl, seen))

    print("\n################ SUMMARY ################", flush=True)
    for tag, ctl, seen in steps:
        print(f"  {tag:28} control={ctl} new nodes seen={seen}", flush=True)
    first = next((tag for tag, _c, seen in steps if seen), None)
    print("\nVERDICT:", f"new nodes first became visible at: {first}" if first else
          "new nodes NEVER became visible through Nodes[] - the walker is reading a different Diagram object "
          "or Nodes[] excludes them; do not build on the walker until this is resolved", flush=True)
    try:
        g.close_panel(S)
        time.sleep(0.3)
        os.remove(S)
        print("scratch deleted", flush=True)
    except Exception as e:
        print("cleanup:", str(e)[:80], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
