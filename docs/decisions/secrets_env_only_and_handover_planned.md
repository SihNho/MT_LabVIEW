---
name: secrets-env-only-and-handover-planned
description: "The user keeps API keys only in user environment variables (never in chat, code, or the repo), wants the set/delete procedure archived, and plans to wipe their personal data and hand the project to another user later — so personal identifiers must stay out of the repository and be listed for removal"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: b5d0cc76-fda8-4724-8899-5a019fc98595
  modified: 2026-09-21T21:58:34.814Z
type: decision
status: in-force
date: 2026-09-21
source: memory/secrets_env_only_and_handover_planned.md
---

# API keys live in environment variables, and the project will change hands

On 2026-09-22 the user obtained a TypeSafe (Jev) API key. They asked what `setx` is, how to delete the variable
later, and then:

> *"그것도 아카이빙 해줘. 나중에 내 개인정보들은 다 초기화하고 다른 유저로 교체할 것 같거든."*

## How I apply it

- **Keys go only into a user environment variable** (`setx NAME "value"` in the user's own terminal). I never ask
  for a key in chat, never write one into a file or the repository, and scripts read `os.environ[...]` and log only
  presence/length. `.gitignore` carries `*.key` and `.env`.
- **The set/delete procedure is documented in the project**: `docs/secrets-and-handover.md` (setx; PowerShell
  `[Environment]::SetEnvironmentVariable(..., $null, "User")` or `reg delete HKCU\Environment`; revoke at the
  provider's console because local deletion does not invalidate a key).
- **A handover is coming.** Keep personal identifiers out of new project files: no user email, no account name in
  new paths where a relative path works, no personal data in docs. Where they already exist (git config and commit
  authorship set on 2026-09-20, `C:\Users\KimLab` paths in ~68 files, Claude memory and session transcripts under
  the user profile), the same document lists each location and the removal step so the wipe is a checklist, not
  an investigation.
- When the handover happens, the next user starts from `CLAUDE.md` → `STATUS.md` → the current plan; the rig-state
  banner and safety rules stay as they are.
