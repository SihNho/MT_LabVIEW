---
type: peer-review
status: historical
date: 2026-08-28
tags: [peer-review]
---

# wire-indicators-api

- **agent:** codex
- **date:** 2026-08-28
- **outcome:** ANSWERED (137s)
- **why asked:** Before building an error-out indicator for OpWire: does erdosmiller Wire Indicators.vi create indicators or only wire existing ones?
- **verdict:** adopted

## Question

In the GitHub repo erdosmiller/lv-scripting (LabVIEW VI Scripting library, MIT), there is an API VI named 'Wire Indicators.vi' and an example named something like 'Example 1 - Get Controls Wire Indicators'. Please look up the repo (and any docs/readme/example descriptions) and answer: (1) What are the exact inputs and outputs of 'Wire Indicators.vi' - does it take a node refnum and create+wire front-panel indicators for that node's output terminals? Can it target specific named terminals like 'error out'? (2) What does Example 1 demonstrate, step by step? (3) Is there any API in that library for creating a single front-panel indicator wired to one specific node terminal? Cite URLs for everything.

## Answer

The public text documentation does not establish the connector pane or internal behavior of `Wire Indicators.vi`. The authoritative details appear to exist only inside the binary VIs, which I did not open under your safety rules.

1. `Wire Indicators.vi`

- The repository README describes LV?멣cripting only generally as a code-generation wrapper around VI Scripting; it does not document `Wire Indicators.vi` inputs, outputs, or terminal-selection behavior. [Repository README](https://github.com/erdosmiller/lv-scripting/blob/master/README.md)
- Therefore I cannot verify that its input is a node refnum, nor give its exact output terminals, from a text source.
- I also found no textual evidence that it accepts a terminal name such as `error out`. Do not assume that capability merely from the VI?셲 plural name.
- The inexpensive decisive check is reporter output containing the VI?셲 connector-pane control names/types and block-diagram object listing. That would show whether it accepts a node, an array of terminals, or another abstraction, and whether any name/filter input exists.

2. Example 1

The exact title appears to be `Example 1 - Get Controls Wire Indicators`, but the repository provides no prose walkthrough of it. The README says that Examples 1??3 are delivered through the VI Package and should be viewed via VIPM?셲 ?쏶how Examples?? it does not describe their individual steps. [README, ?쏬earning to Use LV-Scripting??(https://github.com/erdosmiller/lv-scripting#learning-to-use-lv-scripting)

Consequently, a step-by-step description cannot be sourced reliably without reporter output from that example. At most, its title suggests that it demonstrates the library?셲 ?쏥et Controls??and ?쏻ire Indicators??operations; claiming that it creates indicators for every output of an arbitrary node would be speculation.

3. Single-terminal API

I found no documented API in the README or release notes for ?쐁reate one front-panel indicator and wire it to this specific node terminal.??[README](https://github.com/erdosmiller/lv-scripting/blob/master/README.md), [releases](https://github.com/erdosmiller/lv-scripting/releases)

That is not proof that no such VI exists?봳he library?셲 API is largely stored as binary `.vi` files rather than documented text. The safe conclusion is:

> No text-documented single-specific-terminal API was found. `Wire Indicators.vi` cannot be claimed to support named-terminal selection without inspecting its reporter output.

To settle all three questions, ask the manager for reporter listings of:

- `Wire Indicators.vi`: connector controls/indicators plus block-diagram objects
- `Example 1 - Get Controls Wire Indicators.vi`: block-diagram nodes and wire endpoints
- A filename/palette listing of the library?셲 indicator- and terminal-related APIs

The project itself explicitly identifies the packaged examples?봭ot the README?봞s the intended API tutorial. [Repository README](https://github.com/erdosmiller/lv-scripting#learning-to-use-lv-scripting)

## Sources

(extract from answer)

## What was done with it

Codex found no textual docs and recommended local inspection - followed. Binary extraction then showed Wire Indicators.vi only wires to EXISTING indicators selected by name; creation is separate (New VI Object handles front-panel objects, proven by DONOR_Ex1's structure). Indicator work deferred to the donor-copy op; OpWire_v1 uses Clear Errors sinks instead.
