r"""meter_l2a1_86d - card 86-3: the separator of archive/peer/2026-09-25-hyp-meter86c-err2.md:98-107. FRESH LabVIEW, D1_k
scratch, ops 1-40 with the per-op whole-VI reads SKIPPED, ONE step_44 check (a real read + compare), then op 41 (act 45) +
ONE whole-VI read + R41 uid read-back; if clean, op 42 + its read (R42), then the ordered 2nd pass. No save.
PRIOR ART: meter_l2a1_86c.py (readback, RB - imported), stagexec.Executor.run reused whole; be.read/connect/wire_sr and
SX.compare are wrapped IN MEMORY (stagexec.py untouched). SKIP POLICY: real reads only after add_sr/tunnel (bind_new), op 40
(= step_44 check), ops 41/42; other reads return the last real read, compare skipped. An ADDRESSING ExecStop on a stale read
(no 'op error' = pre-mutation) gets one fresh read + one retry; a silent misroute is caught by the whole-graph step_44 check.
PREDICTION CONTRACT: C1 ops 1-40 ran (skips/retries counted) · C2 step_44 diff reported (want 0) · M MB+handles at load/op40/
check/op41/read41 · E2 error 2 at read41 yes/no (a RESULT) · R41/R42 sole source face, sole sink by uid #5082/#5164 ·
S41/S42 2nd pass wire_delta 0, Is Broken? False · H D1_k md5, scratch gone, LV gone.
    py tools/bgrun.py --material --max-min 40 --log tools/bench/meter_l2a1_86d.log -- py -u tools/bench/meter_l2a1_86d.py"""
import importlib.util, json, os, subprocess, sys, time                              # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import stagekit as K, stagexec as SX, gscript as g                                  # noqa: E401,E402
_sp = importlib.util.spec_from_file_location("m86c", os.path.join(HERE, "meter_l2a1_86c.py"))
M = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(M)                 # noqa: E702
PLAN, BED, BED_MD5, FS, RB = M.PLAN, M.BED, M.BED_MD5, M.FS, M.RB
T0 = time.time()

