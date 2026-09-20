---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, vi-scripting]
---

# opconstvaluen-v1-fail1-connected-wire-short-name

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (40s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

BRIEF ATTACK (LabVIEW 2026 VI Scripting). tools/recipes/build_opconstvaluen_v1.py run 1 (log tools/bench/build_opconstvaluen_v1.log) stopped at a name gate: the property node built for VI Server:Terminal with ID 634A000 (Connected Wire) attached fine but its output terminal is named Wire, not Connected Wire; Constant.Terminal 634AC04 attached with output Terminal as expected and the TMSC branch wire is shared on both ends (543/543). My explanation: scripted property nodes expose the SHORT name of the property as the terminal name (docs/NAMES.md already lists Block Diagram -> Diagram, Terminals[] -> Terms[], Numeric Text -> NumText), and the gate compared against the long name - a recipe naming error, not a wrong property. Fix: gate/wire on Wire. Questions: (1) is that right - the terminal name of a property-node element is the short name (cite the VI Server / labviewwiki naming: long name vs short name vs data name), and is there any case where the short name differs between read and write mode? (2) is 634A000 indeed Terminal.Connected Wire returning a Wire refnum (so GObject.UID 632A813 on it yields the wire UID) - cite; (3) anything else in the remaining chain (Wire -> GObject.UID) likely to fail a name gate: what is the terminal name for GObject.UID 632A813 (UID)? Read-only; cite.

## Answer

Your diagnosis is right: this is a recipe name-gate error, not the wrong property.

1. Property-node elements use the property?셲 displayed short name. LabVIEW Wiki distinguishes:

   - Data Name: programmatic/internal name
   - Short Name: name displayed in the Property Node
   - Long Name: name displayed in the property-selection menus

   Thus property `634A000` has Data/Short Name `Wire`, but Long Name `Connected Wire`; the gate should expect `Wire`. [VI Server naming definitions](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy), [Connected Wire property](https://labviewwiki.org/wiki/Terminal_class/Connected_Wire_property).

   I found no documented case where changing a property element between read and write changes its short name. Read/write changes the terminal direction, while name format is separate. For these two properties this is moot because both are read-only. One caveat: short and long names are localized with the LabVIEW IDE, so text gates are language-dependent.

2. Yes. `634A000` is `Terminal.Connected Wire`; its Data Name and Short Name are `Wire`, and it returns a reference to the connected wire. The property is read-only and VI-Scripting-only. [Connected Wire property](https://labviewwiki.org/wiki/Terminal_class/Connected_Wire_property).

   A Wire is a GObject subclass, so inherited `GObject.UID` applies to that returned wire reference. [Wire class](https://labviewwiki.org/wiki/Wire_class), [GObject UID property](https://labviewwiki.org/wiki/GObject_class/UID_property).

3. `632A813` is `GObject.UID`, and all three names?봁ata, Short, and Long?봞re exactly `UID`. Its output is an I32. Therefore the next gate should expect `UID`; there is no short/long-name mismatch at that step. [GObject UID property](https://labviewwiki.org/wiki/GObject_class/UID_property).

So the expected chain is:

`Terminal --[Wire]--> Wire refnum --[UID]--> I32 UID`

Cheap additional guard: match property ID plus short name, and validate output type/class, rather than relying on the long selection-menu label.

## Sources

(extract from answer)

## What was done with it

Confirmed as a recipe naming error: the gate now expects the SHORT name `Wire` (634A000) and `UID` (632A813).
NAMES.md's short-name list gained `Connected Wire → Wire`, `Terminal → Terminal`, `Numeric Text → NumText`; the
standing rule "gate on ID + short name, never on the menu long name" is recorded there. Rebuild:
`tools/bench/build_opconstvaluen_v1.log` run 2.
