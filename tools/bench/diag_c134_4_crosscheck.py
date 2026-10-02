"""Card 134-4, the review's cheapest discriminating test (archive/peer/2026-10-02-c134-4-fs-chain.md:83-88), OFFLINE, read-only.
(1) every one of the 60 FS frames: the card-127 derivation _fsot_parent (frame owners reset to ['FlatSequenceFrame', 0], as the
reader leaves them) vs fs_parent[fs] (border outer faces, PD289(f)); a non-None mismatch = one derivation wrong (CROSS ONLY: it uses
the graph's carried fs_tunnel_pairs, never an owner source). (2) owners[fs] before / after the 134-4 edit: the pre-edit base_state
already did setdefault(['Diagram', fs_parent]) (diag_c134_4_chain.log, run before the edit) -> closure_of of While 637 / case 22694
is compared between base_state WITHOUT FS owner rows and WITH them, to size the move change the review names.
PREDICTION: X1 0 mismatches (None allowed, listed); X2 FS 26415 / 28381 single-face parents listed with their _fsot_parent;
X3 closure sizes printed (fact only)."""
import copy, json, os, sys, collections                                                      # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, stagesim as SS                                                         # noqa: E402,E401
G = json.load(open(os.path.join(ROOT, "tools/bench/graph_ring_p3b2a_fs_20261002_102553.json"), encoding="utf-8"))
m = SS.fs_measured_state(G)
st = SS.base_state(G)
st0 = copy.deepcopy(st)
for f, fs in m["frame_owner"].items():
    st0["owners"][str(f)] = [SS.FS_FRAME_CLS, 0]
rows, mism, none = [], [], []
for f, fs in sorted(m["frame_owner"].items()):
    a, b = SS._fsot_parent(st0, int(f)), m["fs_parent"].get(fs)
    rows.append((fs, f, a, b))
    if a is None:
        none.append((fs, f, b))
    elif b is not None and a != b:
        mism.append((fs, f, a, b))
print("  FACT  _fsot_parent pairs source: graph fs_tunnel_pairs n={0}".format(len(st0.get("fs_pairs") or [])), flush=True)
for fs in sorted(set(r[0] for r in rows)):
    print("  FS {0}: fs_parent {1}; _fsot_parent per frame {2}".format(fs, m["fs_parent"].get(fs),
          [(r[1], r[2]) for r in rows if r[0] == fs]), flush=True)
ok = []
ok.append(not mism)
print("{0}  X1 _fsot_parent vs fs_parent: {1} mismatches, {2} frames None (listed above)".format(
    "PASS" if not mism else "FAIL", len(mism), len(none)), mism[:20], flush=True)
for fs in (26415, 28381):
    print("  X2 FS {0} single-face parent {1}; _fsot_parent {2}".format(fs, m["fs_parent"].get(fs),
          sorted(set(r[2] for r in rows if r[0] == fs), key=str)), flush=True)
stn = copy.deepcopy(st)
for fs in m["fs_parent"]:
    stn["owners"].pop(str(fs), None)
for u in (637, 22694):
    (na, da), (nb, db) = SS.closure_of(stn, u), SS.closure_of(st, u)
    print("  X3 closure_of({0}): without FS owner rows {1} nodes / {2} diagrams, with {3} / {4}; added nodes {5}, diagrams {6}".format(
        u, len(na), len(da), len(nb), len(db), len(nb - na), sorted(db - da)[:20]), flush=True)
nf = ok.count(False)
print(P.result_line(P.make_result(len(ok) - nf, nf, None if not nf else "X1 _fsot_parent vs fs_parent", [])), flush=True)
sys.exit(1 if nf else 0)
