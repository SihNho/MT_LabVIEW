---
type: archive
status: archived
date: 2026-09-18
tags: [status, narrative, census, cycle1]
---

# Relocated from STATUS.md — 2026-09-18, cycle-1 material session (rule 4: STATUS was 129 lines)

Nothing here is rewritten. Each block is the STATUS text VERBATIM as it stood before the move;
STATUS keeps one line and a pointer per item.

## 1. The `## START HERE` operating hints (STATUS lines 12–28 as of 2026-09-17)

> ## START HERE
> 1. **`docs/pre-rig-master-plan.md` is THE plan**; decisions **`docs/decisions.md`**; cycle `docs/cycle15-plan.md`;
>    **NOW SUPERSEDED FOR P1 by `docs/motor-limit-assurance-plan.md`** (see NEXT). D1: build plan
>    `docs/d1-build-plan.md` + **`docs/d1-route-b-plan.md`** (route A closed, B built; §11u's run-9 gate is UNSOUND —
>    never cite it; §10 OpGetErrors NOT AUTHORISED). 2. ⚠️ A prior-art
>    dispatcher's log MUST be named `priorart_*` / `peer_*` (`tools/logclass.py`) or the guards read the reviewer's
>    prose as a build failure. 3. ✅ Scripting EDITS need the target's FRONT PANEL open; a fixed op PATH is served
>    from LabVIEW's MEMORY — unique scratch name/run.
> 4. ✅ `guard_cycle` releases on a `FIXED: <slug> - <path>:<line> - …` line under a prior-art archive's "What was
>    done with it" (§11g.3) — ONE PER SLUG, or `REFUTED:` with the citation opened. 5. ⚠️ `peer.ps1` only as
>    `powershell -Command "& 'tools/peer.ps1' … -TaskFile <f>"` — `-File` loses a multi-line `-Task`;
>    and `tools/prior_art_review.py` must be launched from **PowerShell**, not the Bash tool (rc 127 there today).
>    Use **`-Dual -TimeoutSec >= 780`**: at the 180 s default the opus arm times out.
> 6. 🔴 **NEVER patch a file with a `py - <<'EOF'` heredoc** — on 2026-09-17 one truncated **this file to 0 bytes**
>    mid-write on a lone-surrogate `UnicodeEncodeError`. Use Edit/Write (CLAUDE.md already says so).
>    ⚠️ Also: `py -m py_compile <path under tools/recipes>` trips `guard_cycle`'s BUILD_RE (the `py` in
>    `py_compile` matches) — compile-check from a different invocation or not at all.

## 2. The `## Where things stand` block (STATUS lines 66–75 as of 2026-09-17)

> ## Where things stand
> 🆕 **P1 step 1 (CENSUS) DONE — `tools/motor_census.py` (a READER) → `docs/motor-call-site-census.md`.**
> `motor_census_run2.log`, `BGRUN END rc=0 after 236s`, 3/3 gates, both originals' md5 unchanged, nothing run/saved.
> ORIGINAL = **97 call sites, 41 MOTION, 41/41 decided by reachability, NAME_ONLY 0**; MOV 7 / VEL 4 match the plan.
> 🔴 **14 UNCLASSIFIED** (reach a serial write, not on the name list — three are LAB VIs) and ⚠️ **11 UNKNOWN**
> (error 1040, no readable vi.lib diagram — never read as "no"). Detail + both dead routes: that doc. ⛔ run 1
> `motor_census.log` is SUPERSEDED (`VI.Callees` returns names, not paths).
> **Stage 1 CLOSED**. **Stage 2**: `…CPU_core_v0` 69/69 · `…_queue_v0` 162/162 — **say it exactly:** bit-identical
> for the **first 10,018 frames only**, both **replay**. **THE GAP:** 174 ops, 123 recipes, 235 peers → **zero
> runnable experimental VIs**.

(The 11 UNKNOWN sentence above is superseded by cycle 1's decision 2: the bucket is abolished and those
sites are `ASSUMED_MOTION`, in scope. See `docs/motor-call-site-census.md`.)

## 3. OPEN 38 / 39 / 41 / 42 as they stood (STATUS lines 80–90 as of 2026-09-17)

> 38. 🔴 **Run 3 changed NOTHING** (63 WIRED / 0 FAILED / 3 NO-ROUTE, ExecState 0, nothing saved). Numbers and the
>    open question: **`docs/d1-route-b-plan.md` §11 / §11a** — read that, not a STATUS line.
>    `SR_QUEUE_AUTHORISED = False`, `TEMP_SINK_AUTHORISED = False`. ⚠️ after a `GObject.Move` every terminal of the
>    moved structure reads `is_source` FALSE **including OUTPUT tunnels** — address those rows by INDEX.
> 39. 🔴 `VI.Get Errors` 452 NOT built; its prior-art review stopped it on `docs/d1-build-plan.md:859-860`
>    ("no diagnostic before F1/F2"), opened and not refutable. Plan at `d1-route-b-plan.md` §10, NOT AUTHORISED.
> 41. 🔴 **judgement only — the stall watchdog's liveness test.** Both arms (ANSWERED) REFUSE "false positive"; the
>    remedy (bgrun heartbeat file, drop the CPU delta) is a fleet-wide design change, **not built**. Fifth
>    false-positive class. Evidence + the full quote: `archive/peer/2026-09-17-stall-preexperiment-sleep-{codex,opus}.md`.
> 42. ⚠️ 39 archived reviews still undisposed (`doc_lint` L6 FAIL) and `docs/cycle15-plan.md` has no
>    `## Pre-decided` section (new L8 WARN) — the section the runner's sessions are told to read first.

## 4. The ROUTE B / ledger-gate block (STATUS lines 117–127 as of 2026-09-17)

> ✅ **ROUTE B WORKS AS FAR AS IT GOES** — 63 of 66 WIRED, 0 FAILED, three runs, no new op. But
> 🔴 **THE LEDGER GATE IS NOT WHAT BLOCKS THE SAVE — the correction of 2026-09-17**: even at 0 NO-ROUTE the VI
> is still `ExecState 0`, because `s1q` (the 8 queues) and `s4b` (the 3 sentinel `Equal?`s) are BOTH unexecuted,
> so 1.2 / 1.5 / 1.7 have **unwired conditional terminals** — broken by construction. The undesigned row is
> **which named output terminal types each of the 8 queues** (§2b never says). Until that is decided nothing
> reaches a saved `Track_v6_D1_GPU.vi`, and N1 / F1 / F2 cannot run.
>
> **The three questions that blocked the save are DECIDED and now live in `docs/cycle15-plan.md` → `## Pre-decided`**
> (queue element types · the shift registers moving into 1.2 · the `Z/dZ` reorder · `OpGetErrors_v0` stays unbuilt ·
> session hygiene) — relocated there VERBATIM on 2026-09-17, because that is the section a material session reads.
> A material session APPLIES them and cites the item number; it does not re-ask. **OPEN 32 still stands above all.**
