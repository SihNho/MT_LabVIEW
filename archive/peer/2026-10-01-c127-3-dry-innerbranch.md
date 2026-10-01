# c127-3-dry-innerbranch

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.2402  in 26 / out 9918 / cache-create 98121 / cache-read 1283730  (114s, 20 turn(s))
- **date:** 2026-10-01 23:22:04
- **outcome:** ANSWERED (117s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** card 127-3: failed prediction (dry PASS predicted) in tools/bench/diag_c127_3_checks.log; JEV-LADDER new-problem p=0.644, hypothesis review owed
- **verdict:** unverified

## Question

ATTACK this claim about a failed offline dry run (no LabVIEW involved). Read-only; cite file:line.

FAILURE: tools/bench/diag_c127_3_checks.log (script tools/bench/diag_c127_3_checks.py). Step C1, `stagesim.simulate(plan_ring_p3b_in.json, graph_ring_p3a_20261001_190155.json)`, PASSED end to end (63 steps, final). Step C2, `stagexec.main(["stagexec.py","dry","tools/bench/plan_ring_p3b.json"])` (DryPlanBE, COM stubbed) then crashed with an UNCAUGHT stagesim.SimError, not an ExecStop:
  stagexec.py:1929 run -> :2082 execute -> :3299 connect_term_uid -> :2961 _apply -> stagesim.py:1119 op_wire -> stagesim.py:1511 _fs_border_wire
  SimError: wire {'uid': 27373, 'term': 'x-y*floor(x/y)'} -> new:RAT1.index: the entry face #-91 of the earlier crossing is gone or unwired
That row (p3b_x_i_rat1) is the first "fs_border_inner_branch" crossing (a 2nd sink of the same source into an FS frame the source already entered, PD257(d)/PD258(a)); earlier crossings p3b_x_i_f1/p3b_x_i_f3/p3b_x_i_ia1 are fs_border.
Context: before this card the dry failed earlier, at the IMAQ Copy create (BINDING on 3 unnamed sink terminals, diag_c127_2_checks.log:5-8). Card 127-3 changed stagexec.bind_new (tools/stagexec.py, the `unnamed_ok` block near line 897) to pair repeated unnamed, unwired terminal keys in read order; stagexec selftest 124/0 after that edit. So this crash is the first time the dry reached the crossings.

CLAIM (ours): the dry backend re-applies each op to a state whose earlier-created objects were re-bound from negative sim uids to positive "real" uids (stagexec bind_new / bind_fs_tunnel), but stagesim._fs_border_wire's inner-branch path (stagesim.py ~1496-1530) looks the earlier crossing's entry face up by the NEGATIVE sim uid (#-91) remembered in sim state; in the dry state that uid no longer exists, so it raises. I.e. a defect in how the dry backend binds/rewrites the FS OUTER/INNER tunnel faces that an fs_border connect_term_uid creates (there is bind_fs_tunnel for FlatSequenceInnerTunnel but apparently nothing for the FS outer tunnel faces made by a border crossing), NOT a plan defect and NOT caused by the 127-3 binder edit.

Questions: (1) strongest reason this claim is wrong; (2) an alternative explanation (e.g. the 127-3 unnamed-terminal pairing mis-binds something; the plan row order; the record of the entry face is keyed per source net that the B12 re-creation changes); (3) what would falsify it; (4) the cheapest offline discriminating test (no LabVIEW). Also say whether the SimError escaping as a non-ExecStop is itself a defect of stagexec's dry path.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict:** your conclusion holds: this is a fault in the dry backend, not in the plan and not in the 127-3 binder edit. But the mechanism you name is wrong, and the fix it points to (a binder for the Flat Sequence outer-tunnel faces) would not remove this error.

## 1. Strongest reason the claim is wrong
The error is raised by `stagesim` working on the dry backend's own copy of the state. That code never looks at `bind_new` or `bind_fs_tunnel`.
- `SimBackend._apply` runs `SS.OPS[a["op"]](self.st, a, P, self.S1, {})` (`tools/stagexec.py:2961`) on `self.st`. The `bind["term"]` / `bind["obj"]` maps that `bind_new` and `bind_fs_tunnel` fill (`tools/stagexec.py:845-949`) are used only for the executor's addressing and comparison. `_fs_border_wire` never reads them.
- After each operation, `_apply` renumbers every newly created negative uid to a fresh positive one (`tools/stagexec.py:2964-2989`). The renumbering covers:
  - `terminals`, `objs`, `loops`, `diagrams`, `owners`, `sym`
  - `case_tunnel_frame`, `case_frames`
  - through `_fs_remap` (`tools/stagexec.py:1632-1645`): `fs_frames`, `fs_alias`, `fs_tunnels`, `fs_pairs`
- It does **not** cover:
  - `st["fs_border_entries"]`. `_fs_border_wire` writes it at `tools/stagesim.py:1573` with `face = faces[-1][1]`, which is a negative uid.
  - `st["act_wires"]` (`tools/stagesim.py:1574`, `:1514`).
  - `st["fs_frame_inferred"]`.

  A grep for these three keys in `stagexec.py` finds nothing.
- So after the `p3b_x_i_ia1` operation, the entry face's terminal row was renumbered to a positive uid, but the entry record still says `#-91`. At `p3b_x_i_rat1`, the lookup at `tools/stagesim.py:1509` finds no terminal with that uid, and line 1511 raises.
- This also explains why C1 passed while C2 failed on the same rows. `stagesim.simulate` never renumbers, so `-91` stays valid there.
- The fault is a missing entry in the dry backend's renumbering table. It is not a missing sim-to-real binder.
- Whether the **real** LabVIEW backend binds Flat Sequence outer-tunnel faces correctly is a separate question. This crash says nothing about it either way.

## 2. Alternative explanations (I checked each)
- **127-3's pairing of unnamed terminals mis-binds something.** Ruled out as the cause of this error. The pairing writes only into `bind` (`tools/stagexec.py:903-914`), which the failing code never reads. It could still mis-pair on a real run, but it cannot produce `#-91 gone`.
- **Plan row order.** Ruled out. `ia1` (the first entry into frame f1) comes before `rat1` (`tools/bench/plan_ring_p3b_in.json:759-781`), and C1 accepted that order.
- **The source net is re-created by a later crossing.** That would change the face's `wire_uid`, not its `term_uid`. Also, no crossing sits between `ia1` and `rat1`; only `p3b_rle_i_ia1`, which changes no state.

## 3. What would falsify the corrected claim
After the `ia1` operation in the dry run, look at `be.st["fs_border_entries"]["27373|<f1 uid>"]["face"]`. If it is positive and matches an existing terminal row, the claim is false and the stale record is not the cause.

## 4. Cheapest offline test (no LabVIEW)
In a scratch script, monkeypatch `SimBackend._apply` so that its `rn` pass also remaps:
- `st["fs_border_entries"][k]["face"]`
- `st["act_wires"][k][*]`

Then rerun `stagexec.main(["stagexec.py","dry","tools/bench/plan_ring_p3b.json"])`.
- If `p3b_x_i_rat1` passes, the cause is confirmed.
- If it still raises, my diagnosis is wrong.

An even cheaper version: catch the `SimError` and print `fs_border_entries` next to the set of terminal uids. If the face is negative and every terminal uid is positive, that settles it.

## Problems you didn't raise
- **The cleanup rows silently do nothing in the dry run.** Because `act_wires` is not renumbered, each `wire_remove_loose_ends of=` row looks up wires by their stale negative uids. `tools/stagesim.py:1599` filters the missing ones out instead of failing. So the cleanup rows `p3b_rle_i_f1`, `p3b_rle_i_f3` and `p3b_rle_i_ia1` already passed the dry run with an empty wire list. Their dry PASS proves nothing. Fix this in the same change.
- **Is the uncaught `SimError` itself a defect? Yes, but it should not become an `ExecStop`.**
  - `dry_run` catches only `ExecStop` (`tools/stagexec.py:3560-3570`), and `prerun_plan`'s X4 gate calls `dry_run` without a guard (`:3596`). The launch gate therefore crashes instead of failing X4, and the bench log ends with `NO RESULT LINE` (`tools/bench/diag_c127_3_checks.log:26`).
  - Converting it to `ExecStop` would also be wrong. In collect mode, `_unroutable` would re-apply the same action (`:3173`) and either raise again or file a fault in the harness as an "unroutable row".
  - The right handling: `dry_run` returns `FAIL` with a distinct prefix such as `SIM-INTERNAL:` and a stack summary, so X4 fails cleanly and the log still gets its RESULT line.

## How sure I am
- **High:** the missing renumbering of `fs_border_entries` and `act_wires`. It is read directly from code: the writes at `stagesim.py:1573`, the rn pass at `stagexec.py:2964-2989`, and the empty grep.
- **Not settled:** whether the real backend binds the Flat Sequence outer-tunnel faces and the unnamed IMAQ Copy terminals correctly. This crash cannot tell us, and only a real run or a recorded real graph can.

No external search was needed: every claim above is about this project's own Python code, and each one cites a file and line. Nothing was built, edited or run. The plan file could not be written because the Write tool is disabled in this session, and ExitPlanMode is not available either.

## Sources

(extract from answer)

## What was done with it

ACCEPTED as the working diagnosis, NOT acted on inside card 127-3 (material protocol: return at the first unexpected result; the
judgement session decides the retry). Our claimed mechanism (missing sim->real binder for FS outer faces) is REPLACED by the reviewer's:
SimBackend._apply's renumbering pass (tools/stagexec.py:2964-2989, _fs_remap :1632-1645) does not remap st["fs_border_entries"]
(written stagesim.py:1573), st["act_wires"] (:1514,:1574) or st["fs_frame_inferred"]. Fix candidate for a follow-up offline card: add
those keys to the rn pass (also makes the RLE `of` rows non-vacuous in the dry, review :79), and have dry_run return FAIL
`SIM-INTERNAL:` on a SimError so X4 fails with a RESULT line (review :80-83). Discriminating test: review section 4 (monkeypatch the rn
pass, rerun dry on plan_ring_p3b.json). Recorded in tools/bench/cards/result_127-3.json.
