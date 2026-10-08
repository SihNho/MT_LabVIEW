# Facts - card 150-a1-2 (PD364(h), STATUS.md relocation), 2026-10-08 20:3x, offline
- Before: STATUS.md 203 lines, md5 050f34f4581c483bd9e65654210fa190 (copy `tools/bench/diag_c150_a1_2_status_before.md`, same md5).
- After: STATUS.md 110 lines, md5 32f6576c82d09ea19b9a5f737d59f489 (UTF-8 BOM + CRLF kept). Archive md5 607edd1243117af10054668be862684d.
- Moved VERBATIM (bytes unchanged, original order) to `archive/2026-10-08-status-cycle150-relocate.md`, appended after the untouched 12-line header:
  - §1 = before lines 10-20 (11 top-banner `(history)` lines) -> pointer at new line 10
  - §2 = before line 22 (top-banner `(history) STOP (lifted 03:2x)`) -> pointer at new line 12
  - §3 = before lines 73-156 (84 `## NEXT` lines: cycle 149 round 3 ... cycle 134 brief) -> pointer at new line 63
- Pointer text: `(history) RELOCATED VERBATIM -> archive/2026-10-08-status-cycle150-relocate.md §<n>`.
- Kept byte-identical (check gates): frontmatter 1-6, STOP/RESTARTED 7-9, START HERE 32-36, lock block 38-44, banner + rig-state 49-56,
  OPEN 61-67 (53, 58 untouched), NEXT heading + PARALLELISM RULE 69-70, CYCLE 150 PURPOSE + OUTCOME ESCALATION 71-72, current-bed 184-185,
  Where to look 199; also every other unlisted line (21, 23-31, 37, 45-48, 57-60, 68, 157-198, 200-203).
- Line 24 (an older `(history) ... RELOCATED VERBATIM` pointer into the cycle-123 archive) is itself a pointer: kept, not moved.
- Scope beyond the brief's literal range: the brief's range (73-102, down to the cycle-142 paragraph) alone gives 164 lines; "every NEXT
  paragraph older than cycle 150" (73-181) gives 85. Cut at the end of the cycle-134 brief (156) = 110 lines (pass 100..120, doc_lint
  L3 limit 110). Kept in NEXT: cycle 133/132/131 briefs (157-175), the older relocation pointers 176-181, pool rule, carries, bed lines.
- Moved also: line 108 `🔴 FOR THE USER` (cycle-141 Insert-vs-Replace report) now in archive §3.
- Move: `tools/bench/diag_c150_a1_2_move.py` -> `tools/bench/diag_c150_a1_2_move.log` PASS 13/0, BGRUN END rc=0.
- Check: `tools/bench/diag_c150_a1_2_check.py` -> `tools/bench/diag_c150_a1_2_check.log` PASS 24/0, rc=0:
  sections == before ranges byte-equal; new STATUS minus 3 pointers == before minus 96 moved (107 lines, order+bytes);
  multiset 203 == 107 + 96; archive header md5 01e1727a unchanged.
- doc_lint before (`diag_c150_a1_2_doclint_before.log`): 4 fail, 9 warn, 4 pass; L2 2 dangling (incl. STATUS.md:136), L3 WARN 203 > 110.
- doc_lint after (`diag_c150_a1_2_doclint_after.log`): 4 fail, 8 warn, 5 pass; same 4 FAILs (L2 ring-p4.md:131, L6, L8, L10), L3 PASS 110,
  L2 dangling 2 -> 1 (STATUS.md:136 citation now inside the archive). No new error.
OPEN: the cut point (end of cycle 134, line 156) is my choice between the brief's literal range (164 lines) and "every older paragraph" (85 lines).
