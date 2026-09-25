r"""meter_l2a1_86b - card 86-1 (b), PD192(b): act 45 ALONE (after the prefix it needs) on a FRESH LabVIEW, metered.
PRIOR ART: tools/bench/unroutable_l2a1_85.py (same Stage/LVBackend skeleton, the P1 face/sink check and the P3 read-back +
ordered second pass), archive/peer/2026-09-25-hyp-unroutable-err2-85.md section 5 (this test), stagexec.Meter (PD192(a)).
PREFIX: ops 1-22 = acts 1-22. Run 1 (86b.log:59) FAILED B1 because act 1 alone leaves #6007 a SINK face: the step files
themselves say #6007 turns source only at step_22 (sr2_L0 wires SR2L.inner into case #5540; #6026 at step_18) - measured
offline over tools/bench/sim/l2a1/step_*.json. So the prefix is the executor's own run over ops[:22] (diff-checked per op).
METHOD: Executor.run() with ex.ops truncated to the first 22, then Executor.execute() on op 41 (act 45, the plan's own routing
-> 'tunouter'), the whole-VI read_live; then 5 NO-EDIT read_live calls (the per-read memory cost in isolation). No save.
PREDICTION CONTRACT:
  B0 ops 1-22 each diff 0 vs their step file (Executor.run raises otherwise)
  B1 before act 45: #6007 source, bare, its tunnel #5680's only OuterTerminal; #5082 bare sink on SubVI #5058
  B2 act 45 routed 'tunouter', op err ''; afterwards the wire on #6007 has ONE source #6007 (owner #5680) and ONE sink,
     read back BY UID == #5082 ('SubVI[17].t0' == #5082)
  B3 ordered second pass (connect_from_wire onto the same sink) wire_delta 0, Is Broken? False
  B4 no LabVIEW error 2 / RPC failure on any read; METER line per step (private MB, handles)
  H  D1_k md5 unchanged, scratch deleted, LabVIEW gone.
    py tools/bgrun.py --material --max-min 25 --log tools/bench/meter_l2a1_86b.log -- py -u tools/bench/meter_l2a1_86b.py"""
import json, os, subprocess, sys, time                                              # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402
PLAN = os.path.join(K.BENCH, "sim/l2a1/plan_l2a1.json")
P, _ = SX.load_final_plan(PLAN)
BASE = SX._j(SX._abs(P["finalized"]["base"]["path"]))
BED, BED_MD5, FS = BASE["vi"], BASE["md5"], BASE["fs_tunnel_pairs"]
TUN, FACE, SNK, NODE = 5680, 6007, 5082, 5058


