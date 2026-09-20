# priorart-testrun3-sharded

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** (cost not parsed: 잘못된 개체가 전달되었습니다. ':' 또는 '}'가 필요합니다. (5520): {"duration_api_ms":219276,"stop_reason":"end_turn","session_id":"f67de2d1-5655-4e66-987f-89f09c2b755a","total_cost_usd":2.5325275000000005,"usage":{"input_tokens":28,"cache_creation_input_tokens":128027,"cache_read_input_tokens":1675935,"output_tokens":16566,"output_tokens_details":{"thinking_tokens":6578},"server_tool_use":{"web_search_requests":0,"web_fetch_requests":0},"service_tier":"standard","cache_creation":{"ephemeral_1h_input_tokens":128027,"ephemeral_5m_input_tokens":0},"inference_geo":"not_available","iterations":[{"input_tokens":2,"output_tokens":6576,"cache_read_input_tokens":148638,"cache_creation_input_tokens":2129,"cache_creation":{"ephemeral_5m_input_tokens":0,"ephemeral_1h_input_tokens":2129},"type":"message"}],"speed":"standard"},"modelUsage":{"claude-opus-5":{"inputTokens":28,"outputTokens":16566,"cacheReadInputTokens":1675935,"cacheCreationInputTokens":128027,"webSearchRequests":0,"costUSD":2.5325275000000005,"contextWindow":1000000,"maxOutputTokens":64000,"canonicalModel":"claude-opus-5","provider":"firstParty","costBasis":"list"}},"permission_denials":[],"terminal_reason":"completed","fast_mode_state":"off","fast_mode_disabled_reason":"sdk_opt_in_required","subagent_stats":{"spawned":0,"requested":{"background":0,"foreground":0,"unset":0},"started_in_background":0,"max_depth":0,"spawned_by_subagents":0,"completed":0,"failed":0,"killed":{"parent":0,"user":0,"system":0},"refused":{"depth_limit":0,"concurrency_limit":0,"budget":0},"by_type":{}},"is_error":false,"num_turns":26,"subtype":"success","api_error_status":null,"result":"# PRIOR-ART REVIEW ??\"next cycle of the V6 parallelisation project\" (direction-change)\n\n**Verdict up front: nothing in the five steps is novel. Four of the five were decided, measured or failed inside this project ??three of them on 2026-09-15, the same day this plan was written.** Step 4 additionally restates a specific factual error that a prior-art review already caught and that the recipe on disk has already been corrected for.\n\n---\n\n## PART A ??THE DIRECTION\n\n### A1 쨌 SETTLED ALREADY ??step 2's \"central risk\" was answered 2026-09-15 at 18:27 and 18:30\n\nThe plan says: *\"everything downstream depends on an operation the fleet has never performed: relocating an existing node from the frame loop into a new loop inside the same VI??Before anything else is built I will establish whether LabVIEW VI Scripting can move a node to a different diagram.\"*\n\nThat is already answered, twice, with machine gates:\n\n- `STATUS.md:269` ??*\"### 0a ANSWERED, 2026-09-15 18:27 ??the in-copy migration route WORKS (attempt 4, 3/3, `tools/recipes/probe_migrate_v2.py`)\"*\n- `STATUS.md:281` ??*\"create a loop in an existing VI ??drop the same subVI inside it ??wire a control across the border into a named terminal ??delete the original. **`GObject.Move` is not needed and was never used.**\"*\n- `STATUS.md:283` ??*\"### ??SETTLED by attempt 5 (`tools/recipes/probe_migrate_v3.py`, 5/5, 18:30) ??the migrated state COMPILES\"*\n- `STATUS.md:297-299` ??*\"So the in-copy restructure method is proven end to end??What remains untested is SCALE (75 nodes, 21 sibling couplings) and RUNTIME behaviour, **not feasibility**.\"*\n- Raw evidence: `tools/bench/probe_migrate_v2.log:3-10` (K1/K2/K3 pass, body uid 472 at Traverse index 1) and `tools/bench/probe_migrate_v3.log:12` ??*\"PASS M5 THE MIGRATED STATE COMPILES (ExecState == 1)\"*.\n\nAnd the framing ??\"move a node\" as the indispensable primitive ??was retired two days earlier: `docs/toolkit-capabilities.md:367` ??*\"### RESOLVED the same day ??the build route is clear, and 'move a node' was never needed\"*, with `docs/toolkit-capabilities.md:384-386` correcting the very inference the plan revives (*\"The earlier probe blamed `move_object` for breaking the VI. It did not: ExecState was already 0 immediately after `for_loop`\"*).\n\n**What my citation does NOT cover:** scale and runtime. `STATUS.md:299` explicitly leaves 75 nodes / 21 sibling couplings untested, and `STATUS.md` line 344 (step 0b) is the open item. A plan whose step 2 is *\"prove it on one harmless fragment in a COPY of the main VI\"* would be novel. *\"Establish whether VI Scripting can move a node\"* is not.\n\n### A2 쨌 REFUTED ALREADY ??step 1's ASI-first ordering was killed by the plan review on 2026-09-15\n\n- `archive/peer/2026-09-15-restructure-in-copy-plan.md:9` records the reviewed ordering as *\"kernel -> ASI serial -> display -> scheduler/writer\"*, and :11-15 kills it: *\"The 5.06 ms 'kernel + one serial round trip' is **not** the ordinary-frame cost??So 'move ASI out to win ~2.5 ms per frame' is void, and ASI-first ordering has no performance support.\"*\n- :93 ??*\"replace 'kernel, then ASI, then display' with 'measure unconditional latency, then construct one live vertical slice, then split whichever measured owner dominates.'\"*\n- Adopted into STATUS the same day: `STATUS.md:124` ??*\"The SHELL decision stands; the ORDERING was refuted by the plan review and is replaced\"*; `STATUS.md:129` ??*\"There is no ~2.5 ms ASI prize on ordinary frames, so ASI-first has no performance support\"*; `STATUS.md:133` ??step 1 is now *\"measure the unconditional per-frame path ??what actually executes every frame, p50 **and p99** | replaces all guessed orderings.\"*\n\n**Does the refutation still apply?** Its *premise* was weakened by the user ??`docs/camera-acquisition-facts.md:142` records *\"USER CORRECTION, 2026-09-15: ?ㅼ젣 ?ъ슜 寃곌낵 ASI濡?focus 議곗젙? 苑ㅻ굹 鍮덈쾲?섍쾶 諛쒖깮??"* ??so an ASI-owned loop is still justified. But :148-149 states the justification precisely: *\"The consequence is **dropped frames during focus adjustment**, i.e. a p99 / tail-latency defect, not an average-throughput one.\"* The plan's stated reason (\"the largest single win available\", ~2.5 ms, 150??00 Hz) is the refuted one, not the surviving one. Releasing this needs you to show that `STATUS.md:133` does not already order the measurement first.\n\n### A3 쨌 CONTRADICTED ??two separate cited facts\n\n**(i) The 5.06 ms / 2.5 ms figure contradicts its own source file, 55 lines above where it is stated.**\n\n- Plan's side ??`docs/camera-acquisition-facts.md:195-198`: *\"Kernel + a single serial round trip is **5.06 ms of the 6.00 ms**??it is the case for moving the serial read and the display out of the frame loop: doing so returns ~2.5 ms, which is the difference between 150 Hz and 200 Hz.\"*\n- The same file's answer ??`docs/camera-acquisition-facts.md:140`: *\"### ANSWERED: the frame loop does NOT transact serial every iteration (2026-09-12)\"*, :162 (the VISA case structure is a *\"gate only\"*), :169-171: *\"**So serial does not block 150 Hz.** It is paid only while a focus key is held\"*, and :177: *\"**What IS paid every frame is two `Value` property nodes**.\"*\n\nThis exact misreading has already been recorded once: `archive/peer/2026-09-15-restructure-in-copy-plan.md:15` ??*\"summation at line 183 and missed its own answer 44 lines earlier.\"* Citing :195 without :140 is the same defect a second time.\n\n**(ii) Step 4's \"Those are the two consumers of wire 751\" is false ??there are three.**\n\nFrom the census the plan's own uids come from, `tools/bench/census_opwiresource_v5.log`:\n\n| line | node | terminal | wire |\n|---|---|---|---|\n| :181 | uid **157** | `Owner` | 751 *(the source)* |\n| :161 | uid **482** | `reference` | **751** |\n| :183 | uid 163 | `reference` | 751 |\n| :221 | uid 1221 | `reference` | 751 |\n\nNode 482 is a Property Node reading `ClassName` (`census_opwiresource_v5.log:165`). It is the third consumer, and it is not in the plan.\n\n### A4 쨌 UNREAD EVIDENCE ??`tools/recipes/build_opownerchain_v0.py`, which already contains the fix for A3(ii)\n\nThe recipe the plan proposes to write exists and has already been corrected for precisely this error:\n\n- `tools/recipes/build_opownerchain_v0.py:64-68` ??*\"**THE THIRD CONSUMER.** The prior-art review (`archive/peer/2026-09-15-priorart-ownerchain.md`?? caught this before the build was ever launched: wire 751 has THREE consumers, not two ??node 163, node 1221 AND **node 482** ??and `tools/bench/build_opwiresource_v5.log:35-39` records that the first v5 rewire failed for exactly this reason??**I read past it.** All three are rewired below.\"*\n- `:69` ??`REWIRE_SINKS = [N_OWNER_CLASSNAME, N_CASTGOBJ, N_OWNER_CLASSNAME2]`.\n\nAlso unconsulted: `docs/NAMES.md:509-532` (for step 5), `docs/toolkit-capabilities.md:244` and `tools/bench/build_opgeterrors.log` (for step 3), and `STATUS.md:269-299` (for step 2).\n\n---\n\n## PART B ??THE ARTIFACTS\n\n### B1 쨌 ALREADY BUILT ??both artifacts the plan proposes are already written recipes\n\n| plan step | file on disk |\n|---|---|\n| 3 ??`VI.Get Errors` (452) as an op | `tools/recipes/build_opgeterrors.py:1-7` ??*\"OpGetErrors_v0.vi: read a VI's ERROR LIST by script (VI method `Get Errors`, ID 0x452????build_invoke(\"VI Server:VI\", \"452\"), branch 'vi reference' -> Invoke.reference, indicators on every Invoke output\"* |\n| 4 ??`OpOwnerChain_v0` from `OpWireSource_v5` | `tools/recipes/build_opownerchain_v0.py:1-41` (full spec + prediction contract B1?밄6), `:57-69` (uid table, corrected rewire list) |\n\nThe plan describes both as work to be done. Neither `OpGetErrors_v0.vi` nor `OpOwnerChain_v0.vi` is in the 168-VI claudeDev listing (`archive/peer/2026-09-15-priorart-ownerchain.md:82`), so the *VIs* do not exist ??but the recipes, uids and acceptance gates do, and step 4's design regresses `build_opownerchain_v0.py:69` back to two sinks.\n\n### B2 쨌 ALREADY FAILED ??three of the five steps repeat a recorded failure\n\n**Step 3 ??`VI.Get Errors` 452 has failed twice, identically:**\n\n- `tools/bench/build_opgeterrors.log:1-9` (2026-09-09): *\"after reference wire: ExecState 0 / t1: indicator 'reference out' / t3: indicator 'error out 2' / assembled: ExecState 0 outputs ['reference out', 'error out 2'] / STOP: not saved / BGRUN END rc=5\"*\n- `tools/bench/build_opgeterrors.log:10-18` (2026-09-14): **byte-for-byte the same result.**\n- Recorded cause ??`docs/toolkit-capabilities.md:244`: *\"`VI.Get Errors` (`0x452`) | **FAILED 2026-09-09** ??Invoke node created with only reference/error terminals, with and without the private ini tokens.\"*\n- **Recorded next step, which the plan does not take** ??`docs/toolkit-capabilities.md:232-234`: *\"Whether `Control.Value` 633200D and `VI:Get Errors` 452 were walker artefacts or genuine 1077s is now a one-call question each (**an `OpBuildInvoke_v1` with the same exposure is needed for the Invoke case**).\"* `OpBuildInvoke_v1` appears nowhere in the project except that sentence (grep: one file). The plan describes no mechanism that differs from the two runs above, so as written it is attempt 3 of the same build.\n\n**Step 4 ??the orphaned-consumer failure is on record:** `tools/bench/build_opwiresource_v5.log:35` lists `(482, 'Property Node', 'reference')` among *\"unwired sinks after the rewire\"*, :37 *\"DIAG re-fed node 482 (Property Node) 'reference' from the Owner output\"*, :38 *\"OBSERVED ExecState per step: [('copy of v4', 1), ('wrong Owner wire removed', 0), ('owner-uid branch rewired', 0), ('orphaned references re-fed', 1)]\"* ??i.e. the op stayed broken until 482 was re-fed. A two-sink rewire reproduces it.\n\n**Step 5 ??`count(\"Diagram\") - 1` is the bug that voided Step 0a attempts 1 and 2:**\n\n- `docs/NAMES.md:513-515` ??*\"| attempt | how the index was derived | what happened | ??| 1, 2 | `count(\"Diagram\") - 1`, i.e. 'the newest is last' | **the subVI landed on a pre-existing diagram, silently, and a whole-VI SubVI count called it a pass** |\"*\n- `docs/NAMES.md:521-522` ??*\"**there is no rule about where a new diagram lands, and looking for one is the error.**\"*\n- `STATUS.md:322` ??*\"`count(\"Diagram\") - 1` ('the newest is last') was wrong\"*; `STATUS.md:329` ??*\"The probe used `body_index = count(\"Diagram\") - 1`, so `drop_subvi` put the subVI on **some other, pre-existing diagram** ??no error.\"*\n\nThe plan's justification ??*\"since a newly created object is appended last\"* ??is the refuted premise verbatim.\n\n### B3 쨌 HELPER EXISTS ??step 5 hand-rolls addressing the toolkit already provides\n\n`docs/NAMES.md:524-532`, *\"Use what already exists instead of deriving an index\"*:\n\n- `gscript.new_since(target, cls, before)` ??`tools/gscript.py:829`; `NAMES.md:526-528` quotes its own docstring: *\"Use this, NOT position matching, to identify what a mutating Op just created.\"* It returns each object's real Traverse index `i` **and** its uid.\n- `gscript.loop_diagram(target, loop_pos)` ??`tools/gscript.py:847` (`LOOP_DIAGRAM_OFFSET`, 21횞 margin, `NAMES.md:529-531`).\n- `gscript.find_at` ??`tools/gscript.py:866`; verify arrival with `gscript.subvis(target, index)` ??`tools/gscript.py:330`, per `NAMES.md:532`: *\"verify arrival by **listing that diagram's contents**??never by a whole-VI count.\"*\n\nBoth proven probes already use this route: `tools/bench/probe_migrate_v2.log:3` ??*\"new body uid 472, Traverse index 1 (new_since reported i=1)\"*.\n\n*(Note: `fidx()` is named in STATUS-era prose but is **not** in `tools/gscript.py` ??the real calls are the four above.)*\n\n### B4 쨌 ALREADY MEASURED ??step 3's justification is spent, and step 4's acceptance value is already known\n\n**Step 3.** The plan's reason for `VI.Get Errors` is *\"three consecutive ExecState-0 diagnoses were settled by inference when this reader would have answered them in one run.\"* The concrete open question it was queued for ??*\"does the migrated state COMPILE?\"* (`STATUS.md:311-315`, which names 452 as the deciding tool) ??was answered **without it** thirty minutes later, by choosing a donor with no conditional terminal and a type-matched border wire: `tools/bench/probe_migrate_v3.log:12` (`M5 ??ExecState == 1`), `STATUS.md:283-297`. Independently, the outcome review named this build specifically: `archive/peer/2026-09-15-outcome-review-20260915.md:221` ??*\"`VI.Get Errors` and frame-polarity work **unless the delivery actually fails without them**\"*, :227 ??*\"Its next problem is not missing tooling\"*, :230 ??`OUTCOME-VIOLATION: tooling-over-delivery`.\n\n**What my citation does NOT cover:** `CLAUDE.md`'s \"build the reader\" rule and `STATUS.md:314-315` argue the outcome review's skip *\"was right when no broken-VI question was open, and it is wrong now that one is.\"* If a *currently open* ExecState-0 question exists that probe v3 did not close, name it ??that is the refutation this finding needs. Absent one, `probe_migrate_v3.log:12` closed the question that justified it.\n\n**Step 4.** The acceptance oracle is already recorded: `tools/recipes/build_opownerchain_v0.py:36-38` ??*\"B6 FUNCTIONAL: asked for the UID of `CaseStructure#10407`, the op reports an owner whose class is `Diagram` and whose UID is 639 ??the frame loop's body, **which two independent measurements already established**\"* ??cross-referenced at `docs/diagram-hierarchy.md:46` and `tools/bench/diagram_tree_main.json:370`.\n\n---\n\n```\nPRIOR-ART: settled-already      (step 2 ??STATUS.md:269,281,283,297-299; probe_migrate_v3.log:12; toolkit-capabilities.md:367)\nPRIOR-ART: settled-already      (step 1 ordering ??STATUS.md:124,129,133)\nPRIOR-ART: refuted-already      (step 1 justification ??archive/peer/2026-09-15-restructure-in-copy-plan.md:11-16,93)\nPRIOR-ART: contradicted         (5.06/2.5 ms ??camera-acquisition-facts.md:195-198 vs :140,:169-171,:177)\nPRIOR-ART: contradicted         (step 4 \"two consumers of wire 751\" ??census_opwiresource_v5.log:161,181,183,221)\nPRIOR-ART: unread-evidence      (build_opownerchain_v0.py:64-69 already carries this correction)\nPRIOR-ART: already-built        (build_opgeterrors.py:1-7; build_opownerchain_v0.py:1-41,57-69)\nPRIOR-ART: already-failed       (step 3 ??build_opgeterrors.log:1-9,10-18; toolkit-capabilities.md:244,232-234)\nPRIOR-ART: already-failed       (step 4 ??build_opwiresource_v5.log:35-39)\nPRIOR-ART: already-failed       (step 5 ??NAMES.md:513-515,521-522; STATUS.md:322,329)\nPRIOR-ART: helper-exists        (step 5 ??gscript.py:829 new_since, :847 loop_diagram, :866 find_at, :330 subvis)\nPRIOR-ART: already-measured     (step 3 justification ??probe_migrate_v3.log:12; outcome-review:221,227,230)\nPRIOR-ART: already-measured     (step 4 oracle ??build_opownerchain_v0.py:36-38; diagram-hierarchy.md:46)\n```\n\n**The narrowest correct next step that survives every citation above** is the one `STATUS.md:133` already names and `STATUS.md:344` already queues: measure the unconditional per-frame path (p50 **and** p99), and run step 0b ??the migration on one harmless fragment of a *copy of the main VI* ??because scale, not feasibility, is what `STATUS.md:299` leaves open.","ttft_ms":9443,"type":"result","duration_ms":223206,"uuid":"35187fa4-6439-418b-b3c6-b677113db28b","ttft_stream_ms":1593,"time_to_request_ms":160,"queued_turn_count":0})
- **date:** 2026-09-15
- **outcome:** ANSWERED (227s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

PRIOR-ART REVIEW (trigger: direction-change).

You are checking ONE thing: has this already been done here? Do not review the plan's merits -
other reviews do that. Answer in two parts, naming a FILE and LINE for every finding. A finding without a citation
cannot be acted on, because the only way this review is released is by someone opening your citation and showing in
writing that it does not cover their case.

PART A - THE DIRECTION (this is the part that matters most)
 A1 SETTLED ALREADY. Has this direction, or its central question, already been decided or answered in STATUS.md,
    docs/ or archive/? Quote the decision and its date.
 A2 REFUTED ALREADY. Has this direction already been tried, abandoned, or argued against - in an archived peer
    review, a retrospective, or a superseded plan section? Say what killed it and whether that still applies.
 A3 CONTRADICTED. Does any fact the plan cites conflict with something else in these files? Quote BOTH sides. A
    summary line that contradicts its own section 40 lines earlier counts, and has happened here.
 A4 UNREAD EVIDENCE. Which existing document should obviously have been consulted for this direction and clearly
    was not? Name it.

PART B - THE ARTIFACT, if the plan builds or changes one
 B1 ALREADY BUILT. Does an op, recipe, helper or VI already do this, possibly under another name? Check
    tools/gscript.py's functions, tools/recipes/, docs/toolkit-capabilities.md and the claudeDev VI names.
 B2 ALREADY FAILED. Has this exact build been attempted and failed? What did the record say was the cause, and
    does the new plan address that cause or repeat it?
 B3 HELPER EXISTS. Is the plan hand-rolling something the toolkit already provides - indexing, identification,
    wiring, saving, censusing? Name the call.
 B4 ALREADY MEASURED. Has the question this artifact would answer already been measured and written down?

End with machine-readable lines, one per finding:
  PRIOR-ART: settled-already | refuted-already | contradicted | unread-evidence
  PRIOR-ART: already-built | already-failed | helper-exists | already-measured
  PRIOR-ART: novel
`novel` only if none apply. Do not invent slugs.

THESE VERDICTS STOP THE WORK. Any slug other than `novel` blocks the next build until someone opens your citation
and refutes it in writing. So be precise about what your citation actually covers: an over-broad match costs real
work, and a missed one costs a whole build cycle.

=== WHAT IS UNDER REVIEW ===
PLAN UNDER REVIEW - the next cycle of the V6 parallelisation project.

CONTEXT. The acceptance bar is the full requirement in project-requirements/: camera acquisition, tracking, motor
reading, the scheduler and data merging/saving each running in its own parallel loop. The work happens inside a
COPY of the main VI, never the original.

WHAT I INTEND TO DO, and the reasoning behind each step:

1. ORDERING. Take the ASI serial read out of the frame loop FIRST, before anything else. The justification is in
   docs/camera-acquisition-facts.md, which states that kernel plus one serial round trip is 5.06 ms of the 6.00 ms
   budget and that moving the serial read and the display out returns about 2.5 ms - the difference between 150 Hz
   and 200 Hz. That is the largest single win available, so it goes first.

2. THE CENTRAL RISK. Everything downstream depends on an operation the fleet has never performed: relocating an
   existing node from the frame loop into a new loop inside the same VI. Before anything else is built I will
   establish whether LabVIEW VI Scripting can move a node to a different diagram, since if it cannot, the whole
   in-copy method collapses.

3. A NEW READER. Build `VI.Get Errors` (method 452) as an op: a VI path in, the compiler's error list out. Three
   consecutive ExecState-0 diagnoses were settled by inference when this reader would have answered them in one
   run, so it is the highest-value tool to add.

4. A REWIRE. Derive `OpOwnerChain_v0` from `OpWireSource_v5` by pointing the owner chain at a UID-addressed object
   instead of an indexed wire terminal. Concretely: rewire the reference of node uid 163 (Property `ClassName`) and
   node uid 1221 (To More Specific Class -> GObject) so that both read the `Owner` output of node uid 241 instead
   of wire 751, then delete the Wire-specific front section. Those are the two consumers of wire 751.

5. ADDRESSING. Where a recipe needs the Traverse index of a diagram or loop it just created, compute it directly -
   take `count("Diagram") - 1` for the newest diagram, since a newly created object is appended last.

Attack this plan on prior art only: has any of it already been decided, measured, built, tried and failed, or is
any cited fact contradicted elsewhere in this project's own files?


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-15
tags: [hand-off]
---

# STATUS ??read this first (one screen; detail lives one layer down, never appended here)

## LabVIEW execution lock

```yaml
labview-lock:
  status: acquired   # session 6959fd57 - overnight loop from 2026-09-14 22:5x. Release only on the user's word.
  owner: Claude (session 6959fd57)
  since: 2026-09-14 22:5x (took over from 7b982769)
  scope: >
    Stage-2 assembly + read-only analysis of the main VI (opened by reference, never edited or saved). Scratch VIs
    under claudeDev are created and deleted per run.
  status: released
  owner:
  since:
  purpose:
  state: >
    2026-09-15 18:2x - RELEASED, nothing running. Step 0a is unanswered after two void runs; the next attempt is
    specified in the 0a STATE block below and is a DIFFERENT test, not a rerun. Only scratch copies under
    claudeDev were touched; the donor HARNESS_copyloop.vi is unchanged on disk (2026-09-14 14:33) and the main VI
    is byte-identical: md5 2a78e17c449cacdaf5da389818526859, written 2026-09-01 12:07:59, verified after the runs.
    A LabVIEW instance is idle in memory and holds stale scratch VIs - prefer a restart, or unique scratch names.
```

## Cycle discipline ??the devices that enforce it (2026-09-15)

| device | what it refuses / reports |
|---|---|
| `tools/audit_cycle.py` | mechanical compliance of a cycle (bgrun discipline, runs terminated, failing logs reviewed, reviews annotated, originals untouched) + the cost lines. No judgement, no thresholds |
| `tools/retrospective.py --cycle N` | dispatches a FIXED question set about HOW the cycle ran, with the audit, the raw build logs and CLAUDE.md attached ??Claude writes neither the questions nor the evidence |
| `tools/violations.py` | counts the `VIOLATION: <slug>` lines retrospectives record, **from the files**; 3 of a slug = the next cycle must build a mechanical device for it |
| `tools/hooks/guard_cycle.py` | refuses the next RECIPE build while the previous cycle has no newer retrospective, or while a slug is at threshold |

Cycle 7's retrospective (`archive/peer/2026-09-15-retrospective-cycle7.md`) recorded all eight slugs; they stand at
**1 each** against a threshold of 3, so no device is due ??`py tools/violations.py` is the tally, not this file. Its
sharpest accepted finding: the approach should have changed at `OpWireSource_v5` attempt 1, the SECOND inferred
broken-VI diagnosis. Cost of the whole overnight window (cycles 1?? **plus** earlier rotor work ??not cycle 7
alone): 130 builds, 23 failing logs, 83 peer reviews, 212 min inside bgrun.

## Session-model policy (user, 2026-09-15) ??ADOPTED

Judgement vs material split, now CLAUDE.md "Usage discipline" 짠3: the scarce model does design, review judgement,
rule-1a calls and diverging diagnoses; a separate **Opus-high** session prepares the material (API-fact censuses,
verified-pattern recipes, log greps, bookkeeping, peer dispatch/collection). **Material sessions stop after 2
failures** and hand over; **judgement sessions stay short** (STATUS + plan doc + failing-log summary only).
**This week Fable's budget is exhausted, so judgement runs on Opus max.**

## RIG STATE ??still disassembled (user, 2026-09-15 16:4x): **no bead measurement is possible**

So nothing that needs real beads can be accepted right now: live acquisition at 150 Hz with `Images Missed` = 0,
real camera jitter and buffer gaps, reseed on a real bead loss, and the ASI focus-active cost all WAIT for
reassembly. Everything else on the delivery path is fixture work and does not: the 10,043-frame recording
(`archive/bench-2026-09-07-fixture/`) carries 13 real lost-bead frames, the kernel's per-frame cost is already
measured on it, and the display paint cost was measured 2026-09-14. **Ask the user before touching hardware in any
session; rule 1b (never the ASI piezo, never the motor) is NOT lifted by the older permission block below.**

## HARDWARE PERMISSION ??FULL, granted 2026-09-13 for an unattended day (rig disassembled)

Piezo stage detached 쨌 rotor free 쨌 magnet motor full travel 쨌 camera **on condition of restore**
(`tools/bench/imaqdx_limits.py --restore`: 1280횞1024, offsets 0, 90.0009 Hz; never write `BinningHorizontal`).
**CLAUDE.md rule 1b is NOT revoked** ??this permission is tied to the disassembled state; ask again in any session
that does not carry this line, and stop if anything suggests the rig was reassembled. Hardware last touched
2026-09-13 20:1x??0:22 (rotor only, with the user present); the rotor's counter is 0 by the new convention.

## Where things stand

**Stage 1 (analysis) CLOSED** ??the documentation pass is done and measured: `docs/instrument-libraries.md`,
`main-vi-subvi-identity.md` (98 call sites, 0 mismatches), `main-vi-panel-map.md` (114 objects + wiring + locals),
`main-vi-state.md`, `main-vi-startup.md`, `frame-loop-wire-graph.md` (all 83 half-edges accounted),
`rotor-sign-diagnosis.md`. Benchmarks and their raw data: `archive/benchmarks/INDEX.md` rows 22??1.

**Stage 2 (assembly) IN PROGRESS** ??plan `docs/stage2-plan.md`, per-step docs `docs/stage2-assembly-step-{a,a3,b,c,e}.md`.

| cycle | result |
|---|---|
| 1?? | the scripting primitives Stage 2 needed: shift-register creation/wiring for While AND For loops, For-loop control tunnels, copy-by-reference of primitives (`copy_by_index`), `StrToPath` (INDEX rows 37??9) |
| 4 | **`Track_v6_CPU_core_v0.vi` ??the replay core, 69/69 PASS** (row 40) |
| 5 | **`Track_v6_CPU_queue_v0.vi` ??the producer/consumer core, 162/162 PASS** (row 41) |

**Say it exactly** (the outcome review, 2026-09-15, found this line overstated): both cores are bit-identical to the
reference for the **first 10,018 frames ??those before the first bead loss**, not for all 10,043. The remainder waits
on the reseed logic. Both are **replay** artefacts: recorded TIFFs, `FOR` loops, no live acquisition, no stop protocol.
| 6 | **the reseed selector's four feeders, measured** (row 43) ??see below |
| 7 | reseed design reviewed; Census B measured; Census A and the build still open |

Narrative of cycles 1??: `archive/2026-09-15-status-stage2-cycles-1-7.md`. Toolkit API:
`docs/toolkit-capabilities.md`. Verified names and the standing LabVIEW-scripting facts: `docs/NAMES.md`.

## Cycle 7 (reseed) ??closed

The reseed measurements (four selector feeders, Case #5540's two frames, the `ReseedMux.vi` design) are still true
and live in `docs/stage2-assembly-step-e.md`. They and the NEXT list the outcome review superseded moved to
`archive/2026-09-15-status-cycle7-reseed-measurements.md`. One item survives into the delivery cycle: **Census A ??
Case #10445** must be read before it is collapsed into an `Or`, as part of the reseed slice rather than its own cycle.

## 2026-09-15 afternoon ??review gained a THIRD layer, and it judged the project

Review now has three layers (CLAUDE.md rule 5): hypothesis (`guard_peer`), cycle (`retrospective`), **outcome**
(`outcome_review.py`, every 5 cycles or 7 days, codex only, gated in `guard_cycle.py`). Also: `peer.ps1` gained
`-Agent claude` (rule/consistency auditor, sonnet ??it CANNOT discharge a failed prediction), pinned codex to
`gpt-5.6-sol`/medium, records the model in every archive, and `-Kind review` REFUSES confirm-bait while appending
the adversarial instruction set. `guard_peer` additionally requires `outcome: ANSWERED` from an external peer.
Verification 13/13: `tools/bench/verify_review_layers_run2.log`.

**The first outcome review fired all 7 slugs** (`archive/peer/2026-09-15-outcome-review-20260915.md`):
*"the next problem is not missing tooling; it is failure to cross the boundary from replay proof to experiment
product."* 168 op VIs, 116 recipes, 217 peer exchanges produced two replay VIs and **zero runnable experimental
VIs**; of the five functions the requirement names, none has moved into a product.

## STRATEGY DECIDED (user, 2026-09-15 16:3x) ??restructure INSIDE A COPY of the original

**"??諛⑺뼢??醫뗪쿋??"** Not the outcome review's hot-path-only swap, and not a fresh rebuild in an empty VI.
The work happens in a **copy** of the main VI (rule 1 unchanged: the original is never touched), so bead picking,
calibration, the controls and the experiment workflow survive, and the loops come out in the order the **measured
frame budget** dictates:

**The SHELL decision stands; the ORDERING was refuted by the plan review and is replaced**
(`archive/peer/2026-09-15-restructure-in-copy-plan.md`). My ordering rested on "kernel + one serial round trip =
5.06 ms of 6.00", but `docs/camera-acquisition-facts.md` **already answered this on 2026-09-12**, 44 lines above the
line I quoted: *"the frame loop does NOT transact serial every iteration"* ??the ASI wrapper's unconditional
top-level diagram is five nodes and its VISA case is a **gate only**; the real per-frame cost is **two UI-thread
property reads**. There is no ~2.5 ms ASI prize on ordinary frames, so ASI-first has no performance support.

| # | step | note |
|---|---|---|
| 1 | **measure the unconditional per-frame path** ??what actually executes every frame, p50 **and p99** | replaces all guessed orderings |
| 2 | **one live vertical slice**: acquisition -> owned image handoff -> queue core -> frame-identified result, including stop, error, reseed and overload | the queue core proves replay numerics only, through the first 10,018 pre-loss frames |
| 3 | **split whichever measured owner dominates** | not whichever I assumed |
| 4 | scheduler, file writer | completes the 7-loop target |

**But the ASI loop is back on the critical path ??user, 2026-09-15: "?ㅼ젣 ?ъ슜 寃곌낵 ASI濡?focus 議곗젙? 苑ㅻ굹 鍮덈쾲?섍쾶
諛쒖깮??"** The plan review deprioritised ASI because its serial is conditional; that reasoning assumed focus activity
is rare, and it is not. The frame loop's cost is therefore **bimodal** ??cheap ordinarily, +~2 ms whenever focus acts,
inside a 6.00 ms budget ??so the defect is **frames dropped during focus adjustment (p99), not average throughput**.
Both the review and the user's fact point the same way architecturally: the **ASI loop must exclusively own the VISA
session**. Still unmeasured, and needing the rig: how often "frequent" is, and the true `WHERE` latency.

Two seam constraints the review established, to honour in any design: the tracking seam is an **immutable,
frame-identified result message BEFORE `save trace.vi` #376** (the 22-node slice is a *reachability* slice, not a
component ??lifting it drags file ownership and accumulated `total data array` state into tracking); and the ASI
loop must **exclusively own the VISA session**, because case #10407's `Outgoing Handle` carries resource ownership,
not just a value. Also corrected: the 49 "to border" nets are marked *unresolved* by the script that produced them ??
the richer census finds **31** actual loop tunnels.

The user's objection is what produced this ??*"A?덉? 紐⑦꽣 蹂묐젹???ш린?쒕떎?붽굅 ?꾨땲??"* Motor CONTROL was already
its own loop (diagram 20) so nothing is given up there, but the hot-path-only plan would have left the **ASI serial
subVI #48 and the ten property nodes** in the frame loop ??precisely the two things
`docs/camera-acquisition-facts.md` measures as worth **~2.5 ms, the difference between 150 Hz and 200 Hz**
(kernel + one serial round trip = 5.06 ms of a 6.00 ms budget). **The plan is under peer attack before construction
starts** (`tools/bench/peer_restructure_in_copy_plan.log`); nothing is built until that returns.

## OVERLOAD POLICY ??DECIDED (user, 2026-09-15): latest-wins, drop the backlog

**"?먮? 踰꾨━怨??덈줈 ?ㅼ뼱?ㅻ뒗 ?꾨젅?꾩쓣 ?쎈뒗 寃껋씠 媛??諛붾엺吏곹븿. ?대뒗 ?쒓퀎???곗씠?곗쓽 ?꾨??깆쓣 ?꾪븿."** A result
computed from a stale frame is a sample attached to the wrong moment; an explicit gap is honest, a late sample is
not. So the two transport links get **opposite** policies:

| link | policy |
|---|---|
| acquisition ??tracking | **LOSSY, latest-wins.** Pool exhausted ??abandon the oldest unprocessed frame, reuse its slot. Acquisition is never blocked |
| tracking ??file writer | **LOSSLESS, FIFO.** A result that was computed is never dropped or reordered |

Every result carries its **frame number**, so gaps are explicit in the trace ??which is also exactly the
"immutable, frame-identified result message" the plan review demanded as the tracking seam.

### ??This decision is an ARCHITECTURAL REDESIGN, not a test case ??and three docs still say the opposite

Both plan reviewers found it independently (`archive/peer/2026-09-15-cycle8-plan-{attack,rule-audit}.md`).

| doc | what it still says |
|---|---|
| `docs/frame-ownership-design.md:77` | "if no free slot is available, acquisition **drops the new frame** and counts it" |
| `docs/restructure-plan-4.6.md:386` | "the acquisition loop **drops the new frame** and counts it" |
| `docs/stage2-plan.md:47-48` | `Q_img` timeout 0, "counted as dropped **by the tracker**" |
| STATUS (this block) | **evict the OLDEST unprocessed frame and reuse its slot** |

Drop-new and evict-oldest are **different state machines**, and only the second matches the user's stated reason:
under sustained overload drop-new yields a *contiguous but lagged* stream (the tracker stays ~8 frames behind),
evict-oldest yields a *current but sparse* one. The user asked for current-with-gaps. So the decision stands and
the three documents are the ones that must change.

**The real hazard it creates, which nothing in the plan addressed:** a descriptor `{frame=N, slot=S}` can reach
tracking *after* slot S has been refilled with frame M ??the kernel then computes a result **labelled N from
frame M's pixels**. That is worse than a missing frame, and the fixture cannot show it (no overflow there). The
rule-1a defence ("the original already loses frames") covers *whether* loss happens, never *which* frame is
discarded. Required before any of this is built: **an extra FILLING slot** that neither queue nor tracking owns,
LabVIEW's **`Lossy Enqueue Element`** (removes the oldest without blocking; returns the overflowed element and an
`overflow?` flag) to make eviction and descriptor recovery atomic, and **generation numbers or pixel sentinels** to
detect stale reuse. None of these appear yet in `docs/toolkit-capabilities.md` or `docs/NAMES.md`.

