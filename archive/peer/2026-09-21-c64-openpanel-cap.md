# c64-openpanel-cap

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.4550  in 18 / out 36447 / cache-create 192052 / cache-read 1013454  (473s, 20 turn(s))
- **date:** 2026-09-21 13:19:56
- **outcome:** ANSWERED (474s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# ATTACK this: a failed prediction — `open_panel` on a plain FILE COPY did not return within the 180 s cap

## The failed prediction, verbatim in its consequences

We predicted that `g.open_panel(<path>)` on `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\OpConnectNested_v2.vi`
would return in a few tens of seconds, as the identical call had just done in an earlier run of the same
script. It did not. The measured facts, all from `tools/bench/diag_c64_connect_v2.log` (run 2,
`BGRUN END rc=1 after 329s`, 2026-09-21 12:57):

* `OpConnectNested_v2.vi` at that moment was **a plain byte-for-byte file copy** of
  `OpConnectNested_v1.vi` (md5 `b7a1bb56…`, 14,666 B). **No edit of any kind had been made to it**, and it
  had never been opened or saved by LabVIEW under its new name.
* `g.open_panel()` on it — which calls `VirtualInstrument.OpenFrontPanel(False, 1)` over COM through
  `tools/gscript.py` `_invoke`, whose watchdog cap is **180 s** — **did not return within the cap**. The
  module was therefore POISONED (`gscript._set_poison`): the worker thread was abandoned alive and every
  later COM call raises `COMPoisoned` rather than queueing behind it.
* The abandoned call **did come back, ~66 s later** — roughly **246 s in total** for one `OpenFrontPanel`.
  `gscript._check_poison` then cleared the poison on its own (`thread.is_alive()` False).
* In **run 1** of the same script, ~19 minutes earlier, the **same call on the same file** returned in
  **~60 s**.
* A **LabVIEW restart had just completed** before run 2's batch (`Z_R1`, kernel handle count 30,839 →
  30,687). `tools/lv_restart.py` waits a fixed settling period after the process answers COM.
* Machine: Windows 10, LabVIEW 2026 (26.3.1f1), single COM client, nothing else driving LabVIEW. The op's
  hierarchy includes `vi.lib` members (e.g. `Clear Errors.vi`, `UID to GObject Reference.vi`) and
  erdosmiller scripting VIs.

## The two explanations on the table — NEITHER is established, and both may be wrong

1. **First-load cost.** Opening the panel of this op forces a full load of its subVI hierarchy
   (`vi.lib` + erdosmiller). On this machine that cost sits near the 180 s cap, so the same call lands
   either side of the cap depending on what is already resident.
2. **Restart settling.** LabVIEW answers COM before it has finished its own start-up work, so a panel
   open issued immediately after a restart contends with it; run 1 was issued into an already-warm
   instance.

## What I am about to do, and why your answer matters

The next diagnostic is forbidden from calling `open_panel` at all. But its edit legs go through
`gscript.connect_terminals` / `connect_nested_v1`, and **those wrappers call `ensure_loaded()`, which
calls `open_panel()` internally** (`tools/gscript.py:1268-1337`) — because a scripting EDIT on a target
loaded only through `GetVIReference` is silently declined. Read-only census calls do not need it. So the
plan is: run every file-only and read-only leg first (which incidentally loads much of the op hierarchy),
and only then let the edit legs trigger the internal `open_panel` on scratch copies of a SMALL op VI.

## Attack all of it

1. Give me the **strongest reason the framing above is wrong** — including the possibility that neither
   explanation is right (e.g. the cap measured something that is not "loading" at all: recompile of a copy
   whose compiled code cache does not match its new path, a modal dialog behind the call, cross-apartment
   marshalling, the file being a copy under a name LabVIEW has never seen, a `Run When Opened` flag, the
   `activate=False` path, or the 66-s tail being the call finishing vs. being cancelled).
