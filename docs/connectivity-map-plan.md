---
type: plan
status: current
date: 2026-09-23
kind: tooling
tags: [jev, connectivity, reader, wiki, graph, pre-runner]
---

# Connectivity map first, Jev per item, LLM sums up — the user's re-plan of 2026-09-23

**Decided by the user in the interactive chat 2026-09-23 03:2x–06:0x, ingested here before any build ("ingest 먼저 해.
어떤 프로세스 할건지 ingest해서 정하고 그 다음 그대로 진행해줘. 나중에 괜히 빼먹지 말고").** The runner stays STOPPED
(STATUS line 7) until every step below is BUILT AND TESTED; then it resumes on `docs/cycle27-plan.md`'s M3a-4 → M4.
`docs/cycle27-plan.md` stays the delivery plan; this document is the tooling plan that precedes it and its Pre-decided
numbers continue that list (134–).

## Why (measured, not argued)

- Cycle 65 today: 80 min, $48.08. Jev: 397 calls, 230 s total (0.56 s/call) — under 5 %. Reviews 20 min, retrospective +
  ingest 7.5 min, LabVIEW diagnostics 7 min, **LLM reading/writing ~45 min**. The bottleneck is the LLM deciding from
  partial, stale, prose evidence — not Jev, not LabVIEW.
- The seven Jev insertions of 2026-09-22 are all ADVISORY lines; nothing left the LLM path, so nothing got faster
  (user: *"Jev가 아무 결정도 대신하지 않기 때문"* is the diagnosis they accepted).
- A whole-VI read was never built: `node_terms` = 0.8 s × 635 nodes ≈ 508 s, the census `tools/bench/main_vi_nodeterms.json`
  is from 2026-09-14 and stale (156 empty wired terminals). **Measured today** (`tools/bench/diag_allwires_probe.log`):
  `Traverse for GObjects` class `Wire` → 1,920 rows in 1.67 s; class `Terminal` → 5,811 rows in 5.28 s, ONE round trip.
- The user cannot follow the op VIs; hand-drawing an op is never the fallback (tool-building is Claude's job).

## Division of labour (user, verbatim intent)

| layer | who | input | output |
|---|---|---|---|
| intent | LLM (or user) | requirements, subVI wiki summaries | "this subVI's result → that subVI's input, in this loop, by this mechanism" |
| facts | Python | reader tables, wiki, current map | graph, path-finding, diff vs original, **exhaustive** legal candidate pairs (no ranking, no judgement) |
| per-item decisions | **Jev** | one candidate + one wiki line | subVI-chain next step (choice), terminal pair yes/no + p, op choice, rule-1a risk yes/no |
| execute + confirm | Python + LabVIEW | decided rows | wiring → re-read map → graph confirms reachability |
| sum up | LLM | finished table, `unknown` rows, risk rows | next intent, report |

Rules: Jev questions are one item + one wiki line, yes/no or ≤3-way exclusive; ask per pair, code takes the best;
dangerous-direction answers (rule 1a risk, ≥2 "yes" candidates) get one LLM look, safe ones act. Every menu is measured on
a labelled set before it acts. **Record keys are node UID + terminal name; wire UIDs change on delete/create and are
transient** (measured: `0 → 176`, `0 → 1231`). Newly created objects record their birth UID.

## Steps — each leaves a file, each has a pass criterion (rule "split and save intermediates")

| # | step | saved artefact | pass criterion |
|---|---|---|---|
| 1 | **Whole-VI terminal reader op** `OpAllTerms_v0.vi` (or `OpAllWires_v0`): one call → per terminal: term_uid, term_name, is_source, wire_uid, owner_uid, owner_class | ✅ **DELIVERED 2026-09-23** — `user.lib\claudeDev\OpAllTerms_v0.vi` md5 `484853aa…`, 14,600 B; `tools/allterms.py` (`read_terms` + `all_wire_uids` + `join_wires`) | ✅ **ALL CRITERIA MET after the three judgement rulings of 2026-09-23 07:2x, and the rulings are now MEASURED, not asserted** (`tools/bench/diag_wiki_probe.log`, 12 pass / 0 fail): ExecState 1 cold; 5,811 rows; **the wire-join criterion is 1,913 TERMED wires + the termless ones by SET DIFFERENCE against `report_all('Wire')` (3.09 s measured, 1.67 s previously) = 1,920**, and the 11 broken wires are **4 one-sided + 7 termless** — `severed()` returns exactly [1731,1893,2819,3947,4833,7337,7388,9635,11232,23502,23540] (ruling 1, gates P3a/P3b/P3c); **warm 9.73–11.9 s passes the ≤ 15 s criterion, cold 24.2 s is the load, not the read** (ruling 2); 4 known endpoints agree; 5/5 random wires == `OpWireSource_v5`; 20 calls handles ±100; **+0.7 MB/call accepted, re-measure at 100 calls** (ruling 3) |
| 2 | **Error-list reader** (`tools/lv_errorlist.py`): open LabVIEW's Error List (Ctrl+L, keyboard only, never the arrow), read EVERY item (UI Automation first; fallback capture+OCR with keyboard scrolling, overlap-checked, count vs the window's "N errors") | `tools/bench/errorlist_<vi>_<date>.json` (item: object, reason, detail) | on the bed (ExecState 0): 11 items, none missing, matches the 11 wire uids where the item names a wire; read-only, VI never run, GUI actions logged with `-Exception Approved -Evidence "user 2026-09-23 error list via GUI"` |
| 3 | **subVI wiki**: per VI `docs/wiki/subvi/<name>.json` — md5, connector-pane table (index, label, direction, type), internal terminal table + graph, input→output paths, ONE LLM sentence per subVI (once; 93 files), call sites in the main VI | ✅ **DELIVERED 2026-09-23** — `docs/wiki/subvi/*.json` (**96 files, 12.8 MB**), `docs/wiki/index.json`, `tools/wiki_build.py` + the minimal walker `tools/vigraph.py` | ✅ **8 pass / 0 fail** (`tools/bench/wiki_gate.log`): all **94** `background VIs` copies (it is 94, not 93 — the subfolder `Tracking kernel (xy_profile)` holds two more, whose names REPEAT two top-level names) + the main VI's S1 copy + the bed are in the index, each with its JSON; a re-run with nothing changed reads **0** files (96 skipped); a touched md5 re-reads **exactly 1**; every index md5 == the file's md5 and every copy is still byte-identical to its ORIGINAL. Build: **851 s for 96 VIs**, 0 unread, per-VI 0.12 s median 0.91 s max 214.7 s (the 649 KB `Track N beads 24-fold over-kernel-v3`, 10,325 terminals / 600 subVI calls) |
| 4 | **Graph + path-finding + diff** (`tools/vigraph.py`): edges from wires; tunnel outer↔inner (same owner uid, tunnel class; frame index for case/sequence); shift registers (right→left next iteration, via `Shift Registers[]`); locals by label; globals by name; subVI = one node | ✅ **DELIVERED 2026-09-23** — `tools/vigraph.py` `build4/reach4/sources_of/path/diff/computation_diff` (the step-3 walker is untouched), the gate `tools/bench/diag_vigraph_check.py`, and `tools/bench/graph_{s1,bed}_20260923.json` + `graph_diff_s1_bed_…` + `graph_computation_diff_s1_bed_…` + `graph_objs_*` / `graph_loops_*` | ✅ **9 pass / 0 fail** (`tools/bench/vigraph_check.log`, `BGRUN END rc=0 after 1s`; 4a `tools/bench/step4a_v1wiki.log` 8/0, rc=0, 891 s). `diff(S1,S1)` ∅; `diff(S1,bed)` = 15 removed / 42 added / 9 changed sinks, and **all 11 severed wires are accounted for one by one** (4 half in the bed, 5 fully wired in S1 and TERMLESS in the bed, 2 termless in both); 23 added nodes, all four delivered stages; 4/4 known endpoints; **`computation_diff(S1,bed)` = 0 rows under ASSUMPTION A**; build 0.07 s + diff 0.02 s |
| 5 | **Jev hierarchical menus** (`tools/jev_chain.py`, `tools/jev_pairs.py`): layer 1 next-subVI-in-chain (choice over Python-listed candidates), layer 2 terminal pair yes/no, op choice, 1a risk | `tools/bench/jev_menu_<name>_set.json` labelled sets + measured accuracy | each menu measured on ≥ 20 labelled items before it acts; asymmetric gating written into the code |
| 6 | **Decision record → stagekit template**: `tools/bench/decision_<stage>.json` (Jev answers verbatim + endpoints by node uid/terminal name) read directly by a stagekit stage; recall without re-asking | `tools/stagekit.py` `from_decision()`; one record for M3a-4 | M3a-4 rows executed from the record; after the run the map is re-read and the graph confirms every row |
| 7 | **Runner resumes** on M3a-4 → M4 with steps 1–6 in force | — | first cycle's LLM read/write minutes and review count reported against cycle 65 |

Order: 1 ∥ 2 → 3, 4 (need 1) → 5 → 6 → 7. Steps 1–6 are MATERIAL sessions (Opus high), failure budget 2 each; the chat
(Fable) only decides and dispatches. Every LabVIEW run under bgrun, refs closed, handles flat; originals never touched.

## Pre-decided (continues docs/cycle27-plan.md's numbering)

134. **The connectivity map is Python; no model in it.** Reader → table → graph → diff → reachability are deterministic.
135. **Jev decides per item, never advises.** A Jev insertion whose answer does not drive a code path is not delegation.
136. **Python lists candidates exhaustively by hard facts only** (direction, type, diagram reachability, sink free);
     any ranking or "plausible subset" is judgement and belongs to Jev.
137. **Record keys = node UID + terminal name (and index); wire UID is transient.** Birth UIDs of created objects are recorded.
138. **Errors of a broken VI are read from the GUI Error List**, keyboard-opened, every item (scrolling if capture),
     count-checked; COM cannot list them (`VI.Get Errors` absent from the exported interface, 2026-09-18).
139. **The op construction for step 1 must not be copy_by_index + move_in into a loop body** (`docs/s0-diff.md` D2+D4,
     failed 4×/0). Allowed: a donor that already owns the `To More Specific Class` (`OpWireSource_v5`, `OpConnectFromWire_v0`,
     `OpSubVIs_v1`) with the loop added around/into it by a route the recipe names and the prior-art review clears; if
     that also fails twice, stop and report — no third construction without the user.
140. **Wiki regeneration is md5-gated**; unchanged files are never re-read; the LLM sentence is written once per md5.
141. **Runner does not resume until steps 1–6 pass** (user: "러너 재개하기 전까지 다 빌드해보고 테스트까지").

## OPEN (for the user)

- **A.** Definition of "scheduling-only change" for the rule-1a graph diff (e.g. shift register ↔ auto-indexed tunnel).
  🟡 **ASSUMED AND IN USE SINCE 2026-09-23, AWAITING THE USER.** Step 4 could not be built without a definition, so
  `tools/vigraph.py` `SCHED_OWNER` carries this one (judgement, chat 2026-09-23): **scheduling** = tunnels (loop,
  selector, flat-sequence), shift registers, structures and their diagrams, `Local`/`Global` relays of the same
  control — **plus, added by measurement,** a front-panel terminal that is WRITTEN on the diagram and read back
  through a Local (`vigraph.transparent`), which is how M3a re-wires — and nodes whose LABEL is a Wait/timing
  primitive (7 on the bed: 3 `Wait (ms)`, 4 `Tick Count (ms)`). **Computation** = subVI calls, primitives,
  constants, real controls — and the SOURCE of each of their inputs, which must be identical. Under it,
  `computation_diff(S1, bed)` = **0 rows**. If the user narrows or widens the definition, the number changes and
  the gate is re-run; nothing else in step 4 depends on it.
- ~~**B.** Frame index of case/sequence inner terminals: from the reader row, or via `OpTunnels_v0`'s `Inner Terminals[]` order.~~ ✅ **ANSWERED 2026-09-23 — FROM THE READER ROW.** `OpAllTerms_v1.vi` (md5 `457a8d73…`, `ExecState` 1, built from the same `_s2` artefact with NO new cast; `OpAllTerms_v0` untouched) adds a seventh column `frame_diagram` = `Terminal.Diagram` **634A002** → UID. Measured on the bed (`tools/bench/allterms_v1_check.log`, **7 pass / 0 fail**): the six v0 columns are identical row for row, `frame_diagram` is non-zero on **all 1,036** inner/frame rows, and its **173** distinct values are exactly the bed's 173 `Diagram` objects, none stray. So the frame is a COLUMN, and `Inner Terminals[]` order is not needed. The wiki was built on v0; `tools/wiki_build.py --op v1` re-reads it with the seventh column (≈14 min).
