# c108a-disp107-visa-refusal

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.8443  in 32 / out 16968 / cache-create 134119 / cache-read 1697210  (227s, 25 turn(s))
- **date:** 2026-09-27 13:20:49
- **outcome:** ANSWERED (231s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim about the failed prediction in tools/bench/disp_107_abba.log (script tools/bench/diag_c104_abba.py, leg guard tools/bench/drive_legguard.py).

FAILURE: gate "V1 leg1 A@15 VISA precheck Rotor+ASRL5 status 0" FAILED (tools/bench/disp_107_abba.log:5-6,18); T12 and T17 failed as consequences (the leg was refused, LabVIEW never started). viOpen('Rotor') and viOpen('ASRL5::INSTR') both returned -1073807246 (0xBFFF0072, "resource valid but VISA cannot currently access it") in 0.1-0.3 ms.

CLAIM: (1) the cause is a machine-level state of the rotor's COM5 port under NI-VISA, outside every VI and script of ours: with LabVIEW closed, viOpen of Rotor/ASRL5 fails 3/3 while CreateFileW(COM5) succeeds and viOpen('ASRL6::INSTR') on the other FTDI adapter succeeds 3/3 (tools/bench/diag_c105d_visa.log:6-23; tools/bench/diag_c106a_visa.log:6-23). (2) The leg guard did what it was designed to do: refuse the leg in seconds before LabVIEW started, so the V1 FAIL is the correct refusal, not a script bug. (3) Clearing it needs a PC-level act that is an open user decision (tools/bench/decisions_pending.json D-2026-09-27-03); no VI is changed and the port is not re-pointed. (4) The failure has no bearing on a structural VI-Scripting build that runs no VI and opens no VISA session (the next build: tools/recipes/stage_d1_l2a2.py, which edits a claudeDev copy and saves it, never runs it).

Already ruled out: a LabVIEW instance holding COM5 (LabVIEW was not running, log line 6); another process holding COM5 at the OS level (CreateFileW opens it); a broken FTDI driver generally (COM6 on the same driver opens under VISA).

Attack each of (1)-(4). In particular: what else produces 0xBFFF0072 on an ASRL resource while the Win32 handle opens (VISA alias/visaconf.ini, NI-VISA Server or a passport lock, an exclusive lock left by a crashed NI process such as nipalsm/NI Device Monitor, a stale VISA shared-lock table), and what single cheap test with LabVIEW closed separates them. And name anything in claim (4) that would make a no-run VI-Scripting build touch the rotor port anyway (e.g. loading a VI whose Configure.vi opens VISA at load time, or a VISA refnum constant resolving on load).


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict:** claim (1) is not shown. The measurements prove the fault is not in any open LabVIEW session, but they do not show it is outside our tooling. Claim (2) holds: the leg guard refused the run correctly. Claim (3) is premature because it rests on (1). Claim (4) mostly holds, with the caveats at the end.

## 1. Strongest reason the claim is wrong

The fault started while only our harness was using the machine, with no hardware or boot event in between.

- **No reboot or replug in the window.** The COM5 adapter last arrived at 09-23 13:19:37 and has never been removed (`tools/bench/diag_c105c_offline.log:29`). NI's `nimxs.exe` has run since the same boot, 09-23 13:19:39 (`diag_c105d_visa.log:3`).
- **What did change was our runs.** The rotor ran normally on 09-26 14:18 and was broken by 09-27 04:30 (`decisions_pending.json:182`). In between, the harness ran LabVIEW over and over, each run opening the rotor setup subVI (`Configure.vi`) on COM5, and each cycle ends by killing LabVIEW (CLAUDE.md rule 1b, cycle end hook).
- **Likely cause:** a LabVIEW process killed while it held a VISA session on COM5 with I/O in progress. That can leave state behind in NI-VISA or in the FTDI adapter/driver.

"Outside every VI and script of ours" describes where the state sits now, not what caused it. If our kills caused it, a replug or reboot (D-03) clears it once and the next killed run can bring it back.

## 2. Alternative explanations of the same evidence

The calibration step matters here. With a child process holding COM5, VISA returned the same `0xBFFF0072` in the same ~0.6 ms (`diag_c105d_visa.log:17`). So VISA gives this code when its own open of the port fails. With the port free, it still fails in 0.4–0.9 ms, while successful opens of COM6 take 6–24 ms (`:18-23`). That points to VISA failing at the open step or before it, not after it has configured the port. Three candidates fit:

- **(A) Stale state inside NI-VISA.** VISA refuses before it asks Windows for the port at all. A reboot or NI service restart clears this; a replug may not.
- **(B) VISA's open differs from ours.** Our probe uses `CreateFileW(..., 0, ...)`, a plain open with flags 0 (`diag_c105d_visa.py:48`). NI-VISA may open in overlapped mode or run serial setup calls straight after opening. If one of those setup calls fails on a wedged FTDI adapter, VISA reports "busy". A replug clears this.
- **(C) Device side.** The rotor controller or the FTDI chip is stuck in a state that the plain open does not touch. NI forum threads report this exact error on USB-serial adapters that only cleared when the device was powered down or moved to another USB port ([NI forum, repeated close](https://forums.ni.com/t5/LabVIEW/After-repeated-Close-functions-I-still-get-the-VISA-Error-quot/td-p/3105653), [NI forum](https://forums.ni.com/t5/LabVIEW/VISA-Hex-0xBFFF0072-The-resource-is-valid-but-VISA-cannot/td-p/835913)).

Hypotheses the evidence already rules out:

- **A stale VISA lock.** The probe opens with access mode 0, i.e. no lock requested (`diag_c105d_visa.py:40`). A leftover lock would show up as `VI_ERROR_RSRC_LOCKED` (0xBFFF000F) on I/O, not "busy" at open.
- **A wrong alias or disabled resource.** `visaconf.ini` maps Rotor → ASRL5 → COM5 with enabled=1 (`diag_c105c_offline.log:31`).

Not checked: the "Console Out" option in NI MAX ([NI forum](https://forums.ni.com/t5/Instrument-Control-GPIB-Serial/VISA-HEX-0xBFFF0072-The-resource-is-valid-but-visa-cannot/td-p/1960503)), and whether a second vendor's VISA is installed and routing ASRL5 away from NI-VISA. `visaconf` does not show that routing. A second VISA seems unlikely, because COM6 goes through the same `visa64.dll` and opens fine.

**The current measurements do not separate A, B and C.** D-03 recommends a replug first, which only fixes B and C.

## 3. What would falsify the claim

- **Refutes "machine-level, not ours":** the port clears with a replug or reboot, then fails again after the next cycle that kills LabVIEW while the rotor session is open.
- **Refutes "needs a PC-level act":** a plain Win32 open plus the same serial setup VISA does succeeds in full, yet VISA still refuses. That leaves VISA's own state as the cause, and a replug would not help.

## 4. Cheapest test that separates them (LabVIEW closed, read-only, about 1 s)

Extend the existing `cf_open` probe in `diag_c105d_visa.py`:

1. Call `CreateFileW("\\.\COM5", GENERIC_READ|WRITE, 0, NULL, OPEN_EXISTING, FILE_FLAG_OVERLAPPED, NULL)`.
2. Then call `GetCommState`, `SetCommState` (9600 8N1, VISA's defaults for ASRL5), `SetupComm`, `SetCommTimeouts`, `PurgeComm`, `ClearCommError`, `EscapeCommFunction(SETDTR)` and `GetCommModemStatus`.
3. Record `GetLastError` after each call. Run the same sequence on COM6 as a control.

How to read it:

| Result | Points to | Fix |
|---|---|---|
| A setup call fails on COM5 but not COM6 | B or C (adapter or device) | replug |
| All calls succeed on COM5 | A (inside NI-VISA) | NI service restart or reboot; a replug is not enough |

If Sysinternals Process Monitor is available, one trace of `viOpen('ASRL5::INSTR')` filtered on `\Device\VCP0` settles it directly: either no open request reaches the port (A), or the open or a specific setup request fails (B or C).

## On claims (2)–(4)

**(2) The leg guard: agreed.** It refused in 2 s, LabVIEW was not running, the md5 hashes are unchanged and the camera was restored (`disp_107_abba.log:5-10,16-23`). But the prediction that failed was the launcher's, not the guard's. Two measurements an hour earlier had already shown COM5 refused (06:45 and 06:56), so starting the A/B run at 07:50 could only fail. Before a real run, the launcher should check the D-03 status and skip the run with a SKIP result, not launch it and report FAIL.

**(3) The PC-level act:** it depends on which of A, B or C holds, so run the test above before the user picks from D-03. D-03 should also say that our own LabVIEW kills are a suspected cause. Otherwise the user fixes the port and the next runs break it again.

**(4) The build script: mostly agreed.** `stage_d1_l2a2.py` never runs the VI. Its `x.run()` (line 53) runs the plan executor, and the file is saved broken on purpose, so it cannot run. Loading a VI and its subVIs does not execute `Configure.vi`, and a VISA resource constant does not open a session when the VI loads. Three things could still reach COM5 or confuse the result:

- **(a) "Run When Opened".** If any VI that gets opened as the top-level VI has this flag set, opening it through the GUI (for example the cycle-start Error List check in `cycle_runner.py:736`, or a GUI Ctrl+S save) could start it. Check the flag on the input VI (the L2-A1 build file) and on the Error List check's scratch copy.
- **(b) A LabVIEW left running from a failed real run.** The build script only kills LabVIEW at exit (`stage_d1_l2a2.py:98`), and it starts from a fresh LabVIEW. Confirm that a fresh start is enforced, so the build never attaches to an instance that already holds COM5.
- **(c) The build passing proves nothing about behaviour.** A PASS is a structural check only. The rotor path it carries stays untested until COM5 works again (STATUS.md:68 notes the recorded-frame replay copies are blocked for the same reason).

Sources: [NI forum, 0xBFFF0072 thread](https://forums.ni.com/t5/LabVIEW/VISA-Hex-0xBFFF0072-The-resource-is-valid-but-VISA-cannot/td-p/835913) · [NI forum, same thread p.2](https://forums.ni.com/t5/LabVIEW/VISA-Hex-0xBFFF0072-The-resource-is-valid-but-VISA-cannot/td-p/1442576/page/2) · [NI forum, repeated close / device power-down](https://forums.ni.com/t5/LabVIEW/After-repeated-Close-functions-I-still-get-the-VISA-Error-quot/td-p/3105653) · [NI forum, Console Out](https://forums.ni.com/t5/Instrument-Control-GPIB-Serial/VISA-HEX-0xBFFF0072-The-resource-is-valid-but-visa-cannot/td-p/1960503) · [NI forum, USB adapter port reassignment](https://forums.ni.com/t5/Switch-Hardware-and-Software/visa-cannot-currently-access-it-error/td-p/323526) · [NI KB article on -1073807246](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019NeQSAU&l=en-US) (the fetch failed with a certificate error, so I could not read it).

## Sources

(extract from answer)

## What was done with it

Dispatched by material card 108-1 (cycle 108) because guard_peer refused the L2-A2 structural launch on
`disp_107_abba.log` (JEV-LADDER new-problem p=0.490 -> old path). Accepted by card 108-1: claims (2) and (4) — the
L2-A2 launch proceeds (structural build, VI never run, fresh LabVIEW, killed at exit). NOT decided here (judgement /
user, returned as OPEN in `tools/bench/cards/result_108-1.json`): claim (1)/(3) — the reviewer's cause hypothesis
(our LabVIEW kills with a COM5 session open) and its proposed Win32 overlapped-open + comm-setup probe before D-03 is
answered; and the launcher change (SKIP instead of FAIL while D-03 is open). Caveat (4a) "Run When Opened" on the
input bed is not checked by this card.