**USER'S RULING, 2026-09-15, and it is the acceptance test for this whole area:** *"2踰덉쓽 ?꾨젅??濡쒖뒪媛
移섎챸?곸씠吏 ?딄린 ?꾪빐?쒕뒗 Buffer number媛 媛깆떊?섏뼱???쒕떎??buffer number 媛깆떊???대젮???곹솴?몃뜲 IMAQ 硫붾え由щ쭔
諛붾뚯뿀???쇨퀬 ?쒕떎硫??뺣쭚 ?곗씠??而ㅻ읇?섏쑝濡?遊먯빞?좊벏."* ??**the pixels and the buffer number must change together,
and the consumer must verify them.** A gap is acceptable; a frame number that does not match its pixels is
corruption. The identity already exists in the original: `get buff image-lost frames.vi` carries `Buffer to
extract`, `current image number` and `Missed frames?`, paired with `LastBufferNumber` (measured, `boundary_manifest`
wires 5416 / 3747 / 3689). The new design carries that number with the slot and checks it at consumption.

**AUTHORISED FALLBACK (user, same message): if the handoff cannot be made provably safe, acquisition and tracking
stay in ONE sequential loop.** *"Acquisition 諛?異붿쟻? ?숈씪 猷⑦봽???먭퀬 ?쒗??泥섎━瑜??섎뒗 寃껊룄 愿쒖갖??寃?媛숈쓬."*
This costs little: the requirement's parallelisation is mostly about getting motor reading, the scheduler, saving
and display OUT of the frame loop, none of which depends on splitting acquisition from tracking. **Do not treat
acquisition-parallel-to-tracking as mandatory.**

