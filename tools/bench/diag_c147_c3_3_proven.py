# ---
# labview: none
# hardware: none
# ---
r"""diag_c147_c3_3_proven - card 147-c3-3 (OFFLINE, no LabVIEW): why guard_cycle refused the s06 scratch launch (prior-art owed).
Reads, without changing anything, the three releases guard_cycle.py:505-559 tries for tools/recipes/stage_d1_ring_p4_s06v18_scratch.py:
(1) re-run exemption = a build log named <recipe stem>*.log newer than the newest priorart review; (2) stage_prerun.proven_pattern;
(3) priorart_diff.scope. PREDICTION: (1) none (the recipe logs to diag_c147_p4s06v18_scratch.log); (2) False; (3) review_needed True.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c147_c3_3_proven.log -- py -u tools/bench/diag_c147_c3_3_proven.py"""
import glob, json, os, sys                                                         # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
from tools import protocol  # noqa: E402
import stage_prerun, priorart_diff                                                 # noqa: E401,E402
REC = "tools/recipes/stage_d1_ring_p4_s06v18_scratch.py"
stem = os.path.splitext(os.path.basename(REC))[0]
print("FACT logs matching {0}*.log: {1}".format(stem, glob.glob(os.path.join(ROOT, "tools", "bench", stem + "*.log"))), flush=True)
ok, stages, sig = stage_prerun.proven_pattern(os.path.join(ROOT, REC))
print("FACT proven_pattern ok {0} stages {1}".format(ok, stages), flush=True)
print("FACT signature {0}".format(json.dumps(sig, default=str)[:3000]), flush=True)
for b in ("tools/recipes/stage_d1_ring_p4_s06v18.py", "tools/recipes/stage_d1_ring_p4_s05v18_scratch.py"):
    try:
        o2, s2, g2 = stage_prerun.proven_pattern(os.path.join(ROOT, b))
        print("FACT proven_pattern({0}) ok {1} stages {2}".format(b, o2, s2), flush=True)
    except Exception as e:                                                          # noqa: BLE001
        print("FACT proven_pattern({0}) raised {1!r}".format(b, e), flush=True)
try:
    nsc = stage_prerun.new_structure_classes(os.path.join(ROOT, REC))
    print("FACT new_structure_classes {0}".format(nsc), flush=True)
except Exception as e:                                                              # noqa: BLE001
    print("FACT new_structure_classes raised {0!r}".format(e), flush=True)
sc = priorart_diff.scope(os.path.join(ROOT, REC))
print("FACT priorart_diff sibling {0} substantive {1} new_classes {2} review_needed {3}".format(
    sc["sibling"], len(sc["substantive"]), sc["new_classes"], sc["review_needed"]), flush=True)
for ln in sc["substantive"][:80]:
    print("  SUBST {0}".format(str(ln)[:220]), flush=True)
print(protocol.result_line(protocol.make_result(1, 0, None, [])), flush=True)
