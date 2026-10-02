r"""diag_chat_m1_mem - card chat-M1 (user 2026-10-03 speed option (나)): where does LabVIEW REALLY run out of memory? MEASUREMENT ONLY.
Today's limits: X10 FAIL > 690 MB predicted, MEMSTOP 700 MB (stagexec.MEM_STOP_MB), one error-2 observation ~770 MB
(com-driving.md:308-312). Card 136-4 reached 653.5 MB in 40 reads with no error (diag_c136_4_mem.log). Here: a dated byte copy
claudeDev\scratch_chat_m1_mem_<ts>.vi of the P3b2b bed (md5 39511877; the bed is never opened) in a FRESH LabVIEW, warn-only meter
(stagexec.Meter stop_mb=None: MEMSTOP DISABLED FOR THIS SCRATCH RUN ONLY), leg 1 = whole-VI checkpoint reads, leg 2 = the edit ops a
build uses (const_row create+wire, delete_object, Remove Bad Wires) with a checkpoint read every N cycles; until the first error /
COM failure, 2000 MB private, or the time caps. Then close the scratch and see whether memory returns. Nothing is saved.
PRIOR ART (reused, nothing new built): skeleton + read + meter = diag_c136_4_mem.py (read_ck == stagexec LVBackend.read =
wiki_build.read_live(work, fs_pairs)); edit verbs = stagekit.Stage.const_row (OpCreateConstOnTerm_v0, stagexec const_on_term route),
Stage.delete_object (build_opfsinnertunnelconnect_v0.del_node), Stage.broken_wire_count(allow_mutation=True) (stagexec LVBackend.rbw);
GDI/USER/handles/private = gscript.lv_counts; responsiveness = lv_gui.ps1 -Action ping (SendMessageTimeout, read-only); kill =
stagexec.kill_labview_at_exit. X10 NOT APPLICABLE: a warn-only measurement whose purpose is to cross 690/700 MB (as card 136-4).
PREDICTION (mechanics; MB curve and error point are the measurement): R1 every leg-1 read returns the same > 0 row count; R2 leg-1
handles flat (max-min <= 100); E1 every edit cycle creates a constant (uid > 0), deletes it, and RBW removes >= 0 wires with no
error until the stop; E2 every leg-2 checkpoint read row count == leg-2 baseline (edits are net zero); S stop reason planned
(error2 / com / error-other / mb / time / count); X bed md5 unchanged; H5 refs opened == closed; scratch deleted; LabVIEW gone.
    py tools/bgrun.py --material --max-min 85 --log tools/bench/diag_chat_m1_mem.log -- py -u tools/bench/diag_chat_m1_mem.py"""
import json, os, re, subprocess, sys, time                                                   # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K, stagexec as SX                                                         # noqa: E401,E402
X10_PROBE = "memory ceiling, scratch only"      # card chat-M2 (fp-35): stage_prerun X10 PROBE-EXEMPT declaration
g = K.g
PL = json.load(open(os.path.join(HERE, "diag_chat_m1_mem_plan.json"), encoding="utf-8"))   # ONE literal: stage_prerun.plan_files
BED, BEDM, FSP = PL["input"]["vi"], PL["input"]["md5"], PL["fs_pairs_from"]
MBMAX, T1, TT = float(PL["max_mb"]), float(PL["reads_leg_min"]) * 60.0, float(PL["total_loop_min"]) * 60.0
NR, NE, EVERY, HFLAT, SETTLE = int(PL["max_reads"]), int(PL["max_edits"]), int(PL["edit_read_every"]), int(PL["handle_flat"]), \
    float(PL["settle_s"])
EX, CCLS = dict(PL["edit_site"]), list(PL["const_classes"])
DRY = bool(getattr(g.report_all, "_dry", False))
ERR2 = re.compile(r"error 2:|memory is full|not enough memory", re.I)
COM = re.compile(r"com_error|RPC|disconnected|0x800706|-2147023174|-2147417848", re.I)
s = K.Stage(BED, BEDM, "scratch_chat_m1_mem", preload=False, deadline_min=float(PL["deadline_min"]), reserve_s=float(PL["reserve_s"]),
            out_json=os.path.join(HERE, "diag_chat_m1_mem.json"), task="card chat-M1")
WB = K.mod("wiki_build")
fsp = json.load(open(os.path.join(ROOT, FSP), encoding="utf-8"))["fs_tunnel_pairs"]
LAST = {}


def probe():
    if DRY:
        return None, None
    c, _e = s.safe("lv_counts", g.lv_counts)
    LAST.clear(); LAST.update(c or {})                                                       # noqa: E702
    return LAST.get("private"), LAST.get("handles")


M = SX.Meter(probe, stop_mb=None, log=lambda m: print(m, flush=True))


