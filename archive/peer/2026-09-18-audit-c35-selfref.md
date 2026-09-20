# audit-c35-selfref

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $2.9750  in 26 / out 29916 / cache-create 156134 / cache-read 1282527  (430s, 23 turn(s))
- **date:** 2026-09-18 19:54:52
- **outcome:** ANSWERED (431s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# ATTACK this reading of `tools/bench/audit_c35.log`

## What happened

Cycle 35 repaired `tools/audit_cycle.py` check C7 (it built the plan filename from the cycle number,
`docs/cycle<N>-plan.md`, which went dead when this project moved to ONE plan spanning cycles 27+; it now reads the
plan whose frontmatter says `status: current`, via `doc_lint.current_plans()`). To verify the repair I ran the
audit: `py tools/bgrun.py --material --max-min 10 --log tools/bench/audit_c35.log -- py -u tools/audit_cycle.py`.

C7 printed, for the first time in many cycles, a real answer (`audit_c35.log:23`):
`C7 files modified in the window but NOT named in docs/cycle27-plan.md [frontmatter status: current]: 138 - …`

The run ended `BGRUN END rc=1 after 1s`, because the audit exits non-zero when any A-check fails
(`audit_c35.log:39`): `AUDIT VIOLATIONS: A1 …, A2 …, A3 …, A4 …`. The four failing lines, verbatim:

```
FAIL  A1 every build log came from bgrun: 88/89 ok; NO BGRUN line in ['motor_gate.log']
FAIL  A2 every bgrun ended (END or TIMEOUT): unfinished: ['audit_c35.log',
      'diag_fstunnelterm_v2_panelcost.log', 'p2_open_copy.log', 'prose_cycle25.log', 'wait_runner_exit.log']
FAIL  A3 every failing log is followed by an archived review: 26 logs recorded a failure;
      unreviewed: ['audit_c35.log']
FAIL  A4 every archived review says what was done with it: 99/121 annotated; blank: [6 named files]…
PASS  A5 the main VI was not modified in this window: md5 2a78e17c449c…, mtime 2026-09-01 12:07
```

`tools/hooks/guard_peer.py` then blocked the next bench run on `audit_c35.log` as a FAILED PREDICTION.

## THE CLAIM YOU ARE ASKED TO REFUTE

**Claim D:** none of those four failures is evidence about the C7 repair or about the work the gate is now
blocking, and in particular:

1. **A2 and A3 are SELF-REFERENTIAL.** `audit_c35.log` is named by A2 as "unfinished" and by A3 as "unreviewed"
   because the audit reads the directory of bench logs *including the log it is at that moment writing* — at the
   instant A2/A3 ran, its own `BGRUN END` line had not been written yet, and no review of a log that does not yet
   exist can exist. This project already recorded that self-reference (STATUS.md OPEN 42: "`audit_cycle` A2/A3
   SELF-REFERENTIAL, not fixed").
2. **A1 and A4 are PRE-EXISTING and untouched by this cycle.** `motor_gate.log` (A1) and the six blank review
   dispositions (A4) were all written in earlier cycles; A4's blank list is STATUS.md OPEN 42's "39 undisposed
   reviews" and `doc_lint` L6's standing warning. Nothing cycle 35 did created or worsened them.
3. **Therefore the safe action is to proceed** with the one remaining task: a READ-ONLY VI-Server measurement
   (`tools/bench/diag_count_indicator.py`) of what the `Count` indicator is wired to, on a `claudeDev` COPY —
   no motor, no serial, no camera, no VI is run, no file is written except a JSON of the readings, and the
   ORIGINAL's md5 is checked before and after.

Attack it:

1. The strongest reason Claim D is WRONG — including any way the four failures could be *caused by* the C7 edit
   or by the `doc_lint.current_plans()` helper added in the same cycle.
2. An ALTERNATIVE explanation of the same log, especially of A2's other four entries
   (`diag_fstunnelterm_v2_panelcost.log`, `p2_open_copy.log`, `prose_cycle25.log`, `wait_runner_exit.log`) —
   are those also benign, or is one of them a live process that should stop something?
3. What observation would FALSIFY Claim D.
4. The cheapest discriminating test, runnable now, that separates "self-reference + pre-existing debt" from
   "the C7 edit broke something".
5. Whether the specific next action — that read-only measurement — can cause any harm the STALL/prediction gate
   exists to prevent. The rig is **assembled**: motors and the ASI are reachable only through `tools/motor_gate.py`
   and this script never imports it.

## Already ruled out — do not spend your answer on these

- "Set `PEER_GUARD_OFF=1`" / "`CYCLE_GUARD_OFF`": forbidden by this project's rules, not under consideration.
- "Fix A1–A4 first": A4's remedy (disposing 22 old reviews) and A1's (`motor_gate.log`'s missing BGRUN line) are
  open items owned by judgement (STATUS.md OPEN 42), and this is a material session with no authority to decide
  them. Say so if you think that ordering is itself the error.
- "The audit should not exit 1 on pre-existing debt": possibly true, but changing the audit's exit code is a
  device change, and this project is under a standing user order to build no further process devices
  (STATUS.md line 10, `docs/cycle27-plan.md` Pre-decided 2).


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

## 1. The single strongest reason Claim D is wrong

**The gate is blocking the NEXT action, so "not caused by this cycle" is the wrong test — and two of the items Claim D files under "pre-existing debt" are about the exact VI the next action opens.**

- `tools/bench/p2_open_copy.log:1-8` — started 14:35:32 with `limit 180.0 min`, last line **`holding references 10000 s (the user runs the VI by hand now)`**, no `BGRUN END`, no `BGRUN TIMEOUT`, still unterminated when the audit ran at 19:46. Its target is `tools/bench/p2_open_copy.py:14` = `…\claudeDev\Track_D0_copy_20260918.vi` — **byte-for-byte the target of `tools/bench/diag_count_indicator.py:58`.** The log also records `original resident, ExecState 1` and `copy front panel open`.
- `archive/peer/2026-09-17-d1-s1-stale-in-memory-copy.md` — one of A4's six blank entries, quoted verbatim in `audit_c35.log:9` — is an **ANSWERED** review whose subject is precisely this: a census that read a VI's in-memory state while the disk file said otherwise. Its NI-sourced remedy (`:45`) is *"prove the target's qualified VI name is absent from `All VIs in Memory` before opening"*, or a fresh instance / unique filename. `diag_count_indicator.py` does none of the three, and its hygiene gates (`:267-268` G1/G8) hash the **disk** file — which cannot detect the failure, because the failure is that the disk file is not what is being read.

That is not a theoretical risk. Open VI Reference "either creates a reference to a VI already loaded in memory or loads a VI into memory from a file path"; wired a path, "LabVIEW searches for a VI in memory that you previously loaded from that path… if a matching VI is not found in memory, LabVIEW then tries to load the VI from that file on disk" ([LabVIEW Wiki, VI Reference](https://labviewwiki.org/wiki/VI_Reference); [Loading VIs](https://labviewwiki.org/wiki/Loading_VIs)).

So the failure mode the gate would prevent is **a wrong answer recorded as a measured fact** about what `Count` is wired to — on a D1 *precondition* — from a copy that another, never-terminated client last reported holding open with its panel up and possibly hand-edited by the user. Claim D's part 2 proves these items are old; it never asks whether they are *relevant*, and they are.

**A second, factual error in the claim's safety premise:** "no VI is run" is false. `diag_count_indicator.py:105` and `:138` call `g._run(vi)` on `OpWireSource_v5.vi` (up to 8× per wire) and `OpOwnerChain_v1.vi` (up to 4 owner hops, `:153-163`). Op VIs, not the target, and they cannot reach an instrument — but a reviewer asked to bless "no VI is run" was handed a premise the file contradicts.

## 2. Alternative explanation of the same log

**Not "self-reference + inert debt" — a failing bgrun termination guarantee, with A2's own exemption dead, so A2 cannot tell its own live log from the orphans.**

- `tools/audit_cycle.py:242` reads `os.environ.get("BGRUN_LOG", "")` to exempt its own in-flight log. **`tools/bgrun.py` never sets it** (grep: 0 hits; the only env work is `DETACH_ENV` at `bgrun.py:52`). This project already found this and had it reviewed *twice* on 2026-09-18 — `archive/2026-09-18-status-cycle20-close.md:107` ("the audit's own-log exemption is **unreachable**"), `archive/peer/2026-09-18-c20-audit-a1-motorgate-codex.md:93`, `…-opus.md:109`. Claim D cites STATUS OPEN 42's "A2/A3 SELF-REFERENTIAL, not fixed" as if self-reference were an inherent property; the project's own record says it is a **one-line environment bug with a named repair**. Treating a repairable defect as an immutable excuse is how a check gets ignored.
- With the exemption dead, A2 is the only thing in the fleet that notices an orphan — and it caught three today:
  - `prose_cycle25.log` — a `BGRUN START` **and nothing else** (13:56:30, 8-min limit). This is verbatim the class STATUS.md OPEN 54 records as having now happened three times ("both bench logs hold a `BGRUN START` and nothing else"), whose detector STATUS says is *deliberately not built*. **A2 is that detector.**
  - `diag_fstunnelterm_v2_panelcost.log` — 12-min limit at 13:29:13, output stops mid-listing at `:49`, no END/TIMEOUT. It had just read `HANDLES before: 30674` and was running a panel census: a client killed mid-census does not close its references (CLAUDE.md reference hygiene).
  - `p2_open_copy.log` — above.
  - `wait_runner_exit.log:1-6` — a **live** 20-second poller waiting for `RUNNER STOP`, started 19:33:35 with a 200-min limit, i.e. 13 minutes old when the audit ran. Correctly listed, not debt, and it is the runner-handover wait STATUS.md:12-14 describes.

Under this reading, `rc=1` is informative and CLAUDE.md's stated guarantee — bgrun "always writes a final `BGRUN END|TIMEOUT` line" — is the thing that failed, three times in one day, unreviewed.

**And A3 is a weaker check than either side assumes.** `audit_cycle.py:257` clears a failing log if *any* file in `archive/peer/` is newer — it never checks the review is *about* that log. Archiving this exchange will clear A3 mechanically, for all 26 failing logs at once. "A3 blocked us" therefore tells you nothing, and neither will its clearing.

## 3. What would falsify Claim D

Any one of these:

1. `tasklist` / `wmic process … get commandline` shows a live `python.exe` running `p2_open_copy.py`, **or** LabVIEW's `All VIs in Memory` contains `Track_D0_copy_20260918.vi` → A2 is reporting live state, and the next measurement would read a resident copy. Claim D's point 3 falls.
2. A bgrun child printing `repr(os.environ.get('BGRUN_LOG'))` returns the log path → A2's exemption is alive, and `audit_c35.log`'s appearance has some *other* cause that nobody has diagnosed.
3. `docs/cycle27-plan.md`'s mtime is **earlier** than `2026-09-18 19:46:42` while C7 still lists `docs/NAMES.md` → C7's matcher is defective, and the failure *is* caused by the C7 edit.
4. Any of the four non-self A2 entries turns out to have a terminating line the audit could not see (encoding, a second file) → A2 over-reports and my alternative weakens.

On (3): `docs/cycle27-plan.md:105` cites `docs/NAMES.md:888-897` **today**, and C7's exclusion at `audit_cycle.py:422` (`rel in ptext or … or fn in ptext`) would have suppressed it — yet `audit_c35.log:23` lists `docs/NAMES.md`. Either the plan gained that line after 19:46:42, or the matcher missed a citation sitting in plain sight. **The measurement does not distinguish these two.** I can say the matcher is not *globally* dead — `docs/d1-route-b-plan.md` and `docs/decisions.md` are both named in the plan and both absent from C7's alphabetical head where they would sort — but that is one positive, not a verification. Nobody checked a single one of the 138 entries. "C7 printed a number" is CLAUDE.md's **structural** verification; the claim reports it as functional.

## 4. Cheapest discriminating test — one foreground command, no LabVIEW lock, ~2 s

```
py -c "import os,glob,time;p='docs/cycle27-plan.md';t=open(p,encoding='utf-8',errors='replace').read();print('PLAN mtime',time.strftime('%%Y-%%m-%%d %%H:%%M:%%S',time.localtime(os.path.getmtime(p))),'| NAMES.md cited:','NAMES.md' in t);print('UNFINISHED:',[(os.path.basename(f),time.strftime('%%H:%%M',time.localtime(os.path.getmtime(f)))) for f in glob.glob('tools/bench/*.log') for b in [open(f,encoding='utf-8',errors='replace').read()] if 'BGRUN START' in b and 'BGRUN END' not in b and 'BGRUN TIMEOUT' not in b])" & wmic process where "name='python.exe'" get commandline,processid
```

It answers all three questions at once: plan mtime vs 19:46:42 settles C7 (claim vs. broken matcher); the unfinished list re-read *now* separates "audit_c35.log was in flight" (it has an END line now, so it drops off) from the four genuine orphans (which stay); and the `wmic` half says whether `p2_open_copy` is still alive — which is the only fact that decides whether the `Count` measurement can be trusted.

If `p2_open_copy` is **not** alive, the one additional read worth making before the measurement is LabVIEW's `All VIs in Memory` (NI recommends exactly this property for monitoring unloading — [NI: Closing References in LabVIEW](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html)), checking for `Track_D0_copy_20260918.vi`. That is the remedy the undisposed A4 review already specified, it costs one COM read, and it converts the measurement from "probably fine" to "known to be reading the disk file".

## Findings with no slug attached

- **`diag_count_indicator.py`'s md5 guarantee is conditional on the happy path.** `:174-178` and `:195-197` return before the hygiene gates at `:267-268`, so a run that stops at G1 or G2b records **no** "ORIGINAL md5 unchanged" line at all. `g.reset()` is in a `finally` (`:286-290`); the hygiene gates are not. Given that three runs today died without reaching their own last line, that ordering is the wrong way round.
- **Two different files are called "the original", and A5 guards one.** `audit_cycle.py:67` hashes `Min_Track N beads V6_ParallelLoop.vi` (md5 `2a78e17c…`, matching `diag_count_indicator.py:63`), while `p2_open_copy.py:13` hashes `Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi` (md5 `c39f36e0…`) — the VI CLAUDE.md rule 1 names as *the reference VI*. `PASS A5` at `audit_c35.log:10` does not cover it.
- **On the ordering objection you asked me to rule on:** deferring A1/A4 to judgement is correct for *remediation*, and wrong for *relevance*. A material session cannot decide to dispose 22 reviews — but reading the one A4 entry that names its own next target costs one file read, and it changes the run. "Owned by judgement" is not a reason not to look.

## Verdict

Claim D's parts 1 and 2 are **half right and wrongly grounded**: A2/A3 do fire on this run's own log, but because of a dead exemption the project has already diagnosed, not because self-reference is unavoidable; and A1/A4 are indeed old. Part 3 — "therefore the safe action is to proceed" — **does not follow, and I think it is wrong.** The measurement cannot reach a motor, the ASI, serial or the camera (`diag_count_indicator.py:47-55` imports `json/os/sys/time` and `gscript` only; `motor_gate` never appears), so the *hardware* harm the rig rules exist for is not in play. The harm in play is the one this project keeps paying for: a measured fact that is wrong because LabVIEW served a resident copy, recorded into `count_indicator.json` as a D1 precondition. Run the command above first; it costs two seconds and it is the difference between a measurement and a guess.

What would change my mind: `wmic` showing no live `p2_open_copy`, **and** `All VIs in Memory` not containing `Track_D0_copy_20260918.vi`. Then the stale-copy objection is dead on the evidence rather than on the argument, and proceeding is right.

**Sources:** [LabVIEW Wiki — VI Reference](https://labviewwiki.org/wiki/VI_Reference) · [LabVIEW Wiki — Loading VIs](https://labviewwiki.org/wiki/Loading_VIs) · [NI — Closing References in LabVIEW](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html) · [NI Forums — Open VI Reference speed when not already in memory](https://forums.ni.com/t5/LabVIEW/Open-VI-reference-is-very-slow-if-VI-is-not-already-loaded-in/td-p/3337386)

## Sources

(extract from answer)

## What was done with it

**Its falsifier #1 was run first, before any LabVIEW call, and it came back NEGATIVE — so the specific danger the
review raised is measured absent, and the measurement proceeded. Two of its corrections are accepted outright.**

**The test (§3 falsifier 1, the one that mattered).** The review's strongest concrete point was that
`tools/bench/p2_open_copy.log` — an unterminated bgrun from 14:35:32 whose last line is
`holding references 10000 s (the user runs the VI by hand now)` — names **byte-for-byte the target of
`tools/bench/diag_count_indicator.py`**, `…\claudeDev\Track_D0_copy_20260918.vi`, with `copy front panel open`.
If that were live, the next measurement would read a resident, possibly dirty copy under another execution path.
Measured at 19:57 with `tasklist | grep -iE "labview|python"`: **NO LabVIEW process exists at all** — five
`python.exe` remain, none of which can be holding a VI Server reference, because references live inside LabVIEW
and there is no LabVIEW. "All VIs in Memory contains `Track_D0_copy_20260918.vi`" is therefore not merely false
but unreachable. `p2_open_copy.log`'s process outlived its LabVIEW, or its python outlived both; either way it
holds nothing. The measurement then opened the copy cold and checked its md5 before and after.

**Accepted, and the file was wrong where the review says it was.** (a) "no VI is run" in the task file was
sloppy: `diag_count_indicator.py` runs the OP VIs (`OpWireSource_v5`, `OpOwnerChain_v1`, `panel_wiring`) through
`g._run`. What is true, and what should have been written, is that **no INSTRUMENT-reaching VI and not the target
VI is run**: the target is only opened by reference and traversed. (b) **A3 is a weaker check than I implied** —
`audit_cycle.py:257` clears a failing log if *any* file in `archive/peer/` is newer, without checking the review
is about that log, so archiving this exchange clears A3 for all 26 failing logs mechanically. I am not treating
A3's clearing as evidence of anything, and say so in the cycle summary.

**Not accepted as blocking, and why.** The review's §2 reframes A2 as "bgrun's termination guarantee is failing,
unreviewed, three times in one day". That is a real and unpleasant possibility, but it is a claim about the
harness's own guarantee (CLAUDE.md's "always writes a final `BGRUN END|TIMEOUT` line") across earlier cycles —
a judgement-owned question, not something a material session may settle or silently patch, and nothing in it
changes the safety of a cold read of a claudeDev copy on a rig with no LabVIEW running. **Raised in this cycle's
`OPEN:` block with the four log names.**

**Unchanged claims.** A1 (`motor_gate.log`) and A4 (blank dispositions) remain pre-existing debt owned by
STATUS.md OPEN 42; the C7 repair itself is confirmed working by the line the same run printed
(`tools/bench/audit_c35.log:23`, `… NOT named in docs/cycle27-plan.md [frontmatter status: current]: 138`),
which is the first real C7 answer in many cycles.
