# c93-h1-stamp-array-copy

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.3040  in 10 / out 7820 / cache-create 129150 / cache-read 457354  (92s, 10 turn(s))
- **date:** 2026-09-26 10:19:29
- **outcome:** ANSWERED (96s)
- **verdict-card:** VERDICT-CARD 93-h1 verdict=refuted -> tools\bench\cards\verdict_93-h1.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id 93-h1, role hypothesis) ---
CLAIM: In t0at (S1 copy + 12 any-thread CLFN stamps, each fed by a BRANCH of an existing wire), the ~110 extra lost frames/120 s at 8 beads come from stamps branching LARGE-ARRAY wires: the shared buffer forces a per-frame array copy. Scalar-wired stamps don't. Test: wire types -> scalar-only copy -> ABBA.
PREDICTED: Stamps cost only their call cost (0.3-1.4 us x 12/iteration; a 1024x1280 U16 branch showed no copy on a scratch VI), so a stamped copy loses about what unstamped S1 loses; then, any-thread CLFNs should remove the extra loss if it was UI-thread switching.
OBSERVED: ABBA, 8 picks, 120 s, 90 Hz: unstamped S1 lost 20/22; any-thread stamped 130/131; UI-thread stamped (earlier) 138/144. Stamped tracking period median 11.16-11.18 ms vs camera 11.11 ms: ~50 us/iteration extra, which 12 x <=1.4 us cannot explain.
ALREADY RULED OUT: UI-thread switching as the main cause: any-thread copy still loses 130/131 (tools/bench/cards/result_92-3.json, tools/bench/m8_anythread8_92.json)
ALREADY RULED OUT: harness first-click loss as a stamp effect: it occurs 2/2 on unstamped legs too and all 4 ABBA legs registered 8/8 after the capture-release fix (docs/d1-loop12-17-split-plan.md PD199 measured block)
ALREADY RULED OUT: the stamp call cost itself: 0.30 us per stamp, 1.40 us with a 1024x1280 U16 branch on a scratch VI (tools/bench/diag_c90_t0stamp_scratch_r3.log)
ATTACHMENT: docs/d1-loop12-17-split-plan.md (md5 None)
ATTACHMENT: tools/bench/cards/result_92-3.json (md5 None)
ATTACHMENT: tools/bench/m8_anythread8_92.json (md5 None)
ATTACHMENT: tools/bench/t0_sites_s1.json (md5 None)
ATTACHMENT: tools/t0stamp/t0stamp.c (md5 None)
--- END REVIEW CARD ---

Refute the claim in the attached review card. The attachments it lists are readable in the project directory.

--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"93-h1","verdict":"<one of: refuted | supported | unverified>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

**I think the claim is wrong.** The large-array-copy idea is only one hypothesis, and it doesn't fit the shape of the recorded data. A more likely cause is built into the stamp DLL itself, and it can be checked offline for free before any new LabVIEW build.

## 1. The strongest reason the claim is wrong

**The stamp DLL blocks the tracking loop for a synchronous disk flush about every 11 s, and the loop's stalls look like that.**

