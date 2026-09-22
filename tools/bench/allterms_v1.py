r"""allterms_v1 - `OpAllTerms_v1.vi`: S3 AGAIN from the same saved `_s2` artefact, plus a SEVENTH column
`frame_diagram` (`Terminal.Diagram` 634A002 -> that diagram's UID). `OpAllTerms_v0.vi` is left INTACT.

WHY IT IS A REBUILD AND NOT AN EDIT OF v0 (the judgement brief's condition, measured 2026-09-23):
`Terminal.Diagram` IS a Terminal property, so it needs NO new `To More Specific Class` - the two TMSCs
saved in `_s2` are all the casts this column needs. But it cannot "sit on the existing Terminal property
node A": ADDING a property to a property node is GROWING A NODE'S TERMINAL COUNT, which is one of the
exactly two operations with no scripting path at all (skill `labview-automation` Rule 0.2). So the column
is a NEW property node, which means the S3 route re-run - which is what the brief prescribed for this case.
It needs no GUI: `_s2` already holds both GUI-placed casts.

WHAT IS ADDED to S3's four new property nodes:
    D    `VI Server:Terminal` [Diagram 634A002]  <- B.'reference out'   (chained, NOT branched: a branch
         adds no Wire object and the W3 gate counts wires; a property node passes `reference out` through
         whether or not its own property errored)
    DU   `VI Server:GObject`  [UID]              <- D.<the Diagram output terminal, READ off the machine>
         (a Diagram IS a GObject, so no cast - the same reason `W` needs none for a Wire)
and a FIFTH auto-indexed output tunnel, so O1b expects +5 and the label map carries `frame_diagram`.

--- S3's original header, unchanged, because every law in it still applies -------------------------------
allterms_s3 - STEP 1 / sub-step S3: wire the two GUI-placed casts into a whole-VI TERMINAL reader.

INPUT: `claudeDev\OpAllTerms_v0_s2.vi` (md5 358c9dca...), which already holds, on the For-loop BODY
diagram (Traverse `Diagram` index 1):
    PN1  `VI Server:GObject` [Position, UID 632A813, ClassName 6327803, Owner 6327806]  <- the tunnel
    PN2  `VI Server:Generic` [ClassName]                                                <- PN1.Owner
    TMSC #587 @ (1897,1647) and TMSC #598 @ (2157,1647)   - GUI Quick Drop, S2, both unwired

WHAT THIS ADDS, and why each node is separate (`docs/toolkit-capabilities.md:74`, and the retarget
review's §5.1: five properties on ONE node means a failing row silently DEFAULTS the rows below it, so an
UNWIRED terminal would return UID and Owner as 0 on the MAJORITY of terminals):
    A    `VI Server:Terminal` [Name 634A004, Is Source? 634A003]   <- TMSC1.'specific class reference'
    B    `VI Server:Terminal` [Connected Wire 634A000]             <- A.'reference out'
    W    `VI Server:GObject`  [UID]                                <- B.'Wire'   (Wire IS a GObject: no cast)
    OU   `VI Server:GObject`  [UID]                                <- TMSC2.'specific class reference'
TMSC1.reference <- PN1.'reference out'      (GObject -> Terminal, the cast the whole op exists for)
TMSC2.reference <- PN2.'reference out'      (Generic  -> GObject, what `owner_uid` needs; `OpWireSource_v5`
                                             and `OpOwnerChain_v1` both take exactly this route)
Each TMSC's `target class` is fed by a TYPED SEED made with `create_control` on the matching property
node's own `reference`, so its class is that node's BY CONSTRUCTION, never a typed string
(`build_opconnectfromwire_v0.py` W6/W9 - the seed is born WIRED, so its birth wire is deleted first).

TWO OF THE SIX COLUMNS NEED NO CAST AND ARE ALREADY BUILT: `term_uid` = PN1.UID = the existing indicator
`Array 2`, `owner_class` = PN2.ClassName = `Array 4`. Only four new auto-indexed tunnels are made.

DEVIATION, STATED NOT DECIDED: the brief asks for `Close Reference` on every ref in the body. **There is
no Close Reference creator in this fleet** (zero hits in `tools/gscript.py`), so it cannot be scripted;
the donor `OpReportAll_v0` has none either. Whether that is acceptable is decided EMPIRICALLY by S4's
20-call handle test, not asserted here.

PREDICTION CONTRACT
  R1  both TMSC uids resolve on body diagram 1 and carry `target class`; their terminal names are READ
  W*  each build/wire step reports its own error column, and the census moves by the predicted amount
  O1  exit_loop makes exactly 4 new auto-indexed tunnels; each gets a typed indicator whose LABEL is
      read back off the machine (never guessed) into tools/bench/opallterms_labels.json
  S1  ExecState is REPORTED; `OpAllTerms_v0.vi` is written ONLY at 1. At 0 the artefact is saved as
      `OpAllTerms_v0_s3.vi` through the broken-intermediate permission and the run STOPS with the
      Error List read by tools/lv_errorlist.py.

  py tools/bgrun.py --material --max-min 40 --log tools/bench/allterms_s3.log -- py -u tools/bench/allterms_s3.py
"""
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402

