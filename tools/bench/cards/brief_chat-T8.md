# Brief chat-T8 - function descriptions in a side file (user 2026-10-09 "권장안대로 처리")

Card chat-T7 (result_chat-T7.json) built the generated function list (185 shared files, 2432 functions, 1155 without a
docstring; 325 of them in the 46 shared tools/*.py). Writing docstrings into existing functions would shift 900+
`file:line` citations. The user chose: descriptions of EXISTING functions live in a side file; NEW functions carry a
docstring (docs/script-writing.md rule 9).

## Do (offline, labview none; the cycle runner is running - touch only the files below)
1. Side file `docs/fn_descriptions.json`: `{"schema":"fn-descriptions/1","about":"...","items":{"<module>.<function>":
   "<one line: what it does, what it returns>"}}`. Start it with an EMPTY items map plus 3 real examples you verify by
   reading the code (pick functions T7 listed as undocumented in stagexec/stage_prerun/stagesim).
2. `tools/gen_capabilities.py`: the description column = first docstring line, else the side file's entry, else
   "(undocumented)". Mark the source (docstring / side file) in the row. Report the count still undocumented per module
   in the block header, so the backlog is visible.
3. doc_lint / drift: a side-file key whose function no longer exists is a WARN line (stale description).
4. Self-tests: extend tools/bench/selftest_t7_capabilities.py (docstring wins over side file; side file used when no
   docstring; stale key -> WARN; undocumented count right); keep its 10 existing cases green. Regenerate the block once.
5. docs/script-writing.md rule 9: add one sentence - an EXISTING function without a docstring gets its description in
   docs/fn_descriptions.json (no line shift); a NEW function gets a docstring.
Commit by explicit path. Return one result/1 JSON.

## Limits
Edit/Write only, no tools/hooks edits, no LabVIEW. Do not write the 325 descriptions - that is a later runner card.
