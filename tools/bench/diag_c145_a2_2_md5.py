# ---
# labview: none
# hardware: none
# ---
r"""diag_c145_a2_2_md5 - card 145-a2-2, OFFLINE: md5 snapshot of everything the card must leave byte-identical (plan, pred,
recipes, stage scripts, stage tools). `before` writes tools/bench/diag_c145_a2_2_md5_before.json; `after` compares to it.
PREDICTION CONTRACT: after == before for every file (gate M1).
    py tools/bgrun.py --material --max-min 1 --log tools/bench/diag_c145_a2_2_md5_<mode>.log -- py -u tools/bench/diag_c145_a2_2_md5.py <mode>"""
import glob, hashlib, json, os, sys                                                         # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
os.chdir(ROOT)
FILES = sorted(set(["tools/bench/plan_ring_p4_s04v18.json", "tools/bench/plan_ring_p4_s04v18_pred.json", "tools/stagekit.py",
                    "tools/stagesim.py", "tools/stage_prerun.py", "tools/stagexec.py", "tools/errorlist_check.py",
                    "tools/bench/prep_c143_3_elrule.py", "tools/bench/errorlist_D1_ring_p4s04_20261007_215031_20261007_220024.json"]
                   + [p.replace("\\", "/") for p in glob.glob("tools/recipes/*.py") + glob.glob("tools/bench/stage_d1_ring_p4_s0*.py")
                      + glob.glob("tools/bench/plan_ring_p4_s05*") + glob.glob("tools/bench/stage_d1_ring_p4_s05*")]))
cur = dict((f, hashlib.md5(open(f, "rb").read()).hexdigest()) for f in FILES)
SNAP = "tools/bench/diag_c145_a2_2_md5_before.json"
mode = (sys.argv[1:] or ["before"])[0]
if mode == "before":
    json.dump(cur, open(SNAP, "w", encoding="utf-8"), indent=1)
    print("SNAPSHOT {0} files -> {1}".format(len(cur), SNAP), flush=True)
    print(protocol.result_line(protocol.make_result(1, 0, None, [])), flush=True)
    sys.exit(0)
before = json.load(open(SNAP, encoding="utf-8"))
diff = sorted(f for f in set(before) | set(cur) if before.get(f) != cur.get(f))
for f in sorted(cur):
    print("MD5 {0} {1} {2}".format(cur[f], "same" if f not in diff else "CHANGED", f), flush=True)
ok = not diff
print("GATE {0} | M1 {1} files byte-identical before/after | {2}".format("PASS" if ok else "FAIL", len(cur), diff), flush=True)
print(protocol.result_line(protocol.make_result(1 if ok else 0, 0 if ok else 1, None if ok else "M1", [])), flush=True)
sys.exit(0 if ok else 1)
