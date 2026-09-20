"""read_opbuildpn_panel.py - does the keystone property-node builder expose the creator's outputs at all?

Peer verdict (archive/peer/2026-09-14-castfree-reader-nondeterministic.md): "attached or not" must be decided
through the CREATOR'S OWN returned reference and error wire, in the same dataflow - not by re-finding the node
by UID afterwards. A property ID the class does not support raises error 1077 from Set Properties[]; if the op
sinks that error and discards the returned PropertyItem[], every unsupported ID looks like a silent empty node,
which is exactly what has been observed for 6375802, 6332006 and, on 2026-09-12, 633200D.

So before changing anything: what does OpBuildPN_v0's front panel actually carry? If an `error out` indicator
exists, `build_property` may merely be failing to read it. If nothing exists, the op needs its creator's
`error out` and `Outputs`/PropertyItem count brought to the panel - a keystone change to be planned, not
improvised.

READ-ONLY on a FILE COPY of the op (an op is a running VI; pointing tooling at the live one raises 6500).
  py tools/bgrun.py --max-min 6 --log tools/bench/read_opbuildpn_panel.log -- py -u tools/bench/read_opbuildpn_panel.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpBuildPN_v0.vi")
COPY = os.path.join(g.CLAUDEDEV, "SCRATCH_buildpn_panel.vi")
g._run.__defaults__ = (6.0, 120.0)


def main():
    g._lv = None
    try:
        g.close_panel(COPY)
        time.sleep(0.3)
    except Exception:
        pass
    if os.path.exists(COPY):
        try:
            os.remove(COPY)
        except OSError:
            pass
    shutil.copyfile(SRC, COPY)
    g.open_panel(COPY)
    time.sleep(0.9)
    print(f"OpBuildPN_v0 (copy) ExecState {g.exec_state(COPY)}", flush=True)
    rows = g.fp_labels(COPY, max_n=40)
    ref = g.lv().GetVIReference(COPY, "", False, 0)
    for i, lab, ind in rows:
        v = ""
        try:
            v = repr(ref.GetControlValue(lab))[:70]
        except Exception as e:
            v = f"<unreadable {str(e)[:40]}>"
        print(f"   {i:2d} {'IND' if ind else 'CTL'} {lab!r:34} = {v}", flush=True)
    print("\n--- top-level diagram: creator subVI terminals and what they are wired to ---", flush=True)
    nodes, wires = g.net_map(COPY, 0, max_nodes=40, max_terms=30)
    for _i, (uid, _l, terms) in sorted(nodes.items()):
        named = [(t, w) for _ti, t, w in terms if t]
        if any(t in ("Outputs", "Properties", "Diagram in", "error out") for t, _w in named):
            print(f"   uid {uid}: {named}", flush=True)
    try:
        g.close_panel(COPY)
        time.sleep(0.3)
        os.remove(COPY)
        print("scratch copy deleted", flush=True)
    except Exception as e:
        print("cleanup:", str(e)[:80], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
