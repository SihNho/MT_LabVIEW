r"""audit_cycle.py - mechanical compliance audit of a work cycle. No judgement, no thresholds, no memory required.

WHY. The peer-review loop can only criticise what Claude chooses to send it, and the session's own account of what
it did is exactly the thing that cannot audit itself (user, 2026-09-15: "피어 리뷰를 통해 판단 및 실행 구조에 대한
비평은 할 수 없는 것 같아"). Most of CLAUDE.md's rules, however, leave TRACES on disk - a log line, a file mtime,
a checksum. This reads the traces and reports what actually happened, so the retrospective review argues about
facts instead of about a summary.

It never judges quality. It answers: did the mechanical rules hold, and what did this cycle cost?

  py tools/audit_cycle.py --from <t> --to <t> [--cycle N] [--json]   # AN EXPLICIT WINDOW - prefer this
  py tools/audit_cycle.py [--since-hours 24] [--json]      # LEGACY: a TIME WINDOW, not a cycle boundary

WINDOW (added 2026-09-16, retrospective v2 proposal 4). `--since-hours` was the only option and it is not a cycle
boundary: the cycle-12 audit ran a 24 h window and reported 19 build logs, 37 peer logs and 59 out-of-plan files
spanning three cycles, and its own line 11 had to warn the reviewer not to quote them as cycle-12 figures.
`--from` / `--to` take epoch seconds or `YYYY-MM-DD[ HH:MM[:SS]]` and bound the window at BOTH ends, so every
check and every cost line below is scoped to one cycle. `tools/retrospective.py` derives the pair from the plan
documents (start = mtime of docs/cycle<N>-plan.md, end = mtime of docs/cycle<N+1>-plan.md or now) and passes it
here. `--since-hours` still works unchanged, with no upper bound, so nothing that called this before changes.

Checks (each prints PASS / FAIL / n-a with the evidence):
  A1  every backgrounded LabVIEW run went through bgrun          - a log with no `BGRUN START` line is a bypass
  A2  every bgrun log ended                                       - `BGRUN END` or `BGRUN TIMEOUT`; neither = a killed
                                                                    client whose handles stayed inside LabVIEW
  A3  every failing log has a peer review archived AFTER it       - the same rule guard_peer enforces, checked over
                                                                    the whole window rather than only the newest log
  A4  every archived peer exchange carries "What was done with it" - an unannotated review is one nobody used
  A5  the originals are untouched                                 - md5 of the main VI against docs/checksums if present,
                                                                    otherwise mtime older than the window
  A6  GUI actions, if any, are in tools/gui_actions.log           - state-changing GUI needs a recorded exception
RUN CLIPPING (added 2026-09-18, OPEN 52). The window selects FILES by mtime, but the cost lines are summed per RUN:
`window_runs()` splits each log at its `BGRUN START <stamp>` lines and keeps only the runs whose own stamp falls
inside --from/--to. Before this, a whole file counted whenever its LAST write landed in the window, and cycle 26's
retrospective charged itself the 1199 s and $13.7777 of a firefighter run that started 19 min before its window
opened. Self-test: tools/bench/selftest_audit_cost_window.py.

Cost lines (no pass/fail, they are the numbers the retrospective needs):
  C1  builds run, failures, distinct failure logs
  C2  peer reviews dispatched
  C3  wall-clock inside bgrun, BUILDS only   C4 the same for REVIEWS, with cost   C5 the total
  C4c the JUDGEMENT SESSION's own bgrun (cycle_runner's `claude -p`), reported separately - see cost_split()
"""
import argparse
import glob
import hashlib
import json
import os
import re
import sys
import time

import logclass

# THIS OUTPUT IS EVIDENCE, NOT A CONSOLE MESSAGE (lint, 2026-09-16). retrospective.py captures it verbatim and hands
# it to the peer, so a character this stream cannot encode is a character the reviewer never sees correctly. On a
# cp949 console the `…` in the truncated md5 and in the `blank:` list came out as `<?>`. bgrun.py learned this on
# 2026-09-06; the same line was never added here.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(HERE, "bench")
PEER = os.path.join(ROOT, "archive", "peer")
MAIN = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\Min_Track N beads V6_ParallelLoop.vi"
# THE DEVICE FOR `device-failed` (round 5, 2026-09-17 retrospective `retrospective-cycle15-d1-build3`,
# threshold 1). The pattern below ended `^\s*(?:->\s*)?FAIL\b`, which cannot match THIS FLEET'S OWN GATE FORM -
# every recipe prints `  **FAIL**  <gate name>` (build_d1_v0.py:263, build_opsentinel_ops.py, probe_move_*.py) -
# and it never looked at the runner's own verdict line, `BGRUN END rc=1`. So C1/A3 reported ZERO failing logs for
# a window that contained five failed gates in `build_d1_v0_run4.log:220-245` and a failed run in
# `build_d1_v0.log:14-18`. That is the fault this device exists to prevent, in the device itself, for the second
# time (round 4 was the COST regex below, the same shape: a pattern written against a format nothing emits).
# Three forms are matched now: the bare word, the fleet's bold form, and a nonzero bgrun exit.
# MOTOR VOCABULARY (cycle 69, device-failed repair): pi_testmove_20260923e.log held `RESULT: NOT at target` (:23),
# `RESULT: REJECTED BY THE CONTROLLER - ERR 216` (:34) and `ERR?=216` (:22) under `BGRUN END rc=0` (:51), and this
# audit counted it green. Same alternatives as bgrun.inner_re; self-test tools/bench/selftest_motor_fail_exit.py.
FAILURE_RE = re.compile(r"OBSERVED:?\s*EXC|VERDICT:\s*BROKEN|STOP at gate|BGRUN TIMEOUT|^STALL:"
                        r"|^\s*(?:->\s*)?FAIL\b|\*\*FAIL\*\*|^BGRUN END rc=(?!0\b)\d+"
                        r"|^RESULT:\s*(?:REJECTED\b|NOT at target\b)"
                        r"|\bERR\?\s*(?:right after send\s*)?=\s*[1-9]\d*",
                        re.I | re.M)