def meter(tag, k):
    r = M(tag, k)
    r["gdi"], r["user"] = LAST.get("gdi"), LAST.get("user")
    print("  GDIUSER {0:<6} k {1!s:>3}  gdi {2} user {3}".format(tag, k, r["gdi"], r["user"]), flush=True)
    return r


def ping(tag):
    if DRY:
        return []
    try:
        p = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", os.path.join(ROOT, PL["lv_gui"]),
                            "-Action", "ping"], capture_output=True, text=True, timeout=SETTLE * 4)
        out = [x.strip() for x in (p.stdout or "").splitlines() if x.strip()]
    except Exception as e:                                                                   # noqa: BLE001
        out = ["ping raised {0}".format(str(e)[:120])]
    s.fact("PING {0}: {1}".format(tag, out[:6]))
    return out


def read_ck():                                      # == stagexec LVBackend.read (diag_c136_4_mem.read_ck)
    lv = WB.read_live(s.work, fs_pairs=fsp)
    return len(SX.dedupe(lv["terminals"]))


def txt(x):
    """an error column as text; a dry stub value (not a str) counts as no error"""
    if isinstance(x, str):
        return x
    return "" if (DRY or not x) else str(x)


def classify(err):
    err = txt(err)
    return "error2" if ERR2.search(err) else ("com" if COM.search(err) else "error-other")


def edit_cycle(k):
    """create const + wire on EX, delete it, Remove Bad Wires. Returns (err text or '', detail dict)."""
    rec = s.const_row(EX, tag="m1 e{0}".format(k))
    res = rec.get("result") or {}
    err = txt(rec.get("err")) or txt(res.get("err")) or txt(res.get("inv_err"))
    uid = res.get("created_uid")
    if err or not uid:
        return err or "const_row returned no created uid", {"create": res}
    gone = False
    for c in CCLS:
        d = s.delete_object(c, uid if DRY else int(uid), tag="m1 e{0}".format(k))
        if txt(d.get("err")):
            return txt(d.get("err")), {"uid": uid, "delete_cls": c}
        if d.get("result"):
            gone = c
            break
    if not gone:
        return "created constant #{0} not found under {1}".format(uid, CCLS), {"uid": uid}
    r, e = s.safe("rbw e{0}".format(k), lambda: s.broken_wire_count(allow_mutation=True, tag="m1 e{0}".format(k)))
    return txt(e), {"uid": uid, "cls": gone, "rbw": (r or {}).get("bad")}


