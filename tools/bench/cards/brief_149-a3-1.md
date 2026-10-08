---
card: 149-a3-1
status: current
date: 2026-10-08
---
# Brief 149-a3-1 - ADOPT s06 (569ffbf5), final Error List expected file, fresh load + graph, `load_by_vi`, Void-type census (docs/d1/ring-p4c.md PD363(b)(c))

ONE LabVIEW card. Read first: `tools/bench/diag_c149_a1_2_facts.md` (the adoption stopped at EL-ADVISORY, rc 1) and
`tools/bench/diag_c149_a1_3_facts.md` (the 51 is explained except item 6). The judgement has since DECIDED (PD363(b)): **s06 IS ADOPTED,
item 6 ("source void -> sink I32") recorded as UNIDENTIFIED.** Nothing is rebuilt; no second scratch; `claudeDev\D1_ring_p4s06_20261008_174730.vi`
(md5 569ffbf5) is never edited. The Error List is a recorded cross-check, not a gate (PD354): the expected file for s06 is the 51-item read.

## Steps (the prepared scripts are the s06 route of card 149-a1-2; copy them to `diag_c149_a3_1_*` with the card id/names changed ONLY)
1. **Invariants BEFORE** (`diag_c149_a1_2_inv.py` form, copy to `diag_c149_a3_1_inv.py`; md5 before/after): stage tools, errorlist_check,
   s05 3f9ac26b, s04 95e408ff, s03 282301ca, bed 39511877, s06 569ffbf5, memory_model 88eeb037.
2. **Adopt** by the PD354(a) route: `diag_c149_a1_2_adopt.py` copy -> `stagexec.adopt_scratch` called by import (the CLI form is refused, fp-39). It
   asks for the scratch log's LAST segment (card 148-a2-4's run, PASS 22/0 `diag_c147_p4s06v18_scratch.log:1040`). Quote the new path + md5
   (the artefact is the existing claudeDev file; adopted_scratch.jsonl gets the record). If the adopt refuses, RETURN with the refusal
   (file:line); do not clear it by editing a stage tool or the log.
3. **Final Error List expected file** from the 51-item read of the SAME bytes: `diag_c149_a1_2_elexp.py <read json>` copy, read json =
   `tools/bench/errorlist_D1_ring_p4s06_20261008_174730_20261008_181243.json` (md5 899e2656, byte copy `_elc_..._181243.vi` identical=True to
   569ffbf5 per `diag_c149_a1_2_facts.md:19`). That IS the elrun-wrapper read of the adopted bytes; quote the count (51 expected). A second
   11-minute read is NOT required. If a card-local gate demands a fresh read, do ONE with `tools/bench/diag_c149_a1_2_elrun.py` (per-command
   wrapper, no install) and report the count; another count than 51 is reported, not fixed.
4. **Fresh-instance load + graph read:** `diag_c149_a1_2_mkgraph.py` / `_graph.py` copies -> `tools/bench/graph_ring_p4s06_<stamp>.json` + md5
   (this is the real s06 graph the s07 rebase will use; quote its path).
5. **`memory_model.json`: ONLY one `load_by_vi` entry** for 569ffbf5 from the measured load (`diag_c149_a1_2_memload.py` copy). Key-by-key diff
   quoted; no limit, coefficient, MEMSTOP or X10 value changes.
6. **Void-type census (PD363(c)) - plain gscript reads, no edit verb, no `Is Broken?`, NOT the stagekit `discard_work` path (fp-63).** Model the
   script on `tools/bench/diag_c149_a1_3_types.py` / `_wire.py` (those ran plain gscript reads and passed 7/0 and 9/0). Take it on (i) the adopted
   s06 and (ii) a BYTE COPY of s05 `3f9ac26b` (never open the s05 original; copy bytes first, delete the copy after). For every wire terminal
   whose type is Void or whose type string contains `Void`: wire uid, terminal uid, owner node uid / class / label, terminal name, type string.
   Write `tools/bench/diag_c149_a3_void_census.md`: both lists, the s06-only entries listed separately, the count of each. FACTS ONLY, no
   interpretation, no claim that item 6 is or is not one of them.
7. **Invariants AFTER**, handle counts before/after (flat +-100 is not required for a fresh instance, record them), no `_elc_*`/byte copy left,
   `tasklist` LabVIEW count 0 (LabVIEW closed and verified gone).

## Return conditions (no retry inside the card)
Adopt refusal; a read that returns a different count than 51 is REPORTED and the expected file written from what was read; an invariant md5
that moved; any step needing an edit verb or a stage-tool edit.

## Report (`tools/bench/diag_c149_a3_1_facts.md`, <= 45 lines)
Adopted path + md5, expected file path + count, graph json + md5 + load MB, `load_by_vi` key-by-key diff, census counts + the s06-only list head,
invariants, handles, LabVIEW gone. `OPEN:` line. Facts only. Dispatch peers only if a gate FAILS (hypothesis review per the failed-prediction rule).
