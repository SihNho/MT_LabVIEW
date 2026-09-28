r"""diag_c116d_opbuild.py - card 116-4 J1 (part 1): build claudeDev\OpWireJoints_v0.vi, a READ-ONLY `Wire.Joints[]` (6371005) reader.
FOUND FIRST (card rule "check what exists"): no Joints reader exists (grep 6371005 over tools/ docs/: only peer text,
archive/peer/2026-09-23-c90-orphan-wires.md:166,185; review c116b-pin :91). The reader shape is the PROVEN typed-control-seed
retarget on an OpSetIndexMode_v0 copy (tools/bench/diag_c97_tools_opbuild.py:104-125, OpCaseFrames_v1 / OpConstValueB_v0):
Traverse(Class Name='Wire', index) -> IA -> TMSC seeded to VI Server:Wire -> ONE Property node [GObject.UID 632A813, Wire.Joints[]
6371005] (a Wire PN reading UID + a wire property is the build_opnetinfo.py:151 shape). The Wire reference is then CLOSED by a
`Close Reference` copied from KernelBuilder_v1 #157 by copy_by_index, fed by the PN's `reference out` (the proven route,
tools/bench/diag_swap_build.py:81-94). No write property, no method: the op only reads.
PREDICTION (GATE lines): D donor copy ES 1; X donor IndexMode PN deleted ES 1; S Wire seed -> TMSC -> PN ES 1; I indicators UID /
Joints / error out created; A assembled ES 1, saved by script; CR Close Reference copied (uid guard 157), its `reference` on the PN's
`reference out`, ES 1; C COLD ES 1 in a fresh LabVIEW; labels -> tools/bench/diag_c116d_oplabels.json. No target VI is touched.
    py tools/bgrun.py --material --max-min 25 --log tools/bench/diag_c116d_opbuild.log -- py -u tools/bench/diag_c116d_opbuild.py
"""
import hashlib, json, os, shutil, subprocess, sys, time, traceback                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))  # noqa: E702
for _p in (os.path.join(ROOT, "tools"), HERE, os.path.join(ROOT, "tools", "recipes")):
    sys.path.insert(0, _p)
import protocol as P                                                                      # noqa: E402
import gscript as g                                                                       # noqa: E402
import bench_prep                                                                         # noqa: E402
CD, KEY = g.CLAUDEDEV, "OpWireJoints_v0"
OP = os.path.join(CD, KEY + ".vi")
KB = os.path.join(CD, "KernelBuilder_v1.vi")
LAB_P = os.path.join(HERE, "diag_c116d_oplabels.json")
STD = ("reference", "reference out", "error in (no error)", "error out")
g._run.__defaults__ = (6.0, 120.0)
G, LAB = {}, {}


