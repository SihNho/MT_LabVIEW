---
name: create-and-delete-scratch-targets
description: "Scratch build-target VIs must be created per run and deleted afterwards, not accumulated as numbered leftovers — the user's cleanup preference"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 1ffa4eb9-19ac-4240-b7d7-6ef33fffb8c1
  modified: 2026-08-27T08:27:25.541Z
type: decision
status: in-force
date: 2026-08-27
source: memory/create_and_delete_scratch_targets.md
---

# Disposable scratch VIs get created and deleted, not piled up

VI Scripting builder runs need a fresh empty target each time, because a builder *drops* new objects
onto a diagram and running it twice on the same file stacks duplicates. The habit that grew out of
this was to keep making new numbered targets — `PARALLEL_build_test`, `test2`, … `testF` — and leave
them all on disk. On 2026-08-27 the user rejected that: *"버려도 되는 파일이면 그냥 만들고
삭제하는게 낫겠다"* — if a file is disposable, create it and delete it.

So the scratch lifecycle is **create → run → verify → delete**, inside the same operation, rather
than create-and-abandon. Only artefacts with a reason to exist survive: a build whose output is being
kept as evidence, or a file another document actually references. Everything else goes away in the
same run that made it, which keeps the working directory readable and stops a future session from
having to guess which of sixteen near-identical files matters.

The point generalises beyond LabVIEW: when a workflow inherently produces throwaway intermediates,
build the deletion into the workflow instead of deferring cleanup to a tidy-up pass that never comes.