- **The flush is in the call path.** In `tools/t0stamp/t0stamp.c:74-78`, every 1024th `stamp()` call runs `WriteFile` and then `FlushFileBuffers` (`:61-62`). This happens inside the calling thread. In the any-thread copy, that thread is the tracking loop's.
- **All six tracking sites flush in the same iteration.** Sites 00/02/03/04/06/08 each fire once per iteration: 10983 stamps each in `m8_anythread8_92.json:425-430`. So all six reach their 1024th stamp together, and one iteration pays six serial disk flushes. That happens about 10 times per 120 s leg.
- **The files go to a real disk.** The `.bin` files land in the leg folder on `G:` (the Glob shows `tools/bench/t0_legs/.../leg2_B_p8_a1/*.bin`). `FlushFileBuffers` stalls are well documented, at about 10 ms per flush on higher-latency disks ([boltdb #516](https://github.com/boltdb/bolt/issues/516)).
- **The size matches.** 10 events costing about 11 frames each (roughly 120 ms of stall) gives the observed ~110 extra lost frames.
- **The long gaps are in the data.** The tracking period max is 211.8 ms in leg 2 and 156.6 ms in leg 3 (`m8_anythread8_92.json:1008, 1219`). Site deltas reach 62–176 ms (`:1023-1099`).
- **The scratch test never saw this.** It ran only n=1100 calls on isolated sites (`diag_c90_t0stamp_scratch_r3.log:91-93`): at most one flush, and it reported only the median and p99. That hides one stall in 1100 by construction. The same log's ruling-out of "the stamp call cost itself" was a median result, so it doesn't reach this.

**The "~50 µs per iteration extra" premise is also not measured.**
- Arm A has no stamps, so it has no period data. The comparison is against the nominal 11.11 ms, not against A.
- Both arms actually ran at a measured 88.9 fps (`result_92-3.json:19`), which is 11.25 ms per frame.
- The tracking loop did 10983 iterations in 123.4 s, a mean of 11.24 ms. So the loop is paced by the camera. Its 11.16 ms median is *below* the real frame period; the gap between median and mean comes from tail stalls, not from a per-iteration cost.
- A per-frame copy of a 2.6 MB array would push the whole distribution up. What the data shows is a mostly normal loop with rare long gaps.

## 2. Alternative explanations

- **(a) Periodic flush stalls, as above.** This also explains why the UI-thread copy (138/144) and the any-thread copy (130/131) lose about the same. The flush costs the same whichever thread makes the call.
- **(b) The in-place copy is real, but on a different wire.** A CLFN's Adapt-to-Type parameter that isn't marked Constant can force LabVIEW to copy a branched buffer. The only large-looking tracking wires are `Filtered X` and `X out` (`t0_sites_s1.json:486-490, 690`). But a per-frame copy would raise the median, and it didn't. That makes (b) weaker than (a).

## 3. What would falsify the claim

The claim fails if the long tracking-period gaps (say over 30 ms) sit at site-00 iteration indices of about 1023, 2047, 3071, … (±1). That would mean the loss follows the flush schedule, not the array wires. The claim fails again if a scalar-only copy still loses about 130 frames.

## 4. Cheapest discriminating test (no LabVIEW, no build)

1. Read the existing `t0_site00_pid26352.bin` and `pid26424.bin` (int64 values: the QPC frequency first, then the counts).
2. Compute the per-iteration periods and list the indices of the top ~15.
3. Check whether they fall at `k·1024−1`.

If they cluster there, the fix is to take `FlushFileBuffers` out of `stamp()`, or to write from a background thread and stagger sites so their chunks don't close together. Then rerun ABBA.

Only if the gaps turn out *not* to align with the flushes is the planned scalar-only build (`d1-loop12-17-split-plan.md:1210-1211`) worth a LabVIEW run.

VERDICT {"schema":"verdict/1","id":"93-h1","verdict":"refuted","alternative":"t0stamp.c:74-78 runs WriteFile+FlushFileBuffers in the tracking thread every 1024th stamp; 6 lockstep sites flush in the same iteration ~10x per leg -> ~120 ms stalls (period max 211/156 ms) ~= 110 extra lost frames. Median 11.16 ms < measured 11.25 ms frame, so no per-frame copy.","discriminating_test":"Offline: read existing leg2/leg3 t0_site00 .bin, list the top-15 period outliers; if their iteration indices sit at k*1024-1 (+/-1), the flush is the cause, not array copies. No LabVIEW run.","violations":[],"sources":["tools/t0stamp/t0stamp.c:61-62,74-78","tools/bench/m8_anythread8_92.json:425-430,1008,1219","tools/bench/cards/result_92-3.json:19","tools/bench/diag_c90_t0stamp_scratch_r3.log:91-94","https://github.com/boltdb/bolt/issues/516"],"note":"The 50us/iter excess is measured against nominal 11.11 ms, not arm A (unstamped, no period data); the real frame period is 11.25 ms. The scratch test (n=1100, median/p99) could not see a once-per-1024 stall."}

## Sources

(extract from answer)

## What was done with it

ACCEPTED by the cycle-93 judgement session (2026-09-26). §1 was checked against the source: `tools/t0stamp/t0stamp.c:61-62` (`WriteFile` + `FlushFileBuffers`) runs inside `stamp()` at `:74-78` on every 1024th call per site, in the caller's thread. The array-copy candidate is set aside and the scalar-only build (PD199(f) 2) is deferred. Decision `docs/d1-loop12-17-split-plan.md` Pre-decided 200, card `tools/bench/cards/task_93-2.json`:
- (1) the §4 offline alignment test;
- (2) `t0stamp` v2: no file I/O in `stamp()`, a preallocated per-site buffer, and the write at process detach; the v1 DLL is kept as a byte copy;
- (3) ABBA at 8 picks, S1 against t0at running on v2, under PD199(c)'s criterion.
The flush is fixed whatever (1) shows: a synchronous disk flush inside a timing probe is an instrument defect in its own right. §1's point that the "~50 µs/iteration" premise was measured against the nominal rather than the real frame period is accepted too.
