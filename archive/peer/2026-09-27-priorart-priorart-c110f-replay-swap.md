# priorart-priorart-c110f-replay-swap

- **agent:** claude
- **role:** priorart
- **model:** claude-opus-5-5 (effort medium; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $0.9244  in 6 / out 2125 / cache-create 103792 / cache-read 257665  (35s, 5 turn(s))
- **date:** 2026-09-27 18:28:25
- **outcome:** ANSWERED (39s)
- **verdict-card:** VERDICT-CARD priorart-priorart-c110f-replay-swap verdict=novel -> tools\bench\cards\verdict_priorart-priorart-c110f-replay-swap.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id priorart-priorart-c110f-replay-swap, role priorart) ---
CLAIM: The work under review (cycle-start) is novel - not already built, measured, refuted or covered by an existing helper in this project's files.
ATTACHMENT: tools\recipes\stage_replay_swap.py (md5 0f06b86533ee486481f5d448c2310809)
--- END REVIEW CARD ---

PRIOR-ART REVIEW (trigger: cycle-start).

You are checking ONE thing: has this already been done here? Do not review the plan's merits -
other reviews do that. Answer in two parts, naming a FILE and LINE for every finding. A finding without a citation
cannot be acted on, because the only way this review is released is by someone opening your citation and showing in
writing that it does not cover their case.

PART A - THE DIRECTION (this is the part that matters most)
 A1 SETTLED ALREADY. Has this direction, or its central question, already been decided or answered in STATUS.md,
    docs/ or archive/? Quote the decision and its date.
 A2 REFUTED ALREADY. Has this direction already been tried, abandoned, or argued against - in an archived peer
    review, a retrospective, or a superseded plan section? Say what killed it and whether that still applies.
 A3 CONTRADICTED. Does any fact the plan cites conflict with something else in these files? Quote BOTH sides. A
    summary line that contradicts its own section 40 lines earlier counts, and has happened here.
 A4 UNREAD EVIDENCE. Which existing document should obviously have been consulted for this direction and clearly
    was not? Name it.

PART B - THE ARTIFACT, if the plan builds or changes one
 B1 ALREADY BUILT. Does an op, recipe, helper or VI already do this, possibly under another name? Check
    tools/gscript.py's functions, tools/recipes/, docs/toolkit-capabilities.md and the claudeDev VI names.
 B2 ALREADY FAILED. Has this exact build been attempted and failed? What did the record say was the cause, and
    does the new plan address that cause or repeat it?
 B3 HELPER EXISTS. Is the plan hand-rolling something the toolkit already provides - indexing, identification,
    wiring, saving, censusing? Name the call.
 B4 ALREADY MEASURED. Has the question this artifact would answer already been measured and written down?

End with machine-readable lines, one per finding:
  PRIOR-ART: settled-already | refuted-already | contradicted | unread-evidence
  PRIOR-ART: already-built | already-failed | helper-exists | already-measured
  PRIOR-ART: novel
`novel` only if none apply. Do not invent slugs.

THESE VERDICTS STOP THE WORK. Any slug other than `novel` blocks the next build until someone opens your citation
and refutes it in writing. So be precise about what your citation actually covers: an over-broad match costs real
work, and a missed one costs a whole build cycle.

