# ---
# labview: none
# hardware: none
# ---
r"""Self-test, card 146-a1-1 (gate-fp fp-44 / fp-46): guard_peer RULE-OFFLINE-NEWPROBLEM - a Jev-ladder `new-problem`
verdict on a failing log whose LAST run launched only `labview: none` + `hardware: none` scripts owes no hypothesis
review; every other case blocks exactly as before.

Existing tools checked first: selftest_guard_peer_ladder.py (ladder classes, live Jev fakes), selftest_guard_peer_jev.py
(discharge), selftest_guard_peer_scrreq_c144.py (log_failure rc carve-out) - none covers a ladder verdict judged
against the launched scripts' headers, so this file is new. The hook's LIVE main() is imported; the ladder verdict is
injected (the one tools/bench/jev_gate.log:4689 / :4755 recorded), every log writer is stubbed (nothing written).

Prediction contract (all must hold):
  A  fp-44: diag_c144_2_cls.log first run (the refusal-time text) + recorded new-problem -> main rc 0, RULE line
  B  fp-46: prep_c145_2_pred.log + recorded new-problem -> main rc 0, RULE line
  C  same fp-44 text, NO ladder verdict (Jev unavailable / budget) -> rc 2 (unchanged)
  D  same fp-44 text, ladder line of another class (already-reviewed-class below the discharge) -> rc 2
  E  new-problem on a run of a `labview: build` recipe -> rc 2
  F  new-problem on stage_prerun.py --dry (labview build, offline-args) -> rc 2 (raw header, not the offline reading)
  G  new-problem on an offline script whose run TIMED OUT -> rc 2
  H  new-problem on a script outside tools/ (no header) -> rc 2
  I  new-problem on a `hardware: camera` script -> rc 2
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
import guard_peer as GP  # noqa: E402
import gate_fp  # noqa: E402
import protocol  # noqa: E402

NP44 = ("JEV-LADDER | 2026-10-07 20:41:04 | diag_c144_2_cls.log | new-problem p=0.750 | BLOCK (review owed) | "
        "NEXT-ACTION: hypothesis review owed (old path)")
NP46 = ("JEV-LADDER | 2026-10-07 21:47:19 | prep_c145_2_pred.log | new-problem p=0.800 | BLOCK (review owed) | "
        "NEXT-ACTION: hypothesis review owed (old path)")
ARC = ("JEV-LADDER | 2026-10-07 20:41:04 | diag_c144_2_cls.log | already-reviewed-class p=0.700 | BLOCK (discharge "
       "said no) | NEXT-ACTION: hypothesis review owed (old path)")
CMD = "py tools/bgrun.py --material --max-min 2 --log tools/bench/x.log -- py -u tools/bench/diag_c144_2_cls.py"
FAIL_RES = protocol.result_line(protocol.make_result(0, 1, "G1 something"))
results = []


def gate(label, ok, detail):
    results.append((label, bool(ok)))
    print("%s  %s | %s" % ("PASS" if ok else "FAIL", label, str(detail)[:300]), flush=True)


def simulate(path, text, ladder_line):
    saved = {k: getattr(GP, k) for k in ("newest_failing_log", "newest_bound_peer", "same_row_review", "_jev_decide",
                                        "_gate_log", "gaterow_advisory", "cite_same_row")}
    saved_fp = gate_fp.discharge_for_log
    GP.newest_failing_log = lambda: (path, os.path.getmtime(path), text)
    GP.newest_bound_peer = lambda *a: (None, [])
    GP.same_row_review = lambda *a, **k: None
    GP._jev_decide = lambda *a: (None if ladder_line is None else False, ladder_line, False, ladder_line)
    GP._gate_log = lambda line: None
    GP.gaterow_advisory = lambda *a: None
    GP.cite_same_row = lambda *a: None
    gate_fp.discharge_for_log = lambda *a: (None, None)
    old_in, old_err = sys.stdin, sys.stderr
    sys.stdin, sys.stderr = io.StringIO(json.dumps({"tool_input": {"command": CMD}})), io.StringIO()
    try:
        rc = GP.main()
        err = sys.stderr.getvalue()
    finally:
        sys.stdin, sys.stderr = old_in, old_err
        for k, v in saved.items():
            setattr(GP, k, v)
        gate_fp.discharge_for_log = saved_fp
    return rc, err


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace") as f:
        return f.read().lstrip("﻿")


def synth(cmd, end="BGRUN END rc=1 after 1s"):
    return "BGRUN START 2026-10-07 20:40:45 limit 2.0 min: %s\nBGRUN PID 1\nGATE FAIL | G1 something | x\n%s\n%s\n" % (
        cmd, FAIL_RES, end)


def main():
    p44 = os.path.join(ROOT, "tools", "bench", "diag_c144_2_cls.log")
    t44 = read("tools/bench/diag_c144_2_cls.log")
    i = t44.find("BGRUN END")
    t44 = t44[: t44.find("\n", i) + 1]                                   # the text at refusal time (first run only)
    gate("A0 fp-44 refusal-time text is a failed run", GP.log_failure(t44)[0] is True, GP.log_failure(t44))
    rc, err = simulate(p44, t44, NP44)
    gate("A fp-44 new-problem on labview none/hardware none -> rc 0", rc == 0 and "RULE-OFFLINE-NEWPROBLEM" in err, err[:200])
    p46 = os.path.join(ROOT, "tools", "bench", "prep_c145_2_pred.log")
    t46 = read("tools/bench/prep_c145_2_pred.log")
    gate("B0 fp-46 log is a failed run", GP.log_failure(t46)[0] is True, GP.log_failure(t46))
    rc, err = simulate(p46, t46, NP46)
    gate("B fp-46 new-problem on labview none/hardware none -> rc 0", rc == 0 and "RULE-OFFLINE-NEWPROBLEM" in err, err[:200])

    rc, err = simulate(p44, t44, None)
    gate("C no ladder verdict -> rc 2", rc == 2 and "RULE-OFFLINE-NEWPROBLEM" not in err, rc)
    rc, err = simulate(p44, t44, ARC)
    gate("D another ladder class -> rc 2", rc == 2 and "RULE-OFFLINE-NEWPROBLEM" not in err, rc)
    for lab, cmd, end in (
            ("E labview build recipe", "py -u tools/recipes/stage_d1_ring_p4_s04v18.py", "BGRUN END rc=1 after 1s"),
            ("F stage_prerun --dry (build header + offline-args)",
             "py -u tools/stage_prerun.py --dry tools/recipes/stage_d1_ring_p4_s04v18.py", "BGRUN END rc=1 after 1s"),
            ("G offline script TIMED OUT", "py -u tools/bench/diag_c144_2_cls.py", "BGRUN TIMEOUT after 120s"),
            ("H script outside tools/ (no header)", "py -u archive/x_offline.py", "BGRUN END rc=1 after 1s"),
            ("I hardware camera script", "py -u tools/bench/camera_attributes.py", "BGRUN END rc=1 after 1s")):
        t = synth(cmd, end)
        rc, err = simulate(p44, t, NP44)
        gate(lab + " -> rc 2", GP.log_failure(t)[0] is True and rc == 2 and "RULE-OFFLINE-NEWPROBLEM" not in err,
             (rc, GP.offline_new_problem(NP44, t)))
    n_fail = sum(1 for _, ok in results if not ok)
    first = next((lab for lab, ok in results if not ok), None)
    print(protocol.result_line(protocol.make_result(len(results) - n_fail, n_fail, first)), flush=True)
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
