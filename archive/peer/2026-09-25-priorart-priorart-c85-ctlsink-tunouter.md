# priorart-priorart-c85-ctlsink-tunouter

- **agent:** claude
- **role:** priorart
- **model:** claude-opus-5-5 (effort medium; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $1.0351  in 12 / out 7820 / cache-create 96049 / cache-read 551510  (81s, 15 turn(s))
- **date:** 2026-09-25 21:25:15
- **outcome:** ANSWERED (85s)
- **verdict-card:** VERDICT-CARD priorart-priorart-c85-ctlsink-tunouter verdict=settled-already -> tools\bench\cards\verdict_priorart-priorart-c85-ctlsink-tunouter.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id priorart-priorart-c85-ctlsink-tunouter, role priorart) ---
CLAIM: The work under review (new-op) is novel - not already built, measured, refuted or covered by an existing helper in this project's files.
ATTACHMENT: tools\recipes\build_opctlsinkwire_v1.py (md5 52d248168923914156442c33a91b36bf)
ATTACHMENT: tools\recipes\build_optunouter_v1.py (md5 7c74e5eb3d8911b144e4e2555b442d98)
--- END REVIEW CARD ---

PRIOR-ART REVIEW (trigger: new-op).

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
---
type: plan
status: draft
date: 2026-09-25
---
# Card 85-2 plan: two routes for the last two unroutable L2-A1 rows (Pre-decided 191, docs/d1-loop12-17-split-plan.md:893-915)

Context: L2-A1 staged move on bed `claudeDev\D1_k_20260925_100155.vi`. The stagexec dry run (tools/bench/dry_l2a1_85b.log:47-48)
lists two unroutable rows after op 36:
- R41 `rw_10988_17272`: bare `min value` output #10988 of Function #10969 -> front-panel ControlTerminal #17272 (sink).
  `wire_indicators` needs a WIRED source (measured limit, tools/gscript.py:1835-1838), so it cannot be used.
- R45 `rw_6007_5082` (+ R46 `rw_6026_5164`): bare OUTER faces of SelectorTunnels #5680 / #6016 (on CaseStructure #5540)
  -> SubVI #5058 inputs `Bead is good? array in` #5082 / `x,y,z array` #5164. Addressing through #5540's Terminals[] is
  ambiguous (two bare '' sources).

Builds (both copy `claudeDev\ops\OpConstWire_v1.vi`, md5 c978863c, built and measured in card 85-1):
1. `tools/recipes/build_opctlsinkwire_v1.py` -> `ops\OpCtlSinkWire_v1.vi`: delete the Constant.Terminal PN; wire the
   Node.Terminals[] IA element into Connect Wire's `Wire Source`; re-type the source TMSC #683 with a Terminal-typed seed
   (create_control on Invoke.reference) and wire it into Connect Wire's `reference`. Call: ladder 1 = Traverse('ControlTerminal')[i]
   (the sink), ladder 2 = Traverse(<source node class>)[j].Terminals[t] (the source).
2. `tools/recipes/build_optunouter_v1.py` -> `ops\OpTunOuterWire_v1.vi`: replace the Constant.Terminal PN by a
   `VI Server:Tunnel` PN reading `Outside Terminal` 6356001, re-type TMSC #683 with a Tunnel-typed seed. Call: ladder 1 =
   Traverse('SelectorTunnel')[i] (the tunnel), ladder 2 = the sink node's Terminals[t] (unchanged from OpConstWire_v1).