=== WHAT IS UNDER REVIEW ===
{
 "schema": "stageplan-lite/1",
 "stage": "stage_replay_swap (card 110-6; PD210(c), PD217(f)) - ONE display-loop replay copy; run as `tools/recipes/stage_replay_swap.py --plan 110`",
 "input": {"vi": "claudeDev\\D1_s1_disp_20260927_041648.vi", "md5": "245a10206b565cba0ba186bd891f5cb8",
           "graph": "tools/bench/graph_disp_20260927.json"},
 "input_tag": "disp",
 "input_pin": "disp",
 "stage_name": "stage_replay_swap_110",
 "task": "110-6",
 "out_json": "stage_replay_swap_110.json",
 "note": "Same two swaps as plan_replay_swap_78.json / _95.json. R0 (tools/bench/diag_c110f_dispgraph.log): the disp graph read live keeps #6810 -> get buff image-lost frames.vi and #22692 -> IMAQdx Get Image.vi and no other node calls either (plan_disp.json names neither uid). No second_input: S1's replay copy claudeDev\\replay\\D1_s1_replay_20260925_075422.vi (md5 126f8497..., stage_replay_swap_78.log) is REUSED and PINNED below (in-run md5 check).",
 "swaps": [
  {"uid": 6810, "old_callee": "get buff image-lost frames.vi", "new": "replay\\replay_get_buff_image.vi",
   "new_md5": "842ecad9a6674a5060ebb3d5522751a9"},
  {"uid": 22692, "old_callee": "IMAQdx Get Image.vi", "new": "replay\\replay_get_image_cal.vi",
   "new_md5": "afce0d04346fc58234d28bcc0fc42e55"}
 ],
 "extra_pins": [["replay buf stand-in", "replay\\replay_imaqdx_get_image_buf.vi", "a89dafc1db03feef7b528f0dd4fcc692"],
                ["S1 replay copy (reused)", "replay\\D1_s1_replay_20260925_075422.vi", "126f84975fca9f6124432a7e4decd0c8"],
                ["S1", "D1_s1_copy.vi", "3e3d23cefd3a334001aa9d6156bf1aee"]],
 "copies": {"disp": "replay\\D1_s1_disp_replay_{ts}.vi"},
 "decisions": [
  {"id": "R01", "action": "copy", "what": "dated byte copy of D1_s1_disp into claudeDev\\replay\\ (md5 == source)"},
  {"id": "R02", "action": "read", "what": "BEFORE: callee census; #6810 -> get buff image-lost frames.vi, #22692 -> IMAQdx Get Image.vi; wire-edge set E0; ES 1"},
  {"id": "R03", "action": "swap", "what": "replace_object #6810 -> replay_get_buff_image.vi"},
  {"id": "R04", "action": "swap", "what": "replace_object #22692 -> replay_get_image_cal.vi"},
  {"id": "R05", "action": "read", "what": "AFTER: callee diff == exactly the two swaps, wire-edge diff 0 after new->old uid remap, ES 1"},
  {"id": "R06", "action": "save", "what": "scripted save (ES 1 route)"},
  {"id": "R07", "action": "read", "what": "COLD (fresh LabVIEW): ES 1, census == warm; disp, S1, S1 replay copy and replay VIs md5 unchanged (stage pins)"}
 ]
}


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-20
tags: [hand-off]
---
??RESUMED ??USER 2026-09-27 17:4x: "1踰덈???吏꾪뻾?섎룄濡? ?쒖옉" (runner relaunched by the chat; first act = the ABBA, see ## NEXT).
(history) STOP (lifted 17:4x) ??USER 2026-09-27 17:1x: "吏湲??몄뀡 醫낅즺??寃? ?댄썑 而댄벂???щ???諛?湲곌퀎 ?ъ뿰寃?吏꾪뻾???덉젙". Runner stopped by the chat mid-cycle 110 (offline planning card, no LabVIEW open); the PC is being rebooted and the rotor adapter reconnected (D-2026-09-27-03). Do NOT relaunch until the user says so.
??Chat 2026-09-27 17:3x (user): "COM5 ?뺤씤 ?덉쑝?? 援щ룞 ?덉슜?섎룄濡???" ??PC rebooted 17:21, rotor reconnected; `diag_c105d_visa.py` after reboot PASS 6/0, viOpen Rotor/ASRL5 횞3 = 0 (`tools/bench/diag_c105d_visa_postreboot.log`). D-2026-09-27-02/-03 ANSWERED. **REAL RUNS ALLOWED again** (the "NO REAL RUN" clause below is lifted). Runner still stopped until the user says resume.
(history) Chat 2026-09-27 08:5x (user): the cycle-107 STOP was LIFTED ("洹??숈븞 猷⑦봽 遺꾪븷 鍮뚮뱶??怨꾩냽 吏꾪뻾?섎룄濡?). ?뵶 NO REAL RUN (camera / motor / bead-pick legs) until the user confirms COM5 in person (D-2026-09-27-03 open; diag_c105d_visa.py must return 0 first). Build-only work continues: display-loop part 2, then L2-A2. Original stop text: cycle 107 judgement, 2026-09-27 (outcome review 짠7, steer_107 FOLLOWED): every real run needs the rotor port, which NI-VISA still refuses (D-2026-09-27-03). Whether structural work continues meanwhile is D-2026-09-27-04. Remove this line only after the user answers; first act then = ## NEXT.
Chat 2026-09-26 01:4x: the chat STOP (cycle-88 boundary, to relaunch on card chat-M1 code) was REMOVED after cycle 88 ended and the runner relaunched on the new cycle_runner.py (judgement ladder, judge A/B, material Fable low). Not a user start; the user said "lint 寃利??댄썑 ?щ꼫 ?ш컻" (2026-09-25).
Chat 2026-09-27 03:3x: the chat STOP at the cycle-103 boundary was REMOVED and the runner relaunched on card chat-N4 code (judgement Opus high fixed, ladder high?뭢ax?뭚able low, firefighter Opus max, retrospective Opus high). Not a user start; continuous running through the weekend per the user.
?뵶 REDIRECT (user 2026-09-26 18:0x, chat): the plot speed-up is built as a SEPARATE DISPLAY LOOP fed by locals, not as an N-frame gate ??`docs/d1-loop12-17-split-plan.md` Pre-decided 210 supersedes 205??09; fgate work dropped; D-2026-09-26-02 answered. Cycle 98 (running) may finish its diagnosis card; cycle 99 starts from PD210(f).

# STATUS ??read this first. One screen. Detail is one layer down, never appended here. ?좑툘 **ONE SESSION AT A TIME** ??re-read `CLAUDE.md` + this. Narrative ??**`archive/2026-09-19-status-cycle47-relocate.md` (latest ??T2's block diff and what it closes, the readable-ORIGINAL correction, the five killed retrospectives)** + `archive/2026-09-19-status-cycle39-judgement.md` + `archive/2026-09-18-status-cycle34-n1.md` + `??cycle23-close.md` + the `archive/2026-09-1[678]-status-*.md` set.
??**DELIVERED:** ?윟?윟?윟 **Display-loop VI (cycle 104) = `claudeDev\D1_s1_disp_20260927_041648.vi` md5 `245a1020??** (PD217(e); ExecState 1, E3 PASS; NEVER RUN ??the ABBA is blocked by the rotor stop, PD217(g)) 쨌 ?윟?윟 **D1 S3 loop 1.5 = `claudeDev\D1_s3_loop15.vi` md5 `1a11d92aacabf7ec844d65b8af19f39f`** (482,312 B; byte copy of `D1_s3b_m4b_20260924_004214.vi`, kept; `tools/bench/promote_d1_s3_loop15.log` 5/0; ExecState 1 warm+cold, `computation_diff(S1,쨌)` 0 rows; STRUCTURAL + graph-equivalent under ASSUMPTION A, NEVER RUN; `docs/connectivity-map-plan.md` Pre-decided 147) 쨌 D0 (cycle 31) 쨌 N1 ACCEPTED (cycle 34) 쨌 D1 **S1** `claudeDev\D1_s1_copy.vi` md5 `3e3d23ce?? 쨌 D1 **S2** `claudeDev\D1_s2_loops.vi` md5 `6ff19497?? 쨌 D1 **S3a** both halves (`??boolcarrier_b3_20260921_010034.vi` md5 `dc14dd00??, `ExecState` 1, `Is Broken?` False) 쨌 D1 **S3b rows 1 and 2**. ?뵷 **THE CURRENT BED IS `claudeDev\D1_l2_a3_20260927_151224.vi`, md5 `14337cfd?? (L2-A3, delivered cycle 109, `docs/d1-loop12-17-split-plan.md` PD223(c); expected Error List file `tools/bench/errorlist_expected_D1_l2_a3_20260927_151224.json`; machine key `current-bed:` in ## NEXT). Its input `D1_l2_a2_20260927_132125.vi` md5 `807c803e?? (L2-A2, cycle 108) is kept. Before that: its input `D1_l2_a1_20260925_235224.vi` md5 `51d9b8a3?? (L2-A1, cycle 88) is kept. HISTORY: `claudeDev\D1_k_20260925_100155.vi`, md5 `6cf5b077?? (stage K, cycle 79, 2026-09-25; ExecState 0 by design) was the bed before it; `D1_s4_loop17.vi` md5 `4b621946?? (L7-R) is its input, kept; every other "bed" named below in this line is HISTORY (`D1_s3_loop15.vi` md5 `1a11d92a?? is kept as the S3 deliverable).** ??**M3a-1 DELIVERED (cycle-63 firefighter, run 5, 2026-09-22 01:0x): `claudeDev\D1_s3b_m3a_BROKEN_20260922_005732.vi` md5 `6b3c1f3c??, 22 gates pass / 0 fail, bytes DIFFER from the bed.** ??**M3a-2 DELIVERED AND INDEPENDENTLY VERIFIED (cycle 64, 2026-09-22 02:3x??2:5x): `claudeDev\D1_s3b_m3a2_20260922_023029.vi` md5 `3842f5e6f128226235dc78353f26ef44`, 303,823 B, 25 gates pass / 0 fail on the build and 15/0 on a separate read-only check anchored at the REGISTER UID. ?뵷 EVERY NEXT STAGE STARTS FROM THAT FILE.** ?뵶 **M3a-3b (ROW D) IS **NOT** DELIVERED ??NO FILE. ?좑툘 CORRECTED 2026-09-22 15:4x (prior-art `archive/peer/2026-09-22-priorart-c87-rowd-stagekit.md` A3): the standing reason given here ??*"its W1 gate measures that NO writer on disk can address a `FlatSequenceInnerTunnel` terminal sink (`tools/bench/c78_rowd_writer.log`)"* ??HAS BEEN FALSE SINCE CYCLE 82. `OpFsInnerTunnelConnect_v1.vi`'s `Wire Source` half IS the FSIT `LeftTerm` property node (`tools/bench/build_d1_m3a3b_d3.log:28`, `term_uid=7488`/`uid_back=7468` on 20/20 calls at `:58-60`), and `tools/bench/diag_c86_norbw.log:87`/`:97` records it WRITING wire 25324 onto `#7488`. THE REAL REASON ROW D HAS NO FILE IS THAT NO RUN HAS YET SAVED ONE. ?윟 **CYCLE-86's MEASUREMENT OUTCOME, never recorded until now: `tools/bench/diag_c86_norbw.log` (14:46) answered plan entry 111a YES on a byte-identical scratch of the bed with Remove Bad Wires rebound to a raising guard ??after `del_wire(7506)` `#7468` STILL RESOLVES (`uid_back=7468`, `:74`), `#7488` comes back BARE (`wire_a=0`, `:76`), the inner wire 7448 survives (`:77`), the connect then writes wire 25324 onto BOTH ends (`wire_delta 1`, `:87`/`:97`) and the net ends with ONE source owner `RightShiftRegister #23868`, `#4334` off, PD85 0, `Is Broken?` False (`:105-110`). It SAVED NOTHING and deleted its scratch (`:113`), and the log has NO `BGRUN END` (truncated mid-cell-B), so D5/D6/D7 were never reached.** THE BED IS STILL `claudeDev\D1_s3b_m3a3_20260922_081056.vi` md5 `33ef524e??, 306,951 B.** Both initial-value rows land the predicted source (`FlatSequenceInnerTunnel #4194` ??LEFT `#23880`; `#3974` ??LEFT `#23909`), the originals stay on their nets, `Wire.Is Broken?` False in a separate ordered pass, PD85 violations 0 on every walk. Still BROKEN BY DESIGN and NEVER RUN (34(f)); `ExecState` 0's cause is formally OPEN and is neither gated on nor reasoned from. The artefact is BROKEN BY DESIGN (uninitialised SRs ??initial values are stage M3a-2) and is NEVER RUN (34(f)). Two root causes were repaired and MEASURED on the way: the identity reader `wire_source_owner` (history-echo, now error-checked + uid-echo-verified, acceptance `diag_c68_echo_accept.log` 8/0) and `gscript._lv_gui` (unquoted spaced args = PowerShell parse error, so NO Evidence-carrying GUI action had EVER dispatched ??`archive/peer/2026-09-22-c72-guisave-foreground-r2.md`). The bed is byte-unchanged and all four md5 pins hold. S3-as-37(g)-defined is WITHDRAWN (cycle 53). **Read `docs/cycle27-plan.md` Pre-decided 84??0 BEFORE 78??3 (78/80/81/82 are WITHDRAWN)**, then 46, 42, 43, 44. Full chronicle VERBATIM ??`archive/2026-09-21-status-cycle67-locknotes.md` 짠2; banner VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠3; facts `??cycle31-d0-delivered.md` 짠1?벬? (read **짠4** before the first D1 click).
?좑툘 **SUPERSEDED, NOT A BED ??`claudeDev\D1_s3b_m3a3b_rowD_20260922_153612.vi`, md5 `c9d38bb194013ac7b916d073466078c7`, 307,093 B.** It is KEPT on disk (a real saved intermediate the user can open) but NO stage starts from it: it was saved carrying an unpurged second-pass junk `Invoke` (`Node` 636, `Diagram #686` 28 nodes). The Row-D bed is whatever the CLEAN re-run leaves ??**tell the two apart by this md5, never by the timestamp** (the `_REJECTED_?? rename is refused by the permission layer, as it was for `D1_s3b_m3a3_20260922_075611.vi`). Written 2026-09-22 16:1x as prior-art `archive/peer/2026-09-22-priorart-c87b-rowd-clean.md` A1's release.
?넅 **USER RULE 17:5x = `docs/cycle27-plan.md` Pre-decided 9 ??EVERY GUI action is capture ??locate ??act ??capture ??confirm; derived or remembered coordinates are NEVER clicked blind.** It turned v4's 13/3 into v5's 39/1.


## START HERE
1. **Cycle plan = `docs/cycle27-plan.md`** (cycle20/21 plans `superseded`; motor plan `docs/motor-limit-assurance-plan.md` **짠A.1 + "P2 live findings"**; master `docs/pre-rig-master-plan.md`; decisions `docs/decisions.md`; D1 `docs/d1-route-b-plan.md`, paused).
2. ?뵶 **NEVER patch a file with a `py - <<'EOF'` heredoc** ??one truncated **this file to 0 bytes** on 2026-09-17.
3. ?좑툘 `peer.ps1` only as `powershell -Command "& 'tools/peer.ps1' ??-TaskFile <f>"`, `-TimeoutSec >= 780`. ?넅 **2026-09-18 (user, TRIAL): codex's roles ??claude roles** ??failed prediction = `-Agent claude -Role hypothesis` SINGLE arm (`-Dual` only for a second opinion on our own tools); `-Kind fact`/`-Kind prose` with no `-Agent` ??fable/low thin; `outcome_review.py` ??fable/medium thin. Check routing free with `-DryRun`.
4. Six more operating hints (prior-art log naming 쨌 front panel open for edits 쨌 `guard_cycle`'s `FIXED:` release 쨌 `py_compile` tripping BUILD_RE 쨌 짠11u unsound 쨌 짠10 not authorised): **`archive/2026-09-18-status-cycle1-census.md` 짠1**. ?좑툘 `BUILD_RE` also fires on a plain `cp a.py tools/recipes/b.py` ??quote both paths (cycle23-close 짠3).

## LabVIEW execution lock

```yaml
labview-lock:
  status: released
  relocated_c81: lock keys owner_c74m8s3/owner_c74m8/owner_c73l7r/owner_c72ff/relocated_c72/owner_step6/owner_step5b2/owner_step5b/owner_step4b/owner_step4/step4_delivered/owner/v1_delivered/purpose/step3_delivered/owner_s1s2/purpose_step1_delivered/purpose_s2_delivered/known_limit_s3/purpose_s1s2/relocated_c68 RELOCATED VERBATIM -> `archive/2026-09-25-status-cycle81-relocate.md` 짠1
```
?뵷 **THE WHOLE CHAINED `purpose:` NARRATIVE ("PREVIOUS PURPOSE, unchanged and still true ????, cycles up to 64, 12,560 bytes on one line) RELOCATED VERBATIM (rule 4) ??`archive/2026-09-22-status-cycle64-locknotes.md` 짠1** ??nothing deleted, nothing rewritten; the `purpose:` key above now states only the CURRENT state.
?뵷 **ALL 50 HISTORICAL LOCK-BLOCK ENTRIES (cycles 48??7: 48 `owner_*`/`lock_*` keys, the superseded `status:` line, and the `motor:` key) RELOCATED VERBATIM (rule 4) ??`archive/2026-09-21-status-cycle67-locknotes.md` 짠1** ??that file also carries the three older `lock_relocated_*` pointers (into `??cycle5556-relocate.md`, `??cycle54-relocate.md`, `??cycle5153-relocate.md`, `??cycle49-relocate.md`, `??cycle48-lockkeys.md`). **Motor state, unchanged and still true:** limits LEFT ON since 2026-09-18 15:37 (PI TMN 0 / TMX 39 in RAM, ASI SL/SU 짹2 mm), ports closed. ?좑툘 The motor clause quoted in this line is HISTORICAL; the live motor state is the rig-state line below.
**Never assume an instance exited**: `tasklist | grep -i labview`. Fresh ??1,500 handles; unique scratch name/run.

## HARDWARE ??permission follows the RIG STATE. Current: **議곕┰ / ASSEMBLED** (machine key `rig-state:` below)
遺꾪빐 = motors ??ASI ??camera ??쨌 **議곕┰ ??WE ARE HERE (user 2026-09-23 14:2x "?ㅽ뿕 留덉묠")** = camera ?? motors/ASI ONLY through `tools/motor_gate.py` inside the envelope, LabVIEW allowed 쨌 ?ㅽ뿕以?= ??????and no LabVIEW use (was the state 12:3x??4:2x; header corrected 2026-09-23 23:4x by the cycle-68 material session). ?좑툘 ASI carve-out **RETIRED** (rule 1b); **only the user announces a state change**.
Rotor counter **0** 쨌 magnet full travel 쨌 camera 1280횞1024, offsets 0, 90.0009 Hz, never write `BinningHorizontal`; **a session open RESETS ROI *and* exposure** ??the acquisition loop applies `tools/bench/camera_contract.py`. **No beads on the rig.**
?넅 **SAFE MOTION ENVELOPE = THE CONTROLLER LIMITS + the gate's command-class denies** (user, 2026-09-18 15:2x at the
rig). PI `SPA 1 0x15/0x30` ??TMN 0 / TMX 39 (RAM, **never WPA**) 쨌 **PI DIRECTION (user 2026-09-27 18:2x, at the rig): 0 mm = CEILING (magnet farthest from the sample, = the negative limit switch `FNL` goes to); larger mm = DOWN, toward the sample** ??so a reference move is the safe direction and any "magnet is low" report means a LARGE mm value 쨌 ASI `SL/SU` absolute mm X ??.8475??.1525, Y ??.7744?╈닋0.7744 (persistent, **never SS Z**),
written+verified by `py tools/motor_gate.py --session start|end` from the user-editable `tools/bench/motor_limits.json`; `--execute` refuses without the session file (tools/bench/motor_session.json, present ONLY while a session is open) **and** a fresh matching readback.
The gate still refuses ?ㅽ뿕以? every ASI home/zero/save, PI GOH/FRF/DFH/RON/POS/SPA/WPA and all rotor motion (self-test `selftest_motor_gate2.py` 85/85, 2026-09-24; FAIL-exit self-test 10/10).
rig-state: 議곕┰   <!-- 2026-09-24 20:xx USER GRANT: "?밸텇媛??닿? 留먰븯湲??꾧퉴吏??紐⑦꽣 ?묒냽 ?덉슜?? ?ㅻ쭔 ?먯젏 ?뺤씤 諛?紐⑦꽣 由щ컠, ??媛吏??瑗??뺤씤 ?꾩슂" ??motors (PI, rotor, ASI) may be driven by the gate AND by a running main VI while the rig stays assembled, until the user withdraws it; PI reference + verify at session start and limits set/released with readback are never skipped; "?ъ씠??醫낅즺?섍퀬?쒕뒗 ?쒕?濡?LabVIEW ?꾨뒗寃??딆? 留먭쾬 (?뱁엳 移대찓?쇨? 怨꾩냽 Acquisition ?섎㈃ 湲곌퀎??醫뗭? ?딆쑝??" = runner end hook closes LabVIEW and verifies the process is gone. Earlier: 2026-09-23 14:2x user: "?ㅽ뿕 留덉묠. ?ㅼ떆 ?몄뀡 ?ㅼ뼱媛??臾닿??? ??rig stays assembled; motors/ASI only through motor_gate inside the envelope, LabVIEW allowed. Before: ?ㅽ뿕以?13:43 ("吏湲??ㅽ뿕以묒씠??) ??limits RELEASED and read back (PI 0..52, ASI 짹500, `tools/bench/motor_session_end_20260923c.log`), PI referenced at 0 (FNL, 13:36), servo on; no motor/ASI/camera/LabVIEW use until the user says otherwise. Earlier 13:3x, on the user's order ("?덇? ?쒕쾲 PI 紐⑦꽣 ?吏곸뿬蹂쇰옒? 0?쇰줈 ?대룞, 5珥??뺤?, 30?쇰줈 ?대룞, 5珥??뺤?, 0?쇰줈 ?대룞"): PI test moves through the gate to diagnose "PI doesn't respond to the main VI". Before that: ?ㅽ뿕以? restored 2026-09-23 13:11 after ONE `motor_gate.py --session end` on the user's order ("寃뚯씠?몃줈 ?댁쨾"): limits RELEASED and read back ??PI TMN 0 / TMX 52, ASI SL/SU 짹500 mm, position unchanged (`tools/bench/motor_session_end_20260923.log`). Set ?ㅽ뿕以?2026-09-23 12:3x on the user's words ("?닿? 怨??ㅽ뿕???쒖옉?섎땲 ??LabVIEW ?쒖슜? ?섏? 留먮룄濡?) ??no motor, no ASI, no camera, and NO LabVIEW use at all until the user announces otherwise. Previous: 議곕┰, set 2026-09-17 23:0x on the user's words ("?ㅽ뿕 1李⑤줈 ?앸궗?붾뜲, 由ш렇???좎??섎뒗 以? + "議곕┰ ?곹깭?먯꽌????踰붿쐞 ?덉씠硫?紐⑦꽣 ?덉슜??) 쨌 the gate's ONE machine-readable key, parsed by motor_gate.rig_state(); ONLY the user's announcement may set it to 遺꾪빐 / 議곕┰ / ?ㅽ뿕以? Keep it at the start of the line, unquoted. -->

## Where things stand ??the three ??lines VERBATIM in `archive/2026-09-18-status-cycle36-relocate.md` 짠4
??tunnel ops BUILT + FUNCTIONALLY VERIFIED (38/38, ?좑툘 **do NOT re-run the recipe, run 1 is the record**) 쨌 ??the "ZERO runnable experimental VIs" gap is BROKEN ??`tools/bench/drive_original_copy_v5.py` drives a plain copy of the original unattended end to end, twice 쨌 ??N1 accepted ??the GPU kernel is cleared for D1. **Order is D0 ??D1 ??D2** (`docs/cycle27-plan.md` Pre-decided 1). Prose VERBATIM ??`archive/2026-09-21-status-cycle67-locknotes.md` 짠3; earlier ??`archive/2026-09-18-status-cycle22-close.md` 짠2.

## OPEN ??**items 1??0 VERBATIM in `archive/2026-09-17-status-runner-build.md` 짠2**; the five CLOSED items (32 쨌 55 쨌 56 쨌 51/52/52a 쨌 53's mechanical half) VERBATIM in `archive/2026-09-19-status-cycle46-relocate.md` 짠5, which forwards to `??026-09-18-status-cycle36-relocate.md` 짠5?벬?. ?좑툘 Two riders survive there: 32 is NOT to be closed unilaterally (the next outcome review judges it), and `audit_cycle` C4 still understates spend (retrospective-cycle31 F4). Only the live items below.
38/39/41. ?윞 **LIVE PART ONLY: `SR_QUEUE_AUTHORISED` stays False for good; `TEMP_SINK_AUTHORISED` is True for the `Z/dZ` row only** (Pre-decided 13 + 13a), and `Z/dZ` is now MEASURED WIRED (Pre-decided 19). `VI.Get Errors` 452 NOT built and `docs/d1-route-b-plan.md` 짠10 NOT AUTHORISED. ??the stall-watchdog liveness item is CLOSED by cycle 40's repair. Full text + run-3 history ??`archive/2026-09-19-status-cycle40-close.md` 짠2.
53. ?뵶 **The JUDGEMENT half STAYS OPEN, both review arms:** `POS` only declares the present location to be a coordinate and PI's `0x15/0x30` are relative to that zero, so **nothing we can read proves the controller zero still equals the ORIGINAL physical zero** ??i.e. that 0??9 still fences the intended physical window. VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠9; dispositions `archive/peer/2026-09-18-pi-err5-unreferenced-{codex,opus}.md`.
54. ?뵶 **TWO RULES YOU MUST FOLLOW, reasoning relocated ??`archive/2026-09-19-status-cycle40-close.md` 짠3.** (a) **The retrospective is the LAST thing a session runs** ??`guard_bash.py:226-227` marks the session retro-done on ANY `retrospective.py` in command position, and `guard_session` then refuses every later dispatch; nothing clears the mark. (b) **Dispatch in the FOREGROUND and wait; when something must run in the background, HOLD THE TURN OPEN until it lands** ??a `claude -p` session cannot take results as they arrive, and ending the turn kills the child. Repair named, deliberately NOT BUILT.
42/43/46/47. ?윞 **LIVE PART ONLY** ??42 ?좑툘 undisposed reviews + `audit_cycle` A2/A3 SELF-REFERENTIAL, not fixed (?좑툘 A4 counts a whole DAY, so it charges the previous cycle's files to this one ??retrospective-cycle40 F4) 쨌 46 ??**CLOSED 2026-09-23 ??FALSE PREMISE**: `SetCommand_signed.vi` IS on disk (`claudeDev\SetCommand_signed.vi`, md5 `ec87a265??, hardware-verified 2026-09-14); the "no disk" claim was a search-scope artefact. The real remaining item is the stage-2 repoint of the nine rotor call sites (Pre-decided 133) 쨌 **47 ?뵶 JUDGEMENT: the audit A1/A2/A3 remedy is NOT a `logclass` entry.** 43 and 48/48a/49/50 ??CLOSED. Full text ??`archive/2026-09-19-status-cycle40-close.md` 짠4.
57. ?윞 **NEEDS JUDGEMENT RATIFICATION (cycle 68, material):** `guard_peer.py` now (a) formats its refusal through a drive-safe `_rel()` ??the same helper `guard_cycle.py:518` has carried since 2026-09-17; without it the hook RAISED instead of refusing when the failing log sat on another drive (`tools/bench/jev_discharge.log:21-26`, rc=99) ??and (b) skips a failing log whose LAST `BGRUN START` command is a **Jev script**, the other half of the user's 2026-09-22 "Jev??硫댁젣" exemption (until now wired only into `RUNNER_RE`, the COMMAND side, so a Jev self-test bundle's fixture text ??`STOP:`/`FAIL` by construction ??armed the gate against every other run). Scoped by the COMMAND, never the filename. Self-test `tools/bench/selftest_guard_peer_jev.py` **17 pass / 0 fail**, two new cases: C7 (a newer Jev log does not become the blocking log) and C7b (a non-Jev build that merely MENTIONS a Jev script still gates).
58. ?윞 **FOR THE USER ??three known limits of the new autofocus loop (loop 1.5) in `D1_s3_loop15.vi`** (decision: `docs/connectivity-map-plan.md` Pre-decided 147(b)). The new loop starts an autofocus when the "focus now" signal switches from off to on. (1) If **Frame rate** is set to 1 the signal is on every frame, so the new loop focuses once instead of every frame. (2) If you run the VI again without reopening it, the first autofocus can be skipped when the previous run stopped on a focus frame. (3) If loop 1.5 falls more than one frame (~11 ms) behind, that one scheduled autofocus is skipped; focus values are not saved data. Tell us if any of these matters for your experiments.

