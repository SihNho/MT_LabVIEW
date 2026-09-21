---
type: reference
status: current
date: 2026-09-22
tags: [secrets, api-key, handover, personal-data]
---

# API 키 보관·삭제와 사용자 교체(인수인계) 체크리스트

사용자 요청(2026-09-22): *"그것도 아카이빙 해줘. 나중에 내 개인정보들은 다 초기화하고 다른 유저로 교체할 것 같거든."*

## 1. API 키는 환경 변수에만 둔다

- 키는 채팅, 코드, 문서, `.env` 파일, git에 절대 넣지 않는다. Claude는 자격 정보를 직접 다루지 않는다.
- 사용자 터미널에서 한 번 실행(사용자 계정에 영구 저장, 새로 여는 프로그램부터 적용):

```powershell
setx TYPESAFE_API_KEY "여기에_키"
```

- 스크립트는 `os.environ["TYPESAFE_API_KEY"]`로만 읽는다. 값을 로그에 찍지 않는다(존재 여부·길이만).
- `.gitignore`에 `*.key`, `.env`가 있다(2026-09-22 추가). 키 파일을 프로젝트 폴더에 만들지 않는 것이 원칙이다.

## 2. 키 삭제

PowerShell:

```powershell
[Environment]::SetEnvironmentVariable("TYPESAFE_API_KEY", $null, "User")
```

명령 프롬프트:

```bat
reg delete "HKCU\Environment" /v TYPESAFE_API_KEY /f
```

- 이미 열린 창에는 남을 수 있으니 창을 닫는다.
- 로컬 삭제는 키를 무효화하지 않는다. **TypeSafe 콘솔에서 해당 키를 폐기(revoke)** 해야 진짜로 끝난다.
- 다른 서비스 키(있다면)도 같은 방식: `setx 이름 "값"` / 위 삭제 명령의 이름만 바꾼다.

## 3. 사용자 교체 시 지울 개인정보의 위치

이 프로젝트에 남는 개인 식별 정보는 아래에 있다(2026-09-22 조사).

| 위치 | 내용 | 조치 |
|---|---|---|
| `.git/config` | `user.name = KimLab`, `user.email = nosskrkrkr@gmail.com` (2026-09-20 `git init` 때 설정) | `git config user.name "<새 이름>"`, `git config user.email "<새 메일>"` |
| git 커밋 이력 | 2026-09-20 이후 모든 커밋의 작성자 메일 | 이력까지 지우려면 `.git` 폴더를 삭제하고 `git init`부터 다시(가장 확실). 이력을 남기려면 `git filter-repo --mailmap`로 재작성 |
| Windows 계정 이름 `KimLab` | 문서·스크립트 68개 파일에 `C:\Users\KimLab\...` 경로 | 새 계정 이름으로 일괄 치환(`tools/` 아래 `.py`/`.ps1`이 우선, 문서는 그다음). LabVIEW `user.lib\claudeDev` 경로는 계정과 무관 |
| Claude 메모리 | `C:\Users\KimLab\.claude\projects\<이 프로젝트>\memory\` | 새 사용자는 새 계정의 같은 경로에 새로 생긴다. 넘길 메모리는 파일 복사, 나머지는 삭제 |
| Claude 세션 기록 | `C:\Users\KimLab\.claude\projects\<이 프로젝트>\*.jsonl` | 대화 원문. 넘기지 않을 것이면 삭제 |
| `.claude/settings.json`(프로젝트 내) | 훅·허용 목록. 개인정보 없음 | 그대로 |
| `archive/peer/`, `archive/prose/` | 피어 대화 원문. 사용자 메일은 없고 경로만 있음 | 경로 치환만 |
| 환경 변수 | `TYPESAFE_API_KEY` 등 | §2로 삭제 + 콘솔에서 폐기 |
| **Codex(ChatGPT) CLI** | 로그인 토큰 `%USERPROFILE%\.codexuth.json`, 대화·상태 DB(`sessions\`, `thread_history_1.sqlite`, `memories_1.sqlite`, `logs_2.sqlite`, `state_5.sqlite`), `config.toml` | `codex logout`(또는 `auth.json` 삭제) → ChatGPT 계정 설정에서 연결된 기기/앱 해제 → 남은 기록이 필요 없으면 `%USERPROFILE%\.codex` 폴더 통째 삭제. 새 사용자는 `codex login` |
| **Gemini CLI (`agy`)** | OAuth 자격 증명 `%USERPROFILE%\.gemini\` 아래(oauth 파일) 또는 환경 변수 `GEMINI_API_KEY`/`GOOGLE_API_KEY`(2026-09-22 조사 시 사용자 변수에는 없음) | Google 계정 → 보안 → 서드파티 액세스에서 Gemini CLI 해제 → `%USERPROFILE%\.gemini` 삭제. 키를 쓴다면 §2 방식으로 삭제 + Google AI Studio에서 키 폐기 |
| **TypeSafe (Jev)** | 사용자 환경 변수 `TYPESAFE_API_KEY`(2026-09-22 설정, 길이 108) | §2로 삭제 + 콘솔에서 키 폐기 |
| **Claude Code** | 로그인 상태(`%USERPROFILE%\.claude`), 이 프로젝트의 메모리·세션 기록 | `/logout` 후 새 사용자가 로그인. 메모리는 위 행 참조 |
| GitHub | 연결된 적 없음(git은 로컬 전용) | 해당 없음 |

## 4. 교체 절차(권장 순서)

1. TypeSafe 등 외부 키를 콘솔에서 폐기하고 §2로 로컬 삭제.
2. `git config`의 이름·메일을 바꾸거나 `.git`을 새로 만든다.
3. `KimLab` 경로를 새 계정 이름으로 치환(먼저 `grep -rl KimLab`로 목록 확인).
4. 옛 계정의 `.claude` 메모리·세션 기록 정리.
5. `STATUS.md`의 `rig-state:`와 하드웨어 배너는 그대로 둔다(개인정보 아님, 안전 규칙).
6. 새 사용자가 첫 세션에서 `CLAUDE.md` → `STATUS.md` → 현재 계획 순으로 읽으면 이어진다.
