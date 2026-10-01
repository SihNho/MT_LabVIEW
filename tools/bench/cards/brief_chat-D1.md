# Brief chat-D1 - long docs: FREEZE in place + short INDEX + per-topic decision files + line cap (user 2026-10-02)

User: *"만약 문서가 너무 길어진다면 쪼개서 링크 거는 방식이 더 좋지 않은지?"* then chose "문서 정리안 전체" and
*"이렇게 하고 한번 테스트해보자"*. Run while the runner is STOPPED between cycle 129 and 130 (STATUS top STOP line,
written by the chat; do NOT remove it - the chat does after this card). Cycle 130 is the test of the new layout.

Why: active plan docs grew to thousands of lines (`docs/cycle27-plan.md` 3,798, `docs/d1-loop12-17-split-plan.md`
2,945, `docs/violation-decisions.md` 1,740, `docs/d1-build-plan.md` 1,281, `docs/d1-route-b-plan.md` 719). Every
judgement agent re-reads them each cycle (cost, faded rules). CLAUDE.md rule 4 already says active docs state only what
is true now and narrative goes one layer down. Thousands of logs/cards/reviews cite these files as `file:line`, so the
files must NOT be cut or have lines inserted above existing content.

## Do (docs/tools only; NO LabVIEW, GUI or hardware)
1. **Freeze in place, line numbers unchanged.** For each long file above: change the existing frontmatter `status:`
   VALUE to `frozen` on the same line (no line added or removed above old content) and APPEND at the END a short
   footer: frozen date, why, and the path of its index. Prove it: for each file, old line k == new line k for every k
   up to the old line count (script check, logged), only the md5 and the tail change.
2. **INDEX docs (short, current).** Create `docs/d1/INDEX.md` (≤ 300 lines) for the D1 loop-split / ring-buffer work:
   current bed (from STATUS `current-bed:`), the ring-buffer step table (P2a..P6 with state), open user decisions,
   and the Pre-decided items STILL IN FORCE - each as one or two lines + a link `docs/<frozen file>.md:<line>`.
   "In force" = PD238 and later not marked superseded, plus any older item a PD238+ item cites as still applying.
   Anything you cannot classify goes to an `## UNSURE (judgement to classify)` list, not silently in or out. Keep a
   `## Pre-decided` heading (doc_lint / CLAUDE.md require it in the current plan). Do the same, smaller, for
   `docs/cycle27-plan.md` and `docs/violation-decisions.md` only if items there are still cited as in force by the
   split plan's PD238+ items or by STATUS; otherwise their index is just the frozen footer pointer.
3. **New decisions go to short per-topic files** under `docs/d1/` (e.g. `docs/d1/ring-p3b.md`, `ring-p4.md`), each
   with frontmatter, numbering continuing from the last PD number in the frozen split plan; INDEX links each file.
   Write a 5-line "how to add a decision" note at the top of INDEX (which file, numbering, link back).
4. **Pointers:** `tools/bench/next.json` `plan` → `docs/d1/INDEX.md` with its md5 (validate with
   `py tools/protocol.py validate`); STATUS "START HERE" item 1 and any other "cycle plan = …" pointer → the INDEX
   (edit those lines only; keep the STOP line and everything else). Find where the runner/judgement prompt or agent
   definitions tell agents which plan to read or where to append Pre-decided items (grep `cycle_runner.py`,
   `.claude/agents/*.md`, `docs/session-protocol.md`, CLAUDE.md for the split-plan path) and REPORT the places; edit
   tool/prompt text only where it hard-codes the split-plan path as the place to write decisions. Do NOT edit CLAUDE.md
   (the chat does) - list the CLAUDE.md lines that need a change.
5. **doc_lint line cap:** in `tools/doc_lint.py` accept `status: frozen` (frozen files are not "current" and are not
   capped); add a cap of 400 lines for active docs under `docs/` (FAIL) with a short EXEMPT list for reference tables
   (`docs/NAMES.md`, `docs/toolkit-capabilities.md`, `docs/camera-acquisition-facts.md` - WARN only, report sizes).
   Self-test the change (a capped file fails, a frozen file passes, an exempt file warns).
6. **Check the runner still reads it:** run the runner's offline/dry path if one exists (`cycle_runner.py --dry-run`
   or its self-test) and `doc_lint`; both green. Report the INDEX line count and the UNSURE list.

## Limits
No LabVIEW, GUI, hardware. Do not rewrite or delete any line of a frozen file's old content. Do not edit CLAUDE.md.
Keep the STATUS STOP line. One git commit at the end (docs + tools + card files). Return one result/1 JSON object.
