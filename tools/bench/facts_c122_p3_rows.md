# Ring P3 (camera loop 1.1) - draft row LIST, facts only (card 122-2, PD240(f))

No plan file. Every uid below is from `tools/bench/facts_c122_p3.json` (built by `tools/bench/diag_c122_p3.py` from
`tools/bench/graph_qrt_pool_20260928.json`, pool bed md5 `93539368...`). Run: `tools/bench/diag_c122_p3.log`,
**4 PASS / 2 FAIL** (N2, X1 - see "Prediction misses"). Route names are `tools/stagexec.py:198-218` CREATE_ROUTES.
P2a-removed uids `#23105 #23118 #23136 #26017 #25898` are EXCLUDED (absent from `sim/ring_p2a/step_08_delete_object.json`).

## Bound facts
- Loop 1.1 = WhileLoop `#637` on `686` (FS1 frame 9); body diagram `639`; `i` = t644 (w3268).
- `#6810` (`get buff image-lost frames.vi`) on 639: BufNum = `current image number` t6897 (w3747, NAMES.md:86); Image In t6857
  (w1651); Image Out t6865 (w3040, 0 sinks); error in t6901 (w1961); error out t6924 (w653); Buffer to extract t6876 (w5416).
- BufNum w3747 sinks: `#5119` x (639); `#2347` x via SelectorTunnel 3078 (case diag 3292); `#1978` x via SelectorTunnels
  2179/1034; `#194` x on 686 via LoopTunnel 1605; indicator `current image number` t34217 (639).
- Image In route (back): LoopTunnel 1666 (inner t1669, 639) <- FSIT 1690 (686) <- FSIT 24936 (4866) <- FSIT 24990 (1817) <-
  **Property `#35869` `Value` t35894 on FS1 frame 3121, its `reference` input UNWIRED** (implicitly linked node).
- Error chain in 1.1: error in <- LoopTunnel 924 (t879) <- Property `#250` on 686; error out w653 -> LoopTunnel 649 (only
  sink) -> FSIT 1828 -> SubVI `#1839` error in on 759 (FS1 frame 10). No other node of 1.1 is on w653.
- Buffer to extract <- LeftShiftRegister `#5351` (t5364, 639): loop 1.1 HAS a shift register.
- Field sources on 639: TransPos `#30117` Value t30145 (w30592; sinks: case `#20530` via SelectorTunnel 20497);
  RotPos `#4580` Value t4728 (w4878; **0 sink rows on w4878 in the graph file**); frame i t644 (w3268; sinks #29240,
  #10068, #1114 `index i`, #2136, #3162 via case 3045, #1628 on 686 via LoopTunnel 2213, #12045 via FS outer tunnel 12195).
- Pool images: IMAQ Create `#23099` in For body `23169` (ForLoop `#23093` on FS2 frame `13236`); `New Image` t23289 fed only
  w26155, deleted by P2a (`plan_ring_p2a.json:33-35`) => **unwired in the P2a bed; no route out of the For loop exists**.
- Measured FS crossing (route `nested`, `opmodels/connect_across_fs.json`, n=1): 13236 -> 639 makes FS outer tunnel on FS
  12938 + FS outer tunnel on FS 681 + LoopTunnel on While 637 + 1 stray Invoke on 639 (PD237(m): census == plan, remove).

## Draft rows, PD238(c) order (+ 238(i) loop-rate row)
| # | row | binds to | route (exists?) |
|---|---|---|---|
| 0 | `Wait (ms)` = 1 in 1.1, no data dependency | diagram 639 | primitive + const_on_term (yes) |
| 1 | duplicate-BufNum skip: prev BufNum (new SR on 637) `Not Equal?` t6897 -> Case on 639 | t6897 w3747 (new sink) | add SR (opmodels/add_shift_reg.json), primitive, case (stagexec.py:215) |
| 2 | slot i = count of NEW frames mod 20 (new counter SR, +1 in True frame, Quotient&Remainder, const 20) | not t644 (counts duplicates too) | primitive/const (yes) |
| 3 | `Num(i) = -1` (Replace Array Subset on local `Num`) | P2b object `Num` | local_read/local_write (yes); object = 122-1 OPEN |
| 4 | `IMAQ Copy` 'Cam' -> `Img(i)` (Index Array on the 20 refnums) | Src: t1669 (w1651) or t6865 (w3040); Dst: pool refnums | subvi (yes); **refnums into 1.1: no route (OPEN)** |
| 5 | per-slot `TransPos(i)`, `RotPos(i)`, `FrameIdx(i)` | t30145 w30592; t4728 w4878; t644 w3268 | local r/w (yes); objects = 122-1 |
| 6 | `Num(i) = BufNum` | t6897 | local r/w; object = 122-1 |
| 7 | `Latest = BufNum` | t6897 | local_write; object = 122-1 |

## Prediction misses (run FAIL 4/2) - recorded, not diagnosed
- N2: predicted Image In <- IMAQ Create `#13938` ('Cam'); measured tip = Property `#35869` Value (reference unwired), and
  `#13938` New Image reaches `#15403` Image In on 15266 instead.
- X1: the 5 P2a uids are absent from step_08 (as predicted), but the bound-fact check hit `#23105/#23118` as sinks of w14741
  in the PRE-P2a forward trace of `#13938` (gate premise used the pool graph).
- The For-loop tunnel and loop-1.1 shift-register searches returned [] though `#5351` and LoopTunnel `#26131`
  (facts_c120_qrtw.json:101-108) exist: the owners map does not carry tunnels (script limitation, not a graph fact).

## OPEN (graph files cannot answer / judgement)
- Which control `#35869` (implicit Property, ref unwired) belongs to, i.e. whether its Value is the 'Cam' buffer.
- IMAQ Copy source: t1669 (before `#6810` by dataflow) vs `#6810` Image Out t6865 (after it); PD237(c) vs 238(b) wording.
- Route of the 20 refnums out of For `#23093` (indexing output tunnel) then `nested` into 639 - the For exit is unmeasured.
- Ordering by error chain needs a new sink on w653 or splicing it (an existing net); w4878 sink rows missing; P2b objects
  and their local-variable uids come from 122-1's saved file.
