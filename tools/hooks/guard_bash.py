"""PreToolUse hook (Bash | PowerShell): no long FOREGROUND command that touches LabVIEW.

Why (user, 2026-09-04): a 120 s foreground chain (COM + GUI + diagnostics) tied up the session while
the user was talking to it, and left a modal dialog open that blocked COM. CLAUDE.md rule 2b says
"background anything slow; short checkable steps" — this hook makes the rule mechanical.

Rule: a command that invokes LabVIEW tooling (lv_gui.ps1, gscript, tools/bench/*, peer.ps1) must either
run with run_in_background=true or declare a timeout of at most MAX_FG_MS. Everything else passes.
Exit code 2 = block (stderr goes back to Claude); 0 = allow.

SECOND RULE, added 2026-09-16: A JUDGEMENT SESSION MAY NOT RUN RECIPES OR BENCH SCRIPTS ITSELF.
CLAUDE.md section 3 says the hand-off is mechanical: "A judgement session spawns these via the Agent tool
and never runs `tools/recipes/*.py` or `tools/bench/*.py` itself". A hook cannot see which model is
calling, so the material session DECLARES itself with an explicit marker on the command line
(`MATERIAL=1 py tools/bgrun.py ...`, or `$env:MATERIAL='1'; py ...` in PowerShell). No marker => refused,
with a pointer to the `material` agent. The user asked for this before a second violation, not after.
"""
import json
import os
import re
import sys
import time

MAX_FG_MS = 30_000

HERE = os.path.dirname(os.path.abspath(__file__))
MARKER_LOG = os.path.join(HERE, "material_marker.log")

# THE RETROSPECTIVE CLOSES THE SESSION'S CYCLE (2026-09-17, CLAUDE.md section 3 item 2 "ENFORCED BY A RUNNER").
# `guard_session.py` refuses material dispatches once the cycle is closed, but it only ever sees Agent calls - the
# retrospective is a Bash/PowerShell command, so THIS hook is the only place that can observe it. It records the
# fact and always allows the command (the remedy is never blocked by the gate that demands it).
# Command position, like MATERIAL_RE: `grep retrospective.py ...` is reading, not running. `retrospective_v1.py`
# cannot match - the pattern requires `.py` immediately after `retrospective` - and that is deliberate: v1 is
# frozen and kept runnable for the v1/v2 comparison only, so running it does not close a cycle.
# card chat-P1 item 2b (user 2026-09-28): the retrospective runs every third cycle; a cycle that does not owe one closes
# with `py tools/retro_due.py --cycle N --close`, and that command closes the session exactly like the retrospective -
# next_gate (next.json first) and mark_retro_done both hold for it. Without `--close`, retro_due.py is a read.
RETRO_RE = re.compile(r"\bpy(?:thon)?[\w.]*\s+(?:-\S+\s+)*[^\s|;&]*\b(?:retrospective\.py\b|"
                      r"retro_due\.py\b(?=[^|;&\n]*\s--close\b))", re.I)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE)))     # tools/ - for stop_record
import guard_session  # noqa: E402  - ONE definition of the per-session state file

# A RECIPE OR BENCH SCRIPT IN COMMAND POSITION - never a substring match. guard_cycle.py's BUILD_RE carries
# the reason in its own comment: until 2026-09-15 it matched the path ANYWHERE on the line, so a read-only
# one-liner that merely CONTAINED "tools/recipes/*.py" inside a glob was blocked as if it were a build.
# The path must follow a python invocation, optionally past its flags.
# gate-fp fp-4 (card 121-3): `\bpy` also matched the EXTENSION of a preceding path - `md5sum tools/stagexec.py
# tools/bench/x.py` read as `py tools/bench/x.py`. The interpreter token may not follow a `.` (a real `py`/`python`
# token starts a word or follows a path separator, e.g. C:\Python\python.exe).
MATERIAL_RE = re.compile(
    r"(?<![.\w])py(?:thon)?[\w.]*\s+(?:-\S+\s+)*[^\s|;&]*tools[\\/](?:recipes|bench)[\\/][^\s|;&]*\.py", re.I)
