r"""lint_verify_20260925b.py - card chat-L2: the SAME verification as card chat-L1's lint_verify_20260925.py (input,
md5 f09a5916...), re-run after chat-L2's fixes. Changes from the L1 file, and nothing else:
  * outputs -> lint_verify_20260925b.json and selftest_chatl2_<name>.log (L1's files are kept as the record);
  * THE LABVIEW SKIP IS A FLAG CHECK, not a name list: a self-test that DECLARES `# REQUIRES: labview` (a line of its
    own in the file) is SKIPPED when the card this run serves (CARD below) has flags.labview == "none", and RUN
    otherwise. Two files declare it: selftest_c67_ensureloaded.py (COM + scratch VIs) and selftest_make_default.py
    (drove LabVIEW for 201 s under chat-L1's labview=none card - the breach this closes for the verifier). A skip is
    reported with the flag value and the declaring line, never silently;
  * the "fake session state files removed" gate prints which files remain.
  * PREDICTION (card chat-L2 pass list): self-tests 48 run / 48 PASS + 2 documented skips; hooks all as documented
    (incl. "settings matcher reaches SendMessage"); doc_lint L2 + L6 PASS.
  Run: MATERIAL=1 py tools/bgrun.py --max-min 40 --log tools/bench/lint_verify_20260925b.log -- py -u tools/bench/lint_verify_20260925b.py

--- chat-L1 docstring, unchanged: ---
lint_verify_20260925.py - card chat-L1: LINT + VERIFY every rule device before the runner resumes.

User 2026-09-25: "지금 작업 마무리한 다음 현재까지의 규율 및 훅을 lint할 것. lint 내용 검증한 이후 러너 재개."
No LabVIEW, no GUI, no hardware, no network (TYPESAFE_API_KEY stripped, JEV_ADVISORY_OFF=1 for the hooks).

WHAT EXISTED (checked before writing): tools/bench/run_selftests_chat_b2.py runs 16 self-tests + one dry runner
cycle - its runner/tally shape is reused here for ALL tools/bench/selftest_*.py; tools/mark_legacy_dispositions.py
(given --cutoff/--note on 2026-09-25 for this card); tools/doc_lint.py; the hooks' own self-tests
(selftest_guard_session, selftest_launch_gate, selftest_guard_peer_*, selftest_motor_gate2 hook cases) - this file
adds only the LIVE pipe of the REAL registered hooks against the documented refuse/allow table.

PREDICTION CONTRACT
  P1  every selftest_*.py except selftest_c67_ensureloaded (opens LabVIEW COM: card labview=none) exits 0
  P2  every hook entry in .claude/settings.json resolves to an existing file; every hook .py compiles
  P3  each hook case below returns the rc CLAUDE.md / the hook docstring documents (state-dependent cases:
      rc in {0,2} and a refusal names its hook)
  P4  mark_legacy_dispositions --cutoff 2026-09-22: G1-G4 PASS; every archive/peer file dated >= 2026-09-22
      byte-identical before/after
  P5  doc_lint: L2 PASS (0 dangling); L6 blank count = number of undisposed reviews dated >= 2026-09-22
  P6  resume checklist: STATUS STOP line present; next.json validates; motor_session.json absent; no LabVIEW.exe
"""
import glob
import hashlib
import json
import os
import py_compile
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P  # noqa: E402

PY = sys.executable
HOOKS = os.path.join(ROOT, "tools", "hooks")
PEER = os.path.join(ROOT, "archive", "peer")
OUT_JSON = os.path.join(HERE, "lint_verify_20260925b.json")
CARD = os.path.join(HERE, "cards", "task_chat-L2.json")
CARD_LABVIEW = json.load(open(CARD, encoding="utf-8"))["flags"]["labview"]
REQUIRES_RE = re.compile(r"^#\s*REQUIRES:\s*labview\b.*$", re.M)


