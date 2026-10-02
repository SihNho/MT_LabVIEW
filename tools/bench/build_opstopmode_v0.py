r"""build_opstopmode_v0.py - card 138-5 (re-issue of 137-2; PD298(e), PD301(d), PD309(d)): two READ-ONLY op VIs.
  OpStopMode_v0.vi   OpLoopEndRef_v0 pattern (tools/recipes/build_oploopendref_v0.py:250-266): donor OpWhileCast_v0 (its
                     WhileLoop-typed TMSC kept), ADDITIVE PN WhileLoop['Stop If True?' 6362C01] branched off the TMSC.
  OpStopModeB_v0.vi  the c97 typed-seed route (tools/bench/diag_c97_tools_opbuild.py:104-131) on an OpSetIndexMode_v0 copy:
                     TMSC retargeted by a Boolean-typed seed -> Boolean['Mechanical Action' 6333808] + UID echo; Traverse for
                     GObjects' required 'Traverse Target' ring re-fed from a CONTROL (0 = FP, 1 = BD, gscript.py:1880) so
                     the op can reach front-panel Booleans.
FOUND FIRST: no generic property reader (docs/cycle27-plan.md:1703); OpLoopEndRef_v0 reads the cond terminal, not its mode;
OpVisibleSet_v0/OpLabelSet_v0 WRITE; no Boolean-typed reader. Ids: 6362C01 labviewwiki (archive/peer/2026-10-02-c136-2-
condterm-mode-claude.md:44), 6333808 labviewwiki (archive/peer/2026-10-02-c138-5-mechaction.md), both CENSUSED here.
PREDICTION (GATE lines): A/B D donor ES 1, census = exactly one data terminal, assembled ES 1, saved, COLD ES 1.
Scratch (EMPTY_v0 copy, While loop + one Boolean control, never a deliverable): a fresh While loop reads Stop If True? = True;
scratch-only writer copies (never saved) write False -> read False, True -> read True; Mechanical Action written 0..5 ->
each read back equal; a past-the-end index -> error + echo 0. Bed BYTE COPY: #10170 echo 10170 + value; 'stop (end)' echo +
numeric. Hygiene per PD242(b) via gscript.hygiene_run (2,000 calls each, 0 errors, h_closed +-100). LabVIEW gone; bed md5
unchanged; scratch files deleted.
    py tools/bgrun.py --material --max-min 40 --log tools/bench/build_opstopmode_v0.log -- py -u tools/bench/build_opstopmode_v0.py
"""
import hashlib, json, os, shutil, subprocess, sys, time, traceback                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))  # noqa: E702
for _p in (os.path.join(ROOT, "tools"), HERE, os.path.join(ROOT, "tools", "recipes")):
    sys.path.insert(0, _p)
import protocol as P                                                                      # noqa: E402
import gscript as g                                                                       # noqa: E402
import bench_prep                                                                         # noqa: E402
CD = g.CLAUDEDEV
BED = os.path.join(CD, "D1_ring_p3b2b_20261002_130007.vi"); BED_MD5 = "395118775a52bc90073f4449b99f899d"   # noqa: E702
TS = time.strftime("%H%M%S")
TGT = os.path.join(CD, "scratch_c138_5_tgt_%s.vi" % TS); BEDC = os.path.join(CD, "scratch_c138_5_bed_%s.vi" % TS)  # noqa: E702
OPA, OPB = os.path.join(CD, "OpStopMode_v0.vi"), os.path.join(CD, "OpStopModeB_v0.vi")
LAB_P, FACTS_P = os.path.join(HERE, "diag_c138_5_oplabels.json"), os.path.join(HERE, "diag_c138_5_facts.json")
STD = ("reference", "reference out", "error in (no error)", "error out")
P_SIT, P_MECH = "6362C01", "6333808"
g._run.__defaults__ = (6.0, 120.0)
G, LAB, F, SCR = {}, {}, {}, []


class Stop(Exception):
    pass


def md5(p): return hashlib.md5(open(p, "rb").read()).hexdigest()


def gate(k, ok, d="", need=True):
    G[k] = bool(ok); print("  GATE %s  %s  %s" % ("PASS" if ok else "FAIL", k, str(d)[:400]), flush=True)  # noqa: E702
    if need and not ok:
        raise Stop(k)
    return bool(ok)


def fact(k, v): F[k] = v; print("  FACT  %s: %s" % (k, str(v)[:600]), flush=True)          # noqa: E702


