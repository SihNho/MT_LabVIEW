# UNDER REVIEW — D1 staged build, stage M3a-3 (cycle 65, slug c75-m3a3)

Stage M3a-3 of the D1 staged build, starting FROM `claudeDev\D1_s3b_m3a2_20260922_023029.vi` (md5 3842f5e6…,
broken by design, never run). It re-sources the TWO downstream consumers that still read the OLD loop's right
shift registers onto the NEW loop's right registers: `Global #7202 'Global motor pos.vi'` terminal 0
`'Focus position'`, today a sink on wire 4859 whose source is OLD `#4256` OUTER; and `FlatSequenceInnerTunnel
#7468`, today a sink on wire 7506 whose source is OLD `#4334` OUTER. The new sources are the still-bare OUTER
terminals of NEW RIGHT registers `#23868` ('VISA out') and `#23895` ('position [internal units]') on loop
`#23032`. Both sinks are ALREADY WIRED, so the per-row operation is delete-and-rebuild (cycle 62's re-cut, plan
Pre-decided 53(d')), not a branch as M3a-2's rows were. Acceptance is the rule-1a invariant of Pre-decided 85:
the sink receives its value from the intended source terminal, asserted on an ordered second idempotent pass,
with `recip == queried_uid` on every reader row. The artefact stays broken by design and is never run;
`ExecState` is not a criterion.

## Pointers for your search (not a corpus — search the project yourself)

- The stage is named in `docs/cycle27-plan.md` Pre-decided 91 (read 91–100, then 84–90; 78/80/81/82 are WITHDRAWN).
- The immediately preceding stage M3a-2 was delivered and independently verified this same day
  (`tools/bench/build_d1_m3a2.log`, `tools/bench/diag_c74_m3a2_verify.log`; recipe
  `tools/recipes/build_d1_m3a2.py`); its own prior-art review is
  `archive/peer/2026-09-22-priorart-priorart-c74-m3a2.md`.
- No recipe file for M3a-3 exists yet; it has not been written.

## The questions this review must answer for THIS stage

Has the direction (re-sourcing these two already-wired downstream consumers onto the new right registers, as a
separate saved stage) or the artefact (a delete-and-rebuild row builder with an ordered idempotent second-pass
assertion) already been decided, refuted, contradicted, built, failed, helper-provided, or measured in this
project's own files?
