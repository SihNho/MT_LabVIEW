# Brief for card 123-6 — STATUS.md back to one screen (cycle 123 judgement, 2026-10-01)

Owed since retrospective-cycle121 (ACCEPTED: "relocate STATUS history and mark `d1-build-plan.md` §9 superseded, in a doc
card after the deliverable step"). CLAUDE.md rule 4: STATUS.md over ~100 lines means narrative crept back in — move it to
`archive/<date>-status-<topic>.md` and leave lock, hardware permission, current state, OPEN items and NEXT. **The narrative
is never rewritten, only relocated.** STATUS.md is ~600 lines today.

## Do
1. Create `archive/2026-10-01-status-cycle123-relocate.md` and move into it, VERBATIM and in order, every block of STATUS.md
   that is history: the "(history)" banner lines at the top, the old "FIRST ACT of cycle …" blocks, the "CYCLE N in brief"
   blocks (cycles 121 and older), the superseded bed narratives, and anything else that describes the past. Leave one
   short pointer line per relocated group (e.g. "Cycles 105–121 in brief → `archive/2026-10-01-status-cycle123-relocate.md`
   §3").
2. KEEP in STATUS.md, byte-for-byte unless stated:
   - every line at the top that is a live marker (the current "✅ STARTED — USER 2026-10-01" line, the 📌 NEW CHAT line);
   - the `labview-lock` YAML block;
   - the whole HARDWARE section including the `rig-state:` line (never touch that line or its comment);
   - the live OPEN items;
   - `## NEXT` with: the PARALLELISM RULE paragraph, the cycle-123 first-act block (the judgement session rewrites it after
     you return), the "CYCLE 122 in brief" block, the USER RULE paragraph on the pool overload (re-confirmed 2026-09-28),
     the CARRY paragraph, the `current-bed:` line and its HTML comment, and the "THE WORK VI (bed)" paragraph.
3. `docs/d1-build-plan.md` §9: add one marker line at its head: superseded by `docs/ring-buffer-design.md` and
   `docs/d1-loop12-17-split-plan.md` Pre-decided 238 (the Q_free/Q_work pool queues only). Change nothing else there.
4. Run `py tools/doc_lint.py` and report its error/warning counts before and after; no NEW error.

## Rules
- Re-read STATUS.md immediately before you write it. If it changed since your first read (a user or chat edit, e.g. a
  line beginning `STOP`), keep that change. Never create a line that begins with `STOP`.
- Nothing is deleted: every relocated line must appear in the archive file (check by a line-multiset comparison: lines of
  old STATUS == lines of new STATUS minus pointer lines + lines of the archive file minus its headings).
- Target: STATUS.md ≤ ~120 lines. No LabVIEW, no GUI, no hardware, no code edits.