# The declaration. It must be its own token, so a path or a log line containing the word cannot launder a run.
#
# THREE accepted forms. `--material` is the ONLY one that works under `claude -p`, and it was added
# 2026-09-18 (cycle 28) after a measured deadlock between this guard and Claude Code's permission layer:
# an allow rule "won't match past an assignment of any other variable" than a small known-safe set
# (https://code.claude.com/docs/en/permissions.md), and MATERIAL is not one of them. So the env-prefix forms
# below put every material command outside EVERY allow rule -> auto-denied with no human to approve, which
# made material recipe runs impossible by construction (two material sessions + one nested sub-agent, 11
# refusals, 7 command shapes). Measured: `ls -la x; echo; grep y z` passes, `MATERIAL=1 ls -d tools` is denied.
# `--material` sits INSIDE the argument list, so `py tools/bgrun.py --material ...` matches the existing
# `Bash(py tools/*)` rule. The guard's meaning is unchanged: a run must still declare itself deliberately and
# still go through bgrun with a deadline. The env forms are kept for PowerShell/interactive use.
MARKER_RE = re.compile(r"(?:^|\s)MATERIAL=1(?=\s|$)|\$env:MATERIAL\s*=\s*['\"]?1['\"]?"
                       r"|(?:^|\s)--material(?=[\s=]|$)", re.I)
# Same exemption idea as guard_cycle.EXEMPT_RE: the review/audit machinery and read-only commands are how a
# judgement session is SUPPOSED to work, so they must never be caught by the gate that pushes work to material.
MATERIAL_EXEMPT_RE = re.compile(
    r"peer\.ps1|retrospective\.py|violations\.py|audit_cycle\.py|outcome_review\.py|prior_art_review\.py|"
    r"guard_|--help|jev_?[\w]*\.py|"          # Jev scripts exempt (user 2026-09-22 "Jev는 면제"; they touch no LabVIEW)
    r"\b(cat|head|tail|sed|grep|less|type|wc|ls|dir)\b", re.I)


def note(marked, cmd):
    """One line per marked run and per refusal, so audit_cycle.py can count judgement-session bypasses.

    Counting must live in a file, not in a session's memory (CLAUDE.md: "when a rule is broken twice, move it
    into a hook" - and a hook whose effect nobody can count is a reminder, not a rule)."""
    try:
        with open(MARKER_LOG, "a", encoding="utf-8") as f:
            f.write("%s\t%s\t%s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),
                                      "MARKED" if marked else "REFUSED",
                                      cmd.replace("\n", " ")[:200]))
    except OSError:
        pass


def material_gate(cmd):
    """0 = pass, 2 = refuse. See the docstring's SECOND RULE."""
    if os.environ.get("MATERIAL_GUARD_OFF") == "1" or os.environ.get("BENCH_CELL"):
        return 0
    if not MATERIAL_RE.search(cmd) or MATERIAL_EXEMPT_RE.search(cmd):
        return 0
    if MARKER_RE.search(cmd):
        note(True, cmd)
        return 0
    note(False, cmd)
    sys.stderr.write(
        "BLOCKED by tools/hooks/guard_bash.py (CLAUDE.md section 3, judgement vs material): this session is "
        "treated as a JUDGEMENT session, and a judgement session never runs tools/recipes/*.py or "
        "tools/bench/*.py itself.\n"
        "Delegate it: spawn the `material` agent with the Agent tool (.claude/agents/material.md) and hand it "
        "the task; it returns a <=30-line fact summary.\n"
        "A material session declares itself with the --material flag on bgrun:\n"
        "  py tools/bgrun.py --material --max-min <N> --log tools/bench/<name>.log -- py -u <script>\n"
        "USE THAT FORM. The older env-prefix forms (MATERIAL=1 py ... / $env:MATERIAL='1'; py ...) are still\n"
        "accepted by this guard but are REFUSED BY THE PERMISSION LAYER under `claude -p`, because an allow\n"
        "rule never matches past an assignment of a non-known-safe variable - so they can never actually run\n"
        "(measured 2026-09-18, cycle 28: 11 refusals across 7 shapes in two material sessions).\n"
        "Reading logs, peer dispatch and the audit/retrospective tools are never blocked.\n")
    return 2
# THIRD RULE, added 2026-09-17: EVERY MOTION COMMAND GOES THROUGH tools/motor_gate.py.
# The user allowed motors while the rig is 조립/assembled ONLY inside a safe envelope (ASI x/y within 1.0 mm of the
# anchor and never a home/origin command, PI 0..39 mm, ASI z free) and ONLY "if the envelope is really enforced by
# code". A survey of tools/ found ~65 files that can reach a motor and no choke point, so the enforcement has to be
# BOTH a gateway (tools/motor_gate.py) and a refusal on every other route - which is this.
# Blocked here = a command that can WRITE motion. Read-only query scripts are named in MOTOR_READONLY_RE and pass.
# A command that mentions motor_gate.py is the sanctioned route and passes.
MOTOR_BLOCKED_RE = re.compile(
    # motion-capable scripts, in command position (py/python ... path, or a .ps1 invoked)
    r"\bpy(?:thon)?[\w.]*\s+(?:-\S+\s+)*[^\s|;&]*(?:hw_rotor_signed_test|hw_rotor_visible|build_rawcmd|"
    r"drive_original_copy)\.py|"
    # the arbitrary-serial-command VI built by build_rawcmd.py, driven from any client
    r"RAWCMD_rotor|RAWCMD\b|"
    # the gate's own sender, run by hand (it also refuses without the gate's token)
    r"motor_send_pi\.ps1|motor_asi_io\.ps1|"
    # inline raw serial - the real bypass route, in either shell
    r"System\.IO\.Ports\.SerialPort|\bimport\s+serial\b|\bserial\.Serial\s*\(|"
    # a raw controller motion command typed into a one-liner
    r"\bMOVREL\b|\bMOVE\s+[XYZ]\s*=|\bMOV\s+[-+0-9]|\bMVR\b|\bGOH\b|\bPIC\s+[-+0-9]|\bPAB\s+[-+0-9]",
    re.I)
