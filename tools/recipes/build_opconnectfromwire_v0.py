r"""build_opconnectfromwire_v0.py - `OpConnectFromWire_v0.vi`: `Terminal.Connect Wire` 6349C03 whose **SOURCE is a
terminal taken from an EXISTING WIRE** (`Wire.Terms[]` 6371003, picked by index), and whose SINK is a node terminal
addressed purely by INDEX on a nested diagram. `docs/d1-build-plan.md` §11t, route B's first item.

    MATERIAL=1 py tools/bgrun.py --max-min 40 --log tools/bench/build_opconnectfromwire_v0.log \
        -- py -u tools/recipes/build_opconnectfromwire_v0.py

WHY IT EXISTS. **16** of the D1 re-wire rows - not 18, corrected by `archive/peer/2026-09-17-priorart-priorart-
cfw-recipe.md` A3 against `tools/bench/d1_tunnel_sources.json` - have a source owned by `FlatSequenceInnerTunnel`
(**14**) or `LeftShiftRegister` of `#637` (**2**), classes that are on NO `Diagram.Nodes[]`, so no index-addressed
writer can name them. The other two of run 9's 18 NO-ROUTE rows are NOT this op's business: `#2222` t0 is a PANEL
CONTROL source (`build_d1_v0_run9.log:324`) and `#376` t7's `LoopTunnel` hop does not advance
(`d1-build-plan.md` §11s.1). codex
(`archive/peer/2026-09-17-flatseq-tunnel-source-addressing-r3.md`, ANSWERED) says `Connect Wire`'s `Wire Source`
takes ANY Terminal reference, including one from `Wire.Terminals[]`. This op is that writer.

WHAT ALREADY EXISTS - checked before a line was written, and the prior-art review
(`archive/peer/2026-09-17-priorart-priorart-connectfromwire.md`, 6 findings, 0 novel, all dispositioned) checked it
again: no `OpConnectFromWire` / `OpWireRef` is on disk; `OpConnect*` are all node-index or panel-index addressed.
Nothing here is hand-rolled - `gscript` supplies `drop_subvi`, `build_property`, `build_index_array`,
`create_control`, `create_indicator`, `copy_by_index`, `wire`, `wire_control`, `delete_object`,
`remove_bad_wires_scripted`, `set_auto_error_handling`; `build_opconnectnested_v1` supplies `walk`, `term`,
`src_of`, `cls_of`, `idx`, `connect`, `del_net`, `ladder_from`.

THE CONSTRUCTION - ADDITIVE on `OpConnectNested_v1.vi`, nothing deleted except ONE wire.
MEASURED topology of both halves, `tools/bench/diag_connectfromwire_facts.log` (A1-A4, this session):
  v1 (21 nodes): `Open VI Reference` #43 (`vi reference` w467) -> `Traverse` #124 -> IA #308(`index`) -> TMSC #683
     -> SINK ladder #235/#236/#237/#239 -> Invoke #757 `reference`;  IA #645(`index 6`) -> TMSC #1045 -> SOURCE
     ladder #744/#750/#751/#753 -> Invoke #757 `Wire Source` (wire w969).
  v5 front half: `UID to GObject Reference.vi` #990 (`Owning VI` <- w467, `UID` <- a control, `GObject` out)
     -> TMSC #1044 (`target class` <- a Wire-typed refnum SEED) -> `Wire.Terms[]` PN #145 -> IA #151 -> a
     TERMINAL reference.
So: build the v5 front half fresh inside a copy of v1 and re-point the Invoke's `Wire Source` at it.

⚠️ THE OLD SOURCE LADDER IS **NOT DELETED**, on purpose. Deleting five nodes means re-stitching an error chain for
no gain: `#744`/`#751`'s `error out` terminals are MEASURED unwired (`diag_connectfromwire_facts.log` N[13],
N[15]), so the dead ladder cannot propagate an error into the Invoke, and `index 4/5/6` may be left at 0. Keeping
it also keeps `Wire Source` fed while `copy_by_index` needs the op at ExecState 1 (`copy_by_index` copies the
FILE - the same constraint `build_opconnectnested_v1.py` gate V4 records).

THE ACCEPTANCE GATE, CHANGED BEFORE THE BUILD by the prior-art review's B4 `already-measured` and by
`archive/peer/2026-09-17-rbw-deleted-wires-run9.md` (codex, ANSWERED, accepted in full):
  * ❌ NOT "the wire survives `remove_bad_wires_scripted`" **as implemented** - that check compares two
    `Terminal.Connected Wire` reads, i.e. object identity. `Terminal.Connect Wire` returns nothing, and run 9's
    `#1359` t4 was counted "deleted" while ending with a NON-ZERO wire (`26189 -> 26412`).
  * ✅ INSTEAD, the list `archive/peer/2026-09-01-2026-09-01-opwireref-donor-plan-attack.md:89` asked for, which
    needs no new op: (a) each endpoint's `Connected Wire` state - the sink goes 0 -> NON-ZERO and is still
    NON-ZERO after RBW (that is sound; only uid EQUALITY was not); (b) each endpoint's owning diagram; (c) the
    target VI is not broken - `ExecState`, reported for the scratch and GATED where the scratch is runnable;
    (d) the new wire's SOURCE terminal is read back with `OpWireSource_v5` and must be the object we asked for.
  ✅ **AND `Wire.Is Broken?` 6371004 AFTER ALL - it needs no second op.** `archive/peer/2026-09-17-priorart-
    priorart-cfw-recipe.md` A1 (`already-built`) found it INSIDE the VI this build copies: node **#242** reads
    `UID` + `Broken?` off node **#241**'s `Wire` output, and #241's `reference` is w572 - the SINK terminal
    itself. Both are already on the panel as `UID 2` and `Is Broken?`. The only thing missing is ORDER: #241's
    `error in (no error)` is unwired, so it may run BEFORE the Connect Wire and read the OLD wire - which is
    exactly why every run-9 readback printed `'UID 2': 0` (`build_d1_v0_run9.log:260-267`). **W7b** branches the
    Invoke's own `error out` into #241's `error in (no error)`, which forces the read to happen after the write,
    and `connect_from_wire` returns both values. My earlier sentence "that is a SECOND op, NOT BUILT" is
    WITHDRAWN.

BUILD GATES (each fatal unless marked; nothing saved on a miss; donors never written)
 W0  `OpConnectNested_v1.vi` at ExecState 1; `UID to GObject Reference.vi` and the NI example on disk; md5s taken.
 W1  copy -> `OpConnectFromWire_v0.vi`; 21 nodes, exactly TWO TMSC, one Invoke, `Wire Source` fed by an
     Index Array; the SOURCE ladder identified BY WIRE TOPOLOGY (`ladder_from`), never by uid.
 W2  `drop_subvi(UID to GObject Reference.vi)` -> exactly ONE new SubVI carrying `GObject`/`Owning VI`/`UID`.
 W3  `Open VI Reference`'s `vi reference` -> the new subVI's `Owning VI` (BRANCH; same wire uid on both ends).
 W4  `create_control` on its `UID` -> exactly ONE new control = the source WIRE's uid input.
 W5  `build_property("VI Server:Wire", 6371003)` -> ONE Property node whose data output is `Terms[]`.
 W6  `create_control` on that node's `reference` -> exactly ONE new control = the WIRE-TYPED SEED, arriving wired.
 W7  two indicators on the two new `error out` terminals (the op must be able to say why it failed).
 W8  ExecState 1 and SAVE - required before `copy_by_index`.
 W9  `copy_by_index(NI example, "Function", 6, expect_uid=99)` -> a THIRD TMSC; in `finish`: delete the seed's
     wire, seed -> new TMSC `target class`, subVI `GObject` -> new TMSC `reference`, new TMSC
     `specific class reference` -> the `Terms[]` node's `reference`; ExecState inside finish reported.
 W10 `build_index_array` + `Terms[]` -> `array` + a new `index` control.
 W11 delete the wire on the Invoke's `Wire Source`; wire the new Index Array's `element` there instead.
 W12 auto error handling OFF; ExecState 1; save; labels JSON; donor md5s unchanged.

FUNCTIONAL TEST
 T1  scratch copy of `EMPTY_v0.vi` (unique name, deleted in the same run): an outer wire `A.error out ->
     B.error in` on diagram 0, a While loop, a third copy of the same subVI in its BODY. Branch from the outer
     wire's SOURCE terminal into the body node's `error in` - the exact shape route B's 18 rows need. Gates:
     op error empty; sink wire 0 -> non-zero; still non-zero after RBW; the new wire's source terminal read back
     through `OpWireSource_v5` is owned by subVI A.
 T2  a fresh working COPY of the original (never the original): source = wire **w5812**, whose only source
     terminal is owned by `FlatSequenceInnerTunnel` **#5818** (MEASURED, `d1_tunnel_sources.json` row 1) - the
     class the whole op exists for. Sink = `#5540` t1 on `Diagram #639` (Traverse index 43), BARED first. Gates:
     op error empty; sink wire 0 -> non-zero; the new wire's source terminal still owned by #5818.
     ⚠️ ExecState is REPORTED, not gated: a fresh copy of the original already reads 0
     (`diag_connectfromwire_facts.log` B0).
 T3  every scratch deleted in this run; donors' md5 unchanged; the ORIGINAL's md5 read before AND after.
"""
import hashlib
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
sys.path.insert(0, HERE)
import gscript as g                                                              # noqa: E402
from build_opconnectnested_v1 import (walk, term, src_of, cls_of, idx, connect,   # noqa: E402
                                      del_net, ladder_from, Stop)
