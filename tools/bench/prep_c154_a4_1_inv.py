# ---
# labview: none
# hardware: none
# offline-args: --before
# evidence: tools/bench/cards/brief_154-a4-1.md
# ---
r"""prep_c154_a4_1_inv - card 154-a4-1 change 6 (offline, json/md5 only, no LabVIEW, no COM): the protected md5s BEFORE and AFTER.
COPY of prep_c154_a3_2b_inv.py (7f9657fb). CHANGED lines: output table prep_c154_a4_1_md5_before.json; card strings; memory_model pin
6f2b5687 -> 386a4cf4 (card 154-a3-3b load_by_vi); ADDED the P5-1a files (plan / plan_in / pred / licence / session / both recipes, by name
and by the glob plan_ring_p5s01a*.json + stage_d1_ring_p5s01a*.py, which cannot catch this card's p5s01b outputs), the adopted P5-1a VI
2482fe7b and its graph bd67a511, errorlist_expected aee0d9fe, docs/violation-decisions.md 6497e984, the P5-1a scratch log and nodes log
(the mapping sources). Everything else unchanged.
PREDICTION: B pins match; A every file in the before table has the same md5 (non-log), no file added or removed.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c154_a4_1_inv_before.log -- py -u tools/bench/prep_c154_a4_1_inv.py --before"""
import glob, hashlib, json, os, sys                                                                       # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
PINS = {"tools/stagekit.py": "604529e8", "tools/addrcheck.py": "207beb0d", "tools/stagexec.py": "1bab9cf9", "tools/stagesim.py": "78b8d5a1",
        "tools/gscript.py": "1a80236e", "tools/vigraph.py": "a7eb58c7", "tools/stage_prerun.py": "9decb20f", "tools/bench/memory_model.json": "386a4cf4",
        os.path.join(CD, "DonorQueue_v0.vi"): "81dba822", "tools/bench/donor_queue_v0.json": "15269b6c",
        os.path.join(CD, "D1_ring_p4s09_20261009_060515.vi"): "eb1d0f31", "tools/bench/graph_ring_p4s09_20261009_062044.json": "22f967b5",
        "tools/bench/plan_ring_p4_s09v18.json": "9d622c95", "docs/d1/ring-p5.md": "9c5ba571",
        "tools/bench/plan_ring_p5s01.json": "ed6ceb9e", "tools/bench/plan_ring_p5s01_in.json": "fabc4b9c",
        "tools/bench/errorlist_expected_D1_ring_p4s09_20261009_060515.json": "5146f980",
        os.path.join(CD, "D1_ring_p5s01a_20261009_101219.vi"): "2482fe7b", "tools/bench/graph_ring_p5s01a_20261009_103621.json": "bd67a511",
        "tools/bench/plan_ring_p5s01a.json": "ed62e8d6", "tools/bench/plan_ring_p5s01a_in.json": "80c3710e",
        "tools/bench/plan_ring_p5s01a_pred.json": "2e84eb2c", "tools/bench/plan_ring_p5s01a_licence.json": "323ac8e0",
        "tools/bench/prep_c154_a3_2b_session.json": "a50bf0a5", "tools/recipes/stage_d1_ring_p5s01a.py": "aee20128",
        "tools/recipes/stage_d1_ring_p5s01a_scratch.py": "3b02d9a7",
        "tools/bench/errorlist_expected_D1_ring_p5s01a_20261009_101219.json": "aee0d9fe", "docs/violation-decisions.md": "6497e984",
        "tools/bench/diag_c154_p5s01a_scratch.log": "", "tools/bench/diag_c154_a3_3_nodes.log": ""}
OUTF = os.path.join(ROOT, "tools", "bench", "prep_c154_a4_1_md5_before.json")
ab = lambda k: k if os.path.isabs(k) else os.path.join(ROOT, k)                                          # noqa: E731
md = lambda k: hashlib.md5(open(ab(k), "rb").read()).hexdigest()                                         # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                               # noqa: E731


def file_set():
    s = set(PINS)
    for pat in ("tools/recipes/stage_d1_ring_p4*.py", "tools/bench/plan_ring_p4*.json", "tools/recipes/stage_d1_ring_p5s01a*.py",
                "tools/bench/plan_ring_p5s01a*.json"):
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
