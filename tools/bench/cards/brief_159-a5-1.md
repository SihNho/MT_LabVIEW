---
card: 159-a5-1
status: current
date: 2026-10-10
---
# Brief 159-a5-1 (assignment 159-1) - OFFLINE: ~60 one-line function descriptions in `docs/fn_descriptions.json` (carry item, chat-T8)

Same work as card 158-a2-5 (brief `tools/bench/cards/brief_158-a2-5.md`, facts `tools/bench/diag_c158_a2_5_facts.md`) - read both first; the json now has 185 entries.
No LabVIEW. Only `docs/fn_descriptions.json` (plus the files `gen_capabilities` rewrites, see below) and `tools/bench/diag_c159_a5_1_*` are written. No edit to any `.py`.
Read `docs/script-writing.md` rule 9 and the json's `about` field.

Beside this card, card 159-a4-1 edits `tools/stage_prerun.py` and `tools/stagekit.py`: add NO entries for functions of those two files (their bodies are changing).

## What to do
1. List the undocumented public functions with the generator's helper (`tools/bench/diag_c158_a2_5_list.py` shows how; call, do not re-implement). Order: the remaining
   stage toolchain first (`stagexec` 32 were left, `stagesim`, `addrcheck`, `vigraph`), then the other shared tools by use.
2. Add about 60 entries `"<module>.<function>"` (method `"Class.method"`): ONE sentence saying what the function does and returns, verified by reading its code. A function whose
   behaviour you could not establish gets no entry (list it under `OPEN:`). Each entry <= 300 chars.
3. After the edit: the json parses; the count rose by about 60; no existing entry changed or removed (compare with `git show HEAD:docs/fn_descriptions.json` AND with the pinned
   input md5 c54377ea); run `py tools/gen_capabilities.py` (its documented rewrite mode, as 158-a2-5 did) and `py tools/doc_lint.py`; quote L12 for the new keys and name any tracked
   file the tools rewrite.

## Report `tools/bench/diag_c159_a5_1_facts.md` (<= 25 lines)
Entry count before / after, added keys by module (counts), md5 of the json before / after, the L12 result, 3 sample entries with the code lines they were read from, `OPEN:` for skipped functions.
