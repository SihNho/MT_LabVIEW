r"""diag_c90_live_endpoints - M3a-4 STEP 2: READ EVERY TERMINAL ROW THE 11 BROKEN WIRES HOLD. READ-ONLY.

PREDICTION CONTRACT. The per-wire comparison is a RESULT, never a gate (a disagreement is the finding,
CLAUDE.md "the brief states the MEASUREMENT"); only P1/P2/N1/N2 below are gates.
  E   For each of the 11 wire uids the c88/c89 baseline names, read every terminal row off the WIRE with
      `Stage.net_sources` -> `OpWireSource_v5` (`Wire.Terms[]` 6371003 -> `Is Source?` 634A003). Each row is
      printed VERBATIM (`repr`), error columns included; a row that raises is a REPORTED row, not a missing
      one. `wmap`/`Diagram.Nodes[]` is NOT used anywhere - it cannot enumerate a tunnel / shift-register /
      panel-control terminal (`tools/bench/diag_c89_wirebirth.log:85`).
      OUTCOME per wire, counted three ways: `unread` = no row carries an owner (raw error reported);
      `agrees` = every observed (owner_class, owner_uid, is_source) endpoint matches a PREDICTED endpoint
      on (uid, is_source) and on class where the prediction names one; `disagrees` = at least one does not.
      A wire answering FEWER rows than predicted still counts `agrees` (subset) - `rows_found` vs
      `rows_predicted` is reported per wire so the partialness is visible and is not hidden by the label.
  P1  POSITIVE CONTROL - >= 2 wires NOT among the 11 and present in this artefact's Wire census are read
      the identical way.  P2  each of them returns >= 1 owner row. P1+P2 separate "the reader cannot read a
      severed half-wire" from "the severed wire genuinely holds only one end".
  N1  NEGATIVE CONTROL - a never-allocated uid (999983) is absent from the Wire census.
  N2  its uid echo MISMATCHES. `tools/bench/diag_c81_uidref.log:85` measured that the resolver answers a
      never-allocated uid with a DIFFERENT object's class and uid and EVERY error column empty; the echo is
      the only column that catches it.
  ⚠ THE TERMINAL NAME IS NOT A COLUMN OF THIS ROUTE: `tools/bench/opwiresource_v5_labels.json` maps no name
      indicator. Reported as absent, never invented.

NOTHING IS BUILT, SAVED, RE-WIRED OR MUTATED; no op is created; the bed is never opened for EXECUTION.
The work copy is a dated scratch deleted in the same run (`discard_work`), `THE FILES THIS RUN LEFT ON
DISK: []` is gated by stagekit H6, the bed md5 + all five pins are asserted at both ends. Rig 조립: NO
motor, NO ASI, NO camera - none is needed.

WHAT ALREADY EXISTS (checked before writing: `grep "^def " tools/gscript.py`, `docs/toolkit-capabilities.md`,
`ls tools/bench tools/recipes`) - NOTHING NEW IS WRITTEN:
  * `tools/stagekit.py:364 net_sources` - the wire-addressed owner reading, with pd85 + per-row errors.
  * `tools/recipes/build_opconnectfromwire_v0.py:423 wire_source_owner` - scrubbed indicators, every
    `error out *` read, uid echo enforced (the c68 history-echo repair).
  * `tools/recipes/build_d1_m3a1.py:823 print_walk` / `:811 pd85_violations` - the printing and the check.
  * `gscript.uids` - the Wire census (one `OpReport_v3` run, not one per object).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402

BED = os.path.join(K.CLAUDEDEV, "D1_s3b_m3a3b_rowD_20260922_161040.vi")
BED_MD5 = "0b84595245dd650c0e8fd3f57104782c"
OUT = os.path.join(K.BENCH, "m3a4_live_endpoints.json")
ELEVEN = (1731, 1893, 2819, 3947, 4833, 7337, 7388, 9635, 11232, 23502, 23540)
NEVER = 999983
# The M3a-1 replacement wires first, then two wires this project's record names intact on THIS artefact
# (25324 = the Row-D connect's own wire, `build_d1_m3a3b_rowD_clean.log:113`; 7448 = the FSIT Right
# Terminal's inner wire, `:92`). The first two that are actually in the census are used.
POS_CANDS = (23804, 23811, 23820, 25324, 7448)
# (owner_class or None when the offline derivation named only a uid, owner_uid, is_source)
PRED = {
    1731: [("LeftShiftRegister", 4344, True), (None, 48, False)],
    3947: [("LeftShiftRegister", 4274, True), (None, 48, False)],
    9635: [("LoopTunnel", 9641, True), (None, 10407, False)],
    7337: [(None, 10407, True), ("RightShiftRegister", 4334, False)],
    1893: [(None, 3447, True), (None, 48, False)],
    2819: [(None, 3560, True), (None, 48, False)],
    4833: [(None, 3529, True), (None, 48, False)],
    7388: [(None, 48, True), (None, 10407, False)],
    11232: [(None, 48, True), (None, 10407, False)],
    23502: [(None, 23499, True), (None, 10407, False)],
    23540: [(None, 23523, True), (None, 10407, False)],
}


def probe(s, wire, kind, target):
    """One wire, every row VERBATIM. Returns the artefact record."""
    net = s.net_sources(wire, n=8, target=target, tag="{0} w{1}".format(kind, wire))
    walk = net.get("walk") or []
    for r in walk:
        s.fact("{0} w{1} ROW VERBATIM {2!r}".format(kind, wire, r))
    if not walk:
        s.fact("{0} w{1} RETURNED NO ROW AT ALL; safe() error column: {2!r}".format(kind, wire,
                                                                                    net.get("err")))
    obs = [(str(r.get("owner_class")), int(r.get("owner_uid")), bool(r.get("is_source")))
           for r in walk if r.get("owner_uid")]
    pred = PRED.get(wire)
    outcome, mismatch = None, []
    if pred is not None:
        if not obs:
            outcome = "unread"
        else:
            mismatch = [o for o in obs
                        if not [p for p in pred if p[1] == o[1] and p[2] == o[2]
                                and (p[0] is None or p[0] == o[0])]]
            outcome = "disagrees" if mismatch else "agrees"
        s.fact("{0} w{1} OUTCOME {2} : rows_found {3} / rows_predicted {4} ; observed {5!r} ; "
               "predicted {6!r} ; unmatched {7!r}".format(kind, wire, outcome, len(walk), len(pred),
                                                          obs, pred, mismatch))
    return {"wire": wire, "kind": kind, "rows": walk, "safe_err": net.get("err"),
            "rows_found": len(walk), "rows_with_owner": len(obs), "observed_endpoints": obs,
            "predicted_endpoints": pred, "rows_predicted": (len(pred) if pred else None),
            "outcome": outcome, "unmatched": mismatch, "source_owners": net.get("source_owners"),
            "all_owners": net.get("all_owners"), "pd85_violations": net.get("pd85_violations"),
            "uid_echoes": [r.get("uid_back") for r in walk if "uid_back" in r]}


def main(s):
    s.start()
    s.discard_work()
    p = s.work
    recs = []
    s.head("[E] THE 11 - every terminal row read OFF THE WIRE (no wmap, no Diagram.Nodes[])")
    s.fact("TERMINAL NAME is NOT a column of OpWireSource_v5 (no name indicator in "
           "tools/bench/opwiresource_v5_labels.json) - reported absent, never invented")
    for w in ELEVEN:
        recs.append(probe(s, w, "E", p))
    tally = {k: len([r for r in recs if r["outcome"] == k]) for k in ("agrees", "disagrees", "unread")}
    s.row("E three-way outcome over the 11", tally, {"agrees": 11, "disagrees": 0, "unread": 0})
    s.gate("E1 all 11 wires were probed and recorded", len(recs) == 11, "{0} record(s)".format(len(recs)))

    s.head("[P] POSITIVE CONTROL - the identical read on wires that are NOT among the 11")
    census, cerr = s.safe("Wire census g.uids", lambda: g.uids(p, "Wire"), set())
    census = census or set()
    s.fact("Wire census on the work copy: {0} uid(s); err {1!r}".format(len(census), cerr))
    chosen = [c for c in POS_CANDS if c in census and c not in ELEVEN][:2]
    s.fact("POSITIVE CONTROL candidates {0!r} -> present in THIS artefact's census and not among the 11: "
           "{1!r} (chosen because the record names them intact here)".format(list(POS_CANDS), chosen))
    s.gate("P1 at least two non-broken wires were available and probed", len(chosen) >= 2, repr(chosen))
    pos = [probe(s, w, "P", p) for w in chosen]
    recs += pos
    s.gate("P2 every positive control returned >= 1 owner row (so the reader CAN read this artefact)",
           bool(pos) and all(r["rows_with_owner"] >= 1 for r in pos),
           repr([(r["wire"], r["rows_found"], r["rows_with_owner"]) for r in pos]))

    s.head("[N] NEGATIVE CONTROL - a never-allocated uid; only the uid echo catches it")
    s.gate("N1 uid {0} is NOT in the Wire census".format(NEVER), NEVER not in census, repr(NEVER))
    n = probe(s, NEVER, "N", p)
    recs.append(n)
    echo = n["uid_echoes"] + [r.get("uid_back") for r in n["rows"]]
    s.fact("N uid echo column(s): {0!r} ; owners returned {1!r}".format(echo, n["all_owners"]))
    s.gate("N2 the uid echo MISMATCHES {0} (a matching echo would mean a fabricated answer)".format(NEVER),
           all(e != NEVER for e in echo) and n["rows_with_owner"] == 0,
           "echo {0!r} rows_with_owner {1}".format(echo, n["rows_with_owner"]))

    doc = {"script": "diag_c90_live_endpoints", "stamp": s.stamp, "bed": BED, "bed_md5_pin": BED_MD5,
           "bed_md5_before": s.R.get("input_md5_before"), "work_copy": os.path.basename(p),
           "reader": "OpWireSource_v5 via stagekit.Stage.net_sources (Wire.Terms[] 6371003)",
           "terminal_name": "NOT A COLUMN of OpWireSource_v5 - opwiresource_v5_labels.json maps no name",
           "eleven": list(ELEVEN), "positive_controls": chosen, "negative_control": NEVER,
           "three_way": tally, "records": recs}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, default=str)
    s.fact("ARTEFACT {0} : {1} B, {2} record(s)".format(OUT, os.path.getsize(OUT), len(recs)))
    s.gate("A1 the artefact exists on disk", os.path.exists(OUT), OUT)


S = K.Stage(BED, BED_MD5, "diag_c90_live_endpoints", deadline_min=18.0, reserve_s=240.0,
            out_json=os.path.join(K.BENCH, "diag_c90_live_endpoints.json"),
            task="M3a-4 step 2: read every terminal row the 11 broken wires hold, + positive/negative controls")
sys.exit(K.run(main, S))
