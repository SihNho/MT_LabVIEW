---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, main-vi]
---

# panelwiring-test-oracle

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (41s)
- **why asked:** failed prediction in test_oppanelwiring.py T1/T2 (predicted every scratch object wired / exactly one orphan; observed 6 / 7). Was it the op or the test's oracle?
- **verdict:** ORACLE error confirmed (term_err=0 + wire_err=1055 on every zero row = valid terminal, no wire; the donor OpNodeInfo_v0 really has six bare controls). Test rewritten as baseline+delta (accepted as sufficient); the main VI's 10 bare terminals go into docs/main-vi-panel-map.md as 'terminal currently unwired', not 'legacy' - local-variable / property-node use is the next pass.

## Question

FAILED PREDICTION check (tools/bench/test_oppanelwiring.log, test tools/bench/test_oppanelwiring.py, op OpPanelWiring_v0 built by tools/recipes/build_oppanelwiring_v0.py). T1 predicted 'every panel object of the scratch (a copy of OpNodeInfo_v0.vi) has a wired diagram terminal' and observed wire UID 0 for 'Class Name','Class Name 2','Names','Names 2','index 2','error out' (6 of 10 objects). T2 constructed an orphan (create_control on an unwired terminal, then deleted the new wire) and predicted exactly ONE orphan; observed those same 6 plus the new 'error in (no error)' control = 7. Everything else passed: labels/Indicator flags/UIDs exact on the scratch, main VI 114 rows 60/54 with 10 orphans, every non-zero wire UID is a real Wire object, IsSource == not Indicator throughout, handles flat. MY EXPLANATION: the test's ORACLE was wrong, not the op - OpNodeInfo_v0 was built (tools/recipes/build_opfplabels.py 'strip to skeleton': every wire deleted except 106 vi path->Open VI Reference and 1066 index->Index Array) and its leftover controls Class Name/Class Name 2/Names/Names 2/index 2 (and the error out indicator) were never re-wired, so they ARE orphans; the constructed orphan shows up as exactly +1 over that baseline, which is the discriminating result the plan review asked for (wire UID 0 == unwired, arrays not shortened: 10 rows -> 11 rows). ATTACK: (1) could the six zeros instead be a failure mode of the op (e.g. Control.Terminal erroring for controls whose terminal exists but is unwired; check: the explicit TermErr/WireErr columns - the test did not print them, what would distinguish 'terminal ref invalid' from 'terminal fine, no wire'?); (2) is 'delta == the constructed control' a sufficient functional acceptance for the orphan semantics, or do you require the 3-element [valid, NaR, valid] probe from the plan review? (3) anything about the main VI's 10 orphans that should be cross-checked before they are written into docs/main-vi-panel-map.md as 'unwired legacy' (the user warned such leftovers exist)? Be brief.

## Answer

Your explanation survives.

1. The six zeros are genuine unwired terminals, not `Control.Terminal` failures. The log already prints the omitted discriminator: all six show `term_err=0`, `wire_err=1055`. Thus the terminal reference was obtained successfully; dereferencing the absent connected-wire reference failed. Error 1055 means an invalid object reference, consistent with Not-A-Refnum, while `Connected Wire` returns the terminal?셲 attached wire reference. [NI error 1055](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019L75SAE&l=en-US), [Connected Wire property](https://labviewwiki.org/wiki/Terminal_class/Connected_Wire_property)

2. The baseline-plus-one test is sufficient functional acceptance. It proves row preservation, default UID `0`, correct identification of the deliberately orphaned control, and no poisoning of adjacent iterations. The `[valid, NaR, valid]` probe is unnecessary because the existing 11-row result already contains multiple valid rows before and after invalid rows.

3. Document the main ten as **?쐔erminal currently unwired??*, not immediately as **?쐕nwired legacy.??* All ten also have `term_err=0`, `wire_err=1055`, so the wiring fact is strong. ?쏬egacy??is an intent/history claim; cross-check cheaply against event-structure registrations, property-node references/local-variable use, and visibility/tab ownership. An unwired terminal can still be used indirectly. Keep UID and error evidence in the map.

## Sources

(extract from answer)

## What was done with it

See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
