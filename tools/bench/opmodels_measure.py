r"""opmodels_measure - card chat-S1 step B (docs/stage-simulator-plan.md "Op effect models"). For each op: ONE dated scratch
COPY of claudeDev\D1_s4_loop17.vi (4b621946...), >= 2 targets applied in order on it; per target READ BEFORE
(allterms.read_terms + report_all GObject) -> op -> READ AFTER (before any junk purge, so stray Invokes are SEEN) ->
opmodels_lib.diff -> tools/bench/opmodels/raw/<op>_<n>.json; then the measured junk purge (setup, not modelled) and the
next target. Setup edits a target needs (a move before a tunnel connect, a delete before a const) run BEFORE the BEFORE read.
Models (rules) are fitted OFFLINE from the raw files by opmodels_fit.py. argv[1] = group B1 | B2.
TARGETS were chosen offline from tools/bench/opmodels/bed_s4_loop17.json + bed_s4_map.json (step A/A2, 12/0 + 13/0):
  B1 move_in #194, #25091 -> body #23405 | delete_wire w2160 (1 sink), w9166 (2 sinks) | delete_object Function #7201,
     SubVI #27605 | remove_bad_wires after delete_object #1628, after move_in #25149 | add_shift_reg WhileLoop #23041 y260,
     #10170 y120 | primitive build_index_array top-level at (200,200), (400,200)
  B2 tunnel (connect_nested_v1 across the #23405 border): IN #25091'x*y' -> moved #25149'x', OUT moved #194'x-y' -> #1628'x'
     | connect_from_wire: moved #9342'array' <- w9415 (FSIT #9426 source), moved #7201'x' <- w23519 (#8486 source, branched)
     | wire_sr RightIn: new SR on #23041 <- #23042'x = y?', new SR on #10170 <- #10171'x = y?'
     | fs_inner_tunnel_connect after delete_wire: FSIT #25059 <- #24065'x*y' (w25092), FSIT #5183 <- #5426'x+y' (w5297)
     | const create_const_on_term: #6440 'error in (no error)' (bare, loop #25380), #23844 'milliseconds to wait' after
       delete_wire w24080 (loop #23032)
PRIOR ART (checked first, nothing new built): stagekit.Stage/scratch/drop_scratch/close; allterms.read_terms;
gscript.report_all/node_labels/node_terms_uid/add_shift_reg/shift_reg/wire_sr/remove_bad_wires_scripted/build_index_array;
build_d1_v0.move_in/diag_index; build_opfsinnertunnelconnect_v0.del_wire/del_node/purge_junk; build_d1_m3a1.node_census;
build_opconnectnested_v1.connect_nested_v1; build_opconnectfromwire_v0.connect_from_wire/wire_source_owner;
build_d1_m3a3b_d3.fsit_call; build_opcreateconstonterm_v0.create_const_on_term. All used unchanged.
PREDICTION CONTRACT (per target, gates): C1 the op returns without raising and without an error string; C2 the diff is
non-empty (the op had an effect); per group: every scratch deleted, K1/H2 bed md5 unchanged, H5 refs opened == closed,
H6 files left []; handles recorded per cell (flat = within +-300 of the cell start, RECORDED, gated only at H5).
No VI run, no original opened (preload=False), nothing saved.
    MATERIAL=1 py tools/bgrun.py --max-min 45 --log tools/bench/opmodels_measure_B1.log -- py -u tools/bench/opmodels_measure.py B1"""
import json, os, sys, time                                                         # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stagekit as K, gscript as g, allterms as A, opmodels_lib as L              # noqa: E401,E402

BED, BED_MD5 = os.path.join(K.CLAUDEDEV, "D1_s4_loop17.vi"), "4b621946492da3d2fbb96b6053e715ec"
RAW = os.path.join(K.BENCH, "opmodels", "raw")
PINS = tuple(K.DEFAULT_PINS) + (("S4 loop17 bed", BED, BED_MD5),)
BODY, B686 = 23405, 686
LAST_SETUP = [None]


