---
name: devils-advocate-before-acting-on-a-diagnosis
description: "A failed prediction is the mandatory trigger for peer review — which means multi-agent search AND monitoring AND the advocate pass, never just one, and never replaced by your own successful test"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 7b982769-ee4e-45be-8846-85edbec23e37
  modified: 2026-08-30T05:36:32.659Z
type: decision
status: in-force
date: 2026-08-30
source: memory/devils_advocate_before_acting_on_a_diagnosis.md
---

# When a hypothesis fails, peer review is mandatory — and it has three parts

Two instructions from the user, given a day apart, that combine into one rule.

**2026-08-29:** *"외부 검색만이 아니라 자체적으로 devil's advocate이 필요하겠는데"* — external search
alone is not enough; argue against your own conclusions.

**2026-08-30:** *"가설을 세워서 결과와 맞지 않으면 피어리뷰 과정을 필수로 넣자. 내가 말한 피어리뷰는
멀티에이전트 검색 및 감시, 더해서 advocate 과정이야"* — **make peer review mandatory whenever a
hypothesis does not match the result**, and by peer review the user means *multi-agent search and
monitoring, plus the advocate pass*.

So the trigger and the composition are both fixed:

- **The trigger is a failed prediction.** Not "a hard problem", not "a big decision" — the specific
  moment when you predicted X, observed not-X, and are about to explain the gap. That explanation is
  a fresh hypothesis formed under time pressure, and it is the one most likely to be wrong, because
  the evidence that would test it is exactly the evidence you just discovered you lacked.
- **All three parts run, not whichever is convenient.** Multi-agent *search* (a peer, or Claude's own
  web session if peers are exhausted) attacks ignorance. *Monitoring* — watching the dispatched work
  and classifying its outcome rather than assuming it answered — keeps the search honest; a peer that
  timed out or hit quota has told you nothing. The *advocate* pass attacks false knowledge: name an
  alternative cause, name what would falsify the current story, run the cheapest discriminating test.

## The failure modes — all observed on 2026-08-30

**1. Comparing options is not a discriminating test.** Choosing between three designs, Claude weighed
them and picked the one needing fewest nodes. That felt adversarial but wasn't: the rejected option
was dismissed on an **unverified factual claim**, and the thirty-second test that would have
falsified it was never run. When it finally was, the rejected design turned out to need one op, not
three. *Name what would falsify the hypothesis, then run the cheapest test that separates the
candidates.* A preference between options, however carefully argued, is not that.

**2. A decision written into the docs stops being a hypothesis.** The rejected design had been
recorded in the project status file as "chosen" days earlier, so it read as established context
rather than as a claim to attack. **Anything marked decided must stay re-openable** — especially when
the work hits friction, which is the signal that the decision may have been wrong.

**3. Your own successful test does not discharge peer review.** Claude ran a genuine discriminating
test, watched a load-bearing hypothesis die, reversed the project's direction, changed a tool, and
wrote a new plan — **dispatching no peer at any point**. The user's question, *"피어리뷰 판단은
어땠어"*, exposed it. A self-run test confirms *the experiment you thought to run*; the peer's job is
to attack **the framing** — whether the API really lacks that capability, whether another cause
explains the same failure, whether the replacement design has a flaw you are not looking for. Both
are required, and passing the first is exactly when it feels safest to skip the second.

## A health check

**If the user is the one raising the objections, the pass is not running.** On 2026-08-30 the user
supplied all four: the misread bandpass parameter, the GUI regression, the advocate's own failure,
and the missing peer review.

A peer used as the adversary must be asked to **refute, not confirm**: "is this right?" invites
shared-prior agreement; "attack this diagnosis — what else explains these symptoms?" is the useful
dispatch.
