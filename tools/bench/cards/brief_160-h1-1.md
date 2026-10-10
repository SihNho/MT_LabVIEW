---
card: 160-h1-1
status: current
date: 2026-10-10
---
# Brief 160-h1-1 (assignment 160-1) - OFFLINE: ~60 one-line function descriptions in `docs/fn_descriptions.json` (carry item, chat-T8)

Same work as card 159-a5-1 (brief `tools/bench/cards/brief_159-a5-1.md`, facts `tools/bench/diag_c159_a5_1_facts.md`) - read both first; the json now has 245 entries.
No LabVIEW. Only `docs/fn_descriptions.json` (plus the files `gen_capabilities` rewrites) and `tools/bench/diag_c160_h1_1_*` are written. No edit to any `.py`.
Read `docs/script-writing.md` rule 9 and the json's `about` field. No card edits a tool file beside this one, so every shared tool is open to describe, including the
functions added this round: `stagekit` 2733-2869 (`made_symbols`, `used_symbols`, `map_symbols`, `map_frames`, `apply_map`, `bound_from_cmap`), `stagesim.termless_wire`,
and the `stagexec` `delete_wire` branch (a branch is not a function: describe only functions).

## What to do
1. List the undocumented public functions with the generator's helper (`tools/bench/diag_c158_a2_5_list.py` shows how; call, do not re-implement). Order: the functions added
   this round first, then the remaining stage toolchain (`stagexec`, `stagesim`, `addrcheck`, `vigraph`, `stagekit`, `stage_prerun`), then the other shared tools by use.
2. Add about 60 entries `"<module>.<function>"` (method `"Class.method"`): ONE sentence saying what the function does and returns, verified by reading its code. A function whose
   behaviour you could not establish gets no entry (list it under `OPEN:`). Each entry <= 300 chars.
3. After the edit: the json parses; the count rose by about 60; no existing entry changed or removed (compare with `git show HEAD:docs/fn_descriptions.json` AND with the pinned
   input md5 bf3224bd); run `py tools/gen_capabilities.py` (its documented rewrite mode, as 159-a5-1 did) and `py tools/doc_lint.py`; quote L12 for the new keys and name any
   tracked file the tools rewrite.

## Report `tools/bench/diag_c160_h1_1_facts.md` (<= 25 lines)
Entry count before / after, added keys by module (counts), md5 of the json before / after, the L12 result, 3 sample entries with the code lines they were read from,
`OPEN:` for skipped functions. md5 unchanged: stagekit 1441bb4c, stagesim a3261b56, stagexec c4a6e0b6, stage_prerun 7605116f; `tools/hooks` untouched.
