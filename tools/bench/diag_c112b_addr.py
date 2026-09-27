r"""diag_c112b_addr - card 112-2 S3 on LabVIEW, READ-ONLY: every B2a end of tools/bench/plan_l2b2a.json addressed on a dated SCRATCH
byte copy of the bed by the REAL executor path (stagexec.LVBackend + Addr + LVReader, the D2 uid echo through OpNodeTermsUid_v0;
the (v) LoopTunnel owner route). Nothing is wired, moved or saved; the scratch is deleted at close (no stagekit mutating verb).
PRIOR ART: diag_c112a_b2a_route2.log (offline, 1/7), diag_c112b_route.log (offline, 7/7 after (v)+D2); stagexec.lv_run's read.
PREDICTION: K0 the live read of the scratch == graph_l2b1 (compare, diff 0); A1 each of the 7 BARE faces (t25588 t9234 t9092
t25606 t29624 t29928 t2282) resolves to exactly ONE owner Terminals[] entry by uid echo, owner = #10170/#1359/#1359/#10170/
#29874/#29874/#2222; A2 the 2 WIRED sources (t8958, t28172) resolve; A3 CT #403 by 179(b); A4 SRB1/SRB2 (right #9603 / #25545)
are Shift Registers[] entries of WhileLoop #10170; H bed md5 unchanged, scratch deleted, LabVIEW gone.
    py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_c112b_addr.log -- py -u tools/bench/diag_c112b_addr.py"""
import json, os, subprocess, sys, time                                              # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, stagexec as X                                   # noqa: E401,E402
GRAPH = X._j(os.path.join(K.BENCH, "graph_l2b1_20260927.json"))
PLAN = X._j(os.path.join(K.BENCH, "plan_l2b2a.json"))
BED, BED_MD5 = GRAPH["vi"], GRAPH["md5"]


def body(s):
    print(__doc__, flush=True)
    s.start()
    s.scratches.append(s.work)             # read-only diagnostic: the work copy is deleted at close (nothing is saved)
    be = X.LVBackend(s, GRAPH["fs_tunnel_pairs"])
    be.addr.owners = GRAPH["owners"]
    real = be.read()
    d = X.compare(X.dedupe(GRAPH["terminals"]), real, {"obj": {}, "term": {}, "diag": {}})
    s.gate("K0 the live read of the scratch == graph_l2b1 (terminal-level diff)", d["n"] == 0, d["n"])
    loop_of = dict((u, v["loop"]) for u, v in X.base_registers(GRAPH).items())
    want_owner = {25588: 10170, 9234: 1359, 9092: 1359, 25606: 10170, 29624: 29874, 29928: 29874, 2282: 2222}
    res = {}
    for a in PLAN["actions"]:
        for side, src in (("src", True), ("dst", False)):
            t = int(a[side]["term_uid"])
            r = next(x for x in real if x["term_uid"] == t)
            if X.is_ct(r):
                c, how = be.addr.ct(real, t)
                res[t] = ("ct", c["diag"], how)
                continue
            if r["owner_class"] in X.SR_CLS and r["term_class"] == "InnerTerminal":
                continue                   # a wire_sr end: addressed by register index (A4), not by a Terminals[] triple
            try:
                (di, ni, ti), how = be.addr.triple(real, t, src, loop_of)
                owner = be.addr.rd.node_uids(di)[ni]
                res[t] = (owner, ti, how)
            except X.ExecStop as e:
                res[t] = ("STOP", str(e)[:300])
            s.fact("END {0} {1} #{2} ({3} {4}): {5}".format(a["id"], side, t, r["owner_class"], r["term_class"], res[t]))
    bare_ok = [t for t, o in want_owner.items() if res.get(t, ("",))[0] == o and "uid echo" in str(res[t][2])]
    s.gate("A1 each BARE B2a face -> ONE owner Terminals[] entry by uid echo, on the predicted owner", len(bare_ok) == 7,
           dict((t, res.get(t)) for t in want_owner))
    s.gate("A2 the wired sources #8958 / #28172 resolve", all(res.get(t, ("STOP",))[0] != "STOP" for t in (8958, 28172)),
           [res.get(8958), res.get(28172)])
    s.gate("A3 CT #403 by its own uid (179(b))", res.get(403, ("",))[0] == "ct", res.get(403))
    li = s.uid_index("WhileLoop", 10170)
    ks = [s.safe("reg_index #{0}".format(u), lambda u=u: be._reg_index(li, u))[0] for u in (9603, 25545)]
    s.gate("A4 SRB1 R #9603 / SRB2 R #25545 are Shift Registers[] entries of WhileLoop #10170", None not in ks and ks[0] != ks[1], (li, ks))
    s.R["c112b_addr"] = dict((str(k), v) for k, v in res.items())
    s.dump()


if __name__ == "__main__":
    st = K.Stage(BED, BED_MD5, "scratch_c112b_addr", deadline_min=17, task="card 112-2 S3",
                 out_json=os.path.join(K.BENCH, "diag_c112b_addr.json"))
    rc = K.run(body, st)
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)  # noqa: E702
    gone = "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
    st.gate("H LabVIEW gone at exit", gone)
    sys.exit(0 if not st.fails else 1)
