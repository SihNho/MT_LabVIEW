# Brief chat-L1 - codebase lint (user 2026-10-09: lint the codebase after the next cycle; ruff installed with the user's OK)

Runner is STOPPED (STATUS 'STOP - CODEBASE LINT'). Offline only, labview none. Read `docs/script-writing.md` first.

Already measured by the chat (`py -m ruff check tools --select F,E9`, ruff 0.16.10): 137 F401 unused-import, 93 F841
unused-variable, 61 F821 undefined-name, 9 F541, 1 F601, 1 F811. Every F821/F601 is in 6 old one-off bench scripts that no
other file imports (diag_m8b_frame_source.py 48, diag_c99_files3/4/5, diag_c92c_capread_selftest, plan_ring_p3b_make);
the only shared-module hit is `tools/stagexec.py:4177` F811 (a second `import hashlib`, harmless). The shared-file list
is `tools/bench/capabilities_shared.json` (written by gen_capabilities from the import graph).

## Do
1. `ruff.toml` at the project root: target py310, select F + E9 (+ B006/B008 mutable defaults, + E711/E712 comparisons to
   None/True, + PLW0602/PLW0603 global misuse if available), exclude archive/ and worktrees; a tools/lint.py wrapper (or a
   documented one-liner) that prints counts per rule and per folder (shared files vs recipes vs one-off bench).
2. REAL-BUG pass on SHARED files only (tools/*.py, hooks, and every file in capabilities_shared.json): list each finding
   of the bug classes (undefined name, redefinition, repeated dict key, mutable default, ==None) with file:line and a
   one-line verdict (bug / harmless / false positive). Fix a confirmed bug only when the fix does NOT shift lines (same
   line edit); otherwise list it. Re-run the module's self-test after each fix.
3. CLEANUP list (no edits: removing lines shifts file:line citations): F401/F841/F541 in shared files, per file.
4. DUPLICATE CODE: write `tools/dupcheck.py` (header at top, docstring, self-test) - normalised windows of >= 8 logical
   lines (strip comments/whitespace, literal numbers/strings -> placeholders) across tools/*.py, tools/hooks, tools/recipes
   and the shared bench files; report every block found in >= 2 files: files:lines, size, what it does (one line). Group
   the recipes' own repeats separately (old recipes are records - only list them).
5. Report `docs/lint-2026-10-09.md`: counts, the shared-file bug table, the duplicate-block table ranked by (copies x
   size), and a short "what to extract next" list in the docs/script-writing.md sense. Commit by explicit path.

## Limits
Edit/Write only; no tools/hooks edits (list hook findings for the chat); no line-shifting edits in existing files; no
LabVIEW. Return one result/1 JSON.
