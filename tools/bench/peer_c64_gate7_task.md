# ATTACK this claim. Do not confirm it.

## The record

`tools/bench/c60c_astcheck.py` is a static, LabVIEW-free gate that a diagnostic script must pass before it is
launched. Run against a new diagnostic, `tools/bench/diag_c64_s3b_row1.py`, it wrote
`tools/bench/c64e_astcheck.log`: eleven of its twelve checks passed and check number 7 — whose whole text is
"move_in is neither imported nor called" — failed, reporting called=True imported=True.

`move_in` is a helper at `tools/recipes/build_d1_v0.py:318`. It relocates an existing block-diagram object
into a different diagram by uid.

Check 7 was written for an EARLIER cycle's task. `tools/bench/c60b_astcheck.py:14`, the predecessor gate,
states its reason in its own comment: "the brief forbids reproducing attempt 1's pointless relocation".
`c60c_astcheck.py:14` carries the same check with no reason attached.

The CURRENT task's written instructions require the relocation: its step 4 is "move_in the new Local onto
Diagram #639", because the object-creating operation places its product on the top-level diagram while the
object it must be wired to lives on a nested diagram, and a wire between two diagrams creates border objects
that the task's own acceptance criteria forbid.

The identical situation is already on record: `tools/bench/c62f_astcheck.log:11` shows the same check failing
the same way for `tools/bench/diag_c62_s3b_movein.py`, a script built for the same route.

## THE CLAIM YOU MUST TRY TO DESTROY

"Check 7 is STALE with respect to this task, not a finding about this script. The script is therefore safe to
run as written, and the right action is to report the failing check verbatim and proceed — editing the gate
file, renaming or aliasing the call, or abandoning the run would each be worse."

## Already ruled out (do not spend your answer on these)

- Editing `c60c_astcheck.py` to remove or re-aim check 7 — the standing rules forbid editing a gate file and
  forbid disabling gates; that option is closed regardless of whether it would "work".
- Hiding the call behind an alias or an indirect import so check 7 stops seeing it — that is evasion, and the
  standing rules name it as a countable violation.
- Writing a NEW gate file with check 7 removed — the task names this gate by filename; a fresh gate that
  differs only by dropping the failing check is the same evasion under another name.

## What I want back

1. The strongest reason the claim above is WRONG — in particular, any reading under which check 7 is a real
   finding about `diag_c64_s3b_row1.py` rather than a leftover from another task.
2. A DIFFERENT explanation for the failure that I have not considered.
3. What observation would falsify the claim.
4. The cheapest discriminating test between your explanation and mine — something runnable, not an argument.

Also answer, as a separate point: is there a hazard in `move_in` itself that would make the relocation the
wrong mechanism here — independent of the gate? It is known to leave a stray `Invoke` object behind on the
diagram it worked on, which this script now deletes by uid immediately afterwards.
