r"""diag_c125_5_stub - card 125-5 STEP 2 (brief_125-5.md, PD252(d)): does connect_term_uid leave a dangling segment end on a case-border
tunnel's OUTER face (P3a w27378, joint 3 LOOSE 0x100, diag_c125_joints.log:26,39) on a MINIMAL scratch VI?
SCRATCH (never saved, deleted): byte copy of claudeDev\EMPTY_v0.vi -> while_loop (OpWhileLoop_v0) -> add_shift_reg (OpAddShiftReg_v0) ->
Max & Min #A in the body (create_primitive_nested) -> case_wired(selector <- #A's first output) -> Max & Min #B in the case's first frame
-> ONE connect_term_uid(sink = #B's first input, source = the LEFT register's INNER face) -> wire_joints on every new wire.
EXISTING FIRST: every verb above exists (gscript.py; case_wired 123-7, connect_term_uid 124-5, wire_joints 117-1); the free-end rule is
diag_c125_joints.py dec() (1 neighbour, no terminal flag). If a stub appears, the Wire class's METHOD names are read off the machine by
build_invoke on candidate ids 6370C00..0F (methods sit 0x400 below the property base: Wire props 6371003-5, docs/NAMES.md; GObject
632A800/632A400, Terminal 634A000/6349C0x) - no new op, nothing invoked; a removal needs an op (judgement, card rule: no change to
connect_term_uid). No whole-VI Remove Bad Wires.
PREDICTION (measurement): S scratch built (loop, register, case, both nodes) / C connect_term_uid err '', Is Broken? False / J every new
wire read (echo, err ''); free ends counted and printed, NO count predicted / X LabVIEW gone, scratch deleted.
    py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_c125_5_stub.log -- py -u tools/bench/diag_c125_5_stub.py"""
import json, os, shutil, subprocess, sys, time, traceback                                  # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)  # noqa: E702
import protocol as P, gscript as g, bench_prep, allterms                                   # noqa: E401,E402
T =os.path.join(g.CLAUDEDEV, "scratch_c125_5_stub_%s.vi" % time.strftime("%Y%m%d_%H%M%S"))
G, OUT = {}, {}


def gate(k, ok, d=""):
    G[k] = bool(ok); print("  %s  %s  %s" % ("PASS" if ok else "FAIL", k, str(d)[:1500]), flush=True); return bool(ok)  # noqa: E702


def fact(k, v):
    OUT[k] = v; print("  FACT  %s: %s" % (k, json.dumps(v, default=str)[:1500]), flush=True)  # noqa: E702


def dec(r):
    """diag_c125_joints.py dec(): joint = [[x, y], flags, n_nb, ...]; flags & 0x1 terminal, & 0x100 LOOSE; free end = 1 neighbour, no terminal."""
    J = [list(x) for x in (r or {}).get("joints") or []]
    return {"joints": len(J), "loose": sum(1 for x in J if int(x[1]) & 0x100), "terms": sum(1 for x in J if int(x[1]) & 0x1),
            "free": [(i, list(x[0])) for i, x in enumerate(J) if int(x[2]) == 1 and not int(x[1]) & 0x1]}


def rows():
    return allterms.read_terms(T, allterms.OP_ALLTERMS_V1)[0]


