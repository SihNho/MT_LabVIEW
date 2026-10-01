# Brief 127-1 — measure the "2nd+ sink into an FS frame the source already entered" route (PD257(d)) + read the bed's Automatic Error Handling (PD256(f))

Plan: `docs/d1-loop12-17-split-plan.md` Pre-decided 254–257 (read 256 and 257). Measurement only; no stage recipe is launched,
no bed is saved over. Diagnostics ≤ 120 lines on stagekit (reuse `diag_c126_4_fs.py` / `diag_c126_6_cross.py` patterns).
Every op hygiene check, if any, goes through `gscript.hygiene_run`.

## STEP A — the route (on a P3a BYTE COPY, unique scratch name)
1. Build the same 3-frame Flat Sequence in case `#22694`'s False frame as 126-4/126-6 (`diag_c126_4_fs.py`).
2. Make the FIRST crossings exactly as P3b will (126-6's measured route, `connect_term_uid`, each followed by
   `wire_remove_loose_ends`): While `#637` `i` → a sink in FS frame 1; `#639` BufNum (t6897) → a sink in FS frame 2.
   Record the FS outer tunnel uid and its INNER-face terminal uid in each frame.
3. Make the SECOND sinks (the 4 P3b rows: `i` → f1 three sinks in total, BufNum → a second sink in f2 standing in for
   `Latest`) by a SAME-FRAME wire from the existing FS tunnel's INNER face in that frame (PD257(d)). Use the verb the
   graph allows (candidates: `connect_term_uid` inner-face uid → sink uid; `case_frame_wire` branch variant). Name the
   verb used and its arguments.
4. Per second-sink wire record: census delta (predicted {} or Wire +1 — LabVIEW branch, R4 analogue, PD250(a)), FS outer
   tunnel count (predicted UNCHANGED — no second tunnel), `Is Broken?`, free/loose ends before and after
   `wire_remove_loose_ends`, Error List count-only (`errorlist_check.py --count-only --role scratch`).
5. Record census samples (`census_samples.json`, variant name e.g. `fs_inner_branch`) and a `scratch_verify/` record.
   Delete the scratch.

## STEP B — Automatic Error Handling (read-only, on the bed or a byte copy of it)
Read the VI property Automatic Error Handling (and, if exposed, the execution-option error-handling flags) of
`claudeDev\D1_ring_p3a_20261001_180540.vi`. Also read the same property on the ORIGINAL only via a BYTE COPY in
claudeDev (rule 1: never open the original itself for this; never save anything). Report the values as facts.

## Return
`result/1` with facts (verb, census per wire, tunnel counts, Is Broken?, loose ends, Error List counts, AEH values for
bed and original copy). Bed md5 unchanged (`4dfa44aac8fb32f706b3eb792ee7d3cc`); LabVIEW closed and verified gone.
At the first result that differs from a prediction above: finish the step, close LabVIEW, record, RETURN — no retry
inside the card.
