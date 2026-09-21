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
