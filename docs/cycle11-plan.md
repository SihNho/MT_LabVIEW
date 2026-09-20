---
type: plan
status: superseded
superseded_by: docs/cycle14-plan.md
date: 2026-09-16
cycle: 11
rev: 2
tags: [plan, delete, opdelete, phase-a]
supersedes: []
reviewed_by: [archive/peer/2026-09-16-priorart-priorart-cycle11-delete.md, archive/peer/2026-09-16-delete-silent-noop2.md]
---

# Cycle 11 — find out why delete deletes nothing, then finish Phase A

One arc, run end to end without stopping (CLAUDE.md rule 2c).

> **rev1 is withdrawn, and saying why is the point of this revision.** rev1 assumed the delete op needed
> REBUILDING because its error indicator was dead. Two reviews and one run killed that premise in under an hour;
> the history is kept below rather than deleted, because the failure mode — repairing a tool before reading it —
> is the one this project keeps paying for.

## What rev1 got wrong

| rev1 claimed | what is actually true | source |
|---|---|---|
| the Invoke node's `error out` is unwired, so AEH pops a dialog and that dialog is the only error signal | the **real** delete produces **no dialog at all**; dialogs come only from impossible inputs, i.e. from `Index Array` / `Traverse`, never from `Generic.Delete` | `tools/bench/diag_delete_error.log:16-19`, re-measured `build_opdelete_v1.log` |
| `create_indicator` declining proves the terminal is already wired | a decline on an **unwired** terminal is already on record; a decline is not evidence about wiring | prior-art finding 5, `archive/peer/2026-09-15-opwiresource-fail1-uid-indicator-not-created.md:26-27` |
| a new indicator labelled `error out 2` confirms terminal 3 is the error **out** | that label appeared for **both** the right and the wrong terminal. The discriminator is name **plus `Is Source?`** | `tools/bench/build_opbuildpn_v1c.log:6-24` |
| the tool is broken | delete has **demonstrably worked** — six nodes of an FPTARGET copy, and 1,403 junk Invokes purged in one `net_map` — while failing on one specific node class | `docs/keystone-op-spec.md:527-529, 567, §33` |
| fixing the error reporting would reveal the cause | *"`Generic.Delete` has no semantic return value at all. Its contract is the side effect."* A clean error cluster was never evidence | codex, `archive/peer/2026-09-16-delete-silent-noop2.md` |

**Cost of that ordering:** one recipe run and one artefact (`OpDelete_v1.vi`) that is probably behaviourally
identical to `OpDelete_v0`. It was launched before its own prior-art review returned.

## The hypothesis now, and it was already written in our own code

`gscript.open_panel`'s docstring, `tools/gscript.py:1042-1048`, **2026-08-28**:

> *"Open the target's front panel — REQUIRED before `wire()` AND before `drop_subvi()`. Wiring a target loaded
> only via GetVIReference is **silently declined (count unchanged, no error)**: the diagram is not fully in
> memory. OpenFrontPanel forces the full load. Discovered after three silent failures."*

Silently declined; count unchanged; no error. That is the delete symptom word for word — and **`delete_object()`
never calls `open_panel()`.** Codex reached the same mechanism independently from NI's documentation, which marks
`Generic.Delete` **"Loads the block diagram into memory: No"**. It also explains the recorded successes: they ran
against targets that other operations had already forced into memory.

## Stage 1 — READ, then run one A/B — `tools/bench/diag_delete_matrix.py`

A diagnostic, not a build. Uses the two **creator-free** readers the prior-art review named, so the `net_map`
contamination problem does not arise at all: `node_terms` (name · **`Is Source?`** · connected-wire uid) and
`panel_wiring` (label · indicator · uid · connected-wire uid).

- **Part A** reads `OpDelete_v0` and `OpDelete_v1` with no mutation. Settles (A2) whether the Invoke's `error out`
  is bare, (A3) whether a real method is attached — an untyped Invoke reports terminals literally named `Method` —
  and (A4) whether `wire_indicators` silently no-op'd this morning.
- **Part B is the whole cycle in one comparison**: same op, same target, same class, same index — only
  `open_panel()` differs. B1 without ⇒ nothing removed. B2 with ⇒ exactly one removed.
- **Part C**, only if B2 holds: sweep the classes with `open_panel`, because the record names one class-specific
  failure (`keystone-op-spec.md:527-529`) and a clean sweep is not assumed.

## Stage 2 — the fix, whichever way B goes

- **If B2 holds:** `delete_object()` calls `open_panel(target)` before running the op, and its docstring records
  *why* — with the 2026-08-28 sentence cited, so the next reader does not re-derive it. Every other mutating
  wrapper is audited for the same omission. `OpDelete_v1.vi` is deleted: it fixed nothing.
- **If B2 fails:** the load-state explanation is refuted and the next read is codex's wire trace —
  `Invoke.Method` (637040E) on uid 297, then terminal 0 → `Connected Wire` (634A000) → `Wire.Terminals[]`
  (6371003) — to prove or disprove that the receiver is `Index Array.element`.

