---
name: archive-history-dont-read-it-by-default
description: "Keep full history and narrative, but move it to an archive directory that is not read by default — routine work references only the current curated docs"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 1ffa4eb9-19ac-4240-b7d7-6ef33fffb8c1
  modified: 2026-08-27T08:33:10.139Z
type: decision
status: in-force
date: 2026-08-27
source: memory/archive_history_dont_read_it_by_default.md
---

# History goes in an archive directory that you do not open by default

The user's rule, given 2026-08-27 while auditing this project's markdown set: *"전체 히스토리랑
이야기를 두는 건 좋아. 그러니 백업 디렉토리에 모아두자. 나중에 필요할 수 있으니, 그러나 평소에는
해당 디렉토리를 보지는 말고 현재 정리한 내용만 참조하여 보는걸로 해야 좋겠어. 이걸 규칙으로
잡아두면 좋겠고"* — keep the whole history and the stories, but collect them in a backup directory;
they may be needed later, yet ordinary work should consult only the current, curated documents.

So documentation splits into two tiers with different reading rules:

- **Active docs** — the small set describing what is true now and how to do the work. These are read
  on every session start and must stay short enough that a cold start is cheap.
- **Archive** — session narratives, superseded plans, concluded benchmarks, decision records whose
  decision is already reflected in an active doc. Nothing is deleted; it is moved. **Do not read the
  archive as part of normal work.** Open a specific archived file only when something in the active
  set is ambiguous or contradicted and the original reasoning is genuinely needed, and say why.

The practical consequences: when a status document starts accumulating dated entries, that is a
signal to move the narrative to the archive rather than to keep appending; and when a decision is
made, the conclusion belongs in an active doc while the argument that produced it belongs in the
archive. The point is that the cost of reading the documentation should stay flat as the project's
history grows.

The user also suspected that having many markdown files was itself causing sluggishness. The
mechanism is worth being honest about — file count alone is cheap; what costs is content pulled into
context every session — but the remedy the user asked for is the right one regardless, because it
attacks exactly the documents that get read repeatedly.
