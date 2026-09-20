---
type: archive
status: historical
date: 2026-09-16
tags: [status-narrative, prior-art-gate, autofocus, cycle10]
---

# Narrative moved out of STATUS.md on 2026-09-16 (session 6564f349)

STATUS had reached 255 lines against a ~100-line budget. Per CLAUDE.md rule 4 the narrative moves down a layer and
nothing is deleted. The settled *decisions* went to `docs/decisions.md`; the *story* is here.

## Cycle 10's plan was SUPERSEDED — its content lives on as the master plan's Phase A

`docs/cycle10-plan.md` went to the prior-art review, which returned **8 non-`novel` verdicts**
(`archive/peer/2026-09-16-priorart-prior-art.md`, opus/high, $3.47, ANSWERED). **All eight were accepted** — every
citation was opened and held — and the plan was rewritten rather than released. Central finding: the plan cited
`docs/NAMES.md:823` for owner-chain semantics, but the fact lives at **:864-866 under the heading "Owner chain
inside a case frame"** and is scoped to `CaseStructure`, one of the main VI's **six** structure classes.
`tools/bench/which_loop_owns_motor.log` names the real blocker 18 times: *"cannot step above this structure without
the structure→home-diagram link"* — the **opposite direction** from what the reader was specified to provide.

What survived, after H4 was deleted (already run in hardware) and H2 replaced: run the recipe that already exists ·
validate owner semantics per structure class · re-walk the 41 unresolved diagrams · re-run the motor-site script ·
derive the unconditional per-frame path · the nested-frame membership delta · one scoped ASI latency tail.

## How the master plan's scope was set

*"내가 명시하기 전까지는 rig 조립 직전까지 할 수 있는 모든 플랜이 필요함."* Cycle 10's plan was preparation only;
the master plan replaced its **scope** and holds until the user announces reassembly. Six tracks: **A** finish the
map · **B** price the frame budget on the fixture · **C** the hardware window · **D** build the seven loops in a
copy · **E** acceptance reachable without beads · **F** the short list that genuinely waits.

**The reframing that changed the schedule:** "needs the rig" was one category and should have been three. **Beads in
a mounted channel** are unavailable; **motors/serial** and **the camera** are available *now*. So live acquisition
acceptance needs no beads and had been deferred for no measured reason.

**Then the user re-scoped it again**, and that is the plan today:

> *"결국에 main vi 만들어서 가동 해보기는 해야함 (리그 없는 상태에서도 가동은 가능할 듯)… bead tracking은
> 안될테니 tracking renewal은 계속 들어가겠지… 그렇다고는 할지라도 루프는 계속 돌테니 모터 가동, 카메라
> acquisition 등 정상 가동 자체는 확인 가능할듯."*

Two questions decide it: **(1) does it solve the frame problem correctly, (2) does it run normally — motor motion
and reading.** Bead tracking failing with no sample is the expected condition, not a defect. Batches go to
`G:\Data\Sihyeong-Developing\<date>-<batch>\`.

## The gate fixes of 2026-09-16, in the order they were found

**The cycle clock**, on the user's instruction: `guard_cycle` now measures the **span of unreviewed build logs**
instead of time elapsed since the last retrospective — it used to refuse the first build of any cycle starting more
than 8 h after a review, i.e. it fired hardest when the least work had been done. Both the retrospective and
prior-art pickers use `min(ctime, mtime)`, so a bulk frontmatter pass can no longer reorder them or silently open
the gate.

**The prior-art stop gate had NEVER worked.** Its pattern required the verdict slug to end the line, while
`prior_art_review.py`'s own prompt demands a file-and-line citation on every finding — so real verdicts
(`PRIOR-ART: contradicted   (A3a — NAMES.md:823 …)`) matched **nothing**. Eight unrefuted verdicts parsed as zero.
The review the user gave stopping power to was inert from the day it was built, and builds had been blocked only by
the unrelated clock bug, by accident. Fixed: a citation may follow the slug, and only the `## Answer` section is
scanned so the archived question's own menu line cannot be read as findings.

**`guard_peer` was deadlocking its own remedy.** `RUNS_RE` matches bare `bgrun.py`, so a review dispatched the way
STATUS prescribes — `py tools/bgrun.py -- py tools/prior_art_review.py …` — was refused with "dispatch a peer
first". `main()` consults a hardcoded regex, **not** `EXEMPT_RE`; it now uses `REMEDY_RE`, listing the five review
runners `guard_cycle` had always exempted. No build's gating changed.

## The prior-art review rounds on the master plan, and what they cost

| round | findings | cost | what it was worth |
|---|---|---|---|
| rev2 | 16 | $3.89 | accepted; plan corrected |
| rev3 | 18 | $4.27 | the startup-ASI blocker, the `Auto-Reset` second arm, the GPU duty-cycle correction, the camera-session question |
| rev4 | 11 | $5.64 | **paid for itself twice** — N (`Frame rate` = 25) and wire 3362 were already in our files, and the implicit-property-node question had been answered on 2026-09-14, so two codex dispatches that day were re-asks |
| rev5 | 13 | $6.57 | mostly **self-inconsistencies introduced the same afternoon**; also caught a rotor repoint that contradicted a standing user instruction |

**The lesson recorded at the time: the problem was not too little review, it was editing faster than checking.**
Round six was not run; the remaining `unread-evidence` items were read and folded in directly.

## Closed during this session

- **`docs/restructure-plan-4.6.md` §4 and §5** corrected — §4's construction method is *restructure inside a COPY*
  (banner + the probe_migrate evidence); §5's three wrong criteria fixed: bit-identical means the **first 10,018
  frames**, `Images Missed = 0` is **not sufficient** under `Buffer Number Mode = Last`, and **90 Hz / 10 ms** is
  the tested condition while 150 Hz / 6.00 ms is the stretch one.
- **`pre-rig-master-plan.md:90`** — "11.111 ms budget" → the measured 10 ms budget (motor read = 26 % of it).
- **Two `sink to find` items** in `stage2-assembly-step-e.md`: wire 9921 (→ Case #10445's selector **and**, negated,
  the autofocus enable) and wire 10187 (→ `LoopTunnel` #10177, i.e. it leaves the frame loop).

## Answers kept because they were expensive

`Limit of Program` = the **cap on auto-resets per run**; at the limit the program **stops and saves** (`Equal?`, so
on equality). The racy `min value` read → **use the current frame** (rule 1a deviation, accepted with the user's
word). Rotor read sign → `SetCommand_signed.vi`, verified in hardware 2026-09-13 (INDEX row 31) — **but** see
`docs/decisions.md`: the restructuring's rotor row keeps the existing `SetCommand.vi` call unchanged.