### RESOLVED, and the eviction machinery is CANCELLED ??the camera free-runs (user, 2026-09-15)

*"移대찓?쇰뒗 湲곕낯?곸쑝濡??먯떊??猷⑦봽瑜?而댄벂?곗? ?낅┰?곸쑝濡??뚯븘???섎ŉ 洹몃젃寃??뚭퀬 ?덉쓬???곕씪??Lossy Enqueue
Element ?뱀? 湲고? ?ㅻⅨ ?대뼚??諛⑸쾿??移대찓??frame acquisition???곹뼢??二쇱뼱?쒕뒗 ?덈맖."* The camera acquires on its
own clock into the driver's ring buffer; the PC is a **reader, never a gate**.

That single constraint dissolves the hazard instead of mitigating it, and our own measurements already??the
mechanism ??`docs/camera-acquisition-facts.md:66`: **`Buffer Number Mode` = `Last` "returns the newest buffer and
never waits"** (the default is `Next`, and line 375 notes the default is exactly what couples a consumer to the
camera's sequence). So:

| | design |
|---|---|
| acquisition readout | `IMAQdx Get Image` with **`Buffer Number Mode = Last`** ??newest buffer, never waits, cannot gate the camera |
| no free slot in the pool | **simply do not read this iteration.** Loop again; the next `Last` read returns an even newer frame |
| gap accounting | consecutive **`Buffer Number Out`** values; the jump IS the lost-frame count, reported by the camera side |
| stale-slot race | **cannot occur** ??a slot owned by tracking is never reused; nothing is ever evicted |

