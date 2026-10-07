# ---
# labview: none
# hardware: none
# ---
"""card 144-3 - offline check of gate false positives fp-34 and fp-41. Reads only; edits nothing.

Prior art: tools/stage_prerun.py vi_modifying_calls / launched_vi_modifying (3133-3167), VI_MOD_EXEMPT_PATHS (3130);
tools/hooks/guard_peer.py log_failure (168-189); tools/protocol.py run_verdict (417-435).

PREDICTION:
  F41a stage_prerun.vi_modifying_calls(selftest_fn_f2.py) == []        (the file no longer imports stagekit, or is pinned)
  F41b launched_vi_modifying(<the fp-41 refused cmd>) == []             (the launch classifier does not gate it)
  F41c the pin in VI_MOD_EXEMPT_PATHS (if present) equals sha256 of the current bytes
  F34a guard_peer.log_failure(prep_c140_2_scrreq_r3.log) == failed      (fp-34 still open: rc 3 counted failed)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "hooks"))
os.chdir(ROOT)

import protocol  # noqa: E402
import stage_prerun as S  # noqa: E402

gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  %s  %s  | %s" % ("PASS" if ok else "FAIL", label, str(detail)[:300]), flush=True)


P = "tools/bench/selftest_fn_f2.py"
CMD = "py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_fn_f2.log -- py -u tools/bench/selftest_fn_f2.py"
calls = S.vi_modifying_calls(P)
gate("F41a vi_modifying_calls(selftest_fn_f2.py) == []", calls == [], calls)
lv = S.launched_vi_modifying(CMD)
gate("F41b launched_vi_modifying(fp-41 cmd) == []", lv == [], lv)
pin = S.VI_MOD_EXEMPT_PATHS.get(P)
cur = S.sha256(P)
gate("F41c pin (if present) == sha256 of current bytes", pin is None or pin == cur, "pin=%s cur=%s" % (pin, cur))
print("FACT sha256(%s) = %s" % (P, cur))

import guard_peer  # noqa: E402
LOG = os.path.join(ROOT, "tools", "bench", "prep_c140_2_scrreq_r3.log")
failed, first = guard_peer.log_failure_file(LOG)
gate("F34a guard_peer.log_failure(prep_c140_2_scrreq_r3.log) counts rc 3 as failed (fp-34 still open)", failed, first)

bad = [g for g in gates if not g[1]]
print("=== %d pass / %d fail" % (len(gates) - len(bad), len(bad)), flush=True)
print(protocol.result_line(protocol.make_result(len(gates) - len(bad), len(bad), bad[0][0] if bad else None, [])),
      flush=True)
sys.exit(1 if bad else 0)
