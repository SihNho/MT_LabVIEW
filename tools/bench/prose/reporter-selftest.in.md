## tools/peer.ps1 `-Kind prose` 변경

- 대상 파일: `tools/peer.ps1` 한 곳만 수정. LabVIEW는 건드리지 않음.
- `tools/peer.ps1:32` — 사용 예시 주석. 옛 문구 "proofread, archives to archive\prose\" → 새 문구 "codex AUTHORS the report from a fact list", 인자 예시도 `-TaskFile block.md` → `-TaskFile fact-list.md`.
- `tools/peer.ps1:72-78` — `$Kind` 파라미터 주석. 옛 의도: `prose` = PROOFREADING. 새 의도: `prose` = REPORT AUTHORING, 입력은 FACT LIST이고 codex가 보고서를 작성함. 근거 인용 추가: 사용자 2026-09-16 "그냥 클로드와 코덱스는 문체가 달라". `.claude/agents/reporter.md` 참조 추가.
- `tools/peer.ps1:192-212` — 실제 프롬프트 프리앰블. 옛 첫 문장 "You are a PROOFREADER. Rewrite the text below" → 새 첫 문장 "You are the REPORT WRITER.", 마지막 구분선 `--- TEXT TO REWRITE ---` → `--- FACT LIST ---`.
- 새 프리앰블 규칙 7개: 이 실험실을 운영하는 사람을 위한 자연스러운 한국어(사실이 영어면 영어), 숫자·파일 경로·코드·인용문·기술 용어는 글자 그대로, 사실 추가 금지·누락 금지, 완충 표현·칭찬·서두 금지, 호출자의 섹션 순서와 제목 유지, 사용자에게 묻는 질문이 있으면 그 질문으로 끝내기, 보고서만 출력.
- 유지한 것: 이름 `prose` 그대로, 보관 경로 `archive\prose\`, UTF-8 처리(`Get-Content -Encoding UTF8`, `[Console]::OutputEncoding`), 기본 타임아웃 180 s, `prose`에서는 adversarial 접미사와 confirm-bait 검사 모두 OFF.
- 프리앰블 본문은 ASCII 유지. 이유는 파일 자체 주석에 있음 — 한국어 리터럴이 PowerShell 5.1 파서를 깨뜨린 적이 있음(2026-09-15, 측정됨).
- 검증: `[System.Management.Automation.PSParser]::Tokenize` 결과 `PARSE OK`, 파일 앞 3바이트는 `ef bb bf`(UTF-8 BOM) 그대로.
- 참고: `.claude/agents/prose-review.md`는 이미 삭제되었고 `.claude/agents/reporter.md`가 그 역할을 대신함.

이대로 두면 될까요?
