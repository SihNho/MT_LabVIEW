# c56-localvar-scripting

- **agent:** claude
- **role:** fact
- **model:** fable (effort low; peer.ps1 default for role fact)
- **kind:** fact
- **cost:** $1.5883  in 18 / out 4287 / cache-create 43925 / cache-read 304879  (106s, 15 turn(s))
- **date:** 2026-09-20 20:47:00
- **outcome:** ANSWERED (107s)
- **why asked:** Pre-decided 45 routes 1.5 FOCUS's two 1.2-sourced inputs through LOCAL VARIABLES, and 45(f) says a diagnostic comes first when a construction verb is unmeasured. Our own files record `LocalVariable` as INVALID for a class traverse (error 109) and `Local` as the valid traverse class (`docs/toolkit-capabilities.md:283-290`) — so before writing "our tools cannot place a local variable by script", CLAUDE.md's MANDATORY external-search rule fires. Asked as the cycle-56 material session's M4, `-Kind fact`, one peer.
- **verdict:** unverified

## Question

API FACT QUESTION (no diagnosis, no project context needed). LabVIEW 2026 (26.3.1f1) on Windows, driven
headlessly over the ActiveX/COM VI Server from Python, with VI Scripting enabled. We create diagram objects
with the scripting method `New VI Object` and we enumerate them with `Traverse for GObjects` / class-name
traverses.

THE QUESTION: how is a LabVIEW **Local Variable** created on a block diagram and bound to a named front-panel
control or indicator, BY VI SCRIPTING / the VI Server API? Specifically, and with citations:

1. The exact **class-name string** that `New VI Object` (or `Diagram.Create Object` / `New VI Object` in the
   scripting palette) takes to create a local variable. Our own measurements record:
   - `"LocalVariable"` is INVALID for a class traverse on this install (error 109),
   - `"Local"` IS the valid traverse class name for finding existing local variables.
   Is `"Local"` also the correct string for CREATION, or is the creation style/class name different from the
   traverse class name? Name the exact bytes.
2. The **property or method that BINDS** a newly created local variable to a particular front-panel control or
   indicator by name. (Candidates we have not verified: a `Terminal`/`Source` property, a `Refresh`/`Linked
   Control` property, `Local.Control` / `Local.Terminal`, setting `Local`'s `Signal Name`, or wiring it through
   `Control.Terminal`.) Give the property's exact name and its data type, and say whether the local variable is
   created UNBOUND and then bound, or bound at creation time by passing the control's reference/name.
3. Whether a local variable can be created **directly on a NESTED diagram** (inside a While loop's subdiagram,
   or a Case structure frame) rather than on the top-level block diagram — i.e. whether the creation call takes
   an arbitrary `Diagram` reference as its owner, and whether anything about nesting is special.
4. Any **LabVIEW-version caveats**, deprecations or known bugs for this specific operation (LabVIEW 2019 through
   2026), and any licensing/edition requirement beyond "VI Scripting enabled".
5. Whether the read/write direction of a local variable (read vs write) is a property set after creation, and
   its exact name.

