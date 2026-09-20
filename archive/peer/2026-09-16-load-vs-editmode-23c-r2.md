# load-vs-editmode-23c-r2

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-16
- **outcome:** ANSWERED (69s)
- **why asked:** mandatory review of the failed prediction in tools/bench/diag_load_vs_editmode.log (A2b: predicted
  1 object removed after the documented 23C load, observed 0). Third dispatch: codex `load-vs-editmode-23c` hit
  "model at capacity" (7s) and gemini `load-vs-editmode-23c-agy` returned ERROR (19s, headless permission refusal).
- **verdict:** adopted — refutation accepted, published wording corrected in 4 files

## Question

ATTACK this result from tools/bench/diag_load_vs_editmode.log (LabVIEW 2026, VI Scripting over ActiveX). Do not agree first; cite NI or labviewwiki. Be concise - under 500 words.

MEASURED, fresh copy of a small op VI per arm (4 Property objects), identical op (Open VI Reference -> Traverse for GObjects 'Property' -> Index Array -> Invoke Generic.Delete 6327400), index 0:
  A0 nothing first                                               4 -> 4  NOTHING deleted, error (False,0,'')
  A2 read VI 'Block Diagram' (23C) first, no window, then delete  4 -> 4  NOTHING deleted
  A3 VI.OpenFrontPanel(activate=False) first, then delete         4 -> 3  deleted uid 115
  A4 same 23C-loaded panel-less copy, GObject.Move instead        (853,300) -> (853,300) DID NOT MOVE
The 23C read was done by RUNNING a separate op VI (Open VI Reference -> PN VI.Block Diagram 23C -> Nodes[] -> Index Array -> reads) which then RETURNED, so its refnums went out of scope.

CLAIM: a documented diagram load happened and two different mutators were still silently declined, so diagram RESIDENCY is not the variable - the panel/edit-mode/UI context is - and my ensure_loaded() must keep calling OpenFrontPanel.
THE HOLE, attack it hardest: I could not read Metrics:Block Diagram Loaded (292) in this run, so I never proved the diagram was still loaded at delete time. Is a block diagram loaded via the 23C property guaranteed to STAY in memory after the refnum that loaded it is closed and the loading VI stops running? If not, what holds it across a SEPARATE later op-VI run - an open diagram refnum, VI.'Block Diagram Window:Open' (237), an Open VI Reference option flag?
SECOND, briefly: building the flag reader, I created a Property Node class 'VI Server:VI' with items 291/292 (they attached: terminals PanelLoaded, DiagramLoaded) and wired its 'reference' by BRANCHING an Open VI Reference node's 'vi reference' output via Terminal.Connect Wire 6349C03 -> wire-count delta 0 and ExecState 0 (BROKEN). Is delta 0 consistent with a successful branch, or does a branch always add a Wire object? What breaks a VI in exactly this shape?
ALREADY RULED OUT: wrong method ID (6327400 confirmed); op VI broken (ExecState 1); target running/reserved (idle fresh copy); error reporting (Generic.Delete has no semantic return value; cluster read (False,0,'') even in the SUCCESSFUL A3).

--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

1. **Strongest reason the claim is wrong:** A2 did not establish diagram residency at mutation time. NI says references opened by a top-level VI are automatically closed when that VI becomes idle, and the referenced object may then be disposed immediately or asynchronously. Thus the separate loader returning creates an unload race; “23C was read earlier” proves only transient loading, not residency during Delete/Move. [NI: Closing References in LabVIEW](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html)

