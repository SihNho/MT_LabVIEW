# priorart-priorart-c74-m3a2

- **agent:** claude
- **role:** priorart
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $6.3017  in 56 / out 37357 / cache-create 271229 / cache-read 5310501  (502s, 41 turn(s))
- **date:** 2026-09-22 01:51:23
- **outcome:** ANSWERED (506s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

PRIOR-ART REVIEW (trigger: cycle-start).

You are checking ONE thing: has this already been done here? Do not review the plan's merits -
other reviews do that. Answer in two parts, naming a FILE and LINE for every finding. A finding without a citation
cannot be acted on, because the only way this review is released is by someone opening your citation and showing in
writing that it does not cover their case.

PART A - THE DIRECTION (this is the part that matters most)
 A1 SETTLED ALREADY. Has this direction, or its central question, already been decided or answered in STATUS.md,
    docs/ or archive/? Quote the decision and its date.
 A2 REFUTED ALREADY. Has this direction already been tried, abandoned, or argued against - in an archived peer
    review, a retrospective, or a superseded plan section? Say what killed it and whether that still applies.
 A3 CONTRADICTED. Does any fact the plan cites conflict with something else in these files? Quote BOTH sides. A
    summary line that contradicts its own section 40 lines earlier counts, and has happened here.
 A4 UNREAD EVIDENCE. Which existing document should obviously have been consulted for this direction and clearly
    was not? Name it.

PART B - THE ARTIFACT, if the plan builds or changes one
 B1 ALREADY BUILT. Does an op, recipe, helper or VI already do this, possibly under another name? Check
    tools/gscript.py's functions, tools/recipes/, docs/toolkit-capabilities.md and the claudeDev VI names.
 B2 ALREADY FAILED. Has this exact build been attempted and failed? What did the record say was the cause, and
    does the new plan address that cause or repeat it?
 B3 HELPER EXISTS. Is the plan hand-rolling something the toolkit already provides - indexing, identification,
    wiring, saving, censusing? Name the call.
 B4 ALREADY MEASURED. Has the question this artifact would answer already been measured and written down?

End with machine-readable lines, one per finding:
  PRIOR-ART: settled-already | refuted-already | contradicted | unread-evidence
  PRIOR-ART: already-built | already-failed | helper-exists | already-measured
  PRIOR-ART: novel
`novel` only if none apply. Do not invent slugs.

THESE VERDICTS STOP THE WORK. Any slug other than `novel` blocks the next build until someone opens your citation
and refutes it in writing. So be precise about what your citation actually covers: an over-broad match costs real
work, and a missed one costs a whole build cycle.

=== WHAT IS UNDER REVIEW ===
# THE PLAN UNDER REVIEW ??stage M3a-2, `tools/recipes/build_d1_m3a2.py` (WRITTEN, NOT YET RUN)

The recipe is on disk at `tools/recipes/build_d1_m3a2.py` and has passed the pinned static gate
(`py tools/bench/c60c_astcheck.py <file> --route owner`, 11 pass / 0 fail,
`tools/bench/c74_astcheck_m3a2.log`). It has NOT been launched: this review decides whether it should be.
Read the file itself ??its header docstring states the whole contract.

## What the stage does

Loop `#23032` (the NEW While loop, created in stage S2 and given two shift registers by stage M3a-1) has two
registers whose LEFT OUTER terminals are BARE, i.e. the registers are uninitialised. M3a-2 wires each LEFT
OUTER to the SAME source that initialises the ORIGINAL loop's corresponding register, so both loops are fed
identically. TWO rows, not four (`docs/cycle27-plan.md` Pre-decided 91).

| row | source | sink | the original sink on the same net |
|---|---|---|---|
| A VISA | the ONE source terminal of wire **4185** = `FlatSequenceInnerTunnel` **#4194** | LEFT register **#23880** OUTER, named `'VISA out'` | **#4344** OUTER |
| B POS | the ONE source terminal of wire **3968** = `FlatSequenceInnerTunnel` **#3974** | LEFT register **#23909** OUTER, named `'position [internal units]'` | **#4274** OUTER |

Both are SAME-DIAGRAM rows on `Diagram #686` (both loop borders ??`#637` at Nodes[4], `#23032` at Nodes[21] ??
and all four wires are owned by `#686` under strict uid echo).

## Where every number comes from

`tools/bench/diag_c73_m3a2_rows.{py,log,json}` ??a measurement-only diagnostic, `BGRUN END rc=0 after 144s`,
5 hygiene gates pass / 0 fail, nothing mutated, the input artefact re-read byte-unchanged, every uid uid-echoed
and every `OpWireSource_v5` walk clean of Pre-decided 85 violations. The recipe RE-MEASURES every one of them on
the live target before use.

## The mechanism, and why no new tool is built

- Writer: `connect_from_wire` = `OpConnectFromWire_v0.vi` (BUILT + SAVED 2026-09-17,
  `docs/toolkit-capabilities.md:70`), which takes its SOURCE as (WIRE uid, terminal index on that wire) and its
  SINK as `Diagram[d].Nodes[n].Terminals[t]`. It wrote M3a-1's t1 row and its sixth row.
- `wire_sr('LeftOutNode'/'LeftOutCtl')` is deliberately NOT used: both sources are `FlatSequenceInnerTunnel`s
  owned by `FlatSequence #681` and a tunnel is not a `Nodes[]` member, so neither variant can address them
  (Pre-decided 93).
- Reader: `wire_source_owner` = `OpWireSource_v5`, repaired 2026-09-22 (indicators scrubbed per call, all 8 op
  error outs read, the op's uid echo required; acceptance `tools/bench/diag_c68_echo_accept.log` 8/0).
- Helpers `find_node` / `terms_at` / `term_state` / `node_view` / `node_census` / `new_nodes` / `delete_by_uid`
  are IMPORTED from `tools/recipes/build_d1_m3a1.py`, not rewritten. `census_and_purge` is deliberately not
  imported (it writes M3a-1's own JSON); its logic is re-stated as `purge_junk`.
- NOTHING NEW IS BUILT ??no op VI, no gscript verb, no checker, no process device (user, 2026-09-18 08:53).

## The acceptance test, per row (Pre-decided 92 + 77), run TWICE ??after the write and after the junk purge

1. the wire carried by the NEW SINK terminal has **exactly ONE** source terminal **of any owner class** ??
   every class counted BEFORE any filter;
2. that one terminal's owner is the predicted source (#4194 / #3974);
3. the ORIGINAL sink (#4344 / #4274) is **still** a terminal of that net ??the rule-1a invariant: the row
   BRANCHES the initial-value net, it does not steal it;
4. the walk has ZERO Pre-decided 85 violations.

A row that STOPS before its write (empty source walk, ambiguous source, an owner that is not the predicted one,
an unresolvable or non-unique sink, a LEFT OUTER that is already wired) wires NOTHING, substitutes NOTHING
(Pre-decided 68) ??and its acceptance gate FAILS, so the run cannot exit 0 with a row that never happened.

## What is measured and never gated

- Pre-decided 95: the bare-terminal census of ALL 14 registers on the OLD loop `#637`, before and after, plus
  `ExecState` at both ends. M3a-2 is NOT required to reach `ExecState 1` and is not judged on it.
- Pre-decided 94: the TYPE CHECK. `Wire.Is Broken?` is read ONLY in a separate ordered pass after both rows ??
  an idempotent re-connect whose `wire_delta` is expected to be 0 ??never in the pass that made the connection.
  The op's own internal `Is Broken?` readback from the write pass is recorded verbatim as a FACT and is
  explicitly NOT the type check.
- Pre-decided 91: M3a-3 is NAMED with its uids and NOT wired here ??`#4256` OUTER ??wire 4859 ??`Global #7202`
  t0, and `#4334` OUTER ??wire 7506 ??`FlatSequenceInnerTunnel #7468` stay exactly as they are, so leaving the
  two new RIGHT OUTER terminals bare drops no consumer (a bare SOURCE is legal LabVIEW, Pre-decided 69).

## Files and hygiene

Input: `claudeDev\D1_s3b_m3a_BROKEN_20260922_005732.vi` md5 `6b3c1f3c4ba80f1fa7411a55f0218bea` ??copied once
with `shutil.copy2`, never opened over COM, never edited, never run; its md5 is a gate at both ends. Output:
`claudeDev\D1_s3b_m3a2_<stamp>.vi`, saved with `g.save(target, allow_broken=True)` (Pre-decided 88/96), with the
after-confirmation being the file's own size and md5 read back off disk and required to differ from the input.
The four STATUS md5 pins (ORIGINAL, S1, S2, the bed) and the two tool pins (`tools/gscript.py`,
`tools/bench/c60c_astcheck.py`) are gates at both ends.

## Already ruled out ??do not re-raise these as new

- "The source must be a `Nodes[]` entry" ??WITHDRAWN by Pre-decided 68; `OpConnectFromWire_v0` addresses the WIRE.
- "Use `wire_sr('LeftOutNode')`" ??answered in Pre-decided 93 and above.
- "Gate on `ExecState 1`" ??Pre-decided 89/95: the artefact is broken by design at this stage.
- "Use the border exemption of Pre-decided 66" ??it does not apply; these are same-diagram rows, measured.
- "Build a device for this" ??the user suspended device-building on 2026-09-18 08:53.

## THE QUESTION FOR YOU

Has any part of this already been analysed, built, measured or REFUTED in this project's own files ??and is
there anything in the corpus that says this recipe will fail, or that a cheaper route already exists? Cite
`file:line`. The one finding that matters most is the one that would waste the run.


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-20
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here. ?좑툘 **ONE SESSION AT A TIME** ??re-read `CLAUDE.md` + this. Narrative ??**`archive/2026-09-19-status-cycle47-relocate.md` (latest ??T2's block diff and what it closes, the readable-ORIGINAL correction, the five killed retrospectives)** + `archive/2026-09-19-status-cycle39-judgement.md` + `archive/2026-09-18-status-cycle34-n1.md` + `??cycle23-close.md` + the `archive/2026-09-1[678]-status-*.md` set.
??**DELIVERED:** D0 (cycle 31) 쨌 N1 ACCEPTED (cycle 34) 쨌 D1 **S1** `claudeDev\D1_s1_copy.vi` md5 `3e3d23ce?? 쨌 D1 **S2** `claudeDev\D1_s2_loops.vi` md5 `6ff19497?? 쨌 D1 **S3a** both halves (`??boolcarrier_b3_20260921_010034.vi` md5 `dc14dd00??, `ExecState` 1, `Is Broken?` False) 쨌 D1 **S3b rows 1 and 2**. ?뵷 **THE CURRENT BED IS `claudeDev\D1_s3b_row2_20260921_160311.vi`, md5 `26c54ff7??** ??every next stage starts FROM THAT FILE. ??**M3a-1 DELIVERED (cycle-63 firefighter, run 5, 2026-09-22 01:0x): `claudeDev\D1_s3b_m3a_BROKEN_20260922_005732.vi` md5 `6b3c1f3c??, 22 gates pass / 0 fail, bytes DIFFER from the bed.** The artefact is BROKEN BY DESIGN (uninitialised SRs ??initial values are stage M3a-2) and is NEVER RUN (34(f)). Two root causes were repaired and MEASURED on the way: the identity reader `wire_source_owner` (history-echo, now error-checked + uid-echo-verified, acceptance `diag_c68_echo_accept.log` 8/0) and `gscript._lv_gui` (unquoted spaced args = PowerShell parse error, so NO Evidence-carrying GUI action had EVER dispatched ??`archive/peer/2026-09-22-c72-guisave-foreground-r2.md`). The bed is byte-unchanged and all four md5 pins hold. S3-as-37(g)-defined is WITHDRAWN (cycle 53). **Read `docs/cycle27-plan.md` Pre-decided 84??0 BEFORE 78??3 (78/80/81/82 are WITHDRAWN)**, then 46, 42, 43, 44. Full chronicle VERBATIM ??`archive/2026-09-21-status-cycle67-locknotes.md` 짠2; banner VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠3; facts `??cycle31-d0-delivered.md` 짠1?벬? (read **짠4** before the first D1 click).
?넅 **USER RULE 17:5x = `docs/cycle27-plan.md` Pre-decided 9 ??EVERY GUI action is capture ??locate ??act ??capture ??confirm; derived or remembered coordinates are NEVER clicked blind.** It turned v4's 13/3 into v5's 39/1.


## START HERE
1. **Cycle plan = `docs/cycle27-plan.md`** (cycle20/21 plans `superseded`; motor plan `docs/motor-limit-assurance-plan.md` **짠A.1 + "P2 live findings"**; master `docs/pre-rig-master-plan.md`; decisions `docs/decisions.md`; D1 `docs/d1-route-b-plan.md`, paused).
2. ?뵶 **NEVER patch a file with a `py - <<'EOF'` heredoc** ??one truncated **this file to 0 bytes** on 2026-09-17.
3. ?좑툘 `peer.ps1` only as `powershell -Command "& 'tools/peer.ps1' ??-TaskFile <f>"`, `-TimeoutSec >= 780`. ?넅 **2026-09-18 (user, TRIAL): codex's roles ??claude roles** ??failed prediction = `-Agent claude -Role hypothesis` SINGLE arm (`-Dual` only for a second opinion on our own tools); `-Kind fact`/`-Kind prose` with no `-Agent` ??fable/low thin; `outcome_review.py` ??fable/medium thin. Check routing free with `-DryRun`.
4. Six more operating hints (prior-art log naming 쨌 front panel open for edits 쨌 `guard_cycle`'s `FIXED:` release 쨌 `py_compile` tripping BUILD_RE 쨌 짠11u unsound 쨌 짠10 not authorised): **`archive/2026-09-18-status-cycle1-census.md` 짠1**. ?좑툘 `BUILD_RE` also fires on a plain `cp a.py tools/recipes/b.py` ??quote both paths (cycle23-close 짠3).

## LabVIEW execution lock

```yaml
labview-lock:
  status: released
  owner:
  since: 2026-09-22 02:1x
  purpose: none - cycle-64 MATERIAL dispatch 2 TOUCHES NO LabVIEW. It writes `tools/recipes/build_d1_m3a2.py` (NOT RUN - the prior-art verdict must be disposed by judgement first, and guard_cycle enforces it), repairs `tools/bench/c60c_astcheck.py` gate 3 per Pre-decided 98(5), runs the PINNED astcheck (`--route owner`) on the new recipe, and dispatches the prior-art review. Gate-3 repair VERIFIED before/after: the old matcher saw 0 of 3 evasions (`allow_broken=1`, `=flag`, `**{"allow_broken": True}`), the widened one sees all 3 and FAILS them, while the authorised `g.save(work, allow_broken=True)` still PASSES. PREVIOUS PURPOSE, unchanged and still true - cycle-64 MATERIAL dispatch 1 IS DONE. `tools/bench/diag_c73_m3a2_rows.py` (MEASUREMENT ONLY, no mutation, no new op) ran BGRUN END rc=0 after 144s, 5 hygiene gates pass / 0 fail, log tools/bench/diag_c73_m3a2_rows.log, JSON ...rows.json. LabVIEW was restarted first (handles 34,642 -> 33,989; 33,995 at exit); a unique scratch copy C73SCRATCH_20260922_012152.vi was read and DELETED in the same run; the M3a-1 artefact was never opened and re-reads md5 6b3c1f3c... unchanged; all four pins hold. MEASURED: the M3a-2 initial-value feeds are FlatSequenceInnerTunnel #4194 (VISA/'Outgoing Handle', wire 4185) and #3974 (POS, wire 3968), both owned by FlatSequence #681, both wires on Diagram #686 - and BOTH loops' borders (#637 Nodes[4], #23032 Nodes[21]) are on #686, so M3a-2's rows are SAME-DIAGRAM rows, not border crossings. The artefact reads ExecState 0 with ZERO bare terminals on the seven moved nodes; the only bare terminals are the four register OUTER terminals. PREVIOUS PURPOSE, unchanged and still true - CYCLE 63 (FIREFIGHTER on build_d1_m3a1.py) IS CLOSED and THE BLOCK IS CLEARED. Run 5 ended BGRUN END rc=0, 22 pass / 0 fail, artefact D1_s3b_m3a_BROKEN_20260922_005732.vi md5 6b3c1f3c... on disk (bytes differ from the bed; BROKEN BY DESIGN, never run). Three measured repairs this cycle: (1) wire_source_owner now scrubs indicators, reads all 8 op error outs, and requires the op's uid echo (UID 3) == queried uid - acceptance diag_c68_echo_accept.log, ghost reads null after live reads both times, 8/0, rc=0; (2) gscript._lv_gui QUOTES its args - they were joined unquoted into powershell -Command, so every -Evidence-carrying action (all spaced/parenthesized) was a PARSE ERROR and NO state-changing GUI action from gscript ever dispatched; confirmed by the c72 review's own discriminating test, then fixed and re-tested DISPATCHED OK (archive/peer/2026-09-22-c72-guisave-foreground-r2.md, ANSWERED, disposed - it REFUTED my foreground/home-window diagnosis by pointing at gui_actions.log's silence); (3) gui_save now clickprobe-verifies the measured foreground before Ctrl+E/Ctrl+S and raises with the OBSERVED per-candidate record. All pins held, originals untouched. LabVIEW left running after run 5 - restart before the next batch if handles are high
```
?뵷 **ALL 50 HISTORICAL LOCK-BLOCK ENTRIES (cycles 48??7: 48 `owner_*`/`lock_*` keys, the superseded `status:` line, and the `motor:` key) RELOCATED VERBATIM (rule 4) ??`archive/2026-09-21-status-cycle67-locknotes.md` 짠1** ??that file also carries the three older `lock_relocated_*` pointers (into `??cycle5556-relocate.md`, `??cycle54-relocate.md`, `??cycle5153-relocate.md`, `??cycle49-relocate.md`, `??cycle48-lockkeys.md`). **Motor state, unchanged and still true:** limits LEFT ON since 2026-09-18 15:37 (PI TMN 0 / TMX 39 in RAM, ASI SL/SU 짹2 mm), ports closed.
**Never assume an instance exited**: `tasklist | grep -i labview`. Fresh ??1,500 handles; unique scratch name/run.

## HARDWARE ??permission follows the RIG STATE. Current: **議곕┰ / ASSEMBLED** (machine key `rig-state:` below)
遺꾪빐 = motors ??ASI ??camera ??쨌 **議곕┰ ??WE ARE HERE** = camera ?? motors/ASI ONLY through `tools/motor_gate.py` inside the envelope 쨌 ?ㅽ뿕以?= ?????? ?좑툘 ASI carve-out **RETIRED** (rule 1b); **only the user announces a state change**.
Rotor counter **0** 쨌 magnet full travel 쨌 camera 1280횞1024, offsets 0, 90.0009 Hz, never write `BinningHorizontal`; **a session open RESETS ROI *and* exposure** ??the acquisition loop applies `tools/bench/camera_contract.py`. **No beads on the rig.**
?넅 **SAFE MOTION ENVELOPE = THE CONTROLLER LIMITS + the gate's command-class denies** (user, 2026-09-18 15:2x at the
rig). PI `SPA 1 0x15/0x30` ??TMN 0 / TMX 39 (RAM, **never WPA**) 쨌 ASI `SL/SU` absolute mm X ??.8475??.1525, Y ??.7744?╈닋0.7744 (persistent, **never SS Z**),
written+verified by `py tools/motor_gate.py --session start|end` from the user-editable `tools/bench/motor_limits.json`; `--execute` refuses without `tools/bench/motor_session.json` **and** a fresh matching readback.
The gate still refuses ?ㅽ뿕以? every ASI home/zero/save, PI GOH/FRF/DFH/RON/POS/SPA/WPA and all rotor motion (self-test `selftest_motor_gate2.py` 74/74).
??The 15:37 run (8/10, L4 a FALSE PASS) is SUPERSEDED by the 16:0x retest ??`??cycle29-retro-trap.md` 짠7. Limits LEFT ON (PI TMN 0 / TMX 39 **in RAM**, ASI SL/SU persistent); **an 18:13 D0 run then moved the magnet to 30 mm and they held**.
rig-state: 議곕┰   <!-- set 2026-09-17 23:0x on the user's words ("?ㅽ뿕 1李⑤줈 ?앸궗?붾뜲, 由ш렇???좎??섎뒗 以? + "議곕┰ ?곹깭?먯꽌????踰붿쐞 ?덉씠硫?紐⑦꽣 ?덉슜??) 쨌 the gate's ONE machine-readable key, parsed by motor_gate.rig_state(); ONLY the user's announcement may set it to 遺꾪빐 / 議곕┰ / ?ㅽ뿕以? Keep it at the start of the line, unquoted. -->

## Where things stand ??the three ??lines VERBATIM in `archive/2026-09-18-status-cycle36-relocate.md` 짠4
??tunnel ops BUILT + FUNCTIONALLY VERIFIED (38/38, ?좑툘 **do NOT re-run the recipe, run 1 is the record**) 쨌 ??the "ZERO runnable experimental VIs" gap is BROKEN ??`tools/bench/drive_original_copy_v5.py` drives a plain copy of the original unattended end to end, twice 쨌 ??N1 accepted ??the GPU kernel is cleared for D1. **Order is D0 ??D1 ??D2** (`docs/cycle27-plan.md` Pre-decided 1). Prose VERBATIM ??`archive/2026-09-21-status-cycle67-locknotes.md` 짠3; earlier ??`archive/2026-09-18-status-cycle22-close.md` 짠2.

## OPEN ??**items 1??0 VERBATIM in `archive/2026-09-17-status-runner-build.md` 짠2**; the five CLOSED items (32 쨌 55 쨌 56 쨌 51/52/52a 쨌 53's mechanical half) VERBATIM in `archive/2026-09-19-status-cycle46-relocate.md` 짠5, which forwards to `??026-09-18-status-cycle36-relocate.md` 짠5?벬?. ?좑툘 Two riders survive there: 32 is NOT to be closed unilaterally (the next outcome review judges it), and `audit_cycle` C4 still understates spend (retrospective-cycle31 F4). Only the live items below.
38/39/41. ?윞 **LIVE PART ONLY: `SR_QUEUE_AUTHORISED` stays False for good; `TEMP_SINK_AUTHORISED` is True for the `Z/dZ` row only** (Pre-decided 13 + 13a), and `Z/dZ` is now MEASURED WIRED (Pre-decided 19). `VI.Get Errors` 452 NOT built and `docs/d1-route-b-plan.md` 짠10 NOT AUTHORISED. ??the stall-watchdog liveness item is CLOSED by cycle 40's repair. Full text + run-3 history ??`archive/2026-09-19-status-cycle40-close.md` 짠2.
53. ?뵶 **The JUDGEMENT half STAYS OPEN, both review arms:** `POS` only declares the present location to be a coordinate and PI's `0x15/0x30` are relative to that zero, so **nothing we can read proves the controller zero still equals the ORIGINAL physical zero** ??i.e. that 0??9 still fences the intended physical window. VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠9; dispositions `archive/peer/2026-09-18-pi-err5-unreferenced-{codex,opus}.md`.
54. ?뵶 **TWO RULES YOU MUST FOLLOW, reasoning relocated ??`archive/2026-09-19-status-cycle40-close.md` 짠3.** (a) **The retrospective is the LAST thing a session runs** ??`guard_bash.py:226-227` marks the session retro-done on ANY `retrospective.py` in command position, and `guard_session` then refuses every later dispatch; nothing clears the mark. (b) **Dispatch in the FOREGROUND and wait; when something must run in the background, HOLD THE TURN OPEN until it lands** ??a `claude -p` session cannot take results as they arrive, and ending the turn kills the child. Repair named, deliberately NOT BUILT.
42/43/46/47. ?윞 **LIVE PART ONLY** ??42 ?좑툘 undisposed reviews + `audit_cycle` A2/A3 SELF-REFERENTIAL, not fixed (?좑툘 A4 counts a whole DAY, so it charges the previous cycle's files to this one ??retrospective-cycle40 F4) 쨌 46 ?좑툘 `SetCommand_signed.vi` is on NO disk 쨌 **47 ?뵶 JUDGEMENT: the audit A1/A2/A3 remedy is NOT a `logclass` entry.** 43 and 48/48a/49/50 ??CLOSED. Full text ??`archive/2026-09-19-status-cycle40-close.md` 짠4.

## NEXT
??**THE M3a-1 BLOCK IS CLEARED ??the artefact is on disk** (`claudeDev\D1_s3b_m3a_BROKEN_20260922_005732.vi` md5 `6b3c1f3c4ba80f1fa7411a55f0218bea`, 22/0 gates, run 5, `tools/bench/build_d1_m3a1.log`). Do NOT re-run `build_d1_m3a1.py` ??run 5 is the record. The artefact is BROKEN BY DESIGN (uninitialised SRs) and NEVER RUN (34(f)).
?뵶 **NEXT CYCLE (normal, judgement Opus max), FIRST ACT ??the M3a-2 stage: initial values for the shift registers**, per `docs/cycle27-plan.md` (read Pre-decided 84??0 BEFORE 78??3, then 46, 42, 43, 44). Start FROM `D1_s3b_m3a_BROKEN_20260922_005732.vi` (rule: every stage starts from the previous stage's saved file, fresh LabVIEW instance). The bed `D1_s3b_row2_20260921_160311.vi` md5 `26c54ff7?? stays READ-ONLY as the fallback.
?뵷 **THREE TOOL REPAIRS LANDED THIS CYCLE ??do not redo, do not revert:** (1) `wire_source_owner` (`tools/recipes/build_opconnectfromwire_v0.py`) is now sound: indicators scrubbed per call, all 8 op error outs read, rows accepted only when the op's uid echo (`UID 3`) == the queried uid; acceptance `tools/bench/diag_c68_echo_accept.log` (ghost reads null after live reads, 8/0, rc=0). Pre-decided 71 is CLOSED by that measurement. (2) **`gscript._lv_gui` now QUOTES its args** ??before this, every `-Evidence`-carrying (= every state-changing) GUI action from gscript was a PowerShell PARSE ERROR that never dispatched; `archive/peer/2026-09-22-c72-guisave-foreground-r2.md` (opus max, ANSWERED, disposed) found it by `gui_actions.log`'s silence and its discriminating test confirmed it. **Any past run whose GUI step "silently did nothing" through gscript is explained by this.** (3) `gui_save` clickprobe-verifies the measured foreground before Ctrl+E/Ctrl+S and raises with the observed per-candidate record ??never an invented cause. Deferred, not declined: the `Modifications:*Bitset` dirty-reader (review 짠6.3) becomes the next build ONLY if a save fails again WITH `keys Key=^s` rows now visible in `gui_actions.log`.
?좑툘 **RUN `py tools/retrospective.py --cycle 64`** ??highest `retrospective-cycle<N>.md` plus one (Pre-decided 64). This cycle archived `retrospective-cycle63.md` (disposed; its one slug ??`inference-over-measurement`, the foreground diagnosis written before the free `gui_actions.log` grep ??post-dates the 00:22 no-device block and re-opens the question). Cost honesty: the cycle's $3.65 headline EXCLUDES a 785 s TIMEOUT opus/max dispatch (`tools/bench/peer_c72_guisave.log`) that left no COST line. Still owed by the next cycle's bookkeeping: dispose `archive/peer/2026-09-21-c71-astgate.md` and pin the astcheck invocation; if any GUI action ever "silently does nothing" again, the next build is the delivery-proof assertion (`_lv_gui` raises on non-zero exit; `gui_save` believes a keystroke only on a fresh `gui_actions.log` row).
?좑툘 Restart LabVIEW before the first batch (left running after run 5). No motor, no camera, no new process device. `inference-over-measurement` reached threshold and is answered `no-device` in `docs/violation-decisions.md` (2026-09-22 00:22, under the user's 2026-09-18 08:53 suspension).
?좑툘 **THE COMMIT IS STILL NOT MADE ??`git add`/`git commit` are REFUSED in these `claude -p` sessions** (now FOUR cycles running). Newly uncommitted this cycle: STATUS.md, `tools/gscript.py`, `tools/recipes/build_opconnectfromwire_v0.py`, `docs/violation-decisions.md`, `tools/bench/peer_task_c72_guisave.md`, `archive/peer/2026-09-22-c72-guisave-foreground-r2.md` (+ the c71 set listed last cycle). **Either the runner commits between cycles or the allow-list needs a `git` entry.**
?뵶 **STILL FOR THE USER, one point only ??the 56(j) rule-1a question**, answered in **Pre-decided 57** and not re-opened: the two-piece transport has no dataflow ordering, but 45(d)'s frame-counter edge in M4 makes a default or stale read a no-op, and the intermediate files are never run. Residual: the payload can reach the ASI command up to one frame late at a 25-frame cadence. Confirm or overturn that one point.
?뵶 **AND THE OUTCOME REVIEW'S FOURTH firing still stands for you** ??five slugs (`archive/peer/2026-09-21-outcome-review-20260921.md:153-157`); CLAUDE.md says on repetition the work stops for a re-plan with you. This cycle's answer to it is the first M3a artefact ON DISK and two load-bearing tool repairs. **Overturn by writing `STOP` at the start of a line near the top of this file.**
?뵶 **STILL FOR THE USER, one point only ??the 56(j) rule-1a question**, answered in **Pre-decided 57** and not re-opened: the two-piece transport has no dataflow ordering, but 45(d)'s frame-counter edge in M4 makes a default or stale read a no-op, and the intermediate files are never run. Residual: the payload can reach the ASI command up to one frame late at a 25-frame cadence. Confirm or overturn that one point.
?뵶 **AND THE OUTCOME REVIEW'S FOURTH firing still stands for you** ??five slugs (`goal-requirement-not-advanced` 쨌 `product-not-runnable` 쨌 `tooling-over-delivery` 쨌 `decision-starved` 쨌 `ordering-stale`, `archive/peer/2026-09-21-outcome-review-20260921.md:153-157`); CLAUDE.md says on repetition the work stops for a re-plan with you. The firefighter did not stop the runner because the reader repair is the one thing that unblocks everything downstream and is worth doing under any re-plan. **Overturn by writing `STOP` at the start of a line near the top of this file.**
**Unchanged, still the user's to overturn:** N1 accepted on the pre-bead-loss window; the bead-4 z-LUT flip excluded by the FLIP mask; the harness RECORDS all 60 front-panel controls and SETS none; `background VIs_COPY` (94 files) untouched; the two new indicators keep their inherited labels (cosmetic).
## Where to look ??`CLAUDE.md` 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 **`docs/toolkit-capabilities.md`** 쨌 **`docs/motor-call-site-census.md`** (P1) 쨌 **`docs/d1-route-b-plan.md`** = the build order 쨌 `tools/recipes/build_d1_routeb_v0.py`.


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

No prior-art blocker kills this run outright, but **this is not `novel`** — four findings, each cited to a line of our own files. The one that matters most is B2: the save-capture rider this recipe claims to satisfy was **measured to produce nothing** in the very run that made the artefact it starts from.

---

# PRIOR-ART REVIEW — stage M3a-2, `tools/recipes/build_d1_m3a2.py`

## PART A — THE DIRECTION

### A1 — SETTLED ALREADY, and settled **the way this plan proposes** (reported, no slug)

The central question — *may the initial values be a second saved stage?* — is already answered, twice, and both answers back the plan:

- `docs/cycle27-plan.md:3097-3107` (Pre-decided 91, **2026-09-22**): loop `#23032` carries exactly two registers, the four bare terminals are the whole bare list, **M3a-2 = the two LEFT ones**, and the two RIGHT ones are named as M3a-3.
- `archive/peer/2026-09-21-c67-m3a-srrows.md:254`: *"**Second half — HOLDS.** An uninitialised SR (left outer bare, both inner terminals wired) is legal LabVIEW; deferring initial values to a second saved stage is sound."* — a peer that searched NI's own documentation for the opposite and did not find it (`:179`, `:186`).

I raise no slug on A1. Naming it matters only because the same review's **first half was REFUTED** — "five severed rows, not four" (`:253`), the fifth being `#10407` t1 `# slices in stack`, which needed a LoopTunnel and appeared in no plan item. That row is now **closed**: `tools/bench/diag_c73_m3a2_rows.log:113` reads `node #10407 … 7 terminal(s), 0 BARE`. M3a-2 does not inherit it.

### A3 — CONTRADICTED: Pre-decided 95's named candidate is already excluded by the very log the plan cites, and the census as coded cannot see the class it is aimed at

- **Side 1 — what the plan and the recipe say.** `docs/cycle27-plan.md:3139-3141`: *"`#4256`/`#4334`'s INSIDE sink terminals are **candidates for 'shift-register terminal unwired'**, a broken class that produces no broken wire."* Repeated verbatim at `tools/recipes/build_d1_m3a2.py:87-89` and `:514-516`.
- **Side 2 — what the log it is built on measured.** `tools/bench/diag_c73_m3a2_rows.log:43` — `#4256 … inside=[{… 'wire': 9113}]`; `:44` — `#4334 … inside=[{… 'wire': 7337}]`. Both INSIDE sink terminals **carry a wire uid**. And `tools/bench/build_d1_m3a1.log:1151-1155` gives 9113 a live single source, `LoopTunnel 24018`.

Two consequences, both mechanical:

1. The recipe's census marks a terminal bare **only** when `wire == 0` (`build_d1_m3a2.py:364-366`, `bare_terminals_of`: *"`wire` 0 = bare"*). On a terminal that carries wire 9113 it will print WIRED and move on. So the instrument **cannot report the class it was aimed at** — the same "pointed at the wrong quantity" fault Pre-decided 85 was written to stop (`docs/cycle27-plan.md:3032-3033`).
2. The candidates were already excluded before the recipe was written, by the measurement it cites as its source.

**To release:** show that `diag_c73_m3a2_rows.log:43-44` reports wire 0 on those two terminals, or re-state 95's candidate as something a wire-uid census can actually distinguish.

### A4 — UNREAD EVIDENCE: this project has already enumerated exactly this sink, on exactly this diagram, and neither the plan nor the recipe cites it

The recipe's whole sink resolution (`build_d1_m3a2.py:582-591`) rests on an unstated premise: *a While loop node's `Terminals[]` table carries its shift registers' terminals, by name, with the uninitialised one bare and at a readable index.* That premise is **measured, in our own files, on `Diagram #686`**:

- `tools/bench/build_d1_routeb_v0_run2.log:303-304` — *"1.5: shift register **#25814** for `'position [internal units]'` … **#25840** for `'VISA out …'`"* on `WhileLoop #338` (`:57`).
- `tools/bench/build_d1_routeb_v0_run2.log:467-468` — `BARE  diagram 19 #686 Diagram[19] **Nodes[22].T[1]** 'position [internal units]'` and `**Nodes[22].T[3]** 'VISA out'`; and `:463-466`, four bare rows for 1.2's four registers.

It **confirms** the route, which is why releasing it costs one citation line. It also carries the detail the recipe should keep: the register rows are **interleaved and odd-indexed** (T[1], T[3], T[5], T[7]) — an index that must be read, never computed. Nothing in `docs/cycle27-plan.md:3091-3128` or the recipe's header mentions this run.

Related and worth writing down while disposing of this: reading that row is measured; **writing** to it is not. No file in this corpus records a `Terminal.Connect Wire` whose SINK is a shift-register OUTER terminal reached through a loop node's `Terminals[]` — the built op for that sink (`wire_sr('LeftOutNode')`, `tools/gscript.py:743`) reaches it through `Loop.Shift Registers[]` instead, and is rejected here on its SOURCE side only (Pre-decided 93). I am **not** slugging that — there is no citation saying it fails, and the recipe's stop-before-write discipline (`:591`, `:788`) turns the bad case into a clean gate failure with the file still saved.

## PART B — THE ARTEFACT

### B2 — ALREADY FAILED: the save captures were measured to produce **no file** in run 5, and this recipe copies the call verbatim

This is the finding that costs something on every future run and cost the last one silently.

- **The claim.** `build_d1_m3a2.py:111-115`: *"this file adds the capture BEFORE and AFTER"* — the discharge of Pre-decided 88's rider 1 and of USER RULE 17:5x. Coded at `:931` and `:937` as `g._lv_gui("-Action", "shot", "-Out", "'%s'" % shot_b)` — the path **pre-quoted by the caller**.
- **The measurement.** `tools/bench/build_d1_m3a1.log:3402` (run 5, stamp `20260922_005732` — the run that produced `D1_s3b_m3a_BROKEN_20260922_005732.vi`): *"capture->act->capture: before 'm3a1_save_before_20260922_005732.png' (**exists False**), after '…' (**exists False**)"*. No such files are on disk. The two earlier runs, `:1966` (23:42) and `:2684` (00:22), both read `exists True` and both PNGs are on disk.
- **The mechanism, and the date that fixes it.** `tools/gscript.py:281-287`: `q()` treats an argument as pre-quoted **only when it starts and ends with a DOUBLE quote**, and otherwise re-wraps anything containing a space — so a caller's `'<path>'` becomes `'''<path>'''` and lv_gui receives a path with literal quotes. That repair landed with `archive/peer/2026-09-22-c72-guisave-foreground-r2.md` (**dated 2026-09-22 00:54:45**), i.e. **between run 4 and run 5** — exactly where the captures stopped landing. `build_d1_m3a1.py:680/686` carries the same pre-quoted form.

So M3a-2 will print a `capture -> act -> capture` FACT line with `exists False, exists False` and claim the rider is met. That is the shape this project keeps writing down as a fault: a log line that asserts a guard the run did not have.

**To release:** show a `m3a2_save_*.png` route that lands, or drop the `'%s'` wrapper at `:931`/`:937` and let `_lv_gui` quote (a one-character change per line, no new tool, no gate touched).

### B4 — ALREADY MEASURED: the **BEFORE** half of Pre-decided 95's 14-register census is already on file, terminal by terminal, for a byte-identical artefact

`tools/bench/diag_c73_m3a2_rows.log:42-56` prints all fifteen slots of `#637` — every register's uid, class, OUTER and INSIDE terminal with its wire uid — and `:57` sums it: *"loop #637 carries 15 shift register(s)"*. It was read on a scratch copy of the same input (`:17`, md5 `6b3c1f3c…`, the recipe's `INPUT_MD5`), with the four pins holding at both ends.

`build_d1_m3a2.py:989` re-runs that as `phase_1_census("BEFORE")` — sixteen `shift_reg_left` calls at ~1 s each (`docs/toolkit-capabilities.md:29`) plus a `report_all('WhileLoop')` echo, inside a 45-minute budget that reserves `ROW_MIN_S = 240` per row (`:198`). It is a FACT step that cannot gate (`:513`), on a file byte-identical to the one already censused.

**Scope, precisely:** this covers the **BEFORE** census only. `phase_1_census("AFTER")` (`:1000`) is novel and is the half that could show something. **To release:** show that the target at `[95 BEFORE]` differs from the artefact `diag_c73` read, or keep the BEFORE census as a cheap re-echo rather than a full sixteen-slot walk.

### B1 / B3 — NO FINDING

Checked and clean, stated so the next reviewer does not re-spend it. The writer (`connect_from_wire` / `OpConnectFromWire_v0`, `docs/toolkit-capabilities.md:70`), the reader (`OpWireSource_v5`, `:60`), the register reader (`shift_reg_left` / `OpShiftRegs_v1`, `:29`), the save route (`tools/gscript.py:2087-2089`) and the diagram resolver (`diag_index`) all exist and are all cited by the recipe; the helpers are **imported** from `build_d1_m3a1` rather than rewritten (`build_d1_m3a2.py:138`), and the one re-stated body, `purge_junk` (`:415-419`), says why. `tools/bench/c74_astcheck_m3a2.log:6` confirms every `g.<verb>` and `_lv_gui` exists, and `:4` that `allow_broken` sits at one `.save()` site. Nothing here is hand-rolled over a toolkit call.

One mechanical note in the same spirit: the `is_source is False` filter at `:628` is safe — `tools/gscript.py:934` coerces to real Python bools (`src = [bool(x) for x in …]`), so the strict identity test cannot silently yield zero candidates.

---

```
PRIOR-ART: contradicted
PRIOR-ART: unread-evidence
PRIOR-ART: already-failed
PRIOR-ART: already-measured
```

**Cheapest order to dispose of this:** B2 is decided by one `dir tools\bench\m3a1_save_*20260922_005732*` (no LabVIEW, no build) and fixed by deleting two pairs of quotes; A3 and B4 are decided by opening `diag_c73_m3a2_rows.log:42-57`, one file, one read. A4 is one citation line added to Pre-decided 92. None of the four requires a build to resolve, and none of them argues against running M3a-2.

## Sources

(extract from answer)

## What was done with it

**ALL FOUR FINDINGS ACCEPTED, NONE REFUTED** — disposed by the cycle-64 judgement session as
`docs/cycle27-plan.md` item **99**. Every one is cited to a line of our own logs rather than argued,
and none of them argues against running M3a-2: three shrink the recipe and one repairs a real
defect. The recipe was edited FIRST; these release lines were written after.

**EDITED AGAIN AFTER THE FIRST RELEASE, 2026-09-22 (cycle-64 MATERIAL dispatch 4)** — recorded here because
the launch gate asks for the edit to be cited in a review that post-dates it. Run 1 of the released bytes died
in phase 1 at `:317` on a `%`-format arity defect; `docs/cycle27-plan.md` item **100 §2** then required the
recipe to change: `main()`'s bare handler no longer routes a Python exception of OURS into `refusal()`
(`defect()` and gate **H9** now carry it, naming the exception type and the source line), and the `%`-arity
defects the new `c60c_astcheck` gate 10 finds are repaired. None of that touches what the four findings below
were about, and every one of them stands as released.

FIXED: already-failed - tools/recipes/build_d1_m3a2.py:948 - the save captures no longer pre-quote their path, so `gscript.py:281-287`'s `q()` quotes it exactly once instead of twice, and each capture is now ASSERTED to exist as gates S3/S4 (`:962`, `:974`) rather than hoped for — M3a-1 run 5's captures produced no file at all (`tools/bench/build_d1_m3a1.log:3402`, "exists False, exists False"), which left USER RULE 17:5x formally unmet on that one act.

FIXED: contradicted - tools/recipes/build_d1_m3a2.py:527 - the `#637` register-census step is DELETED from the recipe and replaced by `cite_pd95_withdrawn()`, a citation-only FACT step: Pre-decided 95's named "severed inside terminal" candidate is withdrawn because `tools/bench/diag_c73_m3a2_rows.log:43-44` shows `#4256` inside on wire 9113 and `#4334` inside on wire 7337 (not bare), and the recipe now neither gates on `ExecState` nor claims anything about it — its cause is recorded as formally OPEN.

FIXED: already-measured - tools/recipes/build_d1_m3a2.py:542 - the BEFORE/AFTER halves of that census are gone from the run and replaced by one citation to `tools/bench/diag_c73_m3a2_rows.log:42-57`, already measured on a byte-identical artefact, whose 15 read slots (not 14) also correct Pre-decided 91/95 in the recipe's own record.

FIXED: unread-evidence - tools/recipes/build_d1_m3a2.py:589 - `tools/bench/build_d1_routeb_v0_run2.log:467-468` is now cited in `resolve_sink`'s contract and its odd-index expectation is logged as a FACT line beside the index actually found (`:661`), while the sink terminal itself is resolved live by register uid on the run's own target — an output, never a criterion, and never an index carried from a census.
