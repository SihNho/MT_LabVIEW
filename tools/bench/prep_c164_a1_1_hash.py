# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_164-a1-1.md
# ---
r"""prep_c164_a1_1_hash - card 164-a1-1 Part 1 (OFFLINE, read only): md5 (hashlib) of the step-4 inputs BEFORE anything else, compared with the
judgement-time values (card `inputs` md5s + brief short values) and the five claudeDev VIs (bytes only, never opened in LabVIEW).
Existing: prep_c163_a1_1_hash.py is the same check with the 163 lists hard-wired (no parameters); this file holds only the 164 lists.
PREDICTION: every file equal (0 changed).
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c164_a1_1_hash.log -- py -u tools/bench/prep_c164_a1_1_hash.py"""
import hashlib, json, os, sys                                                                # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol                                                                   # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
CARD = json.load(open(os.path.join(ROOT, "tools", "bench", "cards", "task_164-a1-1.json"), encoding="utf-8"))
WANT = [(i["path"], i["md5"], "card input") for i in CARD["inputs"]]
WANT += [(os.path.join(CD, n), w, "brief VI") for n, w in (("D1_ring_p5s02c_20261010_125755.vi", "564d8cbe"), ("D1_ring_p5s02b_20261010_105511.vi", "f9ae7751"),
                                                         ("D1_ring_p5s02a_20261010_023239.vi", "94ffff94"), ("D1_ring_p5s01_20261009_124542.vi", "7f2582ae"),
                                                         ("D1_ring_p4s09_20261009_060515.vi", "eb1d0f31"))]
BRIEF = {"tools/bench/plan_ring_p5s02r_in.json": "d84634bd", "tools/bench/graph_ring_p5s02c_20261010_131658.json": "3d5196ab",
         "tools/bench/memory_model.json": "8fb432e4", "tools/bench/errorlist_expected_D1_ring_p5s02c_20261010_125755.json": "26d45c71",
         "tools/stage_shared.py": "b688edd4", "tools/stagekit.py": "dd57c1ca", "tools/stagexec.py": "a4df7e15", "tools/stagesim.py": "95a162ba",
         "tools/stage_prerun.py": "7605116f", "docs/d1/ring-p5c.md": "70fe6983"}
bad, arts = [], []
for p, w, src in WANT:
    fp = p if os.path.isabs(p) else os.path.join(ROOT, p)
    try:
        h = hashlib.md5(open(fp, "rb").read()).hexdigest()
    except OSError as e:
        h = None
        print("HASH {0} | not hashed ({1})".format(p, e), flush=True)
    bw = BRIEF.get(p.replace("\\", "/"))
    ok = h is not None and h.startswith(w) and (bw is None or h.startswith(bw))
    print("HASH {0} | {1} | judgement {2} ({3}){4} | {5}".format(p, h, w[:8], src, "; brief " + bw if bw else "", "equal" if ok else "CHANGED"), flush=True)
    if not ok:
        bad.append(p)
    arts.append({"path": p.replace("\\", "/"), "md5": h})
miss = sorted(set(BRIEF) - set(p.replace("\\", "/") for p, _w, _s in WANT))
print("HASH brief values not in the card inputs: {0}".format(miss), flush=True)
print(protocol.result_line(protocol.make_result(len(WANT) - len(bad), len(bad) + len(miss), bad[0] if bad else (miss[0] if miss else None), [])), flush=True)
sys.exit(1 if bad or miss else 0)