class C97(object):
    """VERBATIM helpers of tools/bench/diag_c97_tools_opbuild.py:32-125 (that file runs its builds at import, so it is not imported)."""
    G, LAB = G, LAB

    @staticmethod
    def md5(p): return hashlib.md5(open(p, "rb").read()).hexdigest()

    @staticmethod
    def gate(k, ok, d=""):
        G[k] = bool(ok); print("  %s  %s  %s" % ("PASS" if ok else "FAIL", k, str(d)[:300]), flush=True); return bool(ok)  # noqa: E702

    class B(object):
        def __init__(s, donor, out):
            s.op = os.path.join(CD, out)
            if os.path.exists(s.op):
                os.remove(s.op)
            shutil.copyfile(os.path.join(CD, donor), s.op); time.sleep(0.3)              # noqa: E702
            g.open_panel(s.op); time.sleep(1.0); s.inv0 = g.uids(s.op, "Invoke")         # noqa: E702

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

        def data(s, uid, src):
            return [r["name"] for r in s.terms(uid)[1] if bool(r["is_source"]) == src and r["name"] not in STD]

        def finish(s, key, lab):
            g.set_auto_error_handling(s.op, False); s.purge(); es = g.exec_state(s.op)   # noqa: E702
            if C97.gate("%s A assembled ExecState 1" % key, es == 1, es):
                g.save(s.op); lab["controls"] = [r["label"] for r in g.panel_wiring(s.op) if not r["indicator"]]  # noqa: E702
                LAB[key] = lab; C97.gate("%s V saved by script" % key, os.path.getsize(s.op) > 0, (os.path.getsize(s.op), C97.md5(s.op)))  # noqa: E702
            try:
                g.close_panel(s.op)
            except Exception:                                                             # noqa: BLE001
                pass

    @staticmethod
    def retarget(b, key, cls, props, pos):
        nodes, _n = g.net_map(b.op, 0, max_nodes=60, max_terms=24)
        props0 = {p["uid"] for p in g.report_all(b.op, "Property")}
        pn_w = next((u for _k, (u, _l, t) in nodes.items() if any(x == "IndexMode" for _i, x, _w in t) and u in props0), None)
        g.delete_object(b.op, "Property", b.idx("Property", pn_w)); g.remove_bad_wires_scripted(b.op); b.purge()  # noqa: E702
        if not C97.gate("%s X donor IndexMode PN #%s deleted, ES 1" % (key, pn_w), g.exec_state(b.op) == 1):
            return None, None
        nodes, _n = g.net_map(b.op, 0, max_nodes=60, max_terms=24)
        tm = next(((u, t) for _k, (u, _l, t) in nodes.items() if any(x == "target class" for _i, x, _w in t)
                   and any(x == "specific class reference" for _i, x, _w in t)), None)
        W = next(w for _i, x, w in tm[1] if x == "target class")
        p = b.pn(cls, props, pos)
        n, rows = b.terms(p); t_ref = next(r for r in rows if r["name"] == "reference" and not r["is_source"])  # noqa: E702
        _o, seed = g.create_control(b.op, n, t_ref["i"]); b.purge()                       # noqa: E702
        w_seed = next(r["wire"] for r in b.terms(p)[1] if r["i"] == t_ref["i"])
        wires = [o["uid"] for o in g.report_all(b.op, "Wire")]; g.delete_object(b.op, "Wire", wires.index(w_seed))  # noqa: E702
        wires = [o["uid"] for o in g.report_all(b.op, "Wire")]; g.delete_object(b.op, "Wire", wires.index(W))  # noqa: E702
        g.wire_control(b.op, [seed], "Function", b.idx("Function", tm[0]), ["target class"]); b.purge()  # noqa: E702
        b.w(tm[0], "specific class reference", p, "reference", sc="Function")
        ok = C97.gate("%s S %s seed %r -> TMSC #%s -> PN #%s: ES 1" % (key, cls, seed, tm[0], p), g.exec_state(b.op) == 1)
        return (tm[0], p) if ok else (None, None)


def sweep(t):
    out = {}
    for n in range(80):
        uid, rows = g.node_terms_uid(t, 0, n)
        if not uid:
            break
        out[int(uid)] = (n, rows)
    return out


def build():
    b = C97.B("OpSetIndexMode_v0.vi", KEY + ".vi")
    if not C97.gate("%s D donor copy ES 1" % KEY, g.exec_state(b.op) == 1):
        return None
    tm, pn = C97.retarget(b, KEY, "VI Server:Wire", [("632A813", False), ("6371005", False)], (900, 450))
    if not tm:
        return None
    outs = b.data(pn, True)
    print("  FACT  PN #%s data outputs %r; terminals %r" % (pn, outs, [(r["i"], r["name"], r["is_source"], r["wire"]) for r in b.terms(pn)[1]]), flush=True)
    jn = [x for x in outs if "oint" in x]
    if not C97.gate("%s P PN carries a Joints output and a UID output" % KEY, len(jn) == 1 and "UID" in outs, outs):
        return None
    lab = {"joints_term": jn[0], "pn": pn, "tmsc": tm}
    lab["UID"] = b.ind(pn, "UID"); lab["Joints"] = b.ind(pn, jn[0]); lab["Err"] = b.ind(pn, "error out")  # noqa: E702
    print("  FACT  labels %r" % lab, flush=True)
    b.finish(KEY, lab)
    return lab if KEY in C97.LAB else None