Either way **`STATUS.md`'s "assume every `verify=False` delete since the regression did nothing" is wrong as
written** and gets corrected: the deletes that ran against fully-loaded targets did work.

## Stage 2 — DECIDED 2026-09-16: the call stays, the EXPLANATION was wrong

`diag_delete_matrix`'s B2 held, so Stage 2's first branch was taken and `ensure_loaded()` went into 26 mutating
wrappers. Codex then refuted the *inference* rather than the measurement
(`archive/peer/2026-09-16-openpanel-ab.md`): `OpenFrontPanel` changes window activation and edit/run-mode
presentation as well as load state, so the A/B showed only "delete works after `OpenFrontPanel`".

`tools/bench/diag_load_vs_editmode.py` ran the discriminating arm codex asked for — the documented load primitive
`VI.Block Diagram` (23C), which opens no window — on fresh copies of `OpFPLabels_v0.vi`
(`tools/bench/diag_load_vs_editmode.log`, `BGRUN END rc=0 after 112s`):

| arm | first | delete |
|---|---|---|
| A0 | nothing | `4 -> 4` nothing |
| **A2** | **read 23C, no window** | **`4 -> 4` nothing** |
| A3 | `OpenFrontPanel(activate=False)` | `4 -> 3`, uid 115 |
| A4 | 23C-loaded, panel-less, `GObject.Move` | `(853,300) -> (853,300)` did not move |

**Decision: `ensure_loaded` keeps `open_panel`** — it is the only thing measured to work. The 23C read is NOT a
drop-in replacement, which is the opposite of what the review's "safer helper" paragraph suggested, and is exactly
why it was tested before being adopted.

**The mechanism is NOT settled, and the docs now say so in those words.** A second review
(`archive/peer/2026-09-16-load-vs-editmode-23c-r2.md`, ANSWERED 69 s) refuted the tempting conclusion: the 23C read
ran inside a *separate* op VI that then returned, and NI closes a top-level VI's references when it goes idle, so
A2 may have deleted against a diagram that had already been unloaded again. "Edit mode is the variable" is an
inference. It also settled two side questions: no Open VI Reference flag pins the diagram (`0x01` = record
modifications, `0x20` = hide loading dialogs), and a wire-count delta of 0 is compatible with a successful branch.

**Flag reader: STOPPED at the 2-failure budget.** 291/292 attach (terminals `PanelLoaded` / `DiagramLoaded`), but
in both attempts (`tools/bench/diag_bdloaded_reader.log`) the branch from `Open VI Reference.vi reference` into a
`VI Server:VI` Property Node's `reference` lands as a **bad wire** — wire uid 467 present, `ExecState 0`,
`remove_bad_wires` will not clear it — and `save()` correctly refuses a broken VI. Note the measurement that
contradicts the obvious guess: after `build_property` and *before* wiring, the VI is still `ExecState 1`.

**Next step, a BUILD not a diagnostic (codex's design):** one op VI that reads 23C, reads `DiagramLoaded` (292) and
calls `Generic.Delete`, keeping the diagram reference live by data dependency, with no window ever opened. That is
the only arrangement that tests residency without the unload race.

## Stage 3 — Phase A1, correctly scoped this time

A1 (`OpOwnerChain_v0`) is **2 pass / 3 fail**, not "one failure left" (`build_opownerchain_v0.log:299`). The three:

| gate | cause | fix |
|---|---|---|
| B2 | `connect2` into `reference` sinks that are **already wired** | delete the Wire-only front section FIRST; the removed wires leave those sinks bare, and only then connect |
| B3 | wire 751 has **three** consumers and node **482** is neither deleted nor re-fed — predicted on 2026-09-15 and never annotated | include 482; `REWIRE_SINKS` already lists it, the recipe's `by.get(482)` lookup is what failed |
| B4 | `#1044` typed as class `SubVI` | class `Node` |

Plus the structural problem the prior-art review found: the recipe calls `net_map` **~14 times** through its
`nodes_by_uid()` helper and reports *"purged 166 junk Invoke(s)"* with a delete that does not delete. With delete
repaired the purge works, but the walk is still the wrong reader — it is replaced by `node_terms` per node, which
drops no junk and needs no purge.

**A7 is NOT next, and rev1 was wrong to put it there.** `pre-rig-master-plan.md:66-77` gives A7 `needs: A4, A6`,
and A4←A3←A2←A1. Two of its three audits are defined *over A4's membership*. What is genuinely missing is only the
membership mapping — `motion-path-audit.md:130` says so itself: *"Step 0 first, unchanged — determine which While
loop holds what. Nothing above matters if these VIs are not on the per-frame path."* The audits themselves are
largely **already measured**: the VISA census is `motion-path-audit.md:30-99`, the UI-thread count is
`g9-core-budget.md:32` (106 nodes, 88 implicit), and the reentrancy instance plus property 288 are both on disk.
So after A1 the next step is **A2**, not A7.

## What is NOT in this cycle

No hardware. No original VI opened. No GUI action. No new op — the cycle's product is a corrected `delete_object`
and the measurement that justifies it.
