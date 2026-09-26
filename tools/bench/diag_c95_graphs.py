r"""diag_c95_graphs.py - card 95-4, READ-ONLY. Three reads, nothing saved, no VI run except op VIs.
(0) the LabVIEW instance 95-2 left running (pid 7984): its handle count is READ, then bench_prep.restart_labview()
    (standing restart authority) and the fresh instance's handle count is read.
(1) the terminal-list graph JSONs tools/stage_prerun.py's dry run / pre-run needs (find_graph keys on the INPUT md5;
    95-2 was BLOCKED because none existed for these inputs): donor OpLoopCast_v0.vi (input of
    tools/recipes/build_opforlooppar_v0.py) and HARNESS_copyloop.vi (input of tools/bench/selftest_opforlooppar_v0.py).
    Same reader + shape as tools/bench/diag_replay_graph77.py:16-19 (wiki_build.read_live on a byte copy ->
    {vi, md5, terminals, objs}); the copies are scratch_c95_g_* under claudeDev, deleted at the end.
(2) FIR Filter (DBL).vi (the callee at S1 #28233, vi.lib 3filter.llb; 95-2: 2 LeftShiftRegister, never read):
    read_live IN PLACE (an original: read, never saved; md5 before == after) -> per LeftShiftRegister its OuterTerminal
    wire (0 = UNINITIALISED shift register) and its owner.
PREDICTION: G1/G2 graph written, terminals > 0 and objs > 0, stage_prerun.graph_shape_error None, header md5 == donor md5;
G1b donor has exactly ONE node with terminals 'specific class reference' + 'target class' (the TMSC the build branches);
G2b harness has exactly 1 ForLoop; F1 FIR LeftShiftRegister count == 2 (95-2) and each OuterTerminal wire RECORDED (not
predicted); md5 of every donor/callee/S1 unchanged; scratches deleted; LabVIEW gone at exit.
    py tools/bgrun.py --material --max-min 12 --log tools/bench/diag_c95_graphs.log -- py -u tools/bench/diag_c95_graphs.py"""
import hashlib, json, os, shutil, subprocess, sys, time                             # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))  # noqa: E702
for p in (os.path.join(ROOT, "tools"), HERE):
    sys.path.insert(0, p)
import protocol as P                                                              # noqa: E402
import gscript as g                                                               # noqa: E402
import wiki_build as Wb                                                           # noqa: E402
import bench_prep                                                                 # noqa: E402
from stage_prerun import graph_shape_error                                        # noqa: E402
CD = g.CLAUDEDEV; STAMP = time.strftime("%Y%m%d_%H%M%S")                          # noqa: E702
DONORS = (("oploopcast_v0", os.path.join(CD, "OpLoopCast_v0.vi")), ("harness_copyloop", os.path.join(CD, "HARNESS_copyloop.vi")))
FIR = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Analysis\3filter.llb\FIR Filter (DBL).vi"
S1 = os.path.join(CD, "D1_s1_copy.vi"); S1_MD5 = "3e3d23cefd3a334001aa9d6156bf1aee"  # noqa: E702
OUT = os.path.join(HERE, "diag_c95_graphs.json")
g._run.__defaults__ = (6.0, 120.0)
G, R, SCR = {}, {"stamp": STAMP}, []


def md5(p): return hashlib.md5(open(p, "rb").read()).hexdigest()


def gate(k, ok, detail=""):
    G[k] = bool(ok); print("GATE %-70s %s  %s" % (k, "PASS" if ok else "FAIL", str(detail)[:300]), flush=True); return bool(ok)


def pids():
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq LabVIEW.exe", "/FO", "CSV", "/NH"], capture_output=True, text=True, errors="replace").stdout
    return [ln.split('","')[1] for ln in out.splitlines() if ln.lower().startswith('"labview.exe"')]


