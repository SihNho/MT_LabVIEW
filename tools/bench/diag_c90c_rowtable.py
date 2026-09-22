r"""diag_c90c_rowtable - THE AUTHORITATIVE M3a-4 ROW TABLE. READ-ONLY on dated scratch COPIES.

PREDICTION CONTRACT. The three tasks are MEASUREMENTS reported as values; the gates below are the only
pass/fail claims and none of them gates on the answer.
  T1  the 11 severed wires READ WHOLE on the CLEAN pre-sever artefact through `Stage.net_sources`
      (OpWireSource_v5, WIRE-addressed, n=8) - never `wmap`/`Diagram.Nodes[]`. Per wire the row COUNT,
      per row owner class / owner uid / Terms[] index / is_source / recip echo / error columns VERBATIM.
      The c90 review's falsifier: any wire with >=3 REAL-owner rows breaks the two-ended model.
  T2  `SubVI #48` and `CaseStructure #10407` walked terminal by terminal on BOTH artefacts
      (`Terminal.Name` 634A004 + `Terminal.Connected Wire` 634A000 via `Stage.wired_terminals` ->
      `build_d1_m3a1.node_view` -> `gscript.node_terms_uid`): index -> (name, wire, state), `bare` on BED.
  T3  `Generic.Owner` 6327806 -> GObject `UID` on 10429 / 10978 / 11220 / 11348 on the BED, uid-echoed
      (`build_d1_v0.owner_of` strict), with each tunnel's own class from the Tunnel census.
  GATES: K1/K2/K3 + pins (stagekit), G1 all 11 uids in the CLEAN Wire census, G2 the NEGATIVE control
  uid 999983 does NOT echo back on either artefact, G3 a machine-chosen intact POSITIVE control wire
  returns >=1 real-owner row with PD85 0 on either artefact, G4a/G4b the BED's md5 before and after,
  G5 the row table exists and keys all 11 wires, H2-H6 hygiene.

NOTHING IS BUILT, SAVED, RE-WIRED, DELETED OR RUN; no op is created; neither artefact is opened for
EXECUTION. Both inputs are copied to dated scratches deleted in the same run (`THE FILES THIS RUN LEFT
ON DISK: []`, stagekit H6). Rig ASSEMBLED: no motor, no ASI, no camera. WHAT ALREADY EXISTS (checked
first): `tools/stagekit.py` `net_sources`:364, `wired_terminals`:354, `scratch`:406, pins, hygiene;
`tools/recipes/build_d1_m3a1.py` `node_view`:572, `term_state`:524; `build_d1_v0.owner_of`:338;
`gscript.report_all`:512. The readers live in `tools/bench/c90c_rows.py` (the <=120-line split).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402
import c90c_rows as C                                                              # noqa: E402

CLEAN = os.path.join(K.CLAUDEDEV, "D1_s3b_row2_20260921_160311.vi")
CLEAN_MD5 = "26c54ff784cb5cea21edbd214d2cc3a0"
BED = os.path.join(K.CLAUDEDEV, "D1_s3b_m3a3b_rowD_20260922_161040.vi")
BED_MD5 = "0b84595245dd650c0e8fd3f57104782c"
LOGP = os.path.join(K.BENCH, "diag_c90c_rowtable.log")
OUTP = os.path.join(K.BENCH, "m3a4_row_table.json")
R = {"task1": {}, "task2": {}, "task3": {}, "controls": {}, "tokens": []}

def assemble(s):
    """The per-row table: T1's endpoints + T2's terminal index/name on each side + the BED's bare state."""
    m, err = C.linemap(R, LOGP)
    R["linemap_error"] = err
    C.cite(R, m)
    for w in C.WIRES:
        rec = R["task1"][str(w)]
        rec["task2_index"] = {}
        for art in ("CLEAN", "BED"):
            for u in C.STRUCTS:
                tab = ((R["task2"].get(art) or {}).get(str(u)) or {}).get("terminals") or {}
                for i, row in tab.items():
                    if row.get("wire") == w:
                        rec["task2_index"].setdefault(str(u), {})[art] = dict(row, terminal_index=int(i))
        for u, d in rec["task2_index"].items():
            bt = ((R["task2"].get("BED") or {}).get(u) or {}).get("terminals") or {}
            if "CLEAN" in d and "BED" not in d:
                d["BED_same_index"] = bt.get(str(d["CLEAN"]["terminal_index"])) or \
                    "unread (the BED walk yielded no row at that index)"
        if not rec["task2_index"]:
            rec["task2_note"] = "no terminal of #48 or #10407 carries this wire on either artefact"
    R["bed_bare_indices"] = {str(u): sorted(int(i) for i, r in
                                            (((R["task2"].get("BED") or {}).get(str(u)) or {})
                                             .get("terminals") or {}).items() if r.get("bare"))
                             for u in C.STRUCTS}
    R["inputs"] = {"clean": {"path": CLEAN, "md5": CLEAN_MD5}, "bed": {"path": BED, "md5": BED_MD5}}
    with open(OUTP, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)
    s.fact("THE ROW TABLE: {0} ({1} B); linemap error {2!r}".format(OUTP, os.path.getsize(OUTP), err))
    s.gate("G5 the row table exists and keys all 11 wires",
           os.path.exists(OUTP) and all(str(w) in R["task1"] for w in C.WIRES), OUTP)

