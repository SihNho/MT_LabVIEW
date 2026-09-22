# allterms-qd-invisible

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.9792  in 38 / out 43907 / cache-create 168119 / cache-read 2230842  (627s, 32 turn(s))
- **date:** 2026-09-23 06:42:12
- **outcome:** ANSWERED (631s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# Failed prediction: a node placed by LabVIEW's Quick Drop is ON the block diagram but ABSENT from a VI Server traverse

Attack the diagnosis below. LabVIEW 2026 (26.3.1f1) VI Scripting, driven headlessly over ActiveX/COM from
Python on Windows 10. Read-only research; you have no LabVIEW here. Your job is to REFUTE, not to confirm.

## What we did, and what we predicted

We need a `To More Specific Class` (TMSC) node inside a For-loop body of a VI we are building. It has no
scripted creator in our fleet, so — as an authorised, enumerated GUI exception — we place it with Quick Drop:

1. front the block-diagram window (`SetForegroundWindow`, verified by `GetForegroundWindow()` afterwards),
2. one REAL left mouse click on that window's TITLE BAR (this is required: without it the next COM call
   blocks — see "already ruled out" below),
3. move the mouse (hover only, no click) to a point on the diagram canvas,
4. `SendKeys` Ctrl+Space — a window titled exactly `Quick Drop` appears (we enumerate top-level window
   titles to check this, no COM involved),
5. `SendKeys` the literal text `To More Specific Class`, then Enter — the `Quick Drop` window disappears,
6. one REAL left mouse click on the title bar again,
7. over COM, run our own "report everything of class X" op VI against the target VI's PATH.

**Predicted:** step 7 returns one new object of Traverse class `Function`.
**Observed:** step 7 returns exactly the same set of uids as before the drop — no new object.

## The node really is there

Full-screen captures taken immediately before step 3 and immediately after step 5, cropped to the SAME
130x130-pixel screen region centred on the drop point and magnified 6x: the "before" crop is uniformly blank
canvas; the "after" crop shows the unmistakable `To More Specific Class` icon (the class-hierarchy glyph with
an arrow into a filled node). So the editor placed the node at the mouse position. Nothing was saved; the VI
was left modified in memory.

## Already ruled out, by measurement, in our own logs

- **"The class filter is wrong."** REFUTED. A TMSC's Traverse class IS `Function`. On a VI that has carried a
  TMSC on disk for days (`OpLoopCast_v0.vi`, uid 683), all three of our readers return it: the one-object-at-a-
  time reporter, the array reporter with class `Function`, and the array reporter with class `Node` — the last
  reports its `Class Name` as the string `Function`. 4 gates pass / 0 fail, donor md5 unchanged.
- **"The COM call failed silently."** Our reader raises on a non-empty error cluster and did not raise; it
  returned a well-formed array containing the VI's pre-existing objects.
- **"LabVIEW's UI was still modal."** This WAS the failure of the previous run (no real mouse click anywhere;
  the identical COM call then never returned within 180 s). Adding the title-bar click removed the hang
  completely — the run that produced the observation above completed all its COM calls in 86 s total.
- **"The op looks at a different file."** The target is addressed by full path, the path is the one open in the
  editor (the window title carries the same file name), and the reader found that VI's OTHER objects.

## The two hypotheses we hold, which you should attack

- **(a) UNCOMMITTED-WHILE-SELECTED.** The freshly dropped node is still selected and LabVIEW has not committed
  the edit into the VI's object model that VI Server traverses; a deselect (a click on empty canvas) or any
  further editor interaction would commit it.
- **(b) STALE VI REFERENCE.** Our op VI reaches the target through `Open VI Reference` on a path; that
  reference (or the traverse behind it) is serving an image of the VI from before the GUI edit, and only a
  save + close + re-open would refresh it.

## What to answer

1. The strongest reason (a) is wrong.
2. The strongest reason (b) is wrong.
3. **A THIRD explanation we have not considered**, consistent with all the measurements above.
4. What would FALSIFY each of the three.
5. The single CHEAPEST discriminating test, given that each attempt costs us a scarce failure budget. Say
   exactly what to do and exactly what reading separates the cases.

