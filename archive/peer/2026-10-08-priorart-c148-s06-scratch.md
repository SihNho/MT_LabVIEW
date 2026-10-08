# priorart-c148-s06-scratch

- **agent:** claude
- **role:** priorart
- **model:** claude-opus-5-5 (effort medium; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $1.2827  in 14 / out 4916 / cache-create 128474 / cache-read 782601  (58s, 11 turn(s))
- **date:** 2026-10-08 15:52:34
- **outcome:** ANSWERED (61s)
- **verdict-card:** VERDICT-CARD priorart-c148-s06-scratch verdict=novel -> tools\bench\cards\verdict_priorart-c148-s06-scratch.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id priorart-c148-s06-scratch, role priorart) ---
CLAIM: The work under review (cycle-start) is novel - not already built, measured, refuted or covered by an existing helper in this project's files.
ATTACHMENT: tools\recipes\stage_d1_ring_p4_s06v18_scratch.py (md5 31009bfce0c0487b0600359c3dac2bd0)
ATTACHMENT: docs\user-rules.md (md5 9e0396da1b6fd9227a6e0ca850337cd5)
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
=== DIFF-ONLY REVIEW (card chat-E3): this script is a copy of tools/recipes/stage_d1_ring_p4_s03v18_scratch.py, whose prior-art review was answered for its current bytes. 8 parameter-only line(s) changed (names, paths, numbers) and are NOT under review. Review ONLY the lines and structure classes below. ===
L19  - 
      + import collections, json, os, re, sys, time
L17  - import json, os, re, sys, time
      + 
L23  - 
      + import stage_d1_ring_p4_s06v18 as R
L24  - 
      + import elrule as ELR
L25  - 
      + SG = SX.check_sink_gates(R.SINK_GATES, R.SINK_FNS)
L26  - 
      + assert len(SG) == 1 == len(R.SINK_GATES) and SG[0]["sink"] == R.SINK, ("scratch expects exactly ONE sink gate", SG)
L23  - import stage_d1_ring_p4_s03v18 as R
      + 
L73  -     print("MEM_STOP_MB {0}; X10 from the md5-pinned pred {1}".format(SX.MEM_STOP_MB, x10()), flush=True)
      +     print("MEM_STOP_MB {0}; X10 from the md5-pinned pred {1}; declared sink gates {2}".format(SX.MEM_STOP_MB, x10(), SG), flush=True)
L78  - 
      + OCR_ALIASES = (("vl", "vi"), ("v", "y"))
L79  - 
      + EL_TOTAL_TOL = 3
L82  - 
      + def norm_ocr(s):
L83  - 
      +     k = re.sub(r"[^a-z0-9]", "", (s or "").lower())
L84  - 
      +     for a, b in OCR_ALIASES:
L85  - 
      +         k = k.replace(a, b)
L86  - 
      +     return k
L89  - 
      + def elcls(it):
L91  - 
      +     c = ELR.item_class("{0} {1}".format(it.get("raw", ""), it.get("detail", "")))
L92  - 
      +     if c:
L93  - 
      +         return c
L94  - 
      +     k = norm_ocr(it.get("raw"))
L95  - 
      +     if "unwiredorbadterminal" in k or ("requiredinput" in k and "notwired" in k):
L96  - 
      +         return "input"
L97  - 
      +     return "other:" + k
L100  - 
      + def el_advisory(items, pred=None):
L103  - 
      +     pr = pred if pred is not None else json.load(open(PREDF, encoding="utf-8"))
L104  - 
      +     el = pr.get("errorlist") or {}
L105  - 
      +     pc = el.get("per_class") or {}
L106  - 
      +     if pred is None and (pr.get("plan") or {}).get("md5") != K.md5(PLAN):
L107  - 
      +         return 2, {"why": "pred not keyed to plan md5"}
L108  - 
      +     if not pc.get("predicted"):
L109  - 
      +         return 2, {"why": "pred has no errorlist.per_class"}
L110  - 
      +     start, want = pc["start_read"]["classes"], pc["predicted"]
L111  - 
      +     got = collections.Counter(elcls(x) for x in items or [])
L112  - 
      +     diff = dict((c, got.get(c, 0) - want.get(c, 0)) for c in sorted(set(got) | set(want)) if got.get(c, 0) != want.get(c, 0))
L113  - 
      +     unseen = sorted(c for c in got if c not in start and c not in want)
L114  - 
      +     td = len(items or []) - int(el["predicted_total"])
L115  - 
      +     rc = 1 if (unseen or abs(td) > EL_TOTAL_TOL) else 0
L116  - 
      +     return rc, {"read_total": len(items or []), "pred_total": el["predicted_total"], "total_diff": td, "per_class_diff": diff, "unseen": unseen,
L117  - 
      +                 "verdict": "RETURN" if rc else "RECORDED"}
L120  - 
      + def el_advisory_print(rc, rep):
L121  - 
      +     print("EL-ADVISORY total read {0} pred {1} diff {2:+}; per-class diff (read - pred) {3}; unseen classes {4}; verdict {5} rc {6}".format(
L122  - 
      +         rep.get("read_total"), rep.get("pred_total"), rep.get("total_diff", 0), json.dumps(rep.get("per_class_diff"), sort_keys=True),
L123  - 
      +         rep.get("unseen"), rep.get("verdict", rep.get("why")), rc), flush=True)
L126  - 
      + def el_selftest():
L128  - 
      +     pr = json.load(open(PREDF, encoding="utf-8"))
L129  - 
      +     want = pr["errorlist"]["per_class"]["predicted"]
L130  - 
      +     txt = {"local": "Local Variable: This variable is not connected to anything.", "sr": "Shift Register: unwired from inside the loop",
L131  - 
      +            "cond": "While Loop: Conditional terminal is not wired", "input": "Index Array 'Index Array': Contains unwired or bad terminal"}
L132  - 
      +     mk = lambda c: {"raw": txt[c] if c in txt else c.split(":", 1)[1], "detail": ""}
L133  - 
      +     base = [mk(c) for c, n in sorted(want.items()) for _ in range(n)]
L134  - 
      +     rt = all(elcls(mk(c)) == c for c in want)
L135  - 
      +     known = sorted(c for c in want if c.startswith("other:"))[0]
L136  - 
      +     cases = [("A unseen class (+1 'Feedback Node: Initializer terminal is not wired')", base + [{"raw": "Feedback Node: Initializer terminal is not wired", "detail": ""}], 1),
L137  - 
      +              ("B total +4 of a known class ({0})".format(known), base + [mk(known)] * 4, 1),
L138  - 
      +              ("C total +2 of a known class ({0})".format(known), base + [mk(known)] * 2, 0),
L139  - 
      +              ("D the prediction itself", base, 0)]
L140  - 
      +     ok = rt
L141  - 
      +     print("EL-SELFTEST synthetic classes round-trip through elcls: {0} ({1} classes, {2} items)".format(rt, len(want), len(base)), flush=True)
L142  - 
      +     for name, items, exp in cases:
L143  - 
      +         rc, rep = el_advisory(items, pr)
L144  - 
      +         el_advisory_print(rc, rep)
L145  - 
      +         print("EL-SELFTEST case {0}: rc {1} expected {2} -> {3}".format(name, rc, exp, "PASS" if rc == exp else "FAIL"), flush=True)
L146  - 
      +         ok = ok and rc == exp
L147  - 
      +     print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if ok else "FAIL", "gates": {"pass": 5 if ok else 0, "fail": 0 if ok else 1},
L148  - 
      +                                   "first_fail": None if ok else "EL-SELFTEST", "artefacts": []}), flush=True)
L149  - 
      +     return 0 if ok else 1
L153  - 
      +     if "--el-advisory-selftest" in sys.argv[1:]:
L154  - 
      +         sys.exit(el_selftest())
L155  - 
      +     if "--el-advisory" in sys.argv[1:]:
L156  - 
      +         _rc, _rep = el_advisory(json.load(open(sys.argv[sys.argv.index("--el-advisory") + 1], encoding="utf-8")).get("items") or [])
L157  - 
      +         el_advisory_print(_rc, _rep)
L158  - 
      +         sys.exit(_rc)
L159  - 
      +     st = K.Stage(R.BASE["vi"], R.BASE["md5"], "scratch_c147_p4s06v18", preload=False, deadline_min=45,
L160  - 
      +                  work_name="D1_ring_p4s06_{0}.vi".format(time.strftime("%Y%m%d_%H%M%S")),
L161  - 
      +                  out_json=os.path.join(K.BENCH, "diag_c147_p4s06v18_scratch.json"), task="card 147-a1-3 scratch P4 v18 session 6")
L153  -     st = K.Stage(R.BASE["vi"], R.BASE["md5"], "scratch_c143_p4s03v18", preload=False, deadline_min=45,
      + 
L153  -                  work_name="D1_ring_p4s03_{0}.vi".format(time.strftime("%Y%m%d_%H%M%S")),
      + 
L153  -                  out_json=os.path.join(K.BENCH, "diag_c143_p4s03v18_scratch.json"), task="card 143-P1 scratch P4 v18 session 3")
      + 