# Proven query-only paths (each one's own file documents and hardcodes its read-only command list), plus the
# gateway and its self-test. Checked BEFORE MOTOR_BLOCKED_RE.
MOTOR_READONLY_RE = re.compile(
    r"motor_gate\.py|selftest_motor_gate|read_motor_anchor\.ps1|serial_roundtrip(?:_asi)?\.ps1|"
    r"hw_rotor_read\.py|probe_setcommand\d?\.py|probe_autonics_configure\.py|test_setcommand_signed\.py|"
    r"read_asi_focus\.py", re.I)
# Reading ABOUT one of those files is not running it.
MOTOR_READ_EXEMPT_RE = re.compile(
    r"^\s*(?:cat|head|tail|sed|grep|rg|less|type|wc|ls|dir|Get-Content|Select-String|Get-ChildItem)\b", re.I)


def motor_gate_check(cmd):
    """0 = pass, 2 = refuse. See the THIRD RULE above. Deliberately NOT disabled by LV_GUARD_OFF or BENCH_CELL:
    a benchmark cell has no more right to move a motor than the session that spawned it."""
    if MOTOR_READ_EXEMPT_RE.search(cmd) or MOTOR_READONLY_RE.search(cmd):
        return 0
    if not MOTOR_BLOCKED_RE.search(cmd):
        return 0
    note(False, "MOTOR " + cmd)
    sys.stderr.write(
        "BLOCKED by tools/hooks/guard_bash.py (motor gate): this command can write MOTION to a motor by a route "
        "that bypasses the safe envelope.\n"
        "The user's 2026-09-17 ruling allows motors while the rig is assembled ONLY inside the envelope (ASI x/y "
        "within 1.0 mm of the fixed anchor and never home/origin; PI 0..39 mm; ASI focus axis free), and ONLY "
        "because the envelope is enforced by code.\n"
        "Decide the command with the gateway first:\n"
        "  py tools/motor_gate.py --device pi|asi|rotor --command \"<one raw command>\" --dry-run\n"
        "Read-only query scripts (serial_roundtrip*.ps1, read_motor_anchor.ps1, hw_rotor_read.py, probe_*) are "
        "never blocked. A VI that moves a motor internally (drive_original_copy.py runs the original's device "
        "setup) cannot be gated command-by-command - that one needs a judgement decision, not a flag.\n")
    return 2


# FOURTH RULE, added 2026-09-18 (cycle 18): A RECIPE STOPPED BY A PRIOR-ART VERDICT MAY NOT BE LAUNCHED.
# THIS IS THE CALL SITE ROUTE-B RUN 3 GOT THROUGH. `guard_cycle.py` gates the BUILD and only ever reads the NEWEST
# prior-art review, so once that review was annotated the recipe launched six seconds later and failed exactly as
# the review predicted (docs/cycle18-plan.md, "What actually failed"; 781 s + $4.85 in the review that followed).
# `tools/stop_record.py` keys the refusal to the recipe's own PATH and HASH and releases only on the SAME
# machine-checked `FIXED:` / `REFUTED:` lines guard_cycle already validates - no second validator, no third
# release form. It fails closed for `tools/recipes/` paths and cannot wedge anything else (its own try/except).
# Deliberately NOT disabled by LV_GUARD_OFF or BENCH_CELL, for the motor gate's reason: a benchmark cell has no
# more right to run a stopped recipe than the session that spawned it.
# card 103-4: a STATIC LINTER segment (`py -m pyflakes|pycodestyle|flake8 <file>`) only parses the file - it never runs it -
# yet stop_record classes any `py -m <module>` outside its py_compile/ast list as "build" and refused the READ
# `wc -l <recipe> && py -m pyflakes <recipe> 2>&1 | head` (material_marker.log:2175). Such segments are dropped before
# the check; nothing else is: a command that pipes into an executor keeps every segment (EXEC_PIPE_RE), and any
# other segment naming the recipe is judged by stop_record unchanged. Self-test: tools/bench/selftest_c103d_hooks.py.
# TIGHTENED after archive/peer/2026-09-27-c103d-hooks-before.md (ACCEPTED): program exactly py/python[N.N] with no env
# prefix and no flags, pyflakes/pycodestyle only (flake8 loads plugins from config files), blank = space/tab only (a
# newline inside a quote-balanced segment ran the recipe), plain path-ish arguments only (no quote, '=', '$'); and no drop
# at all when a segment cd's anywhere but the project root or a pyflakes/pycodestyle shadow sits at the root (`-m` puts
# the working directory first on sys.path).
LINT_SEG_RE = re.compile(r"^[ \t]*py(?:thon[\d.]*)?(?:\.exe)?[ \t]+-m[ \t]+(?:pyflakes|pycodestyle)"
                         r"(?:[ \t]+[\w./\\:-]+)*(?:[ \t]+2>&1)?[ \t]*$", re.I)
