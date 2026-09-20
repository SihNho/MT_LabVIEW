---
type: narrative
status: historical
date: 2026-08-31
tags: [archive]
---

# Current Status — read this first

**Last updated: 2026-08-30 (ingest/lint for a fresh session).** The "pick up here" page for resuming
this work in a fresh session/chat/LLM. It answers *what is true now and what to do next*, nothing
else — session narrative belongs in [archive/](archive/) (latest:
`archive/2026-08-29-oploopkernel-build-narrative.md`,
`archive/2026-08-29-status-sweep-opexitloop-opwireind.md`), technique in the docs below. Read
[CLAUDE.md](CLAUDE.md) before touching LabVIEW; its hard rules (never modify an original VI;
**never operate the piezo stage or the motor**; LabVIEW is shared with real experiments) outrank
anything here.

Where detail lives, so a cold start stays cheap:
**the `labview-automation` skill** = *all* LabVIEW technique — VI Scripting, the ActiveX pipeline, GUI
control, library choices (invoke it before any LabVIEW work) ·
[ARCHITECTURE.md](ARCHITECTURE.md) = the rig's software, the performance model, the backend plan ·
[MAIN_VI_MAP.md](MAIN_VI_MAP.md) = **the call graph, the main VI's loop/case skeleton, and what it
means** (built 2026-08-30; read this before deciding direction) ·
[PLAN_kernel_parallel.md](PLAN_kernel_parallel.md) = the kernel thread's working plan ·
[LEARNING.md](LEARNING.md) = the user's own teaching write-up ·
[REFERENCES.md](REFERENCES.md) = citations · [AGENTS.md](AGENTS.md) = the brief peer agents read ·
[archive/](archive/) = history, **not read by default** (except `archive/peer/`, checked before
asking a peer anything).

## 🚨 INCIDENT 2026-08-30 — the experiment hierarchy no longer opens in LabVIEW 2019

The user runs **harness/scripting work in LabVIEW 2026** and **real experiments in LabVIEW 2019**
(both 64-bit, both installed on this machine). Today LabVIEW 2019 refused to run the experiment.
Two separate, independently proven causes:

### 1. 34 VIs have been re-saved in LabVIEW 2026 format — a one-way upgrade

Every `.vi` carries its saving version as a four-byte value: **`19 00 80 00` = LabVIEW 2019**,
**`26 00 80 00` = LabVIEW 2026**. Read offline, no LabVIEW involved. Result:

| when | what | count |
|---|---|---|
| **2026-08-21 21:04** | `background VIs` — the whole tracking core (both kernels, calibration, bandpass, plotting) | **30** |
| 2026-08-24 16:20 | `check N bead pos v3-kimlab.vi`, `get buff image-lost frames.vi` | 2 |
| 2026-08-24 20:47 | `Min_Track N beads V6_ParallelLoop.vi` (Claude's working copy — expected) | 1 |
| **2026-08-27 15:06** | **the ORIGINAL main VI `Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi`** | 1 |

`Min_Track N beads 4.3 / 4.4 / 4.6` and the older sub-VIs are **still 2019 format**.

**Two honest observations.** The original main VI's upgrade (08-27 15:06) falls inside the Claude
sessions; mtime cannot prove who saved it, and this is exactly the accident rule 1 exists to
prevent. But the *functional* breakage is the **08-21 batch of 30**, which predates this project by
three days — restoring only the main VI would not make the experiment run.

### 2. ~~LabVIEW 2026 has no NI Vision~~ — **RETRACTED, this was wrong**

Claude claimed LabVIEW 2026 had no Vision installed, on the evidence that `LabVIEW 2026\vi.lib`
contains no `vision` directory and no `IMAQdx.llb` / `Image Controls.llb`, while LabVIEW 2019's
`vi.lib` has all of them. The user then reported the hierarchy **works fine in 2026**, and the claim
collapsed.

**Vision IS installed for 2026.** Since **LabVIEW 2022 Q3** NI installs drivers and toolkits into a
version-independent tree instead of each LabVIEW's own folder:

```
C:\Program Files\NI\LVAddons\niimaqdx\1\vi.lib\vision\driver\IMAQdx.llb
C:\Program Files\NI\LVAddons\nivisioncommon\1\vi.lib\vision\Image Controls.llb
```

`LVAddons` here also carries `nivision`, `niimaq`, `nivisa`, `nidaqmx`, `vasexpress` and more.
`<vilib>` is a **virtual overlay**: at startup LabVIEW reads each add-on's `lvaddoninfo.json` and
aggregates its `vi.lib` subtree with the LabVIEW installation's own, so
`<vilib>:\vision\driver\IMAQdx.llb\...` resolves even though nothing of the sort exists under
`LabVIEW 2026\`. **A directory-existence check is therefore not a valid test of whether a driver is
installed.** The deterministic test is `nipkg.exe list-installed | Select-String "imaq|vision"`, or
inspecting `LVAddons` itself.
(Peer review archived: `archive/peer/2026-08-30-...-vilib-vision-detection-failed-prediction.md`.)

**Consequences of the retraction:** no NI Package Manager install is needed before converting; and
the `.llb`-read-as-`.dll` symptom the user described has **no confirmed explanation** — the Vision
story offered for it is withdrawn. PI's driver is present for both versions, so it is not that
either.

### A documented mechanism that may explain the format upgrades

NI's subVI-resolution documentation describes this: when a stored path no longer matches (an LLB
relocated, unpacked, or renamed), LabVIEW searches by VI name across memory, the caller's directory
and the search paths; on finding it, **it relinks in memory and marks the VI dirty, prompting to
save on exit.** So merely *opening* this hierarchy in 2026 can leave every VI dirty, and a single
"Save" answered on exit rewrites the whole hierarchy in 2026 format. That fits both the **08-21
batch of 30** (the day PI's driver was installed into 2026's `instr.lib`) and the **08-27** save of
the original main VI, without anyone deliberately choosing to save.

### ✅ CLOSED — the rig moves to LabVIEW 2026, so there is nothing to recover

**User decision, 2026-08-31: *"앞으로는 그냥 2026 버전 이용할 예정."*** Everything — harness work and
experiments — now targets LabVIEW 2026, which the hierarchy already opens and runs in.

That dissolves the whole problem rather than solving it. The 34 files being in 2026 format is now
**the correct state, not damage**. No `Save for Previous Version` conversion, no NI Package Manager
install, no backup hunt. Recorded here only so a future session does not "helpfully" try to
downgrade anything.

**What changes for this project**

- **"Runs in LabVIEW 2019" is NOT an acceptance criterion.** An earlier note in this file said the
  opposite; it is withdrawn. The parallel-kernel deliverable targets 2026, the version it is being
  built in.
- Rule 1 (never modify or save an original) is **unaffected** — it protects the originals' content,
  which was never what the version story was about.
- Still worth knowing: opening an old hierarchy in a newer LabVIEW relinks subVIs, marks them dirty
  and prompts to save on exit. Harmless now, but it is why a VI that was only *looked at* can come
  back modified — so keep answering **No** to that prompt on originals.

**The user's own account of the trigger:** power was pulled from all the motors before running the
harness, to make sure coding could not break the machine. That fits the *hardware* half of today —
an unplug/replug cycle is exactly how a serial port ends up held or renumbered, which is what
stopped PiMikroMove. It does not explain the format upgrades; the relink-on-open mechanism above
does, and the two happened to surface together.

## LabVIEW execution lock

Per `CLAUDE.md` §3. `released` means LabVIEW is **not** authorized to be touched — wait for the user
to say so explicitly. Never infer "the machine looks free" from process or window state.

```yaml
labview-lock:
  status: released
  owner:
  since: 2026-08-31 (user: "우선 작동 정지")
  purpose:
```

**Handed back mid-build, 2026-08-30.** Everything is saved to disk; nothing is pending in memory.
`OpWireCtl_v0.vi` (10,672 B) is intentionally **broken (ExecState 0)** — that is its correct
in-progress state, not damage. Its two remaining GUI acts are specified below.

Windows Claude left open, none of them originals, all safe for the user to close without saving:
`READONLY_fourfold_COPY.vi` (a disposable copy of the four-fold kernel — deletable),
`OpWireCtl_v0.vi`, `OpCreatePropNode_v0.vi`. LabVIEW was restarted twice during this session, so
older zombie scratch windows are already gone.

**Hardware note:** the user physically unplugged every instrument on 2026-08-27, so the rig cannot be
damaged. Rule 1b applies again the moment power returns, and with devices absent any VI that opens a
hardware session will **fail or hang on device initialisation**, possibly behind a modal dialog — so
the run-button trap (broken-arrow and Run are the same pixels) still matters near the original VI.

## Two levels of verification — do not confuse them

Added 2026-08-30 after the user caught an over-claim (*"데이터 넣어보지 않았는데 어떻게 확인한
거야?"*). Everything this project has verified so far is **structural**. Say which level you mean,
every time.

| level | what it proves | how it is checked here | status |
|---|---|---|---|
| **Structural** | the generated diagram is *legal G*: objects exist with the right owners, wires are type-legal, no required input is unwired | `OpReport_v3` counts/owners by UID + `ExecState == 1` (the same check that makes the run arrow solid) | ✅ done for every op |
| **Functional** | the generated code *computes the right thing*: data reaches the right iteration, parallel results land at the right index, outputs match the old kernel | running the VI with real inputs and comparing numbers | ❌ **never done — no data has ever flowed** |

`ExecState == 1` is a compiler verdict, not a correctness verdict. The functional plan is thread 5
(offline fixture): synthetic smoke first (zero/dummy image + cal clusters → does it run clean and
are the output array lengths right?), then the real acceptance test — **same inputs through the new
parallel kernel and the existing four-fold kernel, X/Y/Z compared numerically.** The drop-in swap
into the main VI waits for that, and for user confirmation.

## Open semantic questions — this is now the priority

User direction, 2026-08-30: the implementation side largely works, so **effort belongs on semantic
analysis**, and `CLAUDE.md` §1a now forbids changing the original's *computation*. Under that rule
the following are unresolved and outrank further construction.

**Q1 — ANSWERED (structurally) 2026-08-30: the substitution preserves the analysis model.**
The criterion, from the user: *"이미지를 분석해서 수치화하는 모델과 그 연산 방법 및 결과가 바뀌면
안된다"* — wiring and scheduling may change; the image-analysis maths and its numbers may not.
Three independent structural findings, all scripted:

1. **Identical analysis subVI sets.** A byte scan shows `Track 1` and `Track 2` call *exactly the
   same* ten VIs — `tracking-calculate radial profile-openv2`, `Tracking-prep I of r`,
   `Tracking-fit prepped I of r to cal`, `tracking-calculate phase in neighborhood`,
   `tracking- quadratic fit to phase nghbrd`, `tracking-average x,y in cross`,
   `tracking-find avg profile center`, `tracking-prep avgx,y profiles`, `rect coord from center`,
   `Omars IMAQ ImageToArray`. No pair-specific or "packed transform" VI exists in `Track 2`.
2. **The analysis chain is instantiated PER BEAD, not shared.** Counting instances by probing each
   SubVI node for a distinctive output: `Track 1` (1 bead) has **1×** `radial intensity profile`
   and **1×** `prepped I(r)`; `Track 2` (2 beads) has **4× each** — i.e. its own full copy of the
   analysis chain per bead, duplicated again across case frames (it has 3 CaseStructures to
   `Track 1`'s 1, which is what inflates node counts to ~4×, not a different algorithm).
3. This **contradicts the old speculation** in `PLAN_kernel_parallel.md` that `Track 2` packs two
   real bead profiles into one shared complex transform — that note was explicitly marked
   untraced, and no shared-transform node exists. What `Track 2` plausibly shares is the
   image-to-array conversion, which is plumbing on the *same* image, not model.

**Conclusion:** replacing `Track 2` with repeated `Track 1` calls re-arranges how beads are grouped
and scheduled while leaving the per-bead image-analysis model and its inputs identical, which is
exactly what §1a permits. The 2026-08-25 decision stands. **This is structural evidence, not a
numerical proof** — the offline-fixture comparison (same inputs → same X/Y/Z) remains the
acceptance test.

*(superseded framing kept for context)* **Does replacing `Track 2 of N` with repeated
`Track 1 of N` change the maths?**
The 2026-08-25 decision was to build the parallel kernel around **`Track 1 of N bds
xyz-kernel-reentrant.vi` only**, on the grounds that `Track 2 of N …-v2.vi` "entangles two beads'
data" and is not a safe atomic unit for parallelism. That is a sound *parallelism* argument, but
§1a now asks a different question: **production today routes beads through both** (the four-fold
kernel has 7 SubVI nodes drawn from exactly those 2 VIs), and `Track 2` is believed to pack two
beads into a single shared complex transform. If that packing is only an efficiency trick yielding
the same per-bead numbers, the substitution is equivalence-preserving and the decision stands. If it
processes the pair differently in any way that reaches the output, **the swap silently changes the
computation and violates §1a.**

**Exposure MEASURED 2026-08-30 — it is not marginal.** Each of the four-fold kernel's 7 SubVI nodes
was classified by probing which outputs it exposes (`X pos 2` resolves ⇒ Track 2; only `X pos 1`
⇒ Track 1), fully scripted:

| node | position | kernel |
|---|---|---|
| 1, 3, and the one at (4001,301) | — | **`Track 1` — 3 nodes** |
| 2, 4, 5, 6 | — | **`Track 2` — 4 nodes** |

Consistent with the expected shape: the **main path pairs beads through `Track 2`**, with `Track 1`
appearing in the remainder cases (`4 pack remainder` is a pane input). **So in production most beads
are tracked by the paired kernel**, and the current plan replaces every one of them with repeated
single-bead calls. That is a real change of decomposition and cannot be waved through.

Next, in order: ① **read `Track 2 of N …-v2.vi`'s diagram** (safe copy in `background VIs_COPY\`,
and `claudeDev` copies are freely modifiable) and determine whether each bead's result is
mathematically independent of its partner's — if the pairing is only a shared FFT for speed, the
substitution is equivalent and the 2026-08-25 decision stands; ② if it is not obviously equivalent,
put the choice to the user, since preserving the computation may mean keeping `Track 2` and
parallelising over *packs* rather than beads; ③ the offline-fixture numeric comparison settles it
empirically, but only at the very end.

**Q2 — Do the calibration and tracking paths share subVIs?** (user's own caveat, 2026-08-30) The
calibration analysis runs through subVIs that likely overlap with the tracking ones. Our work does
not touch the calibration path, but map the shared subVIs before ever modifying it.

**Q3 — Re-verify the four-fold's OUTPUT pane.** `Wire Inputs` cannot see outputs, so the three
outputs are still taken on trust from an older note; confirm with a `Get Outputs`-based probe
before finalising the connector pane.

## What works right now

**The build loop is scripted. No mouse.** `gscript.loop_kernel()` builds a parallel loop with the
kernel wired inside it in about a second, reproducibly, verified structurally. Screenshots are no
longer part of any routine step.

> **CLI caveat:** `py tools\gscript.py kernel <target.vi>` still routes to the older
> `build_kernel()`, which places an **unwired** loop + kernel (`for_loop` + `drop_subvi`). It is
> superseded by `loop_kernel()` and kept only for the containment regression. Do not read its
> output as "the kernel is built".

- **VI Scripting**, on `erdosmiller/lv-scripting` (MIT, via VIPM, 84 API VIs), verified on LabVIEW
  2026. `Create For Loop.vi` sets **`Number of Static Parallel Instances`**, which is the capability
  nothing else could reach and the reason the whole approach works.
- **ActiveX drives everything.** Front-panel controls are set *by label* from Python, the VI is run,
  results are read back (`tools/kb_com.py`, `tools/gscript.py`). This is why every Op VI takes its
  arguments as **front-panel controls, never diagram constants** — a constant is unreachable from
  outside.
- **Structure is readable back.** `OpReport_v3` lists every object of a class with `Class Name`,
  `UID`, `Position` and its owner's class, at 0.06 s a call. Verification is data, not pixels.
- **Errors are readable back (2026-08-29).** The three editing ops (`OpWire_v1`, `OpExitLoop_v0`,
  `OpWireInd_v0`) carry `error out` indicators branched onto their error chains; `gscript.wire()`,
  `exit_loop()` and `wire_indicators()` read `_err()` after every run and raise the REAL error
  (e.g. `error 5001: Get Outputs.vi`) instead of silently no-opping. End-to-end verified with
  deliberate bad names on all three.
- **Modal-dialog deadlock is a two-call scripted recovery**: `lv_gui.ps1 -Action dialogs` finds the
  blocking dialog by window enabled-state, `-Action dismiss` closes it. And it is automatic:
  `gscript._run`/`_invoke` watchdogs poll for modal dialogs, screenshot the blocker, dismiss it and
  raise. Session-level backstop: `tools/lv_stallcheck.ps1` runs from a PostToolUse hook after every
  shell command, flags stalled python COM clients, and never kills anything.

## Op-VI fleet

Architecture directed by the user: **frozen primitive Op VIs in G, composed by Claude-written command
scripts.** Each does one thing, takes its arguments as front-panel controls, and never needs diagram
surgery again. Technique and caveats live in the `labview-automation` skill; the table is the index.

| Op VI | state | what it does |
|---|---|---|
| `OpReport_v3.vi` | ✅ **the reporter** | Per object: class, `UID`, `Position`, owner's class, `# of Refs`. No input can make it raise a dialog. Supersedes `v0`–`v2` (deletable). |
| `OpForLoop_v0.vi` | ⚠ **partly a no-op** | Creates a For Loop at a `location` and sets static parallel instances (both real). **Its tunnel creation has never worked** — `Create For Loop`'s `Inputs` output arrives empty at runtime, so no data tunnel is ever made. The "+1 Tunnel" that hid this for days was the loop's **`N` terminal**, which reports as class `Tunnel` (`P` adds another). Superseded by `OpLoopKernel_v0`; use it only for a bare parallel loop. |
| `OpSubVI_v1.vi` | ✅ 0.1 s | Drops a subVI onto a chosen **Diagram** (index from the reporter). Does NOT expose Create SubVI's tunnel-wiring inputs — that is what `OpLoopKernel_v0` adds. |
| `OpWire_v1.vi` | ✅ **the wirer** | Node→node wire by terminal name. Needs the target's panel OPEN (`gscript.open_panel`); save before `close_panel`. Bad names now raise readable 5001s. |
| `OpExitLoop_v0.vi` | ✅ **the tunnel-maker** | Auto-indexed output tunnels for named node outputs (erdosmiller `Exit For Loop.vi`). 3 tunnels + 3 wires in 0.26 s; default tunnel type is already auto-indexed. Wrapper: `gscript.exit_loop()`. |
| `OpMoveByLabel_v0.vi` | ✅ **the donor-copier** | Copies ANY GObject by **label** between VIs via `GObject.Move(Duplicate)` and the fixed-static-ref **substitution protocol** (`gscript.move_by_label`/`copy_into`; `ensure_move_files_pristine()` guards both Test files). Paste lands at (0,75) top-level. First-match-by-label. |
| `OpDeleteByLabel_v0.vi` | ✅ **the deleter** | Removes an object by label (`Generic:Delete` — the class matters: `Delete` is on `Generic`, not `GObject`). Wrapper `gscript.delete_by_label` cleans broken wires and saves. |
| `OpWireInd_v0.vi` | ✅ **the indicator-wirer** (2026-08-29) | Branches a node's outputs onto EXISTING indicators by label (erdosmiller `Wire Indicators.vi`). Source terminal MUST already be wired; NO new Wire object is created (count checks useless — verify by ExecState/`_err`). Wrapper: `gscript.wire_indicators()`. |
| `OpLoopKernel_v0.vi` | ✅ **the loop+kernel builder** (2026-08-29) | ONE run = parallel For Loop + subVI dropped inside + named FP controls wired to named subVI inputs through AUTO-CREATED tunnels (arrays auto-indexed). Fused `Create For Loop`→`Create SubVI`; CS's `Inputs` fed from `Get Controls` directly (CFL's own Inputs output is empty at runtime — bypassed). `Inputs Indexing?` control is dead. Wrapper: `gscript.loop_kernel()`. 111 KB. |
| `OpNode_v0.vi` | ❌ abandoned | Generic node creator, error 1054. Superseded by the donor pattern — DELETABLE. |
| [`tools/gscript.py`](tools/gscript.py) | ✅ **the runner** | report/count/find_at/uids/new_since/**loop_kernel**/for_loop/drop_subvi/wire/exit_loop/wire_indicators/copy_into/move_by_label/delete_by_label/remove_bad_wires/loop_diagram/open_panel/close_panel/exec_state/save. `save()` refuses paths outside `claudeDev` and refuses a BROKEN VI. |
| [`tools/op_selftest.py`](tools/op_selftest.py) | ✅ **the fault-injector** | Feeds every wrapper a deliberately bad input and asserts the failure is READABLE, not silent. Last run 7 PASS / 2 WARN / 0 FAIL. Run it after any op or wrapper change. |

