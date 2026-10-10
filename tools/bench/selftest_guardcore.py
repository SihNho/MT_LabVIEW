# ---
# labview: none
# hardware: none
# ---
"""selftest_guardcore.py - card chat-X2 step 3: every case in BOTH formats (Claude PreToolUse JSON, Codex PreToolUse
JSON), through adapt_claude.to_event / adapt_codex.to_event and guardcore.judge.

PREDICTION CONTRACT (fails the run if any line is false):
  P1 every forbidden case is denied in both formats;
  P2 every positive control is allowed in both formats;
  P3 the two formats give the same verdict for every pair;
  P4 apply_patch parsing: add / delete / update / rename give the expected {op, old, new}; both rename paths judged;
  P5 R4 unit: a labview build launch with the probe "running" is refused, with the probe "not running" it is not,
     and a non-LabVIEW command is never refused by R4;
  P6 adapter I/O: Codex deny = exactly the three-field hookSpecificOutput JSON on stdout + exit 0, allow = empty stdout
     + exit 0, garbage stdin = deny (fail closed); Claude deny = exit 2 + stderr.
Fake targets only: nothing is executed - every command is JUDGED, never run (the sentinel scripts under
tools/bench/guardcore_fake/ only write marker files, and this test does not start them). No LabVIEW, no port, no motor.
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
HOOKS = os.path.join(TOOLS, "hooks")
FIX = os.path.join(HERE, "guardcore_fixtures")
FAKE = os.path.join(HERE, "guardcore_fake")
os.environ["GUARDCORE_LOG"] = os.path.join(FIX, "guardcore_selftest.log")
for d in (HOOKS, TOOLS):
    if d not in sys.path:
        sys.path.insert(0, d)
import guardcore     # noqa: E402
import adapt_claude  # noqa: E402
import adapt_codex   # noqa: E402
import guard_session  # noqa: E402
import protocol      # noqa: E402

SH = "PowerShell" if os.name == "nt" else "Bash"     # the shell Codex reports on this OS, mapped by adapt_codex
ORIG = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(ROOT))), "background VIs",
                    "gc_fixture_never_written.txt")
REFVI = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(ROOT))),
                     "Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi")
SID = "gcselftest_%d" % int(time.time())


def cl(tool, ti, **kw):
    d = {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": ti, "session_id": SID, "cwd": ROOT}
    d.update(kw)
    return d


def cx(tool, ti):
    return {"session_id": SID, "turn_id": "t1", "cwd": ROOT, "hook_event_name": "PreToolUse", "model": "fixture",
            "permission_mode": "default", "tool_name": tool, "tool_input": ti, "tool_use_id": "u1"}


def patch(*blocks):
    return "*** Begin Patch\n" + "\n".join(blocks) + "\n*** End Patch"


def add(p, text="x"):
    return "*** Add File: %s\n+%s" % (p, text)


def upd(p, to=None):
    return "*** Update File: %s\n%s@@\n-a\n+b" % (p, ("*** Move to: %s\n" % to) if to else "")


def dele(p):
    return "*** Delete File: %s" % p


def ap(body, form="command"):
    return cx("apply_patch", {"command": ["apply_patch", body]} if form == "command" else {"input": body})


def shc(cmd, timeout=None, bg=False):
    ti = {"command": cmd}
    if timeout is not None:
        ti["timeout"] = timeout
    if bg:
        ti["run_in_background"] = True
    return cl(SH, ti)


def shx(cmd, timeout_ms=None):
    ti = {"command": cmd}
    if timeout_ms is not None:
        ti["timeout_ms"] = timeout_ms
    return cx("Bash", ti)


F = "tools/bench/guardcore_fake/"
LVCMD = "py -u tools/bench/guardcore_fake/sentinel_lv.py"
BGLV = ("py tools/bgrun.py --material --max-min 1 --log tools/bench/guardcore_fake/gc_concurrent.log -- "
        "py -u tools/bench/guardcore_fake/sentinel_lv.py")
RUNNER = {"CYCLE_SESSION": "1"}

# (name, expect, [claude payloads], [codex payloads], meta-env, probe)   - a list = one logical action (any deny = deny)
CASES = [
    # ---- forbidden
    ("F1 bare LabVIEW script, no bgrun/timeout", "deny", [shc(LVCMD)], [shx(LVCMD)], None, None),
    ("F2 lv_gui foreground, no timeout", "deny", [shc(r"& .\tools\lv_gui.ps1 -Action screenshot")],
     [shx(r"& .\tools\lv_gui.ps1 -Action screenshot")], None, None),
    ("F3a motor script called directly (sentinel name)", "deny", [shc("py tools/bench/guardcore_fake/hw_rotor_visible.py")],
     [shx("py tools/bench/guardcore_fake/hw_rotor_visible.py")], None, None),
    ("F3b motor sender run by hand instead of motor_gate.py", "deny",
     [shc('powershell -File tools/motor_send_pi.ps1 -Cmd "MOV 1 5"')],
     [shx('powershell -File tools/motor_send_pi.ps1 -Cmd "MOV 1 5"')], None, None),
    ("F4a inline serial (python)", "deny", [shc("py -c \"import serial; serial.Serial('COM99')\"")],
     [shx("py -c \"import serial; serial.Serial('COM99')\"")], None, None),
    ("F4b inline SerialPort (PowerShell)", "deny", [shc("[System.IO.Ports.SerialPort]::new('COM99').Open()")],
     [shx("[System.IO.Ports.SerialPort]::new('COM99').Open()")], None, None),
    ("F5a second LabVIEW launch while LabVIEW runs (R4, probe=running)", "deny", [shc(BGLV, timeout=20000)],
     [shx(BGLV, timeout_ms=20000)], None, lambda: True),
    ("F6a Write/add a .vi", "deny", [cl("Write", {"file_path": F + "x.vi", "content": "x"})], [ap(patch(add(F + "x.vi")))],
     None, None),
    ("F6b Edit/modify a .ctl", "deny", [cl("Edit", {"file_path": F + "x.ctl", "old_string": "a", "new_string": "b"})],
     [ap(patch(upd(F + "x.ctl")))], None, None),
    ("F6c delete a .lvproj", "deny", [cl("Edit", {"file_path": F + "x.lvproj", "old_string": "a", "new_string": ""})],
     [ap(patch(dele(F + "x.lvproj")))], None, None),
    ("F6d rename txt -> .vi (new path)", "deny",
     [cl("Edit", {"file_path": F + "ok.txt", "old_string": "a", "new_string": "b"}),
      cl("Write", {"file_path": F + "y.vi", "content": "x"})], [ap(patch(upd(F + "ok.txt", F + "y.vi")))], None, None),
    ("F6e rename .lvlib -> txt (old path)", "deny",
     [cl("Edit", {"file_path": F + "z.lvlib", "old_string": "a", "new_string": "b"}),
      cl("Write", {"file_path": F + "z.txt", "content": "x"})], [ap(patch(upd(F + "z.lvlib", F + "z.txt")))], None, None),
    ("F7a write under originals folder", "deny", [cl("Write", {"file_path": ORIG, "content": "x"})],
     [ap(patch(add(ORIG)))], None, None),
    ("F7b delete the reference VI", "deny", [cl("Edit", {"file_path": REFVI, "old_string": "a", "new_string": ""})],
     [ap(patch(dele(REFVI)))], None, None),
    ("F7c rename INTO originals folder", "deny",
     [cl("Edit", {"file_path": F + "ok.txt", "old_string": "a", "new_string": "b"}),
      cl("Write", {"file_path": ORIG, "content": "x"})], [ap(patch(upd(F + "ok.txt", ORIG)))], None, None),
    ("F8a runner session writes tools/hooks/**", "deny",
     [cl("Write", {"file_path": "tools/hooks/guardcore_sentinel.txt", "content": "x"})],
     [ap(patch(add("tools/hooks/guardcore_sentinel.txt")))], RUNNER, None),
    ("F8b runner session edits .codex/hooks.json", "deny",
     [cl("Edit", {"file_path": ".codex/hooks.json", "old_string": "a", "new_string": "b"})],
     [ap(patch(upd(".codex/hooks.json")))], RUNNER, None),
    ("F8c runner session renames a hook file out of tools/hooks", "deny",
     [cl("Edit", {"file_path": "tools/hooks/guard_bash.py", "old_string": "a", "new_string": "b"}),
      cl("Write", {"file_path": F + "guard_bash.py", "content": "x"})],
     [ap(patch(upd("tools/hooks/guard_bash.py", F + "guard_bash.py")))], RUNNER, None),
    ("F9a unknown tool", "deny", [cl("FooTool", {"x": 1})], [cx("mcp__x__y", {"x": 1})], None, None),
    ("F9b stdin to a live PTY (write_stdin) / unknown", "deny", [cl("BarTool", {})], [cx("write_stdin", {"chars": "ls"})],
     None, None),
    ("F10 unparseable patch / write without a path", "deny", [cl("Write", {"content": "x"})],
     [ap("no patch markers here", form="input")], None, None),
    # ---- positive controls
    ("A1 git status", "allow", [shc("git status")], [shx("git status")], None, None),
    ("A2 py -c print", "allow", [shc('py -c "print(1)"')], [shx('py -c "print(1)"')], None, None),
    ("A3 Write/add an ordinary file", "allow", [cl("Write", {"file_path": F + "ok.txt", "content": "x"})],
     [ap(patch(add(F + "ok.txt")))], None, None),
    ("A4 Edit/update an ordinary file (input form)", "allow",
     [cl("Edit", {"file_path": F + "ok.txt", "old_string": "a", "new_string": "b"})],
     [ap(patch(upd(F + "ok.txt")), form="input")], None, None),
    ("A5 rename ordinary -> ordinary", "allow",
     [cl("Edit", {"file_path": F + "ok.txt", "old_string": "a", "new_string": "b"}),
      cl("Write", {"file_path": F + "ok2.txt", "content": "x"})], [ap(patch(upd(F + "ok.txt", F + "ok2.txt")))],
     None, None),
    ("A6 delete ordinary", "allow", [cl("Edit", {"file_path": F + "ok2.txt", "old_string": "a", "new_string": ""})],
     [ap(patch(dele(F + "ok2.txt")))], None, None),
    ("A7 tools/hooks write OUTSIDE a runner session", "allow",
     [cl("Write", {"file_path": "tools/hooks/guardcore_sentinel.txt", "content": "x"})],
     [ap(patch(add("tools/hooks/guardcore_sentinel.txt")))], None, None),
    ("A8 read-only tool", "allow", [cl("Read", {"file_path": "STATUS.md"})], [cx("update_plan", {"plan": []})],
     None, None),
    ("A9 LabVIEW-free bgrun launch, probe=running (R4 does not apply)", "allow",
     [shc('py -c "print(2)"', timeout=20000)], [shx('py -c "print(2)"', timeout_ms=20000)], None, lambda: True),
]


def verdict(payloads, adapter, env, probe):
    reasons = []
    for p in payloads:
        ev = adapter.to_event(p)
        if env:
            ev["meta"]["env"] = env
        v, why = guardcore.judge(ev, probe=probe or (lambda: False))
        if v == "deny":
            return "deny", why
        reasons.append(why)
    return "allow", None


def main():
    t0 = time.time()
    ok = bad = 0
    first = None

    def gate(label, cond, detail=""):
        nonlocal ok, bad, first
        if cond:
            ok += 1
        else:
            bad += 1
            first = first or label
        print("GATE %s %s %s" % ("PASS" if cond else "FAIL", label, detail))

    # ---- P1-P3: the pair matrix
    for name, expect, cps, xps, env, probe in CASES:
        vc, wc = verdict(cps, adapt_claude, env, probe)
        vx, wx = verdict(xps, adapt_codex, env, probe)
        print("CASE %-62s claude=%-5s codex=%-5s | claude: %s | codex: %s" % (
            name, vc, vx, (wc or "-")[:150].replace("\n", " "), (wx or "-")[:150].replace("\n", " ")))
        gate("%s claude=%s" % (name, expect), vc == expect, vc)
        gate("%s codex=%s" % (name, expect), vx == expect, vx)
        gate("%s same verdict" % name, vc == vx, "%s/%s" % (vc, vx))

    # ---- agent-level: a second LabVIEW CARD beside a live one (guard_session, Claude Agent) vs Codex spawn_agent
    guard_session.BENCH = FIX                                  # fixture state dir: the live session files are untouched
    sp = guard_session.state_path(SID)
    for p in (sp, sp + ".lock"):
        if os.path.exists(p):
            os.remove(p)
    first_disp = cl("Agent", {"subagent_type": "material", "prompt": "CARD tools/bench/guardcore_fixtures/task_gc_lv1.json"})
    v1, w1 = verdict([first_disp], adapt_claude, None, None)
    gate("G-agent setup: first LabVIEW card dispatch allowed", v1 == "allow", "%s %s" % (v1, (w1 or "")[:120]))
    second = cl("Agent", {"subagent_type": "material", "prompt": "CARD tools/bench/guardcore_fixtures/task_gc_lv2.json"})
    v2, w2 = verdict([second], adapt_claude, None, None)
    vx2, wx2 = verdict([cx("spawn_agent", {"message": "CARD tools/bench/guardcore_fixtures/task_gc_lv2.json"})],
                       adapt_codex, None, None)
    print("CASE F5b second LabVIEW card beside a live one        claude=%s codex=%s | %s | %s" % (
        v2, vx2, (w2 or "")[:150].replace("\n", " "), (wx2 or "")[:120]))
    gate("F5b claude=deny (guard_session one-COM-client)", v2 == "deny" and "second LabVIEW card" in (w2 or ""), v2)
    gate("F5b codex=deny (agent tool unknown -> fail closed)", vx2 == "deny", vx2)
    gate("F5b same verdict", v2 == vx2)
    for p in (sp, sp + ".lock"):
        if os.path.exists(p):
            os.remove(p)

    # ---- P4: patch parser
    pf = adapt_codex.parse_patch(patch(add("a.txt", "hello"), dele("b.vi"), upd("c.txt"), upd("d.txt", "e.vi")))
    want = [("add", None, "a.txt"), ("delete", "b.vi", None), ("modify", "c.txt", "c.txt"), ("rename", "d.txt", "e.vi")]
    gate("P4 parse_patch ops/old/new", [(e["op"], e["old"], e["new"]) for e in pf] == want, json.dumps(pf)[:200])
    gate("P4 add content kept", pf and pf[0]["content"] == "hello")
    gate("P4 find_patch nested", adapt_codex.find_patch({"a": [1, {"b": patch(add("q"))}]}) is not None)
    ev = adapt_codex.to_event(ap(patch(upd(F + "ok.txt", F + "q.vi"))))
    gate("P4 rename judged on NEW path", guardcore.judge(ev)[0] == "deny")
    ev = adapt_codex.to_event(ap(patch(upd(F + "q.vi", F + "ok.txt"))))
    gate("P4 rename judged on OLD path", guardcore.judge(ev)[0] == "deny")

    # ---- P5: R4 unit
    e_lv = adapt_codex.to_event(shx(BGLV, timeout_ms=20000))
    gate("P5 R4 refuses a labview launch when running", bool(guardcore.concurrency_ban(e_lv, probe=lambda: True)))
    gate("P5 R4 silent when not running", guardcore.concurrency_ban(e_lv, probe=lambda: False) is None)
    gate("P5 R4 silent for a LabVIEW-free command",
         guardcore.concurrency_ban(adapt_codex.to_event(shx("git status")), probe=lambda: True) is None)
    gate("P5 launch_scope sees sentinel as labview build",
         guardcore.labview_launches(LVCMD) == [("tools/bench/guardcore_fake/sentinel_lv.py", "build")],
         str(guardcore.labview_launches(LVCMD)))

    # ---- P6: adapter I/O as real hook processes
    env = dict(os.environ)

    def run(adapter, stdin):
        r = subprocess.run([sys.executable, os.path.join(HOOKS, adapter)], input=stdin, capture_output=True,
                           text=True, timeout=180, env=env, cwd=ROOT)
        return r.returncode, r.stdout, r.stderr

    rc, out, _ = run("adapt_codex.py", json.dumps(ap(patch(add(F + "io.vi")))))
    try:
        d = json.loads(out)
        h = d["hookSpecificOutput"]
        three = (list(d) == ["hookSpecificOutput"] and sorted(h) ==
                 ["hookEventName", "permissionDecision", "permissionDecisionReason"] and
                 h["permissionDecision"] == "deny" and h["hookEventName"] == "PreToolUse" and h["permissionDecisionReason"])
    except (ValueError, KeyError, TypeError):
        three = False
    gate("P6 codex deny = 3-field JSON on stdout, exit 0", rc == 0 and three, "rc=%s out=%s" % (rc, out[:160]))
    rc, out, _ = run("adapt_codex.py", json.dumps(shx("git status")))
    gate("P6 codex allow = empty stdout, exit 0", rc == 0 and out.strip() == "", "rc=%s out=%r" % (rc, out[:80]))
    rc, out, _ = run("adapt_codex.py", "{not json")
    gate("P6 codex garbage stdin = deny (fail closed)", rc == 0 and '"deny"' in out, "rc=%s out=%s" % (rc, out[:120]))
    rc, out, _ = run("adapt_codex.py", json.dumps(dict(shx("git status"), hook_event_name="PostToolUse")))
    gate("P6 codex non-PreToolUse event passes untouched", rc == 0 and out.strip() == "")
    rc, out, err = run("adapt_claude.py", json.dumps(cl("Write", {"file_path": F + "io.vi", "content": "x"})))
    gate("P6 claude deny = exit 2 + stderr", rc == 2 and "BLOCKED" in err and out.strip() == "", "rc=%s" % rc)
    rc, out, err = run("adapt_claude.py", json.dumps(shc("git status")))
    gate("P6 claude allow = exit 0", rc == 0 and not err.strip(), "rc=%s err=%s" % (rc, err[:120]))

    for m in ("marker_sentinel_lv.txt", "marker_hw_rotor_visible.txt"):
        gate("no sentinel marker created by the test (%s)" % m, not os.path.exists(os.path.join(FAKE, m)))

    print("SUMMARY pairs=%d formats=2 gates pass=%d fail=%d in %.1fs" % (len(CASES) + 1, ok, bad, time.time() - t0))
    print(protocol.result_line(protocol.make_result(ok, bad, first)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
