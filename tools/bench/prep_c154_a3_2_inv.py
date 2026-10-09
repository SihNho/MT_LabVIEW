# ---
# labview: none
# hardware: none
# offline-args: --before
# evidence: tools/bench/cards/brief_154-a3-2.md
# ---
r"""prep_c154_a3_2_inv - card 154-a3-2 step 8 (offline, json/md5 only, no LabVIEW, no COM): the protected md5s BEFORE and AFTER.
`--before` checks the brief's pins (prefixes) and writes the full table prep_c154_a3_2_md5_before.json (pins + every stored P4 recipe /
plan / pred / licence + tools/hooks/**); `--after` re-reads the same set and compares it with that file. tools/hooks/*.log files are
written by the hooks themselves (material_marker.log, card 154-a3-1 facts :41) and are printed as a FACT, not gated.
Existing: the copy pattern of diag_c154_a3_1_census.py PINS / md() (no invariant helper exists in tools/ for an arbitrary file set).
PREDICTION: B pins match; A every file in the before table has the same md5 (non-log), no file added or removed.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c154_a3_2_inv_before.log -- py -u tools/bench/prep_c154_a3_2_inv.py --before"""
import glob, hashlib, json, os, sys                                                                       # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
PINS = {"tools/stagekit.py": "604529e8", "tools/addrcheck.py": "207beb0d", "tools/stagexec.py": "1bab9cf9", "tools/stagesim.py": "78b8d5a1",
        "tools/gscript.py": "1a80236e", "tools/vigraph.py": "a7eb58c7", "tools/stage_prerun.py": "9decb20f", "tools/bench/memory_model.json": "6f2b5687",
        os.path.join(CD, "DonorQueue_v0.vi"): "81dba822", "tools/bench/donor_queue_v0.json": "15269b6c",
        os.path.join(CD, "D1_ring_p4s09_20261009_060515.vi"): "eb1d0f31", "tools/bench/graph_ring_p4s09_20261009_062044.json": "22f967b5",
        "tools/bench/plan_ring_p4_s09v18.json": "9d622c95", "tools/bench/plan_ring_p4_s09v18_pred.json": "85dbb0ba",
        "tools/bench/plan_ring_p4_s09v18_licence.json": "6d003b8d", "tools/recipes/stage_d1_ring_p4_s09v18.py": "4be3ff28",
        "tools/recipes/stage_d1_ring_p4_s09v18_scratch.py": "b1f6a87c", "docs/d1/ring-p5.md": "9c5ba571"}
OUTF = os.path.join(ROOT, "tools", "bench", "prep_c154_a3_2_md5_before.json")
ab = lambda k: k if os.path.isabs(k) else os.path.join(ROOT, k)                                          # noqa: E731
md = lambda k: hashlib.md5(open(ab(k), "rb").read()).hexdigest()                                         # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                               # noqa: E731


def file_set():
    s = set(PINS)
    for pat in ("tools/recipes/stage_d1_ring_p4*.py", "tools/bench/plan_ring_p4*.json"):
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
