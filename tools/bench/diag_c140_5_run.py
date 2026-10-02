r"""diag_c140_5_run.py - card 140-5 (PD322(c)): build claudeDev\DonorRAS1D_v0.vi = ONE 1-D I32 Replace Array Subset.
FOUND FIRST: no 1-D RAS anywhere (diag_c140_4_facts.md:23-27); the bed byte copy holds 2-D RAS #23206 (census:45-50); a primitive
is placed only by donor copy (gscript.create_primitive_nested, gscript.py:4782); a 1-D I32 array CONTROL = generator For (N=20,
I32 0 const DonorSRInit_v0 #248) -> Greater?.y, then create_control on Greater?.x (139-3 measured: I32[20], diag_c139_3_facts.md:25-28).
Helpers imported from diag_c138_6_run (as 139-1/139-3); the bed itself is never opened (byte copy = donor only).
PREDICTION: copied RAS has 5 terminals (2-D); after RAS.array <- the 1-D I32 control it ADAPTS to 4 terminals (array, index,
new element/subarray, output array; class GrowableFunction, label 'Replace Array Subset'); controls index/new + indicator out
created, labels set to array/index/new/out; ExecState 1; saved by script. ONE run: array 0..19, index 3, new 99 -> out len 20,
out[3] == 99, others unchanged. LabVIEW gone; bed copy deleted; donor kept.
ATTEMPT 2 (v1 log kept as diag_c140_5_run.log): v1 stopped at create_control_nested on top-level RAS #175 (gscript.py:4149 refuses
top-level owners); index/new/out now use create_control / create_indicator by node index (gscript.py:2922/2950), panel uid by
panel_wiring diff. Everything else unchanged.
    py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_c140_5_run2.log -- py -u tools/bench/diag_c140_5_run.py"""
