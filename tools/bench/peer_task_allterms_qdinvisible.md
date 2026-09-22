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