=== THE PLAN (context only; review the lines above) ===
# Context for the DIFF-ONLY prior-art review c148-s06-scratch (card 148-a2-2; docs/d1/ring-p4c.md PD358(c), PD359(e))

Under review: `tools/recipes/stage_d1_ring_p4_s06v18_scratch.py` (md5 31009bfce0c0487b0600359c3dac2bd0), the FULL
scratch run on a byte copy that precedes the real launch of ring P4 session 6 (`tools/recipes/stage_d1_ring_p4_s06v18.py`,
md5 d947df5d9347b389dc4e4b221bf9d241). Its approved sibling is `tools/recipes/stage_d1_ring_p4_s03v18_scratch.py`, last
reviewed in `archive/peer/2026-10-03-priorart-c143-p2-p4s03v18.md` (verdict novel). Review ONLY the substantive changed
lines listed above (the gate code - sink gate SG, E1 real==sim, D/TD/PB structural gates, licence handling, MEMSTOP).

Inputs the changed lines use (read them if a line refers to them):
- plan: `tools/bench/plan_ring_p4_s06v18.json` (md5 cfbd9823d3b47be39de94f2125ad6b66)
- licence: `tools/bench/plan_ring_p4_s06v18_licence.json` (md5 7f70bbf9f64de105f25380f260632d56)
- prediction: `tools/bench/plan_ring_p4_s06v18_pred.json`
- step doc: `docs/d1/ring-p4c.md` (PD354-PD359), index `docs/d1/INDEX.md`

