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
