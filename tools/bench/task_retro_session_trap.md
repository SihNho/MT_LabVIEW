# FAILED PREDICTION — attack this framing

CONTEXT. This project is a LabVIEW refactor run as automated "cycles". One cycle = one fresh judgement session
spawned by `tools/cycle_runner.py`. That session delegates all material work to sub-agents (`subagent_type`
`material` / `log-reader`) and ends its cycle by running `py tools/retrospective.py --cycle N`.

PREDICTION (cycle 29, 2026-09-18). The previous cycle (28) exited without running its retrospective — there is no
`archive/peer/*retrospective-cycle2[78]*` file — so `tools/hooks/guard_cycle.py` would refuse this cycle's recipe
build ("the previous cycle's logs have no newer retrospective"). I therefore launched, as the FIRST action of
cycle 29:

    py tools/bgrun.py --max-min 20 --log tools/bench/retro.log -- py tools/retrospective.py --cycle 28

expecting it to (a) pay cycle 28's debt and (b) discharge `guard_cycle` for cycle 29's own build.

OBSERVATION. The cycle's FIRST material dispatch (Agent, `subagent_type=material`) was refused by
`tools/hooks/guard_session.py`: "THIS SESSION'S CYCLE IS CLOSED BY ITS RETROSPECTIVE ... (dispatches=0,
retro_done=true)". Cycle 29 can no longer delegate any material work, so its planned deliverable (D0 — an
unattended harness driver that runs a copy of the instrument VI with nobody present) cannot be built this session.

MECHANISM AS I READ IT. `tools/hooks/guard_bash.py` sees the retrospective command and calls
`guard_session.mark_retro_done(session_id)`; `guard_session.main()` then refuses every Agent dispatch whose
`subagent_type` is in `{material, log-reader}` while `retro_done` is true (`tools/hooks/guard_session.py:80-116`).
Nothing on that path looks at WHICH cycle the retrospective was for.

MY DIAGNOSIS — refute it. The trigger is an OVER-TRIGGER. The gate's stated purpose (its own docstring, lines
13-15) is "a retrospective reviews a cycle; work done after it belongs to a cycle nobody reviewed" — i.e. it means
THIS session's own closing retrospective. A retrospective run to pay a PREVIOUS cycle's debt reviews a cycle that
is already over and says nothing about this session's work, so marking the session closed is a false positive of
the same class as the `audit_cycle` cost-window bug repaired in cycle 28.

MY PROPOSED REMEDY — refute this too. Make the mark conditional: record `retro_done` only when the retrospective's
`--cycle N` argument is this session's own cycle, and otherwise record something like `retro_other_cycle` that does
not close the session. If the hook cannot know its own cycle number, the opposite remedy: leave the gate alone and
change the RULE — a judgement session may never run another cycle's retrospective, and an owed retrospective is
paid by `tools/cycle_runner.py` before it spawns the next session.

ALREADY RULED OUT — do not propose these:
1. Editing `tools/bench/session_<id>.json`, or any OFF switch, to get past the gate. This project's rules forbid
   routing around a gate; "CYCLE_GUARD_OFF is never the answer".
2. Doing the material work inside the judgement session instead — a counted violation here
   (`judgement-in-material`).
3. Re-dispatching the same work under a `subagent_type` the gate does not count (e.g. `general-purpose`) — gate
   laundering.

QUESTIONS:
1. What is the strongest reason my over-trigger diagnosis is WRONG — the case that the gate fired exactly as
   designed and the whole mistake was mine (a judgement session must not pay another cycle's debt mid-cycle)?
2. What hole does each remedy open? Specifically: with a `--cycle N` check, can a session evade its own close by
   passing a different N, and how much does that matter given the runner independently re-reads STATUS.md?
3. What is the cheapest discriminating test that separates "over-trigger in the hook" from "correct trigger, wrong
   action by the session"?
4. Independent of both: what SHOULD have been done at the start of cycle 29, given that cycle 28 genuinely left its
   retrospective unrun and `guard_cycle` would have blocked the build?
