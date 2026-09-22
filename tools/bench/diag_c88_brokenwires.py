# -*- coding: utf-8 -*-
"""D-1 READER (cycle 88, MATERIAL dispatch 3): READ OUT every broken wire on the CLEAN Row D artefact.

MEASUREMENT ONLY. Nothing is built, nothing is saved, nothing is mutated on any artefact: the dated work
copy is declared a scratch (`discard_work`) and every mutating read runs on a second dated scratch; both are
deleted in this run. The artefact is md5-pinned at entry and exit (K1 / H2).

PRIOR ART CHECKED BEFORE WRITING (CLAUDE.md "check what already exists"):
  - `tools/stagekit.py` (725 lines, self-test 32/0) - the standing kit; this file is its inputs only.
  - `stagekit.broken_wire_count():389` already runs Remove Bad Wires for a COUNT. It does not NAME the wires,
    so this file takes the uid-set DIFFERENCE around the same call - no new verb.
  - `build_opconnectfromwire_v0.wire_source_owner():423` = `OpWireSource_v5`, the wire-addressed terminal walk
    (per row: is_source, owner_class, owner_uid, reciprocal wire; uid-echo checked). No terminal uid and no
    terminal NAME exists in its label map (`tools/bench/opwiresource_v5_labels.json`), so those two columns are
    NOT READABLE by this route; reported as such, never invented.
  - `build_d1_v0.owner_of():338` (uid-echo strict) = the wire's OWNING diagram.
  - `build_d1_m3a1.node_census():487` / `find_node` / `terms_at` - the Node census and a node's terminal table.
  - ⚠️ `Wire.Is Broken?` 6371004 IS built, but every route to it goes through a SINK-terminal read ordered
    after a `Terminal.Connect Wire` (docs/NAMES.md:966-1015); there is no measured route to an arbitrary wire's
    `Broken?` value, and an orphan wire has none at all. LabVIEW's own broken verdict that IS readable here is
    membership in the Remove-Bad-Wires delete set, which is what this file reports.

PREDICTION CONTRACT (machine-checkable, stated before execution):
  G1  the RBW delete set has exactly 11 members == the D6 baseline of 11.
  G2  every one of them resolves an owning diagram (uid echo OK).
  G3  every one of them yields at least one terminal row from the wire-addressed walk.
  G4  the Node census equals 635 and `Diagram #686` carries 27 nodes (the input bed's inherited state).
  Not a gate: which diagrams they sit on, and which involve the five M3 rows' objects - those are the READING.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402

ART = os.path.join(K.CLAUDEDEV, "D1_s3b_m3a3b_rowD_20260922_161040.vi")
ART_MD5 = "0b84595245dd650c0e8fd3f57104782c"
BASELINE = 11
D686, D23058 = 686, 23058
M3 = {7468: "FlatSequenceInnerTunnel (row D sink owner)", 7488: "FSIT Left Terminal (row D sink)",
      23868: "RightShiftRegister (row D NEW source)", 4334: "RightShiftRegister (row D OLD source)",
      23895: "RightShiftRegister (row C new source)", 4256: "RightShiftRegister (row C old source)",
      7202: "Global 'Global motor pos.vi'", 10407: "row-C/B sink node", 637: "WhileLoop (OLD top loop)"}


def body(s):
    s.start()
    s.discard_work()
    M = K.mod("build_d1_m3a1")
    B = K.mod("build_d1_v0")
    CFW = K.mod("build_opconnectfromwire_v0")

    s.head("[A] CENSUS on the untouched work copy")
    s.census(tag="rowD")
    nodes, _e = s.safe("node_census", lambda: M.node_census(s.work, "rowD")[0], [])
    s.gate("G4a Node census == 635", len(nodes or []) == 635, "got {0}".format(len(nodes or [])))
    i686, _e = s.safe("diag_index(#686)", lambda: B.diag_index(s.work, D686))
    rows686, _e = s.safe("node_labels(#686)", lambda: g.node_labels(s.work, i686), [])
    s.gate("G4b Diagram #686 carries 27 nodes", len(rows686 or []) == 27,
           "index {0}, got {1}".format(i686, len(rows686 or [])))
    i23058, _e = s.safe("diag_index(#23058)", lambda: B.diag_index(s.work, D23058))
    rows23058, _e = s.safe("node_labels(#23058)", lambda: g.node_labels(s.work, i23058), [])
    s.fact("Diagram #23058 (new WhileLoop #23032 body) = traverse index {0}, {1} node(s)".format(
        i23058, len(rows23058 or [])))

    s.head("[A2] THE STRAY `Invoke` NODES - uid, where, and their wired state")
    inv = [n for n in (nodes or []) if "Invoke" in str(n.get("class"))]
    s.fact("Node census rows whose class contains 'Invoke': {0}".format(
        [(n["uid"], n["class"], n["pos"], n["owner_class"]) for n in inv]))
    on686 = {r["uid"]: k for k, r in enumerate(rows686 or [])}
    for n in inv:
        if n["uid"] in on686:
            tt, _e = s.safe("terms_at(#{0})".format(n["uid"]),
                            lambda nn=n: M.terms_at(s.work, i686, on686[nn["uid"]], nn["uid"],
                                                    "INV#{0}".format(nn["uid"])), {})
            terms = (tt or {}).get("terminals", [])
            wired = [t for t in terms if t.get("has_wire")]
            s.fact("INVOKE #{0} on Diagram #686 Nodes[{1}]: {2} terminal(s), {3} WIRED; rows {4!r}".format(
                n["uid"], on686[n["uid"]], len(terms), len(wired),
                [(t.get("i"), t.get("name"), t.get("is_source"), t.get("wire")) for t in terms]))
        else:
            s.fact("INVOKE #{0} is NOT on Diagram #686 (owner class {1!r})".format(n["uid"],
                                                                                   n["owner_class"]))
    s.R["invokes"] = inv
    s.dump()

    s.head("[B] WHICH WIRES ARE BROKEN - the Remove-Bad-Wires delete set, on a deleted scratch")
    sc = s.scratch("rbw")
    before, _e = s.safe("report_all('Wire') before", lambda: g.report_all(sc, "Wire"), [])
    res, rerr = s.safe("remove_bad_wires_scripted", lambda: g.remove_bad_wires_scripted(sc))
    after, _e = s.safe("report_all('Wire') after", lambda: g.report_all(sc, "Wire"), [])
    bmap = {r["uid"]: r for r in (before or [])}
    aset = {r["uid"] for r in (after or [])}
    broken = sorted(u for u in bmap if u not in aset)
    s.fact("Wire objects {0} -> {1}; RBW returned {2!r} (err {3!r})".format(
        len(before or []), len(after or []), res, rerr))
    s.fact("BROKEN WIRE UIDS (LabVIEW's own verdict): {0!r}".format(broken))
    s.gate("G1 broken-wire count == {0} (D6 baseline)".format(BASELINE), len(broken) == BASELINE,
           "got {0}".format(len(broken)))
    s.drop_scratch(sc, "H4a")

    s.head("[C] PER-WIRE READING on the untouched work copy - owning diagram + every terminal")
    table, ok_owner, ok_walk = [], 0, 0
    for u in broken:
        row = {"wire": u, "pos": bmap[u].get("pos"), "report_all_owner_class": bmap[u].get("owner")}
        r, err = s.safe("owner_of(w{0})".format(u), lambda uu=u: B.owner_of(s.work, uu))
        row["owner_diagram"] = list(r) if r else None
        row["owner_err"] = err
        ok_owner += 1 if r else 0
        walk, werr = s.safe("wire_source_owner(w{0})".format(u),
                            lambda uu=u: CFW.wire_source_owner(s.work, uu, n=8), [])
        rows = [x for x in (walk or []) if x.get("owner_uid")]
        ok_walk += 1 if rows else 0
        row["terminals"] = [{"i": x.get("i"), "is_source": x.get("is_source"),
                             "owner_class": x.get("owner_class"), "owner_uid": x.get("owner_uid"),
                             "recip_wire": x.get("recip")} for x in rows]
        row["walk_err"] = werr or "; ".join(str(x.get("err")) for x in (walk or []) if x.get("err"))
        row["m3_owners"] = sorted({x.get("owner_uid") for x in rows if x.get("owner_uid") in M3})
        src = ["{0}#{1}".format(x["owner_class"], x["owner_uid"]) for x in row["terminals"]
               if x["is_source"]]
        snk = ["{0}#{1}".format(x["owner_class"], x["owner_uid"]) for x in row["terminals"]
               if not x["is_source"]]
        s.fact("w{0:<6} diag {1!r} pos {2} | SRC {3!r} | SINK {4!r} | M3 {5!r} | IsBroken? {6} | err {7!r}"
               .format(u, row["owner_diagram"], row["pos"], src, snk, row["m3_owners"],
                       "NOT READABLE (no route; RBW-deleted = LabVIEW's verdict)", row["walk_err"][:60]))
        table.append(row)
    s.R["broken_wires"] = table
    s.gate("G2 every broken wire resolved an owning diagram", ok_owner == len(broken),
           "{0}/{1}".format(ok_owner, len(broken)))
    s.gate("G3 every broken wire yielded >=1 terminal row", ok_walk == len(broken),
           "{0}/{1}".format(ok_walk, len(broken)))

    s.head("[D] THE THREE SUMMARIES")
    bydiag = {}
    for r in table:
        key = tuple(r["owner_diagram"]) if r["owner_diagram"] else ("UNRESOLVED", 0)
        bydiag.setdefault(key, []).append(r["wire"])
    for key in sorted(bydiag, key=lambda k: -len(bydiag[k])):
        s.fact("BY DIAGRAM {0}#{1}: {2} wire(s) {3!r}{4}".format(
            key[0], key[1], len(bydiag[key]), bydiag[key],
            "  <- Diagram #686 (OLD top loop's)" if key[1] == D686 else
            ("  <- Diagram #23058 (NEW WhileLoop #23032 body)" if key[1] == D23058 else "")))
    withm3 = [r["wire"] for r in table if r["m3_owners"]]
    s.fact("INVOLVING an M3-row object {0!r}: {1} wire(s) {2!r}".format(sorted(M3), len(withm3), withm3))
    s.fact("INVOLVING NONE of them: {0} wire(s) {1!r}".format(
        len(table) - len(withm3), [r["wire"] for r in table if not r["m3_owners"]]))
    s.R["by_diagram"] = {"{0}#{1}".format(*k): v for k, v in bydiag.items()}
    s.dump()


if __name__ == "__main__":
    st = K.Stage(ART, ART_MD5, "diag_c88_brokenwires", fresh=True, deadline_min=22.0,
                 out_json=os.path.join(K.BENCH, "diag_c88_brokenwires.json"),
                 task="read out every broken wire on the clean Row D artefact; nothing built or saved")
    sys.exit(K.run(body, st))