import json, os, shutil, sys, time, traceback                                              # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)                    # noqa: E702
import diag_c138_6_run as D                                                                    # noqa: E402 (main() guarded)
S5, g, TB, P = D.S5, D.g, D.TB, D.P                                                             # noqa: E702
gate, fact, md5, Stop, rows, one, cp = D.gate, D.fact, D.md5, D.Stop, D.rows, D.one, D.cp       # noqa: E702
CD, BED, BEDM, TS = g.CLAUDEDEV, S5.BED, S5.BED_MD5, time.strftime("%H%M%S")                   # noqa: E702
DON, EMPTY = os.path.join(CD, "DonorRAS1D_v0.vi"), os.path.join(CD, "EMPTY_v0.vi")             # noqa: E702
BEDD = os.path.join(CD, "scratch_c140_5_bdon_%s.vi" % TS); D.TGT2 = DON; RAS_D = 23206          # noqa: E702
IIA = ["array", "index", "new element/subarray", "output array"]                                # census:184-187 (#29157)
OUT, SCR = {}, S5.SCR
def ldump(): json.dump(OUT, open(os.path.join(HERE, "diag_c140_5_out.json"), "w", encoding="utf-8"), indent=1, default=str)   # noqa: E704
def rterms(u): return [(x["term_name"], x["is_source"], x["term_uid"], x["wire_uid"]) for x in rows(DON) if x["owner_uid"] == u]   # noqa: E704
def tidx(u, name, src): return next(r["i"] for r in g.node_terms_uid(DON, 0, g._node_index(DON, 0, u))[1] if r["name"] == name and bool(r["is_source"]) == src)   # noqa: E704
def step1():
    shutil.copyfile(BED, BEDD); SCR.append(BEDD); gate("1 bed byte copy md5 == bed", md5(BEDD) == BEDM)   # noqa: E702
    os.path.exists(DON) and os.remove(DON); shutil.copyfile(EMPTY, DON); g.open_panel(DON)      # noqa: E702
    top = int(g.report_all(DON, "Diagram")[0]["uid"]); d0, f0 = g.uids(DON, "Diagram"), g.uids(DON, "ForLoop")   # noqa: E702
    g.for_loop(DON, (60, 400)); FG = sorted(g.uids(DON, "ForLoop") - f0)[0]; fgb = sorted(g.uids(DON, "Diagram") - d0)[0]   # noqa: E702
    g.create_const_loop_term(DON, "for_n", TB.walk(DON, 0)[FG][0], value=20)
    k0, GH = cp(fgb, "const_donor", (40, 40), {"donor": D.I0_D, "uid": 248}), cp(top, "Greater?", (300, 420), {"donor": BEDD, "uid": 11721})
    RAS = cp(top, "Replace Array Subset", (600, 200), {"donor": BEDD, "uid": RAS_D})
    B = OUT["B"] = {"top": top, "FG": FG, "fgb": fgb, "k0": k0, "GH": GH, "RAS": RAS, "wires": {}}; fact("1 created", B)   # noqa: E702
    B["ras_terms_copied"] = rterms(RAS); fact("1 RAS terminals as copied", B["ras_terms_copied"])   # noqa: E702
    def Wr(tag, snk, src):
        r = g.connect_term_uid(DON, snk, src); B["wires"][tag] = r; fact("1 WIRE %s" % tag, r)   # noqa: E702
        gate("1 wire %s err '' and Is Broken? False" % tag, not r.get("err") and r.get("broken") is False, r); return rows(DON)   # noqa: E702
    R = Wr("GH.y <- k0 (FG out)", one(rows(DON), owner_uid=GH, term_name="y")["term_uid"], one(rows(DON), owner_uid=k0, is_source=True)["term_uid"])
    nx = TB.walk(DON, 0)[GH][0]; tx = next(r["i"] for r in g.node_terms_uid(DON, 0, nx)[1] if r["name"] == "x" and not r["is_source"])   # noqa: E702
    new, lab = g.create_control(DON, nx, tx)
    R = rows(DON); w = one(R, owner_uid=GH, term_name="x")["wire_uid"]; num = one(R, wire_uid=w, is_source=True); B["num"] = (new, lab, num)   # noqa: E702
    gate("1 array control created on Greater?.x", new and w, B["num"])
    R = Wr("RAS.array <- array control", one(R, owner_uid=RAS, term_name="array")["term_uid"], num["term_uid"])
    T = B["ras_terms_wired"] = rterms(RAS); fact("1 RAS terminals after the 1-D wire", T)    # noqa: E702
    gate("1 RAS adapted to 4 terminals (1-D)", len(T) == 4, [t[0] for t in T])
    ix = [t for t in T if not t[1] and t[0] not in ("array", "new element/subarray")]; gate("1 exactly one index sink", len(ix) == 1, ix)   # noqa: E702
    def mk(fn, name, src):   # v2 (attempt 2): TOP-LEVEL route by node index (gscript.py:2922/2950), as Greater?.x above; panel uid by panel_wiring diff
        p0 = set(int(r["uid"]) for r in g.panel_wiring(DON)); nx = TB.walk(DON, 0)[RAS][0]       # noqa: E702
        ti = next(r["i"] for r in g.node_terms_uid(DON, 0, nx)[1] if r["name"] == name and bool(r["is_source"]) == src)
        r = fn(DON, nx, ti); np_ = [x for x in g.panel_wiring(DON) if int(x["uid"]) not in p0]; ok = len(np_) == 1 and bool(np_[0]["wire"])   # noqa: E702
        return {"ret": r, "new_panel": np_, "created_uid": int(np_[0]["uid"]) if ok else None, "err": "" if ok else "new panel rows %r" % np_}
    B["ctl_index"] = mk(g.create_control, ix[0][0], False)
    B["ctl_new"] = mk(g.create_control, "new element/subarray", False)
    B["ind_out"] = mk(g.create_indicator, "output array", True); fact("1 index/new/out", (B["ctl_index"], B["ctl_new"], B["ind_out"]))   # noqa: E702
    gate("1 index/new controls + out indicator, err ''", all(B[k].get("created_uid") and not B[k].get("err") for k in ("ctl_index", "ctl_new", "ind_out")))
    want = {int(B["ctl_index"]["created_uid"]): "index", int(B["ctl_new"]["created_uid"]): "new", int(B["ind_out"]["created_uid"]): "out"}
    pw = g.panel_wiring(DON); fact("1 panel before rename", [(r["uid"], r["label"], r["indicator"], r["wire"]) for r in pw])   # noqa: E702
    rest = [int(r["uid"]) for r in pw if int(r["uid"]) not in want]; gate("1 exactly one other panel object (the array control)", len(rest) == 1, rest)   # noqa: E702
    want[rest[0]] = "array"
    B["rename"] = [(i, r["uid"], want.get(int(r["uid"])), g.set_control_label(DON, i, want[int(r["uid"])]) if int(r["uid"]) in want else None) for i, r in enumerate(pw)]
    pw = B["panel"] = [(r["uid"], r["label"], r["indicator"], r["wire"]) for r in g.panel_wiring(DON)]; fact("1 panel after rename", pw)   # noqa: E702
    gate("1 panel labels == {array, index, new, out}, 'out' the only indicator", sorted(p[1] for p in pw) == ["array", "index", "new", "out"]
         and [p[1] for p in pw if p[2]] == ["out"], pw)
    L = B["labels"] = [x for x in g.node_labels(DON, 0) if int(x["uid"]) == RAS]; T = B["ras_terms_final"] = rterms(RAS)   # noqa: E702
    B["ras_class"] = sorted(set(x["owner_class"] for x in rows(DON) if x["owner_uid"] == RAS)); fact("2 RAS uid/label/class/terminals", (RAS, L, B["ras_class"], T))   # noqa: E702
    gate("2 label == 'Replace Array Subset' (NOT 'Insert Into Array')", len(L) == 1 and L[0]["label"] == "Replace Array Subset", L)
    B["types"] = dict((t[0], (g.read_term_type(DON, t[2]).get("types") or {}).get("sig")) for t in T); fact("2 RAS terminal type sigs", B["types"])   # noqa: E702
    rn = [t[0] for t in T]; B["map"] = [(n, n if n in rn else None) for n in IIA] + [(None, n) for n in rn if n not in IIA]   # noqa: E702
    fact("4 terminal map IIA #29157 -> RAS (None = unmatched)", B["map"])
    es = B["es"] = g.exec_state(DON); gate("1 ExecState 1", es == 1, es)                        # noqa: E702
    g.save(DON); B["md5_saved"] = md5(DON); gate("1 saved by script", os.path.getsize(DON) > 0, B["md5_saved"])   # noqa: E702
    vi = g.lv().GetVIReference(DON, "", False, 0); A = list(range(20))                         # noqa: E702
    vi.SetControlValue("array", A); vi.SetControlValue("index", 3); vi.SetControlValue("new", 99); g._run(vi)   # noqa: E702
    o = B["run_out"] = list(vi.GetControlValue("out")); fact("3 RUN out", o)                    # noqa: E702
    gate("3 RUN out len 20, out[3] == 99, others unchanged", len(o) == 20 and o[3] == 99 and all(o[k] == k for k in range(20) if k != 3), o, need=False)
    json.dump({"function": "Replace Array Subset 1-D: 2-D donor copy adapts on a 1-D wire", "card": "140-5", "t": time.time(),
               "log": "tools/bench/diag_c140_5_run.log", "status": "PASS" if all(S5.G.values()) else "FAIL", "out": B},
              open(os.path.join(HERE, "scratch_verify", "ras1d_c140_5_%s.json" % TS), "w", encoding="utf-8"), default=str, indent=1)