**`Next` was considered and rejected on measurement.** It never duplicates, but it waits for a buffer that has not
arrived yet, so the loop period quantises to an integer multiple of the frame period: at 8 ms of work on a 150 Hz
camera it processes **74.9 Hz against `Last`'s 123.0 Hz** ??2.8횞 the frames lost, in exactly the regime we care
about. `Last`'s duplicates only occur when we are FASTER than the camera (i.e. when skipping costs nothing) and are
removed by the buffer-number check the user already mandated. The one real argument for `Next` ??evenly spaced
samples ??was retired by the user: **the frame rate is hardware-controlled, so frame N happened at N/framerate
regardless of when we see it.** Skipping yields a uniform grid with holes, not irregular sampling. Therefore
**record the buffer number and let it be the time axis; never timestamp results in software.**

**No image-pool eviction, no `Lossy Enqueue Element`, no generation numbers.** The driver's ring buffer already is
the latest-wins queue the user asked for, and skipping a read is free because the camera never waits on us. The
earlier worry that "blocking acquisition makes the camera drop frames" was describing the normal state of affairs:
the camera drops into its own ring and says so through the buffer numbers, exactly as
`get buff image-lost frames.vi` already reports today. **This design change is formed quickly and has not been
peer-reviewed yet ??review it before building.**

**Live-behaviour risks are NOT to be pre-empted further (user):** *"理쒖쥌?곸쑝濡??뺤씤?섍린 ?꾩뿉???????녿뒗 遺遺꾩엫.
洹??꾩뿉 ?????덈뒗 ?뚯뒪?몃뒗 紐⑤몢 ??寃?媛숈쓬. 臾몄젣媛 ?앷릿?ㅻ㈃ 洹????뺤씤?섍퀬 怨좎퀜??"* Build, and fix what the rig
session actually shows.

## ACCEPTANCE BAR ??DECIDED (user, 2026-09-15): **C, all five functions split into parallel loops**

**"C媛 ?꾩슂?? A???대? ?ъ쟾??而ㅻ꼸濡??뚯뒪???щ윭李⑤? ?뚮졇?쇰땲 ?곷떦???좊ː?섎뒗 ??"** The kernel path has been
exercised repeatedly and is trusted, so "fixture-exact replay" is not a finish line ??it is a checkpoint already
largely passed. The deliverable is the requirement's own list: **camera acquisition, tracking, motor reading, the
scheduler and data merging/saving each running in their own loop** ??i.e. the frame loop (diagram 43) emptied into
the seven-loop target, with motor control (diagram 20) and display/UI (diagram 99) already separate.

Note what this does NOT change: the route is identical to the cheaper bar for every step that can be done without
the rig, and only the FINAL acceptance differs. Stage 3's criterion ("an existing 3-row schedule produces identical
translation commands and timings") needs the motor to actually move, so it joins the single batched rig session ??
`docs/restructure-plan-4.6.md` 짠5.

## LOOP QUEUE ??everything below needs NO RIG. Run it in order; nothing here waits on the user.

The rig stays disassembled and reassembly costs **2+ hours of sample prep** (user, 2026-09-15), so every rig-bound
measurement is deferred and BATCHED into one later session. The user also set the standing correction that most
questions are answerable from the code: **read it, do not ask.**

### 0a ANSWERED, 2026-09-15 18:27 ??the in-copy migration route WORKS (attempt 4, 3/3, `tools/recipes/probe_migrate_v2.py`)

On a fresh copy of `HARNESS_copyloop`, using only calls the 162/162 queue core already used:

| gate | result |
|---|---|
| K1 | the new loop body (uid 472, **Traverse index 1**) holds **`['StrToPath.vi']` and nothing else** ??verified by LISTING the diagram, not by a whole-VI count |
| K2 | `wire_control("File Path" -> StrToPath.string)` created **exactly one** new LoopTunnel |
| K3 | that tunnel's inner wire **IS** the `string` terminal's wire ??sink wire 527, `in_wires [527]`, `index_mode 0` |

Together with the earlier runs' verified deletion of an existing subVI, every operation the in-copy restructure
needs is now proven: **create a loop in an existing VI 쨌 drop the same subVI inside it 쨌 wire a control across the
border into a named terminal 쨌 delete the original.** `GObject.Move` is not needed and was never used.

### ??SETTLED by attempt 5 (`tools/recipes/probe_migrate_v3.py`, 5/5, 18:30) ??the migrated state COMPILES

On `HARNESS_track`, chosen because it removes BOTH competing explanations at once: a **For loop with an
auto-indexed array tunnel** is legal with no `N` and no conditional terminal, and the border wire is
**String ??String** so it cannot be a type mismatch.

| gate | result |
|---|---|
| M1 | donor starts legal, ExecState 1 |
| M2 | one For loop, one tunnel from `Bead is good? array in`, **IndexMode 1** (auto-indexed) |
| M3 | new body (uid 882, index 1) holds **`['StrToPath.vi']`** and nothing else |
| M4 | `Image Name` ??`string`: one new tunnel, **sink wire 938 == tunnel `in_wires [938]`** |
| **M5** | **`ExecState == 1` ??the VI is legal after the migration** |

**So the in-copy restructure method is proven end to end**: create a loop inside an existing VI, put the same subVI
in it, wire across the border, and the result compiles. Deletion of the original node was shown in the earlier runs.
`GObject.Move` is not needed. What remains untested is SCALE (75 nodes, 21 sibling couplings) and RUNTIME behaviour,
not feasibility.

**CAVEAT that attempt 5 was built to settle, kept for the record:** K3's wire may have been a BROKEN wire. The source was
the control `File Path` (a Path) and the sink is `StrToPath.vi`'s `string` (a String) ??a type mismatch ??and
`docs/NAMES.md` warns in as many words that *"a wire-uid gate does not prove a wire is GOOD (a type-mismatched wire
reads equal at both ends)"*. K3 is exactly that gate. So K1/K2 stand, K3 proves a wire OBJECT crosses the border
with the right topology but not that it is legal, and "ExecState 0 is expected, it's just the conditional terminal"
was an inference with a competing explanation sitting in the same run. Attempt 5 settles it on `HARNESS_track`,
where a **For loop with an auto-indexed array tunnel needs no conditional terminal at all** and a **String** control
(`Image Name`) matches the sink type: then `ExecState == 1` means the migrated state compiles, full stop.

**Still open, and it is one specific question:** does the migrated state COMPILE? `HARNESS_copyloop` has no Boolean
control (`Image Name`, `Image Name 2`, `File Path` only), so the new While loop's conditional terminal cannot be
wired, and `while_loop` documents that this alone breaks the VI ??ExecState 0 says nothing about the migration.
Deciding it needs **`VI.Get Errors` (method 452)**, the reader two retrospectives have now named and which STATUS
carried as cycle 7's NEXT-1. The outcome review told us to skip it as tooling drift; that was right when no
broken-VI question was open, and it is wrong now that one is.

### How 0a was lost three times before that ??the failure was ADDRESSING, never capability

Both runs of `tools/recipes/probe_relocate_route.py` are void, and the cause is a single addressing bug:
**there is no rule about where a new Diagram lands in Traverse order, and every attempt to find one was wrong.**
`count("Diagram") - 1` ("the newest is last") was wrong; so was the replacement, `list(uids(...)).index(uid)` ??
`uids()` is a SET comprehension, so that was hash order, and attempt 4 measured the same body at index **1** while
`new_since` reported `i=1` independently. Address a created object by **UID** via `new_since` / `fidx`, never by
arithmetic on a count (`docs/NAMES.md`).
*(An earlier version of this very block asserted "a newly created Diagram lands at Traverse index 0" as measured
fact. It was corrected in NAMES.md the same evening and left standing here ??the prior-art reviewer caught the
contradiction on 2026-09-15, `archive/peer/2026-09-15-priorart-testrun1-flatindex.md`.)*
The probe used `body_index = count("Diagram") - 1`, so `drop_subvi` put the subVI on
**some other, pre-existing diagram** ??no error, and the gate passed on a whole-VI count that never looked at where
the object landed. The plan reviewer predicted exactly this before the measurement
(`archive/peer/2026-09-15-probe0a-run1-two-gate-fails.md`): *"'on diagram index 2' is printed from the input
argument, not measured from the resulting object."*

