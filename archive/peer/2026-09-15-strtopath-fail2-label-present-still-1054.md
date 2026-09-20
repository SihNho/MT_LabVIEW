---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review]
---

# strtopath-fail2-label-present-still-1054

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (69s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS DIAGNOSIS (LabVIEW 2026 VI Scripting over COM, zero GUI). Follow-up to your archive/peer/2026-09-14-strtopath-fail1-move-by-label-1054.md. Log: tools/bench/build_strtopath.log (run 2, 23:58).
NEW FACTS: with the donor panel OPEN, set_node_label(src, 0, 7, 'STP') was applied and READ BACK: node_labels shows uid 194 -> 'STP' (uid 194 = the 'String To Path' primitive). OpMoveByLabel_v0 then STILL raised "Error 1054 occurred at Open VI Object Reference ... The specified object was not found" (screenshot; the front panel behind the dialog is 'Test - Moving Objects Source.vi', i.e. the substituted donor, open). The project's own skill notes for this op (built from NI's 'Moving Objects\Simple Move.vi' example, object chosen by the 'Add Label' string; class-specifier constant retargeted from Node to GObject once) record: 1054 = label not found, 1057 = found but the class constant disagrees. So the NAME lookup failed although Node.Label text reads 'STP'.
MY NEW HYPOTHESIS H6: 'Open VI Object Reference' (name = ..., class = GObject/Node) matches on the object's owned label only when that label is VISIBLE / exists as a real Label object; a primitive function such as String To Path has no visible owned label by default, and writing Node.Label -> Text.Text sets text on a hidden label that the name search ignores. The one prior success labelled a Call Library Function Node in the Saleh-lab VI, which very likely already had a VISIBLE label. COMPETING: H7 - Open VI Object Reference by name searches a different name property (e.g. 'Name' of a Node vs the Label text); H8 - the search only considers certain classes even when GObject is passed (functions excluded); H9 - the op's 'Add Label' comparison trims/requires exact including a trailing newline.
QUESTIONS: (1) NI documentation / labviewwiki on Open VI Object Reference's name matching for block-diagram objects: label text? visible only? case? (2) Is there a scripting property to make a node's label visible (Label -> Text 'Visible' / GObject 'Visible' - IDs?), and would that plausibly fix H6? (3) The sturdier alternative you named, 'TRef Find Object By Label.vi' (vi.lib\Utility\traverseref.llb): its pane (inputs/outputs), whether it finds hidden labels, and how an op would use it to feed the Move (Move VI Object Reference ... 'Duplicate?') - or the simplest known-good route to COPY one primitive between VIs given only its UID (e.g. Traverse -> index -> Move.Duplicate). (4) Name the single cheapest discriminating test between H6/H7/H8. Read-only; do not open LabVIEW; cite what you read.


## Answer

The new evidence does not establish H6. It makes H6 testable, but H7??Node.Label` and the name indexed by `Open VI Object Reference` are not necessarily identical?봱emains at least as plausible. H8 is now the weakest hypothesis.

1. Name matching

NI?셲 clearest statement says that For Loops and Compound Arithmetic functions ?쐆ave names??and can be retrieved by supplying that name to `Open VI Object Reference`. Thus ordinary block-diagram functions are not categorically excluded, which strongly attacks H8. The post does not say that the name must be visible, nor does it explicitly equate ?쐍ame??with `Label.Text`. [NI employee discussion](https://forums.ni.com/t5/LabVIEW-APIs-Discussions/Feedback-Request-Open-VI-Object-Reference/m-p/3401796)

I found no NI or LabVIEW Wiki documentation specifying:

- whether the indexed name is exactly the owned-label text,
- whether the label must be visible,
- case sensitivity,
- whitespace trimming.

Therefore, claims that lookup ignores hidden labels or trims text would be guesses.

NI distinguishes owned labels as actual parts belonging to objects and states they can be hidden without being deleted. That weakens the specific wording in H6 that a hidden label does not ?쐃xist as a real Label object?? hidden owned labels still exist conceptually. It does not settle whether `Open VI Object Reference` indexes them. [NI LabVIEW User Manual](https://download.ni.com/support/manuals/320999e.pdf)

H9 is weak: the same literal `STP` is written and supplied to the lookup, and the UID-specific readback returns exactly `STP`. Unless one op performs undocumented normalization, trailing whitespace is no longer a natural explanation.

My ranking is:

1. H7 or an `Open VI Object Reference` implementation quirk.
2. H6, but specifically ?쐖isibility gates name indexing,??not ?쐔he label does not exist.??3. An op-specific class-specifier/configuration problem.
4. H8 as a general exclusion of functions.
5. H9.

2. Making the label visible

There is a documented `Label.Visible` property. NI uses exactly that property name for changing owned-label visibility. [NI KnowledgeBase](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019KbOSAU)

The correct conceptual route is:

```text
String To Path reference
    ??Label reference
    ??Label.Visible = TRUE
