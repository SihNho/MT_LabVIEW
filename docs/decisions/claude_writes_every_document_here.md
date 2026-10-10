---
name: claude-writes-every-document-here
description: "Every document in this project is written by Claude (the LLM-wiki model), so \"hand-written drift\" is never the right frame — the thing that drifts is my own consistency, and the remedy is mechanical checks on my writing plus changing the document format freely when it serves model efficiency"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 1c79eb01-7150-4a78-9689-e6d4f34f7800
  modified: 2026-09-15T10:50:20.337Z
type: decision
status: in-force
date: 2026-09-15
source: memory/claude_writes_every_document_here.md
---

# I write all of these documents. "Manual" is never the problem — I am.

On 2026-09-15 I argued against putting relations in document frontmatter because "hand-written links drift". The
user stopped that immediately:

> *"지금까지 기본적으로 llm wiki 방식을 따라서 클로드가 모든 것을 작성해왔음. 갑자기 손으로 쓴다는 표현이 왜
> 나오는지는 모르겠음."*

They are right, and the framing mattered. `STATUS.md`, `docs/`, `CLAUDE.md`, the archive, every peer annotation —
I wrote all of it. There is no separate author whose discipline can be doubted. So:

- **Stop treating "manual" as a risk category.** The real risk is that *my own* writing is inconsistent, and today
  proved it is: `GLOSSARY.md` had the wrong meaning for `Limit of Program`, `STATUS.md` carried a work order the
  user had superseded a day earlier, and one file's summary line contradicted its own section 44 lines above.
- **The remedy is a mechanical check on what I write**, not a decision to avoid structure because "it might not be
  maintained". If frontmatter should carry `supersedes:` / `refutes:` / `measured_in:`, then an audit verifies the
  referenced paths exist, and the discipline is enforced the same way every other rule in this project is.

## The document format is mine to change, and the user wants it changed

The same message gave an unusually wide mandate:

> *"평면 색인 방법은 아주 값비싸며 컨텍스트가 너무 길어 효율이 낮아 보임. 현행 문서의 포맷을 전부 개선하고
> 쳐서라도 바꾸는게 좋아보임."*

So: a long listing that must be loaded whole is the wrong shape, and **reformatting every existing document is an
acceptable cost** if the result is that a model can find a fact without loading everything. Do not preserve the
current prose-with-frontmatter layout out of conservatism. Facts should be marked where they are stated
(`MEASURED`, `DECIDED`, `ANSWERED`, `FAILED`, `verdict:`), so they can be extracted rather than inferred, and
relations should be declared where a machine can read them.

## And the decision is made on numbers, not on argument

The third instruction in the same message: *"실제 테스트 돌려서 숫자 확인 필요."* Build the test set from
failures that actually happened, score the current setup, then change it and score again. The question is never
"is this a nicer structure" but **"does the model catch more, per dollar"**.
