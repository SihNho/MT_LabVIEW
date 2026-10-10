---
card: 158-a2-5
status: current
date: 2026-10-10
---
# Brief 158-a2-5 (assignment 158-2) - OFFLINE: ~60 one-line function descriptions in `docs/fn_descriptions.json` (carry item, chat-T8)

No LabVIEW. Only `docs/fn_descriptions.json` and `tools/bench/diag_c158_a2_5_*` are written. No edit to any `.py` (a docstring would shift every
`file:line` citation; that is why the descriptions live in the json). Read `docs/script-writing.md` rule 9 and the json's `about` field.

## What to do
1. Find public functions of the shared tools files that have NO docstring and NO entry in the json: the generator `tools/gen_capabilities.py`
   prints `(undocumented)` for them (read how it decides; call it or its helper, do not re-implement). Order candidates by use: the stage
   toolchain first (`stagexec`, `stagekit`, `stagesim`, `addrcheck`, `vigraph`, `stage_prerun`), then the rest.
2. Add about 60 entries `"<module>.<function>"` (method: `"Class.method"`) in the existing style: ONE sentence saying what the function does
   and what it returns, **verified by reading its code**, not guessed from the name. A function whose behaviour you could not establish gets
   no entry (list it under `OPEN:`).
3. After the edit: the json parses; the item count rose by about 60; no existing entry is changed or removed; run
   `py tools/gen_capabilities.py` (or its documented check mode) and `py tools/doc_lint.py` and quote whether L12 (key whose function is gone)
   is clean for the new keys. If either tool rewrites a tracked file, say which.

## Report `tools/bench/diag_c158_a2_5_facts.md` (<= 25 lines)
Entry count before / after, the list of added keys by module (counts), md5 of the json before / after, the L12 result, 3 sample entries
with the code lines they were read from, `OPEN:` for skipped functions. Failure budget 2.