CD_SEG_RE = re.compile(r"^[ \t]*cd[ \t]+(\"[^\"\n]*\"|'[^'\n]*'|[^\s\"']+)[ \t]*$", re.I)
PROJECT_ROOT = os.path.dirname(os.path.dirname(HERE))


def _drop_lint_segments(cmd, sr):
    if sr.EXEC_PIPE_RE.search(cmd or ""):
        return cmd
    segs = sr.split_segments(cmd or "")
    for s in segs:
        m = CD_SEG_RE.match(s)
        if m and os.path.normcase(os.path.abspath(m.group(1).strip("'\""))) != os.path.normcase(PROJECT_ROOT):
            return cmd
    if any(os.path.exists(os.path.join(PROJECT_ROOT, n)) for n in ("pyflakes", "pyflakes.py", "pycodestyle", "pycodestyle.py")):
        return cmd
    keep = [s for s in segs if not LINT_SEG_RE.match(s)]
    return cmd if len(keep) == len(segs) else " ; ".join(keep)


# card 106-4 (PD216(g), the `wc -l` TWIN of archive/peer/2026-09-27-c103d-hooks-before.md s1): stop_record.split_segments
# knows no backslash escapes, so in BASH `wc -l \"x<NL>py -u <recipe><NL>\"` looked like ONE quote-balanced read-only
# segment while bash ran line 2. Before the check, a Bash command's escaped quote characters (outside single quotes -
# where bash has no escapes) are replaced by `_`, so the splitter sees the quotes bash sees. Only `\"` and `\'` change;
# every other byte, and every PowerShell command (no backslash escapes there), reaches stop_record unchanged.
# Self-test: tools/bench/selftest_c106d_tools.py H2 (fails on the pre-106-4 hook, passes now).
def _bash_escaped_quotes(cmd):
    out, q, i, s = [], None, 0, cmd or ""
    while i < len(s):
        ch = s[i]
        if q == "'":
            out.append(ch)
            q = None if ch == "'" else q
        elif ch == "\\" and i + 1 < len(s):        # an escape pair: consumed whole (so `\\"` still closes)
            nxt = s[i + 1]
            out.append("_" if nxt == '"' or (nxt == "'" and q is None) else ch + nxt)
            i += 2
            continue
        else:
            out.append(ch)
            if ch in ("\"", "'") and q is None:
                q = ch
            elif ch == '"' and q == '"':
                q = None
        i += 1
    return "".join(out)


_CUR_TOOL = [None]     # set by _main(); stop_gate keeps its one-argument call shape (selftest_launch_gate patches it)


def stop_gate(cmd, shell=None):
    """0 = pass, 2 = refuse. One call, no logic duplicated - see tools/stop_record.py."""
    try:
        import stop_record
    except Exception:
        return 0                     # a missing/broken module must not wedge every command in the session
    shell = shell or _CUR_TOOL[0] or "Bash"
    seen = _bash_escaped_quotes(cmd) if shell == "Bash" else cmd
    allow, why = stop_record.check_command(_drop_lint_segments(seen, stop_record))
    if allow:
        return 0
    note(False, "STOPPED-RECIPE " + cmd)
    sys.stderr.write(why)
    return 2


_PENDING_STAGE = []     # the stage launch prerun_gate allowed in THIS hook call (card chat-D, retry cap)


