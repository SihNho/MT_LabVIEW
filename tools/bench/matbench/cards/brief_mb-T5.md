# Brief mb-T5 - stage K design (verbatim: docs/d1-loop12-17-split-plan.md at commit 53a5fb2, Pre-decided 177 and 178(a)-(d))

Goal of the plan: stage K (Pre-decided 177): kernel #5058 into 1.2 body #23166. Base graph tools/bench/graph_k_s4_20260925.json (md5 c166d036...), loops table tools/bench/graph_loops_k_s4_20260925.json, fs_pairs wiki docs/wiki/subvi/D1_s3b_m3a3b_rowD_20260922_161040.json, s1_key D1_s1_copy.

177. **(cycle 79 judgement, on `tools/bench/k_facts_79.log:91-169` run 3, `BGRUN END rc=0`, offline; result card
     `tools/bench/cards/result_79-1.json`) STAGE K DESIGN — decided.** Input `claudeDev\D1_s4_loop17.vi` md5 `4b621946…`,
     output `claudeDev\D1_k_<ts>.vi` (GUI save if ExecState 0, rule 6). `#5058` has 16 terminals, 13 wired; the bed wire
     equals the S1 wire on all 13 (`:97-146`). t5/t6/t10 stay UNWIRED (defaults, the same as the original).
     - **(a) MOVE:** `#5058` → body `#23166` of `#10170` (1.2) by `move_in`.
     - **(b) SR pair `#119/#2972` is KERNEL-ONLY** (F3 `:150-161`: left `#2972` → `#5058` t13 only; right `#119` ← w121
       from `#5058` t8 only). By 156 (SRs move with their nodes) K creates ONE new SR pair on `#10170`:
       - t8 → new RIGHT and new LEFT → t13 are S1-MAPPED rows (168/171, Jev argmax check).
       - The new LEFT's initial value comes from the same source as `#2972`'s, FSIT `#6239` on `#686`. That is a
         RULE-SINGLE-CANDIDATE row (165).
       - The old `#119/#2972` is NOT deleted in K. It is retired in L2-R with the other carriers, after the
         live-consumer check.
       - The three MIXED pairs stay in L2-A1: `#1147/#1142` (A+B+K), `#5796/#5805` (A+K) and `#7311/#11001` (no K).
     - **(c) Six top-level rows are re-made as NEW input tunnels on `#10170` (166, rule rows):** t2, t9, t11, t12, t14
       and t15. Each takes the SAME outer FSIT source on `#686` as its `#637` tunnel
       (`#2580`←`#3862` · `#2396`←`#2932` · `#4432`←`#5287` · `#3656`←`#3675` · `#3920`←`#5659` · `#4031`←`#5952`).
       Each new tunnel's IndexMode must EQUAL its original's, read on the live file (rule 1a: whole-array parameters
       stay non-indexed).
       - The old `#637` tunnels stay for any other inside consumer. A tunnel left with none is an L2-R retire row.
     - **(d) The two `#639` sinks of t8** (`Pos within cal image`, `Pos: Diffraction Pattern`; 79-1 OPEN 1) are handled
       like `#3453` in 175:
       - The contract first MEASURES each one's class. It must be a ControlTerminal that is an indicator, with w121 as
         its only source.
       - If so, it MOVES into `#23166` and is re-wired from t8 (rule row, display only).
       - Any other finding ⇒ STOP (a gate, not a branch), and judgement decides.
     - **(e) Rows left OPEN by K** (the gate lists them one by one; none of them is wired in K):
       - t0 ← `#5680` and t7 ← `#6016` (tunnels of `#5540`, group A) go to L2-A1.
       - t3 → `#5796` right goes to L2-A1, with that pair.
       - t4 w505 → `#2626`, `#2765` (group B) and `#1147` right go to L2-A1/L2-B.
       - t8's sinks `#10969` and `#10757` (group A) go to L2-A1.
       - **t1 `Image In` ← `#6810 'Image Out'`** stays on 1.1 and crosses 1.1→1.2 every frame. By 164 it is a
         queue, and it is ADDED TO THE QRT ROW as an owed row, beside t5/t7 of 175. K builds no queue.
     - **(f) `#22700` on w3040** (79-1 F5, present only in `d1_rewire_sources.json`) is the fixture TIFF writer the
       working copy carried. It is absent from S1/S3 and from the original (STATUS cycle 74, PD11 of the m8 plan). It
       is IGNORED and listed as a disagreement row (158), never wired.
     - **(g) Gates:**
       - PB `computation_diff(S1,new)` is FATAL before the save. It must equal exactly (e)'s rows plus the two carried
         L7 rows (w4517 and w3268, the latter visible since the cycle-74 DIAG_TERM fix). The simulator computes the list
         in `tools/bench/plan_<stage>.json`; nobody types it.
       - `diff(prev,new)` is an edge list.
       - The new tunnels' IndexMode must equal their originals'.
       - Second pass `Is Broken?` False on every wired row, addressed by `verify_term_uid` (174).
       - ExecState is MEASURED, not gated (the (e) rows are open).
       - Handles are recorded (176(a)).
       - Input md5 and pins must be unchanged.
     - **(h) Launch:** simulator plan files + dry + pre-run PASS (`docs/stage-simulator-plan.md:34,40,69,91`),
       prior-art released, one LabVIEW run under the retry cap. Mixed-pair creation stays in L2-A1, so K has at most
       11 wired rows (1 init + 2 S1-mapped + 6 tunnels + 2 indicator rows), inside the 10–15 batch size.
178. **(cycle 79 judgement, on result `79-3` FAIL 27/2 — `tools/bench/sim_k_split.log:69`, review
     `archive/peer/2026-09-25-c79-sim-k-split.md` ANSWERED) three rulings. The failures are OUR gate definitions; the
     K design is unchanged.**
     - **(a) Contract measured, 177(d) holds:** `#3173`/`#9519` are indicator ControlTerminals whose sole source is t8
       w121, and the six originals have IndexMode 0 (`k_contract_79.log:28,31-42`). So they move, and the new tunnels
       are IndexMode 0.
     - **(b) The simulator gates are corrected as the review proposed (§4):**
       - A0 becomes an OWNERSHIP check: `#5058` is owned by `#23166`, and `#23166` by `#10170`. Pixel offsets are
         never compared exactly.
       - P3 credits t3 by an end-graph source check (t3 is unwired; the old `#5796` right has no source) plus a
         negative control: a fake t3→`#2626` edge must FAIL the gate.
       - A THIRD offline simulator run is AUTHORISED. The failure budget restarts on card 79-4. This is not the "same
         stage fails twice at the same place" trigger: run 1 failed on a data-file overwrite, run 2 on two gate
         definitions.
     - **(c) PB = the 10 rows the simulator lists** (`sim_k_split.log:24-33`): `#376`×2 (L7), `#2626 'array'`,
       `#5696`/`#6085 'x,y,z array'`, `#10757`/`#10969 'array'`, and `#5058` t0/t1/t7. t3 has NO row of its own; its
       only S1 computation consumer is `#5058` t0, through the mixed pair `#5796/#5805` and the selector tunnels. So
       `#5058` t0's row covers it, and the end-graph source check in (b) proves it separately. ACCEPTED.
     - **(d) 177(b)'s "Jev argmax check" is WITHDRAWN** for `#119/#2972`. That pair is a register chain, and CLAUDE.md
       §3 "Stages are SIMULATED", decision 3, puts chains under RULE-CHAIN-S1 (copied from S1, never asked of Jev;
       `stage_prerun` X7). The standing rule wins over this plan's wording.
