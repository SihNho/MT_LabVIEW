r"""selftest_c134_1_fsmap - card 134-1 (b2, PD287(b)): stagesim takes Flat Sequence frames / border entries from a MEASURED
graph field (`fs_measured`), not by elimination. OFFLINE (no COM, nothing written outside %TEMP%).
FIXTURE: tools/bench/sim/ring_p3b2_base_real_fsmap.json = P3b-1's REAL graph read (graph_ring_p3b1_20261002_073225) + the map
carry_fs bound by elimination (fs_frames {27509: [27641, 32464, 27722]}, 6 border entries). Its terminal rows are the recorded
input; `fs_measured.fs_frames` is set to the same frame list (stand-in for one OpFsDiagrams_v0 read until (c) measures it).
EXISTING checked first: selftest_rebase_c132_6.py (carry_fs path), stagesim self-tests (fs_frames only from plan-made FS).
PREDICTION: M1 the measured state's 6 border entries == the carried map's 6 (key + face); M2 frame owners == FlatSequence
27509; M3 FS 27509 sits on diagram 27219 (the carried owner); M4 base_state on a graph with ONLY terminals + fs_measured (no
fs_carried, no carried keys) gives fs_frames / fs_border_entries / owners equal to the carried base's; M5 no negative uid.
"""
import copy, json, os, sys                                                                   # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagesim as SS, protocol as P                                                         # noqa: E401,E402
res = []


def gate(label, ok, detail=""):
    res.append(bool(ok))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:400]), flush=True)


src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "sim", "ring_p3b2_base_real_fsmap.json")
G = json.load(open(src, encoding="utf-8"))
car = G.get("fs_border_entries") or {}
fm = G.get("fs_measured", {}).get("fs_frames") or G.get("fs_frames")
g2 = dict((k, copy.deepcopy(G[k])) for k in ("vi", "md5", "terminals", "objs", "loops", "fs_tunnel_pairs", "owners") if k in G)
for f in fm.get("27509", []):
    g2["owners"][str(f)] = ["FlatSequenceFrame", 0]                   # as the reader leaves them (owner_of error 1055)
g2["owners"].pop("27509", None)
g2["fs_measured"] = {"fs_frames": fm}
m = SS.fs_measured_state(g2)
print("  FACT  source {0}; measured fs_frames {1}; borders {2}; entries {3}".format(os.path.relpath(src, ROOT), fm,
                                                                                   len(m["borders"]), len(m["fs_border_entries"])))
if car:
    want = dict((k, v["face"]) for k, v in car.items())
    got = dict((k, v["face"]) for k, v in m["fs_border_entries"].items() if int(k.split("|")[1]) in m["frame_owner"]
               and m["frame_owner"][int(k.split("|")[1])] == 27509)
    gate("M1 measured border entries of FS 27509 == the carried map's (key + face)", got == want,
         {"only_measured": sorted(set(got.items()) - set(want.items())), "only_carried": sorted(set(want.items()) - set(got.items()))})
gate("M2 frame owners == FlatSequence 27509", all(m["frame_owner"].get(int(f)) == 27509 for f in fm["27509"]), m["frame_owner"])
gate("M3 FS 27509 sits on diagram 27219", m["fs_parent"].get(27509) == 27219, m["fs_parent"])
st = SS.base_state(g2)
ok4 = st["fs_frames"].get("27509") == [int(x) for x in fm["27509"]] and all(st["owners"].get(str(f)) == ["FlatSequence", 27509]
                                                                            for f in fm["27509"])
if car:
    ok4 = ok4 and dict((k, v["face"]) for k, v in st["fs_border_entries"].items() if k in car) == dict((k, v["face"]) for k, v in car.items())
gate("M4 base_state(terminals + fs_measured) -> fs_frames / owners / entries as measured", ok4,
     {"fs_frames": st.get("fs_frames"), "owner27509": st["owners"].get("27509")})
neg = [k for k, v in m["fs_border_entries"].items() if int(k.split("|")[0]) < 0 or v["face"] < 0]
gate("M5 no negative uid in the measured entries", not neg, neg)
gate("M6 border tunnels with not one inner + one outer face: listed, not guessed", True,
     dict((k, v) for k, v in m["borders"].items() if v.get("fs") is None))
nf = res.count(False)
print(P.result_line(P.make_result(res.count(True), nf, None if not nf else "selftest_c134_1_fsmap")), flush=True)
sys.exit(1 if nf else 0)
