# ---
# labview: none
# hardware: none
# ---
r"""diag_c147_a1_1_check - card 147-a1-1 steps 1/6 (OFFLINE, no LabVIEW): md5 of the card inputs == card; work copy
claudeDev\D1_ring_p4s05_20261008_002621.vi == 3f9ac26b; protected s04 95e408ff, s03 282301ca, bed 39511877 unchanged; no LabVIEW
process. Arg `before` or `after` (after: the card inputs memory_model.json / adopted file are allowed to have changed; the work copy
md5 and the protected md5s must not). COPIED in form from diag_c146_a1_4_check (gate/RESULT skeleton).
PREDICTION: every gate PASS.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c147_a1_1_check_<when>.log -- py -u tools/bench/diag_c147_a1_1_check.py <when>"""
import hashlib, json, os, subprocess, sys                                                   # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
WHEN = (sys.argv[1:] or ["before"])[0]
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.isfile(p) else "MISSING"   # noqa: E731
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)


card = json.load(open(os.path.join(ROOT, "tools", "bench", "cards", "task_147-a1-1.json"), encoding="utf-8"))
for i in card["inputs"]:
    if WHEN == "after" and i["path"].endswith("memory_model.json"):
        continue
    got = md5(os.path.join(ROOT, i["path"]))
    gate("IN {0} md5 == card".format(i["path"]), got == i["md5"], got)
PROT = {"D1_ring_p4s05_20261008_002621.vi": "3f9ac26b69179eb53c202d90407ce7ee",
        "D1_ring_p4s04_20261007_215031.vi": "95e408ff14a406edd3f16b32ba7324f1",
        "D1_ring_p4s03_20261007_202957.vi": "282301caba152e4d16640dae0611972e",
        "D1_ring_p3b2b_20261002_130007.vi": "395118775a52bc90073f4449b99f899d"}
for n, m in PROT.items():
    p = os.path.join(CD, n)
    got = md5(p)
    gate("P {0} md5 == {1} ({2} B)".format(n, m[:8], os.path.getsize(p) if os.path.isfile(p) else 0), got == m, got)
tl = subprocess.run(["tasklist"], capture_output=True, text=True).stdout
gate("L no LabVIEW process", "labview" not in tl.lower(), [ln for ln in tl.splitlines() if "labview" in ln.lower()])
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
