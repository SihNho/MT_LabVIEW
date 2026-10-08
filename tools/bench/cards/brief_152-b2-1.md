---
card: 152-b2-1
status: current
date: 2026-10-09
---
# Brief 152-b2-1 - RE-ISSUE of 152-a2-2: P4 session 9 MADE (not run) on the real s08 graph + measured FS owner, now that stagesim knows the LoopTunnel-source naming; OFFLINE (docs/d1/ring-p4d.md PD368(d)(e), PD369(f), PD365(d), PD366)

Why: 152-a2-2 stopped at v18 op 187 because stagesim refused a LoopTunnel source (naming unmeasured). Card 152-b1-2 measured it, card 152-b1-3 recorded it (`diag_c152_b1_3_facts.md`: table row 135, `stagesim.py:1886-1908`; stagesim is now 128bacfb).
This card is `brief_152-a2-2.md` again (read it first, with `diag_c152_a2_2_facts.md`), with ONLY the changes below. The discriminator (EQUAL, owner Diagram #23166) and the cut (whole remainder = v18 actions 197..202 = ops 185..190, START 595.0, X10 MAIN 638.4, margin 41.6, sensitivities +13.6 / +21.4 MB) are already measured: re-quote them from `diag_c152_a2_2_facts.md` / the 152-a2-2 logs after re-running the probe, do not re-decide.

## Changes against brief_152-a2-2.md
1. **Copies:** `prep_c152_a2_2_mk.py` (5c426b71), `_probe.py` (c8ccd0c2), `_check.py` (659d918c) -> `prep_c152_b2_1_*`; `prep_c150_a3_6_pred.py` / `_licence.py` / `_check.py` -> `prep_c152_b2_1_pred.py` / `_licence.py` (names, pins, paths only; say which lines changed).
   Output names stay `plan_ring_p4_s09v18*`, `tools/recipes/stage_d1_ring_p4_s09v18*.py`, `tools/bench/sim/ring_p4_s09v18/**` (the 152-a2-2 sim dirs may be overwritten; they are not pinned). The pin for stagesim in every check script becomes **128bacfb**; the table pin 769ae8d0.
2. **Replay (PD369(f)):** stagesim pass A AND REALSIM on the derived graph e26b4d90 must replay ops 185..190 to their END, ops 187 and 189 included. Quote the step files and the per-op result. A refusal at any op: RETURN with the verbatim refusal (file:line), the op and the rows of the structure involved. No stagesim or stage-tool edit.
3. Everything else is brief_152-a2-2 steps 4-6 unchanged: rebase (`stage_prerun --rebase`) -> plan `plan_ring_p4_s09v18.json`; pred V18E-R' (3 checks, EL base 46, `elrule.predict` WITH carry {4538,29843,29879,30002,2626} vs s08's 46 quoted, not a gate); licence by script; sink gate by census; X11 `--buildarray-check`;
   recipes (copies of the s08 pair, names/pins only); dry + prerun on FINAL bytes of plan + both recipes; `--scratch-required` rc and `--check-launch` of the scratch recipe quoted. NOT launched, no `--launch`.
4. **Invariants md5 before = after:** stagekit 604529e8, addrcheck 207beb0d, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, stage_prerun c739eb86, vigraph 13be0847, **stagesim 128bacfb**, fs_tunnel_naming_table 769ae8d0, errorlist_check 2b466a89, s08 VI f99e8414, graph 44858dbf, derived e26b4d90, s07 graph 71935a84,
   s08 plan/pred/licence/recipes (c328fdaf, cf2eccbf, 6b978d9e, ca5a5478, 7cab5049), memory_model a28b6dd7, `selftest_c152_fsowner.py` 64918ff7, ring-p4d.md cf2ffa4a. No LabVIEW process before or after. No file under tools/hooks edited.
   A gate that refuses your OWN prep command text is a false positive: `py tools/gate_fp.py log` and go on, or name it in OPEN; never an env bypass.

## Report `tools/bench/diag_c152_b2_1_facts.md` (<= 45 lines)
Discriminator + cut quotes (re-run values); replay result per op 185..190 (pass A and REALSIM, step files); rebase rc; pred checks + carry measurement; licence entries; sink-gate census; X11; dry / prerun / scratch-required / check-launch numbers; invariants; `OPEN:` line. Facts only; a result-dependent action is not yours (RETURN with the facts).
