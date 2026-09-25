r"""constsrc_l2a1_82 - card 82-3 P2: measure candidate verbs for a BARE diagram-CONSTANT source on nested #23166.
PRIOR ART / CANDIDATES (P1, checked before writing):
  C1 gscript.wire:1410 (OpWire_v1: Traverse(src class)[i] + Get Outputs by NAME -> Traverse(dst class)[j] + Get Inputs).
     build_d1_v0.py:1181-1186 records "A Constant is a GObject, not a Node, so no `Get Outputs` reaches it" (never measured
     on a constant source) -> measured here as the cheap first candidate.
  C2 gscript.wire_control:1998 (OpWireCtl_v0, Get Controls on Diagram[i] by LABEL) - the 82-2 'ctl' route; a constant also
     carries a label -> measured as the second candidate.
  C3 Constant.Terminal 634AC04 -> Terminal.Connect Wire 6349C03 (build_d1_v0.py:1184, d1-build-plan.md:1093 "(b)"): NO op
     VI exists (OpConstWire_v0 recipe never built) -> not measurable here; named as the tool to build if C1/C2 fail.
  Excluded: connect_nested_v1 (Nodes[] triples; real Nodes[] omits *Constant, stagexec.py:276), connect_terminals (top-level
  Nodes[]), OpCreateConstOnTerm (replaces the constant - forbidden by the card), connect_from_wire (needs a wired source).
METHOD: the real executor applies ops 1-34 on a D1_k scratch; op 35 stops at ADDRESS (no mutation). Then per row the
candidates are tried in order C1, C2 (C2 only when C1 made no wire) and READ BACK. No op VI built; nothing saved.
PREDICTION CONTRACT:
  P0 ops 1-34 diff 0 and op 35 stops before mutation (ADDRESS/CONNECT-NO-VERB)
  per row (rw_10738_11055, rw_10943_10877), per candidate: err None, Wire +1, the new wire's ONLY source == the constant's
  terminal (owner uid == constant uid), ONLY sink == the plan sink, ordered second pass wire_delta 0 / Is Broken? False;
  row A: real graph == plan step of its act (compare n 0).
  H D1_k md5 unchanged, scratch deleted, LabVIEW gone. Per-phase wall-clock stamps (review hyp-ctsrc82-timeout).
    py tools/bgrun.py --max-min 45 --log tools/bench/constsrc_l2a1_82.log -- py -u tools/bench/constsrc_l2a1_82.py"""
import json, os, subprocess, sys, time                                              # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, stagexec as SX                                  # noqa: E401,E402
PLAN = os.path.join(K.BENCH, "sim/l2a1/plan_l2a1.json")
P, _ = SX.load_final_plan(PLAN)
BASE = SX._j(SX._abs(P["finalized"]["base"]["path"]))
BED, BED_MD5 = BASE["vi"], BASE["md5"]
FS = BASE["fs_tunnel_pairs"]
ROWS = (("rw_10738_11055", 10739, 10738, 10950, 11055), ("rw_10943_10877", 10929, 10943, 10757, 10877))
T0 = time.time()


def stamp(s, what):
    s.fact("STAMP {0:7.1f} s {1}".format(time.time() - T0, what))


def one(real, t):
    r = [x for x in real if x["term_uid"] == t]
    if len(r) != 1:
        raise SX.ExecStop("#{0}: {1} rows".format(t, len(r)))
    return r[0]


