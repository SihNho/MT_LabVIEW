---
name: review-structure-has-three-layers
description: "The user's 2026-09-15 decision that reviewing hypotheses and cycles is not enough — the project's OUTCOMES must be judged periodically by a peer, because a cycle can be run perfectly and still be the wrong cycle"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 1c79eb01-7150-4a78-9689-e6d4f34f7800
  modified: 2026-09-15T06:21:13.469Z
type: decision
status: in-force
date: 2026-09-15
source: memory/review_structure_has_three_layers.md
---

# Reviewing hypotheses and cycles is not enough: the project's outcomes need their own peer

On 2026-09-15 the user said: *"주기적으로 프로젝트의 성과를 판단하는 피어도 필요하지 않을까 싶은데"* — a peer
that periodically judges the project's results. They were right, and the gap was sharp once named.

The project already had two review layers, and **both of them ask HOW, never WHETHER**:

| layer | asks | fires |
|---|---|---|
| `guard_peer.py` | is this diagnosis right? | on every failed prediction |
| `retrospective.py` | was this cycle run well? | at the end of every cycle |
| `outcome_review.py` | did any of it move the deliverable? | every 5 cycles or 7 days |

A cycle can be executed impeccably — every hypothesis peer-reviewed, every rule honoured, the audit clean — and
still be the wrong cycle to have run. Nobody was asking whether 168 op VIs was the right price for the spine, or
whether the standing work order still made sense after everything that had been learned. **That question cannot
come from the session doing the work**, which is why it has to be a peer's.

## What makes this layer different from the other two

- **Its questions are about outcomes, not process**: what can the user RUN today that they could not before; which
  numbered requirement in `project-requirements/` has not moved since the project began; is the cost-to-product
  ratio defensible; if the user had to run a real experiment next week, would they use the original VI or anything
  this project produced.
- **Its consequence is different, and this is the important part.** A process violation is answered by building a
  mechanical device — that is the project's standing rule. An OUTCOME violation cannot be: no tool fixes goal
  drift. It is answered by making the next cycle a **delivery** cycle, and on repetition by stopping and
  re-planning with the user.
- **The reviewer must be external — never the Claude peer.** "Was this work worth doing" is exactly the question a
  reviewer sharing the asker's priors is worst at.

## The self-refuting risk, which the user pre-empted

The honest first verdict of such a review, in a project that already owns four hooks, a compliance audit, a
retrospective dispatcher and a violation counter, is very likely `tooling-over-delivery`. Building an elaborate
apparatus to hear that would prove the point. So the user capped it: **one script, one dispatch, one line in the
existing gate — nothing more.** Respect that budget if this layer is ever extended.

## The related mechanization decided the same day

Cycle 7's retrospective found peer prompts that said "BRIEF CONFIRM" — the opposite of what rule 5 requires. The
user approved making it mechanical rather than a reminder: `peer.ps1` now **refuses** a task containing
confirm-bait ("please confirm", "sanity check", "do you agree", "확인 부탁") and **appends** a mandatory
adversarial instruction (name the strongest reason it is wrong, an alternative explanation, what would falsify it,
and the cheapest discriminating test). `-Kind fact` exempts a pure API-fact question, which has no framing to
attack. The lesson generalizes: when the rule is about how a question is *phrased*, the phrasing gate belongs in
the dispatcher, not in a session's good intentions.