def snap(sc):
    return A.read_terms(sc)[0], g.report_all(sc, "GObject")


def addr(sc, node_uid, diag_uid, term, is_source):
    didx = [int(d["uid"]) for d in g.report_all(sc, "Diagram")].index(int(diag_uid))
    uids = [int(r["uid"]) for r in g.node_labels(sc, didx)]
    nidx = uids.index(int(node_uid))
    echo, rows = g.node_terms_uid(sc, didx, nidx)
    if echo != int(node_uid):
        raise RuntimeError("echo {0} != #{1}".format(echo, node_uid))
    hits = [r for r in rows if r["name"] == term and bool(r["is_source"]) == bool(is_source)]
    if len(hits) > 1:
        hits = [r for r in hits if not r["wire"]]
    if len(hits) != 1:
        raise RuntimeError("#{0} {1!r} src={2}: {3} hits in {4}".format(node_uid, term, is_source, len(hits),
                                                                        [(r["i"], r["name"], r["wire"]) for r in rows]))
    return didx, nidx, int(hits[0]["i"])


def loop_index(sc, uid):
    return [int(o["uid"]) for o in g.report_all(sc, "WhileLoop")].index(int(uid))


class Cell(object):
    def __init__(self, s, op):
        self.s, self.op, self.n = s, op, 0
        s.head("OP {0}".format(op))
        self.sc = s.scratch(op[:10])
        self.h0 = K.mod("bench_prep").labview_handles()

    def apply(self, meta, fn, setup=None):
        s, sc = self.s, self.sc
        self.n += 1
        tag = "{0}_{1}".format(self.op, self.n)
        if setup:
            r, e = s.safe("{0} setup".format(tag), lambda: setup(sc))
            s.fact("{0} SETUP {1} -> {2!r} err {3!r}".format(tag, meta.get("setup"), r, e))
            meta["setup_result"], meta["setup_err"] = r, e
            LAST_SETUP[0] = r
        M = K.mod("build_d1_m3a1")
        before = snap(sc)
        nodes0 = M.node_census(sc, tag)[0]
        t0 = time.time()
        res, err = s.safe(tag, lambda: fn(sc))
        dt = time.time() - t0
        es = s.es(tag + " after op", sc)
        after = snap(sc)
        d = L.diff(before, after)
        rec = {"op": self.op, "n": self.n, "meta": meta, "result": res, "err": err, "op_s": round(dt, 1),
               "exec_state_after": es, "summary": L.summary(d), "diff": d}
        with open(os.path.join(RAW, "{0}.json".format(tag)), "w", encoding="utf-8") as f:
            json.dump(rec, f, default=str, indent=0)
        opstr = ""
        if isinstance(res, dict):
            # OpFsInnerTunnelConnect_v1 never writes its own `error out`: the POISON value that fsit_call pre-loads
            # (build_d1_m3a3b_d3.py:281-296, Pre-decided 125) is its DOCUMENTED readout on every accepted run
            # (build_d1_m3a3b_d3.log G2 calls 1-20). Its real error columns are invoke_err + err_* (run 1 of this
            # script read `err` and failed C1 twice on a successful connect - opmodels_measure_B2.log, our bug).
            cols = [res.get("invoke_err"), res.get("inv_err")] + [v for k, v in res.items() if k.startswith("err_")]
            e0 = res.get("err") or ""
            if "POISON - not overwritten" not in e0:
                cols.append(e0)
            opstr = "; ".join(str(x) for x in cols if x)
        elif isinstance(res, (list, tuple)) and len(res) >= 3 and isinstance(res[2], str):
            opstr = res[2]
        s.fact("{0} META {1} RESULT {2!r}".format(tag, meta, str(res)[:300]))
        s.fact("{0} DIFF {1} uid_alloc new={2} all_above_max={3}".format(
            tag, rec["summary"], d["uid_alloc"]["new_obj_uids"][:20], d["uid_alloc"]["all_new_above_max"]))
        s.gate("C1 {0} op returned without raising and without an error string".format(tag), not err and not opstr,
               (err, opstr))
        s.gate("C2 {0} the op had an effect (diff non-empty)".format(tag), any(rec["summary"].values()), rec["summary"])
        if self.op == "fs_inner_tunnel_connect" and isinstance(res, dict):
            # review archive/peer/2026-09-24-chatS1-opmodels-b2-fsit-c1.md §5: gate this op on its FRESH (poisoned) columns
            fresh = (res.get("wire_delta") == 1, res.get("is_broken") is False, res.get("uid_back") == meta["fsit"],
                     res.get("term_uid") == meta["fsit_term"])
            s.gate("C1f {0} fresh readback: wire_delta 1, Is Broken? False, uid_back == FSIT, term_uid == FSIT term".format(tag),
                   all(fresh), fresh)
        C82 = K.mod("build_opfsinnertunnelconnect_v0")
        s.safe(tag + " purge", lambda: C82.purge_junk(sc, nodes0, tag, []))
        # same review §5: ExecState AFTER the junk purge, RECORDED for every op (gated only for fs_inner_tunnel_connect,
        # whose connect completes a chain the setup broke; other ops legitimately leave the VI broken)
        rec["exec_state_after_purge"] = s.es(tag + " after purge", sc)
        with open(os.path.join(RAW, "{0}.json".format(tag)), "w", encoding="utf-8") as f:
            json.dump(rec, f, default=str, indent=0)
        if self.op == "fs_inner_tunnel_connect":
            s.gate("C3 {0} ExecState 1 after the purge (the connect left a whole VI)".format(tag),
                   rec["exec_state_after_purge"] == 1, rec["exec_state_after_purge"])
        return rec

    def close(self):
        h1 = K.mod("bench_prep").labview_handles()
        self.s.fact("HANDLES cell {0}: {1!r} -> {2!r} (delta {3})".format(self.op, self.h0, h1, (h1 or 0) - (self.h0 or 0)))
        self.s.drop_scratch(self.sc, "H4 " + self.op)


