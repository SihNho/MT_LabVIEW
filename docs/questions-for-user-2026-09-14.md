---
type: reference
status: current
date: 2026-09-15
tags: [docs, open-question]
---

# 사용자 결정이 필요한 항목 — 2026-09-14 자율 루프 결과

오늘(무인 루프) 측정으로 닫힌 것은 STATUS.md와 archive/benchmarks/INDEX.md 22–30행에 있습니다. 아래는 **측정으로는 닫히지
않고 사용자만 답할 수 있는 것**입니다. 각 항목에 근거와 "무엇을 알려주면 되는지"를 적었습니다.
**18:2x 갱신:** 2번(`Rot Speed`)과 5번(GUI 1회)은 저녁에 측정으로 해결되어 취소했습니다 — 남은 질문은 **1번(글로벌 읽는 곳),
3번(로터 영점·부호), 4번**뿐입니다. 프레임 루프의 시프트 레지스터 14개와 암시적 `Value` 노드 88개는 모두 측정으로 이름이
붙었습니다(docs/frame-loop-wire-graph.md, docs/main-vi-panel-map.md).

## 1. `Global motor pos.vi`를 누가 읽나요? (docs/main-vi-state.md)

측정: 메인 VI 안의 접근 7곳(Trans 5/19/83, Rot 8/19/83, Focus 19)이 **전부 쓰기(WRITE)** 입니다. 모터 루프 서브VI
(`Motor control v5_No Recording.vi`, 18 다이어그램)에는 글로벌 노드가 하나도 없고, 지난주 바이트 스캔에서도 이 계층에
다른 접근자가 없었습니다. 즉 이 계층 안에서는 **쓰기만 있고 읽는 곳이 없습니다.**
- 질문: 이 글로벌을 읽는 **다른 top-level VI**가 함께 돌아가나요(예: 별도 모니터/기록 VI)? 아니면 예전 구조의 잔재인가요?
- 재구성에 미치는 영향: 읽는 곳이 없으면 "한 명의 writer" 규칙은 새 loop 설계에서 그냥 지키면 되고, 외부 VI가 읽는다면
  그 VI의 타이밍 요구를 알아야 합니다.

## 2. `Rot \nSpeed` 컨트롤(#73)은 사용 중인가요? (docs/main-vi-panel-map.md, 마지막 절)

측정: 패널 객체 114개 중 터미널이 미배선인 10개를 찾았고, 그중 9개는 **컨트롤 참조(ControlReferenceConstant, 21개)** 를
통해 서브VI(`Motor control v5`, `ASI_adjust focus-subvi`, `check N bead pos v3-kimlab`, `save trace`)가 사용함을
확인했습니다. **`Rot \nSpeed`만 터미널·로컬·참조 어디에도 없습니다.** 남은 경로는 암시적 `Value` 프로퍼티 노드(88개)뿐이었는데,
**14:5x 해결됨 — 질문 취소:** 새 리더(`OpNodeLabels_v0`, `Node.Label` 헤더 읽기)로 암시적 `Value` 노드 88개 전부의 대상을
측정했고, `Rot \nSpeed`는 다이어그램 32·111(둘 다 `Rot Step (deg)` 읽기와 Autonics `SetCommand.vi` 호출이 있는 시퀀스 프레임)
에서 **2회 읽힙니다** — 회전 명령마다 로터로 보내는 속도값입니다. legacy 아님. 패널 객체 114개 중 미귀속 객체는 이제 없습니다
(docs/main-vi-panel-map.md 마지막 절).

## 3. 로터 영점과 부호 (docs/rotor-sign-diagnosis.md, docs/instrument-libraries.md) — **18:3x 사용자 결정: 읽기 부호를 수정한다.**