def body(s):
    print(__doc__, flush=True)
    s.start(); stamp(s, "started")                                                   # noqa: E702
    s.discard_work()
    be = SX.LVBackend(s, FS)
    ex = SX.Executor(PLAN, be, log=lambda m: print(m, flush=True))
    stop = ""
    try:
        ex.run()
    except SX.ExecStop as e:
        stop = str(e)
    stamp(s, "executor stopped")
    diffs = [r["diff"]["n"] for r in ex.report if r.get("diff")]
    s.gate("P0 ops 1-34 diff 0 and op 35 stops before mutation", len(diffs) >= 34 and not any(diffs)
           and (stop.startswith("ADDRESS") or stop.startswith("CONNECT-NO-VERB")) and "10739" in stop,
           "{0} records, diffs {1}; stop {2}".format(len(ex.report), sum(diffs), stop[:200]), fatal=True)
    F = K.mod("build_opconnectfromwire_v0")
    lab = json.load(open(F.MAP_OUT, encoding="utf-8"))
    real, table = be.read(), []
    for k, (rid, cu, ct, nu, snk) in enumerate(ROWS):
        rc, rs = one(real, ct), one(real, snk)
        cls = be.obj_classes(real).get(cu, rc["owner_class"])
        didx = be.addr.rd.diagrams().index(int(rc["frame_diagram"]))
        s.fact("{0}: const #{1} {2} term #{3} {4!r} owner {5} #{6} wire {7} diag #{8}; sink #{9} {10!r} on {11} #{12} wire {13}".format(
            rid, cu, cls, ct, rc["term_name"], rc["owner_class"], rc["owner_uid"], rc["wire_uid"], rc["frame_diagram"],
            snk, rs["term_name"], rs["owner_class"], rs["owner_uid"], rs["wire_uid"]))
        for cand in ("C1", "C2"):
            si, di = s.uid_index(cls, cu), s.uid_index(rs["owner_class"], int(rs["owner_uid"]))
            w0 = s.count("Wire")
            if cand == "C1":
                fn = lambda: g.wire(s.work, cls, si, rc["term_name"], rs["owner_class"], di, rs["term_name"])  # noqa: E731
            else:
                fn = lambda: g.wire_control(s.work, [rc["term_name"]], rs["owner_class"], di, [rs["term_name"]],  # noqa: E731
                                            src_diagram_index=didx)
            rec = s._op(cand, fn, "{0}: {1}[{2}].{3!r}@D[{4}] -> {5}[{6}].{7!r}".format(
                rid, cls, si, rc["term_name"], didx, rs["owner_class"], di, rs["term_name"]))
            s.junk_purge(rid + " " + cand)
            dw = s.count("Wire") - w0
            real2 = be.read()
            w = int(one(real2, ct)["wire_uid"] or 0)
            srcs = sorted(x["term_uid"] for x in real2 if w and x["wire_uid"] == w and x["is_source"])
            snks = sorted(x["term_uid"] for x in real2 if w and x["wire_uid"] == w and not x["is_source"])
            owner = sorted(set(x["owner_uid"] for x in real2 if w and x["wire_uid"] == w and x["is_source"]))
            ns = s.net_sources(w, tag=rid) if w else {"walk": []}
            hit = [x for x in (ns.get("walk") or []) if x.get("is_source")]
            ib, d2, err2 = None, None, None
            if w and len(hit) == 1:
                (dd, nn, tt), _how = be.addr.triple(real2, snk, False)
                res, err2 = s.safe("second pass", lambda: F.connect_from_wire(s.work, w, int(hit[0]["i"]), dd, nn, tt, lab))
                s.junk_purge(rid + " 2nd")
                if res:
                    d2, ib, err2 = res[0], (res[3] or {}).get("Is Broken?"), err2 or res[2]
            row = {"row": rid, "cand": cand, "err": rec["err"], "wire_delta": dw, "wire": w, "sources": srcs,
                   "source_owner": owner, "sinks": snks, "walk_src": [(x.get("owner_class"), x.get("owner_uid")) for x in hit][:3],
                   "second_delta": d2, "is_broken": ib, "second_err": err2}
            ok = (not rec["err"]) and dw == 1 and srcs == [ct] and owner == [cu] and snks == [snk] and d2 == 0 and ib is False
            s.gate("P2 {0} {1}: err None, Wire +1, source #{2} (owner #{3}), sink #{4}, 2nd pass 0 / Is Broken? False".format(
                rid, cand, ct, cu, snk), ok, json.dumps(row, default=str)[:600])
            row["pass"] = ok
            table.append(row)
            stamp(s, "{0} {1} read back".format(rid, cand))
            if k == 0 and ok:
                n = ex.ops[len(diffs)]["acts"][-1]
                d = SX.compare(ex.step(n)["state"]["terminals"], real2, ex.bind, ex.allow)
                s.gate("P2b {0}: real graph == plan step {1} (compare n 0)".format(rid, n), d["n"] == 0,
                       json.dumps({a: b for a, b in d.items() if b and a != "n"}, default=str)[:600])
            real = real2
            if w or dw:                                  # a wire exists now: the next candidate cannot be measured clean
                break
    s.R["p2_table"] = table
    s.fact("P2 TABLE {0}".format(json.dumps(table, default=str)))
    s.dump(); stamp(s, "dumped")                                                     # noqa: E702


if __name__ == "__main__":
    st = time.strftime("%Y%m%d_%H%M%S")
    s = K.Stage(BED, BED_MD5, "constsrc82", work_name="D1_k_scratch_constsrc82_{0}.vi".format(st), preload=False,
                deadline_min=40, out_json=os.path.join(K.BENCH, "constsrc_l2a1_82.json"), task="card 82-3")
    rc = K.run(body, s)
    stamp(s, "K.run returned")
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60)
    time.sleep(4.0)
    tl = subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
    s.gate("H1 LabVIEW process gone at the end", "labview.exe" not in tl)
    s.gate("H2 D1_k md5 unchanged", K.md5(BED) == BED_MD5, K.md5(BED))
    s.gate("H3 scratch copy deleted", not os.path.exists(s.work), s.work)
    s.summary()
    sys.exit(1 if s.fails else 0)