def B1(s):
    B = K.mod("build_d1_v0")
    C82 = K.mod("build_opfsinnertunnelconnect_v0")
    c = Cell(s, "move_in")
    c.apply({"node": 194, "cls": "Function", "dest": BODY, "pos": [4700, 6700]},
            lambda sc: B.move_in(sc, 194, B.diag_index(sc, BODY), (4700, 6700)))
    c.apply({"node": 25091, "cls": "Function", "dest": BODY, "pos": [4800, 6760]},
            lambda sc: B.move_in(sc, 25091, B.diag_index(sc, BODY), (4800, 6760)))
    c.close()
    c = Cell(s, "delete_wire")
    c.apply({"wire": 2160, "sinks": 1}, lambda sc: C82.del_wire(sc, 2160))
    c.apply({"wire": 9166, "sinks": 2}, lambda sc: C82.del_wire(sc, 9166))
    c.close()
    c = Cell(s, "delete_object")
    c.apply({"cls": "Function", "uid": 7201}, lambda sc: C82.del_node(sc, "Function", 7201))
    c.apply({"cls": "SubVI", "uid": 27605}, lambda sc: C82.del_node(sc, "SubVI", 27605))
    c.close()
    c = Cell(s, "remove_bad_wires")
    c.apply({"after": "delete_object Function #1628", "setup": "del_node Function 1628"},
            lambda sc: g.remove_bad_wires_scripted(sc), setup=lambda sc: C82.del_node(sc, "Function", 1628))
    c.apply({"after": "move_in #25149 -> #23405", "setup": "move_in 25149"},
            lambda sc: g.remove_bad_wires_scripted(sc),
            setup=lambda sc: B.move_in(sc, 25149, B.diag_index(sc, BODY), (4900, 6700)))
    c.close()
    c = Cell(s, "add_shift_reg")
    c.apply({"loop": 23041, "y": 260}, lambda sc: g.add_shift_reg(sc, loop_index(sc, 23041), 260, "WhileLoop"))
    c.apply({"loop": 10170, "y": 120}, lambda sc: g.add_shift_reg(sc, loop_index(sc, 10170), 120, "WhileLoop"))
    c.close()
    c = Cell(s, "primitive")
    c.apply({"prim": "IndexArray", "diagram": "top", "loc": [200, 200]}, lambda sc: g.build_index_array(sc, (200, 200)))
    c.apply({"prim": "IndexArray", "diagram": "top", "loc": [400, 200]}, lambda sc: g.build_index_array(sc, (400, 200)))
    c.close()