try:
    shutil.copyfile(os.path.join(g.CLAUDEDEV, "EMPTY_v0.vi"), T); time.sleep(0.3)           # noqa: E702
    bench_prep.restart_labview(); g.reset(); time.sleep(3); g.open_panel(T)                  # noqa: E702
    g.while_loop(T, (200, 150)); lp = g.uids(T, "WhileLoop")                                 # noqa: E702
    body = [o["uid"] for o in g.report_all(T, "Diagram") if o["owner"] == "WhileLoop"]
    rsr = g.add_shift_reg(T, 0)
    fact("S loop / body / right SR", (lp, body, rsr))
    a = g.create_primitive_nested(T, body[0], "Max & Min", (120, 60))
    ra = [r for r in rows() if int(r["owner_uid"]) == a]
    cw = g.case_wired(T, body[0], a, next(r["term_name"] for r in ra if r["is_source"]), pos=(260, 40))
    fr = g.case_frames(T, cw["case"])
    b = g.create_primitive_nested(T, int(fr["frames"][0]), "Max & Min", (60, 60))
    R = rows()
    lsr = [r for r in R if r["owner_class"] == "LeftShiftRegister" and int(r["frame_diagram"] or 0) == body[0] and r["is_source"]]
    bx = [r for r in R if int(r["owner_uid"]) == b and not r["is_source"]]
    fact("S case / frames / node A / node B / left SR inner face / B inputs", (cw["case"], fr, a, b, [(r["term_uid"], r["owner_uid"]) for r in lsr],
         [(r["term_uid"], r["term_name"]) for r in bx]))
    if not gate("S scratch built: 1 loop, 1 body, case, node in frame 0, ONE left SR inner face", len(lp) == 1 and len(body) == 1 and len(lsr) == 1 and bx,
                (lp, body, len(lsr), len(bx))):
        raise RuntimeError("scratch not built")
    w0 = set(g.uids(T, "Wire"))
    c = g.connect_term_uid(T, int(bx[0]["term_uid"]), int(lsr[0]["term_uid"]))
    wn = sorted(set(g.uids(T, "Wire")) - w0)
    fact("C connect_term_uid", (c, wn))
    gate("C connect_term_uid err '', Is Broken? False", not c["err"] and c["broken"] is False, c)
    R = rows()
    fact("C terminals on the new wires (owner class, owner, name, src, frame, wire)", [(r["owner_class"], r["owner_uid"], r["term_name"], r["is_source"],
         r["frame_diagram"], r["wire_uid"]) for r in R if int(r["wire_uid"] or 0) in wn])
    J = dict((w, g.wire_joints(T, w)) for w in wn)
    D = dict((w, dec(j)) for w, j in J.items())
    fact("J joints raw", dict((w, j["joints"]) for w, j in J.items()))
    fact("J decoded (joints, loose, terms, free ends)", D)
    gate("J every new wire read (echo, err '')", J and all(not j["err"] and j["echo"] == w for w, j in J.items()), [(w, j["echo"], j["err"]) for w, j in J.items()])
    stub = sorted(w for w, d in D.items() if d["free"])
    fact("STUB (wires with a free segment end)", stub)
    if stub:
        probes = []
        for k in range(16):
            mid, i0 = "6370C%02X" % k, set(g.uids(T, "Invoke"))
            try:
                g.build_invoke(T, "VI Server:Wire", mid, (40 + 150 * (k % 8), 600 + 120 * (k // 8))); e = ""   # noqa: E702
            except Exception as ex:                                                          # noqa: BLE001
                e = str(ex)[:120]
            nw = sorted(set(g.uids(T, "Invoke")) - i0)
            names = [[(r["name"], r["is_source"]) for r in g.node_terms_uids(T, 0, g._node_index(T, 0, u))[1]] for u in nw]
            probes.append({"id": mid, "err": e, "new": nw, "terms": names})
            print("  PROBE %s" % json.dumps(probes[-1]), flush=True)
        fact("WIRE METHOD probes (6370C00..0F)", [(p["id"], [n for n, _s in (p["terms"][0] if p["terms"] else [])][4:6]) for p in probes])
    json.dump(OUT, open(os.path.join(HERE, "diag_c125_5_stub.json"), "w", encoding="utf-8"), default=str, indent=1)
except Exception as e:                                                                    # noqa: BLE001
    traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:300])  # noqa: E702
finally:
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)  # noqa: E702
    gate("X LabVIEW gone", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower())
    for _i in range(5):
        try:
            os.path.exists(T) and os.remove(T); break                                       # noqa: E702
        except OSError:
            time.sleep(2)
    gate("X scratch deleted", not os.path.exists(T), T)
    bad = [k for k, v in G.items() if not v]
    print("=== GATES: %d pass / %d fail; failing: %s" % (len(G) - len(bad), len(bad), bad), flush=True)
    print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, [])), flush=True)
    sys.exit(1 if bad else 0)
