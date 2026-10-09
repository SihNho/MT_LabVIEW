# Brief chat-D2 - Claude-GPT discussions inside the runner loop (user 2026-10-09: "둘 다 넣자")

Read first: docs/debate.md (what the discussion is and how it runs), docs/script-writing.md (shared functions, no copies).
The user, after two live discussions today ("지금의 디스커션 방식이 너무 훌륭함"), asked whether it belongs in the loop;
the chat proposed TWO places that REPLACE a single-model judgement (no new layer - today's discussions concluded the
system grew by adding layers), and the user approved both.

## 1. Outcome review -> discussion (every 5 cycles, where outcome_review.py runs now)
- `tools/cycle_runner.py` (gates_due / outcome hook, ~:906-940): when the outcome review is due, run a discussion
  instead of `outcome_review.py` (keep outcome_review.py as the FALLBACK when the discussion errors).
- Topic built by code (a shared function, e.g. `tools/debate_topics.py outcome(...)`): the goal (docs/goalmap.json),
  what the last 5 cycles delivered and cost (runner log CYCLE lines, cycle cards / adopted claudeDev files), STATUS NEXT,
  previous steer cards and outcome verdicts, open decisions_pending; question = did the work move the deliverable, is the
  plan heavier than the goal needs, what should the next 5 cycles change. Rule: read sources, not summaries.
- Result -> the existing channels: a `steer/1` card for the next cycle built from the agreed items (the judgement session
  follows or refuses with evidence - existing protocol), and one decisions_pending item per `user_needed`.

## 2. Stuck -> discussion (before the next cycle starts)
- Triggers (already detected by the runner): `HANDBACK-LIMIT` reached in a cycle, or the firefighter trigger (same
  failure two cycles running). Run a discussion BEFORE the next cycle; topic = the hand-back records / failing logs'
  first failing lines / the purpose, question = why is it stuck and what should change (plan, order, tool, or stop).
- Result -> a steer/1 card for the next cycle (+ decisions_pending for user_needed). The firefighter ladder stays as is
  after it (the discussion informs; it does not replace the safety rungs).

## 3. Running a discussion from the runner
- `tools/debate_gdoc.py run --mode rounds` with NEW options: `--max-rounds N` (default 6) and `--auto-end` (on converged /
  repeating / max-rounds: finish instead of waiting for /continue) and `--summary <json>`: writes {converged, rounds,
  agreed(both), open, experiment, user_needed, claude_usd, doc_url} from the two final STATE lines.
- Synchronous inside the runner between cycles, with a hard deadline (e.g. 40 min, bgrun-style kill + STOP file) and a
  logged line `DEBATE | <time> | cycle N | outcome|stuck | doc <url> | rounds r | converged y/n | $x`. The doc link must
  reach the user through the existing report path (heartbeat / runner-cycle-report reads the runner log).
- The user may step in from the chat: the relay dir is tools/bench/debate/<slug>/relay (slug e.g. c160-outcome); the chat
  forwards with `debate_gdoc.py say`. Document this in docs/debate.md ("in the loop" section).
- Env for the runner's process: PYTHONPATH (Claude MSIX LocalCache site-packages, as tools/debate_start.ps1 sets) and
  GOOGLE_OAUTH_CLIENT_FILE; if Google auth fails (7-day expiry), write the discussion to local files only, log
  `DEBATE-NO-DOC`, and put a decisions_pending item asking the user to run `debate_gdoc.py login` - never block the runner.

## Proof (offline, labview none; the runner is stopped)
- Self-tests with stub speakers and a FakeDoc: outcome-due -> discussion runs -> steer card + decisions_pending written;
  stuck trigger -> discussion before the next cycle; Google auth failure -> local-only path, runner continues; deadline
  kill works; existing runner self-tests green (selftest_assign_flow, cycle_runner ff self-test, protocol steer tests).
- Docs: CLAUDE.md §5 outcome-layer paragraph gets one sentence (outcome review = Claude-GPT discussion from 2026-10-09,
  outcome_review.py = fallback) + §3 one sentence for the stuck discussion; docs/debate.md "in the loop" section. PD in
  docs/d1/ topic file per the doc rule. Commit by explicit path.

## Limits
labview none, hardware none, Edit/Write only. `tools/hooks/**` only if a hook must learn the new log line (say which,
and keep the change minimal). Return one result/1 JSON.
