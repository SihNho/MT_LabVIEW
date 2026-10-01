# Brief chat-G1 - bring Gemini back for WEB SEARCH? Measure first (user 2026-09-29: "진행")

The user heard that Gemini is much better at web search and asked whether to use it again. Gemini (agy CLI) was
retired from every default on 2026-09-22 because in headless runs it auto-denies its `command` permission, so it did
nothing useful unattended (CLAUDE.md §5 research ladder). The chat proposed, and the user approved: fix-test first,
then a small known-answer comparison, before any role change. The cloud plan is DROPPED; everything runs locally.

## Part A - headless permission (measure, do not redesign)
1. Read `tools/peer.ps1` (the gemini branch) and `archive/peer/2026-08-28-agy-permissions-schema.md`. Search the web /
   agy's own help (`agy --help`, `agy models`, its settings schema) for the approval/permission mode that lets a
   headless run use WEB SEARCH/FETCH without prompting, while staying read-only (no file writes, no shell).
2. One real call through `peer.ps1 -Agent gemini -Kind fact` (or a direct `agy` call if peer.ps1 cannot pass the flag)
   with a simple web question whose answer you can check (e.g. the current latest LabVIEW release). Record: did it
   search (URLs in the answer), exit status, seconds, any denial text verbatim.
3. If a flag or settings change is needed in `tools/peer.ps1`, patch it with the Edit tool, keep read-only guarantees,
   and state the exact change. If Part A cannot be made to work within the failure budget, STOP and return FAIL with
   the denial text - do not run Part B.

## Part B - known-answer comparison (only if A passes)
- Pick 6-8 PAST web/fact questions from `archive/peer/` (fact / hypothesis / agy exchanges) whose answer was LATER
  verified against the machine, vendor files or a measurement (cite the verifying file:line for each). Prefer the
  narrow topics we actually ask (LabVIEW VI scripting / VI Server properties, NI forums, IMAQdx, NI-VISA, Windows
  COM). Write each as a neutral question that does not leak the answer; store `tools/bench/gsearch/cases.json` with
  question, known answer, verifying evidence.
- Arms, 2 repeats each, same question text:
  - `gemini`: peer.ps1 -Agent gemini (default model; add `gemini-3.1-pro-high` as a second arm only if `agy models`
    lists it)
  - `claude-fact`: peer.ps1 -Kind fact (the current default fact role, whatever the role table resolves to - record it
    via -DryRun)
- Per answer record: correct / partly / wrong vs the known answer, number of source URLs and whether at least one is
  a primary source (ni.com docs/forums, vendor file), seconds, Claude usd (from the claude arm's cost line; gemini = 0
  Claude usage).
- Score blind: a separate scorer call (claude, Sonnet, thin) gets question + known answer + the anonymised answer only.
- Write `tools/bench/gsearch/report_g1.md`: table per case x arm, totals, and the raw facts. No recommendation text
  beyond the numbers; the chat decides.

## Limits
Rig state 실험중: NO LabVIEW, GUI or hardware. Runner stays stopped. Do not change any role default in peer.ps1 (only
a flag needed to make gemini work headless). Do not edit CLAUDE.md or STATUS.md. Archive every peer exchange as
peer.ps1 does. Return one result/1 JSON object.
