# c85-v1-handle-delta

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.3578  in 28 / out 26026 / cache-create 183580 / cache-read 1594983  (364s, 21 turn(s))
- **date:** 2026-09-22 14:25:46
- **outcome:** ANSWERED (366s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK the explanation below. It is a claim formed under pressure after a FAILED PREDICTION, and your job
is to refute it, not to agree with it.

THE FAILED PREDICTION (the log: `tools/bench/build_d1_m3a3b_d3.log`, recipe
`tools/recipes/build_d1_m3a3b_d3.py`, run 2026-09-22 14:0x, `BGRUN END rc=1 after 249s`, 35 gates pass /
12 fail). The FIRST failing gate, and the only machinery one, is:

    **FAIL**  G2 20 consecutive calls leave the handle count flat +-100 (a REGRESSION CHECK against the
    S0 baseline docs/toolkit-capabilities.md:460-478, not a hygiene proof)
    before 42471 -> after 42585, delta +114 ; private-bytes drift 3.3 MB

PREDICTION: a newly built op VI, `claudeDev\OpFsInnerTunnelConnect_v1.vi` (md5
5b4e5f0fb3baae96361c33ce81bcd7b1, 18,797 B, ExecState 1), called 20 times in a row against a scratch copy
of a 307 KB VI, would leave the Windows kernel handle count of LabVIEW.exe within +-100 of where it
started. That is the project's standing acceptance criterion for a new op (CLAUDE.md "Reference hygiene",
20 runs flat +-100). Its DONOR `OpFsInnerTunnelConnect_v0.vi` passed the identical test 5 days-of-work
earlier at **+94** (`tools/bench/build_opfsinnertunnelconnect_v0.log`, gate G2 PASS, private-bytes drift
0.03 MB).

OBSERVED: **+114**, i.e. 5.7 handles per call, and a private-bytes drift of **3.3 MB** where v0's was
0.03 MB - a 100x difference in the memory companion on an op that differs from v0 ONLY by which of two
existing wires feeds which of two existing Invoke terminals (the "roles exchanged" swap) plus one new
front-panel Boolean control for `Auto Route?`.

