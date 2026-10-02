r"""selftest_c134_4_owners - card 134-4 (PD289(f)): base_state of a MEASURED graph takes Flat Sequence owners from the two
measured links only - frame -> FS from fs_measured.fs_frames, FS -> diagram from its border tunnels' OUTER faces when ALL agree,
else UNMEASURED - and _diag_chain walks frame -> FS -> diagram. OFFLINE (no COM, nothing written).
INPUT: tools/bench/graph_ring_p3b2a_fs_20261002_102553.json (b885fa4a; 22 FS, 60 frames read ['FlatSequenceFrame', 0]).
EXISTING checked first: selftest_c134_1_fsmap.py (fs_measured_state on a fixture), diag_c134_4_chain.log (every frame chain stopped
at the frame before this fix; 19 FS have one agreeing outer-face diagram, FS 2499 / 14682 / 43914 have none).
PREDICTION: O1 no owner ['FlatSequenceFrame', *] left; O2 every frame's owner == its FS from fs_frames; O3 22 FS = 19 with a
chain from every frame reaching a non-frame top diagram + 3 UNMEASURED listed [2499, 14682, 43914]; O4 32464 -> 27219 -> 639;
O5 a frame of an UNMEASURED FS raises SimError naming it; O6 disagreeing outer faces (one face of FS 27509 moved) -> 27509
UNMEASURED; O7 no FS owner comes from anything but fs_parent (owners[fs] == ['Diagram', fs_parent[fs]] for all 19)."""
import copy, json, os, sys                                                                   # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagesim as SS, protocol as P                                                         # noqa: E401,E402
res = []


def gate(label, ok, detail=""):
    res.append(bool(ok))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:600]), flush=True)


G = json.load(open(os.path.join(HERE, "graph_ring_p3b2a_fs_20261002_102553.json"), encoding="utf-8"))
m = SS.fs_measured_state(G)
st = SS.base_state(G)
par = dict((int(k), int(v)) for k, v in SS.graph(st)["tree"]["parent"].items() if v is not None)
fsf = dict((int(k), [int(x) for x in v]) for k, v in m["fs_frames"].items())
frames = set(f for fl in fsf.values() for f in fl)
left = sorted(k for k, v in st["owners"].items() if v[0] == SS.FS_FRAME_CLS)
gate("O1 no owner ['FlatSequenceFrame', *] left after base_state ({0} frames replaced)".format(len(frames)), not left, left[:10])
bad = [(f, st["owners"].get(str(f))) for fs, fl in fsf.items() for f in fl if st["owners"].get(str(f)) != [SS.FS_CLS, fs]]
gate("O2 every frame's owner == its FS from fs_frames", not bad, bad[:10])
reach, stuck, um = {}, {}, []
for fs, fl in sorted(fsf.items()):
    if fs in st["fs_unmeasured"]:
        um.append(fs)
        continue
    for f in fl:
        ch = SS._diag_chain(st, f, par)
        if len(ch) < 2 or ch[-1] in frames:
            stuck[f] = ch
        reach.setdefault(fs, []).append(ch)
print("  FACT  FS chains (first frame): " + "; ".join("{0}: {1}".format(fs, c[0]) for fs, c in sorted(reach.items())), flush=True)
gate("O3 22 FS = {0} reaching a non-frame top diagram + {1} UNMEASURED listed {2}".format(len(reach), len(um), um),
     len(fsf) == 22 and not stuck and len(reach) + len(um) == 22 and um == [2499, 14682, 43914], {"stuck": stuck})
c = SS._diag_chain(st, 32464, par)
gate("O4 frame 32464 -> 27219 -> 639 (FS 27509 on 27219, case 22694 in While 637's body 639)", c[:3] == [32464, 27219, 639], c)
try:
    SS._diag_chain(st, 14037, par)
    o5 = (False, "no error")
except SS.SimError as e:
    o5 = ("14682" in str(e) and "UNMEASURED" in str(e), str(e))
gate("O5 a frame of an UNMEASURED FS (14037 of FS 14682) raises SimError naming it", *o5)
g2 = copy.deepcopy(G)
moved = None
for r in g2["terminals"]:
    if int(r["owner_uid"]) in [u for u, b in m["borders"].items() if b.get("fs") == 27509] and int(r.get("frame_diagram") or 0) == 27219:
        r["frame_diagram"], moved = 639, r["term_uid"]
        break
st2 = SS.base_state(g2)
gate("O6 one outer face of FS 27509 moved 27219 -> 639 (faces disagree) -> 27509 UNMEASURED, no owner entry",
     27509 in st2["fs_unmeasured"] and "27509" not in st2["owners"], {"moved_face": moved, "unmeasured": st2["fs_unmeasured"]})
o7 = [fs for fs in reach if st["owners"].get(str(fs)) != ["Diagram", m["fs_parent"][fs]]]
gate("O7 every measured FS owner == ['Diagram', fs_parent] (border outer faces only)", not o7, o7)
nf = res.count(False)
print(P.result_line(P.make_result(res.count(True), nf, None if not nf else "selftest_c134_4_owners")), flush=True)
sys.exit(1 if nf else 0)
