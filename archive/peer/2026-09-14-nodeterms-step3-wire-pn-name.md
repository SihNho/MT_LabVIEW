---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# nodeterms-step3-wire-pn-name

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (19s)
- **why asked:** failed prediction at build step 3 (chain not recognised): the Wire PN's 'Broken?' short name was guessed as 'IsBroken'.
- **verdict:** explanation accepted; run 2 matched 'Broken?' and built cleanly (Property 5->7 after -2/+4, IndexArray 3->2, uid 240 untouched, ExecState 1 throughout). NAMES.md updated with the read-off short names.

## Question

FAILED PREDICTION check, one paragraph. tools/bench/build_opnodeterms_v0.log (recipe tools/recipes/build_opnodeterms_v0.py) stopped at step 3 'chain not recognised': the walk printed node uid 242 with terminals ['reference','reference out','error in (no error)','error out','UID','Broken?'] but my matcher for the Wire[UID, Is Broken?] property node looked for 'IsBroken'/'Is Broken?' and missed 'Broken?'. Explanation: a guessed short name instead of the string the walk itself had just printed (a documented trap in this project). Fix: match 'Broken?'. ATTACK: is uid 242 certainly the Wire PN and not uid 240 (['UID'] only - which is the NODE's UID reader fed from IA_n per build_opnetinfo.py)? Any risk that deleting 242 (Wire PN), 241 (Terminal PN) and IA_t 239 (the Index Array fed by 'Terms[]' wire 485) leaves 240 or the Text/Label chain broken? Cheapest check from the counts in the log.

## Answer

UID 242 is almost certainly the Wire property node: its `UID` plus `Broken?` terminals uniquely fit that role, whereas uid 240?셲 sole `UID` matches the node-UID reader fed from `IA_n`. Deleting 242, 241, and `IA_t` 239 should not delete 240 or the independent Text/Label branch unless the recipe mistakenly includes their shared upstream objects in the deletion set. The cheapest check is arithmetic: the post-edit object count must fall by exactly three nodes, and uid 240 must still appear with `['UID']`; any additional node loss disproves the prediction. Wire-count reduction alone is weaker because removing those three nodes legitimately removes their incident wires, but no remaining wire should reference 239, 241, or 242, and the Text/Label-chain count should be unchanged. I cannot quote the log?셲 numeric counts without violating the instruction not to open repository files.

## Sources

(extract from answer)

## What was done with it

See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