def body(s):
    print(__doc__, flush=True)
    s.start(); s.discard_work()                                                      # noqa: E702
    be = SX.LVBackend(s, FS, mem_stop_mb=None)
    m = be.meter
    ex = SX.Executor(PLAN, be, log=lambda x: print(x, flush=True))
    op41 = ex.ops[40]
    assert op41["acts"] == [45] and ex.ops[21]["acts"] == [22], (op41, ex.ops[21])
    ex.ops = ex.ops[:22]
    stop = ""
    try:
        real = ex.run()
    except SX.ExecStop as e:
        stop = str(e)
    diffs = [r["diff"]["n"] for r in ex.report if r.get("diff")]
    s.gate("B0 ops 1-22 ran, each diff 0 vs its step file", not stop and len(diffs) == 23 and not any(diffs),
           "stop {0!r} diffs {1}".format(stop[:400], diffs), fatal=True)
    be.addr.owners = ex.step(22)["state"].get("owners") or be.addr.owners
    f = [r for r in real if r["term_uid"] == FACE]
    outer = [r["term_uid"] for r in real if r["owner_uid"] == TUN and r["term_class"] == "OuterTerminal"]
    sk = [r for r in real if r["term_uid"] == SNK]
    s.gate("B1 #6007 source bare, sole outer face of #5680; #5082 bare sink on #5058",
           len(f) == 1 and f[0]["is_source"] and not f[0]["wire_uid"] and outer == [FACE] and len(sk) == 1
           and sk[0]["owner_uid"] == NODE and not sk[0]["wire_uid"], json.dumps({"f": f, "outer": outer, "sk": sk}, default=str)[:600],
           fatal=True)
    s.fact("SINK NAME #5082 {0!r}".format(sk[0]["term_name"]))
    st44, st45 = ex.step(44)["state"], ex.step(45)["state"]
    res, err = None, ""
    try:
        res = ex.execute(op41, st44, st45, real)
    except SX.ExecStop as e:
        err = str(e)
    m("op", 45)
    s.fact("ACT45 result {0} err {1!r}".format(json.dumps(res, default=str)[:300], err[:300]))
    real = be.read(); m("read", 45)                                                  # noqa: E702
    w = int(([r["wire_uid"] for r in real if r["term_uid"] == FACE] or [0])[0] or 0)
    srcs = sorted(r["term_uid"] for r in real if w and r["wire_uid"] == w and r["is_source"])
    snks = sorted(r["term_uid"] for r in real if w and r["wire_uid"] == w and not r["is_source"])
    own = sorted(set(r["owner_uid"] for r in real if w and r["wire_uid"] == w and r["is_source"]))
    s.fact("READBACK wire {0}: sources {1} owner {2} sinks {3}".format(w, srcs, own, snks))
    s.gate("B2 act 45 'tunouter', no error; sole source #6007 (owner #5680); sole sink BY UID == #5082",
           not err and (res or {}).get("how", [None])[0] == "tunouter" and srcs == [FACE] and own == [TUN] and snks == [SNK],
           json.dumps({"how": (res or {}).get("how"), "w": w, "srcs": srcs, "own": own, "snks": snks}, default=str)[:500])
    d2, ib = None, None
    if w:
        F = K.mod("build_opconnectfromwire_v0")
        lab = json.load(open(F.MAP_OUT, encoding="utf-8"))
        ns = s.net_sources(w, tag="rw_6007_5082")
        hit = [x for x in (ns.get("walk") or []) if x.get("is_source")]
        if len(hit) == 1:
            (dd, nn, tt), _h = be.addr.triple(real, SNK, False)
            r2, e2 = s.safe("second pass", lambda: F.connect_from_wire(s.work, w, int(hit[0]["i"]), dd, nn, tt, lab))
            s.junk_purge("rw_6007_5082 2nd")
            if r2:
                d2, ib = r2[0], (r2[3] or {}).get("Is Broken?")
    m("2nd", 45)
    s.gate("B3 ordered second pass wire_delta 0, Is Broken? False", d2 == 0 and ib is False, (d2, ib))
    for i in range(1, 6):
        be.read(); m("read", 100 + i)                                                # noqa: E702
    s.R["meter"], s.R["meter_summary"] = m.rows, m.summary()
    s.fact("METER SUMMARY {0}".format(json.dumps(m.summary(), default=str)))
    s.gate("B4 every read completed (no error 2 / RPC failure)", True, len(be.reads))
    s.dump()


if __name__ == "__main__":
    st = time.strftime("%Y%m%d_%H%M%S")
    s = K.Stage(BED, BED_MD5, "meter86b", work_name="D1_k_scratch_meter86b_{0}.vi".format(st), preload=False,
                deadline_min=32, out_json=os.path.join(K.BENCH, "meter_l2a1_86b.json"), task="card 86-1 (b)")
    rc = K.run(body, s)
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60)
    time.sleep(4.0)
    tl = subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
    s.gate("H1 LabVIEW process gone at the end", "labview.exe" not in tl)
    s.gate("H2b D1_k md5 unchanged", K.md5(BED) == BED_MD5, K.md5(BED))
    s.gate("H3b scratch copy deleted", not os.path.exists(s.work), s.work)
    s.summary()
    sys.exit(1 if s.fails else 0)
