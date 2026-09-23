r"""Shared inputs of the step-5b bench scripts (a1/a23/b). Not run on its own.

PRIOR ART USED, NOT RE-TYPED: wiki_build.read_live (added for 5b: GObject + OpAllTerms_v1 + Wire census, fs pairs
reused), jev_candidates.load/from_parts (the S1 graph with the wiki's exact fs pairs), vigraph.diff/computation_diff,
stagekit.Stage (pins, dated scratch, hygiene), gscript.report_all.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(HERE)
TOOLS = os.path.dirname(BENCH)
for p in (TOOLS, BENCH):
    if p not in sys.path:
        sys.path.insert(0, p)
import stagekit as K                                                               # noqa: E402,F401
import gscript as g                                                                # noqa: E402,F401
import vigraph as V                                                                # noqa: E402
import jev_candidates as JC                                                        # noqa: E402
import wiki_build as W                                                             # noqa: E402

S1 = os.path.join(K.CLAUDEDEV, "D1_s1_copy.vi")
S1_MD5 = "3e3d23cefd3a334001aa9d6156bf1aee"
SEED = 20260923
BODY = 639                   # the frame-loop body diagram (WhileLoop #637)
SEVERED = [1731, 1893, 2819, 3947, 4833, 7337, 7388, 9635, 11232, 23502, 23540]


def s1_graph():
    return JC.load(JC.S1_KEY)                      # wiki v1 terminals + the wiki's exact fs pairs


def s1_loops():
    return json.load(open(JC._newest("graph_loops_s1_*.json"), encoding="utf-8"))["loops"]


def live_graph(path, G0, tag):
    """Read `path` from the machine and build its graph exactly like S1's. The flat-sequence faces and the
    Shift Registers[] membership are STRUCTURAL (terminal / register uids), so S1's are reused; the terminal
    table, wire uids and positions are READ."""
    live = W.read_live(path, fs_pairs=G0["wiki"]["fs_tunnel_pairs"])
    rec = {"terminals": live["terminals"], "graph_summary": G0["wiki"]["graph_summary"]}
    G = JC.from_parts(rec, live["objs"], s1_loops(), JC.node_labels_default(), live["fs_tunnel_pairs"], tag)
    G["live"] = {"secs": live["secs"], "n_terms": len(live["terminals"]), "n_objs": len(live["objs"]),
                 "n_wires": len(live["wires"]), "termless": sum(1 for w in live["wires"] if w.get("termless"))}
    return G


def edge_rows(d):
    """diff() output -> the set of changed EDGE rows, keyed by owner uid + terminal name (Pre-decided 137)."""
    return set(("-",) + tuple(e) for e in d["edges_removed"]) | set(("+",) + tuple(e) for e in d["edges_added"])


def show_row(r):
    return "{0} {1} {2} -> {3}".format(r[0], r[1], V.show(r[2]), V.show(r[3]))


def wire_edge(G, w):
    """The ('wire', src key, sink key) edge rows of wire uid `w` in G."""
    return [(k, a, b) for k, a, b, i in G["edges"] if k == "wire" and i == w]


def dump(name, obj):
    p = os.path.join(HERE, name)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, default=str)
    return p