## NEXT
?윞 **CARRY (from the 2026-09-25 verification review `archive/peer/2026-09-25-hyp-lintverify-20260925.md`, not blocking): card flags are checked only on the top-level command (a child process could reach LabVIEW under labview=none); a stage run launched outside bgrun is not counted by the retry cap; a bgrun record failure is only logged (`tools/bgrun.py:219-220`). Close in a tooling cycle, deliverable-first.**
current-bed: D1_l2_a3_20260927_151224.vi
<!-- ^ machine key read by tools/errorlist_check.py current_bed_text(); without it the bed is chosen by mtime among D1_*.vi names in this file, and the newer D1_s1_kswap_* would silently take over (review archive/peer/2026-09-26-c88-reuse-stalepin.md). Change it only when a new bed is accepted. -->
?윟?윟 **FIRST ACT of cycle 110 (relaunch, USER 2026-09-27 17:4x "1踰덈???吏꾪뻾?섎룄濡?) = `docs/d1-loop12-17-split-plan.md` Pre-decided 220(g)(2): ONE ABBA per 217(f) through `tools/bench/diag_c104_abba.py`** (A15 B15 B15 A15, A = `claudeDev\D1_s1_copy.vi`, B = `claudeDev\D1_s1_disp_20260927_041648.vi`, criterion unchanged). COM5 cleared: `diag_c105d_visa.py` PASS 6/0 after the 17:21 reboot (`tools/bench/diag_c105d_visa_postreboot.log`); D-2026-09-27-02/-03 answered; real runs allowed. Then 220(g)(3): GAIN ??the 210(c) replay; NO DIFFERENCE ??re-plan with the user. **L2-B1 comes AFTER the ABBA:** interrupted cycle 110 already planned it (results 110-1..3; card `tools/bench/cards/task_110-4.json` = the ONE launch, launch gate ALLOW, plan md5 9fb69b9b) ??re-issue that card, do not re-plan.
(superseded 17:4x) ?윟 **FIRST ACT of cycle 110 = `docs/d1-loop12-17-split-plan.md` Pre-decided 223(b): ONE material card plans L2-B1 offline from the new bed `claudeDev\D1_l2_a3_20260927_151224.vi` (md5 `14337cfd??).** Group B goes to loop 1.2 as in 짠2, B1..B3 at ??13 rows each. Rows come from `tools/bench/d1_rewire_sources.json` cross-checked against `build_d1_v0.json` (PD158). The card reads the targets of `#30117`/`#4580`, writes the split page + `plan_l2b1.json` (stagesim-finalized) + a ??20-line stagekit recipe, runs dry + pre-run + prior-art, then makes ONE launch ??`claudeDev\D1_l2_b1_<ts>.vi`, and in the same card writes the new file's explicit expected Error List file (PD223(a)). Launch scripts with `py tools/bgrun.py --material ?? and `--retry-card`; env-var prefixes are refused (PD223(c)). The display split on this chain (DISP-D1) waits for the ABBA, which still waits on COM5 (D-2026-09-27-02/-03 open; no real run).
- **CYCLE 109 in brief ??L2-A3 DELIVERED (PD223):**
  - 109-1 BLOCKED 3/0 (permission, not a fault): L2-A2's 35 Error List items = L2-A1's class counts; RBW same 29 uids. Explicit expected file written; its reverdict ran in 109-2: OK.
  - 109-2 FAIL 28/1: recipe LB fixed (`term_uid`), all gates in dry, `Is Broken?` after the save False 횞2; saved `D1_l2_a3_20260927_151224.vi` md5 `14337cfd??. Gate D failed on a simulator uid rule only.
  - 109-3 PASS 5/0: stagesim keeps the stub uid (self-test 66/0, no regression on l2a2/disp); D replays PASS; the new bed's Error List (29) is attributed and its expected file verdicts OK. **New bed.**
  - L2-B destination DECIDED (PD223(b)): all of B ??1.2; DISP-D1 later, after the ABBA.
  - Retrospective-cycle109 (`archive/peer/2026-09-27-retrospective-cycle109.md`, annotated): `device-failed` 1 min ACCEPTED. The launch gate refused a read-only `py -m pyflakes <recipe>`. **The same first card of cycle 110 builds the fix** (`docs/violation-decisions.md` device-failed 15:49: `launched_py` treats `-m` module paths as arguments, `prerun_gate` strips lint segments, self-test 3 cases). Card rule from now on: a conditional write is a gate, and I decide the write.
  - ??DONE 2026-09-27 17:4x (applied from the interactive chat, commit 252fd99; `grep -c "MATERIAL=1 py tools/bgrun"` = 0 in all four material*.md; settings.json matcher already `Agent|Task|SendMessage`): `.claude/agents/material.md:61-62` prescribed the refused `MATERIAL=1` prefix; the permission layer blocks our edit (replacement text `tools/bench/audit_c7_agent_patch.md`).
- (history) ?윟 **FIRST ACT of cycle 109 = `docs/d1-loop12-17-split-plan.md` Pre-decided 222(g): ONE material card that (1) patches `tools/recipes/stage_d1_l2a3.py`'s gate LB (line 66) to count ControlTerminal rows by `term_uid` in `report_all('ControlTerminal')`; (2) makes every gate run in dry mode; (3) adds an ordered `Is Broken?` read of both re-wired nets after the save; (4) greps `tools/recipes/stage_*.py` + `tools/stagekit.py` and fixes every `term_class` index on `allterms.read_terms` rows; then re-dry, pre-run and prior-art, and ONE relaunch of L2-A3 from `claudeDev\D1_l2_a2_20260927_132125.vi` ??`claudeDev\D1_l2_a3_<ts>.vi` (end cdiff == 6 open rows). Then decide L2-B1's destination (1.2 vs display loop) from `tools/bench/facts_c108c_groupB.md` (PD221(e)/222(f)). Still NO real run until the user confirms COM5 (D-2026-09-27-02/-03 open).**
- **CYCLE 108 in brief ??L2-A2 DELIVERED; L2-A3 ran all 6 ops at diff 0 and died on a recipe-gate bug before its save** (PD221??22):
  - 108-1 PASS 20/0: `claudeDev\D1_l2_a2_20260927_132125.vi` md5 `807c803e??, 308,008 B, end cdiff == the 8 planned open rows, gui_save, never run. New bed.
  - 108-2 BLOCKED 3/2: L2-A3 plan (rows 10382.x / 11529.x by indicator + Local, CLAUDE.md 1c''); `#10886` gates the autofocus (motor trigger, no saved data); row 11529.x lacked a verb (SelectorTunnel outer face).
  - 108-3 PASS 5/0: group-B consumer table `tools/bench/facts_c108c_groupB.md` (only `#2626` ??writer `#376` is non-display).
  - 108-4 BLOCKED (my card rule): verb built + scratch-verified 24/0 (`gscript.create_indicator_nested`, SelectorTunnel).
  - 108-5 PASS 5/0: runner `gates_due` at cycle start (live at the next relaunch), UNROUTABLE ??dry FAIL, VISA-refused leg ??SKIP. Owed retrospective-cycle107 device is BUILT.
  - 108-6 FAIL 3/1: stagexec routes SelectorTunnel (106/0); L2-A3 run 1 STEPX 01??6 diff 0, then KeyError `term_class` at recipe :66; nothing saved.
  - Retrospective-cycle108 (`archive/peer/2026-09-27-retrospective-cycle108.md`, annotated): `repeated-failure-class` 12 min ACCEPTED (mine: 108-4 had already reported the missing key, and my 108-6 card did not grep for it). Remedy = cycle 109's first card (grep + fix every `term_class` read; gates also run in dry mode).
  - User decisions still OPEN: D-2026-09-27-02, -03 (COM5 / rotor port: every real run waits on them).
- (history) ?뵶?뵶?뵶 **RUNNER STOPPED AFTER CYCLE 107 ??waiting on the user (D-2026-09-27-03 rotor port, D-2026-09-27-04 structural work meanwhile). FIRST ACT after the fix = `docs/d1-loop12-17-split-plan.md` Pre-decided 220(g):** (1) with LabVIEW closed, `tools/bench/diag_c105d_visa.py` must read `viOpen('Rotor')` and `viOpen('ASRL5::INSTR')` == 0; (2) ONE ABBA per 217(f) through `tools/bench/diag_c104_abba.py` (A15 B15 B15 A15, A = `D1_s1_copy.vi`, B = `D1_s1_disp_20260927_041648.vi`, criterion unchanged); (3) on GAIN, the 210(c) rule-1a replay; on NO DIFFERENCE, re-plan with the user. If D-04 says "continue structural work", the next build is L2-A2: `tools/recipes/stage_d1_l2a2.py` (md5 `f00a7e53??, plan `tools/bench/plan_l2a2.json` `f086df8b??, dry and pre-run already PASS), after judgement settles its three opens (PD220(d)). The display recipe still owes its recorded top-level dry (PD220(e)).
- ??**BUILT in cycle 108 (card 108-5, `tools/cycle_runner.py:886,917,1373`; live at the next runner relaunch ??the chat relaunches at a cycle boundary). Cycle 108 ran both `--due` checks before its first dispatch (empty).** (history) **OWED BEFORE ANY BUILD after the restart (retrospective-cycle107 `device-failed`, accepted, threshold 1; `docs/violation-decisions.md` device-failed 08:30):** the FIRST card makes `cycle_runner.py` run every guard_cycle "due" check at cycle start (`violations.py --due`, `outcome_review.py --due`, retrospective debt, and the recorded-dry/prior-art state of the recipe named in `next.json`), write the list into the cycle card as `gates_due`, and run a due outcome review before the judgement session. Self-test: 7 retrospectives since the last outcome review ??`gates_due` includes it. Until it exists, the judgement session runs `py tools/outcome_review.py --due` and `py tools/violations.py --due` BEFORE its first dispatch. Also owed: the display recipe's RECORDED top-level dry (`stage_prerun --dry tools/recipes/stage_d1_disp.py --from-step 33`, gate now clear), before any launch of that recipe. Decision-header times are always HH:MM.
- **CYCLE 107 in brief ??the ABBA was refused again at the VISA check; L2-A2 is ready; the outcome review stopped the runner** (PD220):
  - 107-1 BLOCKED 4/1: the ABBA leg 1 was refused in 13 s with LabVIEW never started (`tools/bench/disp_107_abba.log:5-8`). The stop record now passes `--dry/--prerun` (25/0), and the newline split is done (regression 23/23). The recorded dry was refused by `guard_cycle`, because my `HH:Mx` decision-header times do not parse (`tools/violations.py:94`). The headers are rewritten, and `--due` is empty.
  - 107-2 PASS 5/0: L2-A2 = 1 row (`#10757 'element'` ??`#23541`), recipe 99 lines, top-level dry + pre-run recorded, prior-art novel. NOT launched.
  - 107-3 BLOCKED 2/1: the display recipe's prior-art is novel; its dry was refused because the outcome review was due.
  - Outcome review (`archive/peer/2026-09-27-outcome-review-20260927.md`, annotated, ACCEPTED): refuted, with 5 OUTCOME-VIOLATIONs (new: `product-not-runnable`). It says to stop the runner, get D-03 answered, run one ABBA, and not fall back to L2-A2.
- (history) FIRST ACT of cycle 107 = `docs/d1-loop12-17-split-plan.md` Pre-decided 219(f). (1) One material card runs the 217(f) ABBA (A15 B15 B15 A15, A = `D1_s1_copy.vi`, B = `D1_s1_disp_20260927_041648.vi`, criterion unchanged) through `tools/bench/diag_c104_abba.py`. Its new leg guard (`tools/bench/drive_legguard.py`) opens `Rotor`/`ASRL5::INSTR` through NI-VISA before leg 1 and refuses the leg in seconds, with LabVIEW never started, while the port is refused. (2a) ABBA numbers ??judge against 217(f); GAIN ??the rule-1a replay (210(c)). (2b) Leg 1 refused (D-2026-09-27-03 still open) ??do NOT wait: name the next M3 build sub-stage from the bed `D1_l2_a1_20260925_235224.vi` in the plan's 짠2 table (saved-file name + pass criteria) and dispatch it, structural only. **In the SAME first card (retrospective-cycle106 `device-failed`, accepted ??threshold 1, no longer a carry):** `stop_record` lets `stage_prerun --dry/--prerun <recipe>` through and still refuses launches (negatives `tools/hooks/material_marker.log:2335`/`:2338`), accepted by a RECORDED top-level dry of `stage_d1_disp.py` (sha `d62f876d`). **Card rule from 107: a gate refusal is returned BLOCKED, never re-run through a self-test child or other exempt route.** Carries: `launched_plan_runs` newline split; the display recipe `1d1784ab` owes a prior-art round before any launch.
- **CYCLE 106 in brief ??the rotor port is STILL refused; the ABBA driver now guards itself; the owed stage tooling is DONE** (PD219):
  - 106-1 PASS 4/0: `viOpen('Rotor')`/`ASRL5` 0xBFFF0072 3/3 at 06:56, COM6 fine, no LabVIEW (`tools/bench/diag_c106a_visa.log:6-23`). The recorded-frame replay copies keep the rotor `Configure.vi` (uid 30064), so the replay is blocked too.
  - 106-2 PASS 47/0: leg guard = VISA precheck before each leg, loop ends on a refused leg or an A leg failing before pick 1, modal-dialog watch ??PrintWindow text + direct kill. Live: the real ABBA refused leg 1 without LabVIEW; a bypassed S1 leg caught the real dialog and killed LabVIEW 1.46 s later.
  - 106-3 PASS 5/0: stagesim finalize with labels + fs pairs (0 class-4 noise), recipe 144 ??90 lines, pre-run X9 verb-precondition and X10 memory-margin checks; stagexec 104/0.
  - 106-4 PASS 5/0: gui_save Evidence = the user's wording, stop_record `wc -l` twin, `selftest_guard_bash_jev` 12/0, `peer.ps1` `loss_usd="?"`?뭤ull, audit A1/A3 skip `jev_*` logs (real data 145/145).
  - 106-5 PASS 5/0: X10 fails ??690 MB (+ WARN when unmeasured), `find_graph` uses the plan's base graph, `launched_py` newline split, Part-B DRY of the 90-line recipe PASS (E3 6 == 6) ???좑툘 but only as a self-test child with `--no-record`, after the stop record refused the top-level dry twice; no dry record exists (retrospective-cycle106 `device-failed`, `archive/peer/2026-09-27-retrospective-cycle106.md`, annotated).
  - Violation decisions 07:4x (`docs/violation-decisions.md`): retrospective-cycle104 `repeated-failure-class` ??device BUILT (106-2); retrospective-cycle105 `inference-over-measurement` ??no new device beyond the VISA precheck.
  - **User decisions still OPEN: D-2026-09-27-01, -02, -03** (-03 blocks every real run: PC restart / replug the rotor USB-serial adapter / NI service restart by script).
- **CYCLE 105 in brief ??THE RUN STOP IS FOUND: NI-VISA refuses the rotor port even with no LabVIEW running** (PD218; when it began, and whether our forced LabVIEW kills caused it, is unmeasured):
  - 105-1 FAIL 25/2: a modal untitled LabVIEW dialog appears 0.41 s after Run and holds S1 paused; the screenshots showed only the covering desktop app. #30488's value stays unread (no VISA-constant reader).
  - 105-2 PASS 14/0: new read-only `lv_gui.ps1 shotwin -Hwnd` (PrintWindow). Dialog text: **"Error -1073807246 at VISA Open in Configure.vi ??the resource is valid, but VISA cannot currently access it"**. Candidate, unmeasured: 104-6's "Run returned after 4 s" was the driver's Esc tap closing it.
  - 105-3 PASS 17/0: COM5 is FREE at the OS level during the dialog; no USB plug/unplug/config event since 09-26 12:00.
  - 105-4 PASS 6/0: **with LabVIEW closed, NI-VISA `viOpen('Rotor')` and `viOpen('ASRL5::INSTR')` fail the same way 3/3, `CreateFileW(COM5)` works, and `viOpen('ASRL6::INSTR')` (the other FTDI adapter) works 3/3** (`tools/bench/diag_c105d_visa.log:6-23`).
  - ??**User decision D-2026-09-27-03 OPEN: PC restart / replug the rotor USB-serial adapter / we restart NI services by script.** No VI is changed and the rotor port is not re-pointed (218(b)).
  - Retrospective-cycle105 (`archive/peer/2026-09-27-retrospective-cycle105.md`, annotated): `inference-over-measurement` 28 min ACCEPTED (mine: 105-3 assumed an OS-level port holder before the 12 s VISA-only check) ??PD218(e): when an error names a resource layer, open that resource through the same layer outside LabVIEW first. Also accepted: a diagnostic leg kills LabVIEW right after its last capture, and every leg driver checks the VISA open before Run (218(d)).
- **CYCLE 104 in brief ???윟 THE DISPLAY-LOOP VI EXISTS: `claudeDev\D1_s1_disp_20260927_041648.vi` md5 `245a10206b565cba0ba186bd891f5cb8`, 479,946 B** (PD217(e); STRUCTURAL + graph-equivalent, NEVER RUN):
  - 104-1 FAIL: Part-B run 1 stopped IN op 43 on a stagexec lookup bug (owners keyed by simulated ids, read with a real uid).
  - 104-2 FAIL 6/1: fixed (`stagexec.py` self-test 93/0); run 2 did ops 34??7 at diff 0, W1 PASS, ExecState 1; E3 6/21.
  - 104-3 PASS: the 15 missing rows are simulator-graph artefacts (no labels / fs pairs), present on the unedited S1 and with sources == S1 ??**PD217(c): E3 = class 1?? rows (6) + class-4 sources == S1**, also checked in the dry run.
  - 104-4 PASS 8/0: run 3 saved the file by script; E3 6 == 6, 15/15; peak 613 MB (the op-33 cut had room). Recipe 144 lines.
  - 104-5 FAIL: the ABBA has NO numbers ??all 4 legs (A and B) stopped before pick 1 with the rotor `Configure.vi` window open (INDEX row 57 NON-RESULT).
  - 104-6 FAIL 11/1: reproduced on the S1 copy alone; Run returns after 4 s with no error; COM5 free; no dialog seen at the capture. Review `archive/peer/2026-09-27-c104-6-configure-empty-resource.md`. User questions D-2026-09-27-01/-02 still open (-02 partly answered by 105-3's PnP read).
  - Zero read-only stop-record refusals this cycle (retrospective-cycle103's `device-failed` check).
  - Retrospective-cycle104 (`archive/peer/2026-09-27-retrospective-cycle104.md`, annotated): `repeated-failure-class` 17 min ACCEPTED (legs 2?? ran after the known-good A leg had failed) ??every leg driver stops the loop when an A leg fails before pick 1 (PD217(g)); the diagnostic leg of cycle 105 must carry that stop.
- **CYCLE 103 in brief ??PART A IS SAVED:**
  - 103-1 PASS 6/0: split page `tools/bench/cards/split_plan_103.md` (prior-art novel); Wait (ms) donor `claudeDev\OpWaitDonor_v0.vi` md5 `6fc80d60?? (uid 163); `r7_wait` ??prim; re-sim the same 21 open rows; recipe Part-A mode.
  - 103-2 FAIL: ops 1??0 matched, but the memory stop fired at 703.8 MB on the step-40 read (limit 700). Nothing saved. The cut moved to op 33 (216(f)).
  - 103-3 PASS 5/0: **`claudeDev\D1_s1_dispA_20260927_024535.vi` md5 `16c2ca00a114a227a81612dd49d111cc`**, ops 1??3, real step 33 == simulated, peak 677 MB, gui_save, broken by design, never run.
  - 103-4 PASS 6/0: Part-B `--from-step` entry built and checked offline (stagexec self-test 91/0); hook repairs (stop-record read-only refusal, selftest_stagekit classing) 17/0.
  - **D-2026-09-27-01 is still OPEN for the user**; cycles 102??03 proceeded under its recommendation ("yes").
  - Retrospective-cycle103 (`archive/peer/2026-09-27-retrospective-cycle103.md`, both items accepted): `inference-over-measurement` (18 min, mine: the op-40 cut ignored r7's memory curve) ??DEVICE: pre-run memory-margin check; `device-failed` (stop-record tail before the 03:14 repair) ??no new device, and cycle 104 must show zero read-only refusals. **The tooling card right after Part B = memory-margin check + verb-precondition check (owed since 01:55) + recipe ??120 lines + gui_save Evidence + `peer.ps1` `loss_usd="?"`?뭤ull + the `guard_bash_jev` fixture.** Part B's worst case from files is ??685 MB (annotation). Material cards: return review design findings as `open`; do not accept them in the card.
- **CYCLE 102 (firefighter, fable/low) in brief ??the `gate:e1` block is cleared through op 40 of 47; NO FILE:**
  - PD214(c) WARN rule is code (`stagexec.classify_step_diff`, 78/0); PD214(d)1 flip seed fixed and MEASURED first (`diag_c102_probe_b.log`; the prior-art "settled-already" on it was REFUTED from files); PD214(d)2: the plan md5 difference is provenance-only (R6b content gate 6/0).
  - r6 stopped at op 31: `stagekit.create_local_read` made WRITE locals (donor `OpCreateLocal_v0`). Fixed: `gscript.create_local_read` = `OpCreateLocalRead_v0` with `Write?`=False.
  - **r7 ran ops 1??0 diff 0 (ops 26??0 for the first time)**, stopped at op 41: `stagekit.copy_in` only works on the NI Moving-Objects pair. Private memory 690 MB vs MEMSTOP 700 at op 40 ??the stage is split (PD215(b)). Retry cap spent (r6, r7); LabVIEW closed.
  - 214(b) offline search: no new For?봚hile sample in cycles 71??01; the scratch move is still owed, non-blocking under 214(c).
  - Violation decisions written 2026-09-27 01:15 (`docs/violation-decisions.md`): device-failed ??device (stop-record read-only refusal + selftest_stagekit classing), owed in the first tooling card after Part A; inference-over-measurement ??no-device.
  - Retrospective-cycle102 (`archive/peer/2026-09-27-retrospective-cycle102.md`, both ACCEPTED): `wrong-ordering` (the split was due after r5; op 41's precondition was on file ??DEVICE: pre-run verb-precondition check, decision 01:55) and `device-failed` (stop-record read-only refusal recurring, same owed card). **Owed tooling card after Part A = stop-record repair + pre-run precondition check + selftest_stagekit classing.**
- **CYCLE 101 in brief:**
  - `guard_peer` jev-ledger exclusion PASS (29/0).
  - stagesim now models a created loop's body; record mode and the `create_local_read` index fix are in.
  - Real run r5 did ops 1??5 of 47 and stopped IN op 26 (fixed). S1 is unchanged; NO FILE.
  - Both escalation rungs are spent ??**D-2026-09-27-01 is OPEN for the user** (continue as planned?).
  - My "primitive deletes / SubVI keeps" rule was an unmeasured inference, and it was refuted.
  - Retrospective-cycle101 (`archive/peer/2026-09-27-retrospective-cycle101.md`, both items accepted): `inference-over-measurement` (mine, card 101-5) and `device-failed`. The stop record refuses read-only commands on a stopped recipe (`material_marker.log:2175`), and the launch gate classes `selftest_stagekit.py` as a stage. ??owed tooling card AFTER the stage card.
Stage pass criteria:
   - ExecState 1;
   - cdiff equals the 21 PD213(d) open rows plus the added objects;
   - the #25261 gate reads False;
   - no termless or loose-end wires beyond RBW's pre-existing uids;
   - saved by script.
   Then the ABBA vs S1 (15 picks, 120 s, 210(c)) and the replay.
- Standing: card `peers` = hypothesis, outcome, priorart. Every card that builds or edits a VI carries `gui: true`; on ExecState 0, read the Error List first.

?윞 **CYCLE 100 (PD213): every verb the display-loop stage needs exists, and its plan passes dry and pre-run. The stage run stopped at op 2 on a simulator-model gap. NO FILE.**
- 100-6 FAIL 4/2:
  - Max & Min names measured (`max(x,y)`, class Comparison); dry 0 unroutable; pre-run 8/0.
  - Run 1 stopped at E1 PARITY (the plan context had no loops or owners).
  - Run 2 got to PRIME parity 0, #25261 = False and STEPX 01 diff 0, then stopped at the op 2 BINDING check: the real run created a Diagram, and the simulation predicted nothing.
  - Retry cap spent; S1 unchanged; the outcome review ran.
- 100-1 (rows, 55 actions): stagexec could not execute `create` rows or nested (symbolic) diagrams.
- 100-2: four new ops, ExecState 1 cold. **#25261 = False**, so TurnOff starts False (PD212(c) settled).
- 100-3: stagexec `create` executor + `new:<alias>.body` diagrams; self-tests stagexec 70/0, stagesim 48/0.
- 100-4 (rung 1, Opus max) PASS 60/3: tunnel-face indicator, `create_control_nested` (refuses a wired sink), `set_visible`, `create_local_write`, and Max & Min by donor copy (`OpPrimCopyNested_v0`).
- 100-5 PASS: widened stageplan schema installed (0 regressions). The 21 end-cdiff rows are classified 15 / 5 / 0 / 1 into PD213(d) classes 4 / 1 / 2 / 3, with 0 unclassified. The pre-run's only failure is X4, on the 2 rows that 100-4 now covers.

?윞 **CYCLE 99 (PD212): the display-loop DESIGN is written and judged GO. No VI yet.**
- 99-1 FAIL 6/1 (`tools/bench/facts_c99_display.json`):
  - #8323 ??w10908 ??BuildArray #11261 ??For #1359 + WLC #11608.
  - #6085/#5696 are NOT display; they feed the ring.
  - The Force path costs 10.3 ms at 15 picks, and it is COMPUTATION. Moving only the indicator would miss 210(c), so the computation set moves too (212(b)).
- 99-2 FAIL 5/2 (`facts_c99b_display.json`):
  - The ring is w9215, 3-D DBL [15][2][20000], 4.8 MB.
  - There are five inbound edges, not three.
  - TurnOff is already a stop carrier for loop #25380 (Value property read).
  - `Wait (ms)` and `Visible = False` verbs are MISSING.
- 99-3 FAIL 23/2 at escalation rung 1 (`facts_c99c_bench.json`):
  - The moved set costs **??7.94 ms per frame at 15 beads** (scratch bench, a lower bound).
  - The ring-write cost is UNMEASURED: both bench routes went ExecState 0 when a panel terminal was moved into a For body. So no control terminal moves (212(i)3).
  - GO under a named ASSUMPTION; the ABBA measures the net gain.
- **Owed tooling card** (retrospective-cycle96 `device-failed`): `peer.ps1 -ReviewCard` must map `loss_usd="?"` to null; audit A1/A3 must stop counting `jev_gate.log`; cards must not demand a foreground peer dispatch.
- Unreviewed standing fail: gate `run1.L8` (bandpass panel) has failed in every leg since 92-3. Pick registration is not affected.
- D-2026-09-26-02 is ANSWERED by PD210. Do not start benchmarks on this PC while a cycle runs legs.
- Machine copy: `tools/bench/next.json`.

?윞 **CYCLE 98 (PD207??09, 211): the fgate break is EXPLAINED, and the fgate is then dropped by the user (PD210).**
- 98-1 PASS 53/0 (`tools/bench/diag_c98_fgate.log`):
  - ExecState is 1 at E1 and 0 after move A.
  - `move_into_frame` leaves 9 OLD severed wires with no terminal (8 in 7911, 1 in 639).
  - Remove Bad Wires on a scratch of the saved broken file gives ExecState 1 and 0 Error List items.
  - Saved: `claudeDev\D1_s1_fgate_BROKEN_20260926_175556.vi`, md5 `b114bb1b??, never run.
- 98-2 FAIL 45/2: deleting only those termless wires after move A still leaves ExecState 0.
- 98-3 FAIL 48/2 (rung 1, Opus max): an in-memory VI-level RBW after A removes the same 8 wires, and ExecState is still 0.
  - So my PD208(d) gate after every move was an unmeasured inference: `inference-over-measurement`, a judgement fault.
- 98-4 BLOCKED by PD210 (user): nothing was run.
- Retrospective-cycle98 (`archive/peer/2026-09-26-retrospective-cycle98.md`), both items accepted:
  - `inference-over-measurement`: when a fix card FAILS on a gate whose premise was never measured, the next card is the READ.
  - `device-failed` (the material-marker read-only refusal; audit A6 misses GUI use): added to the owed tooling card.

?윞 **CYCLE 97 (PD206): the gate is designed and its tools exist, but there is NO FILE yet.**
- 97-1 PASS 5/0 (`tools/bench/f1359_gate_facts_97.json`):
  - Nothing reads #8323 except a `Reinit To Dflt` writer, so step 0 passed.
  - **Magnet2Force #28083 feeds the ring history, so it stays UNGATED.** The gated set is the 11363-only nodes: IndexArray, Subtract, Median, FIR, Bundler (PD206(b)).
- 97-2 FAIL: the synthetic test fixture failed to build (loop_in 1055).
- 97-3 PASS 64/1 on escalation rung 1 (Opus max), with a scratch copy of S1 as the fixture:
  - `gscript.case_in`, `gscript.move_into_frame`, `set_control_label` (`claudeDev\OpLabelSet_v0.vi`), `tunnel_use_default` (`OpTunnelUseDefault_v0.vi`), `OpCaseFrames_v1.vi`;
  - documented in toolkit-capabilities and NAMES.
- 97-4 BLOCKED: my card's `peers` left out `priorart`.
- 97-5 FAIL 45/2 (`tools/bench/fgate_97_stage2.log`):
  - prior-art review came back novel twice; cdiff 0 rows, with 3 added objects; A's 16 and B's 3 edge tables are equal;
  - **ExecState is 1 after the wiring and 0 after `move_into_frame` A+B (`:395`).** Nothing was saved.
  - Reviews `archive/peer/2026-09-26-c97-fgate-es0.md` / `-r2.md` suspect orphaned severed wires (arithmetic only, unmeasured).

?윟/?뵶 **CYCLE 96 (PD204??05): the parallel For loop is REJECTED. The real per-bead cost is a DISPLAY graph.**
- 96-1 PASS 53/0 (INDEX row 56, `tools/bench/par1359_96_abba.json`), 15 picks, all legs 15/15:
  - lost frames: A (S1) **3,435 / 3,389** 쨌 B (par1359) **3,867 / 3,863**, i.e. +13 %, worse;
  - tracking iterations: A 7.7k 쨌 B 7.25k;
  - ??par1359 is rejected and the replay is moot. The file is kept, never shipped.
- 96-2: review `archive/peer/2026-09-26-c96-par1359-h1.md`, verdict refuted, accepted. Its likely causes are serialisation on the non-reentrant `Magnet2Force`, oversubscription (P unwired) and ring-fill memory work. It names `inference-over-measurement` for PD203(b)'s "only serialises" claim.
- 96-3 PASS 5/0 (`tools/bench/diag_c96_cons_trace.log:235-260`): #1359 ??BuildArray #11261 ??indicator #8323 only. Its other output feeds only its own history SR. No case gates it, so it runs every frame.
- Carries: `peer.ps1` fails to parse `loss_usd=?`; the 96-3 owner-tree parser has a G7 fail (not reused).

?윞 **CYCLE 95 (PD203): THE PARALLEL COPY EXISTS; the replay and the ABBA did not run.**
- 95-1 PASS 6/0: `stage_prerun` rejects a wrong-shape graph cleanly instead of crashing (md5 `56697c5c??, self-test 18/0).
- 95-2 read-only precondition, 19/0:
  - #7911 has no Feedback Node, no local or global write, no shift register;
  - Median and FIR are reentrant; FIR re-initialises on every call;
  - `Magnet2Force v3_for M270` is non-reentrant and stateless, so its calls serialise; not blocking.
- 95-4 PASS 84/0 (escalation rung 1, Opus max):
  - new op `OpForLoopParSet_v0.vi` (self-test 18/0);
  - `D1_s1_par1359_20260926_133751.vi`: STRUCTURAL, never run;
  - ?좑툘 it built from `tools/bench` because `guard_cycle` refused `tools/recipes`.
- The 4 DUE violation slugs were then answered: `docs/violation-decisions.md`, 13:47.
- 95-5 and 95-6 were BLOCKED by my own card scoping ("never save", the write globs, the peer list).
- The outcome review was due and ran at the close: `archive/peer/2026-09-26-outcome-review-20260926.md`. It returned 4 violations, and its steer is FOLLOWED.

?윟 **CYCLE 94 (PD202): THE PER-BEAD LEVER IS NAMED.**
- 94-1 passed 65/0 (INDEX 55, `tools/bench/t0_step4v2_94.json`). Six legs ran, and every one registered all its picks on the first try.
  - Lost frames: A11 1,672 쨌 B11 2,137 / 1,588 쨌 A15 4,277 쨌 B15 4,049 / 4,070. The stamps do not perturb at 11 or 15 picks.
  - The tracking loop #637 is compute-bound at 11 and 15 picks (period 13.1 / 16.7 ms, against the 11.1 ms camera period). Its period grows **+972 쨉s/bead**.
  - Site 4, the output of ForLoop #1359, grows **+760 쨉s/bead**. The kernel (#5058) grows only +188.
- 94-3 passed 32/0. #1359 has 0 shift registers, gets its count from auto-indexing, and has parallelism OFF.
  - Each iteration processes one history row: ring insert #8634, then Median #29009 and FIR #28233.
  - Its cost rises as the history ring fills: at 15 picks it goes from 1.3 ms to about 10 ms.
- ??The change is scheduling only (PD202(c)). Changing the filter maths would need the user's decision.
- Carry: `stage_prerun --dry` crashed with `KeyError 'terminals'` on `graph_s1_20260924.json` (PD202(e)).

?윟 **CYCLE 93 (PD200).**
- **The stamps' ~110 lost frames are EXPLAINED AND FIXED.**
- The hypothesis review (`archive/peer/2026-09-26-c93-h1-stamp-array-copy.md`, accepted) refuted the array-copy candidate.
- The cause: `t0stamp` v1 ran `FlushFileBuffers` inside `stamp()` every 1024 calls. Six sites flushed in the same iteration.
- Offline check: in the old B legs, the top-10 periods are exactly at iterations k쨌1024??, at 108??12 ms.
- `t0stamp` v2 has no I/O in `stamp()`. It is in place (`b35b398d??); v1 is kept as `claudeDev\t0stamp_v1.dll`.
- ABBA at 8 picks: unstamped **14 / 19** against stamped v2 **24 / 43**, under the limit of 53 ??**the instrument is CLEARED** (INDEX 54, `tools/bench/m8_flushfree8_93.json`). The clearance is thin: B still loses about 2횞 A, with a 24-vs-43 spread and n = 2.
- The scalar-only build is cancelled.

?윟 **CYCLE 92 (PD199).**
- **The UI-thread hypothesis is REFUTED.**
  - All 12 stamps were UI thread (`Any Thread?` False; `build_clfn`'s `reentrant=True` does not set it).
  - An any-thread copy was built: `claudeDev\D1_s1_t0at_20260926_090833.vi`, md5 `30a15c67??, 12/12 True warm and cold, cdiff 0 rows with 24 added.
  - ABBA at 8 picks: unstamped **20 / 22** lost against any-thread stamped **130 / 131** (UI-thread stamped was 138 / 144). So the instrument is NOT cleared (INDEX 53, `m8_anythread8_92.json`).
- ??**The harness capture fix works.** LabVIEW's own `LVDChild` held the mouse capture before pick 1 in 3 of 4 legs. One title-bar click released it, and all 4 legs registered 8/8 picks.
- ??**New ops:** `OpCLFNThread_v0.vi` (reader) and `OpCLFNThreadSet_v0.vi` (writer), documented in `docs/toolkit-capabilities.md` and `docs/NAMES.md`.
- ??**The bgrun reaper is built** (92-4 PASS 18/0). bgrun now writes a `BGRUN PID` line. `tools/bgrun_reap.py` marks a dead run's log `BGRUN KILLED`, and it runs at every bgrun start and in the runner's cycle-end hook. This closes retrospective-cycle90's `device-failed`. Pre-92-4 logs stay listed as "unfinished" and are never closed by hand (PD199(g)).

?윟 **CYCLE 91 (PD198).**
- ??**Step 3 is DONE.** `claudeDev\D1_s1_t0_20260926_055551.vi`, md5 `25ea4f7d??: 12 While-body stamps, with ExecState 1 read after every site. `computation_diff` is 0 rows with 24 added. It was saved by script, and the smoke run wrote 12 stamp files.
- ??**Step 4 ran** (`tools/bench/t0_step4_91.json`, INDEX row 51).
  - Only **site 4 grows with bead count**: the For #7911 output, which carries Median #29009 + FIR #28233.
  - It adds +255 쨉s/bead (panel normal) and +173 쨉s/bead (minimized).
  - ?좑툘 The 8-pick cell is frame-bound (11.14 ms against the camera's 11.11 ms), so "the kernel does not grow" is WITHDRAWN (retrospective-cycle91 finding 3). At 15 picks, site 4 fires 12.6 ms after `i` and the kernel 8.4 ms after it.
  - This is only a candidate lever until the instrument is cleared (PD198(c)).
- Also owed in the first act: log the capture window's class before pick 1 (a read, not a GUI act; asked by both reviews). With the reaper card: capture the quit dialog before taskkill (`archive/peer/2026-09-26-c91-t0step3c-quit.md`).
- ??(done 2026-09-27 17:4x, commit 252fd99) **FOR THE USER:** `.claude/agents/material*.md` still prescribe the refused `MATERIAL=1` prefix, and the permission layer refused the edit. The replacement text is in `tools/bench/audit_c7_agent_patch.md`; apply it.

?윟/?뵶 **CYCLE 90 (PD197).**
- ??**The stamp tool is DONE.** `claudeDev\t0stamp.dll` md5 `1ea78380??, self-test 4/0 outside LabVIEW. Scratch `claudeDev\t0stamp_scratch_20260926_040425.vi` md5 `5e4fd1f0??: ExecState 1; 0.30 쨉s per stamp, 1.40 쨉s with a 1024횞1280 U16 branch (no copy); handles flat; the negative case (site 64) is caught (`diag_c90_t0stamp_scratch_r3.log` 21/0).
- ??**Stamp-site table:** `tools/bench/t0_sites_s1.json`. `check N bead pos`, `save N xyz traces` and `grayscale color table` run ONCE, outside every While loop, so they are not per-frame costs.
- ?뵶 **Step 3 failed twice** (90-5 fable/low, 90-6 fable/medium; no file). The While-body route works: sites 0 and 2 are ExecState 1. `OpCreateConstOnTerm_v0` refuses a ForLoop owner (1055), and a reader index shift caused run 2's failure (patched, not rerun). There are 4 answered reviews under `archive/peer/2026-09-26-c90-*`.
- ??`audit_cycle` C7 now reads the plan named in `next.json` (self-test 8/0, 90-2). INDEX row 50 was added for the cycle-89 panel legs.

?윟 **CYCLE 89 DONE (PD196).**
- In-VI bracketing and a LabVIEW-primitive stamp helper are unreachable with our verbs (89-1, 89-2).
- The profiler cannot be scripted, and its GUI route failed its liveness test twice, so it was dropped (89-3, 89-4).
- **Display is a minor lever.** 15 picks, unmodified S1, panel minimized via COM, ABBA order: ctl 3,434 / 3,603 lost against min 2,616 / 3,286, about ??6 %. At 8 picks the two are equal (16 / 15). Roughly 30 % loss remains, so the main per-bead cost is neither display nor the kernel.
- ??The firefighter trigger now skips a recipe whose newest run passed (`tools/cycle_runner.py:401` `newest_run_passed`). Self-tests: ff 5/5, runner 10/10, ladder 11/11 (89-6). This closes retrospective-cycle88's `device-failed`.

?윟 **CYCLE 88 DONE.**
- **Bed = `claudeDev\D1_l2_a1_20260925_235224.vi` md5 `51d9b8a3??** (195(a)). The read-only P2 check passed 5/5 (`tools/bench/p2check_l2a1_88.json`). This is structural; the file has never been run.
- **Error List MISMATCH explained** (195(b)): all 11 extras disappear under Remove Bad Wires, and those 29 wires include none on a re-wired sink.
  - Cycle 87's uncapped licence classes were reverted.
  - An explicit `tools/bench/errorlist_expected_D1_l2_a1_20260925_235224.json` (35 items, exact counts) now replaces the derived licences for this bed.
  - Offline re-verdict: OK 0/0. Self-tests 18/0 and 5/5, including a negative case.
  - Reviews: `archive/peer/2026-09-26-c87-errorlist-extras.md`, `??c88-reuse-stalepin.md`.
- **Kernel swap: `claudeDev\D1_s1_kswap_20260926_004935.vi` md5 `e77b8d58??** (ExecState 1; rule 1a on INDEX rows 12/17/40). At 15 picks, 120 s, it lost **3,410 / 3,490** frames against **3,776** for the same-session S1 control (cycle 83: 3,331 / 3,161). ??no lever (195(c)); `archive/benchmarks/INDEX.md` row 49.
- Open, not blocking: `errorlist_check.compare():407` prints `missing` as None for norm_all entries (the verdict is still correct).

?윟 **CYCLE 86 DONE: THE L2-A1 FILE EXISTS.** Stage run 1 (card 86-5, 594 s) saved `D1_l2_a1_20260925_235224.vi` by gui_save. ExecState is 0 by design.
- E1: 42/42 ops match the simulator.
- PB cdiff equals exactly the 9 open rows.
- RBW: 29 bad wires, none on a re-wired sink.
- Peak memory 638 MB, no error 2.
- 5 P2 FAILs: the recipe's reader could not address SelectorTunnel sinks (`stage_d1_l2a1.py:90`). Review `archive/peer/2026-09-26-hyp-l2a1-p2-86-5.md` refuted a build fault.

How the run was made possible (PD192 ??193):
- stagexec now meters private MB and handles per op and per read (md5 `0d131139??, self-test 59/0).
- Most of cycle 85's handle growth was the VI LOAD: 33,987 ??45,631 handles.
- Error 2 recurred right after act 45 when there was a whole-VI read after every op: reads added +140 MB, edits +1.7 MB, and it failed at 695 MB.
- With 9 reads there was no error 2, so act 45 is not the cause. Whether it is the reads or accumulated memory is still OPEN (prior-art amendment).
- The recipe now reads only at checkpoints {0,15,19,23,27,28,40,41,42}, with MEMSTOP 700.
- The prerun needs `--graph tools/bench/sim/l2a1/graph_k_80_owners.json` (194(c)).
- The outcome review ran again: the same 4 verdicts, not a stop (user 2026-09-23). All 7 items in `decisions_pending.json` are ANSWERED; the "4 open questions" line below is stale.
?윞 **CYCLE 85 DONE (cycle 84 never ran: weekly usage limit).** No stage run was launched.
- The separator returned 5001, so the old 1057 came from the source cast (PD191).
- Three new ops were built, each self-tested with a negative case and handle-flat:
  - `ops\OpConstWire_v1.vi` `c978863c??, for op 35.
  - `OpCtlSinkWire_v1.vi` `ce9f2088??, for R41.
  - `OpTunOuterWire_v1.vi` `093b0539??, for R45/46.
- stagexec md5 `4186fcb4??, self-test 50/0. The dry run lists every unroutable row, and a uid-reuse guard was added.
- Dry run 42/42 with 0 unroutable; pre-run 8/0.
- On a real scratch, acts 1??4 had diff 0. After act 45, `report_all` raised **LabVIEW error 2 (memory full)** (`tools/bench/unroutable_l2a1_85.log:562`; review `archive/peer/2026-09-25-hyp-unroutable-err2-85.md`).
- D1_k is unchanged.
燧?Older (cycle 84 plan, now done up to step 2's dry/pre-run):
??**CYCLE 83 (firefighter, fable/low) = the PD188(d) load measurement RAN ??INDEX row 48, `tools/bench/m8_load_83.json`, 8 real legs 8/0, LabVIEW closed after each.** Total Lost Frames S1 copy vs `D1_s3_loop15.vi`, 120 s at ~89 frames/s (~10,680 frames): **8 picks 16 vs 12** (repeat 12 vs 14) 쨌 **15 picks 3,331 vs 3,493** (repeat 3,161 vs 3,269). Frame loss goes from ~0.1 % to ~??between 8 and 15 beads on BOTH VIs ??**the per-bead tracking cost (loop 1.2, M3) is the lever; the loop-1.5 split is neutral at this load.**
- ?좑툘 **150 Hz was NOT reached**: the driver wrote 150 Hz to the camera between legs, but EVERY `IMAQdxOpenCamera` reloads the camera file (`??NI-IMAQdx\Data\JAI Corporation SP-5000M-USB (??.icd`, 90 Hz) ??measured `tools/bench/diag_camrate_persist83b.log` 4/0 after the failed-prediction review `archive/peer/2026-09-25-hyp-camrate83.md` (accepted; `camera-acquisition-facts.md:642` corrected). The "150 Hz" cells are 90 Hz repeats. Real 150 Hz needs a VI-side setting or an `.icd` change ??**user decision D-2026-09-25-05**.
- ??(stale as of cycle 86: all ANSWERED in `decisions_pending.json`) The user had 4 open questions: D-2026-09-25-02 (`.cal` scope), -03 (autofocus limits, OPEN 58), -04 (a supervised S3 run with beads), **-05 (how to reach 150 Hz)**.
- Owed before the constant-source op (violation-decisions 16:10): make the stagexec dry run report EVERY unroutable row.

??**THE L2-A1 run from the bed `claudeDev\D1_k_20260925_100155.vi` md5 `6cf5b077??, Pre-decided 188(c) + 189:**
1. Op 35 needs a verb for a bare constant source: `#10739 ??#10950 'y'` and `#10929 ??#10757 'index'`.
   - First run the review's cheap separator (`archive/peer/2026-09-25-hyp-constsrc82.md:84-86`): is OpWire_v1's 1057 the source cast or the destination cast?
   - Then build the smaller op: either the fixed cast, or `Constant.Terminal` (634AC04) + `Terminal.Connect Wire` (6349C03), with the source taken by uid through report_all(class).
   - Gate: the new wire's only source is owned by the constant uid, and `Is Broken?` is False. Self-test it with a negative case.
   - Route it in `tools/stagexec.py` (md5 `3e2b1527??, self-test 34/0), in both the real Addr and SimReader.
2. Then run dry ??pre-run on all 42 ops (no offline stop) ??run 1. The recipe is `tools/recipes/stage_d1_l2a1.py` md5 `e589dc74??. The stageplan is `tools/bench/sim/l2a1/stageplan_l2a1.json` md5 `329d89ee??. The pass criteria are 187(c)'s. Save `D1_l2_a1_<ts>.vi`.
3. Use `bgrun --max-min 60`: `Stage.close` takes about 20 min after the work (188(e)).
?윞 **CYCLE 82 = no L2-A1 artefact, and no real stage run. The tools the run needs were built and measured on scratch copies; D1_k is unchanged.**
- **Reader parity at PRIME** (187(a)) is built and accepted. It turned up 231 SimReader-only entries before the fit and 0 after, and the 173-diagram holdout is also 0. Run 3's stop is now caught offline.
- **Nested ControlTerminal source** (187(b)) is routed through `gscript.wire_control`. Both rows were measured correct on a scratch at op 31. The dry run now has ops 1??4 at diff 0.
- **Op 35 (bare constant source) is BLOCKED.** OpWire_v1 gives 1057 and wire_control gives 5001 (`tools/bench/constsrc_l2a1_82.log:511-533`). The new op is decided in 188(c).
- **Outcome review ran** (`archive/peer/2026-09-25-outcome-review-20260925.md`): tooling-over-delivery, ordering-stale, goal-requirement-not-advanced, decision-starved. It wrote `steer_82.json`.
- `docs/violation-decisions.md` 14:28 records two decisions:
  - `repeated-failure-class`: the parity device, BUILT.
  - `device-failed`: `audit_cycle` C7 should read the plan named in next.json, not the first `current` plan. This repair is owed after the deliverable.
- Owed tools, not ahead of the deliverable:
  - When L2-A1 resumes, FIRST make the stagexec dry run report EVERY unroutable row, not just the first (`docs/violation-decisions.md` 16:10).
  - Per-phase stamps in `stagekit.close`, to find where the ~20 min goes.
  - The `audit_cycle` C7 repair above.
  - `guard_card` accepts any `cd <dir> &&` before `stagexec.py selftest` (review `archive/peer/2026-09-25-hyp-selftest-elreuse-81.md`).
  - `selftest_launch_gate.py` fails 20/8 (C2-C6, M4-M6).
  - `selftest_cycle_runner.py` needs `--dry-run`.
  - Option (c) of Pre-decided 184 (offline addressing of ends the stage itself wires).
- Fact: there is NO read-only `Wire.Is Broken?` op. The reader exists only inside connect ops (`docs/NAMES.md:1081-1089`), so CLAUDE.md's "BUILT" means only that.
?뵷 **CYCLES 68??0 DONE records, old FIRST ACT paragraphs and carries RELOCATED VERBATIM ??`archive/2026-09-25-status-cycle81-relocate.md` 짠2** (card 81-1). Still-live items there, one line each:
- ?윞 FOR THE USER: `.claude/settings.json` guard_session matcher `Agent|Task` ??`Agent|Task|SendMessage` (only you can apply it); `git commit` at cycle close needs your approval-list entry (짠2).
- ?뵶 Rule: desk-check PREDICTED VALUES, not only gates ??Pre-decided 132 (짠2).
- ?윞 Carries not ahead of the deliverable: cp949 print helper in stagekit, audit A1 vs `jev_gate.log`, bgrun END guarantee under a tree kill (짠2).
- ?좑툘 Per-session cap 180 min: write `## NEXT` by minute 150; every new stage/diagnostic ??20 lines on stagekit (짠2).
- Still the user's to overturn: N1 on the pre-bead-loss window, bead-4 FLIP mask, harness records 60 controls and sets none, `background VIs_COPY` untouched (짠2).

## Where to look ??**`docs/handover-2026-09-22.md` (???몄뀡? ?닿쾬遺??** 쨌 `CLAUDE.md` 쨌 `docs/secrets-and-handover.md` (API keys, ?ъ슜??援먯껜 泥댄겕由ъ뒪?? 쨌 `docs/jev-integration-plan.md` (Jev ?쎌엯 ?먮━, 2026-09-22) 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 **`docs/toolkit-capabilities.md`** 쨌 **`docs/motor-call-site-census.md`** (P1) 쨌 **`docs/d1-route-b-plan.md`** = the build order 쨌 `tools/recipes/build_d1_routeb_v0.py`.

## RUNNER STOPPED history (2026-09-22 09:58, 2026-09-24 07:29, 2026-09-25 01:02, 2026-09-25 10:30) ??`archive/2026-09-25-status-cycle81-relocate.md` 짠3

## RUNNER STOPPED 2026-09-27 08:25:46 ??next.json (cycle 107) sets stop_requested: PD220(g), only after the user fixes the rotor port (D-2026-09-27-03): VISA open check of ASRL5 (diag_c105d_visa.py, no LabVIEW) == 0, then ONE ABBA pe


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"priorart-priorart-c110f-replay-swap","verdict":"<one of: novel | settled-already>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

The work is novel. No replay copy of the display-loop VI has been built before, and nothing I found refutes or contradicts this plan. It reuses an existing recipe that worked last time; it does not rebuild one.

**Part A — the direction**
- **A1 (already settled):** No. The replay of the display-loop VI is ordered by `docs/d1-loop12-17-split-plan.md` Pre-decided 210(c)/217(f), and STATUS `## NEXT` makes it depend on the ABBA showing a GAIN. That is the order for this work, not an earlier answer to it.
- **A2 (already refuted):** No. The same two swaps (#6810 and #22692 replaced by the replay stand-ins) worked on S3 in cycle 78: 29 gates passed, 0 failed, the file was saved, and the log ends `BGRUN END rc=0` (`tools/bench/stage_replay_swap_78.log:50,83-84`). The only other attempt, card 95-6 for par1359, was BLOCKED by its own write flag before any run (`tools/bench/cards/result_95-6.json:1,29`). Nothing killed the approach.
- **A3 (contradicted):** None found. The three pinned replay-VI md5s (842ecad9, afce0d04, a89dafc1) and the reused S1 replay copy (126f8497) match the before and after pins in `stage_replay_swap_78.log:10-12,50,71-73`.
- **A4 (unread evidence):** None. The plan already cites the cycle-78 log, both earlier plans (`plan_replay_swap_78.json`, `_95.json`) and the R0 graph read (`diag_c110f_dispgraph.log`).

**Part B — the artifact**
- **B1 (already built):** The recipe `tools/recipes/stage_replay_swap.py:22-23` exists and is reused on purpose, with plan key `"110"` added. No `D1_s1_disp_replay_*` file appears anywhere in the logs, cards or plans, so the output file is new.
- **B2 (already failed):** No failure of this exact build is on record.
- **B3 (helper exists):** The plan is not hand-rolling anything. It calls the existing recipe and the swap/census path that the cycle-78 run proved.
- **B4 (already measured):** No. Nothing has been replayed or measured on the display-loop VI, which has never been run.

One note, not a finding: 110's plan skips a second replay copy of S1 and pins the one saved in cycle 78, which is the same choice plan 95 made (`plan_replay_swap_95.json:11`). The pinned md5 matches `stage_replay_swap_78.log:50`.

PRIOR-ART: novel

VERDICT {"schema":"verdict/1","id":"priorart-priorart-c110f-replay-swap","verdict":"novel","alternative":"Same two-swap recipe already proven on S3 (cycle 78, 29/0); only the input (disp VI) is new, and no disp replay copy exists on record.","discriminating_test":"grep tools/bench and claudeDev\\replay for D1_s1_disp_replay_* — none found; stage_replay_swap_78.log:83-84 PASS rc=0 confirms the path works.","violations":[],"sources":["tools/bench/stage_replay_swap_78.log:10-12","tools/bench/stage_replay_swap_78.log:50","tools/bench/stage_replay_swap_78.log:83-84","tools/bench/cards/result_95-6.json:1","tools/recipes/stage_replay_swap.py:22-23","tools/bench/plans/plan_replay_swap_95.json:11"],"note":"Recipe reuse is intentional; par1359 attempt (95-6) was blocked by write flags, not a build failure."}

## Sources

(extract from answer)

## What was done with it

Card 110-6 (material, 2026-09-27 18:3x): verdict `novel` taken as the release for the recipe edit (PLANS key "110"). Dry PASS on
the default plan-78 path and on `--plan 110` (`tools/bench/stage_replay_swap_110_dry78b.log`, `tools/bench/stage_replay_swap_110_dryb.log`).
The pre-run then FAILED twice on gate X9, which reads every decisions-row `copy` action as `stagekit.copy_in`
(`tools/stage_prerun.py:1194-1196`); in this recipe R01 is a file byte copy. Plan 110's R01 was relabelled `file_copy`;
plans 78/95 (out of the card's write scope) still carry `copy` and fail X9 (`tools/bench/stage_replay_swap_110_prerunb.log:35`).
Nothing was launched; the question goes back to judgement.
