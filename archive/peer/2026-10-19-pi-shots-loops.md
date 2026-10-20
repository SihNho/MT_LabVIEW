# pi-shots-loops

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.3330  in 32 / out 13147 / cache-create 87616 / cache-read 1342673  (198s, 27 turn(s))
- **date:** 2026-10-19 11:13:20
- **outcome:** ANSWERED (202s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim (judgement session, 2026-10-19), about the failure in tools/bench/pi_shots_loops.log
(script tools/bench/pi_shots_loops.py; first failure: "W P6L #637 ... error 1 Write PNG File.vi / Check Color Table
Size.vi", pi_shots_loops.log:229; facts in tools/bench/cards/result_chat-PI3.json and pi_shots_20261016/loops_p6l.json).

Claim: Node.Get Image (6358C01, via OpGetImage_v0) cannot image the P6L While loops because those loops report GObject
Bounds height 0 (8860x0, 36528x0, 3710x0, 35789x0, all at y 223) - they sit inside a FlatSequenceFrame (owner hops
there give error 1055), so the zero-height image makes Write PNG fail; the two loops that did image came out all white
for a related reason. Handles are NOT the cause (flat after the first shot). The original VI's While #637 imaged fine
because it is not inside such a frame. Therefore the next step should NOT retry Node.Get Image on P6L loops, but take
the WHOLE block diagram of both the original copy and the P6L copy with the verified VI method BD.Get Image Scaled
(42C, OpGetBDImage_v0.vi, hygiene PASS) with Maximum Width/Height wired (e.g. 4000) so LabVIEW scales the huge P6L
diagram down - one fresh LabVIEW per VI.

Attack it: is "height 0 because of the FlatSequenceFrame" supported by the log, or could it be the headless load (no
diagram window opened), a stale layout, or the P6L copy's missing subVIs? Would BD.Get Image Scaled hit the same
zero-height / white-image problem on a headless P6L load? What one check before the run would tell? Read:
tools/bench/pi_shots_loops.log, tools/bench/pi_shots_20261016/loops_p6l.json, tools/bench/cards/result_chat-PI3.json,
tools/bench/cards/result_chat-PI2b.json, tools/bench/pi_shots_20261019.log (P6-1 vs P6L run).


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**No. The project's own logs contradict the claim that the loops have height 0 because they sit inside a FlatSequenceFrame.** Being inside that frame is common to the loops that failed and the ones that worked, so it can't be the cause. The proposed whole-diagram BD.Get Image Scaled run would probably fail the same way. I ran nothing, took no lock and edited nothing. The plan file could not be written because Write is disabled in this session, so the full review is only in this reply.

## 1. The strongest reason the claim is wrong
- **The loops that worked are in the same frame.** All six P6L loops have the same owner, Diagram #686, which belongs to a FlatSequenceFrame. That includes the two with non-zero Bounds, #25380 at 2538x504 and #1175 at 3594x32756 (`tools/bench/pi_shots_loops.log:92-93,118-119,132-133`).
- **The same loop worked in the previous version.** In P6-1, #10170 has the same parent chain (Diagram 686 → FlatSequenceFrame → FlatSequence 681), shown at `pi_shots_20261019.log:17-18,31`. Its image came out 5827x6014, equal to Bounds (`pi_shots_20261019.log:45`). In P6L the same loop reads 36528x0.
- **The original was never shown to be outside the frame.** The original VI also has Diagram #686 owned by a FlatSequenceFrame (`pi_shots_20261016e.log:19`). Its recorded parent chain for #637 stops at #637 (`:14`), so nothing shows #637 is outside it. Most likely it sits in the same place.
- **The error 1055 is not evidence.** Every frame-owned diagram gives error 1055 on the owner hop, in P6-1 and in the original too (`pi_shots_20261019.log:18`). That includes the frames whose contents imaged fine.

## 2. An alternative explanation of the same evidence
**P6L's diagram has grown past LabVIEW's 16-bit coordinate range.** NI says a panel or diagram spans −32768 to 32767 pixels, and going near or past that limit causes "unexpected behaviors" ([NI KB](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019LqySAE&l=en-US)). A third-party write-up says the practical limit is about 16,000 px because some internal rectangle sums overflow into negative or zero rectangles ([industrialmonitordirect](https://industrialmonitordirect.com/blogs/knowledgebase/resolving-labview-block-diagram-crashes-above-16000-pixels)). That second source is not official.

The P6L numbers fit this pattern closely (`loops_p6l.json`):

| Loop | What the log shows | Why it is suspicious |
|---|---|---|
| #10170 | 36528 wide (5827 in P6-1) | Wider than 32767, so the width itself cannot fit in 16 bits |
| #23041 | x 29057 + width 3710 | Right edge = 32767 exactly, the 16-bit maximum |
| #1175 | top −32533, height 32756 | Top is near −32768, bottom = 223 |
| #25380 | top −281, height 504 | Bottom = 223 |
| #637, #10170, #23041, #23032 | height 0 | Top = 223 |

So every loop shares the edge y = 223. That looks like one shared rectangle that was cut off or wrapped around, not something about frames. It also explains why the two "good" images were all white: if their visible area is clipped against a corrupt frame rectangle, nothing is drawn.

The other causes you asked about:
- **Headless load (no diagram window open):** weakened, not ruled out. P6-1 #10170 and P6L #22694, #15173 and #29724 all came out the right size when loaded the same way (`pi_shots_20261019.log:45,117,292,309`). But those runs checked only the size, never whether the image was blank. The only blank check ever made was on the P6L loops, so "headless gives white images" is still open.
- **Stale layout:** possible. Bounds this large may have been left in the file by the earlier scripting moves, and a headless load does not recompute them. The logs cannot tell this apart from the coordinate-overflow explanation.
- **Missing subVIs in the P6L copy:** unlikely. A missing subVI shows as a placeholder icon and does not change a loop's Bounds. The P6L load reported 709 nodes with no error. Nothing in the logs points at it.

## 3. What would falsify the claim
- A loop inside the frame in a VI with ordinary coordinates that images correctly. **This has already happened:** P6-1 #10170.
- P6L loops reporting real heights once the diagram window is opened, with no frame change at all.

## 4. Would BD.Get Image Scaled have the same problem?
Probably yes, on a headless load. The method shrinks the image to the Maximum Width/Height you wire in ([NI docs](https://documentation.help/NI-LabView-Local-Project-Settings/VI_Get_Diagram_ImageScaled.html), [LabVIEW Wiki](https://labviewwiki.org/wiki/VI_class/Block_Diagram.Get_Image_Scaled_method)). Neither page says whether it renders at full size before shrinking; I found nothing on that.
- The P6L diagram runs from about x −10439 to 32767 (about 43,200 px wide) and down to y −32533. That is beyond the 16-bit range on at least one axis.
- So the whole-diagram size would be computed from the same broken rectangles.
- If it does render at full size first, it is over a billion pixels. The 117-million-pixel #1175 image already set off PIL's size warning (`pi_shots_loops.log:47`).

The "hygiene PASS" for OpGetBDImage_v0 was measured only on small Op VIs, the largest 2988x2185 (`result_chat-PI2b.json:11`). It says nothing about a diagram this size.

The original copy and P6-1 have ordinary coordinates (the original #637 is at (2633, 927, 6387, 2832)), so the original-side shot is likely to work. The P6L side is the one at risk.

## 5. The cheapest check that separates the two explanations
This needs no image call. Use one fresh LabVIEW with only the P6L copy loaded headless, and only property reads:
1. Read the GObject Bounds and Position of FlatSequence #681 and of the six loops, plus the VI's block-diagram size metric ([Metrics.Size of Block Diagram](https://labviewwiki.org/wiki/VI_class/Metrics.Size_of_Block_Diagram_property)).
2. Open the block diagram window and read the same values again.
3. Close the reference, close LabVIEW, and verify it is gone.
4. Do the same steps on the P6-1 copy as a control.

What the results mean:
- **Heights still 0, or any size above 32767:** the P6L coordinates are corrupt. Do not run BD.Get Image Scaled on the whole P6L diagram; the fix is the layout, not the capture method.
- **Heights become real once the window is open:** the layout was stale in the headless load. Retry Node.Get Image with the window open. Either way, the frame idea is ruled out.

Also add the blank check to every future image gate, including the P6-1 and original shots. Until then, "headless is fine" has never been tested against white images.

## Sources

(extract from answer)

## What was done with it

Judgement session, 2026-10-19:
- Accepted: the FlatSequenceFrame explanation is refuted (P6-1 #10170 imaged 5827x6014 in the same chain; #25380 and
  #1175 are in the same frame). The whole-diagram BD.Get Image Scaled run on P6L is NOT dispatched.
- Open, recorded as a possible PRODUCT finding (not proven): P6L diagram coordinates near/over the 16-bit range
  (#10170 36528 wide vs 5827 in P6-1; #23041 right edge 32767; shared y 223). Next check, if the user wants it:
  property reads only (Bounds/Position of FS #681 + the six loops + Metrics.Size of Block Diagram), headless then with
  the diagram window open, P6-1 as control; no image calls.
- Future image gates include a blank check (already in pi_shots_loops.py; to be added to the others).
- The PI deck uses the original's While-loop image + a schematic of the current loops instead of a P6L photo.