class B(object):                                     # diag_c97_tools_opbuild.py:39-101, verbatim in substance
    def __init__(s, donor, out):
        s.op = os.path.join(CD, out)
        if os.path.exists(s.op):
            os.remove(s.op)
        shutil.copyfile(os.path.join(CD, donor), s.op); time.sleep(0.3)                  # noqa: E702
        g.open_panel(s.op); time.sleep(1.0); s.inv0 = g.uids(s.op, "Invoke")             # noqa: E702

    def purge(s):
        junk = [u for u in g.uids(s.op, "Invoke") if u not in s.inv0]
        if junk:
            order = [o["uid"] for o in g.report_all(s.op, "Invoke")]
            for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(s.op, "Invoke", i, verify=False)
            g.remove_bad_wires_scripted(s.op)

    def idx(s, cls, uid): return [o["uid"] for o in g.report_all(s.op, cls)].index(uid)

    def terms(s, uid):
        for c in range(80):
            nu, rows = g.node_terms_uid(s.op, 0, c)
            if not nu:
                return None, []
            if nu == uid:
                return c, rows
        return None, []

    def pn(s, cls, props, pos):
        r = g.build_property(s.op, cls, props, pos); s.purge(); return int(r[-1]["uid"])  # noqa: E702

    def w(s, su, st, du, dt, sc="Property", dc="Property", branch=False):
        g.wire(s.op, sc, s.idx(sc, su), st, dc, s.idx(dc, du), dt, branch=branch); s.purge()  # noqa: E702

    def panel(s, ind): return set(r["label"] for r in g.panel_wiring(s.op) if r["indicator"] == ind)

    def ind(s, uid, term):
        n, rows = s.terms(uid); t = next(r["i"] for r in rows if r["name"] == term and r["is_source"])  # noqa: E702
        b = s.panel(True); g.create_indicator(s.op, n, t); s.purge(); new = sorted(s.panel(True) - b)  # noqa: E702
        assert len(new) == 1, (term, new)
        return new[0]

    def ctl(s, uid, term):
        n, rows = s.terms(uid); t = next(r["i"] for r in rows if r["name"] == term and not r["is_source"])  # noqa: E702
        b = s.panel(False); g.create_control(s.op, n, t); s.purge(); new = sorted(s.panel(False) - b)  # noqa: E702
        assert len(new) == 1, (term, new)
        return new[0]

    def data(s, uid, src):
        return [r["name"] for r in s.terms(uid)[1] if bool(r["is_source"]) == src and r["name"] not in STD]

    def node_with(s, *names):
        nodes, _n = g.net_map(s.op, 0, max_nodes=60, max_terms=24)
        return next(((u, t) for _k, (u, _l, t) in nodes.items() if all(any(x == n for _i, x, _w in t) for n in names)), None)


def finish(b, key, lab, save=True):
    g.set_auto_error_handling(b.op, False); b.purge(); es = g.exec_state(b.op)           # noqa: E702
    gate("%s A assembled ExecState 1" % key, es == 1, es)
    lab["controls"] = [r["label"] for r in g.panel_wiring(b.op) if not r["indicator"]]
    LAB[key] = lab; fact("%s labels" % key, lab)                                          # noqa: E702
    if save:
        g.save(b.op); gate("%s V saved by script" % key, os.path.getsize(b.op) > 0, (os.path.getsize(b.op), md5(b.op)))  # noqa: E702


def build_a():                                       # OpLoopEndRef_v0 pattern: additive PN on the WhileLoop TMSC
    b = B("OpWhileCast_v0.vi", "OpStopMode_v0.vi"); key = "OpStopMode_v0"                   # noqa: E702
    gate("%s D donor copy ES 1" % key, g.exec_state(b.op) == 1)
    tm = b.node_with("target class", "specific class reference")[0]
    p = b.pn("VI Server:WhileLoop", [(P_SIT, False)], (900, 1150)); d = b.data(p, True)  # noqa: E702
    gate("%s L3 WhileLoop[%s] censused to ONE data terminal" % (key, P_SIT), len(d) == 1, d)
    b.w(tm, "specific class reference", p, "reference", sc="Function", branch=True)
    gate("%s L4 WhileLoop PN accepts the TMSC output, ES 1" % key, g.exec_state(b.op) == 1)
    lab = {"data": d[0], "pn": p, "tmsc": tm, "UID": "UID"}
    lab["StopIfTrue"] = b.ind(p, d[0]); lab["Err"] = b.ind(p, "error out")                # noqa: E702
    finish(b, key, lab)