def body(s):
    print(__doc__, flush=True)
    s.start(); s.discard_work()                                                      # noqa: E702
    be = SX.LVBackend(s, FS, mem_stop_mb=None)
    ex = SX.Executor(PLAN, be, log=lambda m: print(m, flush=True))
    assert [ex.ops[k - 1]["acts"] for k in RB] == [[45], [46]] and ex.ops[39]["acts"] == [44]
    need, ex.ops = set(k for k, o in enumerate(ex.ops, 1) if o["kind"] in ("add_sr", "tunnel")) | {40, 41, 42}, ex.ops[:42]
    st = {"cur": None, "stale": False, "skipped": [], "fresh": [], "retries": [], "rb": {}, "chk44": None}
    _read, _cmp, _conn, _wsr = be.read, SX.compare, be.connect, be.wire_sr

    def read():
        rows = be.meter.rows
        k = rows[-1].get("k") if rows else 0
        if st["cur"] is not None and rows and rows[-1]["tag"] == "op" and k not in need:
            st["stale"] = True; st["skipped"].append(k)                              # noqa: E702
            return st["cur"]
        st["stale"], st["cur"] = False, _read(); st["fresh"].append(k)               # noqa: E702
        if rows and rows[-1]["tag"] == "op" and k in RB:
            try:
                st["rb"][k] = M.readback(ex, st["cur"], *RB[k])
            except Exception as e:                                                   # noqa: BLE001
                st["rb"][k] = {"err": "{0}: {1}".format(type(e).__name__, str(e)[:300])}
            s.fact("READBACK op {0} {1}".format(k, json.dumps(st["rb"][k], default=str)[:600]))
        return st["cur"]

    def compare(*a, **kw):
        if st["stale"]:
            return {"n": 0, "skipped": True}
        d = _cmp(*a, **kw)
        if be.meter.rows and be.meter.rows[-1]["tag"] == "read" and be.meter.rows[-1]["k"] == 40:
            st["chk44"] = d
            s.fact("STEP44 CHECK vs {0}: diff {1} {2}".format(ex.step_paths[44], d["n"], json.dumps(
                {x: y for x, y in d.items() if y and x not in ("n", "who")}, default=str)[:600]))
        return d

    def retry(fn):
        def w(*a):
            try:
                return fn(*a)
            except SX.ExecStop as e:
                if "op error" in str(e) or not st["stale"]:            # post-mutation, or the read was already fresh
                    raise
                s.fact("STALE-ADDRESS {0}: fresh read + one retry ({1})".format(fn.__name__, str(e)[:200]))
                st["cur"] = _read(); st["retries"].append(str(e)[:120])              # noqa: E702
                a = tuple(st["cur"] if x is not None and isinstance(x, list) and x and isinstance(x[0], dict) else x for x in a)
                return fn(*a)
        return w
    be.read, SX.compare, be.connect, be.wire_sr = read, compare, retry(_conn), retry(_wsr)
    exc, real = "", None
    try:
        real = ex.run()
    except Exception as e:                                          # noqa: BLE001  (ExecStop included, named by class)
        exc = "{0}: {1}".format(type(e).__name__, str(e)[:600])
    SX.compare, rows = _cmp, be.meter.rows
    print("OBSERVED END of replay: exc {0!r}".format(exc[:300]), flush=True)
    pick = lambda tag, k: next(({"mb": r["mb"], "handles": r["handles"]} for r in rows if r["tag"] == tag and r["k"] == k), None)  # noqa: E731
    mem = {"after_load": pick("start", 0), "after_op40_pre_check": pick("op", 40), "after_step44_check": pick("read", 40),
           "after_op41": pick("op", 41), "after_read41": pick("read", 41), "after_op42": pick("op", 42), "after_read42": pick("read", 42)}
    e2, last_op = "error 2" in exc.lower() or "memory" in exc.lower(), max([r["k"] for r in rows if r["tag"] == "op"] or [0])
    s.R.update(meter=rows, meter_summary=be.meter.summary(), mem=mem, exc=exc, error2=e2, last_op=last_op, readback=st["rb"],
               skipped=st["skipped"], fresh=st["fresh"], retries=st["retries"], step44=st["chk44"], read_secs=be.reads)
    s.fact("MEM {0}".format(json.dumps(mem)))
    s.fact("READS skipped {0[skipped]} / real {0[fresh]} / retries {0[retries]}".format(st))
    s.fact("E2 RESULT: last op k {0}; error 2 {1}; exc {2!r}".format(last_op, "YES" if e2 else "no", exc[:300]))
    s.gate("C1 ops 1-40 ran with reads skipped (last op k {0})".format(last_op), last_op >= 40, len(st["skipped"]))
    n44 = (st["chk44"] or {}).get("n"); s.gate("C2 step_44 check measured: diff {0}".format(n44), n44 is not None, n44)  # noqa: E702
    s.gate("M private MB measured at load/op40/check/op41/read41", all(mem[x] for x in list(mem)[:5]) or e2, mem)
    for k, (tun, face, node, snk, tag) in RB.items():
        r = st["rb"].get(k) or {}
        s.gate("R{0} {1}: sole source #{2} (owner #{3}), sole sink BY UID #{4}".format(k, tag, face, tun, snk),
               r.get("srcs") == [r.get("face")] and r.get("own") == [r.get("tun")] and r.get("snks") == [r.get("snk")]
               and r.get("snk_owner") == r.get("node"), json.dumps(r, default=str)[:500])
    if not exc and real is not None:                              # both reads clean -> the ordered 2nd pass (86c B3)
        F = K.mod("build_opconnectfromwire_v0"); lab = json.load(open(F.MAP_OUT, encoding="utf-8"))  # noqa: E702
        for k, (tun, face, node, snk, tag) in RB.items():
            w, sk, d2, ib = (st["rb"].get(k) or {}).get("wire"), (st["rb"].get(k) or {}).get("snk"), None, None
            hit = [x for x in (s.net_sources(w, tag=tag).get("walk") or []) if x.get("is_source")] if w else []
            if len(hit) == 1:
                (dd, nn, tt), _h = be.addr.triple(real, sk, False)
                r2, _e2 = s.safe("second pass " + tag, lambda: F.connect_from_wire(s.work, w, int(hit[0]["i"]), dd, nn, tt, lab))
                s.junk_purge(tag + " 2nd"); d2, ib = (r2[0], (r2[3] or {}).get("Is Broken?")) if r2 else (None, None)  # noqa: E702
            s.gate("S{0} {1} ordered 2nd pass wire_delta 0, Is Broken? False".format(k, tag), d2 == 0 and ib is False, (d2, ib))
    s.dump()
    if exc:                                                    # 85: hygiene hung ~13 min in close_panel after error 2
        subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4.0); g.reset()  # noqa: E702
        s.fact("LabVIEW KILLED after the exception, before hygiene (85's close_panel hang)")


if __name__ == "__main__":
    ts = time.strftime("%Y%m%d_%H%M%S")
    s = K.Stage(BED, BED_MD5, "meter86d", work_name="D1_k_scratch_meter86d_{0}.vi".format(ts), preload=False,
                deadline_min=36, out_json=os.path.join(K.BENCH, "meter_l2a1_86d.json"), task="card 86-3")
    K.run(body, s)
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4.0)  # noqa: E702
    tl = subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
    s.gate("H1 LabVIEW process gone at the end", "labview.exe" not in tl)
    s.gate("H2b D1_k md5 unchanged", K.md5(BED) == BED_MD5, K.md5(BED))
    s.gate("H3b scratch copy deleted", not os.path.exists(s.work), s.work)
    s.summary()
    sys.exit(1 if s.fails else 0)
