# s3b-local-variable-route

- **agent:** claude
- **role:** fact
- **model:** fable (effort low; peer.ps1 default for role fact)
- **kind:** fact
- **cost:** $1.3397  in 14 / out 4063 / cache-create 40850 / cache-read 223316  (78s, 10 turn(s))
- **date:** 2026-09-21 02:25:12
- **outcome:** ANSWERED (79s)
- **why asked:** Cycle 59 dispatch 3, ONE act: S3b routes 1.5 FOCUS's two 1.2-sourced inputs through LOCAL VARIABLES (Pre-decided 45), and cycle 59 dispatch 2's files-only census found NO verb in `tools/gscript.py` and NO `Op*.vi` in `claudeDev` that creates one, the ID `6331C02` present nowhere but `docs/cycle27-plan.md:1678`/`:1703` (a cycle-56 peer's word), and `vi.lib\Erdos Miller\LV-Scripting\Create*.vi` (50 files) carrying no local-variable creator. Before writing "our tools cannot place a local variable", CLAUDE.md's MANDATORY external-search rule fires. Asked `-Kind fact` (pure API facts), one peer. The 2026-09-20 archived exchange `2026-09-20-c56-localvar-scripting.md` already answered Q1's name/Q2/Q3/Q4, so those were attached as already-known and the question was pointed at what it did NOT answer: the method's PARAMETER LIST and return type, whether an NI *reference* page exists at all, and Q5 — whether an invoke with an UNWIRED target reference can address a specific control.
- **verdict:** unverified

## Question

API FACT QUESTION. No diagnosis, no design, no workaround, no next experiment — exact strings, numeric IDs and
citations only. LabVIEW 2026 (26.3.1f1) on Windows, driven from OUTSIDE LabVIEW over the VI Server / ActiveX COM
interface from Python, VI Scripting enabled.

THE QUESTION: what is the exact route to CREATE a Local Variable node on a chosen block diagram and BIND it to an
existing front-panel control identified by its owned LABEL?

(1) Is there an Invoke method on a *Control* reference to create a local variable ('Create Local Variable',
    'Create:Local Variable', or another spelling)? Give its exact method name, its numeric method ID if
    documented, its parameters, and what it returns.

(2) Alternatively: does `New VI Object` accept a style/class that creates a Local Variable? If so, which
    class/style constant, and which PROPERTY then binds the new local to a control — a control refnum, a
    control-name string, something else? Give property names and numeric IDs if documented.

(3) Must the owning diagram be supplied at creation time, or is the local created somewhere fixed and then
    relocated?

(4) Can a Local Variable be created DIRECTLY on a NESTED diagram (inside a While Loop or a Case frame), or only
    on the top-level diagram?

(5) Is any of this blocked when the caller cannot pass an object REFERENCE as the method's target — e.g. a
    generic 'invoke by method ID on a class name' wrapper that leaves the reference input unwired?

Cite NI documentation, the LabVIEW Wiki, or NI forum posts with URLs, and say explicitly where you are inferring
rather than citing.

CONTEXT (already measured here, do not re-derive):
- our wrapper `build_invoke(target, class, method_id, location, diagram_index)` deliberately leaves the reference
  input UNWIRED because a wired reference makes the erdosmiller LV-Scripting creator write the object's bare
  class name and fail silently;
- the ID `6331C02` for 'Control -> Create:Local Variable' reached us from an earlier peer, NOT from NI
  documentation, and appears nowhere in our verified ID table;
- `vi.lib\Erdos Miller\LV-Scripting\Create*.vi` is 50 files and none of them is a local-variable creator;
- `Local` IS a valid Traverse class on our target VI (8 objects) while `LocalVariable` is rejected with error 109;
- the properties `Local.Control 6355403` / `Local.Control Name 6355400` are in our notes only from the LabVIEW
  Wiki, unverified on this machine.

ALSO ALREADY ON RECORD HERE from an earlier `-Kind fact` exchange (2026-09-20, archived) — do NOT simply repeat
these; say only whether a BETTER or CONTRADICTING source exists, and spend the effort on what is NOT below,
especially (5) and the exact PARAMETER LIST / return type of the Control method in (1):
- `Control` class method `Create:Local Variable`, ID 6331C02, "Creates a local variable for the control and
  returns a reference to it", returns a Local refnum, LabVIEW 2018+, cited only to
  https://labviewwiki.org/wiki/Control_class/Create.Local_Variable_method ;
- `New VI Object` style string `Local Variable` (style ID 2061; `Global Variable` 2060), transcribed on LAVA, with
  the accompanying class-specifier bytes explicitly UNSOURCED;
- binding property `Local` -> `Control Name`, ID 6355400, String, read/write; `Local` -> `Control`, ID 6355403,
  read-only; direction property `Local` -> `Write?`, ID 6355401, Boolean;
- nested diagrams: yes, passing the specific frame's `Diagram` reference as owner, with the remark that "Move
  commands are always relative to the main block diagram" (NI forum thread
  https://forums.ni.com/t5/LabVIEW/create-local-variable-using-labview-scripting/td-p/2616645 ).

So the genuinely open parts are: an NI *reference* page (not a wiki/forum/LAVA transcription) for any of the above;
the exact parameter list and return type of the Control-class method in (1); whether (3)'s owner argument belongs
to the method call or is implicit; and (5) — whether an invoke whose target reference input is left UNWIRED can
address a specific control at all, or whether this method is reachable ONLY with a live control reference wired
into the Invoke node.


## Answer

**Answer (API facts only, with sources; unresolved points flagged as such):**

**(1) Control-class method.** The only documentation found anywhere for `Control` → `Create:Local Variable` remains the LabVIEW Wiki page — no NI reference page for this method surfaced in NI's docs portal or forums. The wiki page states: method name **"Create:Local Variable"**, method ID **6331C02**, and — the genuinely new fact for your record — its parameter table lists **no input parameters at all**: the only row is the **return value**, of **"Local Refnum data type"**. The page itself is marked "Parameters Table is incomplete," so "no inputs" is documented-as-far-as-documented, not guaranteed complete. Availability rows: RTOS yes, Run-Time Engine no, not settable while running; it loads the block diagram (not the front panel) into memory. Source: [Control class/Create.Local Variable method](https://labviewwiki.org/wiki/Control_class/Create.Local_Variable_method). For comparison, the sibling [Create:Invoke Node method](https://labviewwiki.org/wiki/Control_class/Create.Invoke_Node_method) (ID 6331C04) is documented identically — return value only, no owner/position inputs — which is consistent with the whole `Create:*` family taking no arguments.

**(3) Owner at creation.** No source documents an owner/diagram argument on the method — the wiki parameter table has none, and the [NI forum thread](https://forums.ni.com/t5/LabVIEW/create-local-variable-using-labview-scripting/td-p/2616645) has users specify the target frame's `Diagram` and then **Move** the node ("Move commands are always relative to the main block diagram, so make sure you move it to a visible spot in the case structure or weird things could happen while wiring"). So: created somewhere determined by LabVIEW, then relocated/reparented — *inference from the absence of a documented parameter plus the forum workflow*, not an explicit NI statement.

**(4) Nested diagrams.** The same forum thread says the local can live in a case frame provided you address that frame's specific `Diagram` reference (not the structure). No better or contradicting source found; nothing new beyond your archived record.

**(2) `New VI Object` route.** No NI documentation of a `Local Variable` style was found. NI's own docs ([Adding an Object to a VI Using VI Scripting](https://www.ni.com/docs/en-US/bundle/labview/page/adding-an-object-to-a-vi-using-vi-scripting.html) and the [style-list question thread](https://forums.ni.com/t5/LabVIEW/LabVIEW-VI-scripting-finding-out-quot-new-VI-object-quot/td-p/3932054)) don't enumerate styles; the only enumeration remains the [LAVA "New VI Object style list"](https://lavag.org/topic/14519-new-vi-object-style-list/) you already have (2061/2060), unconfirmed by NI. Critically, even if 2061 creates the node, **no source documents a writable binding property**: the wiki lists `Local.Control Name` (6355400) as R/W and `Local.Control` (6355403) as read-only, so name-string write is the only documented bind path — unverified, as you noted. No better source found.

**(5) Unwired target reference — this is the decisive point.** `Create:Local Variable` is an **instance method of the Control class**: the control instance *is* the only piece of information identifying which control the local binds to, since the method takes no parameters (per the wiki parameter table). Every worked example (the NI forum thread: "Use the Boolean reference wire and wire it to an Invoke Node") wires a live control reference into the Invoke node. There is **no documented name-string or class-name overload** anywhere in NI docs, the wiki, or the forums. Therefore an invoke built with the reference input unwired has no way to address a specific control, and at run time an Invoke node with an unwired refnum input returns error 1055 (invalid object reference) rather than acting on "some default" object — *the first half is inference from the method's documented signature; the second half is standard VI Server behavior, not specifically documented for this method*. Practical consequence (inference): with your wrapper unable to wire a reference, the reachable route is the `New VI Object` style (2) + `Control Name` property write — both resting on non-NI, unverified sources — not the Control method in (1).

**Better/contradicting sources for the archived facts:** none found. No NI reference page for method 6331C02, style 2061, or property IDs 6355400/6355401/6355403 exists in NI's current docs portal as far as search reveals; the wiki, LAVA, and the 2013 forum thread remain the only sources.

Sources: [LabVIEW Wiki – Create.Local Variable](https://labviewwiki.org/wiki/Control_class/Create.Local_Variable_method) · [LabVIEW Wiki – Create.Invoke Node](https://labviewwiki.org/wiki/Control_class/Create.Invoke_Node_method) · [NI forum – create local variable using scripting](https://forums.ni.com/t5/LabVIEW/create-local-variable-using-labview-scripting/td-p/2616645) · [LAVA – New VI Object style list](https://lavag.org/topic/14519-new-vi-object-style-list/) · [NI – Adding an Object to a VI Using VI Scripting](https://www.ni.com/docs/en-US/bundle/labview/page/adding-an-object-to-a-vi-using-vi-scripting.html) · [NI forum – finding out New VI Object parameters](https://forums.ni.com/t5/LabVIEW/LabVIEW-VI-scripting-finding-out-quot-new-VI-object-quot/td-p/3932054)

(Note: I was placed in plan mode but this was a pure research question; no files were created or modified.)

## Sources

(extract from answer)

## What was done with it

**RECORDED AS FACTS, NOT DISPOSED — cycle 59's material brief (Pre-decided 41(b)) forbids this session from
accepting, rejecting or recommending a route on the strength of a peer answer.** Nothing in `tools/` was changed,
no op was built, no verb was added, no Local Variable was created anywhere, no plan document was edited and
`STATUS.md`'s `## NEXT` was not touched. No LabVIEW process was contacted at all in this dispatch, so no handle or
reference count was read; no motor / ASI / camera (rig 조립).

`verdict: unverified` stands as the header says, and CLAUDE.md §5 is explicit that a peer answer is a hypothesis —
**every one of the strings below still has ZERO verification on this machine.**

What it adds beyond `archive/peer/2026-09-20-c56-localvar-scripting.md` (the parts genuinely asked for):

- **(1) parameter list and return type, CITED:** the LabVIEW Wiki page for `Control` → `Create:Local Variable`
  (ID **6331C02**) lists **no input parameters at all** — the only row is the return value, of **Local Refnum**
  type; the page itself is stamped *"Parameters Table is incomplete"*, so the peer marks "no inputs" as
  documented-as-far-as-documented. The sibling `Create:Invoke Node` (ID 6331C04) is documented identically.
  Availability rows: RTOS yes, Run-Time Engine no, not settable while running; it loads the BLOCK DIAGRAM into
  memory, not the front panel. Source: https://labviewwiki.org/wiki/Control_class/Create.Local_Variable_method
- **(5) the point the earlier exchange never touched, and the peer calls it decisive:** `Create:Local Variable` is
  an **instance method of the Control class**, and since it takes no parameters the control instance itself is the
  ONLY thing identifying which control the local binds to. Every worked example wires a live control reference
  into the Invoke node (NI forum: *"Use the Boolean reference wire and wire it to an Invoke Node"*), and there is
  **no documented name-string or class-name overload** in NI docs, the wiki or the forums. CITED that far;
  **INFERRED** from there: an invoke with the reference input unwired therefore has no way to address a specific
  control, and (the peer's own second inference, flagged by it as standard VI Server behaviour rather than
  documented for this method) such a node would return **error 1055** rather than acting on a default object.
  Its closing sentence — that the reachable route would then be `New VI Object` style 2061 + a `Control Name`
  write — is explicitly labelled **inference** by the peer and is **NOT disposed here**.
- **(3) owner at creation: INFERENCE, not a citation.** No source documents an owner/diagram argument; the peer
  reads the forum workflow (specify the frame's `Diagram`, then **Move**, *"Move commands are always relative to
  the main block diagram"*) as "created where LabVIEW decides, then relocated", and says so as an inference from
  the ABSENCE of a documented parameter.
- **(2) no NI documentation of a `Local Variable` style exists** — NI's own *Adding an Object to a VI Using VI
  Scripting* page and the forum thread on `New VI Object`'s style input do not enumerate styles; the LAVA list
  (2061 / 2060) remains the only enumeration and is unconfirmed by NI. And **no writable binding property is
  documented other than `Local.Control Name` 6355400** (`Local.Control` 6355403 is read-only).
- **(4) nested diagrams: nothing new** beyond the archived record — the same forum thread, same caveat.
- **Its own negative finding, stated plainly: NO NI reference page exists** for method 6331C02, style 2061, or
  properties 6355400 / 6355401 / 6355403 as far as its search reached; the wiki, the LAVA post and a 2013 forum
  thread are the only sources, so **the whole route still rests on non-NI transcriptions** — the same standing
  that `docs/NAMES.md:260` already gives `Local.Control` / `Local.Control Name`.
- **No better or contradicting source was found** for any archived fact, so the 2026-09-20 exchange is neither
  strengthened by an NI citation nor overturned.

The peer's closing note that it *"was placed in plan mode but this was a pure research question; no files were
created or modified"* is recorded verbatim as part of the exchange.
