r"""selftest_stoprecord_c130_2.py - card 130-2 item 1, gate-fp fp-22 (docs/violation-decisions.md `## device-failed -
2026-10-02 02:57` (2)). OFFLINE, no LabVIEW, nothing executed: guard_bash.stop_gate is called with the store STUBBED
(two UNDISPOSED records: the recipe R and a bench script B, so a stop record on a non-recipe script still bites).
FOUND FIRST: selftest_stoprecord_c116a.py (stub pattern), selftest_c103d_hooks.py (stop_gate calls), launchunit.py.
PREDICTION CONTRACT
  A*  a recipe path only as an ARGUMENT -> stop_gate 0: the material_marker.log:2989 gate_fp log command, gate_fp
      --cmd "py -u R", md5sum/grep/cat R, a quoted --cmd holding `;`, the PowerShell spelling, R as an argument of a
      bgrun-launched bench script, the six earlier read-only repairs' shapes
  N*  a real launch -> stop_gate 2: py -u R, bgrun -- py -u R (with cd root), ../ spelling, a launch after a gate_fp
      segment, $( ) inside the --cmd text, bgrun -- cmd /c, bgrun -- py -c, cat | py -, a variable, cd elsewhere, env
      prefix, -m runpy, a second interpreter without `--`, sh -c, powershell -c, PowerShell `& py`, stopped bench
      script B directly and under bgrun
  W0  the gate wrote no record and no marker line
    py tools/bgrun.py --material --max-min 2 --log tools/bench/selftest_stoprecord_c130_2.log -- py -u tools/bench/selftest_stoprecord_c130_2.py
"""
import os, sys                                                                     # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
for p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "hooks")):
    sys.path.insert(0, p)
os.chdir(ROOT)
import protocol as P          # noqa: E402
import stop_record as SR      # noqa: E402
import guard_bash as GB       # noqa: E402

R = "tools/recipes/stage_d1_ring_p3b1.py"
B = "tools/bench/stopped_c130_2_fake.py"
WRITES, NOTES = [], []
SR.load_records = lambda: [{"recipe_path": x, "reviewed_sha256": "0" * 64, "review_file": "archive/peer/none-c130-2.md",
                            "verdict": ["already-failed"], "released": None} for x in (R, B)]
SR.save_records = lambda recs: WRITES.append(len(recs))
GB.note = lambda *a, **k: NOTES.append(a)
sys.stderr = open(os.devnull, "w")                  # the gate's refusal text; the GATE lines carry the verdicts
G = []


def gate(ok, label, detail=""):
    G.append((bool(ok), label)); print("GATE %-78s %s %s" % (label, "PASS" if ok else "FAIL", str(detail)[:160]), flush=True)


RT = ROOT.replace("\\", "/")
CD = 'cd "%s" && ' % RT
BG = "py tools/bgrun.py --material --max-min 5 --log tools/bench/x.log -- "
L2989 = (CD + 'py tools/gate_fp.py log --gate guard_cycle --cmd "md5sum tools/recipes/stage_d1_ring_p3b1.py '
         'tools/recipes/stage_d1_ring_p3b2.py" --why "read-only md5sum refused" --card 129-8')
ml = open(os.path.join(ROOT, "tools", "hooks", "material_marker.log"), encoding="utf-8", errors="replace").read().splitlines()
logged = ml[2988].split("STOPPED-RECIPE ", 1)[-1]
gate("REFUSED" in ml[2988] and L2989.startswith(logged), "A0 material_marker.log:2989 is a prefix of the replayed command",
     logged[-60:])