2. Is "run the read-only legs first to warm the hierarchy" a **real mitigation or a superstition**? Say
   what it would and would not change, and what it could make WORSE.
3. What is the **cheapest discriminating test** between your candidates — one that costs a single batch,
   touches no original file, saves no VI, and does not itself risk a 4-minute stall?
4. What would **falsify** each explanation?
5. Is there a way to reach the "edits actually land" state **without** `OpenFrontPanel` that this project
   has not measured? Our own file records that reading `VI.Block Diagram` (23C) was NOT enough
   (`tools/gscript.py:1273-1295`), and that the experiment which showed that was itself attacked as
   unsound (the diagram ref was not held live at mutation time). Search outside our files before answering.

## Already ruled out — do not spend your answer here

* Not a hung/wedged LabVIEW: the call returned on its own, and the instance served every later call.
* Not our own foreground timeout being too short in the sense of "just raise it": the cap exists because a
  blocking COM call in a single-threaded apartment silently queues every later call behind it.
* Not a second COM client or a human at the keyboard: the run is unattended, one client, rig disassembled
  from LabVIEW's point of view (no instrument is touched).


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled in this cell (correct for a read-only peer). The review is the answer:

---

# 1. The single strongest reason the claim is WRONG

**"In run 1 the same call returned in ~60 s" is a misreading of a timeline offset as a call duration. `open_panel` was never timed, in either run.**

`read_es` prints `t_since_start_s` — the offset from process start (`tools/bench/diag_c64_connect_v2.py:241,244`). The per-call cost is computed as `read_cost_s` (`:242`) and **never printed**. So `+69.2 s` (`diag_c64_connect_v2.log:48`) means "this ExecState read *began* 69.2 s into the run", and it belongs to `exec_state`, not to `open_panel`, which sits one line earlier at `:509` followed by `time.sleep(1.0)` at `:510`.

Those 69.2 s are almost entirely STAGE A plus the pre-batch restart. `lv_restart.py` has a floor of 6 s kill-wait (`:15`) + ≥5 s COM poll (`:20-21`) + 45 s settle (`:29`) + a `lv_gui dialogs` call (`:30`) ≈ **56 s minimum**. Add six hash probes and three git subprocesses and run 1's `open_panel` had at most single-digit seconds.

The run-2 arithmetic pins it near one second. STAGE C's read is the first statement of `stage_c` (`:750`), at `t_since_start_s: 314.1` (`diag_c64_connect_v2.json:99`). Subtract Z_R2's restart (≥56 s) and the 180 s cap: **run 2's `open_panel` began at ≈ t+68–78 s** — the same offset at which run 1 had already finished it.

Same script position, same restart, same settle. Run 1 ≈ 1 s. Run 2 > 180 s. Not 4×. **≥100×** — and a two-order-of-magnitude swing is not what a load-cost or a settling story predicts.

# Both explanations on the table are refuted by this run's own JSON

**First-load cost — dead.** STAGE C read `exec_state(OP2)` in the instance Z_R2 had just restarted, nothing resident: **`read_cost_s: 0.42`**, `exec_state: 1` (`diag_c64_connect_v2.json:97-100`). A VI cannot report ExecState 1 unless its hierarchy is loaded and linked. The cold load of this op — `vi.lib`, erdosmiller and all — is **0.42 s**. Explanation 1 is off by 400×.

**Restart settling — dead.** Both runs ran the identical `lv_restart` at the identical point (log:40, log:109) with the identical 45 s settle, and both reached `open_panel` at ≈ t+68 s. A variable common to both runs cannot explain a difference between them.

# 2. The alternative explanation: the file was deleted and replaced under a path LabVIEW had already loaded

The one thing that differs between the runs is the branch at `diag_c64_connect_v2.py:492-500`. Run 2 found a leftover `OpConnectNested_v2.vi` from run 1 (log:113) and therefore ran, on the fresh instance:

