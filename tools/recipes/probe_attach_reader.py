"""probe_attach_reader.py - make "did the property attach?" a DETERMINISTIC read before asking anything else.

Runs 1 and 2 of the cast-free ladders disagreed about the same creation (Control.Terminal 6332006): run 1's
reader found the new node with a 'Terminal' output; run 2's found nothing for its uid. My run-2 code then printed
'property terminals = []' for BOTH "uid absent from the walk" and "uid present, no property rows" - so the
verdict was void. Same trap as 2026-09-13 (a node that exists per report_all but that net_map cannot see).

This run separates the facts, per created node, and repeats the read three times with a pause:

    F1  report_all(vi, "Property") lists the uid          (object exists)
    F2  net_map(vi, 0) lists the uid                       (the Nodes[] walk sees it)
    F3  net_map terminal count and property-specific names (rows attached)

and it does this for a CONTROL that is known to attach (GObject.Position 632A800 - built dozens of times) before
the two questioned IDs, on the same scratch VI, same code path. If the control is not F1+F2+F3 on every read,
the reader is the problem and the run prints INVALID.

No wiring at all here - attach is decided on unwired nodes so nothing else can break the VI.
  py tools/bgrun.py --max-min 12 --log tools/bench/probe_attach_reader.log -- py -u tools/recipes/probe_attach_reader.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpFPLabels_v0.vi")
S = os.path.join(g.CLAUDEDEV, "SCRATCH_attach_reader.vi")
GENERIC = {"reference", "reference out", "error in (no error)", "error out", "error in"}
CASES = [
    ("CONTROL GObject.Position 632A800", "VI Server:GObject", "632A800"),
    ("Control.Terminal 6332006", "VI Server:Control", "6332006"),
    ("AbstractDiagram.SubVIs[] 6375802", "VI Server:AbstractDiagram", "6375802"),
    ("CONTROL#2 AbstractDiagram.Nodes[] 6375809 (known good ID)", "VI Server:AbstractDiagram", "6375809"),
]
g._run.__defaults__ = (6.0, 120.0)


def read_three(uid):
    f1 = uid in {o["uid"] for o in g.report_all(S, "Property")}
    nodes, _w = g.net_map(S, 0, max_nodes=80, max_terms=24)
    hit = [(u, [t for _ti, t, _w2 in terms if t]) for _i, (u, _l, terms) in nodes.items() if u == uid]
    f2 = bool(hit)
    names = hit[0][1] if hit else None
    extra = [t for t in names if t not in GENERIC] if names else None
    return f1, f2, (len(names) if names else None), extra


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
    print(f"scratch ExecState {g.exec_state(S)}\n", flush=True)

    results = []
    y = 500
    for label, cls, pid in CASES:
        print(f"== {label}", flush=True)
        new = g.build_property(S, cls, [(pid, False)], (1300, y))
        y += 120
        uid = new[-1]["uid"] if new else None
        print(f"   build_property returned uid {uid}", flush=True)
        reads = []
        for k in range(3):
            time.sleep(0.6 if k else 0.0)
            f1, f2, n, extra = read_three(uid)
            reads.append((f1, f2, n, extra))
            print(f"   read {k+1}: exists={f1} in_walk={f2} terminals={n} property_rows={extra}", flush=True)
        stable = len({(r[0], r[1], r[2], tuple(r[3] or [])) for r in reads}) == 1
        attached = all(r[1] and r[3] for r in reads)
        results.append((label, stable, attached, reads[-1]))

    print("\n################ SUMMARY ################", flush=True)
    for label, stable, attached, last in results:
        print(f"  {label:58} stable={stable} attached={attached} last={last}", flush=True)
    ctl_ok = results[0][1] and results[0][2] and results[3][1] and results[3][2]
    print("\nVERDICT:", "controls stable+attached -> the reader is trustworthy on this run; the two questioned "
          "rows above are real" if ctl_ok else
          "INVALID - a control was unstable or unattached, so nothing about the questioned IDs is concluded",
          flush=True)
    try:
        g.close_panel(S)
        time.sleep(0.3)
        os.remove(S)
        print("scratch deleted", flush=True)
    except Exception as e:
        print("cleanup:", str(e)[:80], flush=True)
    return 0 if ctl_ok else 2


if __name__ == "__main__":
    sys.exit(main())
