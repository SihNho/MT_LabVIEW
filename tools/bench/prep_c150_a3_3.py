# ---
# labview: none
# hardware: none
# offline-args: before
# evidence: tools/bench/cards/brief_150-a3-3.md
# ---
"""Card 150-a3-3 before/after record (OFFLINE, no LabVIEW). argv[1] = 'before' | 'after'.
Prior art: COPY of the pin list of tools/bench/diag_c150_a3_2_inv.py (+ s07 adopted b3f86b32) and the brief-150-a3-3 step-6
list; tools/hooks/** tree listed file by file (md5 per file + one tree md5). Old self-tests of the three edited files, found
by grep: selftest_cycle_runner_retro.py (retro_undisposed), selftest_audit_a9_witness.py + selftest_c116a_landed.py (audit A9),
selftest_stamp_window.py (violations._retro_stamp). selftest_c108e_tools.py is `labview: read` -> not run under this card.
`py tools/violations.py` output is recorded verbatim (lines naming cycle148/149).
PREDICTION: every pin == its md5; each self-test's rc and PASS/FAIL counts recorded (in 'after' they equal 'before').
    py tools/bgrun.py --material --max-min 6 --log tools/bench/prep_c150_a3_3_<mode>.log -- py -u tools/bench/prep_c150_a3_3.py <mode>"""
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
MODE = sys.argv[1] if len(sys.argv) > 1 else "before"
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
card = json.load(open(os.path.join(ROOT, "tools", "bench", "cards", "task_150-a3-3.json"), encoding="utf-8"))
EDITED = {"tools/violations.py", "tools/cycle_runner.py", "tools/audit_cycle.py"}
for inp in card["inputs"]:
    if MODE == "before" or inp["path"] not in EDITED:
        PINS[os.path.join(ROOT, inp["path"])] = inp["md5"]


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.exists(p) else "MISSING"


if MODE == "snapshot":     # the OLD code for selftest_c150_a3_3.py, copied byte for byte before any edit
    for r in sorted(EDITED):
        src = open(os.path.join(ROOT, r), "rb").read()
        dst = os.path.join(ROOT, "tools", "bench", "prep_c150_a3_3_old_" + os.path.basename(r)[:-3] + ".txt")
        open(dst, "wb").write(src)
        print("SNAP {0} -> {1} md5 {2}".format(r, os.path.relpath(dst, ROOT), hashlib.md5(src).hexdigest()), flush=True)
    sys.exit(0)
P = F = 0
first = None
for p, pin in PINS.items():
    m = md5(p)
    ok = m.startswith(pin)
    P, F = P + ok, F + (not ok)
    first = first or (None if ok else os.path.basename(p))
    print("GATE {0} | md5 {1} == {2} | {3}".format("PASS" if ok else "FAIL", os.path.basename(p), pin, m), flush=True)
for r in sorted(EDITED) + ["tools/dispo.py"]:
    print("FACT md5 {0} {1}".format(r, md5(os.path.join(ROOT, r))), flush=True)
tree = hashlib.md5()
hooks = []
for d, _, fs in os.walk(os.path.join(ROOT, "tools", "hooks")):
    for fn in fs:
        hooks.append(os.path.relpath(os.path.join(d, fn), ROOT).replace("\\", "/"))
for r in sorted(hooks):
    m = md5(os.path.join(ROOT, r))
    tree.update((r + " " + m + "\n").encode())
    print("HOOK {0} {1}".format(m, r), flush=True)
print("FACT tools/hooks tree md5 {0} ({1} files)".format(tree.hexdigest(), len(hooks)), flush=True)
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
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if F == 0 else "FAIL", "gates": {"pass": P, "fail": F},
                              "first_fail": first, "artefacts": []}), flush=True)
sys.exit(1 if F else 0)
