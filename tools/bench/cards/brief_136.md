# Cycle 136 brief — detail behind cards 136-1 and 136-P1 (judgement, 2026-10-02)

## 136-1 (LabVIEW, scratch only) — pass items in full
1. SCRATCH VI (new, <=120-line stagekit diagnostic, existing ops only): U1+U2+U3 per `tools/bench/prep_c135_p2_facts.md:51-53` —
   Select from donor #529 with a Boolean-ARRAY `s`; I32 const 2147483647 created on Select `f` BEFORE `t` is wired (report its
   class/representation/value before and after `t` is wired); Greater?(array, scalar) out -> Select `s`; Select out -> Array Max & Min.
   Per wire: `Is Broken?` from the connect op; ExecState; Error List COUNT (`--count-only --role scratch`). Record under
   `tools/bench/scratch_verify/` with PASS/FAIL per route.
2. Or for W1's stop (PD293(d)): find an existing donor or creator route for a Boolean Or, create it in the same scratch VI, wire two
   Booleans in and its out into a While conditional terminal; report the route used and `Is Broken?`.
3. SCRATCH BYTE COPY of the bed (md5 checked first): U5 (plan-made While output tunnel OUTER face -> sink inside a plan-made FS frame,
   then RLE) and U6 (sink on the parent diagram <- source inside a single-frame plan-made FS: exit hop, then RLE) per
   `prep_c135_p2_facts.md:54-55`. Per route: `Is Broken?`, census delta (objects/tunnels created), whether the source wire was re-created.
4. On the same byte copy READ `#10170`'s conditional-terminal mode (Stop if True / Continue if True) and `#10171`'s two input wire uids.
5. Real whole-VI graph read of the UNEDITED bed (FS frames + borders, same format as `graph_ring_p3b2a_fs_*.json`) to
   `tools/bench/graph_ring_p3b2b_<stamp>.json`; bed md5 unchanged before and after.
6. LabVIEW closed and verified gone; scratch VI and byte copy deleted after their records are written (md5 kept in the result);
   handle count read before/after.

## 136-P1 (offline prep) — pass items in full
0. fp-30: make `tools/bench/selftest_c134_1_dry.py` pass on its own content (fails 10/1, result_135-2), run it under this card, then
   `py tools/gate_fp.py drain --id fp-30 --fixed <path:line> --selftest selftest_c134_1_dry`. If the refusal needs a `guard_bash.py`
   change, do NOT edit guard_bash (a LabVIEW card is live): log the fact, return fp-30 OPEN, continue.
1. `tools/bench/plan_ring_p4_v2.json` from the draft:
   (a) every loop-1.2 shift register written by the tracking body gets a Select valid?new:old; result to 1.7 only when valid (PD293(b));
   (b) valid = n1==n2 AND n1>last; the n1>-1 actions dropped (PD293(c));
   (c) W1 stop exit = Local read of the program stop control + Or into W1.cond (PD293(d));
   (d) 1.2's scaffold stop `#10171` replaced by the program stop (PD295(c));
   (e) n2's Num read in a one-frame FS whose input tunnel takes a `#5058` output (PD295(d));
   (f) 5th per-slot array `BufDiff`: indicator + init on FS1 `#4866` + 1.1 per-slot write of `#5119` out + 1.2 read into `#2626`
       element|0 t2832 (PD295(a)).
2. Cut into build steps of <= 40 actions, dependency-closed; per step: action count, X10 per LabVIEW session (start = measured P3b-2
   final 578.0 MB, model of PD268(a)/PD275), number of LabVIEW sessions under 675.
3. Every action's route MEASURED (cite census_samples.json / scratch_verify record) or UNMEASURED (name the 136-1 item that measures it).
4. stagesim replay of the whole v2 on the newest available graph of the bed or P3b-2's sim end state (base provisional, `sim_of`
   named); report replay result and computation_diff. No launch, no recipe.
5. Rule-1a list: original node terminals whose wiring changes in v2 and why each keeps the computation.
