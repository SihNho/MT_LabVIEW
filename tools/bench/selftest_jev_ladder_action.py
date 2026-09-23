r"""selftest_jev_ladder_action.py - the Jev review ladder's verdict DRIVES the next action (user 2026-09-24 03:5x),
and it is evaluated ONCE per (log path, log md5).

NO LabVIEW and NO API CALL: ladder_classify / covers_failure / verdicts_for are stubbed (same stubs as
tools/bench/selftest_guard_peer_ladder.py, imported, not copied).

STAGING. When tools/bench/jev_gate.py.new and/or tools/hooks/guard_peer.py.new exist, every child process loads
THOSE as the modules `jev_gate` / `guard_peer` (SourceFileLoader, __file__ = the .new path, so HERE/ROOT resolve
to the real directories). So the copies are tested before they replace the live hook, and the same file re-run
after the move tests the live files. The live hook runs inside the concurrently running cycle runner on every Bash
call - it is only replaced after this passes.

WHAT ALREADY EXISTS (checked): selftest_guard_peer_ladder.py (21 cases, the ladder branch), selftest_guard_peer_jev.py
(the discharge branch), selftest_guard_peer_samerow.py, selftest_guard_peer_failre.py. This file RUNS all four
against the staged modules and adds only the new cases:

  N1  our-script-bug ALLOW: the JEV-LADDER line and the stderr allow message both end with the script-bug NEXT-ACTION
  N2  already-reviewed-class + a covering review: NEXT-ACTION names archive/peer/<that review>
  N3  already-reviewed-class, nothing citable: BLOCK, NEXT-ACTION = hypothesis review owed (stderr + log)
  N4  new-problem: BLOCK, the log line and the block message both carry `NEXT-ACTION: hypothesis review owed`
  N5  below band + the OLD discharge allows: one `old-path discharge` line with the apply-disposition action;
      a second gate call on the same log adds no duplicate
  C1  cache: two gate calls on the same bytes -> ladder_classify called ONCE, one JEV-LADDER line, one allowed
      jsonl line, one cache record, same exit code
  C2  the log is appended to (new md5) -> evaluated again
  C3  write=False (measurements) never reads or writes the cache
"""
import importlib.machinery
import importlib.util
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
HOOKS = os.path.join(TOOLS, "hooks")
STAGED = {"jev_gate": os.path.join(HERE, "jev_gate.py.new"), "guard_peer": os.path.join(HOOKS, "guard_peer.py.new")}
SUITES = ["selftest_guard_peer_ladder.py", "selftest_guard_peer_jev.py", "selftest_guard_peer_samerow.py",
          "selftest_guard_peer_failre.py"]
KNOWN_PREEXISTING = {"selftest_guard_peer_failre.py": {"E1"}}   # unrelated: bold emitters in 3 old diag scripts
_SUM_RE = re.compile(r"(\d+)\s+pass\s*/\s*(\d+)\s+fail", re.I)


def preload():
    for _p in (TOOLS, HERE, HOOKS):
        if _p not in sys.path:
            sys.path.insert(0, _p)
    used = []
    for name in ("jev_gate", "guard_peer"):          # jev_gate first: guard_peer imports it lazily
        path = STAGED[name]
        if not os.path.exists(path):
            continue
        loader = importlib.machinery.SourceFileLoader(name, path)
        spec = importlib.util.spec_from_loader(name, loader)
        mod = importlib.util.module_from_spec(spec)
        mod.__file__ = path
        sys.modules[name] = mod
        loader.exec_module(mod)
        used.append(os.path.relpath(path, ROOT))
    return used


