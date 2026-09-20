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
RETRO_RE = re.compile(r"\bpy(?:thon)?[\w.]*\s+(?:-\S+\s+)*[^\s|;&]*\bretrospective\.py\b", re.I)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE)))     # tools/ - for stop_record
import guard_session  # noqa: E402  - ONE definition of the per-session state file

# A RECIPE OR BENCH SCRIPT IN COMMAND POSITION - never a substring match. guard_cycle.py's BUILD_RE carries
# the reason in its own comment: until 2026-09-15 it matched the path ANYWHERE on the line, so a read-only
# one-liner that merely CONTAINED "tools/recipes/*.py" inside a glob was blocked as if it were a build.
# The path must follow a python invocation, optionally past its flags.
MATERIAL_RE = re.compile(
    r"\bpy(?:thon)?[\w.]*\s+(?:-\S+\s+)*[^\s|;&]*tools[\\/](?:recipes|bench)[\\/][^\s|;&]*\.py", re.I)
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
    r"guard_|--help|"
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
def stop_gate(cmd):
    """0 = pass, 2 = refuse. One call, no logic duplicated - see tools/stop_record.py."""
    try:
        import stop_record
    except Exception:
        return 0                     # a missing/broken module must not wedge every command in the session
    allow, why = stop_record.check_command(cmd)
    if allow:
        return 0
    note(False, "STOPPED-RECIPE " + cmd)
    sys.stderr.write(why)
    return 2


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


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if data.get("tool_name") not in ("Bash", "PowerShell"):
        return 0
    ti = data.get("tool_input") or {}
    cmd = ti.get("command", "") or ""
    # THE MOTOR GATE IS CHECKED FIRST AND IS NOT DISABLED BY ANY ENV VAR (see motor_gate_check).
    rc = motor_gate_check(cmd)
    if rc:
        return rc
    # THE LAUNCH GATE, checked before any env-var escape for the same reason as the motor gate (FOURTH RULE).
    rc = stop_gate(cmd)
    if rc:
        return rc
    # Benchmark cells spawned by tools/bench/matrix_run.py inherit this hook via the project
    # settings; their GUI calls are short and sequential by construction, so the driver sets
    # LV_GUARD_OFF=1 in their environment. The main session never has it set.
    if os.environ.get("LV_GUARD_OFF") == "1":
        return 0
    # Observe-only, never a refusal: mark this session's cycle as reviewed. See RETRO_RE above.
    if not os.environ.get("BENCH_CELL") and RETRO_RE.search(cmd):
        guard_session.mark_retro_done(guard_session.session_id(data))
    rc = material_gate(cmd)
    if rc:
        return rc
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
