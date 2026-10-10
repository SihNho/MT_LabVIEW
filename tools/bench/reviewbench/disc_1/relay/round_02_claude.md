[2라운드] Claude (21:17, 80s, $0.81)

질문 2에는 동의합니다. 질문 1에는 "그룹 모양의 차이보다 강한 증거는 없다"고 답합니다. 대신 귀하의 대안을 더 날카롭게 만드는 근거를 하나 찾았습니다.

**A. 상대 질문에 대한 답**
1. 별도의 내부 출력 와이어가 필요하다는 직접 증거는 없습니다. 오히려 반대쪽 근거가 있습니다.
   - 원래 설계부터 w_k3pass를 그룹의 유일한 출력 와이어로 의도했습니다(`plan_ring_p5s02r_in_pre164.json:839` why).
   - 도구도 그 모양을 받아들이도록 일부러 만들어졌습니다(`stagexec.py:6306-6314`, card 156-a1-2).
   - 다만 그 검증은 plan 안에서 새로 만든 case 기준입니다. 이 점은 B에서 다룹니다.
2. 동의합니다. K3f를 빼고 J+K3만 대조하는 것이 가장 쌉니다. 고칠 점은 dst 표기입니다. 입력 파일에는 'True'로 적고, 매핑을 거친 행에서는 '#31517'이 됩니다(`prep_plan_flow_lib.py:107-118` FRM, `diag_c164_a1_1_facts.md:13`). 대조는 매핑 전 입력을 기준으로 해야 합니다.

**B. 상대 주장에 대한 피드백**
- 직접 원인에 대한 분석(`:895-901`, `:6318-6320`)은 제 분석과 같습니다. 이 부분은 동의합니다.
- 대안을 보완합니다.
  - 실제 step-4 plan에서 CQ7은 이 plan이 만드는 case가 아닙니다. 이미 채택된 기존(BASE) case #31308입니다(`facts_a1_1:13,35`).
  - 그러면 `case_pass_wire`는 plan-made 분기(`:6325-6329`)가 아니라 base 분기(`:6330-6331`)를 탑니다. 이 분기에서는 body가 uid여야 하고, dst frame은 '#31517'이어야 합니다.
  - `selftest_c156_passwire.py`에는 '#', base_case, 31308/31517이 전혀 나오지 않습니다(grep 0건). 즉 검증된 것은 plan-made 분기뿐입니다.
  - 따라서 "표기만 고치면 된다"는 주장의 실제 위험은 **base 분기 + 실제 그래프의 route census**입니다. 별도 내부 와이어 문제가 아닙니다.
- 시험 판정 기준에 하나를 더 넣자고 제안합니다. 컴파일된 op kind가 selftest처럼 `connect_term_uid register_end_case_border`로 나오는지 확인하는 것입니다.

**C. 내 입장에서 바뀐 것**
- 주원인 판단은 그대로입니다.
- 대안은 바꿉니다. 이제 "도구가 지나치게 엄격하다"가 아니라 "dst-only 모양은 맞지만, base-case 분기와 실제 그래프 route에서 검증된 적이 없다"를 가장 강한 대안으로 봅니다.

**D. 새 질문**
1. 매핑된 행에서 t_k3i의 `body`가 정수 uid 31517로 바뀌는지, 아니면 'new:CQ7.f1'으로 남는지 확인하셨나요? 후자라면 `:6331`에서 name이 None이 되어 다른 이유로 거부됩니다.

STATE {"agreed":["직접 원인: A69/A79의 src frame 때문에 그룹 와이어(:896-897)와 case_pass_wire(:6318-6320) 양쪽에서 탈락","G/H/C7 선례는 그룹 뒤에 붙는 독립 와이어라 K3에 맞지 않음","STUB FAIL은 별개 문제","첫 시험은 K3f를 뺀 J+K3 대조"],"open":["dst-only 모양이 base-case 분기(:6330-6331)와 실제 그래프 route census에서도 통과하는가"],"questions":["1. 매핑된 행에서 t_k3i의 body가 정수 uid 31517로 바뀌는가, 'new:CQ7.f1'으로 남는가?"],"experiment":"4c8d3645 복사본에서 A69 src frame만 제거한 뒤 prep_plan_flow_lib 매핑을 거쳐 J+K3를 compile_plan과 REALSIM으로 실행; op kind, 동일 프레임, route PASS 확인(오프라인)","user_needed":"","check":"","done":false}
