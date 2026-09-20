"""probe_attach_reader2.py - does the walker ABORT at the first empty node? Swap the creation order and see.

RUN 1 (tools/bench/probe_attach_reader.log), deterministic over three reads each:

    created 1st  GObject.Position 632A800          exists, IN WALK, 5 terminals, row 'Position'
    created 2nd  Control.Terminal 6332006          exists, NOT in walk
    created 3rd  AbstractDiagram.SubVIs[] 6375802  exists, NOT in walk
    created 4th  AbstractDiagram.Nodes[] 6375809   exists, NOT in walk      <- a KNOWN-GOOD id

So the walk (Nodes[] -> Index Array -> Node.Terminals[] -> Terminal.Name, by index) sees only the first node and
nothing created after it - INCLUDING a control that attaches in working ops. That is not about the IDs; it is
about the walker. HYPOTHESIS under peer review (archive/peer/2026-09-14-walker-aborts-at-empty-node.md): the
walker iterates by index and aborts at the first node with no property rows, so everything after it in Nodes[]
order is never visited; the two questioned IDs really are empty.

THE DISCRIMINATING TEST: create the known-good id BEFORE the questioned ones.

    prediction if the hypothesis holds : Position IN, Nodes[] IN, then Control.Terminal OUT, SubVIs[] OUT,
                                         and a SECOND known-good created LAST is also OUT (walk died before it)
    prediction if it fails             : the known-good ids are visible regardless of position, and the
                                         questioned ones are not -> the walker skips specific nodes, not tails

Also recorded per node: where it sits in the walk (its index) so "died at index k" is literal, not inferred.
No wiring; nothing saved; scratch deleted.
  py tools/bgrun.py --max-min 12 --log tools/bench/probe_attach_reader2.log -- py -u tools/recipes/probe_attach_reader2.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpFPLabels_v0.vi")
S = os.path.join(g.CLAUDEDEV, "SCRATCH_attach_reader2.vi")
GENERIC = {"reference", "reference out", "error in (no error)", "error out", "error in"}
ORDER = [
    ("A known-good  GObject.Position 632A800", "VI Server:GObject", "632A800"),
    ("B known-good  AbstractDiagram.Nodes[] 6375809", "VI Server:AbstractDiagram", "6375809"),
    ("C questioned  Control.Terminal 6332006", "VI Server:Control", "6332006"),
    ("D questioned  AbstractDiagram.SubVIs[] 6375802", "VI Server:AbstractDiagram", "6375802"),
    ("E known-good  GObject.Position 632A800 (created LAST)", "VI Server:GObject", "632A800"),
]
g._run.__defaults__ = (6.0, 120.0)


def walk():
    nodes, _w = g.net_map(S, 0, max_nodes=80, max_terms=24)
    return {u: (i, [t for _ti, t, _w2 in terms if t]) for i, (u, _l, terms) in nodes.items()}


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
    base = walk()
    print(f"scratch ExecState {g.exec_state(S)}; walk sees {len(base)} nodes before any creation\n", flush=True)

    created = []
    y = 500
    for label, cls, pid in ORDER:
        new = g.build_property(S, cls, [(pid, False)], (1300, y))
        y += 110
        uid = new[-1]["uid"]
        created.append((label, uid))
        print(f"created {label}: uid {uid}", flush=True)

    print("\n--- walk after all five creations ---", flush=True)
    w = walk()
    exists = {o["uid"] for o in g.report_all(S, "Property")}
    print(f"report_all sees {len(exists)} Property objects; walk sees {len(w)} nodes", flush=True)
    seen_idx = []
    for label, uid in created:
        if uid in w:
            i, terms = w[uid]
            rows = [t for t in terms if t not in GENERIC]
            print(f"   IN   idx {i:2d}  {label:52} rows={rows}", flush=True)
            seen_idx.append(i)
        else:
            print(f"   OUT  ---     {label:52} exists={uid in exists}", flush=True)
    print(f"\nhighest walk index reached = {max(w) if w else None}; created nodes seen at {seen_idx}", flush=True)

    a, b, c, d, e = (created[k][1] in w for k in range(5))
    if a and b and not c and not d and not e:
        print("VERDICT: matches 'walker aborts at first empty node' - C and D are EMPTY (not attached); "
              "E is hidden only because it sits after them.", flush=True)
    elif a and b and e and not c and not d:
        print("VERDICT: walker SKIPS the empty nodes but continues - C and D are empty; the walker is otherwise fine.",
              flush=True)
    else:
        print("VERDICT: pattern does not match either prediction - do not conclude; see rows above.", flush=True)
    try:
        g.close_panel(S)
        time.sleep(0.3)
        os.remove(S)
        print("scratch deleted", flush=True)
    except Exception as ex:
        print("cleanup:", str(ex)[:80], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
