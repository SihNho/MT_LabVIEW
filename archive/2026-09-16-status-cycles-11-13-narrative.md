---
type: archive
status: superseded-location
date: 2026-09-16
tags: [status-narrative, cycle-11, cycle-12, cycle-13]
---

# STATUS narrative, cycles 11–13 — relocated 2026-09-16 (rule 4)

`STATUS.md` had reached **526 lines**; CLAUDE.md rule 4 sets the threshold at ~100 and says the remedy is to move
the narrative down a layer, unchanged, not to rewrite or delete it. Everything below was cut from `STATUS.md`
verbatim on 2026-09-16 while the retrospective-v2 comparison ran. Nothing here is new, and nothing was edited
except this header. `STATUS.md` keeps a one-line current state per item plus a pointer to this file.

Reading order if you are cold-starting: `STATUS.md` first, then this only when a one-liner there is ambiguous.

---

## From "START HERE" — items 2b, 2c, 2d (the cycle-10/11/12 retrospective history)

2b. ✅ **Cycle-10 retrospective done, 7 VIOLATIONs, all answered.** Six slugs are at 4 occurrences across cycles
   7·8·9·10. Answers: `docs/violation-decisions.md` → Round 2 (2 devices, 4 reasoned no-devices). Both devices are
   **built and tested**: the undisposed-review dispatch gate in `guard_peer.py`, and `audit_cycle.py` C4/C5 review
   cost. `violations.py` now compares decision **timestamps** (user: 타임스탬프 비교로 고친다). Headline the
   retrospective found: **six reviews, 48 min 40 s, $28.55 — and the declared reader never launched.**
