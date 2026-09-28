# brief 120-1 — read-only facts for QRT-W on the pool bed (PD237)

Detail for the card's pass items G1–G8. Measure only; PD237 in `docs/d1-loop12-17-split-plan.md` is decided and the
row plan is card 120-2's job.

- **G1** Graph dump of a BYTE COPY of `claudeDev\D1_qrt_pool_20260928_141055.vi` → `tools/bench/graph_qrt_pool_20260928.json`,
  same dump format as `tools/bench/graph_l2r2_saved_20260928.json`. The bed's md5 `9353936895141d3ec2f890649c5cf22f` is
  unchanged afterwards.
- **G2** The pool's location: the uids and owning diagram of its 2 Obtain Queue, the For loop, IMAQ Create, Enqueue(Q_free)
  and the queue-out terminals; the structure path (frames/tunnels) between that diagram and the loop bodies 639 (1.1)
  and 23166 (1.2): which sequence/frame borders a wire from the pool diagram must cross to reach each body, and whether
  an existing route in stagexec/stagekit wires across them (file:line).
- **G3** `#6810`: class/callee, every terminal name+uid, every existing sink of its Image Out net. `#5058`: every output
  terminal name+uid (is there an Image Out pass-through? an error out?).
- **G4** Data type of each field source terminal: `#30117` Value, `#4580` Value, `#637` i (term 644), `#5119` x-y,
  `#11608` output cluster, `#2626` appended array, by whatever read route exists. A field whose type no route reads is
  reported as such, with the missing reader named, not guessed.
- **G5** M1–M4 of card 113-3 / PD227(d) on `#11261` and `#2626` (Concatenate Inputs, per-input names, index/type): each
  read value, or "no reader" with the reader's name.
- **G6** Route inventory (offline code greps, file:line): creating IMAQ Copy; Dequeue Element; a Case structure inside
  a loop body; a typed constant on the Obtains' diagram (const-on-term + set type, or copy_in of an existing typed
  constant). Each EXISTS (file:line) or MISSING.
- **G7** Every uid named in `tools/bench/qrtw_rows_draft.json` re-checked on the new graph: present with the same owner,
  or changed (list).
- **G8** LabVIEW closed and verified gone at the end; handle count read before/after.

Full tables go to `tools/bench/facts_c120_qrtw.json`; the result card carries ≤ 10 facts with file:line.