from bench_prep import labview_handles                                           # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpConnectNested_v1.vi")
OP = os.path.join(g.CLAUDEDEV, "OpConnectFromWire_v0.vi")
V5 = os.path.join(g.CLAUDEDEV, "OpWireSource_v5.vi")
EX = os.path.join(g.CLAUDEDEV, "NIScriptingExamples", "Finding and Modifying Objects", "Navigating Nodes and Wires.vi")
EX_TMSC_UID, EX_TMSC_FN_INDEX = 99, 6
EMPTY = os.path.join(g.CLAUDEDEV, "EMPTY_v0.vi")
UIDVI = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\VIServer\UID to GObject Reference.vi"
NUMVI = (r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Utility\error.llb"
         r"\Error Cluster From Error Code.vi")
ORIGINAL = os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi")
ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"
BENCH = os.path.join(ROOT, "tools", "bench")
MAP_OUT = os.path.join(BENCH, "opconnectfromwire_v0_labels.json")
V5_MAP = os.path.join(BENCH, "opwiresource_v5_labels.json")
STAMP = time.strftime("%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, f"SCRATCH_cfw1_{STAMP}.vi")
WORK = os.path.join(g.CLAUDEDEV, f"SCRATCH_cfw2_{STAMP}.vi")
T2_DIAG_UID = 639
# Candidate rows for T2, all MEASURED in tools/bench/d1_tunnel_sources.json / build_d1_v0_run9.log:321-338.
# (source wire, its source terminal's owner uid, sink node uid, sink terminal index). RUN 1 of this recipe
# measured that the FIRST row's sink cannot be bared by one delete (`wire 5979 -> 5637`), so T2 now walks the
# list and uses the first row it can ACTUALLY bare - the alternative, a freshly dropped subVI as the sink, is
# rejected because its `error in` is the wrong DATA TYPE for these wires and would make a broken wire by
# construction (the very thing the test exists to rule out).
T2_ROWS = [(5812, 5818, 5540, 1), (2731, 2886, 5540, 4), (5174, 5183, 2222, 3), (5336, 5669, 2222, 4),
           (3853, 3862, 5058, 2), (3668, 3675, 5058, 12)]
g._run.__defaults__ = (6.0, 120.0)

passes, fails = [], []


def gate(name, ok, detail="", fatal=False):
    (passes if ok else fails).append(name)
    print(f"  {'PASS' if ok else '**FAIL**'}  {name}{('  ' + detail) if detail else ''}", flush=True)
    if not ok and fatal:
        raise Stop(name)
    return ok


def fact(line):
    print(f"  FACT  {line}", flush=True)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def new_ctl(target, before_labels):
    now = [l for _i, l, ind in g.fp_labels(target) if not ind and l not in before_labels]
    return now


def ctl_labels(target, indicators=False):
    return {l for _i, l, ind in g.fp_labels(target) if bool(ind) == indicators}


# ============================================================================== BUILD
def build():
    print("\n=== W0: donors", flush=True)
    for p, nm in ((SRC, "OpConnectNested_v1.vi"), (V5, "OpWireSource_v5.vi"), (EX, "NI example"),
                  (UIDVI, "UID to GObject Reference.vi"), (EMPTY, "EMPTY_v0.vi"), (NUMVI, "Error Cluster..vi")):
        gate(f"W0 {nm} on disk", os.path.exists(p), p, fatal=True)
    donor_md5, ex_md5 = md5(SRC), md5(EX)
    g.open_panel(SRC)
    es = g.exec_state(SRC)
    gate("W0 donor OpConnectNested_v1 ExecState 1", es == 1, f"ExecState {es}", fatal=True)
    g.close_panel(SRC)

    print("\n=== W1: the copy, and the topology read BY WIRE, never by uid", flush=True)
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(SRC, OP)
    time.sleep(0.3)
    g.report_all(OP, "SubVI")
    g.open_panel(OP)
    time.sleep(0.8)
    w = walk(OP, 0)
    tmscs = [u for u, (n, lab, rows) in w.items() if term(rows, "specific class reference", True)]
    es = g.exec_state(OP)
    # P1z-shaped STALE-IN-MEMORY GUARD (prior-art B1 `already-failed`): a FIXED op path is served from LabVIEW's
    # MEMORY, so a re-run after a mid-build failure can pass an ExecState+TMSC check on a half-built cached VI.
    # The node COUNT and the ABSENCE of this build's own additions are what distinguish a clean donor copy.
    stale = [lab for u, (n, lab, rows) in w.items() if lab and "UID to GObject Reference" in str(lab)]
    gate("W1 the copy is a CLEAN OpConnectNested_v1: ExecState 1, 21 nodes, exactly TWO TMSC, and none of this "
         "build's own additions present",
         es == 1 and len(tmscs) == 2 and len(w) == 21 and not stale,
         f"ExecState {es}, TMSC {tmscs}, {len(w)} nodes, stale additions {stale}", fatal=True)
    inv = next(u for u, (n, lab, rows) in w.items() if lab == "Invoke Node")
    ws_wire = term(w[inv][2], "Wire Source", False)["wire"]
    gate("W1b the Invoke's `Wire Source` is currently fed", bool(ws_wire), f"Invoke #{inv} w{ws_wire}", fatal=True)
    src_lad = ladder_from(w, ws_wire, "OLD SOURCE ")
    ovr = next(u for u, (n, lab, rows) in w.items() if lab == "Open VI Reference")
    vi_ref_w = term(w[ovr][2], "vi reference", True)["wire"]
    fact(f"W1 Invoke #{inv}; old source ladder head TMSC #{src_lad['head']}; "
         f"Open VI Reference #{ovr} 'vi reference' w{vi_ref_w}")

    print("\n=== W2: drop `UID to GObject Reference.vi`", flush=True)
    sv0 = g.uids(OP, "SubVI")
    g.drop_subvi(OP, UIDVI, 0, (200, 2400))
    new_sv = g.new_since(OP, "SubVI", sv0)
    gate("W2 exactly one new SubVI", len(new_sv) == 1, f"{[o['uid'] for o in new_sv]}", fatal=True)
    u_uid = new_sv[0]["uid"]
    w = walk(OP, 0)
    names = {r["name"]: r for r in w[u_uid][2]}
    gate("W2b it carries `GObject` (out), `Owning VI` and `UID` (in)",
         all(k in names for k in ("GObject", "Owning VI", "UID")) and names["GObject"]["is_source"],
         f"#{u_uid} terminals {[(r['i'], r['name'], r['is_source']) for r in w[u_uid][2]]}", fatal=True)

    print("\n=== W3: feed it the VI reference (a BRANCH off Open VI Reference)", flush=True)
    connect(OP, ovr, "vi reference", u_uid, "Owning VI", branch=True, tag="W3 ")

    print("\n=== W4: the source WIRE's uid control", flush=True)
    before = ctl_labels(OP)
    w = walk(OP, 0)
    g.create_control(OP, w[u_uid][0], names["UID"]["i"])
    got = new_ctl(OP, before)
    gate("W4 exactly ONE new control = the source wire's UID", len(got) == 1, f"{got}", fatal=True)
    wire_uid_ctl = got[0]

    print("\n=== W5: the `Wire.Terms[]` property node", flush=True)
    pn0 = g.uids(OP, "Property")
    g.build_property(OP, "VI Server:Wire", [("6371003", False)], (600, 2400))
    newpn = g.new_since(OP, "Property", pn0)
    gate("W5 exactly one new Property node", len(newpn) == 1, f"{[o['uid'] for o in newpn]}", fatal=True)
    pn_wire = newpn[0]["uid"]
    w = walk(OP, 0)
    outs = [r["name"] for r in w[pn_wire][2] if r["is_source"] and r["name"] not in ("reference out", "error out")]
    gate("W5b its data output is `Terms[]`", outs == ["Terms[]"], f"{outs}", fatal=True)

    print("\n=== W6: the WIRE-TYPED SEED (create_control on that node's own `reference`)", flush=True)
    before = ctl_labels(OP)
    g.create_control(OP, w[pn_wire][0], term(w[pn_wire][2], "reference", False)["i"])
    got = new_ctl(OP, before)
    gate("W6 exactly ONE new control = the Wire-typed seed", len(got) == 1, f"{got}", fatal=True)
    seed = got[0]
    pw = {r["label"]: r for r in g.panel_wiring(OP)}
    gate("W6b the seed arrived WIRED to the `Terms[]` node's `reference`", bool(pw.get(seed, {}).get("wire")),
         f"seed {seed!r} wire {pw.get(seed, {}).get('wire')}", fatal=True)

    print("\n=== W7: one indicator on each new error out", flush=True)
    err_inds = {}
    for uid, tag in ((u_uid, "uidvi"), (pn_wire, "wirepn")):
        w = walk(OP, 0)
        t = term(w[uid][2], "error out", True)
        if not t or t["wire"]:
            fact(f"W7 #{uid} ({tag}) `error out` missing or already wired - skipped")
            continue
        before = ctl_labels(OP, indicators=True)
        g.create_indicator(OP, w[uid][0], t["i"])
        now = [l for _i, l, ind in g.fp_labels(OP) if ind and l not in before]
        if len(now) == 1:
            err_inds[tag] = now[0]
        fact(f"W7 #{uid} ({tag}) error indicator {now}")
    gate("W7 both new error outs carry an indicator", len(err_inds) == 2, f"{err_inds}")

    print("\n=== W7b: ORDER the built-in `Is Broken?` readout AFTER the write (prior-art A1)", flush=True)
    w = walk(OP, 0)
    readers = [u for u, (n, lab, rows) in w.items()
               if term(rows, "Wire", True) and (term(rows, "reference", False) or {}).get("wire")
               == term(w[inv][2], "reference", False)["wire"]]
    gate("W7b exactly one Property node reads `Wire` off the SINK terminal reference", len(readers) == 1,
         f"{readers}", fatal=True)
    pn_read = readers[0]
    ein = term(w[pn_read][2], "error in (no error)", False)
    gate("W7b2 its `error in (no error)` is currently UNWIRED (that is why run 9 read `UID 2: 0`)",
         bool(ein) and ein["wire"] == 0, f"#{pn_read} error in w{ein and ein['wire']}", fatal=True)
    connect(OP, inv, "error out", pn_read, "error in (no error)", branch=True, tag="W7b ")
    fact(f"W7b Invoke #{inv} `error out` now also drives #{pn_read} `error in` - the `Is Broken?` / `UID 2` "
         f"readback is forced to run AFTER `Connect Wire`")

    print("\n=== W8: runnable + saved BEFORE copy_by_index (it copies the FILE)", flush=True)
    es = g.exec_state(OP)
    gate("W8 ExecState 1 before the copy", es == 1, f"ExecState {es}", fatal=True)
    g.save(OP)
    fact(f"W8 saved intermediate ({os.path.getsize(OP)} B); seed {seed!r}, wire-uid control {wire_uid_ctl!r}")

    print("\n=== W9: the THIRD To More Specific Class (copy_by_index, the proven route)", flush=True)
    state = {}

    def finish(dst, added):
        add_uids = sorted({o["uid"] if isinstance(o, dict) else o for o in added})
        wd = walk(dst, 0)
        new_tm = [u for u in add_uids if u in wd and term(wd[u][2], "specific class reference", True)]
        if len(new_tm) != 1:
            raise Stop(f"W9 expected exactly ONE new TMSC among {add_uids}, got {new_tm}")
        tm3 = new_tm[0]
        state["tm3"] = tm3
        print(f"      W9 new TMSC #{tm3} Nodes[{wd[tm3][0]}]", flush=True)
        pwd = {r["label"]: r for r in g.panel_wiring(dst)}
        del_net(dst, pwd[seed]["wire"], "W9a ")
        wd = walk(dst, 0)
        pwd = {r["label"]: r for r in g.panel_wiring(dst)}
        if pwd[seed]["wire"] or term(wd[pn_wire][2], "reference", False)["wire"]:
            raise Stop("W9a the seed / the Terms[] reference are not both free after the net delete")
        g.wire_control(dst, [seed], "Function", idx(dst, "Function", tm3), ["target class"])
        wd = walk(dst, 0)
        pwd = {r["label"]: r for r in g.panel_wiring(dst)}
        a, b = pwd[seed]["wire"], term(wd[tm3][2], "target class", False)["wire"]
        if not (a and a == b):
            raise Stop(f"W9b seed -> new TMSC `target class` not on both ends ({a} vs {b})")
        print(f"      W9b seed {seed!r} -> TMSC #{tm3} 'target class': wire {a} OK", flush=True)
        connect(dst, u_uid, "GObject", tm3, "reference", tag="W9c ")
        connect(dst, tm3, "specific class reference", pn_wire, "reference", tag="W9d ")
        print(f"      W9 ExecState inside finish: {g.exec_state(dst)}", flush=True)

    g.close_panel(OP)
    added, sel = g.copy_by_index(EX, "Function", EX_TMSC_FN_INDEX, OP, expect_uid=EX_TMSC_UID, finish=finish)
    fact(f"W9 copy_by_index added {sorted({o['uid'] if isinstance(o, dict) else o for o in added})}, "
         f"selected uid {sel}; new TMSC #{state.get('tm3')}")
    g.open_panel(OP)
    time.sleep(0.8)

    print("\n=== W10: the Index Array that picks the terminal ON THE WIRE", flush=True)
    ia0 = g.uids(OP, "IndexArray")
    g.build_index_array(OP, (900, 2400))
    new_ia = g.new_since(OP, "IndexArray", ia0)
    gate("W10 exactly one new Index Array", len(new_ia) == 1, f"{new_ia}", fatal=True)
    ia_w = new_ia[0]["uid"]
    connect(OP, pn_wire, "Terms[]", ia_w, "array", tag="W10 ")
    before = ctl_labels(OP)
    w = walk(OP, 0)
    g.create_control(OP, w[ia_w][0], term(w[ia_w][2], "index", False)["i"])
    got = new_ctl(OP, before)
    gate("W10b exactly ONE new control = the terminal index on the wire", len(got) == 1, f"{got}", fatal=True)
    term_ctl = got[0]

    print("\n=== W11: re-point the Invoke's `Wire Source`", flush=True)
    w = walk(OP, 0)
    ws_wire = term(w[inv][2], "Wire Source", False)["wire"]
    del_net(OP, ws_wire, "W11 ")
    w = walk(OP, 0)
    gate("W11a the Invoke's `Wire Source` is BARE", term(w[inv][2], "Wire Source", False)["wire"] == 0,
         f"w{term(w[inv][2], 'Wire Source', False)['wire']}", fatal=True)
    connect(OP, ia_w, "element", inv, "Wire Source", tag="W11 ")

    print("\n=== W12: save", flush=True)
    # FATAL, not a warning (prior-art A2 `contradicted`): the dead source ladder's `error out` terminals are
    # UNWIRED, and gscript.py:1292-1293 records that an unwired error OUT which RECEIVES an error is exactly what
    # raises a modal dialog - which hangs every later COM call. Auto error handling OFF is the only defence this
    # op has, so a failure to turn it off must stop the build, not be noted.
    aeh_ok = True
    try:
        g.set_auto_error_handling(OP, False)
    except Exception as e:
        aeh_ok = False
        fact(f"set_auto_error_handling failed ({str(e)[:60]})")
    gate("W12a auto error handling is OFF (the dead source ladder's error outs are unwired)", aeh_ok, fatal=True)
    es = g.exec_state(OP)
    gate("W12 ExecState 1 - the op is runnable", es == 1, f"ExecState {es}", fatal=True)
    g.save(OP)
    labels = {"route": "wire-terminal-source", "vi_path": "vi path", "class_name": "Class Name",
              "sink_diag": "index", "sink_node": "index 2", "sink_term": "index 3",
              "dead_src_node": "index 4", "dead_src_term": "index 5", "dead_src_diag": "index 6",
              "wire_uid": wire_uid_ctl, "wire_term_index": term_ctl, "seed": seed,
              "err_uidvi": err_inds.get("uidvi", ""), "err_wirepn": err_inds.get("wirepn", ""),
              "method": "6349C03", "wire_terms_prop": "6371003",
              "panel": [(i, lbl, ind) for i, lbl, ind in g.fp_labels(OP)]}
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=1)
    fact(f"W12 saved {OP} ({os.path.getsize(OP)} bytes); labels -> {MAP_OUT}")
    gate("W12b donor OpConnectNested_v1.vi md5 unchanged", md5(SRC) == donor_md5, donor_md5)
    gate("W12c NI example md5 unchanged", md5(EX) == ex_md5, ex_md5)
    g.close_panel(OP)
    return labels