POS = [("A1 marker:2989 gate_fp log --cmd md5sum (Bash)", L2989, "Bash"),
       ("A2 gate_fp log --cmd \"py -u R\"", 'py tools/gate_fp.py log --gate guard_bash --cmd "py -u %s" --why x' % R, "Bash"),
       ("A3 md5sum R", "md5sum %s tools/recipes/stage_d1_ring_p3b2.py" % R, "Bash"),
       ("A4 grep R", 'grep -n "def " %s' % R, "Bash"),
       ("A5 cat R | head", "cat %s | head -5" % R, "Bash"),
       ("A6 --cmd text holding ; and &&", CD + 'py tools/gate_fp.py log --cmd "md5sum %s; py -u %s && x" --why y' % (R, R), "Bash"),
       ("A7 PowerShell spelling of A1", L2989.replace(CD, ""), "PowerShell"),
       ("A8 R as an argument of a bgrun-launched bench script", BG + "py -u tools/bench/diag_c130_2_x.py %s" % R, "Bash"),
       ("A9 earlier repair: wc ; awk | wc", "wc -l %s; awk 'length > 250' %s | wc -l" % (R, R), "Bash"),
       ("A10 earlier repair: for-binding read", "for f in %s; do wc -l $f; done" % R, "Bash"),
       ("A11 earlier repair: py -m pyflakes", "wc -l %s && py -m pyflakes %s 2>&1 | head" % (R, R), "Bash"),
       ("A12 earlier repair: stage_prerun --dry under bgrun", BG + "py -u tools/stage_prerun.py --dry %s" % R, "Bash"),
       ("A13 earlier repair: py -c ast.parse", 'py -c "import ast; ast.parse(open(\'%s\').read())"' % R, "Bash"),
       ("A14 earlier repair: --recipe= form to stop_record.py", "py tools/stop_record.py write --recipe=%s" % R, "Bash")]
NEG = [("N1 py -u R", "py -u %s" % R, "Bash"),
       ("N2 cd root && bgrun -- py -u R", CD + BG + "py -u %s" % R, "Bash"),
       ("N3 ../ spelling", "py -u tools/bench/../recipes/stage_d1_ring_p3b1.py", "Bash"),
       ("N4 gate_fp log then ; py -u R", 'py tools/gate_fp.py log --cmd "x" ; py -u %s' % R, "Bash"),
       ("N5 $( ) inside the --cmd text", 'py tools/gate_fp.py log --cmd "$(py -u %s)"' % R, "Bash"),
       ("N6 bgrun -- cmd /c", BG + 'cmd /c "py -u %s"' % R, "Bash"),
       ("N7 bgrun -- py -c runpy", BG + 'py -c "import runpy; runpy.run_path(\'%s\')"' % R, "Bash"),
       ("N8 cat R | py -", "cat %s | py -" % R, "Bash"),
       ("N9 variable", "f=%s; %spy -u $f" % (R, BG), "Bash"),
       ("N11 env prefix", "PYTHONPATH=x py -u %s" % R, "Bash"),
       ("N12 py -m runpy R", "py -m runpy %s" % R, "Bash"),
       ("N13 second interpreter without --", "py tools/bgrun.py py -u %s" % R, "Bash"),
       ("N14 sh -c", 'sh -c "py -u %s"' % R, "Bash"),
       ("N15 powershell -c", 'powershell -Command "py -u %s"' % R, "PowerShell"),
       ("N16 PowerShell & py", "& py -u %s" % R, "PowerShell"),
       ("N17 stopped bench script B direct", "py -u %s" % B, "Bash"),
       ("N18 stopped bench script B under bgrun", BG + "py -u %s" % B, "Bash"),
       ("N19 backslash spelling", "py -u tools\\recipes\\stage_d1_ring_p3b1.py", "PowerShell")]
# PRE-EXISTING stop_record holes (tools/bench/diag_c130_2_baseline.log: stop_record ALONE allows them; tools/stop_record.py is
# outside card 130-2's write list). Gate = the fp-22 filter does not change the verdict (no regression), nothing more.
HOLES = [("H1 cd tools/recipes && py <basename>", "cd tools/recipes && py stage_d1_ring_p3b1.py", "Bash"),
         ("H2 quoted absolute path (project root has blanks)", 'py -u "%s/%s"' % (RT, R), "Bash"),
         ("H3 quoted absolute path under bgrun", BG + 'py -u "%s/%s"' % (RT, R), "Bash")]
for lab, c, sh in POS:
    rc = GB.stop_gate(c, sh)
    gate(rc == 0, lab + " -> allowed", "rc %d" % rc)
for lab, c, sh in NEG:
    rc = GB.stop_gate(c, sh)
    gate(rc == 2, lab + " -> REFUSED", "rc %d" % rc)
for lab, c, sh in HOLES:
    rc, alone = GB.stop_gate(c, sh), SR.check_command(c)[0]
    gate(rc == (0 if alone else 2), lab + " -> same verdict as stop_record alone", "rc %d alone_allows %s" % (rc, alone))
gate(not WRITES, "W0 the gate wrote no record", WRITES)
n = sum(1 for ok, _l in G if ok)
print("=== GATES: %d pass / %d fail" % (n, len(G) - n))
print(P.result_line(P.make_result(n, len(G) - n, next((l for ok, l in G if not ok), None))), flush=True)
sys.exit(0 if n == len(G) else 1)