def _lint_stripped(cmd, shell=None):
    """card 110-1 (docs/violation-decisions.md device-failed 15:49): the command prerun_gate judges, with the read-only
    lint segments dropped exactly as stop_gate drops them (same escape view, same _drop_lint_segments). A command with
    no droppable segment reaches check_launch byte-for-byte unchanged."""
    try:
        import stop_record
    except Exception:                                                              # noqa: BLE001
        return cmd
    shell = shell or _CUR_TOOL[0] or "Bash"
    seen = _bash_escaped_quotes(cmd) if shell == "Bash" else cmd
    out = _drop_lint_segments(seen, stop_record)
    return cmd if out == seen else out


def prerun_gate(cmd):
    """0 = pass, 2 = refuse. The decision lives in tools/stage_prerun.py check_launch() (argv parsing + records).
    Fails CLOSED only for a command that launches a stage script; anything else passes if the module is broken."""
    try:
        import stage_prerun
    except Exception as e:                                                         # noqa: BLE001
        if re.search(r"tools[\\/]recipes[\\/]stage_\w*\.py|tools[\\/]stagexec\.py\s+run\b", cmd or ""):
            sys.stderr.write("BLOCKED by tools/hooks/guard_bash.py: the stage launch gate cannot load "
                             "tools/stage_prerun.py (%s); a stage script is not launched unchecked.\n" % e)
            return 2
        return 0
    c = _lint_stripped(cmd)           # card 110-1: the same lint-segment drop as stop_gate (violation-decisions 15:49)
    allow, why = stage_prerun.check_launch(c)
    if allow:
        if (stage_prerun.launched_stage_scripts(c) or stage_prerun.launched_plan_runs(c)       # card chat-S3
                or getattr(stage_prerun, "launched_vi_modifying", lambda _c: [])(c)):          # card chat-N1 (2)
            _PENDING_STAGE[:] = [cmd]      # kept for callers; RECORDING moved to tools/bgrun.py (card 78-2)
        return 0
    note(False, "PRERUN-GATE " + cmd)
    sys.stderr.write("BLOCKED by tools/hooks/guard_bash.py: " + why)
    return 2


def retro_closes(cmd, data):
    """True when this retrospective launch really closes the session's cycle (see main)."""
    return not re.search(r"(?:^|\s)--dry-run(?=\s|$)", cmd or "") and not (data or {}).get("agent_id")


# Match INVOCATIONS of LabVIEW-driving tools, not any mention of their paths (cat/grep of a file
# under tools/bench is not a LabVIEW action).
# ANY python script under tools/ (recipes, bench, gscript, lvclick, verify_op, ...) counts — the
# narrower list let tools/recipes/keystone_discovery.py run unbounded for 3 h 48 min (2026-09-05).
# THE DEADLINE RUNNER, with ANY flags before --max-min. Until 2026-09-18 this was the literal
# `bgrun\.py\s+--max-min\s+\d` in two places, i.e. --max-min had to be the FIRST argument. Cycle 28 added the
# `--material` flag (MARKER_RE above) because the env-prefix form is auto-denied by the permission layer - and
# the very first command written in the new, mandated form,
#   py tools/bgrun.py --material --max-min 3 --log ... -- py -u tools/bench/selftest_audit_cost_window.py
# was BLOCKED here ("a backgrounded LabVIEW command must run through py tools/bgrun.py --max-min ..."), because
# --material sat where the regex demanded --max-min. The repair of MARKER_RE had left its sibling pattern behind,
# so the only permitted material form was refused by the same hook that mandates it. Flags before --max-min are
# now skipped; --max-min with a number is still required, so the deadline guarantee is unchanged.
BGRUN_RE = re.compile(r"bgrun\.py\s+(?:-\S+\s+)*--max-min\s+\d")

LABVIEW_RE = re.compile(r"lv_gui\.ps1\s+-Action|py[\w.]*\s+(?:-u\s+)?[^\s|;&]*tools[\\/][^\s|;&]*\.py|"
                        r"py[\w.]*\s+-c\s+.*?(?:import\s+(?:gscript|lvclick)|from\s+(?:gscript|lvclick))|"
                        r"peer\.ps1\s+-Agent|import gscript", re.I | re.S)


NEXT_SECTION_RE = re.compile(r"^##\s+NEXT\s*$(.*?)(?=^##\s|\Z)", re.M | re.S)


def next_md5(status_path):
    """md5 of STATUS.md's `## NEXT` section (stripped), or '' when the file/section is missing."""
    import hashlib
    try:
        with open(status_path, encoding="utf-8", errors="replace") as f:
            m = NEXT_SECTION_RE.search(f.read())
    except OSError:
        return ""
    return hashlib.md5((m.group(1).strip() if m else "").encode("utf-8")).hexdigest()


