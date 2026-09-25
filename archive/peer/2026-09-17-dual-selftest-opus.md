---
type: peer-review
status: historical
date: 2026-09-17
tags: [peer-review, archive, labview]
disposition: legacy
legacy_note: closed as legacy 2026-09-25 by card chat-L1 (cutoff 2026-09-22; user 2026-09-25 lint order before runner resume)
---

# dual-selftest-opus

- **agent:** claude
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** fact
- **cost:** $1.8621  in 10 / out 4581 / cache-create 158866 / cache-read 258782  (70s, 11 turn(s))
- **date:** 2026-09-17
- **outcome:** ANSWERED (74s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

SELF-TEST of peer.ps1's new -Dual switch. This is a pure factual question with no LabVIEW content and no
framing to attack; answer it in at most three sentences.

QUESTION: In LabVIEW VI Scripting, what does the `Wire` class property with short name `6371004` report, and
what is the short name of the `Wire` class property that returns the wire's terminals? Name your source.



## Answer

**Answer (3 sentences).**

`6371004` is the **`Wire` class `Is Broken?` property** — a read-only VI Scripting boolean that returns TRUE when the wire is broken or in a bad state; strictly it is a property **ID**, not a "short name" (the short name this machine prints on the property node is `Broken?`, `docs/NAMES.md:357` — note `docs/NAMES.md:888` writes it as `Is Broken?`, an in-house inconsistency worth reconciling). The wire's terminals property is **`Terminals[]`, ID `6371003`, short/data name `Terms[]`** — element 0 is the source terminal when a valid source exists, the rest are unordered, and more than one source in the list *is itself* the broken condition. Sources: [LabVIEW Wiki — Wire class](https://labviewwiki.org/wiki/Wire_class) and [Wire class/Terminals() property](https://labviewwiki.org/wiki/Wire_class/Is_Broken%3F_property); locally `docs/vi-server-ids.json:59-60` and `docs/NAMES.md:357`.

One reviewer's note outside the three sentences: `docs/vi-server-ids.json:111` still labels `Wire.Is Broken?` **UNVERIFIED**, while `docs/NAMES.md:888` and `tools/bench/build_opconnectfromwire_v0_run2.log:89,103` record it built and measured (False on a good wire, True on a two-source wire) — the JSON registry is stale relative to the machine's own record.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
