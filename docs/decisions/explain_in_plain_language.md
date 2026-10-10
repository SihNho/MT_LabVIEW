---
name: explain-in-plain-language
description: "The user asked \"말이 왜이렇게 어려워\" — write in plain words, especially when asking them to decide something; jargon in a question is a question they cannot answer"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 1c79eb01-7150-4a78-9689-e6d4f34f7800
  modified: 2026-09-15T06:39:53.089Z
type: decision
status: in-force
date: 2026-09-15
source: memory/explain_in_plain_language.md
---

# Write plainly. A question the user cannot parse is not a question.

On 2026-09-15 the user stopped a status report and said: *"말이 왜이렇게 어려워"* — why is the language so hard?
They quoted three phrases back, all of which I had used while asking them to make a decision:

- "원본을 복사해 새 CPU 최상위로 삼고, 획득/추적 핫패스만 검증된 queue 코어로 교체"
- "직접 데이터플로 = 항상 '이번 프레임'의 최소값"
- "`Limit of Program`의 운영상 의미 … `# of Auto-Reset`와 비교되며"

Each of those is a compression of something I understood and they had no way to unpack. The damage is specific:
**these sentences were the decision points.** The user cannot choose between two strategies described in vocabulary
borrowed from the code, so the question stalls, and the stall looks like indecision when it is really bad writing
on my side.

## What to do instead

1. **Say the thing in ordinary words first, then name the jargon once if it is needed later.** "원본 파일을 복사해서
   그 복사본을 고친다 — 엔진만 갈아끼우는 것" before "copy the original as the new top level".
2. **Use a concrete comparison when two options differ structurally.** The car analogy (engine swap vs building a
   new car) did in one line what three sentences of architecture vocabulary failed to do.
3. **Separate what was measured from what it means.** The user needs the meaning to decide; the measurement is
   evidence, not the answer. Lead with "비드를 놓쳤는지 판단하는 기준값" rather than with the terminal name.
4. **When asking a domain question, state what I think the answer is, in plain language, and ask them to confirm or
   correct.** They hold rig knowledge I cannot derive, but they should not have to decode my phrasing to supply it.
5. This applies to the conversation, not just to documents. The existing preference for a teaching-oriented
   write-up in LEARNING.md was about docs; this is about how every reply is written.

Jargon is fine between me and the code. It is not fine in the sentence where I ask the user to decide something.
