r"""diag_c90_endpoints - THE LIVE ENDPOINTS OF THE 11 SEVERED HALF-WIRES. READ-ONLY, NOTHING SAVED.

Pre-decided 131 step (2) (`docs/cycle27-plan.md:3697-3701`): read each of the 11 wires' live endpoint(s)
off the WIRE with `Stage.net_sources` (`tools/stagekit.py:364` -> `wire_source_owner`, `Wire.Terms[]`
6371003 -> `Is Source?` 634A003), NEVER through `wmap`/`Diagram.Nodes[]`, which cannot enumerate a tunnel
terminal, a shift-register outer, a panel-control terminal or a severed half-wire (`docs/NAMES.md:966-991`).

PREDICTION CONTRACT (desk-checked per Pre-decided 132: for every predicted value I named the step that
could already have determined it; two predictions were DELETED for that reason - see DELETED below).
  E1  All 11 uids RESOLVE: for each, `OpWireSource_v5`'s uid echo equals the queried uid and the walk has
      >= 1 row with a REAL owner. FALSIFIED by any `unresolved` row or an all-null walk (the reader's
      outcome A, `build_d1_m3a1.pd85_violations`:815) - which would mean the uid is dead on this artefact
      and the c89 removed-set is not addressable here.
  E2  PD85 holds on all 11: every real-owner row has `recip == queried uid` (0 violations in total).
      FALSIFIED by any violation; a walk that violates it is NOT BELIEVED and its row is reported so.
  E3  Each of the 11 has AT MOST ONE terminal with `Is Source?` True. FALSIFIED by a two-source wire
      (which is what a BROKEN wire normally looks like, `build_opconnectfromwire_v0` T2c2) - so this one
      genuinely can fail here and is the discriminator between "severed half-wire" and "double-driven".
  E4a-E4d  The four priors REPRODUCE on this bed: w1731 SRC `LeftShiftRegister #4344` · w3947 SRC
      `LeftShiftRegister #4274` · w9635 SRC `LoopTunnel #9641` · w7337 SINK `RightShiftRegister #4334`.
      FALSIFIED by a different owner class/uid, or by the side (source/sink) differing. These were read on
      EARLIER artefacts, so a contradiction is a real finding about the bed, not a reader fault.
  DELETED BY THE DESK CHECK, not measured here:
   (i) `Wire.Is Broken?` 6371004 per wire. NO standalone reader op exists in this fleet
       (`docs/toolkit-capabilities.md:68` "the sound reader ... is NOT BUILT";
       `tools/recipes/build_d1_m3a3b_d3b.py:29-38`), and the only readback on disk is the one EMBEDDED in
       the connect ops, which runs only if a `Terminal.Connect Wire` is performed - a MUTATION that on a
       severed half-wire would CREATE the endpoint being measured, and reading it perturbs the target
       (`docs/NAMES.md:1010-1017`). Moreover the value is ALREADY DETERMINED for all 11 by an earlier
       step: LabVIEW's own Remove Bad Wires removed exactly this set on four artefacts
       (`tools/bench/diag_c89_wirebirth.log`, Pre-decided 129) - i.e. LabVIEW classifies all 11 as bad.
       Predicting it again would predict a value a prior step forced (Pre-decided 132). REPORTED NOT
       MEASURED, with the citation, on every row.
   (ii) the terminal's LABEL/NAME. `OpWireSource_v5` returns `Is Source?`, reciprocal wire, owner class and
       owner UID and NO name (`docs/toolkit-capabilities.md:60`). Reported as absent, not routed around.

NOTHING IS BUILT, NOTHING IS SAVED, NO OP IS CREATED, NO VI IS RUN (34(f)). The work copy is discarded
(`discard_work`), so `THE FILES THIS RUN LEFT ON DISK: []` is gated by stagekit H6; the bed's md5 and all
five pins are asserted at both ends. NO motor, NO ASI, NO camera.

WHAT ALREADY EXISTS (CLAUDE.md "check what exists first" - grep of tools/, docs/toolkit-capabilities.md):
  * `tools/stagekit.py` - pins, restart + handle counts, preload, `net_sources` (:364), `census`, hygiene.
  * `tools/recipes/build_opconnectfromwire_v0.wire_source_owner` (:423) - the uid-echo-checked reader.
  * `tools/recipes/build_d1_m3a1.print_walk` (:823) / `.pd85_violations` (:811) - the walk printer + the
    reader precondition. NOTHING NEW IS WRITTEN: this file is inputs, a loop and gates.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402

BED = os.path.join(K.CLAUDEDEV, "D1_s3b_m3a3b_rowD_20260922_161040.vi")
BED_MD5 = "0b84595245dd650c0e8fd3f57104782c"
WIRES = [1731, 1893, 2819, 3947, 4833, 7337, 7388, 9635, 11232, 23502, 23540]
# (wire, side, owner class, owner uid) - Pre-decided 131's four already-read endpoints.
PRIORS = [(1731, "SRC", "LeftShiftRegister", 4344), (3947, "SRC", "LeftShiftRegister", 4274),
          (9635, "SRC", "LoopTunnel", 9641), (7337, "SNK", "RightShiftRegister", 4334)]
NOT_MEASURED = ("Is Broken? NOT MEASURED - no standalone 6371004 reader exists "
                "(toolkit-capabilities.md:68); already determined for all 11 by c89's Remove Bad Wires")


def main(s):
    s.start()
    s.discard_work()
    p = s.work

    s.head("[E0] THE WIRE CENSUS - do these 11 uids exist on the bed at all? (independent of the reader)")
    s.census(("Wire", "Diagram", "WhileLoop", "LoopTunnel"), tag="E0")
    live, e = s.safe("E0 uids(Wire)", lambda: [o["uid"] for o in g.report_all(p, "Wire")], [])
    present = [w for w in WIRES if w in (live or [])]
    s.fact("E0 Wire census {0} uid(s) {1!r}; of the 11, PRESENT {2!r} ; ABSENT {3!r}".format(
        len(live or []), e, present, [w for w in WIRES if w not in (live or [])]))

    s.head("[E1-E3] THE ELEVEN ENDPOINTS, READ OFF THE WIRE (OpWireSource_v5, never wmap)")
    table, resolved, pd85, multi = [], [], 0, []
    for w in WIRES:
        r = s.net_sources(w, n=8, tag="E w{0}".format(w))
        walk = r.get("walk") or []
        real = [t for t in walk if t.get("owner_uid")]
        bad_echo = [t for t in walk if t.get("unresolved")]
        ok = bool(real) and not bad_echo
        resolved.append(ok)
        pd85 += int(r.get("pd85_violations") or 0)
        srcs = [t for t in real if t.get("is_source")]
        if len(srcs) > 1:
            multi.append(w)
        terms = " | ".join("{0} #{1} is_source={2} recip={3}".format(
            t.get("owner_class"), t.get("owner_uid"), t.get("is_source"), t.get("recip")) for t in real)
        table.append("w{0:<6} resolves={1:<5} real_rows={2} rows={3}  [{4}] ; err={5!r}".format(
            w, ok, len(real), len(walk), terms or "NO REAL OWNER", r.get("err")))
        s.R.setdefault("endpoints", {})[str(w)] = {
            "resolves": ok, "real_rows": len(real), "walk_rows": len(walk),
            "terms": [{k: t.get(k) for k in ("i", "owner_class", "owner_uid", "is_source", "recip")}
                      for t in real], "pd85_violations": r.get("pd85_violations"),
            "is_broken": None, "is_broken_note": NOT_MEASURED, "label": None,
            "label_note": "OpWireSource_v5 returns no terminal name (toolkit-capabilities.md:60)"}

    s.head("[TABLE] uid -> resolves? -> terminals (owner class #uid, is_source, recip)")
    for line in table:
        s.fact(line)
    s.fact("Is Broken? column for ALL 11: {0}".format(NOT_MEASURED))
    s.fact("terminal LABEL column for ALL 11: NOT AVAILABLE on this reader - OpWireSource_v5 returns "
           "Is Source?, reciprocal wire, owner class and owner UID, and no name "
           "(docs/toolkit-capabilities.md:60). No other route was tried.")

    s.gate("E1 all 11 uids resolve (uid echo OK and >= 1 real-owner row)", all(resolved),
           "resolved {0}/11 ; failing {1!r}".format(sum(resolved),
                                                    [w for w, o in zip(WIRES, resolved) if not o]))
    s.gate("E2 PD85 holds on all 11 (every real-owner row has recip == the queried uid)", pd85 == 0,
           "{0} violation(s) in total".format(pd85))
    s.gate("E3 no wire of the 11 has more than one terminal with Is Source? True", not multi,
           "multi-source wires {0!r}".format(multi))

    s.head("[E4] THE FOUR PRIORS - AGREE / CONTRADICT / NOT REPRODUCED")
    for w, side, cls, uid in PRIORS:
        rec = (s.R.get("endpoints") or {}).get(str(w)) or {}
        terms = rec.get("terms") or []
        want_src = side == "SRC"
        hit = [t for t in terms if str(t.get("owner_class")) == cls and int(t.get("owner_uid") or 0) == uid
               and bool(t.get("is_source")) == want_src]
        seen = [(t.get("owner_class"), t.get("owner_uid"), t.get("is_source")) for t in terms]
        s.gate("E4 w{0} {1} {2} #{3} reproduces on this bed".format(w, side, cls, uid), bool(hit),
               "observed {0!r}{1}".format(seen, "" if terms else " - NOT REPRODUCED (no real-owner row)"))


S = K.Stage(BED, BED_MD5, "diag_c90_endpoints", deadline_min=18.0, reserve_s=240.0,
            out_json=os.path.join(K.BENCH, "diag_c90_endpoints.json"),
            task="Pre-decided 131 step 2: the live endpoints of the 11 severed half-wires, read off the "
                 "wire with OpWireSource_v5; read-only, nothing saved, no op built")
sys.exit(K.run(main, S))
