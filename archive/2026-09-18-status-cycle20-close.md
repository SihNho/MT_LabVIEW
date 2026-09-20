---
type: archive
status: archived
date: 2026-09-18
tags: [status, cycle20, close, guard-cycle, fstunnel-reader, retrospective-window]
---

# CYCLE 20 — the close, relocated from STATUS (rule 4; STATUS had reached 140 lines)

Written 2026-09-18 ~04:0x by the cycle-20 judgement session. STATUS keeps the STOP, the two-line summary and the
NEXT; everything below is the detail behind them.

## 1. Step 1 — `guard_cycle.premature_build` now enforces CLAUDE.md:449(b) for the first time

MEASURED: `:379`'s `if not newer:` inverted condition (b). The old shape reached the `FIXED:` citation check
**only when the recipe was already newer than the review**, so the branch that is supposed to reject a stale fix
could never fire — condition (b) had never enforced on any build.

DECIDED and built: a new helper `fixed_claim()` (`tools/hooks/guard_cycle.py:157-199`) reads CLAUDE.md:449
(a)+(b)+(c) FIRST, before the mtime rule; `premature_build` restructured at `:431-467`. A release that claims this
recipe but fails (b) now REFUSES with the reason printed.

MEASURED outcome — `tools/bench/selftest_guard_cycle_fixed.log`, **the first time this log has ever existed**:

- `T1 PASS expected=ALLOWED got=ALLOWED` (edited after the review + a valid `FIXED:` cite)
- `T2 / T3 / T5 PASS expected=REFUSED got=REFUSED` (no cite · no review at all · cite to a nonexistent path)
- `T4 PASS` (`FIXED:` above the `## What was done with it` heading) and `T6 PASS expected=REFUSED got=REFUSED`
  (cite to a path changed BEFORE the review) — T4 and T6 now refuse **through the new branch**
- Negative proof (Pre-decided 3), `:10-29`: `B1 … expected=REFUSED got=REFUSED -> PASS`, gate text verbatim —
  `why it failed : (b) tools/recipes/r.py last changed 2026-09-17 09:50, which is NOT after the review
  (frontmatter date+time 2026-09-17 10:00) - a fix must post-date the finding it answers`; `B2 … expected=ALLOWED
  got=ALLOWED -> PASS`.
- Regression `tools/bench/selftest_guard_cycle_rerun.log` 4/4 — C4 ("review newer than the recipe → ALLOWED")
  still passes, so the no-claim path is unchanged.
- Grep: nothing depended on the old inverted behaviour. Only `guard_cycle.py:496` (`main`) calls it;
  `tools/bench/cycle18_stopgate_driver.py:110-112` scrapes a line that is still printed; `stop_record.py:257`
  uses `released_slugs`, signature untouched.

Note on the disputed history: the archived "6/6" (`archive/2026-09-17-status-d1-phase-full-narrative.md:254-256`)
records each test's *expected* verdict in prose, and no `selftest_guard_cycle_fixed.log` existed before today.
Absence of a log is not proof T6 never passed; what is proven is that it failed now. Treated as a first
enforcement, not a repair — `docs/cycle20-plan.md:30`.

## 2. Step 2 — the UID-addressed tunnel reader: written, reviewed, released, ALLOW, and never run

MEASURED first, because getting it wrong would have invalidated the run (`tools/bench/diag_uid_identity.log:20-34`):
**a UID names no VI here — the uid space is SHARED.** `28343` is a `LoopTunnel` in the V6 copy *and* in the
3StateClamping ORIGINAL; `43605` is a `FlatSequenceOuterTunnel` in both; `44036` is a `SubVI` in both. What is
keyed to the V6 copy are the CACHES: `main_vi_nodeterms.json`'s own `vi` field (`:36`) and
`d1_step0_census.json`'s `md5 2a78e17c…` (`:38`). The two VIs differ where STATUS said: ORIGINAL **97** SubVIs vs
V6 **98**, 1898 vs 1902 wires, 170 diagrams each — 97 is the motor census's own count.

