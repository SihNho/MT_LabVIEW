# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_165-2-1.md
# ---
r"""prep_c165_a2_1_close - card 165-2-1 part 3 (OFFLINE, read-only calls): validate tools/bench/cards/result_160-c3-2.json with
`py tools/protocol.py validate` and call guard_write.open_card_pins(tools/stagexec.py) (the live hook function, imported, never copied).
PREDICTION: validate rc 0 (status PASS; the schema enum is PASS/FAIL/BLOCKED/WAITING, SKIP refused by guard_write); open_card_pins lists no
'card 160-c3-2' entry. 2 PASS / 0 FAIL.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c165_a2_1_close.log -- py -u tools/bench/prep_c165_a2_1_close.py"""
import os, subprocess, sys                                                                    # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, B)
import prep_c156_a1_1_lib as L                                                               # noqa: E402
ROOT = L.ROOT
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
import guard_write as GW                                                                      # noqa: E402
gate = L.Gate(fatal_default=False)
RES = os.path.join(ROOT, "tools", "bench", "cards", "result_160-c3-2.json")
p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "protocol.py"), "validate", RES], capture_output=True, text=True, cwd=ROOT)
for ln in (p.stdout + p.stderr).splitlines():
    print("FACT VALIDATE " + ln, flush=True)
gate("V protocol validate result_160-c3-2.json rc {0}".format(p.returncode), p.returncode == 0, (p.stdout + p.stderr).strip()[:400])
pins = GW.open_card_pins(os.path.join(ROOT, "tools", "stagexec.py"))
print("FACT OPEN_CARD_PINS tools/stagexec.py -> {0}".format(pins), flush=True)
gate("P open_card_pins(tools/stagexec.py) has no 160-c3-2 entry", not [x for x in pins if "160-c3-2" in x], pins)
gate.ARTS.append({"path": "tools/bench/cards/result_160-c3-2.json", "md5": L.md5(RES)})
sys.exit(gate.result())