SRC = os.path.join(K.CLAUDEDEV, "OpAllTerms_v0_s2.vi")
SRC_MD5 = "358c9dca27fa38d4748bc9d7170e4aab"
WORK = "OpAllTerms_v1_s3.vi"
FINAL = os.path.join(K.CLAUDEDEV, "OpAllTerms_v1.vi")
LABELS_OUT = os.path.join(K.BENCH, "opallterms_v1_labels.json")
BODY = 1
TMSC_UIDS = [587, 598]

P_NAME, P_ISSRC, P_WIRE, P_UID, P_OWNER, P_CLS = ("634A004", "634A003", "634A000",
                                                  "632A813", "6327806", "6327803")
P_DIAG = "634A002"        # Terminal.Diagram - the frame/diagram a terminal sits on (OpTunnelRead_v0 uses it)
T_NAME, T_ISSRC, T_WIRE, T_UID = "Name", "IsSource", "Wire", "UID"


# ---------------------------------------------------------------- index helpers (34(h): re-read always)
def tidx(s, cls, uid):
    rows, _e = s.safe("report({0})".format(cls), lambda: g.report(s.work, cls), [])
    return next((i for i, o in enumerate(rows or []) if o["uid"] == uid), None)


BODYMAP = {}


def scan_diagram(s, di, tag, limit=24):
    """ONE pass over a diagram's Nodes[]: {uid: (index, terminal rows)}. `node_terms` drops no junk
    (unlike net_map), so this is the cheap, non-perturbing walk. Re-run after every mutation - no index and
    no terminal list is ever carried across one (34(h))."""
    out, misses = {}, 0
    for i in range(limit):
        res, _e = s.safe("node_terms_uid[d{0}n{1}]".format(di, i),
                         lambda j=i: g.node_terms_uid(s.work, di, j), (None, None))
        nu, rows = res if isinstance(res, tuple) else (None, None)
        if not nu:
            misses += 1
            if misses >= 3:
                break
            continue
        misses = 0
        out[nu] = (i, rows)
    s.fact("scan[{0}] diagram {1}: {2} node(s) {3!r}".format(tag, di, len(out), sorted(out)))
    return out


def scan_body(s, tag, limit=24):
    BODYMAP.clear()
    BODYMAP.update(scan_diagram(s, BODY, tag, limit))
    return BODYMAP


def term(rows, name):
    return next((r for r in (rows or []) if r["name"] == name), None)


def find_body_property(s, *names):
    """The body Property node carrying every one of `names` - identified by its TERMINALS, never by uid."""
    rows, _e = s.safe("report(Property)", lambda: g.report(s.work, "Property"), [])
    for o in (rows or []):
        hit = BODYMAP.get(o["uid"])
        if hit and all(term(hit[1], n) for n in names):
            return o["uid"], hit[0], hit[1]
    return None, None, None


