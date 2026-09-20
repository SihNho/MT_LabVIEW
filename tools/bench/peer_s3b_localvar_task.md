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
