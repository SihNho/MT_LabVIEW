# Brief chat-G6 - fact questions: Gemini first, Opus fallback (user 2026-10-01: "이렇게 변경하고 진행하자")

Basis: `tools/bench/gsearch/report_g2.md` (8 LabVIEW cases x 2: gemini-3.1-pro-high 13 C / 3 P / 0 W; Opus fact medium
7/8/1, high 6/9/1; but gemini cites a primary ni.com source only 4/16, Opus 16/16; median 143 s vs 99 s). Prerequisites
already in place: web-only gemini brief and per-call empty cwd in `tools/peer.ps1` (cards chat-G3/G4), the user's
hand-set `deny command(*)` in `~/.gemini/antigravity-cli/settings.json`.

## Approved routing (implement exactly this)
1. `peer.ps1 -Kind fact` with NO `-Agent`: run gemini first with `-Model gemini-3.1-pro-high` and a 600 s timeout.
2. If that call ends ERROR / TIMEOUT / QUOTA / empty answer: in the same invocation fall back to the current claude
   fact role (Opus 5.5 medium, thin, web) and archive BOTH exchanges; the archive header states which arm answered and
   why the fallback fired. Exit code = the arm that answered.
3. An explicit `-Agent claude -Kind fact` keeps today's behaviour exactly (this is the "Opus re-check with primary
   sources before an expensive build"). An explicit `-Agent gemini` keeps today's behaviour too.
4. Nothing else changes: hypothesis / priorart / audit / ingest / outcome / prose / retrospective roles, `-Dual`,
   guard_peer's discharge rules (a fact answer never discharges a failed prediction), the read-only guarantees.
   Effort for the claude fact role stays medium.
5. `-DryRun` prints the new two-step route.

## Verify
- DryRun output for: `-Kind fact` (no agent), `-Agent claude -Kind fact`, `-Agent gemini -Kind fact`, `-Kind review`.
- Real calls: (a) one `-Kind fact` web question that gemini answers (no fallback); (b) one forced-fallback call (e.g.
  `-TimeoutSec` very small for the gemini step only, via a test-only switch or env var) showing the claude arm answers
  and both are archived. Record seconds, which arm answered, Claude usd.
- Existing peer self-tests still pass (find them under tools/bench/ - e.g. selftest for peer routing / guard_peer).
- Write `tools/bench/gsearch/g6/verify.log`. Record before/after md5 of peer.ps1.

## Limits
Rig 실험중: no LabVIEW/GUI/hardware; runner stays stopped; do not touch ~/.gemini; do not edit CLAUDE.md / STATUS.md
(the chat does). Edit tool only. git commit allowed for peer.ps1 + gsearch files only. Return one result/1 object.
