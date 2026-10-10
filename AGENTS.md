---
type: rules
status: current
date: 2026-10-10
tags: [rules]
---

# Core rules - every session, Claude Code or Codex

`CLAUDE.md` and `AGENTS.md` are the SAME text (card chat-X1, user 2026-10-10). This is only the core: the rules in
force are in `docs/rules/`, the user's decisions in `docs/decisions/INDEX.md`, the state in `STATUS.md`.
**Read `docs/START.md` first** - it gives the reading order, who owns execution right now, and what your role may do.
A Codex session is, for now, READ-ONLY analysis plus card proposals. Peers dispatched by `tools/peer.ps1` follow
`docs/peer-brief.md`. Old citations `CLAUDE.md:N` mean line N of the frozen `docs/rules/CLAUDE-full-2026-10-10.md`.

## Never - hard prohibitions

1. **Never modify an original file** (rule 1). Every pre-existing `.vi` (the reference VI
   `Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi`, `zz_LabView VI\background VIs\`, anything opened for
   inspection) is read-only. Derived work goes to `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev`
   only. Answer **Don't Save** to every save prompt naming an original; a dirty original is closed without saving and
   its checksum verified. -> `docs/rules/originals.md`
2. **Never change the original's computation** (rule 1a). Only scheduling may change; the per-bead maths, the
   parameters' route and values, and the numbers out stay identical. Acceptance is NUMERIC (same inputs -> same X/Y/Z);
   `ExecState == 1` proves nothing. Cannot show it preserved -> stop and ask the user. -> `docs/rules/originals.md`
3. **Hardware follows the RIG STATE the user announced** (rule 1b; current state: `STATUS.md` hardware banner).
   Disassembled: all. Assembled: camera; motors and the ASI piezo ONLY through `tools/motor_gate.py` inside the
   safe-motion envelope. Experiment running: nothing. The ASI is not a special case. Controller limits are SET at every
   cycle start and RELEASED at every cycle end, each verified by readback, after a real PI reference move. Every cycle
   ends with LabVIEW CLOSED and verified gone. Only the user announces a state change. -> `docs/rules/hardware.md`
4. **No serial / VISA call on the frame acquisition path** (rule 1c) - not even a conditional one.
5. **Control signals between loops travel by LOCAL VARIABLE, never by queue** (rule 1c''); queues only for lossless
   data streams; never detect an edge on a polled boolean; the focus loop copies the original's arithmetic.
6. **Never touch LabVIEW outside the guarded paths.** LabVIEW-touching commands run with a timeout <= 30 s or in the
   background through `py tools/bgrun.py --max-min N --log <file> -- <cmd>` (material runs: `--material`). One LabVIEW
   client at a time (`labview-lock` in `STATUS.md`). GUI actions only where scripting is VERIFIED unreachable, through
   `tools/lv_gui.ps1` with a recorded `-Exception` and `-Evidence`. Close every VI Server reference you open and prove it
   by handle count. -> `docs/rules/labview-execution.md`
7. **Never route around a refusal.** A hook, gate or card flag that refuses you is obeyed: do what it says, or log a
   provable false positive (`py tools/gate_fp.py log ...`) and end BLOCKED. Never set `PEER_GUARD_OFF` /
   `CYCLE_GUARD_OFF` or any bypass env var. **Runner cards never edit `tools/hooks/**`.**
8. **Never start or stop work on your own.** Only the user starts ("지금 진행해") or stops ("멈춰"); silence is not
   authorization; a `STOP` line in `STATUS.md` holds until the user lifts it.
9. **Secrets live only in user environment variables** - never in chat, code, logs or the repo
   (`docs/secrets-and-handover.md`).
10. **Never edit `*.vi`, `*.ctl`, `*.lvlib`, `*.lvproj` as files**, never patch files with a shell heredoc (use the
    editor tools), never attach `.vi` files to a peer.

## Always - how the work runs

- **Answer the user first (rule 2b).** A user message mid-work is answered in the very next reply, first line, before
  any tool call; a yes/no question gets its yes/no first. -> `docs/rules/interaction.md`
- **Finish the cycle (rule 2c).** Once a cycle runs, do everything that does not depend on an open question, proceed
  under a written assumption for the rest, and report once at the end; stop only when proceeding would be unsafe or
  destructive.
- **Keep `STATUS.md` true during the work** (rule 2): LabVIEW is shared with real experiments and the user may reclaim
  it at any moment.
- **Judgement vs material.** Judgement sessions decide; material sessions measure and build within their card's flags
  and return facts (`result/1`), never the result-dependent decision. Failure budget 2; a card returns at its FIRST
  unexpected result. -> `docs/rules/runner.md`, `docs/session-protocol.md`
- **Every new script** starts with its scope header (`# labview:` / `# hardware:`), calls shared functions instead of
  copying them (`docs/script-writing.md`), and ends with a `RESULT {...}` line.
- **Every failed prediction gets an adversarial peer review**; every factual claim about a tool or API gets an external
  search; name the verification level (structural is not functional). -> `docs/rules/reviews.md`
- **Documents are layered**: `STATUS.md` short, facts in `docs/`, narrative in `archive/` (not read in normal work).
  Leave a file at every step - the next session starts from disk. -> `docs/rules/docs.md`
- **Write in plain words; state confidence and evidence; reports the user reads come through the Claude session**
  (`docs/rules/interaction.md`).