def build_b():                                       # c97 typed-seed retarget, Boolean seed
    b = B("OpSetIndexMode_v0.vi", "OpStopModeB_v0.vi"); key = "OpStopModeB_v0"              # noqa: E702
    gate("%s D donor copy ES 1" % key, g.exec_state(b.op) == 1)
    props0 = {p["uid"] for p in g.report_all(b.op, "Property")}
    pn_w = b.node_with("IndexMode"); pn_w = pn_w[0] if pn_w and pn_w[0] in props0 else None  # noqa: E702
    g.delete_object(b.op, "Property", b.idx("Property", pn_w)); g.remove_bad_wires_scripted(b.op); b.purge()  # noqa: E702
    gate("%s X donor IndexMode PN #%s deleted, ES 1" % (key, pn_w), g.exec_state(b.op) == 1)
    tm = b.node_with("target class", "specific class reference")
    W = next(w for _i, x, w in tm[1] if x == "target class"); tm = tm[0]                 # noqa: E702
    p = b.pn("VI Server:Boolean", [(P_MECH, False)], (900, 450)); d = b.data(p, True)    # noqa: E702
    gate("%s L3 Boolean[%s] censused to ONE data terminal" % (key, P_MECH), len(d) == 1, d)
    n, rows = b.terms(p); t_ref = next(r for r in rows if r["name"] == "reference" and not r["is_source"])  # noqa: E702
    _o, seed = g.create_control(b.op, n, t_ref["i"]); b.purge()                           # noqa: E702
    w_seed = next(r["wire"] for r in b.terms(p)[1] if r["i"] == t_ref["i"])
    for wu in (w_seed, W):
        g.delete_object(b.op, "Wire", [o["uid"] for o in g.report_all(b.op, "Wire")].index(wu))
    g.wire_control(b.op, [seed], "Function", b.idx("Function", tm), ["target class"]); b.purge()  # noqa: E702
    b.w(tm, "specific class reference", p, "reference", sc="Function")
    gate("%s S Boolean seed %r -> TMSC #%s -> PN #%s: ES 1" % (key, seed, tm, p), g.exec_state(b.op) == 1)
    ue = b.pn("VI Server:GObject", [("632A813", False)], (900, 700))
    b.w(tm, "specific class reference", ue, "reference", sc="Function", branch=True)
    tv, trows = b.node_with("Traverse Target", "Class Name")
    wt = next(w for _i, x, w in trows if x == "Traverse Target")
    if wt:
        g.delete_object(b.op, "Wire", [o["uid"] for o in g.report_all(b.op, "Wire")].index(wt)); b.purge()  # noqa: E702
    lab = {"data": d[0], "pn": p, "tmsc": tm, "seed": seed, "TraverseTarget": b.ctl(tv, "Traverse Target")}
    lab["MechAction"] = b.ind(p, d[0]); lab["Err"] = b.ind(p, "error out")                # noqa: E702
    lab["UID"] = b.ind(ue, "UID"); lab["UIDErr"] = b.ind(ue, "error out")                 # noqa: E702
    finish(b, key, lab)


def build_writer(src_key, out, cls, pid, after):    # scratch-only: never saved, deleted at exit
    la = LAB[src_key]; b = B(os.path.basename(OPA if src_key == "OpStopMode_v0" else OPB), out); SCR.append(b.op)  # noqa: E702
    pw = b.pn(cls, [(pid, True)], (1300, 1500))
    if after == "tmsc":
        b.w(la["tmsc"], "specific class reference", pw, "reference", sc="Function", branch=True)
    else:
        b.w(la["pn"], "reference out", pw, "reference")
        b.w(la["pn"], "error out", pw, "error in (no error)", branch=True)   # error out already feeds the reader's Err indicator
    lab = {"Value": b.ctl(pw, b.data(pw, False)[0]), "WErr": b.ind(pw, "error out")}
    finish(b, out[:-3], lab, save=False)
    return b.op, lab


def call(path, la, target, idx, extra=None, tt=0):
    vi = g.op(path); ctl = set(la.get("controls") or [])                                  # noqa: E702
    vi.SetControlValue("vi path", target)
    if "vi path 2" in ctl:
        vi.SetControlValue("vi path 2", target)
    vi.SetControlValue("Class Name", "Boolean" if "MechAction" in la else "WhileLoop")
    vi.SetControlValue("index", int(idx))
    if "index 2" in ctl:
        vi.SetControlValue("index 2", 0)
    if "TraverseTarget" in la:
        vi.SetControlValue(la["TraverseTarget"], int(tt))
    for k, v in (extra or {}).items():
        vi.SetControlValue(k, v)
    if "UID" in la:
        vi.SetControlValue(la["UID"], 0)
    g._run(vi)
    errs = " | ".join(e for e in (g._err(vi, la[k]) or "" for k in ("Err", "UIDErr", "WErr") if k in la) if e)
    out = {"err": errs}
    if "UID" in la:
        out["uid"] = int(vi.GetControlValue(la["UID"]))
    if "StopIfTrue" in la:
        out["v"] = bool(vi.GetControlValue(la["StopIfTrue"]))
    if "MechAction" in la:
        out["v"] = int(vi.GetControlValue(la["MechAction"]))
    return out


