r"""diag_c136_4_mem - card 136-4 (PD298(f)/PD300(c)): WHERE does LabVIEW error 2 really appear today? MEASUREMENT ONLY.
The 700 MB stop (stagexec.MEM_STOP_MB) sits on ONE error-2 observation at ~770 MB (com-driving.md:308-312). A dated byte copy
claudeDev\scratch_c136_4_mem_<ts>.vi of the P3b2b bed (md5 39511877; the bed is never opened) in a FRESH LabVIEW; warn-only meter
(stagexec.Meter stop_mb=None, stagexec.py:72-97); the Executor's checkpoint read repeated until the first error 2, 1300 MB, 40 reads
or 20 min. Nothing is saved (an error-2 state writes stale files).
PRIOR ART (reused, nothing new built): skeleton + read + meter = diag_c129_6_mem.py W1 (read_ck == stagexec LVBackend.read =
wiki_build.read_live(work, fs_pairs) :233); fs_pairs from graph_qrt_pool_20260928.json as diag_c136_1_graph.py; error text from
gscript.report_all :739-741 / allterms.read_terms :80-82 (RuntimeError '... error <code>: <source>'); fresh start =
bench_prep.restart_labview :74-79; kill = stagexec.kill_labview_at_exit :3666. X10 (stage_prerun memory margin) is NOT APPLICABLE:
this is a warn-only measurement whose purpose is to cross the 690/700 MB lines; its model counts read call sites, not iterations.
PREDICTION (mechanics; the MB curve and the error-2 point are the measurement): P1 LabVIEW.exe PE Machine 0x8664 (64-bit);
R1 >= 1 read, every successful read returns the same > 0 terminal row count; R2 handles flat across reads 2.. (max - min <= 100);
R3 stop reason one of error2 / mb / reads / time and, if an exception stopped it, its text is classified; X bed md5 unchanged;
H5 ref counter opened == closed; scratch deleted; LabVIEW gone; fresh-start read after the kill.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c136_4_mem.log -- py -u tools/bench/diag_c136_4_mem.py"""
import json, os, re, struct, sys, time                                                       # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K, stagexec as SX                                                         # noqa: E401,E402
g = K.g
PL = json.load(open(os.path.join(HERE, "diag_c136_4_mem_plan.json"), encoding="utf-8"))   # ONE literal: stage_prerun.plan_files
BED, BEDM, FSP = PL["input"]["vi"], PL["input"]["md5"], PL["fs_pairs_from"]
NMAX, MBMAX, TMAX, HFLAT = int(PL["max_reads"]), float(PL["max_mb"]), float(PL["max_loop_min"]) * 60.0, int(PL["handle_flat"])
DRY = bool(getattr(g.report_all, "_dry", False))
ERR2 = re.compile(r"error 2:|memory is full", re.I)
s = K.Stage(BED, BEDM, "scratch_c136_4_mem", preload=False, deadline_min=26, reserve_s=180,
            out_json=os.path.join(HERE, "diag_c136_4_mem.json"), task="card 136-4")
WB = K.mod("wiki_build")
fsp = json.load(open(os.path.join(ROOT, FSP), encoding="utf-8"))["fs_tunnel_pairs"]


def probe():
    if DRY:
        return None, None
    pb, _e = s.safe("private_bytes", K.private_bytes)
    hc, _e = s.safe("labview_handles", K.mod("bench_prep").labview_handles)
    return (pb if isinstance(pb, int) else None), (hc if isinstance(hc, int) else None)


M = SX.Meter(probe, stop_mb=None, log=lambda m: print(m, flush=True))


def pe_bits(exe):                                   # offline: COFF Machine + optional-header magic
    P = PL["pe"]
    with open(exe, "rb") as f:
        b = f.read(int(P["read_bytes"]))
    off = struct.unpack_from("<I", b, 0x3C)[0]
    sig, mach, magic = b[off:off + 4], hex(struct.unpack_from("<H", b, off + 4)[0]), hex(struct.unpack_from("<H", b, off + 24)[0])
    bits = dict((64 if k == "x64" else 32, v) for k, v in P.items() if k != "read_bytes")
    return {"e_lfanew": hex(off), "sig_ok": sig == b"PE\x00\x00", "machine": mach, "magic": magic,
            "bits": next((n for n, v in bits.items() if v == {"machine": mach, "magic": magic}), None)}


