r"""meter_l2a1_86c - card 86-1 (c), PD192(c): ONE full executor replay of plan_l2a1 (42 ops / 46 acts) on a D1_k scratch,
FRESH LabVIEW, with the PD192(a) meter (stagexec.Meter) in WARN-ONLY mode (mem_stop_mb=None) so the run reaches error 2 if
it comes, and the act / MB where it comes is measured. No save; the scratch is deleted.
PRIOR ART: tools/bench/unroutable_l2a1_85.py (same Stage/LVBackend/Executor skeleton, which died at act 45 with error 2,
unroutable_l2a1_85.log:562), stagexec.lv_run (the E1 gate), meter_l2a1_86b.py (act 45 alone).
Error-2 handling: 85's hygiene hung ~13 min in close_panel after error 2, so on any non-ExecStop exception this script
records it, kills LabVIEW, resets gscript, and only then lets stagekit's hygiene run.
PREDICTION CONTRACT (a measurement - every number is reported, the gates only say whether it was measured):
  C1 the executor ran; its last op, the exception (if any) and its class are recorded
  C2 METER stamps: start + read + (pre, op, read) per executed op; per-op d_mb at 'op' (mutate) vs at 'read' (whole-VI read)
  C3 every executed op's diff == 0 (the 85 result for acts 1-44 is reproduced)
  R41/R42 (card 86-2) READ-ONLY, from the executor's own whole-VI read right after op 41 (act 45) / op 42 (act 46): the
     wire on #6007 / #6026 has sole source that face (owner tunnel #5680 / #6016) and sole sink BY UID #5082 / #5164 on #5058
  S41/S42 only if the replay completed: ordered 2nd pass (connect_from_wire, meter_l2a1_86b.py B3) wire_delta 0, Is Broken?
     False - run AFTER all 42 metered ops, so it cannot perturb the per-op memory numbers
  H  D1_k md5 unchanged, scratch deleted, LabVIEW gone.
    py tools/bgrun.py --material --max-min 50 --log tools/bench/meter_l2a1_86c.log -- py -u tools/bench/meter_l2a1_86c.py"""
import json, os, subprocess, sys, time                                              # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, stagexec as SX, gscript as g                                  # noqa: E401,E402
PLAN = os.path.join(K.BENCH, "sim/l2a1/plan_l2a1.json")
P, _ = SX.load_final_plan(PLAN)
BASE = SX._j(SX._abs(P["finalized"]["base"]["path"]))
BED, BED_MD5, FS = BASE["vi"], BASE["md5"], BASE["fs_tunnel_pairs"]
T0 = time.time()
# card 86-2: op k -> (tunnel, outer face, sink node, sink terminal, plan id); plan actions 45/46 (plan_l2a1.json)
RB = {41: (5680, 6007, 5058, 5082, "rw_6007_5082"), 42: (6016, 6026, 5058, 5164, "rw_6026_5164")}


def readback(ex, real, tun, face, node, snk, tag):
    """READ-ONLY: the wire on the face, its sources/owners and sinks BY UID, from the executor's own whole-VI read."""
    bt, bo = ex.bind["term"], ex.bind["obj"]
    f, sk, tn, nd = bt.get(face, face), bt.get(snk, snk), bo.get(tun, tun), bo.get(node, node)
    w = int(([r["wire_uid"] for r in real if r["term_uid"] == f] or [0])[0] or 0)
    on = [r for r in real if w and r["wire_uid"] == w]
    sr = [r for r in real if r["term_uid"] == sk]
    return {"tag": tag, "face": f, "tun": tn, "snk": sk, "node": nd, "wire": w,
            "srcs": sorted(r["term_uid"] for r in on if r["is_source"]),
            "own": sorted(set(r["owner_uid"] for r in on if r["is_source"])),
            "snks": sorted(r["term_uid"] for r in on if not r["is_source"]),
            "snk_owner": sr[0]["owner_uid"] if sr else None, "snk_name": sr[0].get("term_name") if sr else None}