**In this table ✅ means *structurally* verified** (the op produces legal G, checked by counts and
`ExecState`). None of it means the generated code has been run with data — see the two-levels
section above.

### Standing decisions the fleet is built on

- **Copy from a donor VI; do not generate nodes.** `New VI Object` only creates the styles in its
  ring (For/While Loop, Case). NI's forums say to copy everything else from a donor; brute-forcing
  style codes risks crashing LabVIEW. That is why OpMoveByLabel/OpDeleteByLabel exist.
- **Save the target.** Ops edit LabVIEW's in-memory copy; nothing reaches disk until
  `gscript.save(target)`. Verified the hard way — a whole assembly evaporated on restart.
- **Every node's `error out` must go somewhere.** An unhandled error becomes a modal dialog that
  blocks all COM. `Ignore Errors inside Node` does NOT suppress the dialog; only a wired chain does.
- **An op cannot edit its own .vi while running** — silent no-op. File-copy the op and drive the
  copy (guard built into `wire_indicators`).
- **Containment is proven and encoded**: a loop's body Diagram sits at exactly `loop_pos + (10,22)`
  (21× margin measured); `gscript.loop_diagram()` offset-matches with a ≥4× margin check, and both
  `build_kernel` and `loop_kernel` assert the placed subVI's owner is a structure `Diagram`.
  Identity-level proof if ever needed: `archive/peer/2026-08-28-containment-proof.md`.
- **Claim the level of verification you actually reached** (see the table at the top). Structural
  checks (`ExecState`, counts by class, UID diffs) never license the word "works" or "proven" about
  behaviour — only about legality.

## Machine / file state

