r"""selftest_stoprecord_offline_c107.py - card 107-1 B1 + C1, offline, no LabVIEW, nothing executed but the gate functions.
FOUND FIRST: selftest_stoprecord_table.py (generated table cases), selftest_stoprecord_bgrun.py (bgrun wrapper),
selftest_c106d_tools.py H2 (guard_bash stop_gate shape). This file only adds the stage_prerun --dry|--prerun rows.
B1 (stop_record.offline_checker, the device-failed repair of docs/violation-decisions.md 07:5x):
  S0     FABRICATED state (card 121-3): temp stop store with one undisposed record for the recipe, temp marker log
         holding the two refused lines verbatim; the live store and material_marker.log are never read
  R1/R2  the refused lines (were material_marker.log:2335 / :2338) REPLAYED (truncated tail token dropped) -> ALLOW
  P1..P5 top-level / bgrun / --prerun / cd-prefixed / guard_bash.stop_gate shapes of the dry -> ALLOW (stop_gate 0)
  N1..N8 launches of the recipe (direct, bgrun, && after a dry, newline after a dry, pipe to py, $( ), other program with
         --dry, stage_prerun WITHOUT --dry/--prerun) -> REFUSE; guard_bash.stop_gate(N1) == 2
  W0     the gate wrote nothing (save_records never called)
C1 (stage_prerun.launched_plan_runs newline split): L1 plan run on line 2 found (1); L2 continuation joined (1, the plan
  path right); L3 single line still 1; L5 comment-quote-across-newline shape found (1); L4 the PRE-FIX version (git
  show bf0f5b2^, pinned - HEAD moved past the fix) finds 0 on L5's command (the negative).
    py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_stoprecord_offline_c107.log -- py -u tools/bench/selftest_stoprecord_offline_c107.py
"""
import ast, os, re, shlex, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
import protocol as P          # noqa: E402
import stop_record as SR      # noqa: E402
import stage_prerun as SP     # noqa: E402

G = []
def gate(ok, label, detail=""):
    G.append((bool(ok), label)); print("GATE %-72s %s %s" % (label, "PASS" if ok else "FAIL", detail), flush=True)

WRITES = []
SR.save_records = lambda recs: WRITES.append(len(recs))
R = "tools/recipes/stage_d1_disp.py"
def allow(c): return SR.check_command(c)[0]

# --- FABRICATED STATE (card 121-3, 2026-09-28): the live store/marker log moved on (stage_d1_disp was released, the
# marker log grew), so N1..N9 turned green-to-red with no code change. The test now owns its state: a temp stop-record
# store holding ONE undisposed record for R (its review file carries no release line), and a temp marker log holding
# the two refused lines VERBATIM (were material_marker.log:2335 / :2338 on 2026-09-27). Nothing live is read.
import tempfile                                                      # noqa: E402
TMPD = tempfile.mkdtemp(prefix="c107_sr_")
REV = os.path.join(TMPD, "review_undisposed.md")
open(REV, "w", encoding="utf-8").write("# fabricated review\n\n## Answer\nPRIOR-ART: already-built\n\n## What was done with it\n(nothing)\n")
SR.STORE = os.path.join(TMPD, "stop_records.json"); SR.MARKER = os.path.join(TMPD, "stop_records.marker")
import json                                                          # noqa: E402
open(SR.STORE, "w", encoding="utf-8").write(json.dumps([{"recipe_path": R, "reviewed_sha256": "0" * 64, "review_file": REV,
                                                          "verdict": ["already-built"], "created_utc": "2026-09-27T00:00:00Z", "released": None}]))
_ARGV = ("py tools/bgrun.py --material --max-min 8 --log tools/bench/diag_c106e_dryB.log -- py -u tools/stage_prerun.py --dry "
         "tools/recipes/stage_d1_disp.py --no-record --json-out tools/bench/dia")
MLOG = os.path.join(TMPD, "material_marker.log")
open(MLOG, "w", encoding="utf-8").write("2026-09-27 07:32:25\tREFUSED\tSTOPPED-RECIPE " + _ARGV + "\n"
                                        "2026-09-27 07:35:36\tREFUSED\tSTOPPED-RECIPE " + _ARGV + "\n")
gate(SR.load_records() and not SR.check_command("py -u %s" % R)[0], "S0 fabricated store refuses a bare launch of R")

# --- B1: replay the two refused argv from the (fabricated) marker log
ml = open(MLOG, encoding="utf-8").read().splitlines()
for tag, ln in (("R1", 1), ("R2", 2)):
    line = ml[ln - 1]; argv = line.split("STOPPED-RECIPE ", 1)[-1]
    argv = argv.rsplit(" ", 1)[0] if len(argv) >= 190 else argv          # the logger cuts at 200 chars: drop the partial token
    gate("REFUSED" in line and "--dry" in argv and R in argv, "%s marker line %d is the refused dry" % (tag, ln), argv[-60:])
    gate(allow(argv), "%s replayed argv ALLOWED now" % tag)
