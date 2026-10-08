# ---
# labview: none
# hardware: none
# evidence: tools/bench/selftest_c148_assign_leak.py:106
# ---
r"""selftest_c148_assign_leak - card 148-a2-1 (gate-fp fp-60): a self-test run inside an assignment session's env must not
write that session's assignment state.

THE LEAK (measured, tools/bench/diag_c148_a2_1_measure.log): material sessions inherit CYCLE_SESSION=1 CYCLE_ROLE=assign
ASSIGN_STATE=<live state>; selftest_chat_p1.py feeds guard_session.py a fixture card p1s-A (temp dir, flags.write tools/**)
with that env, guard_assign.check_dispatch evaluates it against the live purpose and writes a sticky c-outside-purpose
hand-back into the live state (tools/bench/assign/state_148_1.json:45-50).

WHAT EXISTED: selftest_assign_flow.py (guard_assign end to end, its own throwaway states), selftest_c148_guard_fp.py
(card_outside window); neither runs a fixture card under a polluted env. Nothing here touches a live state file: every
state is a temp file, every card a temp file or a dict.

GATES (PREDICTION after the fix; on the pre-edit guard_assign / self-tests L1, L4 and L5 FAIL):
  L1 polluted env (CYCLE_SESSION=1 CYCLE_ROLE=assign ASSIGN_STATE=<temp copy>) + fixture card OUTSIDE tools/bench/cards,
     through the real guard_session.py subprocess -> the temp state is byte-identical afterwards (no hand-back/refusal/entry)
  L2 control: the same dispatch with ASSIGN_CARDS_DIR = the fixture's dir -> sticky c-outside-purpose naming the card
     (the fixture WOULD hand back if it counted: L1 is not vacuous)
  L3 in-process: a card path under <ROOT>/tools/bench/cards (mixed separators, as the runner writes them) is still
     evaluated: the same card -> hand-back c written to the state
  L4 in-process: the same card dict at a temp path -> refused (rc 2), state byte-identical, the message says why
  L5 every census self-test that spawns guard_session.py drops ASSIGN_STATE / CYCLE_ROLE / CYCLE_SESSION at module level
Args: --guard-assign <file> runs a candidate guard_assign.py as if it sat at tools/hooks/guard_assign.py (L1-L4).
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TOOLS = os.path.join(ROOT, "tools")
HOOKS = os.path.join(TOOLS, "hooks")
GS = os.path.join(HOOKS, "guard_session.py")
LIVE_GA = os.path.join(HOOKS, "guard_assign.py")
sys.path.insert(0, TOOLS)
sys.path.insert(0, HOOKS)
for _k in ("ASSIGN_STATE", "CYCLE_ROLE", "CYCLE_SESSION"):      # this test sets its own throwaway values per call
    os.environ.pop(_k, None)
import protocol as P  # noqa: E402

CAND = os.path.abspath(sys.argv[sys.argv.index("--guard-assign") + 1]) if "--guard-assign" in sys.argv else LIVE_GA
CENSUS = ["selftest_assign_flow.py", "selftest_chat_p1.py", "selftest_chat_p2.py", "selftest_guard_session.py",
          "selftest_guard_session_pairing.py"]
POP_RE = re.compile(r'^for _k in \("ASSIGN_STATE", "CYCLE_ROLE", "CYCLE_SESSION"\):[^\n]*\n\s+os\.environ\.pop\(_k, None\)',
                    re.M)
# the cycle-148 round-1 purpose (tools/bench/assign/state_148_1.json:6-32), as a literal: the live file is never opened
PURPOSE = {"act": "PD358: tooling card ALONE drains gate-fp fp-51..59", "pass": ["fp-51..fp-59 all drained"],
           "plan": {"path": "docs/d1/ring-p4c.md", "md5": None}, "advances": ["M3", "R1"], "unblocks": None,
           "task_kind": "build", "note": None}
FIXTURE = {"schema": "task/1", "id": "leak-A", "kind": "build", "goal": "fixture (selftest_chat_p1.py:113 shape)",
           "advances": ["M3"], "flags": {"labview": "build", "gui": False, "hardware": "none", "run_vi": False,
                                         "write": ["tools/**", "docs/**", ".claude/agents/**"], "status_edit": False,
                                         "git_commit": False, "peers": []}, "budget": {"failures": 2, "minutes": 60}}
RES = []
TMP = tempfile.mkdtemp(prefix="c148leak_")
SIDS = []


def gate(label, ok, detail=""):
    RES.append((label, bool(ok)))
    print("  %-4s %-70s %s" % ("ok" if ok else "BAD", label, str(detail)[:200]), flush=True)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def load_ga():
    m = types.ModuleType("guard_assign")
    m.__file__ = LIVE_GA
    exec(compile(open(CAND, encoding="utf-8").read(), LIVE_GA, "exec"), m.__dict__)
    return m


GA = load_ga()
SHIM = ("import sys, types; c, live, gs = sys.argv[1], sys.argv[2], sys.argv[3]; m = types.ModuleType('guard_assign'); "
        "m.__file__ = live; exec(compile(open(c, encoding='utf-8').read(), live, 'exec'), m.__dict__); "
        "sys.modules['guard_assign'] = m; sys.argv = [gs]; import runpy; runpy.run_path(gs, run_name='__main__')")


def fresh_state(name):
    p = os.path.join(TMP, "state_%s.json" % name)
    GA.new_state(p, 148, 1, PURPOSE, "0" * 32, os.path.join(TMP, "no_decisions.json"))
    return p


def hook(st, card_path, extra=None):
    env = dict(os.environ, CYCLE_SESSION="1", CYCLE_ROLE="assign", ASSIGN_STATE=st)
    env.pop("ASSIGN_CARDS_DIR", None)
    env.pop("BENCH_CELL", None)
    env.update(extra or {})
    sid = "selftest-c148leak-%d-%d" % (os.getpid(), len(SIDS))
    SIDS.append(sid)
    payload = {"session_id": sid, "tool_name": "Agent", "tool_input": {"subagent_type": "material",
                                                                       "prompt": "CARD %s" % card_path}}
    p = subprocess.run([sys.executable, "-c", SHIM, CAND, LIVE_GA, GS], input=json.dumps(payload), text=True,
                       capture_output=True, encoding="utf-8", errors="replace", timeout=60, cwd=ROOT, env=env)
    return p.returncode, (p.stderr or "") + (p.stdout or "")


def main():
    print("guard_assign under test: %s (md5 %s)" % (os.path.relpath(CAND, ROOT), md5(CAND)), flush=True)
    cards = os.path.join(TMP, "cards_s")
    os.makedirs(cards)
    cp = os.path.join(cards, "task_leak-A.json")
    json.dump(FIXTURE, open(cp, "w", encoding="utf-8"), indent=1)
    try:
        # L1
        st = fresh_state("l1")
        m0 = md5(st)
        rc, out = hook(st, cp)
        s1 = GA.state_load(st)
        gate("L1 polluted env + fixture card outside tools/bench/cards: temp state unchanged", md5(st) == m0,
             "rc %s, handback %s, refusals %d, cards %d" % (rc, (s1.get("handback") or {}).get("trigger"),
                                                           len(s1.get("refusals") or []), len(s1.get("cards") or [])))
        # L2
        st = fresh_state("l2")
        rc, out = hook(st, cp, {"ASSIGN_CARDS_DIR": cards})
        hb = GA.state_load(st).get("handback") or {}
        gate("L2 control: ASSIGN_CARDS_DIR = fixture dir -> hand-back c naming leak-A",
             rc == 2 and hb.get("trigger") == "c-outside-purpose" and "leak-A" in str(hb.get("detail")),
             (rc, hb.get("trigger")))
        # L3
        st = fresh_state("l3")
        inside = os.path.join(ROOT, "tools/bench/cards/task_leak-A.json")       # mixed separators, as in a live state
        rc3, msg3 = GA.check_dispatch(st, "material", dict(FIXTURE), inside)
        hb3 = GA.state_load(st).get("handback") or {}
        gate("L3 a card under <ROOT>/tools/bench/cards is still evaluated (hand-back c)",
             rc3 == 2 and hb3.get("trigger") == "c-outside-purpose", (rc3, hb3.get("trigger")))
        # L4
        st = fresh_state("l4")
        m4 = md5(st)
        rc4, msg4 = GA.check_dispatch(st, "material", dict(FIXTURE), cp)
        gate("L4 the same card at a temp path: refused, state unchanged, reason given",
             rc4 == 2 and md5(st) == m4 and "tools/bench/cards" in msg4, (rc4, md5(st) == m4, msg4[:120]))
        # L5
        miss = [f for f in CENSUS if not POP_RE.search(open(os.path.join(HERE, f), encoding="utf-8").read())]
        gate("L5 census self-tests drop ASSIGN_STATE/CYCLE_ROLE/CYCLE_SESSION at module level", not miss, miss)
    finally:
        import guard_session as G
        for sid in SIDS:
            for p in (G.state_path(G.SAFE_RE.sub("_", sid)), G.state_path(G.SAFE_RE.sub("_", sid)) + ".lock"):
                if os.path.isfile(p):
                    os.remove(p)
        shutil.rmtree(TMP, ignore_errors=True)
    npass = sum(1 for _l, ok in RES if ok)
    bad = [lab for lab, ok in RES if not ok]
    print("SUMMARY %d/%d gates pass%s" % (npass, len(RES), ("; not passing: " + ", ".join(bad)) if bad else ""))
    print(P.result_line(P.make_result(npass, len(bad), bad[0] if bad else None)), flush=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