Prior-art verdict **not `novel`**, 4 findings (`archive/peer/2026-09-18-priorart-fstunnel-reader.md:300-303`),
**all four ACCEPTED by judgement** and all four fixed before any release line was written:

| finding | what it said | what was changed |
|---|---|---|
| `contradicted` | the op cast FSOT only, while `docs/cycle20-plan.md:39` and §A.1 both say `FlatSequence*Tunnel`; **14 of the 18** measured non-node crossings are FSIT (FSIT 518 vs FSOT 58), and `1C3A9000` REFUSED 1077 on the outer class proves FSOT cannot reach them | FSIT cast + op added, `:137` |
| `unread-evidence` | the accepted dual review's **T2 face test** (read `3195B800` *and* `3195B801`, match the arrived terminal) was absent, and L4 scored the falsifier *"the hop does not advance"* as CROSSED | T2 face test via both faces' `Terminal.Connected Wire` 634A000, `:739` |
| `helper-exists` | `tools/bench/diag_tunnelsource_onehop.py:198-233` already IS the hop loop, **with** the "does not advance" refusal; L4 rebuilt it without that guard | L4 calls `resolve()`, `:617` |
| `already-measured` | `Owner→cast→UID` is measured to return uid 0 + error 1055 at a FlatSequenceFrame (`diag_ownerchain_hop.log:7`); L1 read `ownercls` only, so the silent mode passed | L1 gates `owner_uid` + `errs`, `:657` |

Judgement's reasoning for accepting all four (recorded so it is not re-argued): finding 1 was not a scope
question — the FSOT-only recipe **narrowed the plan**, which specifies the inner tunnel's `LeftTerm`/`RightTerm`
explicitly, and with 14 of 18 crossings being FSIT an FSOT-only reader could not satisfy done-when 3 at all.
Findings 2–4 are each a gate that passes on a silent failure, which Pre-decided 3 forbids outright.

Release VALIDATES, verbatim (`tools/bench/c20_release_probe.log`):
`RELEASED SLUGS: 4 -> ['already-measured','contradicted','helper-exists','unread-evidence']` ·
`REJECTED : 0 -> []` · `fixed_claim(recipe): (True, True, '')` · `_released : True`. Launch gate
(`tools/stop_record.py check`): **`ALLOW`**.

⚠️ **The recipe never ran.** Verification level: **none** — not structural, not functional. No live read, no hop
count, no bad-input refusal, no scratch VI, LabVIEW never started for it.

Disclosure from the material session, left standing by judgement: §A.1 is implemented as **two sibling op VIs
built by the one recipe** (`OpFsTunnelTerm_v0` FSOT + `OpFsInnerTunnelTerm_v0` FSIT), because a second
`To More Specific Class` in one VI has no creator and would need `copy_by_index`. A reader `read_any()` presents
one interface over both classes.

## 3. What blocked the launch — and why judgement did not answer it

`guard_cycle` refused twice:

1. `BLOCKED … every cycle ends with a RETROSPECTIVE review` — **17 build logs since the cycle-17 retrospective
   (budget 10)**, with no retrospective for cycle 18 or cycle 19. The material session ran cycle 19's (the hook's
   own remedy) → `archive/peer/2026-09-18-retrospective-cycle19.md`: `wrong-ordering | loss_min=66 |
   loss_usd=8.1295` and `device-failed | loss_min=15 | loss_usd=8.9402475` (the latter already answered
   2026-09-18 00:53, not blocking).
2. `BLOCKED … a retrospective violation has reached its threshold. DUE wrong-ordering: 8 occurrences
   (threshold 3)`. `py tools/violations.py` confirms `wrong-ordering 8 … <== DUE, no decision on file`.

