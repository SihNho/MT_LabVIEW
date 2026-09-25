---
type: peer-review
status: historical
date: 2026-09-17
tags: [peer-review, archive, labview]
disposition: legacy
legacy_note: closed as legacy 2026-09-25 by card chat-L1 (cutoff 2026-09-22; user 2026-09-25 lint order before runner resume)
---

# dual-selftest-codex

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** fact
- **cost:** 
- **date:** 2026-09-17
- **outcome:** ANSWERED (26s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

SELF-TEST of peer.ps1's new -Dual switch. This is a pure factual question with no LabVIEW content and no
framing to attack; answer it in at most three sentences.

QUESTION: In LabVIEW VI Scripting, what does the `Wire` class property with short name `6371004` report, and
what is the short name of the `Wire` class property that returns the wire's terminals? Name your source.



## Answer

Property ID `6371004` (“Is Broken?”) returns `TRUE` when the wire is broken or in a bad state. The terminals property’s short name is `Terms[]`; source: [LabVIEW Wiki Wire class](https://labviewwiki.org/wiki/Wire_class) and [Terminals[] property](https://labviewwiki.org/wiki/Wire_class/Terminals%28%29_property).

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
