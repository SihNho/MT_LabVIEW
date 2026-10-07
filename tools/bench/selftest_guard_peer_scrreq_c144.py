# ---
# labview: none
# hardware: none
# ---
r"""Self-test, card 144-a2-3 (fp-34): guard_peer.log_failure treats `stage_prerun.py --scratch-required` exit 3 with a
`SCRATCH-REQUIRED | ` line and no RESULT line as a DECISION, not a failed prediction.

Existing tools checked first: tools/bench/selftest_guard_peer_failre.py tests FAILURE_RE / the C6 verdict source, not
rc carve-outs; tools/bench/selftest_chat_p1.py tests gate_fp.py itself. Neither covers rc 3, so this file is new.
The hook's LIVE function is imported - never a copy.

Prediction contract (all must hold):
  A  the real log tools/bench/prep_c140_2_scrreq_r3.log is NOT failed
  B  rc 3 + scratch-required command WITHOUT the SCRATCH-REQUIRED line -> failed
  C  rc 3 + SCRATCH-REQUIRED line but ANOTHER command (a recipe, a stage_prerun --rebase) -> failed
  D  rc 1 and rc 2 of the scratch-required command, with the line -> failed, first line `BGRUN END rc=<n>` (unchanged)
  E  rc 3 + the line + a failing RESULT line -> failed; rc 3 + the line + TIMEOUT -> failed
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
import guard_peer  # noqa: E402
import protocol  # noqa: E402

SCR = "py -u tools/stage_prerun.py --scratch-required tools/recipes/stage_d1_ring_p4_s01.py"
LINE = ("SCRATCH-REQUIRED | stage_d1_ring_p4_s01.py | CENSUS-UNPREDICTED tools/bench/plan_ring_p4_s01.json rows [1] - "
        "the scratch run measures the census before the ONE launch")
FAIL_RES = protocol.result_line(protocol.make_result(0, 1, "G1 census mismatch"))


def log(cmd, body, end="BGRUN END rc=3 after 1s"):
    return ("BGRUN START 2026-10-02 20:25:33 limit 3.0 min: %s\nBGRUN PID 1\n%s%s\n"
            % (cmd, (body + "\n") if body else "", end))


results = []


def gate(label, ok, detail):
    results.append((label, bool(ok)))
    print("%s  %s | %s" % ("PASS" if ok else "FAIL", label, detail))


def main():
    real = os.path.join(ROOT, "tools", "bench", "prep_c140_2_scrreq_r3.log")
    with open(real, "r", encoding="utf-8", errors="replace") as f:
        txt = f.read().lstrip("﻿")
    v = guard_peer.log_failure(txt, os.path.getmtime(real))
    gate("A real prep_c140_2_scrreq_r3.log not failed", v == (False, None), v)
    v2 = guard_peer.log_failure_file(real)
    gate("A2 log_failure_file agrees", v2 == (False, None), v2)

    v = guard_peer.log_failure(log(SCR, ""))
    gate("B rc 3 without SCRATCH-REQUIRED line -> failed", v[0] is True, v)
    v = guard_peer.log_failure(log(SCR, "SCRATCH-REQUIRED is mentioned mid-line only"))
    gate("B2 line not at start / no ' | ' -> failed", v[0] is True, v)

    for lab, cmd in (("C recipe rc 3", "py -u tools/recipes/stage_d1_ring_p4_s04v18_scratch.py"),
                     ("C2 stage_prerun --rebase rc 3", "py -u tools/stage_prerun.py --rebase tools/recipes/x.py"),
                     ("C3 stage_prerun plain rc 3", "py -u tools/stage_prerun.py tools/recipes/stage_d1_ring_p4_s01.py")):
        v = guard_peer.log_failure(log(cmd, LINE))
        gate(lab + " with the line -> failed", v[0] is True, v)

    for rc in (1, 2):
        v = guard_peer.log_failure(log(SCR, LINE, "BGRUN END rc=%d after 1s" % rc))
        gate("D rc %d unchanged -> failed" % rc, v == (True, "BGRUN END rc=%d" % rc), v)
    v = guard_peer.log_failure(log(SCR, LINE, "BGRUN END rc=0 after 1s"))
    gate("D2 rc 0 -> not failed", v[0] is False, v)

    v = guard_peer.log_failure(log(SCR, LINE + "\n" + FAIL_RES))
    gate("E rc 3 + failing RESULT line -> failed", v[0] is True, v)
    v = guard_peer.log_failure(log(SCR, LINE, "BGRUN TIMEOUT after 180s"))
    gate("E2 TIMEOUT -> failed", v[0] is True, v)

    n_fail = sum(1 for _, ok in results if not ok)
    first = next((lab for lab, ok in results if not ok), None)
    print(protocol.result_line(protocol.make_result(len(results) - n_fail, n_fail, first)))
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
