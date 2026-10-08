# ---
# labview: none
# hardware: none
# offline-args: after
# evidence: tools/bench/cards/brief_150-a3-4.md
# ---
"""Card 150-a3-4 after-record (OFFLINE, no LabVIEW). Prior art: a copy of tools/bench/prep_c150_a3_3.py (same pin list,
same hooks-tree listing, same four old self-tests, same violations.py capture) with the card-150-a3-4 inputs; the
edited files (tools/dispo.py, tools/bench/selftest_c150_a3_3.py) are reported, not pinned. Adds the cycle17 tally line.
Hooks are compared per file against tools/bench/prep_c150_a3_3_after.log (only material_marker.log may move).
PREDICTION: every pin == its md5; hook .py/.pyc md5 == prep_c150_a3_3_after.log; self-tests cycle_runner_retro 9/0 rc0,
audit_a9_witness 10/0 rc0, c116a_landed 14/4 rc1, stamp_window 15/0 rc0; violations.py 0 awaiting, cycle148 + cycle149
listed, retrospective-cycle17 listed under no slug (its old value, prep_c150_a3_3_before.log).
    py tools/bgrun.py --material --max-min 6 --log tools/bench/prep_c150_a3_4_after.log -- py -u tools/bench/prep_c150_a3_4.py after"""
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
PINS = {os.path.join(CD, "D1_ring_p4s06_20261008_174730.vi"): "569ffbf5",
        os.path.join(CD, "D1_ring_p4s05_20261008_002621.vi"): "3f9ac26b",
        os.path.join(CD, "D1_ring_p3b2b_20261002_130007.vi"): "39511877",
        os.path.join(CD, "D1_ring_p4s07_20261008_222709.vi"): "b3f86b32",
        os.path.join(ROOT, "tools", "stagekit.py"): "06b8d844",
        os.path.join(ROOT, "tools", "stagexec.py"): "1bab9cf9",
        os.path.join(ROOT, "tools", "gscript.py"): "1a80236e",
        os.path.join(ROOT, "tools", "elrule.py"): "a5ee7d5c",
        os.path.join(ROOT, "tools", "stage_prerun.py"): "c739eb86",
        os.path.join(ROOT, "tools", "vigraph.py"): "13be0847",
        os.path.join(ROOT, "tools", "stagesim.py"): "748bbf30"}
card = json.load(open(os.path.join(ROOT, "tools", "bench", "cards", "task_150-a3-4.json"), encoding="utf-8"))
EDITED = {"tools/dispo.py", "tools/bench/selftest_c150_a3_3.py"}
for inp in card["inputs"]:
    if inp["path"] not in EDITED:
        PINS[os.path.join(ROOT, inp["path"])] = inp["md5"]


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.exists(p) else "MISSING"


P = F = 0
first = None


def gate(label, ok, extra=""):
    global P, F, first
    P, F = P + ok, F + (not ok)
    first = first or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, extra), flush=True)


for p, pin in PINS.items():
    m = md5(p)
    gate("md5 {0} == {1}".format(os.path.basename(p), pin), m.startswith(pin), m)
for r in sorted(EDITED):
    print("FACT md5 {0} {1}".format(r, md5(os.path.join(ROOT, r))), flush=True)
prev = {}
for ln in open(os.path.join(ROOT, "tools", "bench", "prep_c150_a3_3_after.log"), encoding="utf-8", errors="replace"):
    mm = re.match(r"HOOK (\w+) (\S+)", ln)
    if mm:
        prev[mm.group(2)] = mm.group(1)
hooks = []
for d, _, fs in os.walk(os.path.join(ROOT, "tools", "hooks")):
    for fn in fs:
        hooks.append(os.path.relpath(os.path.join(d, fn), ROOT).replace("\\", "/"))
moved = []
for r in sorted(hooks):
    m = md5(os.path.join(ROOT, r))
    print("HOOK {0} {1}".format(m, r), flush=True)
    if prev.get(r) != m and not r.endswith("material_marker.log"):
        moved.append(r)
moved += [r for r in prev if r not in hooks]
gate("tools/hooks files == prep_c150_a3_3_after.log (material_marker.log excepted)", not moved and bool(prev),
     "moved %s; %d listed before, %d now" % (moved, len(prev), len(hooks)))
for st in ("selftest_cycle_runner_retro.py", "selftest_audit_a9_witness.py", "selftest_c116a_landed.py", "selftest_stamp_window.py"):
    cp = subprocess.run([sys.executable, "-u", os.path.join(ROOT, "tools", "bench", st)], cwd=ROOT, capture_output=True,
                        text=True, encoding="utf-8", errors="replace", timeout=240)
    out = cp.stdout + cp.stderr
    npass = len(re.findall(r"^\s*(?:GATE |CHECK )?PASS\b", out, re.M))
    nfail = len(re.findall(r"^\s*(?:GATE |CHECK )?FAIL\b", out, re.M))
    res = [ln for ln in out.splitlines() if ln.startswith("RESULT ") or re.search(r"\b\d+\s*/\s*\d+\b.*(pass|PASS)", ln)]
    print("SELFTEST {0} | rc {1} | PASS lines {2} | FAIL lines {3} | {4}".format(st, cp.returncode, npass, nfail,
                                                                               (res[-1] if res else out.strip().splitlines()[-1:])[:300]), flush=True)
cp = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "violations.py")], cwd=ROOT, capture_output=True, text=True,
                    encoding="utf-8", errors="replace", timeout=120)
print("VIOLATIONS rc {0} md5(stdout) {1}".format(cp.returncode, hashlib.md5(cp.stdout.encode()).hexdigest()), flush=True)
for ln in cp.stdout.splitlines():
    print("VIO | " + ln, flush=True)
print("CYCLE17 lines naming retrospective-cycle17: %d" % sum("retrospective-cycle17" in ln for ln in cp.stdout.splitlines()), flush=True)
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if F == 0 else "FAIL", "gates": {"pass": P, "fail": F},
                              "first_fail": first, "artefacts": []}), flush=True)
sys.exit(1 if F else 0)