Each build negative-tests 20 calls on a D1_k scratch (wrong class -> 1057, no wire, handles flat).
Routing (tools/stagexec.py, both backends): `ctlsink` for a bare node-terminal source into a ControlTerminal sink;
`tunouter` for a bare owner-routed tunnel outer face. Gate on a scratch run of the plan: sole source owner = planned uid,
sole sink = plan sink, ordered second pass Is Broken? False. Rule 1a: same edges as S1.
Rejected (PD191): re-cutting {#10969,#17272} into one joint move; carrying the owner's Terminals[] order across the move.


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-20
tags: [hand-off]
---
<!-- STOP line removed 2026-09-25 21:xx: verification chat-L1/L2 green (124/0; selftests 48+2 skip, hooks 46/46, lint L2+L6 PASS, ingest 0 after CLAUDE.md:119/:401 fixes); user: "lint ?댁슜 寃利앺븳 ?댄썑 ?щ꼫 ?ш컻". -->

# STATUS ??read this first. One screen. Detail is one layer down, never appended here. ?좑툘 **ONE SESSION AT A TIME** ??re-read `CLAUDE.md` + this. Narrative ??**`archive/2026-09-19-status-cycle47-relocate.md` (latest ??T2's block diff and what it closes, the readable-ORIGINAL correction, the five killed retrospectives)** + `archive/2026-09-19-status-cycle39-judgement.md` + `archive/2026-09-18-status-cycle34-n1.md` + `??cycle23-close.md` + the `archive/2026-09-1[678]-status-*.md` set.
??**DELIVERED:** ?윟?윟 **D1 S3 loop 1.5 = `claudeDev\D1_s3_loop15.vi` md5 `1a11d92aacabf7ec844d65b8af19f39f`** (482,312 B; byte copy of `D1_s3b_m4b_20260924_004214.vi`, kept; `tools/bench/promote_d1_s3_loop15.log` 5/0; ExecState 1 warm+cold, `computation_diff(S1,쨌)` 0 rows; STRUCTURAL + graph-equivalent under ASSUMPTION A, NEVER RUN; `docs/connectivity-map-plan.md` Pre-decided 147) 쨌 D0 (cycle 31) 쨌 N1 ACCEPTED (cycle 34) 쨌 D1 **S1** `claudeDev\D1_s1_copy.vi` md5 `3e3d23ce?? 쨌 D1 **S2** `claudeDev\D1_s2_loops.vi` md5 `6ff19497?? 쨌 D1 **S3a** both halves (`??boolcarrier_b3_20260921_010034.vi` md5 `dc14dd00??, `ExecState` 1, `Is Broken?` False) 쨌 D1 **S3b rows 1 and 2**. ?뵷 **THE CURRENT BED IS `claudeDev\D1_k_20260925_100155.vi`, md5 `6cf5b077?? (stage K, cycle 79, 2026-09-25; ExecState 0 by design) ??every next stage starts FROM THAT FILE; `D1_s4_loop17.vi` md5 `4b621946?? (L7-R) is its input, kept; every other "bed" named below in this line is HISTORY (`D1_s3_loop15.vi` md5 `1a11d92a?? is kept as the S3 deliverable).** ??**M3a-1 DELIVERED (cycle-63 firefighter, run 5, 2026-09-22 01:0x): `claudeDev\D1_s3b_m3a_BROKEN_20260922_005732.vi` md5 `6b3c1f3c??, 22 gates pass / 0 fail, bytes DIFFER from the bed.** ??**M3a-2 DELIVERED AND INDEPENDENTLY VERIFIED (cycle 64, 2026-09-22 02:3x??2:5x): `claudeDev\D1_s3b_m3a2_20260922_023029.vi` md5 `3842f5e6f128226235dc78353f26ef44`, 303,823 B, 25 gates pass / 0 fail on the build and 15/0 on a separate read-only check anchored at the REGISTER UID. ?뵷 EVERY NEXT STAGE STARTS FROM THAT FILE.** ?뵶 **M3a-3b (ROW D) IS **NOT** DELIVERED ??NO FILE. ?좑툘 CORRECTED 2026-09-22 15:4x (prior-art `archive/peer/2026-09-22-priorart-c87-rowd-stagekit.md` A3): the standing reason given here ??*"its W1 gate measures that NO writer on disk can address a `FlatSequenceInnerTunnel` terminal sink (`tools/bench/c78_rowd_writer.log`)"* ??HAS BEEN FALSE SINCE CYCLE 82. `OpFsInnerTunnelConnect_v1.vi`'s `Wire Source` half IS the FSIT `LeftTerm` property node (`tools/bench/build_d1_m3a3b_d3.log:28`, `term_uid=7488`/`uid_back=7468` on 20/20 calls at `:58-60`), and `tools/bench/diag_c86_norbw.log:87`/`:97` records it WRITING wire 25324 onto `#7488`. THE REAL REASON ROW D HAS NO FILE IS THAT NO RUN HAS YET SAVED ONE. ?윟 **CYCLE-86's MEASUREMENT OUTCOME, never recorded until now: `tools/bench/diag_c86_norbw.log` (14:46) answered plan entry 111a YES on a byte-identical scratch of the bed with Remove Bad Wires rebound to a raising guard ??after `del_wire(7506)` `#7468` STILL RESOLVES (`uid_back=7468`, `:74`), `#7488` comes back BARE (`wire_a=0`, `:76`), the inner wire 7448 survives (`:77`), the connect then writes wire 25324 onto BOTH ends (`wire_delta 1`, `:87`/`:97`) and the net ends with ONE source owner `RightShiftRegister #23868`, `#4334` off, PD85 0, `Is Broken?` False (`:105-110`). It SAVED NOTHING and deleted its scratch (`:113`), and the log has NO `BGRUN END` (truncated mid-cell-B), so D5/D6/D7 were never reached.** THE BED IS STILL `claudeDev\D1_s3b_m3a3_20260922_081056.vi` md5 `33ef524e??, 306,951 B.** Both initial-value rows land the predicted source (`FlatSequenceInnerTunnel #4194` ??LEFT `#23880`; `#3974` ??LEFT `#23909`), the originals stay on their nets, `Wire.Is Broken?` False in a separate ordered pass, PD85 violations 0 on every walk. Still BROKEN BY DESIGN and NEVER RUN (34(f)); `ExecState` 0's cause is formally OPEN and is neither gated on nor reasoned from. The artefact is BROKEN BY DESIGN (uninitialised SRs ??initial values are stage M3a-2) and is NEVER RUN (34(f)). Two root causes were repaired and MEASURED on the way: the identity reader `wire_source_owner` (history-echo, now error-checked + uid-echo-verified, acceptance `diag_c68_echo_accept.log` 8/0) and `gscript._lv_gui` (unquoted spaced args = PowerShell parse error, so NO Evidence-carrying GUI action had EVER dispatched ??`archive/peer/2026-09-22-c72-guisave-foreground-r2.md`). The bed is byte-unchanged and all four md5 pins hold. S3-as-37(g)-defined is WITHDRAWN (cycle 53). **Read `docs/cycle27-plan.md` Pre-decided 84??0 BEFORE 78??3 (78/80/81/82 are WITHDRAWN)**, then 46, 42, 43, 44. Full chronicle VERBATIM ??`archive/2026-09-21-status-cycle67-locknotes.md` 짠2; banner VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠3; facts `??cycle31-d0-delivered.md` 짠1?벬? (read **짠4** before the first D1 click).
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
rig). PI `SPA 1 0x15/0x30` ??TMN 0 / TMX 39 (RAM, **never WPA**) 쨌 ASI `SL/SU` absolute mm X ??.8475??.1525, Y ??.7744?╈닋0.7744 (persistent, **never SS Z**),
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
?뵶?뵶?뵶 **FIRST ACT (cycle 84) = L2-A1 RESUMES, `docs/d1-loop12-17-split-plan.md` Pre-decided 189 (the load test chose loop 1.2)** ??steps 1?? below, in order; machine copy `tools/bench/next.json`; advances M3/R1/R3; follows `steer_82`.
??**CYCLE 83 (firefighter, fable/low) = the PD188(d) load measurement RAN ??INDEX row 48, `tools/bench/m8_load_83.json`, 8 real legs 8/0, LabVIEW closed after each.** Total Lost Frames S1 copy vs `D1_s3_loop15.vi`, 120 s at ~89 frames/s (~10,680 frames): **8 picks 16 vs 12** (repeat 12 vs 14) 쨌 **15 picks 3,331 vs 3,493** (repeat 3,161 vs 3,269). Frame loss goes from ~0.1 % to ~??between 8 and 15 beads on BOTH VIs ??**the per-bead tracking cost (loop 1.2, M3) is the lever; the loop-1.5 split is neutral at this load.**
- ?좑툘 **150 Hz was NOT reached**: the driver wrote 150 Hz to the camera between legs, but EVERY `IMAQdxOpenCamera` reloads the camera file (`??NI-IMAQdx\Data\JAI Corporation SP-5000M-USB (??.icd`, 90 Hz) ??measured `tools/bench/diag_camrate_persist83b.log` 4/0 after the failed-prediction review `archive/peer/2026-09-25-hyp-camrate83.md` (accepted; `camera-acquisition-facts.md:642` corrected). The "150 Hz" cells are 90 Hz repeats. Real 150 Hz needs a VI-side setting or an `.icd` change ??**user decision D-2026-09-25-05**.
- ?윞 The user has 4 open questions: D-2026-09-25-02 (`.cal` scope), -03 (autofocus limits, OPEN 58), -04 (a supervised S3 run with beads), **-05 (how to reach 150 Hz)**.
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


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"priorart-priorart-c85-ctlsink-tunouter","verdict":"<one of: novel | settled-already>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