def body(_):
    print(__doc__, flush=True)
    s.fact("X10 NOT APPLICABLE (card chat-M1): warn-only measurement, Meter stop_mb=None = MEMSTOP DISABLED for this scratch run only")
    s.fact("input md5 before: {0}".format(K.md5(BED)))
    s.start(); s.discard_work()                                                              # noqa: E702
    t0 = time.time()
    meter("load", 0)
    ping("at load")
    # ---------------- leg 1: whole-VI checkpoint reads
    n_rows, stop, err, k = [], None, "", 0
    for k in range(1, NR + 1):
        if DRY:
            n_rows.append(read_ck()); meter("read", k); break                                # noqa: E702
        n, err = s.safe("read_live #{0}".format(k), read_ck)
        r = meter("read", k)
        if err:
            stop = classify(err); break                                                      # noqa: E702
        n_rows.append(n)
        if r["mb"] is not None and r["mb"] >= MBMAX:
            stop = "mb"; break                                                               # noqa: E702
        if time.time() - t0 >= T1 or s.left_s() < 60:
            stop = "time"; break                                                             # noqa: E702
    stop = stop or "count"
    leg1 = {"stop": stop, "err": err[:300], "reads": k, "rows": sorted(set(n_rows)), "s": round(time.time() - t0, 1)}
    s.R["leg1"] = leg1
    s.fact("LEG1 reads: stop {0!r} after {1} read(s) in {2} s; err {3!r}".format(stop, k, leg1["s"], err[:200]))
    ping("after leg 1")
    # ---------------- leg 2: build edit ops (only when leg 1 ended on a cap, not on an error)
    leg2 = {"stop": "skipped (leg 1 ended on an error)", "cycles": 0, "base": None, "rows": [], "dets": []}
    if stop in ("time", "count", "mb") or DRY:
        b, e0 = s.safe("rbw baseline", lambda: s.broken_wire_count(allow_mutation=True, tag="m1 baseline"))
        nb, eb = s.safe("read_live leg2 base", read_ck)
        meter("read", "B")
        leg2.update(base=nb, base_rbw=(b or {}).get("bad"), stop=None, err=(e0 or eb)[:300])
        if e0 or eb:
            leg2["stop"] = classify(e0 or eb)
        t2 = time.time()
        for j in range(1, NE + 1):
            if leg2["stop"]:
                break
            e, det = edit_cycle(j)
            r = meter("op", j)
            leg2["cycles"] = j
            leg2["dets"].append(det)
            if e:
                leg2["stop"], leg2["err"] = classify(e), "cycle {0}: {1}".format(j, e[:300])
                break
            if j % EVERY == 0 or DRY:
                n, e = s.safe("read_live leg2 #{0}".format(j), read_ck)
                r = meter("read", j)
                if e:
                    leg2["stop"], leg2["err"] = classify(e), "read after cycle {0}: {1}".format(j, e[:300])
                    break
                leg2["rows"].append(n)
            if DRY:
                leg2["stop"] = "count"; break                                                # noqa: E702
            if r["mb"] is not None and r["mb"] >= MBMAX:
                leg2["stop"] = "mb"; break                                                   # noqa: E702
            if time.time() - t0 >= TT or s.left_s() < 60:
                leg2["stop"] = "time"; break                                                 # noqa: E702
        leg2["stop"] = leg2["stop"] or "count"
        leg2["s"] = round(time.time() - t2, 1)
    s.R["leg2"] = dict(leg2, dets=leg2["dets"][:3] + leg2["dets"][-3:])
    s.fact("LEG2 edits: stop {0!r} after {1} cycle(s) in {2} s; base rows {3}, base RBW {4}; err {5!r}".format(
        leg2["stop"], leg2["cycles"], leg2.get("s"), leg2["base"], leg2.get("base_rbw"), str(leg2.get("err"))[:200]))
    s.fact("LEG2 rbw per cycle (first/last 3): {0}".format([d.get("rbw") for d in s.R["leg2"]["dets"]]))
    ping("after leg 2")
    # ---------------- close the scratch, does memory return?
    pre = meter("pre", "C")
    s.safe("close_panel(scratch)", lambda: g.close_panel(s.work))
    if not DRY:
        g._loaded.discard(s.work)               # the panel close unloaded it: the next ensure_loaded must reopen
        time.sleep(SETTLE)
    post = meter("close", "C")
    ping("after close")
    s.fact("CLOSE scratch: private {0} -> {1} MB, handles {2} -> {3}, gdi {4} -> {5}, user {6} -> {7}".format(
        pre["mb"], post["mb"], pre["handles"], post["handles"], pre["gdi"], post["gdi"], pre["user"], post["user"]))
    rows = M.rows
    mbs = [r["mb"] for r in rows if r["mb"] is not None]
    s.R.update(meter=rows, summary=M.summary())
    s.fact("PEAK private {0} MB; first {1} MB".format(max(mbs) if mbs else None, mbs[0] if mbs else None))
    s.fact("METER ROWS " + json.dumps([[r["tag"], r["k"], r["mb"], r["handles"], r["gdi"], r["user"]] for r in rows]))
    s.fact("METER SUMMARY " + json.dumps(M.summary()))
    h1 = [r["handles"] for r in rows if r["tag"] == "read" and isinstance(r["k"], int) and r["k"] >= 2
          and r["handles"] is not None and r["t"] <= t0 + leg1["s"]]
    s.gate("R1 leg-1 {0} read(s), each > 0 rows, row count constant {1}".format(len(n_rows), leg1["rows"]),
           DRY or (n_rows and min(n_rows) > 0 and len(set(n_rows)) == 1), n_rows[:5])
    s.gate("R2 leg-1 handles flat across reads 2.. (max - min {0} <= {1})".format((max(h1) - min(h1)) if h1 else None, HFLAT),
           DRY or len(h1) < 2 or max(h1) - min(h1) <= HFLAT, h1[:5])
    d0 = leg2["dets"][0] if leg2["dets"] else {}
    s.gate("E1 the first edit cycle created constant #{0}, deleted it as {1}, RBW removed {2}".format(
        d0.get("uid"), d0.get("cls"), d0.get("rbw")),
        DRY or str(leg2["stop"]).startswith("skipped") or bool(d0.get("cls")), d0)
    s.gate("E2 leg-2 checkpoint row counts == baseline {0}: {1}".format(leg2["base"], sorted(set(leg2["rows"]))),
           DRY or not leg2["rows"] or set(leg2["rows"]) == {leg2["base"]}, leg2["rows"][:5])
    s.gate("S stop reasons planned: leg1 {0!r}, leg2 {1!r}".format(stop, leg2["stop"]),
           stop in ("error2", "com", "error-other", "mb", "time", "count") and (leg2["stop"] in (
               "error2", "com", "error-other", "mb", "time", "count") or str(leg2["stop"]).startswith("skipped")),
           str(leg2.get("err"))[:200])
    s.gate("X input md5 unchanged", K.md5(BED) == BEDM, K.md5(BED))
    s.dump()


if __name__ == "__main__":
    rc = K.run(body, s)
    if not DRY:
        SX.kill_labview_at_exit()
    sys.exit(rc)