Cite NI documentation, the LabVIEW Wiki, or NI/LAVA forum threads where you can; say plainly when you are
reasoning rather than citing. Be concrete about LabVIEW's own semantics (VI Server object model vs the
editor's undo/transaction state, `Open VI Reference` caching, the difference between a VI in memory and a VI
on disk, and anything Quick Drop does differently from a palette drop).


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled in this session (correct — I'm the read-only reviewer). Here is the review.

---

# The prediction did not fail. The traverse was right; the recipe never places the node.

## 0. The single strongest reason the framing is wrong

Quick Drop's **Enter does not place an object.** It loads the object onto the mouse cursor and waits for a click on the canvas.

> "Quick Drop automatically places the highlighted item **on the mouse cursor** so you can type the name of a function and **click once on the block diagram or front panel to place the object**." — [NI, *Boost LabVIEW Productivity with Quick Drop*](https://www.ni.com/en/support/documentation/supplemental/08/boost-labview-productivity-with-quick-drop.html)

> "Pressing Enter while Quick Drop is active will place the top list item **on your cursor**, which you can then use to drop the object in the desired location." — [LabVIEW Wiki, *Quick Drop*](https://labviewwiki.org/wiki/Quick_Drop)

Now the recipe's actual drop sequence, `tools/bench/allterms_s2.py:96-130`:

| step | call | lands where |
|---|---|---|
| 2 | `unwedge()` → `-Action click -X 400 -Y 10` | **title bar** |
| 3 | `-Action move -X 900 -Y 600` | hover only, **no click** |
| 5 | `keys "To More Specific Class"` + `key enter` | item goes **onto the cursor** |
| 6 | `shot(tag+"_after")` | capture — taken **before** any click |
| 7 | `unwedge()` → `-Action click -X 400 -Y 10` | **title bar again** |
| 8 | `g.uids(s.work,"Function")` | traverse → nothing new |

**Not one left-click lands inside the canvas anywhere in that sequence.** Your own author wrote the decisive sentence at `allterms_s2.py:80`: *"`-Action move` is a hover, not a click, so run 1 never delivered one."* That missing click was diagnosed as the cause of the COM hang. It is also why there is no node.

And the loop closes on itself: the mandatory `unwedge` click at step 7 is the only real click after Enter, it lands on the title bar outside the canvas, and under the documented semantics it discards the pending object. **The fix for the hang and the cause of the empty traverse are the same act.**

## 1. Strongest reason (a) UNCOMMITTED-WHILE-SELECTED is wrong

LabVIEW has no "uncommitted edit" tier hidden from VI Server. The editor and VI Scripting share one in-memory object model; selection is a property of an object that already exists. Your fleet depends on this every run and has never needed a deselect: `allterms_s2.log:19-20` reads the loop's position straight back after `move_object`; `gscript.py:1064-1072` (`new_since`) is built entirely on mutate-then-traverse. If a pending-commit tier existed, the fleet would be flaky in exactly this way.

**Trap — the obvious test for (a) is confounded.** "Click empty canvas to deselect, re-traverse" is what (a) prescribes, and it is *also* exactly what my explanation predicts will work, because a canvas click is what places a cursor-loaded object. A node appearing after that click proves nothing. §5 has the version that discriminates.

## 2. Strongest reason (b) STALE VI REFERENCE is wrong

[NI's Open VI Reference page](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/functions/open-vi-reference.html): the function *"either creates a reference to a VI **already loaded in memory** or loads a VI into memory from a file path."* LabVIEW holds one copy per application instance; the panel was opened over the same COM connection (`allterms_s2.py:163`) and lives in the same process (`allterms_s2.log:96`). There is no pre-edit image to serve. A VI Server reference is a live handle, not a snapshot. (b) also proves too much — under it no editor-side change would ever be visible, yet `gui_save` and Ctrl+E workflows read state back routinely.

**Honest caveat:** on the evidence you actually took, (b) and my explanation are *indistinguishable* — both predict "the traverse returns the pre-drop set". (b) dies on documented semantics and fleet history, not on your measurement.

## 3. The third explanation

**(c) The object was never placed. It was riding the cursor, and the title-bar click discarded it.**

| observation | (c) explains it as |
|---|---|
| Quick Drop closes on Enter | documented — Enter closes it and loads the cursor |
| the icon appears at the drop point | the pending object under the cursor; the capture at `allterms_s2.py:125` is taken **before** the only subsequent click |
| traverse returns the pre-drop set | **correct** — no object exists |
| **run 1 hung 180 s** (`allterms_s2.log:32-48`) | editor in a pending-drop tracking state, no click ever delivered |
| **run 2 returned in 86 s once the title-bar click was added** | the click resolved the pending drop — by cancelling it |

(a) and (b) explain neither of the last two rows. (c) explains both with one mechanism. That asymmetry is the argument.

**Where (c) is weak, stated plainly:** `lv_gui.ps1:585-590` captures via `Graphics.CopyFromScreen`, which does **not** composite the Windows mouse cursor. If LabVIEW renders "object on cursor" as an HCURSOR bitmap, the icon could not have been captured at all, and its presence would argue the object *was* placed. If LabVIEW instead paints the pending object into the diagram's own DC, the capture is exactly what (c) predicts. **I cannot tell which from your files, and neither can you from what was measured.** §5 settles it for free.

## 4. Three "already ruled out" claims that are weaker than stated

- **"The class filter is wrong — REFUTED."** Your control (`allterms_tmscclass.log:4-6`) tested a TMSC whose `owner` is `TopLevelDiagram` on all three Functions; the failing case is a drop *inside a For-loop body*. The control never tested recursion. **I checked and it survives** — NI documents `Traverse for GObjects.vi` as recursive ([source](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/vi-lib/utility/traverseref-llb/traverse-for-gobjects-vi.html)), and `allterms_s1.py:70,85` shows `report('Property')` returning body-owned nodes (`owner 'Diagram'`). It stood by luck, not by the control you cited.
- **The brief merges two runs.** The screenshot narrative at `allterms_s2.py:74-80` cites run 1's `061628_calib_after.png`; the traverse observation is run 2's (`allterms_s2.log:103`). Run 1 produced **no traverse result at all** — it timed out and poisoned the module. Run 2 does have its own capture showing the icon at ≈(900,591), so the conclusion is unaffected, but two runs should not be presented as one experiment.
- **`unwedge()`'s docstring states a general law** ("LabVIEW's UI loop blocks COM until a real mouse click lands") from one observation. The narrower reading — COM blocked because *a drop was pending on the cursor* — fits better and is now being generalised fleet-wide.

## 5. Falsifiers and the cheapest discriminating test

**Falsifiers.** (a): the node appears at the *placing click* position rather than the hover point. (b): the node ever appears without a save + close + reopen. (c): the node appears in a traverse with **no** click after Enter, or its position is independent of where the placing click lands.

**Cheapest test — free: zero LabVIEW runs, zero COM calls, zero failure budget.** Add **one** `-Action shot` immediately *after* the existing post-Enter `unwedge` click at `allterms_s2.py:126`, same 130×90 crop. You take a before and an after; this is the third capture nobody took.

- **icon GONE** → never placed; the title-bar click discarded it. **(c) confirmed, (a) and (b) both dead.** A placed node does not vanish on a title-bar click.
- **icon STILL THERE** → it was placed. (c) dead; then save + close + reopen + re-traverse to separate (a) from (b).

**The confirming-and-curing run — the single run you were going to spend anyway.** Make the post-Enter click land **on the canvas at a point B clearly different from the hover point A** (≥200 px, still inside the loop body):

```
move → A ; Ctrl+Space ; type ; Enter ; move → B ; REAL left click at B ; report_all('Node')
```

| result | conclusion |
|---|---|
| new node at diagram coords of **B** | **(c)** — cursor-loaded, the recipe never clicked. You also get the node you wanted. |
| new node at diagram coords of **A** | **(a)** — already placed at A, the click merely committed it. |
| **no** new node | **(b)** or other; now save + close + reopen + re-traverse. |

Read with `'Node'`, not `'Function'`, so a wrong-class drop (To More *Generic* Class, or a same-named subVI, which would be class `SubVI`) shows as a count change instead of another silent zero. Run the free capture test first — if the icon is gone, no further LabVIEW run is needed to diagnose, only to build.

**What would change my mind:** a post-click capture showing the icon still at the hover point, or a LabVIEW 2026 release note stating Enter now places directly (the two sources above are the general behaviour; a non-default Quick Drop configuration or double-click instead of Enter could differ).

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