def skip_reason(path):
    """'' = run it. A self-test is skipped ONLY when it declares `# REQUIRES: labview` AND this run's card forbids
    LabVIEW (flags.labview == 'none'). Structural: the declaration + the card flag, never a name list."""
    try:
        m = REQUIRES_RE.search(open(path, encoding="utf-8", errors="replace").read())
    except OSError:
        return ""
    if m and CARD_LABVIEW == "none":
        return "declares %r; card %s flags.labview=%r" % (m.group(0).strip(), os.path.basename(CARD), CARD_LABVIEW)
    return ""
ENV = {k: v for k, v in os.environ.items() if k not in ("TYPESAFE_API_KEY", "BENCH_CELL", "CYCLE_SESSION",
                                                          "MATERIAL", "LV_GUARD_OFF", "PEER_GUARD_OFF",
                                                          "CYCLE_GUARD_OFF", "MATERIAL_GUARD_OFF")}
HENV = dict(ENV, JEV_ADVISORY_OFF="1")
MY_AID, MY_TYPE = "a491084675a487cb0", "material"
FAKE_SID = "lintverify_%d" % int(time.time())
PASS, FAIL = [], []
REPORT = {"selftests": [], "hooks": [], "settings": [], "legacy": {}, "doc_lint": {}, "resume": {}}


def gate(label, ok, detail=""):
    (PASS if ok else FAIL).append(label)
    print("  %s  %-60s %s" % ("PASS" if ok else "FAIL", label, str(detail)[:200]), flush=True)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