⚠️ **OPEN (user) — 아직 해소되지 않음 (2026-09-16).** 아래 결정(새 VI에서 `SetCommand_signed.vi` 사용)과
`docs/pre-rig-master-plan.md` 1.4 행(*"the schedule's rotor row calls `SetCommand.vi` exactly as the existing
`Send to Rot` path does … The signed variant stays a separate, hardware-verified artefact, not something this
phase adopts"*)이 **동시에 참일 수 없습니다.** `archive/ingest/2026-09-16-ingest-2026-09-16.md` PAIR 4(103–105행).
어느 쪽이 맞는지는 리그 지식이라 **사용자만 결정할 수 있어** 문서 쪽에서 고치지 않았습니다.

사용자: "로터 영점은 읽기 부호 수정 가능하면 하드웨어 셋업 그대로 따라갈 수 있을 것 같아. 읽기부호 수정하도록 하자." → 영점은
컨트롤러 좌표(baseline 0)를 그대로 쓰고, `SetCommand.vi`의 unsigned 파싱을 signed로 고친 **사본**(`claudeDev\SetCommand_signed.vi`)을
새 VI에서만 사용. 원본 드라이버·원본 메인 VI는 그대로. 하드웨어 수치 검증(음의 각도 명령→읽기) 전에 다시 확인 요청.
**19:5x 진행:** `SetCommand_signed.vi` 완성, 하드웨어 없이 주입 테스트 16/16 통과(양수는 원본과 동일, 음수는 부호 복원). 측정된 사실:
Get Position = Ring 2, 0.72°/펄스(500 펄스/회전), `Baseline Startpoint` 단위는 회전수(200 = 72000°). ~~남은 것: 실제 로터로
음의 각도 명령 후 읽기 확인(모터가 움직임 → 승인 필요)~~ → **2026-09-13 20:22/20:28 하드웨어 검증 통과** (INDEX 31행,
이 문서 아래 "20:22 하드웨어 검증 통과" 절): `PIC -10` → 수정본 −7.2° / 원본 +3 092 376 445.92°, 눈에 보이는 −3회전
`PAB 0` 테스트도 사용자 입회 하에 통과. **이 줄은 같은 날 저녁에 이미 무효가 되었는데 그대로 남아 있었고, 2026-09-16
사이클 10 계획이 이 줄을 읽고 "아직 안 됐다"고 판단해 이미 통과한 시험을 다시 하려 했음** (prior-art 리뷰가 잡아냄).
남은 것은 새 VI의 로터 호출을 사본으로 교체하는 것뿐.
또 하나 답변: `Global motor pos.vi`는 **랩 자체 VI Global**(`zz_LabView VI\four-fold tracking\`), instr.lib 아님.

측정: `Baseline Startpoint`는 SetCommand.vi 커넥터에 없어 드라이버 기본값 200.0이 항상 쓰입니다. 읽기 경로는 부호 없는
파싱(`0uL` 기본)이라 음수 위치가 깨집니다(사용자 가설과 일치, 컨트롤러는 `PAB 10, -1`처럼 음수를 받습니다).
- 질문: (a) 로터 영점의 물리적 의미(어느 방향이 0, 어떤 기준), (b) 읽기 파싱을 부호 있는 정수로 고치는 것을 **재구성 안에서**
  할지(원본은 건드리지 않음) — 이건 "연산 변경"에 해당하므로 사용자 승인 없이는 하지 않았습니다.

## 4. 표시(디스플레이) 정책 (archive/bench-2026-09-14-display-path/REPORT.md)

측정: 현재 표시 경로는 프레임당 CPU 2.7 ms + **패널이 보일 때 그리기 ≈6.5 ms**; NI Image Display 컨트롤로 바꾸면 CPU
1.0 ms + 그리기 ≈6.9 ms. 150 Hz 예산(6 ms)에서 어느 쪽도 매 프레임 표시는 불가능 → 표시 루프는 별도·간축(10–20 Hz).
- 질문: 실험 중 라이브 이미지를 **몇 Hz**로 보면 충분한가요? (재구성 계획은 10–20 Hz를 가정)

## 5. 도구 하나를 위해 GUI 클릭 한 번이 필요합니다 (docs/toolkit-capabilities.md "The one missing seed")

시프트 레지스터(프레임 간 상태) 정확 판독, ForLoop 병렬 인스턴스 읽기, 상수 값 읽기 등은 모두 "원하는 클래스로 캐스트"가
필요하고, 그 캐스트 상수의 클래스를 스크립트로 바꾸는 API(`ClassSpecifierConstant.Set Type`)는 있지만 **첫 번째 typed 참조는
사람이 한 번 준비한 도너**가 있어야 합니다(상수 우클릭 → Select VI Server Class → ClassSpecifierConstant, 1회).
- ~~질문: 사용자가 계신 세션에서 이 한 번의 GUI 편집을 허용해 주실지~~ **15:1x 해결됨 — 질문 취소.** GUI 없이 풀렸습니다:
  `To More Specific Class`의 `target class` 입력은 클래스 상수뿐 아니라 **해당 타입의 아무 배선**이나 받습니다(NI 문서, codex 확인).
  NI가 배포한 예제(`examples\…\VI Scripting with Structures - For/While Loop.vi`)의 프로퍼티 노드 `reference` 입력에
  `Terminal.Create Control`을 걸면 그 클래스의 refnum 컨트롤이 생기고, 이를 `copy_into`로 op에 옮겨 캐스트의 씨앗으로 씁니다.
  결과: `OpLoopCast_v0`/`OpWhileCast_v0`가 메인 VI의 For 루프 17개·While 루프 3개를 타입 있는 참조로 읽고, 프레임 루프의
  시프트 레지스터 14개를 UID로 얻었습니다(INDEX 28행). 다음 단계(레지스터별 배선 판독)는 진행 중.

## 참고 — 오늘 만든 것

`gscript.subvis / panel_wiring / node_terms / tunnels / connect_ctl` (모두 기능 검증), 문서 `main-vi-subvi-identity.md`,
`frame-loop-wire-graph.md`, `g9-core-budget.md`, 패널 맵의 배선·로컬·참조 절, INDEX 22–25행, LEARNING.md §12.
**20:22 하드웨어 검증 통과:** 실제 로터(PMC-2HS)에서 `CLL X`로 카운터 0 → `PIC -10`(−7.2°) → 수정본 −7.2° / 원본 +3 092 376 445.92° →
`PIC +10`으로 0 복귀. **주의: 컨트롤러 카운터가 지금 0입니다**(이전엔 100 000펄스 = +200회전 baseline). 원본 메인 VI(Baseline 200)를
다시 돌리면 첫 절대 이동이 200회전이 되므로, 원본을 또 써야 하면 `PIC 100000`으로 되돌린 뒤 쓰거나 새 VI만 쓰세요.

## 4. 표시 정책 — **20:3x 사용자 결정**
"라이브 이미지는 10Hz도 충분히 좋은데, 나중에 컨트롤로 변경할 수 있으면 좋겠음. 다만, 라이브 이미징 때문에 한 프레임이라도 측정상
문제가 생긴다면 랩뷰가 아닌 다른 프로그램 통한 디스플레이로 보이는 것도 진지하게 생각중." → 표시 루프 기본 10 Hz, **런타임
컨트롤로 조절**; 표시가 측정 프레임을 단 하나라도 잃게 하면 외부 표시 프로그램으로 대체(설계 원칙: 표시는 획득·추적에 절대 비용을
전가하지 않음 — 복사-온-디맨드 풀, Last 모드).

## 순서 (20:3x 사용자): 재구성(stage 2~) 먼저 → 나머지 → [옵션, 급하지 않음] 카메라 설정 패널(프레임레이트·노출 등 NI MAX 값)을
VI configuration 단계에서 열 수 있게.

## (추가, 2026-09-15 새벽) 리시드 Case #5540의 `min value` 읽기 — 원본은 경쟁 조건(race)입니다

원본 프레임 루프에서 비드 유실 판정은 `Less?`(#10950)가 `min value` **인디케이터**를 프로퍼티 노드(#17289)로 읽어
비교합니다. 그 인디케이터는 같은 반복 안에서 `Array Max & Min`(#10969, 커널의 `pos in cal image out`)이 씁니다 —
쓰기(단자)와 읽기(프로퍼티 노드) 사이에 와이어가 없어 **어느 쪽이 먼저인지 데이터플로가 정하지 않습니다**. 즉 원본의
판정은 "이번 프레임의 최소값"일 수도, "직전 프레임의 최소값"일 수도 있는 구조입니다.

이번 픽스처(10,043프레임, 유실 13프레임)에서는 "이번 프레임의 `pos out` 최소값 < y"로 읽는 규칙이 .tra를 완전히
재현했습니다(09-07 드라이버, 편차 0.00000). 새 VI는 그 **직접 데이터플로**(결정적)로 만들고 픽스처에서 비트 동일을
확인합니다. 규칙 1a("연산 방법을 바꾸지 말 것") 관점에서 여쭙니다:

1. 이 판정을 직접 데이터플로로 고정하는 것(= 항상 "이번 프레임" 기준)으로 확정해도 될까요? 원본과 수치가 달라질 수
   있는 경우는 프로퍼티 읽기가 "직전 프레임" 값을 잡는 타이밍뿐이며, 그것은 원본에서도 재현 불가능한 우연입니다.
2. ~~`Less?`의 `y`(와이어 10850)와 주기적 auto-reset 항의 실제 값/의도~~ **→ 2026-09-15 측정으로 해결**
   (`docs/stage2-assembly-step-e.md` 표): `Less?.y` = 상수 **I32 0** 이므로 분실 판정은 `min(pos in cal image out) < 0`,
   그리고 나머지 세 입력은 상수가 아니라 **프런트패널 컨트롤** 이었습니다 — `And.y` ← `Auto-Reset`,
   `Or.y` ← `Reset Tracking`, `Equal?.y` ← `Limit of Program`. 따라서 `Reseed.vi`는 이 세 컨트롤 값을 **입력으로** 받습니다.

   남은 질문(운용 의미): `Limit of Program`은 `# of Auto-Reset`과 비교되어 "auto-reset 횟수가 이 한계에 도달하면 프로그램
   종료"로 읽힙니다(GLOSSARY의 VI 내부 주석 "~27..."). 새 VI에서도 **같은 의미로 동작하면 되는지**, 아니면 병렬 구조에서
   달리 다루길 원하시는지 알려주세요. 이번 기록에서는 auto-reset이 한 번도 발동하지 않아 픽스처로는 검증할 수 없습니다.