def B2(s):
    B = K.mod("build_d1_v0")
    C82 = K.mod("build_opfsinnertunnelconnect_v0")
    N = K.mod("build_opconnectnested_v1")
    NL = json.load(open(N.MAP_OUT, encoding="utf-8"))
    F = K.mod("build_opconnectfromwire_v0")
    FL = json.load(open(F.MAP_OUT, encoding="utf-8"))

    def nested(sc, src, dst):
        sd, sn, st = addr(sc, src[1], src[0], src[2], True)
        dd, dn, dt = addr(sc, dst[1], dst[0], dst[2], False)
        return N.connect_nested_v1(sc, dd, dn, dt, sd, sn, st, NL)

    c = Cell(s, "tunnel")
    c.apply({"dir": "in", "src": [B686, 25091, "x*y"], "dst": [BODY, 25149, "x"], "setup": "move_in 25149"},
            lambda sc: nested(sc, (B686, 25091, "x*y"), (BODY, 25149, "x")),
            setup=lambda sc: B.move_in(sc, 25149, B.diag_index(sc, BODY), (4900, 6700)))
    c.apply({"dir": "out", "src": [BODY, 194, "x-y"], "dst": [B686, 1628, "x"], "setup": "move_in 194"},
            lambda sc: nested(sc, (BODY, 194, "x-y"), (B686, 1628, "x")),
            setup=lambda sc: B.move_in(sc, 194, B.diag_index(sc, BODY), (4700, 6700)))
    c.close()

    def cfw(sc, wire, src_uid, dst):
        hit = [x for x in F.wire_source_owner(sc, wire, n=8) if x.get("owner_uid") == src_uid and x.get("is_source")]
        if len(hit) != 1:
            raise RuntimeError("w{0}: {1} source rows owned by #{2}".format(wire, len(hit), src_uid))
        dd, dn, dt = addr(sc, dst[1], dst[0], dst[2], False)
        return F.connect_from_wire(sc, wire, int(hit[0]["i"]), dd, dn, dt, FL)

    c = Cell(s, "connect_from_wire")
    c.apply({"wire": 9415, "src": 9426, "src_cls": "FlatSequenceInnerTunnel", "dst": [BODY, 9342, "array"],
             "setup": "move_in 9342"}, lambda sc: cfw(sc, 9415, 9426, (BODY, 9342, "array")),
            setup=lambda sc: B.move_in(sc, 9342, B.diag_index(sc, BODY), (4700, 6700)))
    c.apply({"wire": 23519, "src": 8486, "src_cls": "Function", "dst": [BODY, 7201, "x"], "setup": "move_in 7201"},
            lambda sc: cfw(sc, 23519, 8486, (BODY, 7201, "x")),
            setup=lambda sc: B.move_in(sc, 7201, B.diag_index(sc, BODY), (4800, 6760)))
    c.close()

    def sr_right_in(sc, loop_uid, body_uid, node_uid, term):
        li = loop_index(sc, loop_uid)
        rights = []
        for k in range(16):
            u = g.shift_reg(sc, li, k).get("uid")
            if u is None:
                break
            rights.append(int(u))
        new = LAST_SETUP[0]                       # add_shift_reg's returned RightShiftRegister uid (the setup)
        if new not in rights:
            raise RuntimeError("new SR #{0} not in Shift Registers[] {1}".format(new, rights))
        k = rights.index(new)
        _d, nidx, ti = addr(sc, node_uid, body_uid, term, True)
        g.wire_sr("RightIn", sc, li, k, node_index=nidx, term_index=ti)
        return {"loop_index": li, "reg_index": k, "rights": rights, "node_index": nidx, "term_index": ti}

    c = Cell(s, "wire_sr")
    c.apply({"variant": "RightIn", "loop": 23041, "src": [BODY, 23042, "x = y?"], "setup": "add_shift_reg 23041 y260"},
            lambda sc: sr_right_in(sc, 23041, BODY, 23042, "x = y?"),
            setup=lambda sc: g.add_shift_reg(sc, loop_index(sc, 23041), 260, "WhileLoop"))
    c.apply({"variant": "RightIn", "loop": 10170, "src": [23166, 10171, "x = y?"], "setup": "add_shift_reg 10170 y120"},
            lambda sc: sr_right_in(sc, 10170, 23166, 10171, "x = y?"),
            setup=lambda sc: g.add_shift_reg(sc, loop_index(sc, 10170), 120, "WhileLoop"))
    c.close()

    D3 = K.mod("build_d1_m3a3b_d3")
    DL = json.load(open(D3.MAP_OUT, encoding="utf-8"))
    FS = {}

    def fs_setup(sc, key, wire, src_uid, src_diag, src_term):
        FS[key] = addr(sc, src_uid, src_diag, src_term, True)      # index triple read BEFORE the delete
        return C82.del_wire(sc, wire), FS[key]

    c = Cell(s, "fs_inner_tunnel_connect")
    c.apply({"fsit": 25059, "fsit_term": 25075, "src": 24065, "src_term": "x*y", "src_diag": 81548,
             "setup": "delete_wire 25092"},
            lambda sc: D3.fsit_call(D3.OP1, DL, sc, 25059, *FS["a"], auto_route=None),
            setup=lambda sc: fs_setup(sc, "a", 25092, 24065, 81548, "x*y"))
    c.apply({"fsit": 5183, "fsit_term": 5260, "src": 5426, "src_term": "x+y", "src_diag": 4866,
             "setup": "delete_wire 5297"},
            lambda sc: D3.fsit_call(D3.OP1, DL, sc, 5183, *FS["b"], auto_route=None),
            setup=lambda sc: fs_setup(sc, "b", 5297, 5426, 4866, "x+y"))
    c.close()

    CC = K.mod("build_opcreateconstonterm_v0")
    CL = json.load(open(os.path.join(K.BENCH, "opcreateconstonterm_labels.json"), encoding="utf-8"))

    def const(sc, loop_uid, body_uid, node_uid, term):
        _d, nidx, ti = addr(sc, node_uid, body_uid, term, False)
        return CC.create_const_on_term(sc, loop_index(sc, loop_uid), nidx, ti, CL)

    c = Cell(s, "const")
    c.apply({"loop": 25380, "node": 6440, "term": "error in (no error)"},
            lambda sc: const(sc, 25380, 25392, 6440, "error in (no error)"))
    c.apply({"loop": 23032, "node": 23844, "term": "milliseconds to wait", "setup": "delete_wire 24080"},
            lambda sc: const(sc, 23032, 23058, 23844, "milliseconds to wait"),
            setup=lambda sc: C82.del_wire(sc, 24080))
    c.close()


def body(s):
    print(__doc__, flush=True)
    os.makedirs(RAW, exist_ok=True)
    s.start(); s.discard_work()                                                    # noqa: E702
    s.fact("HANDLES after open {0!r}".format(K.mod("bench_prep").labview_handles()))
    {"B1": B1, "B2": B2}[GROUP](s)


if __name__ == "__main__":
    GROUP = sys.argv[1]
    st = K.Stage(BED, BED_MD5, "opmodels_measure_" + GROUP, preload=False, deadline_min=42, pins=PINS)
    sys.exit((K.run(body, st), K.mod("bench_prep").restart_labview())[0])