Rounds 1–2 were both `DECISION: no-device` (`docs/violation-decisions.md:45-53`, `:165-178`). Round 2's reasoning
is the decisive text: it grounds `no-device` in CLAUDE.md's own rule that *"an outcome-layer violation is NOT
answered by building a device — answering goal drift with another tool is how the drift happened"*, and closes
**"On a further repeat, escalate to a re-plan with the user rather than to a sixth gate."**

So at round 3 neither branch belongs to Claude: `DECISION: device` contradicts CLAUDE.md:437-440 and round 2's own
pre-commitment; a third self-written `DECISION: no-device` would be Claude waiving its own threshold for the third
time, which CLAUDE.md:335 reserves to the user (*"Only the user may lower that threshold"*). The block was
therefore **left unwritten and the gate left armed**, and the runner stopped — which is also P1's declared exit
condition ("P1 ENDS when the only work left needs a real motor or the user").

## 4. MEASURED — the OPEN 42 audit diagnosis was REFUTED by both dual arms

The earlier explanation (A2/A3 are *self-referential*) is wrong. `tools/audit_cycle.py:186-197` reads an env var
`BGRUN_LOG` that `tools/bgrun.py` **never writes** (grep, 0 hits) — the audit's own-log exemption is **unreachable
code**. Both arms ANSWERED (`archive/peer/2026-09-18-c20-audit-a1-motorgate-{codex,opus}.md`; codex 112 s, opus
376 s) and both REFUTED the session's A1 explanation. They also refused the proposed remedy of registering
`motor_gate` in `logclass.py`: `tools/bench/motor_gate.log:52-71` carries live `SENT rc=0` records, so excluding
it by filename would **hide execution evidence**. The real remedy is a design change (runner-log identity for
audits + content-classifying `motor_gate.log`), which is why it was not taken mid-cycle.

The opus arm's own "confirmatory probe" was never run — no `tools/bench/probe_bgrun_env.log` exists.

## 5. The failed prediction this session made, and the review it still owes

PREDICTED: `py tools/retrospective.py --cycle 18` would reconstruct CYCLE 18's record, to fill the hole in
`violations.py`'s counts before handing the user an "8 occurrences" number.

OBSERVED, from the run's own first lines (`tools/bench/retro_cycle18.log`):
`window 2026-09-18 03:42:17 .. 03:46:50 (5 min); 0 build logs, 2 machinery logs, 11 devices`.

HYPOTHESIS formed under pressure, and therefore **UNCONFIRMED**: the review window is *since the previous
retrospective*, and `--cycle N` is only a LABEL — so the gate-forced cycle-19 retrospective at 03:42 consumed
cycle 20's window, cycle 20 has no retrospective of its own, and cycle 18's is not reconstructible by this tool.

ACTION TAKEN: the run was KILLED before it wrote any archive file, so that a document labelled "cycle 18" and
describing an empty 5-minute window would not enter the record the user is about to re-plan against. Logged here
as a **NON-RESULT** per CLAUDE.md's usage-limit/kill rule: which run (`retrospective.py --cycle 18`), when
(2026-09-18 03:46-03:47), why (mislabelled window; would have polluted `violations.py`'s evidence base). Partial
output remains in `tools/bench/retro_cycle18.log`, with no `BGRUN END` line.

⚠️ **The mandatory `-Dual` failed-prediction review (CLAUDE.md:479-497, :554) was NOT dispatched** — the dispatch
was refused by `tools/hooks/guard_session.py` (`dispatches=3, retro_done=true`), because invoking
`retrospective.py` at all had already marked this session's cycle closed. Per the session's own standing orders
that refusal is the end of the cycle and not something to route around, so the review is carried to NEXT as
STATUS OPEN 49 and must be the first dispatch of the next session.

Consequence the user needs when re-planning: **`violations.py`'s "8 occurrences" of `wrong-ordering` is counted
over the retrospectives that EXIST, with cycle 18 absent.** The direction of that bias is one-way — a missing
cycle can only make the true count higher, never lower.