The work is not novel as planned: `OpConnectCtl_v0` already exists and does R41's wiring step from the sink side. The tunnel-outer-face op (`tunouter`) is new as a writer. Details and citations follow.

## PART A: the direction

- **A1 (settled already): no.** Card 85-1's review recorded both routes as undecided (`archive/peer/2026-09-25-hyp-unroutable-85.md:126-134`). Pre-decided 191(a)/(b) (`docs/d1-loop12-17-split-plan.md:898-915`) is the first place they are decided, and this plan carries that decision out. There is nothing earlier to contradict it.
- **A2 (refuted already): no.** The two directions 191 rejects were each rejected with measured grounds:
  - the joint re-cut: `l2a1_tunflip_80*` has 0 hits (`d1-loop12-17-split-plan.md:902-903`);
  - carrying the owner's `Terminals[]` order across the move: the T2c2 failure on #5680 (`docs/NAMES.md:1132-1137`).

  The plan avoids both. `Outside Terminal` is marked "UNBUILT" (`tools/recipes/build_d1_m3a1.py:1552-1564`, `:1653`). That marks it as not yet built. It does not say anyone tried it and it failed.
- **A3 (contradicted): no.** The plan's facts match their sources:
  - the Wire Indicators wired-source limit: `tools/gscript.py:1835-1838`;
  - the `SelectorTunnel`→`Tunnel` cast, 24/24 on the #5540 tunnels: `docs/toolkit-capabilities.md:77`.

  One scope note: `Tunnel.Outside Terminal` 6356001 was refused (1077) on `FlatSequenceOuterTunnel` (`tools/bench/build_opfstunnelterm_v2_run1.log:38`; `archive/2026-09-18-status-cycle21-wire-semantics.md:113-114`). That refusal was on a different class. The #5680/#6016 tunnels are selector tunnels, where the cast is measured, so it does not bite here. The 20-call negative test should still include one FlatSequence tunnel, which is expected to return 1077.