def body(s):
    print(__doc__, flush=True)
    s.start(); s.discard_work()                                                      # noqa: E702
    be = SX.LVBackend(s, FS, mem_stop_mb=None)
    ex = SX.Executor(PLAN, be, log=lambda m: print(m, flush=True))
    assert [ex.ops[k - 1]["acts"] for k in RB] == [[45], [46]], [ex.ops[k - 1]["acts"] for k in RB]
    rb, _read = {}, be.read

    def read_hooked():                                   # card 86-2: the whole-VI read right after meter('op', 41|42)
        real = _read()
        last = be.meter.rows[-1] if be.meter.rows else {}
        k = last.get("k")
        if last.get("tag") == "op" and k in RB and k not in rb:
            try:
                rb[k] = readback(ex, real, *RB[k])
            except Exception as e:                                                   # noqa: BLE001
                rb[k] = {"err": "{0}: {1}".format(type(e).__name__, str(e)[:300])}
            s.fact("READBACK op {0} {1}".format(k, json.dumps(rb[k], default=str)[:600]))
        return real
    be.read = read_hooked
    stop, exc, real = "", "", None
    try:
        real = ex.run()
    except SX.ExecStop as e:
        stop = str(e)
    except Exception as e:                                                           # noqa: BLE001
        exc = "{0}: {1}".format(type(e).__name__, str(e)[:600])
        print("OBSERVED EXC during the replay: " + exc, flush=True)
        try:
            be.meter("exc", (ex.report[-1].get("k") if ex.report else None))
        except Exception as e2:                                                      # noqa: BLE001
            print("meter after exc failed: " + str(e2)[:200], flush=True)
    s.fact("STAMP {0:.0f} s executor done".format(time.time() - T0))
    rows = be.meter.rows
    last_op = max([r["k"] for r in rows if r["tag"] == "op"] or [0])
    last_rd = max([r["k"] for r in rows if r["tag"] == "read"] or [0])
    acts = next((o["acts"] for o in ex.ops if ex.ops.index(o) + 1 == last_op), None)
    per = [{"k": k, "acts": ex.ops[k - 1]["acts"], "kind": ex.ops[k - 1]["kind"],
            "pre": next((r["d_mb"] for r in rows if r["tag"] == "pre" and r["k"] == k), None),
            "op": next((r["d_mb"] for r in rows if r["tag"] == "op" and r["k"] == k), None),
            "read": next((r["d_mb"] for r in rows if r["tag"] == "read" and r["k"] == k), None),
            "mb": next((r["mb"] for r in rows if r["tag"] == "read" and r["k"] == k), None),
            "h": next((r["handles"] for r in rows if r["tag"] == "read" and r["k"] == k), None)}
           for k in range(1, last_op + 1)]
    for x in per:
        s.fact("PEROP k {k:2d} {kind:<14} acts {acts} d_pre {pre} d_op {op} d_read {read} -> {mb} MB, {h} handles".format(**x))
    sm = be.meter.summary()
    sm.update({"last_op_k": last_op, "last_op_acts": acts, "last_read_k": last_rd, "stop": stop[:600], "exc": exc,
               "error2": "error 2" in exc.lower() or "memory" in exc.lower(), "n_ops": len(ex.ops),
               "read_secs": be.reads})
    s.R["meter"], s.R["meter_summary"], s.R["per_op"] = rows, sm, per
    s.fact("METER SUMMARY {0}".format(json.dumps(sm, default=str)))
    diffs = [r["diff"]["n"] for r in ex.report if r.get("diff")]
    s.gate("C1 the replay ran; last op k {0} acts {1}; stop {2!r}; exc {3!r}".format(last_op, acts, stop[:120], exc[:160]),
           last_op > 0, "")
    s.gate("C2 meter stamps start+read+3/op for {0} executed op(s)".format(last_op), len(rows) >= 2 + 3 * last_op - 1, len(rows))
    s.gate("C3 every executed op diff 0 ({0} diffs, sum {1})".format(len(diffs), sum(diffs)), not any(diffs), diffs)
    for k, (tun, face, node, snk, tag) in RB.items():
        r = rb.get(k) or {}
        s.gate("R{0} {1}: after op {0} sole source #{2} (owner #{3}), sole sink BY UID #{4}".format(k, tag, face, tun, snk),
               r.get("srcs") == [r.get("face")] and r.get("own") == [r.get("tun")] and r.get("snks") == [r.get("snk")]
               and r.get("snk_owner") == r.get("node"), json.dumps(r, default=str)[:500])
    s.R["readback"] = rb
    if not exc and real is not None:                      # AFTER the metered replay: ordered 2nd pass -> Is Broken?
        try:
            be.addr.owners = ex.step(ex.ops[-1]["acts"][-1])["state"].get("owners") or be.addr.owners
        except Exception:                                                            # noqa: BLE001
            pass
        F = K.mod("build_opconnectfromwire_v0")
        lab = json.load(open(F.MAP_OUT, encoding="utf-8"))
        for k, (tun, face, node, snk, tag) in RB.items():
            w, sk, d2, ib = (rb.get(k) or {}).get("wire"), (rb.get(k) or {}).get("snk"), None, None
            if w:
                ns = s.net_sources(w, tag=tag)
                hit = [x for x in (ns.get("walk") or []) if x.get("is_source")]
                if len(hit) == 1:
                    (dd, nn, tt), _h = be.addr.triple(real, sk, False)
                    r2, _e2 = s.safe("second pass " + tag, lambda: F.connect_from_wire(s.work, w, int(hit[0]["i"]), dd, nn, tt, lab))
                    s.junk_purge(tag + " 2nd")
                    if r2:
                        d2, ib = r2[0], (r2[3] or {}).get("Is Broken?")
            be.meter("2nd", k)
            s.gate("S{0} {1} ordered 2nd pass wire_delta 0, Is Broken? False".format(k, tag), d2 == 0 and ib is False, (d2, ib))
    s.dump()
    if exc:                                                    # 85: hygiene hung ~13 min in close_panel after error 2
        subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60)
        time.sleep(4.0)
        g.reset()
        s.fact("LabVIEW KILLED after the exception, before hygiene (85's close_panel hang)")


if __name__ == "__main__":
    st = time.strftime("%Y%m%d_%H%M%S")
    s = K.Stage(BED, BED_MD5, "meter86c", work_name="D1_k_scratch_meter86c_{0}.vi".format(st), preload=False,
                deadline_min=46, out_json=os.path.join(K.BENCH, "meter_l2a1_86c.json"), task="card 86-1 (c)")
    rc = K.run(body, s)
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60)
    time.sleep(4.0)
    tl = subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
    s.gate("H1 LabVIEW process gone at the end", "labview.exe" not in tl)
    s.gate("H2b D1_k md5 unchanged", K.md5(BED) == BED_MD5, K.md5(BED))
    s.gate("H3b scratch copy deleted", not os.path.exists(s.work), s.work)
    s.summary()
    sys.exit(1 if s.fails else 0)
