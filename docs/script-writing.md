---
type: guideline
status: current
date: 2026-10-09
tags: [scripts, stagekit, recipes]
---

# How to write scripts in this project

User, 2026-10-09: *"보통 같은 함수가 계속 반복되면 복사 붙여넣기 대신 공통 함수로 만들고 호출하지 않아?"* ·
*"코드가 길어질수도 있지 그걸 기계적으로 막기는 어렵겠고, 재료 세션 및 배정 세션에 .md파일로 지침을 전달해야겠는데?
지금것도 당연히 공용함수로 빼야하고 추가로 다른 작업을 할 때도 스크립트 제대로 작성하도록"*.

Who reads this: every MATERIAL session before it writes or edits a script, and every ASSIGNMENT session (and the
judgement session) before it writes a brief or a purpose that asks for a script.

## Why this file exists

The P4 batch recipes were made by copying the previous batch's recipe (briefs said "copy the s06 pair", purposes said
"recipes copied from the s03v18 pair"). The open-rows check (PB) ended up inline in 21 recipe files
(`tools/recipes/stage_d1_ring_*.py`, e.g. `stage_d1_ring_p4_s06v18.py:140-149`), and the recipes grew from ~100 to
~200 lines. When card chat-T6 moved the result gates to position keys in `tools/stagekit.py`, the 21 inline copies kept
comparing by name, and cycle 153 failed on it (fp-70). Copying was rewarded (a "proven pattern" skips the prior-art
review; a diff-only review never re-reads copied lines) and nobody's job was to stop it. This file makes it everyone's.

## The rules

1. **Logic lives once.** A block of logic needed in a second place is moved into a shared module and CALLED from both.
   Never paste it. "It worked in the last recipe" is a reason to call the same function, not to copy its text.
   - Stage / recipe / diagnostic machinery → `tools/stagekit.py` (or the module that already owns the topic:
     `stagexec`, `stagesim`, `stage_prerun`, `addrcheck`, `elrule`, `vigraph`, `protocol`, `gscript`).
   - Bench-only helpers shared by several `tools/bench/*.py` → a small module under `tools/` with a self-test, not
     a copy in each script.
2. **A recipe holds inputs and calls.** Plan path, base/start/cut, pred, gates to apply, labels — plus calls into
   stagekit. If a recipe contains a computation (a diff, a key builder, a comparison, a parse) that another recipe also
   needs, that computation belongs in the shared module.
3. **Length is not the measure; duplication is.** A long script is fine when its content is specific to that job. A
   short script that repeats another script's logic is not.
4. **Found a duplicate? Extract first, then use it.** If the code you need already exists inline in another script,
   extract it into the shared module (with a self-test that re-runs at least one recorded case), switch YOUR script to
   call it, and report the old copies in `facts` (file:line). Do not rewrite old recipes that already ran — they are the
   record of what ran; new scripts call the shared function. If the extraction is outside your card's `write` globs,
   return with `open:` naming the block and its copies, instead of pasting it.
5. **Change behaviour in ONE place.** When a shared rule changes (e.g. terminal keys by position, PD366), the change is
   made in the shared function and every NEW script inherits it. If you find a caller that bypasses the shared function,
   that is a defect to report, not a pattern to follow.
6. **Briefs and purposes ask for calls, not copies.** An assignment / judgement brief says "use `stagekit.<fn>` for X"
   or "the s06 recipe's inputs, on the shared gates", never "copy the s06 pair". If the function you would name does not
   exist yet, the brief's first step is to make it (a tooling card that extracts it), then the recipe card.
7. **Every shared function gets a self-test** that replays recorded data (stored graph reads, scratch logs), so a later
   change cannot silently alter what every recipe checks.
8. **Look it up before you write it.** The function list is the generated block at the end of
   `docs/toolkit-capabilities.md` (`tools/gen_capabilities.py`): every public function of the shared modules with its
   signature, one-line description and self-test. Search it (and `grep "def "` in the module) before writing any logic;
   a function that already exists is called, not re-written.
9. **A new or changed shared function carries a docstring** whose first line says what it does and what it returns,
   and names its self-test. The list is regenerated from those docstrings at every cycle end (user 2026-10-09: "전부
   적용"), so a function without a docstring shows up undocumented to every later session. An EXISTING function without
   a docstring gets its one-line description in `docs/fn_descriptions.json` (key `<module>.<function>`), not a docstring,
   so no `file:line` citation shifts; a NEW function gets a docstring (user 2026-10-09 "권장안대로 처리", card chat-T8).

### Write less (user 2026-10-12 "추가하고 테스트"; taken from the Ponytail ruleset, DietrichGebert/ponytail
### skills/ponytail/SKILL.md, after a read-only review - the plugin itself is NOT installed)

These never override rule 1a: the original's computation is never "simplified", shortened or deleted.

10. **Ask whether it needs to exist before writing it.** No option, flag, parameter or "for later" branch the card did
    not ask for. Name what you skipped in ONE line of the result card's `facts` ("skipped: …").
11. **Standard library or an installed package before new code.** Never add a dependency for a few lines.
12. **Code moved into a shared module keeps its error handling and validation unchanged** (rule 4's extraction is a
    move, not a rewrite).
13. **A shortcut with a known limit says so in place:** `# shortcut: <limit>, <when to upgrade>`.
14. **New non-trivial logic in ANY script (a branch, a parser, a comparison) leaves at least one `assert`-based
    self-check** that runs with the script - not only the shared functions of rule 7.
15. **Between options of the same size, take the one that is correct at the edges** (empty input, one row, missing
    file). A one-liner that needs decoding is not short.

The other script rules still hold: scope header (`CLAUDE.md` "ERRORS ARE CAUGHT AT THE START"), `RESULT {...}` line,
runs only under `bgrun --material`, names from `docs/NAMES.md`, Edit/Write tools only.
