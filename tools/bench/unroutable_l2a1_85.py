r"""unroutable_l2a1_85 - card 85-2 P1/P2/P3: the two PD191 routes exercised THROUGH stagexec on a D1_k scratch.
PRIOR ART: tools/bench/constsrc_l2a1_85.py (same executor skeleton and read-back gates, 14/0 in card 85-1).
METHOD: the real executor (LVBackend, stagexec after card 85-2: 'ctlsink' for rw_10988_17272, 'tunouter' for rw_6007_5082 and
rw_6026_5164, every other row on its 85-1 route) runs ALL 42 ops; P1 is read by a backend hook right BEFORE act 45 (the live
graph the executor hands that op). Nothing is saved; the scratch is deleted.
PREDICTION CONTRACT:
  P0 every executed op's graph == its plan step (diff 0); R41 routed 'ctlsink', R45/R46 'tunouter'; no ExecStop
  P1 before act 45: #6007 owner SelectorTunnel #5680, #6026 owner #6016, each the ONLY OuterTerminal of its tunnel, source,
     bare; both tunnels in report_all('SelectorTunnel'); sinks #5082 'Bead is good? array in' / #5164 'x,y,z array' on SubVI
     #5058, bare (the pairing is the S1 names; no data-type reader exists)
  P2/P3 per row: op err '' and Wire +1; the new wire's ONLY source terminal == the planned source, owner == the planned node /
     tunnel; ONLY sink == the plan sink; node sinks: ordered second pass (connect_from_wire) wire_delta 0, Is Broken? False
  H  D1_k md5 unchanged, scratch deleted, LabVIEW gone.
    py tools/bgrun.py --material --max-min 50 --log tools/bench/unroutable_l2a1_85.log -- py -u tools/bench/unroutable_l2a1_85.py"""
import json, os, subprocess, sys, time                                              # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, stagexec as SX, gscript as g                                  # noqa: E401,E402
PLAN = os.path.join(K.BENCH, "sim/l2a1/plan_l2a1.json")
P, _ = SX.load_final_plan(PLAN)
BASE = SX._j(SX._abs(P["finalized"]["base"]["path"]))
BED, BED_MD5, FS = BASE["vi"], BASE["md5"], BASE["fs_tunnel_pairs"]
ROWS = (("rw_10988_17272", "ctlsink", 10969, 10988, 17272), ("rw_6007_5082", "tunouter", 5680, 6007, 5082),
        ("rw_6026_5164", "tunouter", 6016, 6026, 5164))
T0 = time.time()


class ProbeBE(SX.LVBackend):
    """LVBackend + the P1 read-only check on the live graph handed to the op carrying act 45 (before its write)."""
    def connect(self, src, dst, real, loop_of, op):
        if 45 in op["acts"] and not getattr(self, "p1", None):
            self.p1 = p1_check(self.s, real)
        return SX.LVBackend.connect(self, src, dst, real, loop_of, op)


def p1_check(s, real):
    tl = set(o["uid"] for o in g.report_all(s.work, "SelectorTunnel"))
    out = {}
    for _rid, _k, tun, face, snk in ROWS[1:]:
        f = [r for r in real if r["term_uid"] == face]
        outer = [r["term_uid"] for r in real if r["owner_uid"] == tun and r["term_class"] == "OuterTerminal"]
        sk = [r for r in real if r["term_uid"] == snk]
        out[face] = {"face": f, "outer": outer, "in_traverse": tun in tl, "sink": sk}
        ok = (len(f) == 1 and f[0]["owner_uid"] == tun and f[0]["is_source"] and not f[0]["wire_uid"] and outer == [face]
              and tun in tl and len(sk) == 1 and sk[0]["owner_uid"] == 5058 and not sk[0]["wire_uid"])
        s.gate("P1 face #{0}: owner tunnel #{1}, its only outer face, source, bare, in report_all; sink #{2} {3!r} bare on #5058".format(
            face, tun, snk, sk[0]["term_name"] if sk else None), ok, json.dumps(out[face], default=str)[:600])
        if not ok:
            raise SX.ExecStop("P1 mismatch on face #{0}: BLOCKED before any write (card rule)".format(face))
    return out


