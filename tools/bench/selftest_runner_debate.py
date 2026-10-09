# ---
# labview: none
# hardware: none
# ---
r"""Self-test: Claude-GPT discussions inside tools/cycle_runner.py (card chat-D2, user 2026-10-09 "둘 다 넣자").

NO LabVIEW, NO model call, NO Google: the runner runs with --dry-cmd stand-ins and --debate-stub (stub speakers, local
or simulated-auth-failure doc). The judge / assign stand-ins are the ones of tools/bench/selftest_assign_flow.py
(runner_stubs / runner_case, called - not copied); the firefighter case uses tools/bench/selftest_cycle_runner_ff.py's
`fail2` stand-in. Every runner writes only to a temp bench / peer dir.

PREDICTION CONTRACT (gates):
  D1 outcome due (empty peer dir) -> DEBATE line `| outcome | doc file://`, steer_1.json valid (debate:c1-outcome) and
     carried in cycle_1.json, one open decisions_pending item from the stub's user question, an outcome-review archive
     in the peer dir (GATES-DUE outcome=ok), outcome_review.py NOT run, the heartbeat carries the doc link
  D2 Google auth failure -> DEBATE-NO-DOC, a 'log in' decisions item, still a steer card, the cycle runs (CYCLE 1, exit 0)
  D3 deadline (0.1 min, stub 30 s/message) -> DEBATE-DEADLINE, discussion not complete -> fallback outcome_review path
     ('DUE, not dispatched (dry run)'), the cycle runs
  D4 HANDBACK-LIMIT in cycle 1 -> `DEBATE | ... | cycle 2 | stuck` BEFORE cycle 2's card, steer_2.json debate:c2-stuck,
     the topic names the hand-back record
  D5 firefighter trigger (same recipe failed in cycles 1-2) -> stuck discussion before cycle 3, topic names the trigger
     and the failing log; the firefighter cycle still runs (FIREFIGHTER line for cycle 3)
  D6 --outcome-by review -> no outcome discussion, the old path ('DUE, not dispatched (dry run)')
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
import selftest_assign_flow as SAF  # noqa: E402
import guard_assign as GA  # noqa: E402
import protocol  # noqa: E402

GM = os.path.join(ROOT, "docs", "goalmap.json")
RUNNER = os.path.join(ROOT, "tools", "cycle_runner.py")
RESULTS = []


def gate(label, ok, detail=""):
    RESULTS.append((label, bool(ok)))
    print("%s  %s%s" % ("PASS" if ok else "BAD ", label, "" if ok else "   <- %s" % (detail,)), flush=True)


def jload(p):
    try:
        return json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def idx(log, needle):
    i = log.find(needle)
    return i if i >= 0 else 10 ** 9


def main():
    tmp = tempfile.mkdtemp(prefix="runnerdebate_")
    if " " in tmp or " " in sys.executable:
        print("  BAD  a temp or interpreter path contains a space (the dry-cmd stand-ins are whitespace-split)")
        return 1
    cfg = os.path.join(tmp, "cfg.json")
    json.dump(GA.load_config(GA.DEFAULT_CONFIG), open(cfg, "w", encoding="utf-8"))
    st = SAF.runner_stubs(tmp)
    stub = ["--debate-stub", "--goalmap", GM]
    try:
        # D1 outcome discussion
        rc, log, bench = SAF.runner_case(tmp, st, "d1", "write", None, cfg,
                                         ["--flow", "legacy", "--debate-doc", "local"] + stub)
        peer = os.path.join(os.path.dirname(bench), "peer")
        steer = jload(os.path.join(bench, "cards", "steer_1.json"))
        cyc = jload(os.path.join(bench, "cards", "cycle_1.json"))
        decs = protocol.open_decisions(os.path.join(bench, "decisions_pending.json"))
        hb = open(os.path.join(bench, "heartbeat_latest.md"), encoding="utf-8").read() if os.path.exists(
            os.path.join(bench, "heartbeat_latest.md")) else ""
        arch = [f for f in os.listdir(peer) if "outcome-review-debate-c1" in f] if os.path.isdir(peer) else []
        gate("D1 outcome due -> discussion -> steer + decision + archive; outcome_review.py not run; heartbeat link",
             rc == 0 and "| cycle 1 | outcome | doc file://" in log and steer.get("item") == "debate:c1-outcome"
             and protocol.validate_obj(steer, protocol.goalmap_ids(GM)[3])[0]
             and (cyc.get("steer") or {}).get("path", "").endswith("steer_1.json") and len(decs) == 1
             and arch and "outcome=ok" in log and "outcome_review_cycle1.log" not in log
             and "Claude-GPT 토론" in hb and "CYCLE 1 |" in log,
             (rc, steer.get("item"), len(decs), arch, "outcome=ok" in log))

        # D2 auth failure
        rc, log, bench = SAF.runner_case(tmp, st, "d2", "write", None, cfg,
                                         ["--flow", "legacy", "--debate-doc", "authfail"] + stub)
        decs = protocol.open_decisions(os.path.join(bench, "decisions_pending.json"))
        gate("D2 auth failure -> DEBATE-NO-DOC, login item, steer, the cycle runs",
             rc == 0 and "DEBATE-NO-DOC |" in log and any("debate_gdoc.py login" in d["question"] for d in decs)
             and os.path.exists(os.path.join(bench, "cards", "steer_1.json")) and "CYCLE 1 |" in log, (rc, len(decs)))

        # D3 deadline
        rc, log, bench = SAF.runner_case(tmp, st, "d3", "write", None, cfg,
                                         ["--flow", "legacy", "--debate-doc", "local", "--debate-max-min", "0.1",
                                          "--debate-stub-secs", "30"] + stub)
        gate("D3 deadline -> DEBATE-DEADLINE, fallback to the outcome_review path, the cycle runs",
             rc == 0 and "DEBATE-DEADLINE |" in log and "fallback outcome_review.py" in log
             and "DUE, not dispatched (dry run)" in log and "CYCLE 1 |" in log
             and not os.path.exists(os.path.join(bench, "cards", "steer_1.json")), rc)

        # D4 HANDBACK-LIMIT -> stuck discussion before cycle 2
        cfg2 = os.path.join(tmp, "cfg_hb2.json")
        json.dump(dict(GA.load_config(cfg), max_handbacks_per_cycle=2), open(cfg2, "w", encoding="utf-8"))
        rc, log, bench = SAF.runner_case(tmp, st, "d4", "write", "always-hb", cfg2, ["--debate-doc", "local"] + stub,
                                         cycles=2)
        topic = open(os.path.join(bench, "debate", "c2-stuck", "topic_in.md"), encoding="utf-8").read() \
            if os.path.exists(os.path.join(bench, "debate", "c2-stuck", "topic_in.md")) else ""
        s2 = jload(os.path.join(bench, "cards", "steer_2.json"))
        gate("D4 HANDBACK-LIMIT -> stuck discussion before cycle 2 -> steer_2 debate:c2-stuck",
             rc == 0 and "HANDBACK-LIMIT |" in log and idx(log, "| cycle 2 | stuck | doc") < idx(log, "| cycle 2 | wrote")
             and s2.get("item") == "debate:c2-stuck" and "HANDBACK-LIMIT in cycle 1" in topic
             and "handback_1_2.json" in topic, (rc, s2.get("item"), len(topic)))

        # D5 firefighter trigger -> stuck discussion before cycle 3
        b5 = os.path.join(tmp, "ff", "bench")
        os.makedirs(b5)
        sp5 = os.path.join(b5, "STATUS.md")
        open(sp5, "w", encoding="utf-8").write("## NEXT\nx\n")
        # an outcome review already archived: otherwise cycle 1's OUTCOME discussion writes a steer card that the
        # stand-in never answers, and two refusals stop the runner after cycle 2 (the existing steer rule, measured)
        os.makedirs(os.path.join(tmp, "ff", "peer"))
        open(os.path.join(tmp, "ff", "peer", "2026-10-09-outcome-review-seed.md"), "w").write("# seed\n")
        p = subprocess.run([sys.executable, RUNNER, "--cycles", "3", "--bench-dir", b5, "--status", sp5,
                            "--peer-dir", os.path.join(tmp, "ff", "peer"), "--debate-doc", "local"] + stub +
                           ["--dry-cmd", "py tools/bench/selftest_cycle_runner_ff.py fail2"], capture_output=True,
                           text=True, encoding="utf-8", errors="replace", env=dict(os.environ, FF_BENCH=b5), cwd=ROOT,
                           timeout=900)
        log = open(os.path.join(b5, "cycle_runner.log"), encoding="utf-8").read()
        t5 = os.path.join(b5, "debate", "c3-stuck", "topic_in.md")
        topic = open(t5, encoding="utf-8").read() if os.path.exists(t5) else ""
        gate("D5 firefighter trigger -> stuck discussion before cycle 3, the firefighter cycle still runs",
             p.returncode == 0 and "| cycle 3 | stuck | doc" in log and "firefighter trigger" in topic
             and "build_fake_v0" in topic and "cycle 3 runs as claude-opus-5-5/max" in log
             and idx(log, "| cycle 3 | stuck | doc") < idx(log, "| cycle 3 | wrote"), (p.returncode, len(topic)))

        # D6 --outcome-by review
        rc, log, bench = SAF.runner_case(tmp, st, "d6", "write", None, cfg,
                                         ["--flow", "legacy", "--outcome-by", "review"] + stub)
        gate("D6 --outcome-by review -> no discussion, the old path",
             rc == 0 and "| outcome | doc" not in log and "DEBATE-START" not in log
             and "DUE, not dispatched (dry run)" in log, rc)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    good = sum(1 for _, ok in RESULTS if ok)
    bad = [lab for lab, ok in RESULTS if not ok]
    print("SUMMARY %d/%d gates pass" % (good, len(RESULTS)), flush=True)
    print(protocol.result_line(protocol.make_result(good, len(bad), bad[0] if bad else None)), flush=True)
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
