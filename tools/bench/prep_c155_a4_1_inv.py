# ---
# labview: none
# hardware: none
# offline-args: --before
# evidence: tools/bench/cards/brief_155-a4-1.md
# ---
r"""prep_c155_a4_1_inv - card 155-a4-1 (brief_155-a4-1.md item 4; offline, json/md5 only, no LabVIEW, no COM): the protected md5s BEFORE and AFTER.
COPY of prep_c155_a2_1_inv.py (73 lines; OPEN: the gate()/file_set()/before-after block is copied, not extracted - outside this card's write
globs). CHANGED: output table prep_c155_a4_1_md5_before.json; memory_model 386a4cf4 -> c87d170a (155-a3-2); ADDED the P5-1b / P5-1 files
(plan_ring_p5s01b*, stage_d1_ring_p5s01b*.py, prep_c155_a2_1_* makers, session 79447fab), the 155-a3-1 / 155-a3-2 files (diag_c155_a3_2_*.py,
facts e5496944, the P5-1 graph 6716c499, the adopted VI 7f2582ae, the P5-1b work VI 7f2582ae, the EL expected ffc4cf66), adopted_scratch dd0aa787,
p5_route_census.md dba7e3f0, donor_queue_v0.json.
PREDICTION: B pins match; A every file in the before table has the same md5 (non-log), no file added or removed.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c155_a4_1_inv_before.log -- py -u tools/bench/prep_c155_a4_1_inv.py --before"""
import glob, hashlib, json, os, sys                                                                       # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
PINS = {"tools/stagekit.py": "aec03c6c", "tools/addrcheck.py": "207beb0d", "tools/stagexec.py": "53e17623", "tools/stagesim.py": "eb99c6ba",
        "tools/gscript.py": "1a80236e", "tools/vigraph.py": "a7eb58c7", "tools/stage_prerun.py": "9decb20f", "tools/bench/memory_model.json": "c87d170a",
        os.path.join(CD, "DonorQueue_v0.vi"): "81dba822", "tools/bench/donor_queue_v0.json": "15269b6c",
        os.path.join(CD, "D1_ring_p4s09_20261009_060515.vi"): "eb1d0f31", "tools/bench/graph_ring_p4s09_20261009_062044.json": "22f967b5",
        "tools/bench/plan_ring_p4_s09v18.json": "9d622c95", "docs/d1/ring-p5.md": "a4b596f0",
        "tools/bench/plan_ring_p5s01.json": "ed6ceb9e", "tools/bench/plan_ring_p5s01_in.json": "fabc4b9c",
        os.path.join(CD, "D1_ring_p5s01a_20261009_101219.vi"): "2482fe7b", "tools/bench/graph_ring_p5s01a_20261009_103621.json": "bd67a511",
        "tools/bench/plan_ring_p5s01a.json": "ed62e8d6", "tools/bench/plan_ring_p5s01a_in.json": "80c3710e",
        "tools/bench/plan_ring_p5s01b.json": "75a77a00", "tools/bench/plan_ring_p5s01b_in.json": "114b3159",
        "tools/bench/plan_ring_p5s01b_pred.json": "2f2cbcc3", "tools/bench/plan_ring_p5s01b_licence.json": "e592cf7a",
        "tools/recipes/stage_d1_ring_p5s01b.py": "6de2378d", "tools/recipes/stage_d1_ring_p5s01b_scratch.py": "9233749f",
        "tools/bench/prep_c155_a2_1_session.json": "79447fab", "tools/bench/prep_c155_a2_1_mk.py": "2c766af9",
        "tools/bench/prep_c155_a2_1_pred.py": "20726b40", "tools/bench/prep_c155_a2_1_licence.py": "d286d438",
        "tools/bench/prep_c155_a2_1_inv.py": "6ad4df7a", "tools/bench/diag_c155_a2_1_facts.md": "e97f757a",
        "tools/bench/diag_c155_a3_2_facts.md": "e5496944", "tools/bench/p5_route_census.md": "dba7e3f0",
        os.path.join(CD, "D1_ring_p5s01_20261009_124542.vi"): "7f2582ae", os.path.join(CD, "D1_ring_p5s01b_20261009_123319.vi"): "7f2582ae",
        "tools/bench/graph_ring_p5s01_20261009_125622.json": "6716c499",
        "tools/bench/errorlist_expected_D1_ring_p5s01_20261009_124542.json": "ffc4cf66",
        "tools/bench/errorlist_expected_D1_ring_p5s01a_20261009_101219.json": "aee0d9fe",
        "tools/bench/adopted_scratch.jsonl": "dd0aa787", "tools/elrule.py": "", "tools/bench/census_samples.json": "",
        "tools/bench/main_vi_node_labels.json": "", "docs/script-writing.md": "0165fb24"}
OUTF = os.path.join(ROOT, "tools", "bench", "prep_c155_a4_1_md5_before.json")
ab = lambda k: k if os.path.isabs(k) else os.path.join(ROOT, k)                                          # noqa: E731
md = lambda k: hashlib.md5(open(ab(k), "rb").read()).hexdigest()                                         # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                               # noqa: E731


def file_set():
    s = set(PINS)
    for pat in ("tools/recipes/stage_d1_ring_p4*.py", "tools/bench/plan_ring_p4*.json", "tools/recipes/stage_d1_ring_p5s01*.py",
                "tools/bench/plan_ring_p5s01*.json", "tools/bench/diag_c155_a3_*.py", "tools/bench/diag_c155_a3_*_facts.md"):
        s |= set(rel(p) for p in glob.glob(os.path.join(ROOT, pat)))
    for dp, _d, fn in os.walk(os.path.join(ROOT, "tools", "hooks")):
        s |= set(rel(os.path.join(dp, n)) for n in fn if "__pycache__" not in dp)
    return sorted(s)


G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)


now = dict((k, md(k)) for k in file_set())
gate("B pins (prefix) == card", all(now[k].startswith(v) for k, v in PINS.items()), dict((k[-40:], now[k][:8]) for k in PINS if not now[k].startswith(PINS[k])))
if "--before" in sys.argv:
    json.dump(now, open(OUTF, "w", encoding="utf-8"), indent=1)
    print("FACT wrote {0} ({1} files) md5 {2}".format(rel(OUTF), len(now), md(OUTF)), flush=True)
else:
    was = json.load(open(OUTF, encoding="utf-8"))
    logs = sorted(k for k in set(was) | set(now) if k.startswith("tools/hooks/") and k.endswith(".log") and was.get(k) != now.get(k))
    diff = sorted(k for k in set(was) | set(now) if was.get(k) != now.get(k) and k not in logs)
    print("FACT hook-written logs changed (not gated): {0}".format(logs), flush=True)
    gate("A every protected file md5 before == after ({0} files, logs excluded)".format(len(was)), not diff, diff)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