# ============================================================================== the wrapper
def connect_from_wire(target, wire_uid, term_index, sink_diag, sink_node, sink_term, labels):
    """Wire the SOURCE terminal `Wire(uid=wire_uid).Terms[term_index]` into
    Diagram[sink_diag].Nodes[sink_node].Terminals[sink_term]. Returns (wire delta, ExecState, error, op errors)."""
    w0 = g.count(target, "Wire")
    vi = g.op(OP)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", "Diagram")
    vi.SetControlValue(labels["sink_diag"], int(sink_diag))
    vi.SetControlValue(labels["sink_node"], int(sink_node))
    vi.SetControlValue(labels["sink_term"], int(sink_term))
    vi.SetControlValue(labels["wire_uid"], int(wire_uid))
    vi.SetControlValue(labels["wire_term_index"], int(term_index))
    for k in (labels["dead_src_node"], labels["dead_src_term"], labels["dead_src_diag"]):
        try:
            vi.SetControlValue(k, 0)
        except Exception:
            pass
    for k, v in (("error in (no error)", (False, 0, "")), ("error in", (True, 1, "neutralised creator")),
                 ("Class Name 3", ""), ("Class Name 2", "")):
        try:
            vi.SetControlValue(k, v)
        except Exception:
            pass
    err = ""
    try:
        g._run(vi)
        err = g._err(vi, "error out") or ""
    except RuntimeError as e:
        err = "modal dialog (dismissed)" if "modal dialog" in str(e) else f"EXC {str(e)[:140]}"
    sub = {}
    for k in ("err_uidvi", "err_wirepn"):
        if labels.get(k):
            sub[k] = g._err(vi, labels[k]) or ""
    # the op's OWN `Wire.Is Broken?` 6371004 readout, now ORDERED after the write by W7b (prior-art A1).
    for k in ("UID 2", "Is Broken?", "Name"):
        try:
            sub[k] = vi.GetControlValue(k)
        except Exception:
            pass
    return g.count(target, "Wire") - w0, g.exec_state(target), err, sub


