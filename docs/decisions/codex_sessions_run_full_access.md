---
name: codex_sessions_run_full_access
description: The user's 2026-10-10 operating rule - Codex sandboxes fail on this PC, so every Codex session (the user's and Claude-launched ones) runs with full access; the project hooks are the guard
type: feedback
status: in-force
date: 2026-10-10
source: chat 2026-10-10
---

User 2026-10-10: "이유는 모르겠으나 코덱스가 샌드박스를 적용하면 자꾸 에러가 남. 그래서 현재 코덱스 세션 운용할때는 모든 권한 부여하여 샌드박스 나오게 하고 있음. 아마 너가 운용할때도 그렇게 해야할듯"

Measured the same day (card chat-X5): with `-s workspace-write` every allowed write and shell call failed inside Codex with "setup refresh had errors" (also seen 2026-10-09 with read-only), while the project hooks (.codex/hooks.json: guard_bash + guardcore adapt_codex, trusted by the user with /hooks) denied all 8 forbidden sentinel calls.

**Why:** a sandbox that cannot start leaves Codex unable to work at all; the safety layer for Codex is the trusted project hook + the common executor, not the sandbox.
**How to apply:** Claude-launched `codex exec` uses `-s danger-full-access` (debate_gdoc default already; tools/bench/guardcore_fake/codex_live_check.py). OPEN, not changed here: `tools/peer.ps1` still runs the codex peer with `-s read-only` (its "read-only mechanically" promise) - changing it is a rules change for both debaters to agree.