def rd(key, target, idx, tt=0):
    path = OPA if key == "OpStopMode_v0" else OPB
    with g.hygiene_probe(path):
        return call(path, LAB[key], target, idx, tt=tt)


def wr(wpath, wkey, rkey, target, idx, value):
    """A scratch writer = a copy of the reader + one write PN: its labels are the reader's plus Value/WErr."""
    with g.hygiene_probe(wpath):
        return call(wpath, dict(LAB[rkey], **LAB[wkey]), target, idx, {LAB[wkey]["Value"]: value})


def scratch_target():
    shutil.copyfile(os.path.join(CD, "EMPTY_v0.vi"), TGT); SCR.append(TGT); g.open_panel(TGT)  # noqa: E702
    g.while_loop(TGT, (300, 200)); r = g.create_const_loop_term(TGT, "while_cond", 0, value=False)  # noqa: E702
    fact("tgt cond constant", r)
    cu = int(g.build_property(TGT, "VI Server:Control", [("6332000", True)], (700, 80))[-1]["uid"])
    for c in range(40):
        nu, rows = g.node_terms_uid(TGT, 0, c)
        if nu == cu:
            g.create_control(TGT, c, next(r["i"] for r in rows if not r["is_source"] and r["name"] not in STD)); break  # noqa: E702
    g.delete_object(TGT, "Property", [o["uid"] for o in g.report_all(TGT, "Property")].index(cu))
    g.remove_bad_wires_scripted(TGT)
    gate("T tgt (While + Boolean control, carrier deleted) ES 1", g.exec_state(TGT) == 1)
    g.save(TGT)
    ctls = [r for r in g.panel_wiring(TGT) if not r["indicator"]]
    loops = g.report_all(TGT, "WhileLoop")
    gate("T tgt has exactly 1 control and 1 While loop", len(ctls) == 1 and len(loops) == 1, (ctls, loops))
    return int(loops[0]["uid"]), int(ctls[0]["uid"])


