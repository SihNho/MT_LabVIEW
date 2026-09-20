---
type: reference
status: current
date: 2026-09-14
tags: [docs, plan]
---

# System inventory — understand and document BEFORE building

> Ordered by the user, 2026-09-13: *"본격적으로 메인 작업 시작하기 전에 각 instrument library 확인하는게 필수겠다 …
> 프론트 패널과 백 패널 사이의 연결관계, 변수 내용, 이런거 다 확인해서 문서화 해라. 자꾸 불안하다.
> **아니, 애초에 코드 다 뒤져봤으면 당연히 알거 아니야?** … 시작하기 전에 내용 파악후 문서화가 가장 첫 스텝인 것 같네"*
>
> **This supersedes the previous plan's ordering.** The measurements and the restructuring wait behind it.

## Why the previous approach failed, stated plainly

Every investigation so far was a **targeted just-in-time search**: find the camera config node; find the rotor
zero; find `Auto-reset zero`. Each one answers exactly one question and leaves the next just as expensive. The
result is that the user keeps being asked about things the code already contains, and neither side ever gains
confidence in the whole. The user does not trust their own memory of a VI they revised over years — they are
relying on this project to hold that knowledge, and a search that stops at the first answer never builds it.

The cost excuse is also gone. Sweeping the main VI's 626 nodes used to take **618 s** because the reporter ran
once per object; `OpReportAll_v0` returns arrays in **1.70 s**. A full inventory is now a routine call.

## The four documents to produce

| # | document | contents | why it matters |
|---|---|---|---|
| 1 | `docs/instrument-libraries.md` | every instrument: which VIs drive it, the port / protocol / baud it opens, what the main VI's startup configuration block sets | the rotor turned out to be driven by **neither ASI nor PI** — assumptions from VI names are already known to be wrong here |
| 2 | `docs/main-vi-panel-map.md` | every front-panel object: label, control/indicator, **visible or hidden**, position, and the diagram terminal it reaches | hidden and off-screen controls are exactly the ones a screenshot misses — `Auto-reset zero` is one right now |
| 3 | `docs/main-vi-state.md` | every local, global and shift register: name, **writers**, **readers** | the restructuring's whole correctness argument is "one writer per field"; that cannot be asserted without this |
| 4 | `docs/main-vi-startup.md` | the configuration block at the start of the main VI, node by node | where `Current pos rot?`, `Autoreference?`, `Set Focus` and the rotor's zero are decided |

## The authority question, settled by the user (2026-09-13)

> *"우선 main vi는 정상적으로 작동되는 코드야 … 이전 레거시 흔적들이 조금 남아있을 수 있는데 경우에 따라서는
> 프론트 패널에 남아있지만 실제로 와이어링 안되어 있거나 사용하지 않는 부분들이 있을 수 있지. 지금 프로젝트가
> 동시에 main vi 여러명이 작업하는 것도 아니고 main vi 위에 상위 vi들 끼얹어서 프로젝트 만드는 것도 아니니까
> **현재 가동되면 결국 그게 지금으로서는 최종이라는거야.**"*

Three consequences, and they simplify the work considerably:

1. **The running code is the specification.** Not older documents, not anyone's recollection, not this project's
   earlier notes. Where any of those disagree with what the VI currently does, the VI wins and the note is
   corrected.
2. **There is exactly one version, and no concurrent editors.** No merge to reason about, no higher-level VI
   wrapping it. The inventory describes one artefact at one moment, and that is enough.
3. **Unwired leftovers are EXPECTED, not alarming.** Front-panel objects that survive from earlier revisions but
   reach no wire are a normal finding. So the panel map must report **live vs orphaned** as a first-class column
   rather than treating every control as meaningful — and this is precisely what distinguishes a useful inventory
   from a list of names.

That third point also sets the standard for removing anything during the restructuring: *the user believing a
control is unused* and *no wire reaching it* are different claims. Only the second licenses removal, and the
inventory is what establishes it.

## Facts already established, to fold in rather than re-derive

- **The rotor is its own input — not ASI, not PI** (user, 2026-09-13). Its configuration is in the main VI's
  startup section. Strings seen in the file: `Rot, COM3 9600`, `Rot, COM2 115200`, `RotationVISA`.
- **`Cal Zero` / `+ Cal Zero` / `- Cal Zero` are magnet-motor presets**, not calibration or rotor (user,
  2026-09-13; ARCHITECTURE.md §3). `- Cal Zero` is believed legacy — to be *shown* unreachable, not assumed.
- **Startup cluster, seen on the panel and greyed out:** `Autoreference? 1=Y` = 0, `Current pos rot?` = 0,
  `If no: current pos z?` = 30, `Set Focus (0->50)` = 51.5.
- **Front-panel objects: 114 total**, rotor/zero-related ones at tab indices 16, 18, 40, 45, 70–76, 89, 100, 104.
  `Auto-reset zero` is index 40 and was NOT found on screen — hidden or off-view.
- **The diagram was Cleaned Up**, so grouping must come from wire topology, never from position.

## The main VI's structure, measured 2026-09-14

`report_all(MAIN, "Diagram")` — **170 diagrams in 1.3 s**, by owning structure:

| owner | count |
|---|---|
| **CaseStructure** | **76** |
| **FlatSequenceFrame** | **57** |
| ForLoop | 17 |
| Sequence | 11 |
| EventStructure | 5 |
| WhileLoop | 3 |
| *(top level)* | 1 |

Two things follow, and both shape the rest of the inventory.

