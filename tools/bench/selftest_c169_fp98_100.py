# ---
# labview: none
# hardware: none
# ---
r"""selftest_c169_fp98_100 - cards 169-a2-2 / 169-a2-3: the fixes for gate-fp fp-100 (stage_prerun.find_graph skips
post-edit copies stamped with the bed md5) and fp-99 (protocol.check_command run_vi on the command without read-only
segments), plus what is true of X5 now that the fp-98 edit was REVERTED (169-a2-2: it broke c115c T8; fp-98 stays open,
X5 unchanged). No LabVIEW, no COM: stage_prerun --dry/--prerun stub COM; one temp copy of the 167 script is written as
tools/bench/diag_c169_a2_3_tmp_rbwextra.py (the script imports from its own folder) and deleted at the end.

WHAT EXISTED: selftest_stage_prerun_c115c.py / c128 cover X5's DELETE and RLE classes, selftest_stage_prerun_graphload.py
covers find_graph shapes, selftest_protocol.py covers check_command; none covers RBW, a post-edit note or a grep of a
driver. This file adds those cases only.

PREDICTION CONTRACT
  A1 x5_count(['rbw_method410'], [], {}) ok, detail 'ops 0 vs plan wire rows 0'; A2 + 'connect_wire' -> FAIL (ops 1 vs 0)
  A3 --prerun of the 167 RBW script as it is (op label 'rbw_method410'): X5 PASS 'ops 0 vs plan wire rows 0', X10 PASS
  A4 a copy with one extra plan-less Stage._op('connect_wire') -> X5 FAIL 'ops 1 vs plan wire rows 0'
  B1 find_graph(75773b0d, plan_base_graphs(168 script)) -> graph_ring_p5s02e_20261012_173009.json (file md5 7815af09)
  B2 the 4 graph_ring_p6* files stamped 75773b0d with an 'IN-MEMORY copy after' note are in FIND_SKIPPED as post-edit
  B3 older stage tools/recipes/stage_d1_ring_p5s02a.py: find_graph(7f2582ae, its plan bases) == the graph its stored dry
     log names (diag_c157_a1_2_dry.log:19, graph_ring_p5s01_20261009_125622.json)
  B4 --dry of tools/bench/diag_c168_a1_2_rbwdel.py: graph p5s02e, R1 and D1 not FAIL, DRY PASS(-UNVERIFIED), rc 0
  C1 check_command(run_vi false) accepts the fp-99 grep of the v5 driver; C2 refuses `py -u <v5 driver>`, the bgrun form
     and `cat <driver> | py -`
    py tools/bgrun.py --material --max-min 10 --log tools/bench/selftest_c169_fp98_100.log -- py -u tools/bench/selftest_c169_fp98_100.py
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import protocol        # noqa: E402
import stage_prerun as SP  # noqa: E402

BEDM = "75773b0ded2a08586bb1a542ddda5af6"
S167 = os.path.join(HERE, "diag_c167_a1_1_rbw.py")
S168 = os.path.join(HERE, "diag_c168_a1_2_rbwdel.py")
OLD_STAGE = os.path.join(TOOLS, "recipes", "stage_d1_ring_p5s02a.py")
OLD_LOG = os.path.join(HERE, "diag_c157_a1_2_dry.log")
DRIVER = "tools/bench/drive_original_copy_v5.py"
RES = []


def check(label, ok, detail=""):
    RES.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:300]))


def prerun(mode, script):
    """-> (rc, stdout) of `stage_prerun --<mode> <script> --no-record` in a child process (COM stubbed by stage_prerun)."""
    p = subprocess.run([sys.executable, "-u", os.path.join(TOOLS, "stage_prerun.py"), "--" + mode, script, "--no-record"],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    return p.returncode, p.stdout + p.stderr


def gate_line(out, label):
    return next((ln.strip() for ln in out.splitlines() if re.match(r"\s*(PASS|FAIL|UNVERIFIED)\s+" + re.escape(label), ln)), "")


# ---------------------------------------------------------------- X5 as it stands (fp-98 edit reverted, fp-98 open)
ok, det = SP.x5_count(["rbw_method410"], [], {})
check("A1 x5_count of the 167 label 'rbw_method410', no plan rows -> PASS 'ops 0 vs plan wire rows 0'",
      ok and det.startswith("ops 0 vs plan wire rows 0"), det)
ok, det = SP.x5_count(["rbw_method410", "connect_wire"], [], {})
check("A2 x5_count + a plan-less connect_wire -> FAIL 'ops 1 vs plan wire rows 0'",
      not ok and det.startswith("ops 1 vs plan wire rows 0"), det)
rc, out = prerun("prerun", S167)
x5, x10 = gate_line(out, "X5"), gate_line(out, "X10 predicted")
check("A3 prerun of the 167 script as it is: X5 PASS 'ops 0 vs plan wire rows 0', X10 PASS",
      x5.startswith("PASS") and "ops 0 vs plan wire rows 0" in x5 and x10.startswith("PASS") and "N 1 ops" in out,
      "rc {0} | {1} | {2}".format(rc, x5[:90], x10[:80]))
src = open(S167, encoding="utf-8").read()
assert src.count('s._op("rbw_method410"') == 1, "167 script op label moved"
extra = src.replace('    rb = rec["result"]\n',
                    '    s._op("connect_wire", lambda: None, "selftest c169: an unplanned wiring op")\n    rb = rec["result"]\n', 1)
assert extra != src, "167 script anchor line moved"
TMP = os.path.join(HERE, "diag_c169_a2_3_tmp_rbwextra.py")
try:
    with open(TMP, "w", encoding="utf-8", newline="") as f:
        f.write(extra)
    rc, out = prerun("prerun", TMP)
    x5 = gate_line(out, "X5")
    check("A4 the 167 script + one plan-less Stage._op('connect_wire') -> X5 FAIL 'ops 1 vs plan wire rows 0'",
          x5.startswith("FAIL") and "ops 1 vs plan wire rows 0" in x5, "rc {0} | {1}".format(rc, x5[:120]))
finally:
    if os.path.isfile(TMP):
        os.remove(TMP)
check("A5 temp copy deleted", not os.path.isfile(TMP), TMP)

# ---------------------------------------------------------------- fp-100: find_graph skips post-edit copies
g = SP.find_graph(BEDM, SP.plan_base_graphs(S168))
check("B1 find_graph(75773b0d) for the 168 script -> graph_ring_p5s02e_20261012_173009.json, file md5 7815af09",
      g and os.path.basename(g) == "graph_ring_p5s02e_20261012_173009.json" and SP.md5(g).startswith("7815af09"), g)
post = sorted(os.path.basename(p) for p, why in SP.FIND_SKIPPED if why.startswith("post-edit copy"))
check("B2 the 4 graph_ring_p6* post-edit copies stamped 75773b0d are skipped as post-edit",
      len(post) == 4 and all(n.startswith("graph_ring_p6") for n in post), post)
m = re.search(r"DRY graph JSON for input md5 ([0-9a-f]{32})\s+(\S.*\.json)", open(OLD_LOG, encoding="utf-8", errors="replace").read())
g2 = SP.find_graph(m.group(1), SP.plan_base_graphs(OLD_STAGE))
check("B3 older stage stage_d1_ring_p5s02a.py: find_graph({0}) == its stored dry log's graph {1}".format(
      m.group(1)[:8], os.path.basename(m.group(2))), g2 and os.path.basename(g2) == os.path.basename(m.group(2)), g2)
rc, out = prerun("dry", S168)
r1, d1 = gate_line(out, "R1 "), gate_line(out, "D1 ")
check("B4 --dry of the 168 script: graph p5s02e, R1 and D1 not FAIL, DRY PASS, rc 0",
      rc == 0 and "graph_ring_p5s02e_20261012_173009.json" in out and r1 and d1 and not r1.startswith("FAIL")
      and not d1.startswith("FAIL") and "=== DRY PASS" in out, "rc {0} | {1} | {2}".format(rc, r1[:60], d1[:60]))

# ---------------------------------------------------------------- fp-99: run_vi judged without read-only segments
CARD = {"id": "selftest-c169", "flags": {"labview": "build", "gui": True, "hardware": "gate", "run_vi": False,
                                          "write": [], "status_edit": False, "git_commit": False, "peers": []}}
why = protocol.check_command(CARD, "grep -n -i motor " + DRIVER)
check("C1 check_command accepts the fp-99 read-only grep of the v5 driver", why is None, why)
for c in ("py -u " + DRIVER,
          "py tools/bgrun.py --material --max-min 5 --log tools/bench/x.log -- py -u " + DRIVER,
          "cat " + DRIVER + " | py -"):
    why = protocol.check_command(CARD, c)
    check("C2 still refused as a VI run: " + c[:60], why and "run_vi" in why, why)

npass = sum(1 for _l, o in RES if o)
first = next((l for l, o in RES if not o), None)
print(protocol.result_line({"status": "PASS" if first is None else "FAIL", "gates": {"pass": npass, "fail": len(RES) - npass},
                            "first_fail": first, "artefacts": []}))
sys.exit(0 if first is None else 1)
