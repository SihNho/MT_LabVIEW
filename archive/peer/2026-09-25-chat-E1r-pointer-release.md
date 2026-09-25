# chat-E1r-pointer-release

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.4639  in 26 / out 13572 / cache-create 96397 / cache-read 1242254  (172s, 22 turn(s))
- **date:** 2026-09-25 01:13:40
- **outcome:** ANSWERED (176s)
- **verdict-card:** NO-VERDICT: $.alternative: 325 chars > limit 300
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id chat-E1r, role hypothesis) ---
CLAIM: r1 failed because errorlist_check released its ONLY LabVIEW.Application COM pointer (gscript._lv=None before each Dispatch) on a LabVIEW launched by that Dispatch, so LabVIEW exited before OpenFrontPanel; holding one pointer all run (_APP_PIN) fixes it.
PREDICTED: r1 (with a 60 s GetVIReference readiness poll, pointer still reset each try): cold start -> OK verdict, 0 items, ExecState 1
OBSERVED: r1: ClassFactory on try 1, GetVIReference OK try 2 at 20.4 s, then OpenFrontPanel DISP_E_EXCEPTION scode 0x80010107 and close_panel DISP_E_UNKNOWNINTERFACE; LabVIEW gone at end. r2 (pointer held): Version 14.9 s, GetVIReference try 1 at 1.3 s, OK 12/0.
ALREADY RULED OUT: bed defect: same bed read OK 0 items on 2026-09-24 and in r2 (errorlist_D1_s4_loop17_20260925_010723.json)
ALREADY RULED OUT: the original 01:02 failure (errorlist_check_cycle74.log) had the SAME shape: Version answered at 21.5 s, then ClassFactory on the first VI call, after the old code reset g._lv = None before it
ATTACHMENT: tools/bench/errorlist_check_cold_20260925.log (md5 e1c6fee4abf0875e6237b14b29852680)
ATTACHMENT: tools/bench/errorlist_check_cold_20260925_r2.log (md5 67fe487a9ca8e8c0d3cd14dca776952e)
ATTACHMENT: tools/bench/errorlist_check_cycle74.log (md5 4671f722cd2e63f318b759150fca5eb8)
ATTACHMENT: tools/errorlist_check.py (md5 9064e9358b241d98f10ab611993d0326)
ATTACHMENT: tools/gscript.py (md5 None)
--- END REVIEW CARD ---

Read the review/1 card above. Evidence: tools/bench/errorlist_check_cold_20260925.log (r1, lines 2-6), tools/bench/errorlist_check_cold_20260925_r2.log (r2), tools/bench/errorlist_check_cycle74.log (original failure), tools/errorlist_check.py (labview_up, vi_ready, _APP_PIN; git show HEAD~1:tools/errorlist_check.py for the pre-fix version), tools/gscript.py lv() at ~line 212 and vi_ref at ~254.
Attack the claim: is the LabVIEW-exits-on-last-Application-release explanation right for a LabVIEW launched via COM (search NI docs/forums for LabVIEW ActiveX server lifetime when launched by automation client), or is r2's success just timing (a second cold start being warmer)? Give the cheapest discriminating test that does not need a new LabVIEW run if possible, otherwise the smallest one.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"chat-E1r","verdict":"<one of: refuted | supported | unverified>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

**Verdict: not proven.** The failure pattern supports "COM start-up/shutdown lifetime" in general. It does not support the card's specific story, and some of the card's own facts are wrong. r2 being "just warmer" is also unlikely.

