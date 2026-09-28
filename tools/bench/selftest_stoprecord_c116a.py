r"""selftest_stoprecord_c116a.py - card 116-1 S1/S2 (PD230(g)(1), docs/violation-decisions.md device-failed 2026-09-28 07:05).
OFFLINE, no LabVIEW; the gate functions are called, nothing is executed. The store is STUBBED: one UNDISPOSED record for
tools/recipes/stage_d1_l2r1.py (review file absent -> state undisposed -> every build-class segment naming it refuses).
FOUND FIRST: selftest_stoprecord_table.py (generated DECISION_TABLE cases), _bgrun, _eqform, _supersession,
_offline_c107 (the marker-log replay pattern), selftest_c103d_hooks.py / selftest_c106d_tools.py (guard_bash.stop_gate).
MEASURED CAUSE (diag_c116a_replay.log): the `;` split already worked. :2615 was refused because `awk` had no read-only
credit; :2614 because its `$(basename $f .py)` made EXEC_PIPE_RE class EVERY segment build, and its `for f in <recipe>`
binding was a program named `for`.
PREDICTION CONTRACT
  M1/M2  material_marker.log:2614 / :2615, the literal commands (full text from the cycle-115 material transcript; the
         marker log itself cuts at 200 chars - the embedded text is checked against that prefix) -> ALLOWED
  P*     read-only shapes (awk, cut, a for-binding read by wc, a basename substitution) -> ALLOWED
  N*     a real launch -> REFUSED: after `;` / `&&` / lone `&`, plain py and bgrun `--`; through a for variable or an
         assignment; through $( ) (inner launch, or recipe text fed to py -c); awk system()/-f; sh -c; if/then; ( );
         xargs; time; PowerShell `$r = ...`; export
  G1/G2  guard_bash.stop_gate(M2) == 0, stop_gate(N3) == 2
  W0     the gate wrote no record
    py tools/bgrun.py --material --max-min 2 --log tools/bench/selftest_stoprecord_c116a.log -- py -u tools/bench/selftest_stoprecord_c116a.py
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
import protocol as P          # noqa: E402
import stop_record as SR      # noqa: E402

R = "tools/recipes/stage_d1_l2r1.py"
WRITES = []
SR.load_records = lambda: [{"recipe_path": R, "reviewed_sha256": "0" * 64, "review_file": "archive/peer/none-c116a.md",
                            "verdict": ["already-failed"], "released": None}]
SR.save_records = lambda recs: WRITES.append(len(recs))
G = []


def gate(ok, label, detail=""):
    G.append((bool(ok), label)); print("GATE %-74s %s %s" % (label, "PASS" if ok else "FAIL", str(detail)[:160]), flush=True)


def allow(c):
    return SR.check_command(c)[0]


M2614 = ('wc -l tools/recipes/stage_d1_l2r1.py; py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c115b_r1.log '
         '-- py -u tools/bench/diag_c115b_r1.py > /dev/null; grep "PASS  R1\\|FAIL  R1\\|SIM WIRES" tools/bench/diag_c115b_r1.log '
         '| tail -5 | cut -c1-250; for f in tools/recipes/stage_d1_l2r1.py tools/bench/diag_c115b_scratch.py; do b=$(basename $f .py); '
         'py tools/bgrun.py --material --max-min 5 --log tools/bench/${b}_dry.log -- py -u tools/stage_prerun.py --dry $f > /dev/null; '
         'grep "=== DRY" tools/bench/${b}_dry.log | tail -1 | cut -c1-200; done')
M2615 = "wc -l tools/recipes/stage_d1_l2r1.py; awk 'length > 250' tools/recipes/stage_d1_l2r1.py | wc -l"
ml = open(os.path.join(ROOT, "tools", "hooks", "material_marker.log"), encoding="utf-8", errors="replace").read().splitlines()
for tag, ln, lit in (("M1", 2614, M2614), ("M2", 2615, M2615)):
    logged = ml[ln - 1].split("STOPPED-RECIPE ", 1)[-1]
    gate("REFUSED" in ml[ln - 1] and lit.startswith(logged[:190]), "%s material_marker.log:%d is this refused command" % (tag, ln),
         logged[-50:])
    gate(allow(lit), "%s material_marker.log:%d ALLOWED now" % (tag, ln))
BG = "py tools/bgrun.py --material --max-min 5 --log tools/bench/x.log -- py -u "
POS = {"P1 wc && awk | wc": "wc -l %s && awk 'length > 250' %s | wc -l" % (R, R),
       "P2 awk alone": "awk '{print NR}' %s" % R,
       "P3 for-binding read by wc": "for f in %s; do wc -l $f; done" % R,
       "P4 cut | head": "cut -c1-80 %s | head -3" % R,
       "P5 basename substitution, echo": "b=$(basename %s .py); echo $b" % R,
       "P6 cd-prefixed read (Bash form)": 'cd "%s" && wc -l %s; awk \'NF\' %s | wc -l' % (ROOT.replace("\\", "/"), R, R),
       "P7 for-binding into stage_prerun --dry": "for f in %s; do %stools/stage_prerun.py --dry $f; done" % (R, BG)}
for k, c in POS.items():
    gate(allow(c), k + " ALLOWED")
NEG = {"N1 ; py -u": "wc -l %s; py -u %s" % (R, R),
       "N2 && py -u": "wc -l %s && py -u %s" % (R, R),
       "N3 ; bgrun --": "wc -l %s; %s%s" % (R, BG, R),
       "N4 && bgrun --": "grep x %s && %s%s" % (R, BG, R),
       "N5 lone & background": "wc -l %s & py -u %s" % (R, R),
       "N6 for variable launched": "for f in %s; do py -u $f; done" % R,
       "N7 assignment launched": "f=%s; py -u $f" % R,
       "N8 assignment via bgrun ${f}": 'f=%s; %s"${f}"' % (R, BG),
       "N9 $(echo R) as script": "py -u $(echo %s)" % R,
       "N10 $(py -u R) inside wc": "wc -l $(py -u %s)" % R,
       "N11 awk system()": "awk 'BEGIN{system(\"py -u %s\")}'" % R,
       "N12 awk -f": "awk -f %s" % R,
       "N13 cat | py -": "cat %s | py -" % R,
       "N14 py -c $(cat R)": 'py -c "$(cat %s)"' % R,
       "N15 nested substitution": "b=$(basename $(py -u %s))" % R,
       "N16 sh -c": 'sh -c "py -u %s"' % R,
       "N17 if/then": "if true; then py -u %s; fi" % R,
       "N18 subshell": "( py -u %s )" % R,
       "N19 xargs": "echo %s | xargs py -u" % R,
       "N20 time": "time py -u %s" % R,
       "N21 PowerShell assignment": '$r = "%s"; py -u $r' % R,
       "N22 export": "export f=%s; py -u $f" % R,
       "N23 transitive assignment": "f=%s; g=$f; py -u $g" % R,
       "N24 backtick": "wc -l `py -u %s`" % R}
for k, c in NEG.items():
    gate(not allow(c), k + " REFUSED")
import guard_bash as GB      # noqa: E402
GB.note = lambda *a, **k: None
gate(GB.stop_gate(M2615, "Bash") == 0, "G1 guard_bash.stop_gate(M2615) == 0")
gate(GB.stop_gate(NEG["N3 ; bgrun --"], "Bash") == 2, "G2 guard_bash.stop_gate(N3) == 2")
gate(not WRITES, "W0 the gate wrote no record", WRITES)
npass = sum(1 for g in G if g[0]); nfail = len(G) - npass
print(P.result_line(P.make_result(npass, nfail, next((g[1] for g in G if not g[0]), None))), flush=True)
sys.exit(0 if nfail == 0 else 1)
