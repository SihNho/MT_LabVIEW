r"""build_opallwires_v0 - STAGE A of OpAllWires_v0.vi: EVERY wire's uid AND `Is Broken?` in ONE round trip.

WHY THIS FILE IS STAGE A AND NOT THE WHOLE OP (CLAUDE.md "big or blocked work is SPLIT into steps that each
SAVE an intermediate artefact", user 2026-09-19). The brief's full op also carries the two ENDPOINTS per wire,
which needs a SECOND `To More Specific Class` (owner refnum -> GObject for the owner UID) and either a nested
For loop or two Index Arrays. Stage A stops at the wire-level columns, leaves a RUNNABLE SAVED FILE, and
Stage B adds the endpoint columns to that file. If Stage B never runs, Stage A is still the reader this
project has never had: `Wire.Is Broken?` for all 1920 wires at once (STATUS: "no standalone 6371004 reader",
`docs/toolkit-capabilities.md:68`).

MEASURED FIRST (`tools/bench/diag_allwires_probe.log`, 13 pass / 0 fail, BGRUN END rc=0 after 149s):
  * Traverse class `Wire` WORKS on the bed - `report_all(bed,'Wire')` returns **1920 rows in 1.67 s**, ONE op
    run, every uid distinct, and all 11 severed half-wires present. `count(Wire)` alone is 0.16 s.
  * The donor `OpReportAll_v0.vi` on disk (md5 ffcec2c75e92dcad514299ba20e66054, 12,510 B) is exactly what
    `build_opreportall_v1.py` describes: ForLoop 1, LoopTunnel 5, Property 2, SubVI 1, panel
    `... (10,'Array') (11,'Array 2') (12,'Array 3') (13,'Array 4')`.
So the donor is `OpReportAll_v0.vi`: `Open VI Reference -> Traverse(Class Name) -> For loop auto-indexing
`References` -> PN1 `VI Server:GObject` (Position/UID/ClassName/Owner) -> PN2 `Generic.ClassName` on the
owner -> four auto-indexed output tunnels, each with a typed array indicator`. Called with `Class Name`
= `Wire`, its `UID` array IS the wire census. Stage A adds ONE column.

THE ONE NEW THING: a `VI Server:Wire` property node cannot be fed the Traverse ref directly (GObject ->
Wire is a DOWNCAST and reads ExecState 0 - measured, `build_opconnectnested_v0_run1.log`), so it needs a
`To More Specific Class` with a WIRE-TYPED SEED. Both halves are proven and are COPIED, not invented:
  * the seed  = `create_control` on a `VI Server:Wire` property node's own `reference`
                (`build_opconnectfromwire_v0.py` W5/W6, gates W6/W6b).
  * the TMSC  = `copy_by_index(NI example 'Navigating Nodes and Wires.vi', 'Function', 6, expect_uid=99)`
                (same file, W9; also `build_opconstvalue_v1.py:165-199`).
`copy_by_index` FILE-copies the target, runs `finish()` on the copy and REFUSES to save unless ExecState is
1 (`gscript.py:1592`), so EVERY edit that breaks the VI happens inside `finish` and the pre-copy target on
disk stays runnable. That is also why the seed's property node is MOVED into the loop body rather than a
second one built there: `create_control` addresses `VI.Block Diagram -> Nodes[]` and cannot reach a nested
diagram, and `move_in` severs only wires that exist, so its net is deleted first (c89's 37(d)).

NAMES, all read from the project registry, none guessed (`docs/NAMES.md:371`, `docs/vi-server-ids.json`):
  `Wire.Is Broken?` 6371004 -> ITEM TERMINAL **`Broken?`** (the string `Is Broken?` is only ever a PANEL
  label - NAMES.md:992-999, this exact confusion cost a run on 2026-09-21) · `Wire.Terms[]` 6371003 ->
  `Terms[]` · a property node's ref passthrough is `reference out` · TMSC terminals `target class`,
  `reference`, `specific class reference`.

PREDICTION CONTRACT (desk-checked per Pre-decided 132 - nothing predicted that an earlier step forced):
  B1  the copy is the measured donor: ForLoop 1, LoopTunnel 5, Property 2, SubVI 1, ExecState 1. This one IS
      determined by the probe, and is kept as a CONTROL on the copy, not as a discovery.
  B3  `build_property('VI Server:Wire', [6371004, 6371003])` yields ONE new Property node whose data outputs
      are exactly {`Broken?`, `Terms[]`}. FALSIFIED by any other name set - which would mean NAMES.md:371 is
      wrong about 6371004's short name.
  B4  `create_control` on its `reference` yields exactly ONE new control, arriving WIRED (W6/W6b precedent).
  B5  ExecState 1 and a save BEFORE `copy_by_index` (it copies the FILE, gscript.py:1556).
  B6  the copy adds exactly ONE node carrying a `specific class reference` terminal.
  F1-F6 inside `finish`: the net delete leaves both ends bare; both moves land the object on the loop BODY
      diagram (checked by `Generic.Owner`, not by position); each of the three wires reads the SAME uid on
      both ends; `exit_loop` adds exactly one LoopTunnel; `tunnel_indicator` adds a ControlTerminal AND a
      Wire (a ControlTerminal alone is the dangling-indicator failure, gscript.py:1943).
  B7  ExecState 1 after `finish` - enforced by copy_by_index itself, re-read here COLD after the save.
  NOT PREDICTED, MEASURED: the elapsed seconds of a full call and the indicator's LabVIEW-chosen label.

SAFETY: builds a NEW file under claudeDev. The donor is never opened for writing and its md5 is gated at
both ends; the main VI is never touched. No motor, no ASI, no camera. Runner stays STOPPED.
  MATERIAL=1 py tools/bgrun.py --max-min 30 --log tools/bench/build_opallwires_v0.log -- py -u tools/recipes/build_opallwires_v0.py
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "bench"))
sys.path.insert(0, HERE)
import gscript as g                                                              # noqa: E402
import stagekit as K                                                             # noqa: E402
from build_opconnectnested_v1 import walk, term, idx, del_net, Stop              # noqa: E402

DONOR = os.path.join(g.CLAUDEDEV, "OpReportAll_v0.vi")
DONOR_MD5 = "ffcec2c75e92dcad514299ba20e66054"
EX = os.path.join(g.CLAUDEDEV, "NIScriptingExamples", "Finding and Modifying Objects",
                  "Navigating Nodes and Wires.vi")
EX_TMSC_UID, EX_TMSC_FN_INDEX = 99, 6
OP_NAME = "OpAllWires_v0.vi"
MAP_OUT = os.path.join(ROOT, "bench", "opallwires_labels.json")
P_BROKEN, P_TERMS = "6371004", "6371003"
T_BROKEN, T_TERMS = "Broken?", "Terms[]"


def ctls(p, indicators=False):
    return [lab for _i, lab, ind in g.fp_labels(p) if bool(ind) == indicators and lab]


def body_diagram(p):
    return [i for i, d in enumerate(g.report(p, "Diagram")) if "For" in str(d.get("owner"))]


def owner_of(p, uid):
    return [o["owner"] for o in g.report_all(p, "GObject") if int(o["uid"]) == int(uid)]


def main(s):
    s.start()
    p = s.work
    s.safe("open_panel", lambda: g.open_panel(p))
    time.sleep(1.0)

    s.head("[B1] the copy IS the measured donor (control, not a discovery)")
    cen = {c: g.count(p, c) for c in ("ForLoop", "LoopTunnel", "Property", "SubVI", "Function",
                                      "ControlTerminal", "Wire", "Diagram")}
    es = s.es("B1 the fresh copy")
    s.fact("B1 census {0!r}".format(cen))
    s.gate("B1 ForLoop 1 / LoopTunnel 5 / Property 2 / SubVI 1 / ExecState 1",
           cen["ForLoop"] == 1 and cen["LoopTunnel"] == 5 and cen["Property"] == 2
           and cen["SubVI"] == 1 and es == 1, "{0!r} ExecState {1}".format(cen, es), fatal=True)
    bodies = body_diagram(p)
    s.gate("B2 exactly one For-loop BODY diagram", len(bodies) == 1, "{0!r}".format(bodies), fatal=True)
    body = bodies[0]
    pn1_uid = [o["uid"] for o in g.report(p, "Property")][0]
    s.fact("B2 body diagram index {0}; PN1 (the GObject reader) #{1}".format(body, pn1_uid))

    s.head("[B3] the `VI Server:Wire` property node, built AT TOP LEVEL so create_control can reach it")
    pn0 = g.uids(p, "Property")
    g.build_property(p, "VI Server:Wire", [(P_BROKEN, False), (P_TERMS, False)], (600, 2400))
    newpn = g.new_since(p, "Property", pn0)
    s.gate("B3 exactly one new Property node", len(newpn) == 1,
           "{0!r}".format([o["uid"] for o in newpn]), fatal=True)
    pn_wire = newpn[0]["uid"]
    w = walk(p, 0)
    outs = sorted(r["name"] for r in w[pn_wire][2]
                  if r["is_source"] and r["name"] not in ("reference out", "error out"))
    s.gate("B3b its data outputs are exactly {0!r}".format(sorted([T_BROKEN, T_TERMS])),
           outs == sorted([T_BROKEN, T_TERMS]), "{0!r}".format(outs), fatal=True)

    s.head("[B4] the WIRE-TYPED SEED: create_control on that node's own `reference`")
    before = ctls(p)
    g.create_control(p, w[pn_wire][0], term(w[pn_wire][2], "reference", False)["i"])
    got = [l for l in ctls(p) if l not in before]
    s.gate("B4 exactly ONE new control = the Wire-typed seed", len(got) == 1, "{0!r}".format(got),
           fatal=True)
    seed = got[0]
    pw = {r["label"]: r for r in g.panel_wiring(p)}
    s.gate("B4b the seed arrived WIRED to that node's `reference`", bool(pw.get(seed, {}).get("wire")),
           "seed {0!r} wire {1}".format(seed, pw.get(seed, {}).get("wire")), fatal=True)

    s.head("[B5] runnable + saved BEFORE copy_by_index (it FILE-copies the target, gscript.py:1556)")
    es = s.es("B5 before the copy")
    s.gate("B5 ExecState 1 before the copy", es == 1, "ExecState {0}".format(es), fatal=True)
    s.safe("g.save(pre-copy intermediate)", lambda: g.save(p))
    s.file_facts("B5 PRE-COPY INTERMEDIATE", p)

    s.head("[B6/F] the To More Specific Class, and ALL the breaking edits, inside `finish`")
    state = {}

    def finish(dst, added):
        add = sorted({o["uid"] if isinstance(o, dict) else o for o in added})
        wd = walk(dst, 0)
        tms = [u for u in add if u in wd and term(wd[u][2], "specific class reference", True)]
        if len(tms) != 1:
            raise Stop("F1 expected ONE new TMSC among {0!r}, got {1!r}".format(add, tms))
        tm = tms[0]
        state["tmsc"] = tm
        print("      F1 new TMSC #{0}".format(tm), flush=True)

        pwd = {r["label"]: r for r in g.panel_wiring(dst)}
        del_net(dst, pwd[seed]["wire"], "F2 ")
        wd = walk(dst, 0)
        pwd = {r["label"]: r for r in g.panel_wiring(dst)}
        if pwd[seed]["wire"] or term(wd[pn_wire][2], "reference", False)["wire"]:
            raise Stop("F2 the seed / the Wire node's `reference` are not both bare after the net delete")

        bod = body_diagram(dst)
        if len(bod) != 1:
            raise Stop("F3 body diagram lookup on the copy gave {0!r}".format(bod))
        B = mod_move()
        B.move_in(dst, tm, bod[0], (1700, 1000))
        B.move_in(dst, pn_wire, bod[0], (1700, 1150))
        owners = {u: owner_of(dst, u) for u in (tm, pn_wire)}
        if not all("Diagram" in str(v) for v in owners.values()):
            raise Stop("F3 after move_in the owners are {0!r} (want Diagram)".format(owners))
        print("      F3 moved into the body; owners {0!r}".format(owners), flush=True)

        g.wire_control(dst, [seed], "Function", idx(dst, "Function", tm), ["target class"])
        g.wire(dst, "Property", idx(dst, "Property", pn1_uid), "reference out",
               "Function", idx(dst, "Function", tm), "reference")
        g.wire(dst, "Function", idx(dst, "Function", tm), "specific class reference",
               "Property", idx(dst, "Property", pn_wire), "reference")
        wd = walk(dst, bod[0])
        a = term(wd[tm][2], "reference", False)["wire"]
        b = term(wd[tm][2], "specific class reference", True)["wire"]
        c = term(wd[pn_wire][2], "reference", False)["wire"]
        if not (a and b and b == c):
            raise Stop("F4 wires not on both ends: PN1->TMSC w{0}, TMSC->WirePN {1} vs {2}".format(a, b, c))
        print("      F4 PN1 -> TMSC w{0}; TMSC -> WirePN w{1}".format(a, b), flush=True)

        tun0 = g.count(dst, "LoopTunnel")
        g.exit_loop(dst, idx(dst, "Property", pn_wire), [T_BROKEN], bod[0], node_class="Property")
        tun1 = g.count(dst, "LoopTunnel")
        if tun1 != tun0 + 1:
            raise Stop("F5 exit_loop LoopTunnel {0} -> {1}, wanted +1".format(tun0, tun1))
        new_tun = tun1 - 1
        before_ind = ctls(dst, indicators=True)
        g.set_index_mode(dst, new_tun, 1)
        g.tunnel_indicator(dst, new_tun)
        state["indicator"] = [l for l in ctls(dst, indicators=True) if l not in before_ind]
        state["tunnel"] = new_tun
        print("      F5 tunnel {0} -> indicator {1!r}; ExecState in finish {2}".format(
            new_tun, state["indicator"], g.exec_state(dst)), flush=True)

    def mod_move():
        return K.mod("build_d1_v0")

    s.safe("close_panel before the copy", lambda: g.close_panel(p))
    res, cerr = s.safe("copy_by_index(TMSC)",
                       lambda: g.copy_by_index(EX, "Function", EX_TMSC_FN_INDEX, p,
                                               expect_uid=EX_TMSC_UID, finish=finish), None)
    added, sel = res if res else (None, None)
    if cerr:
        s.fact("B6 copy_by_index raised: {0}".format(cerr))
    s.gate("B6 copy_by_index completed and finish wired everything (it refuses to save below ExecState 1)",
           bool(state.get("tunnel") is not None and added),
           "added {0!r} selected {1!r} state {2!r}".format(added, sel, state), fatal=True)
    g.reset()                      # the file on disk was replaced by copy_by_index; drop every cached ref
    time.sleep(1.0)
    s.safe("revert to the file copy_by_index wrote", lambda: g.revert(p))
    s.safe("open_panel after the copy", lambda: g.open_panel(p))
    time.sleep(1.0)

    s.head("[B7] the assembled op")
    cen2 = {c: g.count(p, c) for c in ("ForLoop", "LoopTunnel", "Property", "SubVI", "Function",
                                       "ControlTerminal", "Wire", "Diagram")}
    s.fact("B7 census {0!r} (was {1!r})".format(cen2, cen))
    s.gate("B7 Property 2->3, LoopTunnel 5->7 (one in for the seed, one out for Broken?), Function +1",
           cen2["Property"] == 3 and cen2["LoopTunnel"] >= 6 and cen2["Function"] == cen["Function"] + 1,
           "{0!r}".format(cen2))
    s.save()
    label_map = {"wire_uid": "Array 2", "is_broken": (state.get("indicator") or [None])[0],
                 "class_name_input": "Class Name", "vi_path_input": "vi path",
                 "seed_control": seed, "tunnel_index": state.get("tunnel"),
                 "note": "Array/Array 2/Array 3/Array 4 are the donor's Position/UID/ClassName/OwnerClass "
                         "(tools/bench/opreportall_labels.json); the new one carries Wire.Is Broken? 6371004"}
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(label_map, f, indent=1)
    s.fact("B7 label map -> {0}: {1!r}".format(MAP_OUT, label_map))
    s.R["label_map"] = label_map


S = K.Stage(DONOR, DONOR_MD5, "build_opallwires_v0", work_name=OP_NAME, fresh=True, preload=False,
            deadline_min=28.0, reserve_s=300.0,
            out_json=os.path.join(ROOT, "bench", "build_opallwires_v0.json"),
            task="STAGE A of OpAllWires_v0: every wire's uid and Wire.Is Broken? in ONE round trip, "
                 "built additively on OpReportAll_v0. Nothing but the new op file is written.")
if os.path.exists(S.work):
    try:
        os.remove(S.work)
    except OSError as e:
        print("could not remove the previous {0}: {1}".format(OP_NAME, e), flush=True)
sys.exit(K.run(main, S))
