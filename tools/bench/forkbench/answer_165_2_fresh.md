이번 hand-back 2에 대한 판단은 **next.json 수정(라운드 3/3 진행)** 입니다. 벤치 모드라서 파일은 하나도 쓰지 않았습니다. 아래는 제가 썼을 내용입니다.

**판단 근거**
- **받아들인 것:** 165-2-1이 낸 항목 0–3과 step-5 크기 계산을 받아들입니다. 입력 해시 23/0, c127 선례 인용, 160-c3-2 종료가 확인됐습니다. 접두 구간별 MAIN은 642.6 / 657.1 / 665.0이고 모두 675 이하입니다. REALSIM은 13/13이고, 단계별 경로는 이미 `connect_term_uid`입니다.
- **실패 원인 (코드에서 직접 확인):**
  - 기준 상태 PRIME 단계(`tools/stagexec.py:2621-2640`)는 기준 그래프에서 이미 선이 연결된 계획 끝단을 모두 `be.addr.triple`로 미리 확인합니다.
  - t8776/t24342 안쪽 면에는 기준 시점에 아직 짧은 선 조각(w10362/w25232)이 붙어 있습니다.
  - 그래서 계획의 `delete_wire`가 실행되기도 전에 `_triple`이 `:1934`에서 거부합니다. LoopTunnel이 `FACE_ROUTED`(`:1366`)에 속하기 때문입니다.
  - 시뮬레이션에서는 `pre_fail("ADDRESS")`(`:2650`)로 나타났습니다. 실제 실행이었다면 `:2648`에서 "stop before op 1"로 멈췄을 것입니다.
  - 165-1-1의 셀프 테스트는 컴파일과 단계별 경로만 확인했고 PRIME은 확인하지 않았습니다. 그렇게 요구한 것은 제 PD400(b)이므로 이 빈틈은 판단 쪽 책임입니다.
- **결정:**
  - stagexec만 좁게 고칩니다. PRIME이 건너뛰는 끝단은 다음 조건을 **모두** 만족할 때뿐입니다.
    1. LoopTunnel 안쪽 면의 sink입니다.
    2. 기준 시점의 선이 소스 없이 그 면 하나에만 붙은 선 조각입니다.
    3. 그 선을 지우는 `delete_wire`가 같은 계획에서 더 앞에 있고, 체크포인트입니다.
  - 건너뛸 때마다 로그를 남깁니다.
  - 그다음 step 5를 PD400(c)/PD401(b) 그대로 진행합니다.
  - 컴퓨테이션(rule 1a)은 바뀌지 않습니다. 바뀌는 것은 끝단 주소를 언제 확인하느냐뿐입니다.
- **사이클 제한:** 이번이 마지막 라운드입니다(`max_handbacks_per_cycle` 3). STATUS의 "STOP - USAGE"는 사이클 165를 마친 뒤 멈추라는 뜻이라서 이 라운드는 진행할 수 있습니다.
- gate-fp 대기열은 LabVIEW 카드 다음에 처리합니다. 훅 쪽 항목은 채팅 세션 몫입니다.

