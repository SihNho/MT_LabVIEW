# ---
# labview: none
# hardware: none
# ---
r"""diag_c145_2_check - card 145-a1-2 before/after check (OFFLINE, no LabVIEW): the new plan f349c39a + pred 6a1faf56 (this card,
prep_c145_2_fix_b.log / prep_c145_2_pred.log) and the two recipes fe3f630c / f5e4bdf8 unchanged, s03 file 282301ca and bed 39511877
unchanged, no LabVIEW process. Same shape as diag_c145_1_check.py (card 145-a1-1) with this card's pins.
PREDICTION CONTRACT: 4 pins == md5s above; s03 == 282301ca...; bed == 395118775a52bc90073f4449b99f899d; tasklist has no LabVIEW.exe.
-> RESULT 7/0 (--after: the pred is rewritten on purpose by the census script -> 6/0)
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c145_2_check.log -- py -u tools/bench/diag_c145_2_check.py"""
import hashlib, os, subprocess, sys                                                # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
S03 = "D1_ring_p4s03_20261007_202957.vi"
PINS = {"tools/bench/plan_ring_p4_s04v18.json": "f349c39a17330531e688ff1f70ce426e",
        "tools/bench/plan_ring_p4_s04v18_pred.json": "6a1faf566bb938b62de18b5ce8968ef2",
        "tools/recipes/stage_d1_ring_p4_s04v18.py": "fe3f630c428e00143d54e5be0e18631d",
        "tools/recipes/stage_d1_ring_p4_s04v18_scratch.py": "f5e4bdf823cf206e7701a8673235046d"}
G = {"pass": 0, "fail": 0, "first": None}


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, d), flush=True)


AFTER = "--after" in sys.argv
for pth, want in PINS.items():
    got = md5(os.path.join(ROOT, pth))
    if AFTER and pth.endswith("_pred.json"):
        print("FACT pred rewritten by the census / EL scripts: now {0}".format(got), flush=True)
        continue
    gate("{0} md5 == {1}".format(pth, want[:8]), got == want, got)
s03 = md5(os.path.join(CD, S03))
gate("{0} md5 unchanged (282301ca)".format(S03), s03.startswith("282301ca"), s03)
bed = md5(os.path.join(CD, "D1_ring_p3b2b_20261002_130007.vi"))
gate("bed md5 unchanged", bed == "395118775a52bc90073f4449b99f899d", bed)
tl = subprocess.run(["tasklist"], capture_output=True, text=True).stdout
gate("no LabVIEW process", "labview" not in tl.lower(), [ln for ln in tl.splitlines() if "labview" in ln.lower()])
print("FACT s03 md5 {0}".format(s03), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
