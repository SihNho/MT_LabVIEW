---
type: narrative
status: historical
date: 2026-08-29
tags: [archive]
---

# Incident stories moved out of CLAUDE.md — 2026-08-29 diet

CLAUDE.md keeps every rule and its trigger sentence; the full stories behind them live here.
Each section names the rule it supports. Nothing here is normative on its own — if this file and
CLAUDE.md ever disagree, CLAUDE.md wins.

## Rule 1 — the 2026-08-25 near-miss that set the standard

`4.5_KimLabMTroom_3StateClamping.vi` ended up open with a `*` (unsaved changes) during exploratory
menu-clicking. It was closed without saving and the on-disk file's MD5 was verified unchanged
before continuing. No content was actually at risk — the file was never saved — but this is the
standard being held to, not a one-off: close without saving, verify the checksum, never save "just
to check".

## Rule 5 / external search — the incidents that made it mandatory

The error being stamped out is **false confidence from local evidence**: a `--help` listing does
not enumerate interactive slash commands, a config schema does not describe runtime behaviour, and
concluding "there is no way to do X" because the material at hand did not mention X was wrong
twice in one day (2026-08-28).

The 2026-08-29 incident that added the trigger sentence for claims about our own tools: Claude
declared LabVIEW terminal wiring un-scriptable and clicked through it by hand for a dozen calls,
while `Conditionally Connect Wire.vi` — built for exactly that — sat in a library listing printed
earlier in the same session. A limit of your own toolkit is a factual claim, not settled
knowledge.

Earlier incidents with the same shape: a LabVIEW error code (1054) chased through five experiments
and hundreds of parameter values when one forum query held the answer; a claim that codex quota
could not be inspected when the TUI has `/status` for exactly that.

## Rule 5 / research ladder — why agy lost file access (2026-08-29)

agy's permission syntax could only be made to work as `read_file(*)`, which grants the **whole
machine**. Both documented narrowing forms were tested and both denied even the project's own
files: `read_file(/Codes/.../V6_ParallelLoop)` (the drive-letter-stripped form agy.dev prescribes
for Windows) and `read_file(.)` (workspace-relative). agy.dev documents no Windows example.
Rather than leave the machine open for a capability that was not being used — every agy dispatch
so far has been web research — `read_file` was removed from
`~/.gemini/antigravity-cli/settings.json`, leaving `read_url(*)` alone. Revisit only with a
verified narrow form. (The preceding seven-failure permission saga and its sandbox-overlay root
cause: `archive/peer/2026-08-28-perm-allowlist-test*.md` and the Machine/file state note in
STATUS.md.)

## Rule 5 / peers — dead ends to include in "already ruled out" blocks

This project's known dead ends that a peer will otherwise confidently re-propose:

- the `style` 0–399 sweep that failed and that NI warns can crash LabVIEW;
- the generic node creator abandoned at error 1054 (`New VI Object` is not a node factory);
- the *retracted* "killing a COM client wedges the VI" diagnosis — the real cause was hidden
  modal dialogs, found by the enabled-window scan.

Opening `archive/` to peers is the wrong fix — it is narrative, still contains the retracted
claims, grows without bound, and every file a peer reads is data leaving this machine. Selecting
what matters is the manager's job: a short "already ruled out" block, ~three lines, chosen for
the question.
