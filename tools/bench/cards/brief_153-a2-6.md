---
card: 153-a2-6
status: current
date: 2026-10-09
---
# Brief 153-a2-6 - retry of 153-a2-1: measure the CURRENT original's source for #376 'frame index' by ONE read-only read of a claudeDev byte copy (PD371(c))

Read `tools/bench/cards/result_153-a2-1.json` and `tools/bench/cards/brief_153-a2-1.md` first (steps 2-4 are unchanged). Card 153-a2-1 did step 1 (F2
wording, done: p5_facts.md:36, p5_facts.json:43 - do not redo) and found at wire level that the 2026-09-18 on-disk census says SAME as S1
(w3268; #5119 feeds #2626 'element' instead), but the original file now hashes 2f048e3a, not the census-time c39f36e0. It stopped there and did not edit
any doc. The cause of the stop is explained (the file changed after the census; nobody on this team saved it - the user owns the original's state).
Whether the old census still describes the current file is exactly what this card measures.

## What to do
1. Record the original's md5, size, mtime (read-only, `md5sum`/`stat`; do not open it in LabVIEW) and quote the c39f36e0 -> 2f048e3a difference.
2. Make ONE byte copy under `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\scratch_c153_a2_6_orig.vi` (md5 of the copy ==
   the original's current md5, quoted). Read the node/wire that feeds `frame index` of its `save trace.vi` call with the existing graph reader
   (`tools/gscript.py` readers / `tools/bench/graph_*` producers, as S1's graph was read): NO edit, NO save, NO Run. Close without saving, delete the
   copy, verify `tasklist | grep -i labview` empty, original md5 unchanged (quote before/after).
3. Compare with S1's `w3268 <- #637 i` (`cycle27-plan.md:3748-3751`) by what the wire comes FROM (enclosing While loop `i` terminal) and quote both chains.
4. Decide by comparison exactly as in brief_153-a2-1.md Step 3: SAME => dated, cited correction of `docs/NAMES.md:112` and `docs/fixture-recording.md:18`
   (old text kept) and `p5_facts` F4 (.md + .json) cites it; DIFFERENT => edit NO doc, STOP, both reads quoted.
5. If the graph reader needs a failed-prediction review before it may launch (guard_peer), run the `hypothesis` peer for it (card allows it); do not bypass.

## Invariants (md5 before/after, quote)
original VI (path unchanged; md5 whatever it is now, before == after); s09 VI eb1d0f31; graph 22f967b5; stagekit 604529e8, addrcheck 207beb0d, stagexec
1bab9cf9, gscript 1a80236e, stage_prerun c739eb86, stagesim 78b8d5a1, vigraph 13be0847. No tools/hooks edit; no plan file; no `docs/d1/ring-p5.md`;
no Selection List reader; no motor or camera.

## Return (<= 30 lines)
The md5 difference; the original's source (uid, terminal, how read); S1's source; same/different; doc lines edited (or "stopped"); LabVIEW gone
(tasklist); md5 table. `OPEN:` for anything needing judgement. Failure budget 2.