```json
{
 "schema": "next/1",
 "cycle": 165,
 "act": "Hand-back round 3 of 3 (PD402): base PRIME refuses the stub-holding LoopTunnel inner faces t8776/t24342 before the plan's own delete_wire rows (stagexec.py:2621-2640 -> _triple :1934). Tool fix FIRST only because this gate refuses the step-5 plan itself: PRIME skips such an end narrowly, self-tested; then step-5 plan K3f+K4+K4f on 2a5fa0c4 -> gates + prior-art -> ONE scratch on a new byte copy of 6dcd5c3d -> adopt D1_ring_p5_<ts>.vi if A80 reached -> tooling after the LabVIEW card",
 "task_kind": "build",
 "plan": {"path": "docs/d1/ring-p5c.md", "md5": "<md5 of ring-p5c.md after PD402 is written>"},
 "pass": [
  "Cite only, already met (PD401/PD402): diag_c165_a1_1_facts.md:8-45; diag_c165_a2_1_facts.md hashes 23/0 + c127 precedent diag_c127_1_fsinner.log:81-102; result_160-c3-2.json PASS",
  "Before the edit: re-hash stagexec 6ea6637f, plan_ring_p5s02r_in.json 0b895983, VI 6dcd5c3d, graph 2a5fa0c4; any drift = hand back",
  "PD402(b) stagexec fix: PRIME skips an end ONLY if (1) LoopTunnel InnerTerminal sink, (2) its base wire has exactly one terminal row (this face) and no source, (3) that wire uid is the wire_uid of a delete_wire op EARLIER in the plan than the action using the end, and that op is a checkpoint; each skip logged (end, wire, deleting op); new stagexec md5 quoted",
  "Every other end primed exactly as before; stored dry reports byte-equal (skip key written only when a skip happens)",
  "Self-test on 2a5fa0c4: r_in step-5 plan finalizes in SB REALSIM with route PASS, 0 UNROUTABLE; non-collect PRIME raises nothing for t8776/t24342 and logs 2 PRIME-SKIP lines",
  "Negatives still refuse (counts quoted): n1 no delete_wire; n2 delete_wire of another wire; n3 delete_wire after the connect; n4 wired SelectorTunnel / Flat Sequence inner face; n5 delete_wire not a checkpoint; n6 base wire with a source or >1 terminal row",
  "Six stored plans (p5s01a/b, p5s02a-d) compile + dry byte-equal; c157/c158/c165 innerface, stagesim, stagexec self-tests green (counts quoted)",
  "plan_ring_p5s02e.json re-made on 2a5fa0c4 over the 20bde81a (final False) bytes, new:* bound by quoting diag_c164_p5s02d_scratch.log; K3f+K4+K4f, 13 rows, MAIN <= 675 quoted; final True",
  "Every delete_wire a checkpoint; A70/A80 predictions per PD401(b): census in [{}, {'Wire': 1}], face on the OK3 / OK4.outer net, Is Broken? False",
  "stagesim end graph: w10362 / w25232 absent; t8776 / t24342 on the OK3 / OK4.outer nets, quoted",
  "Recipe pair = the step-4 recipe's inputs on the shared stagekit gates; dry both PASS or PASS-UNVERIFIED (CEN2 only); PB rows quoted; PB block = hand back",
  "prerun PASS; --check-launch PASS (CEN2-only unverified allowed); --scratch-required exit code quoted",
  "Predicted step-5 Error List from step 4's 53-item expected file: items cited to actions, the rest UNPREDICTED; file + md5",
  "Prior-art review of the step-5 plan INCLUDING the PRIME change (flags.peers include priorart): novel + disposition, or released by FIXED:/REFUTED: lines",
  "ONE scratch on a NEW byte copy of 6dcd5c3d: peak <= 675, every BLOCK gate PASS, PRIME-SKIP lines for t8776/t24342 quoted; any other result = RETURN, no second run",
  "Scratch, per stub-delete + connect pair: PD401(b) facts quoted (face wire 0 after delete, census, face on OK net, not broken, Error List delta); anything else = RETURN",
  "On PASS adopt claudeDev D1_ring_p5_<ts>.vi if A80 reached (P5 final, broken file 6 of 6), else D1_ring_p5s02e_<ts>.vi; md5",
  "Adopted file: graph read + md5; t8776 / t24342 real sources vs the stagesim prediction; full Error List vs the prediction item by item",
  "tools/bench/memory_model.json: ONLY one load_by_vi entry for the adopted md5 (MB line cited); every other key equal by JSON compare, fail_above_mb 680",
  "Measured census written into the step-5 pred by a script citing the graph reads; census keys only; md5s",
  "AFTER the LabVIEW card: PD397(e) PB tightening + self-test (3 negatives), stored p5s02c/d + step-5 PB inputs still RECORD every row; fp-86 drained",
  "AFTER the LabVIEW card: E5 + reuse detectors judge a deleted node by identity (class, owner, owner uid, position) in the shared module; self-test with a planted survivor caught; fp-87/fp-88 drained",
  "Gate-run suites re-pinned once (names listed); one fn-descriptions batch (~60) into docs/fn_descriptions.json",
  "Originals not opened; eb1d0f31, 7f2582ae, 94ffff94, f9ae7751, 564d8cbe, 6dcd5c3d unchanged by hash; LabVIEW closed and verified gone"
 ],
 "blocked_by": null,
 "stop_requested": false,
 "advances": ["M3", "M8", "R1"],
 "note": "Hand-back 2 judged (PD402): 165-2-1 items 0-3 + step-5 sizing accepted; the refusal is the base PRIME pass, not the per-step route (my PD400(b) gap). Last round 3/3: a failed self-test or a returned scratch closes cycle 165 on this purpose, and cycle 166 carries it. If A80 is adopted, cycle 166 = P6 run. STATUS STOP-USAGE: the runner stops after cycle 165."
}
```

**참고할 점**
- 디스크에는 이미 PD402, 이 next.json의 이전 판(md5 ffb92f59), 그리고 라운드 3 결과(`result_165-3-*`, `handback_165_3`)가 있습니다. 미래 결과를 쓰면 벤치가 오염되므로 라운드 3 결과는 읽지 않았습니다.
- 다만 원인을 확인하려고 stagexec를 열었을 때, 165-3-1의 PRIME-skip 코드(`:2630-2634`)가 이미 들어가 있는 것은 보였습니다.
- 디스크에 있는 판과 다른 점은 두 가지입니다.
  - 건너뛰기 조건에 "선 조각이 그 면 하나에만 붙어 있고 소스가 없음"을 추가했습니다.
  - 거부 사례 n5(체크포인트가 아닌 삭제)와 n6(소스가 있거나 여러 끝단에 붙은 선)을 추가했습니다.
- `plan.md5`는 PD402를 실제로 쓴 뒤에야 정해지므로 자리표시자로 두었습니다.