# THE DEVICE FOR `device-failed` (docs/violation-decisions.md, 2026-09-16 21:07, round 4; threshold 1).
# The old pattern was `"?(total_cost_usd|cost_usd|total_cost)"?\s*[:=]\s*\$?([0-9]+\.[0-9]+)`. It matches the JSON
# key the claude peer's envelope carries - but peer.ps1 does not print that envelope: it prints
#     COST: $5.1157  in 48 / out 1731 / cache-create 179450 / cache-read 1074828  (296s, 14 turn(s))
# and the regex returns [] on that exact line. So C4 has printed "no log reported a cost - treat the review cost as
# UNKNOWN" for EVERY cycle since it was built, while $20.4241 sat in cycle 11's window alone. The device that
# exists specifically to stop review cost being understated was itself understating it - which is the fault it was
# built to prevent, verbatim, and is why retrospective v2's DEVICE EFFECT question found it on its first outing.
# Both forms are matched now: the JSON key (in case a raw envelope is ever logged) and peer.ps1's own COST: line.
COST_RE = re.compile(r'"?(?:total_cost_usd|cost_usd|total_cost)"?\s*[:=]\s*\$?([0-9]+\.[0-9]+)'
                     r'|^COST:\s*\$\s*([0-9]+\.[0-9]+)', re.M)
# EVERY line that LOOKS like a cost, whether or not COST_RE could parse it. The point of the pair is that a silent
# miss becomes visible: "cost lines seen 4 / parsed 4" is a working device, "seen 4 / parsed 0" is the bug above
# announcing itself instead of hiding as a plausible zero.
COST_SEEN_RE = re.compile(r'^COST:|total_cost_usd|\bcost_usd\b|\btotal_cost\b', re.M)

# THE DEVICE FOR `device-failed` (round 6; cycle-26 retrospective, 2026-09-18; threshold 1). A log FILE's mtime is
# the time of its LAST write, so a run that started long before the window keeps an mtime inside it, and every cost
# line in that file was then charged to a cycle that did not run it. Cycle 26's retrospective (window 13:49..14:03,
# archive/peer/2026-09-18-retrospective-cycle26.md:116) imported the whole of `tools/bench/cycle_12.log` - a
# firefighter run that STARTED at 13:30:03, 19 min before the window opened - and reported its 1199 s and $13.7777
# as cycle-26 cost. Each RUN is now attributed to the window its OWN `BGRUN START` stamp falls in.
BGRUN_START_RE = re.compile(r"^BGRUN START (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", re.M)

# C6 (session protocol v1, user-approved 2026-09-24): FAILURE_RE above is now the LEGACY rule, applied only to runs
# that STARTED before protocol.SWITCH_TS and carry no RESULT line (history is not rewritten). A later run fails iff
# a RESULT line it printed fails or it ended rc!=0 / TIMEOUT (protocol.run_verdict). A log with no BGRUN START at all
# (a watchdog `stall_*` record, a hand-written note) is not a script run and keeps the FAILURE_RE reading.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import protocol  # noqa: E402


