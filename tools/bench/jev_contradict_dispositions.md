---
type: bench
status: current
date: 2026-09-22
tags: [jev, pre-decided, contradiction, disposition]
---
# `jev_contradict` Pre-decided suspects — dispositions (all 10 pairs at p ≥ 0.80)

Source of the pair list: `tools/bench/jev_wave2b.log` §7 "TOP 15 SUSPECTS" (600 pairs, 3 samples each, 265 s;
readings `tools/bench/jev_wave2b_trials.json`). Items read in full from `docs/cycle27-plan.md`.
Checked and annotated 2026-09-22 by a MATERIAL session, user-approved ("전부 적용해보자"). No item text was
rewritten or deleted; each REAL pair got one `⚠️ SUPERSEDED/CONFLICT CHECK` line appended under the EARLIER item
(under BOTH for the unresolved pair).

| # | pair | p | verdict | item start lines (`docs/cycle27-plan.md`, after annotation) |
|---|---|---|---|---|
| 1 | 87 ↔ 80 | 0.96 | **REAL — 87 supersedes 80.** 87's own first line reads "80 IS WITHDRAWN": the junk `Invoke` uids are 23522 / 23786 ×8 / 9649 twice and the run prints `MINTED UID == THE LIVE SOURCE NET 23955 : False`, so the minted uid is not a constant of the op and 71 is NOT retired. | 80 `:3000`, 87 `:3086` |
| 2 | 74 ↔ 72 | 0.94 | **REAL — 74 supersedes 72** (selector only). 74: "72's ROUTE stands and only its selector changes" — `Q_focusback` is a future queue name, node 12589's terminals are `""` / `"position [internal units]"` / `""`, so 72's by-name lookup "fails by construction"; the entry is taken by exposed UID 12673. | 72 `:2882`, 74 `:2913` |
| 3 | 13a ↔ 13 | 0.92 | **NOT A CONTRADICTION** — 13's own headline already reads "⚠️ REVISED FOR THE `Z/dZ` ROW BY 13a BELOW; read both" (`:89-90`), and 13a states the scope of the revision (`TEMP_SINK_AUTHORISED` True for the `Z/dZ` row only, `SR_QUEUE_AUTHORISED` False permanently). A cold session cannot act on the wrong one; no annotation added. | 13 `:89`, 13a `:101` |
| 4 | 80 ↔ 71 | 0.92 | **REAL — 80 supersedes 71, and 80 is itself WITHDRAWN by 87.** 80 declared 71 "closed by measurement … retired, not merely narrowed"; 87 reverses that, so 71's uid-safety question is OPEN again and is answered by 86. Two hops, so a cold session can land on the wrong state twice. | 71 `:2868`, 80 `:3000`, 87 `:3086` |
| 5 | 109 ↔ 107 | 0.91 | **REAL — 109 amends 107.** 109's own first line: "107 IS AMENDED, NOT WITHDRAWN". 107's prescribed table does not exist (`Diagram #686` has 27 `Nodes[]` rows, `#681` absent; `owner_of(#681)` = `TopLevelDiagram #536`), so 107's route AND its "defer Row D" failed-prediction branch are void; 107's prohibition (no owner walk, no improvised address, no GUI fallback) stands. | 107 `:3341`, 109 `:3369` |
| 6 | 80 ↔ 76 | 0.87 | **REAL — 80 supersedes 76** ("retired, **not merely narrowed**" is an explicit contrast with 76's "NARROWED"), **and 80 is itself WITHDRAWN by 87**, so 76's narrowing is the last surviving disposition while the question itself is OPEN. | 76 `:2941`, 80 `:3000` |
| 7 | 121 ↔ 116 | 0.86 | **REAL — 121 (with 119) supersedes 116.** 116-A was "try this first … if A works nothing new is built"; 119 measured that the swapped call BRANCHES (3 source terminals, `Is Broken?` True — `tools/bench/c80_rowd_routeA_r2.log:237`, `:253-261`) and cannot land Row D. 121 also removes the c79 "step 4" probe as unsound and replaces the selecting ~2-minute test with the `UID to GObject Reference.vi` terminal-resolve measurement. 116-B survives as 121's YES branch; 116-C stays withdrawn. | 116 `:3475`, 119 `:3526`, 121 `:3549` |
| 8 | 120 ↔ 117 | 0.86 | **REAL — 120 corrects 117.** 120's own line: "PRE-DECIDED 117's LITERAL UID IS CORRECTED". Expected owner is `RightShiftRegister #23868`, not `WhileLoop #23032` (precedent `tools/bench/build_d1_m3a3_run2.log:182`). 117's owner-identity principle untouched. | 117 `:3498`, 120 `:3540` |
| 9 | 83 ↔ 44 | 0.82 | **REAL — UNRESOLVED (judgement owed → the user).** Same CLAUDE.md §5 repetition clause, opposite action: 44(b) "🔴 **DECISION — `STOP`**" (added 2026-09-20), 83 "The runner was NOT stopped, deliberately" (added 2026-09-21, later). Neither cites the other. The ordinals also disagree — 44 calls its review the **5th**, the LATER 83 calls its own the **fourth**, and `archive/peer/` holds **eight** outcome-review files (2026-09-15 … 2026-09-22). Annotated under BOTH. | 44 `:1544`, 83 `:3029` |
| 10 | 88 ↔ 29 | 0.81 | **REAL — 88 supersedes 29.** 29's headline ("THE ONLY SAVE ROUTE … IS `g.save()` UNDER PRELOAD"), 29(d) ("`allow_broken=True` is **BANNED** in every stage script") and 29(e) ("stage boundaries fall at LEGAL states") are all reversed by 88: `gscript.save(target, allow_broken=True)` diverts a broken VI to `gui_save` (`tools/gscript.py:2087-2089`), "M3a-1 can leave a file TODAY with a one-flag change", "**no boundary is re-cut**". Confirmed by the artefact: `claudeDev\D1_s3b_m3a_BROKEN_20260922_005732.vi` (STATUS.md:10). 29's riders survive inside 88 (GUI capture→locate→act→capture→confirm; verify the saved path and all four md5 pins). | 29 `:595`, 88 `:3095` |

**Totals — 9 REAL, 1 NOT A CONTRADICTION; 1 of the 9 is UNRESOLVED (#9, 83 ↔ 44).**
Detector quality on this sample: 9/10 of the p ≥ 0.80 suspects were real supersessions ⇒ precision 0.9 at that
threshold, consistent with the run's own control hit rate 8/13.

## Annotations written into `docs/cycle27-plan.md`
Under item **71**, **72**, **76**, **80**, **107**, **116**, **117**, **29** (one line each, the earlier member of
the pair) and under **both 44 and 83** for the unresolved pair. No existing sentence was changed.
