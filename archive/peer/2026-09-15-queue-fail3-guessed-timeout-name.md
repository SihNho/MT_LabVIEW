---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, producer-consumer]
---

# queue-fail3-guessed-timeout-name

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (57s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

BRIEF ATTACK (LabVIEW 2026 VI Scripting over COM). Log: tools/bench/build_track_v6_queue.log run 3 (100/101 PASS: PathToStr.vi, head + KT, 7 Obtains, pool loop, ACQ loop, TRK loop with three registers all passed). The stop: in the SINK loop, count_tunnel() called gscript.wire_control(['Control Names'] -> Dequeue.'timeout') and erdosmiller Wire Inputs.vi returned error 5001 (destination name not found).
MY DIAGNOSIS: a guessed terminal name. The Dequeue Element node's exact input is 'timeout in ms (-1)' (measured in tools/bench/test_opqueue.log: Dequeue terminals [queue, 'timeout in ms (-1)', 'error in (no error)', 'queue out', 'element', 'timed out?', 'error out']); docs/NAMES.md's standing rule is "names are exact bytes, never guess from absence". The TRK loop's count tunnel used the kernel's real 'cross size' input and passed. Fix: both count_tunnel calls (sink, drain) use 'timeout in ms (-1)'.
Attack: (1) any other reading of 5001 here (e.g. Wire Inputs refusing a String[] source into an I32 sink BEFORE the tunnel flip - no: the TRK count tunnel went String[] into 'cross size' (I32) and passed, the wire being broken until deleted)? (2) after the fix, the count tunnel deletes the inner wire that briefly connected String -> 'timeout in ms (-1)': can that transient broken wire leave the Dequeue's timeout input in a changed state (it must stay unwired = -1 blocking)? Confirm by readback: node_terms shows 'timeout in ms (-1)' wire 0 after deletion. (3) anything else in the remaining unexecuted phases (sink dequeues -> 4 indexed outputs -> indicators; teardown join via exported 'queue out'/'error out' last-value tunnels; drain; 7 releases) that would fail on a name - list the exact terminal names the recipe must use for Release Queue (queue, 'force destroy? (F)', 'error in (no error)' -> 'error out'?) from NI's Release Queue pane. Read-only; cite what you read.


## Answer

Your diagnosis is correct. I see no credible type-mismatch interpretation of this 5001.

1. Error 5001

The failure occurred during destination-name lookup:

`wire_control ['Control Names'] -> Function.['timeout']`

The measured Dequeue terminal is exactly `timeout in ms (-1)`, while no terminal named `timeout` exists. The same String[]?묲32 transient connection already succeeded at TRK `cross size`, proving Wire Inputs does not reject the call at this stage merely because the provisional wire is broken. See [build_track_v6_queue.log](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/build_track_v6_queue.log:82>) and [test_opqueue.log](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/test_opqueue.log:30>).

Verdict: change both SINK and drain calls to `timeout in ms (-1)`. No competing reading is supported.

2. Transient broken wire

Deleting the inner wire is sufficient. It does not write a value or create a constant; it leaves the timeout terminal unwired. The required readback is exactly:

- terminal name: `timeout in ms (-1)`
- sink terminal
- `wire == 0`
- tunnel remains `IndexMode == 1`

An unwired Dequeue timeout consequently retains its default ??/blocking behavior; NI discussions explicitly confirm that Dequeue defaults to ?? and waits indefinitely ([NI Community](https://forums.ni.com/t5/LabVIEW/SubVI-locks-up-main-VI/td-p/2904518/page/2), [NI Community explanation of ?? behavior](https://forums.ni.com/t5/LabVIEW/Does-setting-Dequeue-Element-Timeout-to-a-value-other-than-1/td-p/4168887)).

I would make the gate check both the terminal name and `wire == 0`, not merely ?쐓ome inner terminal is unwired.??
3. Remaining exact names

The recipe?셲 remaining names agree with the measured queue-node listings:

- Dequeue inputs: `queue`, `timeout in ms (-1)`, `error in (no error)`
- Dequeue outputs: `queue out`, `element`, `timed out?`, `error out`
- Release inputs: `queue`, `force destroy? (F)`, `error in (no error)`
- Release outputs: `queue name`, `remaining elements`, `error out`

The Release pane labels are independently visible in this published LabVIEW diagram ([PDF, p. 148](https://riull.ull.es/xmlui/bitstream/handle/915/967/Puesta%20a%20punto%20de%20sistema%20de%20electroencefalografia%20portatil.pdf?isAllowed=y&sequence=1)). NI also confirms the optional input is named `force destroy?` and that TRUE destroys all references ([NI KnowledgeBase](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000kGUJSA2)).

Your seven obtains paired with seven releases do not require wiring `force destroy? (F)`; leaving it unwired/False is correct. NI says ordinary destruction requires as many Release calls as Obtain calls ([NI KnowledgeBase](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000kGUJSA2)).

One caution: `queue name` and `remaining elements` exist even though the local NAMES entry currently abbreviates Release as only `queue`. The current recipe does not address those outputs, so this omission cannot break it. The actual names it uses??queue`, `error in (no error)`, `error out`?봞re correct.

No additional guessed-name hazard is apparent in the unexecuted phases. The sink outputs, loop exports, drain and release chain all use names already measured elsewhere in the same run or in `test_opqueue.log`.

## Sources

(extract from answer)

## What was done with it

Fix confirmed (both count tunnels use `timeout in ms (-1)`); the count-tunnel gate now also reads the named sink
terminal back as wire 0; NAMES.md records the Enqueue/Dequeue/Release terminal names (Release outputs `queue
name`, `remaining elements` added from this answer). Rerun: `tools/bench/build_track_v6_queue.log` (run 4).