- **A4 (unread evidence): yes.**
  - `tools/recipes/build_opconnectctl_v0.py:1-16` and `docs/toolkit-capabilities.md:25` describe `OpConnectCtl_v0`. It calls `Terminal.Connect Wire` 6349C03 on a front-panel object's own ControlTerminal, reached with no cast (`Panel.Controls[]` → IA → `Control.Terminal` 6332006). Its `Wire Source` is a `Node.Terminals[]` element. That is exactly R41's verb. Neither Pre-decided 191(a) nor card 85-2 mentions it.
  - `docs/cycle27-plan.md:108-110` records a related fact: a ControlTerminal has no node index, and `OpConnectNested_v1` can only address `Diagram[].Nodes[].Terminals[]`. So one of the two ladders has to be a panel ladder or a class `Traverse`.

## PART B: the artefacts

- **B1 (already built): partly, for ctlsink only.**
  - `OpConnectCtl_v0.vi` is on disk (`claudeDev\OpConnectCtl_v0.vi`), wrapped as `gscript.connect_ctl` (`tools/gscript.py:1024-1043`), and measured in `build_harness_dispI.log` run 4 (`toolkit-capabilities.md:25`). Its sink half is the same as ctlsink's.
  - The difference is the source ladder. `connect_ctl` takes its source from the top-level diagram's `Nodes[]`, by index. If #10969 sits inside a loop diagram after `mv_10969`, that half does not reach it. So what is really new in ctlsink is one thing: a nested source reached by class `Traverse`.
  - The plan's sink route (`Traverse('ControlTerminal')` → re-typed TMSC seed) adds a cast that the existing sink route does not need.
  - **tunouter:** no writer uses `Outside Terminal` as `Wire Source`. What exists only reads it:
    - `build_optunnelind.py:45` (for Create Indicator);
    - `build_opshiftregs_v0/v1`;
    - `build_oploopcast_v0.py:280`.
- **B2 (already failed): no.** Neither op build has been attempted before.
- **B3 (helper exists): yes, for ctlsink's sink ladder.** The existing route is `Panel.Controls[i]` → `Control.Terminal` from `OpConnectCtl_v0` / `OpConnectCtlInd_v0` (`gscript.py:1050-1072`). Two ways forward:
  1. Build ctlsink on `OpConnectCtl_v0`'s sink ladder plus `OpConstWire_v1`'s source ladder.
  2. Keep the plan, and state in writing why the `Traverse`+TMSC sink is preferred. One acceptable reason: panel-index addressing does not match stagexec's `Addr.ct` uid route (179(b)/187(b)).
