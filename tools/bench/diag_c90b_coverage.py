r"""diag_c90b_coverage - M3a-4 STEP 3: DO M3a-1's REPLACEMENT WIRES CARRY THE SEVERED ROWS' PAIRS? READ-ONLY.

PREDICTION CONTRACT. The correspondence table is a RESULT, never a gate (the brief states the
MEASUREMENT, CLAUDE.md section 3); only R1/R2/P1/P2/N1/N2/C0/A1 below are gates.
  R   M3a-1's REPLACEMENT wires are ENUMERATED FROM ITS OWN LOG - the `[2c] row #<sink> t<i> <- #<src>
      t<j> : sink wire W / src wire W` lines of the LAST block of `tools/bench/build_d1_m3a1.log`
      (block start = `m3a1_severed_rows.json.last_block_first_line`, so earlier runs' uid assignments
      cannot leak in). R1 exactly 7 are found. R2 every one is in the bed's LIVE `Wire` census.
      Every terminal row of each is then read OFF THE WIRE with `Stage.net_sources` ->
      `OpWireSource_v5` (`Wire.Terms[]` 6371003 -> `Is Source?` 634A003), printed VERBATIM with its
      error columns. `wmap` / `Diagram.Nodes[]` is NOT used anywhere (it cannot enumerate a tunnel /
      shift-register / panel-control terminal, `tools/bench/diag_c89_wirebirth.log:85`).
  C   THE CORRESPONDENCE TABLE. Each of the 11 removed wires has a PREDICTED (source owner uid, sink
      owner uid) pair, read mechanically from `m3a1_severed_rows.json.rows[].endpoints`. Each is
      `covered by w<uid>` when some replacement wire's MEASURED source-owner set contains the predicted
      source AND its measured sink-owner set contains the predicted sink; `not covered` otherwise.
      The 11 are split by the MEASURED row counts of `tools/bench/m3a4_live_endpoints.json` (NOT by a
      hardcoded list): C0 gates that the split is 7 zero-row / 4 one-row, as that run recorded.
      Counted per group and reported; NOT interpreted, and no delete is proposed.
  P   POSITIVE CONTROL - >= 1 wire that is neither among the 11 nor a replacement is read identically
      and (P2) returns >= 1 owner row, separating "the reader cannot read this artefact" from "the wire
      genuinely holds no endpoint".
  N   NEGATIVE CONTROL - never-allocated uid 999983: N1 absent from the Wire census, N2 its uid echo
      MISMATCHES. `tools/bench/diag_c81_uidref.log:85` measured that the resolver answers a
      never-allocated uid with a DIFFERENT object and EVERY error column empty; the echo is the only
      column that catches it.
  WARNING THE TERMINAL NAME IS NOT A COLUMN of this route (`tools/bench/opwiresource_v5_labels.json`
      maps no name indicator) - reported absent, never invented.

NOTHING IS BUILT, SAVED, RE-WIRED, DELETED OR MUTATED; no op is created; the bed is never opened for
EXECUTION. The work copy is a dated scratch deleted in the same run (`discard_work`), `THE FILES THIS
RUN LEFT ON DISK: []` is gated by stagekit H6, the bed md5 + all five pins are asserted at both ends.
Rig ASSEMBLED: NO motor, NO ASI, NO camera - none is needed.

WHAT ALREADY EXISTS (checked before writing: `grep "^def " tools/gscript.py`, `docs/toolkit-capabilities.md`,
`ls tools/bench tools/recipes`) - NOTHING NEW IS WRITTEN:
  * `tools/stagekit.py:364 net_sources` - the wire-addressed owner reading, pd85 + per-row errors.
  * `tools/bench/diag_c90_live_endpoints.py` - step 2, the same probe on the 11; its `probe()` shape is
    reused here rather than re-invented.
  * `tools/recipes/build_opconnectfromwire_v0.py:423 wire_source_owner` - uid-echo-verified reader.
  * `gscript.uids` - the Wire census in one `OpReport_v3` run.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402

BED = os.path.join(K.CLAUDEDEV, "D1_s3b_m3a3b_rowD_20260922_161040.vi")
BED_MD5 = "0b84595245dd650c0e8fd3f57104782c"
OUT = os.path.join(K.BENCH, "m3a4_replacement_coverage.json")
M3A1_LOG = os.path.join(K.BENCH, "build_d1_m3a1.log")
SEVERED = os.path.join(K.BENCH, "m3a1_severed_rows.json")
LIVE = os.path.join(K.BENCH, "m3a4_live_endpoints.json")
NEVER = 999983
POS_CANDS = (25324, 7448, 23952, 24009, 24226, 24002, 23985)
CRE = re.compile(r"\[2c\] row #(\d+) t(\d+) <- #(\d+) t(\d+) : sink wire (\d+) / src wire (\d+)")


def replacements(s):
    """M3a-1's replacement wires, ENUMERATED FROM ITS OWN LOG's LAST block."""
    first = json.load(open(SEVERED, encoding="utf-8"))["last_block_first_line"]
    out = {}
    with open(M3A1_LOG, encoding="utf-8", errors="replace") as f:
        for i, ln in enumerate(f, 1):
            m = CRE.search(ln) if i >= first else None
            if m:
                sink, st, src, rt, sw, cw = (int(x) for x in m.groups())
                out[sw] = {"wire": sw, "log_line": i, "pred_src_owner": src, "pred_sink_owner": sink,
                           "sink_term": st, "src_term": rt, "src_eq_sink_wire": sw == cw}
                s.fact("[R] build_d1_m3a1.log:{0} REPLACEMENT w{1} = #{2} t{3} (src) -> #{4} t{5} "
                       "(sink) ; src wire {6}".format(i, sw, src, rt, sink, st, cw))
    return out


def probe(s, wire, kind, target):
    """One wire, every terminal row VERBATIM."""
    net = s.net_sources(wire, n=8, target=target, tag="{0} w{1}".format(kind, wire))
    walk = net.get("walk") or []
    for r in walk:
        s.fact("{0} w{1} ROW VERBATIM {2!r}".format(kind, wire, r))
    if not walk:
        s.fact("{0} w{1} RETURNED NO ROW AT ALL; safe() error column {2!r}".format(kind, wire,
                                                                                   net.get("err")))
    own = [r for r in walk if r.get("owner_uid")]
    src = sorted({int(r["owner_uid"]) for r in own if r.get("is_source")})
    snk = sorted({int(r["owner_uid"]) for r in own if not r.get("is_source")})
    s.fact("{0} w{1} MEASURED source-owner uids {2!r} ; sink-owner uids {3!r} ; rows {4} ; "
           "rows_with_owner {5}".format(kind, wire, src, snk, len(walk), len(own)))
    return {"wire": wire, "kind": kind, "rows": walk, "safe_err": net.get("err"),
            "rows_found": len(walk), "rows_with_owner": len(own), "src_owner_uids": src,
            "sink_owner_uids": snk, "source_owners": net.get("source_owners"),
            "all_owners": net.get("all_owners"), "pd85_violations": net.get("pd85_violations"),
            "uid_echoes": [r.get("uid_back") for r in walk if "uid_back" in r]}


def predicted_pairs():
    """(src owner uid, sink owner uid) per removed wire, from m3a1_severed_rows.json.rows[].endpoints."""
    out = {}
    for r in json.load(open(SEVERED, encoding="utf-8"))["rows"]:
        eps = r.get("endpoints") or []
        a = [e for e in eps if e.get("is_source")]
        b = [e for e in eps if not e.get("is_source")]
        out[int(r["wire_uid"])] = {"src": (int(a[0]["node_uid"]) if a else None),
                                   "sink": (int(b[0]["node_uid"]) if b else None),
                                   "src_class": (a[0].get("owner_class") if a else None),
                                   "endpoints": eps}
    return out


def main(s):
    s.start()
    s.discard_work()
    p = s.work
    s.head("[R] M3a-1's REPLACEMENT WIRES - enumerated from its own log, then read off the wire "
           "(TERMINAL NAME is NOT a column of OpWireSource_v5: absent, never invented)")
    repl = replacements(s)
    s.gate("R1 exactly 7 replacement wires enumerated from the LAST block of build_d1_m3a1.log",
           len(repl) == 7, repr(sorted(repl)))
    census, cerr = s.safe("Wire census g.uids", lambda: g.uids(p, "Wire"), set())
    census = census or set()
    s.fact("Wire census on the work copy: {0} uid(s); err {1!r}".format(len(census), cerr))
    missing = [w for w in sorted(repl) if w not in census]
    s.gate("R2 every replacement wire is present in the bed's LIVE Wire census", not missing,
           "missing {0!r}".format(missing))
    recs = [probe(s, w, "R", p) for w in sorted(repl)]

    s.head("[C] THE CORRESPONDENCE TABLE - does a replacement carry each removed wire's predicted pair?")
    pred = predicted_pairs()
    live = json.load(open(LIVE, encoding="utf-8"))
    meas = {int(r["wire"]): r for r in live["records"] if r.get("kind") == "E"}
    zero = sorted(w for w, r in meas.items() if r.get("rows_with_owner") == 0)
    one = sorted(w for w, r in meas.items() if r.get("rows_with_owner") == 1)
    s.gate("C0 the c90 measurement splits the 11 into 7 zero-row and 4 one-row wires",
           len(zero) == 7 and len(one) == 4, "zero {0!r} one {1!r}".format(zero, one))
    table = []
    for grp, uids in (("zero-row", zero), ("one-row", one)):
        for w in uids:
            pr = pred.get(w, {})
            hits = [r["wire"] for r in recs
                    if pr.get("src") in r["src_owner_uids"] and pr.get("sink") in r["sink_owner_uids"]]
            table.append({"wire": w, "group": grp, "predicted_src_owner": pr.get("src"),
                          "predicted_src_class": pr.get("src_class"),
                          "predicted_sink_owner": pr.get("sink"), "covered_by": hits,
                          "live_rows_with_owner": meas[w].get("rows_with_owner"),
                          "live_rows_found": meas[w].get("rows_found"), "covered": bool(hits)})
            s.fact("[C] {0} w{1}: predicted #{2}({3}) -> #{4} ; {5}".format(
                grp, w, pr.get("src"), pr.get("src_class"), pr.get("sink"),
                ("covered by " + ", ".join("w{0}".format(h) for h in hits)) if hits else "NOT COVERED"))
    cz = len([r for r in table if r["group"] == "zero-row" and r["covered"]])
    co = len([r for r in table if r["group"] == "one-row" and r["covered"]])
    s.row("C COUNTS", {"zero_row_covered": cz, "zero_row_total": len(zero),
                       "one_row_covered": co, "one_row_total": len(one)})

    s.head("[P] POSITIVE CONTROL - the identical read on a wire that is neither of the 11 nor a replacement")
    chosen = [c for c in POS_CANDS if c in census and c not in meas and c not in repl][:2]
    s.fact("POSITIVE CONTROL candidates {0!r} -> usable {1!r}".format(list(POS_CANDS), chosen))
    s.gate("P1 at least one such wire was available and probed", bool(chosen), repr(chosen))
    pos = [probe(s, w, "P", p) for w in chosen]
    recs += pos
    s.gate("P2 every positive control returned >= 1 owner row (the reader CAN read this artefact)",
           bool(pos) and all(r["rows_with_owner"] >= 1 for r in pos),
           repr([(r["wire"], r["rows_found"], r["rows_with_owner"]) for r in pos]))

    s.head("[N] NEGATIVE CONTROL - a never-allocated uid; only the uid echo catches it")
    s.gate("N1 uid {0} is NOT in the Wire census".format(NEVER), NEVER not in census, repr(NEVER))
    n = probe(s, NEVER, "N", p)
    recs.append(n)
    echo = n["uid_echoes"] + [r.get("uid_back") for r in n["rows"]]
    s.fact("N uid echo column(s): {0!r} ; owners returned {1!r}".format(echo, n["all_owners"]))
    s.gate("N2 the uid echo MISMATCHES {0}".format(NEVER),
           all(e != NEVER for e in echo) and n["rows_with_owner"] == 0,
           "echo {0!r} rows_with_owner {1}".format(echo, n["rows_with_owner"]))

    doc = {"script": "diag_c90b_coverage", "stamp": s.stamp, "bed": BED, "bed_md5_pin": BED_MD5,
           "bed_md5_before": s.R.get("input_md5_before"), "work_copy": os.path.basename(p),
           "reader": "OpWireSource_v5 via stagekit.Stage.net_sources (Wire.Terms[] 6371003)",
           "terminal_name": "NOT A COLUMN of OpWireSource_v5",
           "replacements_from_log": repl, "zero_row_wires": zero, "one_row_wires": one,
           "correspondence_table": table,
           "counts": {"zero_row_covered": cz, "zero_row_total": len(zero),
                      "one_row_covered": co, "one_row_total": len(one)},
           "positive_controls": chosen, "negative_control": NEVER, "records": recs}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, default=str)
    s.fact("ARTEFACT {0} : {1} B, {2} record(s)".format(OUT, os.path.getsize(OUT), len(recs)))
    s.gate("A1 the artefact exists on disk", os.path.exists(OUT), OUT)


S = K.Stage(BED, BED_MD5, "diag_c90b_coverage", deadline_min=20.0, reserve_s=240.0,
            out_json=os.path.join(K.BENCH, "diag_c90b_coverage.json"),
            task="M3a-4 step 3: do M3a-1's replacement wires carry the severed rows' owner pairs?")
sys.exit(K.run(main, S))
