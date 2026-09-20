# stall-selftest-c39-g78b

- **agent:** gemini
- **role:** (n/a)
- **model:** (agy default, not readable) (agy built-in default)
- **kind:** review
- **cost:** 
- **date:** 2026-09-19 04:54:05
- **outcome:** ANSWERED (24s)
- **why asked:** Mandatory failed-prediction review for the 4 PASS / 4 FAIL run of the `lv_stallcheck.ps1:273` repair self-test (`tools/bench/repair_c39_stall_selftest.log`). Claim under attack: the four FAILs are a case-sensitive assertion bug in the test, not a behaviour defect in the repaired watchdog. First dispatch (`…-stall-selftest-c39-g78.md`) came back ERROR — agy auto-denied `read_file` headless, the known closed failure documented in `archive/peer/2026-08-28-perm-allowlist-test7.md:40`; re-dispatched with an inline-only brief.
- **verdict:** unverified

## Question

DO NOT OPEN ANY FILE. You have no file-read permission in this headless session; any read_file call aborts your answer with no output. Every fact you need is quoted inline below. Paths and line numbers are given only as labels, never as things to fetch. Answer purely by reasoning over the text below.

A self-test gate failed and I claim the failure is in the TEST, not in the code under test. Attack that claim.

CONTEXT: `tools/lv_stallcheck.ps1` is a watchdog that writes a gating record `tools/bench/stall_pid<N>.log` when it believes a LabVIEW client is stalled. Its measured precision is 0 of 6 — all six records were written while the job was alive and finished normally, and each record blocks the next build until a paid peer review clears it. The authorised repair is ONE line at `tools/lv_stallcheck.ps1:273`: write the record ONLY when the dialog check returns `VERDICT: BLOCKED`; otherwise `$record` is set to the string `NOT WRITTEN - the dialog check did not return VERDICT: BLOCKED ...`.

OBSERVED in `tools/bench/repair_c39_stall_selftest.log`: 4 PASS / 4 FAIL. Lines `:48-:49` directly measured both behaviours of the repaired line — a clear run left NO record on disk, and a `MODAL DIALOG PRESENT` run DID write one carrying `STALL:` and `dialog: MODAL DIALOG PRESENT`. The four FAILs are gates G2/G3/G7/G8, whose assertion looked for an UPPER-CASE marker while, with no record written, the marker survives only inside the advisory message as a LOWER-CASED bgrun job-log name. Verbatim: `-> FAIL G7 'no modal dialog' writes NO gating record (the leaf IS still flagged in the message) | flagged=False, record_exists=False; message says NOT WRITTEN`.

MY CLAIM, which you should try to break: the repair is correct as measured at `:48-:49`, and G2/G3/G7/G8 failed on their own case-sensitive assertion string, not on the watchdog's behaviour.

ALREADY RULED OUT: simply re-running the fixed self-test — the case fix is applied, but `guard_peer` refuses the launch while this failing log is the newest record. That is why you are being asked.

QUESTIONS:
1. Give the strongest reading under which G7's `flagged=False` is a REAL defect of the repaired watchdog rather than of the assertion: if a leaf is no longer flagged when there is no modal dialog, has the repair silently removed a capability the watchdog was meant to keep?
2. Name one way the `:48-:49` observation can be true and the repair still wrong in production — in particular any path where `$record` is consumed as a FILE PATH after being set to the string `NOT WRITTEN - ...`.
3. What is the cheapest test that discriminates "assertion bug" from "repair bug" WITHOUT running LabVIEW?


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

The claim that the defect lies entirely in the test's case-sensitivity is **unfounded and dangerous**. The evidence indicates that the repair altered the watchdog's output contract and conflated "suppressing a gating file" with "suppressing stall detection."

---

### 1. The Single Strongest Reason the Claim is WRONG

**The repair breaks the watchdog's core contract by conflating modal dialog detection with stall detection.**

A LabVIEW worker can hang in two distinct ways:
1. **Blocked by UI:** A modal dialog halts the UI thread (`VERDICT: BLOCKED`).
2. **Deadlocked / Frozen in Engine:** An infinite loop, COM deadlock, or ActiveX thread lockup where **no dialog appears**, but the worker is dead.

Gate G7 explicitly specifies: `'no modal dialog' writes NO gating record (the leaf IS still flagged in the message)`. 
The test was explicitly written to enforce that when no dialog is present, the watchdog must **still flag the leaf** as stalled/suspect in its telemetry/advisory message while refraining from dropping a hard build-blocking file on disk. 

The repair at line 273 silenced the flag entirely (`flagged=False`). Treating `flagged=False` as a casing bug misinterprets the requirement: the watchdog has been demoted from a process stall detector to a simple modal-dialog detector, blinding the rig to engine deadlocks.

---

### 2. Alternative Explanations of the Same Evidence

1. **Type Poisoning of `$record` (Truthy String vs. Null/Path):**
   In PowerShell, assigning `$record = "NOT WRITTEN - ..."` turns a variable originally typed as a file-path-or-null into a **truthy string** (`[bool]$record -eq $true`). Any downstream code or test harness asserting:
   ```powershell
   if ($record) { ... }
   ```
   evaluates to `$true` even when no record was written. If the test runner inspects `$record` or expects `$null` / an empty string on non-blocking runs, setting it to an arbitrary prose message breaks consumer contract assumptions.

2. **Unparseable Leaf Telemetry:**
   The assertion in G7 looks for the leaf identifier in the watchdog's report/message. The repair replaced the leaf-flagging message block with the literal string `NOT WRITTEN - the dialog check did not return VERDICT: BLOCKED ...`. In doing so, the leaf PID/name was dropped or moved into an unparseable format, causing the parser to return `flagged=False`.

