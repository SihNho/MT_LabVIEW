"""build_d1_m3a1 - CYCLE 68 material #1: STAGE M3a-1, THE DELIVERABLE BUILD.

A RECIPE (it SAVES an artefact), gated by `py tools/bench/c60c_astcheck.py --route movein` BEFORE launch -
`--route movein` because this file calls `move_in` (Pre-decided 62: the route declares what the FILE DOES).

WHAT ALREADY EXISTS AND IS REUSED, NOT REBUILT. Checked before a line was written:
`docs/toolkit-capabilities.md`, `grep "^def " tools/gscript.py`, `ls tools/recipes tools/bench`.
  - `tools/gscript.py:673` `add_shift_reg` and `:723` `wire_sr` - the BUILT register creator / one-side writer,
    REPAIRED in cycle 67 (`ensure_loaded` at :708 and :750; `tools/bench/selftest_c67_ensureloaded.log` 4/4).
  - `tools/gscript.py:769` `shift_reg` / `:802` `shift_reg_left` - the BUILT register readers.
  - `tools/gscript.py:957` `tunnels` - the BUILT LoopTunnel reader. NO LONGER CALLED here: it was the
    probe's reader and the probe is deleted (B4). Left in this list so the next stage does not re-build it.
  - `tools/recipes/build_d1_v0.py:318` `move_in` / `:338` `owner_of` / `:357` `diag_index`.
  - `tools/recipes/build_opconnectnested_v1.py:418` `connect_nested_v1` - the BUILT node->node writer.
  - `tools/recipes/build_opconnectfromwire_v0.py:423` `wire_source_owner` - the ONLY BY-UID walk of a WIRE's
    own `Terms[]`, giving each endpoint's OWNER class and uid.
  - `tools/recipes/build_opconnectfromwire_v0.py:381` `connect_from_wire` - `OpConnectFromWire_v0.vi`,
    BUILT + SAVED 2026-09-17 (`docs/toolkit-capabilities.md:70`; 16 rows in service at
    `docs/d1-route-b-plan.md:84`): THE ONLY WRITER WHOSE **SOURCE NEED NOT BE A NODE** - it takes the
    source as (WIRE uid, terminal index on that wire). THIS IS WHAT WRITES THE t1 ROW.
  - `tools/bench/diag_c66b_s3b_m3.py:183-193` (`SET`) and `:200-210` (`INTERNAL_JOBS`) - THE SEVEN MOVES AND
    THE SEVEN INTERNAL ROWS ARE COPIED VERBATIM FROM THERE, same order, same addressing, NOT re-derived.
  - `tools/bench/diag_c67_m3a.py` - every helper below (gate/fact/probe/dump/safe/read_es/counts/node_census/
    terms_at/term_state/find_node/node_view/delete_by_uid/census_and_purge/save_artefact/unit_boundary/
    loop_index_of/echo_reg_uid/reg_index_of/resolve_term/resolve_dest/body_a_node_uids/census) is reused IN
    SHAPE from it. NO new op, NO new verb, NO edit to `tools/gscript.py`, NO edit to any `*_astcheck.py`.

THE BED  `claudeDev\\D1_s3b_row2_20260921_160311.vi`, md5 26c54ff784cb5cea21edbd214d2cc3a0, 476,759 B.
  READ-ONLY, md5-pinned BEFORE and AFTER, never overwritten. All work happens on fresh stamped copies.

THE ORDER IS FIXED BY THE BRIEF (Pre-decided 59/60/61/62/63) AND IS NOT RE-ORDERED HERE:
  [0] restart, handles, the four md5 pins (+ the two TOOL pins: gscript.py and c60c_astcheck.py).
  [1] DELETED 2026-09-21 by the prior-art review (B4 `already-measured` + B3 `helper-exists`;
      `archive/peer/2026-09-21-priorart-c68-m3a1.md`). THE PROBE AND ITS SCRATCH ARE GONE. Its answer was
      already on file and NEGATIVE (`tools/bench/diag_c67_addsr.log:393-403`, measured on a scratch
      byte-identical to THIS bed), and its PREMISE WAS WRONG: **a source need not be a node**, because
      `OpConnectFromWire_v0.vi` takes the source as (WIRE uid, terminal index on that wire), so the
      `FlatSequenceInnerTunnel #9655` that sources wire 9649 IS addressable. The probe's one genuinely
      unmeasured half - scanning `#686` for a DIFFERENTLY-OWNED terminal NAMED `'# slices in stack'` - is
      deleted WITH it and must never be re-added: a same-named source on another net is a DIFFERENT VALUE,
      i.e. exactly the rule-1a substitution Pre-decided 61 forbids as it forbids a Local.
  [2] copy the bed to WORK; the seven `move_in`s and the seven internal rows, VERBATIM from c66b.
  [3] `add_shift_reg` x2 on `#23032` with the repaired wrapper. PREDICTION: real uids are minted and
      `ExecState` goes 1 -> 0 (tools/gscript.py:683-687) - an unwired new register breaks the VI, and that
      is CORRECT, NOT A FAILURE. The minted uids and the `shift_reg` / `loop_cast` readback are recorded.
  [4] THE FOUR SR ROWS, **RightIn BEFORE LeftIn** (an untyped register takes the type of its first wire, and
      `#10407` t4 / t6 are the SOURCES): `#10407` t4 `'VISA out'`, `#10407` t6 `'position [internal units]'`,
      `#48` t3 `'VISA resource name'`, `#48` t4 `'In position'`. Verified BY WIRE UID AT BOTH ENDS.
  [5] THE FIFTH ROW, `#10407` t1 `'# slices in stack'`, WRITTEN WITH `connect_from_wire` (B3): SOURCE =
      the SOURCE terminal of WIRE 9649, owned by `FlatSequenceInnerTunnel #9655`
      (`tools/bench/diag_c67_addsr.log:395`); SINK = `#10407` t1. TWO MANDATORY PRECAUTIONS.
      (i) The SOURCE is MEASURED on wire 9649 IMMEDIATELY BEFORE the write, by `wire_source_owner`; if the
      walk comes back with NO source terminal, a FACT line is written and THE STEP STOPS - nothing is
      wired, nothing is substituted. Run 8's "w9649 has 0 source terminals" is that reader's blind spot
      (it cannot address tunnels), not a property of the wire, and this step PROVES which by measuring.
      (ii) The SINK's terminal index is RE-READ on the LIVE POST-MOVE target at that moment, NEVER carried
      from a pre-move census - T2c2's recorded cause of failure (`docs/toolkit-capabilities.md:70`).
      ACCEPTANCE, **RE-CUT 2026-09-21 BY PRE-DECIDED 70 (docs/cycle27-plan.md:2843-2853)**: the test is an
      OBJECT-IDENTITY test, in run, immediately after EVERY border write and again after the junk purge -
      `OpWireSource_v5(UID 2 = <source wire>)` must show a NEW terminal `is_source=False`,
      `owner_class LoopTunnel`, owner uid **T**, and `OpWireSource_v5(UID 2 = <new sink wire>)` exactly one
      `is_source=True LoopTunnel` with `owner_uid == T`. PASS = THE SAME T ON BOTH SIDES. `wire_delta 3`,
      "two DIFFERENT wire uids" and `Is Broken? False` are **WITHDRAWN as acceptance** - all three read the
      SINK side only - and survive as FACT lines. `ExecState` is NEVER substituted for the identity test.
      The same read settles Pre-decided 71: the junk `Invoke` the call mints is FACT-logged with its uid,
      because last run it carried **9649**, the uid of the live wire it was told to branch.
  [5b] THE SIXTH ROW (Pre-decided 72, docs/cycle27-plan.md:2866-2876), WIRED **BEFORE** THE CENSUS so A4
      judges the FINISHED stage - and the likely cause of `ExecState` 0 as well, since a SelectorTunnel
      left unwired breaks the VI. Owner chain of `SelectorTunnel #12673` (row label `Q_focusback`) -> its
      owning Case Structure -> that NODE's `Terms[]` -> **the entry that EXPOSES UID 12673** ->
      `connect_from_wire` from `#10407` t6's **LIVE** net (recorded 23963, RE-MEASURED). If the chain does
      not reach a Case Structure, or no entry exposes uid 12673, a FACT line names what the walk returned
      and THE ROW FAILS: no fallback is improvised, and the UNBUILT `Outside Terminal` property is OUT OF
      SCOPE for this run.
      *** FIX 1, 2026-09-21: THE BY-NAME LOOKUP ON `Q_focusback` IS DELETED (c70 prior-art review A3(i),
      `archive/peer/2026-09-21-priorart-c70-m3a1.md:222-231`): that string is a FUTURE QUEUE name
      (`docs/d1-build-plan.md:576`), and the owning node's three terminals are measured as "",
      "position [internal units]", "" (`tools/bench/main_vi_nodeterms.json:14287-14313`). The owner uid and
      the resolved terminal NAME are FACT lines (compared against 12589 / "position [internal units]"),
      never gates - the measurement governs. ***
  [6] THE FULL WIRED-TERMINAL CENSUS of all seven moved nodes plus both registers, same shape as
      `tools/bench/diag_c67_m3a.log:481-486`, PLUS THE BARE-SINK GATE (A4). `#10407` t6 has **TWO** sinks
      in the original - SR `#4256` AND `Q_focusback` `SelectorTunnel #12673` on net 9113
      (`tools/bench/diag_c67_addsr.log:389`) - and this build re-created ONE. Dropping a downstream
      consumer is a CHANGE OF COMPUTATION (rule 1a) that would pass SILENTLY, because a bare source is
      legal LabVIEW. `#12673`'s state is a FACT line either way; if this stage leaves it bare the run
      FAILS and the log names it as a SIXTH ROW for the next stage. Unconditional, whatever `ExecState`
      says. FROM 2026-09-21 THE SIXTH ROW IS WIRED AT [5b] BEFORE THIS GATE RUNS, so A4 now judges the
      FINISHED stage instead of reporting a known hole; it is UNCHANGED in code and should now PASS.
  [7] `ExecState`. 1 => save `claudeDev\\D1_s3b_m3a_<stamp>.vi`, RESTART, COLD reopen, ordered `Broken?`
      read LAST (42(b)/52(f)). 0 => save `claudeDev\\D1_s3b_m3a_BROKEN_<stamp>.vi` with
      **`gscript.save(WORK, allow_broken=True)` - AUTHORISED BY PRE-DECIDED 88, 2026-09-21**
      (docs/cycle27-plan.md:3063-3073): the `RuntimeError: refusing to save a BROKEN VI` that ended two
      cycles with nothing on disk was OUR OWN GUARD'S DEFAULT, and `tools/gscript.py:2087-2089` routes a
      broken VI to `gui_save()`. ⚠️ CITATION CORRECTED by the c71 prior-art review (A3(i)): the call
      site `tools/recipes/build_d1_routeb_v7.py:2276` is a PRECEDENT OF THE SHAPE, NOT OF SUCCESS - its
      run-10 invocation FAILED (`build_d1_routeb_v7_run10.log:367`, mtime did not move), so this save is
      an ATTEMPT whose outcome is recorded verbatim, never assumed. A gui_save failure leaves exactly
      the state cycles 55/56 ended in (no file, refusal recorded) - it cannot make anything worse.
      `gui_save` is the ONE GUI act in this file and carries its own guards (claudeDev-only path, live
      window-title locate, title-bar click, mtime-move confirm - tools/gscript.py:1998-2060); it CALLS
      `open_panel()` internally (tools/gscript.py:2016 - the 246 s / module-poisoning risk measured in
      `archive/peer/2026-09-21-c64-openpanel-cap.md:27-34` is accepted BECAUSE the save is the LAST
      LabVIEW act before [H], and the [H] md5 pins are read by `hash_probe` - pure file I/O, no COM -
      so a poisoned module cannot cost the pin audit). The recipe captures a screenshot BEFORE and
      AFTER the save (`_lv_gui -Action shot`) per the capture rider. The saved path is verified to be
      the claudeDev target, the artefact's bytes-differ-from-the-bed is a GATE (c71 review B3), and all
      four md5 pins are re-read at [H]. A broken artefact is NOT a deliverable, is NEVER run (34(f))
      and is NEVER used as a bed.

*** THE M3a-1 ARTEFACT IS NOT COMPUTATION-EQUIVALENT TO THE ORIGINAL, EITHER WAY: ITS SHIFT REGISTERS ARE
    UNINITIALISED (initial values are stage M3a-2, a rule-1a matter). IT IS NEVER RUN (34(f)). ***

GATING POLICY - Pre-decided 63: THIS RUN GATES ON **HYGIENE ONLY** and exits 0 when hygiene passes.
  H  the md5 pins hold before and after; the bed keeps its size; the working copy starts byte-identical to
     the bed; `tools/gscript.py` and `tools/bench/c60c_astcheck.py` are byte-identical before and after;
     every scratch is `exists=False` at the end; refs opened == closed == 0 live; handles read either side;
     and NO mutator call was REFUSED BY THE MACHINE (a raised wrapper error is a refusal and IS a gate; a
     measurement that comes back negative is a FACT line and is NOT).
  A3-ID THE BORDER IDENTITY GATE, ADDED 2026-09-21 (Pre-decided 70): after EVERY write that creates a
     `LoopTunnel`, the SAME LoopTunnel uid T must be a NEW SINK terminal on the SOURCE wire and the ONE
     SOURCE terminal of the NEW SINK wire. Anything else FAILS the row and the run. It is a gate and not a
     FACT line because the previous run's acceptance test was pointed at the sink side only, so a row could
     read "correct" without anything having been measured about the source side at all.
     *** RE-CUT 2026-09-21 (PD86 outcome A, tools/bench/diag_c68_pd86.log; c71 review B2-second): when the
     post-write walk of the queried source-wire uid is WHOLLY NULL, the write REPLACED that wire and the
     same-T test is UNDECIDABLE ON THE OLD UID - cycle 56's three A3-ID FAILs were this, by construction.
     The gate then decides on the SINK side alone (exactly ONE source of ANY class, a LoopTunnel,
     PD85-clean); a readable old source wire keeps the full same-T test unchanged. ***
  A5 THE SIXTH ROW IS ADDRESSABLE (Pre-decided 72, RE-CUT BY FIX 1): #12673's owner chain reaches a Case
     Structure one of whose `Terms[]` entries EXPOSES UID 12673, and t6's live net hands out a source
     terminal. If not, the row fails - NO fallback is improvised and NO name is guessed.
  A4 THE BARE-SINK GATE, ADDED 2026-09-21 BY THE PRIOR-ART REVIEW: no SINK that was wired on the bed may
     be left bare by this stage. Concretely `SelectorTunnel #12673` on `#10407` t6's net.
     This ONE non-hygiene gate exists because rule 1a outranks Pre-decided 63: a silently dropped consumer
     is a computation change, and the run must not exit 0 with one.
     *** FIX 3, 2026-09-21 - A4 ANCHORS AT THE **CONSUMER** AND NEEDS **ZERO HOPS** (Pre-decided 90,
     docs/cycle27-plan.md:3084-3089; it AMENDS FIX 2's two-branch outward walk, whose BORDER branch was an
     unbounded search with no failure mode). #12673 was measured a sink of a wire whose single source is
     the border LoopTunnel (`build_d1_m3a1.log:1151-1155`), so the gate re-reads the wire carried by the
     CONSUMER's own Terms[] entry (the one [5b] resolved BY UID) and walks THAT ONE wire: PASS = #12673 a
     non-source terminal on it with owner_class SelectorTunnel (the Pre-decided 85 class check), exactly
     ONE `is_source=True` terminal of ANY class (FIX 4 discipline; its class/uid a FACT, not a criterion),
     and zero PD85 recip violations. Hop count is an output, never a criterion. ***
  PD85 THE READER PRECONDITION (Pre-decided 85, added 2026-09-21): every OpWireSource_v5 row with a REAL
     owner must read `recip == queried_uid`; a violating walk is NOT BELIEVED and fails the gate built on
     it. Null padding rows (owner_uid 0) are excluded - measured in tools/bench/diag_c68_pd86.log
     (outcome A: the reader NULLS on an unresolvable uid; it does not echo; live reads are stable).
  Everything else - moves, rows, registers, `ExecState`, the save - is reported as FACT lines.

NO whole-VI `GObject` census anywhere (six of them took handles 34,602 -> 91,288); only the narrow classes
`Node` / `Wire` / `Tunnel` / `LoopTunnel` / `LeftShiftRegister` / `RightShiftRegister` / `ControlTerminal` /
`Local` are counted. FORBIDDEN AND ABSENT: `remove_bad_wires*` (banned since cycle 58), any GUI action
OTHER THAN the `gui_save()` that `save(allow_broken=True)` routes a broken VI to (Pre-decided 88;
gui_save's own guards at tools/gscript.py:1998-2060), any new op or verb, any edit to `tools/gscript.py` or a `*_astcheck.py`,
running any deliverable VI (34(f)), motor / ASI / camera (rig ASSEMBLED), any new process device,
`retrospective.py` / `audit_cycle.py` / `violations.py` / `doc_ingest.py` / `prior_art_review.py` (54(a)),
and any edit to `docs/cycle27-plan.md` or STATUS's `## NEXT`. `CYCLE_GUARD_OFF` is never set.
No route is chosen here and none is recommended. VERIFICATION IS STRUCTURAL, NEVER FUNCTIONAL (34(f)).
"""
import json
import os
import shutil
import sys
import time

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                              # noqa: BLE001
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench"),
           os.path.join(ROOT, "tools", "recipes")):
    sys.path.insert(0, _p)
import gscript as g                                                                # noqa: E402
import diag_s2_scaffold as D                                                       # noqa: E402
from bench_prep import labview_handles                                             # noqa: E402
from build_d1_v0 import diag_index, move_in, owner_of                              # noqa: E402
from build_opconnectfromwire_v0 import connect_from_wire as CONNECT_FROM_WIRE     # noqa: E402
from build_opconnectfromwire_v0 import wire_source_owner as WIRE_TERMS            # noqa: E402
from build_opconnectnested_v1 import connect_nested_v1 as CONNECT_V1               # noqa: E402
from hash_probe import probe as HASH                                               # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")
ORIGINAL, ORIG_MD5 = D.ORIGINAL, D.ORIG_MD5
S1_ARTEFACT, S1_MD5 = D.S1_ARTEFACT, D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
BED = os.path.join(g.CLAUDEDEV, "D1_s3b_row2_20260921_160311.vi")
BED_MD5 = "26c54ff784cb5cea21edbd214d2cc3a0"
BED_SIZE = 476759

# THE FOUR md5 PINS THE BRIEF NAMES, checked BEFORE and AFTER.
PINS = (("ORIGINAL", ORIGINAL, ORIG_MD5), ("S1 D1_s1_copy", S1_ARTEFACT, S1_MD5),
        ("S2 D1_s2_loops", S2_ARTEFACT, S2_MD5), ("THE BED", BED, BED_MD5))
# THE TWO TOOL PINS - "the forbidden list untouched", measured rather than asserted.
TOOL_PINS = (os.path.join(ROOT, "tools", "gscript.py"),
             os.path.join(BENCH, "c60c_astcheck.py"))

