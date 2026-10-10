---
name: claude-subsessions-join-the-peer-pool
description: "The user's direction of 2026-09-15 — Claude sub-sessions must participate in peer review alongside Codex and Gemini, dispatched through the same tools/peer.ps1 path so they are archived and gated like any other peer"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 1c79eb01-7150-4a78-9689-e6d4f34f7800
  modified: 2026-09-15T06:21:22.358Z
type: decision
status: in-force
date: 2026-09-15
source: memory/claude_subsessions_join_the_peer_pool.md
---

# Claude sub-sessions are peers too, not just Codex and Gemini

On 2026-09-15, while the peer-review structure was being explained, the user said:
*"클라우드 하위 세션도 peer review에 참여시키는게 좋겠어. 세션 추가 필요"* — Claude sub-sessions should
take part in peer review as well, and a session for that has to be added.

Until then the peer pool was exactly two external agents, `codex` and `gemini` (agy), both running on cheap
subscriptions that can cut out mid-session. That made the review structure fragile in a way the project's own
research ladder already admitted: when both peers are quota-exhausted, the fallback was "Claude runs the research
itself" — an informal escape rather than a reviewer with the same standing as the others.

## What this means in practice

- A Claude sub-session is a **third `-Agent` value of `tools/peer.ps1`**, not a separate mechanism. Rule 5's
  "dispatch only through peer.ps1 — nothing else validates" still holds, because everything that makes a review
  count hangs off that script: the read-only enforcement, the hard timeout, the ANSWERED/TIMEOUT/QUOTA/ERROR
  classification, and above all the archived file in `archive/peer/` whose mtime is what `guard_peer.py` checks
  before letting the next build run. A review dispatched any other way is invisible to the gate.
- It must be **mechanically read-only**, the same as the other two — a peer that can edit files or drive LabVIEW
  is no longer an adviser, and rule 5 keeps all execution with the main session.
- It should run a **different model or a different effort level from the session asking the question**, because
  the whole point of a peer is an independent attack on the framing; a reviewer that is a copy of the asker
  mostly agrees with it.
- The adversarial framing rule applies unchanged: ask it to **refute**, never to "briefly confirm".

## Its ROLE, decided the same day after discussion

The user chose option A of three: the Claude peer is this project's **rule and consistency auditor**, on
`sonnet`, and explicitly *not* a third framing adversary. The reasoning was that it is the weakest peer at the
core adversarial job — it shares the asker's priors — but the only one that natively understands the project's
own rules, so it is the best reviewer for *does this claim match what our files actually say, and does this plan
violate a rule in CLAUDE.md*. That job was previously done by nobody; cycle 7's `rule-evaded` finding was caught
after the fact by a retrospective, never prevented.

Two consequences that follow from the role, both now in code:

1. **A claude-only review does NOT discharge a failed prediction.** `guard_peer.py` requires the lifting exchange
   to come from codex or gemini. Dispatch the claude audit as well when it helps — it just cannot be the thing
   that opens the gate.
2. Because it spends the **same subscription as the main session** (codex and agy do not), prefer the external
   peers while they are available, and reserve `-Model opus` for a question that earns it.


## Why this is worth keeping

The peer's job in this project is to attack a diagnosis formed under pressure. That job should not stop because
an external subscription ran out of quota — and it should not quietly degrade into the asker reviewing itself.
Adding Claude to the pool makes the review structure survive quota loss with its mechanics intact.