The question is prior art only: does any changed line re-build a gate, helper or check the project already owns
(stagekit.py, stagexec.py, stage_prerun.py, adopt_scratch, earlier s04/s05 scratch recipes), or contradict a measured
or decided fact in those files? Cite file:line for every finding.


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
癤?--
type: status
status: current
date: 2026-09-20
tags: [hand-off]
---
??RESTARTED - USER 2026-10-08 ~11:5x (chat): "?ㅼ떆 ?쒖옉." - rig 議곕┰; runner_supervisor --start-now launched through WMI (Win32_Process.Create, outside the Claude app's process tree, so an app restart does not kill it). Cycle 147 resumes from next.json. When the user announces ?ㅽ뿕以? write a STOP line here.
(history) STOP - RUNNER KILLED 2026-10-08 02:42 when the Claude desktop app restarted (every claude.exe re-created 02:42:53; the detached supervisor/runner were in the app's process tree). Cycle 147 died in assignment round 2 (card 147-a2-1 check PASS 7/0 at 02:42:41, recipe edit unfinished). Chat 11:47: motor limits released and read back (motor_session_end_20261008_appcrash.log); LabVIEW not running. Relaunch only on the user's word.
(history) ??STARTED - USER 2026-10-07 ~23:4x (chat): "?ㅻ뒛 諛ㅻ룞??怨꾩냽 ?뚯븘???좊벏. ?ㅽ뿕 ?≫??덉쑝硫??닿? 留??좉쾶" - rig 議곕┰; runner_supervisor --start-now (8 h rotations, relaunch on routine end). When the user announces ?ㅽ뿕以? write a STOP line here (graceful: the cycle in progress finishes). CHAT 23:4x: the s05 X10 refusal (685.4 > 680, prep_c145_a2_6_pred.log) has its hypothesis review `archive/peer/2026-10-07-c145-s05-x10.md` (ANSWERED): X10's start term is uncertain (two start rules disagree); cheapest test = one load-only scratch of 95e408ff (~1 min LabVIEW); cut under ONE agreed start rule (~op 116, not 120). Judgement decides.
(history) STOP - TWO-CYCLE RUN FINISHED 2026-10-07 23:24 (cycles 144-145, exit 0, $80.54; s03 + s04 adopted, s05 plan made, not launched: X10 685.4 > 680 and the X11 #2626 licence are open). The main runner stays stopped until the user says start.
(history) ??TWO CYCLES - USER 2026-10-07 ~19:5x (chat): "?꾩옱 ?ㅽ뿕 留덉묠. 2 ?ъ씠???뚮젮蹂닿퀬 寃곌낵 蹂댁옄" + "踰ㅼ튂 留먭퀬 ?щ꼫 洹몃?濡??뚮━湲? - rig 議곕┰; main runner launched DIRECTLY with --cycles 2 (no supervisor, no relaunch); the chat restores a STOP line when it ends. Since cycle 143 main has the bench-tool fixes PD347-349 (chat-T3/T4/T5): s03 Error List prediction is now 55 (pred file still says 56 - regenerate first); docs/d1/tooling.md is at 397/400 lines - put the next PD in a new topic file per the doc rule.
(history) STOP - LIVE BENCH FINISHED 2026-10-07 13:18 (report tools/bench/livebench/report_4arms.md); main runner stays stopped until the user says start. (history) LIVE BENCH IN PROGRESS (main runner stays stopped) - USER 2026-10-06 ~15:3x (chat): "?꾩옱 ?ㅽ뿕 留덉낀怨??밸텇媛??ъ슜 ?덊븷?? 留덉? 踰ㅼ튂 吏꾪뻾?섎룄濡? - rig back to 議곕┰ / not in use; the 4-arm live bench (tools/bench/livebench) runs detached in worktrees V6_bench\<arm> one arm at a time: A cycle 2, B cycles 1-2, then function records (chat-F3), then A13, A13K. The main runner restarts only on the user's word.
(history) STOP - TWEEZERS IN USE TODAY (ended ~15:3x, user "?꾩옱 ?ㅽ뿕 留덉낀怨?) - USER 2026-10-06 11:5x (chat): "?ㅻ뒛 ?꾨쭏 ?ㅽ썑 2~3?쒕????몄쐞? ?ъ슜???덉젙?? ?뚮뜕 踰ㅼ튂 硫덉텛怨??섏쨷???댁뼱??吏꾪뻾 媛?ν븯?꾨줉 ?뗮똿?댁쨾". No LabVIEW, camera, motor or ASI work from 13:45 until the user says the experiment is over; EXCEPTION 12:0x user "1踰??몄씠?대쭔 ?곗꽑 ?뚮┫ 寃? + "?쒓컙 留덇컧? 鍮쇱빞吏" = bench arm A cycle 1 only, launched 12:07 in worktree V6_bench\A; it runs to its natural end with NO time limit (the driver's `--not-after 13:45` only stops cycle 2 from starting); the experiment waits for this cycle; the main runner stays stopped; the 4-arm live bench (tools/bench/livebench, card chat-B7) resumes from its per-arm state file on the user's word. Offline cards chat-F2 / chat-B7 wrap up by 13:40. Usage watch line below is history (weekly usage reset 10-05).
(history) STOP - USAGE WATCH (restored by the chat 2026-10-03 12:2x after trial cycle 143 ended, exit 0, $35.00): weekly all-models usage 93 % >= 90 % (user 2026-10-02: "二쇨컙 ?ъ슜??90?쇱꽱???섎㈃ ?ъ씠??吏꾪뻾 硫덉떠以?). Restart only when the user says so (weekly reset 10-05 07:00 KST).
(history) ??SECOND TRIAL CYCLE - USER 2026-10-03 ~10:5x (chat): "洹몃읆 ?ㅼ쓬 ?몄씠?대쭔 ???대낫?? - runner launched with --cycles 1 WITHOUT the supervisor; the chat restores the STOP line below when it ends. Weekly usage 93 %.
(history) STOP (lifted for one more trial cycle) - USAGE WATCH (restored by the chat 2026-10-03 10:4x after trial cycle 142 ended, exit 0, $45.42): weekly all-models usage 93 % >= 90 % (user 2026-10-02: "二쇨컙 ?ъ슜??90?쇱꽱???섎㈃ ?ъ씠??吏꾪뻾 硫덉떠以?). Restart only when the user says so (weekly reset 10-05 07:00 KST).
(history) ??ONE TRIAL CYCLE - USER 2026-10-03 (chat): "???몄씠?대쭩 ?쒕쾾?쇰줈 ?ㅽ뻾?대낫?? - runner launched with --cycles 1 WITHOUT the supervisor (no relaunch); weekly usage 93 %. P4 re-planned with subVIs (next.json).
(history) STOP (lifted for one trial cycle) - USAGE WATCH 2026-10-02 23:04: weekly all-models usage 90 % >= 90 % (user 2026-10-02: "二쇨컙 ?ъ슜??90?쇱꽱???섎㈃ ?ъ씠??吏꾪뻾 硫덉떠以?). Graceful: the cycle in progress finishes, then the runner exits and the supervisor does not relaunch. Restart only when the user says so (after the weekly reset).
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

## HARDWARE ??permission follows the RIG STATE. Current: **議곕┰ / ASSEMBLED, not in use** (user 2026-10-07 "吏湲덉? ?ㅼ떆 ?ㅽ뿕 ?앸궓"; ?ㅽ뿕以?earlier the same day; before: 議곕┰, user 2026-10-01 "?꾩옱??由ш렇 ?ъ슜?섏? ?딆쓬"; machine key `rig-state:` below; ?ㅽ뿕以?2026-09-29 ??10-01 ended)
遺꾪빐 = motors ??ASI ??camera ??쨌 **議곕┰ ??WE ARE HERE (user 2026-09-23 14:2x "?ㅽ뿕 留덉묠")** = camera ?? motors/ASI ONLY through `tools/motor_gate.py` inside the envelope, LabVIEW allowed 쨌 ?ㅽ뿕以?= ??????and no LabVIEW use (was the state 12:3x??4:2x; header corrected 2026-09-23 23:4x by the cycle-68 material session). ?좑툘 ASI carve-out **RETIRED** (rule 1b); **only the user announces a state change**.
Rotor counter **0** 쨌 magnet full travel 쨌 camera 1280횞1024, offsets 0, 90.0009 Hz, never write `BinningHorizontal`; **a session open RESETS ROI *and* exposure** ??the acquisition loop applies `tools/bench/camera_contract.py`. **No beads on the rig.**
?넅 **SAFE MOTION ENVELOPE = THE CONTROLLER LIMITS + the gate's command-class denies** (user, 2026-09-18 15:2x at the
rig). PI `SPA 1 0x15/0x30` ??TMN 0 / TMX 39 (RAM, **never WPA**) 쨌 **PI DIRECTION (user 2026-09-27 18:2x, at the rig): 0 mm = CEILING (magnet farthest from the sample, = the negative limit switch `FNL` goes to); larger mm = DOWN, toward the sample** ??so a reference move is the safe direction and any "magnet is low" report means a LARGE mm value 쨌 ASI `SL/SU` absolute mm X ??.8475??.1525, Y ??.7744?╈닋0.7744 (persistent, **never SS Z**),
written+verified by `py tools/motor_gate.py --session start|end` from the user-editable `tools/bench/motor_limits.json`; `--execute` refuses without the session file (tools/bench/motor_session.json, present ONLY while a session is open) **and** a fresh matching readback.
The gate still refuses ?ㅽ뿕以? every ASI home/zero/save, PI GOH/FRF/DFH/RON/POS/SPA/WPA and all rotor motion (self-test `selftest_motor_gate2.py` 85/85, 2026-09-24; FAIL-exit self-test 10/10).
rig-state: 議곕┰   <!-- 2026-10-07 ~15:xx USER (chat): "吏湲덉? ?ㅼ떆 ?ㅽ뿕 ?앸궓" ??back to 議곕┰ / not in use: LabVIEW allowed, motors only through motor_gate under the 2026-09-24 grant; main runner still stopped until the user says start. Previous: ?ㅽ뿕以???2026-10-07 USER (chat): "??30遺??ㅼ뿉 ?ㅽ뿕 ?쒖옉?댁뼱??吏湲??⑸럭 留뚯?硫??덈맖" ??no LabVIEW, camera, motor or ASI use until the user says the experiment is over; offline (LabVIEW-free) work only. Bench finished 13:18, LabVIEW verified closed, runner stopped. Previous: 議곕┰ ??2026-10-01 USER (chat): "?꾩옱??由ш렇 ?ъ슜?섏? ?딆쓬. 洹몃?濡?肄붾뵫 ?몄씠???뚮━?꾨줉. ?꾨쭏 ?ㅻ뒛 諛ㅼ젙???ъ슜?좎???紐⑤Ⅴ寃좊뒗?? 洹??뚮뒗 ?닿? ?ъ쟾??留먰븯?꾨줉 ?섍쿋??" ??back to 議곕┰: LabVIEW allowed, motors/ASI only through motor_gate inside the envelope under the 2026-09-24 grant (reference + limits verified), LabVIEW closed at every cycle end. The user will announce the next ?ㅽ뿕以?in advance (possibly tonight) ??graceful runner stop. Previous: ?ㅽ뿕以???2026-09-29 USER (chat): "怨??ㅽ뿕 ?쒖옉 ?덉젙?대씪 LabVIEW???ъ슜?섎㈃ ?덈맖. 洹??꾩뿉 ?⑸럭 臾닿??섍쾶 泥섎━ 媛?ν븳 ?꾨줈?몄뒪媛 ?덈떎硫??숈떆 吏꾪뻾?섎뒗嫄?愿쒖갖?꾨벏" ??no LabVIEW, no camera, no motor/ASI; offline (LabVIEW-free) work only. Runner stays stopped. Motor limits were already released at cycle 121 end. Previous: 議곕┰ ??2026-09-24 20:xx USER GRANT: "?밸텇媛??닿? 留먰븯湲??꾧퉴吏??紐⑦꽣 ?묒냽 ?덉슜?? ?ㅻ쭔 ?먯젏 ?뺤씤 諛?紐⑦꽣 由щ컠, ??媛吏??瑗??뺤씤 ?꾩슂" ??motors (PI, rotor, ASI) may be driven by the gate AND by a running main VI while the rig stays assembled, until the user withdraws it; PI reference + verify at session start and limits set/released with readback are never skipped; "?ъ씠??醫낅즺?섍퀬?쒕뒗 ?쒕?濡?LabVIEW ?꾨뒗寃??딆? 留먭쾬 (?뱁엳 移대찓?쇨? 怨꾩냽 Acquisition ?섎㈃ 湲곌퀎??醫뗭? ?딆쑝??" = runner end hook closes LabVIEW and verifies the process is gone. Earlier: 2026-09-23 14:2x user: "?ㅽ뿕 留덉묠. ?ㅼ떆 ?몄뀡 ?ㅼ뼱媛??臾닿??? ??rig stays assembled; motors/ASI only through motor_gate inside the envelope, LabVIEW allowed. Before: ?ㅽ뿕以?13:43 ("吏湲??ㅽ뿕以묒씠??) ??limits RELEASED and read back (PI 0..52, ASI 짹500, `tools/bench/motor_session_end_20260923c.log`), PI referenced at 0 (FNL, 13:36), servo on; no motor/ASI/camera/LabVIEW use until the user says otherwise. Earlier 13:3x, on the user's order ("?덇? ?쒕쾲 PI 紐⑦꽣 ?吏곸뿬蹂쇰옒? 0?쇰줈 ?대룞, 5珥??뺤?, 30?쇰줈 ?대룞, 5珥??뺤?, 0?쇰줈 ?대룞"): PI test moves through the gate to diagnose "PI doesn't respond to the main VI". Before that: ?ㅽ뿕以? restored 2026-09-23 13:11 after ONE `motor_gate.py --session end` on the user's order ("寃뚯씠?몃줈 ?댁쨾"): limits RELEASED and read back ??PI TMN 0 / TMX 52, ASI SL/SU 짹500 mm, position unchanged (`tools/bench/motor_session_end_20260923.log`). Set ?ㅽ뿕以?2026-09-23 12:3x on the user's words ("?닿? 怨??ㅽ뿕???쒖옉?섎땲 ??LabVIEW ?쒖슜? ?섏? 留먮룄濡?) ??no motor, no ASI, no camera, and NO LabVIEW use at all until the user announces otherwise. Previous: 議곕┰, set 2026-09-17 23:0x on the user's words ("?ㅽ뿕 1李⑤줈 ?앸궗?붾뜲, 由ш렇???좎??섎뒗 以? + "議곕┰ ?곹깭?먯꽌????踰붿쐞 ?덉씠硫?紐⑦꽣 ?덉슜??) 쨌 the gate's ONE machine-readable key, parsed by motor_gate.rig_state(); ONLY the user's announcement may set it to 遺꾪빐 / 議곕┰ / ?ㅽ뿕以? Keep it at the start of the line, unquoted. -->

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
?윟?윟 **CYCLE 148 ROUND 2 (hand-back 1 judged 2026-10-08; `tools/bench/next.json`, 11 items; `docs/d1/ring-p4c.md` PD359):** card 148-a1-1 drained fp-51..59: 8 fixes, each with a self-test that fails on the old code, and fp-55 closed as not a false positive. The fp-56 pin is 5708c2d6 because the gate hashes the file without its header; that is accepted. The round was handed back because of card "p1s-A", which is a FIXTURE of `tools/bench/selftest_chat_p1.py:113`, not a real card. The working cause: the self-test passes the assignment session's `ASSIGN_STATE` to `guard_assign`, which then writes into the LIVE state. This is logged as fp-60. **First act = ONE card, ALONE: measure the leak on a throwaway COPY of a state file, then fix it.** The fix drops those env vars in self-tests that spawn guard_session/guard_assign, and `tools/hooks/guard_assign.py` makes hand-backs only for cards under `tools/bench/cards/`. A new self-test must fail on the old code and pass on the new. **Then:** re-pin T0b in `selftest_c147_b1_2.py` (17/0) ??run the prepared `task_148-a1-2.json` (stagekit plain run, 7 x10 tests, t3_regress and 4 suites compared with pre-fix; "green" = rc 0 or same as pre-fix) ??s06 DIFF-ONLY prior-art review ??ONE s06 scratch ??adopt + `load_by_vi`; s07 offline prep beside it.
(round 1) ?윟?윟 **CYCLE 148 PURPOSE (judgement 2026-10-08; `tools/bench/next.json`, 11 items; `docs/d1/ring-p4c.md` PD358):** cycle 147 round 3 met items 0?? (case-J stub fixed, COM blocked 51/0; licence `renames` 5 ??7f70bbf9; build recipe on the new gate API d947df5d; both s06 recipes dry + prerun PASS) and handed back because two gate refusals of one class (fp-56, fp-59) stopped it before any LabVIEW run. **First act = ONE tooling card, ALONE: drain gate-fp fp-51..59** (fp-56: `tools/stage_prerun.py` exempt pin for `selftest_stagekit.py` ??sha256 0007d034?? fp-59: `tools/hooks/guard_cycle.py` re-run glob; fp-55 is not a false positive, PD357(d); the edits are authorised by the purpose) and re-pin `selftest_c147_b1_2.py` P0 (licence 7f70bbf9, recipe d947df5d). **Then** the DIFF-ONLY prior-art review of the s06 scratch recipe is PAID (card peers include `priorart`, not exempted), then ONE s06 scratch on a new byte copy of s05 3f9ac26b (ops 1..21) ??adopt as `D1_ring_p4s06_*.vi` + full EL + fresh load + graph read + `load_by_vi`. Beside the s06 LabVIEW card, ONE offline card prepares session 7 (provisional, then `--rebase` on the real s06 graph; not launched).
(history) ?윟?윟 **CYCLE 147 HAND-BACK 2 JUDGED (2026-10-08; `tools/bench/next.json`, 12 items; `docs/d1/ring-p4c.md` PD357, new topic file):** round 2 finished the re-score (D/TD/PB ALL PASS on the stored s06 read, w23807 = deleted + reused, REUSE-NOTED) and the stagekit gate fix (06b8d844, own self-test 17/0, default path verbatim). It handed back because the older `selftest_stagekit.py` J1 fails on the new stagekit: case J's stub misses `create_local_read` (`stagekit.py:794`, outside the diff, there since cycle 102), so the test made one real COM call (5507). Judged a pre-existing stale stub, **to be measured first: the prepared card `tools/bench/cards/task_147-b1-4.json` (pre-edit vs new, COM blocked, per-check compare) ??then fix the case-J stub only ??licence `renames` (5) ??`stage_d1_ring_p4_s06v18.py:127,139-144` on the new gate API ??dry + prerun ??ONE s06 scratch (new RETRY_CARD, new copy of s05 3f9ac26b) ??adopt + `load_by_vi`.** fp-55 is not a false positive (the selftest imports stagekit ??gscript; run it under `labview: read`).
(history) **CYCLE 147 HAND-BACK 1 JUDGED (2026-10-08; 13 items; `docs/d1/ring-p4b.md` PD356):** the s06 retry (147-a1-8) built the RIGHT graph: SG PASS, E1 real == sim at every op, and the end wiring == the sim's end. It was not adopted because D/TD/PB failed on their KEYS (review `archive/peer/2026-10-08-c147-a1-8-re1.md`): ops 3/4/5/18 renamed #2626 2832/4160/4165 'array'??element' and #9503 9505/9508 'Value'??' (same uids, owners, wires), and LabVIEW reused wire uid 23807 on the same source. **First act = ONE offline card: re-score D/TD/PB on the stored `tools/bench/diag_c147_p4s06v18_scratch.json` with name-free keys (all PASS, else return), quote w23807's base vs end sinks, explain PB's 4-vs-3.** Then, ALONE: the stagekit gate fix (licence-listed renames only, REUSE-NOTED for a reused deleted wire uid), plus self-tests. Then the 5 renames go into the s06 licence, dry + prerun run, ONE more s06 scratch under a new RETRY_CARD on a new copy of 3f9ac26b, and adopt + `load_by_vi`. P6 obligation: #2626 inputs read back 'array'. ?좑툘 `ring-p4b.md` is at 399/400 lines: the next PD opens `docs/d1/ring-p4c.md`.
(resume) ?윟?윟 **CYCLE 147 RESUME (judgement 2026-10-08 after the user's "?ㅼ떆 ?쒖옉."; `tools/bench/next.json`, 8 items, same PD355 work):** round 2 was killed at 02:42 by the app restart, partway through offline card 147-a2-1. It left `tools/recipes/stage_d1_ring_p4_s06v18.py` (7e0edcf8, 02:42:36) with the sink-gate code mostly written and `_scratch.py` (31009bfc) asserting it. Neither has a compile, dry run or prerun on these bytes. **First act = ONE offline card: finish and verify that edit to `tools/bench/cards/brief_147-a2-1.md` (py_compile, both dry runs, prerun, `check_sink_gates` length 1; stagexec/gscript md5 unchanged).** Then the round-2 sequence below, unchanged: the s06 retry scratch on a new byte copy of 3f9ac26b ??adopt ??s06 `load_by_vi`.
(round 2) ?윟?윟 **CYCLE 147 ROUND 2 (hand-back 1 judged 2026-10-08; `tools/bench/next.json`, 5 items; `docs/d1/ring-p4b.md` PD355):** round 1 met 8 of 9 items. **s05 is ADOPTED** (`claudeDev\D1_ring_p4s05_20261008_002621.vi`, 3f9ac26b, EL 55, load 606.7 MB in `load_by_vi`). The s06 maker gate is done, s06 is rebased on the real s05 graph, the scratch EL step is advisory, the runner's retro-undisposed entry and gate-fp fp-53 are written. The ONE s06 scratch ran ops 1..20 clean and stopped IN op 21 (`p4_rbA_re1`): `gscript.wire_indicators` raises "target BROKEN after wiring" whenever the target's ExecState is not 1 (`tools/gscript.py:2152-2155`), and every P4 bed is ExecState 0 by design. The s06 plan declared no sink gate (scratch log :310). The review `archive/peer/2026-10-08-c147-a1-4-re1.md` agrees. **Decided (PD355):** add ONE recipe-owned sink gate for `[23166, 'Pos within cal image']` (it reads back the net shared with #5058 'pos in cal image out'), with no stagexec/gscript edit and no re-cut. **First act = re-issue the s06 scratch with that gate under a RETRY_CARD, from a NEW byte copy of s05 3f9ac26b (a full rerun, not a resume of b58046e3)** ??adopt by PD354(a), full EL recorded, fresh load + graph read, s06 load into `load_by_vi`. Calibration note: metered start 570.2 vs assumed 612.6 MB.
(round 1) ?윟?윟 **CYCLE 147 PURPOSE (judgement 2026-10-08 01:16; `tools/bench/next.json`, 9 items; `docs/d1/ring-p4b.md` PD354):** cycle 146 closed with nothing adopted. Its round-3 card 146-a3-1 showed that no carry rule gets elrule to s05 = 55 per class: the base SubVI #5058's requiredness was never measured. The retrospective (`archive/peer/2026-10-08-retrospective-cycle146.md`, now disposed) is right: the Error List predictor blocked four passing sessions in a row. **Decided (PD354, violation decision 2026-10-08 01:16): the Error List is now a RECORDED cross-check, not an adoption gate.** The scratch recipe prints `EL-ADVISORY` and returns only on a class seen in neither the start read nor the prediction, or a total off by more than 3. elrule is NOT patched (V1/V3/VX declined). **First act = LabVIEW card: ADOPT the s05 work copy `claudeDev\D1_ring_p4s05_20261008_002621.vi` (3f9ac26b) with no rerun** (scripts `tools/bench/diag_c146_a1_4_adopt.py`/`_mkgraph.py`/`_graph.py`/`_t2626.py`): full final EL = expected file, fresh load + graph read, the measured load written into `memory_model.json` `load_by_vi` (that entry only; limits unchanged). Beside it, offline: the s06 maker gate allows branch?뭖onnect for an earlier-session source (PD353(e)). Then s06 is rebased on the real s05 graph (PD353(f), current elrule), followed by ONE s06 scratch ??adopt. Offline, any time: `cycle_runner.py` writes a `retro-undisposed` gates_due entry (device-failed decision), plus one gate_fp entry for the 146-a2-1 refusal.
(round 3) ?윟?윟 **CYCLE 146 ROUND 3 (hand-back 2 judged 2026-10-08; `tools/bench/next.json`, 8 items, same PD353 work):** round 2 ran no card. `guard_assign` refused card 146-a2-1 before dispatch because its pass line listed `memory_model.json` as UNCHANGED, and the guard read the name next to the word "changed" as a limit change (`tools/hooks/guard_assign.py:321-328`). **Judged a false positive.** The purpose now says outright that `memory_model.json` is READ-ONLY this cycle (no card writes it; cards may list it as an invariant), and the refusal is logged as one gate-fp entry, with no hook edit this cycle. **First act = re-issue 146-a2-1 as written (the elrule carry fix, ALONE)**, then the round-2 sequence below, unchanged.
(round 2) ?윟?윟 **CYCLE 146 ROUND 2 (hand-back 1 judged 2026-10-08; `tools/bench/next.json`, 6 items; `docs/d1/ring-p4b.md` PD353):** round 1 drained gate-fp fp-43..50, recorded 605.4 in `load_by_vi`, re-cut s05 to v18 ops 98..114 (X10 674.9), and ran ONE s05 scratch: **22/0, real == sim at all 17 ops, peak 607.7 MB**, saved `claudeDev\D1_ring_p4s05_20261008_002621.vi` (3f9ac26b), NOT adopted because the Error List read 55 vs pred 57. **Judged: our predictor, not the build (PD353(b))** ??`tools/elrule.py:225` passes no `carry`, so 2 base items that s05 closes ('Image In' #5058, IA #29843) stayed counted. s06 prep stopped on the maker's own kind gate (op 116 compiles `connect`, not `branch`, because its source tunnel was made in s05; same wire net). **First act = ONE offline card ALONE: fix the elrule carry; self-test s01..s04 51/53/55/58 unchanged and s05 = 55 PER CLASS equal to the read file (06a59001).** Then ADOPT 3f9ac26b with no rerun (scripts `tools/bench/diag_c146_a1_4_adopt.py`/`_mkgraph.py`/`_graph.py`/`_t2626.py`), fresh load + graph read, load into `load_by_vi`. Then the s06 maker allows branch?뭖onnect for an earlier-session source, s06 is re-made on the real s05 graph (X10 at the measured load, #2626 licence), and ONE s06 scratch runs ??adopt.
(round 1) ?윟?윟 **CYCLE 146 PURPOSE (judgement 2026-10-07, `tools/bench/next.json`, 8 pass items; `docs/d1/ring-p4b.md` PD352):** cycle 145 PURPOSE_MET accepted. **P4 session 4 ADOPTED** as `claudeDev\D1_ring_p4s04_20261007_215031.vi` (95e408ff, EL 58, load 605.4 MB). The two subVIs' inputs are Recommended, which explains EL 58, and elrule is fixed (21/0). **First act = ONE tooling card, ALONE: drain gate-fp fp-43..50** (fp-43/45/47/48/49/50 are one class: `guard_write.py:84` stale-pin on a card's own authorised edit; fp-44 and fp-46 are `guard_peer`). These hook edits are authorised by the purpose. **Then s05 is RE-CUT** (PD352(b)): X10 now has ONE start rule, measured load + op-0 read, so 605.4 goes into `memory_model.json` `load_by_vi`. That is a record only; the limits stay. The cut is the longest group-respecting prefix from op 98 with X10 ??680, about op 116; the old cut at op 120 also failed under the gate's own rule (review `c145-s05-x10`, disposed). If the cut still carries ops 118/119, it gets a uid-keyed `pb-licence/1` for Build Array #2626 (PD352(d)). **Then ONE s05 scratch** on a byte copy of 95e408ff ??adopt on full PASS + full EL + fresh load + graph read, recording the metered start for the deferred X10 recalibration (PD352(c)). Beside it goes the s06 prep. Housekeeping: copy the OpWiringRules hygiene record into `tools/bench/op_hygiene/`.
(round 2) ?윟?윟 **CYCLE 145 ROUND 2 (hand-back 1 judged 2026-10-07 22:3x; `tools/bench/next.json`, 6 items; `docs/d1/ring-p4b.md` PD351):** round 1: 145-a1-1 stopped at op 10 (the SQ1 subVI row in the plan was provisional), 145-a1-2 fixed the row (plan f349c39a) and its s04 scratch ran **24/0, peak 619.3 MB**, saved `claudeDev\D1_ring_p4s04_20261007_215031.vi` 95e408ff; the Error List read 58, pred 60. **Judged EXPLAINED (PD351(b)):** every class matches except the two SubVI drops (PS1, SQ1), which produce no "required input" item. Working cause: their inputs are not Required, and round 2 measures this. **First act = ADOPT 95e408ff** (adopt_scratch ??`D1_ring_p4s04_*.vi`, EL expected file, fresh load + graph read) + read the pane requiredness of `RingPickSlot_v0.vi` / `RingSeqCheck_v0.vi` (an unwired Required input = return). Then, ALONE, fix `tools/elrule.py` (SubVI counts Required inputs only; 51/53/55/58). Then re-make s05 (v18 ops 98..124) on the real s04 graph: X10 at the measured load, then dry + prerun. **No s05 launch:** X11 (Build Array #2626 open row, licence names only plan_l2b1) is for the next judgement, and the card reports its facts. Delete the stopped copy abb76d41. Open, not due: gate-fp fp-43/44/45/46.
(round 1) ?윟?윟 **CYCLE 145 PURPOSE (judgement 2026-10-07, `tools/bench/next.json`, 6 pass items; `docs/d1/ring-p4b.md` PD350):** cycle 144 PURPOSE_MET accepted ??**P4 session 3 ADOPTED** as `claudeDev\D1_ring_p4s03_20261007_202957.vi` (282301ca, EL 55 == pred, load 598.5 MB, graph `graph_ring_p4s03_20261007_205535.json`). **First act = ONE scratch of session 4** (`tools/bench/plan_ring_p4_s04v18.json` 9ff46b0e, rebased on the real s03 graph; pred `plan_ring_p4_s04v18_pred.json` 90eff870, **EL 60**; recipes `tools/recipes/stage_d1_ring_p4_s04v18.py` fe3f630c / `_scratch.py` f5e4bdf8, dry + prerun 16/0, `--scratch-required` rc 3) on a byte copy of the s03 file; full PASS ??adopt as `D1_ring_p4s04_*.vi`, full EL, fresh load + graph read. X10 680.1 vs 680 (??.1 MB) ACCEPTED by PD350(b): the scratch's 680 MB stop is the guard; a stop ??re-cut to ops 79..96. Beside it ONE offline prep card: session 5 (v18 ops 98..), rebased on the real s04 graph if s04 is adopted. Open, not due: gate-fp fp-43/44/45.
(cycle 144 round 2) ?윟?윟 **CYCLE 144 ROUND 2 (hand-back 1 judged 2026-10-07 20:25):** round 1 delivered 144-1 (pred EL 55, dry + prerun on current bytes) and 144-P1 (s04 provisional plan 3353cfc4); 144-2's s03 scratch was refused before LabVIEW by `guard_cycle`, because two violation decisions were owed. Both are now written in `docs/violation-decisions.md` (repeated-failure-class = device already built, PD334/335 + PD347(b); device-failed = stop_record repaired by chat-E3, its replay on `material_marker.log:3332/:3333` still owed). `violations.py`: 0 awaiting. fp-41 DRAINED. Round 2 (`next.json`, 6 items): re-issue 144-2 unchanged; then, ALONE after it, ONE tooling card that edits `tools/hooks/guard_peer.py` for fp-34 (authorised by the purpose) and replays the two stop-record commands. fp-43 (guard_write stale-pin on a card's own write) is open, not due.
(round 1) ?윟?윟 **CYCLE 144 PURPOSE (judgement, `tools/bench/next.json`, 5 pass items) = the act below, plus: (a) the s03v18 scratch recipe's bytes changed since its prep (now fa6423ab, was 573b8537 ??chat-T5) ??dry + prerun both recipes on the CURRENT bytes before the scratch; (b) gate-fp fp-34 + fp-41 are DUE ??ONE tooling card drains them, run ALONE (it edits stage tools ??never beside the LabVIEW card); (c) new Pre-decided items go to `docs/d1/ring-p4b.md` (P4) or a NEW short tooling topic file (`docs/d1/tooling.md` is at 399/400).**
?윟?윟 **FIRST ACT of cycle 144 = P4 SESSION 3 LabVIEW card (`labview: build`, `gui: true`; `docs/d1/ring-p4b.md` PD336(a); plan of record `docs/d1/INDEX.md`):** ONE scratch of `tools/bench/plan_ring_p4_s03v18.json` (da66a030 = v18 ops 59..78, 20 actions, rebased on `graph_ring_p4s02_20261003_112505.json`, X10 676.4 ??680 at 596.0, prerun 16/0, prior-art NOVEL) with `tools/recipes/stage_d1_ring_p4_s03v18_scratch.py` (573b8537) on a BYTE COPY of `claudeDev\D1_ring_p4s02_20261003_110001.vi` (84cac487 ??the adopted session-2 file); predictions: all gates PASS, peak ??680 (MEMSTOP 695), **Error List 55** (CHAT 2026-10-07: rule replaced by PD349 / card chat-T5, `tools/bench/selftest_elpred.py` 15/0; the pred 7fab8cf0 still says 56 - regenerate its EL block first); a third value or a refusal on `new:LRB1.value`/`new:LWB1.value` is a RETURN (fix = measured-name rule PD335(b)). Full PASS ??ADOPT (PD329(a); `stagexec.adopt_scratch` by import ??the CLI form is refused under `labview: none`, fp-39), full Error List + expected file, fresh-instance load + graph read. Beside it ONE offline prep card: session 4 = v18 ops 79.. (starts with the PS1 subVI drop), provisional on stagesim's end of s03, made like `tools/bench/prep_c143_p1_mk.py`, EL by the fixed rule, recipes copied from the s03v18 pair. Carries: gate-fp queue fp-34/36/37/38/39 (fp-38: `git add` naming recipes refused by the stop_record gate; sub-agents cannot `git add` ??the runner's cycle-end commit carries cycles 142??43's files); `gscript.for_loop` junk constants (per-caller delete); relocate the cycle 131??39 briefs out of STATUS.
- **CYCLE 143 in brief ??P4 SESSION 2 ADOPTED (in-between file); session 3 launch-ready; three tool/predictor defects closed:**
  - 143-1 FAIL 3/1: prior-art r3 NOVEL (r1/r2 FIXED); scratch 21/0, peak 620.3 (X10 678.5), saved `D1_ring_p4s02_20261003_110001.vi` 84cac487; Error List 53 ??51/52. 143-P1/P2 (offline): session-3 plan (v18 ops 59..78) + recipes, prior-art NOVEL.
  - 143-2 PASS 5/0: graph read (load 596.0); the 2 extra items = 1.2 loop `#10170` stop terminal + StopAll read Local `#6902`, both open in the sim end and wired by s03's first action; hypothesis review: our EL predictor bug (PD333).
  - 143-3 FAIL 13/1: s02 ADOPTED, expected EL 53, EL rule fixed (s02 ??53, s01 ??51); rebase refused UID-REUSE #23276. 143-4 FAIL 5/1: rebase-path raw-uid keys fixed (census 19 sites, 4 fixed; named re-issue refuses, else REUSE-NOTED) (PD334??35).
  - 143-5 FAIL 2/2: s03 address `value` ??measured `StopAll`, rebase PASS (da66a030); our pred script scanned `why` text. 143-6 PASS 8/0: X10 676.4, EL 56, dry + prerun 16/0 both recipes (PD336).
- (history) ?윟?윟 **FIRST ACT of cycle 143 = P4 SESSION 2 (plan v18, WITH the two subVIs) LabVIEW card (`labview: build`, `gui: true`, peers `priorart`; `docs/d1/ring-p4b.md` PD332(d); plan of record `docs/d1/INDEX.md`):** (1) prior-art review of `tools/recipes/stage_d1_ring_p4_s02v18.py` (owed ??not a proven pattern); (2) ONE scratch of `tools/bench/plan_ring_p4_s02v18.json` (e941ebbf = v18 ops 25..58, 34 actions: the 26 remaining slot-write repair actions + the first reader actions; rebased on `graph_ring_p4s01_20261002_234419.json`, dry PASS, prerun 16/0, X10 678.5 ??680) on a byte copy of `claudeDev\D1_ring_p4s01_20261002_232547.vi` (dc61e193) with `tools/recipes/stage_d1_ring_p4_s02v18_scratch.py`; the scratch is REQUIRED (census unpredicted, `--scratch-required` exit 3) and its measured census is the prediction; Error List 51 or 52 (#23166 newly unwired), a third value is a return; (3) every gate PASS ??ADOPT the scratch as `D1_ring_p4s02_*.vi` (PD329, no second run), full Error List, load + graph read in a fresh instance. Beside it ONE offline prep card: session 3 = v18 ops 59.. provisional on stagesim's end of s02v18 (`--rebase` after the adoption). Plans `plan_ring_p4_s02.json` (v17) and `plan_ring_p4_rasrest.json` are SUPERSEDED ??never launch them. Carries: gate-fp fp-36 (guard_peer lacks the reverse of RULE-OFFLINE-CARD), fp-37 (`--scratch-required` plain form refused by guard_cycle); `gscript.for_loop` leaves 3 junk constants per call (per-caller delete, `docs/toolkit-capabilities.md:60`); sub-agents' `git commit` is refused by the permission layer ??cycle 142's files are uncommitted; relocate the cycle 131??39 briefs out of STATUS.
- **CYCLE 142 in brief (ONE trial cycle, user 2026-10-03) ??P4 re-planned WITH SUBVIs; BOTH subVIs DELIVERED and RUN; session 2 launch-ready:**
  - 142-1 FAIL 9/1, 142-2 FAIL 16/1 (our build script: per-delete count after a For delete; then a terminal looked up by its diagram owner) ??142-3 (escalation 1, Opus max) PASS 87/0: `claudeDev\RingPickSlot_v0.vi` 6fcf153f (smallest Num > last), 7/7 vectors == reference, fresh-instance re-run equal (PD330, PD331(a)).
  - 142-4 PASS 121/0: `claudeDev\RingSeqCheck_v0.vi` 0295a8d3 (valid = n1==n2 AND n1>last; next last; next discards), 7/7 + fresh re-run (PD331(a)).
  - 142-P1 (offline): decomposition table of v17 ??2 subVIs worth making; rollback Selects and single Index Arrays stay bed primitives (PD330). 142-P2 PASS 13/0: plan v18 2ea6cafa, 202 actions (was 235), end cdiff == v17 (PD331(b)). 142-5 PASS: rebind key (uid, owner, name) 4/0; session-2 plan s02v18 ready (PD332).
- (history) ?윟?윟 **FIRST ACT of cycle 142 = P4 SESSION 2 build card (LabVIEW, `labview: build`, `gui: true`; `docs/d1/ring-p4b.md` PD326(e); plan of record `docs/d1/INDEX.md`):** (1) `py tools/stage_prerun.py --rebase tools/bench/plan_ring_p4_s02.json --graph tools/bench/graph_ring_p4s01_20261002_234419.json` (s02 5e483ea6 = v17 `plan_ring_p4_v17.json` e19d7e14 ops 25..54, provisional on stagesim's end of s01); (2) X10 at start **596.5** (measured load of the session-1 file, PD320(d)) must be ??675, else re-cut by PD320(c) before any LabVIEW; regenerate the pred, dry + prerun both recipes `tools/recipes/stage_d1_ring_p4_s02.py` / `_scratch.py`; (3) ONE scratch on a byte copy of `claudeDev\D1_ring_p4s01_20261002_232547.vi` (dc61e193 ??the INPUT of session 2; the bed key stays on P3b-2b); (4) launch only if every gate PASSes (prim + TD by (uid, owner, name)), EL == pred, scratch peak ??675 ??`D1_ring_p4s02_*.vi`, full EL, load + graph read in a fresh instance. Beside it ONE offline prep card: session 3 provisional on stagesim's end of s02. Carry (PD326(d)): stagexec binding compares raw `term_uid` sets (`stagexec.py:946-950`) ??fix only if a scratch fails there. X10 recalibration after session 2's measured peak (PD326(c)). After the deliverable cards: relocate the cycle 131??39 briefs out of STATUS (154 lines).
- **CYCLE 141 in brief ??P4 SESSION 1 DELIVERED (in-between file); slot-write repair under way; prim gate built:**
  - 141-1 PASS 6/0 (offline): prim gate run-time (`stagexec.py:435-461`) + offline X17, self-tests 13/0; X10 refuses a provisional base (4/0); v16 36981c83 = 50 repair actions (create-first order, PD324(b)) + v15; 11 sessions by X10.
  - 141-2 FAIL 24/1 (LabVIEW scratch): real == sim, prim gate 3/3 Replace Array Subset, peak 601.4; gate TD keyed on raw uids that LabVIEW re-used after deletes (review c141-2-scratch-td) (PD325). 141-P1 PASS 29/0: v17 e19d7e14 (`p4_eq_seq` donor #10019), s02 provisional.
  - 141-3 PASS 6/0: `stagekit.term_identity_gates` (9/0); scratch 23/0, launch 23/0 ??`claudeDev\D1_ring_p4s01_20261002_232547.vi` dc61e193, EL 51 OK, peak 605.0, graph read 596.5 MB load (PD326). `docs/d1/ring-p4.md` frozen; P4 decisions continue in `docs/d1/ring-p4b.md` from PD323.
- (history) ?윟?윟 **FIRST ACT of cycle 141 = ONE offline card, ALONE (it edits stage tools; `docs/d1/ring-p4.md` PD322; plan of record `docs/d1/INDEX.md`):** (1) the created-node PRIM GATE (PD322(d)): stagekit/stagexec compare every created node's read-back label/class with the plan's declared prim and FAIL on mismatch; self-test includes the 140-3 case (#29489 'Insert Into Array' declared 'Replace Array Subset'); (2) P4 plan v16 = `tools/bench/plan_ring_p4_v15.json` (eb4ffb6e) with FIRST the repair of the five bed slot-write nodes that are Insert Into Array (`#27928`, `#28916`, `#29048`, `#29265`, `#29316`; census `tools/bench/diag_c140_4_facts.md`): each deleted and re-created from `claudeDev\DonorRAS1D_v0.vi` (e8a9417c, Replace Array Subset uid **175**, terminals array t182 / output array t185 / new element/subarray t188 / index t191, run-verified `tools/bench/diag_c140_5_facts.md`), every old source and sink reconnected by terminal uid (`#29048/#29265/#29316` share index wire w28367; remember 140-2's 1055 = RLE on a wire whose only sinks were deleted ??delete such wires first, PD321); `p4_ras_bufdiff` donor ??uid 175; replay END, end cdiff == v15 + the 5 swaps; (3) session table re-cut by PD320(c), session-1 plan FINAL + recipe dry/prerun/X10, Error List predicted ONE item per created node with an unwired input (PD322(e)). Then a LabVIEW card: session-1 scratch on a bed byte copy ??launch only if every gate PASSes + EL == prediction + scratch peak ??675 ??load + graph read of the in-between file (PD320(e)); then session 2 by `--rebase` (140-P1's cut ops 17..31 is stale once v16 prepends the repair). **Carries into that offline card (review c140-2-failed-logs, retrospective-cycle140):** X10 must REFUSE (not fall back to 570 MB) on a provisional base (`stage_prerun.py:1997-1998`); the scratch recipe's `x10()` takes its limit from the md5-pinned pred file, not the last log line; `--scratch-required` rc 3 is not a failure (gate-fp fp-34); recalibrate X10's high bias (140-3: 615.5 measured vs 673.4) before the re-cut. After the deliverable cards: `docs/d1/ring-p4.md` is 429 lines > 400 ??freeze it and open `docs/d1/ring-p4b.md` from PD323; relocate the cycle 131??39 briefs out of STATUS.
?뵶 **FOR THE USER (report it): every ring slot write built in P3b-1/P3b-2 is an Insert Into Array (lengthens the 20-slot arrays each frame) where the ring design says Replace Array Subset ??our donor mistake since cycle 131, found by the 140-3 review; the bed is being repaired toward the design, no decision needed.** Cycle 141: 2 of the 5 are now Replace Array Subset in the session-1 file (the 3rd is half-done, the rest follow in session 2), and a new check stops the build whenever a created node is not the function the plan asked for.
- **CYCLE 140 in brief ??P4 sessions cut by memory; a computation defect found in the bed; 1-D Replace Array Subset donor built and run; no new work VI:**
  - 140-1 PASS 7/0 (offline): X10 formula reproduces 750.7; table A 9 sessions, B 8 (bind merge needs a binder edit ??not built, PD320).
  - 140-2 FAIL 2/1: session-1 scratch op 3 RLE w23255 ??error 1055 (wire wholly removed); 140-P1 FAIL 13/1: session 2 = ops 17..31 (674.6), dry only after rebase (PD321).
  - 140-3 FAIL 4/1: v15 eb4ffb6e (delete_wire w23255 first) scratch PASS 19/0, peak 615.5 MB; Error List 52 ??51 ??review c140-3-el52: the new node is Insert Into Array; 140-4 census: 0 of 6 ring slot writes are the intended Replace Array Subset (PD322).
  - 140-5 PASS 22/0 (2nd attempt; 1st = our script used the nested-diagram control route on a top-level node): `claudeDev\DonorRAS1D_v0.vi` uid 175, ExecState 1, run 0..19 / index 3 / 99 ??len 20, [3] = 99.
- (history) ?윟?윟 **FIRST ACT of cycle 140 = ONE offline measurement card (`labview: none`; `docs/d1/ring-p4.md` PD319(c); plan of record `docs/d1/INDEX.md`):** (1) the X10 session table of the WHOLE P4 plan `tools/bench/plan_ring_p4_v14.json` (22f58271, 185 actions; meta `plan_ring_p4_v14_meta.json`): dependency-closed prefixes, each predicted ??675 MB (FAIL 690) at start 606.1, per session first/last action id, ops, reads, peak; (2) of the step-1 plan `tools/bench/plan_ring_p4s1.json` (e6992800, FINAL, 39 actions, R 29 BIND reads, X10 750.7 ??`tools/bench/diag_c139_7_facts.md`), how many BIND reads could share one whole-VI read placed before the bound uid's first use, and the resulting R/peak. No tool edit. Then judgement picks the session cut (and whether a bind-merge tool is worth building), then the FIRST P4 session: its plan, dry/prerun/X10, ONE scratch run on a bed byte copy (recipe `tools/recipes/stage_d1_ring_p4s1.py` + `_scratch.py` as base), then its launch saving an in-between file. P4 = one counted broken file at its end (CLAUDE.md "Big or blocked work" item 2: user answered D-2026-10-02-02 "?몄? ?딄린" / -04 "???듭뀡" ??the decisions file may still show them open; ask the chat to close them, never re-word them). Carries: re-pin `selftest_c133_1_fsroutes` / `selftest_c133_6_fr` on frozen fixtures; `docs/toolkit-capabilities.md` rows for OpStopMode ops and the new base-loop `stop` route (`stagexec.base_cond`); `loop_in`'s For/While route needs a SubVI somewhere in the VI (PD314(d)); sim step dirs `tools/bench/sim/ring_p4_v2..v14/` not deleted. Open user decision: D-2026-10-02-01.
- **CYCLE 139 in brief ??P4 plan v14 complete and routable; first build step refused by the memory model; no new work VI:**
  - 139-1 FAIL 8/2 (LabVIEW scratch): Error List item 52 after `delete_wire` w25415 = "Case Structure: Unwired selector" (#10465, re-wired at once by the plan); For group not built ??our scratch lacked a SubVI that `loop_in` needs (PD314).
  - 139-P1 PASS 24/0 ??v10 (regenerated fs_routes); 139-P2 PASS 23/0 ??v11 (StopAll born on a False constant on #4866, written in #639 by local); 139-2 PASS 5/0 ??gate-fp fp-31 drained (report_gate reads older runner logs too).
  - 139-3 PASS 38/0 (LabVIEW scratch): `claudeDev\DonorBoolF_v0.vi` uid 126; For-loop min group inside a While MEASURED (IndexMode 1 횞3, ExecState 1, runs 3 / 2147483647) (PD315).
  - 139-4 FAIL 19/2 ??v12; 139-5 FAIL 3/2 but the TOOL PASSED: stop onto an EXISTING loop's cond (`stagexec.base_cond`, `stagesim.cond_target`, self-test 13/0) ??v13 0 UNROUTABLE (PD316??17).
  - 139-6 FAIL 2/1 ??v14 (steps stepped; step 2 = 43); 139-7 FAIL 7/1: step-1 plan FINAL but X10 750.7 > 690 (29 BIND reads) ??sessions cut by X10 (PD318??19). Reviews disposed: c138-6-p1cmp-routes, c139-3-hyp-c139-1.
- (history) ?윟?윟 **FIRST ACT of cycle 139 = TWO cards in ONE message (`docs/d1/ring-p4.md` PD313(e); plan of record `docs/d1/INDEX.md`):** (1) LabVIEW card (`labview: build`, `gui: true`, `run_vi` for the scratch VI only, bed never edited) = rerun 138-6 step 2 with the group INSIDE a While body as v8 has it (For + 3 auto-index tunnels with IndexMode read back, scalar Select whose f = `claudeDev\DonorI32Max_v0.vi` constant uid 127, Array Max & Min; ExecState 1; one run: Num=[-1,5,3,9,??, last 2 ??3, all ??last ??2147483647) + a FULL Error List read of a bed byte copy after `delete_wire` w25415 naming item 52 (script `tools/bench/diag_c138_6_run.py` as the base; facts `tools/bench/diag_c138_6_facts.md`); (2) offline card (`labview: none`, plan files only) = v10 = `tools/bench/plan_ring_p4_v8.json` (059b5296) + StopAll writer (as v9's `p4_i_stopall`) + StopAll := False on FS1 frame `#4866` (PD313(d)) + KMX1/KMX2 bound to uid 127 + IndexMode recipe gates (`tools/bench/plan_ring_p4_v9_recipe_gates.json`), with `finalized.fs_routes` REGENERATED, never copied (PD313(c)); replay + `compile_plan` + route compare v8?뭭10 (changes only on added/edited actions); write the disposition of review `archive/peer/2026-10-02-c138-6-p1cmp-routes.md`. Then: the 17-class scratch route run (PD303(c)), then P4 build sessions. Carries: re-pin `selftest_c133_1_fsroutes` / `selftest_c133_6_fr` on frozen fixture copies (stale at HEAD, `tools/bench/prep_c138_3_facts.md`); `docs/toolkit-capabilities.md` rows for OpStopMode ops; sim step dirs `tools/bench/sim/ring_p4_v2..v9/` not deleted. Open user decisions: D-2026-10-02-04, D-03, D-02, D-01.
- **CYCLE 138 in brief ??simulator and memory-check tools fixed; P4 plan v8 accepted; stop (end) measured as a latch; no new work VI:**
  - 138-1 FAIL 5/1 (offline): stagesim FS-exit row from U6??(14/0), `delete_wire` row-loss fix (cause: `Tunnel` in `DROP_WHEN_UNWIRED`), stagexec `fs_exit` route, c125_1 6/0, v7 replay END 172/172. The 1 FAIL = two stale self-test fixtures, red at HEAD (138-3 PASS).
  - 138-2 PASS 5/0 (offline): X10 counts whole-VI reads from the script SOURCE (12/0); `diag_c136_1_routes` now FAILs at 806 MB (dry count said ~670); P3b-2 a/b still PASS (PD312(a)).
  - 138-4 PASS 5/0 (offline): v8 059b5296 = 181 actions, For + scalar Select + Array Min, compile 163 ops, replay END; prior-art released (FIXED IndexMode, REFUTED const_row) (PD312(b)(c)).
  - 138-5 PASS 5/0 (LabVIEW): ops `OpStopMode_v0` / `OpStopModeB_v0`; all bed While loops Stop-if-True; `stop (end)` Mechanical Action 4 (PD312(d)).
  - 138-6 FAIL 23/1 (LabVIEW scratch): `DonorI32Max_v0.vi` uid 127 I32 2147483647; `#10465` survives delete_wire (EL 51??2); latch + local breaks the VI (confirmed); For-group step stopped on our script (top-level placement) (PD313(a)(b)).
  - 138-P1 FAIL 19/1 (offline): v9 b91cf4d7 rejected ??the maker copied a position-indexed `fs_routes` table, so 3 untouched wires changed route; StopAll needs an init (PD313(c)(d)).
- (history) ?윟?윟 **FIRST ACT of cycle 138 = ONE offline TOOLING card, ALONE (no LabVIEW card beside it ??it edits stage tools; `docs/d1/ring-p4.md` PD311(e), plan of record `docs/d1/INDEX.md`):** (1) `tools/stagesim.py` gets an FS-frame EXIT row modelled on the MEASURED U6??(`tools/bench/diag_c137_7_types.log:290-306,317,328`: tunnel faces take the source type, both wires unbroken; new faces carried the label `Index of closest\ncal image slice, bead 2`, :301-302) and stops losing `#10465`'s terminal rows after `delete_wire` (PD310(c), `tools/bench/prep_c137_6_facts.md`), each with a self-test; `tools/stagexec.py` `compile_plan` gives the FS exit its own route kind (today a plain `connect`, `stagexec.py:720-721`); **X10 (`tools/stage_prerun.py`) counts whole-VI reads from the script's SOURCE call sites ??the device owed by retrospective-cycle136's `device-failed`**; rerun `tools/bench/c125_1_offline_measure.py` (PD252(a)). (2) Then v8 = `tools/bench/plan_ring_p4_v7.json` (01ab0893) with the smallest-`Num > last` group rebuilt as a For loop + scalar Select + Array Min, MAX I32 by `const_donor` (PD311(b) ??Select takes a scalar `s` only, MEASURED) and Select's output named `'s? t:f'` (PD311(d)); replay + `compile_plan`; prior-art review (new structure class). (3) Then ONE scratch route run: the For-loop group + the 17 uncovered route classes (`tools/bench/prep_c137_p1_facts.md` 짠3). (4) Stop-mode op card `tools/bench/cards/task_137-2.json` (validated, not dispatched) when the LabVIEW slot is free. Carries: `stagekit.address` cannot see a constant in a NEW body (PD307(a)) ??list v8 actions that rely on it; steps 160/162 replay "ok" unmeasured (PD309(c)); `errorlist_check.compare()` names missing classes (PD302(c)); `selftest_x10_c132_1` T3 stale fixture; sim step dirs `tools/bench/sim/ring_p4_v2..v7/` not deleted. Open user decisions: D-2026-10-02-04 (now: 11 sessions / 6 broken files under option 2 at load 600.2, PD303(b)), D-03, D-02, D-01.
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
VERDICT {"schema":"verdict/1","id":"priorart-c148-s06-scratch","verdict":"<one of: novel | settled-already>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

The verdict is **novel**: none of the changed lines rebuilds a gate or helper the project already has in a way that should block the build, and none contradicts a decided fact.

**What I checked:** the substantive diff list in `tools/bench/diag_c147_c3_3_proven.log:9-87` against the recipe (`tools/recipes/stage_d1_ring_p4_s06v18_scratch.py:15-104`), `tools/errorlist_check.py`, `tools/stagexec.py`, the PD354/PD355 decisions and the cycle-147 peer archive.

## PART A — the direction

- **A1 (already decided):** both new blocks carry out decisions; they don't reopen them.
  - The `el_advisory` Error List check carries out PD354(a), decided 2026-10-08 (`docs/d1/INDEX.md:244`): "Error List = recorded cross-check, not an adoption gate (RETURN only on an unseen class or |Δtotal| > 3)". `EL_TOTAL_TOL = 3` and the `RETURN`/`RECORDED` rule in the recipe (lines 85 and 121) copy this word for word.
  - The single sink-gate assertion (lines 31-32) carries out PD355(b) (`docs/d1/INDEX.md:245`): "ONE recipe sink gate for `[23166, 'Pos within cal image']` … no stagexec/gscript edit".
  - Following an earlier decision is not "settled-already" in the blocking sense.
- **A2 (already refuted):** none. The cycle-147 reviews that touched this recipe do not argue against the gate code:
  - `archive/peer/2026-10-08-c147-a1-4-re1.md` recommended the sink gate.
  - `archive/peer/2026-10-08-c147-a1-8-re1.md:63-103` traces the a1-8 D/TD/PB failure to name-keyed gates on renamed terminals. That fix lives in stagekit and the licence (`renames`, 7f70bbf9), not in these lines.
- **A3 (contradicted):** none. The recipe's `MEM_STOP_MB = X10_FAIL_MB` (680, line 33) matches the 680 MB guard in the STATUS round-1 text for cycle 145 and in PD331(c).
- **A4 (unread evidence):** none found.

## PART B — the artefact

- **B1 / B3 (already built / helper exists), noted but not blocking:**
  - Recipe lines 84-92 re-implement `errorlist_check.OCR_ALIASES` / `norm` / `ocr_fold` / `norm_ocr` (`tools/errorlist_check.py:315-332`).
  - The copy is labelled as a copy (`# == errorlist_check.OCR_ALIASES (copied)`, `# == errorlist_check.norm`) and behaves the same: lower-case, strip non-alphanumerics, apply the same two alias swaps in the same order.
  - Importing `errorlist_check` instead would pull its GUI/OCR module (`E.ocr_lines`, `errorlist_check.py:308`) into a recipe whose advisory modes must not touch LabVIEW (recipe lines 17-21). So this is a deliberate local copy, not an unnoticed duplicate.
  - The one real risk is drift if `OCR_ALIASES` changes in `errorlist_check.py:322`.
  - `elcls` reuses `ELR.item_class` (`tools/elrule.py`) and only adds a fallback. `check_sink_gates` is the existing `tools/stagexec.py:2734`, called, not rebuilt.
- **B2 (already failed):** this recipe family already ran twice as s06 scratches (`diag_c147_p4s06v18_scratch.log`).
  - The a1-4 run stopped at op 21; the sink gate on lines 31-32 addresses that.
  - The a1-8 run failed D/TD/PB on name keys. The cause is outside the reviewed lines and is addressed by the licence `renames` plus the stagekit gate fix (PD356/PD357, `docs/d1/ring-p4c.md:41,61`).
  - The changed lines do not repeat either cause.
- **B4 (already measured):** none. The Error List advisory is new as code. PD354 decided the rule; nothing has measured it on an s06 read yet.

## PART C — user rules

No contradiction. The changed lines are offline gate and report code: no queue, no camera pacing, no serial, and no change to any per-bead number. Rules U1-U13 are not touched.

PRIOR-ART: novel

VERDICT {"schema":"verdict/1","id":"priorart-c148-s06-scratch","verdict":"novel","alternative":"OCR_ALIASES/norm_ocr at recipe:84-92 duplicate errorlist_check.py:315-332 (labelled copy, same behaviour, kept to avoid importing the GUI/OCR module); drift risk only, not prior art that blocks.","discriminating_test":"Assert recipe.OCR_ALIASES == errorlist_check.OCR_ALIASES and norm_ocr(x)==errorlist_check.norm_ocr(x) on the s05 EL read items, offline.","violations":[],"sources":["tools/errorlist_check.py:315-332","tools/stagexec.py:2734","docs/d1/INDEX.md:244","docs/d1/INDEX.md:245","archive/peer/2026-10-08-c147-a1-8-re1.md:63-103","tools/bench/diag_c147_c3_3_proven.log:9-87"],"note":"Changed gate lines implement PD354(a) (EL advisory) and PD355(b) (one sink gate); a1-8's D/TD/PB failure cause lies outside the diff (licence renames + stagekit fix)."}

## Sources

(extract from answer)

## What was done with it

Card 148-a2-2 (material, 2026-10-08 15:53): verdict `novel`, no release line needed; stop_record wrote a NOVEL RECORD
for the scratch recipe's bytes (md5 31009bfce0c0487b0600359c3dac2bd0). Launch-gate dry check after the review: guard_cycle
rc 0 (`tools/bench/diag_c148_a2_2_gate_after.log`). The non-blocking B1/B3 note (recipe:84-92 copies
errorlist_check.py:315-332 OCR_ALIASES/norm, drift risk) and its suggested offline equality assert are returned to the
judgement session as an open question; nothing was edited.