**1. Strongest reason the claim is wrong as written.** The r1 record contradicts "LabVIEW exited before OpenFrontPanel":
- **The failing call was not OpenFrontPanel.** `ref_counts` shows `opened 1, closed 1` (`tools/bench/errorlist_D1_s4_loop17_20260925_010538.json:25-29`). `_REF_OPENED` only goes up *after* `GetVIReference` returns (`tools/gscript.py:263-264`), and that one count is vi_ready's successful try 2. So the exception came from the **`GetVIReference` inside `open_panel`'s `vi_ref`** (`gscript.py:1293`), before `OpenFrontPanel` could be reached.
- **The error code is misread.** The inner scode `-2147418105` is **0x80010007, RPC_E_SERVER_DIED** ("callee … disappeared; the call may have executed", https://www.hresult.info/FACILITY_RPC/0x80010007). It is not 0x80010107.
- **This does not match this project's known "LabVIEW is dead" error.** When LabVIEW was killed, the recorded error was 0x800706BA (`gscript.py:274`). The next call here returned DISP_E_UNKNOWNINTERFACE instead.
- **A LabVIEW process was alive at the end of the script.** `handles_after` = 37,535 (`010538.json:24`), read by `Get-Process LabVIEW` (`tools/bench/bench_prep.py:64-71`) after both failing calls. The original 01:02 failure shows the same: `handles_after` 37,449 (`...010221.json:21`). The card's "LabVIEW gone at end" can only mean *after Python exited*, and every run ends that way, r2 included.

**2. Alternative explanation of the same evidence: a second `CoCreateInstance` during start-up, not the release.** All three failing runs made a **second** `Dispatch("LabVIEW.Application")` while LabVIEW was still coming up:
- the old code reset `g._lv`;
- r1 reset it on every try.

Both passing runs made **one** `Dispatch` and never another. r1's own timing shows the second activation was abnormal. Try 1 hit ClassFactory, then after a 4 s sleep, try 2 took about 16 s (`vi_ready_s` 20.4). A warm `GetVIReference` + ExecState on the same bed takes 1.3 s (r2 log line 5). 16 s is roughly a cold launch (Version answered at 14.4–14.9 s).

So try 2 probably connected to a **second LabVIEW process** or to one that was being torn down. That would explain:
- ClassFactory on a class object that was revoked or not yet registered;
- RPC_E_SERVER_DIED when that process went away;
- a LabVIEW process (possibly the other one) still being counted at the end.

`Get-Process … | Select-Object -First 1` cannot tell two processes apart, and no PID was recorded. Microsoft's own guidance allows both readings: an out-of-process server can start shutting down on its final release even before it has finished initialising, and activation races across class objects are a known hazard (https://learn.microsoft.com/en-us/windows/win32/com/out-of-process-server-implementation-helpers).

I found **no NI document or forum post** saying LabVIEW.exe exits when its last automation reference is released. Searches (https://forums.ni.com/t5/NI-TestStand/Unable-to-Launch-LabView-Application-ActiveX-automation-server/td-p/895920, https://www.ni.com/docs/en-US/bundle/labview/page/activating-labview-as-an-activex-server.html) came back empty on that point. The mechanism is plausible COM behaviour that nobody has measured for LabVIEW. Nothing in this project's files records it either; the only mention is the hypothesis comment at `tools/errorlist_check.py:69`.

**"r2 is just warmer" is weak.** r1 and r2 were both cold (`was_running=False`), with nearly identical timings: Version at 14.4 vs 14.9 s, handles settled at 19.8 vs 20.3 s. The real difference is "re-Dispatched or not", not how warm LabVIEW was. Both the card's claim and my alternative predict that `_APP_PIN` fixes the problem. So r2 **does not tell the two explanations apart**, and it is one pass. The cycle-74 rerun at 01:09 is a second pass on the same code, not independent evidence.

**3. What would falsify the claim.** Release the only Application pointer on a COM-launched LabVIEW, with no second `Dispatch`. If the same PID is still alive and answers a fresh `Dispatch` 30 s later, "exits on last release" is dead. Separately, if a second `Dispatch` made **while the first pointer is still held** also gets ClassFactory or a new PID, then the fault is the second creation, not the release.

**4. Cheapest test that tells them apart.** No existing record can settle this, because no run logged PIDs or process start times. The smallest new run is about 90 s of COM only: no VI, no GUI, no hardware. It still needs the LabVIEW lock.
- **Arm A:**
  1. Cold start with one `Dispatch` and `.Version`.
  2. Log `Get-Process LabVIEW | Id, StartTime, CommandLine` for all processes. The command line shows whether COM launched it with `-Embedding` or `/Automation`.
  3. Set the pointer to None, run `gc.collect()`, and poll every 1 s for 30 s: does the PID vanish?
  4. `Dispatch` again and log the PIDs and any error.
- **Arm B:** kill LabVIEW, cold start again, hold pointer A and make a second `Dispatch` B right after Version. Log B's `.Version` and the PIDs.

The claim predicts: in Arm A the PID disappears (or goes into shutdown) and the re-Dispatch gives a new PID; in Arm B, nothing goes wrong. The alternative predicts: in Arm A the PID survives; in Arm B you get ClassFactory or a second PID. In both cases `_APP_PIN` should stay, as long as `labview_up` is the only `Dispatch` in the process. Also check that nothing else calls `g.reset()` or sets `g._lv = None` during a run.

VERDICT {"schema":"verdict/1","id":"chat-E1r","verdict":"unverified","alternative":"The failure is a SECOND CoCreateInstance during LabVIEW start-up (ClassFactory, then a 16 s cold-launch-like try 2 that reached a second/tearing-down process), not exit-on-release. r1 failed in GetVIReference (opened=1) with 0x80010007, not in OpenFrontPanel, and a LabVIEW process was alive at the end (handles_after 37535).","discriminating_test":"About 90 s of COM only, no VI. A: cold Dispatch+Version, log all LabVIEW PIDs/StartTime/CommandLine, release pointer, poll 30 s, re-Dispatch. B: fresh cold start, hold pointer A, second Dispatch B. PID vanishes in A = claim; PID survives in A and ClassFactory/2nd PID in B = alternative.","violations":[],"sources":["tools/bench/errorlist_D1_s4_loop17_20260925_010538.json:24-29","tools/gscript.py:263-264","tools/gscript.py:274","tools/bench/errorlist_check_cold_20260925_r2.log:2-5","https://www.hresult.info/FACILITY_RPC/0x80010007","https://learn.microsoft.com/en-us/windows/win32/com/out-of-process-server-implementation-helpers"],"note":"Both hypotheses predict _APP_PIN works; r2 cannot tell them apart. The card's scode 0x80010107 and 'OpenFrontPanel' are misreads. No NI source found for LabVIEW exiting on last release."}

## Sources

(extract from answer)

## What was done with it

ANSWERED / UNVERIFIED (judgement, chat 2026-09-25). The pointer-release hypothesis is neither refuted nor
supported: the reviewer's alternative (a second `Dispatch` during a cold launch reaching a torn-down or second
instance; try 2 took ~16 s, the cold-launch time) fits the same evidence, and the reviewer corrected the r1 reading
(the failing call was `GetVIReference`, scode 0x80010007, not `OpenFrontPanel`/0x80010107). KEPT: `_APP_PIN` in
`tools/errorlist_check.py` (both explanations predict it works; cold proof r2 12/0 and the runner's own 01:09 pass).
NOT CLAIMED as root cause. OWED, next card that gets the LabVIEW lock: the reviewer's ~90 s A/B COM test (A release
the pointer, poll the PID 30 s, re-Dispatch; B hold + second Dispatch; log PIDs/StartTime), and the `_APP_PIN`
comment corrected to the right call and scode. Card id reserved: chat-E2.

**UPDATE 2026-09-25 11:xx (card chat-E2, A/B test `tools/bench/com_pointer_ab_20260925.log`): hypothesis (a) SUPPORTED — arm A: releasing the only Application pointer ended PID 18944 within 2.9 s and the re-Dispatch launched a new PID; arm B: with the pointer held a second Dispatch reached the same PID 9192. LabVIEW had been launched by COM (`/Automation -Embedding`). `_APP_PIN` is the right fix; comment corrected to GetVIReference / 0x80010007.**