# ------------------------------------------------------------------------------------------------ new cases
def new_cases():
    import io
    import json
    import shutil
    import tempfile
    import jev
    import jev_gate
    import jev_gaterow
    import guard_peer
    import selftest_guard_peer_ladder as base   # FAKE_LOG, FAKE_REVIEW, stubs, run_main, read
    npass = nfail = 0

    def gate(ok, label, detail=""):
        nonlocal npass, nfail
        npass += bool(ok)
        nfail += (not ok)
        print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, detail))

    tmp = tempfile.mkdtemp(prefix="jevaction_")
    bench, peer = os.path.join(tmp, "bench"), os.path.join(tmp, "peer")
    os.makedirs(bench)
    os.makedirs(peer)
    logp = os.path.join(bench, "fake_ladder_stage.log")
    revp = os.path.join(peer, "2026-09-22-fake-ladder-review.md")
    with open(revp, "w", encoding="utf-8") as f:
        f.write(base.FAKE_REVIEW)
    time.sleep(1.1)
    with open(logp, "w", encoding="utf-8") as f:
        f.write(base.FAKE_LOG)
    saved = (guard_peer.BENCH, guard_peer.PEER, guard_peer.ROOT, jev_gate.PEER, jev_gate.GATE_LOG,
             jev_gate.LADDER_ALLOWED, jev_gate.ladder_classify, jev_gate.covers_failure,
             jev_gaterow.verdicts_for, jev.get_key, guard_peer.same_row_review)
    guard_peer.same_row_review = lambda *a, **k: None
    guard_peer.BENCH, guard_peer.PEER, guard_peer.ROOT = bench, peer, tmp
    jev_gate.PEER, jev_gate.GATE_LOG = peer, os.path.join(bench, "jev_gate.log")
    jev_gate.LADDER_ALLOWED = os.path.join(bench, "jev_ladder_allowed.jsonl")
    jev_gaterow.verdicts_for = lambda *a, **k: "D7: prediction-error (p=0.91)"
    jev.get_key = lambda: "x" * 40
    cmd = "py tools/bgrun.py --material --max-min 5 --log tools/bench/x.log -- py -u tools/recipes/next.py"
    cache = os.path.join(bench, "jev_ladder_cache.jsonl")

    def reset():
        for p in (jev_gate.GATE_LOG, jev_gate.LADDER_ALLOWED, cache, os.path.join(bench, "jev_discharge_cache.json")):
            try:
                os.remove(p)
            except OSError:
                pass

    def ladder_lines():
        return [x for x in base.read(jev_gate.GATE_LOG).splitlines() if x.startswith("JEV-LADDER |")]

    try:
        # N1
        reset()
        ls, cs = base.LadderStub("our-script-bug", 0.95), base.CoversStub(0.02)
        jev_gate.ladder_classify, jev_gate.covers_failure = ls, cs
        rc, err = base.run_main(cmd, capture=True)
        ll = ladder_lines()
        want = "NEXT-ACTION: " + jev_gate.NEXT_ACTION_SCRIPT_BUG
        gate(rc == 0 and ll and ll[-1].endswith(want), "N1 our-script-bug ALLOW: log line ends with the script-bug NEXT-ACTION",
             (ll[-1] if ll else "(no line)")[-110:])
        gate(want in err, "N1b the allow message on stderr carries the same NEXT-ACTION", err.strip()[-90:])
        # C1 - the same bytes again: no new evaluation, no new line
        rc2, err2 = base.run_main(cmd, capture=True)
        recs = [x for x in base.read(cache).splitlines() if x.strip()]
        jl = [x for x in base.read(jev_gate.LADDER_ALLOWED).splitlines() if x.strip()]
        gate(ls.calls == 1 and rc2 == rc, "C1 second gate call on the same log md5 -> ladder_classify NOT re-asked",
             "classify calls=%d code %s/%s" % (ls.calls, rc, rc2))
        gate(len(ladder_lines()) == 1 and len(jl) == 1 and len(recs) == 1,
             "C1b one JEV-LADDER line, one allowed-jsonl line, one cache record after two calls",
             "lines=%d jsonl=%d cache=%d" % (len(ladder_lines()), len(jl), len(recs)))
        gate(want in err2, "C1c the cached allow still prints the NEXT-ACTION", err2.strip()[-60:])
        # C2 - append (new md5) -> re-evaluated
        with open(logp, "a", encoding="utf-8") as f:
            f.write("BGRUN START 2026-09-22 18:05:00 limit 10 min: py -u tools/recipes/fake_ladder_stage.py\n"
                    "STOP: A2 again\nBGRUN END rc=1 after 3s\n")
        base.run_main(cmd, capture=True)
        gate(ls.calls == 2, "C2 the log changed (new md5) -> evaluated afresh", "classify calls=%d" % ls.calls)
        # C3 - write=False neither reads nor writes the cache
        n0 = len([x for x in base.read(cache).splitlines() if x.strip()])
        jev_gate.jev_ladder(logp, base.read(logp), write=False)
        jev_gate.jev_ladder(logp, base.read(logp), write=False)
        n1 = len([x for x in base.read(cache).splitlines() if x.strip()])
        gate(ls.calls == 4 and n1 == n0, "C3 write=False evaluates every time and leaves the cache alone",
             "classify calls=%d cache %d->%d" % (ls.calls, n0, n1))

        # N2
        reset()
        ls, cs = base.LadderStub("already-reviewed-class", 0.92), base.CoversStub(0.97)
        jev_gate.ladder_classify, jev_gate.covers_failure = ls, cs
        rc, err = base.run_main(cmd, capture=True)
        ll = ladder_lines()
        tail = "apply the cited review's disposition (archive/peer/2026-09-22-fake-ladder-review.md)"
        gate(rc == 0 and ll and tail in ll[-1], "N2 reviewed class + covering review: NEXT-ACTION cites that review",
             (ll[-1] if ll else "(no line)")[-120:])
        gate(tail in err, "N2b ... and the allow message says the same", err.strip()[-100:])

        # N3
        reset()
        ls, cs = base.LadderStub("already-reviewed-class", 0.92), base.CoversStub(0.05)
        jev_gate.ladder_classify, jev_gate.covers_failure = ls, cs
        rc, err = base.run_main(cmd, capture=True)
        ll = ladder_lines()
        owed = "NEXT-ACTION: " + jev_gate.NEXT_ACTION_REVIEW_OWED
        gate(rc == 2 and ll and ll[-1].endswith(owed) and owed in err,
             "N3 reviewed class, nothing citable: BLOCK + review owed (log and stderr)", "code %s" % rc)

        # N4
        reset()
        ls, cs = base.LadderStub("new-problem", 0.95), base.CoversStub(0.02)
        jev_gate.ladder_classify, jev_gate.covers_failure = ls, cs
        rc, err = base.run_main(cmd, capture=True)
        ll = ladder_lines()
        gate(rc == 2 and ll and ll[-1].endswith(owed) and "BLOCKED by tools/hooks/guard_peer.py" in err and owed in err,
             "N4 new-problem: BLOCK, the log line and the block message carry `review owed`", "code %s" % rc)
        rc2, _ = base.run_main(cmd, capture=True)
        gate(ls.calls == 1 and rc2 == 2, "N4b a blocked verdict is cached too (second call: no re-ask, still BLOCK)",
             "classify calls=%d code %s" % (ls.calls, rc2))

        # N5
        reset()
        ls, cs = base.LadderStub("our-script-bug", 0.55), base.CoversStub(0.97)
        jev_gate.ladder_classify, jev_gate.covers_failure = ls, cs
        rc, err = base.run_main(cmd, capture=True)
        ll = ladder_lines()
        gate(rc == 0 and ll and "old-path discharge" in ll[-1] and "apply the cited review's disposition" in ll[-1],
             "N5 below band + old discharge allows: the newest ladder line says apply-disposition",
             (ll[-1] if ll else "(no line)")[-100:])
        before = len(ll)
        base.run_main(cmd, capture=True)
        gate(len(ladder_lines()) == before, "N5b a second call adds no duplicate line",
             "%d -> %d" % (before, len(ladder_lines())))
    finally:
        (guard_peer.BENCH, guard_peer.PEER, guard_peer.ROOT, jev_gate.PEER, jev_gate.GATE_LOG,
         jev_gate.LADDER_ALLOWED, jev_gate.ladder_classify, jev_gate.covers_failure,
         jev_gaterow.verdicts_for, jev.get_key, guard_peer.same_row_review) = saved
        shutil.rmtree(tmp, ignore_errors=True)
    print("=== new cases: %d pass / %d fail ===" % (npass, nfail))
    return 0 if nfail == 0 else 1


