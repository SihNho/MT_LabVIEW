---
card: 153-a2-1
status: current
date: 2026-10-09
---
# Brief 153-a2-1 - the ORIGINAL's source for #376 'frame index' (rule 1a reference); F2 wording (docs/d1/ring-p4d.md PD371(a), (c))

Read `docs/d1/ring-p4d.md` PD371 (a) and (c) (lines 163-198), `tools/bench/p5_facts.md` F2 (line 29) and F4 (line 48), and the cited
lines `docs/NAMES.md:112`, `docs/fixture-recording.md:18`, `docs/cycle27-plan.md:3748-3751`, `docs/main-vi-subvi-identity.md:98`,
`docs/main-vi-stop-and-save.md:125`.

## Step 1 - F2 wording (offline, first)
In `tools/bench/p5_facts.md` F2 (and the same text in `p5_facts.json`) add the exact words "class level; per-item uids unmeasured" with the
cite "PD371(a)". Do NOT build a `Selection List[]` reader. Nothing else in F2 changes.

## Step 2 - MEASURE the source of 'frame index' in the ORIGINAL
Question: in the original `Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi`, which node/terminal/wire feeds the `frame index` input of its
call of `save trace.vi` (the S1 node #376)? S1 says: w3268 <- #637 i (the enclosing While loop's iteration terminal, I32).
The two docs in step 4 say #5119 (x-y). Numbering differs between the original and S1: compare by what the wire comes FROM (loop `i`
terminal of the enclosing While vs the subtract), and quote the original's uids.

1. Search the on-disk reads of the ORIGINAL first (`docs/main-vi-*.md`, `tools/bench/*census*`, `tools/bench/*orig*`, graph/wiki json of the original; NOT
   S1 artefacts). If one gives the uid of the wire into that input, quote it file:line - no LabVIEW needed.
2. Only if no on-disk original read gives it: ONE read-only LabVIEW read of a claudeDev BYTE COPY of the original (copy it with a unique scratch name
   under `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\`, md5 of the copy == md5 of the original, quoted). Use the existing
   graph reader (`tools/gscript.py` readers / `tools/bench/graph_*` producers, the way S1's graph was read); NO edit, NO save of the copy, NO Run.
   Name the read in the facts file. Never open the original path itself. Close without saving, delete the copy, verify
   `tasklist | grep -i labview` is empty, original md5 unchanged (quote before/after).
3. Quote: original's source uid + terminal (file:line) next to S1's `w3268 <- #637 i` (`cycle27-plan.md:3748-3751`).

## Step 3 - decide by comparison (this is a measurement report, not a design)
- **Same source (loop iteration `i`)**: edit `docs/NAMES.md:112` and `docs/fixture-recording.md:18` with a dated note
  ("2026-10-09 (card 153-a2-1): corrected - frame index is fed by the While loop `i`, not #5119; evidence <file:line>") that cites the evidence; do not
  delete the old text. Then update `p5_facts.md` F4 (and .json) so its "Doc conflict" line cites the correction.
- **Different source** (anything but the loop's `i`): do NOT edit any doc and do NOT touch p5_facts.md F4. STOP and return `status FAIL`/`OPEN:` with BOTH
  reads quoted (original uid chain, S1 uid chain). The assignment session hands the purpose back (rule 1a: only judgement decides).

## Invariants (md5 before/after, quote)
original VI; s09 VI eb1d0f31; graph 22f967b5; stagekit 604529e8, addrcheck 207beb0d, stagexec 1bab9cf9, gscript 1a80236e, stage_prerun c739eb86,
stagesim 78b8d5a1, vigraph 13be0847. No tools/hooks edit; no plan file; no `docs/d1/ring-p5.md`; no motor or camera.

## Return (<= 30 lines)
F2 wording line (file:line); the original's source (uid, terminal, how read: on-disk file:line or the one named read); S1's source; same/different;
the doc lines edited (or "stopped"); LabVIEW gone (tasklist); md5 table. `OPEN:` for anything needing judgement. Failure budget 2.
