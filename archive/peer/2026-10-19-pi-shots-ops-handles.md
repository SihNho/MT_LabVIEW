# pi-shots-ops-handles

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $0.9245  in 18 / out 9819 / cache-create 65653 / cache-read 594669  (125s, 19 turn(s))
- **date:** 2026-10-19 11:01:28
- **outcome:** ANSWERED (129s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim (judgement session, 2026-10-19), about the failure in tools/bench/pi_shots_ops.log
(script tools/bench/pi_shots_ops.py, gate at :114, failure line: "H handles at end <= start + 1000 (34003 -> 35474)").

Claim: the +1,471 rise in the LabVIEW process handle count during pi_shots_ops.py is NOT a reference leak of our ops and
does not invalidate the seven Op PNGs, because (1) the script's own ref counter says refs opened 7 / closed 7 / live 0
(pi_shots_ops.log:56-57); (2) the rise happened after loading seven Op VI copies into one LabVIEW (each load brings its
subVIs, front panels and diagrams into memory, which costs OS handles that LabVIEW keeps until the VIs leave memory);
(3) OpGetBDImage_v0.vi itself passed the 2,000-call op_hygiene run with max_dev_closed 23
(tools/bench/op_hygiene/OpGetBDImage_v0.json, build_op_getbdimage_v0b.log:51); (4) LabVIEW was killed and verified gone
afterwards, so nothing persists.

Attack it: what else could explain +1,471 handles (BD.Get Image Scaled loading the diagram/front panel of each VI,
image buffers, Write PNG File, unclosed VI refs inside OpGetBDImage_v0, the 1000 threshold being arbitrary)? Which of
these would matter for the planned next step - one more run of tools/bench/pi_shots_loops.py that opens ONE large VI
(P6L, 54f7cd2f) alone in a fresh LabVIEW and calls OpGetImage_v0 (Node.Get Image) on 6 While loops? State what check
would distinguish "loaded-VI handles" from "op leak" cheaply, and whether the Op PNGs should be trusted.
Read: tools/bench/pi_shots_ops.log, tools/bench/pi_shots_ops.py, tools/bench/op_hygiene/OpGetBDImage_v0.json,
tools/bench/build_op_getbdimage_v0b.log, tools/bench/cards/result_chat-PI2b.json.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict:** the conclusion probably holds: this is a one-time load cost, not a leak, and the seven Op PNGs can be used. But three of the four reasons given don't support it, and the one that does is half wrong about where the handles went. The run cannot tell a load cost from a leak, because it took no handle reading between ops.

## 1. Strongest reason the claim is wrong: reason (1) is not evidence

- The project's own code says this counter cannot be used this way. `ref_counts()` counts only the references Python opens through gscript. Its docstring says these counters "CANNOT see refnum-class exhaustion inside an op VI and must never be cited as if a flat reading here excluded it" (`tools/gscript.py:462-467`).
- So "opened 7 / closed 7 / live 0" (`pi_shots_ops.log:56`) says nothing about the Open VI Reference or Get Image calls inside `OpGetBDImage_v0`.
- Reason (3), the 2,000-call hygiene run, doesn't cover this run's conditions either:
  - It ran on one small diagram only: OpReport_v3, 857×321 (`OpGetBDImage_v0.json:41`).
  - It read handles after the copy was **closed** each round (the `h_closed` series, `:91-111`). `pi_shots_ops.py` never closes any of its seven copies: `ensure_loaded` opens each panel and leaves it open (`gscript.py:1626`).
  - Four of the seven diagrams are 2.4 to 7.6 times larger in area than anything the hygiene run measured (`pi_shots_ops.log:15,20,25,35`).
- Reason (4), "killed afterwards", is true but beside the point. What matters for the next step is growth **within** one session.

## 2. A different explanation of the same numbers

Most of the +1,471 has nothing to do with the seven copies. It is what loading one image op plus a first target costs:

| run | after restart | first hygiene sample | rise |
|---|---|---|---|
| OpGetBDImage build | 33,994 (`build_op_getbdimage_v0b.log:32`) | 35,168 (`:38`) | +1,174 |
| OpGetImage build | 34,004 (`build_op_getimage_v0d.log:58`) | 35,219 (`:64`) | +1,215 |

Each of those had **one** op and **one** small copy loaded. That leaves only about 250–300 handles for six more copies and gscript's report and subVI ops (`cached_op_vis 3`).

So the claim's explanation in (2), that the seven copies each brought in their subVIs and panels, is mostly wrong about the source. The gate itself was the bad prediction. The script expected "back near the baseline with only small VIs loaded" (`pi_shots_ops.py:20-21`). The card's own build log from five minutes earlier already showed the baseline sitting about 1,170 above that. The 1,000 limit was set below a cost that had already been measured.

These data do **not** rule out a small leak on each call to a large diagram (for example 20–40 handles per call). It would be hidden inside the 250–300 that is left.

## 3. What would prove the claim wrong

Call the op repeatedly on one large diagram that is already loaded:
- **Leak:** handles climb steadily with each call.
- **Load cost:** one step up, then flat.

A second sign of a leak: after the copies are closed without saving, handles do not fall back to the level of "op loaded, no copies".

## 4. What matters for `pi_shots_loops.py` (P6L, OpGetImage_v0)

- **Reason (3) doesn't apply.** That script uses OpGetImage_v0 (Node.Get Image), not OpGetBDImage. The hygiene record that applies is `op_hygiene/OpGetImage_v0.json`: PASS, max_dev 10. But it imaged `Traverse('Node')[0]` of the small OpSetIndexMode_v0, so again only a tiny image (`:41`).
- **The real warning in the record is a different run.** In the session with P6-1 and P6L loaded, handles went from 34,311 to 64,876, a rise of 30,565 (`pi_shots_20261019.log:6,310`). In that same session, Write PNG failed with `error 1` on every P6L loop (`:105-115, :278-284`). NI forum posts read error 1 from Write PNG File as invalid input, typically an empty image passed in ([NI forum: Error 6 when using Write PNG File.vi, p.2](https://forums.ni.com/t5/LabVIEW/Error-6-when-using-Write-PNG-File-vi/td-p/3907898/page/2)). Very large images have also been reported coming out as 0×0 ([NI forum: Saving extremely large images with IMAQ](https://forums.ni.com/t5/LabVIEW/Saving-extremely-large-images-with-IMAQ/td-p/2891502)). Loop #1175 is 3594 × 32756 px (`pi_shots_loops.py:17`).
- **That failure was never settled.** The run did not separate handle buildup from image size from "P6-1 was loaded first". The planned run removes only the third cause.
- **`pi_shots_loops.py` has no handle gate.** It only logs one handle reading at the end (`pi_shots_loops.py:149`). If it fails again, it can't separate those causes either.
- **On automatic cleanup:** NI states that LabVIEW closes a reference by itself when the top-level VI that opened it goes idle ([NI: Closing References in LabVIEW](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html)). Each op is run as a top-level VI over ActiveX, so references left open inside an op should not pile up from one call to the next. That supports "load cost" over "leak". It is documentation, not a measurement here.

## 5. Can the Op PNGs be trusted?

Yes, for what was checked. The handle count can't damage a PNG that was already written. What it does not show is that each PNG holds the **whole** diagram:
- Gate I checks only RGB, not blank, and size > 0 (`pi_shots_ops.py:110-111`). It never compares the PNG size to the diagram's own size.
- One cross-check exists: OpReport_v3 came out 857×321 in both the hygiene run and this run (`build_op_getbdimage_v0b.log:36`, `pi_shots_ops.log:10`).
- For the other six, a quick look at each picture for clipping is the remaining check.

## Cheapest test that tells load cost from leak

**No LabVIEW needed:** the comparison in section 2 already shows that about 80% of the rise matches the cost of loading one op.

**For the rest, add to the planned P6L run rather than a separate run.** Log handles right after `load()` and after every `take()`. Shoot one mid-size loop, say #637, three times in a row before the others.
- Flat after the first shot: load cost.
- A steady rise per shot: leak. Stop and investigate before trusting #1175.

This adds a few PowerShell handle readings and no extra LabVIEW session.

**What would change my mind:** a steady per-call rise in that repeated shot, or P6L handles going past about 40k before Write PNG fails again.

## Sources

(extract from answer)

## What was done with it

Judgement session, 2026-10-19:
- Accepted: the claim's reason (2) was mostly wrong about the source - ~80 % of the +1,471 matches the one-op load cost
  seen in both op builds; the +1000 gate in pi_shots_ops.py was the bad prediction. The seven Op PNGs are kept; the
  judgement session checks each picture for clipping by eye (OpReport_v3 matches its hygiene size 857x321).
- Applied to the next run (card chat-PI3): log handles after load() and after every take(); shoot #637 three times in a
  row first - flat after the first shot = load cost, steady rise = leak -> stop before #1175; report the handle count
  when Write PNG fails (the 34,311 -> 64,876 rise of the P6-1+P6L session is the unsettled warning).
