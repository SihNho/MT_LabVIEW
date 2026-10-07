# ---
# labview: none
# hardware: none
# ---
r"""diag_c145_a2_1_check - card 145-a2-1 step 7 (OFFLINE, read-only): pins after the card's work - s03 282301ca, bed 39511877, adopted
s04 95e408ff, subVIs 6fcf153f / 0295a8d3, plan f349c39a, pred a2bbc8bf, recipes fe3f630c / f5e4bdf8 (prefixes, diag_c145_2_facts.md),
abb76d41 still present (NOT deleted: step 6 runs only after requiredness succeeded), no LabVIEW process.
PREDICTION: every pin holds -> RESULT n/0.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c145_a2_1_check.log -- py -u tools/bench/diag_c145_a2_1_check.py"""
import hashlib, os, subprocess, sys                                                          # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
B = os.path.join(ROOT, "tools", "bench")
R = os.path.join(ROOT, "tools", "recipes")
PINS = [(os.path.join(CD, "D1_ring_p4s03_20261007_202957.vi"), "282301ca"), (os.path.join(CD, "D1_ring_p3b2b_20261002_130007.vi"), "39511877"),
        (os.path.join(CD, "D1_ring_p4s04_20261007_215031.vi"), "95e408ff"), (os.path.join(CD, "RingPickSlot_v0.vi"), "6fcf153f"),
        (os.path.join(CD, "RingSeqCheck_v0.vi"), "0295a8d3"), (os.path.join(CD, "D1_ring_p4s04_20261007_212230.vi"), "abb76d41"),
        (os.path.join(B, "plan_ring_p4_s04v18.json"), "f349c39a"), (os.path.join(B, "plan_ring_p4_s04v18_pred.json"), "a2bbc8bf"),
        (os.path.join(R, "stage_d1_ring_p4_s04v18.py"), "fe3f630c"), (os.path.join(R, "stage_d1_ring_p4_s04v18_scratch.py"), "f5e4bdf8")]
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:400]), flush=True)


for p, m in PINS:
    got = hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.isfile(p) else "MISSING"
    gate("pin {0} {1}".format(os.path.basename(p), m), got.startswith(m), got)
tl = subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()
gate("no LabVIEW process", "labview" not in tl, [ln for ln in tl.splitlines() if "labview" in ln])
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
