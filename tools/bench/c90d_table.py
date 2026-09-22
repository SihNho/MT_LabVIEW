r"""c90d_table - the v2 ROW-TABLE ASSEMBLY for diag_c90d_outstanding (the <=120-line split).

It READS `tools/bench/m3a4_row_table.json`, deep-copies it, and writes `m3a4_row_table_v2.json`: v1 is
never rewritten, so no cell measured in cycle 68's earlier dispatch is at risk. Every new cell cites this
run's own `diag_c90d_outstanding.log:<line>` through `c90c_rows.linemap`/`cite`; anything the machine did
not yield stays `unread` with its raw error. NOTHING IS CLASSIFIED: `endpoints_identical_to_clean_row` is
a set comparison of measured (owner_class, owner_uid) pairs, not a verdict about the row.
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c90d_reads as C                                                             # noqa: E402


def assemble(s, R, src, outp, logp, inputs):
    m, err = C.linemap(R, logp)
    R["linemap_error"] = err
    C.cite(R, m)
    v2 = copy.deepcopy(json.load(open(src, encoding="utf-8")))
    v2["v2_note"] = ("EXTENDED INTO A NEW FILE so no cell of m3a4_row_table.json is at risk: v1 is copied "
                     "verbatim and every new cell sits under `disposition_evidence`, `m1_unread_bed_wires`, "
                     "`m2_m3_borders`, `repl_nets_bed` or `controls_c90d`.")
    v2["m1_unread_bed_wires"], v2["m2_m3_borders"] = R["m1"], R["borders"]
    v2["controls_c90d"], v2["repl_nets_bed"] = R["controls"], R["repl_nets"]
    v2["inputs_c90d"] = dict(inputs, log=os.path.basename(logp), source_table=os.path.basename(src),
                             linemap_error=err)
    kls = {b[0]: b[1] for b in C.BORDERS}
    for w, row in v2["task1"].items():
        clean = sorted({(str(e["owner_class"]), int(e["owner_uid"])) for e in row["endpoints"]
                        if e.get("owner_uid")})
        repl = C.REPL.get(int(w))
        bed = R["repl_nets"].get(str(repl)) or {}
        de = {"clean_row_endpoints": clean, "clean_terminal_index": row.get("task2_index"),
              "replacement_wire_on_that_terminal_index": repl,
              "replacement_endpoints": bed.get("real_owner_rows", "unread"),
              "replacement_read_err": bed.get("err", "unread"),
              "replacement_src": bed.get("src", "unread - the replacement wire was never read"),
              "endpoints_identical_to_clean_row": (bed.get("real_owner_rows") == clean
                                                   if bed.get("endpoints") else "unread"),
              "outstanding_row": int(w) in [b[2] for b in C.BORDERS]}
        if de["outstanding_row"]:
            uid = next(b[0] for b in C.BORDERS if b[2] == int(w))
            de["old_border_object"] = {"uid": uid, "briefed_class": kls[uid],
                                       "BED": (R["borders"].get("BED") or {}).get(str(uid), "unread"),
                                       "CLEAN": (R["borders"].get("CLEAN") or {}).get(str(uid), "unread")}
        row["disposition_evidence"] = de
    with open(outp, "w", encoding="utf-8") as f:
        json.dump(v2, f, indent=1, default=str)
    s.fact("THE v2 ROW TABLE: {0} ({1} B); linemap error {2!r}".format(outp, os.path.getsize(outp), err))
    ok = (os.path.exists(outp) and len(v2["task1"]) == 11
          and all("disposition_evidence" in r for r in v2["task1"].values()))
    s.gate("G5 the v2 row table exists and all 11 rows carry a disposition_evidence block", ok, outp)
    return v2
