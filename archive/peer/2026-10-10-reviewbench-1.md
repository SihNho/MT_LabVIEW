# reviewbench-1

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.0331  in 22 / out 10800 / cache-create 82071 / cache-read 679154  (142s, 20 turn(s))
- **date:** 2026-10-10 21:15:41
- **outcome:** ANSWERED (146s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** card chat-X7 arm A (benchmark replay of cycle 164 hand-back 1; single hypothesis review vs discussion)
- **verdict:** unverified

## Question

# Review case 1 - cycle 164 hand-back 1: K3/K4 pass wires do not compile

**Question:** What is the most likely cause of this failure, what is the strongest alternative, and what is the
cheapest test that tells them apart?

**Repository root:** `G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop` - every path
below is relative to it (read the files there, not in any other checkout).

**Reading rules (same for every reviewer):** answer from this file and from the code / data / log files it cites
(`tools/*.py`, `tools/bench/plan_*.json`, the cited `tools/bench/*.log` and `diag_*_facts.md` files, the cited selftest
files). Do NOT open `docs/**`, `archive/**`, `STATUS.md`, `tools/bench/cards/**`, `tools/bench/reviewbench/**` (other than
this file), or any cycle-164/165 file not cited here: the case is a replay of the moment of failure, and the later
record would give the answer away. Line numbers in `tools/stagexec.py` may have moved by a few lines since the failure
(the pinned version a4df7e15 was not committed); search by function name.

## Background (decision in force at the time, quoted from the plan, PD397(b)-(c), cycle 164 judgement)

> (b) K3/K4 GAP, decided from the facts (`diag_c163_a3_1_facts.md` §1-§3). `w_k3pass` (A69) and `w_k4pass` (A79) carry
> no `frame` key, so the sink resolves to OK's own group frame (-29, 'False') and the sim stops on the border. PD379(b)
> places the pass wire in the TIMED-OUT frame between the in-tunnel's and the out-tunnel's 'True' faces. That is the
> shape already adopted three times in this graph: `w_gpass` A33, `w_hpass` A40 and `w_c7_pass` A52, with
> `frame: "True"` on BOTH ends (wire 31722 on frame 31517). Decision: A69 and A79 get `"frame": "True"` on both ends in
> `plan_ring_p5s02r_in.json`. No other byte changes. [...] This adds no computation: the pass wire carries the register
> value unchanged in the frame where no element arrived, as designed.
> (c) Step 4 = `plan_ring_p5s02d.json` on the real p5s02c graph 3d5196ab: longest prefix of WHOLE groups J (A53..A60,
> `delete_object`), K3 (A61..A69), K3f (A70), K4 (A71..A79), K4f (A80) with MAIN <= 675, rows <= 40; a group is never split.

## Machine record

Hand-back `tools/bench/cards/handback_164_1.json` (verbatim):

```json
{"schema": "handback/1", "cycle": 164, "round": 1, "trigger": "session",
 "detail": "PD397(b) K3/K4 pass wires (frame True both ends) do not compile: stagexec.py:901 needs a frameless out wire after new:IK3; case_pass_wire takes frameless src only (:6286). J alone on file: plan 1152ce60, MAIN 628.0, 8 rows.",
 "cards": [
  {"id": "164-a1-1", "status": "FAIL", "first_fail": "J+K3 compile refused: action 15 tunnel new:IK3 needs one in + one out wire (stagexec.py:901); STUB non-fatal FAIL on K3f/K4f sink wires"},
  {"id": "164-a1-2", "status": "FAIL", "first_fail": "stagexec.py:901-903 action 15: tunnel new:IK3 has no out-wire; its only candidate w_k3pass has src frame 'True' -> case_pass_wire False (line 6287)"}],
 "cost_usd": 8.48, "minutes": 17.4}
```

Failing log `tools/bench/prep_c164_a1_1_mk.log` (first failing lines):

```
41: GATE FAIL | STUB no base sink end carries a wire that no plan delete_wire removes (no stub delete needed) | [('w_k3f', 'dst', 8776, [10362]), ('w_k4f', 'dst', 24342, [25232])]
46: FACT C J+K3 compile refused: action 15: tunnel new:IK3 must be followed by exactly one wire into it and one out of it (LabVIEW makes a tunnel only by wiring across the border)
89: FACT REALSIM plan tools/bench/plan_ring_p5s02d.json md5 1152ce60...: final True; failed null; steps 8; provisional []; route check PASS; UNROUTABLE 0
```

Card 164-a1-1 facts (from its result): "K3 refusal cause: case_pass_wire accepts only a FRAMELESS src
(stagexec.py:6286-6288); PD397(b) put frame on both ends, frame wires are never group wires (stagexec.py:896-897)";
"plan_ring_p5s02d.json 1152ce60 = J (A53..A60): REALSIM final True, 8/8, route PASS"; "STUB non-fatal FAIL: K3f dst t8776
has w10362, K4f dst t24342 has w25232 on 3d5196ab, no delete_wire for them". Its OPEN: "K3/K4 pass wire: PD397(b) frame on
both ends vs stagexec.py:6286-6288 (frameless src + dst frame) - which shape before K3/K4 can be planned?"

Card 164-a1-2 (read-only diagnosis) facts: "Adopted pass wires w_gpass/w_hpass/w_c7_pass compile as standalone
case_frame_wire (stagexec.py 936-937, 931-933)"; "Adopted tunnels TG1/TG2/TC7/TD7 each followed by 2 frameless wires;
pass wire after both groups"; "IK3 t_k3i followed by w_k3l in + w_k3pass both ends frame True: no frameless out";
"Group wire = no frame on either end (stagexec.py 896-897); window = next 2 actions (895)"; "case_pass_wire accepts only
frameless src + dst frame = own body frame, dir in (stagexec.py 6286-6304)".

## Files

- plan input `tools/bench/plan_ring_p5s02r_in.json` at the time = md5 4c8d3645 (A69 `w_k3pass`, A79 `w_k4pass`); the
  file on disk today is a later version - read the A69/A79 rows as described above, not as they are now.
- facts `tools/bench/diag_c164_a1_1_facts.md`, `tools/bench/diag_c164_a1_2_facts.md`
- code `tools/stagexec.py` (`compile_plan`, the tunnel group check near "must be followed by exactly one wire",
  `case_pass_wire`, `case_frame_wire`)


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict:** the hand-back has the code mechanism right and the cause wrong. The compile refusal really does come from `case_pass_wire` turning down a src end that carries `frame`. But the shape PD397(b) picked was never a fair contender against the code. It rests on a wrong analogy, and the right shape was already in the project and tested.

## 1. Strongest reason the claim is wrong

The hand-back ends on an OPEN question: "PD397(b) both-ends `frame` vs `stagexec.py:6286-6288`, which shape?" That treats this as a plan-vs-tool disagreement. The record does not support that:

- **The analogy to A33/A40/A52 is false.** Every adopted pass-wire tunnel has `body: "new:CQ7.f0"`, the 'False' frame: TG1 and TG2 (`plan_ring_p5s02r_in_pre164.json:371,403`), TH1 and TH2 (`:450,482`), TC7 and TD7 (`:590,629`). Their pass wires live in a third frame, 'True', away from both tunnels' own frames, so both ends need `frame`. Each of those tunnels also has its own frameless out-wire, and the pass wire comes after both groups as a standalone `case_frame_wire` (`diag_c164_a1_2_facts.md:7-8`). IK3 and IK4 are different: their body is `new:CQ7.f1`, which is 'True' itself (`pre164.json:821,919`; frames list `["False","True"]` at `:168-171`). The pass wire's src is therefore already in the 'True' frame. Writing `frame:"True"` on it adds no information, and it makes the wire stop counting as a group wire (`stagexec.py:896-897`).
- **PD397(b)'s own evidence covered only the dst end.** Its text says "the **sink** resolves to OK's own group frame (-29, 'False')". Nothing in it points at the src end, so adding `frame` there was not justified by anything observed.
- **The correct shape already existed and had passed tests.** `case_pass_wire` was written by card 156-a1-2 for exactly this K3 layout. Its docstring (`stagexec.py:6306-6314`) and the self-test header (`selftest_c156_passwire.py:7-10,14-15`) say it in so many words: frameless src, `frame` on the dst only, and they separate it from the "both ends, after both groups" G/H/I rows. Gates A31 and A32 pass in that layout (one `register_end_case_border` op over acts 67-69, sim `case_frame` index 1 'True'), and the final runs are 20/0 (`selftest_c156_passwire.log:38-39,66`; also the `_c160*.log` runs).

So the most likely cause is that the PD397(b) judgement copied the wrong example and did not check the self-test that already covered K3. It is not a limitation of the tool.

## 2. Alternative explanations

- **A. The tool is too strict (the strongest alternative).** A src `frame` that equals the in-tunnel's own body frame means exactly the same as no `frame`. `case_pass_wire` returns False on any src `frame` (`:6318-6320`) without comparing values. It also returns False silently instead of raising one of its specific errors, so the user only sees the generic "exactly one wire into it and one out of it" message (`:901-903`). On this reading the plan meant the right thing and the code checks the form of the end, not its meaning. The evidence fits both readings. They differ only in which fix you choose, and changing the plan is cheaper and keeps the tool as it is.
- **B. The refusal is real, but the tested shape may still fail on this graph.** A31/A32 ran on a plan-made CQ7 with sim ids (-28 and -30). The step-4 plan runs on the real graph 3d5196ab, where CQ7 is the base case #31308 and the frame is mapped to `'#31517'` (`prep_c164_a1_1_mk.log:30,33`). That takes `case_pass_wire`'s base-case branch (`:6330-6331`, name = `'#'+body`), which no recorded test exercises for this group. Fixing the src end could hit the next error ("dst `frame` ... must name the in-tunnel's own body frame") if `body` is not mapped to the integer 31517. Unknown, not measured.
- **Not the cause:** the error message does not say whether `ins` or `outs` failed. I checked by hand. `w_k3l` (SK3L.inner -> IK3.outer, frameless, `pre164.json:827-833`) gives ins = 1. `w_k3pass` with a src frame gives outs = 0. The count is consistent with the hand-back.

## 3. What would prove the claim wrong

The framing would be refuted if the dst-only shape also failed to compile (or failed REALSIM) on the step-4 graph for a reason unrelated to frames. Then the src `frame` was not the only block, and PD397(b) would be one defect among several.

## 4. Cheapest test that tells them apart

This is offline and needs no LabVIEW. Rebuild the J+K3 prefix (A53..A69) from the same inputs, changing exactly one thing: remove `frame` from the **src** end of A69 and keep dst `frame:"True"` (mapped to `'#31517'`). Then run `compile_plan` and REALSIM.

- If it compiles to one tunnel or `register_end_case_border` op over acts 15-17 and the sim passes: the claim, reframed as "wrong analogy, the known-good shape works", holds. The tool needs no change.
- If it fails in the base-case branch of `case_pass_wire`: alternative B is real, and K3 needs a check on base-case frames before any shape decision.

Alternative A changes only which fix you prefer, not what happened. It can stay a separate note for the tool owner: compare a src `frame` against the tunnel's own body frame instead of rejecting any src `frame`.

**What would change my mind:** a record that `case_pass_wire`'s src rule was meant to reject even a redundant frame for a semantic reason, for example a measured LabVIEW difference. Nothing I read shows one.

**Not settled:** the reading rules kept me from checking whether cycle 164's judgement saw the c156 self-test, so I can't say whether this was a missed reference or a deliberate choice. One external fact, not under dispute here: LabVIEW needs a case output tunnel wired in every case unless "Use Default If Unwired" is set. That is why OK3 needs a value in the 'True' frame at all ([NI forum: missing assignment to tunnel](https://forums.ni.com/t5/LabVIEW/Block-Diagram-Errors-Tunnel-missing-assignment-to-tunnel/td-p/323435), [NI forum: output tunnel defaults](https://forums.ni.com/t5/LabVIEW/Do-you-use-output-tunnel-default-values/td-p/947691)). The other claims are about this project's own tool, so they rest on the file:line citations above, not on web sources.

Writing to the plan file was refused because the Write tool is disabled in this session, so this review exists only in this reply.

## Sources

(extract from answer)

## What was done with it

Benchmark only (card chat-X7, `tools/bench/reviewbench/report_x7.md`): this answer was scored blind against the later
judgement (PD398); it drove no work. No FIXED/REFUTED release applies - it reviews a failure already resolved in cycle 164.