def main(s):
    s.start()
    p = s.work

    s.head("[R1] read the body: the two GUI-placed casts and the donor's two property nodes")
    es0 = s.es("s2 input, broken by design")
    cen0 = dict((c, s.count(c)) for c in ("Function", "Property", "LoopTunnel", "ControlTerminal", "Wire"))
    s.fact("census at entry {0!r}  ExecState {1!r}".format(cen0, es0))
    scan_body(s, "R1")
    casts = []
    for u in TMSC_UIDS:
        i, rows = BODYMAP.get(u, (None, None))
        s.fact("TMSC #{0}: body Nodes[{1!r}] terminals {2!r}".format(
            u, i, [(r["i"], r["name"], r["is_source"], r["wire"]) for r in (rows or [])]))
        casts.append((u, i, rows))
    s.gate("R1 both TMSC resolve on body diagram {0} and carry `target class`".format(BODY),
           all(i is not None and term(r, "target class") for _u, i, r in casts),
           "indices {0!r}".format([i for _u, i, _r in casts]), fatal=True)
    tref = next((n for n in ("reference", "reference 2", "object reference")
                 if term(casts[0][2], n)), None)
    s.gate("R1b the cast's INPUT terminal name was read off the machine", tref is not None,
           "name {0!r}".format(tref), fatal=True)
    s.fact("the cast's input terminal is {0!r}; its output is 'specific class reference'".format(tref))

    pn1_uid, _i1, _r1 = find_body_property(s, T_UID, "Owner", "Position")
    pn2_uid, _i2, _r2 = find_body_property(s, "ClassName")
    s.gate("R1c PN1 (GObject: UID/Owner/Position) and PN2 (Generic: ClassName) both found",
           pn1_uid is not None and pn2_uid is not None and pn1_uid != pn2_uid,
           "PN1 {0!r} PN2 {1!r}".format(pn1_uid, pn2_uid), fatal=True)

    s.head("[W1] the four new property nodes, ONE concern each (toolkit-capabilities.md:74)")
    made = {}
    for key, cls, props, loc in (("A", "VI Server:Terminal", [(P_NAME, False), (P_ISSRC, False)], (1900, 1900)),
                                 ("B", "VI Server:Terminal", [(P_WIRE, False)], (1900, 2100)),
                                 ("W", "VI Server:GObject", [(P_UID, False)], (1900, 2300)),
                                 ("OU", "VI Server:GObject", [(P_UID, False)], (2200, 2300)),
                                 ("D", "VI Server:Terminal", [(P_DIAG, False)], (2500, 1900)),
                                 ("DU", "VI Server:GObject", [(P_UID, False)], (2500, 2100))):
        rec = s._op("build_property({0})".format(key),
                    lambda c=cls, pr=props, lo=loc: g.build_property(p, c, pr, lo, diagram_index=BODY),
                    "{0} on the body".format(cls))
        out = rec.get("result") or []
        made[key] = out[-1]["uid"] if out else None
        s.gate("W1{0} property node {0} created".format(key), made[key] is not None,
               "uid {0!r} err {1!r}".format(made[key], rec.get("err")), fatal=True)
    s.R["new_property_nodes"] = made
    s.fact("new property nodes {0!r}".format(made))

    s.head("[W2] the two TYPED SEEDS - built on the ROOT diagram, because create_control cannot reach a "
           "node inside a loop body")
    # RUN 1 MEASURED THIS, and the cause is in the function's own source, not inferred:
    # `create_control` (tools/gscript.py:2478-2481) walks **VI -> Block Diagram -> Nodes[] -> Terminals[]**,
    # i.e. the ROOT diagram only, so the body-diagram Nodes[] index this stage passed addressed a different
    # node (or none): it returned `label None`, no control appeared, and `wire_control` then died with
    # 5001 "Control  not found" (allterms_s3.log, gates W2Ab/W2Ac/W2OUb/W2OUc).
    # THE ROUTE THAT DOES WORK, and it needs nothing new: build a THROWAWAY property node of the same
    # class on the ROOT, make the typed seed from ITS `reference` (so the seed's class is that node's BY
    # CONSTRUCTION - `build_opconnectfromwire_v0.py` W6), delete the throwaway, and let `wire_control`
    # carry the seed across the loop border - LabVIEW makes the border tunnel itself.
    seeds = {}
    for k2, (key, cast_uid, seed_cls) in enumerate((("A", TMSC_UIDS[0], "VI Server:Terminal"),
                                                    ("OU", TMSC_UIDS[1], "VI Server:GObject"))):
        rec = s._op("build_property(root seed donor {0})".format(key),
                    lambda c=seed_cls, kk=k2: g.build_property(p, c, [(P_UID, False)],
                                                               (700 + 400 * kk, 2600), diagram_index=0),
                    "{0} on the ROOT, throwaway".format(seed_cls))
        out = rec.get("result") or []
        donor_uid = out[-1]["uid"] if out else None
        s.gate("W2{0}a the throwaway seed donor exists on the root".format(key), donor_uid is not None,
               "uid {0!r} err {1!r}".format(donor_uid, rec.get("err")), fatal=True)
        root = scan_diagram(s, 0, "W2{0} root".format(key))
        ni, rows = root.get(donor_uid, (None, None))
        rterm = term(rows, "reference")
        s.gate("W2{0}b the donor's `reference` terminal was found on the ROOT".format(key),
               ni is not None and rterm is not None,
               "Nodes[{0!r}] terminals {1!r}".format(ni, [r["name"] for r in (rows or [])]), fatal=True)
        res, _e = s.safe("create_control({0})".format(key),
                         lambda n=ni, t=rterm["i"]: g.create_control(p, n, t), (None, None))
        _new_ctls, label = res if isinstance(res, tuple) else (None, None)
        root = scan_diagram(s, 0, "W2{0} root after".format(key))
        birth = term((root.get(donor_uid) or (None, None))[1], "reference")
        s.gate("W2{0}c one typed seed control was born, WIRED into `reference`".format(key),
               bool(label) and bool(birth and birth["wire"]),
               "label {0!r} birth wire {1!r}".format(label, birth and birth["wire"]), fatal=True)
        seeds[key] = label
        s.delete_wire(birth["wire"], tag="W2{0} seed birth wire".format(key))
        s.safe("delete throwaway donor {0}".format(donor_uid),
               lambda du=donor_uid: g.delete_object(p, "Property", tidx(s, "Property", du)))
        s.safe("remove_bad_wires_scripted", lambda: g.remove_bad_wires_scripted(p))
        gone = tidx(s, "Property", donor_uid) is None
        s.gate("W2{0}d the throwaway donor is gone, the seed control remains".format(key),
               gone and label in [l for _i, l, ind in g.fp_labels(p) if not ind],
               "donor gone {0!r} seed {1!r}".format(gone, label))
        r1 = s._op("wire_control(seed->target class)",
                   lambda lb=label, cu=cast_uid: g.wire_control(p, [lb], "Function",
                                                                tidx(s, "Function", cu), ["target class"]),
                   "{0!r} -> TMSC #{1} 'target class'".format(label, cast_uid))
        s.gate("W2{0}e the seed feeds the cast's `target class`".format(key), not r1["err"],
               "err {0!r}".format(r1["err"]))
    s.R["seeds"] = seeds

    s.head("[W3] the casts: input from the pre-cast node, output into the typed node")
    plan = [("TMSC1.in", "Property", pn1_uid, "reference out", "Function", TMSC_UIDS[0], tref),
            ("TMSC1.out", "Function", TMSC_UIDS[0], "specific class reference", "Property", made["A"], "reference"),
            ("TMSC2.in", "Property", pn2_uid, "reference out", "Function", TMSC_UIDS[1], tref),
            ("TMSC2.out", "Function", TMSC_UIDS[1], "specific class reference", "Property", made["OU"], "reference"),
            ("A->B", "Property", made["A"], "reference out", "Property", made["B"], "reference"),
            ("B->W", "Property", made["B"], T_WIRE, "Property", made["W"], "reference"),
            ("B->D", "Property", made["B"], "reference out", "Property", made["D"], "reference")]
    for label, sc, su, st, dc, du, dt in plan:
        w0 = s.count("Wire")
        r = s._op("wire({0})".format(label),
                  lambda a=sc, b=su, c=st, d=dc, e=du, f=dt: g.wire(p, a, tidx(s, a, b), c,
                                                                    d, tidx(s, d, e), f),
                  "{0}: {1}#{2}.{3!r} -> {4}#{5}.{6!r}".format(label, sc, su, st, dc, du, dt))
        w1 = s.count("Wire")
        s.gate("W3 {0}: op error empty and Wire {1} -> {2}".format(label, w0, w1),
               not r["err"] and w1 == w0 + 1, "err {0!r}".format(r["err"]))

    s.head("[W4] D's `Diagram` OUTPUT terminal name is READ off the machine, then wired into DU")
    scan_body(s, "W4", limit=32)
    d_rows = (BODYMAP.get(made["D"]) or (None, None))[1] or []
    s.fact("D #{0} terminals {1!r}".format(
        made["D"], [(r["i"], r["name"], r["is_source"]) for r in d_rows]))
    skip = {"reference", "reference out", "error in (no error)", "error in", "error out"}
    d_out = next((r["name"] for r in d_rows if r["is_source"] and r["name"] not in skip), None)
    s.gate("W4a D's Diagram output terminal was read, not guessed", d_out is not None,
           "terminal {0!r}".format(d_out), fatal=True)
    w0 = s.count("Wire")
    r = s._op("wire(D->DU)",
              lambda t=d_out: g.wire(p, "Property", tidx(s, "Property", made["D"]), t,
                                     "Property", tidx(s, "Property", made["DU"]), "reference"),
              "D#{0}.{1!r} -> DU#{2}.'reference'".format(made["D"], d_out, made["DU"]))
    w1 = s.count("Wire")
    s.gate("W4b D->DU: op error empty and Wire {0} -> {1}".format(w0, w1),
           not r["err"] and w1 == w0 + 1, "err {0!r}".format(r["err"]))

    s.head("[O1] FIVE auto-indexed OUTPUT tunnels and their typed indicators")
    before_lab = set(l for _i, l, ind in g.fp_labels(p) if ind and l)
    t0 = s.count("LoopTunnel")
    outs = [("A", [T_NAME, T_ISSRC]), ("W", [T_UID]), ("OU", [T_UID]), ("DU", [T_UID])]
    for key, names in outs:
        r = s._op("exit_loop({0})".format(key),
                  lambda k=key, n=names: g.exit_loop(p, tidx(s, "Property", made[k]), n, BODY,
                                                     node_class="Property"),
                  "{0} -> {1!r}".format(key, names))
        s.gate("O1 exit_loop({0}) made its tunnels".format(key), not r["err"], "err {0!r}".format(r["err"]))
    t1 = s.count("LoopTunnel")
    s.gate("O1b LoopTunnel {0} -> {1} (+5)".format(t0, t1), t1 == t0 + 5, "")

    meanings = ["term_name", "is_source", "wire_uid", "owner_uid", "frame_diagram"]
    label_map = {"vi_path": "vi path", "class_name": "Class Name",
                 "term_uid": "Array 2", "owner_class": "Array 4", "error": "error out 2"}
    for k, tun in enumerate(range(t0, t1)):
        s.safe("set_index_mode({0})".format(tun), lambda t=tun: g.set_index_mode(p, t, 1))
        s.safe("tunnel_indicator({0})".format(tun), lambda t=tun: g.tunnel_indicator(p, t))
        now = set(l for _i, l, ind in g.fp_labels(p) if ind and l)
        fresh = sorted(now - before_lab)
        before_lab = now
        if k < len(meanings) and len(fresh) == 1:
            label_map[meanings[k]] = fresh[0]
        s.fact("tunnel {0} -> indicator {1!r} = {2!r}".format(tun, fresh, meanings[k] if k < len(meanings) else "?"))
    s.R["label_map"] = label_map
    s.gate("O1c every one of the SEVEN columns has a front-panel label",
           all(m in label_map for m in ("term_uid", "term_name", "is_source", "wire_uid",
                                        "owner_uid", "owner_class", "frame_diagram")), repr(label_map))

    s.head("[S1] Remove Bad Wires, ExecState, save")
    s.safe("remove_bad_wires_scripted", lambda: g.remove_bad_wires_scripted(p))
    es = s.es("after the whole v1 build")
    s.R["exec_state_final"] = es
    cen1 = dict((c, s.count(c)) for c in ("Function", "Property", "LoopTunnel", "ControlTerminal", "Wire"))
    s.fact("census at exit {0!r}".format(cen1))
    s.save(broken_ok=True, cold_check=(es == 1))
    s.gate("S1 ExecState 1 - the reader is a RUNNABLE VI", es == 1, "ExecState {0!r}".format(es))
    if es == 1:
        with open(LABELS_OUT, "w", encoding="utf-8") as f:
            json.dump(label_map, f, indent=1)
        s.safe("close_panel(work)", lambda: g.close_panel(p))
        shutil.copyfile(p, FINAL)
        s.gate("S1b OpAllTerms_v1.vi written", os.path.exists(FINAL),
               "{0} md5 {1}".format(FINAL, K.md5(FINAL) if os.path.exists(FINAL) else "-"))
    else:
        s.fact("ExecState 0: the deliverable name is NOT written; the broken intermediate stays at "
               "{0} and the Error List is the next read (tools/lv_errorlist.py).".format(WORK))


S = K.Stage(SRC, SRC_MD5, "allterms_v1", fresh=True, preload=False, work_name=WORK,
            deadline_min=34.0, reserve_s=200.0,
            out_json=os.path.join(K.BENCH, "allterms_v1.json"),
            task="OpAllTerms_v1 from the same _s2 artefact: S3's six columns PLUS a seventh, "
                 "frame_diagram = Terminal.Diagram 634A002 -> UID, on two new property nodes chained off "
                 "B. No new To More Specific Class; OpAllTerms_v0.vi is left untouched.")
sys.exit(K.run(main, S))