def wire_source_owner(target, wire_uid, n=6):
    """`OpWireSource_v5` on `target`: the owner of the wire's single SOURCE terminal. Read-only.
    NOTE the caller bug this project recorded twice: the op is UID-addressed, so `UID 2` MUST be set
    (docs/toolkit-capabilities.md:48, :51).

    REPAIRED (STATUS NEXT 2026-09-22; `archive/peer/2026-09-22-c71-run3.md` §2; measured unsound by
    `tools/bench/diag_c68_quote_echo.log` [E]): the wrapper used to read four answer indicators and NO
    error output, so on an unresolvable uid it returned the PREVIOUS call's rows (history-determined).
    Now, per call: (1) the answer indicators are SCRUBBED to sentinels before the run, so a run that
    dies early cannot leave last call's answer readable; (2) every mapped `error out *` is read after
    the run; (3) the op's own uid echo (`uid_back`, "UID 3") must equal the queried uid — a mismatch,
    or any op error, yields an explicit `unresolved`/`err` row carrying NO owner fields, never a stale
    answer. Acceptance test: `tools/bench/diag_c68_quote_echo.py` [E] ghost reads must return null."""
    with open(V5_MAP, encoding="utf-8") as f:
        lab = json.load(f)
    vi = g.op(V5)
    err_keys = [k for k in ("errT", "errO", "errU", "errL", "errG", "errS", "errWU", "errCO")
                if lab.get(k)]
    out = []
    for i in range(n):
        # (1) scrub the answer indicators — a failed run must not leave the previous answer readable
        for k, v in ((lab["uid_back"], 0), (lab["owner_uid"], 0), (lab["recip_wire"], 0),
                     (lab["is_source"], False), (lab["ownercls"], "")):
            try:
                vi.SetControlValue(k, v)
            except Exception:
                pass
        try:
            vi.SetControlValue("vi path", target)
            vi.SetControlValue(lab["uid_in"], int(wire_uid))
            vi.SetControlValue(lab["term_index"], i)
            g._run(vi)
            # (2) the op's error outputs — the review's §2: no error was ever read here
            errs = "; ".join("%s=%s" % (k, e) for k in err_keys
                             for e in (g._err(vi, lab[k]),) if e)
            # (3) the uid echo — the op says which uid it actually matched
            uid_back = None
            try:
                uid_back = int(vi.GetControlValue(lab["uid_back"]))
            except Exception:
                pass
            if uid_back != int(wire_uid):
                out.append(dict(i=i, unresolved=True, uid_back=uid_back,
                                err=errs or "uid echo %r != queried %r" % (uid_back, wire_uid)))
                break
            if errs:
                # uid resolved but the op errored (e.g. term index out of range): the answer
                # indicators may hold the PREVIOUS iteration's row — report the error, no owner fields
                out.append(dict(i=i, err=errs))
                break
            r = dict(i=i, is_source=bool(vi.GetControlValue(lab["is_source"])),
                     owner_class=vi.GetControlValue(lab["ownercls"]),
                     owner_uid=int(vi.GetControlValue(lab["owner_uid"])),
                     recip=int(vi.GetControlValue(lab["recip_wire"])))
        except Exception as e:
            out.append(dict(i=i, err=str(e)[:70]))
            break
        out.append(r)
        if not r["owner_uid"] and not r["is_source"]:
            break
    return out