```

Do not set the primitive/GObject?셲 own `Visible` property: that controls the whole diagram object, not merely its label.

I cannot substantiate the numeric property IDs from public documentation, so I would not hard-code a guessed ID. Obtain the exact property-node names/IDs from the project?셲 existing property registry or reporter output.

Would this plausibly fix H6? Yes, and it is the cheapest direct test. But there is no published evidence I found saying `Open VI Object Reference` requires visibility, so it should be treated as an experiment, not a repair.

3. `TRef Find Object By Label.vi` and the UID route

The strongest description comes from Darren Nattinger: `TRef Find Object By Label.vi` wraps recursive traversal, then reads each discovered object?셲 label until it finds a match. That is materially different from relying on the internal name index used by `Open VI Object Reference`. [Darren Nattinger?셲 description](https://labviewartisan.blogspot.com/2009/06/labview-scripting-tip-1-power-of.html)

Because it explicitly reads labels, a hidden owned label should plausibly match?봳he label?셲 text still exists when hidden?봟ut the available documentation does not explicitly confirm hidden-label behavior. That needs one functional check.

I could not find a reliable published connector-pane listing. Do not guess its terminal pane. Request reporter output for:

```text
vi.lib\Utility\traverseref.llb\TRef Find Object By Label.vi
```

At minimum, public descriptions establish that it accepts traversal scope/class plus a label and returns the matched reference/?쏤ound???state; a forum discussion confirms the built-in VI reports `Found? = false` rather than raising an error when no object matches. [NI Community discussion](https://forums.ni.com/t5/LabVIEW/Malleable-wrapper-for-Traverse-for-GObjects/m-p/4154652)

For the present job, the most robust route is simpler than either label lookup:

```text
source diagram Nodes[]
    ??select the reference whose UID == 194
    ??invoke Move on that exact reference
       owner = target diagram
       Duplicate? = TRUE
```

That eliminates label creation, visibility, case/whitespace rules, and name-index behavior entirely. The Move method is known to support copying to an owner in another VI, although it does not return the duplicated object reference. NI community guidance recommends finding the copied object afterward by a unique label when a returned reference is needed. [Move-method discussion](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Scripting-method-Move-add-quot-Moved-Object-Reference/idc-p/2687099)

Here, no post-copy reference appears necessary merely to build `StrToPath.vi`. If one is needed, census the target before and after and take the new UID/reference.

4. Cheapest discriminating test

The single cheapest useful test is:

1. On UID 194, read and record `Label.Visible`.
2. Set `Label.Visible = TRUE`.
3. Confirm UID 194 still reads `Label.Text == "STP"`.
4. Run the unchanged `OpMoveByLabel_v0`.

Interpretation:

- Success: strong support for H6.
- Still 1054: falsifies H6?셲 visibility claim; H7 or an op-specific lookup/configuration defect becomes leading.
- 1057: lookup succeeded, and the op?셲 class specifier is wrong?봫atching the project?셲 established error distinction and attacking both H6 and H7.

This one toggle cannot logically distinguish H7 from every possible form of H8 if it still returns 1054. But the NI Compound Arithmetic example already attacks broad H8. The decisive engineering fix is to bypass the name lookup and feed the UID-selected object reference directly into `Move`.

## Sources

(extract from answer)

## What was done with it

Ranking adopted: H7 first. The recipe (`tools/recipes/build_strtopath.py`) now runs the discriminating test as
plan A — look the primitive up by its OWN name `"String To Path"` with no label write — and the `STP` route as
declared plan B; log `tools/bench/build_strtopath.log` (run 3). If both miss, the next reviewed batch builds the
reviewer's robust route: select the source node by **UID** (Traverse → `Nodes[]` → uid == 194) and invoke
`Move(owner = target diagram, Duplicate? = TRUE)` — no label, no name index. `Label.Visible` is recorded as an
experiment, not a repair (no published evidence that visibility gates the name index).
