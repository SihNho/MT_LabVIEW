---
name: no-coined-terms-use-standard-names
description: "The user's 2026-09-26 complaint — I keep inventing project jargon (verb, leg, bed, rung, card, stage…) so they cannot follow reports without asking; use standard LabVIEW/programming words in every report, gloss any unavoidable internal term in parentheses on first use, never coin new names, and do not mass-rename working code to fix it"
metadata:
  node_type: memory
  pinned: true
  originSessionId: b607b493-a66f-4081-b122-a7a95d2c2a67
  modified: 2026-10-01T11:59:25.102Z
type: decision
status: in-force
date: 2026-10-01
source: memory/no_coined_terms_use_standard_names.md
---

# Stop inventing words; use standard names (user, 2026-09-26)

> "너가 단어를 이상한걸 자작해서 자꾸 만들어 내는 것 같아. 그러니 맥락 이해가 안되서 계속 물어보지. 그렇다고 지금 또
> 전반적인 수정을 해버리면 돌아가던 부분 마저 고장날까봐 바꾸라고도 못하겠네"

Trigger: I wrote "move_into_frame 동사" and the user had to ask whether that meant a function or a subVI, and
whether "동사" is a normal word. It is not; it is a term I coined ("scripting verb" = a Python function in
tools/gscript.py plus the op VIs it calls). Same for "leg" (one real measurement run), "bed" (the current working
VI), "rung" (an escalation step), "card" (a JSON task file), "stage" (one scripted build step). The user's remote
reading of reports depends on words they already know.

## How I apply it

- In every report to the user: standard words only. 함수 / subVI / 스크립트 / 실측 1회(구동 1회) / 작업 VI / 상승 단계 /
  작업 지시 파일(JSON) / 빌드 단계. Never "동사", "leg", "bed", "rung" unquoted.
- When a term already baked into file names, logs or code must be mentioned, gloss it in parentheses the first time
  in that report, e.g. `verb(스크립팅 함수)`.
- Never coin a new name for a new mechanism; describe it with existing LabVIEW or programming terminology.
- Do NOT mass-rename code, hooks, schemas or logs to purge old coinages: the user explicitly fears breaking what runs.
  Record the existing internal terms once in `docs/GLOSSARY.md` and leave the code alone.
- Never name a piece of work by its internal card/task id alone ("B5", "G1", "C2", "PD238"). The user asked on
  2026-09-29 "B5라고 하면 모르지" when I offered to "rerun B5". Say what the work IS (e.g. "문서 간 모순 찾기 과제를
  울트라코드로 1회 돌려 비용을 재는 시험"); an id may follow in parentheses at most.
- "row / 행" for a build-plan entry is also mine: on 2026-10-01 the user asked whether "행" meant lines of a .md file.
  Say "편집 동작" (one LabVIEW edit operation in the plan JSON: create a node, wire, add a register) instead.
- Related standing rule: explain-in-plain-language (2026-09) — jargon in a question is a question the user cannot answer.
