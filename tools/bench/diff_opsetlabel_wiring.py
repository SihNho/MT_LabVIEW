"""diff_opsetlabel_wiring.py - what did my deletions actually disconnect?

THE QUESTION. `OpReportNodes_v0` (built from donor `OpSetLabel_v0`) stays at ExecState 0 although every wire I
intended exists. The peer review named the most testable suspect:

    "your deletion may have removed a wire that previously satisfied a required input on 243, even if the subVI
     itself was 'untouched'. Compare node 243's terminal connectivity before and after - not just the node's
     presence."

That is a direct discriminating test and it needs no new tooling: net_map the pristine donor, net_map the broken
result, and diff every node's terminal-by-terminal wiring. Anything that was wired in the donor and is unwired
now is a candidate cause, and anything else is excluded.

It also answers a second peer point cheaply - **counts are weak evidence**. `LoopTunnel=3` says three tunnel
objects exist, not that each has a valid inner AND outer connection; NI documents that a half-connected tunnel
can break a VI while producing an *empty* Error List. A terminal-level diff at least shows which terminals lost
their wires.

READ-ONLY on the donor: it is inspected through a FILE COPY, never opened directly (an op is a running VI;
pointing tooling at a live op raises 6500 and can wedge it).

  py tools/bench/diff_opsetlabel_wiring.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

DONOR = os.path.join(g.CLAUDEDEV, "OpSetLabel_v0.vi")
DONOR_COPY = os.path.join(g.CLAUDEDEV, "SCRATCH_setlabel_pristine.vi")
BROKEN = os.path.join(g.CLAUDEDEV, "OpReportNodes_v0.vi")
g._run.__defaults__ = (6.0, 180.0)


def wiring(path, diagram):
    """{uid: {terminal_name: wire_id}} for one diagram."""
    nodes, _wires = g.net_map(path, diagram, max_nodes=40, max_terms=24)
    out = {}
    for _i, (uid, _lbl, terms) in nodes.items():
        out[uid] = {tname: w for _ti, tname, w in terms if tname}
    return out


def main():
    g._lv = None
    try:
        g.close_panel(DONOR_COPY)
        time.sleep(0.3)
    except Exception:
        pass
    if os.path.exists(DONOR_COPY):
        try:
            os.remove(DONOR_COPY)
        except OSError:
            pass
    shutil.copyfile(DONOR, DONOR_COPY)
    g.open_panel(DONOR_COPY)
    time.sleep(0.9)

    print(f"pristine donor ExecState = {g.exec_state(DONOR_COPY)}", flush=True)
    if not os.path.exists(BROKEN):
        print(f"{os.path.basename(BROKEN)} does not exist - the build refused to save it (correctly).",
              flush=True)
        print("Re-run tools/recipes/build_opreportnodes.py first if you want the after-state.", flush=True)
        before = wiring(DONOR_COPY, 0)
        print(f"\ndonor diagram 0: {len(before)} nodes", flush=True)
        for uid, terms in sorted(before.items()):
            wired = {k: v for k, v in terms.items() if v}
            print(f"   uid={uid:<6} wired: {wired}", flush=True)
        cleanup()
        return 0

    g.open_panel(BROKEN)
    time.sleep(0.9)
    print(f"built op ExecState     = {g.exec_state(BROKEN)}", flush=True)

    before = wiring(DONOR_COPY, 0)
    after = wiring(BROKEN, 0)
    print(f"\ndonor diagram 0: {len(before)} nodes   built diagram 0: {len(after)} nodes\n", flush=True)

    for uid in sorted(set(before) | set(after)):
        b, a = before.get(uid), after.get(uid)
        if b is None:
            print(f"   uid={uid:<6} ADDED", flush=True)
            continue
        if a is None:
            print(f"   uid={uid:<6} DELETED (intended)", flush=True)
            continue
        lost = [t for t, w in b.items() if w and not a.get(t)]
        gained = [t for t, w in a.items() if w and not b.get(t)]
        if lost or gained:
            print(f"   uid={uid:<6} LOST {lost}   GAINED {gained}", flush=True)
    print("\nAny terminal in LOST on a node I did not intend to touch is the prime suspect.", flush=True)
    cleanup()
    return 0


def cleanup():
    try:
        g.close_panel(DONOR_COPY)
        time.sleep(0.3)
        os.remove(DONOR_COPY)
        print("scratch copy deleted", flush=True)
    except Exception as e:
        print("cleanup:", str(e)[:100], flush=True)


if __name__ == "__main__":
    sys.exit(main())
