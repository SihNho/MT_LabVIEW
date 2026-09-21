# THE PLAN UNDER REVIEW — stage M3a-2, `tools/recipes/build_d1_m3a2.py` (WRITTEN, NOT YET RUN)

The recipe is on disk at `tools/recipes/build_d1_m3a2.py` and has passed the pinned static gate
(`py tools/bench/c60c_astcheck.py <file> --route owner`, 11 pass / 0 fail,
`tools/bench/c74_astcheck_m3a2.log`). It has NOT been launched: this review decides whether it should be.
Read the file itself — its header docstring states the whole contract.

## What the stage does

Loop `#23032` (the NEW While loop, created in stage S2 and given two shift registers by stage M3a-1) has two
registers whose LEFT OUTER terminals are BARE, i.e. the registers are uninitialised. M3a-2 wires each LEFT
OUTER to the SAME source that initialises the ORIGINAL loop's corresponding register, so both loops are fed
identically. TWO rows, not four (`docs/cycle27-plan.md` Pre-decided 91).

| row | source | sink | the original sink on the same net |
|---|---|---|---|
| A VISA | the ONE source terminal of wire **4185** = `FlatSequenceInnerTunnel` **#4194** | LEFT register **#23880** OUTER, named `'VISA out'` | **#4344** OUTER |
| B POS | the ONE source terminal of wire **3968** = `FlatSequenceInnerTunnel` **#3974** | LEFT register **#23909** OUTER, named `'position [internal units]'` | **#4274** OUTER |

Both are SAME-DIAGRAM rows on `Diagram #686` (both loop borders — `#637` at Nodes[4], `#23032` at Nodes[21] —
and all four wires are owned by `#686` under strict uid echo).

## Where every number comes from

`tools/bench/diag_c73_m3a2_rows.{py,log,json}` — a measurement-only diagnostic, `BGRUN END rc=0 after 144s`,
5 hygiene gates pass / 0 fail, nothing mutated, the input artefact re-read byte-unchanged, every uid uid-echoed
and every `OpWireSource_v5` walk clean of Pre-decided 85 violations. The recipe RE-MEASURES every one of them on
the live target before use.

## The mechanism, and why no new tool is built

- Writer: `connect_from_wire` = `OpConnectFromWire_v0.vi` (BUILT + SAVED 2026-09-17,
  `docs/toolkit-capabilities.md:70`), which takes its SOURCE as (WIRE uid, terminal index on that wire) and its
  SINK as `Diagram[d].Nodes[n].Terminals[t]`. It wrote M3a-1's t1 row and its sixth row.
- `wire_sr('LeftOutNode'/'LeftOutCtl')` is deliberately NOT used: both sources are `FlatSequenceInnerTunnel`s
  owned by `FlatSequence #681` and a tunnel is not a `Nodes[]` member, so neither variant can address them
  (Pre-decided 93).
- Reader: `wire_source_owner` = `OpWireSource_v5`, repaired 2026-09-22 (indicators scrubbed per call, all 8 op
  error outs read, the op's uid echo required; acceptance `tools/bench/diag_c68_echo_accept.log` 8/0).
- Helpers `find_node` / `terms_at` / `term_state` / `node_view` / `node_census` / `new_nodes` / `delete_by_uid`
  are IMPORTED from `tools/recipes/build_d1_m3a1.py`, not rewritten. `census_and_purge` is deliberately not
  imported (it writes M3a-1's own JSON); its logic is re-stated as `purge_junk`.
- NOTHING NEW IS BUILT — no op VI, no gscript verb, no checker, no process device (user, 2026-09-18 08:53).

## The acceptance test, per row (Pre-decided 92 + 77), run TWICE — after the write and after the junk purge

1. the wire carried by the NEW SINK terminal has **exactly ONE** source terminal **of any owner class** —
   every class counted BEFORE any filter;
2. that one terminal's owner is the predicted source (#4194 / #3974);
3. the ORIGINAL sink (#4344 / #4274) is **still** a terminal of that net — the rule-1a invariant: the row
   BRANCHES the initial-value net, it does not steal it;
4. the walk has ZERO Pre-decided 85 violations.

A row that STOPS before its write (empty source walk, ambiguous source, an owner that is not the predicted one,
an unresolvable or non-unique sink, a LEFT OUTER that is already wired) wires NOTHING, substitutes NOTHING
(Pre-decided 68) — and its acceptance gate FAILS, so the run cannot exit 0 with a row that never happened.

## What is measured and never gated

- Pre-decided 95: the bare-terminal census of ALL 14 registers on the OLD loop `#637`, before and after, plus
  `ExecState` at both ends. M3a-2 is NOT required to reach `ExecState 1` and is not judged on it.
- Pre-decided 94: the TYPE CHECK. `Wire.Is Broken?` is read ONLY in a separate ordered pass after both rows —
  an idempotent re-connect whose `wire_delta` is expected to be 0 — never in the pass that made the connection.
  The op's own internal `Is Broken?` readback from the write pass is recorded verbatim as a FACT and is
  explicitly NOT the type check.
- Pre-decided 91: M3a-3 is NAMED with its uids and NOT wired here — `#4256` OUTER → wire 4859 → `Global #7202`
  t0, and `#4334` OUTER → wire 7506 → `FlatSequenceInnerTunnel #7468` stay exactly as they are, so leaving the
  two new RIGHT OUTER terminals bare drops no consumer (a bare SOURCE is legal LabVIEW, Pre-decided 69).

## Files and hygiene

Input: `claudeDev\D1_s3b_m3a_BROKEN_20260922_005732.vi` md5 `6b3c1f3c4ba80f1fa7411a55f0218bea` — copied once
with `shutil.copy2`, never opened over COM, never edited, never run; its md5 is a gate at both ends. Output:
`claudeDev\D1_s3b_m3a2_<stamp>.vi`, saved with `g.save(target, allow_broken=True)` (Pre-decided 88/96), with the
after-confirmation being the file's own size and md5 read back off disk and required to differ from the input.
The four STATUS md5 pins (ORIGINAL, S1, S2, the bed) and the two tool pins (`tools/gscript.py`,
`tools/bench/c60c_astcheck.py`) are gates at both ends.

## Already ruled out — do not re-raise these as new

- "The source must be a `Nodes[]` entry" — WITHDRAWN by Pre-decided 68; `OpConnectFromWire_v0` addresses the WIRE.
- "Use `wire_sr('LeftOutNode')`" — answered in Pre-decided 93 and above.
- "Gate on `ExecState 1`" — Pre-decided 89/95: the artefact is broken by design at this stage.
- "Use the border exemption of Pre-decided 66" — it does not apply; these are same-diagram rows, measured.
- "Build a device for this" — the user suspended device-building on 2026-09-18 08:53.

## THE QUESTION FOR YOU

Has any part of this already been analysed, built, measured or REFUTED in this project's own files — and is
there anything in the corpus that says this recipe will fail, or that a cheaper route already exists? Cite
`file:line`. The one finding that matters most is the one that would waste the run.