def seg_failures(seg):
    """Failure count of ONE run segment (starts at its BGRUN START line): legacy findall count before the switch,
    else 0/1 from the C6 verdict."""
    m = BGRUN_START_RE.search(seg)
    ts = time.mktime(time.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")) if m else None
    if not protocol.all_result_lines(seg) and protocol.is_legacy(ts):
        return len(FAILURE_RE.findall(seg))
    return 1 if protocol.run_verdict(seg)["failed"] else 0


def log_failed(body):
    """A3's question for a whole log: did ANY run in it fail (legacy rule for pre-switch runs)."""
    marks = list(BGRUN_START_RE.finditer(body))
    if not marks:
        return bool(FAILURE_RE.search(body))
    if FAILURE_RE.search(body[:marks[0].start()]):          # pre-START preamble: judged as before
        return True
    return any(seg_failures(body[m.start():(marks[i + 1].start() if i + 1 < len(marks) else len(body))])
               for i, m in enumerate(marks))


def window_runs(body, cutoff, until):
    """The parts of a bgrun log that belong to THIS window: one segment per `BGRUN START` stamped inside it.

    A segment runs from its own START line to the next one (or to EOF), so the `BGRUN END ... after <n>s` and
    `COST:` lines of that run travel with it. A run whose START predates the window is dropped whole - not clipped
    pro rata: the seconds and the dollars were spent by the earlier cycle, not shared with this one.

    A log carrying NO `BGRUN START` line at all (a watchdog record, a hand-written note) has no run stamps, so its
    mtime is the only timestamp it has and that is what already selected it: it is returned unchanged, exactly as
    before this repair. Behaviour stated here because it is the one case the fix cannot measure.
    """
    marks = list(BGRUN_START_RE.finditer(body))
    if not marks:
        return [body]
    segs = []
    for i, m in enumerate(marks):
        stop = marks[i + 1].start() if i + 1 < len(marks) else len(body)
        try:
            t = time.mktime(time.strptime(m.group(1), "%Y-%m-%d %H:%M:%S"))
        except ValueError:
            continue
        if cutoff <= t <= until:
            segs.append(body[m.start():stop])
    return segs


def cost_split(machinery_logs, cutoff, until):
    """Wall-clock and dollars of the MACHINERY logs, split into REVIEW spend and JUDGEMENT-SESSION spend.

    THE DEVICE FOR `device-failed` (round 7; cycle-64 retrospective, 2026-09-22, threshold 1; accepted in full in
    `archive/peer/2026-09-22-retrospective-cycle64.md`). `logclass.split` returns everything that is not a build as
    "machinery", and C4 charged all of it to REVIEWS. But one of those files is the cycle's own judgement session
    (`tools/bench/cycle_<n>.log`, `claude.exe -p` under bgrun), and it is by far the largest line: cycle 64's C4
    read `$63.9903 from 4 log(s)` and `reviews are 94%` of the wall-clock, when the three real reviews were
    $12.3687 (6.3017 + 2.6899 + 3.3771) and 1,490 s of 7,976 - the rest, $51.6216 and 6,055 s, was the session
    (`tools/bench/cycle_59.log:62`). A cost line wrong by 5.2x in composition is the same fault this device was
    built to prevent, for the third time (round 4 = the cost regex, round 6 = the window), so the repair keeps the
    number and moves it: nothing is dropped, C4c prints it on its own line and C5's total is unchanged.

    Classification is `logclass.is_judgement_session_log` - the log's own `BGRUN START` COMMAND, not its name.
    Returns a dict: rsecs/rcost/rcosted/rseen (reviews), jsecs/jcost/jcosted/jseen/jlogs (judgement sessions).
    """
    out = dict(rsecs=0, rcost=0.0, rcosted=0, rseen=0, jsecs=0, jcost=0.0, jcosted=0, jseen=0, jlogs=[])
    for p in machinery_logs:
        pre = "j" if logclass.is_judgement_session_log(p) else "r"
        priced = False
        for body in window_runs(read(p), cutoff, until):
            for m in re.finditer(r"BGRUN (?:END rc=\d+|TIMEOUT killed) after (\d+)s", body):
                out[pre + "secs"] += int(m.group(1))
            out[pre + "seen"] += len(COST_SEEN_RE.findall(body))
            for m in COST_RE.finditer(body):
                out[pre + "cost"] += float(m.group(1) or m.group(2))
                out[pre + "costed"] += 1
                priced = True
        if pre == "j" and priced:
            out["jlogs"].append(os.path.basename(p))
    return out


RESULT = []
WARNS = []      # (check, count) - reported and put in --json, never a violation (A8)


def _self_test():
    """Asserted at import, not in a test file nobody runs (round-4 decision: "add a self-test line that asserts the
    regex matches the literal `COST: $5.1157` form"). Two lines of cost, one of them the exact text that defeated
    the previous regex for seven cycles."""
    sample = ("COST: $5.1157  in 48 / out 1731 / cache-create 179450 / cache-read 1074828  (296s, 14 turn(s))\n"
              '{"total_cost_usd":4.9719,"usage":{}}\n')
    got = sorted(float(a or b) for a, b in COST_RE.findall(sample))
    assert got == [4.9719, 5.1157], f"COST_RE self-test FAILED: parsed {got}, expected [4.9719, 5.1157]"
    assert len(COST_SEEN_RE.findall(sample)) == 2, "COST_SEEN_RE self-test FAILED"
    # ROUND-6 DEVICE, asserted at import for the same reason: a run that STARTED before the window is not this
    # cycle's cost, however recently the file was last written. Full cases: tools/bench/selftest_audit_cost_window.py
    two = ("BGRUN START 2026-09-18 13:30:03 limit 180.0 min: x\nCOST: $13.7777  in 1 / out 1\nBGRUN END rc=0 after 1199s\n"
           "BGRUN START 2026-09-18 13:55:00 limit 10.0 min: y\nCOST: $1.0000  in 1 / out 1\nBGRUN END rc=0 after 60s\n")
    w = (time.mktime(time.strptime("2026-09-18 13:49:00", "%Y-%m-%d %H:%M:%S")),
         time.mktime(time.strptime("2026-09-18 14:03:00", "%Y-%m-%d %H:%M:%S")))
    kept = window_runs(two, *w)
    assert len(kept) == 1 and "13:55:00" in kept[0], f"window_runs self-test FAILED: kept {kept}"
    assert window_runs("no bgrun lines here\n", *w) == ["no bgrun lines here\n"], "window_runs fallback FAILED"


_self_test()


def a2_state(body):
    """A2's reading of one log body (card 92-4): "" (no bgrun run at all), "ended" (END or TIMEOUT present),
    "killed" (no END/TIMEOUT but a `BGRUN KILLED` line from tools/bgrun_reap.py), "unfinished" (START only)."""
    if "BGRUN START" not in body:
        return ""
    if "BGRUN END" in body or "BGRUN TIMEOUT" in body:
        return "ended"
    if re.search(r"^BGRUN KILLED \(external\) pid=\d+", body, re.M):
        return "killed"
    return "unfinished"


def say(check, ok, detail):
    RESULT.append(dict(check=check, ok=ok, detail=detail))
    mark = "PASS" if ok is True else ("FAIL" if ok is False else "n-a ")
    print(f"  {mark}  {check}: {detail}", flush=True)


def read(p):
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def parse_ts(s):
    """Epoch seconds, or `YYYY-MM-DD[ HH:MM[:SS]]` in local time. Returns None for an empty value."""
    if not s:
        return None
    s = str(s).strip()
    try:
        return float(s)
    except ValueError:
        pass
    for f in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return time.mktime(time.strptime(s, f))
        except ValueError:
            continue
    raise SystemExit(f"cannot parse timestamp {s!r}; use epoch seconds or 'YYYY-MM-DD HH:MM:SS'")


JEV_CONTRADICT_STATE = os.path.join(ROOT, "tools", "bench", "jev_contradict_state.json")
JEV_CONTRADICT_MAX_PAIRS = 40          # a cycle's ceiling; the full 600-pair sweep is a measurement, not this
JEV_CONTRADICT_P = 0.85                # the suspect threshold asked for; the CLI's own default is 0.80


def _say_line(line):
    """print(), but a cp949 console may not hold the plan's arrows or emoji - a lost glyph is not a failure."""
    try:
        print(line, flush=True)
    except UnicodeEncodeError:
        print(line.encode("ascii", "backslashreplace").decode("ascii"), flush=True)


def _jev_contradict(a, plan_path=None):
    """ADVISORY. Pair the Pre-decided items ADDED since the last run against earlier ones and print suspects.

    Returns the list of printed suspect lines (for the self-test); main() ignores it. Never raises, never
    appends to RESULT, never changes an exit code. `plan_path` overrides the document (the self-test's own
    three-item plan); live callers pass nothing and get the plan whose frontmatter says `status: current`,
    the SAME predicate C7 and doc_lint's L4/L8 use."""
    lines = []
    if os.environ.get("JEV_ADVISORY_OFF") == "1" or getattr(a, "no_jev", False):
        return lines
    try:
        for d in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench")):
            if d not in sys.path:
                sys.path.insert(0, d)
        import jev
        import jev_contradict as JC
        plan = plan_path
        if plan is None:
            try:
                import doc_lint as _dl
                cur = _dl.current_plans()
                plan = cur[0] if cur else None
            except Exception:                                                  # noqa: BLE001
                plan = None
        plan = plan or JC.PLAN
        items = JC.parse_items(plan)
        if not items:
            return lines
        ids = [it["id"] for it in items]
        state = {}
        try:
            with open(JEV_CONTRADICT_STATE, encoding="utf-8") as fh:
                state = json.load(fh)
            if not isinstance(state, dict):
                state = {}
        except (OSError, ValueError):
            state = {}
        seen = set(state.get("seen_ids") or [])
        new_idx = {i for i, it in enumerate(items) if it["id"] not in seen}
        first_run = not seen
        if first_run:
            # A FIRST RUN DOES NOT BACK-PAY FOR 130 ITEMS. The whole list has already been swept once
            # (tools/bench/jev_contradict.json, 2026-09-22); this step exists for what is ADDED from now on.
            _say_line("  C8 Pre-decided contradictions: first run - %d item(s) recorded as the baseline, "
                      "no pair asked (the full sweep is tools/bench/jev_contradict.json)" % len(ids))
            new_idx = set()
        pairs = []
        if new_idx:
            for score, i, j in JC.build_pairs(items, cap=600):
                if i in new_idx or j in new_idx:
                    pairs.append((score, i, j))
                if len(pairs) >= JEV_CONTRADICT_MAX_PAIRS:
                    break
        if pairs and not jev.get_key():
            _say_line("  C8 Pre-decided contradictions: %d new item(s), %d candidate pair(s), no key - skipped"
                      % (len(new_idx), len(pairs)))
            pairs = []
        hits = 0
        for _score, i, j in pairs:
            p, _ps, err = JC.ask_pair(items[i]["text"], items[j]["text"], samples=3)
            if err or p is None or p < JEV_CONTRADICT_P:
                continue
            hits += 1
            line = "  JEV-CONTRADICT | %s↔%s p=%.2f | %s || %s" % (
                items[i]["id"], items[j]["id"], p, items[i]["title"][:70], items[j]["title"][:70])
            lines.append(line)
            _say_line(line)
        if not first_run:
            _say_line("  C8 Pre-decided contradictions: %d new item(s) since the last run, %d pair(s) asked, "
                      "%d suspect at p>=%.2f  (advisory; docs/jev-integration-plan.md 2nd wave #7)%s"
                      % (len(new_idx), len(pairs), hits, JEV_CONTRADICT_P,
                         "" if pairs or not new_idx else " - no candidate pair shared enough uncommon tokens"))
        state = {"plan": os.path.basename(plan), "seen_ids": ids, "n_items": len(ids),
                 "last_run": time.strftime("%Y-%m-%d %H:%M:%S"), "last_pairs": len(pairs),
                 "last_suspects": hits}
        tmp = JEV_CONTRADICT_STATE + ".tmp"
        try:                     # atomic: a cycle-runner cell may read this file at any moment
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(state, fh, ensure_ascii=False, indent=1)
            os.replace(tmp, JEV_CONTRADICT_STATE)
        except OSError:
            pass
    except Exception as e:                                                     # noqa: BLE001
        _say_line("  C8 Pre-decided contradictions: not run (%s)" % type(e).__name__)
    print("", flush=True)
    return lines


def c7_plan(root=None, next_path=None):
    """Which plan document C7 measures scope against. Returns (path or None, basis string).

    REPAIRED 2026-09-26 (card 90-2; retrospective-cycle89 `device-failed`, threshold 1): for eight cycles C7 read
    `doc_lint.current_plans()[0]` = `docs/cycle27-plan.md` while the cycles were actually working from
    `docs/d1-loop12-17-split-plan.md`, the plan the runner's own `tools/bench/next.json` names in `plan.path`.
    Order now: (1) next.json `plan.path` when the file exists (relative to `root`, either slash flavour);
    (2) `doc_lint.current_plans()`; (3) the newest `docs/cycle<N>-plan.md`. Only the plan SOURCE changed; the
    scan below is untouched. `root`/`next_path` exist for the self-test (tools/bench/selftest_audit_c7.py)."""
    root = root or ROOT
    next_path = next_path or os.path.join(root, "tools", "bench", "next.json")
    try:
        with open(next_path, encoding="utf-8") as fh:
            nx = json.load(fh)
        rel = (nx.get("plan") or {}).get("path") if isinstance(nx, dict) else None
        if isinstance(rel, str) and rel.strip():
            cand = rel if os.path.isabs(rel) else os.path.join(root, rel.replace("/", os.sep).replace("\\", os.sep))
            if os.path.isfile(cand):
                return cand, "tools/bench/next.json plan.path"
            print(f"  C7 note: next.json plan.path {rel!r} does not exist; falling back to `status: current`")
        else:
            print("  C7 note: next.json has no plan.path; falling back to `status: current`")
    except FileNotFoundError:
        print("  C7 note: tools/bench/next.json absent; falling back to `status: current`")
    except Exception as e:                                                     # noqa: BLE001
        print(f"  C7 note: next.json unreadable ({e}); falling back to `status: current`")
    plan, plan_basis = None, ""
    try:
        import doc_lint as _dl
        cur = _dl.current_plans()
        if cur:
            plan, plan_basis = cur[0], "frontmatter `status: current`"
            if len(cur) > 1:                       # doc_lint L4 FAILs on this; C7 just says which it took
                plan_basis += f" (WARNING: {len(cur)} current plans, took the first)"
    except Exception as e:                                                     # pragma: no cover
        print(f"  C7 note: doc_lint.current_plans() unavailable ({e}); falling back to the newest cycle plan")
    if plan is None:
        pl = [(int(m.group(1)), p) for p in glob.glob(os.path.join(root, "docs", "cycle*-plan.md"))
              for m in [re.match(r"cycle(\d+)-plan\.md$", os.path.basename(p))] if m]
        if pl:
            plan, plan_basis = max(pl)[1], "FALLBACK: newest docs/cycle<N>-plan.md, none is `status: current`"
    return plan, plan_basis


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since-hours", type=float, default=24.0)
    ap.add_argument("--from", dest="ts_from", default=None,
                    help="window start: epoch seconds or 'YYYY-MM-DD HH:MM:SS' (overrides --since-hours)")
    ap.add_argument("--to", dest="ts_to", default=None,
                    help="window end: epoch seconds or 'YYYY-MM-DD HH:MM:SS' (default: now)")
    ap.add_argument("--cycle", type=int, default=None,
                    help="cycle number: labels the run and picks the window. C7's plan document is NOT "
                         "derived from it - it is the plan whose frontmatter says `status: current` "
                         "(doc_lint.current_plans(); repaired 2026-09-18, STATUS.md OPEN 56)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-jev", dest="no_jev", action="store_true",
                    help="skip C8, the advisory Pre-decided contradiction reading (no network, no cost)")
    a = ap.parse_args()
    # SCOPE WARNING, from the first retrospective: --since-hours is a TIME WINDOW, not a cycle boundary. On
    # 2026-09-15 a 20-hour window swept 77 logs covering cycles 1-7 and earlier rotor work, and the cost lines were
    # then quoted as "cycle 7". --from/--to close the window at BOTH ends; retrospective v2 derives them from the
    # cycle's plan documents. With --since-hours alone, `until` stays +inf and behaviour is byte-identical to before.
    tf, tt = parse_ts(a.ts_from), parse_ts(a.ts_to)
    if tf is not None:
        cutoff, until = tf, (tt if tt is not None else time.time())
        window = f"{time.strftime('%Y-%m-%d %H:%M', time.localtime(cutoff))} .. " \
                 f"{time.strftime('%Y-%m-%d %H:%M', time.localtime(until))} " \
                 f"({(until - cutoff) / 60:.0f} min, an explicit cycle window)"
    else:
        cutoff, until = time.time() - a.since_hours * 3600, float("inf")
        window = f"last {a.since_hours:g} h (a TIME WINDOW, not a cycle boundary - scope the quote accordingly)"
    logs = [p for p in glob.glob(os.path.join(BENCH, "*.log")) if cutoff <= os.path.getmtime(p) <= until]
    # A REVIEW'S OWN LOG IS NOT A BUILD LOG. Until 2026-09-15 only `peer_*` was recognised, so the dispatcher logs
    # of the retrospective, the outcome review and the new prior-art review were counted as BUILDS - inflating the
    # cost line the retrospective then argues about, and hiding the review traffic it is meant to see.
    # The classifier now lives in tools/logclass.py - it was maintained separately in three files and had already
    # diverged (2026-09-16 lint). This copy was two terms behind guard_cycle's and counted `stall_pid*.log` as
    # builds, which is what made A1 report "NO BGRUN line" for two watchdog RECORDS.
    build_logs, peer_logs = logclass.split(logs)
    # Scope reviews by the DATE IN THE FILENAME/frontmatter, not by mtime: a bulk edit (the 2026-09-15 frontmatter
    # pass touched all 216 peer files) rewrites every mtime and would drag years of history into the window.
    day_cut = time.strftime("%Y-%m-%d", time.localtime(cutoff))
    day_end = time.strftime("%Y-%m-%d", time.localtime(until)) if until != float("inf") else "9999-12-31"
    reviews = [p for p in glob.glob(os.path.join(PEER, "*.md"))
               if (re.match(r"(\d{4}-\d{2}-\d{2})", os.path.basename(p)) or [None])[0] is not None
               and day_cut <= re.match(r"(\d{4}-\d{2}-\d{2})", os.path.basename(p)).group(1) <= day_end]
    print(f"\n== cycle audit, {window}: {len(build_logs)} build logs, {len(peer_logs)} peer logs, "
          f"{len(reviews)} archived reviews\n"
          f"   (A4 scopes reviews by the DATE in the filename, so it is day-granular even inside a tight window)\n",
          flush=True)

    # A1 - bgrun discipline
    bypass = [os.path.basename(p) for p in build_logs if "BGRUN START" not in read(p)]
    say("A1 every build log came from bgrun", not bypass, f"{len(build_logs) - len(bypass)}/{len(build_logs)} ok"
        + (f"; NO BGRUN line in {bypass}" if bypass else ""))

    # A2 - every run terminated. SELF-MEASUREMENT: when this audit runs inside a bgrun (the retrospective does
    # exactly that), that log cannot have its END line yet, and the first retrospective duly reported A2 as failed
    # and called STATUS's "audit passed" inaccurate. The still-running log is therefore listed, not counted.
    # KILLED (card 92-4): a runner taken down by an OUTSIDE tree kill cannot write END; `tools/bgrun_reap.py` appends
    # `BGRUN KILLED (external) pid=<n>` once its pid is gone. Such a log is ENDED-BUT-FLAGGED here: A2 does not fail
    # on it (the record is closed) but it is LISTED, never silent - a kill is a fact the retrospective must see.
    running = os.environ.get("BGRUN_LOG", "")
    unfinished, in_flight, killed = [], [], []
    for p in build_logs:
        st = a2_state(read(p))
        if st == "unfinished":
            (in_flight if os.path.basename(p) == os.path.basename(running) else unfinished).append(os.path.basename(p))
        elif st == "killed":
            killed.append(os.path.basename(p))
    say("A2 every bgrun ended (END or TIMEOUT)", not unfinished,
        ("all runs accounted for" if not unfinished else f"unfinished: {unfinished}")
        + (f"; still running (this audit's own runner): {in_flight}" if in_flight else "")
        + (f"; KILLED from outside, closed by bgrun_reap (flagged): {killed}" if killed else ""))

    # A3 - a failing log must be followed by an archived review
    failing = [p for p in build_logs if log_failed(read(p))]
    unreviewed = []
    for p in failing:
        t = os.path.getmtime(p)
        if not any(os.path.getmtime(r) > t for r in glob.glob(os.path.join(PEER, "*.md"))):
            unreviewed.append(os.path.basename(p))
    say("A3 every failing log is followed by an archived review", not unreviewed,
        f"{len(failing)} logs recorded a failure; unreviewed: {unreviewed or 'none'}")

    # A4 - reviews are annotated (an unused review is a skipped review). Check the "What was done with it" SECTION
    # only: the template's `why asked` field carries the same placeholder, and matching the whole file reported 66
    # false violations on its first run (2026-09-15) - a checker that cries wolf gets ignored, which is worse than
    # not having it.
    blank = []
    for p in reviews:
        body = read(p)
        i = body.find("## What was done with it")
        tail = body[i + len("## What was done with it"):].strip() if i >= 0 else ""
        if i < 0 or tail.startswith("(Claude fills in)") or not tail:
            blank.append(os.path.basename(p))
    say("A4 every archived review says what was done with it", not blank,
        f"{len(reviews) - len(blank)}/{len(reviews)} annotated" + (f"; blank: {blank[:6]}{'…' if len(blank) > 6 else ''}" if blank else ""))

    # A5 - the original is untouched
    if os.path.exists(MAIN):
        md5 = hashlib.md5(open(MAIN, "rb").read()).hexdigest()
        touched = cutoff <= os.path.getmtime(MAIN) <= until
        say("A5 the main VI was not modified in this window", not touched,
            f"md5 {md5[:12]}…, mtime {time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getmtime(MAIN)))}")
    else:
        say("A5 the main VI was not modified in this window", None, "main VI not found from this machine")

    # A7 - vault hygiene: an archive note must not wikilink INTO the active set, or the Obsidian graph fills with
    # 200+ peer exchanges around every live document (user, 2026-09-15). Plain paths are fine; [[wikilinks]] are not.
    active_stems = {os.path.splitext(f)[0] for f in os.listdir(ROOT) if f.endswith(".md")}
    docs_dir = os.path.join(ROOT, "docs")
    if os.path.isdir(docs_dir):
        active_stems |= {os.path.splitext(f)[0] for f in os.listdir(docs_dir) if f.endswith(".md")}
    leaks = []
    for p in glob.glob(os.path.join(ROOT, "archive", "**", "*.md"), recursive=True):
        for link in re.findall(r"\[\[([^\]|#]+)", read(p)):
            if os.path.basename(link.strip()) in active_stems:
                leaks.append(f"{os.path.relpath(p, ROOT)} -> [[{link.strip()}]]")
    say("A7 no archive note wikilinks into the active set", not leaks,
        "archive links stay inside archive" if not leaks else f"{len(leaks)} leak(s): {leaks[:4]}")

    # A6 - GUI actions are recorded
    gui_log = os.path.join(HERE, "gui_actions.log")
    recent_gui = [l for l in read(gui_log).splitlines() if l.strip()] if os.path.exists(gui_log) else []
    say("A6 state-changing GUI actions are recorded", None,
        f"{len(recent_gui)} lines in gui_actions.log (all time); this cycle used no GUI if the retrospective agrees")

    # A8 - C6 compliance (session protocol v1 wiring, 2026-09-24): bgrun marks a recipe/bench run that ended with no
    # RESULT line as `BGRUN END ... (NO RESULT LINE)`. Its verdict fell back to the exit code alone, so it is a WARN,
    # never a violation: counted and named, and it does not change `AUDIT PASS`.
    no_result = sorted({os.path.basename(p) for p in build_logs for s in window_runs(read(p), cutoff, until)
                        if re.search(r"^BGRUN END rc=-?\d+ after \d+s \(NO RESULT LINE\)", s, re.M)})
    print(f"  {'WARN' if no_result else 'PASS'}  A8 recipe/bench runs ended with a RESULT line (C6): "
          + (f"{len(no_result)} log(s) with a run that printed none: {no_result[:6]}{'…' if len(no_result) > 6 else ''}"
             if no_result else "every scoped run in the window printed one (or predates the mark)"), flush=True)
    WARNS.append(("A8", len(no_result)))

    # cost lines
    # EVERY COST LINE BELOW IS SUMMED OVER `window_runs`, NOT OVER WHOLE FILES - see BGRUN_START_RE above.
    starts = sum(s.count("BGRUN START") for p in build_logs for s in window_runs(read(p), cutoff, until))
    fails = sum((seg_failures(s) if BGRUN_START_RE.match(s) else len(FAILURE_RE.findall(s)))
                for p in build_logs for s in window_runs(read(p), cutoff, until))
    secs = 0
    for p in build_logs:
        for s in window_runs(read(p), cutoff, until):
            for m in re.finditer(r"BGRUN (?:END rc=\d+|TIMEOUT killed) after (\d+)s", s):
                secs += int(m.group(1))
    # C4 - REVIEW COST, which C3 used to hide entirely (device for `unreported-fact`, 2026-09-16, round 2).
    # C3 sums only BUILD logs, because peer/priorart logs are deliberately excluded from `is_build_log`. The
    # consequence was not cosmetic: the cycle-10 audit reported "3 min 12 s" for a cycle whose reviews actually
    # took 48 min 40 s and $28.5530, and the reviewer had to reconstruct the real number by hand from the peer
    # logs before it could judge whether the cycle was worth its cost (retrospective-cycle10, section 6). Every
    # cost-versus-value argument the retrospective layer exists to have was being made against a figure an order
    # of magnitude too small. Reviews stay OUT of C3 - they are evidence, not builds - and get their own line.
    # THE JUDGEMENT SESSION'S OWN BGRUN IS NOT A REVIEW (round 7, 2026-09-22) - see cost_split().
    cs = cost_split(peer_logs, cutoff, until)
    rsecs, rcost, rcosted, rseen = cs["rsecs"], cs["rcost"], cs["rcosted"], cs["rseen"]
    jsecs, jcost, jcosted, jlogs = cs["jsecs"], cs["jcost"], cs["jcosted"], cs["jlogs"]

    print(f"\n  C1 builds run {starts}, failure markers {fails}, logs carrying a failure {len(failing)}")
    print(f"  C2 peer reviews dispatched {len(peer_logs)}, archived {len(reviews)}")
    print(f"  C3 wall-clock inside bgrun, BUILDS ONLY {secs // 60} min {secs % 60} s")
    print(f"  C4 wall-clock inside bgrun, REVIEWS {rsecs // 60} min {rsecs % 60} s"
          + (f"; cost ${rcost:.4f} from {rcosted} log(s) that report one" if rcosted
             else "; no log reported a cost - treat the review cost as UNKNOWN, not as zero"))
    # SEEN vs PARSED - the visibility half of the round-4 device. A parser that silently drops every cost line
    # reports the same "$0.00 / no cost" as a cycle that genuinely bought no reviews, and that is exactly how the
    # old regex hid $20.42. A mismatch here names the bug instead of printing a plausible number.
    print(f"  C4b cost lines seen {rseen} / parsed {rcosted}"
          + ("" if rseen == rcosted else "   <- MISMATCH: a cost line in the logs is not being parsed; the C4 "
                                         "figure is an UNDERSTATEMENT, not a measurement"))
    # C4c - THE JUDGEMENT SESSION'S OWN SPEND, on its own line so the repair MOVES the number instead of dropping
    # it. This is usually the largest single figure in a cycle and it went unreported in the session's own account
    # (retrospective-cycle64 finding 6: "$51.62 ... 81% of the cycle's total dollar spend ... STATUS.md itemizes
    # $6.30, $2.69 and $3.38 and never mentions it"). It is NOT review traffic and NOT a build.
    print(f"  C4c judgement session (cycle_runner's own `claude -p`), NOT a review: "
          f"{jsecs // 60} min {jsecs % 60} s"
          + (f"; cost ${jcost:.4f} from {jcosted} log(s) - {', '.join(jlogs)}" if jcosted
             else "; no judgement-session cost line in this window")
          + ("" if cs["jseen"] == jcosted else
             f"   <- MISMATCH: {cs['jseen']} cost line(s) seen, {jcosted} parsed"))
    total = secs + rsecs + jsecs
    print(f"  C5 total wall-clock {total // 60} min {total % 60} s"
          f"  (builds {100 * secs // max(1, total)}%, reviews {100 * rsecs // max(1, total)}%, "
          f"judgement session {100 * jsecs // max(1, total)}%)\n")

    # C6 - THE JUDGEMENT/MATERIAL SPLIT, counted from the machine's record (2026-09-16). guard_bash.py refuses a
    # recipe/bench run that carries no `MATERIAL=1` marker and logs both the marked runs and the refusals; a
    # refusal here means a judgement session tried to do material work itself, which is the thing CLAUDE.md
    # section 3 exists to stop. Counting it in the session that did it would be counting by memory - the user's
    # standing objection ("회고가 반복해서 위반을 지적하는지는 어떻게 알아?").
    marked = refused = 0
    for line in read(os.path.join(HERE, "hooks", "material_marker.log")).splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        try:
            t = time.mktime(time.strptime(parts[0], "%Y-%m-%d %H:%M:%S"))
        except ValueError:
            continue
        if t < cutoff or t > until:
            continue
        if parts[1] == "MARKED":
            marked += 1
        elif parts[1] == "REFUSED":
            refused += 1
    print(f"  C6 material-marked recipe/bench runs {marked}, judgement-session attempts refused {refused}"
          + ("" if not refused else "  <- delegate to the `material` agent instead") + "\n")

    # C7 - THE DEVICE FOR `scope-creep` (docs/violation-decisions.md, 2026-09-16 19:16, round 3). Occurrences:
    # cycles 7, 10, 11; the cycle-11 instance is the 26-wrapper `ensure_loaded` patch made on ONE measured case and
    # the `OpDelete_v1` rebuild the plan never asked for. A COUNTER, NOT A REFUSAL, by the decision's own wording:
    # an out-of-plan change is sometimes exactly right (a measured bug fix), so the verdict stays with the
    # retrospective - only the LIST is taken away from Claude, who is otherwise the one summarising its own scope.
    # Excluded by the brief: archive/ (history, rewritten in bulk), tools/bench/*.log|*.json (a cycle's own output,
    # which would drown the signal), and .claude/ (harness config).
    # "Named in the plan" is generous on purpose - the relative path in either slash flavour, or the bare filename.
    # A checker that cries wolf gets ignored (the A4 lesson of 2026-09-15), and plans cite `OpOwnerChain_v1.vi` and
    # `build_x.py` far more often than a full path. False NEGATIVES here are cheap; false positives are not.
    # WHICH PLAN (repaired 2026-09-18, cycle 35, STATUS.md OPEN 56). C7 used to build the filename from the cycle
    # number, `docs/cycle<N>-plan.md`. That went DEAD when the scheme moved to ONE plan spanning cycles 27+
    # (docs/cycle27-plan.md): with `--cycle 35` - which is how cycle_runner always calls it - the candidate file
    # simply did not exist, so `plan` was None and C7 printed "scope cannot be checked mechanically" every cycle.
    # It now reads the SAME predicate doc_lint's L4/L8 use, `doc_lint.current_plans()` = the plan whose frontmatter
    # says `status: current`, so a future scheme rename breaks one function instead of three. The cycle NUMBER
    # still selects the time window (cutoff/until above); it no longer selects the document.
    plan, plan_basis = c7_plan()
    if plan is None:
        print("  C7 out-of-plan files: no docs/cycle*-plan.md found - scope cannot be checked mechanically\n")
    else:
        ptext = read(plan)
        skip_dirs = {"archive", ".claude", ".git", "__pycache__", ".obsidian", "node_modules", ".venv"}
        out_of_plan = []
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames if d not in skip_dirs]
            for fn in filenames:
                fp = os.path.join(dirpath, fn)
                rel = os.path.relpath(fp, ROOT).replace(os.sep, "/")
                if rel.startswith("tools/bench/") and os.path.splitext(fn)[1].lower() in (".log", ".json"):
                    continue
                if os.path.abspath(fp) == os.path.abspath(plan):
                    continue          # a plan rarely names itself; listing it is a guaranteed false positive
                try:
                    if not (cutoff <= os.path.getmtime(fp) <= until):
                        continue
                except OSError:
                    continue
                if rel in ptext or rel.replace("/", "\\") in ptext or fn in ptext:
                    continue
                out_of_plan.append(rel)
        out_of_plan.sort()
        shown = ", ".join(out_of_plan[:12]) + ("…" if len(out_of_plan) > 12 else "")
        print(f"  C7 files modified in the window but NOT named in "
              f"{os.path.relpath(plan, ROOT).replace(os.sep, '/')} [{plan_basis}]: "
              f"{len(out_of_plan)}" + (f" - {shown}" if out_of_plan else " - none") + "\n")

    # C8 - PRE-DECIDED CONTRADICTIONS (docs/jev-integration-plan.md 2nd wave #7; user 2026-09-23 "Jev 최대한
    # 활용하는 방법으로 제시한게 위의 테이블이잖아"). The plan's `## Pre-decided` list is past 130 numbered items
    # written over five days, and several exist only to withdraw or supersede an earlier one; nothing mechanical
    # tells a material session that item 88 has already withdrawn item 81. This runs `tools/jev_contradict.py`
    # over that list at cycle close and prints the suspect pairs into the audit output, which the retrospective
    # attaches - so the pairs reach a judgement session without anyone having to ask for them.
    #
    # ADVISORY, NEVER A GATE: nothing below appends to RESULT, so `AUDIT VIOLATIONS:` can never name it, and
    # every failure (no key, no network, an unparseable plan, any exception) is silence. Deciding WHICH of two
    # decisions stands is the judgement call CLAUDE.md reserves, and the measurement says why it may not be more
    # than a signal: 8 of 13 known withdrawals were found, and the pairing itself only nominated 7 of those 13.
    #
    # COST IS BOUNDED BY THE STATE FILE. The full run is 600 pairs x 3 samples = 265 s; that is a measurement,
    # not a per-cycle cost. tools/bench/jev_contradict_state.json remembers which item ids have been paired, so
    # a cycle only pays for pairs involving items ADDED since the last run - a few pairs, or none at all.
    _jev_contradict(a)

    # L - THE DOCUMENT LINT (CLAUDE.md section 4, "Documents are LINTED by code and INGESTED by a model every
    # cycle"; cadence "every cycle close, run by audit_cycle"). It runs HERE rather than as a separate command so
    # there is no second thing to remember, which is the same reason the compliance checks live in one script.
    # --skip-dispositions: A4 above already FAILS on a placeholder disposition with the same file list, and the
    # prior-art review of docs/doc-lint-plan.md fired `already-built` on exactly that duplication - one condition
    # must not have two FAIL sources. `doc_lint.py` standalone still checks it.
    # Its FAILs are reported as audit checks so `AUDIT VIOLATIONS:` names them, but the lint's own WARN lines are
    # printed and not counted: a warning that blocks is a warning nobody reads.
    try:
        import doc_lint
        lint = doc_lint.run(skip_dispositions=True)
    except Exception as e:                         # a broken linter must never take the compliance audit with it
        lint = [("WARN", "L0 document lint", f"doc_lint.py did not run: {e}")]
    print("\n== document lint (tools/doc_lint.py; CLAUDE.md section 4)\n", flush=True)
    for level, check, detail in lint:
        if level == "FAIL":
            say(check, False, detail)
        else:
            print(f"  {level}  {check}: {detail}", flush=True)
    print("", flush=True)

    bad = [r for r in RESULT if r["ok"] is False]
    print(f"AUDIT {'PASS' if not bad else 'VIOLATIONS: ' + ', '.join(r['check'] for r in bad)}\n", flush=True)
    if a.json:
        print(json.dumps(dict(checks=RESULT, warns=dict(WARNS), builds=starts, failures=fails, failing_logs=len(failing),
                              reviews_dispatched=len(peer_logs), reviews_archived=len(reviews), bgrun_seconds=secs),
                         indent=1))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