# ============================================================================== FUNCTIONAL TEST
def t1(labels):
    print("\n=== T1: branch from an OUTER wire into a node inside a NEW While loop (scratch EMPTY_v0)", flush=True)
    if os.path.exists(SCRATCH):
        os.remove(SCRATCH)
    shutil.copyfile(EMPTY, SCRATCH)
    time.sleep(0.3)
    g.report_all(SCRATCH, "SubVI")
    g.open_panel(SCRATCH)
    time.sleep(0.8)
    sv0 = g.uids(SCRATCH, "SubVI")
    g.drop_subvi(SCRATCH, NUMVI, 0, (200, 200))
    A = g.new_since(SCRATCH, "SubVI", sv0)[0]["uid"]
    sv1 = g.uids(SCRATCH, "SubVI")
    g.drop_subvi(SCRATCH, NUMVI, 0, (900, 200))
    Bu = g.new_since(SCRATCH, "SubVI", sv1)[0]["uid"]
    dg0 = g.uids(SCRATCH, "Diagram")
    g.while_loop(SCRATCH, (200, 800))
    nD = g.new_since(SCRATCH, "Diagram", dg0)
    gate("T1a two subVIs on diagram 0 and one new While-loop body diagram", len(nD) == 1,
         f"A #{A} B #{Bu}; new diagrams {[o['uid'] for o in nD]}", fatal=True)
    body = [o["uid"] for o in g.report_all(SCRATCH, "Diagram")].index(nD[0]["uid"])
    sv2 = g.uids(SCRATCH, "SubVI")
    g.drop_subvi(SCRATCH, NUMVI, body, (60, 60))
    C = g.new_since(SCRATCH, "SubVI", sv2)[0]["uid"]
    w0 = walk(SCRATCH, 0)
    t_out = term(w0[A][2], "error out", True)
    t_in = term(w0[Bu][2], "error in (no error)", False)
    gate("T1b the outer pair has `error out` / `error in (no error)`", bool(t_out) and bool(t_in),
         f"{t_out} / {t_in}", fatal=True)
    connect(SCRATCH, A, "error out", Bu, "error in (no error)", tag="T1 ")
    w0 = walk(SCRATCH, 0)
    outer_wire = term(w0[A][2], "error out", True)["wire"]
    fact(f"T1 outer wire w{outer_wire} (A #{A}.error out -> B #{Bu}.error in)")
    terms = wire_source_owner(SCRATCH, outer_wire)
    srcs = [r for r in terms if r.get("is_source") and r.get("recip") == outer_wire]
    fact(f"T1 OpWireSource_v5 on w{outer_wire}: {terms}")
    gate("T1c the outer wire has exactly ONE source terminal, owned by subVI A", len(srcs) == 1
         and srcs[0]["owner_uid"] == A, f"{srcs} vs A #{A}")
    src_i = srcs[0]["i"] if srcs else 0
    wb = walk(SCRATCH, body)
    n_c, _l, rowsC = wb[C]
    t_c = term(rowsC, "error in (no error)", False)
    gate("T1d the body node has a BARE `error in (no error)`", bool(t_c) and t_c["wire"] == 0,
         f"{t_c}", fatal=True)
    es_before = g.exec_state(SCRATCH)
    lt_before = g.count(SCRATCH, "LoopTunnel")
    dw, es, err, sub = connect_from_wire(SCRATCH, outer_wire, src_i, body, n_c, t_c["i"], labels)
    wb = walk(SCRATCH, body)
    after = next((r["wire"] for r in wb[C][2] if r["i"] == t_c["i"]), 0)
    fact(f"T1 op error {err[:160]!r}; sub-errors {sub}; wire delta {dw}; "
         f"LoopTunnel {lt_before} -> {g.count(SCRATCH, 'LoopTunnel')}; ExecState {es_before} -> {es}")
    gate("T1e the op reported NO error", not err, f"{err[:200]!r} {sub}")
    gate("T1f the body node's `error in` went 0 -> NON-ZERO", bool(after), f"wire {after}")
    gate("T1f2 the op's OWN `Wire.Is Broken?` 6371004 on the created wire reads FALSE (ordered by W7b) - THIS is "
         "the sound gate, not uid equality after RBW", sub.get("Is Broken?") is False,
         f"Is Broken? {sub.get('Is Broken?')!r}, UID 2 {sub.get('UID 2')!r}")
    g.remove_bad_wires_scripted(SCRATCH)
    wb = walk(SCRATCH, body)
    after2 = next((r["wire"] for r in wb[C][2] if r["i"] == t_c["i"]), 0)
    gate("T1g it still carries a wire AFTER Remove Bad Wires (non-zero; uid EQUALITY is not the test - §11u.1)",
         bool(after2), f"wire {after} -> {after2}, ExecState {g.exec_state(SCRATCH)}")
    if after2:
        fact(f"T1h OpWireSource_v5 on the NEW wire w{after2}: {wire_source_owner(SCRATCH, after2)}")
    fact(f"T1 scratch ExecState {g.exec_state(SCRATCH)} (REPORTED, not gated: a While loop whose conditional "
         f"terminal is unwired is a broken VI by itself - build_opstopfromnode_v0.py:438-441)")


