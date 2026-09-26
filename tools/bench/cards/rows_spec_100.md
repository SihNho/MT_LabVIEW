# Display-loop stage — row specification (cycle 100 judgement, PD212(c)/(h)/(i)3 applied)

Base `claudeDev\D1_s1_copy.vi` (md5 `3e3d23ce…`), output `claudeDev\D1_s1_disp_<ts>.vi`. Apply as written; a row
that cannot be written as specified is reported as a FACT/OPEN, not redesigned.

- **R1** New While loop (the display loop) on the owner diagram of loop #25380 (sequenced after Property #8603).
- **R2** A For loop inside R1's body.
- **R3** MOVE into R2's body the PD206(b) 11363-only set: #8741 IndexArray, #8764 Subtract, constants
  #8775 / #8795 / #27716 / #28180, FIR #28233, Median #29009, Bundler #11310. Tunnels 31051 / 31137 are not moved;
  their role is taken by new tunnels on R2 fed from R6's local reads.
- **R4** MOVE BuildArray #11261 into R1's body (outside R2), fed by R2's output and by R6's L2 read.
- **R5 frame side (crossings).** Create two NEW hidden (`Visible = False`) indicators on existing wires — never an
  existing terminal moved: `plot ring (display)` on the w9215 source inside 639 (L1, 3-D DBL [beads][2][#FD points]),
  and `plot WLC (display)` on #11608's output (L2). The frame loop writes both every frame.
- **R6 display side.** Local READ of L1 (auto-indexed into R2, one page per bead), local READ of L2 into #11261,
  local READs of `Exp Baseline` and of BOTH half-width controls (w31059's and w31166's). **No control terminal moves**
  (PD212(i)3). `Force (pN) vs Extension (nm)` #8323 is written by a **local WRITE** in R1's body from #11261's
  output; #8323's terminal stays where it is (decided by the judgement from the same (i)3 fact).
- **R7** New I32 control `Display period (ms)`, default 100, clamped ≥ 1 by a Max node, into `Wait (ms)` in R1's body.
- **R8** R1 stops on a local READ of `TurnOff` #24444. A `Value` Property READ in the style of #25116 is an equally
  accepted form (both are latest-value reads, CLAUDE.md 1c'').
- **Every row** names its op VI or gscript/stagekit function and every uid/terminal it binds, taken from the S1 graph
  file (name the file) — never re-typed from memory. Rows with no existing op/verb are listed as MISSING with the
  smallest verb that would do it. Expected MISSING: `Wait (ms)` creator, `Visible = False`, local WRITE. Anything else
  MISSING is reported, not built, in this card.
