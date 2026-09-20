---
type: peer-review
status: historical
date: 2026-08-28
tags: [peer-review]
---

# archive/peer — every exchange with a peer agent

One file per question, named `YYYY-MM-DD-<slug>.md`. Per `CLAUDE.md` rule 5 **every** exchange is
archived, whether or not it turned out useful — a wrong answer is worth keeping, because it stops the
same question being asked again on finite quota.

Each file holds:

```markdown
# <the question, in one line>

- **agent:** codex | gemini
- **date:** YYYY-MM-DD
- **why asked:** the decision this was meant to inform
- **verdict:** adopted | rejected | unverified

## Question
(exactly what was sent, including which files the peer was told to read)

## Answer
(their reply, verbatim enough to be checkable)

## Sources
(URLs they gave)

## What was done with it
(confirmed against what? which active doc got the conclusion? or why it was rejected)
```

Two rules govern how this directory is used, and they pull in opposite directions on purpose:

- **Rule 4 — not read in ordinary work.** Anything that mattered has had its *conclusion* copied
  into an active document with its sources, so a normal session never needs to come here.
- **Rule 5 — but always checked before asking a peer.** Re-asking burns quota that may be needed
  later in the same session, and the archived answer already records whether it was ever verified.

The `verdict` field is the important one. A peer answer is a hypothesis until something on the
machine or in the vendor's own files confirms it, and `unverified` must not quietly become fact
through repetition.
