Codex-Claude bidirectional harness setup

The user requests starting a multi-round discussion about the current Codex-Claude bidirectional setup. Discuss in Korean under docs/debate.md and docs/decisions/claude_gpt_debate_live_gdoc.md. Both participants are peers; question, rebut, and revise positions across rounds. The user watches live and may intervene through the coordinating chat.

READ ONLY: no source modifications, no LabVIEW, hardware, runner start, or implementation. This discussion is not authorization to execute its conclusions.

Read original source, not summaries. Shared evidence: docs/START.md, AGENTS.md, STATUS.md, docs/guardcore.md, .codex/hooks.json, .claude/settings.json, tools/hooks/guardcore.py, tools/hooks/adapt_codex.py, tools/hooks/adapt_claude.py, tools/debate_relay.py, tools/debate_gdoc.py, tools/debate_loop.py, tools/protocol.py, tools/bench/cards/result_chat-X2.json.

Questions: What currently works versus remains unverified? How should the representative chat call both CLIs with the same rules? How should hook trust, normalized tool and agent identity, duplicate checks, and encoding errors be handled? How should individual completed messages become visible without waiting for the other speaker? How should user interventions and immediate stop work? How can unilateral proposals be kept distinct from jointly approved decisions?

Observed in the coordinating Codex chat: ASCII read commands passed through guardcore; attempts containing Korean characters were denied before process creation with UnicodeEncodeError involving surrogate characters. Do not repeat model identity claims as proof of backend model availability. Distinguish code inspection, fake tests, and real tool-path tests. Verify current files because changes may be ongoing.

Conclude with keep / simplify or change / discriminating experiment, concrete smallest next actions and remaining uncertainties. No automatic implementation. Follow the existing STATE format. Keep discussion open for user participation; no auto-end.
