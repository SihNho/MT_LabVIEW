# Card 148-a2-2 facts - DIFF-ONLY prior-art review of the s06 scratch recipe (2026-10-08)

- Review: `archive/peer/2026-10-08-priorart-c148-s06-scratch.md` (md5 before disposition 9fb3e86389a62c14476b1d651c4080c3), outcome ANSWERED (61s, line 9), $1.2827, claude-opus-5-5 medium.
- Run: `tools/bench/diag_c148_a2_2_priorart.log` - `prior_art_review.py --slug c148-s06-scratch --recipe tools/recipes/stage_d1_ring_p4_s06v18_scratch.py --diff-from tools/recipes/stage_d1_ring_p4_s03v18_scratch.py`, BGRUN END rc=0 after 65s; context file `tools/bench/diag_c148_a2_2_plan.md`.
- Diff scope (priorart_diff.scope): sibling s03v18_scratch, 78 substantive lines, 8 parameter-only, new classes none.
- VERDICT line (archive:538): `PRIOR-ART: novel`; verdict card `tools/bench/cards/verdict_priorart-c148-s06-scratch.json` verdict=novel.
- Findings: A1 el_advisory implements PD354(a) (docs/d1/INDEX.md:244, EL_TOTAL_TOL=3 recipe:85,121); sink gate recipe:31-32 implements PD355(b) (INDEX.md:245).
- A2/A3/A4 none; MEM_STOP_MB = X10_FAIL_MB 680 (recipe:33) consistent with PD331(c).
- B1/B3 non-blocking: recipe:84-92 is a labelled copy of errorlist_check.py:315-332 (OCR_ALIASES/norm/norm_ocr), kept to avoid importing the GUI/OCR module; drift risk only. check_sink_gates is stagexec.py:2734, called not rebuilt.
- B2: two earlier s06 scratch runs (diag_c147_p4s06v18_scratch.log: a1-4 stop at op 21, a1-8 D/TD/PB name keys); changed lines repeat neither cause. PART C: no user-rule contradiction.
- stop_record: "STOP RECORD: none"; "NOVEL RECORD written: ... sha 1603fb518d6b".
- Launch-gate dry check (guard_cycle.py on a simulated bgrun launch of the scratch recipe): BEFORE rc 0 empty (`diag_c148_a2_2_gate_before.log`, already passed via the fp-59 re-run exemption, guard_cycle.py:542-555); AFTER rc 0 empty (`diag_c148_a2_2_gate_after.log`).
- Unchanged inputs (md5 after): scratch 31009bfc..., build d947df5d..., plan cfbd9823..., licence 7f70bbf9..., brief 4cc99cc1...
- LabVIEW process count: 0 before (15:49) and 0 after (15:53).
- Written: the facts file, the gate dry-check script `tools/bench/diag_c148_a2_2_gate.py` + its input json, the context file, the archive disposition section. No tool/hook/plan/licence/recipe edit.

OPEN: should the reviewer's drift test (recipe OCR_ALIASES/norm_ocr == errorlist_check's, offline) be added before the s06 scratch, or left as a note?