def child(target):
    used = preload()
    print("[child] staged modules: %s" % (used or "none (live files)"))
    sys.stdout.flush()
    if target == "NEW":
        return new_cases()
    import runpy
    sys.argv = [os.path.join(HERE, target)]
    try:
        runpy.run_path(os.path.join(HERE, target), run_name="__main__")
    except SystemExit as e:
        return int(e.code or 0)
    return 0


def main():
    staged = [os.path.relpath(p, ROOT) for p in STAGED.values() if os.path.exists(p)]
    print("=== selftest_jev_ladder_action - testing %s ===" % (staged or "the LIVE files"))
    tot_p = tot_f = 0
    worst = 0
    fail_re = re.compile(r"^\s*FAIL\s+(\S+)", re.M)
    pre = 0
    for target in SUITES + ["NEW"]:
        r = subprocess.run([sys.executable, "-u", os.path.abspath(__file__), "--child", target],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
        out = r.stdout + r.stderr
        sums = _SUM_RE.findall(out)
        p, f = (int(sums[-1][0]), int(sums[-1][1])) if sums else (0, 1)
        if f and target != "NEW" and not staged:
            # LIVE mode (after the move): the one case measured failing identically on the PRE-CHANGE modules at
            # 2026-09-24 03:27 (this log, staged run: "live modules fail the same cases: ['E1']") is excluded by name.
            got = set(fail_re.findall(out))
            known = KNOWN_PREEXISTING.get(target, set())
            if got and got <= known:
                pre += f
                print("--- %-34s %d pass, %d PRE-EXISTING %s (measured on the pre-change modules, not counted)" % (
                    target, p, f, sorted(got)))
                tot_p += p
                continue
        if f and target != "NEW" and staged:
            # A case that fails identically on the LIVE modules is pre-existing and not this change's doing
            # (2026-09-24: selftest_guard_peer_failre E1 scans tools/bench/*.py for bold emitters, unrelated).
            rl = subprocess.run([sys.executable, "-u", os.path.join(HERE, target)], capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=300)
            live_fails = set(fail_re.findall(rl.stdout + rl.stderr))
            new_fails = set(fail_re.findall(out)) - live_fails
            print("    (live modules fail the same cases: %s; failures NEW with the staged copies: %s)" % (
                sorted(live_fails), sorted(new_fails) or "none"))
            if not new_fails and r.returncode == rl.returncode:
                pre += f
                print("--- %-34s %d pass, %d PRE-EXISTING (identical on live modules, not counted)" % (target, p, f))
                tot_p += p
                continue
        tot_p, tot_f = tot_p + p, tot_f + f
        worst = max(worst, r.returncode)
        print("--- %-34s code %d  %d pass / %d fail" % (target, r.returncode, p, f))
        for ln in out.splitlines():
            if ln.strip().startswith(("FAIL", "Traceback")) or "Error" in ln or target == "NEW":
                print("    " + ln)
    print("=== TOTAL: %d pass / %d fail, %d pre-existing excluded (worst code %d) ===" % (tot_p, tot_f, pre, worst))
    return 0 if (tot_f == 0 and worst == 0) else 1


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--child":
        sys.exit(child(sys.argv[2]))
    sys.exit(main())