2c. ✅ **Cycle-11 retrospective DONE — `archive/peer/2026-09-16-retrospective-cycle11.md`, codex, ANSWERED 258 s,
   and it fired ALL NINE slugs**, including the first-ever `judgement-in-material` (question 7's first use).
   Every citation was re-checked against the file named and all nine are **factually true**; the per-slug
   disposition is in that file's "What was done with it". `py tools/violations.py --due` now reports **two** slugs
   at threshold with no newer decision: **`scope-creep` (3)** and **`premature-build` (3)** — the other seven are
   held below the line only by the round-2 decision blocks dated `2026-09-16 15:05`, which compare NEWER than a
   retrospective whose stamp is a bare date. Hardest verified fact: `priorart_cycle11.log` ran 16:24:00 → 16:31:07
   while `build_opdelete_v1.log` started **16:26:10** — the build ran five minutes inside its own prior-art review.
2d. ✅ **Cycle-12 retrospective DONE — `archive/peer/2026-09-16-retrospective-cycle12.md`, codex, ANSWERED 247 s,
   and it fired ALL NINE slugs again.** Every citation was re-checked against the file named and the checked ones
   are true; the per-slug disposition table is in that file's "What was done with it".
   **`py tools/violations.py --due` exits 0 with NO output — nothing is at threshold, so cycle 13 is not blocked.**
   Counts now: the six round-2 slugs at **6** (answered `2026-09-16 15:05`), `scope-creep` and `premature-build`
   at **4** (answered `19:16`), **`judgement-in-material` at 2 — one below threshold and UNANSWERED**. Hardest
   facts it surfaced: A2 sampled 3/17 For, 3/76 Case and 1/57 FlatSequence-frame diagrams (so "all six classes"
   meant *sampled*, and cycle 13's 3a removes that); `priorart_cycle12_a2.log:4` reads **`COST: $5.1157 …
   48 turn(s)`**, which STATUS had not carried; `diag_load_vs_editmode.log:31` reads **`flags=UNAVAILABLE`**, so
   `Block Diagram Loaded` was never measured; `diag_owner_semantics.py` calls `g.reset()` with **no handle count
   either side**; and `audit_cycle.py:10` calls itself *"a TIME WINDOW, not a cycle boundary"*, so its 19 builds /
   37 peer logs / 59 out-of-plan files must not be quoted as cycle-12 figures.
   ⚠️ The runner that drove it exited `rc=1` on a **cp949 `UnicodeEncodeError` while printing the child's stdout**
   (`retro_cycle12.log:33-36`) — the audit and the review both completed and archived at 19:44; only the print
   failed. Not re-run.

## From "START HERE" — item 3, the silent-decline diagnosis in full

3. ✅ **SOLVED — the delete tool was never broken. Scripting EDITS are SILENTLY DECLINED until the target's FRONT
   PANEL HAS BEEN OPENED.** ⚠️ **Say it that way, not "until the diagram is loaded"** — that was an inference and
   it is now REFUTED by measurement (`tools/bench/diag_load_vs_editmode.log`, 2026-09-16, `rc=0 after 112s`,
   fresh copy of `OpFPLabels_v0.vi` per arm, same raw op, class `Property`, index 0):

   | first | delete |
   |---|---|
   | nothing | `4 → 4` nothing |
   | **read `VI.Block Diagram` (23C), the documented load primitive, NO window** | **`4 → 4` nothing** |
   | `OpenFrontPanel(activate=False)` | `4 → 3`, removed uid 115 |
   | 23C-loaded, panel-less, **`GObject.Move`** instead of Delete | `(853,300) → (853,300)` did not move |

   What is **MEASURED**: only `OpenFrontPanel` makes an edit land; the decline is **general across mutator
   families** (Delete *and* Move), not delete-specific; `ensure_loaded()` therefore keeps `open_panel` and the
   name is a misnomer. What is **NOT established — do not write it as if it were** (codex,
   `archive/peer/2026-09-16-load-vs-editmode-23c-r2.md`, ANSWERED 69 s): *"A2 did not establish diagram residency
   at mutation time… the separate loader returning creates an unload race"* — NI closes a top-level VI's
   references when it goes idle, so the 23C-reading op may have taken the diagram back out of memory before the
   delete ran. **"Edit mode is the variable" is an inference, not a result.** Same file: no Open VI Reference flag
   pins the diagram (`0x01` = record modifications, `0x20` = hide dialogs), and a wire-count delta of 0 IS
   consistent with a successful branch.
   🔴 **The flag reader is at the 2-failure stop.** `Metrics:Block Diagram Loaded` = **292** and
   `Metrics:Front Panel Loaded` = **291** are verified to ATTACH (`build_property('VI Server:VI',…)` → terminals
   `DiagramLoaded` / `PanelLoaded`), but both attempts to build a reader around them died the same way
   (`tools/bench/diag_bdloaded_reader.log`): after `build_property` the VI is still **ExecState 1**, `connect2`
   DOES wire `reference` (wire uid 467) and the VI then goes **ExecState 0**, and `remove_bad_wires` does not
   clear it — i.e. the branch from `OpReportAll_v0`'s `Open VI Reference.vi reference` into a `VI Server:VI`
   Property Node lands as a **bad wire**. Next move is codex's own design, and it is a BUILD, not a diagnostic:
   ONE op VI that reads 23C, reads `DiagramLoaded`, and deletes, holding the diagram ref live by data dependency,
   with no window ever opened.

   The A/B that put the call in 26 wrappers stands as a measurement — `tools/bench/diag_delete_matrix.log`, same
   op / target / class / index, only `OpenFrontPanel(target)` differing:

   | | without | with |
   |---|---|---|
   | OpWireSource_v5 · Property | 12 → 12, **nothing** | 12 → **11** |
   | OpFPLabels_v0 · Property | 4 → 4, **nothing** | 4 → **3** |

   With it, **every class works** (Constant · Property · SubVI · IndexArray · Wire · ControlTerminal — all
   removed exactly one, none removed an object of another class). The error cluster stayed `(False,0,'')` in
   *every* case, deleting or not: *"`Generic.Delete` has no semantic return value at all — its contract is the
   side effect"* (codex). The mechanism was already in our code, in `open_panel`'s docstring, **2026-08-28**:
   *"silently declined (count unchanged, no error): the diagram is not fully in memory"* — never generalised
   beyond `wire()`/`drop_subvi()`.
   ✅ **Fixed in `tools/gscript.py`**: new `ensure_loaded(target)` (idempotent, cached, cleared by `reset()`) now
   guards **26 mutating wrappers**; readers are deliberately untouched (they work unloaded, and the main VI is
   read constantly — rule 1d).
   ⚠️ **The old note "assume every `verify=False` delete did nothing" was WRONG** and is withdrawn: deletes
   against targets another operation had already opened *did* work — `keystone-op-spec.md:527-529,§33` records six
   node deletions and a 1,403-junk purge succeeding.
   🔴 **The same mechanism very likely explains A1's failures**: `build_opownerchain_v0.py` never calls
   `open_panel`, so its `connect2` calls were being declined too. A1 is **2 pass / 3 fail** (not "1 left").
   Reviews archived **and annotated**: prior-art cycle-11 (16 verdicts, 15 accepted), delete-silent-noop2 (codex),
   plus the earlier B2/B3, delete no-op and uid 9775 exchanges. Plan: `docs/cycle11-plan.md` **rev2**.

## From the lock block — the "last held by" history before 2026-09-16 20:10

```
# last held by material/cycle13-A3, 2026-09-16 20:00-20:06: diag_hierarchy_a3.py (bgrun END rc=1 after 304 s,
# 12 gates pass / 1 fail - gate B2, a REAL failed prediction, peer dispatched). READ-ONLY: main VI md5
# 2a78e17c449cacdaf5da389818526859 before AND after (gate Z). Scratch ScratchA3_21976.vi created from EMPTY_v0
# for the Frames[] attach census and DELETED in the same run (verified in the log). No op VI built, modified or
# saved. LabVIEW pid 23312 (started by fresh()) exited with its client - verified 20:06, no LabVIEW process.
# last held by material/cycle12-A2, 2026-09-16 19:34-19:36: diag_owner_semantics.py (bgrun END rc=0 after 73 s,
# 54 gates pass / 0 fail). READ-ONLY: main VI md5 2a78e17c449cacdaf5da389818526859 before AND after (re-verified
# out-of-band after the run). No op built, modified or saved; no scratch VI. LabVIEW pid 23668 (started by
# fresh()) exited with its client - verified 19:36, no LabVIEW process.
# last held by material/cycle11-closeout, 2026-09-16 19:03-19:04: diag_ownerchain_hop.py (bgrun END rc=1 after
# 34 s, 8 gates pass / 3 fail - a REAL failed prediction, peer dispatched). READ-ONLY: main VI md5
# 2a78e17c449cacdaf5da389818526859 before and after. No op built, no VI saved, no scratch VI. LabVIEW pid 14952
# (started by fresh()) exited with its client - verified 19:0x, no LabVIEW process.
# last held by material/cycle11-A1-run, 2026-09-16 18:52-19:0x: build_opownerchain_v1.py (20 pass / 0 fail,
# 90 s, bgrun rc=1 is the regex false positive in OPEN 6) and diag_reset_gate_outer.py (rc=0, 46 s). Main VI
# md5 2a78e17c449cacdaf5da389818526859 BEFORE and AFTER both runs. OpOwnerChain_v1.vi saved (17 151 bytes),
# OpDelete_v1.vi deleted, no scratch VI left. Verified 19:0x: no LabVIEW process (both fresh() instances exited).
# last held by material/cycle11-A1, 2026-09-16 18:00-18:45: wrote tools/recipes/build_opownerchain_v1.py (NOT run -
# prior-art gate), 3 prior-art dispatches, and re-ran diag_save_persists.py (rc=0, 82 s, W2). No original opened,
# no hardware, no scratch VI left on disk. LabVIEW pid 5476 (started by the diagnostic's second fresh()) EXITED
# with its client - verified at 18:47, no LabVIEW process. Main VI md5 2a78e17c449cacdaf5da389818526859, the
# recorded baseline (docs/diagram-hierarchy.md:85), unchanged.
# last held by material/cycle11-loadmode, 2026-09-16 17:2x-17:4x: diag_load_vs_editmode.py (rc=0, 112s) +
# diag_bdloaded_reader.py (rc=1, 66s, 2-failure stop). LabVIEW pid 23084 left running, no scratch VIs on disk.
```

**Verified, not assumed:** no LabVIEW process at 15:4x — the last diagnostic's instance (pid 14352) did **not**
exit with its client and was killed explicitly. So the old note *"a COM-launched LabVIEW with no panel exits with
its client"* is **not reliable**: always `tasklist | grep -i labview` and kill a stray rather than trusting it or
this file. Fresh instances sit at ~31,500 handles; use a unique scratch VI name per run, and delete the scratch in
the same run that creates it.

## From OPEN 1 — the full measured record of the periodic auto-reset question

1. 🟡 **Is the PERIODIC auto-reset gated by `Auto-Reset`?** It decides whether an hours-long dry run terminates
   itself on `Limit of Program`. Measured 2026-09-16 (`tools/bench/diag_reset_arm.log`): the period **enters** the
   frame loop through `LoopTunnel` #10114 and the remainder **leaves** through `LoopTunnel` #10177 — the decision is
   assembled **outside diagram 43**, so it needs A1's owner chain. The lost-bead arm *is* gated, by `And` #9647.
   **⚠️ CORRECTED 2026-09-16 19:5x (judgement, from the A2 owner reads below):** the modulo `Function` #10068 sits on
   **Diagram 639 = the frame loop's own body**; #10114 is an **input** tunnel of WhileLoop 637 (the period enters);
   #10177 is an **input** tunnel of **ForLoop 1359, which itself sits on 639**. So the remainder does not *leave*
   the frame loop — the reset decision is computed **inside** it and fed into an inner ForLoop. "Assembled outside
   diagram 43" was wrong. Whether `Auto-Reset` gates it is now one read: the sources of ForLoop 1359's input
   tunnels (cycle 13, task 3d).
   **VERDICT 2026-09-16 20:2x (judgement, from cycle 13 3d):** ForLoop #1359's ten input wires contain **no**
   `Auto-Reset` (wire 9806) and **zero** panel-control sources — the periodic reset path is **NOT gated at the
   wire level**. Not yet final: this VI reads its panel through 106 `Value` property nodes, so a property read of
   `Auto-Reset` *inside* #1359's diagram would still gate it. One read closes it (cycle 14): `node_labels` on
   #1359's inner diagram for a node labelled `Auto-Reset`.
   ⚠️ **A cheaper route may exist and has never been run** (prior-art review, 2026-09-16, rev3 finding 4 /
   rev2 finding 4): `tunnels()` gives #10114's **outer** terminal and wire, `OpWireSource_v5` gives that wire's
   **driving object's uid**, and `diagram_tree_main.json`'s per-diagram lists are net_map's FULL node lists (not
   just structures), so the driver's home diagram may already be a lookup. Two op runs. It does not remove the
   need for A1 in general (the JSON walk is capped at `max_nodes=120` per diagram and holds neither 10114 nor
   10177), but it might answer THIS question without it — a scope call for a judgement session.
   ✅ **The cheap route has now been RUN — `tools/bench/diag_reset_gate_outer.log`, 2026-09-16 19:0x, rc=0, 46 s,
   4/4 wires resolved, census agreement 2/2, main VI md5 unchanged. MEASURED WIRE SOURCES ONLY, no conclusion:**

   | wire | source (owner class, uid) | sinks |
   |---|---|---|
   | **9000** — 10114 outer, never read before | `('Diagram', 686)` | `('GrowableFunction', 8953)`, `('LoopTunnel', 10114)` |
   | 10103 — 10114 inner (re-read, agrees with `diag_reset_arm.log`) | `('LoopTunnel', 10114)` | `('Function', 10068)` |
   | 10187 — 10177's other side (re-read, agrees) | `('Function', 10068)` | `('LoopTunnel', 10177)` |
   | **10166** — 10177's remaining side, never read before | `('LoopTunnel', 10177)` | `('GrowableFunction', 8634)` |

   Against the script's own prediction contract: 10114's outer source matched **NEITHER** signature (class
   `Diagram`, i.e. a terminal owned by diagram 686 — not a combiner, not one of `Terminal`/`ControlTerminal`/
   `Constant`); 10177's outer source matched the **GATED** signature by class alone (`Function` #10068 — but that
   is the modulo itself, so the class test is not sufficient here). **What these two rows mean for "is the
   PERIODIC auto-reset gated by `Auto-Reset`", and which wire to read next, is judgement — not written here.**

   ✅ **ONE MORE HOP — `tools/bench/diag_ownerchain_hop.log`, 2026-09-16 19:03, `BGRUN END rc=1 after 34s`,
   8 gates pass / 3 fail, `OpOwnerChain_v1.vi`, main VI md5 unchanged. MEASURED, NO INTERPRETATION:**

   | uid asked | its own class (op self-read) | owner class | owner uid | error |
   |---|---|---|---|---|
   | **686** | `Diagram` | **`FlatSequenceFrame`** | **0 — not returned** | `error 1055: Property Node in OpOwnerChain_v1.vi`; the op's cast-class echo came back **empty** (`''`), where the two rows below echo `'Diagram'` |
   | **8634** | `GrowableFunction` | `Diagram` | **7911** | none |
   | **8953** | `GrowableFunction` | `Diagram` | **686** | none |

   🔴 **The second hop was NOT reachable**: hop 1 returned owner uid 0, so "the owner of 686's owner" is
   unmeasured. Three predictions failed — P1a (686 resolves with no error), P2 (686's owner is a structure or the
   VI; `FlatSequenceFrame` was not in the contract's list), P3 (the second hop returns). Mandatory peer review:
   the first dispatch **TIMED OUT at 180 s and told us nothing** (`peer_ownerchain-flatseqframe-1055.log`,
   `BGRUN END rc=2`); re-dispatched with `-TimeoutSec 700` and **ANSWERED in 147 s** —
   `archive/peer/2026-09-16-ownerchain-flatseqframe-1055-r2.md`, annotated. (Saying only "dispatched" was the
   `unreported-fact` the cycle-11 retrospective caught; dispatch is not completion.)
   **Confirmed in our own code, and it is a measurement gap, not an opinion:** `read_owner()` reads
   `("errL","errT","errO","errU","errG")` (`build_opownerchain_v1.py:269`) and never reads **`errCO`**, the cast
   node's own error, which the labels file does define. So *"the cast to `GObject` failed"* is **implied, never
   measured**. Codex's hypothesis — `FlatSequenceFrame` is a sibling of `GObject` under `Generic`, so it has no
   `GObject.UID` to read at all — is **unverified** (labviewwiki, not the machine). Its cheapest discriminating
   test, not run: branch the RAW `Generic.Owner` with no cast and read `Class Name`, `Class ID`, and that owner's
   own `Generic.Owner` class name; predicted `FlatSequenceFrame` → `FlatSequence`, no 1055.

   ✅ **THE THREE OWNERS ARE NOW READ — `tools/bench/diag_owner_semantics.log`, 2026-09-16 19:34, `BGRUN END
   rc=0 after 73 s`, 54 gates pass / 0 fail, main VI md5 unchanged. MEASURED, NO INTERPRETATION:**

   | uid asked | its own class | owner class | owner uid | error |
   |---|---|---|---|---|
   | **10068** | `Function` (the PERIODIC modulo) | **`Diagram`** | **639** | none |
   | **10114** | `LoopTunnel` | **`WhileLoop`** | **637** | none |
   | **10177** | `LoopTunnel` | **`ForLoop`** | **1359** | none |

   For scale, from the same run: `Diagram#639`'s owner is `WhileLoop#637` — the frame loop — and `ForLoop#1359`'s
   own diagram is 7911, whose owner is `ForLoop#1359`… i.e. 1359 is a ForLoop that **sits on diagram 639**
   (`docs/diagram-hierarchy.md`, A2 table row ForLoop 7911 → `ForLoop#1359` → parent `Diagram#639`).
   **What this says about "is the PERIODIC auto-reset gated by `Auto-Reset`" is judgement and is NOT written here.**

   ✅ **ALL TEN TERMINALS OF `ForLoop#1359` ARE NOW READ — `tools/bench/diag_hierarchy_a3.log` 3d, 2026-09-16
   20:0x, `node_terms_uid(MAIN, 43, 16)` live (uid and wire set identical to `main_vi_nodeterms.json`), then
   `OpWireSource_v5` on each of the 7 input wires. MEASURED, NO INTERPRETATION:**

   | t | terminal name | dir | wire | the node that DRIVES it (class, uid, label) |
   |---|---|---|---|---|
   | 0 | `''` | in | **0 — BARE** | nothing: this is the For loop's **`N`/count terminal and it is UNWIRED** |
   | 1 | `''` | in | 9097 | `LeftShiftRegister` **9025** |
   | 2 | `''` | **out** | 9215 | — |
   | 3 | `Value` | in | 30592 | `Property` **30117**, label **`Trans Pos (mm)`** |
   | 4 | `''` | in | 28847 | `Function` **8885**, label **`Multiply`** |
   | **5** | `''` | **in** | **10187** | **`Function` 10068, label `Quotient & Remainder`** — the PERIODIC modulo |
   | 6 | `''` | **out** | 11352 | — |
   | 7 | `Force\nsmoothing\nhalf-width` | in | 31059 | `Diagram` **639**; `panel_wiring` puts control uid **28148** (`Force smoothing half-width`) on the same wire |
   | 8 | `Extension\nmedian filter\nhalf-width` | in | 31166 | `Diagram` **639**; control uid **28996** on the same wire |
   | 9 | `Magnet position output` | in | 28338 | `LoopTunnel` **28343** |

   🔴 **`Auto-Reset`'s wire is 9806** (control uid 17472, `docs/main-vi-panel-map.md:317`) and **9806 is NOT among
   `ForLoop#1359`'s ten terminal wires** — measured, gate D1c. **Zero** of the seven input sources is a
   `ControlTerminal`/`Terminal`; two are `Function` (10068 `Quotient & Remainder`, 8885 `Multiply`).
   ⚠️ **API fact worth keeping:** a front-panel control's diagram terminal reports its source owner as class
   **`Diagram`** (t7/t8 above), which is the same shape as the unexplained `('Diagram', 686)` row further up —
   so "class `Diagram`" in an `OpWireSource_v5` source means *a terminal owned by that diagram*, and
   `panel_wiring`'s wire match is what names it. ⚠️ Small correction to `docs/frame-loop-wire-graph.md:440`,
   which names the t1 shift register **9018**: the machine says **9025**.
   **What this says about "is the PERIODIC auto-reset gated by `Auto-Reset`" is judgement and is NOT written here.**

   **Tunnel direction — MEASURED, and the reporter is `g.tunnels()`** (`tools/gscript.py:747`; it already returns
   `out_is_source` for the outer terminal and `in_is_source` for the inner ones. `node_terms()` also reports
   `is_source` but is addressed by (diagram index, node index), which is recorded for neither tunnel, so
   `tunnels()` is the one that answers with the access index `main_vi_tunnels.json` already holds):

   | tunnel | outer terminal `Is Source?` (wire) | inner terminal `Is Source?` (wire) | index_mode | direction |
   |---|---|---|---|---|
   | **#10114** (idx 62, name `'# FD points'`) | **False** (9000) | **True** (10103) | 0 | data flows **INTO** the loop |
   | **#10177** (idx 33, name `''`) | **False** (10187) | **True** (10166) | 0 | data flows **INTO** the loop |

   ⚠️ **Two corrections to the wording above, from the census the run re-verified (P5 passed 2/2):** for #10177
   the OUTER wire is **10187** and the INNER wire is **10166** — calling 10166 "10177's outer wire" is wrong. And
   both tunnels measure as **input** tunnels, so "the remainder **leaves** through `LoopTunnel #10177`" is an
   inference the measurement does not support.

## From OPEN — the long-form entries 2, 2c, 7, 8, 9, 10

2. 🟢 **Autofocus decision path — closed.** `CaseStructure #10407` fires on `(frame counter mod 25) == 0 AND
   NOT(Fix to a Certain Pattern)` — **every 25 frames ≈ 3.6 Hz at 90 Hz** — and transacts serial when it fires.
   But `Fix to a Certain Pattern` is **written by code every iteration** (Property Node #1469) from
   `NOT( Auto-Focus AND NOT(reseed-And 9921) AND (counter < Limit of Auto-Focus) )`, so **the switch that stops the
   piezo is `Auto-Focus` (uid 24266)**, exactly as the user said. Derivation: `docs/camera-acquisition-facts.md`.
2c. 🟢 **uid 9775 READS the camera geometry — and the size the VI WRITES is the FRONT-PANEL display area, not the
   camera ROI.** MEASURED 2026-09-16, both halves (the second confirms the user from memory: read the camera frame
   size, then set the IMAQ display size). Chain, divisor and caveats: `docs/camera-acquisition-facts.md`,
   "MEASURED 2026-09-16 — uid 9775 READS the geometry". **Consequence: the plan’s 1280×1024 budget basis is safe.**
   ⚠️ Do NOT widen it to "the VI does not set frame size" — the codex review refuses that (archived, annotated);
   the residual test is `Property Items[] → Is Write` across the 106 Property nodes. The fresh-session 640×512 ROI
   reading stays **unexplained** and is a different thing from the ÷2 display size.
6. ✅ **RESOLVED 2026-09-16 — `tools/bgrun.py:56` regex narrowed.** The summary alternative is now
   `=== .*?\b[1-9]\d*\s+fail(?:ed|ure)?\b` (was `=== .*?\bfail(?:ed|ure)?\b`): a non-zero count must precede the
   word. The other two alternatives (`\b(?:exit|rc)\s*=\s*([1-9]\d*)`, `^\s*\*\*FAIL\*\*`) are byte-identical.
   The pattern is **not shared** — `logclass.py` holds no failure regex, and `audit_cycle.py:53` /
   `guard_peer.py:67` have their own separate `FAILURE_RE`, untouched. Tested 11/11:

   | line | before | after |
   |---|---|---|
   | `=== OpOwnerChain_v1 build: 20 pass, 0 fail ===` | match (the bug) | **no match** |
   | `=== build: 17 pass, 3 fail ===` | match | match |
   | `=== build: 0 failed ===` / `=== build: 20 pass, 0 failure ===` | match | **no match** |
   | `=== build: 2 failed ===` · `probe exit=1` · `rc=2` · `**FAIL** …` | match | match |
   | `-> FAIL  B2 ...` | **no match** | **no match** |

   ⚠️ **Fact that corrects the brief:** `-> FAIL` was **never** a bgrun pattern — bgrun only ever matched
   `**FAIL**` at line start. `^\s*(?:->\s*)?FAIL\b` lives in `audit_cycle.py:53` and `guard_peer.py:67`, and both
   still match `-> FAIL  B2 ...` (verified in the same test). Whether bgrun should ALSO gain that alternative is a
   widening, not a narrowing, and was not done.
7. ✅ **RESOLVED 2026-09-16 (cycle 12) — both round-3 slugs answered and BOTH DEVICES BUILT AND TESTED.**
   `py tools/violations.py --due` now exits 0 with no output. The decisions are `docs/violation-decisions.md`
   round 3 (`2026-09-16 19:16`), both `DECISION: device`:
   - **`premature-build` → `tools/hooks/guard_cycle.py:premature_build()`**, checked before the verdict gate (a
     review still in flight has no verdicts to refute, which is exactly the cycle-11 case). Refuses a RECIPE build
     while (a) a `tools/bench/priorart_*.log` newer than the newest retrospective has no `BGRUN END|TIMEOUT` line,
     or (b) no `archive/peer/*priorart*.md` is newer than the recipe FILE's mtime. **Tested 4/4 on fake files in a
     scratch tree**: running review → REFUSED · ended review + archive newer than recipe → ALLOWED · recipe edited
     after its review → REFUSED · no priorart archive at all → REFUSED.
   - **`scope-creep` → `tools/audit_cycle.py` line C7** (counter, not refusal, by the decision's own wording):
     every file modified in the window not named in `docs/cycle<N>-plan.md` (`--cycle`, else the newest plan);
     excludes `archive/`, `tools/bench/*.log|json`, `.claude/`, and the plan file itself. First run:
     **62 files not named in `docs/cycle11-plan.md`**.
8. ✅ **RESOLVED 2026-09-16 — `tools/bgrun.py` now skips the inner-failure scan for REVIEW logs**
   (`logclass.is_review_log(--log)`; the process's own exit code still decides). Measured both ways on the exact
   sentence from `retro_cycle11.log:102`: review-named log → **`BGRUN END rc=0`** (was rc=1), build-named log →
   **`rc=1` unchanged**, so no failure-detection capability was lost. The probe logs were deleted in the same run.
9. 🟢 **A2 IS DONE — owner semantics measured for all six structure classes** (`tools/bench/diag_owner_semantics.log`,
   54/54, 73 s; table and the five numbered facts: `docs/diagram-hierarchy.md`, "A2 — OWNER SEMANTICS PER STRUCTURE
   CLASS"). **Five classes behave exactly like `CaseStructure`** (diagram → structure returns a non-zero uid; the
   structure → parent-diagram hop returns, for the first time ever). **`FlatSequence` is the one exception**,
   reproduced on a second diagram (113, not just 686): owner class `FlatSequenceFrame`, uid **0**, `error 1055`,
   empty cast echo — and `errCO` (the cast node's own error, read for the first time) carries **the same** 1055
   string while the op's `error out` stays empty. **Position matching agreed with the machine 14/14.**
   ✅ **ALL THREE JUDGEMENT CALLS BELOW WERE TAKEN by the judgement session, 2026-09-16, and are recorded in
   `docs/cycle13-plan.md`:** (a) **A3 proceeds now** on the five clean classes with `OpOwnerChain_v1` unchanged;
   (b) **FlatSequence is handled TOP-DOWN by measurement**, not by modifying the op and not by building
   `AllTypes[]`, which stays under OPEN; (c) the 1055's origin is settled by **one read** (cycle 13's 3c), not by
   argument. ⚠️ Also correct the wording above: A2 measured **sampled** class behaviour (3/17 For, 3/76 Case,
   1/57 FlatSequence-frame…), not all 170 — the cycle-12 retrospective's `unreported-fact`. Cycle 13's 3a is what
   makes it exhaustive for the 112 clean diagrams.
   **The three judgement calls, as they were posed:**
   (a) does A3 now proceed on the five classes and treat FlatSequence separately, or wait for the reader?
   (b) codex's uncast `Generic.Class Name` / `Class ID` / `Owner` test is still unrun — and the prior-art review
   named a cheaper route nobody has cited: **`ClassSpecifierConstant.AllTypes[]`** (`docs/NAMES.md:611-622`)
   enumerates the VI Server classes **with their parents**, which answers "is `FlatSequenceFrame` outside the
   `GObject` subtree?" from the machine instead of from labviewwiki. Supporting evidence found the same day:
   the machine refuses `FlatSequenceFrame` as a *traverse* class with **error 1092** = "not in the VI Server
   GObject hierarchy" (`build_diagram_hierarchy_run3.log:8`; `docs/NAMES.md` corrected accordingly).
   (c) whether the 1055 in `errCO` is generated by the cast or propagated into it.
   ⚠️ **brief pre-scripted: none** — the brief asked only for the measurement, and the FlatSequence arm was
   predicted to fail from the earlier measurement, so gate FS passing is a reproduction, not a surprise.
10. 🟢 **A3 IS MEASURED FOR THE 112 CLEAN DIAGRAMS — `tools/bench/diag_hierarchy_a3.log`, 2026-09-16 20:00,
   `BGRUN END rc=1 after 304 s`, 12 gates pass / 1 fail, main VI md5 unchanged.** Table:
   `tools/bench/diagram_tree_a3.json`; narrative: `docs/diagram-hierarchy.md`, "A3 — THE 112 CLEAN DIAGRAMS".
   **112 diagrams → 63 structures → parent diagram, every hop from the machine. Position matching: 100 agree,
   0 DISAGREE; 12 of the 41 it never resolved are now resolved; the `diagram_tree_main.json` lookup agrees
   112/112.** What is left is exactly the **57 `FlatSequenceFrame` diagrams**.
   🔴 **The FlatSequence top-down route is CLOSED with the ops we own — and that is the one FAILED PREDICTION
   of this run (gate B2).** Four independent measurements: traverse `Tunnel` works (**468** objects) but **zero**
   are owned by a FlatSequence, so `OpTunnelRead_v0` has nothing to seed; traverse `Structure` = **63** = 84 − 21;
   traverse `MultiFrameStructure` = **43** = 37+4+2, so **FlatSequence is not a MultiFrameStructure**;
   `SequenceTunnel`/`FlatSequenceTunnel` → **1092**; and `Frames[]` **6363801** on `VI Server:FlatSequence` is
   **refused with 1077** while the same id attaches on `VI Server:MultiFrameStructure`.
   ✅ **THE PEER REFUTED IT AND THE MACHINE AGREES WITH THE PEER —
   `archive/peer/2026-09-16-flatseq-frame-unreachable.md` (codex, ANSWERED 125 s, annotated) +
   `tools/bench/diag_flatseq_diagrams_attach.log` (`BGRUN END rc=0 after 33 s`, **5 gates pass / 0 fail**,
   scratch VI deleted in the same run, main VI never opened).** `FlatSequence` (class id **16459**) has its OWN
   accessors: **`Diagrams[]` = `3578BC00` ATTACHES with data terminal `'Diagrams[]'`** — the frame **Diagram**
   references directly — and `Frames[]` = `3578BC07` attaches too; `6363801` was refused only because that id
   belongs to `MultiFrameStructure`. So **the 57 frames ARE reachable**, and the claim that died was *"unreachable
   by any traverse-class + property route"*, not the narrower measured one (`FlatSequence` sits outside the
   `Structure`/`MultiFrameStructure`/`Tunnel` branches, and `FlatSequenceFrame` is not a `GObject`).
   🟡 **Walking `Diagrams[]` needs a NEW OP VI — that is the judgement call, and the ids are now measured, not
   guessed.** The cheapest shape codex named: traverse `FlatSequence` → `Diagrams[]` (`3578BC00`) → per element
   `GObject.UID` (`632A813`), no `Owner`, no cast, no tunnels.
   🟢 **3c answered the errCO question and the answer is clean:** on diagram 113 the **upstream `Owner` property
   node (`errO`) is EMPTY**, and only `errG` (the UID node) and `errCO` (a `ClassName` node) — **both downstream
   of the cast** — carry the 1055. ⚠️ The cast is a Function with **no error indicator in the op**, so this does
   NOT establish that the cast generated it; it establishes that the `Owner` read succeeded and the cast's
   OUTPUT is what cannot be read.

## From NEXT — the cycle 11/12/13 result blocks

🔵 **CYCLE 13 closed the cycle-12 retrospective and measured A3.** Plan: `docs/cycle13-plan.md`.
Prior-art review `archive/peer/2026-09-16-priorart-priorart-cycle13-a3.md` (opus, ANSWERED 591 s, $5.1239,
**10 verdicts, all accepted, none argued**) — it deleted 3d's ~40-run ownership walk before it ran
(`main_vi_nodeterms.json` already held #1359's terminals), cut the `Frames[]` arm to one attach census, corrected
the `errCO` mislabel, replaced "no 1077 = attached" with the data-terminal-name census, and handed over
`Auto-Reset = wire 9806`. Released by ten `FIXED:` lines. **Four judgement questions are waiting, all under
OPEN 9/10 and OPEN 1, and none was answered inside this material session:**
1. **The FlatSequence 57 — build the `Diagrams[]` reader, or ship 112/170 and move to A4?** No longer "is it
   possible": `FlatSequence.Diagrams[]` **3578BC00** is **measured attaching** with data terminal `Diagrams[]`
   (peer refuted my claim, machine confirmed the peer — 5/5, 33 s). It needs **one new op VI** — traverse
   `FlatSequence` → `Diagrams[]` → `GObject.UID` `632A813`, no cast, no `Owner`, no tunnels — which the plan's
   STOP condition reserves for judgement. `ClassSpecifierConstant.AllTypes[]` is now **unnecessary for access**
   (codex: it only confirms the class tree) and can be dropped unless wanted for its own sake.
2. **Is a 112-of-170 hierarchy enough for A4?** A4 is "the frame loop's TRUE membership, body and nested frames"
   — and the 57 unresolved diagrams are precisely *frames*.
3. **STATUS OPEN 1** is now fully measured on the input side (table above) and needs its verdict.
4. **`judgement-in-material` sits at 2 of 3** with no decision recorded (`docs/violation-decisions.md`).

🟡 **Judgement call first (cycle 11, stage "load vs edit mode"):** the operational rule is settled and unchanged —
edits need `open_panel`, so nothing in the fleet needs editing — but the MECHANISM is open and the cheap route to
it is closed (flag reader at the 2-failure stop; see item 3). The remaining test is a BUILD: one op VI that reads
23C + `Metrics:Block Diagram Loaded` (292) + `Generic.Delete`, diagram ref held live by data dependency, no window.
**Is that worth a build cycle at all?** It changes no code; it changes what we write. A1 does not depend on it.

🟢 **SAVE WORKS — measured 2026-09-16 18:41, `tools/bench/diag_save_persists.log` (`rc=0, 82 s`).** One
`delete_object(..., verify=True)` on a fresh donor copy returned `gone=[1319]`, the class count went `12 → 11`,
and after `save()` (18 021 bytes vs the donor's 18 163) **and a killed/restarted LabVIEW** the uid was still gone
and `ExecState 1`. **Verdict W2: saving is not the defect; v0's edits never happened.** This diagnostic had
aborted at 15:22 on the silent-decline bug and was never re-run — the prior-art reviewer found that.

✅ **A1 IS BUILT AND WORKS — `OpOwnerChain_v1.vi`, 20 gates pass / 0 fail, `tools/bench/build_opownerchain_v1.log`
(2026-09-16 18:52, 90 s).** Released by the three archives' new `FIXED:` lines. Nine deletes each returned exactly
the wanted uid; wire 1081 survived (B3c `{990,307,310} → 1081`); R1 gave 241.`reference` = 1081, R2 `Owner` wire
672 read by all three consumers 163/1221/482; junk purge `[154,151,148,145]`; `ExecState 1` before and after
`save()` (17 151 bytes) **and after a killed/restarted LabVIEW** (B5/B5b). **FUNCTIONAL, on the main VI read-only
(B6):** uid `10407 → owner Diagram#639`, uid `1359 → Diagram#639`, and `639 → WhileLoop#637` — the hop
`docs/diagram-hierarchy.md:36` predicted. `OpDelete_v1.vi` deleted (B7); main VI md5 unchanged (B8).
⚠️ The runner said `rc=1` on a **passing** run: `tools/bgrun.py:56`'s inner-failure regex `=== .*?\bfail…` matches
the summary line *"=== OpOwnerChain_v1 build: 20 pass, 0 fail ==="*. A false positive in a device built the same
day; not patched here (see OPEN 6).

The A1 rewrite, all four changes justified by measurement or review:
1. **`ensure_loaded` is now automatic** in `connect2`/`delete_object`, so the silent declines should stop.
2. ⚠️ **CORRECTED 2026-09-16: delete by class `Node` (nodes) and `Wire` (wires), NOT `GObject`.** The `GObject`
   prescription was never measured — `diag_delete_matrix.py:65` swept seven concrete classes and not that one —
   and it cannot work: `GObject` also enumerates Terminals (`toolkit-capabilities.md:103`, 10030 vs `Terminal`
   5763), so deleting a node removes objects inside the same class list and a `gone == {uid}` check can never
   hold. The `#1044` question is answered by measurement instead: `diag_ownerchain_state.log:13-19` lists all
   seven delete targets under `Node` (1044 ONLY there), which is also the class five existing recipes delete by.
3. **Deletes FIRST, then connects.** Removing the Wire-only front section leaves the three `reference` sinks bare,
   which is the only safe state to connect into. Node 241's `reference` needs its feeding **wire** deleted too.
4. **Node 482 is the third consumer of wire 751** — predicted 2026-09-15 (`archive/peer/2026-09-15-priorart-ownerchain.md:117`), confirmed by `build_opownerchain_v0.log:143`
   (`consumers {163: 751, 1221: 751, 482: 1444}`), and missing from every fix list since.
5. **No `net_map`.** The v0 recipe walks it ~14 times through `nodes_by_uid()`; replace with one `node_terms_uid`
   sweep (creator-free, drops no junk).

✅ **CYCLE 12: both round-3 devices built and tested, the bgrun review-log false positive fixed, and
A2 measured.** Plan: `docs/cycle12-plan.md`. Prior-art review
`archive/peer/2026-09-16-priorart-priorart-cycle12-a2.md` (opus, ANSWERED 481 s, **8 verdicts / 7 slugs, all
accepted, none argued**) — it deleted 18 op runs from the A2 script before it ran (`helper-exists`:
`report_all('Diagram')` returns uid + owner class for all 170 in ONE run), narrowed A2 to the two things genuinely
unmeasured (`contradicted`: the owner **uid** and the parent hop, not the owner class), cut the FlatSequence arm
from three instances to one, and added the `errCO` read. **After A2 comes A3** — with the judgement calls in
OPEN 9 answered first.

**A7 is NOT next.** `pre-rig-master-plan.md:66-77` gives A7 `needs: A4, A6`, and A4←A3←A2←A1; two of its three
audits are defined over A4's membership. The audits are also largely **already measured** — the VISA census is
`motion-path-audit.md:30-99`, the UI-thread count is `g9-core-budget.md:32` (106 nodes, 88 implicit), reentrancy
property 288 and the `ASI_adjust focus-subvi.vi` instance are both on disk. **After A1 comes A2.**