No documented Open VI Reference flag pins the diagram: `0x01` means “record modifications,” while `0x20` only hides loading dialogs. [NI option flags](https://www.ni.com/docs/sw-UG/csh?context=lvcore_lvhowto_combining_options) A live VI/diagram-child reference should retain the parent until closed; alternatively, `Block Diagram Window:Open=True` explicitly loads both diagram and panel, but introduces UI state and therefore is a confounded test. [LabVIEW Wiki: BDWin.Open](https://labviewwiki.org/wiki/VI_class/Block_Diagram_Window.Open_property)

2. **Alternative explanation:** A2/A4 reached the mutator after LabVIEW had discarded the transient diagram representation. A3’s open front panel kept the target resident long enough—or altered editability—so mutation worked. Another untested variable is opening the target with `0x01 Record modifications`; the current evidence does not isolate it from front-panel state.

3. **Observation that would falsify the claim:** With no panel/window ever opened, keep the 23C-returned diagram or child-object reference live through the mutation, verify `DiagramLoaded=True` immediately before it, and observe Delete or Move succeed. That would show residency—not UI context—was sufficient. Conversely, `DiagramLoaded=True` immediately before a still-silent mutation would defeat the unload alternative and materially strengthen the claim.

4. **Branch question:** Wire-count delta zero is compatible with a successful branch: one wire has one source and multiple sinks, and branches are segments/junctions rather than necessarily new Wire objects. [NI wiring model](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html) Method `6349C03` accepts a terminal or node as its source. [LabVIEW Wiki](https://labviewwiki.org/wiki/Terminal_class/Connect_Wire_method) ExecState 0 cannot identify the fault; likely causes include an unconnected required reference terminal or an incompatible/broken wire, which NI says must be resolved from the Error List. [NI debugging](https://www.ni.com/en/support/documentation/supplemental/12/debugging-techniques-in-labview.html)

**Cheapest discriminating test:** combine 23C read, `DiagramLoaded` read, and Delete in one op VI, retain the diagram/Nodes reference through an explicit data dependency, and never open either window.

## What was done with it

**ACCEPTED, and it stopped a second over-claim within an hour of the first.** This was the mandatory review of the
failed prediction in `tools/bench/diag_load_vs_editmode.log` (A2b: predicted 1 removed after the 23C load, observed
0). Two earlier dispatches told us nothing and are logged as non-results: codex `load-vs-editmode-23c`
**"Selected model is at capacity"** after 7 s, and gemini `load-vs-editmode-23c-agy` **ERROR (19 s)** — agy refused a
tool permission in headless mode. This third one is the review.

1. **The refutation taken:** *"A2 did not establish diagram residency at mutation time… the separate loader
   returning creates an unload race; '23C was read earlier' proves only transient loading."* NI: references opened
   by a top-level VI are closed automatically when that VI goes idle. My op VI reads 23C, returns, and **its
   refnums go with it** — so A2 may have deleted against an *unloaded* diagram, and my sentence "the variable is
   the panel/edit-mode context" was an inference dressed as a measurement. It has been **rewritten** wherever it
   was already published: `STATUS.md` item 3, `tools/gscript.py:ensure_loaded`, `docs/cycle11-plan.md` Stage 2,
   `docs/toolkit-capabilities.md`.
2. **"Wire-count delta zero is compatible with a successful branch"** — so the flag reader's `ExecState 0` is NOT
   evidence that `connect2` declined, and my explanation (a) was wrong to lead with that. Attempt 2
   (`tools/bench/diag_bdloaded_reader.py`) therefore reads the PN's `reference` terminal wire uid directly instead
   of inferring it from the wire count, samples `ExecState` after every build step, and runs `remove_bad_wires`.
3. **No Open VI Reference flag pins the diagram** (`0x01` = record modifications, `0x20` = hide loading dialogs),
   and `Block Diagram Window:Open` (237) is itself confounded by UI state — so there is no cheap way to keep the
   diagram resident across a separate op run. That kills the "just swap `open_panel` for a headless loader" idea
   as a one-line change and is why `ensure_loaded` keeps the panel call.
4. **The discriminating test it ends with is NOT yet run:** one op VI that reads 23C, reads `DiagramLoaded`, and
   deletes, holding the diagram reference live by data dependency, with no window ever opened. That is a real
   build (a new op), not a diagnostic, so it is recorded as the next step rather than attempted here.

**What survives regardless of how that comes out:** `open_panel` is the only thing measured to make an edit land,
so `ensure_loaded` is unchanged in behaviour; and the decline is general across mutator families (Delete and Move
both, A4).

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