def close_ref(lab):
    """diag_swap_build.py:81-94: restart, locate KB #157, restart, copy it into the op; finish wires its `reference`."""
    bench_prep.restart_labview(); g.reset(); time.sleep(3)                               # noqa: E702
    idx = next((i, c) for c in ("Node", "Function") for i, o in enumerate(g.report(KB, c)) if int(o["uid"]) == 157)
    print("  FACT  KB #157 = %s[%d]" % (idx[1], idx[0]), flush=True)
    g.reset(); bench_prep.restart_labview(); g.reset(); time.sleep(3)                    # noqa: E702
    pn = lab["pn"]

    def finish(dst, added):
        by = sweep(dst); cr = [u for u in by if u in set(int(o["uid"]) for o in added)]
        print("  FACT  finish: new top-level nodes %r" % cr, flush=True)
        ref = next(r for r in by[cr[0]][1] if r["name"] == "reference" and not r["is_source"])
        out = next(r for r in by[pn][1] if r["name"] == "reference out" and r["is_source"])
        g.connect_terminals(dst, by[cr[0]][0], ref["i"], by[pn][0], out["i"])
        by = sweep(dst); lab["close_ref"] = cr[0]
        lab["close_ref_wire"] = next(r["wire"] for r in by[cr[0]][1] if r["name"] == "reference" and not r["is_source"])
        print("  FACT  Close Reference #%s reference wire %r (PN reference out wire %r), ES %r" % (
            cr[0], lab["close_ref_wire"], next(r["wire"] for r in by[pn][1] if r["name"] == "reference out"), g.exec_state(dst)), flush=True)
    add, sel = g.copy_by_index(KB, idx[1], idx[0], OP, expect_uid=157, finish=finish)
    C97.gate("%s CR Close Reference copied (uid guard 157), fed by the PN's reference out" % KEY,
             sel == 157 and bool(lab.get("close_ref_wire")), (sel, len(add), lab.get("close_ref_wire")))


h0 = None
try:
    bench_prep.restart_labview(); g.reset(); time.sleep(3); h0 = bench_prep.labview_handles()  # noqa: E702
    print("  FACT  handles after restart %r" % h0, flush=True)
    lab = build()
    if lab:
        close_ref(lab)
        g.reset(); bench_prep.restart_labview(); g.reset(); time.sleep(3)                # noqa: E702
        C97.gate("%s C COLD ExecState 1 (fresh LabVIEW)" % KEY, g.exec_state(OP) == 1, C97.md5(OP))
        by = sweep(OP)
        print("  FACT  cold top-level nodes %r" % sorted(by), flush=True)
        C97.gate("%s CR2 cold: the Close Reference node is present and its reference is wired" % KEY,
                 lab.get("close_ref") in by and any(r["name"] == "reference" and r["wire"] for r in by[lab["close_ref"]][1]), lab.get("close_ref"))
        lab["controls"] = [r["label"] for r in g.panel_wiring(OP) if not r["indicator"]]
        lab["md5"] = C97.md5(OP)
        json.dump({KEY: lab}, open(LAB_P, "w", encoding="utf-8"), indent=1)
        print("  FACT  labels written %r" % lab, flush=True)
except Exception as e:                                                                    # noqa: BLE001
    traceback.print_exc(); C97.gate("the run completed without an unhandled exception", False, repr(e)[:200])  # noqa: E702
finally:
    try:
        print("  FACT  handles at end %r (start %r); refs %r" % (bench_prep.labview_handles(), h0, g.ref_counts()), flush=True)
    except Exception:                                                                     # noqa: BLE001
        pass
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)  # noqa: E702
    C97.gate("H LabVIEW gone", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower())
    bad = [k for k, v in G.items() if not v]
    arts = [{"path": OP, "md5": C97.md5(OP)}] if os.path.exists(OP) else []
    print("=== GATES: %d pass / %d fail; failing: %s" % (len(G) - len(bad), len(bad), bad), flush=True)
    print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, arts)), flush=True)
    sys.exit(1 if bad else 0)
