---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, vi-scripting]
---

# opexitwhile-fail1-duplicate-terminal-names

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (100s)
- **why asked:** failed prediction in build_opexitwhile.log run 1 (duplicate terminal names Outputs/Shift Registers collapsed in a name-keyed dict)
- **verdict:** unverified

## Question

FAILED PREDICTION check (brief). tools/bench/build_opexitwhile.log (tools/recipes/build_opexitwhile.py): swapping erdosmiller Exit For Loop.vi for Exit While Loop.vi in a copy of our OpExitLoop_v0 left the op broken (ExecState 0). The log shows the recipe wired Traverse's '# of Refs' output into the new node's 'Outputs' and 'Shift Registers' inputs. MY EXPLANATION: the recipe built a dict of terminals keyed by NAME; the erdosmiller connector has two terminals named 'Outputs' (input 5, output 6) and two named 'Shift Registers' (7 in, 8 out), so the dict kept the OUTPUT (wire 0) and the source search 'which terminal drives wire 0' matched the first unwired source ('# of Refs') - a recipe defect, not a library or LabVIEW problem. The later 'Stop Condition' attempts (Index Array element, then the whole Control Terminals array) could not be judged because the VI was already broken by those two wrong wires, and wire_indicators raised for the same reason (it requires ExecState 1 after wiring). FIX: key terminals by (name, direction), take the INPUT side for Outputs/Shift Registers, wire the error-out indicator LAST (after the stop condition), and re-test which Stop Condition type compiles (single terminal ref vs array). ATTACK: (a) agree? (b) from erdosmiller's Exit While Loop.vi / Exit For Loop.vi: is 'Stop Condition' a single terminal refnum or an array, and does 'Conditional Terminals' need anything for a While loop; (c) does Get Controls return terminal refs usable as 'Stop Condition' (a control's block-diagram terminal) - i.e. will wiring the control's terminal to the loop's conditional terminal make the loop stop when the Boolean is TRUE?

## Answer

Yes?봶ith one correction.

**(a) Diagnosis:** The recipe defect explains the failure. Duplicate-name dict entries selected the output-side `Outputs`/`Shift Registers` terminals, whose unwired `wire == 0` then falsely matched `# of Refs`, also unwired with `wire == 0`. So the real bug is both:

- losing direction when keying terminals; and
- treating wire ID `0` as a valid connection identity.

Require `(name, is_source)` and never source-match unless `wire != 0`. Since `ExecState` was already 0 immediately after dropping the replacement, then remained broken after those erroneous wires, neither Stop Condition experiment was diagnostic. Wiring the indicator last is correct.

**(b) Connector contract:** `Stop Condition` should be **one terminal refnum**, not an array. Thus `Index Array.element ??Stop Condition` is the plausible route; the whole `Control Terminals[]` is not. `Conditional Terminals` should not require anything for an ordinary While Loop: a While Loop inherently has one conditional terminal, whereas a For Loop?셲 conditional terminal is optional and must be enabled. NI confirms that While Loops inherently evaluate their conditional terminal and that conditional For Loop execution must first be configured. [NI While Loop guide](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YJYUCA4), [NI conditional For Loop guide](https://www.ni.com/en/support/documentation/supplemental/07/configuring-labview-for-loops-to-exit-conditionally.html)

I cannot prove the exact erdosmiller connector datatypes without a plain-text connector-pane/type reporter for those two VIs; the public repository contains compiled VIs rather than readable source. [erdosmiller/lv-scripting](https://github.com/erdosmiller/lv-scripting)

**(c) Get Controls:** Yes, an indexed `Control Terminals` element is the appropriate kind of block-diagram terminal reference to supply as `Stop Condition`; VI Scripting connects terminal objects using the terminal `Connect Wire` method. [NI scripting discussion/example](https://forums.ni.com/t5/LabVIEW/Wiring-the-conditional-terminal-of-a-while-loop-created-by/m-p/2115512)

But location matters: if the Boolean terminal remains **outside** the While Loop, its value is read before loop execution and changing the front-panel control will not stop the running loop. The terminal must be inside the loop?봮r otherwise provide a Boolean evaluated inside every iteration. NI explicitly documents the outside-terminal infinite-loop failure. [NI LabVIEW User Manual](https://download.ni.com/support/manuals/320999e.pdf)

**Retest prediction:** after fixing direction and excluding wire `0`, the scalar `Index Array.element ??Stop Condition` attempt should compile provided the selected target control is Boolean and its terminal is placed/evaluated inside the loop. Leave `Conditional Terminals` unwired initially.

## Sources

(extract from answer)

## What was done with it

Fixed both defects the reviewer named (direction-keyed terminals, wire 0 never matches); rerun built the op with the scalar Index Array element on Stop Condition (ExecState 1), and test_opexitwhile.log passed 5/5 including a real run stopped by the control. The 'terminal must be inside the loop' warning went into docs/stage2-plan.md item 7. Verdict: correct.
