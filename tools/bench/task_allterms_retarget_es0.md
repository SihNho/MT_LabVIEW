# Failed prediction: a re-targeted `To More Specific Class` feeding a `Terminal` property node reads ExecState 0

Attack the diagnosis below. LabVIEW 2026 VI Scripting, driven headlessly over COM. Read-only research;
no LabVIEW here.

## What we are trying to build and why the construction matters

`OpAllTerms_v0.vi`: ONE call on a VI path returning every block-diagram terminal (uid, name, is_source,
connected-wire uid, owner uid, owner class). `Traverse for GObjects` with class `Terminal` returns 5,811
refs on our test VI in 5.28 s in one round trip, against ~508 s for the per-node reader we have.

The blocker is a type one: `Traverse` yields **GObject** refs, and `Name` (634A004) / `Is Source?`
(634A003) / `Connected Wire` (634A000) are **Terminal**-class properties, so each element needs a
`To More Specific Class` (TMSC). Measured, one variable at a time, on ONE copy:

- `Traverse.References` -> a `VI Server:Terminal` property node inside a For-loop body: ExecState **0**.
- the SAME wire -> a `VI Server:GObject` property node in the SAME body: ExecState **1**.
  (`tools/bench/diag_allterms_donor.log:33`)

A TMSC has no scripted creator in this fleet, and our project rule forbids the `copy_by_index` +
`move_in`-into-a-loop-body construction (4 attempts, 0 successes). Measured this session:
`copy_by_index` has no destination-diagram parameter; our loop creator makes an EMPTY loop and cannot
enclose existing nodes; and a census of **all 26** op VIs that own both a Function node and a loop found
**0** carrying a TMSC inside a loop body (`tools/bench/diag_allterms_donor2.log`, 26 pass / 1 fail, the
one fail being that free prediction).

So the remaining construction is: put the cast in a one-row **subVI** whose own ROOT diagram holds it,
and call that subVI from inside the loop. Its one unmeasured link is whether an existing TMSC can be
**re-targeted** to `Terminal` and feed a Terminal-class property node.

## The prediction and what was measured

PREDICTED: ExecState **1**.  MEASURED: ExecState **0**.  (`tools/bench/diag_allterms_retarget2.log:114`)

The run took a dated scratch copy of `OpLoopCast_v0.vi` (a working op, ExecState 1, whose root diagram
carries TMSC uid 683 with `target class` fed by a refnum-control seed) and:

1. deleted its Property nodes (they read `ForLoop`-class properties off the cast, so they had to go);
   Property 2 -> 0, Function unchanged 3 -> 3.
2. created `build_property("VI Server:Terminal", [634A004, 634A003, 634A000, 632A813, 6327806])` on the
   ROOT diagram - op error `''`, Property 0 -> 1.
3. `create_control` on that node's own `reference` -> a control LabVIEW named `'reference 2'`, arriving
   WIRED (birth wire w362), which is the documented behaviour.
4. deleted w362, deleted the old seed wire and the old cast-output wire, then wired
   `'reference 2'` -> TMSC `target class` and TMSC `specific class reference` -> the Terminal node's
   `reference`. Both landed: Wire count 8 -> 9 -> 10, both op errors `''`.
5. ExecState: **1 at open -> 0 at the end**.

The final root-diagram census read back off the machine (node index, uid, terminal -> connected wire):

```
0  #43   Open VI Reference  vi path w106, vi reference w467, error out 0
1  #124  Traverse           VI Refnum w467, Traverse Target w415, Class Name w373, References w600
2  #308  Index Array        array w600, element w605, index w1066
3  #683  TMSC               reference w605, target class w333, specific class reference w348
4  #316  Open VI Reference  vi path w550, vi reference 0, error out 0
5  #331  (no terminals at all)
6  #186  Terminal property   reference w348, Name 0, IsSource 0, Wire 0, UID 0, Owner 0
```

## The diagnosis to attack

**H1 (ours): the 0 is leftover wreckage from stripping the donor, not the cast.** Node 5 (`#331`) reports
no terminals, which in our reader is how a STRUCTURE appears; `OpLoopCast_v0` owns a For loop whose body
held the Property nodes that step 1 deleted. Our own recipe notes say of a freshly created For loop
"ExecState 0 is EXPECTED - an empty loop has no N" (`tools/recipes/build_opreportall_v1.py:134`). Node 4
(`#316`) is a second `Open VI Reference` whose output is now unwired. On H1 the cast chain itself is
sound - `#683.specific class reference` w348 does reach `#186.reference` w348 - and the construction
stands.

**H2: a re-targeted TMSC genuinely cannot serve a Terminal-class property node.** The `target class`
input takes any wire of the target type, so a refnum control made on a Terminal node's own `reference`
should specify `Terminal` by construction - but we have never verified that the CONTROL's class is what
we assume, only that a control appeared and that the wire landed with an empty error. On H2 the last
construction our rules permit is closed.

We would like: the strongest reason H1 is wrong; any third explanation for ExecState 0 on this diagram
that neither H1 nor H2 covers; what observation would falsify H1; and the cheapest discriminating test
we can run headlessly over COM (we can read ExecState, class censuses, per-node terminal/wire maps,
`Wire.Is Broken?` on one wire after a write, and a GUI Error List is being built in parallel). Note that
"the VI is broken" is all our COM path exposes - `VI.Get Errors` (452) is absent from the exported
ActiveX interface here, so per-object error text is not readable by script.

Also worth attacking: is the subVI-in-loop construction itself sound in LabVIEW terms - a For loop
auto-indexing an array of GObject refs into a subVI whose connector-pane input is a GObject refnum
control, that subVI casting to Terminal on its own root diagram and returning scalars that the loop
auto-indexes back out?
