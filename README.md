---
type: reference
status: current
date: 2026-09-15
tags: []
---

# Project Wiki — Kim Lab Magnetic Tweezers Tracking Software

Reference wiki for the `2. Tracking` project, written for whoever (human or LLM) picks the work up
next. The source is LabVIEW `.vi` — a compiled binary with no plain-text diagram — so parts of this
wiki were reconstructed by extracting text embedded in those files. **VI Scripting is proven working**
on this machine, so open or script a VI for ground truth whenever wiring or logic matters; byte
extraction is only a fallback for fast offline diffing.

**Documentation is two-tier** (`CLAUDE.md` rule 4): the files listed below are the *active* set and are
meant to be read. Everything historical lives in **[archive/](archive/)** and is **not** part of normal
reading — it is kept in case it is needed, not consulted by default.

## Start here

1. **[CLAUDE.md](CLAUDE.md)** — the hard rules. Never modify an original `.vi`; **never operate the
   ASI piezo stage or the motor**; LabVIEW is shared with live experiments and start/stop is always
   explicit.
2. **[STATUS.md](STATUS.md)** — what is true right now and the next actions.
3. **[AGENTS.md](AGENTS.md)** — if you are a **peer agent** (Codex, Gemini/Antigravity), that file is
   your brief and this one is not: you are read-only, you never touch LabVIEW, and Claude Code is the
   only agent that executes anything (`CLAUDE.md` rule 5).

## Doing the work

- **`.claude/skills/labview-automation/`** — **the single source of truth for LabVIEW technique, and
  it is PORTABLE.** VI Scripting (the `New VI Object` contract, decoded errors, class paths), the
  **COM/ActiveX pipeline**, GUI control (coordinate laws, `probe`, `wire`, menu paths), the
  scripting-library comparison, the **Op-VI architecture**, and the safety rules. Invoke it before any
  LabVIEW work — and copy the directory into any other LabVIEW project or machine, where it works
  immediately.
- **`archive/2026-08-31-plan-kernel-parallel-superseded.md` (superseded; layout since settled)** — the kernel-parallelization thread's plan.
- **[docs/UITARS_GROUNDER.md](docs/UITARS_GROUNDER.md)** — **local, free** GUI grounding with UI-TARS-1.5-7B via
  Ollama: "where is X on this window?" → screen coordinate. Calibrated; needs a zoom pass.
- **[tools/gscript.py](tools/gscript.py)** — **the runner.** Drives the Op-VI fleet over ActiveX to
  build LabVIEW code and verify it, with no GUI at all: `py tools\gscript.py kernel <target.vi>`.
- **[tools/](tools/)** — `lv_gui.ps1` (GUI automation and the `dialogs`/`dismiss` modal-deadlock
  recovery; its header carries hard-won technique), `kb_com.py` (the raw ActiveX layer), and the
  Python extraction scripts.

## Understanding the project

- **[ARCHITECTURE.md](ARCHITECTURE.md)** — subsystems and sub-VI map, the parallel-loop design, and
  **§10 the performance model and the CPU/GPU backend plan**.
- `archive/2026-08-31-overview-lineage-background.md` (background) — what the software and rig do, at a glance.
- [LEARNING.md](LEARNING.md) — **written for the user**, not for an LLM: what was done in LabVIEW and
  why it works, as explanation rather than log.
- [docs/GLOSSARY.md](docs/GLOSSARY.md) — front-panel controls and domain terms, one line each.

## Rules and provenance

- **[docs/REFERENCES.md](docs/REFERENCES.md)** — **citations for every third-party library and example used**,
  with a derivation map showing which of our files came from which original. Add to this whenever any
  borrowed code is used.
- [Requests.md](Requests.md) — the user's original ground rules, in their words.
- [project-requirements/](project-requirements/) — task specs for the V6 build.
- `.claude/skills/labview-vi-analysis/` — packaged form of the byte-extraction technique.

## History (not read by default)

**[archive/](archive/)** — session worklog, the `.vi` version history, concluded benchmarks, the
capability test matrix, superseded option analyses, and the idle Gemini executor. See
[archive/README.md](archive/README.md) for what each file is and why it moved.

One subdirectory has a standing exception: **[archive/peer/](archive/peer/)** holds every exchange
with a peer agent and **is** consulted before asking a peer anything, because re-asking burns finite
subscription quota (`CLAUDE.md` rule 5).

## Ground rules (from Requests.md, expanded in CLAUDE.md)

1. Read/reference `Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi` — **never modify it**.
   (Base VI resolved 2026-08-26: V6 builds on **4.5_3StateClamping**, confirmed by the user.)
2. All paths/references in new work follow that file's conventions.
3. New sub-VIs go in `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev`, never here.
4. Record each change so the work is resumable across chats, sessions and LLMs.
5. **Never operate the ASI piezo stage, and never run the motor.** The stage can collide and break
   parts; the motor was added to the forbidden list by the user on 2026-08-27 (*"우선 모터 가동은
   절대 하지 않는 선에서 계속 처리해"*), narrowing an earlier permission that had allowed it. The real
   hazard is running a VI that drives hardware as a side effect — see `CLAUDE.md` rule 1b.

## Fastest way to get oriented

`CLAUDE.md` → `STATUS.md` → invoke the `labview-automation` skill. Read `ARCHITECTURE.md` and
`docs/` when you need domain context.
