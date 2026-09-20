# stall-waitlogs-c37b

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.0051  in 20 / out 33899 / cache-create 162630 / cache-read 970191  (499s, 18 turn(s))
- **date:** 2026-09-19 00:48:30
- **outcome:** ANSWERED (500s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# ATTACK this claim about a watchdog exclusion we just wrote

## The failure record under review
`tools/bench/stall_pid1556_002547.log` (project root: the LabVIEW V6_ParallelLoop tree). Its three lines are:

```
STALL: 2026-09-19 00:28:39 pid 1556 alive 172s, job log tools/bench/wait_c37_b.log last written 172s, CPU +0.00s in the last 64s
dialog: no modal dialog - LabVIEW busy or two clients contending
cmd pid 1556 (started 20260919002547): C:\...\python.exe -u tools/wait_logs.py --seconds 540 tools/bench/repair_c37_selftest.log tools/bench/peer_zdz_5001.log
```

This is the FOURTH record of one class in three cycles. Two of the four (`stall_pid18476_232310.log`,
`stall_pid1556_002547.log`) fired on a `tools/wait_logs.py` waiter; two (`stall_pid11424_221324.log`,
`stall_pid3792_235020.log`) fired on real LabVIEW COM build clients. Each record blocks the next build through
`tools/hooks/guard_peer.py` until an archived peer review is newer than it, so each false positive costs a paid
review and delays the project's actual deliverable.

## THE CLAIM YOU MUST TRY TO DESTROY

> A `tools/wait_logs.py` leaf holds NO LabVIEW client — it only opens files with `open()`, regex-searches them
> and `time.sleep(1.0)` — so the watchdog's own sentence "STALLED LabVIEW client" can never be true of it, and no
> threshold or liveness probe can make the test meaningful there. Therefore the correct repair is to exclude such
> a leaf **by the script name on its own bound command line**, unconditionally, before any CPU or log-freshness
> test:
>
> ```powershell
> if ($cl -and $cl -like '*wait_logs.py*') { Say-Why $p.Id 'skip - tools/wait_logs.py waiter (holds no LabVIEW client)'; continue }
> ```
>
> placed in `tools/lv_stallcheck.ps1` immediately after the existing matrix-driver skip, where `$cl` is already
> bound to the process by the (pid, CreationDate) pair. Coverage for real clients is unaffected, because neither
> real-client record names `wait_logs.py` on its command line.

Give me the STRONGEST reason this is wrong; an ALTERNATIVE explanation of why the class keeps firing; what
OBSERVATION would falsify the claim; and the CHEAPEST discriminating test.

Specific attack surfaces I want you to look at, and say so if any of them breaks the claim:

1. **Name-matching on a command line as a security/correctness primitive.** `$cl -like '*wait_logs.py*'` is a
   substring test on text. What else can carry that substring — a `grep wait_logs.py`, an editor, a future
   wrapper that both waits AND drives LabVIEW, a path that merely contains the words? What is the blast radius
   if a real client is ever excluded by accident, given that this watchdog is the only mechanism that notices a
   hung COM client at all?
2. **Is "holds no LabVIEW client" actually load-bearing, or is it a category error?** The watchdog's message is
   hard-coded to say "STALLED LabVIEW client(s)". Is the right repair to fix the *message* and keep flagging
   genuinely stuck processes of any kind, rather than to carve out a script by name?
3. **Does this exclusion hide a real failure mode?** A waiter CAN be wrong: if the job it waits on died without
   writing its terminal line, the waiter sits until its own deadline. Under the claim, nothing reports that any
   more. Is losing that signal worse than the false positives?
4. **The precedent.** This is the SECOND clause added to the same watchdog in the same cycle (the first, at
   `tools/lv_stallcheck.ps1:154-184`, compares every `.log` path on the leaf's own command line for freshness,
   and it did NOT stop this record: the job being watched was a `claude -p` peer cell that is alive and silent
   for its whole 640 s, so both watched logs were stale beyond the 90 s threshold). Is a watchdog that needs a
   new exclusion every cycle converging or diverging? Name the structural alternative if you think there is one.

## Already ruled out — do not spend your answer on these
- **Raising `$LogFreshSeconds`**: rejected. The silent job here was a 640 s `claude -p` cell; any threshold that
  covers it is longer than most real stalls, so it would blind the watchdog to the class it exists for.
- **A liveness probe on the watched job** (is the PID still alive?): rejected as a new device — the project is
  under a standing user order of 2026-09-18 08:53 not to build further process machinery.
- **Changing `tools/hooks/guard_peer.py` so stall records stop gating builds**: out of scope; the gating is a
  direct user instruction of 2026-09-14.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled for this role — correct for a read-only reviewer (`archive/peer/2026-09-18-stall-waitlogs-c37.md:71` records the same). The review is the deliverable in full.

---

# The claim excludes the two records it can explain and leaves the same defect firing on the other two — which are also false positives.

## 1. Strongest reason the claim is WRONG

**The sentence the whole repair rests on is factually false, and it is already written into the file.** `tools/lv_stallcheck.ps1:116-118` justifies the narrow carve-out with: *"The other two records … are real build clients and are untouched by this clause … so the class the rule exists for keeps firing and keeps being discharged by the mandatory review."*

I measured those two. Neither was a stall.

| record | fired | job it named | that job's own ending | bgrun limit | tree-killed? |
|---|---|---|---|---|---|
| `stall_pid18476_232310` | 175 s in | `wait_priorart_run5.log` | `END rc=0 after 331s` | 18 min | no |
| `stall_pid11424_221324` | 808 s in | `build_d1_routeb_v1_run4.log:354` | `END rc=1 after **1713s**` | 30 min = 1800 s | **no** |
| `stall_pid3792_235020` | 616 s in | `build_d1_routeb_v2_run5.log:428` | `END rc=1 after **1668s**` | 40 min = 2400 s | **no** |
| `stall_pid1556_002547` | 172 s in | `wait_c37_b.log:6` | `END rc=1 after 461s` | 10 min = 600 s | no |

`build_d1_routeb_v1_run4.log:340-353` settles it. After being accused at 22:26:52 ("log stale 499 s, CPU +0.00 s over 113 s"), that client went on to write `PASS S6b original md5 AFTER`, then `FACT LabVIEW handles after: 49062`, then raised its own `RuntimeError` out of a `Traverse for GObjects` call and exited — **905 s after the accusation, inside its own deadline.** LabVIEW answered. The process was never "blocked on a LabVIEW that will never answer" (`tools/lv_stallcheck.ps1:14-15`), and following the record's instruction — *"Do not wait: diagnose now … and stop the task"* (`:274`) — would have killed a job that was working.

So the discriminator the claim installs (*is it a waiter?*) is not the discriminator that separates these four records from a real stall. **Nothing separates them, because none of them is a real stall.** Precision goes from 0/4 to 0/2. Add `tools/lv_stallcheck.ps1:202-204`, which records *"4 false positives, 0 true stalls"* for the 2026-09-14 batch, and this watchdog is **0-for-8 lifetime with no confirmed true positive ever** — at `$3.1519` for the last review (`archive/peer/2026-09-18-stall-waitlogs-c37.md:7`) and `$5.78` + 16 min for cycle 35's (`:153`).

A second, independent hit: the exclusion at `:120` runs *before* `:184-196`, so it makes that clause unreachable for the only leaf class it was written for, and falsifies its stated, peer-reviewed guarantee at `:176-177` — *"a waiter sleeping on a genuinely dead job still fires, because then both logs are stale."* One cycle after buying that property for $3.15, the claim deletes it without arguing against it. The file now documents behaviour it does not have.

## 2. Alternative explanations of the same evidence

**A — the time constants are an order of magnitude below the legitimate quiet periods of the work being watched.** `$StallSeconds=150`, `$LogFreshSeconds=90`, `$DeltaWindowSeconds=60` (`:25,32,34`) against *measured* legitimate silences of 499 s and 357 s inside builds that ran 1713 s and 1668 s. And zero client CPU is not a symptom — it is the documented *normal* state of a healthy out-of-process COM call: "While the server is processing the call, the client is blocked … until the server has finished processing" ([Marshaling Details, MS Learn](https://learn.microsoft.com/en-us/windows/win32/com/marshaling-details)). The file half-knows this at `:125-127` and patched it with a 90 s escape hatch that is far shorter than the LabVIEW operations this project actually runs. Waiter-vs-client is orthogonal; the waiters are just the population that happened to be quiet.

**B — the records may be a real signal about LabVIEW's state, mislabelled as a client stall.** `build_d1_routeb_v1_run4.log:341` reads `LabVIEW handles after: 49062` — roughly **17,500 above the project's own fresh-start baseline of ~31,500** (CLAUDE.md, reference hygiene). A LabVIEW degrading under handle load makes operations that used to finish inside 90 s take 500 s, which produces exactly this record shape. Under that reading the firings are information about *when to restart LabVIEW*, and the claim disposes of them as noise. I cannot settle this from one handle sample (`before 0` — nothing was read at start), but it is consistent with every record and the exclusion would hide the cheaper half of it.

**C — snapshot answering an outcome question**, from `…-stall-liveness-class-c36.md:94`, still unrefuted: the fact that resolves every one of these four (the job's terminal line) does not exist at alert time.

## 3. What would falsify the claim — and what would falsify me

- **Falsifies the claim:** one `stall_pid*.log` naming a non-waiter leaf whose job ends `BGRUN TIMEOUT` or never reaches a terminal line. That would show the retained coverage is worth something and the waiter trim is the right cut. No such record exists in the eight.
- **Falsifies the claim's mechanism, cheaply:** rename the waiter to `wait_logs_v2.py`. `-like '*wait_logs.py*'` does not match it and the class returns unchanged — proving the fix is bound to a filename, not to a property. CLAUDE.md's own firefighter rule anticipates precisely this ("the same mistake under another name … even if the recipe was renamed v1 → v2").
- **Falsifies MY alternative A:** a record whose named job was actually killed at its deadline *while* the silence exceeded any plausible LabVIEW operation — i.e. a case where 150/90/60 was not the reason. Or a demonstration that raising the constants to cover 499 s would have suppressed a record later proven to be a real hang.

## 4. Cheapest discriminating test

**One pass over `tools/bench/stall_pid*.log` — seconds, no LabVIEW, no build, no dispatch.** For each record, resolve the job log named on line 1, read its `BGRUN START` limit and its terminal line, and bucket by **"killed at the deadline / never terminal"** — *not* by `rc`. My prediction, stated in advance: **zero records land in that bucket.** One that does refutes me.

That correction matters beyond this review. The earlier reviewer's table (`archive/peer/2026-09-18-stall-waitlogs-c37.md:89-94`) used `rc≠0` as the "true positive" bucket and therefore recorded `stall_pid11424` as *"stands — correctly"*. It conflates *the build failed* with *the client hung*. The shelved cycle-36 retraction rule (`…-stall-liveness-class-c36.md:94`, "retract a stall record whose named job later ends `BGRUN END rc=0`") inherits the same defect and would still leave both client records standing as true positives that are not true. **Fix the discriminator before building the retraction.**

## Your four attack surfaces, answered straight

1. **Name-matching blast radius — does NOT break the claim today.** `:104` enumerates only `py`/`python`, so a `claude -p` cell carrying the string in its prompt is never a candidate (it is node, not python), and the realistic python carrier (`py tools/bgrun.py … -- py -u tools/wait_logs.py …`) is already skipped as a wrapper at `:124`. Blast radius ≈ 0. The cost is not today's over-match; it is that the predicate is a filename, so the same waiter under any other name re-enters the class.
2. **Category error — yes, and further than you framed it.** Fixing the message alone does not help: `guard_peer.py:73` matches the **content** `^STALL:`, not the filename (`logclass.py:75` only governs build accounting). Message and gate are coupled through one token — which means `lv_stallcheck.ps1` can stop gating *on its own*, without touching `guard_peer.py`, so your "out of scope" item does not block the real repair.
3. **Hidden failure mode — yes, and it is the one the previous cycle deliberately bought** (`:176-177`). Small in absolute terms, because `wait_logs.py` is self-bounded and bgrun tree-kills anyway, but it was paid for and is now silently gone.
4. **Converging or diverging — diverging, measurably.** Six skip clauses now (`:108`, `:120`, `:124`, `:159`, `:164`, `:184-196`); three added in three cycles; the newest makes one of the others dead. **The structural alternative is subtraction, not a seventh clause:** after `:159` the watchdog can only see leaves that have a bgrun ancestor, and `tools/bgrun.py:226-246` tree-kills at the deadline with a *verified* `taskkill /F /T` and always writes `END`/`TIMEOUT`. The unbounded seven-hour hang in the header (`:4-9`) is structurally impossible for everything this watchdog can still see. Concretely: keep the `systemMessage`, and write the gating `stall_pid*.log` **only when corroborated** by the dialog check already running at `:238-244` returning `VERDICT: BLOCKED`. All four records say "no modal dialog" — that one condition writes **zero** of the four while keeping the case the watchdog was actually built for. One line removed, no new device, `guard_peer.py` untouched.

## What I concede, and what would change my mind

Conceded: `wait_logs.py` genuinely holds no LabVIEW client (it imports only `argparse/os/re/sys/time`, `:23-27`), the accusation is literally untrue of it, and no threshold makes *that sentence* true. Conceded too that the record was not *wrong when written* — at 00:28:39 a healthy and a wedged process were identical in every quantity the watchdog reads.

What does not follow is that a name exclusion is the repair. **Changed by:** the table in §4 coming back with any record in the killed/never-terminal bucket; or a decision record showing the dialog-corroboration option was considered and rejected on stated grounds, in which case this is policy rather than omission.

One thing I could not settle: whether either build client was killed by a session rather than exiting on its own. `BGRUN END rc=1` plus a Python traceback at `:342-353` is strong evidence it exited by itself, but the logs do not exclude an external kill, and that is the one observation that would soften §1.

**Sources:** [Marshaling Details — MS Learn](https://learn.microsoft.com/en-us/windows/win32/com/marshaling-details) · [Get-Process — MS Learn](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-process?view=powershell-7.6) (module reads are bitness-bound, which is why a positive "does this leaf hold a COM reference" test via `-Module` is not free — worth knowing before anyone proposes it as the next clause).

**Local:** `tools/lv_stallcheck.ps1:4-9,14-15,25-34,104,108,116-120,124,153,159,164,176-177,184-196,202-204,238-244,274` · `tools/wait_logs.py:23-27,80-94` · `tools/bgrun.py:226-246` · `tools/hooks/guard_peer.py:73` · `tools/logclass.py:75` · `tools/bench/build_d1_routeb_v1_run4.log:1,340-354` · `tools/bench/build_d1_routeb_v2_run5.log:1,428` · `tools/bench/wait_c37_b.log:1-6` · `tools/bench/stall_pid{18476_232310,11424_221324,3792_235020,1556_002547}.log` · `archive/peer/2026-09-18-stall-waitlogs-c37.md:7,71,89-94`

## Sources

(extract from answer)

## What was done with it

Disposed by the cycle-37 MATERIAL session (dispatch 4) immediately on return. This session may correct facts it
got wrong; it may not change the watchdog's design, so the findings split cleanly.

**ACCEPTED AND ACTED ON — §1, finding (1): the justification sentence I wrote was FALSE.** I had written into
`tools/lv_stallcheck.ps1` that the other two records "are real build clients … so the class the rule exists for
keeps firing". The reviewer resolved the job named on line 1 of each record and neither client was killed at its
deadline (`build_d1_routeb_v1_run4.log` `END rc=1 after 1713s` under a 30-min limit; `build_d1_routeb_v2_run5.log`
`END rc=1 after 1668s` under a 40-min limit), and run 4's client went on writing PASS lines for 905 s after being
accused (`build_d1_routeb_v1_run4.log:340-353`). Both run-log endings are independently corroborated by
`STATUS.md`'s own lock-block record of runs 4 and 5, so this is confirmed, not taken on the peer's word. The
false sentence is **deleted** and replaced by the measured table plus the consequence — this clause moves
precision from 0/4 to 0/2, it does not restore a working test: `tools/lv_stallcheck.ps1:114-135`.

**ACCEPTED AND ACTED ON — §1, second hit: the new clause makes the cycle-36 clause unreachable.** Because the
`wait_logs.py` skip runs at `:136`, before the own-command-line freshness clause at `:200-211`, that clause's
stated and peer-reviewed guarantee at `:192` ("a waiter sleeping on a genuinely dead job still fires") no longer
holds. Recorded in the same comment block; the guarantee is not silently left in the file as a claim.

**ACCEPTED AS A FACT, NOT ACTED ON — §4.4, the structural alternative (write the gating `stall_pid*.log` only
when the dialog check at `:257` returns `VERDICT: BLOCKED`; all four records say "no modal dialog", so it writes
zero of them, one line removed, no new device, `guard_peer.py` untouched).** This is a DESIGN CHANGE to a gate
that blocks builds, and a material session does not make those (CLAUDE.md §3). It is written into the clause
comment and carried to the judgement session as the cycle's `OPEN:` item.

**NOT ACTED ON — §3, the rename falsification** (`wait_logs_v2.py` would not match `-like '*wait_logs.py*'`, so
the fix is bound to a filename rather than a property). Correct, and it argues for the reviewer's §4.4 route
rather than for widening the pattern; it therefore rides with the same judgement decision.

**NOT ACTED ON — §2.B, the handle-load reading** (49,062 handles ≈ 17,500 above the ~31,500 baseline could make
sub-90 s operations take 500 s, so the records may be information about when to restart LabVIEW). This is the
same measurement problem `STATUS.md` records for the `error 2` question: `tools/bench/bench_prep.py:64-71` reads
KERNEL handles, which cannot see VI Server refnums, so the numbers in evidence cannot settle it either way. Left
open, cross-referenced rather than argued.

**NOT RUN — §4, the cheapest discriminating test** (one pass over `tools/bench/stall_pid*.log`, bucketing by
"killed at the deadline / never terminal" rather than by `rc`). The reviewer's prediction is that zero records
land in that bucket. It needs no LabVIEW and would take seconds, but it is a new diagnostic outside this
dispatch's four named items, and its result feeds exactly the design decision above — so it is named to
judgement as the first thing to run if that decision needs more than the four records already resolved here.

**REFUTED: nothing.** Every checkable claim in this review that I checked held.