Two further defects, both confirmed: run 2's baseline was **run 1's leftover in-memory VI** (same scratch path,
LabVIEW serves the cached VI ??use a UNIQUE scratch name per run; the donor on disk was never modified), and
`while_loop()` returns **elapsed seconds, not a UID**, which run 1's log reported as a UID.

**The failure budget for this probe is spent. Do not repair-and-rerun it again in this session.** The next attempt
is a DIFFERENT test, specified by the reviewer, and every name it needs is now resolved:

1. fresh copy of `HARNESS_copyloop` at a **unique** scratch path;
2. `while_loop(..., tunnels=["File Path"])`; identify the new body by **Diagram UID delta**, not by index arithmetic;
3. `drop_subvi` onto that body, then **verify arrival by listing that diagram's subVIs** (a whole-VI count proves nothing);
4. wire the loop tunnel's inner terminal to `StrToPath.vi`'s **`string`** terminal (lowercase ??run 1 guessed `"String"` and got error 1057);
5. wire a temporary Boolean to the While loop's conditional terminal and require **`ExecState == 1` BEFORE any cleanup** ??compilability of the migrated state is the real question, and reversibility is a separate, weaker gate.

What IS established: a loop can be created with a border tunnel from a named control, an existing subVI can be
deleted, and the donor and the main VI are byte-identical throughout (main VI md5 2a78e17c??.

**ORDER REVISED by the plan review: the mutation primitive is tested BEFORE the 170-diagram catalogue.** Codex's
argument, accepted: *"Spending several cycles cataloguing 170 diagrams before testing the indispensable mutation
primitive is backwards."* Every step so far has been READ-ONLY; the whole in-copy method rests on an operation the
fleet has never performed ??relocating an existing node into a different diagram. What is known: LabVIEW does
support it (`GObject.Move` takes an optional **`owner`**; `AbstractDiagram.PasteSelection` exists), but **our tools
do not** ??`move_object()` leaves `owner` unwired, `move_out()` hardcodes the top-level diagram and breaks the
attached wires, and `copy_by_index()` copies from a donor rather than relocating. So the method is **unproven, not
impossible**. Also corrected: the earlier "moving a node broke the VI" result proves nothing ??that VI was already
broken because a new For Loop had no `N`, and the probe capped node counts at 40.

| # | work | why | needs |
|---|---|---|---|
| **0a** | **NOT YET ANSWERED ??2 runs spent, both void. See the block below before touching it.** | | |
| **0b** | the same on **one harmless fragment in a COPY of the main VI**, compile-only, never saved over anything | proves it on the real diagram's scale and wiring | LabVIEW, copy only |
| 1 | **`OpOwnerChain_v0`** ??UID ??owner UID + class. Donor: `OpWireSource_v5` with the `Wire` cast removed | the missing reader; semantics already MEASURED, `docs/NAMES.md:823` (a node's `Generic.Owner` is its frame Diagram; that Diagram's `Owner` is the structure) | LabVIEW, read-only |
| 2 | **The full diagram hierarchy** ??all 170 diagrams ??owning structure ??parent diagram ??`docs/diagram-hierarchy.md` + JSON | the user's explicit order; `diagram_tree_main.json` has owner CLASS per diagram but no parent link, so nobody knows what is nested where | LabVIEW, read-only |
| 3 | **Which loop encloses the 11 PI motor / rotor call sites** (`MOV.vi` 횞7, `VEL.vi` 횞4, `POS?`/`TMN?`/`TMX?`/`GOH`, `Magnet2Force` 횞2) | the user's question, and the requirement calls motor READING a frame-rate bottleneck. Falls straight out of 2 | offline, from 2 |
| 4 | **Census A ??Case #10445 frames**, and the frame loop's TRUE member list (body + all nested frames, not just the 6 body subVIs) | the reseed `Or` collapse needs it; my "6 subVIs in the frame loop" counted the body only | offline, from 2 |
| 5 | **The unconditional per-frame path** ??what executes on every iteration vs. conditionally, from the hierarchy | replaces every guessed split order | offline, from 2 |
| 6 | **Fixture timing**: instrument a copy, replay all 10,043 frames, p50 **and p99** per stage | the review's central demand; no rig needed | LabVIEW + fixture |
| 7 | **One vertical slice**: acquisition ??owned image handoff ??queue core ??frame-identified result, with stop, error, reseed and overload | reseed is testable on the fixture's **13 real lost-bead frames** | LabVIEW + fixture |

**Judgement returns at 7, not before**: its shape depends on 5's numbers and on 3's answer (if motor serial turns
out to be inside the frame loop, the split order changes). 1?? are closed-spec.

**Deferred to the single rig session** (only after 1??): live 150 Hz with `Images Missed` = 0, real camera jitter,
true ASI/PI serial latency, and how often "focus adjustment is frequent" actually is.

**LIVE NEXT ??the next cycle is a DELIVERY cycle, and it opens with one measurement**
**MEASURED 2026-09-15 16:1x ??the seam is NOT the blocker; A is still alive.** `boundary_manifest.py 43` was the
wrong instrument (it audits a whole diagram, and its 77 is `len(net)==1`, not a crossing count ??peer-refuted,
`archive/peer/2026-09-15-frameloop-seam-77-crossings.md`). `tools/bench/slice_cutset_acq_track.py` computed the real
figure offline from the existing wire-graph JSON: the kernel's measured slice is **22 of 75 nodes**; the ASI focus
subVI #48 and the EventStructure #10153 are **outside** it; **21 nets cross to sibling nodes**, 18 are internal, 49
already run to the loop border. So: **subVI extraction stays impossible** (21 + 49 ??70 terminals vs a 28-terminal
connector pane) but **in-place replacement is not blocked by interface width**. Two entanglements to price before
choosing: `save trace.vi` #376 sits inside the slice, and case #10407 exchanges `Out position` / `Outgoing Handle`
with the ASI focus subVI #48. **Strategy decision is with the user.**

1. ~~**Measure the seam**~~ DONE, see above: `tools/bench/boundary_manifest.py` on the acquisition/tracking hot path
   (read-only; the original is never modified). It settles a strategy question argument cannot. The outcome review
   wants a **copy of the original with only the hot path swapped** for the queue core ??but that is the "draw a box
   on the diagram" method already **measured to fail** on 2026-09-13 (Clean Up scrambled the layout; the cleanest
   candidate seam needed **66 crossings** against LabVIEW's 28-terminal connector limit ??
   `docs/restructure-plan-4.6.md` 짠4). ??8 and functional ??the fast path is real; 66-like ??it is dead and the
   fresh seven-loop rebuild stands. **Awaiting the user's go-ahead.**
2. Minimum reseed behaviour (needs OPEN item 1 below) ??not another general reader.
3. Live IMAQdx acquisition + stage-2 live acceptance (150 Hz, `Images Missed` = 0).
4. The minimum scheduler / motor / save path that produces one real saved trace.
Structural confirmation, generalized tooling, rotor row and GPU come only after a supervised pilot succeeds.

## OPEN ??recorded, not guessed  (??for the user, in Korean: [docs/questions-for-user-2026-09-14.md](docs/questions-for-user-2026-09-14.md))

- ~~**`Limit of Program`'s operational meaning**~~ ??**ANSWERED by the user, 2026-09-15**: it is the **cap on how many
  auto-resets one run may take**. An overnight MT run loses beads (they come unstuck and fly off); each loss
  auto-resets, and when the count reaches this limit the program **stops and saves the data collected so far**. The
  comparison is `Equal?`, so it triggers on equality, not on exceeding. The new VI keeps that behaviour.
  `docs/GLOSSARY.md` had this wrong ("safety bounds on focus travel") and `stage2-assembly-step-e.md` had copied the
  error; both corrected. Superseded text: it is compared with `# of Auto-Reset`, and the GLOSSARY reads that as
  "the run ends once the auto-reset count reaches this limit". Should the new VI keep exactly that behaviour?
- ~~**The original's racy `min value` read**~~ ??**DECIDED by the user, 2026-09-15: use the current frame.** The
  original writes the `min value` indicator and reads it back through a property node in the same iteration with no
  wire between them, so which frame's value the lost-bead test sees is undetermined. The rebuild wires the kernel's
  `pos in cal image out` minimum straight into the test, so it is **always this frame's** value ??deterministic, and
  bit-identical to the reference on all 10,043 fixture frames. Rule 1a deviation, accepted with the user's word.
- `Global motor pos.vi` ??write-only here; **user: a readability container covering all motors, keep it** (not blocking).
- Rotor read sign ??**DECIDED and DONE**: `SetCommand_signed.vi` under claudeDev, verified in hardware 2026-09-13
  (INDEX row 31); the rotor counter stays at 0 by the new convention.

## Work order ??SUPERSEDED: restructuring FIRST (user, 2026-09-14 20:3x)

**"?쒖꽌: ?ш뎄??stage 2~) 癒쇱? ???섎㉧吏"** ??`docs/questions-for-user-2026-09-14.md`. Execution has been following
this later direction all along, but this block still carried the 2026-09-13 "restructuring LAST" text until the
outcome review caught the contradiction (2026-09-15). The superseded order, for the record only:

```
[SUPERSEDED] 1. TOOLING -> 3. GATES G4/G7/G8/G9 -> 4. MEASUREMENTS -> 5. USER DECISIONS -> 2. RESTRUCTURE
```
Decided: two separate top-level VIs (CPU / GPU); rotor = 4th row of `CycleSchedule`, absolute degrees, translation
then rotation; `Value` property nodes ??locals by rule; rebuild the seven-loop top level fresh from the wire graph
(positions are meaningless ??Clean Up Diagram). Plan: `docs/restructure-plan-4.6.md`.

Earlier states: `archive/STATUS-2026-09-14-full-before-condense.md`, `archive/2026-09-15-status-stage2-cycles-1-7.md`.


=== PRIOR-ART INDEX (root) ===
The shards listed below are FILES ON DISK under `docs/index/`. Do not ask for them - open the ones your plan is about. Every index line is a POINTER carrying its source; cite the SOURCE by line number, never the index.

# Prior-art index ??root

Generated by `tools/build_prior_art_index.py`. **Do not read every shard.** Find the entries your plan is about: look its names up in `by-name.md`, open those shards, then open the sources they cite.


| shard | scope | size |
|---|---|---|
| [`camera.md`](index/camera.md) | acquisition, buffers, frame rate, IMAQdx, display cost | 4,239 chars |
| [`general.md`](index/general.md) | everything else | 14,608 chars |
| [`kernel-tracking.md`](index/kernel-tracking.md) | the tracking kernel, beads, calibration, reseed, xyz | 6,952 chars |
| [`motor-asi.md`](index/motor-asi.md) | PI motor, rotor, ASI stage and focus, serial/VISA | 5,477 chars |
| [`review-machinery.md`](index/review-machinery.md) | peer reviews, retrospectives, gates, violations, cost | 9,110 chars |
| [`toolkit-scripting.md`](index/toolkit-scripting.md) | ops, gscript helpers, recipes, VI Scripting technique | 42,512 chars |
| [`vi-structure.md`](index/vi-structure.md) | diagrams, wires, terminals, loops, the VI's own layout | 18,077 chars |
| [`by-name.md`](index/by-name.md) | identifier -> shard lookup, 286 names | |

Classes inside each shard: **MEASURED** (already measured) 쨌 **DECIDED** (already decided) 쨌 **FAILED** (already tried and failed) 쨌 **SUPERSEDED** (no longer true) 쨌 **EXISTS** (already built) 쨌 **OPEN** (known unknown).


=== by-name lookup ===
# by-name ??which shard to open for a given identifier

A plan always names things: an op, a VI, a wire, a uid, a method id. Look the name up here, open that shard, then open the source it cites.

