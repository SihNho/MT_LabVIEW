---
name: stay-responsive-during-long-work
description: "Answer the user's mid-turn questions immediately instead of finishing the tool chain first; keep long work backgrounded so the conversation is never blocked"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 1ffa4eb9-19ac-4240-b7d7-6ef33fffb8c1
  modified: 2026-08-28T09:31:32.100Z
type: decision
status: in-force
date: 2026-08-28
source: memory/stay_responsive_during_long_work.md
---

# Stop and answer when the user speaks, even mid-task

**Recurrence, 2026-09-04 (third time):** two mid-turn messages were met with tool calls (a
memory save, an agent dispatch, a CLI check) and a one-line progress note instead of an answer,
and the following direct question got its yes/no buried under a long explanation. The user:
*"대답을 왜 안해"* then *"전체 세션을 돌더라도 항상 응답 즉각적으로 할 수 있게 규칙 잡지 않았었나?"*.
Sharpened rule: **the first line of the very next reply is the answer**; tool calls come after
it, and a progress line ("지금 ~ 확인 중") does not count as answering. A yes/no question gets
its yes/no in the first sentence. Written into CLAUDE.md rule 2b again in that form.

**Recurrence, 2026-08-28:** after a context compaction the behaviour faded and the user had to
interrupt and repeat the rule ("계속 해서 내가 대화 하면 들을 수 있도록 준비해. 컨텍스트 정리하고
다시 까먹은 것 같아. 규율에 적어두자"). It is now codified in the project's `CLAUDE.md` as rule 2b
so it survives compaction; this memory stays pinned as the cross-project copy. Treat any
post-compaction session start as a moment to actively re-arm this habit.

The user's complaint, 2026-08-27: *"추가 세션을 잡던지 해서 코드 진행과는 별개로 현행 프로세스가
끝나지 않았더라도 내 질문이나 코멘트를 들을 준비가 되어 있으면 좋겠어. 전에 보면 질문을 해도
일한다고 멈추지를 않더라"* — they want their questions and comments heard even while a process is
still running, because previously a question would go unanswered while work continued.

Messages sent during a running turn do arrive. The failure was not missing them but **deferring
them**: continuing a long chain of tool calls and only replying once the work finished. So when a
mid-turn message appears, treat it as an interrupt — answer it in the very next reply, before
continuing, and if the running work should stop or change direction because of what they said, stop
it.

Two habits make this possible rather than merely intended:

- **Background anything slow.** A command that may block for minutes belongs in a background task
  from the start, not in the foreground where it holds the turn hostage. The conversation stays free
  and the result arrives as a notification.
- **Prefer short, checkable steps to long uninterruptible chains.** Batching a dozen dependent calls
  into one unbroken run maximises the window in which the user is talking to a wall.

Note that spawning a separate agent does not by itself make the main conversation more responsive —
a subagent starts cold and re-derives context. The lever that actually works is backgrounding the
slow work and keeping the foreground turn short enough to yield.
