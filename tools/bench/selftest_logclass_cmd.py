r"""selftest_logclass_cmd.py - card 76-2: tools/logclass.py classifies by the log's LAST `BGRUN START` command.

PRIOR ART (checked first): `logclass.last_bgrun_command` / `command_program` / `is_judgement_session_log` already
read the command; `tools/bgrun.py:124` and `tools/hooks/guard_peer.py:215-224` hold the Jev and command-position
rules reused here. Existing self-tests: selftest_logclass_recipebuild, selftest_audit_c4c_split (runs 4 more),
selftest_bgrun_fail_scan, selftest_stamp_window - rerun in [3] and compared with their pre-change baseline logs
`tools/bench/selftest_logclass_base_*.log` (03:2x-03:30, BEFORE the edit): failre 25/1 on E1 (bold emitters in
diag_c83/c86 scripts, unrelated), which cascades into recipebuild C10 and c4c G14 x2.
PREDICTION: [1] 18 fixture gates pass; [2] no log leaves the review set, every log that leaves the build set has
command kind review, and those leavers are exactly the review-set joiners (Jev logs stay builds, recipebuild C4); [3] every pre-existing failing gate is one of the 4 baseline names, and no new one.
No LabVIEW. Run: py tools/bgrun.py --material --max-min 10 --log tools/bench/selftest_logclass_cmd.log --
py -u tools/bench/selftest_logclass_cmd.py
"""
import glob, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import logclass, protocol                                                          # noqa: E402,E401
BENCH = os.path.join(ROOT, "tools", "bench"); P, F = [], []
BG = "BGRUN START 2026-09-25 03:00:00 limit 5.0 min: %s\n"


def gate(n, ok, d=""):
    (P if ok else F).append(n)
    print(("  %s  %s  %s" % ("PASS" if ok else "FAIL", n, d)).encode("ascii", "replace").decode(), flush=True)


def fact(s):
    print(("  FACT  " + s).encode("ascii", "replace").decode(), flush=True)


PEER_F = r"powershell -NoProfile -ExecutionPolicy Bypass -File tools\peer.ps1 -Kind fact -Slug x -TaskFile t.txt"
CASES = [  # label, filename, body, want kind, want review, want build
    ("F1 review under a build-like name (-File peer.ps1)", "m8b_x_fact.log", BG % PEER_F, "review", True, False),
    ("F1b review under a build-like name (-Command & peer.ps1)", "diag_y.log",
     BG % "powershell -NoProfile -Command & 'tools/peer.ps1' -Agent claude -Role hypothesis", "review", True, False),
    ("F1c peer.ps1 wrapped in bgrun (after --)", "wrap.log",
     BG % "py tools/bgrun.py --max-min 5 --log a.log -- powershell -File tools/peer.ps1 -Kind fact", "review", True, False),
    ("F1d retrospective under a build-like name", "c75_close.log", BG % "py -u tools/retrospective.py --cycle 75",
     "review", True, False),
    ("F1e claude.exe session under a build-like name", "sess.log", BG % "claude.exe -p --model opus x", "review", True, False),
    ("F2 build under a review-like name: ASYMMETRIC, stays review", "peer_whatever.log",
     BG % "py -u tools/recipes/build_d1_m3a3.py", "build", True, False),
    ("F2b build under a normal name", "build_x.log", BG % "MATERIAL=1 py -u tools/recipes/build_x.py", "build", False, True),
    ("F2c bench script whose ARGS name peer.ps1", "diag_z.log", BG % "py -u tools/bench/diag_z.py --note tools/peer.ps1",
     "build", False, True),
    ("F2d utility prefix then recipe", "run4.log", BG % "py -u tools/lv_restart.py; py -u tools/recipes/build_d1_v0.py",
     "build", False, True),
    ("F3 no BGRUN START, build-like name: filename rule", "orphan.log", "text only\n", "", False, True),
    ("F3b no BGRUN START, review-like name: filename rule", "peer_orphan.log", "FAIL quoted\n", "", True, False),
    ("F3c watchdog record: neither", "stall_pid1.log", "STALL: pid 1\n", "", False, False),
    ("F3d unrecognised command: filename rule", "probe_bgrun_inner.log", BG % "powershell -Command Write-Output hi",
     "", False, True),
    ("F4 Jev bench script: kind jev, not review, build unchanged", "survey.log", BG % "py -u tools/bench/jev_gate.py --x",
     "jev", False, True),
    ("F4b Jev top-level script", "ladder.log", BG % r"py -u tools\jev_ladder.py", "jev", False, True),
    ("F5 LAST run wins: peer after recipe", "app1.log", BG % "py -u tools/recipes/a.py" + "x\n" + BG % PEER_F,
     "review", True, False),
    ("F5b LAST run wins: recipe after peer", "app2.log", BG % PEER_F + "x\n" + BG % "py -u tools/recipes/a.py",
     "build", False, True),
]