def t2(labels):
    print("\n=== T2: a source wire whose only source terminal is owned by a FlatSequenceInnerTunnel", flush=True)
    if os.path.exists(WORK):
        os.remove(WORK)
    shutil.copyfile(ORIGINAL, WORK)
    time.sleep(0.4)
    g.open_panel(WORK)
    time.sleep(1.2)
    fact(f"T2 working copy {os.path.basename(WORK)} ExecState {g.exec_state(WORK)} "
         f"(a fresh copy already reads 0 - diag_connectfromwire_facts.log B0)")
    d = [o["uid"] for o in g.report_all(WORK, "Diagram")].index(T2_DIAG_UID)

    def bare(uid, t_i):
        """Delete wires off one sink terminal until it reads 0. RUN 1 MEASURED that ONE delete is not enough on a
        structure tunnel (`#5540` t1: `wire 5979 -> 5637`) - a cross-boundary net is several Wire objects, so the
        terminal picks up the next segment. Returns (the sequence of uids seen, the final value)."""
        seq = []
        for _ in range(6):
            rows = g.node_terms(WORK, d, uid)
            w_now = next((r["wire"] for r in rows if r["i"] == t_i), 0)
            seq.append(w_now)
            if not w_now:
                return seq, 0
            order = [o["uid"] for o in g.report_all(WORK, "Wire")]
            if w_now not in order:
                return seq, w_now
            g.delete_object(WORK, "Wire", order.index(w_now), verify=False)
            g.remove_bad_wires_scripted(WORK)
        rows = g.node_terms(WORK, d, uid)
        last = next((r["wire"] for r in rows if r["i"] == t_i), 0)
        seq.append(last)
        return seq, last

    wd = walk(WORK, d)
    chosen = None
    for src_wire, owner, sink_uid, sink_t in T2_ROWS:
        if sink_uid not in wd:
            fact(f"T2 candidate #{sink_uid} not on Diagram[{d}] - skipped")
            continue
        n_i = wd[sink_uid][0]
        seq, last = bare(n_i, sink_t)
        fact(f"T2 candidate sink #{sink_uid} t{sink_t} on Diagram[{d}].N[{n_i}]: wire sequence {seq}")
        if last == 0:
            chosen = (src_wire, owner, sink_uid, sink_t, n_i)
            break
        # METHOD FIX (archive/peer/2026-09-17-wireinputs-forloop-tunnel-name.md): never measure past a sink that
        # is not ACTUALLY bare - that is how this session drew a wrong conclusion once already today.
        fact(f"T2 candidate #{sink_uid} t{sink_t} could NOT be bared in 6 deletes - moving to the next row")
        wd = walk(WORK, d, )
    if not gate("T2a2 at least one measured from-tunnel sink could be bared to wire 0 (fatal - nothing is "
                "measured past a sink that is still occupied)", chosen is not None,
                f"tried {[(r[2], r[3]) for r in T2_ROWS]}", fatal=False):
        return
    src_wire, owner, sink_uid, sink_t, n_i = chosen
    T2_WIRE, T2_OWNER = src_wire, owner
    # prior-art B2 `unread-evidence`: read the SOURCE wire AFTER the delete + Remove Bad Wires, never before -
    # a uid taken before a topology change is exactly the staleness §11u.1 is about.
    terms = wire_source_owner(WORK, T2_WIRE)
    srcs = [r for r in terms if r.get("is_source") and r.get("recip") == T2_WIRE]
    fact(f"T2 OpWireSource_v5 on w{T2_WIRE}, re-read AFTER baring the sink: {terms}")
    if not gate(f"T2a w{T2_WIRE}'s single source terminal is owned by FlatSequenceInnerTunnel #{T2_OWNER}",
                len(srcs) == 1 and srcs[0]["owner_uid"] == T2_OWNER
                and "FlatSequence" in str(srcs[0]["owner_class"]), f"{srcs}"):
        return
    src_i = srcs[0]["i"]
    dw, es, err, sub = connect_from_wire(WORK, T2_WIRE, src_i, d, n_i, sink_t, labels)
    rows = g.node_terms(WORK, d, n_i)
    after = next((r["wire"] for r in rows if r["i"] == sink_t), 0)
    fact(f"T2 sink #{sink_uid} t{sink_t}: op error {err[:160]!r}; sub-errors {sub}; wire delta {dw}; ExecState {es}")
    gate("T2b the op reported NO error", not err, f"{err[:200]!r} {sub}")
    gate("T2c the sink terminal went 0 -> NON-ZERO", bool(after), f"wire 0 -> {after}")
    gate("T2c2 the op's OWN `Wire.Is Broken?` 6371004 on the created wire reads FALSE (ordered by W7b)",
         sub.get("Is Broken?") is False, f"Is Broken? {sub.get('Is Broken?')!r}, UID 2 {sub.get('UID 2')!r}")
    if after:
        got = wire_source_owner(WORK, after)
        s2 = [r for r in got if r.get("is_source")]
        fact(f"T2 OpWireSource_v5 on the NEW wire w{after}: {got}")
        gate("T2d the new wire's source terminal resolves (owner reported, not gated on identity: LabVIEW makes "
             "its own border tunnels, so a cross-boundary net's source may be a LoopTunnel - T1h measured that)",
             bool(s2), f"{s2}")