def main():
    D.bench_prep.restart_labview(); g.reset(); time.sleep(3); gate("bed md5 before", md5(BED) == BEDM)   # noqa: E702
    step1()
if __name__ == "__main__":
    try:
        main()
    except Stop as e:
        print("STOP at the first unexpected result: %s" % e, flush=True)
    except Exception as e:                                                                      # noqa: BLE001
        traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:300], need=False)   # noqa: E702
    finally:
        ldump(); g.reset()                                                                       # noqa: E702
        S5.subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(5)   # noqa: E702
        gate("5 LabVIEW gone", "labview.exe" not in S5.subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower(), need=False)
        for p in SCR:
            for _ in range(5):
                try:
                    os.path.exists(p) and os.remove(p); break                                    # noqa: E702
                except OSError:
                    time.sleep(2)
        gate("5 scratch files deleted", not any(os.path.exists(p) for p in SCR), SCR, need=False)
        gate("5 bed md5 unchanged; donor kept", md5(BED) == BEDM and os.path.exists(DON), (os.path.exists(DON) and md5(DON)), need=False)
        bad = [k for k, v in S5.G.items() if not v]
        print("=== GATES: %d pass / %d fail; failing: %s" % (len(S5.G) - len(bad), len(bad), bad), flush=True)
        print(P.result_line(P.make_result(len(S5.G) - len(bad), len(bad), bad[0] if bad else None, [])), flush=True)
        sys.exit(1 if bad else 0)