1. `g.close_panel(OP2)` → `vi_ref` → **`GetVIReference(OP2)`** (`gscript.py:1261`, `:253`) — this *loads* v2;
2. `os.remove(OP2)`;
3. `shutil.copyfile(DONOR, OP2)` — **`copyfile` does not preserve mtime** (the script uses `copy2` for scratches at `:762`), so the new file is byte-identical but carries a fresh timestamp;
4. `open_panel(OP2)` → `GetVIReference` → `OpenFrontPanel`.

Run 1 executed none of steps 1–3. This is textbook *"VI has changed on disk since last saved or loaded"*: LabVIEW does not reload a VI already in memory, and opening it after the file is replaced raises a conflict dialog — "you'll get one of the more interesting dialogs that LV has to offer, noting that the diagram saved doesn't match the VI in memory" ([labviewwiki, Loading VIs](https://labviewwiki.org/wiki/Loading_VIs); [NI KB kA00Z000000kEssSAE](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000kEssSAE) — cert error on direct fetch, title and summary from search). VI Server runs in the UI execution system, and a modal dialog blocks it ([NI Idea Exchange](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Make-it-possible-to-dispatch-VIs-dynamically-when-the-UI-thread/idi-p/1579534)).

Two instrument defects make this invisible to you:

- **`_invoke` has no dialog watchdog** (`gscript.py:307-338`) — only `_run` does (`:341-350`) — yet the exception it raises says **"(no dialog)"** (`:333`). That phrase is asserted, never measured.
- **`lv_restart.py` kills LabVIEW at `:13` before censusing dialogs at `:30`.** Every "VERDICT: clear (no modal dialog)" in the log describes the *fresh* instance.

This also predicts your future: v2 now exists on disk, so **every** re-run takes the slow branch.

## The 66-second tail is the restart, not the call returning

`_check_poison` measures `thread.is_alive()` (`gscript.py:142`), which is not call completion. **Z_R2's restart (log:120) ran before the poison-clear (log:125)**, and `_recover_poison`'s own docstring says "the abandoned worker's RPC dies with the server" (`:158-160`). 314.1 − (68 + 180) = 66.1 — the "66 s" *is* the Z_R2 interval.

So your "already ruled out" list is wrong on both halves: nothing observed the call return, and the instance that served every later call is **a different process**. There is no 246 s datum. There is only "≥180 s, once, unbounded above".

# 3. Is the warm-up a real mitigation?

Close to a superstition, and it can cause the failure it is meant to prevent.

- There was never 180 s of loading to front-load — cold load is 0.42 s.
- It does not touch the run-1/run-2 difference at all.
- **It manufactures the hazard**: reading a target before its file is replaced is exactly what run 2 did via `close_panel`'s `GetVIReference`.
- **It will look like it worked.** The scratch names carry `STAMP` (`:165-168`), so they never pre-exist and never take the remove-and-replace branch. A green run would be credited to warming and the real cause buried.
- It burns wall clock inside the same `bgrun` budget while leaving the 180 s cap where it is, so the edit legs run nearer the process deadline.
- Unremarked in the same log: handles **30,705 → 54,669** across STAGE C (log:121, log:138). The `opened 6 == closed 6, live 0` line (log:137) counts Python-side only (`gscript.py:251-259`) and is not evidence about LabVIEW.

# 4. What would falsify each

| explanation | falsifier | status |
|---|---|---|
| first-load cost | a cold `GetVIReference`+`ExecState` on this op costing minutes | **already falsified**, `json:100` = 0.42 s |
| restart settling | arm A1 below stalling on a fresh name in a fresh instance | **already falsified** by run 1 |
| mine (replace-under-a-loaded-VI) | A3 as fast as A1; or A4 stalling like A3 (then replacement alone suffices, no prior load needed); or a clear dialog census taken *during* a stall while A3 is slow | open |

# 5. The cheapest discriminating test — one batch, ~2 min, nothing saved

One freshly restarted instance, `hard_timeout_s=20` on `open_panel` (`gscript.py:314` accepts it), an explicit `time.time()` either side — the number that has never once been recorded — a small op VI, scratch names under a fresh `STAMP`, ordered so the first stall ends the batch:

| arm | sequence | prediction |
|---|---|---|
| A1 | `copy2` → `open_panel` | fast |
| A2 | `copy2` → `exec_state` → `open_panel` | fast |
| A4 | `copy2` → `remove` → `copyfile` → `open_panel` | fast |
| A3 | `copy2` → `exec_state` → `remove` → `copyfile` → `open_panel` | **stalls** |

Plus a `lv_gui -Action dialogs` census from a **separate process** at +5 s and +15 s of every arm, since `_invoke` never looks and the documented failure mode is a dialog.

# 6. Reaching "edits land" without `OpenFrontPanel`

**`VI.Block Diagram Window:Open := True`** is the untested arm. labviewwiki records **"Loads the block diagram into memory: Yes"** *and* it opens a window — which `VI.Block Diagram` (23C) does not. Your own A/B has exactly two arms: no window (23C) → edits don't land; a window (FP) → edits land. The BD window separates "an editor window exists" from "the front panel specifically". The page also says "Remote access allowed: No" — that bars TCP VI Server to another machine; local ActiveX is not remote access, but a refusal would itself be information.

Worth reviving alongside it: hold the 23C reference live *in the same op run as the mutation* (the plan already written at `gscript.py:1291-1295`), now that `Wire.Is Broken?` 6371004 is built, and read `VI.Metrics:Block Diagram Loaded` (292) so the question stops being inferential.

**I found no external source stating that scripting mutations require an open front panel.** Absence is not proof, and I am not claiming your four-row A/B is wrong — but NI's framing is about the block diagram being *in memory*, not about the panel being *open*, so the rule may be over-specified by one window.

---

**Where the evidence does not settle it:** I cannot distinguish "conflict dialog" from "silent relink/recompile of a path whose in-memory image no longer matches disk" — both are consequences of the same replace-under-a-loaded-VI, both predict A3 stalling, and only the dialog census during the stall separates them. That is why the census is in the test rather than optional.

**Sources:** [Loading VIs — labviewwiki](https://labviewwiki.org/wiki/Loading_VIs) · [VI Has Changed on Disk — NI](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000kEssSAE) · [reload a vi from disk — NI Forums](https://forums.ni.com/t5/LabVIEW/reload-a-vi-from-disk/td-p/543655) · [Block Diagram Window.Open — labviewwiki](https://labviewwiki.org/wiki/VI_class/Block_Diagram_Window.Open_property) · [Metrics.Block Diagram Loaded — labviewwiki](https://labviewwiki.org/wiki/VI_class/Metrics.Block_Diagram_Loaded_property) · [UI thread blocks VI Server dispatch — NI Idea Exchange](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Make-it-possible-to-dispatch-VIs-dynamically-when-the-UI-thread/idi-p/1579534)

## Sources

(extract from answer)

## What was done with it

Disposed in full by cycle 64 material #3 (2026-09-21 13:2x), finding by finding. The review is
**ANSWERED** (claude / role hypothesis, opus effort max, 474 s; log `tools/bench/peer_c64_openpanel_cap.log`,
`BGRUN END rc=0 after 475s`; task `tools/bench/peer_c64_openpanel_cap_task.md`).

**§1 — ACCEPTED, and it kills my premise, not just my conclusion.** `open_panel` was **never timed, in
either run**: `+69.2 s` in `diag_c64_connect_v2.log:48` is `t_since_start_s` (the offset at which an
`ExecState` read BEGAN), not a call duration; `read_cost_s` is computed and never printed. So **"run 1's
identical call took ~60 s" is withdrawn** — it was my own misreading, carried into STATUS.md's cycle-64
material-#2 release note and into this cycle's brief. Likewise **there is no 246 s datum**: the "66 s tail"
is Z_R2's restart interval (314.1 − 180 − ≈68), and `_check_poison` measures `thread.is_alive()`, which is
not call completion. What is actually on the record is **"≥180 s, once, unbounded above"**.

**§1b — ACCEPTED: both explanations in my task are refuted by our own JSON.** First-load cost is off by
~400× (`diag_c64_connect_v2.json:97-100`: a cold `exec_state` on that same op in a just-restarted instance
cost **0.42 s** and returned 1, which cannot happen unless the hierarchy is loaded and linked). Restart
settling is common to both runs and so cannot explain a difference between them.

**§2 — ACCEPTED as the live explanation, and this run is built so it cannot recur.** The one branch run 2
took and run 1 did not was `close_panel(OP2)` (which loads the file through `GetVIReference`) → `os.remove`
→ `shutil.copyfile` → `open_panel` — i.e. *replace a file under a path LabVIEW has already loaded*, the
documented "VI has changed on disk" case, whose dialog blocks VI Server because it runs in the UI execution
system. **Acted on:** `tools/bench/diag_c64_readerfree.py` creates every scratch under a fresh `STAMP` with
`shutil.copy2` and **never removes-and-replaces a path it has loaded**; the one file it deletes
(`OpConnectNested_v2.vi`, judgement's decision) is deleted and **never re-created**, with the deletion
retried after the pre-batch restart if the first attempt is refused. The review's prediction that "v2 now
exists on disk, so every re-run takes the slow branch" is therefore closed by the deletion rather than
worked around.

**§3 — ACCEPTED; the claim was withdrawn from the diagnostic before it ran.** The "run the read-only legs
first to warm the hierarchy" sentence is now recorded in the script as an ordering **with no mitigating
value claimed** (there was never 180 s of loading to front-load), and the script does not credit a green
run to it. Not acted on beyond that: the 180 s `_invoke` cap is left where it is (changing it is an edit to
`tools/gscript.py`, forbidden in this dispatch). ⚠️ Its unremarked fact is confirmed and carried forward:
handles 30,705 → **54,669** across dispatch #2, and `opened == closed, live 0` counts Python-side refs only
and is not evidence about LabVIEW — this run reports kernel handles before, after the restart and after.

**§4 — ACCEPTED, recorded.** Two of the three rows were already falsified; only the replace-under-a-loaded-VI
row is open.

**§5 — NOT RUN, and deliberately: it is a new four-arm batch plus a separate-process dialog census, i.e. a
route decision, which a material session does not take (CLAUDE.md §3).** It is reported to judgement as the
one open question of this dispatch. What WAS adopted from it at zero cost: every `ExecState` read in
`diag_c64_readerfree.py` records `read_cost_s`, and every wrapper call records an explicit `call_cost_s`
around it — so this cycle stops inferring durations from offsets, which is the mistake §1 identified.

**§6 — RECORDED, NOT ACTED ON.** `VI.Block Diagram Window:Open := True` as the untested middle arm between
`VI.Block Diagram` (23C, no window, edits do not land) and `OpenFrontPanel` (window, edits land), plus
holding the 23C reference live inside the mutating op run and reading `VI.Metrics:Block Diagram Loaded`
(292). Both are new verbs/ops and are forbidden in this dispatch. The reviewer's own caveat is carried with
it: no external source says scripting mutations require an open FRONT PANEL, so our rule may be
over-specified by one window — an inference, not a measurement, and it is not being treated as settled in
either direction.

**Where it does not settle:** the reviewer states plainly that a conflict dialog and a silent
relink/recompile are not separated by anything measured so far, and only a dialog census taken *during* a
stall separates them. Nothing in this cycle claims otherwise.

(Claude fills in)
