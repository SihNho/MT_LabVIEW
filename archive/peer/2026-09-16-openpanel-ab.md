# openpanel-ab

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-16
- **outcome:** ANSWERED (254s)
- **why asked:** before generalising the diag_delete_matrix A/B across the whole toolkit (the conclusion had
  already been inserted into 26 mutating wrappers in tools/gscript.py).
- **verdict:** adopted — its discriminating test was run (tools/bench/diag_load_vs_editmode.log) and it overturned
  the project's stated mechanism; the call it attacked stays, the explanation does not

## Question

ATTACK this conclusion before it is generalised across a whole toolkit. It comes from tools/bench/diag_delete_matrix.log (script tools/bench/diag_delete_matrix.py). Do not confirm it.

BACKGROUND. In LabVIEW 2026 VI Scripting over ActiveX, a scripting op VI (Open VI Reference -> Traverse for GObjects -> Index Array -> Invoke Node Generic.Delete 6327400) was deleting NOTHING: the op ran, returned normally, no dialog, error cluster clean (False,0,''), object census unchanged. You previously told me Generic.Delete has no semantic return value and that NI marks it 'Loads the block diagram into memory: No'.

THE A/B I THEN RAN. Identical op, identical scratch target, identical Traverse class, identical index 0. The ONLY difference is whether the Python driver first invoked VI.OpenFrontPanel on the TARGET:

  without OpenFrontPanel   OpWireSource_v5 copy, class Property   12 -> 12   NOTHING removed
  with    OpenFrontPanel   OpWireSource_v5 copy, class Property   12 -> 11   removed uid 1554
  without OpenFrontPanel   OpFPLabels_v0  copy, class Property     4 ->  4   NOTHING removed
  with    OpenFrontPanel   OpFPLabels_v0  copy, class Property     4 ->  3   removed uid 115

With OpenFrontPanel, a sweep over every class removed exactly one object each: Constant, Property, SubVI, IndexArray, Wire, ControlTerminal. None removed an object of a different class. Error cluster stayed clean in EVERY case, deleting or not.

MY CONCLUSION, which you must attack: the target VI must be fully loaded (block diagram in memory) before ANY scripting EDIT, LabVIEW silently declines the edit otherwise, and the error cluster never reports it. I have acted on this by inserting an idempotent ensure_loaded(target) -> OpenFrontPanel call into 26 mutating wrappers in tools/gscript.py (delete, connect, wire, build_invoke, build_property, create_control/indicator, move, set_label, remove_bad_wires, loops, CLFN, etc.), while deliberately NOT touching the read-only wrappers.

ALREADY RULED OUT: wrong method name (you confirmed 6327400 is correct); the op being broken (ExecState 1); the target running or reserved (idle fresh copy); error-reporting plumbing (Generic.Delete has no return value).

ANSWER THESE:
1. Strongest reason OpenFrontPanel is NOT the real variable here - name a confound that differs between my two arms other than diagram load state. Note both arms ran in the same process, same fresh LabVIEW instance, alternating.
2. Is OpenFrontPanel the RIGHT way to force a full load for scripting, or is there a documented, cheaper or safer mechanism (an Open VI Reference option flag, a VI property, an explicit load method)? Cite NI where you can. I care because opening panels leaves windows open and this project has recorded UI-thread hangs associated with open windows.
3. Is it true in general that LabVIEW scripting EDITS are silently declined on a partially loaded VI while READS (Traverse for GObjects, Property reads, Nodes[]/Terminals[]) succeed? That asymmetry is what my whole patch assumes. If reads can also be silently wrong on a partially loaded VI, a large amount of this project's measured data is suspect and I need to know.
4. Any documented case where OpenFrontPanel on a target is HARMFUL during scripting - reentrancy, run-mode, front panel bindings, or an edit that behaves differently with the panel open.
5. What is the cheapest test that would falsify 'load state is the variable' and support your alternative instead?

--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

The strongest reason the conclusion is wrong is that `OpenFrontPanel` does not isolate diagram load state. It simultaneously changes panel visibility, window activation, and potentially the VI?셲 edit/run-mode presentation. Your experiment therefore proves only:

