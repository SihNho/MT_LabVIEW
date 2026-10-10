# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/task_163-a2-2.json
# ---
r"""diag_c163_a2_2_hash - card 163-a2-2 (OFFLINE, bytes only, hashlib). COPY of diag_c163_a2_1_hash.py; changed line ONLY: CARD
(task_163-a2-2.json). Calls protocol.input_md5_changes and prep_c156_a1_1_lib (md5, Gate); no logic of its own.
argv[1] = before | after. 'after' drops memory_model.json, plan_ring_p5s02c_pred.json, adopted_scratch.jsonl from (1) and prints their md5.
PREDICTION CONTRACT: before: 0 input changes, every pin equal. after: same, except the three named files.
    py tools/bgrun.py --material --max-min 1 --log tools/bench/diag_c163_a2_2_hash_<mode>.log -- py -u tools/bench/diag_c163_a2_2_hash.py <mode>"""
import glob, json, os, sys                                                                  # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import protocol as PR                                                                       # noqa: E402
import prep_c156_a1_1_lib as L                                                              # noqa: E402
MODE = sys.argv[1] if len(sys.argv) > 1 else "before"
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
CARD = os.path.join(ROOT, "tools", "bench", "cards", "task_163-a2-2.json")
MUTABLE = ("tools/bench/memory_model.json", "tools/bench/plan_ring_p5s02c_pred.json", "tools/bench/adopted_scratch.jsonl")
VIS = [("D1_ring_p4s09_20261009_060515.vi", "eb1d0f31"), ("D1_ring_p5s01a_20261009_101219.vi", "2482fe7b"),
       ("D1_ring_p5s01_20261009_124542.vi", "7f2582ae"), ("D1_ring_p5s02a_20261010_023239.vi", "94ffff94"),
       ("D1_ring_p5s02b_20261010_105511.vi", "f9ae7751")]
TOOLS = [("tools/stagekit.py", "dd57c1ca"), ("tools/stagesim.py", "95a162ba"), ("tools/stagexec.py", "a4df7e15"),
         ("tools/stage_prerun.py", "7605116f")]
gate = L.Gate(fatal_default=False)
card = json.load(open(CARD, encoding="utf-8"))
if MODE == "after":
    card["inputs"] = [i for i in card["inputs"] if i["path"] not in MUTABLE]
bad = PR.input_md5_changes(card)
gate("I {0} md5-pinned card inputs equal in the main tree".format(len(card["inputs"])), not bad, bad or "all equal")
for p in MUTABLE:
    print("FACT {0} md5 {1}".format(p, L.md5(os.path.join(ROOT, p))), flush=True)
for name, pin in VIS:
    m = L.md5(os.path.join(CD, name))
    gate("H {0} md5 {1} vs pin {2}".format(name, m, pin), m.startswith(pin), "equal" if m.startswith(pin) else "UNEQUAL")
for rel, pin in TOOLS:
    m = L.md5(os.path.join(ROOT, rel))
    gate("T {0} md5 {1} vs pin {2}".format(rel, m, pin), m.startswith(pin), "equal" if m.startswith(pin) else "UNEQUAL")
print("FACT claudeDev *p5s02* {0}".format([(os.path.basename(p), L.md5(p)[:8]) for p in sorted(glob.glob(os.path.join(CD, "*p5s02*")))]),
      flush=True)
sys.exit(gate.result([]))
