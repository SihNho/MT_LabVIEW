# zdz-wirecontrol-5001

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.9728  in 30 / out 44376 / cache-create 188755 / cache-read 1641319  (639s, 31 turn(s))
- **date:** 2026-09-19 00:33:27
- **outcome:** ANSWERED (640s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim. A build prediction failed in a new place, and the explanation below is the one this project
formed under pressure, minutes after the failure. It is about to drive the next expensive build, so if it is
wrong we need to know now.

Context you need: this project edits LabVIEW block diagrams programmatically over ActiveX/COM, using the
open-source **erdosmiller `lv-scripting`** library (`LV-Scripting.lvlib`) wrapped by our own op VIs. One op,
`wire_control`, is used to wire a named terminal of one object to a named terminal of another. The build is
rewiring a `Z/dZ` signal so that it terminates on a temporary sink node (a newly created `Equal?` primitive)
instead of its original destination.

## The claim under attack (quote it, then attack it)

"The `Z/dZ` -> `#2222 t0` wiring failed only because `wire_control` cannot address the created `Equal?` node's
`x` input by name; the temporary-sink ROUTE itself is sound, and the fix is to reach that terminal by INDEX with
an op we already have."

## The machine record, verbatim (all from `tools/bench/build_d1_routeb_v2_run5.log`)

* `:332` — the created node is WELL FORMED, our own census of its terminals:
  `created Equal? #10104 terminal census = {0: ('x = y?', True, 0), 1: ('y', False, 0), 2: ('x', False, 0)}`
  with `src_names=()`. (Tuple = (name, is_source, ...).)
* `:402` — one step later:
  `'Z/dZ': wire_control to the temporary sink failed: wire_control ['Z/dZ'] -> Function.['x']: error 5001:
  LV-Scripting.lvlib:Get Controls.vi<ERR>`
* So our own census says `x` EXISTS at index 2 with `is_source` False, while `Get Controls.vi` cannot find it.
  **That contradiction is the thing to explain.**
* Second, INDEPENDENT failure in the same run: LabVIEW `error 2` ("memory is full") recurred at
  `tools/recipes/build_d1_routeb_v2.py:1252` — a `count(LoopTunnel)` call routed through our `OpReport_v3.vi` —
  logged at `:406`, measured at **38,824 LabVIEW handles** (`:405`). The SAME call SUCCEEDED in run 4 at
  **51,284** handles. Six other rows failed the same way (`:396-401`).

## Already ruled out - do not spend your answer re-proposing these

1. REORDER route: `ControlTerminal #403` has no node index on `Diagram[56]`; our `OpConnectNested_v1` addresses
   `Diagram[].Nodes[].Terminals[]` only, so a control terminal is unreachable by that path
   (`tools/bench/build_d1_routeb_v1_run4.log:163-164`).
2. The RETRY guard returning early before the sink was reached: FIXED this cycle; it now logs and falls through
   (`tools/bench/build_d1_routeb_v2_run5.log:331`).
3. "A silent default/invalid refnum came out of the creation because `src_names=()`": REFUTED by measurement at
   `:332` - the node is well formed and its terminals are readable.
4. Handle exhaustion as the cause of `error 2`: REFUTED - it recurred at a LOWER handle count (38,824) than a
   count at which the identical call SUCCEEDED (51,284).

## What I want from you

(a) **What does `error 5001` mean specifically in erdosmiller `lv-scripting`'s `Get Controls.vi`?**
    EXTERNAL SEARCH REQUIRED - this is a third-party open-source library (github erdosmiller/lv-scripting) and a
    user-defined error range; do not answer from general LabVIEW error-code memory. Quote the library's own
    definition / source if you can find it, with the URL.
(b) Given the VI's NAME, does `wire_control` in that library address FRONT-PANEL CONTROLS only - i.e. is it
    simply the wrong op for an input terminal of a Function node on the block diagram? Say what evidence
    settles this either way.
(c) **The strongest reason the claim above is WRONG** - i.e. the case that the temporary-sink route is itself
    unsound and the `Z/dZ` row needs something else entirely, not an addressing fix.
(d) What else produces LabVIEW `error 2` at a property/report call when memory is plainly NOT exhausted?
    Name concrete mechanisms, not "memory pressure".
(e) The SINGLE cheapest discriminating test for (a)+(b), given this constraint: the created `Equal?` - unlike
    the `ControlTerminal #403` above - DOES have a node index on the diagram, so index-addressed ops we already
    own (`OpConnectFromWire_v0`, `OpConnectNested_v1`) are available without building anything new.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**The claim is wrong at its first noun: `Get Controls.vi` never looks at the `Equal?` node.** It is the *source*-side resolver. The name it failed to find is `'Z/dZ'`, not `'x'`, and the destination lookup never ran.

---

## 1. The single strongest reason the claim is WRONG

> *"The `Z/dZ` → `#2222 t0` wiring failed only because `wire_control` cannot address the created `Equal?` node's `x` input by name."*

`wire_control` is `OpWireCtl_v0`, and your own dispatcher documents its internal dataflow: it "swaps that source for `Get Controls.vi`, which turns control LABELS into terminal refnums and **hands them to `Wire Inputs.vi`'s `Inputs` array**" (`tools/gscript.py:1876-1877`). `Get Controls` runs **upstream** of `Wire Inputs`. When it errors, the error cluster propagates and `Wire Inputs.vi` — the only VI that would ever have looked at `x` — **never executes**.

So there is no contradiction to explain. Your census at `:332` read `Node.Terminals[]` on `#10104`. `Get Controls.vi` reads control terminals on a *diagram*. The two calls address different objects; one succeeding and the other failing is not a paradox, it is two unrelated lookups.

**The record already discriminates the two sides, and you have both strings in the same file:**

| failing lookup | `source` field | example |
|---|---|---|
| a node's **output** name | `Get Outputs.vi` | `run5.log:392` — `error 5001: LV-Scripting.lvlib:Get Outputs` |
| a **control label** | `Get Controls.vi` | `run5.log:402` — the row under discussion |
| an **indicator label** | `Wire Indicators.vi` | `tools/bench/build_harness_dispI.log:31,:70,:71` |

5001 is the library's generic *"named object not found"*; the `source` field says which side. The claim reads the wrong side.

**And the destination-addressing story is refuted by variance.** `tools/bench/build_d1_v0_run9.log:315-320` shows **six** identical `error 5001: …Get Controls.vi<ERR>` failures spanning **five different control labels** and **three different destination classes** — `Function.['y']`, `ForLoop.['Force\nsmoothing\nhalf-width']`, `CaseStructure.['Correction Factor']`. No destination-addressing defect is invariant across three node classes and six different destination names. `build_d1_v0_run7.log:295-301` is the same six, a run earlier.

Finally, `Function` destinations demonstrably work: `run5.log:367` — `wire_control 'Auto-Reset' -> 'y'` onto `Function #9647` t1, `attempts [(24, 'no error', 28475)]`. Same op, same destination class, same run.

---

## 2. The alternative explanation — measured, and it is a *repeat*

**The temp-sink call searched the wrong diagram for the control.**

- `tools/recipes/build_d1_routeb_v2.py:1376-1377` passes a **single, unconditional** `src_diagram_index=diag_index(TARGET, FRAME_BODY_UID)`, and `FRAME_BODY_UID = 639` (`:288`) is the *original* frame body.
- `Z/dZ`'s `ControlTerminal #403` is no longer there: `run5.log:171` — `PASS S3-ct ControlTerminal #403 ('Z/dZ') -> 1.2  owner Diagram#567`.
- The five sibling labels went through the **other** code path (`:1567-1584`), which tries **both** diagram indices, and all five landed on index **24** on the first attempt (`run5.log:367,:369,:381,:382,:387`, all `reparented=True`). Since `order` begins with `sd_moved` when the label is in `ct_moved`, **`diag_index(#567) == 24`** — and #639's diagram, being a different object, cannot also be 24.
- The temporary `Equal?` was itself created on **`Diagram[24]`** (`run5.log:332`). So one call placed its sink on diagram 24 while asking `Get Controls` to search the stay diagram. It is internally inconsistent on its face.
- `Get Controls.vi` sees **only** control terminals on the diagram index it is given — measured 2026-09-01, `gscript.py:1890-1891`.

**This is the same mistake for the third time, and the recipe says so in its own comment**: `build_d1_routeb_v2.py:1562-1566` — *"run 9 failed with six 5001s from `Get Controls.vi` for exactly that reason"*. The two-index retry was the fix. The temp-sink branch at `:1376` is the **one call site that never received it**. Your archive already reached this conclusion once: `archive/peer/2026-09-17-zdz-wirecut-opus.md:177-180` records the reorder as *"itself a fix for run 7's six 5001s."*

A second, cheaper-to-exclude variant of the same alternative: the label string. `Z/dZ` is the only one of the six containing `/`, and `docs/NAMES.md` exists precisely because these strings are literal. A caption/label mismatch or a stray character produces the identical error from the identical VI. The test below separates this from the diagram-index cause for free.

---

## 3. What would FALSIFY each

- **Falsifies the claim:** the same `wire_control` call to the same `Equal?` `['x']`, with `src_diagram_index = diag_index(loops["1.2"]["body"])`, **succeeding**. Then `x` was addressable by name all along and no index-addressed op was ever needed.
- **Falsifies my alternative:** that call still raising 5001 from `Get Controls.vi`. Then the source lookup fails for a different reason (label identity), and the diagram index was never the variable.
- **The only observation that would revive the claim:** a 5001 whose `source` is `Wire Inputs.vi`, or whose `<ERR>` description names `x`. Nothing in any log on this disk shows that.

---

## 4. Cheapest discriminating test (the mandated closer)

**One op run on a throwaway copy. No new op, no build, no `OpConnectFromWire_v0`, no `OpConnectNested_v1`.**

On a scratch copy taken to the same point (or on the kept crash copy, `…\claudeDev\SCRATCH_routeb_235020_crash_001808.vi`, `STATUS.md:21` — use it before the next run's S0 deletes it), call the failing `wire_control` **twice**, changing exactly one argument:

1. `src_diagram_index = diag_index(TARGET, FRAME_BODY_UID)` — reproduce the failure.
2. `src_diagram_index = diag_index(TARGET, loops["1.2"]["body"])` — the diagram `#403` actually lives on.

…and log the **full `error out` source string**, because you are currently discarding the answer: `gscript.py:396` returns `src.splitlines()[0]`, and LabVIEW's `<ERR>` tag is exactly where a library appends its custom **description**. Every 5001 in your logs ends at a bare `<ERR>` with nothing after it.

| outcome | verdict |
|---|---|
| (2) succeeds | claim dead; fix = pass the right diagram, or reuse the existing two-index retry at `:1567-1584` |
| both fail, description says *"Control 'Z/dZ' not found"* | source-side label identity; still not `x` |
| both fail, description names `x` | only now is the claim live |

Note what the claim's proposed fix would have bought: **the destination end is already proven on this very sink.** `OpConnectFromWire_v0` wired `#2222` t3 and t4 at `run5.log:385-386`, `Is Broken? FALSE`. Spending a build hardening the end that works, while the end that failed is untouched, reproduces `:402` verbatim.

---

## (a) What `error 5001` means in `lv-scripting` — external search does **not** settle it, and here is why

- The library ships as **compiled VIs**. `github.com/erdosmiller/lv-scripting` contains `images/ source/ tests/ vipb/`, `README.md`, `Scripting.lvproj` — **no error-definition file**, and the README documents no API and no error codes.
- **No `*errors.txt` is installed on this machine** under `LabVIEW 2026\user.lib` or `project\errors` (globbed; none). So LabVIEW has no registered description for 5001 — consistent with the bare `<ERR>`.
- What *is* externally settled: **5000–9999 is the user-defined error range** ([LabVIEW Wiki, Custom Error Code](https://labviewwiki.org/wiki/Custom_Error_Code)), and the `<ERR>` tag inside an error cluster's *source* string is how LabVIEW carries a **custom description** alongside the source ([NI Community, custom error messages](https://forums.ni.com/t5/LabVIEW/Best-way-to-throw-custom-error-from-SubVI/td-p/1332790); [NI, Defining Custom Error Codes](https://www.ni.com/docs/en-US/bundle/labview/page/defining-custom-error-codes-using-the-general-error-handler-vi.html)).

**Conclusion:** 5001 is Erdos Miller's own *"named object not found"*, and its meaning is disambiguated by the `source` VI — a reading your own `gscript.py:1882-1883` docstring already states ("*a control label that does not exist raises from Get Controls ('Control %s not found')*"). The library's literal wording is probably sitting in the error cluster you are truncating. That costs zero LabVIEW time to recover.

## (b) Does `wire_control` address front-panel controls only?

**The source end, yes. The destination end is a node — and that end is not the problem.** `OpWireCtl_v0` is name-addressed on *both* ends but on *different object kinds*: `Get Controls.vi` (control terminals on a diagram) → `Wire Inputs.vi` (a node's named input terminals). The library's own example set confirms the split — `Example 1 - Getting Controls and Wiring Indicators.vi` alongside `Example 3/4 - Primitive Functions` (`…\vi.lib\Erdos Miller\LV-Scripting\`, `…\examples\Erdos Miller\LV-Scripting\examples\`).

**The evidence that settles it** is in the failing run itself: the same op wired controls into `Function`, `ForLoop` and `CaseStructure` destinations five times (`run5.log:367,369,381,382,387`). It is not the wrong op for a Function input terminal.

## (c) The strongest case that the ROUTE is unsound, not the addressing

Asked for honestly, even though I judge §2 the live explanation. Two hazards, neither touched by any addressing fix:

**(i) The next guard has already fired on another row in this same run.** After the sink, `build_d1_routeb_v2.py:1386-1389` requires `wire_source_owner(zw)` to return **exactly one** source terminal, else NO-ROUTE. At `run5.log:404` that guard killed `#10407 t1`: *"w9649 has 0 source terminals, not 1: []"*. **Nobody has measured what `wire_source_owner` returns for a wire whose source is a `ControlTerminal`** rather than a node output — and `ControlTerminal` is precisely the class this fleet's index-addressed ops cannot see (`Diagram.Nodes[]` does not list them; `run5.log:331`, externally confirmed at `archive/peer/2026-09-17-zdz-wirecut-opus.md:130`). The temp sink changes *which op meets* the ControlTerminal; it does not stop the ControlTerminal being the source. If that call is node-based, the row dies one line later for the same underlying reason the REORDER route died — and the claim's fix would not have helped.

**(ii) The delete tail is allowed to undo the work.** `:1395-1403` deletes the temporary and runs `remove_bad_wires_scripted`; the recipe's own comment concedes *"the branch and the temporary's own segment belong to ONE net, so deleting the sink node can take the branch with it"*. "Wired, then unwired by the cleanup" is a legal outcome of this route. It is at least instrumented, so it will be measured rather than inferred — which is why I rank it below (i).

**(iii) And the uncomfortable one:** this is 1 of 66 rows in a VI that by `STATUS.md:52` cannot reach `ExecState 1` regardless (8 queues and 3 sentinels unbuilt ⇒ three While loops with unwired conditional terminals). `archive/peer/2026-09-17-zdz-wirecut-opus.md:185-188` made this point and it was not answered. If the next expensive build's justification is "the `Z/dZ` row", that justification is weak whichever mechanism wins.

## (d) `error 2` when memory is plainly not exhausted

**First: your refutation #4 does not hold, for two independent reasons.**

1. **The counter cannot see the resource.** `bench_prep.labview_handles()` reads `Get-Process LabVIEW … .HandleCount` (`tools/bench/bench_prep.py:64-71`) — **kernel object handles**. LabVIEW VI-Server/GObject **refnums are not kernel handles**; neither are **GDI** or **USER** objects (those need `GetGuiResources` / Process Explorer's GDI column). 38,824 vs 51,284 is silent about every mechanism below.
2. **Even for memory, the comparison is invalid.** `mFullErr` is returned for *one failed allocation*; contiguity and fragmentation are path-dependent, so failing at a lower total than an earlier success is ordinary. And the two readings come from **two different LabVIEW processes** (both runs restarted) — not two points on one curve.

Concrete mechanisms, most-likely first:

- **Refnum-class exhaustion.** LabVIEW permits at most **2²⁰ simultaneously open references of the same type**; past that, allocation fails ([LAVA, "Error 2: Memory is full — but it isn't"](https://lavag.org/topic/18730-error-2-memory-is-full-but-it-isnt/), Aristos Queue). `Traverse for GObjects` returns an **array of GObject refnums on every call**, and this recipe runs `report_all(Diagram)`/`count()` per row. Leaked traverse arrays are thousands of invisible refnums per row — and `CLAUDE.md`'s own reference-hygiene rule already names "Traverse arrays" as something every op must close. **The observed pattern fits: error 2 is sticky** — six consecutive `report_all` failures (`:396-401`) then the `count` crash (`:406`), never recovering. Fragmentation would be intermittent; a monotonic resource crossing a threshold is not.
- **GDI/USER quota** — default 10,000 per process (`GDIProcessHandleQuota`); LabVIEW surfaces failed GDI allocation as mFullErr ([NI forum](https://forums.ni.com/t5/LabVIEW/The-GDI-Object-limit-problem/td-p/2399534), [Microsoft, GDI Objects](https://learn.microsoft.com/en-gb/windows/win32/sysinfo/gdi-objects)).
- **`Open VI Reference` failing** — NI's KB titles error 2 exactly *"when Opening a New Reference"* ([NI KB](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019KhWSAU)); every op opens a reference to the target by path.
- **A VI in an inconsistent state.** LAVA reports error 2 on a corrupted VI even with a blank diagram. This build reparents six ControlTerminals across diagrams and moves shift registers with their nodes; a recursive traverse over an inconsistent owner graph is a plausible producer. `Traverse for GObjects` also has documented class-specific failures ([NI, VI Scripting: Error Ring](https://forums.ni.com/t5/LabVIEW/VI-Scripting-Error-Ring/td-p/3957513)).
- Legacy code reuse: error 2 also means GPIB "no listeners" — irrelevant here, but it is why the string deserves no trust.

**Cheap discriminator for (d)**, one background run, read-only: loop `g.count(TARGET,"LoopTunnel")` on **(A)** a pristine copy and **(B)** the kept `SCRATCH_routeb_235020_crash_001808.vi`, logging call number, kernel handles **and GDI count** each iteration. Same *call count* on both ⇒ refnum/GDI leak in our ops. Immediate on B, never on A ⇒ diagram state. That run also supplies the "20 runs, handles flat ±100" measurement `CLAUDE.md` requires of `OpReport_v3` and which has never been taken on the dimensions that matter.

---

## One unreported fact worth flagging

`STATUS.md:21` and `:69-72` now assert, at the top level of the project, that *"handle pressure is refuted as the cause a second time."* On this evidence it is not refuted — it is **unmeasured**, by a counter that cannot observe any of the candidate resources, across two different processes. That sentence is one relocation away from becoming a settled premise nobody re-examines.

**Sources:** [erdosmiller/lv-scripting](https://github.com/erdosmiller/lv-scripting) · [LabVIEW Wiki — Custom Error Code](https://labviewwiki.org/wiki/Custom_Error_Code) · [NI — Defining Custom Error Codes](https://www.ni.com/docs/en-US/bundle/labview/page/defining-custom-error-codes-using-the-general-error-handler-vi.html) · [NI Community — throwing custom errors / `<err>` tag](https://forums.ni.com/t5/LabVIEW/Best-way-to-throw-custom-error-from-SubVI/td-p/1332790) · [LAVA — Error 2: Memory is full, but it isn't](https://lavag.org/topic/18730-error-2-memory-is-full-but-it-isnt/) · [NI KB — Error 2 when Opening a New Reference](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019KhWSAU) · [NI Community — GDI Object limit](https://forums.ni.com/t5/LabVIEW/The-GDI-Object-limit-problem/td-p/2399534) · [Microsoft — GDI Objects](https://learn.microsoft.com/en-gb/windows/win32/sysinfo/gdi-objects) · [NI — Traverse for GObjects VI](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/vi-lib/utility/traverseref-llb/traverse-for-gobjects-vi.html) · [NI Community — VI Scripting: Error Ring](https://forums.ni.com/t5/LabVIEW/VI-Scripting-Error-Ring/td-p/3957513)

## Sources

(extract from answer)

## What was done with it

Dispatched by the cycle-37 MATERIAL session (dispatch 3) as the MANDATORY failed-prediction review for run 5's new
failure, `tools/bench/build_d1_routeb_v2_run5.log:402`. Single arm per `docs/cycle27-plan.md` Pre-decided 7:
`-Agent claude -Role hypothesis` (opus / effort max). Outcome **ANSWERED (640 s), COST $3.9728**, dispatch log
`tools/bench/peer_zdz_5001.log`.

MATERIAL disposition — RECORDED, not decided (the route call and the recipe patch are judgement's):

- The peer **REFUTES judgement's claim at its first noun**: `Get Controls.vi` is the SOURCE-side resolver, so the
  name it failed to find is `'Z/dZ'`, not `'x'`, and `Wire Inputs.vi` — the only VI that would have looked at `x` —
  never executed. There is therefore no contradiction between the `:332` census and the `:402` error: two unrelated
  lookups on two different object kinds.
- Its alternative, and it is a REPEAT: `build_d1_routeb_v2.py:1376-1377` passes one unconditional
  `src_diagram_index=diag_index(TARGET, FRAME_BODY_UID)` with `FRAME_BODY_UID = 639` (`:288`) — the STAY diagram —
  while `ControlTerminal #403` had already been reparented to `Diagram#567` (`…run5.log:171`) and the temporary
  `Equal?` was created on `Diagram[24]` (`…run5.log:332`). The five sibling labels used the OTHER code path
  (`:1567-1584`), which tries BOTH diagram indices, and all five succeeded on index 24. The temp-sink branch is the
  one call site that never got the two-index retry the recipe's own comment (`:1562-1566`) says was added after run
  9's six identical 5001s.
- Independent local confirmation found by this session while the peer ran, same conclusion, different evidence:
  `tools/gscript.py:1882-1883` ("a control label that does not exist raises from Get Controls"),
  `docs/toolkit-capabilities.md:67` ("`wire_control` (name-addressed, 5001 from `Get Controls.vi`/`Get Outputs.vi`)")
  and `docs/NAMES.md:152-153` (`Get Controls` lists only pane-root controls; `src_diagram_index` exists for this).
- Its cheapest test costs ONE op run on a throwaway copy — the same `wire_control` twice, changing only
  `src_diagram_index`, and logging the FULL `error out` source string, which `tools/gscript.py:396` currently
  truncates at `src.splitlines()[0]` and so discards the library's `<ERR>` description.
- ⚠️ Two findings it raises that nobody asked for, both carried to judgement: (c)(i) `wire_source_owner` has never
  been measured on a wire whose source is a `ControlTerminal`, and that guard (`:1386-1389`) already killed another
  row at `…run5.log:404`; and (d) the `error 2` refutation in `STATUS.md:21` is **unsound** —
  `bench_prep.labview_handles()` reads KERNEL handles (`tools/bench/bench_prep.py:64-71`), which cannot observe VI
  Server refnums, GDI or USER objects, and the two readings come from two different LabVIEW processes.
- NOTHING WAS PATCHED on this evidence: the brief forbade touching the recipe, and the fix is a route decision.
