# hyp-selftest-elreuse-81

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $0.9728  in 18 / out 7500 / cache-create 82342 / cache-read 768857  (90s, 13 turn(s))
- **date:** 2026-09-25 11:55:03
- **outcome:** ANSWERED (94s)
- **verdict-card:** VERDICT-CARD hyp-selftest-elreuse-81 verdict=refuted -> tools\bench\cards\verdict_hyp-selftest-elreuse-81.json
- **why asked:** failed prediction in tools/bench/selftest_errorlist_reuse_81.log (C1, K6), JEV-LADDER new-problem p=0.612; card 81-3 R1
- **verdict:** partly confirmed by measurement (C1 self-test bug; K6 hid a real guard_card hole)

## Question

--- REVIEW CARD (review/1, id hyp-selftest-elreuse-81, role hypothesis) ---
CLAIM: Both gate failures in selftest_errorlist_reuse_81.log are defects of the self-test itself, not of the code under test: C1 passed effort 'e' to write_cycle_card (schema rejects), K6 asserted a refusal for a nonexistent foreign path that protocol cannot scan.
PREDICTED: 15/15 gates PASS: C1 cycle card carries bed {path, md5}; K6 foreign stagexec.py path refused by guard_card.
OBSERVED: 13 pass / 2 fail: C1 -> "$.effort: 'e' not in [low..max]", bed None; K6 -> decide() returned no refusal (None) for py C:/elsewhere/tools/stagexec.py selftest.
ALREADY RULED OUT: C1: cycle_runner bed fallback absent - result_81-1 E1 cites cycle_runner.py:592 current_bed_text + md5 fallback; the card was never written because schema validation failed first on effort
ALREADY RULED OUT: K6: exemption too wide - pure_selftest() (guard_card.py:51-60) accepts only tools/stagexec.py or this project's abs path; the None came from protocol having no source file to scan
ATTACHMENT: tools/bench/selftest_errorlist_reuse_81.log (md5 e03740e803139e08a0d1dee13fa76c9d)
ATTACHMENT: tools/bench/selftest_errorlist_reuse_81.py (md5 57c8d944fe10f1742f55890fc83a4e7a)
ATTACHMENT: tools/hooks/guard_card.py (md5 1865c9843efa78317d6f1b5250fd696e)
ATTACHMENT: tools/cycle_runner.py (md5 1e48ceb961e40246ffb258349b89c6ad)
--- END REVIEW CARD ---

Failed prediction: `tools/bench/selftest_errorlist_reuse_81.log` ended 13 PASS / 2 FAIL (C1, K6).

Hypothesis under attack (see the review card above): both failures are bugs in the self-test, not in
`tools/cycle_runner.py` `write_cycle_card` (bed field) or in `tools/hooks/guard_card.py` `pure_selftest` /
`decide` (the stagexec self-test exemption).

Files: the log, the self-test (`tools/bench/selftest_errorlist_reuse_81.py`, lines 127-164 are C1 and K*),
`tools/hooks/guard_card.py` lines 36-80, `tools/cycle_runner.py` (search `def write_cycle_card`, and the bed
fallback near line 560-600), `docs/protocol/cycle.json` (the effort enum).