**The VI is overwhelmingly case structures and flat sequence frames** — 133 of 170. That is the shape of code
where behaviour is gated by mode selectors and staged in fixed order, and it is why "which frame is live" will
matter as much as "what is wired" when the panel map's wiring column is filled in.

**`net_map` cannot do the full sweep.** Measured the same run: **12 diagrams took 312 s** — ~26 s each, so all
170 would take about **74 minutes**, and it returns no labels anyway (see below). The array-returning approach is
not a preference; it is the only viable one at this size.

## Tools that have to exist first — BUILT 2026-09-14 under other names (see "Order of work" below and docs/toolkit-capabilities.md top section)

`report_all` returns uid / class / pos / owner. That is not enough for any of the four documents — **names** are
missing. Three array-returning ops are needed, each a small variant of `OpReportAll_v0`, whose recipe is now
proven (`tools/recipes/build_opreportall_v1.py`):

| op | ladder | gives |
|---|---|---|
| `OpReportSubVI_v0` | `Traverse('SubVI')` → loop → `SubVI.VI Name` 635E401, `SubVI.VI Path` 635E403 | document 1: which instrument VI is called where |
| `OpReportPanel_v0` | `Panel.Controls[]` 6348801 → loop → `Control.Label`→`Text.Text`, `Control.Indicator` 6332007, `Visible`, `GObject.Position` | document 2, and it finally locates hidden controls |
| `OpReportVar_v0` | `Traverse('Local')` / `('Global')` → loop → the linked control's name | document 3 |

`OpReportPanel_v0` also **replaces `fp_labels`**, which currently costs 120 s and an 8-second dialog because it
runs one op call per control and walks past the end of the array to find the end.

### Two routes ruled out by measurement, so they are not retried

- **`net_map` does not return labels.** It returns `(uid, label, terminals)` and the label is plausibly the subVI
  name — `node_info` showed exactly that on a top-level diagram, `(1, 'Unknown', 'Traverse for GObjects.vi')`,
  where Style is `'Unknown'` for a subVI but the LABEL is the VI name. Probed across **12 non-empty diagrams of
  the main VI: 66 nodes, 0 with a label** (`tools/bench/probe_netmap_labels.py`). Whatever populates it on a
  top-level diagram does not on sub-diagrams.
- **`node_info` is top-level only** by construction, and the main VI's top-level diagram holds **1 node**. The
  whole program lives in the other 169.

### Status of `OpReportNodes_v0`: three failed builds, under peer review

Attempts and what each taught, all logged under `tools/bench/build_opreportnodes*.log`:

1. `wire()`'s boundary guard rejected a wire that had succeeded — the guard assumed `1 + tunnels` extra wire
   segments; LabVIEW may merge them, so the contract is now a **range**, not a formula.
2. The recipe deleted the **wrong Index Array** — it picked "the last uid in report order" and removed the
   diagram-selecting one instead of the `Nodes[]`-consuming one. **Every step still reported `ok`**; only
   ExecState disagreed. Now identified structurally, by which node sits on the `Nodes[]` wire.
3. Orphaned Index Arrays (donor leftovers with an unwired `array` input) were then found and deleted — and the VI
   is **still ExecState 0** with every intended wire present.

I do not have a confident explanation for (3), which is precisely the situation the project's rules cover, so a
peer review was dispatched to attack it rather than a fourth attempt being thrown at it. **The peer gate
(`tools/hooks/guard_peer.py`, built 2026-09-14) enforced this** — it blocked the next build until the review was
archived. That is the gate working as designed on its first real use.

The underlying problem is that **I am debugging blind**: `ExecState == 0` says "broken" and nothing else. Reading
LabVIEW's actual error list by script (`VI.Get Errors`, method 452, private) is the capability that would end
this class of failure, and it is the first question put to the peer.

## Order of work — STATE 2026-09-14 12:5x: the four documents are measured, the tools exist under other names

```
1. OpReportSubVI_v0   -> DONE as OpSubVIs_v1  (gscript.subvis; docs/main-vi-subvi-identity.md: 98 sites, 56 callees)
2. OpReportPanel_v0   -> DONE as OpPanelWiring_v0 (gscript.panel_wiring; wiring column + locals section in doc 2)
3. OpReportVar_v0     -> DONE without a cast: OpNodeTerms_v0 (gscript.node_terms) — a global's / local's terminal
                         NAME is its field / control (observed on 7 globals + 8 locals + NI's example globals) and
                         Terminal.Is Source? gives read/write; docs/main-vi-state.md: all 7 global sites are WRITES
4. startup block trace -> frame 10 = ASI Initialize (COM4), frame 12 = ASI Get Current Position; frames 5/8 write
                         the globals (docs/main-vi-startup.md)
```

The three failed `OpReportNodes_v0` builds are explained: they had called `net_map` on an OPEN target, whose
walker drops one junk Invoke per op run (spec §33) — the target was broken by the reader, not by the build
(measured `probe_builder_artifact.log`, `walk_junk_probe.log`). `VI.Get Errors` was never needed.

**Still open after this pass (recorded, not guessed):** the bound object of the 88 implicit `Value` property
nodes and any event-structure registrations — the only routes by which 9 of the 10 bare-terminal panel objects
could still be in use; `Constant.Value` (the VISA resource literal on frame 10); the rotor zero's meaning (user).

Then the measurements and the restructuring resume (STATUS work order).

## Verification standard for these documents

Structural counts are not enough. Each document states, per row, **how the fact was obtained** — a property read,
a wire trace, a user statement, or an inference — and inferences are labelled as such. Where the code and the
user's memory disagree, both are recorded; the user has already been right once (`Cal Zero`) and my byte-scan
guess wrong, and the reverse will happen too.
