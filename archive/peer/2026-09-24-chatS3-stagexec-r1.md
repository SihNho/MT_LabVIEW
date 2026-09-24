# chatS3-stagexec-r1

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.3367  in 34 / out 12851 / cache-create 89971 / cache-read 1571469  (162s, 20 turn(s))
- **date:** 2026-09-24 23:38:09
- **outcome:** ANSWERED (166s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

FAILED PREDICTION (card chat-S3, tools/stagexec.py bench, log tools/bench/stagexec_l7_bench.log run 1).
Predicted: every real op's graph equals its simulated step file. Observed: ops 1-7 diff 0; op 8 (plan action err_init:
wire ClusterConstant #4910 'error out' -> the NEW left shift register SR1L's OUTER face on WhileLoop #23041) produced edge
4965 -> 24291 where the simulation has 4965 -> 24205 (24205 = bound SR1L outer face; 24291 = the other new register's
left outer face). The executor stopped there (as designed) and discarded the scratch.
Our diagnosis: the loop Terminals[] index of a register's outer face was TRACKED by difflib alignment on (name, direction)
across ops; wire_sr on the inner faces RENAMES outer faces ('' -> 'error out' ...), so ops 4-7 misaligned the tracked
indexes (report: lost_register_faces [24280, 24291] from op 4 on) and op 8 used index 4 (SR2L) for SR1L.
Fix applied before run 2: identity mapping when the loop's Terminals[] length is unchanged; (direction, wire) alignment
when it changes; and the face is addressed FIRST by a unique live (name, direction, wire) match (the stage_d1_l7_1b route),
the tracked index only when that is ambiguous. Self-test T15 in tools/stagexec.py covers the rename case.
Already ruled out: a wrong binding (SR uids 24083/24133, 24150/24187 bound by terminal-table diff, identical to the
original L7-1a run); a model error (ops 1-7 diff 0).
Files: tools/stagexec.py (Addr.snap_loop / track_new / retrack / _triple), tools/bench/stagexec_l7_split.json (report),
tools/bench/stagexec_l7_bench.log.
Question: what is the strongest reason this diagnosis or fix is wrong - e.g. does LabVIEW reorder a loop's Terminals[]
when a register is typed or renamed, so identity mapping is unsafe; and what cheapest test separates that?


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict:** the diagnosis holds. The fix is the weaker part, and a pass in run 2 won't show that it works.

## Why the diagnosis holds
Run 1's report is gone: run 2 overwrote `tools/bench/stagexec_l7_split.json`, which now has 308 lines and none of run 1's per-op fields. I checked the diagnosis by hand instead.

- difflib's `SequenceMatcher` breaks ties by taking the earliest match in the old list.
- After op 3, the loop's Terminals[] reads `[t0, ('',src), ('',snk), ('',src), ('',snk)]`.
- Op 4 renames SR1's faces to `'error out'`. The longest shared run is then the unchanged `('',src),('',snk)` pair. difflib matches the OLD SR1 entries (index 1,2) to the NEW positions 3,4 and treats SR2's entries (3,4) as deleted.
- That gives SR1L → 4 and lost `[24280, 24291]`, which are exactly the numbers the log records (`stagexec_l7_bench.log:91-92`).
- The layout is independently confirmed. The successful earlier route read the loop as SR1 at 1,2 and SR2 at 3,4 after all the wire_sr ops (`stage_d1_l7_1b.log:271-279`).

## 1. Strongest reason the fix is wrong
The fix assumes two things about LabVIEW that nobody has measured op by op:
- that the Terminals[] order stays the same whenever the list length stays the same;
- that `add_shift_reg` puts the new faces at the end.

The second one isn't measured by `track_new` either. When the new faces look the same as SR1's unwired faces, the same tie-break always reports "inserted at the end", wherever LabVIEW actually put them (`tools/stagexec.py:290`). Self-test T15 (`tools/stagexec.py:1038-1064`) builds both assumptions into its fake terminal list, so it tests the code against the hypothesis, not against LabVIEW.

The only real-LabVIEW evidence for a stable order is one final snapshot (`stage_d1_l7_1b.log:271-279`). It is consistent with a stable order, but it doesn't prove the order was stable after each op.

## 2. Alternative explanations
- **(a) Same bug, later op.** When the list length changes (a tunnel is added), the fix aligns on (direction, wire). Unwired faces with the same direction, such as SR1R and SR2R outer (both source, wire 0), are still identical keys. If LabVIEW inserts the tunnel between them rather than at the end, the same tie-break maps one onto the other. That is the run-1 failure in a later op. L7-1b shows sink tunnels appended at the end (t5–t7); that is not shown for source tunnels.
- **(b) Names are recomputed across the loop.** In `opmodels/raw/wire_sr_1.json:72-118`, wiring register 23789 renamed faces of a different register (24150/24187: `'' → 'total data array out'`). L7-1b shows the same SR2 faces as `''`. So names are recomputed for more than the register being wired. If order is also rebuilt then (for example, re-sorted by position or type), identity mapping fails without any error.

## 3. What would falsify the fix
A run in which the tracked index for a register face points at a different face than the unique live match, with the list length unchanged.

## 4. Cheapest test (no extra LabVIEW run)
Run 2 is in progress. Its log so far holds only the restart, at `stagexec_l7_bench_r2.log:18`. When it finishes:

1. **Read the `how` field for op 8 and every later register-face address.**
   - `unique live name … (tracked index N)` with no `DISAGREES`: identity mapping agrees with LabVIEW in this case.
   - `DISAGREES`: identity mapping is wrong.
2. **Don't read a clean diff 0 as proof.** SR1L (`'error out'`) and SR2L (`''` or `'total data array out'`) probably have different names, so the name-first route addresses op 8 correctly on its own. A pass would hide a broken identity mapping. Only the `DISAGREES` tag separates the two.
3. **Make the check rigorous next time.** Have `Addr` log the loop's full Terminals[] after every op, as `stage_d1_l7_1b` does at `:271-279`, together with the uid of each register face. Stop on any `DISAGREES` rather than just reporting it (`tools/stagexec.py:367-368`). That measures directly whether LabVIEW ever reorders the list.

A possibly more stable key is Data Type (the NI forum thread below mentions it for telling terminals apart). Once the register faces are wired, type separates the error cluster from the array faces, and type doesn't get recomputed the way names do. It doesn't help for unwired, untyped faces.

**What would change my mind:** a per-op Terminals[] log from run 2 showing no reorder at any op, including a source-side tunnel insertion.

The web searches found nothing from NI about whether a loop's Terminals[] order is guaranteed. That gap is why the question has to be answered from the machine's own logs.

Sources:
- [NI forum: Scripting – Terminal Information](https://forums.ni.com/t5/LabVIEW/Scripting-Terminal-Information/td-p/4303374)
- [LabVIEW Wiki: VI Scripting](https://labviewwiki.org/wiki/VI_Scripting)
- [NI forum: tunnel vs. shift register](https://forums.ni.com/t5/LabVIEW/tunnel-vs-shift-register/td-p/3213328)

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
