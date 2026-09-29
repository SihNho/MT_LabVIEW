# brief chat-B1 — decision bench ("decbench"): build the case set + harness, dry-run, smoke (user 2026-09-29: "벤치 설계 및 실행해보도록")

Rig state 실험중: NO LabVIEW, no camera, no motor, no GUI. Everything here is offline replay of past records.

## Why
matbench v1 measured only MATERIAL work (code writing/running). The user now says the checks at the JUDGEMENT and
PROGRESS level matter more, and named five areas: (1) project steering, (2) troubleshooting/guidance on a specific
problem, (3) peer-review accuracy and efficiency, (4) code writing/execution [= matbench, done], (5) inter-session
communication. This bench covers **(1), (2), (3)**. Census of what exists: docs/chat-handoff.md §4 (2026-09-29 lines).

## Arms (5) — pin model ids, never aliases
| arm | how |
|---|---|
| H  | `claude-opus-5-5`, effort high, one cell |
| XH | `claude-opus-5-5`, effort **xhigh** (never measured on 5.5; first verify the CLI accepts it — a cheap probe) |
| MX | `claude-opus-5-5`, effort max |
| FL | `claude-fable-5-1`, effort low |
| PAR | "parallel agents": 3 independent `claude-opus-5-5`/high cells on the same case (prompt varied only by a lens line: correctness / alternative-cause / what-would-falsify), then 1 `claude-opus-5-5`/high synthesiser cell that sees the 3 answers and must refute before merging. Implemented as separate `claude -p` cells (NOT the Workflow tool), so the runner could use the same shape later. Its cost = sum of 4 cells. |

## Cases — 10, each at a BASE commit where the answer did not yet exist
Reuse `tools/bench/matbench/matbench.py`'s worktree-at-base mechanism, `cell_guard.py` (labview none, peers none,
git history forbidden, every call logged) and `BENCH_CELL=1`. Grep the worktree at base for the answer string: if the
answer is already on disk at base, the case is LEAKED — replace it.

Pick from these candidates (or better ones you find); each needs a known answer that later MACHINE evidence or a
recorded user decision settled, and a rubric fixed BEFORE any cell runs:
- **C1 steering (3)** — give the cell STATUS + current plan at base and ask "is NEXT the right next act? what should
  the next cycle do and why?". Candidates: (a) the pool/queue plan with "full Q_work ⇒ skip the newest read"
  (PD233/234) — known: it violates the user's latest-wins rule already recorded (docs/decisions.md:25, memory-free
  version in the repo at base); (b) 2026-09-16 outcome review "zero runnable experimental VIs" → known answer
  delivery-first; (c) the N-frame plot gate (PD205–209) vs a separate display loop (PD210) — only if the base-commit
  rules make the answer derivable (camera free-runs / display rules); otherwise pick another.
- **C2 troubleshooting (3)** — give the failing log excerpt + code at base, ask "root cause, and the cheapest
  discriminating test". Candidates: (a) cycle 116 L2-R2 Error List loose ends 22 vs pinned 24 (known: 2 pass-through
  nets re-joined; needs a Wire.Joints reader); (b) gscript `_lv_gui` unquoted spaced args ⇒ no Evidence GUI action
  ever dispatched (archive/peer/2026-09-22-c72-guisave-foreground-r2.md); (c) cycle 119's "handles ±100" gate failing
  (known: normal open→save band +176…+684, the gate was wrong, not the build).
- **C3 peer review (4)** — give a plan/claim and ask an ADVERSARIAL review (use peer.ps1's adversarial preamble
  text verbatim). 3 cases with a known defect + **1 clean case with no real defect** (to measure false alarms).
  Candidates: (a) the c121-3 launch-gate time-filter proposal (archive/peer/2026-09-28-c121-3-launch-gate-l4.md);
  (b) the "no writer can address a FlatSequenceInnerTunnel sink" claim (false since cycle 82, STATUS row-D
  correction); (c) the overload branch "skip newest" (distinct wording from C1a, or pick another); (d) CLEAN: a plan
  that was later executed and passed without a defect found.

## Scoring — rubric per case, fixed and md5-pinned before the run
- `must_hit[]` (root cause / key defect / the right next act), `forbidden[]` (known-wrong claims), `bonus[]`
  (discriminating test named). C3 clean case: score = no blocker-level defect claimed.
- Score each answer twice: a mechanical keyword/regex pass (like score.py) AND one blind scorer cell
  (`claude-opus-5-5`/high, arm name and model hidden, answers shuffled) against the rubric → 0/0.5/1 per item.
  Report both; disagreements listed.
- Record per arm-run: score, minutes, usd (from the json envelope), turns, tool calls.

## Repeats and scale
2 repeats per case × arm ⇒ 100 arm-runs (PAR = 4 cells each). Concurrency ≤ 4 cells. Cell cap 30 min.
Rough cost estimate to verify in the dry run: $400–500.

## This card's scope (B1) — BUILD, DRY-RUN, SMOKE; the full run is a separate card after the chat reviews the cases
1. `tools/bench/decbench/`: cases.json (id, category, base commit, inputs copied, prompt, rubric, leak-check result),
   the harness (≤ ~300 lines, reuse matbench functions by import, do not copy), scorer, report writer. Ends with a
   `RESULT {...}` line.
2. Dry run with `stub_claude.py` for all arms (plumbing, worktrees created and removed, leak check).
3. SMOKE: one real run of each arm on ONE case (≈ 8 cells). Report per arm usd/min and whether xhigh was accepted.
4. Return result/1 with: the 10 cases (one line each: id, base commit, known answer, leak check), smoke numbers,
   the projected full-run cost/time, and `open:` for anything the chat must decide. Do NOT start the full run.
