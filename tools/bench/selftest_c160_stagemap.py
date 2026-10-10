# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_160-b1-1.md
# ---
r"""selftest_c160_stagemap - card 160-b1-1 (docs/d1/ring-p5b.md PD390(c)), OFFLINE: no LabVIEW, no COM.
Under test (called): stagekit.made_symbols / used_symbols / map_symbols / map_frames / apply_map / bound_from_cmap (stagekit.py:2741-2868),
moved from tools/bench/prep_c159_c1_1_lib.py (unedited, imported here only as the reference for T4).
Data = the lib's own --selftest case (card 155-a2-1): P5-1b rows 21..32 of plan_ring_p5s01_in.json mapped with the P5-1a sim end sym + the
STEPX `bound` lines of diag_c154_p5s01a_scratch.log on graph bd67a511 (graph_ring_p5s01a_20261009_103621.json).
PREDICTION 4/0 (+P0): T1 all used symbols map (bad []); T2 frame map ['#30914'] (bad []); T3 apply_map == plan_ring_p5s01b.json actions (12, 75a77a00);
T4 for each of the six functions stagekit.<f> == prep_c159_c1_1_lib.<f> on those inputs (bound_from_cmap on the P5-1a creation map
plan_ring_p5s01a_ed62e8d6_20261009_101431.jsonl and on the 94ffff94 run's map plan_ring_p5s02a_4284c22a_20261010_023453.jsonl).
    py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_c160_stagemap.log -- py -u tools/bench/selftest_c160_stagemap.py"""
import copy, os, re, sys                                                                     # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import stagekit as K                                                                         # noqa: E402
import prep_c156_a1_1_lib as L                                                               # noqa: E402  Gate, md5, J (one copy)
import prep_c159_c1_1_lib as OLD                                                             # noqa: E402  reference only (T4)
md5, J = L.md5, L.J
B = os.path.join(ROOT, "tools", "bench")
g = L.Gate(fatal_default=False)
PINS = {os.path.join(B, "prep_c159_c1_1_lib.py"): "218af76c", os.path.join(B, "plan_ring_p5s01b.json"): "75a77a00",
        os.path.join(B, "graph_ring_p5s01a_20261009_103621.json"): None}
got = dict((os.path.basename(p), md5(p)[:8]) for p in PINS)
g("P0 pins: lib 218af76c (unedited), plan_ring_p5s01b 75a77a00", all(w is None or md5(p).startswith(w) for p, w in PINS.items()), got)
SIN, PA, PB = J(os.path.join(B, "plan_ring_p5s01_in.json")), J(os.path.join(B, "plan_ring_p5s01a.json")), os.path.join(B, "plan_ring_p5s01b.json")
GR = J(os.path.join(B, "graph_ring_p5s01a_20261009_103621.json"))
last = max((PA.get("finalized") or {}).get("step_files") or [], key=lambda x: int(x["n"]))
SYM = J(last["path"])["state"]["sym"]
BOUND = {}
for ln in open(os.path.join(B, "diag_c154_p5s01a_scratch.log"), encoding="utf-8", errors="replace"):   # 155-a2-1's source (test only)
    m = re.search(r"STEPX\s+\d+\s+.*bound (\{[^}]*\})", ln)
    if m:
        BOUND.update(dict((int(k), int(v)) for k, v in re.findall(r"(-?\d+):\s*(-?\d+)", m.group(1))))
RAW = copy.deepcopy(SIN["actions"][20:])
used = K.used_symbols(RAW, K.made_symbols(RAW))
REAL, bad, _l = K.map_symbols(used, SYM, BOUND, GR)
g("T1 155-a2-1 symbols {0} all map (bad {1})".format(used, bad), not bad and len(REAL) == len(used))
FMAP, fbad, _l2 = K.map_frames(RAW, SIN["actions"], SYM, BOUND, GR.get("owners") or {})
g("T2 155-a2-1 frame map {0} (bad {1})".format(sorted(set(v["addr"] for v in FMAP.values())), fbad), bool(FMAP) and not fbad)
ACTS = K.apply_map(RAW, REAL, FMAP)
PBJ = J(PB)
g("T3 apply_map(155-a2-1 rows) == plan_ring_p5s01b.json actions ({0}; md5 {1})".format(len(ACTS), md5(PB)[:8]),
  ACTS == PBJ["actions"][:len(ACTS)] and len(ACTS) == len(PBJ["actions"]), [a["id"] for a, b in zip(ACTS, PBJ["actions"]) if a != b])
# T4: the same calls through the lib, value for value
CM = [os.path.join(B, "creation_map", n) for n in ("plan_ring_p5s01a_ed62e8d6_20261009_101431.jsonl", "plan_ring_p5s02a_4284c22a_20261010_023453.jsonl")]
same = {
    "made_symbols": K.made_symbols(RAW) == OLD.made_symbols(RAW) and K.made_symbols(SIN["actions"]) == OLD.made_symbols(SIN["actions"]),
    "used_symbols": used == OLD.used_symbols(RAW, OLD.made_symbols(RAW)),
    "map_symbols": (REAL, bad, _l) == OLD.map_symbols(used, SYM, BOUND, GR),
    "map_frames": (FMAP, fbad, _l2) == OLD.map_frames(RAW, SIN["actions"], SYM, BOUND, GR.get("owners") or {}),
    "apply_map": ACTS == OLD.apply_map(RAW, REAL, FMAP) and RAW == SIN["actions"][20:],
    "bound_from_cmap": all(K.bound_from_cmap(p) == OLD.bound_from_cmap(p) and len(K.bound_from_cmap(p)[1]) > 0 for p in CM)}
g("T4 stagekit.<f> == prep_c159_c1_1_lib.<f> on the 155-a2-1 inputs (bound_from_cmap on 2 creation maps): {0}".format(same), all(same.values()),
  dict((os.path.basename(p), len(K.bound_from_cmap(p)[1])) for p in CM))
print("FACT md5 stagekit {0} lib {1}".format(md5(os.path.join(ROOT, "tools", "stagekit.py")), md5(os.path.join(B, "prep_c159_c1_1_lib.py"))), flush=True)
sys.exit(g.result())
