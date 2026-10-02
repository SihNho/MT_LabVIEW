"""Card 134-4 step 1 (offline, read-only): per Flat Sequence of the measured graph, what the two MEASURED links give
(fs_measured.fs_frames; border outer faces) and what stagesim's base_state + tree parent + _diag_chain currently make of it.
WHAT EXISTED: stagesim.base_state / fs_measured_state / graph / _diag_chain (read, not changed here).
PREDICTION: 22 FS; FS 27509 fs_parent 27219 (8 outer faces agree); frame 32464 chain stops at [32464] (no tree parent, owner
[FlatSequence, 27509] so _fsot_parent is skipped) -> the 134-2 'no common diagram' cause. Prints facts only."""
import json, os, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, stagesim as SS                                              # noqa: E402,E401
G = os.path.join(ROOT, "tools/bench/graph_ring_p3b2a_fs_20261002_102553.json")
g = json.load(open(G, encoding="utf-8"))
m = SS.fs_measured_state(g)
st = SS.base_state(g)
par = dict((int(k), int(v)) for k, v in SS.graph(st)["tree"]["parent"].items() if v is not None)
outer = collections.defaultdict(list)
for u, b in m["borders"].items():
    if b.get("fs") is not None:
        outer[b["fs"]].append(b["outer_frame"])
print("TREE-PARENT entries", len(par), "diagrams", len(st["diagrams"]))
for fs, fl in sorted(m["fs_frames"].items(), key=lambda x: int(x[0])):
    fs = int(fs)
    print("FS", fs, "frames", fl, "outer_faces", collections.Counter(outer.get(fs, [])), "fs_parent", m["fs_parent"].get(fs),
          "owners[fs]", st["owners"].get(str(fs)), "tree par fs", par.get(fs))
    for f in fl:
        print("   frame", f, "owner", st["owners"].get(str(f)), "tree par", par.get(int(f)), "chain", SS._diag_chain(st, int(f), par)[:8])
print("CHAIN 639", SS._diag_chain(st, 639, par)[:10])
print("CHAIN 27219", SS._diag_chain(st, 27219, par)[:10])
print(P.result_line(P.make_result(1, 0, None, [])))