Cite NI documentation (ni.com help pages, the VI Scripting class/property/method help), the shipped scripting
examples under `<LabVIEW>\examples\Application Control\VI Scripting\`, or `vi.lib` scripting VIs, by page title
or file path. If you cannot find an authoritative statement for a sub-question, say so explicitly rather than
inferring it from a similar class.

DO NOT propose a design, a workaround, or a next experiment. Return the exact strings and the citations only.


## Answer

**Findings (read-only research; no changes made):**

**1. Creation class/style string.** `New VI Object` takes two things: a *VI Object Class* (class specifier constant) and a *style* string. The definitive style list for `New VI Object` (extracted from LabVIEW's own ring constant, posted on LAVA in the "New VI Object style list" thread) contains the entry **`Local Variable`** (style ID 2061; global is `Global Variable`, 2060). So the creation **style string is `"Local Variable"`**, while the VI Server class name — the one used for traverses and returned references — is **`Local`** (LabVIEW Wiki "Local class"). Your measurement is consistent: `"Local"` is the traverse class; the creation style name differs from it. Note also there is a second, simpler creation route that bypasses `New VI Object` entirely: the **Control class method `Create:Local Variable`** ("Creates a local variable for the control and returns a reference to it", returns a **Local Refnum**) — documented on LabVIEW Wiki as available in LabVIEW 2018+ (the wiki mirrors NI's per-class scripting help). I did not find an NI page that states in prose that `"Local"` is invalid as the New VI Object class-name input, so I can't authoritatively confirm the exact class-specifier byte string used alongside the `"Local Variable"` style — the LAVA list documents the style string only.

**2. Binding.** The binding property is **`Local` class → `Control Name`** (property ID 6355400), **String**, read/write, "Name of the control to which the local variable refers" (LabVIEW Wiki, Local class/Control Name property). With `New VI Object` the local is created **unbound** and then bound by writing `Control Name` — the NI forum thread "create local variable using labview scripting" describes exactly this flow ("After you create the local variable, you can set the control it points to using the Control Name property"). With the `Control:Create:Local Variable` method the local is **bound at creation** to that control. There is also a read-only **`Control`** property (ID 6355403, returns a reference to the bound control) — read-only, so not usable for binding.

**3. Nested diagrams.** Yes. From the same NI forum thread: *"You can create the local variable on the main block diagram or you can create it on the diagram of the case structure"* — you must pass the specific **frame's Diagram reference** as owner, not the structure node itself, and note that *"Move commands are always relative to the main block diagram."* Nothing else special about nesting is documented.

**4. Version/licensing caveats.** The wiki documents `Create:Local Variable`, `Control Name`, and `Write?` as "LabVIEW 2018 and later" scope "VI Scripting"; not available in the Run-Time Engine, cannot be executed while the VI runs. I found **no documented deprecations or known bugs** for this operation in LabVIEW 2019–2026, and no licensing requirement beyond enabling VI Scripting — no authoritative statement either way, so treat that as "nothing found," not "nothing exists."

**5. Read/write direction.** Yes, a post-creation settable property: **`Local` class → `Write?`** (property ID 6355401), **Boolean**, read/write — "If TRUE, the variable is a write local. If FALSE, the variable is a read local" (LabVIEW Wiki, Local class).

Sources:
- [Control class/Create.Local Variable method — LabVIEW Wiki](https://labviewwiki.org/wiki/Control_class/Create.Local_Variable_method)
- [Local class — LabVIEW Wiki](https://labviewwiki.org/wiki/Local_class)
- [Local class/Control Name property — LabVIEW Wiki](https://labviewwiki.org/wiki/Local_class/Control_Name_property)
- [create local variable using labview scripting — NI Community](https://forums.ni.com/t5/LabVIEW/create-local-variable-using-labview-scripting/td-p/2616645)
- ["New VI Object" style list — LAVA](https://lavag.org/topic/14519-new-vi-object-style-list/)
- [Tutorial: Adding an Object to a VI Using VI Scripting — NI](https://www.ni.com/docs/en-US/bundle/labview/page/tutorial-adding-an-object-to-a-vi-using-vi-scripting.html)
- [VI Scripting - Input for style in "New VI Object" — NI Community](https://forums.ni.com/t5/LabVIEW/VI-Scripting-Input-for-style-in-quot-New-VI-Object-quot-function/td-p/3267356)

## Sources

(extract from answer)

## What was done with it

**RECORDED AS FACTS, NOT ACTED ON — the cycle-56 material session's brief (Pre-decided 41(b)) forbids this
session from accepting, rejecting or building on a peer answer.** Nothing in `tools/` or `docs/` was changed on
the strength of it; no op was built; no local variable was created anywhere. The strings it returns are carried
to the judgement session on the `OPEN:` line and are UNVERIFIED against this machine (the archive header says
`verdict: unverified`, and CLAUDE.md §5 is explicit that a peer answer is a hypothesis).

The exact strings it returns, verbatim and for the record:

- **Creation style string = `Local Variable`** (style ID 2061; `Global Variable` is 2060), from LabVIEW's own
  `New VI Object` style ring as transcribed on LAVA — while the **traverse / reference class name is `Local`**
  (LabVIEW Wiki, *Local class*). It says our two measurements are consistent with that split and that it found
  **no NI page** stating the class-specifier bytes that accompany the `Local Variable` style, so that half is
  explicitly unsourced.
- **A second creation route that bypasses `New VI Object` entirely: the `Control` class method
  `Create:Local Variable`** — "Creates a local variable for the control and returns a reference to it", returns
  a Local refnum, LabVIEW 2018+. On this route the local is **bound at creation**.
- **Binding property = `Local` → `Control Name`, property ID 6355400, String, read/write** ("Name of the control
  to which the local variable refers"). Via `New VI Object` the local is created **unbound** and then bound by
  writing `Control Name`. There is also a **read-only** `Control` property, ID 6355403, returning the bound
  control's reference — read-only, so not a binding route.
- **Direction = `Local` → `Write?`, property ID 6355401, Boolean, read/write** (TRUE = write local, FALSE = read
  local).
- **Nested diagrams: YES** — the owner passed in must be the specific **frame's `Diagram` reference**, not the
  structure node, and it warns that "Move commands are always relative to the main block diagram."
- **Version/licensing: nothing found either way** for 2019–2026 beyond "VI Scripting enabled" and "not available
  in the Run-Time Engine; cannot execute while the VI runs"; it states this as *nothing found*, not *nothing
  exists*.

Every source it cites is a wiki, a forum thread or a LAVA post except the NI tutorial page and the NI forum
thread on `New VI Object`'s style input; no NI *reference* page for `Local`'s properties was produced. Whether
any of this is reachable over THIS project's COM path is unmeasured — which is exactly the judgement call this
session is not permitted to make.
