# Failed prediction — attack this diagnosis. Do NOT confirm it.

Your job is to REFUTE. Find the strongest reason the diagnosis below is wrong, give an alternative
explanation, say what would falsify it, and name the cheapest discriminating test.

## PREDICTION (what we believed)
Material sub-agents spawned by a `claude -p --permission-mode acceptEdits` judgement session can
execute recipe runs of the form `py tools/bgrun.py --max-min N --log <f> -- py -u <script>`.

## OBSERVATION (what happened)
Every Bash/PowerShell command was refused: 11 refusals across 7 different command shapes, in two
independent material sessions plus one nested sub-agent. The refusals came from the harness
permission layer. `tools/hooks/guard_bash.py`'s own refusal text NEVER appeared in any refusal —
i.e. the PreToolUse hook was not the refuser.

## DIAGNOSIS UNDER TEST
`guard_bash.py`'s MARKER_RE required the literal string `MATERIAL=1` to appear inside the command
string, so every material command had to be written as `MATERIAL=1 py tools/bgrun.py ...` (bash) or
`$env:MATERIAL='1'; py tools\bgrun.py ...` (PowerShell). Claude Code permission allow rules do not
match past an assignment of a non-known-safe environment variable. Therefore the prefixed command
matched NO allow rule and was auto-denied, with no human present to approve it. That is a deadlock
between two of our OWN rules (the project's material-marker rule and the harness's permission
matching), not a transient outage.

## EVIDENCE
- In one session `ls -la <path>; echo ---; grep -n <x> <f>` was PERMITTED while `MATERIAL=1 ls -d tools`
  was DENIED — same binary, same session, same directory; the sole difference was the env prefix.
- Documentation: https://code.claude.com/docs/en/permissions.md — "an allow rule won't match past an
  assignment of any other variable" (only known-safe variables are tolerated).

## FIX APPLIED (this is what you should attack hardest)
A `--material` FLAG on `tools/bgrun.py`, accepted by `guard_bash.py`'s MARKER_RE in place of the env
prefix. Guard semantics are unchanged: a run still declares itself as material and still goes through
`bgrun` with a hard deadline. The bypass env var `MATERIAL_GUARD_OFF` was left untouched and was NOT
used. The flag sits inside the existing `Bash(py tools/*)` allow rule, so the command head matches.

## ALREADY RULED OUT (do not spend your answer here)
1. `guard_bash.py` as the refuser — its own refusal text never appeared in any of the 11 refusals.
2. A stalled or hung LabVIEW/COM client — no run ever reached LabVIEW; the refusal was before execution.
3. Agent-definition tool restrictions — `.claude/agents/material.md` grants all tools, and Edit/Write
   calls succeeded in the very same sessions that had every Bash call denied.

## QUESTIONS FOR YOU
1. Is the root cause right? What else could deny 11 commands across 7 shapes while Edit/Write pass?
2. Does the `--material` flag actually FIX it, or does it merely RELOCATE the marker into a position
   that some other rule (deny rules, `--` REMAINDER parsing, prefix matching on the command head,
   sub-agent permission inheritance, `acceptEdits` mode semantics) still denies?
3. Does moving the marker from an env var to a CLI flag WEAKEN the judgement/material separation the
   marker exists to enforce (e.g. is it now trivially forgeable or trivially omitted)?
4. What is the single cheapest test that would FALSIFY the diagnosis if it is wrong?