def next_json_state(root):
    """(md5 of tools/bench/next.json bytes | 'absent', why-invalid | None). Session protocol v1 C7: the machine copy
    of NEXT is `next.json` (docs/protocol/next.json); the prose `## NEXT` in STATUS stays for people."""
    # NEXT_JSON / NEXT_SNAPSHOT env overrides: self-tests only (selftest_guard_session G12/G13, card chat-L2) - so a
    # test never reads the LIVE hand-off files. Unset in every real session.
    path = os.environ.get("NEXT_JSON") or os.path.join(root, "tools", "bench", "next.json")
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        import protocol
    except Exception as e:      # noqa: BLE001
        return "absent", "protocol.py not importable: %s" % e
    m, card, why = protocol.next_state(path)
    return m, (None if (card is not None or m == "absent") else why)


def next_gate():
    """Refuse a retrospective launch until the cycle has written a NEW, VALID `tools/bench/next.json`.

    SESSION PROTOCOL v1, C7 (2026-09-24): the runner writes `tools/bench/next_snapshot.md5` = md5 of next.json's
    bytes (or `absent`) right before it spawns the session; the retrospective is refused while next.json is absent,
    unchanged from that snapshot, or invalid against docs/protocol/next.json. (Until 2026-09-24 this compared the md5
    of STATUS.md's prose `## NEXT` section; sessions 58/64/65/66 are why the gate exists at all.)

    A next.json that passes then gets one ADVISORY Jev reading of STATUS's prose NEXT (docs/jev-integration-plan.md
    #5). It prints and it logs; it NEVER blocks. Any failure of the reading is silence, by construction."""
    root = os.path.dirname(os.path.dirname(HERE))
    snap_path = os.environ.get("NEXT_SNAPSHOT") or os.path.join(root, "tools", "bench", "next_snapshot.md5")

    def _jev_advisory():
        """ADVISORY ONLY. Reads STATUS's NEXT, asks Jev whether a fresh session could start from it, and on a
        low probability writes one `JEV-NEXT-POOR` line to stderr and to tools/bench/jev_gate.log."""
        try:
            for d in (os.path.join(root, "tools"), os.path.join(root, "tools", "bench")):
                if d not in sys.path:
                    sys.path.insert(0, d)
            import jev
            from jev_next_q import MISSING_Q, NEXT_Q
            with open(os.path.join(root, "STATUS.md"), encoding="utf-8", errors="replace") as fh:
                m = NEXT_SECTION_RE.search(fh.read())
            text = (m.group(1).strip() if m else "")[:6000]
            if not text:
                return
            resp, err = jev.ask({"next": text}, {"startable": NEXT_Q},
                                purpose="next-gate", timeout=20, retries=0)
            if err:
                return
            p = jev.noul(resp, "startable")
            if p is None or p > jev.UNKNOWN_LO:      # 0.30: anything above it is not a complaint
                return
            missing = "?"
            mresp, merr = jev.ask({"next": text}, {"missing": MISSING_Q},
                                  purpose="next-gate-missing", timeout=20, retries=0)
            if not merr:
                missing = jev.choice(mresp, "missing")[0] or "?"
            line = "JEV-NEXT-POOR p=%.2f: %s" % (p, missing)
            sys.stderr.write(line + "  (advisory, nothing is blocked; docs/jev-integration-plan.md #5)\n")
            try:
                with open(os.path.join(root, "tools", "bench", "jev_gate.log"), "a", encoding="utf-8") as fh:
                    fh.write("%s | %s | next_gate\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), line))
            except OSError:
                pass
        except Exception:      # noqa: BLE001 - an advisory reading may never break the hook
            return

    try:
        with open(snap_path, encoding="utf-8") as f:
            snap = f.read().strip()
    except OSError:
        return 0          # no runner snapshot (interactive chat, self-tests): nothing to compare against
    if not snap:
        return 0
    cur, invalid = next_json_state(root)
    if cur != "absent" and cur != snap and not invalid:
        _jev_advisory()
        return 0
    why = ("tools/bench/next.json does not exist" if cur == "absent" else
           "tools/bench/next.json is INVALID: %s" % invalid if invalid else
           "tools/bench/next.json is byte-identical to what this cycle started with")
    sys.stderr.write(
        "BLOCKED by tools/hooks/guard_bash.py (NEXT before the retrospective; user 2026-09-21; session protocol v1\n"
        "C7): %s. Write the hand-off FIRST - `tools/bench/next.json` (schema next/1: act, task_kind, plan {path,md5},\n"
        "pass, advances or unblocks, stop_requested) checked with `py tools/protocol.py validate tools/bench/next.json`,\n"
        "and STATUS.md's prose `## NEXT` for people - then launch the retrospective. Reading, diagnostics and every\n"
        "other command are not affected.\n" % why)
    return 2


# FIFTH AND SIXTH, added 2026-09-22 (user, "이거 다 적용해보자"): TWO ADVISORY READINGS, NEITHER OF WHICH BLOCKS.
# docs/jev-integration-plan.md's second-wave table #4 (per-command drift) and #3 (stage-file pre-flight). They
# are deliberately NOT gates: every path below returns None, main() discards the result, and a missing key, a
# dead network or a raised exception is silence. The blocking gates above decide whether a command runs; these
# two only write a line to stderr and to tools/bench/jev_gate.log.
#
# COST DISCIPLINE: the drift reading is rate-limited to one Jev call per 60 s per session (jev_drift._rate_ok,
# a state file beside the gate log) and skips read-only commands; the pre-flight reading fires only when a
# recipe or stage script is actually being launched, under its own 60 s limiter. Jev's own scripts are skipped
# so a measurement run cannot ask about itself.
_JEV_SELF_RE = re.compile(r"jev[\w]*\.py|jev_\w+", re.I)
# The script a bgrun command is about to launch: after the `--` separator, or in plain command position.
_LAUNCHED_RE = re.compile(
    r"--\s+py(?:thon)?[\w.]*\s+(?:-\S+\s+)*\"?([^\"\s|;&]*tools[\\/](?:recipes|bench)[\\/][\w.\-]+\.py)\"?|"
    r"\bpy(?:thon)?[\w.]*\s+(?:-\S+\s+)*\"?([^\"\s|;&]*tools[\\/](?:recipes|bench)[\\/][\w.\-]+\.py)\"?", re.I)


def jev_advisories(cmd, data):
    """ADVISORY ONLY. Returns the lines it printed (for the self-test); main() ignores them. Never raises."""
    lines = []
    if os.environ.get("BENCH_CELL") or os.environ.get("JEV_ADVISORY_OFF") == "1":
        return lines
    if not cmd or _JEV_SELF_RE.search(cmd):
        return lines
    try:
        root = os.path.dirname(os.path.dirname(HERE))
        for d in (os.path.join(root, "tools"), os.path.join(root, "tools", "bench")):
            if d not in sys.path:
                sys.path.insert(0, d)
        sid = guard_session.session_id(data)
    except Exception:      # noqa: BLE001
        return lines
    try:
        import jev_drift
        line = jev_drift.advisory(cmd, sid=sid)
        if line:
            lines.append(line)
    except Exception:      # noqa: BLE001
        pass
    try:
        m = _LAUNCHED_RE.search(cmd)
        if m:
            import jev_drift as _jd
            import jev_preflight
            script = m.group(1) or m.group(2)
            path = script if os.path.isabs(script) else os.path.join(root, script)
            if os.path.exists(path) and _jd._rate_ok(str(sid) + ":preflight"):
                line = jev_preflight.advisory(path)
                if line:
                    lines.append(line)
    except Exception:      # noqa: BLE001
        pass
    return lines


def main():
    """RETRY CAP (user 2026-09-24, card chat-D). This hook only CHECKS the cap (prerun_gate -> check_launch). It no
    longer RECORDS: a PreToolUse hook runs before later hooks, guard_cycle and the permission layer, so a launch it
    recorded could still be refused and never start (stage_runs.jsonl:3-7, docs/violation-decisions.md
    "device-failed - 2026-09-25 07:05"). The run is recorded by tools/bgrun.py at CHILD START (card 78-2)."""
    _PENDING_STAGE.clear()
    return _main()


def _main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if data.get("tool_name") not in ("Bash", "PowerShell"):
        return 0
    ti = data.get("tool_input") or {}
    cmd = ti.get("command", "") or ""
    # SESSION PROTOCOL v1, C2 (2026-09-24): a card-carrying sub-agent (payload has agent_id + agent_type) is bound to
    # its task/1 card by its first command, `py tools/protocol.py bind <card>`, and every later command is checked
    # against the card's flags (labview / gui / hardware / run_vi / status_edit / git_commit / peers). ONE decision
    # function, tools/protocol.py hook_decision(), shared with tools/hooks/guard_card.py (the non-shell tools). The
    # main session has no agent_id and is not affected. Checked first and not disabled by any env var.
    try:
        import guard_card
        rc, msg = guard_card.decide(data)
    except Exception:      # noqa: BLE001 - a broken card guard must not wedge every command
        rc, msg = 0, None
    if rc:
        sys.stderr.write("BLOCKED by tools/hooks/guard_bash.py (session protocol v1, card flags): %s\n" % msg)
        return rc
    # THE MOTOR GATE IS CHECKED FIRST AND IS NOT DISABLED BY ANY ENV VAR (see motor_gate_check).
    rc = motor_gate_check(cmd)
    if rc:
        return rc
    # THE LAUNCH GATE, checked before any env-var escape for the same reason as the motor gate (FOURTH RULE).
    _CUR_TOOL[0] = data.get("tool_name")
    rc = stop_gate(cmd)
    if rc:
        return rc
    # FIFTH RULE (user 2026-09-24, CLAUDE.md §3 "Stages are SIMULATED and PRE-RUN OFFLINE", decisions 1/2/4): a
    # stage script (`tools/recipes/stage_*.py` in COMMAND position - argv, never a substring) is launched only with a
    # dry-run PASS and a pre-run PASS for its current sha256 + plan md5s, both newer than its last failing run.
    rc = prerun_gate(cmd)
    if rc:
        return rc
    # Benchmark cells spawned by tools/bench/matrix_run.py inherit this hook via the project
    # settings; their GUI calls are short and sequential by construction, so the driver sets
    # LV_GUARD_OFF=1 in their environment. The main session never has it set.
    if os.environ.get("LV_GUARD_OFF") == "1":
        return 0
    # NEXT BEFORE THE RETROSPECTIVE (user, 2026-09-21: "NEXT 작성하도록 훅에 강제할 필요성 있을듯"): four sessions
    # (58, 64, 65, 66) launched their retrospective, waited on it, and exited without ever rewriting STATUS's
    # `## NEXT`, so the next cycle started from a stale hand-off every time. The runner snapshots the NEXT
    # section's md5 right before it spawns the session (tools/bench/next_snapshot.md5); a retrospective launch
    # while NEXT still hashes the same is refused - and refused BEFORE the retro-done mark below, so the
    # session can still write NEXT and launch again.
    if not os.environ.get("BENCH_CELL") and RETRO_RE.search(cmd):
        rc = next_gate()
        if rc:
            return rc
    # Observe-only, never a refusal: mark this session's cycle as reviewed. See RETRO_RE above.
    # NOT by a `--dry-run` retrospective (it reviews nothing) and NOT by a call carrying `agent_id` (a sub-agent's
    # command is not the judgement session closing its cycle) - the false close of 2026-09-24 (card chat-C1).
    if not os.environ.get("BENCH_CELL") and RETRO_RE.search(cmd) and retro_closes(cmd, data):
        guard_session.mark_retro_done(guard_session.session_id(data))
    rc = material_gate(cmd)
    if rc:
        return rc
    # AFTER every blocking gate and before the foreground/background routing: the two advisory readings.
    # Their value is discarded on purpose - see jev_advisories().
    jev_advisories(cmd, data)
    if not LABVIEW_RE.search(cmd):
        return 0
    # A PROSE dispatch (`peer.ps1 -Kind prose`, the reporter agent writing a user-facing report through codex)
    # touches no LabVIEW and must be WAITED FOR in the foreground: twice on 2026-09-16 the reporter cell, refused
    # a >30 s foreground run here, backgrounded the call and returned before the report existed - and the
    # second time the agent's exit killed the child before codex even started. A bounded foreground wait
    # (<= 6 min, bgrun still mandatory) is the correct shape for it.
    if re.search(r"peer\.ps1\b.*-Kind\s+prose\b", cmd, re.I) and BGRUN_RE.search(cmd):
        timeout = ti.get("timeout")
        if not ti.get("run_in_background") and timeout is not None and int(timeout) <= 360_000:
            return 0
    if ti.get("run_in_background"):
        # Background is allowed ONLY through the deadline runner (user, 2026-09-05: a background
        # job hung 3 h 48 min with no limit). Task-Scheduler launches of the matrix driver are
        # PowerShell Start-Process/Register-ScheduledTask calls and do not match here.
        if BGRUN_RE.search(cmd):
            return 0
        sys.stderr.write("BLOCKED by tools/hooks/guard_bash.py: a backgrounded LabVIEW command must run through "
                         "`py tools/bgrun.py --max-min <N> --log <file> -- <command>` so it has a hard deadline "
                         "and a final log line.\n")
        return 2
    timeout = ti.get("timeout")
    if timeout is not None and int(timeout) <= MAX_FG_MS:
        return 0
    sys.stderr.write(
        f"BLOCKED by tools/hooks/guard_bash.py (CLAUDE.md 2b): a LabVIEW-touching command must run with "
        f"run_in_background=true, or with an explicit timeout <= {MAX_FG_MS // 1000} s. "
        f"Got timeout={timeout}. Background it (you will be notified) or split it into a short step.\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())