TOP = 0
D639 = 639                       # the nested diagram the loop-1.5 set lives on today
D639_RECORDED = 46
D639_NODES_RECORDED = 75
D686 = 686                       # the diagram that carries #637 and #23032
D686_RECORDED = 19               # diag_c67_addsr.log:381 - ECHOED here, never trusted as a constant
LOOP_A_UID = 23032               # the NEW While Loop; docs/cycle27-plan.md:951 - CITED, never re-derived
BODY_A_UID = 23058               # its body diagram, the destination of every move
LOOP11_UID = 637                 # the ORIGINAL While Loop that owns Diagram #639
LOOP637_TERMS_RECORDED = 59
LOOP637_WIRED_RECORDED = 48

SUBVI_UID = 48                   # ASI_adjust focus-subvi.vi
CASE_UID = 10407                 # the autofocus CaseStructure
LOCAL_ROW1_UID = 23499
LOCAL_ROW2_UID = 23523

# THE t1 NET, as diag_c67_addsr.log:390-392/395 measured it. RE-MEASURED on the LIVE target at step [5].
T1_TERM_NAME = "# slices in stack"
T1_TERM_INDEX = 1
T1_LOOP_TUNNEL = 9641            # the LoopTunnel on #637 that carries the value in today
T1_OUTER_WIRE = 9649             # its OUTER-side wire - THE SOURCE `connect_from_wire` IS GIVEN
T1_OUTER_SOURCE = 9655           # that wire's source owner: a FlatSequenceInnerTunnel. NOT a Nodes[] entry
                                 # - and that no longer matters: OpConnectFromWire_v0 addresses the WIRE.
T1_BORDER_WIRE_DELTA = 3         # A3 (WITHDRAWN as an acceptance test by Pre-decided 70 - still REPORTED):
                                 # the loop border auto-tunnels, so a border row was expected to add 3 wires
                                 # (docs/toolkit-capabilities.md:68, docs/cycle27-plan.md:2477-2479)

# PRE-DECIDED 70 - THE BORDER-ROW ACCEPTANCE TEST IS AN OBJECT-IDENTITY TEST, NOT A NUMBER.
# `wire_delta`, "two DIFFERENT wire uids" and `Is Broken? False` are all read on the SINK side of the new
# border; the "SOURCE-side wire 9649" of tools/bench/build_d1_m3a1.log:488 was the INPUT ARGUMENT, not an
# observation. Those three are kept as FACT lines and are NOT the acceptance test any more. The test is:
#   OpWireSource_v5(UID 2 = <source wire>) shows a NEW terminal is_source=False owner_class LoopTunnel uid T
#   OpWireSource_v5(UID 2 = <new sink wire>) shows EXACTLY ONE is_source=True LoopTunnel with owner_uid == T
# PASS = the SAME LoopTunnel uid T is a SINK on the source wire and the SOURCE of the sink wire.
# Properties already built - `Wire.Terms[]` 6371003, `Is Source?` 634A003, `Connected Wire` 634A000,
# `Generic.Owner` 6327806, `GObject.UID` 632A813. NO NEW OP. `ExecState` is NEVER substituted for this test.
T1_RECORDED_MINTED_UID = 9649    # PRE-DECIDED 71: last run the junk `Invoke` the call minted carried **the
                                 # uid of the live source wire**, while every other new object took a
                                 # monotonic uid in the 23,800-24,009 band (build_d1_m3a1.log:475, :498-526).
T1_RECORDED_SINK_WIRE = 24009    # last run's `UID 2` readback - the wire the call created at the sink
                                 # (build_d1_m3a1.log:473). RECORDED; RE-MEASURED live, never carried.

# PRE-DECIDED 72 - THE SIXTH ROW. A tunnel is not a `Nodes[]` entry, but its terminal IS an entry in its
# OWNING STRUCTURE NODE's `Terminals[]`. Route: owner chain of #12673 -> its owning Case Structure -> that
# node's Terms[] -> the entry that EXPOSES UID 12673 -> `connect_from_wire` from t6's **LIVE** net.
#
# *** FIX 1, 2026-09-21 (c70 prior-art review A3(i) `contradicted`, archive/peer/2026-09-21-priorart-c70-
#     m3a1.md:222-231): THE BY-NAME LOOKUP IS DELETED. `Q_focusback` IS NOT A TERMINAL NAME ON THIS BED -
#     it is the name of a FUTURE 1-element QUEUE in the D1 target design (`docs/d1-build-plan.md:576`),
#     and the measured census of the owning node says its three terminals are named "",
#     "position [internal units]", "" (`tools/bench/main_vi_nodeterms.json:14287-14313`, node uid 12589).
#     A by-name match on "Q_focusback" fails by construction. The string survives ONLY as a human-readable
#     ROW LABEL in log text (T6_SIXTH_SINK_LABEL) and in comments; it is on NO lookup or comparison path.
#     The selection is BY UID: the entry of the owner's Terms[] that exposes uid 12673. That is neither a
#     carried index (Pre-decided 72 forbids one) nor a guessed name.
#     HOW A UID IS READ OFF A Terms[] ENTRY, MEASURED, NOT ASSUMED: `node_terms` returns
#     {i, name, is_source, wire, err..., node_uid} and NO per-terminal uid (tools/gscript.py:931-937;
#     the recorded census carries the same four fields), and no reader this fleet owns returns one. The
#     ONLY uid-bearing walks are `OpWireSource_v5` (a WIRE's Terms[] -> each terminal's OWNER class+uid,
#     docs/toolkit-capabilities.md:60) and `OpOwnerChain_v1` (:61). So each entry's uid is resolved
#     THROUGH THE WIRE IT CARRIES: walk `OpWireSource_v5(entry.wire)` and read the owner uids. An entry
#     that carries NO wire exposes NO uid and therefore cannot be selected - and per (e) the ROW FAILS,
#     with every entry of the walk in the FACT lines. NO fallback is improvised.
T6_SIXTH_SINK_LABEL = "Q_focusback"   # LOG TEXT ONLY - see FIX 1 above. NEVER compared against a name.
T6_OWNER_CASE_RECORDED = 12589        # main_vi_nodeterms.json:14287 - the owner uid the census recorded.
                                      # FACT-logged and compared, NEVER a gate: the measurement governs.
T6_OWNER_TERM_NAME_RECORDED = "position [internal units]"   # :14304 - same status: FACT, not a gate
T6_LIVE_NET_RECORDED = 23963     # build_d1_m3a1.log:548 - the net t6 carried LAST RUN, NOT the 9113 the row
                                 # inventory names. It is a uid this build MINTS, so it is RE-MEASURED on
                                 # the live target and the recorded value is only ever compared, never used.
T6_OWNER_HOPS = 3                # an owner chain can terminate silently at a FlatSequenceFrame (rule: FACT
                                 # the hops VERBATIM and FAIL the row - never improvise a fallback)

# A4, THE BARE-SINK GATE. #10407 t6's net 9113 carries ONE source and TWO sinks in the original
# (tools/bench/diag_c67_addsr.log:389). This build re-creates the SR sink; the OTHER one is measured here.
T6_TERM_NAME = "position [internal units]"
T6_TERM_INDEX = 6
T6_ORIGINAL_NET = 9113
T6_SINKS_ORIGINAL = (4256, 12673)   # RightShiftRegister #4256 ; Q_focusback SelectorTunnel #12673
T6_SECOND_SINK = 12673
T6_SOURCE_FACE_RECORDED = 2017      # the SelectorTunnel face that SOURCES t6's net - PREDICTED BEFORE
                                    # THE RUN, as Pre-decided 90 requires: measured on the untouched bed
                                    # (tools/bench/diag_c68_pd86.log Q5: wire 9113's one source is
                                    # SelectorTunnel 2017) AND unchanged after cycle 56's write
                                    # (tools/bench/build_d1_m3a1.log:1233: post-write net 24226's source
                                    # is SelectorTunnel 2017). A4's provenance walk must terminate here.
T6_PROV_HOP_CAP = 4                 # the walk's FAILURE MODE (c71 review A3(ii)/B4): more hops than the
                                    # measured chain (2 tunnels) plus slack means something is wrong.

BASE = {"Node": 632, "Wire": 1907, "ControlTerminal": 116, "Local": 10, "LoopTunnel": 135}
BASE_TUNNEL = 471

# THE MOVE SET - SEVEN objects, VERBATIM from tools/bench/diag_c66b_s3b_m3.py:183-193.
SET = [
    (3529, "- Inc (PgDn)", (40, 60), "ControlReferenceConstant; docs/d1-build-plan.md:330"),
    (3560, "+ Inc (PgUp)", (40, 170), "ControlReferenceConstant; docs/d1-build-plan.md:331"),
    (3447, "Focus Step (F1)", (40, 280), "ControlReferenceConstant; docs/d1-build-plan.md:332"),
    (48, "ASI_adjust focus-subvi.vi", (300, 170), "SubVI; docs/d1-build-plan.md:306"),
    (10407, "Case Structure", (620, 60), "CaseStructure (autofocus); docs/d1-build-plan.md:305"),
    (LOCAL_ROW1_UID, "Local (row 1 carrier)", (40, 430),
     "Local; binds to its control BY LABEL, so the move is scheduling only (rule 1a)"),
    (LOCAL_ROW2_UID, "Local (row 2 carrier)", (40, 520),
     "Local; binds to its control BY LABEL, so the move is scheduling only (rule 1a)"),
]
SET_UIDS = [u for u, _n, _p, _e in SET]

# THE SEVEN INTERNAL ROWS - VERBATIM from tools/bench/diag_c66b_s3b_m3.py:200-210.
# (sink_uid, sink_name, sink_t, src_uid, src_name, src_t, evidence)
INTERNAL_JOBS = [
    (48, "-Inc reference", 0, 3529, "- Inc (PgDn)", 0, "w4833; c53_row_class.json :1919 / :2096"),
    (48, "+Inc reference", 1, 3560, "+ Inc (PgUp)", 0, "w2819; d1_rewire_sources.json:1946 / :2126"),
    (48, "Focus inc reference", 2, 3447, "Focus Step (F1)", 0, "w1893; d1_rewire_sources.json:1973 / :2156"),
    (10407, "Outgoing Handle", 3, 48, "Outgoing Handle", 6, "w11232; d1_rewire_sources.json:1820 / :2066"),
    (10407, "Out position", 5, 48, "Out position", 5, "w7388; d1_rewire_sources.json:1865 / :2036"),
    (10407, "", 0, LOCAL_ROW1_UID, "", 0,
     "row 1; wire 23502 measured at #10407 t0 and at Local #23499 t0"),
    (10407, "index", 2, LOCAL_ROW2_UID, "index", 0,
     "row 2; wire 23540 measured at #10407 t2 and at Local #23523 t0"),
]

# THE FOUR SR ROWS, **RightIn BEFORE LeftIn** (Pre-decided 59: the SOURCES type the register).
# variant RightIn -> the node terminal is a SOURCE (the right register's INSIDE terminal is the sink)
# variant LeftIn  -> the node terminal is a SINK   (the left register's INSIDE terminal is the source)
# (pair, variant, node_uid, term_name, term_index, node_term_is_source)
SR_JOBS = [
    ("VISA", "RightIn", CASE_UID, "VISA out", 4, True),
    ("POS", "RightIn", CASE_UID, "position [internal units]", 6, True),
    ("VISA", "LeftIn", SUBVI_UID, "VISA resource name", 3, False),
    ("POS", "LeftIn", SUBVI_UID, "In position", 4, False),
]
SR_PAIRS = ("VISA", "POS")

REG_PROBE_MAX = 8
RUN_DEADLINE_S = 45 * 60.0       # the bgrun --max-min this file is launched under
RESERVE_S = 420.0                # held back for the save, the restart and the cold reopen
BUILD_MIN_S = 600.0
ROW_MIN_S = 150.0

STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(BENCH, "build_d1_m3a1.json")
V1_LABELS = json.load(open(os.path.join(BENCH, "opconnectnested_v1_labels.json"), encoding="utf-8"))
CFW_LABELS = json.load(open(os.path.join(BENCH, "opconnectfromwire_v0_labels.json"), encoding="utf-8"))

WORK = os.path.join(g.CLAUDEDEV, "WORK_C68M3A1_%s.vi" % STAMP)
FINAL_PATH = os.path.join(g.CLAUDEDEV, "D1_s3b_m3a_%s.vi" % STAMP)
BROKEN_PATH = os.path.join(g.CLAUDEDEV, "D1_s3b_m3a_BROKEN_%s.vi" % STAMP)

T_START = time.time()
passes, fails, facts, refusals = [], [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "cycle 69 material #1: STAGE M3a-1 - the seven move_in calls and seven internal rows VERBATIM "
             "from diag_c66b_s3b_m3.py, two add_shift_reg pairs on #23032 with the repaired wrapper, the "
             "four SR rows RightIn-before-LeftIn, THE FIFTH ROW WRITTEN WITH connect_from_wire off WIRE "
             "9649 (the probe is DELETED), the full wired-terminal census WITH THE A4 BARE-SINK GATE, and "
             "the save",
     "recut_by_prior_art_review": "archive/peer/2026-09-21-priorart-c68-m3a1.md - all six findings ACCEPTED",
     "verification_level": "STRUCTURAL, never functional (34(f))",
     "gating_policy": "Pre-decided 63: HYGIENE ONLY. A negative measurement is a FACT line, not a gate. A "
                      "mutator call REFUSED BY THE MACHINE is a gate.",
     "bed": {"path": BED, "md5_pin": BED_MD5, "size_pin": BED_SIZE,
             "never_overwritten": "the bed is only ever READ; all work is on WORK"},
     "artefact_is_not_computation_equivalent":
         "THE M3a-1 ARTEFACT IS NOT COMPUTATION-EQUIVALENT TO THE ORIGINAL - ITS SHIFT REGISTERS ARE "
         "UNINITIALISED (initial values = stage M3a-2). It is never run (34(f)).",
     "initial_values_out_of_scope":
         "wire_sr('LeftOutNode') and wire_sr('LeftOutCtl') are NOT called anywhere in this file",
     "no_new_verb": True, "no_new_op": True, "no_new_device": True,
     "no_open_panel_call_in_this_file":
         "this FILE'S TEXT makes no open_panel call, BUT gscript.gui_save calls open_panel internally "
         "(tools/gscript.py:2016) when the PD88 broken save runs - c71 review A4; the 246 s poisoning "
         "risk (archive/peer/2026-09-21-c64-openpanel-cap.md:27-34) is accepted because the save is the "
         "last LabVIEW act and the [H] md5 pins are hash_probe file I/O, not COM",
     "gscript_not_edited": True,
     "no_astcheck_gate_file_edited":
         "THIS RUN edits no astcheck file; the cycle-57 FIREFIGHTER session amended c60c_astcheck.py "
         "gate 3 BEFORE this run (blanket allow_broken ban -> 'at most one site, only on .save()'), "
         "because the blanket ban encoded the WITHDRAWN Pre-decided 81 and contradicted Pre-decided 88 "
         "(c71 review B2-mechanical; hypothesis review archive/peer/2026-09-21-c71-astgate*). The [H] "
         "tool-pin gate still verifies the checker byte-identical ACROSS the run",
     "gui_actions": "ONLY gscript.gui_save, reached through save(allow_broken=True) on a broken VI - "
                    "Pre-decided 88 (docs/cycle27-plan.md:3063-3073); its guards: claudeDev-only path, "
                    "live window-title locate, mtime-move confirm (tools/gscript.py:1998-2060)",
     "broken_save_bypass": "AUTHORISED by Pre-decided 88: save(WORK, allow_broken=True) diverts a "
                           "broken VI to gui_save; the saved path and all four md5 pins are re-verified",
     "remove_bad_wires_scripted": "not imported, not called (BANNED since cycle 58)",
     "no_whole_vi_gobject_census": True,
     "no_vi_run": "no D1 artefact and no main VI is run (34(f)); OP VIs are run, the fleet's mechanism",
     "rig_state": "assembled - no motor, no ASI, no camera; tools/motor_gate.py not called",
     "chooses_no_route": True, "recommends_no_route": True,
     "edits_no_plan_document": True, "edits_no_status_next": True, "cycle_guard_off_never_set": True,
     "handles": {}, "hash_probe": [], "exec_state_timeline": [], "artefacts_on_disk": [],
     "purges": [], "build": {}, "census": {}}
K = R["build"]


class Halt(Exception):
    pass


