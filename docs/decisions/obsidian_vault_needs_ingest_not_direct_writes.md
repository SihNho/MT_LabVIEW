---
name: obsidian-vault-needs-ingest-not-direct-writes
description: "The user's 2026-09-21 correction — never drop files directly into the Obsidian-비서 wiki; anything for the vault goes through its own LLM rules and ingest process, and ad-hoc deliverables (figures, data for a talk) go to the Desktop instead"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 0a83e59e-f544-4fdc-ab0b-875dde4859f2
  modified: 2026-09-20T22:29:49.946Z
type: decision
status: in-force
date: 2026-09-20
source: memory/obsidian_vault_needs_ingest_not_direct_writes.md
---

# Do not write directly into the Obsidian-비서 vault — ingest by its rules, or use the Desktop

On 2026-09-21 I generated presentation figures and saved them into a new folder under
`G:\Data\SiHyeong\Dropbox\Obsidian-비서\Knowledge\Presentations\`. The user corrected this:

> "그냥 wiki에 쓰면 안되고, llm 규칙 읽은 후에 ingest해야함. 아니면 바탕화면에 아예 만들어버리는것도 괜찮을듯"

The vault is an LLM-maintained wiki with its own contracts (`AGENTS.md`, `rules/contracts/source-lifecycle.md`,
naming/UID rules, an ingest queue). A file placed there by hand bypasses provenance and lifecycle tracking, which is
exactly what those rules exist to prevent.

## How I apply it

- **Reading the vault is fine** (for example to learn what a talk needs). **Writing into it is not**, unless I first
  read the vault's `AGENTS.md` and the relevant contract module and follow the ingest/admit procedure.
- **Ad-hoc deliverables** (figures, CSVs, README for a presentation, scripts that make them) go to the **Desktop**
  (`C:\Users\KimLab\Desktop\<dated folder>`), not into any vault directory.
- If something I made should end up in the vault, say so and let the ingest process bring it in, rather than
  saving it there directly.
