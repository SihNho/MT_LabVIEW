---
card: 152-a1-1
status: current
date: 2026-10-09
---
# Brief 152-a1-1 - FIRST owner read of Flat Sequence #29721 on s08 (docs/d1/ring-p4d.md PD368(c)); the ONE LabVIEW card of this step

Why: cycle 151 could not make P4 s09 because `stagesim` has no measured diagram for FS #29721 (frame #29869, 0 border tunnels;
`stagesim.py:1805-1807`, PD289(f)). PD368(c) adds a THIRD measured owner link: ask LabVIEW who owns the FS, with the strict uid echo.
This card only MEASURES. It edits no tool, builds nothing, saves nothing.

## Read first (and nothing else)
`docs/d1/ring-p4d.md` PD368(b)(c); `tools/bench/diag_c151_a1_1_facts.md` (FS #29721 rows, load of s08); `tools/bench/diag_c151_a1_1_fs.py` (offline FS reader, shows the graph keys);
`tools/bench/diag_c150_a3_2_mkgraph.py` / `diag_c151_a1_1_graph.py` (how a fresh-instance read of an adopted VI is launched under bgrun with the memory meter);
`tools/bench/cards/brief_151-a1-1.md` steps 7-8 (invariants, handles, LabVIEW-gone). `OpOwnerChain_v1` and `gscript.owner_of` (strict echo) are existing - grep before writing anything.

## Inputs (md5 pinned in the task; a mismatch is a RETURN)
s08 VI `claudeDev\D1_ring_p4s08_20261009_031503.vi` md5 `f99e8414a2081538552e26ba24ee713d` (NEVER edited, NEVER saved - a read-only load in a fresh instance),
graph `tools/bench/graph_ring_p4s08_20261009_033522.json` md5 `44858dbf...` (never rewritten).

## Steps
1. **Invariants before**: md5 of `tools/stagekit.py` 604529e8, `addrcheck.py` 207beb0d, `stagexec.py` 1bab9cf9, `gscript.py` 1a80236e, `stage_prerun.py` c739eb86, `vigraph.py` 13be0847, `stagesim.py` 748bbf30, s08 f99e8414,
   graph 44858dbf (copy `diag_c151_a1_1_inv.py` -> `diag_c152_a1_1_inv.py`, names only). LabVIEW process count and handle count before.
2. **Reader script** `tools/bench/diag_c152_a1_1_owner.py`, <= 120 lines on `tools/stagekit.py` (existing scratch/launch skeleton; header `# labview: read`). Fresh instance, load s08 read-only, then:
   (a) `OpOwnerChain_v1` (via `gscript.owner_of`, strict uid echo) of FS uid **29721** -> record owner class, owner uid, echo uid; (b) the same for frame **29869**;
   (c) CONTROL (extra fact, not a pass item): the same read for ONE other Flat Sequence of the graph that HAS border tunnels (choose from `fs_measured.borders`; its face-derived diagram is
   what `stagesim.fs_measured_state` already computes) - quote read vs face-derived. Close every reference (handle count flat +-100 over the run).
   Predictions (write them in the script header): (a) class `Diagram`, uid non-zero, echo == 29721; (c) read == face-derived diagram. A different result is REPORTED, not fixed (no retry inside this card).
3. **Store** `fs_owner_read` as a graph key WITHOUT rewriting graph 44858dbf: write a DERIVED file `tools/bench/graph_ring_p4s08_20261009_033522_fsowner.json` = byte-for-byte the same JSON plus the top-level key
   `"fs_owner_read": {"29721": ["Diagram", <uid>]}` and a sibling key `"fs_owner_read_cite"` (read log path:line, s08 md5, graph md5). Store only a read that returned class `Diagram`, non-zero uid, echo == FS uid;
   otherwise write NO derived file and RETURN with the facts (PD368(c): such a read is UNMEASURED). Check the derived file still loads through the existing graph readers (`vigraph` / `stagesim.fs_measured_state` import-load, no edit).
   Do NOT extend `vigraph.py` (the derived-file route keeps its md5 13be0847).
4. **Invariants after**: s08 md5 unchanged (quote), graph 44858dbf unchanged, all tool pins above unchanged, `tasklist` LabVIEW count 0 (closed AND verified gone), no scratch/byte copy left.
5. No tool or hook edit; no second launch (a retry is a new card); write only the globs of the task.

## Report (`tools/bench/diag_c152_a1_1_facts.md`, <= 30 lines)
Owner read: class / uid / echo for FS #29721 and frame #29869 with the log line numbers; control FS read vs face-derived; derived file path + md5 (or "none written" + reason); s08 md5 before = after;
handles before/after; LabVIEW gone. `OPEN:` line. Facts only.
