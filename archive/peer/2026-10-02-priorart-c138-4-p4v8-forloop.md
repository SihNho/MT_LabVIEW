# priorart-c138-4-p4v8-forloop

- **agent:** claude
- **role:** priorart
- **model:** claude-opus-5-5 (effort medium; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $2.3004  in 56 / out 14982 / cache-create 150023 / cache-read 4001881  (243s, 47 turn(s))
- **date:** 2026-10-02 17:55:22
- **outcome:** ANSWERED (247s)
- **verdict-card:** VERDICT-CARD priorart-c138-4-p4v8-forloop verdict=settled-already -> tools\bench\cards\verdict_priorart-c138-4-p4v8-forloop.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id priorart-c138-4-p4v8-forloop, role priorart) ---
CLAIM: The work under review (new-op) is novel - not already built, measured, refuted or covered by an existing helper in this project's files.
ATTACHMENT: docs\user-rules.md (md5 9e0396da1b6fd9227a6e0ca850337cd5)
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

PART C - THE USER'S RULES (card chat-P2, user 2026-09-28; docs/user-rules.md is attached in full below)
 C1 Does this plan contradict any rule in user-rules.md? Name the rule and the plan line. Quote both. A plan that
    puts a queue on a control signal or at the acquisition boundary, lets the camera loop wait, puts serial on the
    frame path, or changes a per-bead number is the kind of contradiction this question exists for. If the plan
    relies on a rule correctly, say nothing about it.

End with machine-readable lines, one per finding:
  PRIOR-ART: settled-already | refuted-already | contradicted | unread-evidence
  PRIOR-ART: already-built | already-failed | helper-exists | already-measured
  PRIOR-ART: user-rule-contradicted
  PRIOR-ART: novel
`novel` only if none apply. Do not invent slugs.

THESE VERDICTS STOP THE WORK. Any slug other than `novel` blocks the next build until someone opens your citation
and refutes it in writing. So be precise about what your citation actually covers: an over-broad match costs real
work, and a missed one costs a whole build cycle.

=== WHAT IS UNDER REVIEW ===
# Prior-art question, card 138-4: For loop with auto-index tunnels inside a plan-made While body (P4 reader, PD311(b))

Plan file: tools/bench/plan_ring_p4_v8.json md5 059b5296 (v7 01ab0893 + this re-cut, actions 26/29/53-62 new;
maker tools/bench/prep_c138_4_mkv8.py, log tools/bench/prep_c138_4_mkv8.log).
Deviation from PD311(b)'s wording: Greater? stays OUTSIDE the For on the arrays (v7 p4_gt_last unchanged) and its Boolean
array is auto-indexed in, because compile_plan's tunnel group (stagexec.py:685-694) cannot chain `last` through two tunnels.
Decision cited: docs/d1/ring-p4.md:226-244 (PD311 (a) Select takes a scalar s only; (b) the redesign; (d) name 's? t:f').

