---
card: 161-b1-1
status: current
date: 2026-10-10
---
# Brief 161-b1-1 (assignment 161-1) - OFFLINE: re-make the p5s02b checkpoint-set files on stagexec a4df7e15, then dry / prerun / check-launch / scratch-required / VI hashes; NOT launched

`labview: none` (no LabVIEW process), no `--launch`, no `tools/hooks` edit, no `tools/*.py` edit. Read `tools/bench/diag_c161_a1_1_facts.md`, `tools/bench/diag_c160_c3_3_facts.md` (the previous pass of exactly this card, ended at a dry stop that 161-a1-1 fixed) and `docs/d1/ring-p5b.md` PD392(b), PD393 (lines 192-245).
Use the same command forms as card 160-c3-3 (`tools/bench/cards/brief_160-c3-3.md`; logs `prep_c160_c3_3_*.log`).

## Decisions already taken (PD392(b), PD393) - apply, do not ask
- The only change allowed is the **checkpoint set**: stagexec is now a4df7e15, and for p5s02b `checkpoint_ops` returns **(0,1,2,3,4,5,7,8,9,10)** (stored (0,2,3,5,7,9,10) plus delete_wire ops **1, 4, 8**: three extra reads, not the two PD393 names;
  the literal rule "every delete_wire op" was accepted by the assignment session, 161-a1-2 brief). Plan f4520b10 (20 actions, end graph) and the predicted Error List items are NOT changed.
- X10 is a READ-ONLY check: prerun reports the planned MAIN against 675 MB (now with the 3 extra reads); the limit value stays as it is in the tool. **If the planned MAIN exceeds 675, quote the line and stop (hand-back); no cut, no limit change.**
- The dry may end `PASS-UNVERIFIED` when the ONLY unverified gate is CEN2 with the census UNPREDICTED (no census sample exists yet; the step-2 scratch measures it, PD261(c) / PD292(c)). Any other unverified gate, a dry FAIL, or a refusal by prerun / `--check-launch` is quoted verbatim and handed back; no gate loosened, no census sample added.

## Do
1. Re-pin the c3 makers' stagexec pin to a4df7e15 (`prep_c160_c3_1_md5.py:17`, `prep_c160_c3_1_pred.py:39`, `prep_c160_b3_1_mk.py:46`; measure the line first, change only the stagexec md5). Re-run, in the c3-1 order, `prep_c160_c3_1_md5.py` (all other pins must hold), `_pred.py`, `_licence.py`, `_el.py`.
2. Name every file whose md5 changed and its cause: pred (48b50b29 -> ?), licence (f61a2514 -> ?), Error List `errorlist_predicted_D1_ring_p5s02b_end.json` (79ec3207 -> ?), recipe pair (083fda6d / 3f6fb898 -> ?), plan f4520b10 (must be unchanged). The cause for each must be "checkpoint set only" - show it by a diff of the changed lines (e.g. the checkpoint list, `E1` rows for ops 1/4/8, the recipe docstring line 15). Any other changed content = stop and report.
   The recipes are pinned by the prior-art review `archive/peer/2026-10-10-priorart-priorart-c160-d4-1-p5s02b.md`: if the recipe text must change, change ONLY the stated checkpoint set (its docstring / literal), quote the diff, and say whether the set is read from `RingSession.CHECKPOINTS` (`tools/stagekit.py:2376`) so the recipe needs no edit at all.
3. Dry of both recipes (`stage_d1_ring_p5s02b.py`, then `_scratch.py`), same forms as `prep_c160_c3_3_dry.log`. Quote word-for-word: PASS / PASS-UNVERIFIED, unverified count and each label, **and that the dry runs past ops 5 and 9** (the c160 stop was UNROUTABLE at them).
4. Prerun (X10 read-only incl. the 3 extra reads, MAIN <= 675; X14, X17, X8) and `--check-launch` (no `--launch`), on the final tool md5s; then `py tools/stage_prerun.py --scratch-required tools/recipes/stage_d1_ring_p5s02b.py`: quote every rc and reason line (expected exit 3, PD391(e)).
5. Re-run `tools/bench/prep_c160_c3_3_hash.py` (hashlib, bytes only): s09 eb1d0f31, P5-1a 2482fe7b, P5-1 7f2582ae, p5s02a 94ffff94 - quote equal/unequal.
6. Hook false positive on your own command text: `py tools/gate_fp.py log ...`, report, no env bypass. Background anything slow under `py tools/bgrun.py --material --max-min N --log ... -- ...`.

## Report `tools/bench/diag_c161_b1_1_facts.md` (<= 40 lines, facts only)
md5 of every re-made file and of every file whose md5 changed, each with its cause (diff quoted); dry (both recipes) / prerun / check-launch / scratch-required lines with rc, unverified count + labels, MAIN number vs 675; hashes of the four VIs;
md5 UNCHANGED: stagesim 95a162ba, stagexec a4df7e15, stagekit 0b5bb678, stage_prerun 7605116f, plan f4520b10; `OPEN:` lines.
