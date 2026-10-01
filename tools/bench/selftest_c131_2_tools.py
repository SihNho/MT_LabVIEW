"""selftest_c131_2_tools - card 131-2 self-test of its three hook fixes. OFFLINE: imports the hooks and calls their
functions on literal commands and on throw-away scripts in %TEMP%; guard_cycle.main is fed one JSON payload in a child
process. No LabVIEW, no COM, nothing dispatched.
  G1-G9  guard_peer v2 offline classification (fp-22, fp-24; docs/violation-decisions.md device-failed 2026-10-02 04:52)
  P1-P8  protocol.peer_role_of on read-only commands (fp-25) and real dispatches
  C1-C8  guard_cycle.BUILD_RE command position (cp a.py tools/recipes/b.py is not a build; py tools/recipes/x.py is)
PREDICTION: every gate PASS."""
import json, os, subprocess, sys, tempfile                                          # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
import protocol as P                                                               # noqa: E402
import guard_peer as gp                                                            # noqa: E402
import guard_cycle as gc                                                           # noqa: E402
res = []


def gate(name, ok, det=""):
    res.append(bool(ok))
    print("{0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(det)[:400]), flush=True)


def tmp_script(body):
    fd, p = tempfile.mkstemp(prefix="c131_2_", suffix=".py")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write("import os, sys\nsys.path.insert(0, %r)\n%s\n" % (os.path.join(ROOT, "tools"), body))
    return p


T = lambda rel: os.path.join(ROOT, rel)                                            # noqa: E731
# ---------------------------------------------------------------- guard_peer
gate("G1 fp-24 script selftest_x10_c130_1.py (imports stage_prerun, calls x10_probe->dry) is offline",
     not gp.script_touches_labview(T("tools/bench/selftest_x10_c130_1.py")))
gate("G2 fp-22 scripts (selftest_stoprecord_c130_2, diag_c130_2_baseline: import guard_bash) are offline",
     not gp.script_touches_labview(T("tools/bench/selftest_stoprecord_c130_2.py"))
     and not gp.script_touches_labview(T("tools/bench/diag_c130_2_baseline.py")))
gate("G3 a recipe (stage_d1_ring_p3a.py, imports stagekit) and stagexec.py launched still reach LabVIEW",
     gp.script_touches_labview(T("tools/recipes/stage_d1_ring_p3a.py")) and gp.script_touches_labview(T("tools/stagexec.py")))
cases = [
    ("G4 import stagexec + SX.LVBackend(...) reaches", "import stagexec as SX\nSX.LVBackend(None, [])", True),
    ("G5 from stagexec import lv_run + call reaches", "from stagexec import lv_run\nlv_run('x.json')", True),
    ("G6 import stagexec + SX.compile_plan only is offline", "import stagexec as SX\nSX.compile_plan({})", False),
    ("G7 import stage_prerun + SP.dry (COM stubbed) is offline", "import stage_prerun as SP\nSP.dry('r.py')", False),
    ("G8 function-local `import gscript` in the LAUNCHED script reaches", "def f():\n    import gscript\nf()", True),
    ("G9 unparseable launched script fails closed", "def (:\n", True),
]
for name, body, want in cases:
    p = tmp_script(body)
    try:
        got = gp.script_touches_labview(p)
    finally:
        os.remove(p)
    gate(name, got is want, "got %s" % got)
cmd24 = "py tools/bgrun.py --material --max-min 6 --log tools/bench/selftest_x10_c130_3.log -- py -u tools/bench/selftest_x10_c130_1.py"
gate("G10 offline_command(fp-24 argv) True; stagexec run plan False",
     gp.offline_command(cmd24) and not gp.offline_command("py -u tools/stagexec.py run tools/bench/plan_ring_p3a.json"))
gate("G11 selftest_exempt(fp-22 blamed log start line) True",
     gp.selftest_exempt("BGRUN START x limit 3.0 min: py -u tools/bench/selftest_stoprecord_c130_2.py"))
gate("G12 fp-26 script selftest_stagesim_tunnel_naming.py (card 131-1) is offline",
     not gp.script_touches_labview(T("tools/bench/selftest_stagesim_tunnel_naming.py")))
# ---------------------------------------------------------------- gate_fp.note (P4: open entries carry a note)
import gate_fp as GF                                                               # noqa: E402
fd, qp = tempfile.mkstemp(prefix="c131_2_q_", suffix=".jsonl")
with os.fdopen(fd, "w", encoding="utf-8") as f:
    f.write(json.dumps({"id": "fp-1", "status": "open", "gate": "guard_peer", "cmd": "x"}) + "\n")
e1, _w = GF.note("fp-1", "stays open: owner card 131-1", path=qp)
e2, w2 = GF.note("fp-9", "x", path=qp)
rows = GF.read_queue(qp)
os.remove(qp)
try:
    os.remove(qp + ".lock")
except OSError:
    pass
gate("N1 gate_fp.note sets the note, keeps status open; unknown id refused",
     e1 is not None and rows[0].get("note") == "stays open: owner card 131-1" and rows[0].get("status") == "open"
     and e2 is None, "%r / %r" % (rows[0], w2))
# ---------------------------------------------------------------- protocol.peer_role_of (fp-25)
pr = [
    ("P1 md5sum naming peer.ps1 is no dispatch", "md5sum tools/protocol.py tools/peer.ps1 tools/hooks/guard_bash.py", None),
    ("P2 grep | head naming peer.ps1", "grep -n Role tools/peer.ps1 | head -5", None),
    ("P3 Get-FileHash / cat / wc", "Get-FileHash tools/peer.ps1; cat tools/peer.ps1 | wc -l", None),
    ("P4 grep naming retrospective.py", "grep -n DECISIONS tools/retrospective.py", None),
    ("P5 bgrun -> powershell -File peer.ps1 -Role hypothesis", "py tools/bgrun.py --max-min 14 --log tools/bench/peer_x.log -- "
     "powershell -NoProfile -File tools/peer.ps1 -Agent claude -Role hypothesis -Slug x -TaskFile t.md", "hypothesis"),
    ("P6 md5sum; then & peer.ps1 -Kind fact", "md5sum tools/peer.ps1; & .\\tools\\peer.ps1 -Kind fact -Slug x -Task q", "fact"),
    ("P7 py prior_art_review.py", "py tools/bgrun.py --max-min 20 --log l -- py tools/prior_art_review.py --plan x", "priorart"),
]
for name, cmd, want in pr:
    got = P.peer_role_of(cmd)
    gate(name, got == want, "got %r" % got)
card = {"id": "c131-2-fixture", "flags": {"labview": "none", "peers": [], "write": ["tools/bench/x*"]}}
gate("P8 check_command(peers []) allows md5sum of peer.ps1, refuses a real dispatch",
     P.check_command(card, pr[0][1]) is None and P.check_command(card, pr[4][1]) is not None,
     "%r / %r" % (P.check_command(card, pr[0][1]), P.check_command(card, pr[4][1])))
# ---------------------------------------------------------------- guard_cycle.BUILD_RE
def g1(cmd):
    m = gc.BUILD_RE.search(cmd)
    return m.group(1) if m else None


bc = [
    ("C1 cp a.py tools/recipes/b.py is not a build", "cp a.py tools/recipes/b.py", None),
    ("C2 md5sum two recipe paths is not a build", "md5sum tools/recipes/a.py tools/recipes/b.py", None),
    ("C3 py tools/recipes/x.py is a build", "py tools/recipes/x.py", "tools/recipes/x.py"),
    ("C4 bgrun -- py -u recipe is a build", "py tools/bgrun.py --material --max-min 5 --log l -- py -u tools/recipes/x.py",
     "tools/recipes/x.py"),
    ("C5 interpreter by path is a build", "C:\\Python312\\python.exe -u tools/recipes/x.py", "tools/recipes/x.py"),
    ("C6 py OTHER script naming a recipe stays a build (fail closed)", "py tools/x.py tools/recipes/r.py", "tools/recipes/r.py"),
    ("C7 stage_prerun --dry recipe matches (released by offline_only)", "py -u tools/stage_prerun.py --dry tools/recipes/r.py",
     "tools/recipes/r.py"),
]
for name, cmd, want in bc:
    got = g1(cmd)
    gate(name, got == want, "got %r" % got)
gate("C7b offline_only(stage_prerun --dry recipe) True", gc.offline_only(bc[6][1]))
cp = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "hooks", "guard_cycle.py")],
                    input=json.dumps({"tool_input": {"command": "cp a.py tools/recipes/b.py"}}), capture_output=True,
                    text=True, cwd=ROOT, timeout=60)
gate("C8 guard_cycle.main on `cp a.py tools/recipes/b.py` exits 0 (not gated)", cp.returncode == 0,
     "rc %s %s" % (cp.returncode, cp.stderr[:200]))
print("=== GATES: %d pass / %d fail" % (sum(res), len(res) - sum(res)))
print(P.result_line(P.make_result(sum(res), len(res) - sum(res), None if all(res) else "see FAIL lines")), flush=True)