New structure class on this build path (the P4 ring reader, loop 1.2 body #23166, plan-made While W1):
1. `create ForLoop` FMN1 on W1's body (a plan-made While body), count terminal N UNWIRED (count from auto-indexed inputs).
2. Three EXPLICIT plan `tunnel` actions with `indexing: true` on that plan-made For:
   - IN  TFN1: the local read 'Num' (I32[20], already wired to Greater?.x) -> Num[i] -> Select.t
   - IN  TFB1: Greater?(Num array, last) Boolean[20] -> b[i] -> Select.s (scalar)
   - OUT TFS1: Select 's? t:f' -> I32[20] -> Array Max & Min.array (on W1's body)
3. Two `const_donor` DigitalNumericConstants I32 2147483647 (KMX1 on the For body -> Select.f; KMX2 on W1's body -> Less?.y).
   No claudeDev donor VI holding I32 2147483647 exists today (DonorSRInit_v0 #134 U32 max, #248 I32 0; DonorRingConst_v0 #249 I32 -1).

What I want to know (has this been done / measured / refuted here already?):
- Has a plan `tunnel` action with `indexing: true` on a plan-made ForLoop ever run through stagexec, and what IndexMode did
  the real tunnel get? (stagexec applies `index_mode_fix` only inside `if lost:` at stagexec.py:2104-2109.)
- Has a For loop with an UNWIRED N and only auto-indexed inputs been built by our scripting anywhere (plan_disp DLF1?), and
  did it compile (ExecState) or break?
- Has Select with a scalar Boolean s fed by an auto-indexed Boolean array tunnel been built before?
- Is there an existing donor VI / op that makes an I32 constant of a chosen value (not DBL), so a new donor VI is not needed?
- Was Greater? on (I32 array, I32 scalar) followed by an auto-indexed For already used in the original VI or a prior stage
  (a precedent this re-cut could copy instead)?


=== docs/user-rules.md IN FULL (the user's standing design rules; PART C asks about these) ===
---
type: reference
status: current
date: 2026-09-28
tags: [user-rules, design-check, prior-art, card-chat-P2]
---
# The user's standing DESIGN rules ??every new design is checked against this list before it is built

Card chat-P2 item 1 (user 2026-09-28 17:xx, "洹몃젃寃?1~4踰??곸슜?섏뿬 ?섏젙?섎㈃ ?섍쿋??). The largest single loss in cycles
84??20 was not a bad build but a design direction (the image pool with `Q_free`/`Q_work` queues, PD233??37) that
contradicted rules the user had already given; nobody compared the plan with them before building. This file is that
comparison's input. Every row is the user's own words, dated, with where it was recorded.

How it is used (mechanical):
- `tools/prior_art_review.py` attaches this file to EVERY prior-art dispatch and asks one fixed question: *does this
  plan contradict any rule in user-rules.md? Name the rule and the plan line.* A contradiction is the verdict
  `PRIOR-ART: user-rule-contradicted` ??a non-`novel` verdict, released only by the usual `REFUTED:` / `FIXED:` lines.
- A judgement session that writes a new Pre-decided DESIGN item reads this file first and puts a `USER-RULES:` line in
  the item (the rule ids it relies on, or `USER-RULES: none apply`); `tools/doc_lint.py` L9 warns when a Pre-decided
  item numbered 238 or later lacks one.
- A row is added only from a user statement (quote + date + source). A row is never re-worded; a later user statement
  that changes a rule is a NEW row that names the row it supersedes.

| id | rule (one line) | the user's words (verbatim) | date | source |
|---|---|---|---|---|
| U1 | The original's computation (per-bead maths, its parameters, its numbers) never changes; only scheduling may. | "?먮낯???곗궛諛⑸쾿 ?먯껜瑜?諛붽씀硫??덈뤌. ?닿굔 瑗?紐낆떖?섍퀬." 쨌 "?대?吏瑜?遺꾩꽍?댁꽌 ?섏튂?뷀븯??紐⑤뜽怨?洹??곗궛 諛⑸쾿 諛?寃곌낵媛 諛붾뚮㈃ ?덈맂?ㅻ뒗 留먯씠吏." | 2026-08-30 | CLAUDE.md:25-37 (rule 1a); memory preserve_the_original_computation.md |
| U2 | Hardware access follows the rig state (disassembled / assembled / experiment running); the ASI is a motor like any other. | "紐⑦꽣 ?묎렐 諛?移대찓???묎렐??'由ш렇 遺꾪빐 / 由ш렇 議곕┰ / ?ㅽ뿕以? ?곹깭???곕씪 ?ㅻⅤ寃??먮뒗寃?留욌뒗?? ???대뒗 Piezo stage??ASI 而⑦듃濡ㅻ윭瑜??ы븿?섎뒗 ?댁슜 (ASI? ?ㅻⅨ 紐⑦꽣瑜?援щ텇?섏뿬 沅뚰븳 ?먯? 留먭쾬)." | 2026-09-16 | CLAUDE.md:39-44 (rule 1b) |
| U3 | No VISA/serial call anywhere on the frame acquisition path; serial lives in its own loop with a non-blocking handoff. | "I don't want to have even a single frame loss coming from the motor communication if possible. And it is so clear that serial communication through VISA can somehow stall the loop, and cause unwanted frame stop." | 2026-09-16 | CLAUDE.md:89-100 (rule 1c); memory no_serial_on_the_frame_path.md |
| U4 | Loop-to-loop CONTROL signals go by local variable (latest value), never by queue; queues only for lossless data streams. | "?먮? ?ｌ뼱踰꾨┛?ㅻ㈃ ??猷⑦봽 ?ъ씠???곴?愿怨꾧? ?앷꺼踰꾨┛?ㅻ뒗 寃?媛숈??? 洹몃윴 由ъ뒪?щ? 媛먮떦???꾩슂媛 ?덈뒗吏 紐⑤Ⅴ寃좎쓬. 洹몃깷 Boolean 媛?諛??寃?媛믪쓣 local variable濡??꾨떖?섎뒗寃???醫뗭? ?딆쓣吏?" | 2026-09-25 | CLAUDE.md:102-124 (rule 1c''); memory locals_not_queues_focus_loop_own_clock.md |
| U5 | The ASI autofocus loop runs on its own clock, not in step with frame acquisition. | "ASI autofocus 猷⑦봽???좎큹??frame acquisition 猷⑦봽? ?숈떆?????꾩슂媛 ?놁쓣??" | 2026-09-25 | CLAUDE.md:102-124 (rule 1c''); memory locals_not_queues_focus_loop_own_clock.md |
| U6 | The camera free-runs; nothing we build may throttle, block or pace acquisition (the PC is a reader, never a gate). | "移대찓?쇰뒗 湲곕낯?곸쑝濡??먯떊??猷⑦봽瑜?而댄벂?곗? ?낅┰?곸쑝濡??뚯븘???섎ŉ 洹몃젃寃??뚭퀬 ?덉쓬. 而댄벂?곕? ?듯븳 移대찓???꾨젅??而⑦듃濡ㅼ쓣 ?좊ː?????녾린 ?뚮Ц?? ?곕씪??Lossy Enqueue Element ?뱀? 湲고? ?ㅻⅨ ?대뼚??諛⑸쾿??移대찓??frame acquisition???곹뼢??二쇱뼱?쒕뒗 ?덈맖." | 2026-09-15 | docs/decisions.md:21; memory camera_free_runs_never_gate_it.md |
| U7 | The buffer number is the time axis (frame N happened at N/framerate); never a software timestamp. | "?쒓컙 媛꾧꺽? 而댄벂??猷⑦봽???蹂꾧컻濡??꾨젅?꾩씠 媛숇떎硫??숈씪?? 移대찓??猷⑦봽??acquisition ?뺣낫??frame rate??蹂꾨룄???섎뱶?⑥뼱濡??듭젣?섍린 ?뚮Ц. 洹몃윭???곗씠???꾨떖?먯꽌 ?앷린???쒓컙 遺덇퇏?쇱? ?ш쾶 以묒슂?섏? ?딆쓬." | 2026-09-15 | docs/decisions.md:24; memory camera_free_runs_never_gate_it.md |
| U8 | Overload, acquisition ??tracking: discard the backlog and take the newest frame (latest-wins). | "?먮? 踰꾨━怨??덈줈 ?ㅼ뼱?ㅻ뒗 ?꾨젅?꾩쓣 ?쎈뒗 寃껋씠 媛??諛붾엺吏곹븿. ?대뒗 ?쒓퀎???곗씠?곗쓽 ?꾨??깆쓣 ?꾪븿." | 2026-09-15 | docs/decisions.md:25; memory prefer_the_freshest_frame_over_a_complete_backlog.md |
| U9 | No corruption: image memory and its buffer number change together and the consumer verifies them; a gap is fine, a mismatched pair is corruption. | "留뚯빟 buffer number 媛깆떊???대젮???곹솴?몃뜲 IMAQ 硫붾え由щ쭔 諛붾뚯뿀???쇨퀬 ?쒕떎硫??뺣쭚 ?곗씠??而ㅻ읇?섏쑝濡?遊먯빞?좊벏." | 2026-09-15 | docs/decisions.md:27; memory prefer_the_freshest_frame_over_a_complete_backlog.md |
| U10 | Authorised fallback: acquisition and tracking may stay in ONE sequential loop if the handoff cannot be made provably safe. | "2踰덉씠 臾몄젣媛 ?쒕떎硫?Acquisition 諛?異붿쟻? ?숈씪 猷⑦봽???먭퀬 ?쒗??泥섎━瑜??섎뒗 寃껊룄 愿쒖갖??寃?媛숈쓬." | 2026-09-15 | docs/decisions.md:31; memory prefer_the_freshest_frame_over_a_complete_backlog.md |
| U11 | Frame rules have a PRIORITY ORDER: (1) no corruption, (2) latest-wins, (3) the sequential fallback. Search these rows before asking the user a frame question. | "?꾩뿉 ?꾨젅??愿?⑦빐?쒕뒗 ?닿? 留먰븳 ?댁슜???덉쓬. ?ㅼ떆 李얠븘遊? ?곗꽑?쒖쐞媛 ?덈뒗?? | 2026-09-28 | memory prefer_the_freshest_frame_over_a_complete_backlog.md |
| U12 | Pure-display indicators (plots) are drawn by a SEPARATE display loop on its own clock, fed by local variables; never an every-N-frames gate inside the frame loop. | "洹몃옒???뚮’ 湲곕뒫???뱀떆 蹂꾨룄 猷⑦봽濡??먮뒗 寃껋? ?대뼡吏? 濡쒖뺄 蹂?섏뿉 ?곗씠?곕뱾? ???낅젰?섍퀬 ?곗씠???뚮’? 蹂꾨룄 猷⑦봽濡? ??"?대?濡?吏꾪뻾" | 2026-09-26 | memory display_in_separate_loop_fed_by_locals.md; docs/d1-loop12-17-split-plan.md Pre-decided 210 |
| U13 | Frame handoff 1.1 ??1.2 is a RING BUFFER of 20 IMAQ slots (slot = camera loop counter mod 20), seqlock per slot, no `Q_free`/`Q_work` queues; on overwrite jump to the newest slot; slot numbers come from the camera loop. Supersedes the pool-queue design (PD233??37) and cancels the "option C" rollback. | "1踰?吏?곸? ?뚮???遺遺?/ 2踰????뱀젙 ?꾨젅?꾩? ?볦퀜踰꾨┫ ?섎룄 ?덉쑝?덇퉴 / 3踰???踰꾪띁濡?20 ?꾨젅?꾩씠 ?덉뼱??臾몄젣媛 ?앷릿?ㅻ㈃ 理쒖떊 移몄쑝濡??吏곸씠?붽쾶 留욎쓬 / 4踰???移?踰덊샇??移대찓??猷⑦봽瑜????섎컰???놁? ?딅굹?" | 2026-09-28 16:3x | docs/ring-buffer-design.md:10-38 |

## Reading the rows together (what a reviewer checks first)

- A **queue** between two of our loops is allowed only for a lossless DATA stream (tracking ??file writer). A queue that
  carries a control signal (U4) or sits at the acquisition boundary (U6, U13) contradicts the rules.
- Anything whose failure mode is "the camera loop waits" contradicts U6; anything that can put serial on the frame path
  contradicts U3; anything that changes a per-bead number contradicts U1.
- A frame-handling design must say how it meets U9 (pair verified), then U8 (latest-wins), then U13 (ring + seqlock) ??
  in that order (U11).


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-20
tags: [hand-off]
---
??RELAUNCHED 2026-10-02 ~03:2x by the chat after card chat-D1 PASS 5/0 (commit 689c565e): the plan of record is now `docs/d1/INDEX.md`; new decisions go to `docs/d1/<topic>.md` from PD268; cycle 130 is the test of the new layout.
(history) STOP (lifted 03:2x) ??CHAT 2026-10-02 ~02:1x for the user's approved doc reorganisation ("臾몄꽌 ?뺣━???꾩껜 ???대젃寃??섍퀬 ?쒕쾲 ?뚯뒪?명빐蹂댁옄"): graceful ??cycle 129 finishes, the runner exits, the chat runs card chat-D1 (freeze long docs in place + short index + per-topic decision files + doc_lint line cap), then removes this line and relaunches; cycle 130 is the test. Not a rig/experiment stop.
??STARTED ??USER 2026-10-01 (chat): "?꾩옱??由ш렇 ?ъ슜?섏? ?딆쓬. 洹몃?濡?肄붾뵫 ?몄씠???뚮━?꾨줉" (rig 議곕┰; the user's LabVIEW was closed by the user first; runner relaunched by the chat via runner_supervisor; first act = ## NEXT). The user may announce ?ㅽ뿕以?tonight ??then write a STOP line here (graceful).
(history) The superseded top banner lines (STOP/START/REDIRECT markers 2026-09-26 .. 2026-09-28, all lifted or superseded) RELOCATED VERBATIM (rule 4, card 123-6) ??`archive/2026-10-01-status-cycle123-relocate.md` 짠1
?뱦 **NEW CHAT? Read `docs/chat-handoff.md` right after this file** (2026-09-28 19:4x): the chat's duties (30-min usage ??`run_mode.py write`, report_gate acks, the tick), today's decisions, and the OPEN proposals awaiting the user.

# STATUS ??read this first. One screen. Detail is one layer down, never appended here. ?좑툘 **ONE SESSION AT A TIME** ??re-read `CLAUDE.md` + this. Narrative ??**`archive/2026-09-19-status-cycle47-relocate.md` (latest ??T2's block diff and what it closes, the readable-ORIGINAL correction, the five killed retrospectives)** + `archive/2026-09-19-status-cycle39-judgement.md` + `archive/2026-09-18-status-cycle34-n1.md` + `??cycle23-close.md` + the `archive/2026-09-1[678]-status-*.md` set.
?뵷 **The DELIVERED line (display-loop VI ACCEPTED functionally in cycle 110; D1 S1/S2/S3/S3a/S3b artefacts) and the superseded bed narratives (L2-A3 back to M3a-3b row D) RELOCATED VERBATIM ??`archive/2026-10-01-status-cycle123-relocate.md` 짠2.** The live bed is the `current-bed:` key in ## NEXT.
?넅 **USER RULE 17:5x = `docs/cycle27-plan.md` Pre-decided 9 ??EVERY GUI action is capture ??locate ??act ??capture ??confirm; derived or remembered coordinates are NEVER clicked blind.** It turned v4's 13/3 into v5's 39/1.


## START HERE
1. **Cycle plan = `docs/d1/INDEX.md`** (card chat-D1 2026-10-02: the in-force decisions, one line each, linked into the FROZEN long plans `docs/d1-loop12-17-split-plan.md` / `docs/cycle27-plan.md` / `docs/d1-build-plan.md` / `docs/d1-route-b-plan.md`, whose line numbers are unchanged; NEW decisions go to the topic files `docs/d1/*.md` it lists, numbered from 268; cycle20/21 plans `superseded`; motor plan `docs/motor-limit-assurance-plan.md` **짠A.1 + "P2 live findings"**; master `docs/pre-rig-master-plan.md`; decisions `docs/decisions.md`).
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

## HARDWARE ??permission follows the RIG STATE. Current: **議곕┰ / ASSEMBLED, not in use** (user 2026-10-01 "?꾩옱??由ш렇 ?ъ슜?섏? ?딆쓬"; machine key `rig-state:` below; ?ㅽ뿕以?2026-09-29 ??10-01 ended)
遺꾪빐 = motors ??ASI ??camera ??쨌 **議곕┰ ??WE ARE HERE (user 2026-09-23 14:2x "?ㅽ뿕 留덉묠")** = camera ?? motors/ASI ONLY through `tools/motor_gate.py` inside the envelope, LabVIEW allowed 쨌 ?ㅽ뿕以?= ??????and no LabVIEW use (was the state 12:3x??4:2x; header corrected 2026-09-23 23:4x by the cycle-68 material session). ?좑툘 ASI carve-out **RETIRED** (rule 1b); **only the user announces a state change**.
Rotor counter **0** 쨌 magnet full travel 쨌 camera 1280횞1024, offsets 0, 90.0009 Hz, never write `BinningHorizontal`; **a session open RESETS ROI *and* exposure** ??the acquisition loop applies `tools/bench/camera_contract.py`. **No beads on the rig.**
?넅 **SAFE MOTION ENVELOPE = THE CONTROLLER LIMITS + the gate's command-class denies** (user, 2026-09-18 15:2x at the
rig). PI `SPA 1 0x15/0x30` ??TMN 0 / TMX 39 (RAM, **never WPA**) 쨌 **PI DIRECTION (user 2026-09-27 18:2x, at the rig): 0 mm = CEILING (magnet farthest from the sample, = the negative limit switch `FNL` goes to); larger mm = DOWN, toward the sample** ??so a reference move is the safe direction and any "magnet is low" report means a LARGE mm value 쨌 ASI `SL/SU` absolute mm X ??.8475??.1525, Y ??.7744?╈닋0.7744 (persistent, **never SS Z**),
written+verified by `py tools/motor_gate.py --session start|end` from the user-editable `tools/bench/motor_limits.json`; `--execute` refuses without the session file (tools/bench/motor_session.json, present ONLY while a session is open) **and** a fresh matching readback.
The gate still refuses ?ㅽ뿕以? every ASI home/zero/save, PI GOH/FRF/DFH/RON/POS/SPA/WPA and all rotor motion (self-test `selftest_motor_gate2.py` 85/85, 2026-09-24; FAIL-exit self-test 10/10).
rig-state: 議곕┰   <!-- 2026-10-01 USER (chat): "?꾩옱??由ш렇 ?ъ슜?섏? ?딆쓬. 洹몃?濡?肄붾뵫 ?몄씠???뚮━?꾨줉. ?꾨쭏 ?ㅻ뒛 諛ㅼ젙???ъ슜?좎???紐⑤Ⅴ寃좊뒗?? 洹??뚮뒗 ?닿? ?ъ쟾??留먰븯?꾨줉 ?섍쿋??" ??back to 議곕┰: LabVIEW allowed, motors/ASI only through motor_gate inside the envelope under the 2026-09-24 grant (reference + limits verified), LabVIEW closed at every cycle end. The user will announce the next ?ㅽ뿕以?in advance (possibly tonight) ??graceful runner stop. Previous: ?ㅽ뿕以???2026-09-29 USER (chat): "怨??ㅽ뿕 ?쒖옉 ?덉젙?대씪 LabVIEW???ъ슜?섎㈃ ?덈맖. 洹??꾩뿉 ?⑸럭 臾닿??섍쾶 泥섎━ 媛?ν븳 ?꾨줈?몄뒪媛 ?덈떎硫??숈떆 吏꾪뻾?섎뒗嫄?愿쒖갖?꾨벏" ??no LabVIEW, no camera, no motor/ASI; offline (LabVIEW-free) work only. Runner stays stopped. Motor limits were already released at cycle 121 end. Previous: 議곕┰ ??2026-09-24 20:xx USER GRANT: "?밸텇媛??닿? 留먰븯湲??꾧퉴吏??紐⑦꽣 ?묒냽 ?덉슜?? ?ㅻ쭔 ?먯젏 ?뺤씤 諛?紐⑦꽣 由щ컠, ??媛吏??瑗??뺤씤 ?꾩슂" ??motors (PI, rotor, ASI) may be driven by the gate AND by a running main VI while the rig stays assembled, until the user withdraws it; PI reference + verify at session start and limits set/released with readback are never skipped; "?ъ씠??醫낅즺?섍퀬?쒕뒗 ?쒕?濡?LabVIEW ?꾨뒗寃??딆? 留먭쾬 (?뱁엳 移대찓?쇨? 怨꾩냽 Acquisition ?섎㈃ 湲곌퀎??醫뗭? ?딆쑝??" = runner end hook closes LabVIEW and verifies the process is gone. Earlier: 2026-09-23 14:2x user: "?ㅽ뿕 留덉묠. ?ㅼ떆 ?몄뀡 ?ㅼ뼱媛??臾닿??? ??rig stays assembled; motors/ASI only through motor_gate inside the envelope, LabVIEW allowed. Before: ?ㅽ뿕以?13:43 ("吏湲??ㅽ뿕以묒씠??) ??limits RELEASED and read back (PI 0..52, ASI 짹500, `tools/bench/motor_session_end_20260923c.log`), PI referenced at 0 (FNL, 13:36), servo on; no motor/ASI/camera/LabVIEW use until the user says otherwise. Earlier 13:3x, on the user's order ("?덇? ?쒕쾲 PI 紐⑦꽣 ?吏곸뿬蹂쇰옒? 0?쇰줈 ?대룞, 5珥??뺤?, 30?쇰줈 ?대룞, 5珥??뺤?, 0?쇰줈 ?대룞"): PI test moves through the gate to diagnose "PI doesn't respond to the main VI". Before that: ?ㅽ뿕以? restored 2026-09-23 13:11 after ONE `motor_gate.py --session end` on the user's order ("寃뚯씠?몃줈 ?댁쨾"): limits RELEASED and read back ??PI TMN 0 / TMX 52, ASI SL/SU 짹500 mm, position unchanged (`tools/bench/motor_session_end_20260923.log`). Set ?ㅽ뿕以?2026-09-23 12:3x on the user's words ("?닿? 怨??ㅽ뿕???쒖옉?섎땲 ??LabVIEW ?쒖슜? ?섏? 留먮룄濡?) ??no motor, no ASI, no camera, and NO LabVIEW use at all until the user announces otherwise. Previous: 議곕┰, set 2026-09-17 23:0x on the user's words ("?ㅽ뿕 1李⑤줈 ?앸궗?붾뜲, 由ш렇???좎??섎뒗 以? + "議곕┰ ?곹깭?먯꽌????踰붿쐞 ?덉씠硫?紐⑦꽣 ?덉슜??) 쨌 the gate's ONE machine-readable key, parsed by motor_gate.rig_state(); ONLY the user's announcement may set it to 遺꾪빐 / 議곕┰ / ?ㅽ뿕以? Keep it at the start of the line, unquoted. -->

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
?뵷 **PARALLELISM RULE (user 2026-09-28 19:3x, "洹멸쾶 醫뗪쿋?? 洹몃젃寃?吏꾪뻾?섏옄"):** keep at most 2 live cards (1 LabVIEW build + 1 offline). The offline slot takes ONLY work that cannot be changed by the ring-buffer outcome: the next ring step's prep, FACT CENSUS OF THE ORIGINAL VI (motor / display / scheduler / focus nodes and wires ??the original never changes), and tool/test debt. NO design of the display, motor, scheduler, focus or GPU tracks until the ring buffer (P2?밣6) is done ??they all take the ring's final shape as input (user: "???몄씠?댁쓣 留덉낀?????ㅼ쓬 ?몄씠?댁뿉 蹂?숈씠 ?앷린???쇱씠?쇨퀬 ?섎㈃, 蹂묐젹???덈릺??嫄곗옏??). After P6: ONE interface-contract step (every loop's published/read locals: names, types, writer, cadence; checked against docs/user-rules.md), then the remaining tracks may be designed in parallel. **How (user 2026-09-28 19:4x, "寃곌뎅 怨꾪쉷??議곗쑉?섍퀬 ?뺤젙?섎뒗嫄??먮떒 ?몄뀡??吏꾪뻾?댁빞??):** parallel track sessions only PROPOSE ??each writes its changes (original nodes touched, target loop, locals created with name/type, contract values read) to ONE shared change ledger; a script checks conflicts mechanically; a combined offline stagesim runs all proposals in build order on one graph; the JUDGEMENT session alone reconciles conflicts, fixes the build order and finalises the plan in the plan document. Track sessions never negotiate or decide with each other directly. Ledger format + conflict checker are built in the interface-contract step.
?윟?윟 **FIRST ACT of cycle 138 = ONE offline TOOLING card, ALONE (no LabVIEW card beside it ??it edits stage tools; `docs/d1/ring-p4.md` PD311(e), plan of record `docs/d1/INDEX.md`):** (1) `tools/stagesim.py` gets an FS-frame EXIT row modelled on the MEASURED U6??(`tools/bench/diag_c137_7_types.log:290-306,317,328`: tunnel faces take the source type, both wires unbroken; new faces carried the label `Index of closest\ncal image slice, bead 2`, :301-302) and stops losing `#10465`'s terminal rows after `delete_wire` (PD310(c), `tools/bench/prep_c137_6_facts.md`), each with a self-test; `tools/stagexec.py` `compile_plan` gives the FS exit its own route kind (today a plain `connect`, `stagexec.py:720-721`); **X10 (`tools/stage_prerun.py`) counts whole-VI reads from the script's SOURCE call sites ??the device owed by retrospective-cycle136's `device-failed`**; rerun `tools/bench/c125_1_offline_measure.py` (PD252(a)). (2) Then v8 = `tools/bench/plan_ring_p4_v7.json` (01ab0893) with the smallest-`Num > last` group rebuilt as a For loop + scalar Select + Array Min, MAX I32 by `const_donor` (PD311(b) ??Select takes a scalar `s` only, MEASURED) and Select's output named `'s? t:f'` (PD311(d)); replay + `compile_plan`; prior-art review (new structure class). (3) Then ONE scratch route run: the For-loop group + the 17 uncovered route classes (`tools/bench/prep_c137_p1_facts.md` 짠3). (4) Stop-mode op card `tools/bench/cards/task_137-2.json` (validated, not dispatched) when the LabVIEW slot is free. Carries: `stagekit.address` cannot see a constant in a NEW body (PD307(a)) ??list v8 actions that rely on it; steps 160/162 replay "ok" unmeasured (PD309(c)); `errorlist_check.compare()` names missing classes (PD302(c)); `selftest_x10_c132_1` T3 stale fixture; sim step dirs `tools/bench/sim/ring_p4_v2..v7/` not deleted. Open user decisions: D-2026-10-02-04 (now: 11 sessions / 6 broken files under option 2 at load 600.2, PD303(b)), D-03, D-02, D-01.
- **CYCLE 137 in brief ??P4 plan v7 compiles end to end; four route causes MEASURED; no new VI (6-dispatch cap):**
  - 137-P1 PASS 5/0 (offline): step 102 = plan addressed control terminals by owner diagram (vigraph/stagexec key a CT by its own uid) ??v4; session table 12/11 at 600.2/675; 24 unmeasured route classes; P3b-1?뭁3b-2 one-sided wires differ by {4878} only ??bed stays (PD303).
  - 137-1 FAIL 3/1 ??137-3 PASS 5/0 (scratch-VI rule): a constant in a NEW While body is NOT in `Diagram.Nodes[]` (node_labels / Stage.address blind); `read_terms` by owner uid finds it (PD304, PD307).
  - 137-P2 / 137-P3 / 137-4 / 137-6 (offline): v4 ??v5 (explicit `#10170` tunnels, PD298(b) precedent) ??v6 (RLEs dropped; step 3 = 41 accepted under "??~40") ??v7 01ab0893 (reseed decide = PD300(b) option 2): `compile_plan` ALL 172 actions ??160 ops; replay to 158 (PD305?밣D310).
  - 137-5 FAIL 3/1 (LabVIEW scratch): A2, U1, U2, W1-Or, U5 PASS; U3, U6 broken. 137-7 PASS 5/0: Select's `s` is scalar-only (measured + NI) ??reader redesign PD311(b); U6 failed only on an untyped source, U6??PASS ??FS exit modellable (PD311).
  - Reviews disposed: c135e (bed stays), c137-p3-mkv5-stepcount, c137-4-mkv6-step164, c137-7-hyp, c137-7-gemini.
- (history) ?윟?윟 **FIRST ACT of cycle 137 = two cards in ONE message (`docs/d1/ring-p4.md` PD301(c)-(e); plan of record `docs/d1/INDEX.md`):** (1) LabVIEW card (`labview: build`, `gui: true`, scratch only, bed never edited) = patch `tools/bench/diag_c136_3_routes.py`'s per-node lookup for nodes created in a NEW While body (`diag_c136_3_routes.log:36-46`), list its whole-VI read call sites, X10 prerun, ONE run of routes U1 U2 U3 U5 U6 + W1 Or (brief `tools/bench/cards/brief_136.md`); then build a read-only op (pattern `tools/bench/build_oploopendref_v0.py:250-266`) and READ `#10170` `Stop If True?` (6362C01, community-sourced) and `stop (end)`'s Mechanical Action on a bed byte copy; (2) offline card (`labview: none`) = diagnose stagesim step 102 of `tools/bench/plan_ring_p4_v3.json` d14c1bba ("#686 owns no terminal" while the real graph `graph_ring_p3b2b_20261002_133824.json` lists t8936 on 686; `prep_c136_p2_sim.log:101-106`), read-only, and recompute v3's session table from MEASURED per-session loads (PD301(a): fresh LabVIEW 567.7 MB, bed load 576.5??00.2, memory resets per session). Carries: hypothesis review `archive/peer/2026-10-02-c136-3-c135e-elmismatch.md` has no disposition written yet (it holds `guard_peer` for `launch_p3b2_c135_e.log`; owed: its offline one-sided-wire test + `errorlist_check.compare()` naming fix); `selftest_x10_c132_1` T3 stale fixture; X10 counts dry-executed reads only (PD299(b)); 65+103 sim step files in `tools/bench/sim/ring_p4_v2|v3/` not deleted (permission layer). Open user decisions: **D-2026-10-02-04 (new: P4 = 159??63 edits, file count)**, D-03, D-02, D-01.
- **CYCLE 136 in brief ??P4 planned to v3, memory wall measured and refuted; no new VI:**
  - 136-1 BLOCKED 16/1: FS-aware graph of the bed `graph_ring_p3b2b_20261002_133824.json` (bed md5 unchanged); routes script blocked by X10 on non-Executor edit diagnostics (fp-33). `#10171` x,y on one wire confirmed; Or donor = bed `#10247`.
  - 136-P1 FAIL 5/1 (offline): P4 v2 = 159 actions (rollback Selects 43), replay stops at the pool crossing (PD298). fp-30 self-test fixed.
  - 136-2 FAIL 3/2 (offline): X10 edit-diagnostic branch (fp-33 drained, 6/0); bed load not in memory_model; reads undercounted by the dry (PD299).
  - 136-P2 FAIL 5/1 (offline): P4 v3 163 actions, replay to step 101 on the real graph; fp-30/fp-32 drained (PD300).
  - 136-3 FAIL 3/2: bed load 600.2 entered; routes run stopped on our lookup bug; no stop-mode reader exists.
  - 136-4 PASS 13/0: LabVIEW 64-bit, fresh 567.7 MB, bed +9 MB, 40 reads to 653.5 MB with no error 2 ??P4 feasible in fresh sessions (PD301).
- (history) ?윟?윟 **FIRST ACT of cycle 136 = P4 preparation (`docs/d1/ring-p4.md` PD293 + PD295; plan of record `docs/d1/INDEX.md`), two cards in ONE message:** (1) LabVIEW card (`labview: build`, `gui: true`, scratch only, no bed edit) = PD295(e): ONE scratch VI verifying Select on a Boolean array / I32 MAX constant / Array Max & Min / Boolean-array selector, ONE scratch byte copy verifying While outer face ??FS frame and FS-frame exit, find or make the `Or` donor for W1's stop, plus a real graph read of the new bed `D1_ring_p3b2b_20261002_130007.vi` (39511877) and `#10170`'s conditional-terminal mode; (2) offline prep card (`labview: none`) = P4 draft v2 from `tools/bench/plan_ring_p4_draft.json` with PD293(b)-(d) + PD295(a)(c)(d) (rollback Selects on every 1.2 register written by tracking, 5th per-slot array `BufDiff`, W1 stop exit, 1.2 stop replaced, n2 via one-frame FS on a `#5058` output), cut into ??40-action build steps, X10 per LabVIEW session, routes marked measured/unmeasured. Open user decisions: D-2026-10-02-03 (P4 file count; proceed with ??40-action steps), D-2026-10-02-02, D-2026-10-02-01. Tooling carry: fp-30 ??fix `selftest_c134_1_dry.py` (fails 10/1 on its own content, 135-2), then drain; F3 reference of `diag_c134_1_finalize_b.py` wrong for an a-file finalize (PD294(c)).
- **CYCLE 135 in brief ??P3b-2 DELIVERED (bed moved); P4 sized and its design decided:**
  - 135-1 FAIL 11/1: launch session a PASS 20/0 (645.7 MB, CEN2 == pred); compare DIFFERENT only on a reader annotation ??the runner's finalize branch failed F3 and overwrote plan b (PD294).
  - 135-2 FAIL 6/1 (offline): plan b restored ae6b6111, strict re-annotated compare EQUAL, finalize write-guard + completeness gate (6/0), resume runner dry 11/0, review r2; fp-30 not drained.
  - 135-3 FAIL 2/1: plan-content diff = base-file identity only ??accepted (PD296). 135-4 PASS 13/0: resume launch, b 620.6 MB, `D1_ring_p3b2b_20261002_130007.vi`, EL 51. 135-5 PASS 18/0: expected file from the final read, bed key moved, in-between files deleted (PD297).
  - Prep 135-P1 PASS: P4 = 93 actions, X10 824 MB ??user decision D-2026-10-02-03; design PD293 (rollback, valid = n1==n2 AND n1>last, W1 + stop exit). Prep 135-P2 PASS: `#5119` value is SAVED ??`BufDiff` per-slot array; 1.2's stop is an S2 scaffold (PD295).
- (history) **FIRST ACT of cycle 135 = the ONE launch of ring step P3b-2 (`docs/d1/ring-p3b.md` PD291(f); plan of record `docs/d1/INDEX.md`).** Both LabVIEW sessions (a 21 edits / b 18) from the bed, one chained runner prepared and dry-checked in cycle 134: `py tools/bgrun.py --material --max-min 200 --log tools/bench/launch_p3b2_c135.log -- py -u tools/bench/launch_p3b2_c135.py --launch` (card: `labview: build`, `gui: true`). PD291(b)(c)(d) were CLOSED by card 134-6 (PASS 4/0, PD292(a)(b)): a's census in its pred from graph-read uids, vanished Error List items = loose ends 22 ??20 only (class level, PD274 precedent), runner `launch_p3b2_c135.py` 16e941a6 with no failing-by-design log. Offline step 0 = ONLY PD292(c): read whether recipe a's CEN2 is fatal before the save and whether stagekit's census and the graph-diff census count created uids by the same class keys; if not, the launch card names a's CEN2 as an expected unverified gate. Predictions: a peak ??50.9 MB, b ??677 (stop 690), graph compare EQUAL ??plan b `ae6b6111` reused, final Error List 49..52 (scratch measured 51). On acceptance: bed ??P3b-2 final (STATUS `current-bed:` + INDEX), 4 of 6 broken files (assumption D-2026-10-02-02), delete `scratch_c133_6_ring_p3b2a_20261002_093837.vi` and the launch's in-between file.
- **CYCLE 134 in brief ??P3b-2 made launch-ready; no new bed (6-dispatch cap):**
  - 134-1 FAIL 5/2: dry rule device live (a gate FALSE on simulated data fails the dry; `DRY PASS-UNVERIFIED` refused at launch unless named; 11/0); FS reader records frames/borders ??**f0 of FS #27509 MEASURED = 27641**; 7 nested-FS border tunnels unclassifiable (PD288).
  - 134-2 FAIL 3/1 ??134-3 (return at step 1) ??134-4 BLOCKED 4/0 (fp-30): gate B scoped to borders the plan uses; launch needs `dry_rule` 2; FS owners from measured links (fs_frames + border outer faces); **session b FINALIZED on the measured graph** `plan_ring_p3b2b.json` ae6b6111, cdiff 16, prerun 15/0, X10 667.0 (PD289??90).
  - 134-5 FAIL 4/1 (only a's census missing): **scratch b PASS 20/0, peak 629.0 MB, Error List 51 in 49..52**, b's census measured into its pred (PD291(a)). Prep 134-P1 PASS 5/0: launch runner `launch_p3b2_c135.py` + children, self-test 13/0, runner dry 17/0; session a re-dried under rule 2.
  - Retrospective-cycle134: `repeated-failure-class` 24 min (FS owner fact recorded in PD279(b) dropped by the reader spec) ??DEVICE owed in cycle 135 AFTER the launch (before it if the runner re-finalizes): base-graph completeness gate in finalize/rebase + finalize writes the plan only on success (`docs/violation-decisions.md` 2026-10-02 12:2x).
  - Carries: fp-30 (`labview: none` refuses `selftest_c134_1_dry.py`, offline); nested-FS borders (FS 2499/14682/43914) UNMEASURED ??measure when a plan first routes through one (check P4); recipe b writes P3b-1's 53-item list as expected (not used); still open from 133: `load_by_vi` from stage-context meters, X10 refuses unmeasured load, stale rebase/rebind fixtures, `decisions_pending.json` D-2026-09-28-01 > 300 chars fails validate.
- **CYCLE 133 in brief ??P3b-2 cut into two LabVIEW sessions by memory; session a PASSED as a scratch; no new bed (6-dispatch cap):**
  - 133-1 FAIL 2/1 (offline): 98992a59's `final: false` was no regression; the op-24 route stop = FS wires compiled from the plan only ??`finalized.fs_routes` (6/0); rebased P3b-2 04204133 final, route 39/39, but BIND 22 / R 24 ??X10 701.9 MB. 133-2 PASS (memory meter facts) (PD283).
  - 133-3 PASS 5/0 (offline): X10 start from the measured input load; rebase keeps the original plan_in; cut a 21 / b 18 (X10 671.8 / 677.7); a dry 21/21 + prerun 15/0; final-file Error List range 49..52; gate-fp queue drained (fp-21, fp-28 closed) (PD284).
  - 133-4 FAIL 3/1 (offline): the `wrong-ordering` device is live ??guard_session refuses a LabVIEW card beside a card that writes stage tools (10/10; `docs/violation-decisions.md` 2026-10-02 08:25); chat_p1 fixture narrowed in 133-5 (46/0).
  - 133-5 FAIL 12/2 (LabVIEW): scratch a ran 21 ops real == simulated, then our FR gate refused the empty-by-design frame f0 (PD285). Stage-context start 570.4 MB, not the reader's 590 (carry).
  - 133-6 FAIL 3/1 (LabVIEW): FR fixed (9/0, review = our-script-bug); scratch a PASS 20/0 at 650.9 MB, in-between kept; b's rebase refused on a's created tunnel terminal ??0 (PD286).
  - Steer `steer_132` FOLLOWED. New user question D-2026-10-02-02 (does the in-between file count toward the 6-file cap? we proceed as "no"). Carries (PD284(b)(e), PD285(c), PD286(e)): X10 must refuse an unmeasured load; `load_by_vi` from stage-context meters; graph reader records FS frames/borders; stale rebase/rebind self-test fixtures; `decisions_pending.json` item D-2026-09-28-01 (613 chars) fails `protocol.py validate` for the whole file.
- **CYCLE 132 in brief ??tools for the P3b-2 rebase built one gap at a time; real P3b-1 graph read; no new VI (6-dispatch cap):**
  - 132-1 FAIL 3/1 (offline): X10 + final-read 17.4 MB, FAIL 690 (P3b-1 680.8 vs 680.4 measured; P3b-2 681.7); per-op tunnel-name gate `stagexec.tunnel_name_check` (fs_border only; FS inner names unmodelled); `errorlist_expect_p3b2.py` ??range 50..52; fp-19/20 drained; fp-21 left (not on P3b-2's path); fp-28 needs a close verb in `gate_fp.py` (PD275??76).
  - 132-2 BLOCKED (my card's own no-stage_prerun rule) ??132-3 BLOCKED on fp-29 (X10 UNMEASURED for a read-only reader) ??132-4 FAIL 3/1: X10 reader branch (fp-29 drained); graph read `graph_ring_p3b1_20261002_073225.json` (bed md5 unchanged, 584.1 / 599.9 MB, #6810 nets 9/9, 0 swapped loose ends); rebase refused on simulator LABEL keys (PD277??78).
  - 132-5 FAIL 2/1: rebind by connectivity (7/0, Unbundler status ??Select); re-sim stopped at step 24 (no FS map in the real graph); the failed rebase had overwritten the plan (PD279).
  - 132-6 FAIL 1/1: FS-map carry + no-write-on-failure (8/0); provisional P3b-2 re-made 98992a59 (same 39 actions, but `final: false`); re-sim 39/39 on the real base; route check stops at op 24 (PD280). LabVIEW ran once (graph read). Retrospective-cycle132: `wrong-ordering` 9 min (132-2 dispatched beside the card editing its gate) ??PD281.
- **CYCLE 131 in brief ??FS tunnel-naming rule measured; P3b-1 LAUNCHED and ACCEPTED as the bed:**
  - 131-1 PASS 3/0 (offline): 18-crossing table `tools/bench/fs_tunnel_naming_table.json`; rule = a SubVI source names the tunnel with its terminal name (Function `''`), stagesim 105/0; P3b-1/P3b-2 re-finalized (edbdba99 / b25c1ecb), P3b-1 dry 31/31 + prerun 15/0 (PD271).
  - 131-2 PASS 4/0 (offline): guard_peer offline rule v2 (AST), measured 5/5 false positives pass + 53/53 LabVIEW launches still held; fp-22/24/25/26/27 drained; guard_cycle BUILD_RE fixed (PD271(d)).
  - 131-3 FAIL 1/1 (LabVIEW scratch pin4): 22/0 gates, names right; peak 680.8 MB > 675 from the final whole-VI read (+17.4) ??launch stop 690 (PD272).
  - 131-4 FAIL 16/3: scratch Error List 53 vs 54 (one extra loose wire end cleared on a rebuilt net) (PD273). 131-5 FAIL 4/1: P3b-1 LAUNCHED 22/0, 680.4 MB, `D1_ring_p3b1_20261002_060910.vi`; final read stopped on the helper's per-entry debit. 131-6 PASS 25/0: final read 53, only loose ends 24 ??22 ??bed moved (PD274).
  - Open gate-fp: fp-19/20/21 (stage_prerun); fp-28 is a CORRECT refusal ??close it, no code change (retrospective-cycle131, `VIOLATION: none`).
  - Owed in card 1 of cycle 132 (retrospective-cycle131): `diag_c131_5_stubs.py` PASS must depend on its check; P3b-2's expected Error List computed from the simulator's retired-wire set, never typed (`w27378` in P3b-1's `pred.removed` is unmeasured). Cycle 131 ended on the 6-dispatch cap.
- **CYCLES 127??30 in brief RELOCATED VERBATIM ??`archive/2026-10-02-status-cycle133-relocate.md` 짠1** (P3b split and re-cut by memory, X10 model, FS tunnel-naming, the error guard's donors). Still-live carries from them: `census_predict` lacks wire/RLE/FS row branches (PD261(c)); bounded close in stagekit's FAIL path (PD270(c)); stop_record H1?밐3.
- Tools now available (cycles 126??27): `gscript.hygiene_run` (EVERY op hygiene check goes through it); ops `OpFsAddFrame_v0`, `OpFsDiagrams_v0`, `OpWireRemoveLooseEnds_v0` + `gscript.wire_remove_loose_ends`; stagexec routes `fs_create` / `fs_frame` / `fs_frame_to_frame` / `fs_border` / `fs_border_inner_branch`.
- **CYCLES 124??26 in brief RELOCATED VERBATIM ??`archive/2026-10-02-status-cycle129-relocate.md` 짠1** (P3a delivered by 124-8; FS ops, `hygiene_run`, crossing routes). Still-live carries there: `docs/NAMES.md` lacks the measured Wire method ids (`diag_c126_2_op.log:8-16`) and the FS methods; `selftest_fs_c126.py` not in `protocol.OFFLINE_SELFTESTS`; `c125_1_offline_measure.py` reruns after any `stagexec.py`/`stagekit.py` edit (PD252(a)).
- **CYCLE 123 in brief RELOCATED VERBATIM ??`archive/2026-10-01-status-cycle126-relocate.md` 짠1.** Still live from it: user decision D-2026-10-01-01 ??ANSWERED 2026-10-01 (option 1: ??~40 edit operations per ring step, full scratch run before each, 6-file cap kept); carries `docs/d1-build-plan.md` still `status: current` (L5), decisions item 13 over 300 chars, cycle 122's carries (stagekit donor declaration, `_check_units`, RULE-OFFLINE-CARD reverse, `requires` for routes/donors, fp-10).
- **CYCLE 122 in brief RELOCATED VERBATIM ??`archive/2026-10-01-status-cycle123-relocate.md` 짠6** (its carries are repeated in the cycle-123 brief above).
- **CYCLE 121 in brief and the cycle-121-start FIRST ACT block (chat-P3, then the ring-buffer plan) RELOCATED VERBATIM ??`archive/2026-10-01-status-cycle123-relocate.md` 짠3.**
?뵶 **USER RULE, re-confirmed 2026-09-28 15:3x (chat) ??the POOL's overload branch (D-2026-09-28-01, now ANSWERED): the user decided this on 2026-09-15 and it has a PRIORITY ORDER.** (1) NO CORRUPTION: an image and its buffer number change together and the consumer verifies them ??a pixel/number mismatch is corruption. (2) LATEST-WINS: when tracking falls behind, discard the queued backlog and read the newest frame ("?먮? 踰꾨━怨??덈줈 ?ㅼ뼱?ㅻ뒗 ?꾨젅?꾩쓣 ?쎈뒗 寃껋씠 媛??諛붾엺吏곹븿. ?대뒗 ?쒓퀎???곗씠?곗쓽 ?꾨??깆쓣 ?꾪븿"); a gap recorded by the buffer number is fine. (3) FALLBACK: if (1)+(2) cannot be made provably safe, acquisition and tracking may stay in ONE sequential loop. **The planned "full Q_work ??skip the newest read" (d1-build-plan.md 짠9, PD233/234) VIOLATES (2)** ??the judgement session re-decides the overload branch against this order before any real run (memory `prefer_the_freshest_frame_over_a_complete_backlog`, `docs/decisions.md:25`). Structure already built (the 20-slot pool) may stay; only the overload behaviour changes.
?윞 **CARRY (from the 2026-09-25 verification review `archive/peer/2026-09-25-hyp-lintverify-20260925.md`, not blocking): card flags are checked only on the top-level command (a child process could reach LabVIEW under labview=none); a stage run launched outside bgrun is not counted by the retry cap; a bgrun record failure is only logged (`tools/bgrun.py:219-220`). Close in a tooling cycle, deliverable-first.**
current-bed: D1_ring_p3b2b_20261002_130007.vi
<!-- ^ machine key read by tools/errorlist_check.py current_bed_text(); without it the bed is chosen by mtime among D1_*.vi names in this file, and the newer D1_s1_kswap_* would silently take over (review archive/peer/2026-09-26-c88-reuse-stalepin.md). Change it only when a new bed is accepted. Moved 2026-10-02 by cycle 135 (PD297, card 135-5): ring P3b-2 accepted (md5 395118775a52bc90073f4449b99f899d, expected Error List tools/bench/errorlist_expected_D1_ring_p3b2b_20261002_130007.json from the final read errorlist_D1_ring_p3b2b_20261002_130007_20261002_130834.json, 51 items). Moved 2026-10-02 by cycle 131 (PD274(c), docs/d1/ring-p3b.md): ring P3b-1 accepted (md5 9d7bf28738b7c154280e5e7c2c9d4961, expected Error List tools/bench/errorlist_expected_D1_ring_p3b1_20261002_060910.json, 53 items). Moved 2026-10-01 by cycle 124 (PD251(a)): ring P3a accepted (md5 4dfa44aac8fb32f706b3eb792ee7d3cc, expected Error List tools/bench/errorlist_expected_D1_ring_p3a_20261001_180540.json, 55 items). Before: ring P2b (cycle 123, PD246(a), md5 652b1447ebbda761a7d5ba36455a0fa1). -->
?뵷 **THE WORK VI (bed) IS NOW `claudeDev\D1_ring_p3b2b_20261002_130007.vi`, md5 `395118775a52bc90073f4449b99f899d` (cycle 135, PD297, `docs/d1/ring-p3b.md:409`): P3b-1 plus the other 39 slot-write actions (TransPos/RotPos/FrameIdx groups, `Num(i)=-1`, Latest) ??P3 complete. Error List 51 (loose ends 22 ??20), expected file `tools/bench/errorlist_expected_D1_ring_p3b2b_20261002_130007.json`. STRUCTURAL, ExecState 0 by design, never run; broken-file count 4 of 6.** Its input P3b-1 (below) is kept.
?뵷 **(history) THE WORK VI (bed) WAS `claudeDev\D1_ring_p3b1_20261002_060910.vi`, md5 `9d7bf28738b7c154280e5e7c2c9d4961` (cycle 131, PD274): P3a plus the first 31 slot-write actions (IMAQ Copy into the slot + the error guard; FS frames f0 0 / f1 16 / f2 18 terminals). Launch 22/0 gates, peak 680.4 MB; Error List 53 (P3a's 55 minus 2 loose wire ends on nets the plan rebuilt), expected file `tools/bench/errorlist_expected_D1_ring_p3b1_20261002_060910.json`. STRUCTURAL, ExecState 0 by design, never run; broken-file count 3 of 6.** Its input P3a (below) is kept.
?뵷 **(history) THE WORK VI (bed) WAS `claudeDev\D1_ring_p3a_20261001_180540.vi`, md5 `4dfa44aac8fb32f706b3eb792ee7d3cc` (cycle 124, PD251(a)): P2b plus loop 1.1's control ??`Wait (ms)` 1, the previous-BufNum register (I32, ??), `Equal?`, the duplicate/new-frame case, the new-frame counter (I32, 0; incremented in False, passed through in True), `i = count mod 20`. Error List 55; STRUCTURAL, ExecState 0 by design, never run; broken-file count 2 of 6.** Its input P2b (below) is kept.
?뵷 **THE WORK VI (bed) IS NOW `claudeDev\D1_ring_p2b_20261001_140658.vi`, md5 `652b1447ebbda761a7d5ba36455a0fa1` (cycle 123, PD246(a)): P2a plus the five ring indicators `Num`/`TransPos`/`RotPos`/`FrameIdx`/`Latest` and their initial values on FS1 frame `#4866`; Error List 54 items, expected file `tools/bench/errorlist_expected_D1_ring_p2b_20261001_140658.json`; STRUCTURAL, ExecState 0 by design, never run; broken-file count 1 of 6.** (history) Its input `claudeDev\D1_ring_p2a_20260928_191739.vi`, md5 `c22a473f26ebcc67296d1c2441f8a47a` (cycle 121, PD238(l)), is kept: the pool bed below minus its two queues; Error List 54 items, expected file `tools/bench/errorlist_expected_D1_ring_p2a_20260928_191739.json`. The bed before it was `claudeDev\D1_qrt_pool_20260928_141055.vi`, md5 `9353936895141d3ec2f890649c5cf22f`. It is the POOL stage: 20 image buffers `Cam_pool00`??19` and the two queues Q_free / Q_work, added to R2 and not yet consumed. Expected Error List file `tools/bench/errorlist_expected_D1_qrt_pool_20260928_141055.json`: 53 items (== R2's), reverdict OK (PD236(a)). STRUCTURAL, ExecState 0 by design, never run. Its input R2 (`D1_l2_r2_20260928_110756.vi`, md5 `7dac9f04??) is kept.
- **Cycles 82??20: the FIRST ACT blocks, the cycle briefs, the cycle-84 L2-A1 run plan and the cycle-101 stage pass criteria RELOCATED VERBATIM ??`archive/2026-10-01-status-cycle123-relocate.md` 짠4.**
- Standing: card `peers` = hypothesis, outcome, priorart. Every card that builds or edits a VI carries `gui: true`; on ExecState 0, read the Error List first.
?뵷 **CYCLES 68??0 DONE records, old FIRST ACT paragraphs and carries RELOCATED VERBATIM ??`archive/2026-09-25-status-cycle81-relocate.md` 짠2** (card 81-1). Still-live items there, one line each:
- ?윞 FOR THE USER: `.claude/settings.json` guard_session matcher `Agent|Task` ??`Agent|Task|SendMessage` (only you can apply it); `git commit` at cycle close needs your approval-list entry (짠2).
- ?뵶 Rule: desk-check PREDICTED VALUES, not only gates ??Pre-decided 132 (짠2).
- ?윞 Carries not ahead of the deliverable: cp949 print helper in stagekit, audit A1 vs `jev_gate.log`, bgrun END guarantee under a tree kill (짠2).
- ?좑툘 Per-session cap 180 min: write `## NEXT` by minute 150; every new stage/diagnostic ??20 lines on stagekit (짠2).
- Still the user's to overturn: N1 on the pre-bead-loss window, bead-4 FLIP mask, harness records 60 controls and sets none, `background VIs_COPY` untouched (짠2).

## Where to look ??**`docs/handover-2026-09-22.md` (???몄뀡? ?닿쾬遺??** 쨌 `CLAUDE.md` 쨌 `docs/secrets-and-handover.md` (API keys, ?ъ슜??援먯껜 泥댄겕由ъ뒪?? 쨌 `docs/jev-integration-plan.md` (Jev ?쎌엯 ?먮━, 2026-09-22) 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 **`docs/toolkit-capabilities.md`** 쨌 **`docs/motor-call-site-census.md`** (P1) 쨌 **`docs/d1/INDEX.md`** = the current plan (`docs/d1-route-b-plan.md` frozen 2026-10-02) 쨌 `tools/recipes/build_d1_routeb_v0.py`.

## RUNNER STOPPED history (2026-09-22 09:58, 2026-09-24 07:29, 2026-09-25 01:02, 2026-09-25 10:30) ??`archive/2026-09-25-status-cycle81-relocate.md` 짠3

## RUNNER STOPPED 2026-09-27 08:25:46 (cycle 107, lifted) ??`archive/2026-10-01-status-cycle123-relocate.md` 짠5


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"priorart-c138-4-p4v8-forloop","verdict":"<one of: novel | settled-already>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

**Verdict: not novel. Most of this structure has already been built here, and the open questions about indexing and the I32 constant were answered in earlier cycles.**

## PART A: the direction

**A1, settled already (this is the plan's own source, not a blocker).** The design itself (a For loop, a scalar Select, then Array Max & Min, with MAX = I32 2147483647 from `const_donor`) was decided in PD311(b), `docs/d1/ring-p4.md:233-237`. The plan moves Greater? outside the For loop and says so, so it does not contradict PD311(b).

**A1, settled already: how the indexing mode is enforced.** The plan asks this as an open question, but it was answered in PD235(c), `docs/d1-loop12-17-split-plan.md:2212` (cycle 119): *"The names tunnel keeps an explicit set-indexing row plus its read-back gate, even though LabVIEW auto-indexed it … The build must not depend on that automatic behaviour. `stagexec.py:1561` (index_mode_fix only under `if lost:`) is NOT changed."* The way it is applied:
- The recipe calls `be.index_mode_fix(...)` itself after `Executor.run`: `tools/recipes/stage_d1_qrt_pool.py:46-47`. The rule is written down in `tools/bench/plan_qrt_pool_pred.json:18`.
- On the real launch the gate passed, IndexMode 1: `tools/bench/stage_d1_qrt_pool.log:222` (*"TI names tunnel #26131 IndexMode == 1 (plan indexing True), set + read back by index_mode_fix"*).
- So v8's three tunnels TFN1, TFB1 and TFS1 each need the same gate in the recipe, as on the pool stage. The plan does not mention it.

**A4, evidence the plan did not use: a constant in a NEW body cannot be addressed.** PD307(a), `docs/d1/ring-p4.md:188-193`, measured that a `const_donor` constant in a new While body is not in `Diagram.Nodes[]`, so `stagekit.address` cannot see it. STATUS NEXT carries this forward as *"list v8 actions that rely on it"*. KMX1 (on the For body) and KMX2 (on W1's body) are both `const_donor` constants in NEW bodies, and the brief does not say how their wires will be addressed.

**A2 / A3:** I found nothing.

## PART B: the artefact

**B1, already built: a plan-made For inside a plan-made While, with indexing tunnels, run through stagexec.**
- The display-loop stage (`tools/bench/sim/c109c_post/plan_disp.json`):
  - `create ForLoop DLF1` on `new:DL1.body` (`:36-43`).
  - `tunnel` TRING1, input, `indexing: true` (`:425-434`), and TOUT1, output, `indexing: true` (`:556-565`).
  - DLF1's N is never wired: no `N`/`count` wire anywhere in the plan.
- It ran through `stagexec` (STEPX tunnel ops, `tools/bench/stage_d1_disp_c104B3.log:90,130`). It ended at ExecState 1 and was saved by script (`:311-324`), and the display VI was accepted functionally in cycle 110 (STATUS, DELIVERED line).
- So "a For loop with N unwired and only auto-indexed inputs, built by our scripting" has been done once, and it compiled.
- The pool stage did the same with For PF1 (`plan_qrt_pool.json:316-321`), but on an existing diagram (parent 13236), and in a broken-by-design bed.
- Caveat: no `index_mode` line appears in any disp log, so LabVIEW's default modes were right there without the fix. Whether that default holds was not measured for a For inside a While that sits in a Flat Sequence frame.

**B3, a helper exists, for KMX2 only.**
- `stagekit.const_row` (`tools/stagekit.py:897-910`, `OpCreateConstOnTerm_v0`) creates a constant typed by the sink, with a chosen value, on a node in a While body. It was measured with the value read back (`docs/d1-route-b-plan.md:154`).
- It accepts a value of 2147483647 (`diag_c137_7_types.log:77`). It came out DBL there only because Select.f's sink had no type yet (`:218`, PD311(b)).
- Less?.y on W1's body, created after Less?.x is wired, is the typed-sink case. So KMX2 probably does not need a donor; the I32 result after x is wired has not been measured.
- KMX1 on the For body is different: `const_row` looks up a WhileLoop by `loop_uid` (`stagekit.py:903`), so it does not cover a For body. The existing donors (`DonorSRInit_v0` #134 U32 max, #248 I32 0; `DonorRingConst_v0` #249 I32 −1, `ring-p4`/`d1-loop12-17-split-plan.md:2448-2451`) hold no I32 MAX. A new donor, or a For-body route, really is needed for KMX1 only.

**B4, already measured: the Select pieces.**
- A scalar Boolean on `s` leaves the wire unbroken; a Boolean array breaks it (`diag_c137_7_types.log:171-189`, PD311(a)).
- Greater? on (I32 array, I32 scalar) gives Boolean[] (`:220-224`).
- What has not been measured: an auto-indexed Boolean tunnel feeding Select.s inside a For. Nothing I found covers that.
- I could not confirm a precedent in the original VI for Greater? on an array followed by an auto-indexed For. That remains unread, not refuted.

## PART C: the user's rules

I found no contradiction. The plan uses no queue, adds no wait or gate on the camera, puts no serial on the frame path, and changes no per-bead number. MAX is a value used only by the new reader (U1, U4, U6, U13 hold).

PRIOR-ART: settled-already
PRIOR-ART: already-built
PRIOR-ART: helper-exists
PRIOR-ART: unread-evidence

VERDICT {"schema":"verdict/1","id":"priorart-c138-4-p4v8-forloop","verdict":"settled-already","alternative":"Copy the disp DLF1-in-DL1 pattern (ExecState 1) and PD235(c)'s recipe-level index_mode_fix + read-back gate (stage_d1_qrt_pool.py:46-47) for TFN1/TFB1/TFS1; use const_row for KMX2 after Less?.x is wired; a new I32-MAX donor only for KMX1 in the For body.","discriminating_test":"Scratch run: for each of TFN1/TFB1/TFS1, read IndexMode with index_mode_fix (want 1), check Select.s unbroken on the auto-indexed b[i], and read the KMX2 type (I32) when created by const_row after x is wired.","violations":[],"sources":["docs/d1-loop12-17-split-plan.md:2212","tools/recipes/stage_d1_qrt_pool.py:46-47","tools/bench/stage_d1_qrt_pool.log:222","tools/bench/sim/c109c_post/plan_disp.json:36-43","tools/bench/stage_d1_disp_c104B3.log:311-324","tools/stagekit.py:897-910","docs/d1/ring-p4.md:188-193"],"note":"Release by FIXED: add TI-style IndexMode gates for the 3 tunnels and list the KMX1/KMX2 wires that PD307(a) affects."}

## Sources

(extract from answer)

## What was done with it

Card 138-P1 (offline, 2026-10-02), on the cycle-138 judgement PD312(c) (`docs/d1/ring-p4.md:258-263`). v9 = v8 + the items below,
made by `tools/bench/prep_c138_p1_mkv9.py` (log `tools/bench/prep_c138_p1_mkv9.log`, 19/0; facts `tools/bench/prep_c138_p1_facts.md`).

- A1 (IndexMode) ACCEPTED: each auto-index tunnel TFN1/TFB1/TFS1 gets a recipe-level `index_mode_fix` + read-back gate in PD235(c)
  form; the plan's tunnel whys point to it.
- B3 (const_row for KMX2) NOT TAKEN: ONE donor `DonorI32Max_v0` (built and read back by card 138-6; uid 0 in v9 until then) serves
  KMX1 and KMX2 (PD312(c)).
- A4 / B1 / B4 (`already-built`, `unread-evidence`): no release line from this card; the For/tunnel shape already copies the disp
  pattern (v8), and the new-body constants / auto-indexed `Select.s` stay on 138-6's scratch run.

FIXED: settled-already - tools/bench/plan_ring_p4_v9_recipe_gates.json:9 - v9 adds a fatal TI gate per auto-index tunnel (TI-TFN1 :9, TI-TFB1 :21, TI-TFS1 :33) calling be.index_mode_fix(tunnel, True) after Executor.run with read-back == 1 (PD235(c), stage_d1_qrt_pool.py:46-47), and the three tunnel actions cite it (tools/bench/plan_ring_p4_v9.json:1026,1051,1083).

REFUTED: helper-exists - tools/bench/diag_c137_7_types.log:218 says const_row's KMX came out DBL (type set by wiring order), and this review's own B3 (:319) marks the I32 outcome after Less?.x is wired UNMEASURED, so stagekit.py:897-910 does not cover KMX2 as an I32 2147483647 constant; PD312(c) uses one donor (measured by 138-6 before launch) for both.


## Launch gate - NO RECIPE (explicit opt-out)

No stop record was armed for this review. `tools/prior_art_review.py` was run with `--no-recipe`,
and its mandatory reason is recorded here verbatim:

    NO-RECIPE: card 138-4 is an offline plan card (flags.labview none); the v8 plan is not launched here

This is an opt-out, not a release. It frees no recipe and discharges no verdict; the only release
lines are the two `guard_cycle.py` already validates, and neither of them is this.
