r"""prep_c143_3_elrule - card 143-3 (PD333(b)): the FIXED Error List predictor. MOVED to the shared module tools/elrule.py by
card chat-S5 (PD337(c)); this file only re-exports it so prep_c142_5_pred.py, prep_c143_p1_pred.py, prep_c143_3_pred.py,
prep_c143_5_pred.py and selftest_elpred.py keep working unchanged. Do not add code here.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from elrule import owners_map, items, unwired_inputs, predict  # noqa: E402,F401
