# ATTACK this claim. Cycle 67, LabVIEW 2026 (26.3.1f1) VI Scripting over ActiveX/COM.

## 0. THE FAILING LOG UNDER REVIEW

`tools/bench/diag_c66c_coercion.log` — `BGRUN END rc=1 after 118s`, GATES 44 pass / 1 fail.
The one fail, verbatim (`:46`):

```
FAIL  R4 634A006 the measured short name is the claimed 'Coerced?'  measured 'Coerce Dot?'
```

A prior peer answer told us that LabVIEW Property ID `634A006` on a Terminal reference is short-named
`Coerced?`. The machine says otherwise: the created property node carries exactly ONE non-standard
terminal and its name reads `'Coerce Dot?'` (`:44`, `is_source=True wire=0 errs=[0,0,0,1055]`). So the
peer-reported short name was WRONG, and the coercion question stayed **UNMEASURED**, not answered
(`:186-188`). That is the failed prediction this exchange must discharge. Say explicitly, in your
answer, whether you think `Coerce Dot?` and `Coerced?` are the same property under two spellings or two
different properties, and what a LabVIEW 2026 terminal's coercion-dot flag is actually called.

## 1. THE CLAIM TO REFUTE

> **M3's persistent `ExecState` 0 is caused by the four severed shift-register rows and nothing else.
> Two `add_shift_reg` pairs on `#23032`, wired AFTER the seven `move_in`s and the seven internal rows as
> `#48` t3 `VISA resource name` ← left-inside (`LeftIn`), `#48` t4 `In position` ← left-inside (`LeftIn`),
> `#10407` t4 → right-inside (`RightIn`), `#10407` t6 `position [internal units]` → right-inside
> (`RightIn`), will take the VI to `ExecState` 1. An UNINITIALISED shift register — outer-left terminal
> unwired — is legal LabVIEW and does NOT by itself hold `ExecState` at 0, so the initial-value wires can
> be a SECOND saved stage without blocking the first.**

Attack it. I want the strongest reason it is wrong, an alternative explanation of the `ExecState` 0, what
would falsify the claim, and the cheapest discriminating test.

## 2. THE THREE SPECIFIC QUESTIONS I MOST NEED ATTACKED

**(a) Does an UNINITIALISED shift register really compile in LabVIEW 2026?**
Our ONLY evidence is our own docstring, `tools/gscript.py:758`, which asserts *"wire 0 = unwired (an
uninitialised register's outside terminal is legitimately unwired)"*, and `:683-687`, which says
*"BOTH SIDES COME BACK UNWIRED, and an unwired register breaks the VI (ExecState 0) until they are wired
— that is correct, not a failure."* Those two sentences are in tension: the second says "until they are
wired" without saying WHICH sides. If LabVIEW requires the outer-LEFT (initial-value) terminal to be
wired before the VI is executable, the claim's second half collapses and the M3a-1 stage can never reach
`ExecState` 1 without the initial values. Search NI's own documentation and say what LabVIEW actually
does with a shift register whose left OUTER terminal is bare while both inner terminals are wired.

**(b) Can `LeftIn` / `RightIn` address a node that arrived on the body diagram via `move_in` rather than
by creation?** Our wrapper (`tools/gscript.py:713-723`) documents:
  - `'LeftIn'`  : left INSIDE → `Terminals[term_index]` of `Nodes[node_index]` INSIDE the loop body
    (addressed through `Loop.Diagram`)
  - `'RightIn'` : `Terminals[term_index]` of body `Nodes[node_index]` → right INSIDE
  - indices are *creation-order* `Nodes[]`.
The four target terminals sit on `#48` (a SubVI, `ASI_adjust focus-subvi.vi`) and `#10407` (a
CaseStructure) — both of which were MOVED into the loop body `Diagram #23058` by `move_in` from
`Diagram #639`. Is "creation-order `Nodes[]`" on the destination diagram stable and does a moved object
appear in it at all? If `Loop.Diagram`'s `Nodes[]` enumeration differs from the `node_terms_uid`
enumeration we read off `Diagram #23058` immediately before the call, every one of the four rows lands on
the wrong node and the whole stage is silently mis-wired while reporting success.

**(c) What ELSE in the 14-edit state is bare besides those four rows?** Name any structural obligation a
LabVIEW While Loop imposes that our enumeration of "the four severed SR rows" could be missing — case
structure tunnels that renumber or go unwired on move, a case frame that must have every output tunnel
wired in EVERY frame, conditional/selector tunnels, an auto-indexing tunnel, the loop condition terminal,
a SubVI required-input rule. `#10407` is a Case Structure with multiple frames; `#23032` is a While Loop.
Be concrete about which of these hold a VI at `ExecState` 0.

## 3. ALREADY RULED OUT — do not spend your answer on these

- **Coercion is NOT the cause.** `tools/bench/diag_c66c_coercion.log` measured it: no wrapped column of
  this fleet carries a coercion flag or a data type, so coercion is UNMEASURED, but the three artefacts'
  full terminal tables (name, is_source, connected wire, error codes) show no broken-type signature, and
  the stage under discussion is a pure SCHEDULING move that changes no data types.
- **The moves do not DESTROY wires.** `tools/bench/diag_c66b_s3b_m3.log` measured the whole-VI `Wire`
  class census at three points on one bed: **1907 COLD** (`:30`), **1907 after all seven `move_in`s**
  (`:284`), **1914 after the seven internal rows** (`:441`) — i.e. the moves sever roughly 12 wire
  *connections* without deleting a single `Wire` object, and the seven rows then add 7. `Node` stayed 632,
  `ControlTerminal` 116, `Local` 10, `LoopTunnel` 135, `Tunnel` 471 throughout.
- **`ExecState` went to 0 at the FIRST `move_in` and never came back.** Timeline from the same log:
  COLD 1 (`:28`) → 0 after move #3529 (`:130`) → 0 after each of the other six moves (`:155`, `:180`,
  `:205`, `:230`, `:255`, `:280`) → 0 after each of the seven `connect_nested_v1` rows (`:306`, `:327`,
  `:348`, `:369`, `:390`, `:411`, `:432`) → 0 at the decision point (`:440`). Final gate: `82 pass / 1
  fail`, the one fail being the pass criterion itself (`:458`). Nothing was saved.
- The moved set is seven objects into `Diagram #23058` (body of While Loop `#23032`): `#3529`, `#3560`,
  `#3447` (ControlReferenceConstants), `#48` (SubVI), `#10407` (CaseStructure), and the two Locals
  `#23499` / `#23523`.

## 4. WHAT I WILL DO WITH YOUR ANSWER

The next diagnostic runs the route above and takes a FULL `node_terms` census of the seven moved nodes
both before and after the four SR rows, printing every terminal whose `WireUID` is 0. It runs whatever
you say, because the census is what makes it informative. So do not optimise your answer for "should he
run it" — optimise it for "what will the census show, and what is he going to conclude wrongly from it".
If the claim is wrong, tell me the observation that will prove it wrong, in terms of that census.