def main():
    bench_prep.restart_labview(); g.reset(); time.sleep(3); h0 = bench_prep.labview_handles()  # noqa: E702
    fact("handles after restart", h0)
    gate("0 bed md5 before", md5(BED) == BED_MD5, md5(BED))
    build_a(); build_b()
    json.dump(LAB, open(LAB_P, "w"), indent=1)
    g.reset(); bench_prep.restart_labview(); g.reset(); time.sleep(3)                     # noqa: E702
    for p in (OPA, OPB):
        gate("C %s COLD ExecState 1 (fresh LabVIEW)" % os.path.basename(p), g.exec_state(p) == 1, md5(p))
    lu, bu = scratch_target()
    wa, _la = build_writer("OpStopMode_v0", "scratch_c138_5_wA.vi", "VI Server:WhileLoop", P_SIT, "tmsc")
    wb, _lb = build_writer("OpStopModeB_v0", "scratch_c138_5_wB.vi", "VI Server:Boolean", P_MECH, "pn")
    r0 = rd("OpStopMode_v0", TGT, 0)
    gate("S1 fresh While loop reads Stop If True? = True, echo = loop uid", r0.get("v") is True and r0["uid"] == lu and not r0["err"], (r0, lu))
    for v in (False, True):
        w = wr(wa, "scratch_c138_5_wA", "OpStopMode_v0", TGT, 0, v); r = rd("OpStopMode_v0", TGT, 0)  # noqa: E702
        gate("S2 write Stop If True?=%s (scratch writer) -> read back %s" % (v, v), r.get("v") is v and not w["err"] and not r["err"], (w, r))
    m0 = rd("OpStopModeB_v0", TGT, 0); fact("S3 fresh Boolean (Create Control on a Boolean sink) Mechanical Action", m0)  # noqa: E702
    gate("S3 Boolean echo = control uid, no error", m0.get("uid") == bu and not m0["err"], (m0, bu))
    bd = rd("OpStopModeB_v0", TGT, 0, tt=1); fact("S3b same call with Traverse Target = 1 (BD)", bd)
    for v in range(6):
        w = wr(wb, "scratch_c138_5_wB", "OpStopModeB_v0", TGT, 0, v); r = rd("OpStopModeB_v0", TGT, 0)  # noqa: E702
        gate("S4 write Mechanical Action=%d -> read back %d" % (v, v), r.get("v") == v and not w["err"] and not r["err"], (w, r))
    na, nb = rd("OpStopMode_v0", TGT, 5), rd("OpStopModeB_v0", TGT, 5)
    gate("S5 past-the-end index -> error and echo 0 (both ops)", na["err"] and na["uid"] == 0 and nb["err"] and nb["uid"] == 0, (na, nb))
    # ---- bed byte copy -----------------------------------------------------------------------------------------------
    shutil.copyfile(BED, BEDC); SCR.append(BEDC)                                          # noqa: E702
    gate("B0 bed byte copy md5 == bed", md5(BEDC) == BED_MD5)
    loops = [int(o["uid"]) for o in g.report_all(BEDC, "WhileLoop")]
    gate("B1 #10170 is a WhileLoop of the bed copy", 10170 in loops, loops)
    rows = [dict(rd("OpStopMode_v0", BEDC, i), index=i) for i in range(len(loops))]
    fact("B2 Stop If True? of every bed While loop", [(r["uid"], r.get("v"), r["err"][:40]) for r in rows])
    hit = next(r for r in rows if r["uid"] == 10170)
    gate("B2 #10170 Stop If True? read (echo 10170, no error)", not hit["err"], hit); fact("B2 #10170", hit)  # noqa: E702
    pw = {int(r["uid"]): r["label"] for r in g.panel_wiring(BEDC)}
    se = [u for u, lb in pw.items() if lb == "stop (end)"]
    gate("B3 exactly one top-level panel object labelled 'stop (end)'", len(se) == 1, se)
    bools = []
    for i in range(300):
        r = rd("OpStopModeB_v0", BEDC, i)
        if r["uid"] == 0:
            fact("B4 scan ended at index %d" % i, r); break                               # noqa: E702
        bools.append(dict(r, index=i, label=pw.get(r["uid"], "<nested>")))
    fact("B4 Mechanical Action of every front-panel Boolean (uid, label, value)", [(b["uid"], b["label"], b["v"]) for b in bools])
    sb = [b for b in bools if b["uid"] == se[0]]
    gate("B4 'stop (end)' #%s Mechanical Action read (no error)" % se[0], len(sb) == 1 and not sb[0]["err"], sb)
    fact("B4 stop (end)", sb[0])
    # ---- hygiene, PD242(b) ---------------------------------------------------------------------------------------------
    for key, path in (("OpStopMode_v0", OPA), ("OpStopModeB_v0", OPB)):
        rec = g.hygiene_run(path, lambda c, k=key, p=path: call(p, LAB[k], c, 0)["err"], TGT, total=2000, per_round=100,
                            card="138-5", log="tools/bench/build_opstopmode_v0.log",
                            workload_text="%s on index 0 of a byte copy of the scratch target" % key,
                            record_path=os.path.join(HERE, "hygiene_%s.json" % key))
        gate("H %s hygiene PASS (calls %s, errors %s, max_dev %s, refs %s)" % (key, rec["calls"], rec["errors"], rec["max_dev_closed"],
             rec["refs_live_delta"]), rec["status"] == "PASS", rec["error_samples"][:3], need=False)
    fact("handles at end", (bench_prep.labview_handles(), h0))


if __name__ == "__main__":
    try:
        main()
    except Stop as e:
        print("STOP at the first unexpected result: %s" % e, flush=True)
    except Exception as e:                                                                # noqa: BLE001
        traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:300], need=False)  # noqa: E702
    finally:
        json.dump(LAB, open(LAB_P, "w"), indent=1, default=str); json.dump(F, open(FACTS_P, "w"), indent=1, default=str)  # noqa: E702
        g.reset()
        subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(5)  # noqa: E702
        gate("E LabVIEW gone", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower(), need=False)
        for p in SCR:
            for _ in range(5):
                try:
                    os.path.exists(p) and os.remove(p); break                             # noqa: E702
                except OSError:
                    time.sleep(2)
        gate("E scratch files deleted", not any(os.path.exists(p) for p in SCR), SCR, need=False)
        gate("E bed md5 unchanged", md5(BED) == BED_MD5, need=False)
        bad = [k for k, v in G.items() if not v]
        arts = [{"path": p, "md5": md5(p)} for p in (OPA, OPB) if os.path.exists(p)]
        print("=== GATES: %d pass / %d fail; failing: %s" % (len(G) - len(bad), len(bad), bad), flush=True)
        print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, arts)), flush=True)
        sys.exit(1 if bad else 0)
