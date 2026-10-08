---
type: brief
status: current
date: 2026-10-08
---
# Brief 147-a1-2 — s06 maker kind gate: allow branch -> connect for a source made in an earlier session (PD353(e)); OFFLINE, prep file only

Card 146-a1-5 stopped at its own maker's kind gate: v18 op 116 (`p4_w_idx_frameidx`, src `new:TS1.outer`) compiles `branch` in v18 (TS1 created in the same plan,
`tools/stagexec.py:808-809`) but `connect` in s06, where TS1 is an s05 uid (`stagexec.py:812-813`). The maker's whitelist allowed only `wire_sr` -> `connect`
(`tools/bench/prep_c146_a1_5_mk.py`, md5 in the card inputs; facts `tools/bench/diag_c146_a1_5_facts.md`). PD353(e) decided: the pair `branch` -> `connect` is
ALLOWED when the source symbol was created in an EARLIER session; both make the same wire net; the computation check stays the maker's end comparison + the
scratch's E1.

## Steps
1. Copy `tools/bench/prep_c146_a1_5_mk.py` to the NEW file `tools/bench/prep_c147_a1_2_mk.py` and widen ONLY the kind gate: a (v18 kind, session kind) pair
   `branch` -> `connect` passes when the action's source is a `new:<sym>` symbol whose creating op lies before this session's first op (i.e. an earlier session, now a
   uid in the session's base). Keep every other check. A `branch` -> `connect` whose source symbol is created in THIS session still FAILs. Edit `stagexec.py`,
   `stagekit.py`, `stagesim.py`, `stage_prerun.py`: NO.
2. Run it on the CURRENT provisional base (the simulated end of s05, as 146-a1-5 did): s06 = v18 ops 115.., group-respecting longest prefix with MAIN X10 <= 680 at
   the provisional start; report the cut, the start assumption, and the +-5 MB sensitivity. The provisional start is void once card 147-a1-3 rebases on the real
   s05 graph; this card only proves the gate and makes the provisional s06 files (`plan_ring_p4_s06v18*.json` are overwritten by the maker, as in 146-a1-5; the old
   md5 are 8f33ad75 / 08b8dbe2 in the card inputs).
3. Report: every kind-gate decision on the s06 ops (which pair, which action, why allowed or refused), the line for op 116, and the maker's end comparison
   "s06 sim end == v18 end over the same ops" (`cdiff` 0 or the exact difference). A negative control: a synthetic `branch` -> `connect` whose source is created in
   this session is REFUSED (one line, offline, no file written).
4. `stagexec.py` md5 unchanged before/after (report both). No LabVIEW process at any time.

## Never
Edit a stage tool, v18, the s05 files, memory_model.json or the recipes of s05; launch anything; write pred / recipes / licence files (card 147-a1-3 does that on the
real graph).

## Return
`result/1` + `tools/bench/diag_c147_a1_2_facts.md`: the gate diff (file:line), op-116 decision, cut / start / sensitivity, sim-end comparison, negative control,
protected md5 before/after.
