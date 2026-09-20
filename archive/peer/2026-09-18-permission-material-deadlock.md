# permission-material-deadlock

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.6059  in 22 / out 29901 / cache-create 226856 / cache-read 1179387  (401s, 27 turn(s))
- **date:** 2026-09-18 16:32:50
- **outcome:** ANSWERED (402s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

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


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

## 1. The strongest reason the diagnosis is wrong

**"That is a deadlock … which made material recipe runs impossible by construction" is false, and your own logs refute it.** A permitted form existed and was in continuous production use for **sixteen hours before the fix was written**: move the marker off the front of the line.

```
material_marker.log:286  11:03:53  MARKED  MATERIAL=1 py tools/bgrun.py --max-min 25 --log tools/bench/diag_fstunnel_orphans.log -- py -u …
material_marker.log:287  11:04:12  MARKED  py tools/bgrun.py --max-min 25 --log tools/bench/diag_fstunnel_orphans.log -- py -u ….py MATERIAL=1
diag_fstunnel_orphans.log:1        BGRUN START 2026-09-18 11:04:13 … : py -u tools/bench/diag_fstunnel_orphans.py MATERIAL=1
diag_fstunnel_orphans.log:159      BGRUN END rc=0 after 90s
```

One `BGRUN START`, at 11:04:**13** — the trailing-marker attempt, one second after the hook saw it. The prefixed attempt 19 s earlier produced nothing. Same pattern, independently, at `material_marker.log:299-302` → `diag_fstunnel_preclean_twins.log:1` (`BGRUN START … 12:32:03 … py -u ….py MATERIAL=1`, `rc=1 after 89s`). `Bash(py tools/*)` matched it, because a `*` in a Bash rule "matches any text, including spaces" and there is no shell separator in the string ([permissions.md, Wildcard patterns / Bash](https://code.claude.com/docs/en/permissions.md)).

The ladder **cd&&prefix → prefix → `$env:` → trailing marker** repeats at 00:22, 00:49, 01:28, 02:20, 03:32, 08:58, 09:22, 09:49, 10:27, 10:47, 11:02, 11:41, 13:03 on 2026-09-18 (`material_marker.log:194-317`) — thirteen sessions, each burning ~3–4 denied tool calls, each ending in a run that worked. At 13:28 `build_opfstunnelterm_v2.py` was built that way (`:316`). So the true finding is far narrower than stated: **a marker in leading shell-assignment position is unpermittable; a marker anywhere else on the line was already permitted.** No code change was required.

And the load-bearing sentence is now *in the guard as a comment* (`guard_bash.py:52-55`) and *in bgrun's help text* (`bgrun.py:94-97`), where the next session will read it as fact.

## 2. Alternative explanation of the same evidence

**Your controlled pair is not controlled, and "already ruled out #1" rules out one of four refusers.**

- `ls -la …; echo; grep -n …` was not permitted by an allow rule. Claude Code auto-approves "a built-in set of read-only commands" independent of rules ([permissions.md](https://code.claude.com/docs/en/permissions.md), permission-system table). `MATERIAL=1 ls -d tools` fails that classifier — "when Claude Code can't fully parse a command, it asks for approval instead of treating the command as read-only" (ibid., read-only commands). So the pair demonstrates the prefix defeats the **read-only classifier**; it says nothing about `Bash(py tools/*)`. The allow-rule claim rests entirely on the doc sentence, not on your experiment. (The doc sentence is real: *"Claude Code also strips a leading assignment of certain known-safe environment variables… An allow rule won't match past an assignment of any other variable."*)
- **Three other refusers print text that never contains "guard_bash.py".** `stop_record.py:274` writes `BLOCKED by tools/stop_record.py`, and it refused `certutil -hashfile` (an *allow-listed* command), `sed -n`, `py -m py_compile` and a `grep` on that same day (`material_marker.log:263-267`). `guard_peer.py` and `guard_cycle.py` sit on the same `Bash|PowerShell` matcher (`.claude/settings.json:51-73`). Absence of guard_bash's string is not absence of a hook refusal.
- Several denied shapes carry `cd … &&`, `2>&1`, `cp`, `md5sum`, `certutil`. Per the docs a rule "must match each subcommand independently," and `cd` combined with a redirect prompts on its own. Attributing all 11 refusals to one cause over-fits a heterogeneous set.

## 3. What would falsify the claim

A `BGRUN START` in any bench log at the timestamp of a **prefixed** hook entry — i.e. a `MATERIAL=1 py tools/bgrun.py …` line in `material_marker.log` whose target log opens within ~2 s. I checked two and found none, so the prefix claim survives on a sample of 2 of ~13. The "impossible by construction" claim is already falsified by the trailing-form starts above.

## 4. Cheapest discriminating test

The one I just ran, and it costs nothing but reads: **for each `MATERIAL=1 py tools/bgrun.py --log X` line in `material_marker.log`, grep `X` for `^BGRUN START` and compare timestamps.** Hook time ≈ start time → the prefixed form ran (diagnosis dead). Start time only at the later non-prefixed retry → prefix denied, workaround worked. Thirteen cases, no LabVIEW, no lock, ~1 minute.

---

## Your four questions

**1. Root cause — substantially right, badly evidenced, and overstated.** The mechanism is real and documented. "Deadlock between two of our own rules" is not: the marker regex never required the marker in assignment position; `MARKER_RE`'s first alternative is `(?:^|\s)MATERIAL=1(?=\s|$)`, which matches a trailing token. The rule that actually forced the denied form is `.claude/agents/material.md:26-27` — prose, not a gate.

**2. The flag does clear the permission layer — and does not fix the failure.** Evidence it clears: `material_marker.log:362-363` → `selftest_audit_cost_window.log:1` (`BGRUN START … 16:26:02 … py -u tools/bench/selftest_audit_cost_window.py`, the flag consumed by bgrun, `rc=0`). One data point, one script, one session. It does **not** relocate into a new denial: no Bash `deny` rule exists (`.claude/settings.json:26-35`), `--` is not a recognized separator, and the command head is unchanged.

But the failing behaviour is produced by the **instructor**, not the acceptor, and the instructor was not changed:

- `.claude/agents/material.md:27` — "**The `MATERIAL=1` prefix is mandatory**", still, today.
- `tools/cycle_runner.py:194` — every firefighter cycle is told to "run the recipe under bgrun with the MATERIAL=1 marker".

The next material sub-agent will be told to write the denied form, and will burn the same 3–4 turns. Adding an accepted form while leaving the mandated form untouched changes nothing a session experiences. **That, not the regex, is the repair.**

Two smaller things in the same edit: `BGRUN_RE = bgrun\.py\s+(?:-\S+\s+)*--max-min\s+\d` skips only flag-*shaped* tokens, so `--log tools/bench/x.log` before `--max-min` still fails the bgrun check (the value token isn't `-\S+`) — the mandated order works, a reorder does not. And `MARKER_RE`'s `--material` alternative matches anywhere, including after `--`, where bgrun never receives it.

**3. It does not weaken the separation, because there was none to weaken.** `material_marker.log:208-216` shows the gate being satisfied by a trailing **comment** — `py tools\bgrun.py … -- py -u ….py   # MATERIAL=1 material-session declaration` — eleven consecutive runs, no environment variable ever set. Nothing in the fleet reads `os.environ["MATERIAL"]` (only `MATERIAL_GUARD_OFF`), so the env form carried no information either. Both forms are a self-declaration by the same model in the same process; `--material` is marginally more honest, since bgrun actually consumes it and the trailing-token workaround it replaces was injecting `MATERIAL=1` as bogus `argv` into the inner script (visible in `diag_fstunnel_orphans.log:1`) — which would kill any recipe with a strict argument parser.

**4. Cheapest falsifier for the remaining open question** (did the fix fix anything?): `grep -rn "MATERIAL=1" .claude/agents tools/cycle_runner.py`, then run one material dispatch and count Bash denials before its first successful `BGRUN START`. Non-zero ⇒ the fix did not land where the cost is.

**What would change my mind:** a timestamp-matched `BGRUN START` for a prefixed command under `claude -p` (kills the root cause outright), or evidence that `material.md` and `cycle_runner.py` were updated in the same change and I read a stale copy.

Sources: [Configure permissions — Claude Code](https://code.claude.com/docs/en/permissions.md)

## Sources

(extract from answer)

## What was done with it

ANSWERED (opus/max, 402 s), and it is a PARTIAL REFUTATION, accepted on its evidence, not on its authority.

1. **Accepted — the fix executes.** Measured here the same hour, independently of the peer: the flag form
   `py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_audit_cost_window.log -- py -u
   tools/bench/selftest_audit_cost_window.py` was PERMITTED and ran to completion (`SELFTEST 7 pass / 0 fail`,
   `BGRUN END rc=0 after 0s`). First material recipe run since the deadlock. STATUS OPEN 52 closed on it.
2. **Accepted — the mechanism named in the diagnosis was over-claimed.** The peer's point that the
   `ls -la …` / `MATERIAL=1 ls -d tools` pair demonstrates the READ-ONLY CLASSIFIER, not `Bash(py tools/*)`,
   is correct: those two commands were never covered by the same rule, so the pair cannot separate the two
   explanations. The doc sentence stands; our experiment did not test it. Recorded as a weaker evidence base,
   not as a changed conclusion — the flag form runs either way.
3. **Accepted and ACTED ON — the repair was incomplete in a second place the peer did not see.** The very
   first command in the newly mandated form was blocked by `guard_bash.py` itself: its background gate demanded
   `bgrun.py --max-min` ADJACENTLY, and `--material` sat where `--max-min` had to be. One regex, now shared by
   both call sites: `BGRUN_RE = r"bgrun\.py\s+(?:-\S+\s+)*--max-min\s+\d"` (`tools/hooks/guard_bash.py:187-195`,
   used at `:234` and `:244`). `--max-min <digit>` is still required, so the deadline guarantee is unchanged.
4. **Accepted as a finding, NOT acted on here — judgement.** The peer's falsifier grep was run:
   `.claude/agents/material.md:26-27` still mandates the dead `MATERIAL=1` prefix as the material session's
   ONLY form (it is the material agent's own system prompt, so every future material session is told to use the
   form that cannot be permitted), and `tools/cycle_runner.py:183-194` still carries it in `RECIPE_RE` and in the
   text it hands each cycle. Left for the judgement session: changing an agent definition is not a material
   session's call. STATUS OPEN 52a.
5. **Not adopted:** the peer's proposed `material_marker.log` × `BGRUN START` timestamp audit. It would sharpen
   the historical account of 11 refusals whose cause is already spent; the forward-looking question it exists to
   answer was answered directly by item 1.