THE EXPLANATION THIS SESSION FORMED, WHICH YOU MUST ATTACK:
"v1 leaks a handful of VI Server references per call because its internal chain (`UID to GObject
Reference.vi` -> To More Specific Class -> `FlatSequenceInnerTunnel.Left Terminal` 1C3A9000 ->
`Terminal.Connect Wire` 6349C03 -> `Terminal.Connected Wire` 634A000 -> `Wire.Is Broken?` 6371004) opens
references it never closes, and the measured 1.00 stray `Invoke` node minted per call adds a persistent
object to the target VI; +114 over 20 calls is therefore a real per-call leak in the op, and the op needs
a `Close Reference` repair before it is used."

ALSO ON FILE, and relevant:
* `docs/toolkit-capabilities.md:462` - "`OpReport_v3.vi`, `OpReportAll_v0.vi` and `OpWireSource_v5.vi`
  carry a traverse and **no `Close Reference`**".
* `docs/toolkit-capabilities.md:484-485` - "the kernel handle count is BLIND to VI Server refnums".
* `docs/toolkit-capabilities.md:460-478` - the S0 baseline the +-100 tolerance comes from.
* CLAUDE.md - "this LabVIEW 2026 install holds ~31,500 handles one minute after a fresh start; the first
  '32,480 = leak' diagnosis was WRONG; judge growth relative to that baseline, never the absolute number."
  In this run the 20 calls started at 42,471 - i.e. ~11,000 handles ABOVE the fresh baseline, after an
  op build that had already opened panels, run Remove Bad Wires and saved.
* The same run's phase [1] restarted LabVIEW: 33,950 -> 33,994 handles; after all the work 42,763; at
  exit, after a second restart, 33,998.
* v1 was called 20 times with `Auto Route?` TRUE on a scratch copy of the bed; the SAME 20 calls produced
  a perfect uid echo on both sides (term_uid 7488, uid_back 7468 on 20/20) - i.e. every call did the
  same work.
* The 12 failing gates of that run are otherwise all the GATE S measurement outcome (the method MERGES
  nets instead of replacing), not machinery.

WHAT I NEED FROM YOU, in this order:
1. The strongest reason the explanation above is WRONG.
2. At least one ALTERNATIVE explanation for +114 / 3.3 MB that does not require a leak in v1 - and say
   what in the file record supports it. Consider in particular: whether a +-100 tolerance is even a
   meaningful discriminator at a 42,471 starting point; whether the handle counter can attribute
   anything to an op at all given the "blind to VI Server refnums" line; whether the 20 calls in v1's
   test differ from v0's 20 calls in a way OTHER than the op (v0's arm ran on a scratch with wire 7506
   ALIVE and was a BRANCH; v1's 20 calls also ran wire-alive, but v1 additionally carries the
   `Auto Route?` control and a front-panel Boolean write per call).
3. WHAT WOULD FALSIFY the leak claim.
4. The CHEAPEST DISCRIMINATING TEST, runnable with tools this project already has (no new op, no new
   device), that separates "v1 leaks" from your alternative - state it as concrete steps with the
   numbers that decide.
5. Whether this failure should block the NEXT dispatch at all, given that the next dispatch's task is a
   READ-ONLY measurement (delete one wire on a scratch copy and ask whether a tunnel uid still resolves)
   followed by at most TWO calls of the same op - i.e. a workload 10x smaller than the one that produced
   +114. Say plainly if you think the gate is being applied at the wrong granularity.

ALREADY RULED OUT (do not spend your answer on these):
* Not the op's correctness: v1 reached ExecState 1 both at the save and re-read after it, and its two uid
  echoes held on 20/20 calls.
* Not a hung or killed client: refs 29 opened / 29 closed / 0 live at exit, and the run ended rc=1 from
  its own gate arithmetic, not from a timeout.
* Not the stray `Invoke` nodes being left behind: they were purged in-run (Node 635 -> 655 -> 635) and
  the scratch was deleted.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

I have what I need. Here is the review.

---

# The claim is wrong, and the strongest reason is that the two numbers being compared were not produced by the same experiment.

## 1. The single strongest reason the explanation is WRONG

**The metric cannot see the mechanism the explanation blames, and the project already measured and wrote that down.**

The explanation says v1 "leaks a handful of **VI Server references** per call" and that this is why the **kernel handle count** moved. Those are two different things, and the link between them is not weak — it is documented as absent, in this project's own audited source:

- `tools/gscript.py:227-228` — "The counters are IN-PROCESS and count this module's own VI Server references — they are **NOT the kernel handle count** (`bench_prep.labview_handles`), **which cannot see VI Server refnums at all**."
- `docs/toolkit-capabilities.md:484-485` — "the kernel handle count is **blind to VI Server refnums** … which is why G-C exists beside G-B."
- `tools/bench/bench_prep.py:64-67` — `labview_handles()` is literally `(Get-Process LabVIEW | Select-Object -First 1).HandleCount`, i.e. the Win32 count of handles to **kernel executive objects** (files, events, sections, threads, ALPC ports) — [GetProcessHandleCount](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocesshandlecount).

And the recipe that produced the failing gate **says this in its own gate text** (`build_d1_m3a3b_d3.py:554-556`, printed at `build_d1_m3a3b_d3.log:61`). The session wrote the refutation into the log line above the one it is now trying to explain.

**Second, independent kill — NI's refnum lifetime rule.** Even if a kernel handle were minted per refnum, a missing `Close Reference` *inside an op VI* cannot accumulate across calls, because each call is a complete top-level run of `OpFsInnerTunnelConnect_v1.vi` that then goes idle:

> "LabVIEW automatically closes a reference when the top-level VI that opened the reference goes idle" — [NI, Closing References in LabVIEW](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html)
> "Once the VI hierarchy that called the Open Reference goes idle, any reference is automatically closed … LabVIEW … controls the lifetime of its objects by the lifetime of the top level VI in whose hierarchy the Open call was done." — [NI Community](https://forums.ni.com/t5/LabVIEW/Labview-Auto-Close-VI-Reference/td-p/1988529)

So the proposed chain (`UID to GObject Reference.vi` → TMSC → `Left Terminal` → `Connect Wire` → `Connected Wire` → `Is Broken?` opening refs it never closes) is the one mechanism that is *structurally incapable* of producing a monotonic 20-call accumulation. Those refs die at the end of every call, by LabVIEW's own rule. Hygiene inside the op is a rule-compliance question (CLAUDE.md §3), not a candidate cause here.

**Third — the stray `Invoke` node is dead as evidence.** The explanation adds "the measured 1.00 stray `Invoke` node minted per call adds a persistent object." v0 minted **exactly the same 1.00/call** (`build_opfsinnertunnelconnect_v0.log:96-97`, node census 635 → 655) and passed at +94 with **0.03 MB**. An identical quantity in both arms cannot explain a difference between them.

## 2. The alternative explanation: the two 20-call windows are not the same workload — v1's window contains 80 extra traverse-op runs that v0's deliberately excluded

This is not a hypothesis about LabVIEW. It is a diff of the two recipes.

| | v0 arm | v1 arm |
|---|---|---|
| per-call function | `fsit_connect(...)`, `build_opfsinnertunnelconnect_v0.py:597`, **`count_wires=False` by default** and the call site at `:669` passes nothing | `fsit_call(...)`, `build_d1_m3a3b_d3.py:279` |
| `g.count(target,"Wire")` | `:602` — **skipped** | `:284` **and** `:337` — always |
| `g.count(target,"Invoke")` | none | `:285` **and** `:338` — always |
| **op-VI runs inside the measured window** | **20** (1/call) | **100** (5/call) |

`g.count()` is `gscript.py:1035-1044` → `op(OP_REPORT)` → **`OpReport_v3.vi`** (`gscript.py:62`), run with `Open VI Reference` on the target each time — a full `Traverse for GObjects` of a 307 KB, 653-node VI. `report_all`'s own docstring puts the fixed cost of that `Open VI Reference` at ~960 ms on a large VI (`gscript.py:505-507`).

**`OpReport_v3.vi` is one of the three ops `docs/toolkit-capabilities.md:462` names as carrying a traverse and no `Close Reference`.** The v1 window therefore contains 80 runs of a documented no-`Close Reference` traverse op; the v0 window contains zero. The explanation attributes the difference to the op under test while the harness around it changed by 5×.

And the v0 recipe **says it excluded them on purpose**, in a comment, at `build_opfsinnertunnelconnect_v0.py:677-678`:

> "NO census inside the loop, **on purpose**: a `report_all('Node')` on a 635-node VI **moves the very handle count this window is measuring**."

v1's recipe put four such traversals back inside the loop, per call. The donor's author identified this exact confound and engineered it out; the derived recipe reintroduced it and then read the result as a property of the op.

**The arithmetic runs the wrong way for a leak.** Per unit of LabVIEW work: v0 = 94/20 = **4.7 handles per op-VI run**; v1 = 114/100 = **1.14**. If op-VI runs leaked handles, quintupling them would have quintupled the delta, not raised it by 20. The delta is much closer to constant-per-*window* than constant-per-*run* — the signature of drift, not of a leak.

**On whether ±100 is a discriminator at all — it is not, and the fleet's own logs settle it.** The counter's routine dynamic range in this project, from `tools/bench/*.log`:

- `build_d1_routeb_v5_run8.log:17,38,431,441` — 31,130 → **51,353** ("with the copy open") → 35,555 → 50,709. **±16,000 inside one run**; merely having a VI copy open is worth ~20,000 handles.
- `build_d1_m3a2.log:24,51` — 30,689 → **45,677** in a single build (+14,988).
- `build_d1_m3a1.log:2722,3426` — 34,619 → **34,090**: a whole build ending **529 handles below** where it started. The counter goes *down*.

A ±100 window is **0.6 %** of what opening one VI costs on this install. v0 passed with **6 handles** of headroom out of 100. +94 and +114 are not "clean" and "leaking"; they are two draws from the same distribution, and neither run repeated the measurement even once, so the gate has **n=1 per arm and no variance estimate at all**.

**Two smaller defects in the same machinery, both worth fixing:**
- `bench_prep.py:61` — `HANDLE_LIMIT = 12000`, below the ~31,500 fresh baseline recorded in CLAUDE.md. `bench_prep.py:113` therefore restarts LabVIEW on **every** run; the "restart above the limit" mechanism always fires and discriminates nothing. This is the same error CLAUDE.md records as already made once ("judge growth relative to that baseline, never the absolute number").
- `labview_handles` uses `Select-Object -First 1`, while `build_opfstunnelterm_v1.py:204` uses `Measure-Object -Sum`. Two definitions of "the handle count" coexist; with a stray second LabVIEW process they disagree and `-First 1` picks arbitrarily.

**The 3.3 MB** is the one number with real signal in it, and it also points at the harness: 3.46 MB ÷ 80 extra `OpReport_v3` traversals ≈ 43 KB per traversal of a 307 KB diagram. It is a *memory* observation about traversals, and it should not be read as corroborating a *handle* claim — they are independent quantities, which is exactly why the project made private bytes a companion rather than a second gate.

**Where the evidence genuinely does not decide:** neither log records the wall-clock duration of the 20-call window. A time-proportional drift term therefore cannot be separated from a per-call term from the record as it stands. That is a gate design flaw, not an inference you can make either way.

## 3. What would FALSIFY the leak claim

Any one of these:

1. **v1 called 20× with the four `g.count()` calls removed lands within ±100** (≈ v0's +94). The delta was the harness.
2. **v0 called 20× *with* the counts added lands at ≈ +114.** Proof the counts, not the op, move the number.
3. **The delta does not scale linearly with call count.** A genuine per-call leak is linear: 100 calls must cost ≈ +570. If 100 calls of v1 (counts off) costs +150, there is no per-call term.
4. **An idle LabVIEW drifts comparably over the same wall-clock with zero calls.**

Conversely, the claim survives only if v1-with-counts-off still reads ≈ +114 *and* the delta is linear in call count *and* v0 under the identical harness reads ≈ +94. Short of all three, "v1 leaks" is not established — and even then it would be a kernel-object cost (threads/events/file handles from execution), **not** the refnum leak the explanation describes.

## 4. The cheapest discriminating test — existing tools, no new op, no new device

`tools/bench/diag_c83_connect2x2.py:267-268` **already** defines `fsit_call(op_path, …, count_wires=True)` — parameterised by op path *and* with the count pass behind a flag. Nothing new is needed.

One script, one fresh LabVIEW instance, one bed copy per arm, arms **interleaved** so drift is common-mode:

- **Arm N (null)** — read handles, `sleep` for the measured duration of one 20-call window, read again. *Zero LabVIEW work.*
- **Arm A** — 20 × v0, `count_wires=False` (reproduces the donor: expect ≈ +94)
- **Arm B** — 20 × **v1**, `count_wires=False` ← **the decisive arm**
- **Arm C** — 20 × v0, `count_wires=True`
- Repeat the block **3×** and report per-arm mean and spread. Log the window duration each time.

**The numbers that decide:**

| observation | verdict |
|---|---|
| **B ≈ A** (within the spread) | **v1 is exonerated**; the +114 was the harness. G2 re-run under v0's exact conditions is the acceptance record. |
| **C ≈ 114** | confound **proven** — the four `g.count()` calls are the cause, independent of which op is under test. |
| **B ≈ 114 while A ≈ 94** | v1 has a real per-call cost. Then run 100 calls: linear (+570) ⇒ per-call term; sub-linear ⇒ still not a leak. |
| **Arm N alone approaches ±100** | the gate is refuted as a discriminator regardless of every other arm. |

If only one thing can be run: **Arm N + Arm B**. N costs ~1 minute and zero LabVIEW work and can refute the gate on its own; B is the direct test of the claim.

## 5. Should this block the next dispatch? No — and the gate is being applied at the wrong granularity

Plainly: **no, it should not block, and the framing is a category error.**

G2 is CLAUDE.md's **acceptance criterion for admitting a new op to the fleet** ("A new op is accepted only if 20 runs leave the handle count flat"). It licenses the statement *"v1 is accepted"*. It is not a safety interlock on calling the VI. The next dispatch is a **read-only measurement** (delete one wire on a scratch copy, ask whether a tunnel uid still resolves) plus **at most two calls**. Taking the failing number at face value, 2 calls cost ≈ **11 handles** — against a ~31,500 fresh baseline and a within-run dynamic range of ±16,000. It is unmeasurable, on a scratch copy, with the originals untouched.

Blocking also inverts the cost structure: the cheap dispatch is the one that would generate the evidence to settle this, and it is the one being held.

The correct bookkeeping, and I'd push for both halves:

- **Do not block** the next dispatch.
- **Do not record v1 as accepted** either. G2's status is **UNRESOLVED — CONFOUNDED**, not PASS and not "leak found". The op is provisional until re-measured under v0's identical harness (Arm B).
- **Fix the gate before it is trusted again**: it must run its target under a *fixed* harness, contain no traverse calls inside the window, record the window duration, repeat ≥3×, and carry a null arm. Until then a G2 PASS means no more than a G2 FAIL does — note that v0's "+94 PASS" is, by this same argument, not evidence that v0 is clean.

---

**If you want me to reconsider:** show me Arm B landing at ≈ +114 with counts off, across ≥3 repeats, *and* a 100-call run at ≈ +570. Linear scaling under a fixed harness is the one pattern drift cannot produce, and I would accept a per-call cost on that evidence — though still not as the VI-Server-refnum leak the explanation describes, since NI's idle rule and `gscript.py:227-228` rule that specific mechanism out no matter what the counter does.

**One process note, since it bears on how this failure got framed:** the brief's "ALREADY RULED OUT" list includes "refs 29 opened / 29 closed / 0 live at exit." Those counters are `gscript.ref_counts()`, whose own docstring (`gscript.py:236-238`) says they "**CANNOT** see refnum-class exhaustion inside an op VI and **must never be cited as if a flat reading here excluded it**." It was cited in the rule-out list — in the opposite direction, but it is the same counter being read as more informative than its author documented it to be. That is the pattern behind this whole failure: three separate readings (`HandleCount`, `ref_counts`, private bytes) each carry an explicit written warning about what they cannot see, and the explanation was built by reading past all three.

**Sources:**
- [GetProcessHandleCount — Microsoft Learn](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocesshandlecount)
- [Closing References in LabVIEW — NI](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html)
- [LabVIEW Auto Close VI Reference? — NI Community](https://forums.ni.com/t5/LabVIEW/Labview-Auto-Close-VI-Reference/td-p/1988529)
- [Circumvent reference cleanup when VI ends? — NI Community](https://forums.ni.com/t5/LabVIEW/Circumvent-reference-cleanup-when-VI-ends/td-p/3873810)

## Sources

(extract from answer)

## What was done with it

Dispatched 2026-09-22 14:19 by the cycle-85 MATERIAL session as the mandatory failed-prediction review of
`tools/bench/build_d1_m3a3b_d3.log`'s first failing gate (G2, handles +114 vs ±100). ANSWERED in 366 s,
claude / `hypothesis` / opus effort max, $3.3578. Disposed in full, finding by finding.

**1. §1 — "the metric cannot see the mechanism the explanation blames". ACCEPTED, and the session's
explanation is WITHDRAWN.** The kernel handle count is blind to VI Server refnums
(`docs/toolkit-capabilities.md:484-485`, which this session cited in the same breath as the leak claim and
then argued past), and NI's refnum lifetime rule closes an op VI's own references when the top-level call
goes idle — so a missing `Close Reference` *inside* `OpFsInnerTunnelConnect_v1.vi` cannot accumulate
across calls at all. "v1 leaks references" is not a live hypothesis and is not carried forward anywhere.

**2. §1 third kill — the stray `Invoke` node is dead as evidence. ACCEPTED.** v0 minted the identical
1.00 stray `Invoke` per call (`build_opfsinnertunnelconnect_v0.log:96-97`) and passed at +94. An identical
quantity in both arms cannot explain a difference between them; the session had offered it as
corroboration.

**3. §2 — THE CONFOUND, and this is the finding that matters. ACCEPTED IN FULL.** The two 20-call windows
are not the same workload: v0's `fsit_connect` defaults to `count_wires=False`
(`build_opfsinnertunnelconnect_v0.py:597`, call site `:669`) so its window contains **20** op-VI runs,
while c84's `fsit_call` calls `g.count()` four times per call (`build_d1_m3a3b_d3.py:284/285/337/338`) so
its window contains **100** — 80 of them `OpReport_v3.vi`, one of the three ops
`docs/toolkit-capabilities.md:462` names as carrying a traverse and **no** `Close Reference`. The donor's
own comment at `build_opfsinnertunnelconnect_v0.py:677-678` says it excluded exactly these on purpose
("a `report_all('Node')` on a 635-node VI moves the very handle count this window is measuring"), and c84
put them back and then read the result as a property of the op. Per op-VI run the arithmetic runs
backwards for a leak: v0 4.7, v1 1.14.

**4. §2 — "±100 is not a discriminator at a 42,471 starting point". ACCEPTED and recorded as a fact, not
acted on.** The counter's routine range in this project is ±16,000 inside one run
(`build_d1_routeb_v5_run8.log:17,38,431,441`), +14,988 in one build (`build_d1_m3a2.log:24,51`), and −529
across a whole build (`build_d1_m3a1.log:2722,3426`). n=1 per arm, no variance estimate.

**5. APPLIED TO THIS CYCLE'S RECIPE, `tools/recipes/build_d1_m3a3b_d3b.py`** (written in the same turn,
before the answer landed, and checked against it afterwards): it carries **no ±100 handle gate at all** —
there is no G2, no 20-call loop, and no op is being admitted to the fleet, because `OpFsInnerTunnelConnect_v1.vi`
is used **as-is** and never rebuilt. Handles are read before the restart, after the work and at exit and
reported as FACTS only. The recipe does call `g.uids()` / `M.node_census()` around each connect, so by
§2's own argument its handle numbers are **window-level and not attributable per call** — that is stated
here rather than discovered later.

**6. §5 — "this should not block the next dispatch; the gate is at the wrong granularity". ACCEPTED as
reasoning; the block was lifted the ordinary way, by this exchange being ANSWERED.** `PEER_GUARD_OFF` was
never set and is never the answer. Recorded for judgement: the reviewer's point is that G2 is CLAUDE.md's
*acceptance criterion for admitting a new op*, not a safety interlock on calling one, and the next
dispatch makes at most four calls on scratch copies.

**7. NOT ACTED ON — three items, deliberately, because each is a change this material session does not
decide** (they are listed in the session's `OPEN:` line):
   - §2's two machinery defects: `bench_prep.py:61` `HANDLE_LIMIT = 12000` sits **below** the ~31,500
     fresh baseline, so `bench_prep.py:113` restarts LabVIEW on every run and the mechanism discriminates
     nothing — the same error CLAUDE.md records as already made once; and `labview_handles` uses
     `Select-Object -First 1` while `build_opfstunnelterm_v1.py:204` uses `Measure-Object -Sum`, two
     definitions of "the handle count" that disagree whenever a stray LabVIEW process exists.
   - §4's cheapest discriminating test (interleaved Arms N / A / B / C, 3 blocks, using the ALREADY
     PARAMETERISED `tools/bench/diag_c83_connect2x2.py:267-268` `fsit_call(..., count_wires=)` — no new
     op, no new device). It settles whether v1 is exonerated, and whether G2 is a discriminator at all.
     It is a different cycle's work and was not smuggled into a Row-D dispatch.
   - §2's note that neither log recorded the 20-call window's wall-clock duration, so a time-proportional
     drift term cannot be separated from a per-call term from the record as it stands — a gate design
     flaw, named and left for judgement.

**No claim from this review was taken as confirmation of anything.** Its §1/§2 refute this session's
explanation, and that is how it is recorded above: the leak claim is withdrawn, the confound is the
standing explanation, and the discriminating test that would settle it is unrun and flagged.
