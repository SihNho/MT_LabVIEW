# Card chat-X1 - common rules, decisions and start procedure (user 2026-10-10 "좋음. 진행하도록")

Runs in the MAIN tree after the runner stopped (cycle 165 finished, STATUS STOP line in force). No LabVIEW, no hardware,
no tools/hooks/** edits (card chat-X2 owns those), do not edit STATUS.md. Read docs/script-writing.md before writing any
script; new tools/ scripts carry the header block at the TOP (# --- / # labview: none / # hardware: none / # ---).

## Why
Claude-GPT discussion token-efficiency-01 (tools/bench/debate/token-efficiency-01/relay/round_16_claude.md and
round_16_gpt.md, STATE agreed) converged: the project must continue from ANY session, Claude Code or Codex, with the same
rules and state, and the fixed start context must shrink (measured 2026-10-10: every runner session starts with 42.7k
tokens of memory files = CLAUDE.md 83,338 chars + MEMORY.md; times 765 turns that was ~30 % of all read tokens in cycle
164). Agreed: common rules, decisions and state live in the repo; CLAUDE.md and AGENTS.md carry only the core
prohibitions and the reading procedure.

## Deliverables
1. Decisions into the repo: read every file in
   C:\Users\KimLab\.claude\projects\G--Codes-LabVIEW-Codes-MinLab-zz-LabView-VI-AAA-UNIST-2--Tracking-V6-ParallelLoop\memory\
   (not MEMORY.md itself; do NOT modify that directory). Write docs/decisions/<same-slug>.md per memory file: keep its
   frontmatter fields, add `source: memory/<file>` and `status: in-force|superseded` (superseded only when the file itself
   or a later one says so), body VERBATIM. Write docs/decisions/INDEX.md: one line per decision grouped by topic
   (hardware/motors, originals & computation, LabVIEW technique, runner & sessions, models & cost, reviews & peers, docs,
   reporting & communication with the user); superseded ones in a separate list at the end.
2. Rules: copy CLAUDE.md byte-for-byte to docs/rules/CLAUDE-full-2026-10-10.md (frozen; append a footer only, never insert
   above, so every existing `CLAUDE.md:N` citation maps to the same line N there). Write topic files docs/rules/<topic>.md
   with every rule in force stated briefly (rule, scope, the mechanism that enforces it) and a link to the frozen line for
   history and quotes. Write docs/rules/coverage.md: a table mapping EVERY heading and every bold rule sentence of the old
   CLAUDE.md to its new home (file:line), and tools/rules_coverage.py (labview none) that fails if any heading or bold rule
   of the frozen copy is unmapped. Nothing may be dropped.
3. New CLAUDE.md and AGENTS.md: the same short core in both (target <= 9,000 chars each): hard prohibitions (rule 1
   originals, 1a computation, 1b rig state / motor gate / limits set and released with readback / LabVIEW closed at cycle
   end, 1c no serial on the frame path, 1c'' locals not queues, 2b answer first, 2c finish the cycle, LabVIEW commands
   through bgrun with timeouts, GUI only with recorded exceptions, close every reference, hooks never edited by runner
   cards, never route around a refusal, start/stop only by the user, secrets only in env vars) + "read docs/START.md
   first". The current AGENTS.md is the PEERS' brief: move it to docs/peer-brief.md and update every reference (grep
   tools/peer.ps1, tools/*.py, docs) so peer dispatch still sends the same brief.
4. docs/START.md - the common start procedure for any session (Claude or Codex; chat or runner): rules version (git hash
   of docs/rules), decisions index, STATUS.md, tools/bench/next.json + open cards, unfinished work, latest report
   (tools/bench/heartbeat_latest.md, tools/bench/reports/), tools/bench/decisions_pending.json, who owns execution now
   (runner running? STATUS STOP lines, labview-lock), allowed actions per role (chat / judgement / assignment / material;
   for now a Codex session = read-only analysis and card proposals only, per the discussion).
5. Skill: move the content of .claude/skills/labview-automation/ (SKILL.md + references) to docs/labview/ verbatim; leave
   SKILL.md as a short pointer with its frontmatter so Claude still triggers it.
6. Every tool that reads or cites CLAUDE.md must keep working: grep tools/ for 'CLAUDE.md' (retrospective.py attaches it,
   doc_lint checks file:line citations, outcome / prior-art / ingest prompts, guard messages citing sections). doc_lint:
   citations `CLAUDE.md:N` that no longer resolve resolve against docs/rules/CLAUDE-full-2026-10-10.md (do not edit the
   citing documents). Attachments that need the full rules attach docs/rules/*.md instead of the old CLAUDE.md.
7. Measure: run `claude -p "/context" --model claude-sonnet-5-5 --output-format text` with env BENCH_CELL=1 (timeout
   120 s) and quote the Memory files tokens (before = 42.7k). Report AGENTS.md size. Run doc_lint and
   tools/rules_coverage.py and quote the results. Commit.

Return <= 30 lines: commit hash, files created/changed, coverage result (0 unmapped), doc_lint result, memory-files tokens
before/after, what could not be done and why, OPEN: decisions that belong to the chat (e.g. which decisions you marked
superseded and why).
