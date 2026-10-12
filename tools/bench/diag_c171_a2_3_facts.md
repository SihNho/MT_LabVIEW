# diag_c171_a2_3 facts (card 171-a2-3) - BLOCKED before step 1, nothing dispatched, nothing drained

1. Step 1 refused by guard_peer: "the previous priorart review is UNDISPOSED. review: archive\peer\2026-10-13-priorart-c170-paced60.md, reason: disposition is empty or still the placeholder" (tools/hooks/guard_peer.py:1181-1194).
2. That review ends with "## What was done with it" / "(Claude fills in)" (archive/peer/2026-10-13-priorart-c170-paced60.md:681-683); its verdict is novel (:673,:675).
3. The rule (guard_peer.py:838-855) checks the NEWEST archived *priorart*.md; any command naming the prior-art review script is refused until it is disposed.
4. Card 171-a2-3 flags.write does not include archive/peer/2026-10-13-priorart-c170-paced60.md, so this card cannot dispose it (task_171-a2-3.json flags.write).
5. Step 2 (drain fp-103, queue c130_5 T3) depends on step 1 per the brief -> NOT done. fp-103 still "open" (gate_fp.py list).
6. Side refusal logged: fp-105 (guard_peer refused a read-only cat/head chain naming the script; same class as fp-78).
7. stage_prerun.py md5 af6937e84fbe857e571f19bb55301465 (unchanged); patch diff f8f1fd958637a66b065c5e08bc886108.
8. fp-102, fp-104 untouched; no hook edit; no LabVIEW process before/after (tasklist empty).