root_q = '"%s"' % ROOT.replace("\\", "/")
POS = {"P1 top-level --dry --from-step 33": "py tools/stage_prerun.py --dry %s --from-step 33" % R,
       "P2 bgrun-wrapped --dry": "py tools/bgrun.py --material --max-min 8 --log tools/bench/x.log -- py -u tools/stage_prerun.py --dry %s --from-step 33" % R,
       "P3 --prerun --stop-after 40": "py -u tools/stage_prerun.py --prerun %s --stop-after 40" % R,
       "P4 cd-prefixed, backslash path": "cd %s && py tools\\stage_prerun.py --dry tools\\recipes\\stage_d1_disp.py" % root_q,
       "P5 MATERIAL=1 env prefix": "MATERIAL=1 py tools/bgrun.py --max-min 8 --log x.log -- py -u tools/stage_prerun.py --dry %s" % R}
for k, c in POS.items():
    gate(allow(c), k + " ALLOWED")
NEG = {"N1 bgrun launch of the recipe": "py tools/bgrun.py --material --max-min 40 --log x.log -- py -u %s" % R,
       "N2 direct launch": "py -u %s" % R,
       "N3 dry && launch": "py tools/stage_prerun.py --dry %s && py -u %s" % (R, R),
       "N4 dry <NL> launch": "py tools/stage_prerun.py --dry %s\npy -u %s" % (R, R),
       "N5 dry piped into py": "py tools/stage_prerun.py --dry %s | py -" % R,
       "N6 command substitution": "py tools/stage_prerun.py --dry $(py -u %s)" % R,
       "N7 other program with --dry": "py tools/other_tool.py --dry %s" % R,
       "N8 stage_prerun without --dry/--prerun": "py tools/stage_prerun.py --graph x.json %s" % R}
for k, c in NEG.items():
    gate(not allow(c), k + " REFUSED")
import guard_bash as GB      # noqa: E402
GB.note = lambda *a, **k: None
gate(GB.stop_gate(POS["P2 bgrun-wrapped --dry"], "Bash") == 0, "P6 guard_bash.stop_gate(P2) == 0")
gate(GB.stop_gate(NEG["N1 bgrun launch of the recipe"], "Bash") == 2, "N9 guard_bash.stop_gate(N1) == 2")
gate(not WRITES, "W0 the gate wrote no record", str(WRITES))

# --- C1: launched_plan_runs splits on newlines
c1 = "py -V\npy tools/stagexec.py run tools/bench/sim/disp/plan_disp.json"
f1 = SP.launched_plan_runs(c1)
gate(len(f1) == 1 and f1[0][1].replace("\\", "/").endswith("tools/bench/sim/disp/plan_disp.json"), "L1 plan run on line 2 found", str(f1))
f2 = SP.launched_plan_runs("py tools/stagexec.py \\\n run p.json")
gate(len(f2) == 1 and f2[0][1].endswith("p.json"), "L2 bash continuation joined", str(f2))
gate(len(SP.launched_plan_runs("py tools/stagexec.py run p.json")) == 1, "L3 single line still found")
# The shape HEAD misses (review archive/peer/2026-09-27-c107a-l4-selftest_stoprecord_offline_c107.md:62-76, ACCEPTED): a
# real quote that bash does not treat as one - inside a bash COMMENT - spans the newline; bash runs line 2, shlex groups it
# into one token. Run 1 used the plain two-line shape for L4, which HEAD also finds (it scans every py token); the escaped
# quote shape is found by HEAD too (non-posix shlex ignores quotes inside words, diag_c106e_oldcode.log:12).
c4 = 'echo x # "a\npy tools/stagexec.py run tools/bench/sim/disp/plan_disp.json\n# "'
gate(len(SP.launched_plan_runs(c4)) == 1, "L5 comment-quote shape: plan run on line 2 found", str(len(SP.launched_plan_runs(c4))))
c6 = 'git commit -m "notes\npy tools/stagexec.py run tools/bench/sim/disp/plan_disp.json\n"'
print("INFO F1 known cost (review :97-100): quoted multi-line argument, new finds %d (bash runs 0)" % len(SP.launched_plan_runs(c6)), flush=True)
# Baseline PINNED to the commit before the fix (card 121-3): `HEAD` moved past the fix at bf0f5b2 (cycle 107), after
# which "HEAD misses it" could never hold again. History is immutable; HEAD is not.
BASE = "bf0f5b2^"
head = subprocess.run(["git", "show", BASE + ":tools/stage_prerun.py"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout
fn = next(n for n in ast.parse(head).body if isinstance(n, ast.FunctionDef) and n.name == "launched_plan_runs")
ns = {"re": re, "shlex": shlex, "os": os, "STAGEXEC": SP.STAGEXEC, "STAGEXEC_RE": SP.STAGEXEC_RE, "ROOT": SP.ROOT}
exec(compile(ast.Module(body=[fn], type_ignores=[]), BASE + ":launched_plan_runs", "exec"), ns)
gate(ns["launched_plan_runs"](c4) == [], "L4 pre-fix (%s) launched_plan_runs misses the comment-quote line 2 (negative)" % BASE, str(ns["launched_plan_runs"](c4)))
npass = sum(1 for g in G if g[0]); nfail = len(G) - npass
print(P.result_line(P.make_result(npass, nfail, next((g[1] for g in G if not g[0]), None))), flush=True)
sys.exit(0 if nfail == 0 else 1)
