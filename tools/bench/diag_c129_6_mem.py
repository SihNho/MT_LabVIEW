r"""diag_c129_6_mem - card 129-6 (brief_129-6.md): WHERE does LabVIEW's private memory grow ~4 MB per stage op?
MEASUREMENT ONLY. A dated byte copy claudeDev\scratch_c129_mem_<ts>.vi of the P3a bed (md5 4dfa44aa; the bed is never opened
for edit) in a FRESH LabVIEW; private MB + handles at: M0 (after open) - W1 15 x the Executor's per-op checkpoint read, no edit
between - W2 15 x one cheap scripted edit on diagram 27219, no checkpoint read between - W3 close WITHOUT saving, reopen.
PRIOR ART (checked, reused, nothing new built): the W1 read is EXACTLY stagexec.Executor.run's checkpoint read (stagexec.py:2021
`real_new = be.read()` -> LVBackend.read :2391-2395 = wiki_build.read_live(work, fs_pairs=BASE fs_tunnel_pairs) (wiki_build.py:233:
report_all GObject + allterms.read_terms OP_ALLTERMS_V1 + join_wires) then dedupe); the W2 edit is the plan's constant route
(stagexec.py:2650-2656 `primitive` -> gscript.create_primitive_nested, prim 'const_donor', donor DonorRingConst_v0.vi #249,
plan_ring_p3b1_in.json); the meter is stagexec.Meter (:72) on stagekit.private_bytes + bench_prep.labview_handles (as LVBackend :2373);
skeleton diag_c122_hyg.py. No tool, plan or recipe edited; no LabVIEW option or ini touched.
PREDICTION (mechanics only - the slopes are the measurement, not predicted): S0 W1 15 reads, each returns > 0 terminal rows, row
count constant; S1 W2 15 creates, 0 errors, Constant count +15 exactly; S2 after W3 reopen the copy's md5 == input (never saved)
and Constant count == M0's; a window stops early (ROW, not a gate) if private MB >= 680 (error 2 seen at 695). LabVIEW gone, copy deleted.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c129_6_mem.log -- py -u tools/bench/diag_c129_6_mem.py"""
import json, os, sys, time                                                           # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K, stagexec as SX                                                 # noqa: E401,E402
g = K.g
PL = json.load(open(os.path.join(HERE, "diag_c129_6_mem_plan.json"), encoding="utf-8"))   # ONE literal: stage_prerun.plan_files
BASE = json.load(open(os.path.join(ROOT, PL["input"]["graph"]), encoding="utf-8"))
BED, N, DG, POS, CEIL = os.path.join(g.CLAUDEDEV, PL["input"]["vi"]), PL["reps"], PL["diagram"], PL["pos"], PL["soft_ceiling_mb"]
DONOR = {"donor": PL["donor"]["donor"], "uid": int(PL["donor"]["uid"])}
DRY = bool(getattr(g.report_all, "_dry", False))
s = K.Stage(BED, PL["input"]["md5"], "scratch_c129_mem", preload=False, deadline_min=28,
            out_json=os.path.join(HERE, "diag_c129_6_mem.json"), task="card 129-6")
WB = K.mod("wiki_build")


def probe():
    if DRY:
        return None, None
    pb, _e = s.safe("private_bytes", K.private_bytes)
    hc, _e = s.safe("labview_handles", K.mod("bench_prep").labview_handles)
    return (pb if isinstance(pb, int) else None), (hc if isinstance(hc, int) else None)


M = SX.Meter(probe, stop_mb=None, log=lambda m: print(m, flush=True))


def slope(rows):
    p = [(i, r["mb"]) for i, r in enumerate(rows, 1) if r["mb"] is not None]
    if len(p) < 2:
        return None
    mx, my = sum(x for x, _ in p) / float(len(p)), sum(y for _, y in p) / float(len(p))
    return round(sum((x - mx) * (y - my) for x, y in p) / sum((x - mx) ** 2 for x, _ in p), 3)


def window(tag, fn):
    rows, out, t0 = [], [], time.time()
    for k in range(1, N + 1):
        out.append(fn(k))
        rows.append(M(tag, k))
        if rows[-1]["mb"] is not None and rows[-1]["mb"] >= CEIL:
            s.row("{0} stopped early at rep {1}: private {2} MB >= soft ceiling {3}".format(tag, k, rows[-1]["mb"], CEIL), k, N)
            break
    sec = round(time.time() - t0, 1)
    s.fact("{0} {1} reps in {2} s; slope {3} MB/rep (all), {4} MB/rep (reps 2..); MB {5}".format(
        tag, len(rows), sec, slope(rows), slope(rows[1:]), [r["mb"] for r in rows]))
    s.R[tag] = {"rows": rows, "slope_all": slope(rows), "slope_2on": slope(rows[1:]), "secs": sec}
    return rows, out


def read_ck(_k):                                    # == LVBackend.read (stagexec.py:2391-2395), byte for byte in effect
    lv = WB.read_live(s.work, fs_pairs=BASE["fs_tunnel_pairs"])
    return len(SX.dedupe(lv["terminals"]))


def edit(k):                                        # == stagexec.py:2655's call, without _op/node_mark/junk_purge (reads)
    r, e = s.safe("create_primitive_nested #{0}".format(k), lambda: g.create_primitive_nested(
        s.work, DG, "const_donor", (POS[0] + 30 * k, POS[1] + 20 * k), donor=DONOR))
    return {"uid": r, "err": e}


def body(_):
    print(__doc__, flush=True)
    s.start(); s.discard_work()                                                       # noqa: E702
    M("M0", 0)
    c0 = s.count("Constant")
    s.fact("M0 Constant count {0}".format(c0))
    M("M0cnt", 0)
    w1, n1 = window("W1", read_ck)
    s.gate("S0 W1 {0} checkpoint reads, every read > 0 rows, row count constant {1}".format(len(w1), sorted(set(n1))),
           DRY or (n1 and min(n1) > 0 and len(set(n1)) == 1), n1)
    w2, e2 = window("W2", edit)
    c2 = s.count("Constant")
    errs = [x for x in e2 if x["err"]]
    s.gate("S1 W2 {0} creates, 0 errors, Constant {1} -> {2} (+{0} expected)".format(len(w2), c0, c2),
           DRY or (not errs and c2 - c0 == len(w2)), errs[:3])
    M("W2cnt", 0)
    s.safe("close_panel(work) WITHOUT saving", lambda: g.close_panel(s.work))
    M("W3close", 0)
    time.sleep(5.0)
    M("W3close5", 0)
    ld = getattr(g, "_loaded", None)
    isinstance(ld, set) and ld.discard(s.work)                                        # noqa: W0106 - so ensure_loaded reopens
    s.safe("ensure_loaded(work) REOPEN", lambda: g.ensure_loaded(s.work))
    M("W3open", 0)
    c3, m3 = s.count("Constant"), (None if DRY else K.md5(s.work))                  # dry: no copy on disk
    s.gate("S2 W3 reopened copy: md5 == input (never saved) and Constant {0} == M0's {1}".format(c3, c0),
           DRY or (m3 == PL["input"]["md5"] and c3 == c0), m3)
    M("W3cnt", 0)
    s.R["meter"] = M.rows
    s.fact("METER ROWS " + json.dumps([[r["tag"], r["k"], r["mb"], r["handles"]] for r in M.rows]))
    s.dump()


if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or SX.kill_labview_at_exit()
    sys.exit(rc)