def gate(name, ok, detail=""):
    # `FAIL`, NOT `**FAIL**` (37(i)): the bold form is invisible to guard_peer's FAILURE_RE anchor.
    (passes if ok else fails).append(name)
    print(("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""))
          .encode("ascii", "replace").decode("ascii"), flush=True)
    return ok


def fact(line):
    facts.append(line)
    print(("  FACT  %s" % line).encode("ascii", "replace").decode("ascii"), flush=True)


def refusal(where, msg):
    """A MUTATOR CALL THE MACHINE REFUSED. This is the only class of negative result that gates (63)."""
    refusals.append({"where": where, "error_verbatim": msg})
    fact("MACHINE REFUSAL at %s: %s" % (where, msg))


def probe_hash(tag, path):
    line = HASH(path)
    R["hash_probe"].append({"tag": tag, "line": line})
    fact("%s: %s" % (tag, line))
    return dict(kv.strip().split("=", 1) for kv in line.split(" | ")[1:])


def dump():
    R["gates"] = {"pass": len(passes), "fail": len(fails), "failing": fails}
    R["facts"] = facts
    R["machine_refusals"] = refusals
    R["elapsed_s"] = round(time.time() - T_START, 1)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


def left_s():
    return RUN_DEADLINE_S - (time.time() - T_START) - RESERVE_S


def safe(label, fn, default=None):
    """Run one READ, record its error VERBATIM, never let it kill the run."""
    try:
        return fn(), ""
    except Exception as e:                                                         # noqa: BLE001
        msg = "%s: %s" % (type(e).__name__, str(e)[:250])
        fact("%s raised %s" % (label, msg))
        return default, msg


def read_es(tag, target):
    t0 = time.time()
    try:
        es = g.exec_state(target)
    except Exception as e:                                                         # noqa: BLE001
        es = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    row = {"step": len(R["exec_state_timeline"]) + 1, "tag": tag,
           "target": os.path.basename(target), "exec_state": es,
           "wall_clock": time.strftime("%H:%M:%S"), "t_since_start_s": round(t0 - T_START, 1),
           "read_cost_s": round(time.time() - t0, 2)}
    R["exec_state_timeline"].append(row)
    fact("ExecState [%02d %s] = %r   (+%.1f s, read cost %.2f s)"
         % (row["step"], tag, es, row["t_since_start_s"], row["read_cost_s"]))
    return es


def counts(path, tag, classes=("Node", "Wire", "ControlTerminal", "Local", "LoopTunnel", "Tunnel")):
    """NARROW CLASS CENSUSES ONLY - never a whole-VI GObject census (six of those took handles 34,602 ->
    91,288)."""
    rec = {}
    for c in classes:
        rec[c], _ = safe("%s count(%r)" % (tag, c), lambda cc=c: g.count(path, cc))
    K.setdefault("censuses", {})[tag] = rec
    fact("%s counts: %r" % (tag, rec))
    return rec


def sr_counts(path, tag):
    rec = {}
    for c in ("LeftShiftRegister", "RightShiftRegister"):
        rec[c], _ = safe("%s count(%r)" % (tag, c), lambda cc=c: g.count(path, cc))
    fact("%s shift-register class counts: %r" % (tag, rec))
    return rec


def node_census(path, tag):
    rows, err = safe("%s report_all('Node')" % tag, lambda: g.report_all(path, "Node"), [])
    out = [{"i": r["i"], "uid": r["uid"], "class": r["class"], "pos": r["pos"], "owner_class": r["owner"]}
           for r in (rows or [])]
    fact("%s node census: %d rows%s" % (tag, len(out), ("  [%s]" % err) if err else ""))
    return out, err


def new_nodes(before, after):
    seen = {n["uid"] for n in before}
    return [n for n in after if n["uid"] not in seen]


def terms_at(path, diagram_index, nodes_index, expect_uid, tag, quiet=False):
    """The FULL terminal table of one node, with the node's own uid echoed back before it is believed."""
    rec = {"diagram_index": diagram_index, "nodes_index": nodes_index, "expected_uid": expect_uid}
    try:
        echo, rows = g.node_terms_uid(path, int(diagram_index), int(nodes_index))
        rec["uid_echo"] = echo
        rec["ok"] = (expect_uid is None) or (echo == expect_uid)
        rec["terminals"] = [{"i": t["i"], "name": t["name"], "is_source": t["is_source"], "wire": t["wire"],
                             "has_wire": bool(t["wire"]),
                             "errs": [t["name_err"], t["src_err"], t["conn_err"], t["wire_err"]]}
                            for t in rows]
    except Exception as e:                                                         # noqa: BLE001
        rec["ok"] = False
        rec["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        rec["terminals"] = []
    if not quiet:
        fact("%s terminal table of #%s (Diagram idx %r, Nodes[%r], echo %r): %d terminal(s)"
             % (tag, expect_uid, diagram_index, nodes_index, rec.get("uid_echo"), len(rec["terminals"])))
        for t in rec["terminals"]:
            fact("    %s t%-2d %-34r is_source=%-5r wire=%-7r errs=%r"
                 % (tag, t["i"], t["name"], t["is_source"], t["wire"], t["errs"]))
    return rec


def term_state(t):
    """WIRED / BARE / UNREAD for ONE terminal row (Pre-decided 14; gscript.py:874 gives the one legitimate
    bare-terminal error pattern: wire 0 with conn_err/wire_err 1055 and name_err/src_err 0)."""
    ne, se, ce, we = [int(x or 0) for x in t.get("errs", [0, 0, 0, 0])]
    if t.get("wire"):
        return "UNREAD" if (ne or se or ce or we) else "WIRED"
    if ne or se:
        return "UNREAD"
    if (ce and ce != 1055) or (we and we != 1055):
        return "UNREAD"
    return "BARE"


def wired_count(rows):
    return sum(1 for t in rows if term_state(t) == "WIRED")


def find_node(path, uid, hints, tag, budget_s=240.0, quiet=False):
    """Which DIAGRAM lists `uid` in its Nodes[] - answered by the census that finds it, NEVER by owner_of
    (owner_of is measured to answer with the PREVIOUS query's object, silently; Pre-decided 53(d^8))."""
    t0 = time.time()
    rec = {"uid": uid, "hints": list(hints), "scanned": [], "found": None}
    diags, derr = safe("%s report_all('Diagram')" % tag, lambda: g.report_all(path, "Diagram"), [])
    rec["diagram_rows"] = len(diags or [])
    rec["diagram_census_error"] = derr
    by_index = {d["i"]: d for d in (diags or [])}
    order = [i for i in hints if isinstance(i, int) and i in by_index]
    order += [i for i in sorted(by_index) if i not in order]
    for i in order:
        if time.time() - t0 > budget_s:
            rec["scan_stopped"] = "budget %.0f s reached after %d diagrams" % (budget_s, len(rec["scanned"]))
            break
        rows, err = safe("%s node_labels(%d)" % (tag, i), lambda k=i: g.node_labels(path, k), [])
        rec["scanned"].append({"diagram_index": i, "diagram_uid": by_index[i]["uid"],
                               "nodes": len(rows or []), "error": err})
        hit = next((k for k, r in enumerate(rows or []) if r["uid"] == uid), None)
        if hit is not None:
            rec["found"] = {"diagram_index": i, "diagram_uid": by_index[i]["uid"],
                            "diagram_class": by_index[i]["class"], "nodes_index": hit,
                            "nodes_on_diagram": len(rows), "label": rows[hit]["label"]}
            break
    rec["scan_cost_s"] = round(time.time() - t0, 1)
    if not quiet:
        fact("%s #%s lives at: %r  (%d diagram(s) scanned of %d, %.1f s)"
             % (tag, uid, rec["found"], len(rec["scanned"]), rec["diagram_rows"], rec["scan_cost_s"]))
    return rec


def node_view(path, uid, hints, tag, quiet=False):
    loc = find_node(path, uid, hints, tag, quiet=quiet)
    f = loc.get("found") or {}
    if f.get("nodes_index") is None:
        return loc, []
    tt = terms_at(path, f["diagram_index"], f["nodes_index"], uid, tag, quiet=quiet)
    loc["uid_echo"] = tt.get("uid_echo")
    loc["terminal_table"] = tt
    return loc, tt.get("terminals", [])


def delete_by_uid(path, cls, uid, tag):
    """report_all(cls) -> .index(uid) -> delete_object(cls, idx). The shape cycle 58 used; no new verb."""
    rec = {"class": cls, "uid": uid}
    rows, err = safe("%s report_all(%r) before delete" % (tag, cls), lambda: g.report_all(path, cls), [])
    rec["census_before"] = len(rows or [])
    rec["census_error"] = err
    idx = next((r["i"] for r in (rows or []) if r["uid"] == uid), None)
    rec["index"] = idx
    if idx is None:
        rec["result"] = "NOT IN THE %s CENSUS (%d rows) - nothing deleted" % (cls, len(rows or []))
        fact("%s delete %s #%s: %s" % (tag, cls, uid, rec["result"]))
        return rec
    t0 = time.time()
    try:
        gone = g.delete_object(path, cls, idx, verify=True)
        rec["gone"] = sorted(int(x) for x in (gone or []))
        rec["error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        rec["gone"] = None
        rec["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
        refusal("%s delete %s #%s" % (tag, cls, uid), rec["error_verbatim"])
    rec["call_cost_s"] = round(time.time() - t0, 2)
    after, _ = safe("%s report_all(%r) after delete" % (tag, cls), lambda: g.report_all(path, cls), [])
    rec["census_after"] = len(after or [])
    rec["still_present"] = any(r["uid"] == uid for r in (after or []))
    fact("%s delete %s #%s at index %r: gone %r, error %r, census %r -> %r, still present %r (%.2f s)"
         % (tag, cls, uid, idx, rec.get("gone"), rec.get("error_verbatim"), rec["census_before"],
            rec["census_after"], rec["still_present"], rec.get("call_cost_s", 0.0)))
    return rec


def census_and_purge(path, nodes_before, tag, hints, keep_uids=()):
    """55(c): after EVERY move_in and EVERY connect_nested_v1, diff the `Node` census and purge the junk BY
    UID. A new node is DELETED only when it is an `Invoke` with ZERO wired terminals (the measured junk
    shape). Anything else is REPORTED VERBATIM and left alone."""
    nodes_after, _ = node_census(path, "%s AFTER" % tag)
    fresh = new_nodes(nodes_before, nodes_after)
    rec = {"tag": tag, "node_count_before": len(nodes_before), "node_count_after": len(nodes_after),
           "new_uids": [(n["uid"], n["class"], n["pos"]) for n in fresh],
           "kept": list(keep_uids), "deleted": [], "reported_not_deleted": []}
    fact("%s CENSUS DIFF: Node %d -> %d ; %d new uid(s): %r"
         % (tag, len(nodes_before), len(nodes_after), len(fresh), rec["new_uids"]))
    for n in fresh:
        if n["uid"] in keep_uids:
            fact("%s new node #%s (%s) is INTENDED by this build - kept" % (tag, n["uid"], n["class"]))
            continue
        loc, rows = node_view(path, n["uid"], hints, "%s new #%s" % (tag, n["uid"]))
        wired = [t for t in rows if t.get("has_wire")]
        entry = {"uid": n["uid"], "class": n["class"], "pos": n["pos"],
                 "label": (loc.get("found") or {}).get("label"),
                 "diagram_index": (loc.get("found") or {}).get("diagram_index"),
                 "diagram_uid": (loc.get("found") or {}).get("diagram_uid"),
                 "terminals": rows, "n_terminals": len(rows), "n_wired": len(wired)}
        if n["class"] == "Invoke" and rows and not wired:
            fact("%s THE JUNK NODE'S FULL TERMINAL TABLE IS PRINTED ABOVE; %d terminal(s), %d WIRED - the "
                 "purge precondition (ZERO wired) HOLDS" % (tag, len(rows), len(wired)))
            entry["delete"] = delete_by_uid(path, "Node", n["uid"], "%s purge" % tag)
            rec["deleted"].append(entry)
        elif n["class"] == "Invoke" and not rows:
            rec["reported_not_deleted"].append(entry)
            fact("%s AN `Invoke` NEW NODE #%s COULD NOT BE LOCATED OR READ - IT IS NOT DELETED. Deleting a "
                 "node whose table was never read is the one branch that could destroy the artefact."
                 % (tag, n["uid"]))
        else:
            rec["reported_not_deleted"].append(entry)
            fact("%s NEW NODE NOT DELETED (not the measured junk shape): #%s class %r label %r, %d "
                 "terminal(s), %d wired - REPORTED, left alone"
                 % (tag, n["uid"], n["class"], entry["label"], entry["n_terminals"], entry["n_wired"]))
    final = nodes_after
    if rec["deleted"]:
        final, _ = node_census(path, "%s AFTER THE PURGE (the next step's baseline)" % tag)
        fact("%s purge arithmetic: Node %d -> %d -> %d (pre-call value %d)"
             % (tag, len(nodes_before), len(nodes_after), len(final), len(nodes_before)))
    rec["node_count_after_purge"] = len(final)
    R["purges"].append(rec)
    dump()
    return final, rec


def save_artefact(tag, dest, not_equal_to, not_equal_label):
    """g.save writes the WORKING copy in place; the artefact is a fresh path LabVIEW has never seen.
    A file byte-identical to its predecessor means THE IN-MEMORY EDITS DID NOT LAND."""
    rec = {"tag": tag, "dest": dest, "save_error_verbatim": "",
           "NOT_COMPUTATION_EQUIVALENT": "THE M3a-1 ARTEFACT IS NOT COMPUTATION-EQUIVALENT TO THE ORIGINAL "
                                         "- ITS SHIFT REGISTERS ARE UNINITIALISED. It is never run."}
    rec["exec_state_at_save"] = read_es("%s immediately before the save" % tag, WORK)
    # PRE-DECIDED 88 (2026-09-21, docs/cycle27-plan.md:3063-3073): allow_broken=True diverts a broken VI
    # to gui_save() instead of raising - the refusal that ended cycles 55 and 56 with nothing on disk
    # was our own guard's default. gui_save is a GUI act: its own guards are the claudeDev-only path
    # check, the live window-title locate and the mtime-move confirm (tools/gscript.py:1998-2060); the
    # saved path is WORK (inside claudeDev by construction) and the four md5 pins are re-read at [H].
    rec["allow_broken"] = True
    # The capture rider (Pre-decided 88 / docs/cycle27-plan.md:66-68): screenshot BEFORE and AFTER the
    # save. gui_save's own locate is the window-title match and its confirm is the mtime move + the
    # bytes-differ GATE below; the captures are the visual record either side of the one GUI act.
    shot_b = os.path.join(BENCH, "m3a1_save_before_%s.png" % STAMP)
    shot_a = os.path.join(BENCH, "m3a1_save_after_%s.png" % STAMP)
    safe("%s capture BEFORE the save" % tag, lambda: g._lv_gui("-Action", "shot", "-Out", "'%s'" % shot_b))
    try:
        rec["save_returned_size"] = g.save(WORK, allow_broken=True)
    except Exception as e:                                                         # noqa: BLE001
        rec["save_returned_size"] = None
        rec["save_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
    safe("%s capture AFTER the save" % tag, lambda: g._lv_gui("-Action", "shot", "-Out", "'%s'" % shot_a))
    rec["captures"] = {"before": shot_b, "before_exists": os.path.exists(shot_b),
                       "after": shot_a, "after_exists": os.path.exists(shot_a)}
    fact("%s capture->act->capture: before %r (exists %r), after %r (exists %r)"
         % (tag, os.path.basename(shot_b), rec["captures"]["before_exists"],
            os.path.basename(shot_a), rec["captures"]["after_exists"]))
    if rec["save_error_verbatim"]:
        fact("%s THE SAVE WAS REFUSED EVEN WITH allow_broken=True, VERBATIM: %s"
             % (tag, rec["save_error_verbatim"]))
        fact("%s NO FILE IS WRITTEN AT %s. Copying the working copy's DISK bytes would produce a file "
             "byte-identical to the bed - the in-memory edits would not be in it - so nothing is copied. "
             "This is reported to judgement, not worked around." % (tag, os.path.basename(dest)))
        refusal("%s g.save(WORK, allow_broken=True)" % tag, rec["save_error_verbatim"])
        rec.update({"exists": False, "md5": None, "size": None})
        R["artefacts_on_disk"].append(rec)
        dump()
        return rec
    try:
        shutil.copy2(WORK, dest)
        rec["copy_error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        rec["copy_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
    ff = D.file_facts("%s the artefact" % tag, dest)
    rec.update({"exists": bool(ff.get("exists")), "md5": ff.get("md5"), "size": ff.get("size"),
                "version_candidates": ff.get("version_candidates")})
    rec["compared_against"] = not_equal_label
    rec["bytes_equal_to_the_predecessor"] = (ff.get("md5") == not_equal_to)
    # c71 prior-art review B3 (helper-exists): whether the in-memory edits reached the disk is the whole
    # question, so bytes-differ is a GATE, not a FACT - the fleet's own precedent is
    # tools/recipes/build_d1_routeb_v7.py:2280 ("the SAVED bytes are NOT the original's").
    gate("%s the saved artefact's bytes DIFFER from %s - the in-memory edits reached the disk"
         % (tag, not_equal_label), rec["exists"] and not rec["bytes_equal_to_the_predecessor"],
         "artefact md5 %r vs %r" % (rec.get("md5"), not_equal_to))
    R["artefacts_on_disk"].append(rec)
    fact("%s FILE ON DISK: %s  md5 %r  size %r  (ExecState at the save %r ; bytes equal to %s %r)"
         % (tag, dest, rec["md5"], rec["size"], rec["exec_state_at_save"], not_equal_label,
            rec["bytes_equal_to_the_predecessor"]))
    fact("*** %s IS NOT COMPUTATION-EQUIVALENT TO THE ORIGINAL - ITS SHIFT REGISTERS ARE UNINITIALISED. "
         "The initial values are stage M3a-2. IT IS NEVER RUN (34(f)). ***" % os.path.basename(dest))
    dump()
    return rec


def unit_boundary(tag):
    """The user's 2026-09-19 split rule, applied MECHANICALLY and not as a branch: read ExecState at every
    unit boundary and, WHENEVER it reads 1, leave a file on disk before the next unit starts."""
    es = read_es("[UNIT] %s" % tag, WORK)
    K.setdefault("unit_boundaries", []).append({"tag": tag, "exec_state": es})
    if es == 1:
        k = sum(1 for a in R["artefacts_on_disk"] if "_u" in os.path.basename(a["dest"])) + 1
        save_artefact("[UNIT %d] %s - ExecState 1 at a unit boundary" % (k, tag),
                      os.path.join(g.CLAUDEDEV, "D1_s3b_m3a_u%d_%s.vi" % (k, STAMP)), BED_MD5, "the bed")
    else:
        fact("[UNIT] %s: ExecState %r - NOT 1, so no intermediate file is written at this boundary" % (tag, es))
    dump()
    return es


# ============================================== the A7 pattern: a loop_index is ECHOED, never carried
def loop_index_of(uid, tag):
    rows, err = safe("%s report_all('WhileLoop')" % tag, lambda: g.report_all(WORK, "WhileLoop"), [])
    idx = next((r["i"] for r in (rows or []) if r["uid"] == uid), None)
    echo = next((r["uid"] for r in (rows or []) if r["i"] == idx), None) if idx is not None else None
    K.setdefault("loop_index_echoes", []).append(
        {"tag": tag, "want_uid": uid, "loop_index": idx, "echoed_uid": echo,
         "whileloop_rows": len(rows or []), "error_verbatim": err})
    fact("%s A7 ECHO: report_all('WhileLoop')[%r].uid == %r (want #%d; %d WhileLoop row(s))"
         % (tag, idx, echo, uid, len(rows or [])))
    if echo != uid:
        refusal("%s loop_index echo" % tag,
                "report_all('WhileLoop')[%r].uid == %r, not #%d" % (idx, echo, uid))
        return None
    return idx


def echo_reg_uid(loop_index, reg_index, want_uid, tag):
    sr, err = safe("%s shift_reg(reg_index=%r) echo" % (tag, reg_index),
                   lambda: g.shift_reg(WORK, loop_index, reg_index))
    got = (sr or {}).get("uid")
    fact("%s REGECHO: shift_reg[reg_index=%r].uid == %r (want #%r)%s"
         % (tag, reg_index, got, want_uid, (" ; ERROR " + err) if err else ""))
    return got


def reg_index_of(loop_index, reg_uid, tag):
    """Map a RightShiftRegister uid to its reg_index by READING shift_reg(...) for each slot. Never assumed."""
    probes, hit = [], None
    for k in range(REG_PROBE_MAX):
        sr, err = safe("%s shift_reg(reg_index=%d)" % (tag, k),
                       lambda kk=k: g.shift_reg(WORK, loop_index, kk))
        row = {"reg_index": k, "uid": (sr or {}).get("uid"), "error_verbatim": err,
               "out": (sr or {}).get("out"), "inside": (sr or {}).get("inside"),
               "op_errors": (sr or {}).get("errors")}
        probes.append(row)
        fact("%s shift_reg[reg_index=%d] -> uid %r ; out %r ; inside %r ; errors %r"
             % (tag, k, row["uid"], row["out"], row["inside"], row["op_errors"]))
        if row["uid"] == reg_uid and hit is None:
            hit = k
        if err:
            break
    K.setdefault("reg_index_probes", []).append({"tag": tag, "want_uid": reg_uid, "resolved": hit,
                                                 "probes": probes})
    fact("%s REGINDEX: RightShiftRegister #%r -> reg_index %r (READ, never assumed)" % (tag, reg_uid, hit))
    return hit


def resolve_term(rows, want_name, want_i, want_source, tag):
    """Address a terminal OFF THE MACHINE: by NAME when the name is non-empty and unique among terminals of
    the right direction, otherwise by the RE-MEASURED index. Never by a remembered coordinate."""
    cands = [t for t in rows if t.get("is_source") is want_source]
    if want_name:
        named = [t for t in cands if t.get("name") == want_name]
        if len(named) == 1:
            return named[0]["i"], "by NAME %r (unique among %d %s terminals)" % (
                want_name, len(cands), "source" if want_source else "sink")
    hit = next((t for t in cands if t["i"] == want_i), None)
    if hit is not None:
        return hit["i"], ("by RE-MEASURED INDEX t%d (name %r is empty or not unique); that terminal reads "
                          "name %r is_source %r" % (want_i, want_name, hit.get("name"), hit.get("is_source")))
    fact("%s UNRESOLVED: no %s terminal named %r and none at index %d among %d row(s)"
         % (tag, "source" if want_source else "sink", want_name, want_i, len(rows)))
    return None, "UNRESOLVED"


# ============================= PRE-DECIDED 70: THE BORDER-ROW IDENTITY GATE (added 2026-09-21, cycle 70)
def pd85_violations(wire_uid, walk):
    """PRE-DECIDED 85, THE READER PRECONDITION (docs/cycle27-plan.md:3031-3038): before any assertion
    built on an `OpWireSource_v5` walk can be believed, EVERY row with a REAL owner must satisfy
    `recip == queried_uid`. Rows with owner_uid 0 are the reader's NULL PADDING and are excluded -
    MEASURED 2026-09-21 (tools/bench/diag_c68_pd86.log): an unresolvable uid returns exactly one
    all-zero row (outcome A - the reader NULLS, it does not echo: the live read straight after the
    two unresolvable ones returned the true rows, twice, 1 s apart, field-for-field identical),
    and every LIVE walk carries one trailing all-zero padding row. A row with a real owner whose
    recip differs is the `:1096-1098` artefact - one wire read under another's name."""
    return [t for t in (walk or []) if t.get("owner_uid") and t.get("recip") != wire_uid]


def print_walk(tag, wire_uid, walk, err=""):
    """One FACT line per terminal of `OpWireSource_v5(UID 2 = wire_uid)`: is_source / owner_class /
    owner_uid / recip. This is the raw material of BOTH Pre-decided 70 (identity) and 71 (recycled uid)."""
    real = [t for t in (walk or []) if t.get("owner_uid")]
    fact("%s OpWireSource_v5(UID 2 = %r): %d row(s), %d with a REAL owner%s"
         % (tag, wire_uid, len(walk or []), len(real), (" ; " + err) if err else ""))
    for t in (walk or []):
        fact("    %s   t%-2r is_source=%-5r owner_class=%-26r owner_uid=%-7r recip=%r%s"
             % (tag, t.get("i"), t.get("is_source"), t.get("owner_class"), t.get("owner_uid"),
                t.get("recip"), ("  READ ERROR " + str(t["err"])) if t.get("err") else ""))
    bad = pd85_violations(wire_uid, walk)
    fact("%s PD85 PRECONDITION: %d real-owner row(s), %d violate recip==queried_uid%s"
         % (tag, len(real), len(bad),
            (" -> %r - THIS WALK IS NOT BELIEVED (Pre-decided 85)"
             % [(t.get("i"), t.get("owner_class"), t.get("owner_uid"), t.get("recip")) for t in bad])
            if bad else ""))
    K.setdefault("pd85_checks", []).append({"tag": tag, "wire_uid": wire_uid,
                                            "real_rows": len(real), "violations": len(bad)})
    return walk or []


def wire_walk(tag, wire_uid):
    """`OpWireSource_v5(UID 2 = wire_uid)` on the LIVE target, printed terminal by terminal."""
    walk, err = safe("%s OpWireSource_v5(UID 2 = %r)" % (tag, wire_uid),
                     lambda: WIRE_TERMS(WORK, int(wire_uid)) if wire_uid else [], [])
    return print_walk(tag, wire_uid, walk, err), err


def loop_tunnel_sinks(walk):
    return sorted({int(t["owner_uid"]) for t in (walk or [])
                   if t.get("owner_class") == "LoopTunnel" and not t.get("is_source")
                   and t.get("owner_uid")})


def identity_gate(tag, source_wire, src_before, src_after, sink_wire, sink_walk, mandatory):
    """PRE-DECIDED 70, THE WHOLE TEST, READ OFF THE MACHINE AND NOTHING ELSE.

    PASS = the SAME `LoopTunnel` uid T is (a) a NEW **SINK** terminal on the SOURCE wire and (b) the ONE
    **SOURCE** terminal of the NEW SINK wire. `ExecState`, `wire_delta`, `Is Broken?` and "two different
    wire uids" are NEVER substituted for it - the first says nothing about this wire and the other three
    read the SINK side only (tools/bench/build_d1_m3a1.log:488; docs/cycle27-plan.md:2843-2853).
    `mandatory` False records the same measurement as FACT lines when the write created no LoopTunnel at
    all, i.e. when it was not a border write; the row's own gate then decides it.

    *** FIX 4, 2026-09-21 - COUNT FIRST, FILTER NEVER (c70 prior-art review B4 `already-measured`,
    `archive/peer/2026-09-21-priorart-c70-m3a1.md:252-258`). As first coded this gate filtered the sink
    wire's source terminals to `owner_class == "LoopTunnel"` BEFORE counting them, so the ONE recorded
    pathology it claimed to re-test would have PASSED: broken wire w1231 has TWO `is_source=True`
    terminals - `SelectorTunnel #5680` AND `LoopTunnel #2497` - with `Wire.Is Broken? True`
    (`tools/bench/build_opconnectfromwire_v0_run2.log:103-104`), and the LoopTunnel filter leaves exactly
    one. The order is now reversed: **ALL** `is_source=True` terminals on the sink wire are counted, of
    EVERY owner class, the total must be exactly **1**, and that one must be the LoopTunnel **T**. The
    source-wire side gets the same discipline - the full walk is logged and sinks of every class are
    counted before the LoopTunnel-owned subset is taken to define T. ***
    """
    before_t = loop_tunnel_sinks(src_before)
    after_t = loop_tunnel_sinks(src_after)
    new_t = [u for u in after_t if u not in before_t]
    # ---- FIX 4: the SINK side. Count EVERYTHING that claims to be a source, THEN look at its class.
    sink_all_src = [t for t in (sink_walk or []) if t.get("is_source")]
    sink_all_classes = [(t.get("owner_class"), t.get("owner_uid")) for t in sink_all_src]
    the_one = sink_all_src[0] if len(sink_all_src) == 1 else None
    sink_src = [t for t in sink_all_src
                if t.get("owner_class") == "LoopTunnel" and t.get("owner_uid")]
    sink_t = sorted({int(t["owner_uid"]) for t in sink_src})
    shared = [u for u in new_t if u in sink_t]
    one_is_the_loop_tunnel = bool(
        the_one is not None and the_one.get("owner_class") == "LoopTunnel" and the_one.get("owner_uid")
        and int(the_one["owner_uid"]) in new_t)
    # ---- PRE-DECIDED 85 (added 2026-09-21, cycle 57): the reader precondition COMES FIRST. A walk with
    #      a real-owner row whose recip is not the queried uid is the :1096-1098 artefact and is NOT
    #      believed - the gate cannot PASS on it.
    pd85_bad = (pd85_violations(source_wire, src_before) + pd85_violations(source_wire, src_after)
                + pd85_violations(sink_wire, sink_walk))
    # ---- PD86 OUTCOME A (measured, tools/bench/diag_c68_pd86.log; c71 review B2-second): a wholly
    #      NULL post-write walk of the queried source-wire uid means the write REPLACED that wire (the
    #      reader nulls on an unresolvable uid - it does not echo). The same-T test is then UNDECIDABLE
    #      ON THE OLD UID - failing it there would fail correct work by construction (that is what the
    #      three A3-ID FAILs of cycle 56 were). The gate then decides on the SINK side alone: exactly
    #      ONE source terminal of ANY class, it is a LoopTunnel, and the walk is PD85-clean; the
    #      LoopTunnel's uid is a FACT line. When the old source wire IS still readable, the full same-T
    #      identity applies unchanged.
    source_replaced = not [t for t in (src_after or []) if t.get("owner_uid")]
    sink_ok = (bool(sink_wire) and len(sink_all_src) == 1 and the_one is not None
               and the_one.get("owner_class") == "LoopTunnel" and bool(the_one.get("owner_uid"))
               and not pd85_violations(sink_wire, sink_walk))
    if source_replaced:
        ok = sink_ok
        fact("%s PD86 OUTCOME A: the post-write walk of source wire %r is WHOLLY NULL - the write "
             "replaced that wire; same-T is undecidable on the old uid and the gate decides on the "
             "SINK side alone (sink_ok %r)" % (tag, source_wire, sink_ok))
    else:
        ok = (sink_ok and one_is_the_loop_tunnel and len(shared) == 1 and not pd85_bad)
    # ---- FIX 4: the SOURCE side, same discipline - every sink terminal of every class, unfiltered.
    src_all_sinks_before = [(t.get("owner_class"), t.get("owner_uid")) for t in (src_before or [])
                            if t.get("is_source") is False]
    src_all_sinks_after = [(t.get("owner_class"), t.get("owner_uid")) for t in (src_after or [])
                           if t.get("is_source") is False]
    src_all_sources_after = [(t.get("owner_class"), t.get("owner_uid")) for t in (src_after or [])
                             if t.get("is_source")]
    rec = {"tag": tag, "source_wire": source_wire, "sink_wire": sink_wire,
           "source_side_loop_tunnel_sinks_before": before_t,
           "source_side_loop_tunnel_sinks_after": after_t, "NEW_on_the_source_wire": new_t,
           "source_side_ALL_sink_terminals_before": src_all_sinks_before,
           "source_side_ALL_sink_terminals_after": src_all_sinks_after,
           "source_side_ALL_source_terminals_after": src_all_sources_after,
           "sink_wire_loop_tunnel_sources": sink_t,
           "sink_wire_loop_tunnel_source_terminal_count": len(sink_src),
           "sink_wire_ALL_source_terminal_count": len(sink_all_src),
           "sink_wire_ALL_source_terminals": sink_all_classes,
           "the_one_source_terminal_is_the_loop_tunnel_T": one_is_the_loop_tunnel,
           "pd85_violations": [(t.get("i"), t.get("owner_class"), t.get("owner_uid"), t.get("recip"))
                               for t in pd85_bad],
           "source_wire_replaced_pd86_outcome_A": source_replaced, "sink_side_ok": sink_ok,
           "T": (shared[0] if (ok and len(shared) == 1) else None), "pass": ok,
           "mandatory": bool(mandatory), "exec_state_is_never_substituted_for_this": True,
           "fix4": "ALL is_source=True terminals are counted before any class filter "
                   "(archive/peer/2026-09-21-priorart-c70-m3a1.md:252-258; the w1231 pathology at "
                   "tools/bench/build_opconnectfromwire_v0_run2.log:103-104 would pass a filtered count)"}
    fact("%s IDENTITY: source wire %r LoopTunnel SINK owners %r -> %r (NEW %r) ; ALL sink terminals on the "
         "source wire %r -> %r ; ALL source terminals on it %r"
         % (tag, source_wire, before_t, after_t, new_t, src_all_sinks_before, src_all_sinks_after,
            src_all_sources_after))
    fact("%s IDENTITY (FIX 4, COUNT BEFORE FILTER): sink wire %r has %d source terminal(s) OF ANY CLASS %r "
         "(want EXACTLY 1) ; of those %d are LoopTunnel-owned %r ; the ONE is the new LoopTunnel T: %r ; "
         "SAME uid T on both sides: %r"
         % (tag, sink_wire, len(sink_all_src), sink_all_classes, len(sink_src), sink_t,
            one_is_the_loop_tunnel, (shared[0] if len(shared) == 1 else None)))
    label = ("A3-ID %s: the SAME LoopTunnel uid is a SINK on the source wire and the SOURCE of the sink "
             "wire (Pre-decided 70)" % tag)
    if mandatory:
        gate(label, ok, "T=%r ; new-on-source %r ; sink-side LoopTunnel %r ; sink wire %r ; ALL source "
                        "terminals on the sink wire %d %r (want exactly 1, and it must be T - FIX 4) ; "
                        "PD85 violations %d (want 0)"
             % (rec["T"], new_t, sink_t, sink_wire, len(sink_all_src), sink_all_classes, len(pd85_bad)))
    else:
        fact("%s NOT GATED HERE - this write created no LoopTunnel, so it is not a border write; the "
             "identity numbers above are FACT lines and the row's own gate decides it. Result would have "
             "been %r." % (tag, ok))
    K.setdefault("identity_gates", []).append(rec)
    return rec


# ======================================================================= [0] files only, zero LabVIEW
def phase_0():
    print("\n---------- [0] FILES ONLY, ZERO LabVIEW - the md5 pins BEFORE, then the pre-batch restart",
          flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r (fresh-instance baseline ~31,500; the pre-batch restart below is "
         "MANDATORY - 44(e))" % R["handles"]["before"])
    for tag, path, pin in PINS:
        pr = probe_hash("H %s BEFORE" % tag, path)
        gate("H %s md5 == its pin %s" % (tag, pin[:8]), pr.get("md5") == pin, "%r" % (pr.get("md5"),))
    pr = probe_hash("H THE BED size", BED)
    gate("H the bed is %d B" % BED_SIZE, str(pr.get("size")) == str(BED_SIZE), "%r" % (pr.get("size"),))
    K["tool_pins_before"] = {}
    for p in TOOL_PINS:
        pr = probe_hash("H TOOL %s BEFORE" % os.path.basename(p), p)
        K["tool_pins_before"][p] = pr.get("md5")

    D.fresh("[0] pre-batch LabVIEW restart (44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the restart: %r" % R["handles"]["after_restart"])
    dump()


# [1] DELETED 2026-09-21 BY THE PRIOR-ART REVIEW (B4 `already-measured` + B3 `helper-exists`).
# The probe, its scratch copy and the scratch's create/delete machinery are GONE. Its answer was already on
# file and NEGATIVE (tools/bench/diag_c67_addsr.log:393-403); its premise - "a source is addressable only as
# a NODE in some diagram's Nodes[]" - is WITHDRAWN, because `OpConnectFromWire_v0.vi` addresses the WIRE.
# Its one unmeasured half, the #686 scan for a differently-owned terminal NAMED '# slices in stack', is
# deleted with it and MUST NOT BE RE-ADDED: a same-named source on another net is a DIFFERENT VALUE.


# ================================================= [2a] the working copy and its cold baseline
def step_2_baseline():
    print("\n---------- [2a] THE WORKING COPY AND ITS COLD BASELINE", flush=True)
    shutil.copy2(BED, WORK)
    pr = probe_hash("[2a] the working copy", WORK)
    gate("H the working copy starts byte-identical to the bed", pr.get("md5") == BED_MD5,
         "%r" % (pr.get("md5"),))
    es = read_es("[2a] the working copy, COLD", WORK)
    if es != 1:
        refusal("[2a] the working copy's COLD ExecState", "reads %r, not 1" % (es,))
        raise Halt("the working copy does not reopen at ExecState 1")
    c = counts(WORK, "[2a] COLD")
    K["counts_before"] = c
    for k, v in BASE.items():
        fact("[2a] %s == %r (recorded baseline %d ; match %r)" % (k, c.get(k), v, c.get(k) == v))
    fact("[2a] Tunnel == %r (recorded baseline %d ; match %r)"
         % (c.get("Tunnel"), BASE_TUNNEL, c.get("Tunnel") == BASE_TUNNEL))
    K["sr_counts_before"] = sr_counts(WORK, "[2a] COLD")

    di, err = safe("[2a] diag_index(#%d)" % D639, lambda: diag_index(WORK, D639))
    K["d639_index"] = di
    if di is None:
        refusal("[2a] diag_index(#%d)" % D639, err or "returned None")
        raise Halt("Diagram #%d does not resolve" % D639)
    rows, lerr = safe("[2a] node_labels(%r)" % di, lambda: g.node_labels(WORK, di), [])
    K["d639_nodes"] = len(rows or [])
    fact("[2a] Diagram #%d -> traverse index %r (recorded %d) ; %d node(s) (recorded %d)%s"
         % (D639, di, D639_RECORDED, len(rows or []), D639_NODES_RECORDED, (" ; " + lerr) if lerr else ""))
    ncen, _ = node_census(WORK, "[2a] whole-VI Node")
    K["node_census_before"] = ncen
    hints = [di, TOP]
    _loc, lrows = node_view(WORK, LOOP11_UID, hints, "[2a] #%d the WhileLoop" % LOOP11_UID, quiet=True)
    K["loop637_before"] = {"n_terms": len(lrows), "n_wired": wired_count(lrows)}
    fact("[2a] #%d (WhileLoop): %d terminals, %d WIRED (recorded %d / %d)"
         % (LOOP11_UID, len(lrows), wired_count(lrows), LOOP637_TERMS_RECORDED, LOOP637_WIRED_RECORDED))
    dump()
    return hints


# ================================================================= [2b] the seven `move_in` calls
def resolve_dest(tag):
    """38(e): RE-RESOLVE the destination index BY UID from a freshly-read traverse list immediately before
    every `move_in`."""
    lst, err = safe("%s report_all('Diagram')" % tag, lambda: g.report_all(WORK, "Diagram"), [])
    uids = [o["uid"] for o in (lst or [])]
    idx = uids.index(BODY_A_UID) if BODY_A_UID in uids else None
    owns = idx is not None and uids[idx] == BODY_A_UID
    K.setdefault("dest_index_resolutions", []).append(
        {"tag": tag, "want_diagram_uid": BODY_A_UID, "resolved_index": idx, "traverse_len": len(uids),
         "index_still_owns_it": owns, "error_verbatim": err})
    fact("%s DESTINDEX: Diagram #%d -> traverse index %r (array length %d ; still owns it %r)"
         % (tag, BODY_A_UID, idx, len(uids), owns))
    if not owns:
        refusal("%s resolve_dest" % tag, "the traverse array does not list Diagram #%d" % BODY_A_UID)
    return idx


def body_a_node_uids(tag):
    """THE AUTHORITATIVE READ: Diagram #23058's own Nodes[] census, by uid."""
    idx, err = safe("%s diag_index(#%d)" % (tag, BODY_A_UID), lambda: diag_index(WORK, BODY_A_UID))
    if idx is None:
        fact("%s Diagram #%d could not be resolved: %s" % (tag, BODY_A_UID, err))
        return [], idx
    rows, lerr = safe("%s node_labels(%r)" % (tag, idx), lambda: g.node_labels(WORK, idx), [])
    uids = [r["uid"] for r in (rows or [])]
    fact("%s Diagram #%d [traverse %r] Nodes[] census: %d node(s) -> %r%s"
         % (tag, BODY_A_UID, idx, len(uids), uids, (" ; " + lerr) if lerr else ""))
    return uids, idx


def step_2_moves(hints):
    print("\n---------- [2b] THE SEVEN `move_in` CALLS, VERBATIM FROM diag_c66b_s3b_m3.py (37(d) severs "
          "every wire on the moved object)", flush=True)
    before_uids, bidx = body_a_node_uids("[2b] BEFORE")
    K["body_a_before"] = before_uids
    nodes = K["node_census_before"]
    after_hints = [bidx, hints[0], TOP]
    for uid, name, pos, why in SET:
        _loc, rows = node_view(WORK, uid, hints, "[2b] #%d BEFORE" % uid, quiet=True)
        fact("[2b] #%d %r BEFORE the move: %d terminal(s), %d WIRED  (%s)"
             % (uid, name, len(rows), wired_count(rows), why))
        bi = resolve_dest("[2b] before move #%d" % uid)
        rec = {"uid": uid, "name": name, "dest_diagram_uid": BODY_A_UID, "dest_index_used": bi,
               "position": list(pos), "wired_before": wired_count(rows), "n_terms_before": len(rows)}
        try:
            rec["echoed_uid"] = move_in(WORK, uid, bi, pos)
            rec["error_verbatim"] = ""
            fact("[2b] MOVE #%d %r -> Diagram #%d [traverse %r] at %r; the op echoed uid %r (37(d): the "
                 "echo is NOT the moved object)" % (uid, name, BODY_A_UID, bi, pos, rec["echoed_uid"]))
        except Exception as e:                                                     # noqa: BLE001
            rec["echoed_uid"] = None
            rec["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
            refusal("[2b] move_in(#%d)" % uid, rec["error_verbatim"])
        nodes, _p = census_and_purge(WORK, nodes, "[2b] after move #%d" % uid, after_hints)
        after_uids, _ = body_a_node_uids("[2b] after move #%d" % uid)
        rec["in_body_a_nodes"] = uid in after_uids
        fact("[2b] #%d in Diagram #%d's Nodes[] after the move: %r (body holds %d node(s))"
             % (uid, BODY_A_UID, rec["in_body_a_nodes"], len(after_uids)))
        own, oerr = safe("[2b] owner_of(%d) after the move" % uid, lambda u=uid: owner_of(WORK, u))
        rec["owner_of_after"] = list(own) if own else None
        rec["owner_of_error"] = oerr
        fact("[2b] owner_of(%d) AFTER the move = %r (REPORTED ALONGSIDE the Nodes[] census, never instead "
             "of it - 53(d^8))" % (uid, own))
        _l2, rows2 = node_view(WORK, uid, after_hints, "[2b] #%d AFTER" % uid, quiet=True)
        rec["wired_after"] = wired_count(rows2)
        rec["n_terms_after"] = len(rows2)
        fact("[2b] #%d AFTER the move: %d terminal(s), %d WIRED (was %d)"
             % (uid, len(rows2), wired_count(rows2), rec["wired_before"]))
        rec["exec_state_after"] = unit_boundary("after move #%d %s" % (uid, name))
        K.setdefault("moves", []).append(rec)
        dump()
    final_uids, _ = body_a_node_uids("[2b] AFTER all seven")
    K["body_a_after_moves"] = final_uids
    missing = [u for u in SET_UIDS if u not in final_uids]
    K["moves_missing"] = missing
    fact("[2b] *** ALL SEVEN MOVED UIDS IN Diagram #%d's Nodes[]: %r (missing %r ; body holds %d) ***"
         % (BODY_A_UID, not missing, missing, len(final_uids)))
    K["counts_after_moves"] = counts(WORK, "[2b] after the seven moves")
    dump()
    return nodes, not missing, after_hints


# ================================================================ [2c] the seven internal rows
def one_row(nodes, hints, sink_uid, sink_name, sink_t, src_uid, src_name, src_t, why, tag, slot,
            src_hints=None):
    """ONE `connect_nested_v1` row, addressed off the machine at both ends and verified BY WIRE UID."""
    job = {"sink_uid": sink_uid, "sink_name": sink_name, "sink_t_recorded": sink_t,
           "src_uid": src_uid, "src_name": src_name, "src_t_recorded": src_t, "evidence": why}
    if left_s() < ROW_MIN_S:
        job["result"] = "NOT STARTED - only %.0f s left before the reserve" % left_s()
        fact("%s row #%d t%r <- #%d t%r: %s" % (tag, sink_uid, sink_t, src_uid, src_t, job["result"]))
        K.setdefault(slot, []).append(job)
        dump()
        return nodes, job
    sloc, srows = node_view(WORK, sink_uid, hints, "%s sink #%d" % (tag, sink_uid), quiet=True)
    rloc, rrows = node_view(WORK, src_uid, src_hints or hints, "%s src  #%d" % (tag, src_uid), quiet=True)
    job["sink_wired_before"] = wired_count(srows)
    job["src_wired_before"] = wired_count(rrows)
    job["sink_terminals_before"] = srows
    job["src_terminals_before"] = rrows
    si, show = resolve_term(srows, sink_name, sink_t, False, "%s sink #%d" % (tag, sink_uid))
    ri, rhow = resolve_term(rrows, src_name, src_t, True, "%s src #%d" % (tag, src_uid))
    job["sink_term_resolution"] = show
    job["src_term_resolution"] = rhow
    sd = (sloc.get("found") or {}).get("diagram_index")
    sn = (sloc.get("found") or {}).get("nodes_index")
    rd = (rloc.get("found") or {}).get("diagram_index")
    rn = (rloc.get("found") or {}).get("nodes_index")
    job["addr"] = {"sink_diag": sd, "sink_node": sn, "sink_term": si,
                   "src_diag": rd, "src_node": rn, "src_term": ri}
    job["same_nested_diagram"] = (sd is not None and sd == rd)
    fact("%s row #%d t%r <- #%d t%r : %r ; sink %s ; src %s ; same diagram %r"
         % (tag, sink_uid, si, src_uid, ri, job["addr"], show, rhow, job["same_nested_diagram"]))
    if None in (si, ri, sn, rn):
        job["result"] = "NOT ADDRESSABLE - one end did not resolve"
        fact("%s row #%d t%r <- #%d t%r: %s" % (tag, sink_uid, sink_t, src_uid, src_t, job["result"]))
        K.setdefault(slot, []).append(job)
        dump()
        return nodes, job
    try:
        dw, es, err = CONNECT_V1(WORK, sd, sn, si, rd, rn, ri, V1_LABELS)
        job["connect"] = {"wire_delta": dw, "exec_state": es, "machine_error": str(err)[:200]}
    except Exception as e:                                                        # noqa: BLE001
        job["connect"] = {"call_error": "%s: %s" % (type(e).__name__, str(e)[:250])}
        refusal("%s connect_nested_v1 row #%d t%r" % (tag, sink_uid, si), job["connect"]["call_error"])
    fact("%s connect_nested_v1 -> %r" % (tag, job["connect"]))
    nodes, _p = census_and_purge(WORK, nodes, "%s after row #%d t%r" % (tag, sink_uid, si), hints)
    _l3, srows2 = node_view(WORK, sink_uid, hints, "%s sink #%d AFTER" % (tag, sink_uid), quiet=True)
    _l4, rrows2 = node_view(WORK, src_uid, src_hints or hints, "%s src  #%d AFTER" % (tag, src_uid),
                            quiet=True)
    job["sink_wired_after"] = wired_count(srows2)
    job["src_wired_after"] = wired_count(rrows2)
    srow = next((t for t in srows2 if t["i"] == si), None)
    rrow = next((t for t in rrows2 if t["i"] == ri), None)
    job["same_wire_uid"] = bool(srow and rrow and srow["wire"] and srow["wire"] == rrow["wire"])
    job["wire_uid"] = (srow or {}).get("wire")
    job["landed"] = bool(srow and srow.get("wire")) and job["sink_wired_after"] > job["sink_wired_before"]
    fact("%s row #%d t%r <- #%d t%r : sink wire %r / src wire %r ; same net %r ; WIRED-TERMINAL counts "
         "sink %d -> %d, src %d -> %d ; LANDED %r"
         % (tag, sink_uid, si, src_uid, ri, (srow or {}).get("wire"), (rrow or {}).get("wire"),
            job["same_wire_uid"], job["sink_wired_before"], job["sink_wired_after"],
            job["src_wired_before"], job["src_wired_after"], job["landed"]))
    job["exec_state_after"] = unit_boundary("after row #%d t%r <- #%d t%r" % (sink_uid, si, src_uid, ri))
    K.setdefault(slot, []).append(job)
    dump()
    return nodes, job


def step_2_rows(nodes, hints):
    print("\n---------- [2c] THE SEVEN INTERNAL ROWS, VERBATIM FROM diag_c66b_s3b_m3.py", flush=True)
    for sink_uid, sink_name, sink_t, src_uid, src_name, src_t, why in INTERNAL_JOBS:
        nodes, _job = one_row(nodes, hints, sink_uid, sink_name, sink_t, src_uid, src_name, src_t, why,
                              "[2c]", "internal_rows")
    landed = sum(1 for j in K.get("internal_rows", []) if j.get("landed"))
    fact("[2c] INTERNAL ROWS LANDED: %d of %d" % (landed, len(INTERNAL_JOBS)))
    return nodes


# ======================================================= [3] two add_shift_reg pairs on #23032
def step_3_registers():
    print("\n---------- [3] TWO `add_shift_reg` PAIRS ON #%d, WITH THE CYCLE-67 REPAIRED WRAPPER"
          % LOOP_A_UID, flush=True)
    K["sr_counts_before_add"] = sr_counts(WORK, "[3] before the two add_shift_reg calls")
    made = {}
    for n, pair in enumerate(SR_PAIRS):
        li = loop_index_of(LOOP_A_UID, "[3] before add_shift_reg #%d (%s)" % (n + 1, pair))
        if li is None:
            made[pair] = {"right_uid": None, "error_verbatim": "no loop_index for #%d" % LOOP_A_UID}
            continue
        y = 120 + 90 * n
        uid, err = safe("[3] add_shift_reg(y=%d)" % y,
                        lambda ll=li, yy=y: g.add_shift_reg(WORK, ll, y_position=yy))
        if err:
            refusal("[3] add_shift_reg(%s pair)" % pair, err)
        fact("[3] add_shift_reg #%d for the %s pair at y=%d -> RightShiftRegister uid %r%s"
             % (n + 1, pair, y, uid, (" ; ERROR " + err) if err else ""))
        made[pair] = {"right_uid": uid, "y": y, "error_verbatim": err}
        made[pair]["sr_counts_after"] = sr_counts(WORK, "[3] after add_shift_reg #%d (%s)" % (n + 1, pair))
        made[pair]["exec_state_after"] = unit_boundary("after add_shift_reg #%d (%s pair)" % (n + 1, pair))
    fact("[3] NOTE FOR THE RECORD: both registers come back UNTYPED with BOTH SIDES UNWIRED, so `ExecState` "
         "0 from here on is CORRECT, NOT A FAILURE (tools/gscript.py:683-687). The names 'VISA' and 'POS' "
         "are THIS RUN'S assignment of a pair to a row set; the terminal NAMES read off the machine below "
         "are what justify each row's membership.")
    # THE reg_index <-> uid MAPPING IS READ, NEVER ASSUMED, and loop_cast's own list is read alongside.
    li = loop_index_of(LOOP_A_UID, "[3] before the reg_index readback")
    if li is not None:
        lc, lerr = safe("[3] loop_cast(index=%r)" % li, lambda: g.loop_cast(WORK, li, class_name="WhileLoop"))
        K["loop_cast_readback"] = {"loop_uid": (lc or {}).get("loop_uid"),
                                   "shift_reg_uids": (lc or {}).get("shift_reg_uids"),
                                   "errors": (lc or {}).get("errors"), "error_verbatim": lerr}
        fact("[3] *** loop_cast READBACK on #%d: loop_uid %r ; shift_reg_uids %r ; op errors %r%s ***"
             % (LOOP_A_UID, (lc or {}).get("loop_uid"), (lc or {}).get("shift_reg_uids"),
                (lc or {}).get("errors"), (" ; " + lerr) if lerr else ""))
        for pair in SR_PAIRS:
            if made.get(pair, {}).get("right_uid"):
                made[pair]["reg_index"] = reg_index_of(li, made[pair]["right_uid"], "[3] %s pair" % pair)
    fact("[3] MINTED: %r" % ({p: {"right_uid": made.get(p, {}).get("right_uid"),
                                  "reg_index": made.get(p, {}).get("reg_index")} for p in SR_PAIRS},))
    K["shift_registers"] = made
    K["counts_after_add"] = counts(WORK, "[3] after the two add_shift_reg calls")
    dump()
    return made


# ============================================================= [4] the four SR rows, RightIn first
def step_4_sr_rows(made, hints):
    print("\n---------- [4] THE FOUR SHIFT-REGISTER ROWS - RightIn BEFORE LeftIn (the sources type the "
          "register)", flush=True)
    for pair, variant, node_uid, term_name, term_i, node_is_source in SR_JOBS:
        job = {"pair": pair, "variant": variant, "node_uid": node_uid,
               "term_name_recorded": term_name, "term_index_recorded": term_i,
               "node_terminal_is_source": node_is_source,
               "reg_index": (made.get(pair) or {}).get("reg_index"),
               "right_reg_uid": (made.get(pair) or {}).get("right_uid")}
        if job["reg_index"] is None:
            job["result"] = "NO reg_index resolved in step [3] - the row is NOT attempted"
            fact("[4] %s %s row on #%d: %s" % (pair, variant, node_uid, job["result"]))
            K.setdefault("sr_rows", []).append(job)
            dump()
            continue
        bidx, berr = safe("[4] diag_index(#%d)" % BODY_A_UID, lambda: diag_index(WORK, BODY_A_UID))
        brows, lerr = safe("[4] node_labels(%r)" % bidx, lambda: g.node_labels(WORK, bidx), [])
        nidx = next((k for k, r in enumerate(brows or []) if r["uid"] == node_uid), None)
        job.update({"body_diagram_index": bidx, "body_nodes_index": nidx,
                    "body_nodes_len": len(brows or []), "addr_errors": [berr, lerr]})
        if nidx is None:
            job["result"] = "#%d IS NOT IN Diagram #%d's Nodes[] - the row is NOT attempted" \
                            % (node_uid, BODY_A_UID)
            fact("[4] %s %s: %s" % (pair, variant, job["result"]))
            K.setdefault("sr_rows", []).append(job)
            dump()
            continue
        tt = terms_at(WORK, bidx, nidx, node_uid, "[4] %s %s #%d" % (pair, variant, node_uid))
        rows = tt.get("terminals", [])
        job["node_terminals_before"] = rows
        ti, how = resolve_term(rows, term_name, term_i, node_is_source,
                               "[4] %s %s #%d" % (pair, variant, node_uid))
        job["term_resolution"] = how
        job["term_index_used"] = ti
        fact("[4] %s %s row: node #%d at Nodes[%r] of Diagram #%d [traverse %r], terminal %r resolved %s"
             % (pair, variant, node_uid, nidx, BODY_A_UID, bidx, ti, how))
        if ti is None:
            job["result"] = "TERMINAL UNRESOLVED - the row is NOT attempted"
            fact("[4] %s %s row on #%d: %s" % (pair, variant, node_uid, job["result"]))
            K.setdefault("sr_rows", []).append(job)
            dump()
            continue
        li = loop_index_of(LOOP_A_UID, "[4] before wire_sr(%s, %s)" % (variant, pair))
        if li is None:
            job["result"] = "NO loop_index for #%d - the row is NOT attempted" % LOOP_A_UID
            K.setdefault("sr_rows", []).append(job)
            dump()
            continue
        job["reg_uid_echo"] = echo_reg_uid(li, job["reg_index"], job["right_reg_uid"],
                                           "[4] before wire_sr(%s, %s)" % (variant, pair))
        nodes_before, _ = node_census(WORK, "[4] before wire_sr(%s, %s)" % (variant, pair))
        t0 = time.time()
        try:
            g.wire_sr(variant, WORK, li, job["reg_index"], node_index=nidx, term_index=ti)
            job["error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            job["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
            refusal("[4] wire_sr(%s, %s) on #%d t%r" % (variant, pair, node_uid, ti), job["error_verbatim"])
        job["call_cost_s"] = round(time.time() - t0, 2)
        fact("[4] wire_sr(%r, loop_index=%r, reg_index=%r, node_index=%r, term_index=%r) -> error %r (%.2f s)"
             % (variant, li, job["reg_index"], nidx, ti, job["error_verbatim"], job["call_cost_s"]))
        census_and_purge(WORK, nodes_before, "[4] after wire_sr(%s, %s)" % (variant, pair), hints)
        # VERIFY BY WIRE UID AT BOTH ENDS.
        tt2 = terms_at(WORK, bidx, nidx, node_uid, "[4] %s %s #%d AFTER" % (pair, variant, node_uid),
                       quiet=True)
        after_row = next((t for t in tt2.get("terminals", []) if t["i"] == ti), None)
        job["node_terminal_after"] = after_row
        node_wire = (after_row or {}).get("wire") or 0
        srl, serr = safe("[4] shift_reg_left after the row",
                         lambda: g.shift_reg_left(WORK, li, job["reg_index"], 0))
        job["register_after"] = srl
        job["register_read_error"] = serr
        if variant == "LeftIn":
            side = ((srl or {}).get("left") or {}).get("inside") or []
            side_label = "the LEFT register's INSIDE terminal"
        else:
            side = (srl or {}).get("inside") or []
            side_label = "the RIGHT register's INSIDE terminal"
        reg_wires = [t.get("wire") for t in side]
        job["register_side_wires"] = reg_wires
        job["node_wire_uid"] = node_wire
        job["landed"] = bool(node_wire) and node_wire in reg_wires
        fact("[4] *** %s %s row #%d t%r <-> reg_index %r: node terminal carries wire %r ; %s carries %r ; "
             "ONE NON-ZERO WIRE UID AT BOTH ENDS: %r ***"
             % (pair, variant, node_uid, ti, job["reg_index"], node_wire, side_label, reg_wires,
                job["landed"]))
        job["exec_state_after"] = unit_boundary("after the %s %s row on #%d" % (pair, variant, node_uid))
        K.setdefault("sr_rows", []).append(job)
        dump()
    landed = sum(1 for j in K.get("sr_rows", []) if j.get("landed"))
    fact("[4] SR ROWS LANDED: %d of %d" % (landed, len(SR_JOBS)))
    fact("[4] NOT CALLED, DELIBERATELY OUT OF SCOPE: wire_sr('LeftOutNode') and wire_sr('LeftOutCtl') - the "
         "registers' INITIAL VALUES are STAGE M3a-2. An uninitialised register is legal LabVIEW and the "
         "initial values are a rule-1a question, not a compile question.")


# ============================================================ [5] the fifth row, #10407 t1
def step_5_t1(nodes, hints):
    """THE FIFTH ROW, RE-CUT 2026-09-21 by the prior-art review's B3 `helper-exists`.

    WRITER: `connect_from_wire` = `OpConnectFromWire_v0.vi` (BUILT + SAVED 2026-09-17,
    docs/toolkit-capabilities.md:70) - the ONE writer whose SOURCE is a terminal of an existing WIRE rather
    than a `Nodes[]` entry. SOURCE = wire 9649's source terminal (`FlatSequenceInnerTunnel #9655`,
    tools/bench/diag_c67_addsr.log:395). SINK = `#10407` t1 `'# slices in stack'`.

    (i)  THE SOURCE IS MEASURED FIRST, ON THE LIVE TARGET. If the walk returns no source terminal, a FACT
         line is written and THE STEP STOPS: nothing is wired, nothing is substituted, no Local (rule 1a).
         Run 8's "w9649 has 0 source terminals" came from a reader that cannot address tunnels; this
         measurement is what decides, not that record.
    (ii) THE SINK INDEX IS RE-READ ON THE LIVE POST-MOVE TARGET here, never carried from the pre-move
         census - the recorded cause of T2c2's broken wire.
    ACCEPTANCE, **REPLACED 2026-09-21 BY PRE-DECIDED 70**: the test is OBJECT IDENTITY, in run, immediately
    after the write and again after the junk purge - the SAME `LoopTunnel` uid T must be a NEW SINK terminal
    on the SOURCE wire and the ONE SOURCE terminal of the NEW SINK wire (`identity_gate`). `wire_delta == 3`,
    "two DIFFERENT wire uids" and `Wire.Is Broken? False` are WITHDRAWN as acceptance - all three are read on
    the SINK side only - and are kept as FACT lines. `ExecState` is NEVER substituted for the identity test.
    """
    print("\n---------- [5] THE FIFTH ROW: #%d t%d %r, VIA `connect_from_wire` OFF WIRE %d"
          % (CASE_UID, T1_TERM_INDEX, T1_TERM_NAME, T1_OUTER_WIRE), flush=True)
    rec = {"writer": "connect_from_wire / OpConnectFromWire_v0.vi (docs/toolkit-capabilities.md:70)",
           "source_wire": T1_OUTER_WIRE, "source_owner_recorded": T1_OUTER_SOURCE,
           "acceptance": "A3 BORDER ROW: wire_delta == %d, TWO DIFFERENT wire uids at the two ends, "
                         "Is Broken? False. The one-uid-at-both-ends check is NOT applied here."
                         % T1_BORDER_WIRE_DELTA,
           "never_a_local": "A Local is NEVER substituted for this row (rule 1a)."}

    # ---- (i) MEASURE THE SOURCE ON THE LIVE TARGET, IMMEDIATELY BEFORE THE WRITE
    walk, werr = safe("[5] wire_source_owner(%d) on the LIVE target" % T1_OUTER_WIRE,
                      lambda: WIRE_TERMS(WORK, T1_OUTER_WIRE), [])
    rec["source_walk"] = walk
    rec["source_walk_error"] = werr
    src = next((t for t in (walk or [])
                if t.get("is_source") and t.get("owner_uid") and t.get("recip") == T1_OUTER_WIRE), None)
    rec["source_terminal"] = src
    fact("[5] (i) SOURCE MEASURED ON THE LIVE TARGET: wire %d Terms[] walk %r -> SOURCE endpoint %r%s"
         % (T1_OUTER_WIRE, walk, src, (" ; " + werr) if werr else ""))
    # PRE-DECIDED 70/71: the SOURCE-wire read IMMEDIATELY BEFORE the border write, terminal by terminal.
    src_before = print_walk("[5] (a) SOURCE WIRE %d IMMEDIATELY BEFORE THE t1 BORDER WRITE" % T1_OUTER_WIRE,
                            T1_OUTER_WIRE, walk, werr)
    rec["source_walk_before"] = src_before
    if not src:
        rec["result"] = ("STEP STOPPED - wire %d came back with NO source terminal on the live target. "
                         "Nothing is wired, nothing is substituted." % T1_OUTER_WIRE)
        fact("[5] *** %s This is the precaution the prior-art review required, not a machine refusal: the "
             "run carries on to the census and the row is reported OPEN. ***" % rec["result"])
        K["t1_row"] = rec
        dump()
        return nodes, rec
    src_i = src["i"]
    rec["source_term_index"] = src_i
    rec["source_owner_matches_the_record"] = (src.get("owner_uid") == T1_OUTER_SOURCE)
    fact("[5] (i) source terminal index %r, owner #%r %r (recorded owner #%d ; match %r)"
         % (src_i, src.get("owner_uid"), src.get("owner_class"), T1_OUTER_SOURCE,
            rec["source_owner_matches_the_record"]))

    # ---- (ii) RE-READ THE SINK ON THE LIVE POST-MOVE TARGET (T2c2's cause of failure)
    sloc, srows = node_view(WORK, CASE_UID, hints, "[5] sink #%d LIVE" % CASE_UID, quiet=True)
    sd = (sloc.get("found") or {}).get("diagram_index")
    sn = (sloc.get("found") or {}).get("nodes_index")
    si, show = resolve_term(srows, T1_TERM_NAME, T1_TERM_INDEX, False, "[5] sink #%d" % CASE_UID)
    sink_before = next((t for t in srows if t["i"] == si), None)
    rec["sink_addr"] = {"diagram_index": sd, "nodes_index": sn, "term_index": si}
    rec["sink_term_resolution"] = show
    rec["sink_terminal_before"] = sink_before
    rec["sink_wired_before"] = wired_count(srows)
    fact("[5] (ii) SINK RE-READ ON THE LIVE POST-MOVE TARGET: #%d at Diagram idx %r Nodes[%r], terminal "
         "%r resolved %s ; it currently carries wire %r (NEVER carried from the pre-move census - T2c2)"
         % (CASE_UID, sd, sn, si, show, (sink_before or {}).get("wire")))
    if None in (sd, sn, si):
        rec["result"] = "STEP STOPPED - the sink did not resolve on the live target"
        fact("[5] *** %s. Nothing is wired, nothing is substituted. ***" % rec["result"])
        K["t1_row"] = rec
        dump()
        return nodes, rec

    # ---- the baselines the border measurement is read against
    before = {}
    for c in ("LoopTunnel", "Tunnel", "Wire"):
        before[c], _ = safe("[5] count(%r) before" % c, lambda cc=c: g.count(WORK, cc))
    _lloc, lrows = node_view(WORK, LOOP_A_UID, hints, "[5] #%d before" % LOOP_A_UID, quiet=True)
    before["loop_%d_terminals" % LOOP_A_UID] = len(lrows)
    rec["counts_before"] = before
    fact("[5] baselines before the write: %r" % (before,))
    nodes_before, _ = node_census(WORK, "[5] before connect_from_wire")

    # ---- THE WRITE
    t0 = time.time()
    try:
        dw, es, err, sub = CONNECT_FROM_WIRE(WORK, T1_OUTER_WIRE, src_i, sd, sn, si, CFW_LABELS)
        rec["connect"] = {"wire_delta": dw, "exec_state": es, "op_error": str(err)[:250],
                          "op_readback": sub}
    except Exception as e:                                                         # noqa: BLE001
        rec["connect"] = {"call_error": "%s: %s" % (type(e).__name__, str(e)[:250])}
        refusal("[5] connect_from_wire(wire %d t%r -> #%d t%r)" % (T1_OUTER_WIRE, src_i, CASE_UID, si),
                rec["connect"]["call_error"])
    rec["call_cost_s"] = round(time.time() - t0, 2)
    fact("[5] connect_from_wire(wire=%d, wire_term=%r, sink_diag=%r, sink_node=%r, sink_term=%r) -> %r "
         "(%.2f s)" % (T1_OUTER_WIRE, src_i, sd, sn, si, rec["connect"], rec["call_cost_s"]))

    # ---- PRE-DECIDED 70/71: THE IDENTITY READ, IMMEDIATELY AFTER THE WRITE AND **BEFORE THE JUNK PURGE**
    # (the purge deletes a node that last run carried the SOURCE WIRE'S OWN uid, so the state has to be
    #  measured on either side of it - never only after).
    lt_now, _lterr = safe("[5] count('LoopTunnel') immediately after the write",
                          lambda: g.count(WORK, "LoopTunnel"))
    rec["loop_tunnel_immediately_after_write"] = lt_now
    lt_delta = (lt_now or 0) - (before.get("LoopTunnel") or 0)
    rec["loop_tunnel_delta"] = lt_delta
    fact("[5] (a) LoopTunnel %r -> %r (delta %r): this write %s a LoopTunnel"
         % (before.get("LoopTunnel"), lt_now, lt_delta, "CREATED" if lt_delta > 0 else "did NOT create"))
    src_after, _e1 = wire_walk("[5] (a) SOURCE WIRE %d IMMEDIATELY AFTER THE WRITE, BEFORE THE PURGE"
                               % T1_OUTER_WIRE, T1_OUTER_WIRE)
    rec["source_walk_immediately_after"] = src_after
    _sl1, srows1 = node_view(WORK, CASE_UID, hints, "[5] sink #%d immediately after" % CASE_UID, quiet=True)
    sink_now = next((t for t in srows1 if t["i"] == si), None)
    sink_wire_now = (sink_now or {}).get("wire") or 0
    rec["sink_wire_immediately_after"] = sink_wire_now
    fact("[5] (a) the sink terminal #%d t%r carries wire %r immediately after the write (last run's `UID 2` "
         "readback was %d - RECORDED, never carried)" % (CASE_UID, si, sink_wire_now, T1_RECORDED_SINK_WIRE))
    sink_walk1, _e2 = wire_walk("[5] (a) SINK WIRE %r IMMEDIATELY AFTER THE WRITE" % sink_wire_now,
                                sink_wire_now)
    rec["sink_walk_immediately_after"] = sink_walk1
    rec["identity_immediately_after"] = identity_gate(
        "[5](a) the t1 border row, immediately after the write", T1_OUTER_WIRE, src_before, src_after,
        sink_wire_now, sink_walk1, mandatory=True)

    nodes, _p = census_and_purge(WORK, nodes_before, "[5] after the t1 row", hints)
    # ---- PRE-DECIDED 71: WAS A LIVE OBJECT'S uid RE-USED BY THE OBJECT THIS CALL MINTED?
    rec["minted_uids"] = (_p or {}).get("new_uids")
    minted = [int(u) for u, _c, _pos in ((_p or {}).get("new_uids") or [])]
    rec["minted_uid_equals_the_live_source_wire_uid"] = (T1_OUTER_WIRE in minted)
    fact("[5] *** PRE-DECIDED 71 MEASUREMENT: the call MINTED %r ; the op's own `UID 2` readback (the wire "
         "it created at the sink) is %r ; MINTED UID == THE LIVE SOURCE WIRE UID %d : %r. Last run the junk "
         "`Invoke` carried %d - the source wire's own uid - while every other object created took a "
         "monotonic uid in the 23,800-24,009 band. This FACT never gates the run. ***"
         % (rec["minted_uids"], ((rec.get("connect") or {}).get("op_readback") or {}).get("UID 2"),
            T1_OUTER_WIRE, rec["minted_uid_equals_the_live_source_wire_uid"], T1_RECORDED_MINTED_UID))

    # ---- THE BORDER-ROW ACCEPTANCE (A3), READ OFF THE MACHINE
    _sl2, srows2 = node_view(WORK, CASE_UID, hints, "[5] sink #%d AFTER" % CASE_UID, quiet=True)
    sink_after = next((t for t in srows2 if t["i"] == si), None)
    sink_wire = (sink_after or {}).get("wire") or 0
    walk2, werr2 = safe("[5] wire_source_owner(%d) AFTER" % T1_OUTER_WIRE,
                        lambda: WIRE_TERMS(WORK, T1_OUTER_WIRE), [])
    rec["source_walk_after"] = walk2
    src_side_wire = T1_OUTER_WIRE
    after = {}
    for c in ("LoopTunnel", "Tunnel", "Wire"):
        after[c], _ = safe("[5] count(%r) after" % c, lambda cc=c: g.count(WORK, cc))
    _lloc2, lrows2 = node_view(WORK, LOOP_A_UID, hints, "[5] #%d after" % LOOP_A_UID, quiet=True)
    after["loop_%d_terminals" % LOOP_A_UID] = len(lrows2)
    rec["counts_after"] = after
    rec["sink_terminal_after"] = sink_after
    rec["sink_wire_uid"] = sink_wire
    rec["source_side_wire_uid"] = src_side_wire
    rec["sink_wired_after"] = wired_count(srows2)
    # ---- PRE-DECIDED 70 AGAIN, ON THE STATE THE ARTEFACT WOULD ACTUALLY KEEP: after the junk purge.
    print_walk("[5] (b) SOURCE WIRE %d AFTER THE JUNK PURGE" % T1_OUTER_WIRE, T1_OUTER_WIRE, walk2, werr2)
    sink_walk2, _e3 = wire_walk("[5] (b) SINK WIRE %r AFTER THE JUNK PURGE" % sink_wire, sink_wire)
    rec["sink_walk_after_purge"] = sink_walk2
    rec["identity_after_purge"] = identity_gate(
        "[5](b) the t1 border row, after the junk purge", T1_OUTER_WIRE, src_before, walk2 or [],
        sink_wire, sink_walk2, mandatory=True)
    dw = (rec.get("connect") or {}).get("wire_delta")
    is_broken = ((rec.get("connect") or {}).get("op_readback") or {}).get("Is Broken?")
    rec["wire_delta"] = dw
    rec["is_broken"] = is_broken
    rec["two_different_wire_uids"] = bool(sink_wire) and sink_wire != src_side_wire
    rec["landed"] = bool(sink_wire) and rec["sink_wired_after"] > rec["sink_wired_before"]
    fact("[5] *** BORDER-ROW REPORT - A3 IS WITHDRAWN AS AN ACCEPTANCE TEST BY PRE-DECIDED 70 AND THESE "
         "FOUR NUMBERS ARE NOW FACT LINES ONLY; the acceptance test is the A3-ID identity gate above: "
         "wire_delta %r (the old expectation was %d) ; SOURCE-side wire %r vs SINK-side "
         "wire %r -> TWO DIFFERENT uids %r ; `Wire.Is Broken?` %r ; sink WIRED-terminal count %d -> %d ; "
         "LANDED %r ***"
         % (dw, T1_BORDER_WIRE_DELTA, src_side_wire, sink_wire, rec["two_different_wire_uids"], is_broken,
            rec["sink_wired_before"], rec["sink_wired_after"], rec["landed"]))
    fact("[5] THE ONE-WIRE-UID-AT-BOTH-ENDS CHECK IS DELIBERATELY NOT APPLIED TO THIS ROW: LabVIEW "
         "auto-tunnels #%d's border (docs/toolkit-capabilities.md:68, docs/cycle27-plan.md:2477-2479), so "
         "a CORRECT border wire reads TWO different uids. Same-diagram rows keep that check unchanged."
         % LOOP_A_UID)
    fact("[5] *** THE AUTO-TUNNEL MEASUREMENT: before %r -> after %r%s ***"
         % (before, after, (" ; walk error " + werr2) if werr2 else ""))
    rec["exec_state_after"] = unit_boundary("after the t1 row #%d t%r" % (CASE_UID, si))
    K["t1_row"] = rec
    dump()
    return nodes, rec


# ============================ [5b] THE SIXTH ROW - `Q_focusback` SelectorTunnel #12673 (Pre-decided 72)
def step_6_sixth_row(nodes, hints):
    """THE SIXTH ROW, WIRED **BEFORE** THE CENSUS SO THE A4 BARE-SINK GATE JUDGES THE FINISHED STAGE.

    A4 fired on its first run (`tools/bench/build_d1_m3a1.log:548-552`): `#10407` t6's SECOND consumer,
    `Q_focusback` `SelectorTunnel #12673`, was left bare - a dropped consumer, i.e. a rule-1a change of
    computation. Pre-decided 72 dissolves the "no reader this fleet owns can address a tunnel" blocker: a
    tunnel is not a `Nodes[]` entry, but its terminal IS an entry in its OWNING STRUCTURE NODE's Terms[].

    THE ROUTE, EXACTLY, AND NOTHING ELSE:
      (1) the OWNER CHAIN of #12673 (`OpOwnerChain_v1` through `owner_of(..., strict=True)`, whose identity
          echo is what makes the reader trustworthy - 53(d^8)) up to its owning **Case Structure**;
      (2) that NODE's `Terms[]`, and the entry that **EXPOSES UID 12673** - never a carried index (the
          recorded cause of T2c2's broken wire) and never a guessed NAME (FIX 1: `Q_focusback` is a FUTURE
          QUEUE name, `docs/d1-build-plan.md:576`, and the measured terminal names of the owning node are
          "", "position [internal units]", "" - `tools/bench/main_vi_nodeterms.json:14287-14313`). Each
          entry's uid comes from `OpWireSource_v5` on the wire that entry carries, the only uid-bearing
          walk this fleet owns for a terminal; an entry with no wire exposes no uid and FAILS the row;
      (3) `connect_from_wire` with SOURCE = t6's **LIVE** net, RE-MEASURED here. The recorded value is
          23963 (build_d1_m3a1.log:548), NOT the 9113 the row inventory names - and even 23963 is a uid
          THIS BUILD MINTS, so it is compared against the live read, never used in its place.
    HAZARDS HANDLED RATHER THAN HOPED PAST: an owner chain terminates SILENTLY at a `FlatSequenceFrame`. If
    the chain does not reach a Case Structure, or the by-name entry is not in its Terms[], a FACT line names
    exactly what the walk returned and the ROW FAILS. **NO FALLBACK IS IMPROVISED.** `Outside Terminal` is
    UNBUILT, its short name would have to be read off the machine, and it is OUT OF SCOPE for this run: an
    unbuilt property added mid-build has not been through this cycle's prior-art review.
    """
    print("\n---------- [5b] THE SIXTH ROW: SelectorTunnel #%d (row label `%s`) <- #%d t%d %r, VIA "
          "`connect_from_wire` OFF t6's LIVE NET"
          % (T6_SECOND_SINK, T6_SIXTH_SINK_LABEL, CASE_UID, T6_TERM_INDEX, T6_TERM_NAME), flush=True)
    rec = {"sink_uid": T6_SECOND_SINK, "sink_class_recorded": "SelectorTunnel",
           "sink_row_label_LOG_TEXT_ONLY": T6_SIXTH_SINK_LABEL,
           "source_node": CASE_UID, "source_term_name": T6_TERM_NAME,
           "source_term_index_recorded": T6_TERM_INDEX, "live_net_recorded": T6_LIVE_NET_RECORDED,
           "original_net": T6_ORIGINAL_NET, "addressed": False, "landed": False,
           "no_fallback": "`Outside Terminal` is UNBUILT and OUT OF SCOPE for this run; no fallback is "
                          "improvised and no Local is ever substituted (rule 1a).",
           "evidence": "docs/cycle27-plan.md:2866-2876 (Pre-decided 72); "
                       "tools/bench/build_d1_m3a1.log:548-552"}
    K["sixth_row"] = rec
    if left_s() < ROW_MIN_S:
        rec["result"] = "NOT STARTED - only %.0f s left before the reserve" % left_s()
        fact("[5b] %s" % rec["result"])
        dump()
        return nodes, rec

    # ---- (1) THE OWNER CHAIN OF #12673, HOP BY HOP, EACH HOP ECHO-CHECKED (owner_of strict=True)
    chain, cur, case_uid = [], T6_SECOND_SINK, None
    for hop in range(T6_OWNER_HOPS):
        own, oerr = safe("[5b] owner_of(#%d) hop %d" % (cur, hop + 1),
                         lambda u=cur: owner_of(WORK, u, strict=True))
        row = {"hop": hop + 1, "uid": cur, "owner_class": (own[0] if own else None),
               "owner_uid": (own[1] if own else None), "error_verbatim": oerr}
        chain.append(row)
        fact("[5b] OWNER CHAIN hop %d: #%s -> owner_class %r owner_uid %r%s"
             % (hop + 1, cur, row["owner_class"], row["owner_uid"], (" ; " + oerr) if oerr else ""))
        if not own or not own[1]:
            break
        if str(own[0]) == "CaseStructure":
            case_uid = int(own[1])
            break
        cur = int(own[1])
    rec["owner_chain"] = chain
    rec["case_structure_uid"] = case_uid
    # ---- FIX 1 (b): THE MEASURED OWNER UID IS A **FACT**, COMPARED AGAINST THE CENSUS, NEVER A GATE.
    rec["owner_uid_equals_the_recorded_12589"] = (case_uid == T6_OWNER_CASE_RECORDED)
    fact("[5b] FIX 1(b) FACT, NOT A GATE: the MEASURED owning Case Structure uid is %r ; the recorded census "
         "value is %d (tools/bench/main_vi_nodeterms.json:14287) ; EQUAL %r. THE MEASUREMENT GOVERNS - a "
         "mismatch is reported and the walk below still decides the row."
         % (case_uid, T6_OWNER_CASE_RECORDED, rec["owner_uid_equals_the_recorded_12589"]))
    if case_uid is None:
        rec["result"] = ("THE OWNER CHAIN OF #%d DID NOT REACH A CaseStructure IN %d HOP(S). WHAT THE WALK "
                         "RETURNED, VERBATIM: %r. An owner chain terminates silently at a FlatSequenceFrame "
                         "(docs/d1-build-plan.md:912), so this is a MEASURED outcome, not an error."
                         % (T6_SECOND_SINK, T6_OWNER_HOPS, chain))
        fact("[5b] *** %s NOTHING IS WIRED AND NO FALLBACK IS IMPROVISED. ***" % rec["result"])
        gate("A5 the sixth row is ADDRESSABLE: #%d's owner chain reaches a Case Structure one of whose "
             "Terms[] entries EXPOSES UID %d" % (T6_SECOND_SINK, T6_SECOND_SINK), False,
             "owner chain %r" % (chain,))
        dump()
        return nodes, rec

    # ---- (2) FIX 1 (c): THAT NODE'S Terms[], AND THE ENTRY THAT **EXPOSES UID 12673** - NOT A NAME, NOT
    #      A CARRIED INDEX. Each entry's uid is resolved through the wire it carries, because `node_terms`
    #      returns no per-terminal uid and no reader this fleet owns does (tools/gscript.py:931-937;
    #      docs/toolkit-capabilities.md:60-61 - the only uid-bearing walks are OpWireSource_v5 on a WIRE
    #      and OpOwnerChain_v1 on an object). An entry carrying NO wire exposes NO uid: per (e) that is a
    #      MEASURED failure of the row, never an occasion to guess.
    cloc, crows = node_view(WORK, case_uid, hints, "[5b] the owning CaseStructure #%d" % case_uid)
    cd = (cloc.get("found") or {}).get("diagram_index")
    cn = (cloc.get("found") or {}).get("nodes_index")
    rec["case_structure_found"] = cloc.get("found")
    rec["case_structure_n_terminals"] = len(crows)
    exposure = []
    for t in crows:
        w = t.get("wire") or 0
        walk, werr = (([], "") if not w else wire_walk(
            "[5b] (2) Terms[t%r] of #%d carries wire %r" % (t.get("i"), case_uid, w), w))
        owners = sorted({int(x["owner_uid"]) for x in (walk or []) if x.get("owner_uid")})
        exposure.append({"i": t.get("i"), "name": t.get("name"), "is_source": t.get("is_source"),
                         "wire": w, "exposed_owner_uids": owners, "walk_error": werr})
        fact("[5b] (2) ENTRY t%-2r name %-30r is_source %-5r wire %-7r EXPOSES owner uid(s) %r%s"
             % (t.get("i"), t.get("name"), t.get("is_source"), w, owners,
                (" ; " + werr) if werr else ""))
    rec["terms_exposure"] = exposure
    matches = [e for e in exposure if T6_SECOND_SINK in (e["exposed_owner_uids"] or [])]
    rec["uid_matches"] = matches
    hit, how = None, ""
    if len(matches) == 1:
        hit = next((t for t in crows if t["i"] == matches[0]["i"]), None)
        how = ("BY UID - Terms[t%r] of #%d is the ONE entry exposing uid %d (its wire %r carries a terminal "
               "owned by #%d)" % (matches[0]["i"], case_uid, T6_SECOND_SINK, matches[0]["wire"],
                                  T6_SECOND_SINK))
    elif len(matches) > 1:
        sinks = [e for e in matches if e["is_source"] is False]
        if len(sinks) == 1:
            hit = next((t for t in crows if t["i"] == sinks[0]["i"]), None)
            how = ("BY UID - %d entries expose uid %d and exactly ONE of them is a SINK (t%r)"
                   % (len(matches), T6_SECOND_SINK, sinks[0]["i"]))
    if hit is None or None in (cd, cn):
        rec["result"] = ("NO ENTRY OF CaseStructure #%s's Terms[] EXPOSES UID %d: %d terminal(s) read, %d "
                         "uid match(es), node located at %r. WHAT THE WALK RETURNED, ENTRY BY ENTRY: %r"
                         % (case_uid, T6_SECOND_SINK, len(crows), len(matches), cloc.get("found"),
                            exposure))
        fact("[5b] *** %s NOTHING IS WIRED AND NO FALLBACK IS IMPROVISED - `Outside Terminal` IS UNBUILT "
             "AND OUT OF SCOPE FOR THIS RUN, AND THE DELETED BY-NAME LOOKUP IS NOT REINSTATED (FIX 1). ***"
             % rec["result"])
        gate("A5 the sixth row is ADDRESSABLE: #%d's owner chain reaches a Case Structure one of whose "
             "Terms[] entries EXPOSES UID %d" % (T6_SECOND_SINK, T6_SECOND_SINK), False,
             "CaseStructure #%r ; %d terminal(s) ; exposure %r" % (case_uid, len(crows), exposure))
        dump()
        return nodes, rec
    rec["sink_addr"] = {"diagram_index": cd, "nodes_index": cn, "term_index": hit["i"]}
    rec["sink_term_resolution"] = how
    rec["sink_terminal_before"] = hit
    rec["sink_wired_before"] = wired_count(crows)
    # ---- FIX 1 (d): THE RESOLVED ENTRY'S **NAME** IS A FACT, COMPARED, NEVER A GATE.
    rec["resolved_term_name"] = hit.get("name")
    rec["resolved_term_name_equals_the_recorded_one"] = (hit.get("name") == T6_OWNER_TERM_NAME_RECORDED)
    fact("[5b] FIX 1(d) FACT, NOT A GATE: the resolved entry's NAME is %r ; the recorded census value is %r "
         "(tools/bench/main_vi_nodeterms.json:14304) ; EQUAL %r. The row label %r is a FUTURE QUEUE name "
         "(docs/d1-build-plan.md:576) and is on NO lookup path (FIX 1)."
         % (hit.get("name"), T6_OWNER_TERM_NAME_RECORDED,
            rec["resolved_term_name_equals_the_recorded_one"], T6_SIXTH_SINK_LABEL))
    fact("[5b] (2) SINK RESOLVED %s ; CaseStructure #%d at Diagram idx %r Nodes[%r], terminal t%d, "
         "is_source %r, it currently carries wire %r (NEVER a carried index - T2c2)"
         % (how, case_uid, cd, cn, hit["i"], hit.get("is_source"), hit.get("wire")))

    # ---- (3) THE SOURCE: #10407 t6's **LIVE** net, RE-MEASURED HERE
    sloc, srows = node_view(WORK, CASE_UID, hints, "[5b] source #%d" % CASE_UID, quiet=True)
    ti, thow = resolve_term(srows, T6_TERM_NAME, T6_TERM_INDEX, True, "[5b] source #%d" % CASE_UID)
    trow = next((t for t in srows if t["i"] == ti), None) if ti is not None else None
    live_net = (trow or {}).get("wire") or 0
    rec["source_term_index_used"] = ti
    rec["source_term_resolution"] = thow
    rec["live_net"] = live_net
    rec["live_net_equals_the_recorded_one"] = (live_net == T6_LIVE_NET_RECORDED)
    fact("[5b] (3) #%d t%r %r resolved %s ; ITS LIVE NET IS %r (last run's was %d ; equal %r). The LIVE "
         "value is what is used - this uid is minted by THIS build, so the recorded one is only compared."
         % (CASE_UID, ti, T6_TERM_NAME, thow, live_net, T6_LIVE_NET_RECORDED,
            rec["live_net_equals_the_recorded_one"]))
    src_before, swerr = wire_walk("[5b] (3) t6's LIVE net %r BEFORE the write" % live_net, live_net)
    src = next((t for t in src_before
                if t.get("is_source") and t.get("owner_uid") and t.get("recip") == live_net), None)
    rec["source_walk_before"] = src_before
    rec["source_terminal"] = src
    if not live_net or not src:
        rec["result"] = ("#%d t%r CARRIES NET %r AND ITS Terms[] WALK RETURNED NO SOURCE ENDPOINT: %r%s. "
                         "Nothing is wired, nothing is substituted."
                         % (CASE_UID, ti, live_net, src_before, (" ; " + swerr) if swerr else ""))
        fact("[5b] *** %s ***" % rec["result"])
        gate("A5 the sixth row is ADDRESSABLE: #%d's owner chain reaches a Case Structure one of whose "
             "Terms[] entries EXPOSES UID %d" % (T6_SECOND_SINK, T6_SECOND_SINK), False,
             "the SOURCE side did not resolve: live net %r, walk %r" % (live_net, src_before))
        dump()
        return nodes, rec
    rec["addressed"] = True
    gate("A5 the sixth row is ADDRESSABLE: #%d's owner chain reaches a Case Structure one of whose "
         "Terms[] entries EXPOSES UID %d" % (T6_SECOND_SINK, T6_SECOND_SINK), True,
         "CaseStructure #%d, Diagram idx %r Nodes[%r], t%d ; source net %r t%r"
         % (case_uid, cd, cn, hit["i"], live_net, src["i"]))

    # ---- THE WRITE
    lt_before, _lb = safe("[5b] count('LoopTunnel') before", lambda: g.count(WORK, "LoopTunnel"))
    rec["loop_tunnel_before"] = lt_before
    nodes_before, _ = node_census(WORK, "[5b] before connect_from_wire")
    t0 = time.time()
    try:
        dw, es, err, sub = CONNECT_FROM_WIRE(WORK, live_net, src["i"], cd, cn, hit["i"], CFW_LABELS)
        rec["connect"] = {"wire_delta": dw, "exec_state": es, "op_error": str(err)[:250], "op_readback": sub}
    except Exception as e:                                                         # noqa: BLE001
        rec["connect"] = {"call_error": "%s: %s" % (type(e).__name__, str(e)[:250])}
        refusal("[5b] connect_from_wire(wire %r t%r -> CaseStructure #%d t%d)"
                % (live_net, src["i"], case_uid, hit["i"]), rec["connect"]["call_error"])
    rec["call_cost_s"] = round(time.time() - t0, 2)
    fact("[5b] connect_from_wire(wire=%r, wire_term=%r, sink_diag=%r, sink_node=%r, sink_term=%r) -> %r "
         "(%.2f s)" % (live_net, src["i"], cd, cn, hit["i"], rec["connect"], rec["call_cost_s"]))

    # ---- PRE-DECIDED 70's IDENTITY READ, IMMEDIATELY AFTER THE WRITE AND BEFORE THE JUNK PURGE
    lt_after, _la = safe("[5b] count('LoopTunnel') immediately after the write",
                         lambda: g.count(WORK, "LoopTunnel"))
    rec["loop_tunnel_immediately_after_write"] = lt_after
    lt_delta = (lt_after or 0) - (lt_before or 0)
    rec["loop_tunnel_delta"] = lt_delta
    fact("[5b] LoopTunnel %r -> %r (delta %r): this write %s a LoopTunnel, so Pre-decided 70's identity "
         "gate %s to it"
         % (lt_before, lt_after, lt_delta, "CREATED" if lt_delta > 0 else "did NOT create",
            "APPLIES" if lt_delta > 0 else "does NOT apply - it is not a border write"))
    src_after, _e1 = wire_walk("[5b] SOURCE net %r IMMEDIATELY AFTER THE WRITE, BEFORE THE PURGE"
                               % live_net, live_net)
    rec["source_walk_immediately_after"] = src_after
    _c2, crows2 = node_view(WORK, case_uid, hints, "[5b] sink CaseStructure #%d AFTER" % case_uid,
                            quiet=True)
    sink_after = next((t for t in crows2 if t["i"] == hit["i"]), None)
    sink_wire = (sink_after or {}).get("wire") or 0
    rec["sink_terminal_after"] = sink_after
    rec["sink_wire_uid"] = sink_wire
    rec["sink_wired_after"] = wired_count(crows2)
    sink_walk, _e2 = wire_walk("[5b] SINK WIRE %r IMMEDIATELY AFTER THE WRITE" % sink_wire, sink_wire)
    rec["sink_walk"] = sink_walk
    rec["identity"] = identity_gate("[5b] the sixth row", live_net, src_before, src_after, sink_wire,
                                    sink_walk, mandatory=(lt_delta > 0))
    nodes, _p = census_and_purge(WORK, nodes_before, "[5b] after the sixth row", hints)
    rec["minted_uids"] = (_p or {}).get("new_uids")
    minted = [int(u) for u, _c3, _p3 in ((_p or {}).get("new_uids") or [])]
    rec["minted_uid_equals_the_live_source_wire_uid"] = (live_net in minted)
    fact("[5b] PRE-DECIDED 71 MEASUREMENT: the call MINTED %r ; `UID 2` readback %r ; MINTED UID == THE "
         "LIVE SOURCE NET %r : %r. This FACT never gates the run."
         % (rec["minted_uids"], ((rec.get("connect") or {}).get("op_readback") or {}).get("UID 2"),
            live_net, rec["minted_uid_equals_the_live_source_wire_uid"]))
    rec["landed"] = bool(sink_wire) and rec["sink_wired_after"] > rec["sink_wired_before"]
    fact("[5b] *** THE SIXTH ROW: sink terminal t%d of CaseStructure #%d carries wire %r ; CaseStructure "
         "WIRED-terminal count %d -> %d ; `Wire.Is Broken?` %r ; LANDED %r. THE DECIDING GATE IS A4 BELOW, "
         "WHICH RE-READS #%d t%d's NET AND LOOKS FOR #%d ON IT. ***"
         % (hit["i"], case_uid, sink_wire, rec["sink_wired_before"], rec["sink_wired_after"],
            ((rec.get("connect") or {}).get("op_readback") or {}).get("Is Broken?"), rec["landed"],
            CASE_UID, T6_TERM_INDEX, T6_SECOND_SINK))
    rec["exec_state_after"] = unit_boundary("after the sixth row SelectorTunnel #%d (row label `%s`)"
                                            % (T6_SECOND_SINK, T6_SIXTH_SINK_LABEL))
    dump()
    return nodes, rec


# ============================================= [6b] A4, THE BARE-SINK GATE (prior-art review, 2026-09-21)
def bare_sink_gate(hints):
    """`#10407` t6 `'position [internal units]'` has TWO sinks in the original, on net 9113: the
    `RightShiftRegister #4256` this build re-creates AND `Q_focusback` `SelectorTunnel #12673`
    (tools/bench/diag_c67_addsr.log:389). This build re-created ONE. Dropping a downstream consumer is a
    CHANGE OF COMPUTATION (rule 1a) and it would pass SILENTLY, because a bare source is legal LabVIEW.

    A SelectorTunnel is not a `Nodes[]` entry, so it cannot be read with `node_terms`; what IS readable
    is the wire the CONSUMER's own Terms[] entry carries, walked by uid with `wire_source_owner`.

    *** FIX 3, 2026-09-21 - THE GATE ANCHORS AT THE CONSUMER AND NEEDS ZERO HOPS (Pre-decided 90,
    docs/cycle27-plan.md:3084-3089; it AMENDS FIX 2's two-branch outward walk, whose BORDER branch was
    an unbounded search with no failure mode - "which is how `wire_delta==3` died"). The failed-
    prediction review measured that #12673 is already a SINK of a wire whose single source is the
    border LoopTunnel (`build_d1_m3a1.log:1151-1155`) - so start FROM THE CONSUMER: [5b] resolved the
    owner node (#12589's measured uid) and the Terms[] entry that EXPOSES uid 12673; A4 re-reads THAT
    entry's wire live and walks ONE wire. PASS requires ALL of:
      (i)   #12673 is a NON-SOURCE terminal of that wire, and its owner_class reads `SelectorTunnel`
            (the class check Pre-decided 85 carries from NI's own advice);
      (ii)  that wire has EXACTLY ONE `is_source=True` terminal counted over ALL owner classes (the
            FIX 4 discipline) - its (class, uid) is a FACT line, never a criterion;
      (iii) the walk satisfies the PD85 precondition (every real-owner row's recip == the queried uid).
    Hop count is an output, never a criterion; there is no outward walk left in this gate. ***
    """
    print("\n---------- [6b] A4 THE BARE-SINK GATE (FIX 3, consumer-anchored): does the CONSUMER entry "
          "that exposes SelectorTunnel #%d still carry a wire, and is #%d a sink on it?"
          % (T6_SECOND_SINK, T6_SECOND_SINK), flush=True)
    rec = {"second_sink": T6_SECOND_SINK, "original_net": T6_ORIGINAL_NET,
           "original_sinks": list(T6_SINKS_ORIGINAL), "anchor": "THE CONSUMER (Pre-decided 90)",
           "why": "rule 1a: a dropped downstream consumer is a computation change, and a bare source is "
                  "legal LabVIEW, so nothing else in this run would catch it "
                  "(tools/bench/diag_c67_addsr.log:389)"}
    sixth = K.get("sixth_row") or {}
    case_uid = sixth.get("case_structure_uid")
    addr = sixth.get("sink_addr") or {}
    rec["consumer_case_uid_measured_at_5b"] = case_uid
    rec["consumer_addr_measured_at_5b"] = addr
    if not case_uid or addr.get("term_index") is None:
        fact("[6b] THE CONSUMER WAS NEVER RESOLVED AT [5b] (case uid %r, addr %r) - A4 has no anchor "
             "and FAILS; the [5b] FACT lines carry what the owner-chain walk returned." % (case_uid, addr))
        gate("A4 no SINK that was wired on the bed is left bare by this stage (SelectorTunnel #%d, "
             "consumer-anchored - FIX 3)" % T6_SECOND_SINK, False,
             "no consumer anchor from [5b]: case uid %r, addr %r" % (case_uid, addr))
        R["bare_sink_gate"] = rec
        dump()
        return rec
    # ---- RE-MEASURED LIVE, never carried: the owner node's Terms[] entry at the [5b]-resolved index.
    cloc, crows = node_view(WORK, case_uid, hints, "[6b] the CONSUMER's owner node #%d" % case_uid,
                            quiet=True)
    row = next((t for t in crows if t["i"] == addr.get("term_index")), None)
    wire = (row or {}).get("wire") or 0
    rec.update({"consumer_found": cloc.get("found"), "consumer_terminal": row, "consumer_wire_uid": wire})
    fact("[6b] the CONSUMER entry: #%d Terms[t%r] name %r re-read LIVE ; it carries wire %r"
         % (case_uid, addr.get("term_index"), (row or {}).get("name"), wire))
    if not wire:
        fact("[6b] *** THE CONSUMER ENTRY CARRIES NO WIRE - #%d is left bare by this stage. ***"
             % T6_SECOND_SINK)
        gate("A4 no SINK that was wired on the bed is left bare by this stage (SelectorTunnel #%d, "
             "consumer-anchored - FIX 3)" % T6_SECOND_SINK, False,
             "the consumer entry t%r of #%d carries wire 0" % (addr.get("term_index"), case_uid))
        R["bare_sink_gate"] = rec
        dump()
        return rec
    walk, werr = wire_walk("[6b] the CONSUMER's wire %r" % wire, wire)
    rec["net_walk"] = walk
    rec["net_walk_error"] = werr
    # (i) #12673 as a NON-SOURCE terminal, WITH the class check (Pre-decided 85 / NI's advice).
    uid_rows = [t for t in (walk or []) if t.get("owner_uid") == T6_SECOND_SINK
                and t.get("is_source") is False]
    class_ok = any(t.get("owner_class") == "SelectorTunnel" for t in uid_rows)
    if uid_rows and not class_ok:
        fact("[6b] *** UID %d IS ON THE WIRE BUT ITS CLASS READS %r, NOT SelectorTunnel - a reassigned "
             "uid (Pre-decided 85's class check exists for exactly this). NOT accepted. ***"
             % (T6_SECOND_SINK, [t.get("owner_class") for t in uid_rows]))
    present_12673 = bool(uid_rows) and class_ok
    # (ii) EXACTLY ONE source terminal of ANY class (FIX 4: count first, filter never).
    srcs = [t for t in (walk or []) if t.get("is_source") and t.get("owner_uid")]
    rec["all_source_terminals"] = [(t.get("owner_class"), t.get("owner_uid")) for t in srcs]
    single_source = (len(srcs) == 1)
    fact("[6b] the CONSUMER's wire %r: source terminal(s) OF ANY CLASS %r (want EXACTLY 1) - the "
         "source's (class, uid) is a FACT, never a criterion" % (wire, rec["all_source_terminals"]))
    # (iii) the PD85 precondition on THIS walk.
    bad = pd85_violations(wire, walk)
    rec["pd85_violations"] = [(t.get("i"), t.get("owner_class"), t.get("owner_uid"), t.get("recip"))
                              for t in bad]
    # (iv) THE BOUNDED PROVENANCE WALK (Pre-decided 90's four constraints, restored by the c71 review
    #      A3(ii)/B4: FIX 3 as first cut passed on "any single source", which cannot distinguish "fed
    #      from #10407 t6" from "fed from anything" - the one distinction rule 1a turns on). From the
    #      consumer's wire: follow ONLY unique source terminals, FAIL on ambiguity, hop through a
    #      LoopTunnel to its unique other-side wire, STOP at the first non-LoopTunnel source, and assert
    #      that terminal's (class, uid) against the value predicted BEFORE the run - (SelectorTunnel,
    #      T6_SOURCE_FACE_RECORDED). Hop count is an OUTPUT; the failure modes are ambiguity, an
    #      unlocatable tunnel, a PD85-dirty wire, and the hop cap.
    prov = {"hops": [], "ok": False, "why": ""}
    cur, seen = wire, set()
    n_lt, _nlterr = safe("[6b] count('LoopTunnel') for the provenance walk",
                         lambda: g.count(WORK, "LoopTunnel"))
    for hop in range(T6_PROV_HOP_CAP + 1):
        w_walk = walk if cur == wire else wire_walk("[6b] PROV hop %d wire %r" % (hop, cur), cur)[0]
        if pd85_violations(cur, w_walk):
            prov["why"] = "wire %r is PD85-dirty" % cur
            break
        srcs_h = [t for t in (w_walk or []) if t.get("is_source") and t.get("owner_uid")]
        if len(srcs_h) != 1:
            prov["why"] = "wire %r has %d source terminal(s) - ambiguity FAILS the walk" % (cur, len(srcs_h))
            break
        s = srcs_h[0]
        prov["hops"].append({"wire": cur, "source_class": s.get("owner_class"),
                             "source_uid": s.get("owner_uid")})
        fact("[6b] PROV hop %d: wire %r <- source (%r, %r)"
             % (hop, cur, s.get("owner_class"), s.get("owner_uid")))
        if s.get("owner_class") != "LoopTunnel":
            prov["ok"] = (s.get("owner_class") == "SelectorTunnel"
                          and int(s.get("owner_uid") or 0) == T6_SOURCE_FACE_RECORDED)
            prov["why"] = ("terminated at (%r, %r); predicted (SelectorTunnel, %d): %r"
                           % (s.get("owner_class"), s.get("owner_uid"), T6_SOURCE_FACE_RECORDED,
                              prov["ok"]))
            break
        T = int(s["owner_uid"])
        if T in seen:
            prov["why"] = "LoopTunnel #%d seen twice - a cycle FAILS the walk" % T
            break
        seen.add(T)
        trec = None
        for i in range(int(n_lt or 0)):
            cand, _ce = safe("[6b] PROV tunnels(index=%d)" % i, lambda ii=i: g.tunnels(WORK, ii))
            if cand and int(cand.get("uid") or 0) == T:
                trec = cand
                break
        if trec is None:
            prov["why"] = "LoopTunnel #%d not found in the %r-entry traverse" % (T, n_lt)
            break
        others = [w for w in ([trec.get("out_wire")] + list(trec.get("in_wires") or []))
                  if w and int(w) != int(cur)]
        if len(others) != 1:
            prov["why"] = ("LoopTunnel #%d has %d other-side wire(s) %r - ambiguity FAILS the walk"
                           % (T, len(others), others))
            break
        cur = int(others[0])
    else:
        prov["why"] = "hop cap %d reached" % T6_PROV_HOP_CAP
    rec["provenance"] = prov
    fact("[6b] PROVENANCE (Pre-decided 90): %s ; %d hop(s) %r ; ok %r"
         % (prov["why"], len(prov["hops"]), prov["hops"], prov["ok"]))
    present = bool(present_12673 and single_source and not bad and not werr and prov["ok"])
    rec["second_sink_present"] = present
    fact("[6b] *** #%d (SelectorTunnel, row label `%s`) IS %sA NON-SOURCE TERMINAL OF THE CONSUMER'S "
         "OWN WIRE %r (class check %r ; single-source %r ; PD85 violations %d ; walk error %r) ***"
         % (T6_SECOND_SINK, T6_SIXTH_SINK_LABEL, "" if present else "**NOT** ", wire, class_ok,
            single_source, len(bad), werr or ""))
    if not present:
        rec["sixth_row"] = {"sink_uid": T6_SECOND_SINK, "sink_class": "SelectorTunnel",
                            "sink_label": "Q_focusback",
                            "source": "#%d t%d %r" % (CASE_UID, T6_TERM_INDEX, T6_TERM_NAME),
                            "original_net": T6_ORIGINAL_NET,
                            "evidence": "tools/bench/diag_c67_addsr.log:389",
                            "status": "NOT PROVEN WIRED BY THIS STAGE - it stays a SIXTH ROW for the "
                                      "next stage"}
        fact("[6b] *** SIXTH ROW, ON FILE AND NOT PASSED OVER: `Q_focusback` SelectorTunnel #%d must be "
             "re-connected to #%d t%d %r (original net %d, tools/bench/diag_c67_addsr.log:389). It is "
             "NOT worked around here. ***"
             % (T6_SECOND_SINK, CASE_UID, T6_TERM_INDEX, T6_TERM_NAME, T6_ORIGINAL_NET))
    gate("A4 no SINK that was wired on the bed is left bare by this stage (SelectorTunnel #%d, "
         "consumer-anchored + bounded provenance walk - FIX 3)" % T6_SECOND_SINK, present,
         "consumer wire %r ; uid+class hit %r ; sources %r ; PD85 violations %d ; walk error %r ; "
         "provenance ok %r (%s)"
         % (wire, present_12673, rec["all_source_terminals"], len(bad), werr or "",
            prov["ok"], prov["why"]))
    R["bare_sink_gate"] = rec
    dump()
    return rec


# ================================================================= [6] the full census
def census(tag, hints, include_registers=True):
    """THE FULL WIRED-TERMINAL CENSUS of the seven moved nodes (and both registers) - EVERY terminal, not a
    selection - plus the derived BARE list. Unconditional, whatever ExecState says."""
    print("\n---------- [6] FULL `node_terms` CENSUS OF THE SEVEN MOVED NODES PLUS BOTH SHIFT REGISTERS",
          flush=True)
    rec = {"tag": tag, "exec_state_at_census": read_es("[6] at the census", WORK),
           "nodes": {}, "bare": [], "registers": {}}
    for uid, name, _pos, _why in SET:
        loc, rows = node_view(WORK, uid, hints, "[6] #%d %s" % (uid, name))
        rec["nodes"][str(uid)] = {"uid": uid, "name": name, "found": loc.get("found"),
                                  "uid_echo": loc.get("uid_echo"), "n_terminals": len(rows),
                                  "n_wired": wired_count(rows), "terminals": rows}
        for t in rows:
            if not t.get("wire"):
                rec["bare"].append({"node_uid": uid, "node_name": name, "term_index": t.get("i"),
                                    "term_name": t.get("name"), "is_source": t.get("is_source"),
                                    "wire": t.get("wire"), "errs": t.get("errs"), "state": term_state(t)})
        fact("[6] #%d %r: %d terminal(s), %d WIRED, %d with WireUID 0"
             % (uid, name, len(rows), wired_count(rows), sum(1 for t in rows if not t.get("wire"))))
    if include_registers:
        li = loop_index_of(LOOP_A_UID, "[6] before the register read")
        for pair in SR_PAIRS:
            ri = (K.get("shift_registers") or {}).get(pair, {}).get("reg_index")
            if ri is None or li is None:
                rec["registers"][pair] = {"reg_index": ri, "note": "no reg_index / loop_index to read with"}
                fact("[6] the %s pair cannot be read back (reg_index %r, loop_index %r)" % (pair, ri, li))
                continue
            srl, err = safe("[6] shift_reg_left(%s)" % pair, lambda rr=ri: g.shift_reg_left(WORK, li, rr, 0))
            rec["registers"][pair] = {"reg_index": ri, "read": srl, "error_verbatim": err}
            fact("[6] %s pair reg_index %d -> right #%r out %r inside %r ; left #%r out %r inside %r"
                 % (pair, ri, (srl or {}).get("uid"), (srl or {}).get("out"), (srl or {}).get("inside"),
                    ((srl or {}).get("left") or {}).get("uid"), ((srl or {}).get("left") or {}).get("out"),
                    ((srl or {}).get("left") or {}).get("inside")))
            for side, d in (("right", srl or {}), ("left", (srl or {}).get("left") or {})):
                for where, t in [("outer", (d.get("out") or {}))] + \
                        [("inside", x) for x in (d.get("inside") or [])]:
                    if not t.get("wire"):
                        rec["bare"].append({"node_uid": d.get("uid"),
                                            "node_name": "%s SR %s %s" % (pair, side, where),
                                            "term_index": None, "term_name": t.get("name"),
                                            "is_source": t.get("is_source"), "wire": t.get("wire"),
                                            "errs": None, "state": "BARE (WireUID 0)"})
    print("\n  *** [6] THE BARE LIST - EVERY TERMINAL WITH WireUID 0 (%d row(s)) ***" % len(rec["bare"]),
          flush=True)
    for b in rec["bare"]:
        fact("[6] BARE  node #%-6r %-26r t%-4r %-34r is_source=%-5r state=%s"
             % (b["node_uid"], b["node_name"], b["term_index"], b["term_name"], b["is_source"], b["state"]))
    fact("[6] BARE LIST SIZE: %d terminal(s) with WireUID 0" % len(rec["bare"]))
    R["census"] = rec
    dump()
    rec["bare_sink_gate"] = bare_sink_gate(hints)
    dump()
    return rec


# ============================== [7] ExecState, the save, the restart, the ordered Broken? read LAST
def step_7_save(hints):
    print("\n---------- [7] ExecState AND THE SAVE", flush=True)
    es = read_es("[7] the decision point", WORK)
    K["exec_state_decision"] = es
    K["counts_final"] = counts(WORK, "[7] final, in memory")
    K["sr_counts_final"] = sr_counts(WORK, "[7] final, in memory")
    _l, lrows = node_view(WORK, LOOP11_UID, hints, "[7] #%d the WhileLoop" % LOOP11_UID, quiet=True)
    K["loop637_after"] = {"n_terms": len(lrows), "n_wired": wired_count(lrows)}
    fact("[7] #%d (WhileLoop): %r (before %r) - 37(e)/50(e)'s no-new-tunnel comparison, REPORTED"
         % (LOOP11_UID, K["loop637_after"], K.get("loop637_before")))
    if es == 1:
        rec = save_artefact("[7] the M3a-1 artefact", FINAL_PATH, BED_MD5, "the bed")
        if not rec.get("exists"):
            return rec
        D.fresh("[7] LabVIEW RESTART before the COLD reopen")
        R["handles"]["after_final_restart"] = labview_handles()
        es_cold = read_es("[7] COLD, after the restart", FINAL_PATH)
        K["exec_state_cold"] = es_cold
        fact("[7] *** THE SAVED ARTEFACT REOPENS COLD AT ExecState %r ***" % (es_cold,))
        K["counts_cold"] = counts(FINAL_PATH, "[7] COLD")
        # THE ORDERED `Broken?` PASS, LAST OF ALL (42(b)/52(f)) - never above a save point.
        print("\n---------- [7d] THE ORDERED `Broken?` PASS, LAST OF ALL (42(b)/52(f))", flush=True)
        br, berr = safe("[7d] report_all('Wire') for the ordered pass",
                        lambda: g.report_all(FINAL_PATH, "Wire"), [])
        K["cold_wire_rows"] = len(br or [])
        fact("[7d] COLD Wire census: %d row(s)%s" % (len(br or []), (" ; " + berr) if berr else ""))
        vb, verr = safe("[7d] exec_state(FINAL) second ordered read", lambda: g.exec_state(FINAL_PATH))
        K["exec_state_cold_second"] = vb
        fact("[7d] the SECOND ordered ExecState read on the cold artefact = %r%s (52(f): the type checker "
             "answers only on a second ordered pass)" % (vb, (" ; " + verr) if verr else ""))
        safe("[7] close_panel(final)", lambda: g.close_panel(FINAL_PATH))
        return rec
    fact("[7] ExecState %r. The brief asks for `%s` in this case, so THE SAVE IS ATTEMPTED and whatever "
         "the machine answers is recorded verbatim below." % (es, os.path.basename(BROKEN_PATH)))
    rec = save_artefact("[7] the BROKEN M3a-1 artefact", BROKEN_PATH, BED_MD5, "the bed")
    if rec.get("exists"):
        fact("[7] *** %s IS NOT A DELIVERABLE. IT IS NEVER RUN (34(f)) AND IT IS NEVER USED AS A BED FOR "
             "ANY LATER STAGE. Its shift registers are uninitialised AND it does not compile. ***"
             % os.path.basename(BROKEN_PATH))
    else:
        fact("[7] *** NO BROKEN ARTEFACT IS ON DISK: even the Pre-decided 88 route "
             "(save(allow_broken=True) -> gui_save) refused, verbatim above. NOTHING WAS WRITTEN "
             "UNDER %s. This is reported to judgement, not worked around. ***" % os.path.basename(
                 BROKEN_PATH))
    # A COLD REOPEN IS NOT ATTEMPTED ON A BROKEN ARTEFACT: the skill's own rule - never cold-load a
    # broken-saved VI headless (recompile spin).
    fact("[7] NO COLD REOPEN IS ATTEMPTED at ExecState 0 - the labview-automation skill's rule: never "
         "cold-load a broken-saved VI headless (recompile spin).")
    return rec


# ======================================================================= main
def main():
    print("=== build_d1_m3a1  %s  (bgrun --material --max-min 45)" % STAMP, flush=True)
    print("=== STAGE M3a-1. ANY ARTEFACT THIS RUN SAVES IS **NOT COMPUTATION-EQUIVALENT TO THE ORIGINAL** "
          "- ITS SHIFT REGISTERS ARE UNINITIALISED (initial values = stage M3a-2). IT IS NEVER RUN (34(f)).",
          flush=True)
    hints = [D639_RECORDED, TOP]
    try:
        phase_0()
        # [1] IS GONE - the probe was deleted by the prior-art review (B4 + B3). See the header.
        if left_s() < BUILD_MIN_S:
            fact("HALTED: only %.0f s left before the reserve; the build needs %.0f s"
                 % (left_s(), BUILD_MIN_S))
            raise Halt("no wall-clock left for the build")
        hints = step_2_baseline()
        nodes, _all_moved, after_hints = step_2_moves(hints)
        hints = after_hints
        nodes = step_2_rows(nodes, hints)
        made = step_3_registers()
        step_4_sr_rows(made, hints)
        nodes, _t1 = step_5_t1(nodes, hints)
        nodes, _t6 = step_6_sixth_row(nodes, hints)      # Pre-decided 72 - BEFORE the census, so A4 judges
        census("CENSUS", hints, include_registers=True)  # the FINISHED stage
        step_7_save(hints)
    except Halt as e:
        fact("HALTED: %s" % e)
    except Exception as e:                                                         # noqa: BLE001
        R["unexpected_exception"] = "%s: %s" % (type(e).__name__, str(e)[:600])
        fact("UNEXPECTED EXCEPTION: %s" % R["unexpected_exception"])
        refusal("main", R["unexpected_exception"])
    finally:
        safe("close_panel(WORK)", lambda: g.close_panel(WORK))
        for path in (WORK,):        # the probe SCRATCH is gone with step [1]; WORK is the only scratch now
            if os.path.exists(path):
                safe("remove %s" % os.path.basename(path), lambda p=path: os.remove(p))
            gate("H scratch %s is gone (exists=False)" % os.path.basename(path), not os.path.exists(path), "")
        print("\n---------- [H] THE md5 PINS AFTER, THE TOOL PINS, THE REFS AND THE HANDLES", flush=True)
        for tag, path, pin in PINS:
            pr = probe_hash("H %s AFTER" % tag, path)
            gate("H %s md5 is STILL its pin %s" % (tag, pin[:8]), pr.get("md5") == pin,
                 "%r" % (pr.get("md5"),))
        for p in TOOL_PINS:
            pr = probe_hash("H TOOL %s AFTER" % os.path.basename(p), p)
            gate("H TOOL %s is byte-identical before and after" % os.path.basename(p),
                 pr.get("md5") == (K.get("tool_pins_before") or {}).get(p),
                 "%r vs %r" % (pr.get("md5"), (K.get("tool_pins_before") or {}).get(p)))
        rc = g.ref_counts()
        R["ref_counts"] = rc
        fact("refs: %r" % (rc,))
        gate("H refs opened == closed and 0 live", rc.get("live") == 0, "%r" % (rc,))
        R["handles"]["after"] = labview_handles()
        fact("LabVIEW handles AFTER: %r (before %r)" % (R["handles"]["after"], R["handles"].get("before")))
        gate("H the LabVIEW handle count was read at entry and at exit",
             isinstance(R["handles"].get("before"), int) and isinstance(R["handles"].get("after"), int),
             "%r -> %r" % (R["handles"].get("before"), R["handles"].get("after")))
        gate("H no mutator call was REFUSED BY THE MACHINE", not refusals,
             "%d refusal(s): %r" % (len(refusals), [r["where"] for r in refusals]))
        left = [(os.path.basename(a["dest"]), a.get("md5"), a.get("size"))
                for a in R["artefacts_on_disk"] if a.get("exists")]
        R["files_left_on_disk"] = left
        print("\nTHE FILES THIS RUN LEFT ON DISK: %r" % (left,), flush=True)
        fact("THE FILES THIS RUN LEFT ON DISK: %r" % (left,))
        if left:
            fact("*** EVERY FILE NAMED ABOVE IS NOT COMPUTATION-EQUIVALENT TO THE ORIGINAL - ITS SHIFT "
                 "REGISTERS ARE UNINITIALISED. NONE OF THEM IS EVER RUN (34(f)). ***")
        dump()
        print("\n=== GATES: %d pass / %d fail%s" % (len(passes), len(fails),
                                                    ("; failing: " + ", ".join(fails)) if fails else ""),
              flush=True)
        print("=== JSON: %s" % OUT, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