- `- quadratic fit to phase nghbrd.vi` -> toolkit-scripting
- `-calculate phase in neighborhood.vi` -> toolkit-scripting
- `-calculate radial profile-openv2.vi` -> toolkit-scripting
- `-fit prepped I of r to cal.vi` -> toolkit-scripting
- `2026091` -> review-machinery
- `4294967` -> general
- `566EF80` -> general
- `566EFC0` -> general
- `632A813` -> vi-structure
- `633200D` -> vi-structure
- `6349C02` -> toolkit-scripting, vi-structure
- `6349C03` -> vi-structure
- `634AC00` -> kernel-tracking, toolkit-scripting
- `6356000` -> vi-structure
- `6356001` -> vi-structure
- `6356C00` -> vi-structure
- `6361000` -> vi-structure
- `6362004` -> kernel-tracking, toolkit-scripting
- `636D400` -> vi-structure
- `636D409` -> vi-structure
- `_v0.vi` -> toolkit-scripting
- `ASTRA_GUIBENCH_20260913.vi` -> toolkit-scripting
- `ASTRA_WIRING_20260913_v1.vi` -> toolkit-scripting
- `BenchE_Example8_ForLoops.vi` -> toolkit-scripting
- `build OpBuildPN_v0.vi` -> toolkit-scripting
- `byte readback for OpConstValue_v1.vi` -> toolkit-scripting
- `CAMBENCH_every_image.vi` -> toolkit-scripting
- `CAMDUMP_attributes.vi` -> toolkit-scripting
- `CAMDUMP_enumerate.vi` -> toolkit-scripting
- `Create Case Structure.vi` -> toolkit-scripting, vi-structure
- `Create While Loop.vi` -> motor-asi, toolkit-scripting
- `Create.vi` -> toolkit-scripting
- `DONOR_arrayops.vi` -> toolkit-scripting
- `DONOR_clfn.vi` -> toolkit-scripting
- `DONOR_Ex1_GetControlsWireIndicators.vi` -> toolkit-scripting
- `DONOR_Ex3_PrimitiveFunctions.vi` -> toolkit-scripting
- `Draw Flattened Pixmap.vi` -> camera
- `EMPTY_v0.vi` -> motor-asi, toolkit-scripting
- `Ex5_SubVIs_COPY.vi` -> toolkit-scripting
- `Ex6_WhileLoops_COPY.vi` -> toolkit-scripting
- `Exit While Loop.vi` -> motor-asi, toolkit-scripting
- `Flatten Pixmap.vi` -> camera
- `FPTARGET_v0.vi` -> toolkit-scripting
- `GObject Reference.vi` -> vi-structure
- `GPU_clfn_target.vi` -> toolkit-scripting
- `GPU_kernel_base.vi` -> toolkit-scripting
- `GPU_kernel_probe.vi` -> toolkit-scripting
- `GPU_kernel_v1.vi` -> toolkit-scripting
- `GPU_kernel_v1_partial.vi` -> toolkit-scripting
- `GUIBENCH_v0.vi` -> kernel-tracking, toolkit-scripting
- `HARNESS_base` -> kernel-tracking
- `HARNESS_base.vi` -> toolkit-scripting
- `HARNESS_compare.vi` -> toolkit-scripting
- `HARNESS_copy` -> toolkit-scripting
- `HARNESS_copy0` -> camera, motor-asi
- `HARNESS_copy0.vi` -> toolkit-scripting
- `HARNESS_copy1.vi` -> toolkit-scripting
- `HARNESS_copyloop` -> camera, vi-structure
- `HARNESS_copyloop.vi` -> toolkit-scripting
- `HARNESS_copyloop0.vi` -> toolkit-scripting
- `HARNESS_copyloopX.vi` -> toolkit-scripting
- `HARNESS_copyloopX0.vi` -> toolkit-scripting
- `HARNESS_disp` -> toolkit-scripting
- `HARNESS_disp0.vi` -> toolkit-scripting
- `HARNESS_disp1.vi` -> toolkit-scripting
- `HARNESS_disp2.vi` -> toolkit-scripting
- `HARNESS_disp3.vi` -> toolkit-scripting
- `HARNESS_disp4.vi` -> toolkit-scripting
- `HARNESS_dispI` -> camera
- `HARNESS_dispI.vi` -> toolkit-scripting
- `HARNESS_gpu` -> kernel-tracking
- `HARNESS_gpu.vi` -> toolkit-scripting
- `HARNESS_gpu2` -> kernel-tracking
- `HARNESS_gpu2.vi` -> toolkit-scripting
- `HARNESS_gpuk.vi` -> toolkit-scripting
- `HARNESS_loadcal.vi` -> toolkit-scripting
- `HARNESS_par.vi` -> toolkit-scripting
- `HARNESS_seq.vi` -> toolkit-scripting
- `HARNESS_track.vi` -> toolkit-scripting
- `HARNESS_Tracking` -> toolkit-scripting
- `HARNESS_tracking` -> toolkit-scripting
- `HARNESS_Tracking-prep I of r.vi` -> toolkit-scripting
- `Initialize.vi` -> motor-asi
- `KERNEL_asm.vi` -> toolkit-scripting
- `KERNEL_asm2.vi` -> toolkit-scripting
- `KERNEL_build_A.vi` -> toolkit-scripting
- `KernelBuilder_v1.vi` -> toolkit-scripting
- `KernelBuilder_v1_testbench_BACKUP.vi` -> toolkit-scripting
- `Load and prep N cal images.vi` -> toolkit-scripting
- `Move Axis to Position.vi` -> motor-asi
- `N beads PARALLEL over-kernel v2_KERNEL.vi` -> toolkit-scripting
- `Navigating Nodes and Wires.vi` -> kernel-tracking
- `OP_test1.vi` -> toolkit-scripting
- `OpAddShiftReg_v0` -> toolkit-scripting
- `OpAddShiftRegF_v0` -> toolkit-scripting
- `OpBuildBA_v0` -> toolkit-scripting
- `OpBuildCase_v0` -> toolkit-scripting, vi-structure
- `OpBuildCase_v1` -> kernel-tracking, toolkit-scripting
- `OpBuildFlatten_v0` -> toolkit-scripting
- `OpBuildIA_v0` -> toolkit-scripting
- `OpBuildInvoke_v0` -> toolkit-scripting
- `OpBuildPN_v0` -> toolkit-scripting
- `OpBuildPN_v1` -> toolkit-scripting, vi-structure
- `OpBuildUnflatten_v0` -> toolkit-scripting
- `OpCaseFrames_v0` -> toolkit-scripting
- `OpCLFNBuild_v0` -> toolkit-scripting
- `OpCLFNParams_v0` -> toolkit-scripting
- `OpCLFNPre_v0` -> toolkit-scripting
- `OpConnect2_v0` -> toolkit-scripting
- `OpConnect_v0` -> toolkit-scripting
- `OpConnectCtl_v0` -> camera, toolkit-scripting, vi-structure
- `OpConPane_v0` -> toolkit-scripting
- `OpConPaneAssign_v0` -> toolkit-scripting
- `OpConstValue_v1` -> kernel-tracking, toolkit-scripting
- `OpConstValueN_v0` -> kernel-tracking, toolkit-scripting
- `OpConstValueN_v1` -> motor-asi, toolkit-scripting
- `OpCreateControl_v0` -> toolkit-scripting
- `OpCreateControl_v1` -> toolkit-scripting
- `OpCreateIndicator_v0` -> toolkit-scripting
- `OpCreatePropNode_v0` -> toolkit-scripting
- `OpDelete_v0` -> toolkit-scripting
- `OpDeleteByLabel_v0` -> toolkit-scripting
- `Open` -> toolkit-scripting, vi-structure
- `OpExitLoop_v0` -> kernel-tracking, motor-asi, toolkit-scripting
- `OpExitWhile_v0` -> motor-asi, toolkit-scripting
- `OpForLoop_v0` -> motor-asi, toolkit-scripting
- `OpForLoop_v1` -> motor-asi, toolkit-scripting
- `OpForLoopIn_v0` -> kernel-tracking, toolkit-scripting
- `OpFP_v0` -> toolkit-scripting
- `OpFPLabels_v0` -> toolkit-scripting
- `OpLoopCast_v0` -> toolkit-scripting
- `OpLoopCast_v1` -> kernel-tracking, toolkit-scripting
- `OpLoopKernel_v0` -> toolkit-scripting
- `OpMakeDefault_v0` -> kernel-tracking, toolkit-scripting
- `OpMove_v0` -> toolkit-scripting
- `OpMoveByIndex_v0` -> toolkit-scripting
- `OpMoveByLabel_v0` -> toolkit-scripting
- `OpMoveOut_v0` -> toolkit-scripting
- `OpNetInfo` -> motor-asi
- `OpNetInfo_v0` -> toolkit-scripting
- `OpNetInfo_v1` -> toolkit-scripting, vi-structure
- `OpNo` -> vi-structure
- `OpNode_v0` -> toolkit-scripting
- `OpNodeInfo_v0` -> toolkit-scripting, vi-structure
- `OpNodeLabels_v0` -> toolkit-scripting, vi-structure
- `OpNodeTerms_v0` -> toolkit-scripting, vi-structure
- `OpOwnerChain_v0` -> vi-structure
- `OpPanelWiring_v0` -> toolkit-scripting, vi-structure
- `OpQueueDequeue_v0` -> toolkit-scripting
- `OpQueueEnqueue_v0` -> toolkit-scripting
- `OpQueueObtain` -> motor-asi
- `OpQueueObtain_v0` -> toolkit-scripting
- `OpQueueRelease_v0` -> toolkit-scripting
- `OpRemoveBadWires_v0` -> toolkit-scripting
- `OpReport_v0` -> toolkit-scripting
- `OpReport_v1` -> toolkit-scripting
- `OpReport_v2` -> toolkit-scripting
- `OpReport_v3` -> toolkit-scripting
- `OpReportAll_v0` -> toolkit-scripting
- `OpReportNodes_v0` -> vi-structure
- `OpSetAutoErr_v0` -> toolkit-scripting
- `OpSetIndexMode_v0` -> toolkit-scripting
- `OpSetLabel_v0` -> toolkit-scripting
- `OpSetName_v0` -> toolkit-scripting
- `OpShiftRegs_v0` -> toolkit-scripting, vi-structure
- `OpShiftRegs_v1` -> toolkit-scripting, vi-structure
- `OpSub` -> motor-asi
- `OpSubVI_v0` -> toolkit-scripting
- `OpSubVI_v1` -> toolkit-scripting
- `OpSubVIs_v0` -> toolkit-scripting
- `OpSubVIs_v1` -> toolkit-scripting, vi-structure
- `OpTunnelInd_v0` -> toolkit-scripting
- `OpTunnelRead_v0` -> toolkit-scripting
- `OpTunnels_v0` -> toolkit-scripting, vi-structure
- `OpWhileCast_v0` -> motor-asi, toolkit-scripting
- `OpWhileLoop_v0` -> motor-asi, toolkit-scripting
- `OpWhileLoopIn_v0` -> kernel-tracking, toolkit-scripting
- `OpWire_v0` -> toolkit-scripting
- `OpWire_v1` -> toolkit-scripting
- `OpWireCtl_v0` -> toolkit-scripting
- `OpWireInd_v0` -> toolkit-scripting
- `OpWireSource_v0` -> toolkit-scripting
- `OpWireSource_v1` -> motor-asi, toolkit-scripting
- `OpWireSource_v2` -> toolkit-scripting
- `OpWireSource_v3` -> toolkit-scripting
- `OpWireSource_v4` -> toolkit-scripting
- `OpWireSource_v5` -> toolkit-scripting, vi-structure
- `OpWireSR_` -> toolkit-scripting
- `OpWireSR_LeftIn` -> motor-asi
- `OpWireSR_LeftIn_v0` -> toolkit-scripting
- `OpWireSR_LeftOutCtl_v0` -> toolkit-scripting
- `OpWireSR_LeftOutNode_v0` -> toolkit-scripting
- `OpWireSR_RightIn_v0` -> toolkit-scripting
- `OpWireSRF_LeftIn_v0` -> toolkit-scripting
- `OpWireSRF_LeftOutCtl_v0` -> toolkit-scripting
- `OpWireSRF_LeftOutNode_v0` -> toolkit-scripting
- `OpWireSRF_RightIn_v0` -> toolkit-scripting
- `PARALLEL_build_testA.vi` -> toolkit-scripting
- `PARALLEL_kernel_v2.vi` -> toolkit-scripting
- `PARALLEL_kernel_v3.vi` -> toolkit-scripting
- `PARALLEL_kernel_v3_withdead.vi` -> toolkit-scripting
- `PARALLEL_kernel_v3clean.vi` -> toolkit-scripting
- `PARALLEL_kernel_v3fix.vi` -> toolkit-scripting
- `PARALLEL_smoke.vi` -> toolkit-scripting
- `PathToStr.vi` -> toolkit-scripting
- `py - augment the saved OpConstValue_v1.vi` -> toolkit-scripting
- `py - EMPTY_v0.vi` -> toolkit-scripting
- `py - finish GPU_kernel_v1.vi` -> toolkit-scripting
- `py - GPU_kernel_v1.vi` -> toolkit-scripting
- `py - HARNESS_copyloop.vi` -> toolkit-scripting
- `py - HARNESS_disp4.vi` -> toolkit-scripting
- `py - HARNESS_dispI.vi` -> toolkit-scripting
- `py - HARNESS_gpu.vi` -> toolkit-scripting
- `py - HARNESS_gpu2.vi` -> toolkit-scripting
- `py - OpAddShiftReg_v0.vi` -> toolkit-scripting
- `py - OpBuildBA_v0.vi` -> toolkit-scripting
- `py - OpBuildCase_v1.vi` -> toolkit-scripting
- `py - OpCaseFrames_v0.vi` -> toolkit-scripting
- `py - OpCLFNBuild_v0.vi` -> toolkit-scripting
- `py - OpCLFNParams_v0.vi` -> toolkit-scripting
- `py - OpCLFNPre_v0.vi` -> toolkit-scripting
- `py - OpConnectCtl_v0.vi` -> toolkit-scripting
- `py - OpConPane_v0.vi` -> toolkit-scripting
- `py - OpConPaneAssign_v0.vi` -> toolkit-scripting
- `py - OpConstValue_v0.vi` -> toolkit-scripting
- `py - OpConstValue_v1.vi` -> toolkit-scripting
- `py - OpConstValueN_v0.vi` -> toolkit-scripting
- `py - OpConstValueN_v1.vi` -> toolkit-scripting
- `py - OpConstWire_v0.vi` -> toolkit-scripting
- `py - OpCtrlValue_v0.vi` -> toolkit-scripting
- `py - OpExitWhile_v0.vi` -> toolkit-scripting
- `py - OpForLoop_v1.vi` -> toolkit-scripting
- `py - OpGetErrors_v0.vi` -> toolkit-scripting
- `py - OpLoopCast_v0.vi` -> toolkit-scripting
- `py - OpLoopCast_v1.vi` -> toolkit-scripting
- `py - OpMakeDefault_v0.vi` -> toolkit-scripting
- `py - OpMoveByIndex_v0.vi` -> toolkit-scripting
- `py - OpMoveOut_v0.vi` -> toolkit-scripting
- `py - OpNodeLabels_v0.vi` -> toolkit-scripting
- `py - OpNodeTerms_v0.vi` -> toolkit-scripting
- `py - OpOwnerChain_v0.vi` -> toolkit-scripting
- `py - OpPanelWiring_v0.vi` -> toolkit-scripting
- `py - OpReportAll_v0.vi` -> toolkit-scripting
- `py - OpReportNodes_v0.vi` -> toolkit-scripting
- `py - OpReportSubVI_v0.vi` -> toolkit-scripting
- `py - OpSetLabel_v0.vi` -> toolkit-scripting
- `py - OpShiftRegs_v0.vi` -> toolkit-scripting
- `py - OpShiftRegs_v1.vi` -> toolkit-scripting
- `py - OpSubVIs_v0.vi` -> toolkit-scripting
- `py - OpTunnelInd_v0.vi` -> toolkit-scripting
- `py - OpTunnelRead_v0.vi` -> toolkit-scripting
- `py - OpTunnels_v0.vi` -> toolkit-scripting
- `py - OpWhileLoop_v0.vi` -> toolkit-scripting
- `py - OpWireSource_v0.vi` -> toolkit-scripting
- `py - OpWireSource_v1.vi` -> toolkit-scripting
- `py - OpWireSource_v2.vi` -> toolkit-scripting
- `py - OpWireSource_v3.vi` -> toolkit-scripting
- `py - OpWireSource_v4.vi` -> toolkit-scripting
- `py - OpWireSource_v5.vi` -> toolkit-scripting
- `py - RAWCMD_rotor.vi` -> toolkit-scripting
- `py - SetCommand_signed.vi` -> toolkit-scripting
- `py - StrToPath.vi` -> toolkit-scripting
- `py - TRACK_kernel_v1.vi` -> toolkit-scripting
- `py - Track_v6_CPU_core_v0.vi` -> toolkit-scripting
- `py - Track_v6_CPU_queue_v0.vi` -> toolkit-scripting
- `RAWCMD_rotor.vi` -> toolkit-scripting
- `READONLY_fourfold_COPY.vi` -> toolkit-scripting
- `replayable build of PARALLEL_kernel_v3.vi` -> toolkit-scripting
- `s Configure.vi` -> toolkit-scripting
- `ScriptDriver_DropForLoop.vi` -> toolkit-scripting
- `ScriptTest_Driver.vi` -> toolkit-scripting
- `ScriptTest_Target.vi` -> toolkit-scripting
- `SetCommand.vi` -> motor-asi
- `SetCommand_orig_TEST.vi` -> toolkit-scripting
- `SetCommand_signed.vi` -> motor-asi, toolkit-scripting
- `SetCommand_signed_TEST.vi` -> toolkit-scripting
- `StrToPath.vi` -> toolkit-scripting
- `the saved HARNESS_gpu.vi` -> kernel-tracking
- `then StrToPath.vi` -> toolkit-scripting
- `Track N beads PARALLEL over-kernel v1.vi` -> toolkit-scripting
- `TRACK_kernel_v1.vi` -> toolkit-scripting
- `Track_v6_CPU_core_v0.vi` -> kernel-tracking, toolkit-scripting
- `Track_v6_CPU_queue_v0.vi` -> kernel-tracking, toolkit-scripting
- `uid 240` -> vi-structure
- `uid 43997` -> motor-asi
- `wire 4329` -> kernel-tracking