def main(s):  # noqa: C901
    s.start()
    s.discard_work()
    p = s.work
    s.head("[T0] THE TWO INPUTS - md5 asserted at both ends; the CLEAN Wire census")
    s.file_facts("T0 BED", BED)
    s.gate("G4a the BED's md5 is {0}".format(BED_MD5), K.md5(BED) == BED_MD5, K.md5(BED), fatal=True)
    cc, _e = s.safe("CLEAN report_all('Wire')", lambda: g.report_all(p, "Wire"), [])
    cset = {r["uid"] for r in (cc or [])}
    s.fact("T0 CLEAN Wire census: {0} wire(s)".format(len(cset)))
    missing = [w for w in C.WIRES if w not in cset]
    s.gate("G1 all 11 briefed uids are in the CLEAN artefact's Wire census", not missing,
           "missing {0!r}".format(missing))

    s.head("[T1] THE 11 WIRES READ WHOLE ON THE CLEAN ARTEFACT (net_sources, n=8)")
    C.t1_wires(s, p, cset, R)
    pos = sorted(cset - set(C.WIRES))[0] if (cset - set(C.WIRES)) else 0
    C.controls(s, p, "CLEAN", cset, pos, R)
    s.head("[T2a] TERMINAL INDEX + NAME on the CLEAN artefact")
    C.t2_terms(s, p, "CLEAN", R)

    bed = s.scratch("bed", source=BED)
    s.head("[T3] THE FOUR REPLACEMENT-SIDE TUNNELS' OWNERS, on the BED")
    C.t3_owners(s, bed, R)
    bc, _e2 = s.safe("BED report_all('Wire')", lambda: g.report_all(bed, "Wire"), [])
    bset = {r["uid"] for r in (bc or [])}
    s.fact("T0 BED Wire census: {0} wire(s)".format(len(bset)))
    C.controls(s, bed, "BED", bset, pos if pos in bset else (sorted(bset - set(C.WIRES))[0] if bset else 0),
               R)
    if s.left_s() > 180:
        s.head("[T2b] TERMINAL INDEX + NAME on the BED - which of those indices are now BARE")
        C.t2_terms(s, bed, "BED", R)
    else:
        s.fact("T2b SKIPPED - only {0:.0f} s left inside the deadline".format(s.left_s()))
    s.gate("G4b the BED's md5 is STILL {0} after every read".format(BED_MD5), K.md5(BED) == BED_MD5,
           K.md5(BED))

    s.head("[X] THE ROW TABLE - every cell carries its own log:line")
    assemble(s)

S = K.Stage(CLEAN, CLEAN_MD5, "diag_c90c_rowtable", deadline_min=26.0, reserve_s=260.0,
            out_json=os.path.join(K.BENCH, "diag_c90c_rowtable.json"),
            task="the authoritative M3a-4 row table: the 11 wires read whole on the CLEAN artefact, "
                 "terminal index+name on both artefacts, the four replacement-side tunnel owners")
sys.exit(K.run(main, S))