- The original VI's state is the **user's to manage — do not track it** (2026-08-28: *"원본은 내가
  알아서 셋팅할테니 패스나 다른것 건들지 말고"*). No checksum baseline, no re-baseline escalation.
  Rule 1 unchanged and absolute. On any Close-All dialog listing an original → **Cancel**.
- In `user.lib\claudeDev` (disk-verified 2026-08-30): the Op-VI fleet, all saved —
  `OpLoopKernel_v0` 111,243 B · `OpExitLoop_v0` 11,677 · `OpWireInd_v0` 11,388 · `OpWire_v1` 11,149
  · `OpReport_v3` 10,235 · `OpMoveByLabel_v0` 9,736 · `OpSubVI_v1` 9,594 · `OpDeleteByLabel_v0`
  9,558 · `OpForLoop_v0` 110,296. No `SCRATCH*` files remain.
  Also: `KernelBuilder_v1.vi` (superseded monolithic driver, kept as parts donor);
  `PARALLEL_build_testA.vi` — **NOT "the P=4 evidence" it was long labelled**: it has N/P terminals
  but **no data tunnels**, which is how OpForLoop's silent no-op stayed hidden; it evidences the
  parallel-instances setting only. `Track N beads PARALLEL over-kernel v2_KERNEL.vi`,
  `KERNEL_build_A.vi`, `KERNEL_asm2.vi` (pristine kernel copies, MD5
  `f6c3197a4f750684ae6d2eb4d8b59c9d`); `background VIs_COPY\`; `NIScriptingExamples\`;
  `VISnippet_EVAL\`.
- **CAUTION:** `…over-kernel v1.vi` was saved dirty by the 08-28 Save All (62,138 → 70,933 B). For
  a clean kernel build use `v2_KERNEL.vi` or re-copy from `background VIs\`.
- **Provenance, settled by the user 2026-08-30:** *nothing* in this project's tree was placed there
  by the user — **every file here was copied or created by a Claude session**, and the same goes for
  `Min_Track N beads V6_ParallelLoop.vi` in `2. Tracking\` (471,337 B, 2026-08-24), which an early
  Claude session cloned from the 4.5 original. **It is therefore a working copy and may be modified
  freely** — the useful thing it buys is a main VI that can be opened, traced and experimented on in
  the editor without ever touching the original. The project directory itself holds no `.vi` files.
  Rule 1 continues to protect the true originals in `2. Tracking\` and `zz_LabView VI\background
  VIs\`; when provenance is unclear, ask rather than infer it from timestamps.
- Loose ends: `OpNode_v0` (deletable), `OP_test1.vi`, `PARALLEL_smoke.vi` (old canvases, deletable).
- Re-check what is open with `& .\tools\lv_gui.ps1 -Action windows` before assuming anything.
- **This session's shell sandboxes filesystem writes** outside the project: anything the user's own
  processes must see (global npm installs, `~/.gemini/...` config files) must be written by the
  user — a write from this shell lands in an overlay only this session sees while looking
  successful. When a config edit for an external tool has no effect, suspect the overlay FIRST and
  hand the content to the user to paste.

## Active threads

1. **Scripting toolchain** — working, error-visible, fleet complete for current needs (the fused
   loop+kernel op landed 2026-08-29). Backlog only: error chains for the two `op_selftest` WARNs.
2. **Kernel parallelization** — the *builder* is done and structurally verified
   (`gscript.loop_kernel`); the *kernel* is not built. Remaining (= "Do this next" 4a–f):
   starting-x/y feed, the three source-less inputs, output tunnels, connector pane, save, then
   **functional verification**, then the drop-in swap (user confirmation before the main VI is
   touched). See [PLAN_kernel_parallel.md](PLAN_kernel_parallel.md).
3. **Main VI Loop-2 split** — **the experiment-phase regions ARE now located** (2026-08-30): see
   [MAIN_VI_MAP.md](MAIN_VI_MAP.md) §3b for the init frame, the event/cycle-schedule region, the
   motor clamping state machine, and the **single** tracking-kernel call site. Still open: which of
   the 3 While loops owns each region.
4. **Performance / backends** — model and CPU+GPU decision in [ARCHITECTURE.md](ARCHITECTURE.md)
   §10. Next action there is a **measurement, not a build** (item 5).
5. **Offline test fixture** — the user will supply `.cal`/`.tra`/images after a future experiment;
   becomes the regression baseline for any rewrite.
6. **Peer agents — connected and verified.** Dispatch only through
   [`tools/peer.ps1`](tools/peer.ps1): `& .\tools\peer.ps1 -Agent codex|gemini -Slug <name> -Task
   "…"` (read-only enforced, hard timeout, ANSWERED/TIMEOUT/QUOTA/ERROR classification, quota
   verdicts confirmed by liveness probe, auto-archive to `archive/peer/`). **codex reads files
   (project-scoped sandbox), agy is web-only** (`read_file` removed — only the whole-machine form
   ever worked; both documented narrowings tested and denied). Only
   `~/.gemini/antigravity-cli/settings.json` matters for agy, and Claude's shell cannot write it
   (overlay) — the user edits it by hand. Prompts travel via stdin, never argv; the brief is
   inlined (agy does not scan AGENTS.md); the binary is `agy` at `%LOCALAPPDATA%\agy\bin`.
   Human quota check for codex: TUI `/status` (headless has none — the liveness probe is the
   automated check).

## Do this next

1. ~~OpWire error chain~~ / 2. ~~containment proof~~ / 3. ~~donor-copy op~~ — **DONE 2026-08-28.**
   3b. ~~Readable error indicators fleet-wide~~ — **DONE 2026-08-29** (see "What works right now").
4. **Finish the kernel body.** The builder now exists; the kernel does not yet.

   **DONE — `OpLoopKernel_v0.vi` (111,243 B, ExecState 1, cold-verified).** Wrapper:
   `gscript.loop_kernel(target, location, control_names, kernel_path, input_names, parallel)`.
   ONE call ⇒ parallel For Loop at `location` + kernel subVI dropped **inside** it (owner=Diagram)
   + each `control_names[i]` front-panel control wired to `input_names[i]` on the kernel through a
   tunnel LabVIEW **auto-creates on the border crossing** (auto-indexed for arrays, plain for
   scalars). Last regression: 3 inputs (`Array of cal clusters`→`Calibration cluster 1`,
   `Image In`→`Image`, `cross size`→`cross size`), P=4, on a fresh `v2_KERNEL` copy, ~1 s, target
   **ExecState 1 afterwards** = every wire type-legal. Build story + the wrong turns:
   `archive/2026-08-29-oploopkernel-build-narrative.md`.

   **⚠ Verification level: STRUCTURAL only. No data has ever flowed through a generated loop.**
   See "Two levels of verification" above before writing the word "verified" about this.

   ### The wiring map — MEASURED 2026-08-30, supersedes the byte-extracted list

   Earlier notes listed the bead kernel's inputs from byte extraction and were **wrong**
   (`cross arm width` does not exist). These pairs were established by *wiring them for real* on
   scratch copies — a 5001 from `Wire Inputs.vi` means the name is not on the kernel's connector
   pane, a clean wire + `ExecState 1` means it is:

   | four-fold control | → | kernel input | result |
   |---|---|---|---|
   | `Array of cal clusters` | → | `Calibration cluster 1` | ✅ wired, auto-indexed |
   | `Image In` | → | `Image` | ✅ wired, broadcast (scalar) |
   | `cross size` | → | `cross size` | ✅ wired, broadcast |
   | `Bead is good? array in` | → | `Bead 1 is good? in` | ✅ wired, auto-indexed |
   | (needs Decimate) | → | `starting x 1` | ✅ **on the pane** (proved by wiring `cross size` to it) |
   | (needs Decimate) | → | `starting y 1` | ✅ **on the pane** |
   | `Cosine bandpass` | → | `cosine bandpass` | ❌ **5001 — NOT on the kernel's connector pane** |
   | `# slices in stack` | → | `# slices in stack` | ❌ **5001 — NOT on the pane** |

   ### THE CALIBRATION CLUSTER — the correction that matters (2026-08-30)

   **A flat reading of `ExportVIStrings` is a trap: it prints nested CLUSTER FIELDS as if they were
   sibling front-panel controls.** Reading it flat, Claude declared `cosine bandpass`,
   `# slices in stack`, `z step` and `forget radius` "unreachable leftovers" that would "keep the
   kernel's defaults". The user challenged this from domain knowledge — they set **forget radius
   and bandpass during calibration analysis**, so those cannot be irrelevant to tracking. They were
   right, and the nesting proves it:

   ```
   Array of cal clusters        (four-fold pane)   Calibration cluster 1     (bead-kernel pane)
     └ cluster                                       ├ forget radius
        ├ # slices in stack                          ├ z step
        ├ r shifted cal real                         ├ cosine bandpass
        ├ r-shifted corkscrew cal                    ├ 2D array of prepped…
        ├ r shifted cal ampl                         ├ 2D array of complex…
        ├ Cosine bandpass                            ├ Real portion of…
        └ obj step between slices                    └ # slices in stack
   ```

   **Every "missing" parameter is a FIELD of the calibration cluster**, which *is* on both panes and
   which the parallel loop already auto-indexes per bead. So they arrive **fully populated, per
   bead, for free** — the design loses nothing. The earlier conclusion ("item 4b is void") happens
   to survive, but its reasoning was wrong in a way that mattered: "falls back to defaults" would
   have been silently incorrect tracking; "travels inside the cluster" is correct.

   The user's account of the calibration procedure, which this matches: a For Loop of
   *grab image → find/track bead centre → raise the ASI piezo stage one depth step → repeat*;
   then the stack is analysed, **the user chooses forget radius and bandpass**, and the result is
   clustered with the other calibration parameters and images, saved, and handed to the experiment
   while-loop. (This is also why the piezo is the one instrument that must never be actuated — it
   belongs to calibration, not tracking.) Corroboration from the main VI's own control list:
   it carries **`bandpass/forget array`** sitting directly among `cal image array`,
   `# slices in stack`, `obj step between slices`, `# avg per slice` and the `Intensity vs Radius`
   graph — i.e. the calibration block.

   **Still to double-check (user's own caveat):** the cal analysis runs through **subVIs**, and
   several of them likely overlap with the subVIs used by the tracking analysis. Nothing here
   touches the calibration path, but if that path is ever modified, map the shared subVIs first.
   This confirmation is **structural** (LabVIEW's own string export, two VIs agreeing plus the main
   VI's control block) — not runtime.

   ### Where `Cosine bandpass` is NOT — measured, and still true

   Probed by name on every VI in the tracking chain (`Wire Inputs` 5001 = not a *top-level* pane
   terminal; positive controls passed each time): not a standalone pane input on
   `Track 1 of N bds xyz-kernel-reentrant.vi`, nor `Track 2 of N …-v2.vi`, nor the four-fold
   kernel. Correct interpretation: **it is not a separate wire anywhere — it rides inside the
   cluster.** A byte scan also shows the four-fold kernel calls only those two sub-VIs (7 SubVI
   *nodes*, 2 distinct VIs).

   ### The four-fold connector pane — MEASURED, and PLAN's list was wrong

   Every FP control probed for pane membership. **`Real-space cosine window` and `4 pack remainder`
   are on the pane and were missing from PLAN's list**, so the drop-in replacement must carry them:

   **INPUTS (9, all verified):** `Image In` · `x,y,z array` · `Array of cal clusters` ·
   `Bead is good? array in` · `pos in cal image in` · `cross size` · `# of bead 4 packs` ·
   `4 pack remainder` · `Real-space cosine window`
   **Not standalone pane inputs — because they are FIELDS INSIDE the cal cluster** (see above):
   `Cosine bandpass` · `# slices in stack` · `r shifted cal real` · `r-shifted corkscrew cal` ·
   `r shifted cal ampl` · `obj step between slices`
   **OUTPUTS (3, from PLAN, not yet re-verified):** `x,y,z array out` · `Bead is good? array out` ·
   `pos in cal image out`. **`Wire Inputs` cannot see outputs** (it only resolves input terminals),
   so re-verify these with a `Get Outputs`-based probe before finalising the pane.

   This also **kills the array→array auto-index worry**: the only array-to-array pair
   (`Cosine bandpass`→`cosine bandpass`) is not reachable, so every reachable pair is either
   array→element (auto-index, correct) or scalar→scalar (broadcast, correct).

   **NEXT, in order:**
   - **a. starting-x/y feed — the one unsolved construction.** `x,y,z array` is FLAT
     (x,y,z per bead interleaved), so a plain border-crossing wire would auto-index it to ONE
     SCALAR per iteration — wrong. **Chosen design: `Decimate 1D Array` with 3 outputs, placed
     OUTSIDE the loop** — it distributes elements round-robin, so out0 = all x, out1 = all y,
     out2 = all z ([NI docs](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/functions/decimate-1d-array.html)).
     Then out0/out1 cross the border into `starting x 1`/`starting y 1` and auto-index correctly.
     **Zero nodes inside the loop, parallel-safe, and symmetric with the output side** (item 4c
     ends in `Interleave 1D Arrays`, the exact inverse, rebuilding `x,y,z array out`).
     **Blocker:** the node defaults to 2 outputs and must be grown to 3. Peer research
     (`archive/peer/2026-08-29-decimate-resize.md`): **no VI Server property sets terminal count**
     (`GObject.Bounds` is read-only); the documented routes are right-click a terminal →
     `Add Output`, or drag the node's bottom border with the Positioning tool. Neither is
     scripted, and injected right-clicks have historically opened nothing on this LabVIEW.
     **RESIZE SOLVED 2026-08-30 — gesture proven, recipe in the skill.** Quick Drop places the
     node; selecting it shows **blue resize handles** top- and bottom-centre; dragging the bottom
     handle grows it (~8 px per terminal, a 16 px drag added two, drag back up 8 to remove one).
     Verified by data: `Decimate 1D Array` reached **4 terminals (1 in + 3 out)**, counted as
     `Terminal` GObjects whose owner is the node. **Its class is `Unbundler`, not `Function`** —
     a `Function` traverse misses it and looks like a failed placement.
     **The donor/label plan is DROPPED**: a freshly placed primitive has unwired required inputs,
     so the donor VI is BROKEN and `save()` refuses it — and labelling a primitive needs GUI too.
     **Place the node directly into the kernel target instead** (4 GUI calls, now scripted-recipe).

   ### DIRECTION CHANGE 2026-08-30 — the whole build is scriptable; drop the GUI plan

   The user challenged the GUI work (*"왜 gui 쓴거야? 스크립트 쓰기로 한거 아닌가"*) and the
   challenge was right. Researching properly instead of assuming produced three findings that
   together remove **every** GUI step from the remaining assembly:

   1. **`LoopTunnel.IndexMode` is a WRITABLE scripting property** — this is what turns a tunnel's
      auto-indexing on and off, and it was the single unknown blocking the fully-scripted design.
      The reference must be cast to **`LoopTunnel`** (not `Tunnel`) with `To More Specific Class`,
      which the fleet already does routinely.
      [NI forum: How to change tunnel mode using VI scripting](https://forums.ni.com/t5/LabVIEW/How-to-change-tunnel-mode-using-vi-scripting/td-p/3969392)
   2. **`Create Property Node.vi` builds property nodes from strings** — controls `Class Name`
      (string) and `Properties` = array of {`ID String` (string), **`Is Write?` (boolean)**},
      returning `Inputs`/`Outputs` terminal refnums. So a *write* property node for any class and
      any property is scriptable; no right-click menu is involved.
      `Create To More Specific Class.vi` likewise scripts the cast (`reference` + `target class`).
   3. **The library's `Create *.vi` family is a refnum algebra** — verified on `Create Add.vi`
      (`x`,`y` in as wire-source refnums, `x+y` out as a terminal refnum) and `Create Constant.vi`
      (`Type`/`Value` in, `Terminal` out), plus `Create Index Array.vi`. **They create AND wire AND
      hand back a handle to chain from.** ~50 node types are covered.

   **The constraint that shapes every op**: refnums live only inside one VI's dataflow, so a chain
   of node creation must sit in **one fused op**, never split across COM calls. That is why
   `OpLoopKernel_v0` had to fuse Create For Loop → Create SubVI, and it is why the starting-x/y
   arithmetic must be one op too, not three.

   **So the Decimate plan is DROPPED.** No donor VI, no node placement by hand, no resize gesture,
   no primitive-name wiring (which crashed LabVIEW), no GUI wiring. Replace it with:

   > **`OpLoopKernelXY_v0`** — an extension of `OpLoopKernel_v0` that additionally, in the same
   > dataflow: takes the flat `x,y,z array` control terminal, wires it across the loop border,
   > **sets that LoopTunnel's `IndexMode` to non-indexed**, then builds
   > `Create Constant(3)` → `Create Add`(i+i, +i ⇒ 3i) → `Create Add`(3i+1) →
   > `Create Index Array`(array = tunnel inner terminal, indices = [3i, 3i+1]) and wires the two
   > element outputs into the kernel's `starting x 1` / `starting y 1`.

   The only hand edit the new op should need is the one the fleet has always needed: **setting a
   VI-Server class-specifier constant** (here to `LoopTunnel`) via its left-click picker — a click
   that goes into the *tool*, not the deliverable, which is the allowed kind.

   Open detail to confirm while building: the inner-side terminal of a LoopTunnel is exposed as a
   property (`InsideTerms[]` / `Outside Term` appear on property nodes inside `Create For Loop.vi`),
   which is where `Create Index Array`'s `array` input comes from.

   ### ✅ `OpCreatePropNode_v0` WORKS — and the "COM cannot set cluster arrays" claim was WRONG

   **2026-08-30, two corrections in one session. Read this before trusting anything below it.**

   The op's first end-to-end run failed with a modal dialog, and `Properties` read back as `()`.
   Claude concluded that **`SetControlValue` silently ignores an array-of-cluster** and reversed the
   project's direction on that basis. **That diagnosis was false.** The real fault was a single
   inherited bug:

   - the op carries an **orphaned `Open VI Reference`** from `OpSubVI_v1` (fed by the now-unused
     `vi path 2`), which still executes and raises **error 7 with a blank path** — looking exactly
     like a failure of the *first* path input. `ExecState == 1` does not catch it.

   With `vi path 2` set to any valid VI, the op runs clean (`error out` = no error) and **creates a
   real property node**: against a scratch target, GObjects went 161 → 168 — one **`Property`**,
   five `Terminal`s, one **`PropertyItem`**.

   **Claude then over-corrected**, reading that as proof the `Properties` write had worked and
   writing "GetControlValue cannot read an array-of-cluster" into the skill. **Also wrong** — a
   property node always carries one default row, so an empty array produces exactly that picture.
   The peer dispatch settled it (`archive/peer/2026-08-30-...-activex-cluster-array-setcontrolvalue.md`,
   Gemini, citing NI's ActiveX data-conversion doc and an NI forum thread):

   - **pywin32 marshals `[('IndexMode', True)]` as a 2-D SAFEARRAY** (a sequence of equal-length
     sequences), LabVIEW wants a **1-D SAFEARRAY of VARIANTs each holding a 1-D SAFEARRAY**, and on
     the dimension mismatch LabVIEW discards the write **while returning `S_OK`** — hence no error.
   - Wrapping explicitly with `win32com.client.VARIANT` works and round-trips. **Confirmed on the
     machine:** plain list → `()`; VARIANT form → `(('IndexMode', True),)`.
   - Now wrapped as **`gscript.cluster_array(rows)`**; recipe and sources in the skill.

   **So the read-back was fine all along and the write was the broken half.** Three readings of the
   same `()`, two of them confidently wrong, before a peer search produced the mechanism.

   **What the op still needs — now backed by evidence.** Running it with two real property names
   raises **error 1077 (0x435) "Invalid property value", method `Set Properties[]`**. That is the
   array arriving correctly and the *names* being rejected: the created node has **no class
   context**, because `Create Property Node.vi`'s `reference` input is unwired. This answers the
   question left open earlier ("the created node's class is uncertain"): the op must wire
   `reference` to an object cast to **`LoopTunnel`** before `IndexMode` will resolve.

   #### Peer review of the replacement plan — codex, `archive/peer/2026-08-30-...-xyz-array-layout-refute.md`

   The replacement design (`Decimate 1D Array` outside the loop → three auto-indexed tunnels) was
   dispatched for refutation. **Verdict: UNDETERMINED — do not wire it yet.** The layout assumption
   is not proven anywhere: `PLAN_kernel_parallel.md` records an `i*3` walk as *likely*, and
   `STATUS.md` then promoted it to a declared fact. Note this question is **orthogonal to the route
   choice** — `Index Array(3i, 3i+1)` needs the same layout guarantee that Decimate does.

   Silent-failure risks codex raised, all of which apply to **either** route:
   - `Decimate` **drops trailing elements** when the length is not a multiple of 3 — data loss, no error.
   - A For Loop silently uses the **shortest** auto-indexed input, so any length mismatch against
     the calibration-cluster or `Bead is good?` arrays quietly shortens the bead count.
   - The triplet order could be `x,z,y` or another historical convention; `i*3` cannot distinguish.
   - Rejected beads may occupy **padded slots**, so equal lengths would not detect misalignment.
   - Z is unused by the single-bead kernel, so a wrong third stream stays invisible during tracking
     yet corrupts `x,y,z array out` downstream.

   **Cheapest settling check:** trace upstream from the kernel call's `x,y,z array` input to the node
   that *constructs* it. `Interleave 1D Arrays(x,y,z)` or a per-bead `Build Array(x,y,z)` proves
   interleaved; concatenating three whole coordinate arrays proves blocked.
   **Minimum guards before acceptance:** assert `len(xyz) mod 3 == 0`, assert `len(xyz)/3` equals
   every bead-indexed companion array, and compare the reconstructed flat output numerically against
   the existing four-fold kernel.

   ### (retracted) the Decimate argument, kept because both routes still need points 1 and 2

   Two arguments were used to justify the Decimate route while the IndexMode route looked blocked.
   The premise is gone, but they remain the reasons Decimate is still a *reasonable* option:

   1. **It deletes the hardest part of the deliverable.** Splitting the flat `x,y,z array` into
      x[]/y[]/z[] *outside* the loop means all three cross the border as **ordinary auto-indexed
      tunnels — the default**. No property node, no `IndexMode` write, and none of the in-loop
      `Constant(3)` → `Add` → `Add` → `Index Array` chain. Decimate is a pure permutation of the
      same values, so the numeric-equivalence argument (rule 1a) stays trivial.
   2. **The output side needs the same machinery regardless.** Rebuilding `x,y,z array out` uses
      `Interleave 1D Arrays` — another resizable primitive with the identical placement problem.
      A donor VI plus a working `copy_into` solves both; the IndexMode route solved neither.

   **Two tool gaps to close before the donor works** (both are *tool* work, paid once):
   - `copy_into()` calls `save()`, and `save()` refuses `ExecState == 0` because **`SaveInstrument`
     blocks forever on a broken VI**. Copying a fresh primitive in *always* leaves the target
     briefly broken (unwired required input). Needs a **GUI `File ▸ Save` fallback** — already
     proven to work on broken VIs (see the skill).
   - The donor node needs a **label** for `copy_into` to find it (`Add Label`), and labelling a
     primitive is a GUI act.

   #### ✅ Tool gap 1 CLOSED — `gscript.gui_save()` / `save(allow_broken=True)`

   Verified end-to-end on a scratch: adding a For Loop with an unwired `N` drove `ExecState` to 0,
   and `save(SCRATCH, allow_broken=True)` routed to the new `gui_save()`, which focuses the VI's own
   window by file name and sends Ctrl+S. File grew **11,677 → 12,594 B** and the For Loop read back.
   `copy_into()` now passes `allow_broken=True`, so it can land a briefly-broken intermediate.
   Guarded three ways against ever saving an original: claudeDev-only, `focus` must match the
   target's own file name (it raises otherwise), and the save is only believed if mtime moves.

   #### ✅ Tool gap 2 DISSOLVED — labelling is scriptable: **`Set Name.vi`**

   `vi.lib\Erdos Miller\LV-Scripting\Set Name.vi` takes a GObject reference and a **`Name`** string
   (confirmed controls: `Name`, `error in (no error)`, `error out`). So "labelling a primitive needs
   the GUI" was **another unverified assumption** — the same error the build-by-scripting memory
   already records. **No GUI is needed for the donor at all**: the 3-output Decimate already exists
   in `PARALLEL_kernel_v2.vi` at **(-620, 991)**, class `Unbundler`, uid 4026, owner TopLevelDiagram
   (the only `Unbundler` in that file, so a traverse finds it unambiguously at index 0).

   ### ✅ ARRAY LAYOUT SETTLED, 2026-08-30 — interleaved, stride 3, x at 3k / y at 3k+1

   Read off the four-fold kernel's own diagram (a disposable copy,
   `claudeDev\READONLY_fourfold_COPY.vi`; the original was never opened). Structural census first:
   **40 `IndexArray`, 15 numeric constants, 1 `ForLoop`, 1 `CaseStructure` with 5 frames, 6 SubVI,
   no Decimate and no Interleave** — the kernel does all extraction with Index Array.

   The index arithmetic, read from the diagram:

   - `i × 4` → **4i** — the pack's first BEAD index (4 beads per pack); `+1` steps feed the magenta
     `Array of cal clusters` / `Bead is good?` index arrays.
   - `i × 12` → **12i** — the pack's first ARRAY ELEMENT (12 elements per pack); `+1` gives
     `12i+1`, a `+3` gives `12i+3`, `+1` gives `12i+4`, and the `6` / `9` constants continue the
     pattern.

   So the elements read are the **pairs** `(12i, 12i+1)`, `(12i+3, 12i+4)`, `(12i+6, 12i+7)`,
   `(12i+9, 12i+10)` — a pair every 3 elements, with the third of each triplet **skipped**. Since
   `12i + 3j = 3(4i+j) = 3k` for bead `k`:

   > **bead k occupies elements 3k (x), 3k+1 (y), 3k+2 (z); z is not an input to the kernel.**

   This confirms the interleaved layout and **rules out `x,z,y`** (the pair is consecutive, the
   skipped element is the third). `# of bead 4 packs` is the outer loop's `N`, and the 5-frame case
   structure is the `4 pack remainder` handling — which a per-bead parallel loop removes entirely,
   since `N = len(x,y,z array)/3`. That is a scheduling change, not a computation change.

   **Residual, minor:** which member of each pair goes to `starting x` vs `starting y` was read from
   the natural ordering, not traced wire-by-wire to the subVI terminal. Confirm with a Context Help
   hover on the `TRACK 2 of N XYZ` node before final acceptance.

   Codex's guards still apply and should become assertions: `len(xyz) mod 3 == 0`, and
   `len(xyz)/3` equal to every bead-indexed companion array.

   ### 🔑 The control→node wiring gap is NOT a library limit — `Get Controls.vi` closes it

   The fleet's standing gap ("cannot wire a front-panel CONTROL terminal to a node input", which is
   what has blocked `x,y,z array` → Decimate all along) is a limit of **`OpWire_v1`'s construction**,
   not of the library. Probing the library's panes shows:

   - **`Wire Inputs.vi`** takes `Names` (string array) **and `Inputs` — an array of SOURCE TERMINAL
     REFNUMS.** It does not care where those refnums came from.
   - **`Get Controls.vi`** takes `Control Names` (string array) and returns the front-panel controls'
     terminal refnums.

   So `Get Controls.vi` → `Wire Inputs.vi` wires any control to any named node input. `OpWire_v1`
   only ever fed `Inputs` from `Traverse` + `Get Outputs`, which is why it looked node-to-node only.
   (`Conditionally Connect Wire.vi` exposes no string/numeric controls — it takes refnums, so it is
   the low-level primitive, not the convenient entry point.)

   **Build `OpWireCtl_v0`**: `vi path` → Open VI Ref → `Get Controls.vi`(`Control Names`) →
   `Wire Inputs.vi`(`Inputs` = those refnums, `Names` = destination terminal names, node from
   `Traverse for GObjects`(`Class Name`, `index`)).

   **The one bootstrap cost:** building this op needs its own `Control Names` control wired to a
   node, which is the very thing the fleet cannot do — so **that single wire is made in the GUI,
   once.** It is a click into a *tool*, not into a deliverable, which is the permitted kind. Base it
   on `OpWireInd_v0` (the mirror: `Get Outputs` → `Wire Indicators`), whose control wiring is
   already in place, and swap the two subVIs.

   ### Progress this turn on `OpSetName_v0`

   `OpSetName_v0.vi` exists in `claudeDev` (10,128 B, ExecState 1): a copy of `OpCreatePropNode_v0`
   with the `Create Property Node.vi` branch stripped by `delete_by_label('Create Property Node.vi')`
   — **a subVI node's default label is its VI name, so `delete_by_label` reaches subVIs without any
   labelling step.** SubVI 2→1, Wire 11→9. Still to do: delete the `To More Specific Class` cast
   (it would raise 1057 on an `Unbundler`), drop `Set Name.vi`, and wire it — which needs the same
   control→node capability, so **`OpWireCtl_v0` comes first**.

   **Beware:** after a `delete_by_label` the in-memory VI is STALE — counts read unchanged until
   `close_panel()` + `revert()` reload it from disk. The substitution rewrites the file underneath
   the loaded copy.

   ### `PARALLEL_kernel_v2.vi` is the right base again, not a fresh v3

   The direction change had written v2's hand-placed Decimate off as dead weight. With the layout
   settled, v2 already holds everything: the P=4 loop, the kernel inside, 4 inputs wired, **and** the
   3-output Decimate at (-620, 991). All that remains is three wires — `x,y,z array` → Decimate
   `array`, and Decimate out0/out1 across the loop border into `starting x 1` / `starting y 1`. The
   first of those is exactly the control→node wire `OpWireCtl_v0` provides. No donor, no `copy_into`,
   no `Set Name` needed for this build.

   ### ✅ Parallel output ordering — positional bead identity is SAFE (user's question, 2026-08-30)

   The user asked how the refactor keeps bead identity when parallel iterations finish in a random
   order. Verified against NI's documentation (peer dispatch, archived as
   `archive/peer/2026-08-30-...-parallel-forloop-output-order.md`):

   - **An auto-indexed output tunnel maps iteration k to array index k**, regardless of completion
     order. Same for **Concatenating** mode (slices join in ascending iteration order) and for
     **Conditional** mode (surviving elements keep ascending iteration order). No NI CAR has ever
     reported otherwise since the feature shipped in LabVIEW 2009.
   - Ordering **is** lost for: shift registers / feedback nodes (which the compiler rejects under
     parallelism anyway — the reason for this whole refactor), the merge order of simultaneous
     errors in the auto-created error register, and any **side effect inside the subVI** (queue,
     global, DVR, file write).
   - Chunk size and the partitioning schedule affect task distribution only, never slot assignment.

   So **no explicit bead-index array is needed.** This also matches the original's own contract: the
   four-fold kernel writes results with `Replace Array Subset` at computed indices, not by appending.

   **Still a hypothesis until checked on the machine** (peer answers always are): add a cheap
   confirmation to the acceptance run — a small P>1 loop that auto-indexes `i` out and yields
   `0..N-1`.

   ### ✅ Kernel reentrancy — confirmed, no serialization risk

   Read over COM from both kernels: `IsReentrant = True`, `ReentrancyType = 1`,
   `PreferredExecSystem = 7`, for **both** `Track 1 of N bds xyz-kernel-reentrant.vi` and
   `Track 2 of N bds xyz-kernel-reentrant-v2.vi`. A non-reentrant subVI would have made parallel
   instances queue on one mutex — correct data, zero speedup — so this was worth checking before
   building. The exact `ReentrancyType` enum (shared vs preallocated clone) has **not** been verified
   against NI's documentation; `IsReentrant` settles the part that matters. Note that changing it
   is not an option anyway: these are originals (rule 1).

   ### ✅ `OpWireCtl_v0.vi` COMPLETE, 2026-08-31 — the fleet can now wire CONTROLS to nodes

   **10,708 B · SubVI 6 · Wire 26 · ExecState 1**, cold-verified. The two GUI acts are done and
   they are the last ones this capability will ever need. Wrapped as **`gscript.wire_control()`**:

       wire_control(target, ['x,y,z array'], 'Unbundler', 0, ['array'])

   Technique notes now in the skill, both hard-won: the class-specifier picker only opens after a
   click on empty canvas (deselect first), you *hover* to descend its submenus and click the first
   entry of a submenu to pick that class (`Generic ▶ GObject ▶ AbstractDiagram ▶ Diagram ▶ Diagram`);
   and a hand-drawn wire must END on the node's **left edge at the terminal's row** — three attempts
   aimed at the middle of the icon failed silently, the first at the edge worked. Both operations
   leave LabVIEW modal and hang the next COM call until `Esc` is sent.

   ### ✅ `PARALLEL_kernel_v3.vi` — INPUT SIDE COMPLETE, 2026-08-31 (68,178 B, ExecState 1, saved)

   Route 2 executed: fresh build on a copy of `READONLY_fourfold_COPY.vi`, old structure left in
   place as dead code (the standing plan). Cold-verified from disk:
   **ForLoop 2 · SubVI 7 · Unbundler 1 · Wire 254 · ExecState 1.**

   What it contains now:
   - **P=4 parallel For Loop** at (-1300, 1150) with `Track 1 of N bds xyz-kernel-reentrant.vi`
     inside (owner=Diagram), built by `loop_kernel()` in one call — 4 inputs wired by name:
     `Image In`→`Image`, `Array of cal clusters`→`Calibration cluster 1` (auto-indexed),
     `cross size`→`cross size`, `Bead is good? array in`→`Bead 1 is good? in` (auto-indexed).
   - **3-output `Decimate 1D Array`** at (-1012, 549), owner TopLevelDiagram (outside the loop),
     placed by Quick Drop + the blue-handle resize (GUI, recipe from the skill), fed by a **branch**
     of the `x,y,z array` control wire.

   Kernel control names CONFIRMED by probing (`GetControlValue`): inputs `Image`,
   `Calibration cluster 1`, `cross size`, `starting x 1`, `starting y 1`, `Bead 1 is good? in`;
   output found so far: `Bead 1 is good? out` (X/Y/Z output names still unknown — probe more names
   or read the panel). Four-fold copy's image control is **`Image In`** (capital I in "In").

   **Set Name / DEC3 labelling is DEAD and unnecessary**: `Set Name.vi` writes a property literally
   called `Name` (offline scan — no `Label`/`Text` strings in it), which is NOT the owned label
   `move_by_label` searches, so the label never took (`copy_into` → error 1054). The refnum input's
   pane name, read off its front panel, is **`Type in`** — `OpSetName_v0.vi` is finished and saved
   (10,164 B, ExecState 1) but sets the wrong property for our purpose. Kept for parts.

   #### Lessons that cost real time today (all now in the skill):

   - **A wire BRANCH does not change the Wire count.** A wire object owns all its segments/sinks, so
     `wire_control`'s `+1 Wire` check misreads a successful branch as a silent decline — it
     "failed" twice while actually succeeding. Verify branches by **ExecState going 0→1** (required
     input now fed) or by the segment's pixels, never by count. `wire_control` needs a
     `branch=True` mode that skips the count check.
   - **`Wire Inputs.vi` refuses to branch from an already-wired source, but a GUI branch is normal
     LabVIEW** — and `loop_kernel`'s Create-SubVI path branches fine (it wired 4 already-wired
     controls). The refusal is specific to `Wire Inputs.vi`.
   - **Never cold-load a broken-saved VI headless**: GetVIReference on the 30 KB broken v3 sent
     LabVIEW into a 100%-CPU recompile spin (>8 min, killed). `open_panel()` first loads the same
     VI in 16 s. Also `lv()`/`op()`/GetVIReference are UNGUARDED COM calls — they hang the caller
     forever, outside the watchdog.
   - **Ctrl+S during error 2 (memory full) writes a STALE file**: mtime moves, content is the
     previous state — the first Decimate placement was lost this way despite a "successful" save.
     After error 2, restart; only then save.
   - **Trust the title strip, not `focus`'s return value**: keystrokes went to a non-LabVIEW window
     twice; one Quick-Drop text landed in another app. Verify the foreground title pixel-wise before
     every typed sequence (the skill's z-order rule, re-learned).
   - The original `Track 1 of N` kernel raised a **save-changes prompt** when leaving memory
     (relink dirt) — answered **Don't Save**, and the file verified byte-identical afterwards
     (28,333 B, md5 59e94608a7ba). Rule-1 protocol worked.

   ### ✅ Output tunnels DONE, 2026-08-31 (68,418 B, ExecState 1, saved)

   `exit_loop(V3, 0, ['X pos 1','Y pos 1','Z pos 1','Bead 1 is good? out'], 1)` — LoopTunnel 9→13,
   all auto-indexed, VI stays legal. (`loop_diagram()` returns a dict; `exit_loop` wants the bare
   integer `i` — it takes `1` here, the P-loop's inner diagram.)

   **Kernel pane read in full from its front panel** (read-only, panel closed after):
   inputs `Image`, `Bead 1 is good? in`, `starting x 1`, `starting y 1`, `cross size`,
   `Calibration cluster 1`, **`cosine window for hilbert`**, **`real-space cosine window`**;
   outputs `X pos 1`, `Y pos 1`, `Z pos 1`, `Bead 1 is good? out`,
   `bead 1 z position as a cal image index` (DBL), `Index of closest cal image slice, bead 1` (I32).

   **Two inputs are still unwired and they are rule-1a critical:** the two cosine windows are
   whole-array parameters shared by every bead, so they must cross the loop border through
   **NON-indexed tunnels** — the default auto-indexing would slice them per-iteration and silently
   change the computation. Wiring them therefore needs the IndexMode flip
   (the property-node op with its `reference` input wired — the diagnosed fix) or a GUI tunnel
   toggle. NOT yet done.

   **`pos in cal image out` settled by type**: the indicator is an I32 array; the kernel's only I32
   output is `Index of closest cal image slice, bead 1` (the DBL twin is the fractional z index).
   So per bead it is `Index of closest cal image slice, bead 1` → auto-indexed tunnel → indicator.

   **User authorization 2026-08-31: v3 is a copy, originals stay untouched — free to delete and
   rework anything inside it**, including the dead four-fold structure and the old indicator wires.

   ### ✅ OUTPUT SIDE COMPLETE, 2026-08-31 (68,426 B, Wire 262, ExecState 1, cold-verified)

   All three output indicators are now driven by the parallel kernel:

   - `Bead 1 is good? out` → auto-indexed tunnel → **`Bead is good? array out`** (wire_indicators)
   - `Index of closest\ncal image slice, bead 1` → tunnel → **`pos in cal image out`**
     (**the label contains a real newline** — probing `'...closest\ncal image...'` succeeded where
     the single-line spelling 5001'd; second confirmed two-line label:
     `'bead 1 z position\nas a cal image index'`)
   - `X pos 1` / `Y pos 1` / `Z pos 1` → tunnels → **3-input `Interleave 1D Arrays`** →
     **`x,y,z array out`** (input order X,Y,Z = interleaved x0,y0,z0,… — each tunnel identified by
     Context Help hover on its wire before wiring, not guessed)

   The three dead wires that used to drive those indicators were click-selected and deleted first
   (user authorized editing the copy freely).

   **The move that unlocked the GUI work: `Clean Up Diagram` (Ctrl+U) on the whole copy.** The
   scripted loop was a 50-px collapse with 15 tunnels overlapping — unclickable. Cleanup spread the
   loop to ~165×160 with tunnels at 20-px spacing, and **moved `x,y,z array out` right next to the
   loop**, dissolving the 1600-px long-wire problem. Wire/ExecState verified unchanged across
   cleanup. Positions are not semantics; on an authorized copy this is the cheap way out of every
   viewport problem.

   Session-lesson: **two error-2 (memory-full) events recurred during GUI work; a GUI Ctrl+S in
   that state wrote a stale file once** (the first Decimate loss) but a later one wrote correctly
   (size moved 67,826→67,966). After every error 2: restart, reload panel-first, re-verify counts
   before continuing. The final Interleave→indicator wire was lost to exactly this and had to be
   redrawn once (13:50 save had it missing; redrawn cold at Wire 261→262).

   **NEXT (the last assembly items):**
   0. **Cosine windows, rule-1a critical**: `Cosine bandpass for Hilbert` → kernel
      `cosine window for hilbert`, `Real-space cosine window` → `real-space cosine window`; both
      whole-array parameters ⇒ tunnels must be **NON-indexed** (GUI: select tunnel → VK_APPS
      context menu → Tunnel Mode ▸ Last Value, or the IndexMode property op). Wire first
      (`wire_control` with `branch=True` — the controls feed the dead structure already), then flip.
   1. Connector pane: 9 inputs / 3 outputs to match the four-fold pane (read it from the original's
      Context Help before assigning).
   2. Final save + STATUS sweep, then the functional acceptance fixture.

   **Old list (superseded):**
   1. **The fleet's one missing primitive: tunnel-outer-terminal access.** Indicators are far from
      the loop (~1600 px), GUI wiring across that span is impractical, and every scripted path dies
      on the same fact: tunnels have no named terminals. Build **`OpTunnelOut_v0`** — Traverse
      `LoopTunnel[i]` → property **`Outside Terminal`** (seen in Create For Loop.vi's internals) →
      hand the refnum to `Wire Inputs`/`Wire Indicators`. One GUI class-pick into the op, then
      tunnel→indicator wiring is scripted forever.
   2. Delete the dead structure's three wires into `Bead is good? array out`, `x,y,z array out`,
      `pos in cal image out` (or the whole dead structure — authorized; wires click-select
      reliably, the structure border does not).
   3. `Index of closest cal image slice, bead 1` → 5th output tunnel (exit_loop again) → 
      `pos in cal image out`.
   4. `Interleave 1D Arrays` (Quick Drop + resize to 3 inputs, proven recipe) ← x[],y[],z[] tunnels;
      output → `x,y,z array out`. `Bead is good? out` tunnel → indicator directly.
   5. Cosine windows: wire + IndexMode flip (see above).
   6. Connector pane, final save, then the functional acceptance fixture.

   **Old NEXT list (superseded by the above):**
   1. Kernel X/Y/Z output terminal names — probe candidates or read its connector pane.
   2. `exit_loop()` those outputs (auto-indexed tunnels out of the P-loop, order-safe per the
      parallel-ordering verification).
   3. Rebuild `x,y,z array out` — needs `Interleave 1D Arrays` grown to 3 inputs (same Quick-Drop +
      resize recipe) — or decide the pane carries x[]/y[]/z[] separately (user's call: that changes
      the caller's contract).
   4. The three output indicators are still driven by the DEAD structure — those wires must be
      deleted (wires select reliably by click; Delete key) before the new sources connect.
   5. Connector pane, final save, then the functional acceptance fixture.

   ### 🔧 `OpSetName_v0.vi` — one terminal name short (10,540 B, ExecState 0, saved 2026-08-31)

   Route decided with the user: **build `PARALLEL_kernel_v3` fresh** rather than unpick v2's old
   wiring. That needs the 3-output Decimate copied in by label, so `OpSetName_v0` has to work first.

   Done and on disk:
   - class-specifier constant changed `Diagram` → **`GObject`** (an `Unbundler` is a GObject, so the
     cast succeeds for any object we want to label). GUI, using the recipe now in the skill.
   - `Set Name.vi` dropped at (800, 281).
   - error chain wired, and **the `Class Name 2` control wired to `Set Name`.`Name` by
     `wire_control` — fully scripted.** First real payoff of `OpWireCtl_v0`.

   **The one blocker: `Set Name.vi`'s reference input terminal name is still unknown.** `Refnum`,
   `Object`, `GObject`, `reference` each return a clean 5001 from `Wire Inputs`; `GObject in`,
   `Object in`, `Reference in`, `refnum`, `Refnum in` were lost when LabVIEW wedged mid-probe.
   `GetControlValue` cannot read refnum controls, an offline zlib scan of the VI yields only
   `Name` / `Refnum` / the error terminals, and **`ExportVIStrings` hangs over COM** (three
   signatures tried, each to the watchdog).

   **Next action — stop guessing, read it:** open `Set Name.vi`'s own **front panel** and read the
   refnum control's label off the screen. One screenshot, no COM, no wiring attempts. (Context Help
   was tried and is unreliable here: the Functions palette steals the hover, and both it and the
   palette leave LabVIEW modal so the next COM call hangs.)

   Note for whoever continues: LabVIEW wedged twice during this work with **no modal dialog** — the
   UI stayed responsive while COM blocked. `Esc` clears the menu/wiring-mode cases; a genuine wedge
   needs the process killed. Save via GUI `Ctrl+S` first — it works while COM is blocked, and that
   is how this VI's edits survived.

   ### ⛔ `PARALLEL_kernel_v2.vi` cannot simply be finished — its `x,y,z array` is already wired

   First real use of `wire_control` failed with no error and no wire. Discriminating test settled
   why (v2 was reverted afterwards; it is back at Wire 255 / 31,626 B):

   - `'1D array'` and `'Array'` → **explicit error from `Wire Inputs.vi`** (name not found).
   - `'array'` → **no error** ⇒ **`array` is the correct input terminal name** of
     `Decimate 1D Array`. Worth recording: this was obtained by *contrast*, not by brute-forcing
     names into `Get Outputs`, which crashes LabVIEW.
   - `'x,y,z array'` → `array` was **silently declined**, which is the documented signature of
     **branching from an already-wired source terminal**.

   So in v2 the `x,y,z array` control is already wired straight into the P=4 loop — the *old*
   design, from before the layout was settled. The new design needs it to go to the Decimate first.

   **Decision needed next session:** either delete that one wire in v2 (the fleet has no
   delete-a-specific-wire op — `remove_bad_wires` only clears broken ones), or **build
   `PARALLEL_kernel_v3.vi` fresh** with `loop_kernel()` and wire it correctly from the start, which
   avoids surgery but needs the 3-output Decimate copied in from v2 (`copy_into` by label, so
   `OpSetName_v0` has to be finished first to give that node a label).

   ### 🔧 `OpWireCtl_v0.vi` — built to 90%, 2026-08-30 (10,672 B, SubVI 6, Wire 25, ExecState 0)

   Base: a copy of `OpWire_v1`, whose source branch is
   `Traverse`(124) → `IndexArray`(308) → `To More Specific Class`(683, class constant 755) →
   *[was `Get Outputs`]*, and whose dest branch feeds `Wire Inputs`(262).

   Done, all by script:
   - `delete_by_label('Get Outputs.vi', allow_broken=True)` — removed 13 objects.
   - `drop_subvi(Get Controls.vi)` at (725, 281) → uid 372.
   - `To More Specific Class`.**`specific class reference`** → `Get Controls`.**`Diagram in`**
     *(the output terminal name is confirmed — it wired first try, Wire 21→22)*.
   - `Get Controls`.**`Control Terminals`** → `Wire Inputs`.**`Inputs`**.
   - error chain restored: `To More Specific Class` → `Get Controls` → `Wire Inputs`.

   **Remaining — the two GUI acts, both into the tool, both on the source branch:**
   1. Set **ClassSpecifierConstant uid 755 at (587, 243)** to **`Diagram`** (left-click picker). It
      still names the class `Get Outputs` needed, so the new wire is a type mismatch until changed.
   2. Wire the **`Names` control (uid 926, at (679, 240))** → `Get Controls`.**`Control Names`**.
      This is the one wire the fleet cannot make — and the whole reason this op exists.

   Then `save(allow_broken=False)` should succeed with ExecState 1, and `OpWireCtl_v0` makes every
   future control→node wire scriptable.

   ### Two tool bugs found and fixed this session — both had masqueraded as a wedged LabVIEW

   - **`SendKeys "^s"` leaves the File MENU ACTIVATED, and an active menu blocks ALL COM.** Every
     subsequent COM call hangs for the full 180 s watchdog. Diagnosed from a hang screenshot showing
     `File` highlighted in the menu bar; `Esc` clears it instantly. `gui_save()` now always sends
     `Esc` after the accelerator. **Two LabVIEW restarts were spent on this before the screenshot
     was actually read** — a hang is not automatically a wedge.
   - **A VI's Front Panel and Block Diagram windows both match a substring title search**, and
     Ctrl+S on the Front Panel did nothing. `gui_save()` now tries `"<name> Block Diagram"` first
     and sleeps 0.8 s after focusing, because `SetForegroundWindow` needs a moment.
   - `delete_by_label(..., allow_broken=True)` added: removing the node that fed a required input
     legitimately breaks the VI mid-swap, and the refusal made the swap impossible.

   **Caution recorded:** a failed substitution op can leave the NI Move example VI **dirty in memory
   with the substituted diagram**, so a stray save corrupts it. `ensure_move_files_pristine()`
   restores it (verified: 4,656 B / 4,300 B match the `.ORIG.bak` files), but check it after any
   exception inside `delete_by_label` / `copy_into`.

   **Next action, in order:**
   **ROUTE DECIDED: Decimate.** With the layout confirmed as stride-3 interleaved, a 3-output
   `Decimate 1D Array` outside the loop yields exactly x[]/y[]/z[], and all three cross the border as
   default auto-indexed tunnels. Nothing goes inside the loop, and the equivalence argument stays a
   pure permutation. The IndexMode route is no longer blocked either, but it puts a property node,
   a constant and three arithmetic nodes into the deliverable — more surface to verify for no gain.
   (If it is ever revived, `OpCreatePropNode_v0` needs two fixes, both now diagnosed: wire
   `Create Property Node.vi`'s **`reference`** from a `To More Specific Class` cast to **`LoopTunnel`**
   — without it, error 1077 on `Set Properties[]` — and set or delete the orphan fed by `vi path 2`.)

   1. **Build `OpWireCtl_v0`** (see above) — one GUI wire into the tool, then never again.
   2. **Finish `PARALLEL_kernel_v2.vi`**: `x,y,z array` → Decimate `array` (via `OpWireCtl_v0`);
      Decimate out0 → `starting x 1`, out1 → `starting y 1` (both plain `wire()`, border crossing
      auto-indexes); `exit_loop` for the outputs; connector pane; save.
   3. **Confirm the residual** with a Context Help hover on `TRACK 2 of N XYZ`: which member of each
      `(3k, 3k+1)` pair reaches `starting x` vs `starting y`.
   4. **Functional acceptance** — the only verification that counts: same inputs through the
      four-fold path and the parallel path, same X/Y/Z out. Add codex's assertions
      (`len(xyz) mod 3 == 0`; `len(xyz)/3` == every bead-indexed companion array length).

      **Fixture format decided 2026-08-31** (user asked how to persist IMAQdx images; research
      archived at `archive/peer/2026-08-31-...-imaq-image-save-exact-roundtrip.md`, essentials in
      the skill). Use `IMAQ ImageToArray` → binary file → `IMAQ ArrayToImage` — a memcpy round trip,
      bit-exact for every grayscale type, no codec in the path. TDMS is an equally exact option that
      can carry per-frame stage/magnet state. **Store alongside the pixels:** image type, width,
      height and **border size** (never written to any image file, and neighbourhood operators need
      it), plus the kernel's other inputs — `Array of cal clusters`, `x,y,z array`,
      `Bead is good? array`, `cross size`, `pos in cal image`. Avoid BMP (errors on 16-bit), JPEG
      and AVI2; PNG is fine for U16 but silently offsets **I16** by 32768 unless the destination
      image is pre-created as I16.

      **FIXTURE DESIGN AGREED WITH THE USER, 2026-08-31.** Drop the frame rate right down and, in
      the **working copy** (`Min_Track N beads V6_ParallelLoop.vi` — never the original), save per
      frame: the image as a TIFF named by zero-padded frame number, plus that frame's trace row.
      `.cal` and `.tra` are kept as they already are.

      Why this beats replaying a whole sequence: **each frame becomes an independent test case.**
      `image[N]` plus the positions from `tra[N-1]` are exactly the kernel's inputs for frame N, so a
      mismatch localises to one frame instead of poisoning everything downstream.

      **Must be checked before trusting the comparison:** whether `.tra` holds the kernel's RAW
      output or a processed value — the main VI runs `exp-ref management.vi` and converts z through
      the calibration, so the trace may be in physical units. Safest fix is to log the kernel's own
      output as an extra column rather than assume.

      Also per frame: the **`Bead is good?` array** (it changes when beads are lost, and it is a
      kernel input). Once per session, a sidecar with image type, width, height, **border size**,
      cross size, the cal file used, and bead count — `IMAQ Create` needs these to rebuild an
      equivalent image.

      **What `.cal` actually contains** (read directly from `G:\Data\Seongeun\...\cal001`, big-endian
      LabVIEW flattened binary): a `[beads][2]` array of doubles = bead centre x,y, then per bead a
      `[119][60]` array = the I(r) radial profile over 119 z-steps × 60 radial bins. Size scales at
      **57,200 bytes per bead** (2 beads 114,400 / 3 beads 171,552 / 5 beads 285,856), which is why
      **no pixel data is in there** — hence the TIFFs. The `.bmp` files in the data tree are 646×518
      24-bit display snapshots, not raw frames.

      **Readability is solved at the viewing end, not the writing end** (settled 2026-08-31;
      details in `archive/peer/2026-08-31-...-fiji-raw-and-sequence-import.md`). Fiji opens a raw
      sequence via `File > Import > Raw…` and a numbered folder via `Import > Image Sequence` — in
      place, no conversion, no duplicate — and can then `Save As > Tiff` to one multi-page TIFF,
      bit-exact for 16-bit. **So no LabVIEW stack-writer is needed.**

      Fiji `Import > Raw…` settings for LabVIEW-written frames: type **16-bit Unsigned** (for a U16
      camera), offset `0`, gap `0`, **"Little-endian byte order" UNTICKED** — LabVIEW's binary write
      and ImageJ's raw import are both big-endian by default, so they pair exactly (independently
      confirmed by decoding this rig's own `cal001`, whose doubles read correctly as big-endian).
      Tick "Use virtual stack" for long sequences.

      **Trap: never choose "16-bit Signed" for unsigned camera data** — ImageJ adds +32768 to the
      buffer and hides it behind a display calibration, so the picture looks right while scripted
      pixel access is wrong. Zero-padded filenames are **not** required (`Sort names numerically` is
      on by default) but remain good practice.

      **Open question for the user:** the tracking camera's bit depth and image type (U8 / U16 /
      I16), and whether the acquisition buffer uses a non-default border.

      **Reuse before building:** the rig already loads image stacks from disk
      (`Load and prep N cal images.vi`), so its existing format may serve directly. Its internals
      are compressed and could not be read offline — check it in LabVIEW before writing anything new.

   **Still-valid findings from this session** (independent of the retraction):

   - `OpSetName_v0` — `vi path` → Open VI Ref → `Traverse for GObjects`(`Unbundler`, 0) →
      `Set Name.vi`(`Name` = control). Run it against `PARALLEL_kernel_v2.vi` to label the Decimate
      **`DEC3`**. Easiest base to copy is `OpCreatePropNode_v0`, which already has
      `vi path` → Open VI Ref → Traverse(`Class Name`, `index`) built and wired.

      **The reference input is named `Refnum`** — best lead, not yet confirmed. `GetControlValue`
      **cannot read a refnum control at all** (35 name candidates, 0 hits, while `Name` and both
      error terminals read fine), so the name came from an offline zlib byte scan of `Set Name.vi`.
      **The build is self-verifying: `Wire Inputs` raises error 5001 on a name that does not exist**,
      so a wrong guess fails loudly and immediately — no separate probe op is needed first.
      (A general `OpGetControls_v0` wrapping the library's `Get Controls.vi` would end pane-name
      guessing permanently and is worth building later, but it is not on the critical path.)
   3. Clean `PARALLEL_kernel_v3.vi`; `loop_kernel()` for the P=4 loop + kernel;
      `copy_into(v2, 'DEC3', v3)` for the Decimate; wire `x,y,z array` → Decimate, and Decimate
      out0/out1 across the loop border into `starting x 1` / `starting y 1` (plain auto-indexing —
      **no IndexMode work**); `exit_loop` for the outputs; fix the connector pane; save.

   `OpCreatePropNode_v0.vi` stays on disk but is **not on the path**. If it is ever revived, note
   its orphaned `Open VI Reference` (set `vi path 2` or delete the node).

   ### ✅ `OpCreatePropNode_v0.vi` BUILT AND SAVED (2026-08-30) — 10,795 B, ExecState 1

   Cold-verified from disk: **SubVI 2 · Wire 11 · ControlTerminal 8 · ExecState 1**. Structure:
   `vi path` → `Open VI Reference` → `Traverse for GObjects`(`Class Name`, `index`) →
   `To More Specific Class`(Diagram) → **`Create Property Node.vi`**`.Diagram in`, with the
   `Properties` control wired to `.Properties`, and an `error out` indicator.

   **Its real connector pane, read from Context Help** (the string dump is misleading — it lists FP
   controls that are NOT on the pane): inputs **`Diagram in`[0]**, **`Properties`[1]**,
   `error in`[11]; outputs `Diagram out`[4], `reference out`[6], `Outputs`[8], `error out`[10].
   **`Class Name` is NOT on the pane** — so the copied `Class Name 2` control in this op is an
   unused leftover, and the created node's class must come from what gets wired to `reference out`.
   Terminal geometry (hover-verified): left edge 528=`Diagram in`, 532/536=`reference`,
   540=`Inputs`, 544=`error in`; **`Properties` is the magenta terminal on the TOP edge** (936,521).

   **Build lessons banked in the skill this session** — all three cost real time here:
   - **File-substitution ops (`copy_into`/`move_by_label`/`delete_by_label`) destroy unsaved
     in-memory edits.** They save the target and copy it back over the file, so a node drop + wire
     made beforehand simply vanishes. Order: file ops first (or `save()` between), then in-memory
     work, then save.
   - **A library-member VI cannot be a substitution donor.** Using
     `LV-Scripting.lvlib:Create Property Node.vi` as the `copy_into` donor raised **error 1026
     "VI Reference is invalid"** — its bytes at a foreign path break library membership. Copy such
     controls from a **plain** VI instead (`Class Name` came from `OpReport_v3.vi`).
   - **Pasted controls land stacked at (0,75).** Two `copy_into` calls put both controls at exactly
     the same coordinates; drag one aside before trying to click either, and get the stub position
     from a zoomed capture — the terminal was at y 107–124 while repeated clicks at y 127 hit
     nothing.

   **Next:** use this op to create the `LoopTunnel` / `IndexMode` write property node inside a new
   `OpSetIndexMode_v0`, then the non-indexed tunnel, then the fused `OpLoopKernelXY_v0`.

   ### BOOTSTRAP ANALYSIS — where the ONE unavoidable GUI act sits (2026-08-30)

   **Diagnosed, not assumed:** `Create For Loop.vi`'s `Inputs` / `Inputs Indexing?` path is **dead**.
   Measured on a scratch copy — `for_loop()` with a valid control name adds **+1 ForLoop and +1
   Tunnel (the N terminal) but LoopTunnel stays 8 and Wire stays 251**, for `indexing=[False]` *and*
   `[True]`. So OpForLoop can create a parallel loop but never a data tunnel, and the indexing
   argument is inert. The `IndexMode` route is therefore required.

   **The dependency chain, and where it bottoms out.** Every remaining capability reduces to
   "script a property node", and property nodes can be created by `Create Property Node.vi`
   (`Class Name` string + `Properties` = array of {`ID String`, `Is Write?`}). But to *run* that VI
   we need an Op wrapping it, and wiring that Op needs the one thing the fleet still cannot do:

   > **Gap: wire a front-panel CONTROL terminal to an arbitrary NODE input.** `OpWire_v1` is
   > node→node (`Get Outputs`/`Wire Inputs` both take Nodes); `loop_kernel`'s control sourcing is
   > hard-wired into `Create SubVI`. A control terminal is class `Terminal`, invisible to both.
   > **This is why GUI kept creeping into every Op build** — it was never the nodes, it was their
   > controls.

   Closing it properly needs `Conditionally Connect Wire.vi` (joins two terminals) plus a node's
   `Terminals[]` property — i.e. it needs a property node, which is the thing we are trying to
   build. **The circle breaks with exactly one hand edit**, and it should be spent here:

   > **Build `OpCreatePropNode_v0` and GUI-wire only its two string/array controls**
   > (`Class Name`, `Properties`) into `Create Property Node.vi`. Everything else in it —
   > `Diagram in` and `reference` — comes from traverse+cast chains that `OpWire_v1` already wires
   > by name. Two clicks, into a tool, once, forever.

   After that: `OpCreatePropNode_v0` builds the LoopTunnel/IndexMode write node inside
   `OpSetIndexMode_v0`, which unblocks the non-indexed tunnel, which unblocks the fused
   `OpLoopKernelXY_v0`. And the same op closes the control→node gap for every future build.

   **Progress this session:** `OpCreatePropNode_v0.vi` skeleton exists in `claudeDev` (a copy of
   `OpSubVI_v1`), and the node swap is proven in one scripted call — `delete_by_label('Create
   SubVI.vi')` leaves a clean skeleton (SubVI 2→1, Wire 13→9, **ExecState 1**), then
   `drop_subvi(Create Property Node.vi)` puts the new node at (915,492). That swap was left
   **unsaved** (the VI is broken until wired); redo it with those two calls.

   ### ASSEMBLY SO FAR — **`PARALLEL_kernel_v2.vi`** (2026-08-30, still valid)

   `v1` is **superseded and deletable**: its loop was built at (4600,300), ~5,800 px away from the
   control terminals, which makes GUI wiring geometrically impossible. `v2` rebuilds it beside them.

   **On disk, cold-verified on a fresh LabVIEW** (31,626 B — small because currently BROKEN, so no
   compiled code; the diagram is complete):

   | | state |
   |---|---|
   | P=4 For Loop at **(-1300, 1150)**, bead kernel inside at (-1299,1151), owner=Diagram | ✅ |
   | 4 inputs wired by name (cal clusters / Image / cross size / Bead is good?) | ✅ |
   | `Decimate 1D Array` at **(-620, 991)**, owner=**TopLevelDiagram**, grown to **3 outputs** | ✅ |
   | ForLoop 3 · SubVI 8 · Wire 255 · LoopTunnel 12 · Unbundler 1 | ✅ counts verified |
   | 3 wires · output tunnels · connector pane · final save | ⬜ |

   **Coordinates for the remaining wiring** (all measured, not guessed):

   - `x,y,z array` **control terminal ≈ (-1357, 228)** — identified by matching the on-screen label
     stack (`x,y,z array` / `Array of cal clusters` / `pos in cal image in`) to the reported
     ControlTerminal list.
   - Decimate: input **(-620, 991)**; outputs **(-604, 991)**, **(-604, 999)**, **(-604, 1007)**.
     out0 → `starting x 1`, out1 → `starting y 1` (out2 = z, unused).
   - Kernel node **(-1299, 1151)** inside the loop.
   - **Screen ↔ diagram mapping is derived per scroll position** by matching one known object; at the
     last working scroll it was `screen = diagram + (1325, -127)`. Re-derive it after any scroll.
   - Wire the two pairs in **separate scroll positions** — control→Decimate spans 763 px, and
     Decimate→kernel spans 160 px, but control→kernel spans 923 px which does not fit one viewport.

   **`OpWire_v1` CANNOT be used for the Decimate** — see the skill: feeding guessed primitive
   terminal names to `Get Outputs` **crashed LabVIEW**. These three wires must be drawn with
   `lv_gui.ps1 -Action wire`, hover-verifying each endpoint first.

   ### Session hazards hit repeatedly (all now in the skill)

   - **Error 2 = memory full.** Every scripting call fails after heavy use (~770 MB private). Cure:
     **save first, then restart** (drops to ~410 MB). Happened twice in one session.
   - **A broken VI cannot be saved by `gscript.save()`** — use **File ▸ Save from the menu**. The
     file then shrinks dramatically (72 KB → 31 KB) because a broken VI carries no compiled code;
     the diagram is intact, verified by cold reload.
   - **Every forced kill queues a `Select Files to Recover` dialog** on the next launch, which blocks
     COM. Read its file list before answering — once it offered only a deliberately deleted scratch
     VI, so Cancel was right — and expect it to respond only after a delay.
   - Floating windows (Navigation, Context Help) placed at (0,0) **cover the diagram's menu bar**.

   ### (superseded) earlier v1 attempt

   **Target:** `claudeDev\PARALLEL_kernel_v1.vi`, a copy of `v2_KERNEL.vi`. **On disk and
   cold-verified** (31,626 B — small because it is currently BROKEN, so it carries no compiled
   code; that is normal and the diagram is complete):

   | | state |
   |---|---|
   | P=4 For Loop at (4600,300) with the bead kernel inside (owner=Diagram) | ✅ built |
   | 4 inputs wired by name: `Array of cal clusters`→`Calibration cluster 1`, `Image In`→`Image`, `cross size`→`cross size`, `Bead is good? array in`→`Bead 1 is good? in` | ✅ built, ExecState was 1 at this stage |
   | `Decimate 1D Array` grown to **3 outputs**, at (4286,532), **owner=TopLevelDiagram** (outside the loop, correct) | ✅ placed, 4 terminals verified |
   | 3 wires: `x,y,z array`→Decimate `array`; Decimate out0→`starting x 1`; out1→`starting y 1` | ⬜ **next** |
   | output tunnels `X pos 1`/`Y pos 1`/`Z pos 1` via `gscript.exit_loop()` | ⬜ |
   | connector pane (9 in / 3 out) · final save · delete the old four-fold code | ⬜ |

   ExecState is **0** only because the Decimate's `array` input is unwired — expected mid-assembly.

   **The open question for the next step:** can `OpWire_v1` address a primitive's terminals **by
   name**? The probe was written but never ran (LabVIEW hit the memory ceiling first). Candidates to
   try for the Decimate outputs, from its Context Help: `elements 0, n, 2n, ...` /
   `elements 1, n+1, 2n+1, ...`, and `array` for the input. If none resolves, fall back to three
   GUI wires with `lv_gui.ps1 -Action wire` — the loop and the Decimate are ~300 px apart on screen
   at the (4600,300) region, so both endpoints are visible at once.

   **Session hazards hit twice, now documented in the skill:** LabVIEW threw **error 2 (memory
   full)** on every scripting call after heavy use (~770 MB private); the cure is **save first, then
   restart** (a restart dropped it to ~410 MB). A broken VI cannot be saved by `gscript.save()` —
   use **File ▸ Save from the menu**, and move floating windows first because the Navigation window
   at (0,0) covers the block diagram's menu bar.

   **Superseded plan text below** (the original 4a step list):
   1. `PARALLEL_kernel_v1.vi` ← copy of `v2_KERNEL.vi` (the deliverable; nothing is built there yet).
   2. `gscript.loop_kernel()` with the 4 proven pairs from the table above → loop + kernel + 4 wires.
   3. Quick-Drop + resize a 3-output `Decimate 1D Array` on the target's top-level diagram.
   4. Wire `x,y,z array` control → Decimate `array` input. **Open question:** the fleet has no
      control→node wiring op (`OpWire_v1` is node→node; `loop_kernel`'s control sourcing is
      hard-wired to Create SubVI). Either GUI-wire this one with `lv_gui.ps1 -Action wire`, or
      settle whether `Get Outputs`/`Wire Inputs` can address a primitive's terminals **by name**
      (Context Help shows the outputs as "elements 0, n, 2n, …" — probably not usable names).
      **Test this before building**: drive `OpWire_v1` with source class `Unbundler` and a
      candidate name; a 5001 means the name path is unusable and everything Decimate-side must be
      GUI-wired.
   5. Decimate out0 → kernel `starting x 1`, out1 → `starting y 1` (border crossing auto-indexes).
   - **c. output tunnels.** `gscript.exit_loop()` on the placed kernel for `X pos 1`, `Y pos 1`,
     `Z pos 1` — three outputs, NOT four (`cal image slice, bead 1` is front-panel-only; including
     it raises 5001). This op is structurally verified (3 tunnels + 3 wires, auto-indexed glyph
     confirmed at 12× zoom).
   - **d. connector pane** to match today's four-fold pane exactly (see
     [PLAN_kernel_parallel.md](PLAN_kernel_parallel.md)), so the result is a drop-in replacement.
   - **e. save the assembled kernel** — no assembly run has ever saved its target.
   - **f. functional verification** (see the two-levels section): synthetic smoke first, then the
     offline-fixture numeric comparison against the existing four-fold kernel. **Only after (f)
     may the main VI be touched, and that swap needs user confirmation.**
5. **Measure per-stage timing** on a **copy** of the main VI (ARCHITECTURE §10 — higher-leverage
   than more parallelisation). **The user runs this** — it touches hardware.
6. **Maintenance — ALL THREE DONE 2026-08-29 late:** ① CLAUDE.md diet done (rules + trigger
   sentences kept; stories → `archive/2026-08-29-claude-md-incident-stories.md`); ② STATUS sweep
   done (narrative → `archive/2026-08-29-status-sweep-opexitloop-opwireind.md`); ③
   **`tools/op_selftest.py` exists and ran: 7 PASS / 2 WARN / 0 FAIL** — no silent failure paths
   in the fleet. Run it whenever an op or wrapper changes. The 2 WARNs are loud-but-fragile
   (failure surfaces as a modal dialog the watchdog dismisses after ~8 s, not as error data):
   `OpSubVI_v1` on a nonexistent subVI path, and `OpDeleteByLabel_v0` on a label that matches
   nothing. Backlog: give those two proper error chains (or accept the watchdog as their catcher).
   Also fixed: `gscript.count()` now checks `_err` like `report()` does.

**At project wrap-up (user, 2026-08-28 — deferred):** make the project reproducible on a fresh PC:
zip `user.lib\claudeDev` into `archive/`; write `SETUP.md` (LabVIEW 2026 + VI Scripting +
erdosmiller via VIPM; Ollama + UI-TARS two-`FROM` import; Node.js + codex/agy + login;
`Set-ExecutionPolicy RemoteSigned`).

## Do not re-attempt

- **A generic node creator via `New VI Object`.** Settled; use a donor VI.
- **Brute-forcing `style` codes.** 0–399 swept, nothing created; NI warns it can crash LabVIEW.
- **Selecting a structure's border by simulated click on a dense diagram.**
- **Verifying wiring or containment by screenshot.** Use the reporter — user-ruled.
- **Identifying what an Op just created by position.** Use uid set difference.
- **Restarting LabVIEW as the *first* move when COM hangs.** Run `-Action dialogs` first — it is
  usually a hidden modal dialog, and that is a two-call fix. **But the "always a dialog" rule was
  falsified on 2026-08-29:** a wedge with *no* dialog (Run blocked ≥180 s, property reads instant,
  no VI running, Abort → 0x3E8) was cured only by a restart, and restarts now carry standing
  permission. So: scan first, restart without hesitation when the scan is clean.
- **`SaveInstrument` on a BROKEN VI** — blocks indefinitely.
- **Dispatching parallel scripting jobs over ActiveX** — every caller gets the same base VI.
- **Capturing a popup/dropdown menu with a window-only capture** — full-screen `shot` only.
- **`Diagram > CleanUp` on a dense real diagram.**
- **Asking an op to edit its own .vi while it runs** — silent no-op; drive a file-copy instead.
- **Raw click-click wire gestures** — use `lv_gui.ps1 -Action wire` (approach+settle) or scripted
  wiring; a failed gesture leaves a pending band that blocks all COM until Esc.

## Resolved facts

- **Base VI: `Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi`** — user-confirmed 2026-08-26.
- **Why the existing kernel is sequential:** the one-fold kernel's result arrays terminate in
  **shift registers** — a loop-carried dependency that makes parallelism illegal; that is why the
  four-fold kernel's `P` terminal exists but sits unwired. Fix: auto-indexed output tunnels.
- **`P` is not a thread count.** Static instances are compile-time duplicates; runtime `P` selects
  how many run, on a pool sized from the CPU (i5-10500, 6C/12T here → P=4 is the sensible start).
- **Error 1054 = "The specified object was not found"** (`resource\errors\English\LabVIEW-errors.txt`
  — read NI's shipped error text before theorising).
- **`Traverse for GObjects` returns GObject references** regardless of the Class Name filter — a
  `To More Specific Class` cast is mandatory before `Get Outputs`/`Wire Inputs`.
- **TopLevelDiagram inherits Diagram** (`Generic▸GObject▸AbstractDiagram▸Diagram▸TopLevelDiagram`),
  and a `Diagram` traverse returns the top-level too — one cast constant covers both.
- **A For Loop's `N` terminal reports as class `Tunnel`** (and `P` adds a second when parallelism
  is configured). **Data tunnels report as `LoopTunnel`.** Counting `Tunnel` to prove a data tunnel
  was created is the mistake that hid a silent no-op for days — count `LoopTunnel`.
- **Wiring a source OUTSIDE a structure to a sink INSIDE it auto-creates the tunnel** (auto-indexed
  for arrays, plain for scalars). This is how `OpLoopKernel_v0` feeds the loop body, and it is
  simpler than asking the library for tunnel refs.
- **GUI-control model choice: strongest available.** Haiku 0/3, Sonnet 2/3, Opus 3/3, Fable 3/3
  (see [BENCHMARKS.md](archive/BENCHMARKS.md)).