try:
    md0 = {"S1": md5(S1), "FIR": md5(FIR)}; md0.update({t: md5(p) for t, p in DONORS}); R["md5_before"] = md0
    R["lv_before"] = {"pids": pids(), "handles": bench_prep.labview_handles()}
    print("LabVIEW BEFORE: %r" % R["lv_before"], flush=True)
    bench_prep.restart_labview(); g.reset()
    R["lv_after_restart"] = {"pids": pids(), "handles": bench_prep.labview_handles()}
    print("LabVIEW AFTER restart: %r" % R["lv_after_restart"], flush=True)
    gate("R0 pid 7984 gone, one fresh LabVIEW, handle count read", "7984" not in R["lv_after_restart"]["pids"]
         and len(R["lv_after_restart"]["pids"]) == 1 and R["lv_after_restart"]["handles"] > 0, R["lv_after_restart"])
    for tag, src in DONORS:
        cp = os.path.join(CD, "scratch_c95_g_%s_%s.vi" % (tag, STAMP)); shutil.copyfile(src, cp); SCR.append(cp); time.sleep(0.4)
        gate("C %s scratch is a byte copy" % tag, md5(cp) == md0[tag])
        lv = Wb.read_live(cp, fs_pairs=[])
        out = os.path.join(HERE, "graph_%s_c95.json" % tag)
        d = {"vi": src, "md5": md0[tag], "terminals": lv["terminals"], "objs": lv["objs"], "secs": lv["secs"],
             "note": "card 95-4 diag_c95_graphs.py: wiki_build.read_live on byte copy %s" % os.path.basename(cp)}
        with open(out, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=0)
        why = graph_shape_error(json.load(open(out, encoding="utf-8")))
        gate("G %s graph written: %d terminals, %d objs, shape OK" % (tag, len(lv["terminals"]), len(lv["objs"])),
             lv["terminals"] and lv["objs"] and why is None, why or out)
        by = {}
        for r in lv["terminals"]:
            by.setdefault(int(r["owner_uid"]), []).append(r)
        cls = {int(o["uid"]): o["class"] for o in lv["objs"]}
        R[tag] = {"graph": os.path.relpath(out, ROOT), "graph_md5": md5(out), "n_terms": len(lv["terminals"]), "n_objs": len(lv["objs"]),
                  "classes": sorted(set(cls.values()))}
        if tag == "oploopcast_v0":
            tm = [u for u, rows in by.items() if {"specific class reference", "target class"} <= set(r["term_name"] for r in rows)]
            R[tag]["tmsc"] = tm; R[tag]["tmsc_terms"] = [(r["term_uid"], r["term_name"], r["is_source"], r["wire_uid"]) for u in tm for r in by[u]]
            R[tag]["property_nodes"] = sorted(u for u, c in cls.items() if c == "Property")
            gate("G1b donor has exactly ONE TMSC (specific class reference + target class)", len(tm) == 1, R[tag]["tmsc_terms"])
        else:
            fl = sorted(u for u, c in cls.items() if c == "ForLoop"); R[tag]["forloops"] = fl
            R[tag]["whileloops"] = sorted(u for u, c in cls.items() if c == "WhileLoop")
            gate("G2b harness has exactly 1 ForLoop", len(fl) == 1, R[tag])
        print("FACT %s %s" % (tag, json.dumps(R[tag], default=str)[:900]), flush=True)
    lv = Wb.read_live(FIR, fs_pairs=[])
    cls = {int(o["uid"]): o for o in lv["objs"]}
    lsr = sorted(u for u, o in cls.items() if o["class"] == "LeftShiftRegister")
    rows = [{"lsr": u, "owner": cls[u].get("owner"), "terms": [(r["term_uid"], r["term_name"], r["term_class"], r["is_source"], r["wire_uid"])
                                                               for r in lv["terminals"] if int(r["owner_uid"]) == u]} for u in lsr]
    for x in rows:
        outer = [t for t in x["terms"] if t[2] == "OuterTerminal"]
        x["outer_wire"] = [t[4] for t in outer]; x["initialised"] = bool(outer) and all(t[4] for t in outer)
        print("FACT FIR LSR #%d owner %r initialised=%s terms %r" % (x["lsr"], x["owner"], x["initialised"], x["terms"]), flush=True)
    R["fir"] = {"path": FIR, "lsr": rows, "classes": sorted(set(o["class"] for o in cls.values())),
                "controls": [(r["term_uid"], r["term_name"], r["is_source"], r["wire_uid"]) for r in lv["terminals"] if r.get("owner_class") == "ControlTerminal"]}
    print("FACT FIR controls %r" % R["fir"]["controls"], flush=True)
    gate("F1 FIR Filter (DBL) LeftShiftRegister count == 2, each OuterTerminal wire read", len(rows) == 2 and all(x["outer_wire"] for x in rows), [(x["lsr"], x["outer_wire"]) for x in rows])
except Exception as e:                                                             # noqa: BLE001
    import traceback; traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:200])  # noqa: E702
try:
    g.reset()
except Exception:                                                                  # noqa: BLE001
    pass
subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"], capture_output=True); time.sleep(6)
for p in SCR:
    for _ in range(5):
        try:
            os.path.exists(p) and os.remove(p); break                              # noqa: E702
        except OSError:
            time.sleep(3)
gate("H1 scratches deleted", not any(os.path.exists(p) for p in SCR), SCR)
md1 = {"S1": md5(S1), "FIR": md5(FIR)}; md1.update({t: md5(p) for t, p in DONORS}); R["md5_after"] = md1  # noqa: E702
gate("H2 donors, FIR callee and S1 md5 unchanged", md1 == R.get("md5_before"), md1)
gate("H3 LabVIEW gone at exit", not pids())
json.dump({"schema": "diag-c95-graphs/1", "card": "95-4", "gates": G, "R": R}, open(OUT, "w"), indent=1, default=str)
bad = [k for k, v in G.items() if not v]
arts = [{"path": os.path.relpath(OUT, ROOT), "md5": md5(OUT)}] + [{"path": R[t]["graph"], "md5": R[t]["graph_md5"]} for t, _p in DONORS if t in R]
print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, arts)), flush=True)
sys.exit(1 if bad else 0)
