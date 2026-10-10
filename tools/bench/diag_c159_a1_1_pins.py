# ---
# labview: none
# hardware: none
# ---
r"""diag_c159_a1_1_pins - card 159-a1-1: md5 pins before/after the read-only graph read (no LabVIEW, hashlib only).
Found before writing: diag_c158_a3_2_inv.py does the same with card-158 pins and logs outside this card's write globs, so a
4-pin hashlib list is used here. PREDICTION: adopted 94ffff94, s09 eb1d0f31, P5-1a 2482fe7b, P5-1 7f2582ae; mode 'before'
memory_model c87d170a; no LabVIEW process.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c159_a1_1_pins_<mode>.log -- py -u tools/bench/diag_c159_a1_1_pins.py <mode>"""
import hashlib, json, os, subprocess, sys                                                   # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
MODE = sys.argv[1] if len(sys.argv) > 1 else "before"
PINS = [(os.path.join(CD, "D1_ring_p5s02a_20261010_023239.vi"), "94ffff9413599d5153a5e6fb409294ab"),
        (os.path.join(CD, "D1_ring_p4s09_20261009_060515.vi"), "eb1d0f31"),
        (os.path.join(CD, "D1_ring_p5s01a_20261009_101219.vi"), "2482fe7b"),
        (os.path.join(CD, "D1_ring_p5s01_20261009_124542.vi"), "7f2582ae"),
        (os.path.join(ROOT, "tools", "bench", "adopted_scratch.jsonl"), "83e74ded")]
if MODE == "before":
    PINS.append((os.path.join(ROOT, "tools", "bench", "memory_model.json"), "c87d170a"))
ok = fail = 0
for p, pin in PINS:
    h = hashlib.md5(open(p, "rb").read()).hexdigest()
    good = h.startswith(pin)
    ok, fail = ok + good, fail + (not good)
    print("GATE {0} pin {1}: {2} {3}".format("PASS" if good else "FAIL", os.path.basename(p), pin, h), flush=True)
mm = os.path.join(ROOT, "tools", "bench", "memory_model.json")
print("FACT memory_model.json md5 {0}".format(hashlib.md5(open(mm, "rb").read()).hexdigest()), flush=True)
tl = subprocess.run(["tasklist"], capture_output=True, text=True).stdout
lv = [ln for ln in tl.splitlines() if "labview" in ln.lower()]
good = not lv
ok, fail = ok + good, fail + (not good)
print("GATE {0} no LabVIEW process: {1}".format("PASS" if good else "FAIL", lv), flush=True)
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if not fail else "FAIL",
                              "gates": {"pass": ok, "fail": fail}, "first_fail": None, "artefacts": []}), flush=True)
sys.exit(0 if not fail else 1)