> `Generic.Delete`, on references obtained through this traversal path, works after `OpenFrontPanel`.

It does not prove that every scripting edit requires the front panel?봮r even that block-diagram loading is the causal change.

1. Strongest confound: edit mode and UI state

`OpenFrontPanel` defaults to `activate=True`; it creates and activates an editor window, not merely loads data. Its documentation makes no claim that it is a block-diagram load primitive. [OpenFrontPanel ActiveX documentation](https://documentation.help/NI-ActiveX-LabView/VI_Open_Front_PanelAX.html)

More importantly, LabVIEW has a distinct `Edit Mode On Open` property: when true, opening the panel puts the VI in edit mode; when false, it opens in run mode. That property must be set before the panel is opened. [NI Community reproduction of the LabVIEW help text](https://forums.ni.com/t5/LabVIEW/Edit-Mode-On-Open-Property/td-p/467770)

That makes **edit-mode transition** the strongest concrete confound. Check it alongside load state; otherwise ?쐂iagram became loaded??and ?쏺I became editable??are indistinguishable.

There is also a narrower alternative that your sweep does not exclude: this may be a `Generic.Delete` plus reference-materialization defect. Both `Traverse` and `Generic.Delete` are classified as **not loading the block diagram**. [Traverse characteristics](https://labviewwiki.org/wiki/Generic_class/Class_Operator.Traverse_method), [Delete characteristics](https://labviewwiki.org/wiki/Generic_class/Delete_method). Opening the panel before traversal may make the returned GObject references ?쐋ive??in a way that makes this particular no-load method work. Testing Delete across six object classes still tests only one mutator and one acquisition path; it does not validate create, move, wire, property-write, or structure-building operations.

A further prerequisite worth auditing is how Python obtains the reference. `GetVIReference` has independent `resvForCall` and `options` parameters:

- `resvForCall=True` explicitly prohibits editing.
- `options=0x01` records VI Server modifications, but requires edit mode.
- The default options value is `0x10`, not `0x01`.

[GetVIReference documentation](https://documentation.help/NI-ActiveX-LabView/GetVIReference.html)

`0x01` is not documented as a load flag, but an uncontrolled reservation/edit-mode difference could masquerade as one.

2. `OpenFrontPanel` is not the right load primitive

There is no documented Open VI Reference option meaning ?쐋oad the complete block diagram.??NI?셲 option list contains record modifications, template editing, save prompting, reentrant-call preparation, missing-subVI prompting, and loading-dialog behavior?봟ut no force-diagram-load option. [NI option-flag table](https://www.ni.com/docs/sw-UG/csh?context=lvcore_lvhowto_combining_options)

The explicit scripting operation is the VI?셲 **Block Diagram property**:

- It returns the top-level diagram reference.
- It is marked ?쏬oads the block diagram into memory: Yes.??- It also loads the front panel into memory, but does not require opening either window.
- It must run when the UI is idle.

[VI Block Diagram property](https://labviewwiki.org/wiki/VI_class/Block_Diagram_property)

So the safer helper is conceptually:

> obtain `VI.Block Diagram` ??close the returned diagram reference ??verify `Metrics:Block Diagram Loaded=True`

The metrics property distinguishes ?쐒esident in memory??from ?쐗indow open?? LabVIEW explicitly says the diagram can be loaded while its window is closed. [VI property table, properties 291??92](https://labviewwiki.org/wiki/VI_class)

That is preferable to leaving activated windows around. `OpenFrontPanel` should remain an empirical workaround until an explicit-load arm proves it necessary.

3. The edit/read asymmetry is not established

No, the evidence does not justify ?쏿ll edits silently fail while reads remain valid.??
LabVIEW documents load behavior per property or method, not by a blanket read-versus-write rule:

- `Traverse`: does not load the diagram and returns `FALSE` if traversal fails. [Traverse](https://labviewwiki.org/wiki/Generic_class/Class_Operator.Traverse_method)
- `Nodes[]`: read-only and explicitly does not load it. [Nodes[]](https://www.labviewwiki.org/wiki/AbstractDiagram_class/Nodes%28%29_property)
- `Terminals[]`: read-only and explicitly does not load it. [Terminals[]](https://www.labviewwiki.org/wiki/Node_class/Terminals%28%29_property)
- `Control.Terminal`: read-only, but explicitly loads both panel and diagram. [Control.Terminal](https://labviewwiki.org/wiki/Control_class/Terminal_property)
- Some writable properties, such as node Description, also do not load the diagram. [Node Description](https://labviewwiki.org/wiki/Node_class/Description_property)

NI defines ?쏬oads the block diagram into memory: Yes??to mean LabVIEW performs the load and returns error 1012 if it cannot. [VI Server characteristic definitions](https://documentation.help/NI-LabView-Local-Project-Settings/documentation.pdf)

Thus the correct model is:

> Every individual API member has its own loading and editability contract.

Your existing read measurements are not automatically invalid. However, every `Traverse`-based reporter should retain and assert the traversal Boolean. Ignoring that Boolean could turn a documented failure signal into an apparently clean incomplete census.

4. Documented harms from opening the panel

`OpenFrontPanel` is not neutral:

- It activates the window by default, altering foreground/UI state. [OpenFrontPanel](https://documentation.help/NI-ActiveX-LabView/VI_Open_Front_PanelAX.html)
- Front-panel redraw/invalidation consumes UI work and can produce lag on complex panels. [NI front-panel performance guidance](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000kHjFSAU&l=en-US)
- A VI configured to run when opened can begin execution on opening, which immediately makes editing illegal. [NI Run When Opened guidance](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019L9GSAU&l=en-US)
- An open front panel conflicts with subpanel insertion; LabVIEW returns an error unless the relevant reentrancy exception applies. [SubPanel Insert VI documentation](https://labviewwiki.org/wiki/SubPanel_class/Insert_VI_method)
- Closing the panel can allow the VI to leave memory when no other reference retains it, so blindly opening and closing panels also changes lifetime conditions. [GetVIReference documentation](https://documentation.help/NI-ActiveX-LabView/GetVIReference.html)

I found no documentation establishing that merely opening a panel changes front-panel bindings or fires value-change events, so I would not claim those effects.

5. Falsification and cheapest discriminating test

The load-state claim is falsified if:

> `Metrics:Block Diagram Loaded` is true before Delete, yet Delete still does nothing until `OpenFrontPanel` is called.

That observation would support a panel/edit/UI-context explanation instead of diagram residency.

The cheapest discriminating test is one extra arm using a fresh copy:

1. Keep the panel closed.
2. Record `Metrics:Block Diagram Loaded`, execution/edit state, reservation state, and traversal Boolean.
3. Read `VI.Block Diagram` once and close only that returned diagram ref.
4. Verify `Metrics:Block Diagram Loaded=True` while `FPWinOpen=False`.
5. Run the unchanged Traverse ??index 0 ??Delete op.

Interpretation:

- **Delete succeeds:** supports the narrow load-state explanation, but still does not justify patching all 26 mutators without representative tests.
- **Delete fails, then succeeds after `OpenFrontPanel`:** falsifies ?쐂iagram load is the variable??and points to edit mode, panel/UI context, or Delete/reference materialization.
- **A second edit such as position/description write succeeds headlessly while Delete fails:** establishes a Delete-specific failure and directly refutes the toolkit-wide generalization.

I do not believe the 26-wrapper conclusion currently holds. I would change my mind after the explicit `VI.Block Diagram` arm succeeds and at least one representative operation from each mutation family?봡elete, create, move/property-write, wire, and structure creation?봲hows the same headless failure with edit mode, reservation, and reference options held constant.

## Sources

(extract from answer)

## What was done with it

**THE DISCRIMINATING TEST WAS RUN, AND THE REVIEWER WAS RIGHT ABOUT THE INFERENCE.**
`tools/bench/diag_load_vs_editmode.py` → `tools/bench/diag_load_vs_editmode.log` (2026-09-16, `BGRUN END rc=0
after 112s`), each arm a FRESH copy of `OpFPLabels_v0.vi`, same raw op, class `Property`, index 0:

| arm | what was done first | result |
|---|---|---|
| A0 | nothing | `4 -> 4  NOTHING REMOVED`, `err=(False, 0, '')` |
| A2 | read `VI.Block Diagram` (23C), **no window** | `4 -> 4  NOTHING REMOVED`, `err=(False, 0, '')` |
| A3 | `OpenFrontPanel(activate=False)` | `4 -> 3  REMOVED ONE  elsewhere={'Property': [115]}` |
| A4 | 23C-loaded, panel-less, **`GObject.Move` instead of Delete** | `(853, 300) -> (853, 300)  DID NOT MOVE` |

A Win32 window census taken inside the run confirms the separation: `afterA2=6` windows, `afterA3=7` — the 23C
route opened none, the panel route opened `ScratchLM_..._A3.vi Front Panel`.

Point by point:

1. **"`OpenFrontPanel` does not isolate diagram load state" — ACCEPTED, and now measured.** The `diag_delete_matrix`
   A/B proved only what this review said it proved. The project's own conclusion ("the diagram must be in memory")
   was an inference laid over a panel-vs-no-panel comparison, and A2 breaks it: the documented load primitive alone
   does not make the edit land.
2. **"The explicit scripting operation is the VI's `Block Diagram` property; prefer it to leaving activated windows
   around" — ACCEPTED as documentation, REFUTED as a replacement.** Reading 23C through an op that already does it
   (`OpNodeInfo_v0`: `Open VI Reference → PN VI.Block Diagram → Nodes[]`) left both `Generic.Delete` and
   `GObject.Move` silently declined. So `gscript.ensure_loaded()` **keeps `open_panel`** — it is what works.
   ⚠️ **But do not promote this into "edit mode is the variable", which is where this session first went.** A
   follow-up review (`2026-09-16-load-vs-editmode-23c-r2.md`) refuted that reach: the 23C read ran inside a
   separate op VI that then returned, and NI closes a top-level VI's references when it goes idle, so the diagram
   may have been unloaded again before the delete. `Metrics:Block Diagram Loaded` (292) is still unread — two
   reader builds failed on a bad wire into the Property Node's `reference`. The *action* is identical under either
   reading; only the mechanism is open.
3. **"The edit/read asymmetry is not established; every API member has its own loading and editability contract" —
   ACCEPTED.** Nothing here generalises to reads. The fleet's readers run on `Traverse` / `Nodes[]` / `Terminals[]`,
   which labviewwiki marks as not loading the diagram, and they have always returned correct censuses on
   unloaded targets (A0/A2 counted 4 Property objects on a target that no edit could touch). The reviewer's
   narrower warning — **keep and assert the `Traverse` Boolean** — is NOT yet done and is recorded as work.
4. **Documented harms of `OpenFrontPanel` — RECORDED as caveats** in `ensure_loaded`'s docstring, since the call
   stays: window activation (mitigated — the project passes `activate=False` since 2026-09-05), a Run-When-Opened
   VI beginning execution and making edits illegal, the subpanel-insert conflict, front-panel redraw cost on
   complex panels, and closing the panel letting the VI leave memory (already recorded in `close_panel`).
5. **"I do not believe the 26-wrapper conclusion currently holds … I would change my mind after at least one
   representative operation from each mutation family shows the same headless failure" — ADVANCED, not finished.**
   Two families now behave identically (`Generic.Delete`, `GObject.Move`: A4), which is what makes "the decline is
   general, not delete-specific" a measurement rather than an assumption. Create / wire / structure-building
   families are still untested against a panel-less target.

**What this cost and what it bought:** one 112 s run; it overturned a conclusion that had already been written into
26 wrappers and into `STATUS.md`, and it did so before that conclusion was used to justify removing the call that
actually works. The one thing it failed to deliver is the flag itself (see the `ExecState 0` reader, below), which
is the subject of `tools/bench/diag_bdloaded_reader.py`.