def body(s):
    print(__doc__, flush=True)
    s.start(); s.discard_work()                                                      # noqa: E702
    be = ProbeBE(s, FS)
    ex = SX.Executor(PLAN, be, log=lambda m: print(m, flush=True))
    stop = ""
    try:
        ex.run()
    except SX.ExecStop as e:
        stop = str(e)
    s.fact("STAMP {0:.0f} s executor done".format(time.time() - T0))
    diffs = [r["diff"]["n"] for r in ex.report if r.get("diff")]
    hows = dict((i, (r.get("result") or {}).get("how")) for r in ex.report for i in (r.get("ids") or []) if i in [x[0] for x in ROWS])
    s.gate("P0 all {0} ops diff 0; routes ctlsink/tunouter/tunouter; no stop".format(len(ex.ops)),
           not stop and len(diffs) == len(ex.ops) + 1 and not any(diffs) and [(hows.get(x[0]) or [None])[0] for x in ROWS] == [x[1] for x in ROWS],
           "stop {0!r}; diffs {1}; hows {2}".format(stop[:500], sum(diffs), json.dumps(hows, default=str)[:400]), fatal=True)
    F = K.mod("build_opconnectfromwire_v0")
    lab = json.load(open(F.MAP_OUT, encoding="utf-8"))
    ops = dict((o["verb"], o) for o in s.R["ops"] if o["verb"] in ("wire_ctlsink", "wire_tunouter"))
    real, table = be.read(), []
    for rid, kind, owner_u, src_t, snk in ROWS:
        rc = [x for x in real if x["term_uid"] == src_t][0]
        w = int(rc["wire_uid"] or 0)
        srcs = sorted(x["term_uid"] for x in real if w and x["wire_uid"] == w and x["is_source"])
        snks = sorted(x["term_uid"] for x in real if w and x["wire_uid"] == w and not x["is_source"])
        own = sorted(set(x["owner_uid"] for x in real if w and x["wire_uid"] == w and x["is_source"]))
        opr = [o for o in s.R["ops"] if o["verb"] == "wire_" + kind]
        d2, ib, err2 = "n/a (CT sink: 179(b) partners)", None, None
        if kind == "tunouter" and w:
            ns = s.net_sources(w, tag=rid)
            hit = [x for x in (ns.get("walk") or []) if x.get("is_source")]
            if len(hit) == 1:
                (dd, nn, tt), _how = be.addr.triple(real, snk, False)
                res, err2 = s.safe("second pass", lambda: F.connect_from_wire(s.work, w, int(hit[0]["i"]), dd, nn, tt, lab))
                s.junk_purge(rid + " 2nd")
                if res:
                    d2, ib, err2 = res[0], (res[3] or {}).get("Is Broken?"), err2 or res[2]
        row = {"row": rid, "ops": [(o.get("err"), o.get("result")) for o in opr], "wire": w, "sources": srcs, "source_owner": own,
               "sinks": snks, "second_delta": d2, "is_broken": ib, "second_err": err2}
        ok = (bool(opr) and all(not o.get("err") and (o.get("result") or [0])[0] == 1 for o in opr) and srcs == [src_t]
              and own == [owner_u] and snks == [snk] and (kind == "ctlsink" or (d2 == 0 and ib is False)))
        s.gate("{0} {1} ({2}): Wire +1 no error; sole source #{3} (owner #{4}); sole sink #{5}{6}".format(
            "P2" if kind == "ctlsink" else "P3", rid, kind, src_t, owner_u, snk, "" if kind == "ctlsink" else "; 2nd pass 0 / Is Broken? False"),
            ok, json.dumps(row, default=str)[:600])
        table.append(dict(row, **{"pass": ok}))
        real = be.read()
    s.R["p1"], s.R["p23_table"] = getattr(be, "p1", None), table
    s.fact("P23 TABLE {0}".format(json.dumps(table, default=str)))
    s.dump()


if __name__ == "__main__":
    st = time.strftime("%Y%m%d_%H%M%S")
    s = K.Stage(BED, BED_MD5, "unroutable85", work_name="D1_k_scratch_unroutable85_{0}.vi".format(st), preload=False,
                deadline_min=45, out_json=os.path.join(K.BENCH, "unroutable_l2a1_85.json"), task="card 85-2 P1-P3")
    rc = K.run(body, s)
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60)
    time.sleep(4.0)
    tl = subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
    s.gate("H1 LabVIEW process gone at the end", "labview.exe" not in tl)
    s.gate("H2 D1_k md5 unchanged", K.md5(BED) == BED_MD5, K.md5(BED))
    s.gate("H3 scratch copy deleted", not os.path.exists(s.work), s.work)
    s.summary()
    sys.exit(1 if s.fails else 0)