# ------------------------------------------------------------------ 1. legacy close (before doc_lint)
def legacy():
    print("\n=== 1. legacy-close undisposed reviews dated before 2026-09-22", flush=True)
    recent = {p: md5(p) for p in glob.glob(os.path.join(PEER, "*.md")) if os.path.basename(p)[:10] >= "2026-09-22"}
    r = subprocess.run([PY, os.path.join(ROOT, "tools", "mark_legacy_dispositions.py"), "--cutoff", "2026-09-22",
                        "--note", "closed as legacy 2026-09-25 by card chat-L1 (cutoff 2026-09-22; user 2026-09-25 "
                        "lint order before runner resume)"],
                       cwd=ROOT, env=ENV, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(r.stdout, flush=True)
    gl = re.findall(r"^GATE (PASS|FAIL)\s+(G\d)", r.stdout, re.M)
    marked = re.search(r"marked legacy\s*:\s*(\d+)", r.stdout)
    debt = re.findall(r"^\s+DEBT (\S+)", r.stdout, re.M)
    gate("legacy closer rc 0 and G1-G4 PASS", r.returncode == 0 and len(gl) == 4 and all(s == "PASS" for s, _ in gl),
         gl)
    changed = [os.path.basename(p) for p, h in recent.items() if md5(p) != h]
    gate("post-2026-09-22 reviews byte-identical (%d files)" % len(recent), not changed, changed[:5])
    REPORT["legacy"] = {"marked": int(marked.group(1)) if marked else None, "debt_post_0922": debt,
                        "recent_checked": len(recent), "recent_changed": changed}


# ------------------------------------------------------------------ 2. self-tests
def selftests():
    print("\n=== 2. every tools/bench/selftest_*.py", flush=True)
    head0 = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    for path in sorted(glob.glob(os.path.join(HERE, "selftest_*.py"))):
        name = os.path.splitext(os.path.basename(path))[0]
        why_skip = skip_reason(path)
        if why_skip:
            REPORT["selftests"].append({"name": name, "status": "SKIPPED", "rc": None, "why": why_skip})
            print("  SKIP  %-60s %s" % (name, why_skip), flush=True)
            continue
        t0 = time.time()
        try:
            r = subprocess.run([PY, "-u", path], cwd=ROOT, env=ENV, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=600)
            rc, out = r.returncode, (r.stdout or "") + (r.stderr or "")
        except subprocess.TimeoutExpired as e:
            rc, out = "TIMEOUT", str(e.stdout or "")[-2000:]
        with open(os.path.join(HERE, "selftest_chatl2_%s.log" % name), "w", encoding="utf-8") as f:
            f.write(out)
        tail = [ln for ln in out.strip().splitlines() if ln.strip()][-1:] or [""]
        REPORT["selftests"].append({"name": name, "status": "PASS" if rc == 0 else "FAIL", "rc": rc,
                                    "sec": round(time.time() - t0, 1), "tail": tail[0][:200]})
        gate("selftest " + name, rc == 0, "rc %s %.0fs | %s" % (rc, time.time() - t0, tail[0]))
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    gate("no self-test made a git commit", head == head0, "%s -> %s" % (head0[:8], head[:8]))


# ------------------------------------------------------------------ 3. settings resolve + compile
def settings():
    print("\n=== 3. .claude/settings.json hook entries", flush=True)
    s = json.load(open(os.path.join(ROOT, ".claude", "settings.json"), encoding="utf-8"))
    for ev, groups in s.get("hooks", {}).items():
        for g in groups:
            for h in g.get("hooks", []):
                cmd = h.get("command", "")
                m = re.search(r"\"([^\"]+\.(?:py|ps1))\"", cmd)
                p = m.group(1) if m else None
                ok = bool(p and os.path.isfile(p))
                comp = None
                if ok and p.endswith(".py"):
                    try:
                        py_compile.compile(p, doraise=True, cfile=os.path.join(tempfile.gettempdir(), "lv_l1.pyc"))
                        comp = "compiles"
                    except py_compile.PyCompileError as e:
                        comp, ok = "COMPILE ERROR %s" % e, False
                elif ok and p.endswith(".ps1"):
                    r = subprocess.run(["powershell", "-NoProfile", "-Command",
                                        "$e=$null;[void][System.Management.Automation.Language.Parser]::ParseFile("
                                        "'%s',[ref]$null,[ref]$e);$e.Count" % p.replace("'", "''")],
                                       capture_output=True, text=True, timeout=60)
                    comp = "ps parse errors=%s" % r.stdout.strip()
                    ok = ok and r.stdout.strip() == "0"
                REPORT["settings"].append({"event": ev, "matcher": g.get("matcher"), "file": p, "ok": ok,
                                           "compile": comp})
                gate("settings %s[%s] %s" % (ev, g.get("matcher") or "*", os.path.basename(p or "?")), ok, comp)
    for f in sorted(glob.glob(os.path.join(HOOKS, "*.py"))):
        try:
            py_compile.compile(f, doraise=True, cfile=os.path.join(tempfile.gettempdir(), "lv_l1.pyc"))
            gate("compile " + os.path.basename(f), True)
        except py_compile.PyCompileError as e:
            gate("compile " + os.path.basename(f), False, e)
    return s


# ------------------------------------------------------------------ 4. hooks, live, piped payloads
def hook(name, payload, env=None, timeout=200):
    t0 = time.time()
    r = subprocess.run([PY, os.path.join(HOOKS, name)], input=json.dumps(payload), cwd=ROOT, env=env or HENV,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    return r.returncode, (r.stderr or "").strip(), (r.stdout or "").strip(), round(time.time() - t0, 1)


def bash(cmd, bg=False, timeout_ms=None, sid=FAKE_SID, **extra):
    ti = {"command": cmd}
    if bg:
        ti["run_in_background"] = True
    if timeout_ms is not None:
        ti["timeout"] = timeout_ms
    d = {"tool_name": "Bash", "tool_input": ti, "session_id": sid, "hook_event_name": "PreToolUse"}
    d.update(extra)
    return d


def case(hookname, label, payload, expect, doc, env=None):
    """expect: 0 / 2 exact, or 'state' (rc in {0,2}; a refusal must name the hook)."""
    rc, err, out, sec = hook(hookname, payload, env)
    first = (err.splitlines() or out.splitlines() or [""])[0]
    if expect == "state":
        ok = rc in (0, 2) and (rc == 0 or "BLOCKED by tools/hooks/" + hookname in err)
    else:
        ok = rc == expect
    REPORT["hooks"].append({"hook": hookname, "case": label, "expect": expect, "rc": rc, "sec": sec,
                            "first_line": first[:300], "doc": doc})
    gate("%s | %s" % (hookname, label), ok, "rc=%s expect=%s %.1fs | %s" % (rc, expect, sec, first))
    return rc, err, out


BG = "py tools/bgrun.py --material --max-min 5 --log tools/bench/x_l1.log -- py -u "


def hooks(settings_obj):
    print("\n=== 4. hooks live (JEV_ADVISORY_OFF=1, TYPESAFE_API_KEY stripped, fake session %s)" % FAKE_SID,
          flush=True)
    B = "guard_bash.py"
    case(B, "read-only cat", bash("cat STATUS.md"), 0, "Everything else passes")
    case(B, "bench script, no marker", bash("py tools/bench/selftest_protocol.py", bg=True), 2,
         "CLAUDE.md s3: judgement never runs tools/bench/*.py (material marker)")
    case(B, "bgrun --material bench, background", bash(BG + "tools/bench/selftest_protocol.py", bg=True), 0,
         "--material form, bgrun with --max-min")
    case(B, "MATERIAL=1 env form, background",
         bash("MATERIAL=1 py tools/bgrun.py --max-min 5 --log tools/bench/x.log -- py -u "
              "tools/bench/selftest_protocol.py", bg=True), 0, "env form still accepted by the guard")
    case(B, "bgrun --material bench, foreground 600 s", bash(BG + "tools/bench/selftest_protocol.py",
                                                             timeout_ms=600000), 2,
         "CLAUDE.md Tooling: LabVIEW-touching foreground needs timeout <= 30 s")
    case(B, "tools script background WITHOUT bgrun",
         bash("py -u tools/gscript_probe_l1.py", bg=True), 2,
         "backgrounded LabVIEW command must run through bgrun --max-min")
    case(B, "motor: sender by hand", bash('powershell -File tools/motor_send_pi.ps1 -Command "MOV 1 5"'), 2,
         "rule 1b: motors only through tools/motor_gate.py")
    case(B, "motor: inline serial", bash('py -c "import serial; serial.Serial(\'COM3\')"'), 2,
         "inline raw serial refused")
    case(B, "motor: raw MOV one-liner", bash("echo MOV 1 5 > COM3"), 2, "raw controller motion refused")
    case(B, "motor: gateway dry-run", bash('py tools/motor_gate.py --device pi --command "MOV 1 5" --dry-run',
                                           timeout_ms=20000), 0, "the sanctioned gateway passes")
    case(B, "motor: grep of a blocked name", bash("grep -n SerialPort tools/motor_send_pi.ps1"), 0,
         "reading about it is not running it")
    stage = sorted(glob.glob(os.path.join(ROOT, "tools", "recipes", "stage_*.py")))
    stage_rel = os.path.relpath(stage[0], ROOT).replace("\\", "/") if stage else "tools/recipes/stage_none.py"
    case(B, "launch gate: stage script %s" % os.path.basename(stage_rel), bash(BG + stage_rel, bg=True), "state",
         "CLAUDE.md s3 FIFTH RULE: stage launched only with dry-run + pre-run PASS for its current sha")
    case(B, "launch gate: non-stage recipe (stop_record)", bash(BG + "tools/recipes/build_d1_v0.py", bg=True),
         "state", "FOURTH RULE: a recipe stopped by a prior-art verdict may not launch")
    # retrospective / NEXT gate
    snap = open(os.path.join(ROOT, "tools", "bench", "next_snapshot.md5"), encoding="utf-8").read().strip() \
        if os.path.exists(os.path.join(ROOT, "tools", "bench", "next_snapshot.md5")) else ""
    cur = md5(os.path.join(ROOT, "tools", "bench", "next.json")) if os.path.exists(
        os.path.join(ROOT, "tools", "bench", "next.json")) else "absent"
    exp_retro = 2 if (snap and (cur == "absent" or cur == snap)) else "state"
    case(B, "retro: next.json == snapshot (%s)" % ("same" if cur == snap else "differs"),
         bash("py tools/retrospective.py --cycle 999", bg=True), exp_retro,
         "C7: retrospective refused while next.json unchanged from the runner snapshot")
    sp = os.path.join(ROOT, "tools", "bench", "session_%s.json" % FAKE_SID)
    gate("retro refused => session NOT marked retro_done", not (os.path.exists(sp) and
                                                               json.load(open(sp)).get("retro_done")),
         os.path.exists(sp))
    sid2 = FAKE_SID + "_dry"
    case(B, "retro --dry-run (LV_GUARD path)", bash("py tools/retrospective.py --cycle 999 --dry-run", bg=True,
                                                    sid=sid2), exp_retro, "same NEXT gate applies")
    # card flags through guard_bash
    case(B, "card: bound material, gui click", bash("& .\\tools\\lv_gui.ps1 -Action click -X 1 -Y 1",
                                                    agent_id=MY_AID, agent_type=MY_TYPE), 2,
         "session protocol v1: flags.gui false")
    case(B, "card: bound material, git status", bash("git status --short", agent_id=MY_AID, agent_type=MY_TYPE), 0,
         "read-only command inside the card")
    case(B, "card: unbound material agent", bash("ls", agent_id="ffff0000l1unbound", agent_type="material"), 2,
         "binding rule: first command must be protocol.py bind")

    C = "guard_card.py"

    def wp(path, aid=MY_AID, atype=MY_TYPE, tool="Write"):
        return {"tool_name": tool, "tool_input": {"file_path": os.path.join(ROOT, path), "content": "x"},
                "agent_id": aid, "agent_type": atype, "session_id": FAKE_SID}
    case(C, "bound: Write STATUS.md", wp("STATUS.md"), 2, "flags.status_edit false")
    case(C, "bound: Write tools/x", wp("tools/bench/x_l1_probe.txt"), 0, "write glob tools/**")
    case(C, "bound: Write CLAUDE.md (outside globs)", wp("CLAUDE.md"), 2, "write globs tools/** archive/peer/** docs/**")
    case(C, "bound: Edit a .vi under tools", wp("tools/x.vi", tool="Edit"), "state", "(.vi also denied by settings)")
    case(C, "unbound material: Read", {"tool_name": "Read", "tool_input": {"file_path": "STATUS.md"},
                                        "agent_id": "ffff0000l1unbound", "agent_type": "material"}, 2,
         "unbound card agent refused everything except bind")
    case(C, "Explore agent (no card type): Read", {"tool_name": "Read", "tool_input": {"file_path": "STATUS.md"},
                                                   "agent_id": "ffff0000l1explore", "agent_type": "Explore"}, 0,
         "agent types that take no card are never affected")
    case(C, "main session Write STATUS.md", {"tool_name": "Write", "tool_input": {"file_path": "STATUS.md"}}, 0,
         "main session (no agent_id) never affected")

    S = "guard_session.py"
    sid3 = FAKE_SID + "_sess"

    def ag(sub, sid=sid3):
        return {"tool_name": "Agent", "tool_input": {"subagent_type": sub, "prompt": "x"}, "session_id": sid}
    case(S, "Explore not counted", ag("Explore"), 0, "only material/log-reader counted")
    for i in range(1, 9):
        rc, _, _, _ = hook(S, ag("material" if i % 2 else "log-reader"))
        if rc != 0:
            break
    gate("guard_session.py | dispatches 1..8 allowed", rc == 0, "stopped at %d rc=%s" % (i, rc))
    case(S, "9th material dispatch refused", ag("material"), 2, "MAX_DISPATCHES = 8")
    sid4 = FAKE_SID + "_retro"
    json.dump({"dispatches": 1, "retro_done": True},
              open(os.path.join(ROOT, "tools", "bench", "session_%s.json" % sid4), "w"))
    case(S, "after retrospective: material refused", ag("material", sid4), 2, "cycle closed by its retrospective")
    sm = {"tool_name": "SendMessage", "tool_input": {"to": "agent123", "message": "x"}, "session_id": sid3}
    case(S, "SendMessage in CYCLE_SESSION (direct pipe)", sm, 2, "(c) no SendMessage resume",
         env=dict(HENV, CYCLE_SESSION="1"))
    case(S, "SendMessage to main in CYCLE_SESSION", dict(sm, tool_input={"to": "main", "message": "x"}), 0,
         "(c) exception: to main", env=dict(HENV, CYCLE_SESSION="1"))
    matchers = [g.get("matcher") or "" for g in settings_obj["hooks"].get("PreToolUse", [])
                for h in g.get("hooks", []) if "guard_session.py" in h.get("command", "")]
    reach = any(re.fullmatch(m, "SendMessage") for m in matchers if m)
    REPORT["hooks"].append({"hook": S, "case": "settings matcher reaches SendMessage", "expect": True, "rc": reach,
                            "first_line": "matchers=%s" % matchers, "doc": "guard_session (c) is registered for it"})
    gate("guard_session.py | settings matcher reaches SendMessage (rule (c) live)", reach, matchers)

    R = "report_gate.py"
    tb = tempfile.mkdtemp(prefix="l1rg_")
    try:
        with open(os.path.join(tb, "cycle_runner_main_20990101.log"), "w", encoding="utf-8") as f:
            f.write("CYCLE 5 | rc=0 | fake\nnoise\n")
        renv = dict(HENV, REPORT_GATE_BENCH=tb)
        stop = {"hook_event_name": "Stop", "stop_hook_active": False}
        case(R, "Stop, unacked event", stop, 2, "turn may not end until reported", env=renv)
        case(R, "Stop, stop_hook_active", dict(stop, stop_hook_active=True), 0, "no loop", env=renv)
        case(R, "Stop, CYCLE_SESSION exempt", stop, 0, "runner cells exempt", env=dict(renv, CYCLE_SESSION="1"))
        rc, err, out = case(R, "UserPromptSubmit prints context", {"hook_event_name": "UserPromptSubmit"}, 0,
                            "stdout is context", env=renv)
        gate("report_gate.py | UserPromptSubmit stdout names the event", "UNREPORTED" in out, out[:120])
        subprocess.run([PY, os.path.join(HOOKS, R), "--ack"], env=renv, capture_output=True, text=True)
        case(R, "Stop after --ack", stop, 0, "acked events do not block", env=renv)
    finally:
        shutil.rmtree(tb, ignore_errors=True)
    r = subprocess.run([PY, os.path.join(HOOKS, R), "--status"], cwd=ROOT, env=HENV, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    REPORT["report_gate_live_status"] = r.stdout[:1500]
    print("  live report_gate --status: " + r.stdout.splitlines()[0] if r.stdout else "", flush=True)

    Pp = "guard_peer.py"
    case(Pp, "read-only cat", bash("cat tools/bench/x.log"), 0, "reading logs never blocked")
    case(Pp, "cycle_runner under bgrun", bash("py tools/bgrun.py --max-min 700 --log tools/bench/x.log -- py "
                                              "tools/cycle_runner.py", bg=True), 0, "the runner is not a build")
    case(Pp, "jev script under bgrun", bash(BG + "tools/bench/jev_ladder_selftest_l1.py", bg=True), 0,
         "Jev scripts exempt (user 2026-09-22)")
    case(Pp, "recipe build under bgrun", bash(BG + "tools/recipes/build_d1_v0.py", bg=True), "state",
         "a failed prediction blocks the next build until reviewed")
    case(Pp, "PEER_GUARD_OFF=1", bash(BG + "tools/recipes/build_d1_v0.py", bg=True), 0, "escape for bench cells",
         env=dict(HENV, PEER_GUARD_OFF="1"))

    Cy = "guard_cycle.py"
    case(Cy, "read-only cat", bash("cat STATUS.md"), 0, "diagnostics stay open")
    case(Cy, "bench diagnostic", bash(BG + "tools/bench/selftest_protocol.py", bg=True), 0,
         "bench scripts are not builds")
    case(Cy, "retrospective itself", bash("py tools/retrospective.py --cycle 999", bg=True), 0,
         "the remedy is never blocked")
    case(Cy, "recipe build", bash(BG + "tools/recipes/build_d1_v0.py", bg=True), "state",
         "blocked while previous cycle lacks a retrospective / slug at threshold / prior-art")
    case(Cy, "CYCLE_GUARD_OFF=1", bash(BG + "tools/recipes/build_d1_v0.py", bg=True), 0, "bench-cell escape",
         env=dict(HENV, CYCLE_GUARD_OFF="1"))

    for s in (FAKE_SID, sid2, sid3, sid4):
        try:
            os.remove(os.path.join(ROOT, "tools", "bench", "session_%s.json" % s))
        except OSError:
            pass
    try:
        os.remove(os.path.join(ROOT, "tools", "bench", "x_l1_probe.txt"))
    except OSError:
        pass
    left = glob.glob(os.path.join(ROOT, "tools", "bench", "session_lintverify_*.json"))
    gate("fake session state files removed", not left, [os.path.basename(p) for p in left])


# ------------------------------------------------------------------ 5. doc_lint
def doclint():
    print("\n=== 5. doc_lint", flush=True)
    r = subprocess.run([PY, os.path.join(ROOT, "tools", "doc_lint.py")], cwd=ROOT, env=ENV, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=300)
    print(r.stdout[-4000:], flush=True)
    rows = {m.group(2): (m.group(1), m.group(3)) for m in
            re.finditer(r"^\s+(PASS|FAIL|WARN)\s+(L\d+[a-z]?)\s+(.*)$", r.stdout, re.M)}
    REPORT["doc_lint"] = {k: {"verdict": v[0], "text": v[1][:400]} for k, v in rows.items()}
    l2 = rows.get("L2", ("?", ""))
    gate("doc_lint L2 0 dangling", l2[0] == "PASS", l2[1][:150])
    l6 = rows.get("L6", ("?", ""))
    m = re.search(r"(\d+) still blank", l6[1])
    blank = int(m.group(1)) if m else 0
    debt = len(REPORT["legacy"].get("debt_post_0922") or [])
    gate("doc_lint L6 blank == post-09-22 debt only (%d)" % debt, blank == debt, l6[1][:200])
    gate("doc_lint L6 0 blank (card wording)", l6[0] == "PASS", l6[1][:200])


# ------------------------------------------------------------------ 6. resume checklist
def resume():
    print("\n=== 6. resume checklist", flush=True)
    st = open(os.path.join(ROOT, "STATUS.md"), encoding="utf-8").read()
    stop = [ln for ln in st.splitlines() if re.match(r"^\s*STOP\b", ln)]
    gate("STATUS STOP line present (left in place)", bool(stop), stop[:1])
    nj = os.path.join(ROOT, "tools", "bench", "next.json")
    try:
        ok, why = P.validate_obj(json.load(open(nj, encoding="utf-8")))
        sr = json.load(open(nj, encoding="utf-8")).get("stop_requested")
    except Exception as e:  # noqa: BLE001
        ok, why, sr = False, str(e), None
    gate("next.json validates", ok, why)
    REPORT["resume"] = {"stop_line": stop[:1], "next_valid": ok, "next_why": why, "stop_requested": sr}
    ms = os.path.exists(os.path.join(ROOT, "tools", "bench", "motor_session.json"))
    gate("motor_session.json absent", not ms)
    tl = subprocess.run(["tasklist"], capture_output=True, text=True, errors="replace").stdout
    lv = "labview.exe" in tl.lower()
    gate("no LabVIEW.exe running", not lv)
    REPORT["resume"].update({"motor_session": ms, "labview_running": lv})


def main():
    t0 = time.time()
    legacy()
    s = settings()
    hooks(s)
    doclint()
    resume()
    selftests()
    REPORT["gates"] = {"pass": len(PASS), "fail": len(FAIL), "failing": FAIL}
    REPORT["minutes"] = round((time.time() - t0) / 60, 1)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(REPORT, f, indent=1, ensure_ascii=False)
    print("\n=== GATES: %d pass / %d fail%s" % (len(PASS), len(FAIL),
                                                ("; failing: " + " || ".join(FAIL)) if FAIL else ""), flush=True)
    print(P.result_line(P.make_result(len(PASS), len(FAIL), FAIL[0] if FAIL else None,
                                      artefacts=[{"path": os.path.relpath(OUT_JSON, ROOT).replace("\\", "/"),
                                                  "md5": md5(OUT_JSON)}])), flush=True)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