def read_ck():                                      # == stagexec LVBackend.read (diag_c129_6_mem.read_ck)
    lv = WB.read_live(s.work, fs_pairs=fsp)
    return len(SX.dedupe(lv["terminals"]))


def body(_):
    print(__doc__, flush=True)
    pe = pe_bits(PL["lv_exe"])
    s.R["pe"] = pe
    s.fact("P1 {0} PE header: {1}".format(PL["lv_exe"], pe))
    s.gate("P1 LabVIEW.exe PE header read: Machine {0}, magic {1} -> {2}-bit".format(pe["machine"], pe["magic"], pe["bits"]),
           pe["sig_ok"] and pe["bits"] in (32, 64), pe)
    s.fact("X10 NOT APPLICABLE (card 136-4 rule 2): warn-only measurement, Meter stop_mb=None; it must cross 690/700 MB")
    s.fact("input md5 before: {0}".format(K.md5(BED)))
    s.start(); s.discard_work()                                                              # noqa: E702
    M("load", 0)
    rows, n_rows, stop, err, t0 = [], [], None, "", time.time()
    for k in range(1, NMAX + 1):
        if DRY:
            n_rows.append(read_ck()); rows.append(M("read", k)); break                       # noqa: E702
        n, err = s.safe("read_live #{0}".format(k), read_ck)
        rows.append(M("read", k))
        if err:
            stop = "error2" if ERR2.search(err) else "error-other"
            break
        n_rows.append(n)
        if rows[-1]["mb"] is not None and rows[-1]["mb"] >= MBMAX:
            stop = "mb"; break                                                               # noqa: E702
        if time.time() - t0 >= TMAX or s.left_s() < 60:
            stop = "time"; break                                                             # noqa: E702
    stop = stop or "reads"
    mbs = [r["mb"] for r in rows if r["mb"] is not None]
    hs = [r["handles"] for r in rows[1:] if r["handles"] is not None]
    last = rows[-1] if rows else {}
    s.R.update(meter=M.rows, summary=M.summary(), stop=stop, stop_err=err, n_rows=n_rows, loop_s=round(time.time() - t0, 1))
    s.fact("R stop reason {0!r} after {1} read(s) in {2} s; at stop private {3} MB handles {4}; err {5!r}".format(
        stop, len(rows), s.R["loop_s"], last.get("mb"), last.get("handles"), err[:200]))
    s.fact("R first error 2: {0}".format("read {0} at {1} MB".format(last.get("k"), last.get("mb")) if stop == "error2"
                                         else "NOT REACHED; max private {0} MB".format(max(mbs) if mbs else None)))
    s.fact("METER ROWS " + json.dumps([[r["tag"], r["k"], r["mb"], r["handles"]] for r in M.rows]))
    s.fact("METER SUMMARY " + json.dumps(M.summary()))
    s.gate("R1 {0} successful read(s), each > 0 rows, row count constant {1}".format(len(n_rows), sorted(set(n_rows))),
           DRY or (n_rows and min(n_rows) > 0 and len(set(n_rows)) == 1), n_rows[:5])
    s.gate("R2 handles flat across reads 2.. (max - min {0} <= {1})".format((max(hs) - min(hs)) if hs else None, HFLAT),
           DRY or (len(hs) < 2 or max(hs) - min(hs) <= HFLAT), hs)
    s.gate("R3 stop reason {0!r} is a planned one (error2 / mb / reads / time)".format(stop),
           stop in ("error2", "mb", "reads", "time"), err[:200])
    s.gate("X input md5 unchanged", K.md5(BED) == BEDM, K.md5(BED))
    s.dump()


def fresh_read():                                   # card pass 5: a SEPARATE fresh-start read after the kill
    bp = K.mod("bench_prep")
    bp.restart_labview()                            # stop (none running), start, 45 s
    time.sleep(max(0, int(PL["fresh_wait_s"]) - 45))
    pb, hc = K.private_bytes(), bp.labview_handles()
    print("FRESH-START after kill: private {0} MB, handles {1} (~{2} s after start)".format(
        round((pb or 0) / 1048576.0, 1), hc, PL["fresh_wait_s"]), flush=True)


if __name__ == "__main__":
    rc = K.run(body, s)
    if not DRY:
        SX.kill_labview_at_exit()
        fresh_read()
        SX.kill_labview_at_exit()
    sys.exit(rc)