## Answer

{"duration_api_ms":219276,"stop_reason":"end_turn","session_id":"f67de2d1-5655-4e66-987f-89f09c2b755a","total_cost_usd":2.5325275000000005,"usage":{"input_tokens":28,"cache_creation_input_tokens":128027,"cache_read_input_tokens":1675935,"output_tokens":16566,"output_tokens_details":{"thinking_tokens":6578},"server_tool_use":{"web_search_requests":0,"web_fetch_requests":0},"service_tier":"standard","cache_creation":{"ephemeral_1h_input_tokens":128027,"ephemeral_5m_input_tokens":0},"inference_geo":"not_available","iterations":[{"input_tokens":2,"output_tokens":6576,"cache_read_input_tokens":148638,"cache_creation_input_tokens":2129,"cache_creation":{"ephemeral_5m_input_tokens":0,"ephemeral_1h_input_tokens":2129},"type":"message"}],"speed":"standard"},"modelUsage":{"claude-opus-5":{"inputTokens":28,"outputTokens":16566,"cacheReadInputTokens":1675935,"cacheCreationInputTokens":128027,"webSearchRequests":0,"costUSD":2.5325275000000005,"contextWindow":1000000,"maxOutputTokens":64000,"canonicalModel":"claude-opus-5","provider":"firstParty","costBasis":"list"}},"permission_denials":[],"terminal_reason":"completed","fast_mode_state":"off","fast_mode_disabled_reason":"sdk_opt_in_required","subagent_stats":{"spawned":0,"requested":{"background":0,"foreground":0,"unset":0},"started_in_background":0,"max_depth":0,"spawned_by_subagents":0,"completed":0,"failed":0,"killed":{"parent":0,"user":0,"system":0},"refused":{"depth_limit":0,"concurrency_limit":0,"budget":0},"by_type":{}},"is_error":false,"num_turns":26,"subtype":"success","api_error_status":null,"result":"# PRIOR-ART REVIEW ??\"next cycle of the V6 parallelisation project\" (direction-change)\n\n**Verdict up front: nothing in the five steps is novel. Four of the five were decided, measured or failed inside this project ??three of them on 2026-09-15, the same day this plan was written.** Step 4 additionally restates a specific factual error that a prior-art review already caught and that the recipe on disk has already been corrected for.\n\n---\n\n## PART A ??THE DIRECTION\n\n### A1 쨌 SETTLED ALREADY ??step 2's \"central risk\" was answered 2026-09-15 at 18:27 and 18:30\n\nThe plan says: *\"everything downstream depends on an operation the fleet has never performed: relocating an existing node from the frame loop into a new loop inside the same VI??Before anything else is built I will establish whether LabVIEW VI Scripting can move a node to a different diagram.\"*\n\nThat is already answered, twice, with machine gates:\n\n- `STATUS.md:269` ??*\"### 0a ANSWERED, 2026-09-15 18:27 ??the in-copy migration route WORKS (attempt 4, 3/3, `tools/recipes/probe_migrate_v2.py`)\"*\n- `STATUS.md:281` ??*\"create a loop in an existing VI ??drop the same subVI inside it ??wire a control across the border into a named terminal ??delete the original. **`GObject.Move` is not needed and was never used.**\"*\n- `STATUS.md:283` ??*\"### ??SETTLED by attempt 5 (`tools/recipes/probe_migrate_v3.py`, 5/5, 18:30) ??the migrated state COMPILES\"*\n- `STATUS.md:297-299` ??*\"So the in-copy restructure method is proven end to end??What remains untested is SCALE (75 nodes, 21 sibling couplings) and RUNTIME behaviour, **not feasibility**.\"*\n- Raw evidence: `tools/bench/probe_migrate_v2.log:3-10` (K1/K2/K3 pass, body uid 472 at Traverse index 1) and `tools/bench/probe_migrate_v3.log:12` ??*\"PASS M5 THE MIGRATED STATE COMPILES (ExecState == 1)\"*.\n\nAnd the framing ??\"move a node\" as the indispensable primitive ??was retired two days earlier: `docs/toolkit-capabilities.md:367` ??*\"### RESOLVED the same day ??the build route is clear, and 'move a node' was never needed\"*, with `docs/toolkit-capabilities.md:384-386` correcting the very inference the plan revives (*\"The earlier probe blamed `move_object` for breaking the VI. It did not: ExecState was already 0 immediately after `for_loop`\"*).\n\n**What my citation does NOT cover:** scale and runtime. `STATUS.md:299` explicitly leaves 75 nodes / 21 sibling couplings untested, and `STATUS.md` line 344 (step 0b) is the open item. A plan whose step 2 is *\"prove it on one harmless fragment in a COPY of the main VI\"* would be novel. *\"Establish whether VI Scripting can move a node\"* is not.\n\n### A2 쨌 REFUTED ALREADY ??step 1's ASI-first ordering was killed by the plan review on 2026-09-15\n\n- `archive/peer/2026-09-15-restructure-in-copy-plan.md:9` records the reviewed ordering as *\"kernel -> ASI serial -> display -> scheduler/writer\"*, and :11-15 kills it: *\"The 5.06 ms 'kernel + one serial round trip' is **not** the ordinary-frame cost??So 'move ASI out to win ~2.5 ms per frame' is void, and ASI-first ordering has no performance support.\"*\n- :93 ??*\"replace 'kernel, then ASI, then display' with 'measure unconditional latency, then construct one live vertical slice, then split whichever measured owner dominates.'\"*\n- Adopted into STATUS the same day: `STATUS.md:124` ??*\"The SHELL decision stands; the ORDERING was refuted by the plan review and is replaced\"*; `STATUS.md:129` ??*\"There is no ~2.5 ms ASI prize on ordinary frames, so ASI-first has no performance support\"*; `STATUS.md:133` ??step 1 is now *\"measure the unconditional per-frame path ??what actually executes every frame, p50 **and p99** | replaces all guessed orderings.\"*\n\n**Does the refutation still apply?** Its *premise* was weakened by the user ??`docs/camera-acquisition-facts.md:142` records *\"USER CORRECTION, 2026-09-15: ?ㅼ젣 ?ъ슜 寃곌낵 ASI濡?focus 議곗젙? 苑ㅻ굹 鍮덈쾲?섍쾶 諛쒖깮??"* ??so an ASI-owned loop is still justified. But :148-149 states the justification precisely: *\"The consequence is **dropped frames during focus adjustment**, i.e. a p99 / tail-latency defect, not an average-throughput one.\"* The plan's stated reason (\"the largest single win available\", ~2.5 ms, 150??00 Hz) is the refuted one, not the surviving one. Releasing this needs you to show that `STATUS.md:133` does not already order the measurement first.\n\n### A3 쨌 CONTRADICTED ??two separate cited facts\n\n**(i) The 5.06 ms / 2.5 ms figure contradicts its own source file, 55 lines above where it is stated.**\n\n- Plan's side ??`docs/camera-acquisition-facts.md:195-198`: *\"Kernel + a single serial round trip is **5.06 ms of the 6.00 ms**??it is the case for moving the serial read and the display out of the frame loop: doing so returns ~2.5 ms, which is the difference between 150 Hz and 200 Hz.\"*\n- The same file's answer ??`docs/camera-acquisition-facts.md:140`: *\"### ANSWERED: the frame loop does NOT transact serial every iteration (2026-09-12)\"*, :162 (the VISA case structure is a *\"gate only\"*), :169-171: *\"**So serial does not block 150 Hz.** It is paid only while a focus key is held\"*, and :177: *\"**What IS paid every frame is two `Value` property nodes**.\"*\n\nThis exact misreading has already been recorded once: `archive/peer/2026-09-15-restructure-in-copy-plan.md:15` ??*\"summation at line 183 and missed its own answer 44 lines earlier.\"* Citing :195 without :140 is the same defect a second time.\n\n**(ii) Step 4's \"Those are the two consumers of wire 751\" is false ??there are three.**\n\nFrom the census the plan's own uids come from, `tools/bench/census_opwiresource_v5.log`:\n\n| line | node | terminal | wire |\n|---|---|---|---|\n| :181 | uid **157** | `Owner` | 751 *(the source)* |\n| :161 | uid **482** | `reference` | **751** |\n| :183 | uid 163 | `reference` | 751 |\n| :221 | uid 1221 | `reference` | 751 |\n\nNode 482 is a Property Node reading `ClassName` (`census_opwiresource_v5.log:165`). It is the third consumer, and it is not in the plan.\n\n### A4 쨌 UNREAD EVIDENCE ??`tools/recipes/build_opownerchain_v0.py`, which already contains the fix for A3(ii)\n\nThe recipe the plan proposes to write exists and has already been corrected for precisely this error:\n\n- `tools/recipes/build_opownerchain_v0.py:64-68` ??*\"**THE THIRD CONSUMER.** The prior-art review (`archive/peer/2026-09-15-priorart-ownerchain.md`?? caught this before the build was ever launched: wire 751 has THREE consumers, not two ??node 163, node 1221 AND **node 482** ??and `tools/bench/build_opwiresource_v5.log:35-39` records that the first v5 rewire failed for exactly this reason??**I read past it.** All three are rewired below.\"*\n- `:69` ??`REWIRE_SINKS = [N_OWNER_CLASSNAME, N_CASTGOBJ, N_OWNER_CLASSNAME2]`.\n\nAlso unconsulted: `docs/NAMES.md:509-532` (for step 5), `docs/toolkit-capabilities.md:244` and `tools/bench/build_opgeterrors.log` (for step 3), and `STATUS.md:269-299` (for step 2).\n\n---\n\n## PART B ??THE ARTIFACTS\n\n### B1 쨌 ALREADY BUILT ??both artifacts the plan proposes are already written recipes\n\n| plan step | file on disk |\n|---|---|\n| 3 ??`VI.Get Errors` (452) as an op | `tools/recipes/build_opgeterrors.py:1-7` ??*\"OpGetErrors_v0.vi: read a VI's ERROR LIST by script (VI method `Get Errors`, ID 0x452????build_invoke(\"VI Server:VI\", \"452\"), branch 'vi reference' -> Invoke.reference, indicators on every Invoke output\"* |\n| 4 ??`OpOwnerChain_v0` from `OpWireSource_v5` | `tools/recipes/build_opownerchain_v0.py:1-41` (full spec + prediction contract B1?밄6), `:57-69` (uid table, corrected rewire list) |\n\nThe plan describes both as work to be done. Neither `OpGetErrors_v0.vi` nor `OpOwnerChain_v0.vi` is in the 168-VI claudeDev listing (`archive/peer/2026-09-15-priorart-ownerchain.md:82`), so the *VIs* do not exist ??but the recipes, uids and acceptance gates do, and step 4's design regresses `build_opownerchain_v0.py:69` back to two sinks.\n\n### B2 쨌 ALREADY FAILED ??three of the five steps repeat a recorded failure\n\n**Step 3 ??`VI.Get Errors` 452 has failed twice, identically:**\n\n- `tools/bench/build_opgeterrors.log:1-9` (2026-09-09): *\"after reference wire: ExecState 0 / t1: indicator 'reference out' / t3: indicator 'error out 2' / assembled: ExecState 0 outputs ['reference out', 'error out 2'] / STOP: not saved / BGRUN END rc=5\"*\n- `tools/bench/build_opgeterrors.log:10-18` (2026-09-14): **byte-for-byte the same result.**\n- Recorded cause ??`docs/toolkit-capabilities.md:244`: *\"`VI.Get Errors` (`0x452`) | **FAILED 2026-09-09** ??Invoke node created with only reference/error terminals, with and without the private ini tokens.\"*\n- **Recorded next step, which the plan does not take** ??`docs/toolkit-capabilities.md:232-234`: *\"Whether `Control.Value` 633200D and `VI:Get Errors` 452 were walker artefacts or genuine 1077s is now a one-call question each (**an `OpBuildInvoke_v1` with the same exposure is needed for the Invoke case**).\"* `OpBuildInvoke_v1` appears nowhere in the project except that sentence (grep: one file). The plan describes no mechanism that differs from the two runs above, so as written it is attempt 3 of the same build.\n\n**Step 4 ??the orphaned-consumer failure is on record:** `tools/bench/build_opwiresource_v5.log:35` lists `(482, 'Property Node', 'reference')` among *\"unwired sinks after the rewire\"*, :37 *\"DIAG re-fed node 482 (Property Node) 'reference' from the Owner output\"*, :38 *\"OBSERVED ExecState per step: [('copy of v4', 1), ('wrong Owner wire removed', 0), ('owner-uid branch rewired', 0), ('orphaned references re-fed', 1)]\"* ??i.e. the op stayed broken until 482 was re-fed. A two-sink rewire reproduces it.\n\n**Step 5 ??`count(\"Diagram\") - 1` is the bug that voided Step 0a attempts 1 and 2:**\n\n- `docs/NAMES.md:513-515` ??*\"| attempt | how the index was derived | what happened | ??| 1, 2 | `count(\"Diagram\") - 1`, i.e. 'the newest is last' | **the subVI landed on a pre-existing diagram, silently, and a whole-VI SubVI count called it a pass** |\"*\n- `docs/NAMES.md:521-522` ??*\"**there is no rule about where a new diagram lands, and looking for one is the error.**\"*\n- `STATUS.md:322` ??*\"`count(\"Diagram\") - 1` ('the newest is last') was wrong\"*; `STATUS.md:329` ??*\"The probe used `body_index = count(\"Diagram\") - 1`, so `drop_subvi` put the subVI on **some other, pre-existing diagram** ??no error.\"*\n\nThe plan's justification ??*\"since a newly created object is appended last\"* ??is the refuted premise verbatim.\n\n### B3 쨌 HELPER EXISTS ??step 5 hand-rolls addressing the toolkit already provides\n\n`docs/NAMES.md:524-532`, *\"Use what already exists instead of deriving an index\"*:\n\n- `gscript.new_since(target, cls, before)` ??`tools/gscript.py:829`; `NAMES.md:526-528` quotes its own docstring: *\"Use this, NOT position matching, to identify what a mutating Op just created.\"* It returns each object's real Traverse index `i` **and** its uid.\n- `gscript.loop_diagram(target, loop_pos)` ??`tools/gscript.py:847` (`LOOP_DIAGRAM_OFFSET`, 21횞 margin, `NAMES.md:529-531`).\n- `gscript.find_at` ??`tools/gscript.py:866`; verify arrival with `gscript.subvis(target, index)` ??`tools/gscript.py:330`, per `NAMES.md:532`: *\"verify arrival by **listing that diagram's contents**??never by a whole-VI count.\"*\n\nBoth proven probes already use this route: `tools/bench/probe_migrate_v2.log:3` ??*\"new body uid 472, Traverse index 1 (new_since reported i=1)\"*.\n\n*(Note: `fidx()` is named in STATUS-era prose but is **not** in `tools/gscript.py` ??the real calls are the four above.)*\n\n### B4 쨌 ALREADY MEASURED ??step 3's justification is spent, and step 4's acceptance value is already known\n\n**Step 3.** The plan's reason for `VI.Get Errors` is *\"three consecutive ExecState-0 diagnoses were settled by inference when this reader would have answered them in one run.\"* The concrete open question it was queued for ??*\"does the migrated state COMPILE?\"* (`STATUS.md:311-315`, which names 452 as the deciding tool) ??was answered **without it** thirty minutes later, by choosing a donor with no conditional terminal and a type-matched border wire: `tools/bench/probe_migrate_v3.log:12` (`M5 ??ExecState == 1`), `STATUS.md:283-297`. Independently, the outcome review named this build specifically: `archive/peer/2026-09-15-outcome-review-20260915.md:221` ??*\"`VI.Get Errors` and frame-polarity work **unless the delivery actually fails without them**\"*, :227 ??*\"Its next problem is not missing tooling\"*, :230 ??`OUTCOME-VIOLATION: tooling-over-delivery`.\n\n**What my citation does NOT cover:** `CLAUDE.md`'s \"build the reader\" rule and `STATUS.md:314-315` argue the outcome review's skip *\"was right when no broken-VI question was open, and it is wrong now that one is.\"* If a *currently open* ExecState-0 question exists that probe v3 did not close, name it ??that is the refutation this finding needs. Absent one, `probe_migrate_v3.log:12` closed the question that justified it.\n\n**Step 4.** The acceptance oracle is already recorded: `tools/recipes/build_opownerchain_v0.py:36-38` ??*\"B6 FUNCTIONAL: asked for the UID of `CaseStructure#10407`, the op reports an owner whose class is `Diagram` and whose UID is 639 ??the frame loop's body, **which two independent measurements already established**\"* ??cross-referenced at `docs/diagram-hierarchy.md:46` and `tools/bench/diagram_tree_main.json:370`.\n\n---\n\n```\nPRIOR-ART: settled-already      (step 2 ??STATUS.md:269,281,283,297-299; probe_migrate_v3.log:12; toolkit-capabilities.md:367)\nPRIOR-ART: settled-already      (step 1 ordering ??STATUS.md:124,129,133)\nPRIOR-ART: refuted-already      (step 1 justification ??archive/peer/2026-09-15-restructure-in-copy-plan.md:11-16,93)\nPRIOR-ART: contradicted         (5.06/2.5 ms ??camera-acquisition-facts.md:195-198 vs :140,:169-171,:177)\nPRIOR-ART: contradicted         (step 4 \"two consumers of wire 751\" ??census_opwiresource_v5.log:161,181,183,221)\nPRIOR-ART: unread-evidence      (build_opownerchain_v0.py:64-69 already carries this correction)\nPRIOR-ART: already-built        (build_opgeterrors.py:1-7; build_opownerchain_v0.py:1-41,57-69)\nPRIOR-ART: already-failed       (step 3 ??build_opgeterrors.log:1-9,10-18; toolkit-capabilities.md:244,232-234)\nPRIOR-ART: already-failed       (step 4 ??build_opwiresource_v5.log:35-39)\nPRIOR-ART: already-failed       (step 5 ??NAMES.md:513-515,521-522; STATUS.md:322,329)\nPRIOR-ART: helper-exists        (step 5 ??gscript.py:829 new_since, :847 loop_diagram, :866 find_at, :330 subvis)\nPRIOR-ART: already-measured     (step 3 justification ??probe_migrate_v3.log:12; outcome-review:221,227,230)\nPRIOR-ART: already-measured     (step 4 oracle ??build_opownerchain_v0.py:36-38; diagram-hierarchy.md:46)\n```\n\n**The narrowest correct next step that survives every citation above** is the one `STATUS.md:133` already names and `STATUS.md:344` already queues: measure the unconditional per-frame path (p50 **and** p99), and run step 0b ??the migration on one harmless fragment of a *copy of the main VI* ??because scale, not feasibility, is what `STATUS.md:299` leaves open.","ttft_ms":9443,"type":"result","duration_ms":223206,"uuid":"35187fa4-6439-418b-b3c6-b677113db28b","ttft_stream_ms":1593,"time_to_request_ms":160,"queued_turn_count":0}



## Sources

(extract from answer)

## What was done with it

(Claude fills in)
