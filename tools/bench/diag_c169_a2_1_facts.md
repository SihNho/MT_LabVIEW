---
card: 169-a2-1
status: current
date: 2026-10-12
---
# Facts 169-a2-1 - the bed moved to the saved runnable P6-1 file c2d9c13c (text edit, no LabVIEW)

1. Before: all 10 card inputs equal their pins (md5sum); saved file `claudeDev\D1_ring_p6_20261012_212645.vi` python md5 of bytes
   c2d9c13cb40c0a5cab7433896d1df157, 511194 B. requires PASS 2/0 (`cards/requires_169-a2-1.json`).
2. STATUS.md 251cc747 -> 414c70ef (148 lines): :126 `current-bed: D1_ring_p6_20261012_212645.vi`; :127 comment prefixed with
   "Moved 2026-10-12 by cycle 169 (PD406(e) ...)"; :128 NEW bed paragraph "THE WORK VI (bed) IS NOW ... RUNNABLE" (ExecState 1,
   EL 0, count stays 6 of 6, cites launch_c169_p6.json:7,472,477,511-513 and diag_c169_a1_3_facts.md:22,24-25,27-31; inputs kept
   P5 final 75773b0d + p5s01, p5s02a..e); :129 P5 paragraph now "(history) ... WAS ...".
3. docs/d1/INDEX.md 8b2a5143 -> f2bf859f: :26 'Work VI (bed)' names D1_ring_p6_20261012_212645.vi c2d9c13c, RUNNABLE, ExecState 1,
   EL 0 (5e2a4e6f), graph fbc7b7ee, load 603.7 MB; "(Before: P5 final ... 75773b0d, 47 items ...)". :27 count line untouched.
4. `errorlist_check.current_bed_text(open('STATUS.md').read())` (errorlist_check.py:164) returned
   'C:\\Program Files\\National Instruments\\LabVIEW 2026\\user.lib\\claudeDev\\D1_ring_p6_20261012_212645.vi'.
5. `git diff --stat -- STATUS.md docs/d1/INDEX.md`: STATUS.md 11 +++++++----, docs/d1/INDEX.md 8 ++++++--, 13 insertions(+),
   6 deletions(-). The stat is against HEAD and includes edits both files already carried before this card (git status M at start).
6. Hygiene: files written by this card = STATUS.md, docs/d1/INDEX.md, this file, cards/result_169-a2-1.json. No ## NEXT, plan,
   memory_model, hooks or recipe edit. No .vi opened or loaded; no LabVIEW started (tasklist probe refused by guard_bash under labview none).

skipped: STATUS.md is 148 lines (> ~110) but the card limits STATUS edits to the bed key/comment/paragraph, so no relocation;
INDEX :27 broken-count line ("P6 must RUN") left as is (card names only the bed entry).
