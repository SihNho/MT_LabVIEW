r"""diag_c106d_jevrc2.py - card 106-4 H3: WHICH gate returns 2 for selftest_guard_bash_jev's BG command.

Prediction: selftest_guard_bash_jev C2/C3/C5 fail with rc=2 (selftest_guard_bash_jev_c103d.log). The stderr of that
refusal names the gate. Offline, no LabVIEW, jev.ask stubbed. Prints the stderr per case, ends with a RESULT line.
"""
import io
import json
import os
import sys
import tempfile
from contextlib import redirect_stderr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
sys.path.insert(0, HERE)
import guard_bash  # noqa: E402
import jev  # noqa: E402
import protocol  # noqa: E402

jev.ask = lambda *a, **k: (None, "stub")
guard_bash.MARKER_LOG = os.path.join(tempfile.gettempdir(), "material_marker_selftest.log")
BG = ("py tools/bgrun.py --material --max-min 5 --log tools/bench/x.log "
      "-- py -u tools/bench/diag_c88_brokenwires.py")
for name, cmd in (("BG", BG), ("BG-other", BG.replace("diag_c88_brokenwires", "diag_c106d_nonexistent"))):
    payload = {"tool_name": "Bash", "session_id": "selftest-jev",
               "tool_input": {"command": cmd, "run_in_background": True, "timeout": None}}
    old, buf = sys.stdin, io.StringIO()
    try:
        sys.stdin = io.StringIO(json.dumps(payload))
        with redirect_stderr(buf):
            rc = guard_bash.main()
    finally:
        sys.stdin = old
    print("CASE %s code %s" % (name, rc))
    print("STDERR " + buf.getvalue().replace("\n", "\n       "))
print(protocol.result_line(protocol.make_result(1, 0)))
