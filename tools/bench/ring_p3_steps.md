# Ring P3 (camera loop 1.1 rows) - step list, card 123-2 (OFFLINE, 2026-10-01)

Design of record: `docs/ring-buffer-design.md` + `docs/d1-loop12-17-split-plan.md` PD238(b)(c)(d)(i), 241(d), 242(c).
Facts: `tools/bench/facts_c123_p3.json` (run `diag_c123_ring_p3_facts.log`, 18/0, on the P2b sim END graph
`sim/ring_p2b/step_10_create.json` md5 `830fbe67...`). Routes: `tools/bench/routes_c123_ring_p3.json` (run
`diag_c123_ring_p3_routes.log`). Base for both steps = the saved P2b bed (card 123-1), provisional until it exists.

## Bound facts the rows use (all `facts_c123_p3.json`)
- Loop 1.1 = While `#637` on FS1 frame `686`, body `639`; 4 existing shift registers (right 1117/862/15197/580).
- `#6810`: BufNum `current image number` t6897 (w3747, 5 sinks), Image Out t6865 (w3040, 0 sinks), error out t6924
  (w653, 1 sink: LoopTunnel 649). Wire uids equal the c122 pool read on these nets.
- `#30117` Value t30145 (w30592, 1 sink); `#4580` Value t4728 (w4878, **0 sinks**); `#637` i = t644 (w3268, 7 sinks).
- P2b indicators (sim ids, real uids come from 123-1's file): Num t-3, TransPos t-7, RotPos t-11, FrameIdx t-15,
  Latest t-19, all ControlTerminal sinks on `#4866`.
- Pool images: IMAQ Create `#23099` in For `#23093` body `23169` (parent FS2 frame `13236`); New Image t23289 UNWIRED.
  For tunnels today: LoopTunnel `#26131` (names in, Control Names -> element) and a bare `Tunnel` `#23148` (both faces
  unwired). No output tunnel exists.
- Image Type: `#20436` <- RingConstant `#20327` (t20324, w20761, diagram 20261); `#23099` <- RingConstant `#26846`
  (t26843, w26084, body 23169); `#26846` is the pool stage's duplicate of `#13245` (value 0, read
  `stage_d1_qrt_pool.log:224`). **`#20327`'s value is in NO file** - card 123-1 reads it. Not the same object or wire.

## Steps (cap: P3 <= 2 broken intermediates; P2b = 1 of 6, P6 = the first run)
| step | rows (est.) | saved file | pass |
|---|---|---|---|
| **P3a** loop-1.1 control: `Wait (ms)`=1; prev-BufNum SR + compare + case on 639; new-frame counter SR (+1 only on a new frame) and `i = count mod 20` (Q&R, const 20) | ~24 (create 12, wire 12) | `claudeDev\D1_ring_p3a_<ts>.vi` | dry+prerun PASS; E1 every op == sim; cdiff == P2b bed's 16 rows; Error List == P2b + predicted; no existing net spliced (new sinks on w3747 only) |
| **P3b** slot writes in the new-frame case frame, PD238(c) order: `Num(i)=-1` -> `IMAQ Copy` (Src t6865, Dst `Index Array`(pool refnums, i)) -> TransPos/RotPos/FrameIdx at i -> `Num(i)=BufNum` -> `Latest=BufNum`; pool refnums out of For `#23093` by a NEW indexing output tunnel, route `nested` into 639 | ~50 | `claudeDev\D1_ring_p3b_<ts>.vi` | same gates + order structure read back + the For tunnel's indexing mode read back |

**The cap and the row rule cannot both hold:** ~74 rows in 2 steps = ~37 per step; the rule is <= 15 (<= 25 only on a
pattern X14 reports proven, and the case route and locals inside case frames have no clean stage). OPEN for judgement.

## ASSUMPTIONS (not decided here; the plan would proceed under the first option of each)
- ASSUMPTION A1 (order): a Flat Sequence inside the new-frame case frame, one frame per PD238(c) phase. Alternatives:
  (b) the writes as `Value` property nodes chained by error wire after `IMAQ Copy` (property nodes have error terminals,
  locals do not; PD238(d) names locals); (c) one new claudeDev subVI doing the slot write with error in/out, ordered by
  the error chain (collapses ~50 bed rows to ~10; a new VI, not an existing one).
- ASSUMPTION A2 (per-slot arrays): local READ -> `Replace Array Subset` -> local WRITE in the case frame, the indicator's
  own value as the master copy. Alternative: a shift-register master copy in 1.1 written out by local each new frame.
- ASSUMPTION A3 (registers): both new SRs on While `#637`; prev-BufNum initial -1, counter initial 0, written at loop
  start from constants on `686` (PD240(b) reasoning: an uninitialised SR keeps its value across runs). Alternatives:
  (b) uninitialised SRs (first BufNum 0 would be skipped as a duplicate, values carry across runs); (c) init by `i == 0`
  + Select (no Select donor exists).
- ASSUMPTION A4 (compare): `Equal?` (8 donors in the bed; no `Not Equal?` anywhere) with the case's True frame = duplicate
  (empty) and False = new frame. Alternative: a `Not Equal?` donor VI built in claudeDev.
- ASSUMPTION A5 (counter): increment inside the new-frame frame (output tunnel; the duplicate frame passes the old value)
  vs `count + (new ? 1 : 0)` on 639 (needs `Boolean To (0,1)` or Select: no donor in the bed).

## Routes P3a needs (`routes_c123_ring_p3.json`)
PRESENT: `gscript.add_shift_reg` (gscript.py:804) + opmodel; `gscript.wire_sr` (:854); `gscript.case_in` (:3508);
`create_primitive_nested` (:4603) with registered `Wait (ms)` donor (facts_c100_oplabels.json:266-273);
`stagekit.const_row` (stagekit.py:861) for sinks on 639.
**MISSING - SR initialisation from a constant (A3(a)):** `connect_route` refuses a constant source into a shift-register
face (stagexec.py:932-937) and `const_on_term` refuses a sink whose diagram is not a While body (stagexec.py:2219-2223);
the SR left OUTER face sits on FS frame 686.
**UNMEASURED (present in code, never run):** case_in into a loop body (scratch plan only, `scratch_plan_c120_routes.md:1`);
a NODE duplicated from the work VI as `$work` donor (only a RingConstant: plan_qrt_pool_in.json:25-26) - needed for
`Equal?`, `Increment`, `Quotient & Remainder`.
## Routes P3b needs
**MISSING:** a Flat Sequence creator (no verb in gscript/stagekit; A1(a)). PRESENT-by-precedent: `IMAQ Copy` llb member
(`docs/NAMES.md:967`; drop_subvi took an llb member for IMAQ Create, diag_c118_p1b_plan.json:8); locals
(gscript.py:4520/4528). UNMEASURED: the For `#23093` output tunnel (opmodels/tunnel.json measured While borders only;
connect_across_fs.json n=1 from FS2 frame, not from a For body); `Replace Array Subset` donor (1 bed candidate
`#29157`, GrowableFunction).

**Stop rule applied:** P3a needs a MISSING route (SR init under A3(a)), so STEP 4 (plan/recipe/dry/prerun) and STEP 5 are
not run.