- **B4 (already measured): no.** Nobody has measured a write through either route; the cheapest tests in `hyp-unroutable-85.md:101-112` were never run. Note that the `wire_ctlsink` and `wire_tunouter` wrappers at `tools/gscript.py:2064-2090` belong to this card and are uncommitted. They are not earlier work.

## Machine-readable lines

PRIOR-ART: helper-exists
PRIOR-ART: unread-evidence

**How to release this:** add a `FIXED:` or `REFUTED:` line that does one of two things. Either re-base ctlsink's sink half on the `OpConnectCtl_v0` `Panel.Controls[]`→`Control.Terminal` ladder, or show in writing why the uid route has to use `Traverse('ControlTerminal')`+TMSC. Also confirm #10969 is not on the top-level diagram after `mv_10969`; if it is, `connect_ctl` already wires R41 as it stands. tunouter is not blocked by anything I found.

VERDICT {"schema":"verdict/1","id":"priorart-priorart-c85-ctlsink-tunouter","verdict":"settled-already","alternative":"ctlsink's sink half already exists: OpConnectCtl_v0 (Panel.Controls[]->Control.Terminal, cast-free, Connect Wire on the ControlTerminal, Wire Source = Node.Terminals[] element). Only a nested class-Traverse source is new; tunouter is novel.","discriminating_test":"Read #10969's owning diagram after mv_10969 on a scratch: top-level => connect_ctl wires R41 as is; nested => build ctlsink from OpConnectCtl_v0's sink ladder + OpConstWire_v1's source ladder, or justify the Traverse+TMSC sink.","violations":[],"sources":["tools/recipes/build_opconnectctl_v0.py:1-16","docs/toolkit-capabilities.md:25","tools/gscript.py:1024-1043","docs/cycle27-plan.md:108-110","docs/d1-loop12-17-split-plan.md:898-915","tools/bench/build_opfstunnelterm_v2_run1.log:38"],"note":"helper-exists + unread-evidence apply to ctlsink only (the sink ladder); tunouter (Outside Terminal as Wire Source) has no prior writer and its cast is measured 24/24 (toolkit-capabilities.md:77)."}

## Sources

(extract from answer)

## What was done with it

Card 85-2 (material), 2026-09-25 ~21:4x. The discriminating test was answered offline from the plan's own step files, and the
sink-ladder choice is justified in writing (the reviewer's option 2); tunouter gets the FlatSequence negative the review asked for.
- #10969 is NOT on the top-level diagram after `mv_10969`: the plan moves it to Diagram #23166
  (`tools/bench/sim/l2a1/plan_l2a1.json`, action `mv_10969` `dest_diagram` 23166; `step_40_wire.json` row #10988
  `frame_diagram` 23166), so `connect_ctl`'s top-level `Nodes[]` source cannot reach it.
- The sink stays `Traverse('ControlTerminal')` + TMSC(Terminal): stagexec addresses every ControlTerminal end by its OWN uid
  through `report_all('ControlTerminal')` (`Addr.ct`, 179(b)/187(b), `tools/stagexec.py:540-563`), whose order IS
  `Traverse('ControlTerminal')`'s; `Panel.Controls[i]` indexes panel CONTROLS (another class, another order) and would need a
  second, unmeasured uid -> panel-index mapping in both backends.
- tunouter: `build_optunouter_v1.py` N4 adds one call with a `FlatSequenceOuterTunnel` source, expected to return an error and
  no wire (the 1077 scope note, A3).

REFUTED: helper-exists - tools/gscript.py:1024 says connect_ctl (OpConnectCtl_v0) wires a panel terminal from a TOP-LEVEL Nodes[] source by panel index, which does not cover R41 because #10969 sits on nested Diagram #23166 after mv_10969 (plan_l2a1.json mv_10969 dest_diagram 23166) and stagexec addresses ControlTerminals by uid through report_all('ControlTerminal') (tools/stagexec.py:540), not by Panel.Controls[] index
REFUTED: unread-evidence - docs/toolkit-capabilities.md:25 says OpConnectCtl_v0 reaches the sink by Panel.Controls[] -> Control.Terminal with a top-level Nodes[] source, which does not cover a nested class-Traverse source nor a tunnel Outside Terminal source (tunouter), because neither ladder exists in that op; both builds were re-read against it and kept
