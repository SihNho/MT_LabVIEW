# c88-reuse-stalepin

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.3020  in 24 / out 10454 / cache-create 104809 / cache-read 1271778  (114s, 21 turn(s))
- **date:** 2026-09-26 01:25:01
- **outcome:** ANSWERED (118s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim about the failed self-test tools/bench/selftest_errorlist_reuse_88.log (script tools/bench/selftest_errorlist_reuse_81.py).

OBSERVED (selftest_errorlist_reuse_88.log:3,16): 14 pass / 2 fail.
  R1 "real bed D1_k, unchanged md5 -> REUSE, OK, 22 items" got ('OK', 0 GUI calls, 35 items, extra []), and the REUSE line names
  errorlist_D1_l2_a1_20260925_235224_..._reuse.json (bed md5 51d9b8a3...), NOT the D1_k bed (md5 6cf5b077...).
  C1 "cycle card carries the bed {path, md5}" got bed = D1_l2_a1_20260925_235224.vi / 51d9b8a3..., expected D1_k_20260925_100155.vi.

CLAIM: both failures are a STALE FIXTURE in the self-test, not a fault in tools/errorlist_check.py or tools/cycle_runner.py.
  The self-test fed the LIVE STATUS.md text to run_hook()/write_cycle_card(); STATUS.md now names D1_l2_a1_20260925_235224.vi as the
  bed (docs/d1-loop12-17-split-plan.md Pre-decided 195(a), cycle 88), so both functions correctly followed STATUS to the new bed.
  The checker verdict itself (OK, 35 items, 0 extra) matches tools/bench/c88_reverdict.log:5 on the same read.
  Patch already made (selftest_errorlist_reuse_81.py:87-91): status text pinned to "current-bed: D1_k_20260925_100155.vi\n"
  (errorlist_check.py:166, `current-bed:` wins).

Also planned in the same card (Pre-decided 195(b), "no uncapped licence for a bed with an explicit file"):
  errorlist_check.py derive_expected():375-377 still appends an UNCAPPED wire_from_open_rows licence (count None) even when an
  explicit expected file (errorlist_expected_<stem>.json) exists; explicit entries consume first, so here it absorbed 0, but a new
  loose-ends fault would be silently absorbed. Planned edit: skip derived licences when an explicit file exists (both call sites,
  reverdict():223-225 and main():456-461), plus a new negative self-test (explicit file + 1 extra "wire has loose ends" item -> MISMATCH).

Questions to attack: Is the stale-pin explanation wrong or incomplete (e.g. does current_bed() resolution or write_cycle_card read
something other than the status text passed in, so pinning the text would not isolate the test)? Could R1's 35-vs-22 reflect a
real reuse-selection bug (wrong newest read chosen) rather than the bed change? Does dropping ALL derived licences (not only the
uncapped wire class) when an explicit file exists break a bed whose explicit file is partial? Name the cheapest discriminating test.
Read-only; do not edit files.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

The claim is **partly wrong**. Both self-test failures do come from a stale fixture, and pinning the status text does isolate the test. But the claim's reason, that "STATUS.md now names D1_l2_a1 as the bed, so both functions correctly followed STATUS", is false. The bed was chosen by **newest file time**, not by anything STATUS decides, and that fallback will move the runner to the wrong bed again.

## 1. Strongest reason the claim is wrong

- **STATUS.md has no `current-bed:` line.** A grep for `^current-bed` finds 0 matches.
- **So the fallback at `tools/errorlist_check.py:167-170` decided the bed.** It collects every `D1_*.vi` name in STATUS, keeps the ones that exist in claudeDev, and returns the one with the newest mtime (`max(paths, key=os.path.getmtime)`).
- **STATUS names about 17 D1 files.** They are on lines 10, 11, 50, 54, 62, 88 and 93. `D1_k_20260925_100155.vi` is still named as a bed on line 93 ("THE L2-A1 run from the bed `claudeDev\D1_k_…`").
- **`D1_l2_a1` won on file time only.** It lines up with Pre-decided 195(a) by coincidence; nothing in the code reads 195(a).
- **The same fallback is live in production.** It feeds `errorlist_hook` (`tools/cycle_runner.py:685`) and `write_cycle_card` (`tools/cycle_runner.py:749`).
- **A newer D1 file already exists.** `claudeDev\D1_s1_kswap_20260926_004935.vi` is on disk. Pre-decided 195(d) also plans another instrumented copy of the S1 file. As soon as STATUS names either one, the cycle-start check and the cycle card switch to that file:
  - It is runnable (ExecState 1), so a GUI read returns 0 items and the verdict is OK.
  - The L2-A1 bed would then silently stop being checked.
- **Pinning the text in the self-test hides this; it does not fix it.** The self-test was the only thing that noticed the bed had moved.

## 2. Alternative explanation of the same evidence

"The runner's bed is chosen by file time, not by decision, and the self-test is the only thing that noticed." The log (`tools/bench/selftest_errorlist_reuse_88.log:2,16`) looks identical under the claim and under this reading. They predict different things for the next new D1 file STATUS mentions.

## 3. What would falsify the claim

If STATUS gained a line naming `D1_s1_kswap_20260926_004935.vi` and `current_bed_text` still returned `D1_l2_a1`, the claim would hold. The code at `tools/errorlist_check.py:166-170` says it will return the kswap file instead. I did not run this (read-only).

## The three sub-questions

- **Does pinning isolate the test? Yes.**
  - Both functions take `status_text` as an argument. `current_bed_text` is pure apart from the claudeDev directory and file times.
  - `write_cycle_card` reads `<bench>/bed.json` first, and the test's bench is an empty temp directory.
  - `D1_k_20260925_100155.vi` still exists in claudeDev.
  - R1 still depends on the real bench. That is fine: the latest D1_k re-verdict (`errorlist_D1_k_20260925_100155_20260925_223239_reuse.json`) is OK with 22 items and 0 extra. Its items are licensed only by `subvi_input_not_wired`, `node_unwired`, the header rule and the four wire classes left after the revert. So the cycle-87 revert does not break R1.
- **Is 35 vs 22 a reuse-selection bug? No.**
  - `find_reusable` globs by the bed's name stem and checks the basename (`tools/errorlist_check.py:187-195`).
  - The 35 items belong to the L2-A1 read `…_001456`, the same read and verdict as `tools/bench/c88_reverdict.log:3-5`.
  - The wrong input was the bed, not the choice of read.
- **Does dropping all derived licences break a bed with a partial explicit file?**
  - Explicit entries are required with exact counts (`tools/errorlist_check.py:393,407`). A partial file therefore produces extra items and a MISMATCH. That fails loudly, which is the safe direction.
  - Today only one explicit file exists, and it is complete: 35 of 35 used, derived licences 0 (`tools/bench/c88_reverdict.log:16`).
  - Two caveats:
    - (a) 195(b) does not literally say "no derived licences when an explicit file exists". That wording appears only in `tools/bench/cards/task_88-4.json:6`. Dropping the capped `node_unwired` and `subvi_input_not_wired` licences goes further than 195(b). It is defensible, but it is an interpretation and should be labelled as one.
    - (b) `missing` is built from `e.get("match")` (`tools/errorlist_check.py:407`). The explicit file uses `norm_all` entries, so every missing entry would print as `None`. The verdict is still correct, but the report is unreadable.
- **The planned negative self-test can pass without testing anything.** With current code, a 15th "Wire has loose ends" item is absorbed by the uncapped `wire_from_open_rows` licence only if `plan_for_bed` finds `sim/l2a1/stageplan_l2a1.json`. A fake bench without that plan gives no derived licences, so the test reports MISMATCH on both the old and the new code. The test must first be run against the unpatched checker and shown to get OK. It needs the real bench, or a copy of `stage_d1_l2a1.json` plus the sim plan.

## 4. Cheapest discriminating test

Offline, no LabVIEW, about one second:

```
py -c "import sys; sys.path.insert(0,'tools'); import errorlist_check as E; t=open('STATUS.md',encoding='utf-8').read(); print(E.current_bed_text(t)); print(E.current_bed_text(t+'\nD1_s1_kswap_20260926_004935.vi\n'))"
```

- **If the claim is right:** both lines print `D1_l2_a1`.
- **If my alternative is right:** the second line prints `D1_s1_kswap…`.

If the second line prints the kswap file, the fix belongs in STATUS and the runner, not only in the self-test:
- Write `current-bed: D1_l2_a1_20260925_235224.vi` into STATUS; the mechanism already exists at `tools/errorlist_check.py:166`.
- Log a warning, or refuse, whenever the mtime fallback is what picked the bed.

No web search was needed. Every claim here is about this project's own Python and is cited by file and line.

## Sources

(extract from answer)

## What was done with it

Outcome: the review was ANSWERED and partly REFUTED the claim. Card 88-4 (material session), 2026-09-26 01:2x.
- The cheapest test was run offline. `current_bed_text(STATUS)` returned D1_l2_a1. After appending the name `D1_s1_kswap_20260926_004935.vi` to that text, it returned the kswap file. The **alternative is confirmed**: the bed is picked by newest mtime (errorlist_check.py:167-170), not by a `current-bed:` line. The self-test fix (pinning the status text) still stands. The production fix is not part of card 88-4 (status_edit false); it is passed on as an OPEN judgement item: write `current-bed:` into STATUS, and/or warn or refuse on the mtime fallback.
- Caveat (a) was accepted and labelled. errorlist_check.py reverdict() and main() now drop ALL derived licences when an explicit file exists; the code comment calls this an interpretation of PD195(b).
- The review said the negative test must discriminate (:92). It was built on the real bench, where the plan is found (`sim/l2a1/plan_l2a1.json`). Control N1c: the old rule absorbs the extra item, so extra is []. N1 with the new rule gives MISMATCH with extra ['Wire: Wire has loose ends.'] (tools/bench/selftest_errorlist_reuse_88b.log:17-18).
- Caveat (b) was not acted on, because card 88-4 allows changing only the derived-licence condition. `missing` prints None for norm_all entries.
- Reruns: the reuse self-test passed 18/0, the header self-test 5/0, and c88_reverdict 6/0 (OK, 0 extra, 0 missing, derived []).