---

### 3. Observations that Would FALSIFY the Claim

1. **Offline Regex Re-evaluation Remains `False`:** 
   Evaluating the assertion logic of G7 against the verbatim log output using case-insensitive matching (`-match` / `(?i)`) **still returns `flagged=False`**.
2. **Downstream Path Resolution Exception:** 
   Any consumer passing `$record` to `Test-Path`, `Get-Item`, `[System.IO.File]::Exists()`, or `Remove-Item` throws:
   `System.ArgumentException: Illegal characters in path.` (caused by the colon `:` in `VERDICT: BLOCKED`).
3. **Undetected Worker Hang in Production:** 
   A worker process hangs with 0% CPU and an unresponsive ActiveX interface without triggering a dialog. The repaired watchdog outputs `NOT WRITTEN`, exits 0, and the rig deadlocks indefinitely because the leaf was never flagged.

---

### 4. Direct Answers to Your Questions

#### Q1: Strongest reading under which `flagged=False` is a REAL defect of the watchdog
G7's specification (`'no modal dialog' writes NO gating record (the leaf IS still flagged in the message)`) proves that non-dialog stalls were designed to emit an advisory warning identifying the suspect leaf. By tying the watchdog's leaf-flagging state entirely to `VERDICT: BLOCKED`, the repair silently stripped out the rig's ability to detect COM/ActiveX deadlocks and non-dialog hangs. The test caught this regression: the leaf ceased to be flagged.

#### Q2: How `:48-:49` can pass while the repair is broken in production
Lines `:48-:49` only verify two binary file states:
1. Did a file appear when `MODAL DIALOG PRESENT` was injected? (Yes)
2. Was the file absent when clean? (Yes)

This test does **not** verify how downstream scripts consume `$record`. In production:
- If a post-flight cleanup or aggregation script checks `if ($record) { Test-Path $record }`, PowerShell throws a fatal path exception because `NOT WRITTEN - ... VERDICT: BLOCKED` contains a colon (`:`), which is illegal in Windows filenames outside drive letters.
- If a caller checks `if ([string]::IsNullOrEmpty($record))`, it will believe a stall record exists because the string is non-empty.

#### Q3: The cheapest discriminating test WITHOUT running LabVIEW
Do not execute LabVIEW or launch a test run. Run an offline evaluation of the test assertion against the existing log file `tools/bench/repair_c39_stall_selftest.log`:

```powershell
# In PowerShell: test the assertion logic against the actual output in the log
$logMessage = "NOT WRITTEN - the dialog check did not return VERDICT: BLOCKED ..." # (extract exact text from line 49)
$testPattern = "<G7_ASSERTION_REGEX>"

# Test 1: Exact case (current test)
$caseSensitive = [regex]::IsMatch($logMessage, $testPattern)

# Test 2: Case-insensitive (claim hypothesis)
$caseInsensitive = [regex]::IsMatch($logMessage, $testPattern, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)

[PSCustomObject]@{
    CaseSensitive   = $caseSensitive
    CaseInsensitive = $caseInsensitive
}
```

- **If `CaseInsensitive` is `False`:** The claim is **definitively refuted**. The failure is due to a missing leaf marker/telemetry, not letter casing.
- **If `CaseInsensitive` is `True`:** The claim of a casing mismatch in the assertion holds for G7, **provided** you also confirm that `$record` being a non-path sentinel string does not violate downstream callers.

---

### Final Assessment

The claim that the failure is merely a casing bug is **rejected**. The repair introduced a sentinel string containing invalid path characters (`:`) into a variable contract previously holding a path, and it appears to have suppressed leaf-level stall reporting whenever a dialog is absent. 

What would change this assessment: Demonstrating that (1) making G7's regex case-insensitive evaluates `flagged=True` on the existing log, and (2) no downstream consumer ever tests or reads `$record` as a file system path when no stall occurs.



## Sources

(extract from answer)

## What was done with it

Dispatched and collected by a MATERIAL session (cycle 40); classification and the three answers were
reported to the judgement session, which owns the disposition. The peer REJECTS the "assertion bug only"
claim on three grounds, none of them yet tested against the machine:

1. **Capability claim (Q1)** — it reads G7's own title (`the leaf IS still flagged in the message`) as a
   REQUIREMENT that a non-dialog stall still flags the leaf advisorily, so `flagged=False` would be the
   repair demoting a stall detector to a modal-dialog detector, blind to COM/ActiveX deadlocks with no
   dialog. NOT VERIFIED here: whether G7's title states a requirement or merely describes the pre-repair
   behaviour is a reading of the test's intent, which is a judgement call, not a measurement.
2. **Type/path claim (Q2)** — `$record` set to the sentinel `NOT WRITTEN - ... VERDICT: BLOCKED ...` stays
   TRUTHY in PowerShell, so any downstream `if ($record)` believes a record exists, and any downstream
   `Test-Path`/`Get-Item`/`Remove-Item` on it throws on the illegal `:` in the string. This is a concrete,
   checkable prediction about consumers of `$record` after line 273; it was NOT checked in this session
   (the brief forbids further edits to `lv_stallcheck.ps1` and any consumer census).
3. **Discriminating test (Q3)** — re-evaluate G7's assertion regex against the verbatim log text offline,
   case-sensitive vs `IgnoreCase`. `CaseInsensitive == False` refutes the casing claim outright;
   `True` supports it only if no consumer reads `$record` as a path.

Step 2 of the same brief re-ran the already case-fixed self-test; its result is reported alongside this
review. No `lv_stallcheck.ps1` change was made on the strength of this answer.
