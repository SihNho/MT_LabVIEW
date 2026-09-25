# hyp-unroutable-err2-85

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.4600  in 34 / out 11136 / cache-create 105583 / cache-read 1728314  (138s, 30 turn(s))
- **date:** 2026-09-25 22:20:00
- **outcome:** ANSWERED (142s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

FAILED PREDICTION, card 85-3: tools/bench/unroutable_l2a1_85.py (stagexec real executor on a D1_k scratch), log
tools/bench/unroutable_l2a1_85.log.

Prediction (P0/P2/P3): all 42 ops run with graph diff 0; act 45 (row rw_6007_5082, route 'tunouter', op
ops\OpTunOuterWire_v1.vi built and gated 28/0 in unroutable_l2a1_85_build_tun2.log) adds one wire whose only source is tunnel
#5680's outer face #6007 and only sink SubVI #5058 terminal #5082.
Observed: ops 00-40 (acts 1-44) all diff 0 (log:329-554); P1 read before act 45 PASSED for both faces (log:555-556); the op
logged "OP wire_tunouter SelectorTunnel[11] #5680 -> SubVI[17].t0 -> err '' (0.5 s)" and "CENSUS DIFF: Node 635 -> 635"
(log:558-560); then the executor's next read, be.read() -> wiki_build.read_live -> gscript.report_all(GObject), raised
"error 2: Invoke Node in TRef Traverse.vi ... Traverse for GObjects.vi->OpReportAll_v0.vi (Traverse Failed)" (log:562-578),
~18 min after start (LabVIEW fresh restart, 33,997 handles, log:29). Hygiene then hung in close_panel until LabVIEW was killed
(~13 min). LabVIEW error 2 = memory full.

My explanation: memory exhaustion accumulated over the run (two full GObject traversals of a ~600-node VI per op, 41 ops,
plus censuses) - NOT caused by the tunouter write itself; the failure just landed on the first read after act 45.
Alternative I cannot exclude: the tunouter op itself made something pathological (e.g. 'SubVI[17].t0' is NOT #5082 and the wire
landed on a different/incompatible terminal, or a type-propagation storm) so the next Traverse blew up.

Question: which is it, and what in our own files (tools/stagexec.py LVBackend.read ~line 1009, tools/wiki_build.py read_live
~line 240, gscript.report_all, previous long stagexec runs e.g. tools/bench/constsrc_l2a1_85.log, stage_d1_l2a1*.log) shows
whether a 40+-op real stagexec run has ever completed without error 2? Is 'SubVI[17].t0' the terminal #5082? Cheapest test that
separates "accumulated memory" from "the tunouter write caused it" without a full 30-min rerun.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict:** the files support "accumulated exhaustion" as the more likely cause, but the run measured nothing that proves it. Your framing rests on inference, and the tunouter op is not cleared. Nobody has yet checked which terminal it actually wired, and LabVIEW crashed afterwards in a way the documented error-2 state does not.

## 1. Strongest reason the claim is wrong

The run had no memory meter, so "memory exhaustion accumulated" was never measured.
- `tools/stagekit.py:177` already has `private_bytes()`, but `unroutable_l2a1_85.log` has no private-bytes line anywhere.
- The only meter logged is the handle count. `stagekit.py:178` itself says that count cannot see VI Server references.
- The error-2 threshold we have is about 770 MB of private bytes (`com-driving.md:310`). It is not a handle number.

The failure also landed on the first read after the one step this run had never executed before: `OpTunOuterWire_v1` running live inside a stagexec sequence. Every other step type in acts 1–44 had run before (`constsrc_l2a1_85.log`). The claim treats this timing as chance without showing it.

Error 2 does not by itself prove that RAM ran out. NI documents it for failures to open new references ([NI KB](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019KhWSAU&l=sv-SE)), and LAVA has a thread titled ["Error 2: Memory is full – but it isn't"](https://lavag.org/topic/18730-error-2-memory-is-full-but-it-isnt/).

## 2. Evidence for your explanation (it is strong, but unmeasured)

- **Every whole-VI read leaks references.** `docs/REFERENCES.md:158` records `OpReportAll_v0.vi` with Open VI Reference → Traverse → For Loop and **0 Close Reference**. `gscript.report_all` still calls v0 (`gscript.py:505`), and `read_live` runs a whole-VI `report_all(path,"GObject")` on every read (`wiki_build.py:240`). So each executor read leaks the VI reference plus every object it visited.
- **Memory grows with each op.** `s0b_refleak_profile.log:32-56` shows private bytes rising 609 → 652 MB over 20 mutating iterations while the handle count stayed flat.
- **This pattern has been seen before.** A route-B run died with the same error 2 in the same op, after about 50 steps (`docs/cycle27-plan.md:234`). The earlier review found `report_all(Diagram)` succeeded about 30 times and then stopped, which points to time or state rather than object class (`peer_routeb_run10_error2_class.log:18`).
- **Has a 40+-op real stagexec run ever finished?** Only `constsrc_l2a1_85.log`: 36 steps and 40 acts, PASS, with handles going from 33,954 to 46,075 (`:27`, `:560`). This run died at act 45, after 44 acts plus two extra P1 reads. That margin is thin but consistent with a budget of about 40–45 whole-VI reads. It does not prove that budget exists. The `stage_d1_l2a1*.log` runs all ended on E1 or earlier, never error 2.

## 3. Alternative explanations of the same evidence

- **(A) The tunouter write caused it.** The op wrote a wire, and the executor then traversed the VI while LabVIEW was still working through that edit (a crash or long type propagation), and the traverse failed. The aftermath fits this better than a plain memory-full state:
  - `close_panel` then failed with `-2147023170` = `0x800706BE`, "The remote procedure call failed" (`log:581`). That usually means the COM server died or failed ([Microsoft Learn](https://learn.microsoft.com/en-us/archive/msdn-technet-forums/e5770797-1b9b-4a25-8d6c-1f54e0f7ead2)).
  - The handle count then read 0 (`log:584`).
  - In the documented error-2 state, LabVIEW stays alive and `SaveInstrument` still works (`com-driving.md:314-316`). A process that dies is a different signature.
  - Out-of-memory can also crash a process, so this does not decide the question. It does undercut the claim that it "just landed" on this read.
- **(B) The wire went somewhere else.** The op addresses its target by index (`SubVI[17]`, terminal 0), not by uid (`stagexec.py:1085-1090`). Nothing read back which terminal it wired, because the P2/P3 read-backs never ran.
  - **Is `SubVI[17].t0` terminal #5082?** Very likely by name, not proven by uid. #5058's terminal 0 is `'Bead is good? array in'` in several logs (`build_d1_routeb_v0.log:183`, `apply_conpane.log:2`), and P1 gives #5082 that same name on #5058 (`log:555`).
  - What is unverified: that class-traverse index 17 was still #5058 when the op ran, and that the terminal ordering inside the op matches. The index is resolved by `uid_index`, a class traverse just before the op. An index shift of +1 has been measured before (`archive/peer/2026-09-19-routeb-run7-index-shift.md`). The node count stayed 635 → 635, which lowers that risk but does not remove it.
  - A wrong-type wire would normally only break the wire, not fill memory. So (B) matters for correctness more than for the crash.

## 4. What would falsify your claim

- **It would be falsified by:** a fresh LabVIEW instance with private bytes near 600 MB, running only the tunouter op on a clean scratch, then one `read_live`, and getting error 2 or a crash.
- **It would be confirmed by:** the same single-op sequence reading back cleanly (and wiring terminal #5082), plus a 45-read loop of `report_all(GObject)` with no edits that climbs toward about 770 MB and fails.

## 5. Cheapest test that separates the two (about 3–5 min, not a 30-min rerun)

One fresh LabVIEW instance on a new D1_k scratch. Log `stagekit.private_bytes()` and the handle count after every step:
1. Run `read_live` once, as a baseline.
2. Run acts 1–2 only if needed to make faces #6007 and #5082 reachable; otherwise run act 45 (`wire_tunouter`) directly. The P1 log shows both are bare.
3. Run `read_live` once more, then a one-line read-back of the new wire's sink terminal uid.

How to read the outcome:
- **Error 2 or an RPC failure at step 3, at low private bytes:** the tunouter write is the cause.
- **Clean, and the sink is #5082:** the tunouter op is cleared, and the question becomes the read budget. To confirm that, loop `report_all(GObject)` with no edits and log private bytes per call until it fails. That is the loop the earlier review proposed at `peer_routeb_run10_error2_class.log:52`, and it has not been run.
- **Clean, but the sink is not #5082:** separate correctness bug in index addressing.

**What would change my mind:** if the single-op test comes back clean at low memory, I accept the accumulation explanation. In that case the fix is structural either way: `OpReportAll_v0` should close its references, or the executor should not traverse the whole VI after every op. A restart does not fix it.

Sources:
- [NI KB: Error 2 "Memory is Full" when opening a new reference](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019KhWSAU&l=sv-SE)
- [LAVA: "Error 2: Memory is full – but it isn't"](https://lavag.org/topic/18730-error-2-memory-is-full-but-it-isnt/)
- [NI: Traverse for GObjects VI](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/vi-lib/utility/traverseref-llb/traverse-for-gobjects-vi.html)
- [Microsoft Learn: 0x800706BE "The remote procedure call failed"](https://learn.microsoft.com/en-us/archive/msdn-technet-forums/e5770797-1b9b-4a25-8d6c-1f54e0f7ead2)

## Sources

(extract from answer)

## What was done with it

Card 85-3 (material), 2026-09-25 ~22:3x. Card budget failures=1 spent and card rule "review owed -> review then stop": NO
further LabVIEW run in this card; the discriminating test is handed to judgement.
- Point 1 accepted: "accumulated memory" is the leading explanation, NOT measured (no private-bytes line in the run log).
- Point 3(A) partly REFUTED by the timeline: the close_panel RPC failure 0x800706BE (log:581) and handle count 0 (log:584)
  came AFTER the material session killed LabVIEW (Stop-Process ~22:16, hygiene had hung ~13 min in close_panel after the
  error 2 at ~22:03). They are artefacts of the kill, not evidence that LabVIEW crashed on its own.
- Point 3(B) accepted as OPEN: sink of the act-45 wire never read back (P3 never ran); 'SubVI[17].t0' == #5082 by name only.
- Point 5 (single-op test with private_bytes per step, then a no-edit report_all(GObject) loop) proposed to judgement as
  the next card; OpReportAll_v0's missing Close Reference (docs/REFERENCES.md:158) reported, not patched here.
