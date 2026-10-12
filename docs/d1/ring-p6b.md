---
type: decision
kind: topic
status: current
date: 2026-10-13
parent: docs/d1/INDEX.md
tags: [d1, ring-buffer, p6, replay, dry-taint, fp-103, pre-decided]
---

# Ring buffer P6 — continued (`docs/d1/ring-p6.md` is near the 400-line cap; PD412 and earlier live there)

413. **(cycle 171 judgement, 2026-10-13 — `handback_171_1.json`, trigger a: 171-a1-2, the one retry of PD412's fix, FAILed
     `selftest_dry_c130_5` T3, cause not diagnosed)**
     USER-RULES: U1 (relied on: a dry-checker change touches no VI and no computation); none contradicted.
     - **(a) PD412(b) is NARROWED to the value criterion of patch af6937e8 (`diag_c171_a1_2_patch.diff`, f8f1fd95).** The
       literal rule ("every name bound in a stub-touching statement is tainted") contradicts card 134-1 T1: its FR gate reads
       `real` = 5911 simulated rows bound by `x.run()`, which touches Fakes inside the simulator, and T1 must FAIL at FR
       (`diag_c171_a1_1_facts.md:10-12`). The bound VALUE separates the two cases: a name is tainted when its value is a
       Fake, holds a Fake, is an EMPTY container, or is unbound. Scalars from a stub stay clean; that is the checker's
       behaviour BEFORE this fix (status quo, not a new hole). Evidence the patch met PD412(c)(1)-(2): plan 170 A2
       UNVERIFIED, dry ends PASS-UNVERIFIED, unverified 7 (`diag_c171_a1_2_dry170.log:10,28`); c134_1 11/0 = record.
     - **(b) PD412(c)(3) is met in substance:** with the patch, plans 78 and 110 give their stored verdicts again (same
       labels), and the unpatched db81a1d3 does NOT (FAIL A2), so fp-103 already broke them. Plan 95 has no graph (same
       before and after); the ring recipe p5s02c gives PASS before and after (stored FAIL PB is older than the recipe's
       last change). These are facts, not failures (`diag_c171_a1_1_facts.md:26-30`).
     - **(c) c130_5 T3 is decided by ONE measurement:** run `selftest_dry_c130_5.py` on the UNPATCHED db81a1d3 first. Its
       stored records (cycles 134, 152) are older than the PB-criterion change of PD370(b) (cycle 153, `ring-p5b.md:165`),
       so the FAIL may well predate the patch. Rule set now: if the unpatched run FAILs T3 at the same GATE PB, the
       patch is not the cause → re-apply af6937e8, record the T3 FAIL as a stale self-test fact (gate-fp entry, fixed
       after P6-2, not in this purpose). If the unpatched run PASSes T3, the patch causes it → the card returns and hands
       back; no third version of the patch is tried in this cycle.
     - **(d) Brief step 0 label swap accepted:** a89dafc1 = `replay_imaqdx_get_image_buf.vi`, 842ecad9 =
       `replay_get_buff_image.vi` (`ring-p6.md:313-315`), not drift.
     - **(e) Then PD412(c)-(d) unchanged:** prior-art review on the patch (peers priorart), drain fp-103 naming
       `selftest_c171_a1_1_taint.py` + c134_1; then P6 replay copy → S1 leg → P6 leg → compare with D = 20 → fp-102 last.
