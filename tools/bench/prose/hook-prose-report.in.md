## 훅 업그레이드 — 완료, 검증됨

`tools/hooks/guard_bash.py`에 재료 게이트가 추가되었습니다. `tools/recipes/*.py`나 `tools/bench/*.py`를 명령 위치에서 실행하면 거부되고, 재료 세션이 붙이는 `MATERIAL=1` 접두가 있을 때만 통과합니다. 가짜 훅 입력으로 10가지 경우를 시험했고 모두 예상대로였습니다:

| 명령 | 결과 |
|---|---|
| `py tools/bench/nonexistent.py` (마커 없음) | 거부 (exit 2) |
| `MATERIAL=1 py tools/bgrun.py ... -- py -u tools/recipes/foo.py` (백그라운드) | 통과 |
| `cat tools/bench/x.log`, `grep -n def tools/recipes/foo.py` | 통과 (읽기 전용) |
| PowerShell `$env:MATERIAL='1'; py tools\bench\x.py` | 통과 |

거부와 통과가 모두 `tools/hooks/material_marker.log`에 기록되고, `audit_cycle.py`에 C6 줄이 생겨 마커 붙은 실행과 거부된 실행을 셉니다. 판단 세션이 마커를 손으로 타이핑해 우회하면 회고에서 보입니다. 시험용 기록 12건은 지운 뒤 로그를 비워 두었습니다.

한 가지 짚을 점: `MATERIAL=1`을 붙여도 타임아웃 없이 포그라운드로 실행하면 기존 규칙 2b 게이트가 여전히 막습니다. 설계대로이며, 재료 에이전트가 쓰는 백그라운드 bgrun 형식은 통과합니다.

## 문장 검수 경로 — 완료, 실제 한국어로 1회 시험

`tools/peer.ps1`에 `-Kind prose`와 `-TaskFile`이 추가되었습니다. 반박 지시문과 confirm-bait 검사를 붙이지 않고 교정 지시문만 앞에 붙이며, 결과는 `archive/prose/`에 따로 저장됩니다. `guard_peer.py`, `violations.py`, `prior_art_review.py`가 `archive/peer/`만 읽는다는 것을 확인했으므로 검수 기록이 리뷰 집계에 섞이지 않습니다.

시험 결과: `OUTCOME: ANSWERED (8s)`, codex(gpt-5.6-sol). 첫 줄 예시: "`tools/bgrun.py`는 백그라운드에서 실행되는 명령에 마감 시간을 강제로 적용하는 실행기다."

**시험 중 찾아 고친 버그 하나:** 첫 검수 결과가 전부 깨진 글자였습니다. `peer.ps1`이 codex의 UTF-8 답을 cp949로 읽고 있었습니다. 영어로만 오간 217건의 피어 교환에서는 드러나지 않았고, 한국어에서 처음 드러났습니다. `-Encoding UTF8`과 콘솔 인코딩 지정으로 고쳤고, 깨진 첫 기록은 무효로 삭제했습니다.

## 바뀐 파일
`guard_bash.py`, `audit_cycle.py`, `peer.ps1`, `.claude/agents/material.md`(bgrun 줄에 `MATERIAL=1` 필수), `.claude/agents/prose-review.md`(결과를 UTF-8 저장 파일에서 읽도록).

## 다음
STATUS의 NEXT에 있는 A1 v1 설계를 `material` 에이전트에 넘기기 전에, codex가 지적한 26개 패치의 변수 미분리(다이어그램 로드 vs 편집 모드)를 먼저 분리 실험으로 확인하는 순서를 제안합니다. 진행 여부를 알려 주세요.
</content>
