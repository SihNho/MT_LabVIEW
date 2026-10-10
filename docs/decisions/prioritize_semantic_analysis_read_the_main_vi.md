---
name: prioritize-semantic-analysis-read-the-main-vi
description: "Map and DOCUMENT the whole system — instrument libraries, front-panel↔diagram wiring, every variable — before any main work; targeted just-in-time searching is what the user rejected"
metadata:
  node_type: memory
  pinned: false
  originSessionId: 7b982769-ee4e-45be-8846-85edbec23e37
  modified: 2026-09-13T14:59:02.612Z
type: decision
status: in-force
date: 2026-09-13
source: memory/prioritize_semantic_analysis_read_the_main_vi.md
---

# Understand and document the whole system first — meaning outranks construction

The user's redirection, 2026-08-30, in two steps. First: *"이제는 룰에 메인 vi도 경우에 따라 같이
살펴야겠어. 이제 코드 구현 자체는 거의 문제가 없는 것 같으니 의미 분석에 힘을 더 써야겠네."* Then,
more decisively: *"이제는 다시 원점으로 돌아가서 원본 메인 vi 및 subvi 연결관계, 프로세스 흐름을
디테일하게 파악하고 구조화하며 의미를 이해해야겠어. 그래야 진행 방향을 더 확실히 결정할 수 있겠다."*

## Re-issued far more sharply on 2026-09-13, after it had quietly lapsed

Asked where a specific rotor control lived, I had to go and search for it — and the user's reply named the real
problem:

> "나도 기억이 정확하지 않으니까 프론트 패널과 백 패널 사이의 연결관계, 변수 내용, 이런거 다 확인해서 문서화 해라.
> 자꾸 불안하다. **아니, 애초에 코드 다 뒤져봤으면 당연히 알거 아니야?**"
> "내 생각에 아무리봐도 본격적으로 메인 작업 시작하기 전에 각 instrument library 확인하는게 필수겠다."
> "시작하기 전에 내용 파악후 문서화가 가장 첫 스텝인 것 같네"

The criticism is precise and correct. What I had been doing was **targeted just-in-time searching** — hunt the
camera config node, then hunt the rotor zero, each time from scratch. Every hunt answers one question and leaves
the next one just as expensive, so the user keeps being asked things the code already knows, and neither of us
ever gains confidence in the whole. **The user does not trust their own memory of the VI and is relying on me to
hold that knowledge; a search that ends when one answer is found does not build it.**

## What this requires, concretely

Before main construction work, produce and maintain written maps of:

1. **Every instrument library** — which VIs drive which device, the port/protocol/baud each one opens, and what
   the configuration block at the start of the main VI sets. Verified against the code, not assumed from names:
   on this rig the rotor is driven by *neither* the ASI nor the PI library but a separate input of its own, and
   `Cal Zero` turned out to be a magnet-motor preset rather than any kind of calibration zero.
2. **Front panel ↔ block diagram** — for every front-panel object: label, control vs indicator, visible or
   hidden, and which diagram terminal it reaches. Hidden and off-screen controls are exactly the ones that get
   missed by looking at a screenshot.
3. **Every variable** — locals, globals, shift registers: name, who writes it, who reads it.

Read nested structures properly: a flat dump of front-panel strings hides cluster nesting, which once made
calibration-cluster *fields* look like stray controls and nearly designed a live parameter out of the tracker.
Whenever a name "isn't there", check whether it is a field of something that is.

## Why this is now cheap, and was not before

The excuse for searching narrowly used to be real: the object reporter ran once per object and took 618 s to
sweep the main VI's 626 nodes. `OpReportAll_v0` (2026-09-13) returns arrays in **1.70 s** — 380× — so a full
inventory is now a routine call. There is no longer any cost argument for not having the map.

**Treat a request to build, arriving before that documentation exists, as premature** — and do not wait to be
asked for the map again.
