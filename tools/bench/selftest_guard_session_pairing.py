r"""Self-test for guard_session.py (g): no gate-tool edit beside a LabVIEW card (card 133-4,
docs/violation-decisions.md "wrong-ordering - 2026-10-02 08:25").

Existing tools found first: selftest_guard_session.py (G1-G27, cap/retro/chat), selftest_chat_p1.py S1-S7 (pipeline),
selftest_chat_p2.py S5 (escalation). None covers write-glob pairing; this file adds only that.
No LabVIEW, no agents: synthetic + recorded PreToolUse payloads piped to the hook as subprocesses.
GS_UNDER_TEST=<path> runs a candidate file as if it sat at tools/hooks/guard_session.py (exec with __file__ = live).

PREDICTION CONTRACT (10 gates):
  P1 132-1 (none, writes stage_prerun.py ...) then 132-2 (build) -> 2nd REFUSED "LabVIEW CARD BESIDE A GATE-TOOL EDIT"
  P2 132-2 then 132-1 -> 2nd REFUSED "GATE-TOOL EDIT BESIDE A LabVIEW CARD"
  P3 132-2 + an offline card writing only tools/bench/** -> ALLOWED (and its live record carries "write")
  P4 two offline cards, one writing tools/stagexec.py -> both ALLOWED
  P5 legacy live entry (no "write" key, card = 132-1) then 132-2 -> REFUSED, judged from the "card file"
  P6 legacy live entry whose card file is unreadable, then 132-2 -> REFUSED "CANNOT READ", names the card id
  P7 legacy live entry whose card writes only tools/bench/** then 132-2 -> ALLOWED
  P8 an offline card writing `tools/**` beside 132-2 -> REFUSED (a glob that MATCHES a tool counts)
  P9 recorded Agent tool_input (cycle 132 transcript, 132-2) with harness fields, fresh session -> exit 0
  P10 recorded tool_inputs 132-1 then 132-2, same session -> exit 0 then exit 2
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TOOLS = os.path.join(ROOT, "tools")
LIVE = os.path.join(TOOLS, "hooks", "guard_session.py")
if "--candidate" in sys.argv:                   # CLI form of GS_UNDER_TEST (env prefixes are auto-denied)
    os.environ["GS_UNDER_TEST"] = os.path.abspath(sys.argv[sys.argv.index("--candidate") + 1])
CAND = os.environ.get("GS_UNDER_TEST") or LIVE
CARDS = os.path.join(HERE, "cards")
# RELATIVE, as the judgement session writes them: the project path holds a space and CARD_RE takes \S+, so an
# absolute path here would be read as an unreadable card (labview "read", id "zz_LabView") - measured on the first run
C1, C2 = "tools/bench/cards/task_132-1.json", "tools/bench/cards/task_132-2.json"
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "hooks"))
import guard_session as G  # noqa: E402  (state_path/load/save only - unchanged by (g))
import protocol as P  # noqa: E402
SHIM = ("import sys; p, L = sys.argv[1], sys.argv[2]; sys.argv = [L]; "
        "exec(compile(open(p, encoding='utf-8').read(), L, 'exec'), {'__name__': '__main__', '__file__': L})")
TMP = tempfile.mkdtemp(prefix="gsp_")
RES, SIDS = [], []
# recorded: archive transcript d8fa9862-....jsonl lines 148/149 (cycle 132 judgement's Agent calls)
REC1 = {"description": "132-1 stage_prerun tooling", "subagent_type": "material",
        "prompt": "CARD tools/bench/cards/task_132-1.json", "run_in_background": False}
REC2 = {"description": "132-2 P3b-1 graph read", "subagent_type": "material",
        "prompt": "CARD tools/bench/cards/task_132-2.json", "run_in_background": False}


def gate(label, ok, detail=""):
    RES.append((label, bool(ok)))
    print("  %-4s %-62s %s" % ("ok" if ok else "BAD", label, str(detail)[:150]), flush=True)


def sid(tag):
    s = "selftest-gsp-%s-%d" % (tag, os.getpid())
    SIDS.append(s)
    return s


def hook(payload):
    env = dict(os.environ)
    env.pop("CYCLE_SESSION", None)
    env.pop("BENCH_CELL", None)
    cmd = [sys.executable, LIVE] if CAND == LIVE else [sys.executable, "-c", SHIM, CAND, LIVE]
    p = subprocess.run(cmd, input=json.dumps(payload), text=True, capture_output=True, timeout=60, cwd=ROOT, env=env)
    return p.returncode, p.stderr or ""


def disp(s, card_path):
    return hook({"session_id": s, "tool_name": "Agent", "tool_input": {"subagent_type": "material",
                                                                       "prompt": "CARD %s" % card_path}})


def mk(cid, labview, write):
    d = json.load(open(os.path.join(ROOT, C2), encoding="utf-8"))
    d["id"], d["flags"] = cid, dict(d["flags"], labview=labview, write=write)
    p = os.path.join(TMP, "task_%s.json" % cid)
    json.dump(d, open(p, "w", encoding="utf-8"))
    return p


def legacy(s, card_path, cid):
    """A live entry as recorded before (g): no 'write' key."""
    G.save(G.SAFE_RE.sub("_", s), {"dispatches": 1, "retro_done": False,
                                   "live": [{"id": cid, "labview": "none", "t": time.time(), "card": card_path,
                                             "minutes": 60}]})


def main():
    s = sid("p1"); disp(s, C1); rc, err = disp(s, C2)
    gate("P1 132-1 then 132-2 refused", rc == 2 and "LabVIEW CARD BESIDE A GATE-TOOL EDIT" in err, (rc, err[:120]))
    s = sid("p2"); disp(s, C2); rc, err = disp(s, C1)
    gate("P2 132-2 then 132-1 refused", rc == 2 and "GATE-TOOL EDIT BESIDE A LabVIEW CARD" in err, (rc, err[:120]))
    s = sid("p3"); disp(s, C2); rc, err = disp(s, mk("gsp-bench", "none", ["tools/bench/**"]))
    ent = [e for e in G.load(G.SAFE_RE.sub("_", s)).get("live", []) if e.get("id") == "gsp-bench"]
    gate("P3 LabVIEW + offline tools/bench/** allowed, write recorded", rc == 0 and ent and
         ent[0].get("write") == ["tools/bench/**"], (rc, err[:120], ent))
    s = sid("p4"); rca, _ = disp(s, mk("gsp-off1", "none", ["tools/stagexec.py"]))
    rcb, err = disp(s, mk("gsp-off2", "none", ["tools/bench/x*"]))
    gate("P4 two offline cards (one writes stagexec.py) allowed", (rca, rcb) == (0, 0), (rca, rcb, err[:120]))
    s = sid("p5"); legacy(s, os.path.join(ROOT, C1), "132-1"); rc, err = disp(s, C2)
    gate("P5 legacy entry judged from its card file -> refused", rc == 2 and "card file" in err and "132-2" in err,
         (rc, err[:120]))
    s = sid("p6"); legacy(s, os.path.join(TMP, "task_gone.json"), "gsp-gone"); rc, err = disp(s, C2)
    gate("P6 legacy entry, unreadable card -> refused, names it", rc == 2 and "CANNOT READ" in err and "gsp-gone" in err,
         (rc, err[:120]))
    s = sid("p7"); legacy(s, mk("gsp-legb", "none", ["tools/bench/**"]), "gsp-legb"); rc, err = disp(s, C2)
    gate("P7 legacy entry writing only tools/bench/** -> allowed", rc == 0, (rc, err[:120]))
    s = sid("p8"); disp(s, C2); rc, err = disp(s, mk("gsp-all", "none", ["tools/**"]))
    gate("P8 offline tools/** beside LabVIEW refused", rc == 2 and "stage_prerun.py" in err, (rc, err[:120]))
    harness = {"transcript_path": os.path.join(TMP, "none.jsonl"), "cwd": ROOT, "permission_mode": "default",
               "hook_event_name": "PreToolUse", "tool_name": "Agent"}
    rc, err = hook(dict(harness, session_id=sid("p9"), tool_input=REC2))
    gate("P9 recorded payload (132-2) alone -> exit 0", rc == 0, (rc, err[:120]))
    s = sid("p10")
    rca, _ = hook(dict(harness, session_id=s, tool_input=REC1))
    rcb, err = hook(dict(harness, session_id=s, tool_input=REC2))
    gate("P10 recorded payloads 132-1 then 132-2 -> exit 0 then 2", (rca, rcb) == (0, 2), (rca, rcb, err[:100]))


if __name__ == "__main__":
    print("under test: %s" % CAND, flush=True)
    try:
        main()
    except Exception as e:  # noqa: BLE001
        import traceback
        traceback.print_exc()
        gate("main raised", False, "%s: %s" % (type(e).__name__, e))
    finally:
        for s in SIDS:
            for p in (G.state_path(G.SAFE_RE.sub("_", s)), G.state_path(G.SAFE_RE.sub("_", s)) + ".lock"):
                if os.path.isfile(p):
                    os.remove(p)
        shutil.rmtree(TMP, ignore_errors=True)
    bad = [l for l, ok in RES if not ok]
    print("SUMMARY %d/%d gates pass" % (len(RES) - len(bad), len(RES)), flush=True)
    print(P.result_line(P.make_result(len(RES) - len(bad), len(bad), bad[0] if bad else None)), flush=True)
    sys.exit(1 if bad else 0)
