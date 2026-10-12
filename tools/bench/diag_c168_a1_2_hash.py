# ---
# labview: none
# hardware: none
# offline-args: before
# evidence: tools/bench/cards/task_168-a1-2.json
# ---
r"""diag_c168_a1_2_hash - card 168-a1-2 hash check (OFFLINE, bytes only). Holds only the card path and the mode; the check is
prep_c168_hashlib.check (shared with card 168-a1-1, whose thin caller diag_c168_a1_1_hash.py is the same two lines). argv[1] = before | after.
PREDICTION CONTRACT: 20 card inputs equal, 7 VI pins equal -> 8/0.
    py tools/bgrun.py --material --max-min 1 --log tools/bench/diag_c168_a1_2_hash_<mode>.log -- py -u tools/bench/diag_c168_a1_2_hash.py <mode>"""
import os, sys                                                                              # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prep_c168_hashlib as H                                                               # noqa: E402

gate = H.L.Gate(fatal_default=False)
H.check("tools/bench/cards/task_168-a1-2.json", sys.argv[1] if len(sys.argv) > 1 else "before", gate)
sys.exit(gate.result([]))