Questions:
1. Does the old C1 call really pass effort 'e' (argument order vs `write_cycle_card`'s signature), and with a
   valid effort would `write_cycle_card` actually emit bed {path, md5} of D1_k_20260925_100155.vi when
   tools/bench/bed.json is absent? Or is there a second defect hidden behind the schema error?
2. K6: with a foreign path `C:/elsewhere/tools/stagexec.py`, is `decide()` returning allow a defect of guard_card
   (a real foreign stagexec.py that does exist would then be exempted?) or only an artefact of protocol having no
   source file to scan? Does replacing K6 with K8 (testing `pure_selftest` directly) leave any path uncovered?
3. The cheapest test that separates "self-test bug" from "code bug" for each gate.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"hyp-selftest-elreuse-81","verdict":"<one of: refuted | supported | unverified>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

**Verdict: partly refuted.** C1 is a self-test bug, as claimed. K6 is also a self-test bug, but it hides a real hole in `guard_card`'s exemption, and replacing K6 with K8 does not cover that hole.

## 1. The strongest reason the claim is wrong (K6)

"The None came from protocol having no source file to scan" is true, but it is not the end of the story.

- **Why K6 could never test the matcher.** `protocol._launched_scripts` scans only paths where `os.path.isfile(_abs(p))` is true (`tools/protocol.py:479-487`). A path that does not exist is never scanned, so protocol allows the command. `decide()` only looks at `pure_selftest` when protocol has refused on `flags.labview` (`tools/hooks/guard_card.py:72`). So K6 would have returned 0 whatever `pure_selftest` did. The claim is right that this is a test design defect.
- **The real hole.** `_abs()` resolves relative paths against ROOT and ignores any `cd` (`tools/protocol.py:455-456`). The exemption regex, meanwhile, accepts `cd <any dir> &&` followed by the relative `tools/stagexec.py` (`guard_card.py:44,57`). Take this command:
  `cd "C:/elsewhere" && py tools/stagexec.py selftest`
  1. Protocol scans the project's own `stagexec.py` and refuses on `flags.labview`.
  2. `pure_selftest` returns True, so `decide()` exempts the command.
  3. The shell actually runs `C:/elsewhere/tools/stagexec.py`, a foreign file that was never scanned.

  That is exactly the "foreign stagexec.py" case K6 was meant to cover, and `guard_card` lets it through. The `guard_card.py:36-41` comment says the exemption is "never by filename". In the `cd` form it is effectively by filename.
- **What K8 misses.** K8 tests `pure_selftest` directly, and only with an absolute foreign path and the project's absolute path (`selftest_errorlist_reuse_81.py:162-164`). K2 checks `cd` only with ROOT. So the `cd <foreign> && py tools/stagexec.py` path is uncovered.
- **The same `cd` blindness in protocol.** It affects every relative script, not just this exemption: `cd X && py y.py` gets its source scan from ROOT/y.py, or no scan at all if that file is absent. That is outside this card, but it is the same fail-open pattern.

## 2. Alternative explanation of the same evidence

- **K6:** the observation is equally consistent with "`guard_card` has a real foreign-path hole and K6 was too blunt to show it". The logged None tells the two apart for the absolute form only; nothing tested the `cd` form.
- **C1:** "a second defect hidden behind the schema error" is possible in principle. I checked and found nothing likely:
  - With a valid effort, the fallback calls `EC.current_bed_text(status_text)` (`tools/cycle_runner.py:595-602`). That is the same resolver the errorlist hook uses. R1 got md5 `6cf5b077…` from it on the same STATUS text in the same run (log line 2), so the fallback should give that path and md5.
  - `hashlib` is imported (`cycle_runner.py:41`).
  - `protocol._rel` catches the cross-drive `ValueError` for the temp dir on C: against ROOT on G: (`protocol.py:72-77`). Python raises that error when path and start are on different drives (https://docs.python.org/3/library/os.path.html). The absolute path it falls back to is well under the 400-character limit.
  - The md5 matches the pattern in `docs/protocol/cycle.json:30`.
  - I could not confirm how the old call produced `'e'`, whether a placeholder argument or shifted arguments. The file on disk already has `"medium"` at line 130, and the older source is untracked and gone. Only the log's message is left.
- **C1 residual risk:** the fallback swallows every exception and leaves `bed` null (`cycle_runner.py:601`). If the rerun fails, the log will give no reason.

## 3. What would falsify the claim

- **K6 part:** `decide()` returning 0 for `cd "C:/elsewhere" && py tools/stagexec.py selftest` on the labview:none card 81-1. By the code above, I predict it does.
- **C1 part:** the rerun with `"medium"` still getting `bed` None, or an md5 other than `6cf5b077…`.

## 4. Cheapest discriminating tests

These are for the executing session to run; I have run nothing.

- **K6:** add one gate: `dec('cd "C:/elsewhere" && py tools/stagexec.py selftest')` and expect rc 2. If it returns rc 0, the defect is in `guard_card`.
  - Fix options: accept the `cd` prefix only when its directory normalises to ROOT, or drop the `cd` alternative from `PURE_SELFTEST_RE`.
  - Also add an end-to-end gate: `decide()` refusing an existing foreign `stagexec.py` (a temp file that imports `gscript`, run by absolute path).
- **C1:** rerun the self-test as it is now on disk (line 130 already passes `"medium"`). Pass means C1 was only a self-test bug. If it fails, temporarily log the exception at `cycle_runner.py:601`.

VERDICT {"schema":"verdict/1","id":"hyp-selftest-elreuse-81","verdict":"refuted","alternative":"C1 is a self-test bug, but K6 hides a real guard_card hole: the exemption regex accepts `cd <any dir> && py tools/stagexec.py selftest` while protocol._abs resolves against ROOT and ignores the cd, so a foreign stagexec.py gets exempted. K8 does not cover this.","discriminating_test":"Add gate dec('cd \"C:/elsewhere\" && py tools/stagexec.py selftest') and expect rc 2 on card 81-1; rc 0 means a guard_card defect. Rerun C1 with effort 'medium' and expect bed md5 6cf5b077 for D1_k_20260925_100155.vi.","violations":[],"sources":["tools/hooks/guard_card.py:44","tools/hooks/guard_card.py:57","tools/hooks/guard_card.py:72","tools/protocol.py:455-456","tools/protocol.py:479-487","tools/cycle_runner.py:595-602","tools/bench/selftest_errorlist_reuse_81.py:162-164","https://docs.python.org/3/library/os.path.html"],"note":"C1 part of the claim holds (the schema rejected effort 'e' before bed was used; the fallback resolver is the same one R1 used successfully). K6 part holds only for the nonexistent absolute path; the cd-relative foreign path is exempted by the code as written."}

## Sources

(extract from answer)

## What was done with it

- Ran both discriminating tests (material session, card 81-3), `tools/bench/selftest_errorlist_reuse_81_r2.log`, 16 PASS / 0 FAIL, `BGRUN END rc=0`.
- **C1 ACCEPTED as a self-test bug:** with effort "medium" the cycle card carries bed `{D1_k_20260925_100155.vi, md5 6cf5b0777aafa12112d8a786a9eed1ed}` with no bed.json. No second defect.
- **K6 finding ACCEPTED, measured:** gate K9 (`tools/bench/selftest_errorlist_reuse_81.py`) sends `cd "C:/elsewhere" && py tools/stagexec.py selftest` through `guard_card.decide` on the labview:none card 81-1. It returns rc 0 (exempted). The review predicted exactly that. K9 records the hole as known; it does not assert a fix.
- **NOT fixed here:** card 81-3's write flags exclude `tools/hooks/`. The guard_card fix (accept `cd` only when it normalises to ROOT, or drop the `cd` alternative from `PURE_SELFTEST_RE`) is left OPEN for the judgement session. The review's end-to-end foreign-file gate is left open too.
