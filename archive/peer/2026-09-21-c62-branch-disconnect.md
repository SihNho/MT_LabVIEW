# c62-branch-disconnect

- **agent:** claude
- **role:** fact
- **model:** fable (effort low; peer.ps1 default for role fact)
- **kind:** fact
- **cost:** $1.8352  in 28 / out 4808 / cache-create 45101 / cache-read 514362  (115s, 17 turn(s))
- **date:** 2026-09-21 10:12:40
- **outcome:** ANSWERED (116s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# QUESTION (pure API fact about LabVIEW VI Scripting itself, not about our code)

In **LabVIEW VI Scripting** (LabVIEW 2026, VI Server / ActiveX-COM, property and invoke nodes on the
`Wire`, `Terminal`, `GObject`, `Node`, `Diagram` classes), is there **any documented way to disconnect
ONE TERMINAL from a wire — i.e. to remove a single BRANCH of a wire net — without deleting the whole
`Wire` object?**

Concretely: a boolean source terminal `A` is wired to two sinks, `B` (a Case Structure selector inside a
while loop) and `C` (a front-panel indicator's terminal). LabVIEW reports this as ONE `Wire` object whose
terminal set is {A, B, C}. We want B to become bare while A→C survives, and we want it done by scripting,
not by mouse.

Please answer with citations (NI documentation, the LabVIEW VI Scripting property/method reference, NI
forums, or the `vi.lib`/`resource` scripting palettes) on each of these:

1. Does any **method** on `Wire`, `Terminal`, `GObject` or `Node` disconnect one terminal / delete one
   branch? (e.g. anything named Disconnect, Disconnect Wire, Remove Wire, Break Wire, Sever, Detach,
   `Terminal.Disconnect`, `Wire.Remove Segment`, …) If it exists, give its **exact class, method name and
   numeric method ID** if you can find one.
2. Does any **writable property** achieve it (e.g. writing `Terminal.Connected Wire`, `Wire.Terminals[]`,
   `Wire.Wire Path`/`Wire Joints`, or similar)? Which of those are read-only?
3. Is `Terminal.Connect Wire` (6349C03) usable to *re*-connect a terminal that has been bared, and does
   connecting a NEW wire to an already-wired sink implicitly remove the old branch?
4. If none of the above exists, what is the standard scripting idiom people use instead — delete the whole
   `Wire` and re-connect the surviving pairs? Anything else?

# WHAT WE ALREADY RULED OUT (do not repeat these)

- Our own toolkit has no such verb — a census of all 165 function definitions in our scripting wrapper found
  none; our only route today is deleting the whole `Wire` object, which we measured bares all three terminals.
- We are not asking about GUI/mouse editing, and not asking about "Remove Broken Wires" (Ctrl+B), which
  removes BAD wires only.
- We are not asking whether our specific code is right; only what LabVIEW's scripting API itself offers.

Answer briefly (a short list with citations). If the answer is "no such API exists", say so explicitly and
cite what you checked.


## Answer

**Answer: Yes — a documented method exists that our census apparently missed: `Wire.Disconnect Terminal` (VI Scripting, LabVIEW 2018+).** Point-by-point:

1. **Method to disconnect one terminal**: The `Wire` class has a **Disconnect Terminal** method — Method ID **6370C0D**, on Wire class (Class ID 16439), one required parameter (a Terminal refnum), no return value, VI Scripting scope, available since LabVIEW 2018. Documented on the [LabVIEW Wiki Wire class page](https://labviewwiki.org/wiki/Wire_class) and in NI's current API reference at [Disconnect Terminal — NI docs](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/wire/disconnectterminal.html) (also [the labview bundle page](https://www.ni.com/docs/en-US/bundle/labview/page/lvscript/wire_disconnect_terminal.html)). **Caveat honestly stated**: the NI doc pages are JS-rendered and I could not extract their body text, and the wiki page lacks a behavioral description — so whether disconnecting sink B leaves A→C intact as the same `Wire` object, versus baring the wire, is **not settled by the evidence I could fetch**; it should be verified empirically. No `Terminal`-class disconnect exists — the [Terminal class](https://labviewwiki.org/wiki/Terminal_class) has only Create Constant/Control/Indicator, Connect Wire, Create Described Wire, Create Shared Variable Node.

2. **Writable property**: none. `Terminal.Connected Wire` is **read-only**, and `Wire.Terminals[]` is **read-only** ([Terminal class](https://labviewwiki.org/wiki/Terminal_class), [Wire class](https://labviewwiki.org/wiki/Wire_class)). `Joints[]` is a geometry read used only for recreating wires (via Create Described Wire); `Delete Joint` removes a bend joint, not a logical branch.

3. **`Terminal.Connect Wire` (ID 6349C03)** exists and "connects a wire to the terminal; the wire source can be either another terminal or a node" ([Terminal class](https://labviewwiki.org/wiki/Terminal_class), [NI Connect Wire doc](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/terminal/connectwire.html)) — so yes, it is the tool to re-wire a bared terminal. I found **no documentation stating** that connecting a new wire to an already-wired sink implicitly removes the old branch; the forum idiom always deletes first, which suggests no such implicit removal is relied on. Unsettled otherwise.

4. **Standard idiom** (pre-2018, and still what NI staff recommend on the forums): capture refs to the source and the surviving sinks, **Delete the whole Wire**, then re-`Connect Wire` the pairs you want to keep — this is the accepted answer by Darren (NI) in [Disconnect wire through VI scripting](https://forums.ni.com/t5/LabVIEW/Disconnect-wire-through-VI-scripting/td-p/3046807) (2015, predating the 2018 method). To preserve routing, read `Joints[]` before deleting and rebuild with `Create Described Wire`.

**Recommendation**: try `Wire.Disconnect Terminal` (6370C0D) with B's terminal ref on the {A,B,C} wire; keep the delete-and-reconnect idiom as the proven fallback.

Sources:
- [LabVIEW Wiki — Wire class](https://labviewwiki.org/wiki/Wire_class)
- [LabVIEW Wiki — Wire class / Disconnect Terminal method](https://labviewwiki.org/wiki/Wire_class/Disconnect_Terminal_method)
- [LabVIEW Wiki — Terminal class](https://labviewwiki.org/wiki/Terminal_class)
- [NI docs — Wire Disconnect Terminal](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/wire/disconnectterminal.html)
- [NI docs — Terminal Connect Wire](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/terminal/connectwire.html)
- [NI forums — Disconnect wire through VI scripting](https://forums.ni.com/t5/LabVIEW/Disconnect-wire-through-VI-scripting/td-p/3046807)

## Sources

(extract from answer)

## What was done with it

Classified **ANSWERED** (claude / fact, fable effort low, 116 s, `$1.8352`). This was the mandatory external
search behind cycle 62's claim *"no verb removes ONE BRANCH"*
(`docs/cycle27-plan.md` Pre-decided 53(c)); it does not gate any build and nothing was built on it.

**Its headline is a real correction to our framing, recorded and NOT acted on:** LabVIEW VI Scripting is
documented to expose **`Wire.Disconnect Terminal`, method ID `6370C0D`** (Wire class 16439, one Terminal
refnum parameter, LabVIEW 2018+) on the LabVIEW Wiki and in NI's API reference. 53(c)'s census was a census
of **our own** `tools/gscript.py` (165 defs, `NONE FOUND`) and remains true as written; what is now known is
that the *platform* may offer what our fleet lacks, so the sentence "no verb removes one branch" must
henceforth be qualified as being about our toolkit, not about LabVIEW.

**Not verified, and the reviewer says so itself:** the NI pages are JS-rendered and it could not extract
their bodies, so whether disconnecting sink B leaves A→C intact *as the same Wire object* is undocumented in
what it could fetch. **Nothing was built, seeded or tested against 6370C0D in this dispatch** — building a
new op is a route decision that belongs to the judgement session, and the forced hypothesis review of the
same run (`archive/peer/2026-09-21-c62-row1-precond.md`) independently concludes it is unneeded for the
tests it names. Carried to `OPEN:`.

Accepted as fact and useful immediately: `Terminal.Connected Wire` and `Wire.Terminals[]` are **read-only**,
so no property route exists; there is **no `Terminal`-class disconnect**; and `Joints[]` / `Delete Joint` are
geometry, not topology. The pre-2018 idiom it cites (delete the whole wire, re-`Connect Wire` the pairs to
keep) is exactly what this cycle measured, so the fleet's current route is the documented fallback rather
than an improvisation.
