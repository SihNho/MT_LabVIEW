"""probe_walk_raw.py - what does the node walker's op RETURN at each index past the donor's nodes?

Two five-node probes (before and after the skip-fix in net_map) saw exactly the donor's 8 nodes and none of the
five nodes created on the same diagram - while `report_all` (a class traversal) sees all of them. So the walk
is not aborting on a bad node; it is ENDING at 8. The candidate explanations are different and each is cheap to
distinguish if the raw per-index result is printed instead of net_map's summary:

    (i)   OpNetInfo_v1 at index 8..12 raises  -> the op cannot address nodes beyond the original count
    (ii)  it returns UID 0                     -> Nodes[] really has 8 entries for the diagram it walks
    (iii) it returns the new uids               -> net_map's own post-processing drops them (e.g. the
                                                 'junk Invoke' end-of-nodes heuristic or the empty-terminal trim)
    (iv)  the new nodes sit under a DIFFERENT Traverse('Diagram') index than 0

So: create ONE known-good node and ONE questioned node, then (a) drive OpNetInfo_v1 directly for index 0..13 on
diagram 0 and print UID / exception per index; (b) list every diagram index Traverse('Diagram') returns and
the node count net_map reports for each. No wiring; scratch deleted; nothing saved.
  py tools/bgrun.py --max-min 10 --log tools/bench/probe_walk_raw.log -- py -u tools/recipes/probe_walk_raw.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpFPLabels_v0.vi")
S = os.path.join(g.CLAUDEDEV, "SCRATCH_walk_raw.vi")
g._run.__defaults__ = (6.0, 120.0)


def raw_index(vi, diagram, n):
    """One OpNetInfo_v1 run for Nodes[][n] of Traverse('Diagram')[diagram]; returns ('uid', value) or ('exc', msg)."""
    vi.SetControlValue("vi path", S)
    vi.SetControlValue("Class Name", "Diagram")
    vi.SetControlValue("index", diagram)
    vi.SetControlValue("index 2", n)
    vi.SetControlValue("index 3", 0)
    vi.SetControlValue("error in (no error)", (False, 0, ""))
    vi.SetControlValue("error in", (True, 1, "neutralised creator"))
    vi.SetControlValue("Class Name 3", "")
    vi.SetControlValue("Class Name 2", "")
    try:
        g._run(vi)
    except RuntimeError as e:
        return ("exc", str(e)[:80])
    try:
        return ("uid", int(vi.GetControlValue("UID")))
    except Exception as e:
        return ("noread", str(e)[:60])


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
    dias = g.report_all(S, "Diagram")
    print(f"scratch ExecState {g.exec_state(S)}; Traverse('Diagram') returns {len(dias)} diagram(s): "
          f"{[(i, d['owner']) for i, d in enumerate(dias)]}", flush=True)
    vi = g.op(g.OP_NETINFO) if hasattr(g, "OP_NETINFO") else g.op(os.path.join(g.CLAUDEDEV, "OpNetInfo_v1.vi"))

    print("\n--- BEFORE creation: raw walk of diagram 0, index 0..13 ---", flush=True)
    for n in range(14):
        print(f"   [{n:2d}] {raw_index(vi, 0, n)}", flush=True)

    before = {o["uid"] for o in g.report_all(S, "Property")}
    good = g.build_property(S, "VI Server:GObject", [("632A800", False)], (1300, 500))[-1]["uid"]
    quest = g.build_property(S, "VI Server:Control", [("6332006", False)], (1300, 620))[-1]["uid"]
    after = {o["uid"] for o in g.report_all(S, "Property")}
    print(f"\ncreated known-good uid {good}, questioned uid {quest}; report_all Property before={len(before)} after={len(after)}",
          flush=True)

    print("\n--- AFTER creation: raw walk of diagram 0, index 0..13 ---", flush=True)
    seen = set()
    for n in range(14):
        r = raw_index(vi, 0, n)
        mark = ""
        if r[0] == "uid":
            if r[1] == good:
                mark = "   <-- KNOWN-GOOD new node"
            elif r[1] == quest:
                mark = "   <-- QUESTIONED new node"
            seen.add(r[1])
        print(f"   [{n:2d}] {r}{mark}", flush=True)

    print("\n--- every diagram index: node count per net_map ---", flush=True)
    for i in range(len(dias)):
        try:
            nodes, _w = g.net_map(S, i, max_nodes=80, max_terms=6)
            hit = [u for _k, (u, _l, _t) in nodes.items() if u in (good, quest)]
            print(f"   diagram {i}: {len(nodes)} nodes; new nodes present: {hit}", flush=True)
        except Exception as e:
            print(f"   diagram {i}: EXC {str(e)[:100]}", flush=True)

    verdict = ("(iii) walker post-processing drops them" if (good in seen or quest in seen) else
               "(i)/(ii)/(iv) - see the raw rows: exceptions, UID 0, or another diagram index")
    print(f"\nVERDICT: {verdict}", flush=True)
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
