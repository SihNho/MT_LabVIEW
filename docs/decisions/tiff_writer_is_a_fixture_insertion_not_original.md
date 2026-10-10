---
name: tiff-writer-is-a-fixture-insertion-not-original
description: "The per-frame TIFF writer in the working copy (IMAQ Write TIFF File 2 #22700, Build Path #23020) was inserted by Claude on 2026-09-01 for fixture recording; the true original never saves TIFFs and real experiments do not need them (user, 2026-09-17) — remove it from any derived VI, never treat it as original behaviour"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 97b1695e-68c2-4985-8cac-1ca3097b3b15
  modified: 2026-09-17T00:45:02.963Z
type: decision
status: in-force
date: 2026-09-17
source: memory/tiff_writer_is_a_fixture_insertion_not_original.md
---

# The TIFF-per-frame write is ours, not the instrument's

On 2026-09-17, when I reported that "the original writes every frame as a 1.3 MB TIFF (118 MB/s), with no
panel switch", the user corrected the premise:

> *"실제 실험에서는 tiff 저장 불필요함. 아마 지금 참조하는 코드는 클로드 사본으로 픽스처 생성을 위해 tiff 저장
> 기능 추가한 vi로 보임."*

They were right, and the record confirms it: `docs/fixture-recording.md` (2026-09-01) lists `IMAQ Write TIFF
File 2` (#22700) and `Build Path` (#23020) as nodes **inserted into the user-authorised working copy**
`Min_Track N beads V6_ParallelLoop.vi` to record the 10,043-frame fixture; the true original
`Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi` was never touched.

## What follows

- `Min_Track N beads V6_ParallelLoop.vi` — the file every census, plan and D1 copy calls "MAIN" — is the
  **original plus two fixture-recording nodes**. Anything derived from it (D1 and later) **removes #22700 and
  #23020 and their wires first**; that is restoring the original, not changing it (rule 1a is untouched).
- Never build a "Save TIFF?" switch, a TIFF cap or a TIFF-deletion step into a deliverable — those were answers to
  a problem that does not exist in the instrument. Unattended 5-minute and overnight runs are fine without them.
- I had treated the writer as "unconditional original behaviour to preserve" across three plan revisions. The
  lesson is the standing one: when a node looks out of place in the original (a raw-frame dump on the hot path
  of a 90 Hz instrument), check `docs/fixture-recording.md` and the archive for our own insertions before calling
  it original.