def cleanup():
    for p in (SCRATCH, WORK):
        try:
            g.close_panel(p)
        except Exception:
            pass
        for _ in range(6):
            try:
                if os.path.exists(p):
                    os.remove(p)
                break
            except OSError:
                time.sleep(1.0)
        gate(f"T3 scratch deleted: {os.path.basename(p)}", not os.path.exists(p), p)


def main():
    fact(f"LabVIEW handles at start: {labview_handles()}")
    labels = build()
    try:
        t1(labels)
    except Stop as e:
        gate(f"T1 stopped: {e}", False)
    except Exception as e:
        import traceback
        print(f"   T1 EXC {str(e)[:200]}\n{traceback.format_exc()[-900:]}", flush=True)
        gate("T1 raised", False, str(e)[:120])
    try:
        t2(labels)
    except Stop as e:
        gate(f"T2 stopped: {e}", False)
    except Exception as e:
        import traceback
        print(f"   T2 EXC {str(e)[:200]}\n{traceback.format_exc()[-900:]}", flush=True)
        gate("T2 raised", False, str(e)[:120])
    cleanup()
    fact(f"LabVIEW handles at end: {labview_handles()}")
    print("\n  NOTE on the gate: `Wire.Is Broken?` 6371004 IS read here - node #242 of the donor, ordered after "
          "the write by W7b - so T1f2/T2c2 are the sound gate and uid equality after Remove Bad Wires is not "
          "used anywhere in this file (docs/d1-build-plan.md §11u.1).", flush=True)
    print(f"\n=== build_opconnectfromwire_v0: {len(passes)} pass, {len(fails)} fail"
          f"{(' -> ' + ', '.join(fails)) if fails else ''} ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    rc = 1
    try:
        rc = main()
    except Stop as e:
        print(f"\nSTOP at gate: {e}", flush=True)
    except Exception as e:
        import traceback
        print(f"\nOBSERVED EXC {str(e)[:300]}\n{traceback.format_exc()[-1800:]}", flush=True)
    finally:
        try:
            cleanup()
        except Exception:
            pass
        same = md5(ORIGINAL) == ORIG_MD5
        print(f"  {'PASS' if same else '**FAIL**'}  Z(finally) original md5 unchanged  {md5(ORIGINAL)}", flush=True)
        if not same:
            rc = 1
    sys.exit(rc)
