---
name: rig-reassembly-is-a-last-resort
description: "Reassembling the magnetic-tweezers rig costs 2+ hours of sample prep, channel assembly and incubation — so every plan must complete as much as possible WITHOUT it, and rig measurements are deferred to the very end and batched into one session"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 1c79eb01-7150-4a78-9689-e6d4f34f7800
  modified: 2026-09-15T07:52:00.432Z
type: decision
status: in-force
date: 2026-09-15
source: memory/rig_reassembly_is_a_last_resort.md
---

# A measurement that needs the rig is the last thing you plan, not the first

On 2026-09-15 the user shut down a plan that had "measure it on the live rig" near the front of it:

> *"재조립 후 측정은 정말 최후의 최후에 고민할 부분임. 단순히 조립에서 끝나는 것이 아니고 샘플 준비, 채널
> 조립 및 incubation 등 기본적으로 2 시간 넘는 준비 기간이 필요하기 때문. 따라서 현재로서는 재조립 필요없는
> 선에서 가능한 모든 것을 완비해야함."*

Reassembly is not "put the parts back". It is sample preparation, channel assembly and incubation — **over two
hours before a single frame can be taken**, and that is the floor, not the estimate. So a plan that casually says
"then we measure it live" is spending two hours of the user's bench time per iteration, often on something a
recording or a structural read could have answered.

## How this changes planning

1. **Sort work by whether it needs the rig, and finish the entire no-rig side first.** With the rig apart, these
   still work: reading the VI's structure by script (read-only), anything driven by the 10,043-frame fixture —
   which contains 13 real lost-bead frames, so even reseed behaviour is testable — component timings already
   measured, and building and compiling new VIs.
2. **When something seems to need the rig, ask what question it really answers**, and whether the fixture, a
   structural read, or a synthetic timing VI answers the same question. Most "we need to see it live" turns out to
   be "we need a number we never tried to get another way".
3. **Batch everything that genuinely needs the rig into ONE session**, so the two-hour preparation is paid once.
   Live acceptance (150 Hz, `Images Missed` = 0), real serial latency and frequency, and camera jitter all belong
   in that single batch — not scattered across cycles.
4. This tightens, and does not replace, the older rule that hardware is never touched without the user present and
   asking first (rule 1b; the ASI piezo and the motor stay off limits by default).

The same message carried a second instruction worth keeping with it: when a structural fact is missing — in that
case the VI's diagram hierarchy — **document it properly rather than measuring around it**. The user's words:
*"문서화가 충분히 되지 않은 것 같은데, 다이어그램 계층 구조 확실히 준비하도록."*