def old(p):
    b = os.path.basename(p)
    rv = bool(logclass.REVIEW_LOG_RE.match(b))
    return rv, not (rv or logclass.WATCHDOG_LOG_RE.match(b))


def main():
    print("=== [1] fixtures", flush=True)
    tmp = tempfile.mkdtemp(prefix="logclass_cmd_")
    for lab, name, body, k, rv, bd in CASES:
        p = os.path.join(tmp, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(body)
        got = (logclass.log_kind(p), logclass.is_review_log(p), logclass.is_build_log(p))
        gate(lab, got == (k, rv, bd), "got %r want %r" % (got, (k, rv, bd)))
    real = os.path.join(BENCH, "m8b_replay_prep_75_fact.log")
    gate("F6 the real misfiled log is now a review", os.path.isfile(real) and logclass.is_review_log(real)
         and not logclass.is_build_log(real), logclass.last_bgrun_command(real)[:80])
    print("=== [2] survey of tools/bench/*.log, filename rule vs command rule", flush=True)
    allp = sorted(glob.glob(os.path.join(BENCH, "*.log")))
    left_rev, left_build, joined = [], [], []
    for p in allp:
        (orv, obd), nrv, nbd = old(p), logclass.is_review_log(p), logclass.is_build_log(p)
        if orv and not nrv: left_rev.append(p)
        if obd and not nbd: left_build.append((os.path.basename(p), logclass.log_kind(p)))
        if nrv and not orv: joined.append(os.path.basename(p))
    fact("logs %d ; left build set %d ; joined review set %d" % (len(allp), len(left_build), len(joined)))
    for b, k in left_build:
        fact("  LEFT BUILD  %-55s kind=%s" % (b, k))
    gate("S1 no log leaves the review set", not left_rev, str([os.path.basename(p) for p in left_rev][:5]))
    gate("S2 every log leaving the build set has command kind review", all(k == "review" for _, k in left_build))
    gate("S3 the build-set leavers are exactly the review-set joiners", sorted(b for b, _ in left_build) == sorted(joined))
    print("=== [3] pre-existing self-tests vs baseline", flush=True)
    base = {"E1 no line-start bold emitter remains under tools/bench/",
            "C10 selftest_guard_peer_failre.py still passes UNCHANGED (rc 0 and 0 failures)",
            "G14 selftest_logclass_recipebuild.py still passes UNCHANGED (rc 0, 0 failures)",
            "G14 selftest_guard_peer_failre.py still passes UNCHANGED (rc 0, 0 failures)"}
    for st in ("selftest_logclass_recipebuild.py", "selftest_audit_c4c_split.py", "selftest_bgrun_fail_scan.py",
               "selftest_stamp_window.py", "selftest_guard_peer_jev.py", "selftest_guard_peer_failre.py",
               "selftest_audit_cost_window.py"):
        r = subprocess.run([sys.executable, "-u", os.path.join(BENCH, st)], cwd=ROOT, capture_output=True,
                           text=True, timeout=600, env=dict(os.environ, MATERIAL="1"), encoding="utf-8", errors="replace")
        fails = [m.strip() for m in re.findall(r"^\s*FAIL\s+(.+?)(?:\s{2,}.*)?$", r.stdout or "", re.M)]
        new = [x for x in fails if not any(x.startswith(b) or b.startswith(x) for b in base)]
        tally = re.findall(r"(\d+)\s*pass\s*/\s*(\d+)\s*fail", r.stdout or "", re.I)
        fact("%s rc=%s tally=%s fails=%s" % (st, r.returncode, tally[-1] if tally else None, fails))
        gate("B %s no failure beyond baseline" % st, not new, str(new))
    print("=== GATES: %d pass / %d fail%s" % (len(P), len(F), ("; failing: " + ", ".join(F)) if F else ""), flush=True)
    print(protocol.result_line(protocol.make_result(len(P), len(F), F[0] if F else None)), flush=True)
    return 1 if F else 0


if __name__ == "__main__":
    sys.exit(main())
