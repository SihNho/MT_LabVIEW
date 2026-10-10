토큰 효율 - 모델·세션 구성·규칙, 그리고 10월 16일 구독 결정 (2026-10-10)

## 사용자 질문 (원문 요지)
1. 능률(채택 속도·품질)은 해치지 않으면서 토큰은 최대한 줄이는 방향: 모델(Sonnet 5.5가 괜찮다는 결과 포함), 세션 구성, 규칙.
2. Claude Max 20x 플랜인데도 주간 사용량이 부족하다. 10월 16일 이후 구독을 유지/변경할지, GPT(Codex)로 옮길지도 고려 중.

## 측정 사실 (채팅 세션이 2026-10-10에 잼; 원문 기록 경로 표시)
- 사이클 164 (P5 4단계, 156분, 회차 3, 채택 1): 세션 21개, 턴 765, 비용 $58.4 (list 가격 환산).
  - 모델별: Opus 5.5 1M 문맥(재료) $38.5 · Sonnet 5.5(배정) $14.0 · Opus 5.5(판단·넘김 판단) $5.9.
  - 토큰: 캐시 읽기 107M, 캐시 쓰기 3.95M, 출력 663k(그중 thinking 132k). 비용 비중 추정(가격 배율 가정 입력1/쓰기2/읽기0.1/출력5): 문맥 읽기·쓰기 ~85%, 출력 ~15%, thinking ~3%.
  - 원문: tools/bench/cycle_164*.log 의 마지막 JSON 줄(modelUsage), 세션 기록 ~/.claude/projects/<proj>/<session_id>.jsonl 과 subagents/.
- 세션 시작 고정 문맥 (러너 세션에서 `claude -p "/context"`로 잼): 시작 직후 86.4k 토큰.
  - 메모리 파일 42.7k (CLAUDE.md 83,338자 + MEMORY.md 18,138자) · 시스템 도구 정의 28.4k · 시스템 프롬프트 8.8k · 에이전트 목록 3.2k · 스킬 2.6k · MCP(지연 로드) 0.6k.
  - 재료 세션은 첫 턴부터 74k, 배정/판단 세션 90k. 이 고정분 × 765턴 ≈ 60M = 읽기 107M의 절반 이상.
- 세션별 (재료 세션 12개): 턴 22~73, 평균 문맥 10.6만~20.8만, 최대 28.5만. 배정 세션(Sonnet) 턴 28~64, 평균 12.7만~13.5만.
- 가정 계산(턴 기록 재현, 대략): 자동 압축 200k → 읽기 −13.5M(13%), 150k → −42M(40%, 품질 위험), 도구 결과 1만 자 상한 → −4.8M(4.5%).
- 비용 추이(러너만, list 환산): 10-07 $116(3사이클) · 10-08 $208(4) · 10-09 $339(7) · 10-10 $287(6). 채택당 비용: 사이클 122–143 ~$135, 144–149 ~$65, 150–161 ~$84, 162–163 ~$28 (stuck 토론 뒤).
- 사용량 (2026-10-10 16:3x KST): 주간 전체 모델 77% (리셋 10-12 07:00 KST), Fable 주간 1%, 5시간 창 16%. 추가 사용량 꺼짐.
- 현재 모델 표 (CLAUDE.md §3 'MODEL LADDERS', tools/cycle_runner.py): 판단 Opus 5.5 high · 배정 Sonnet 5.5 high · 재료 Opus 5.5 high(1M 문맥 변형) → 단계 상승 Opus max → Fable low · 로그 읽기 Opus low · 회고 Opus high · 선행사례 Opus medium · 사실/글 Opus medium thin.
- 모델 벤치 원문: 배정 tools/bench/assignbench/report_cloud.md (Sonnet 5.5 high 0.74 정답률 $0.20 vs Opus high 0.62 $0.35), 재료 tools/bench/matbench/report_v1.md (Opus 5.5 low/medium/high/max만 비교, Sonnet은 재료 역할로 측정된 적 없음).
- 이미 있는 구조: 카드마다 새 세션(= 짧은 지점에서 재시작), 판단/재료 분리, 도구 결과는 로그 파일로 남기고 log-reader가 요약.
- Claude Code 사실(공식 문서, 채팅이 확인): /rewind 는 대화창 전용, `claude -p`에서 특정 메시지로 되돌아가는 옵션 없음. 쓸 수 있는 손잡이: CLAUDE_CODE_AUTO_COMPACT_WINDOW / autoCompactWindow, --disallowedTools(도구 정의 제거), bashOutputMaxChars, --bare(CLAUDE.md·훅·메모리 생략 — 훅이 필수라 러너에는 부적합). API의 context editing(clear_tool_uses)은 Claude Code 설정으로 노출 안 됨.

## 토론할 것
A. 모델 배치: 재료 세션을 Sonnet 5.5로 일부/전부 옮겨도 되는가? 1M 문맥 변형이 필요한가? 판단은? 무엇을 먼저 벤치로 재야 하는가(기존 matbench 재생 방식).
B. 세션 구성: 고정 문맥(CLAUDE.md 42.7k, 도구 28.4k) 줄이는 방법 — CLAUDE.md를 규칙만 남기고 이력·인용문을 docs로, 러너 세션 MEMORY 끄기, 역할별 도구 제한, 재료 카드 쪼개기, 자동 압축 기준.
C. 규칙: 토큰을 많이 쓰는 규칙(회고 주기, 선행사례 리뷰, 동료 리뷰, 게이트 정리 카드 등) 중 효과 대비 비싼 것.
D. 구독: Max 20x 유지 / 다른 조합 / GPT(Codex)로 일부 또는 전부 이전. 이 프로젝트는 훅·에이전트 정의·claude -p 러너가 Claude Code에 묶여 있다는 사실을 고려할 것. 요금제·한도 숫자는 추측하지 말고 check로 확인할 것.

## 규칙
- 요약(이 문서)을 믿지 말고 필요하면 원문 파일을 열어 볼 것 (file:line 인용).
- 결론 형식: 각 항목 '계속 / 줄이거나 바꿈 / 판별 실험(무엇을 어떻게 재는지)', 예상 절감(토큰 또는 %)과 능률 위험을 함께.
- 사용자만 답할 수 있는 것(예: 현재 ChatGPT 요금제, 예산 상한)은 user_needed 로.
