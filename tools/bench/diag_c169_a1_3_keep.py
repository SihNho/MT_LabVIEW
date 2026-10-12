# ---
# labview: none
# hardware: none
# offline-args:
# evidence: tools/bench/cards/task_169-a1-3.json
# ---
r"""diag_c169_a1_3_keep - card 169-a1-3 step 3: keep the 169-a1-2 post log as diag_c169_a1_2_post_run1.log BEFORE the re-run (bgrun
appends, bgrun.py:104). Byte copy (shutil.copyfile, never overwrites), md5 of both equal. Offline, bytes only; Gate is prep_c156_a1_1_lib.Gate.
PREDICTION CONTRACT: C1 run1 did not exist; C2 copy md5 == source md5 (0512f85f, card input) -> 2/0.
    py tools/bgrun.py --material --max-min 1 --log tools/bench/diag_c169_a1_3_keep.log -- py -u tools/bench/diag_c169_a1_3_keep.py"""
import os, shutil, sys                                                                      # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prep_c156_a1_1_lib as L                                                              # noqa: E402

SRC = os.path.join(HERE, "diag_c169_a1_2_post.log")
DST = os.path.join(HERE, "diag_c169_a1_2_post_run1.log")
gate = L.Gate(fatal_default=False)
fresh = not os.path.exists(DST)
gate("C1 {0} did not exist (no overwrite)".format(os.path.basename(DST)), fresh, fresh)
fresh and shutil.copyfile(SRC, DST)                                                         # noqa: expression-as-statement
gate("C2 copy md5 == source md5", os.path.isfile(DST) and L.md5(DST) == L.md5(SRC), "{0} vs {1}".format(L.md5(SRC), L.md5(DST) if os.path.isfile(DST) else None))
sys.exit(gate.result([]))
